# Nutanix Prism Central at Scale

## Scope

Prism Central (PC) deployment sizing, scale-out architecture, multi-site management patterns, high availability, disaster recovery, and feature scaling considerations for environments managing 10,000+ VMs across multiple clusters and sites.

## Checklist

- [ ] [Critical] Has the correct Prism Central sizing tier been selected based on current VM count and 3-year growth projection? Undersizing PC causes performance degradation across all managed clusters; oversizing wastes resources on the hosting cluster.
- [ ] [Critical] For environments exceeding 12,000 VMs, is Prism Central deployed in scale-out mode (3-VM deployment) rather than single-VM mode? A single PC VM supports up to 12,000 VMs; scale-out extends this to 25,000 powered-on VMs with n+1 fault tolerance.
- [ ] [Critical] For environments spanning 5+ sites with 12,000+ VMs, has a deliberate decision been made between a single centralized scale-out PC versus multiple regional PC instances? A single scale-out PC simplifies policy consistency and reporting but introduces WAN dependency; multiple PCs provide regional autonomy but fragment management and require Nutanix Central (Service Central) for unified visibility.
- [ ] [Critical] Is Prism Central backup configured with at least two geographically distributed backup target clusters? Continuous backup replicates IDF data every 30 minutes (RPO 30 min, RTO 2 hours) to up to three registered PE clusters, which should be in different physical locations for site-level protection.
- [ ] [Critical] For Flow Network Security deployments, is Prism Central sized at X-Large (14 vCPU, 60 GB RAM per VM)? Flow Virtual Networking requires X-Large PC -- Small and Large PC VMs are not supported for Flow virtual networking features.
- [ ] [Recommended] Has the PC hosting cluster been sized to accommodate the PC VM(s) without resource contention? A 3-VM X-Large scale-out deployment consumes 42 vCPUs, 180 GB RAM, and 7.5 TB disk across the hosting cluster, plus additional resources for enabled features (Calm, Flow, DR).
- [ ] [Recommended] Is point-in-time backup configured to an offsite S3-compatible target (AWS S3 or Nutanix Objects) for ransomware and site-loss protection? Point-in-time backup provides RPO 2 hours, RTO 2 hours, with restore capability for backups up to one month old.
- [ ] [Recommended] Are PC-to-cluster communication paths verified for port 9440 (HTTPS/API) and port 9440 (IDF replication) across all managed sites, with latency under 200 ms round-trip for acceptable UI and API responsiveness?
- [ ] [Recommended] Is the Prism Central upgrade path documented -- understanding that in-place tier resizing is not natively supported and requires deploying a new PC instance, restoring from backup, and re-registering clusters?
- [ ] [Recommended] Are category taxonomies (key:value pairs) planned before deployment at scale? Categories underpin Flow policies, Calm blueprints, reporting, and RBAC -- retrofitting taxonomy across 10,000+ VMs is operationally expensive.
- [ ] [Recommended] Has API rate limiting been accounted for in automation workflows? Large-scale environments with multiple automation tools (Terraform, Calm, custom scripts) hitting the PC API concurrently can trigger throttling, causing deployment failures and monitoring gaps.
- [ ] [Recommended] For multi-PC deployments, is Nutanix Central (Service Central, requires PC 2023.4.0.2+) deployed to provide aggregated visibility, centralized policy distribution, and unified alerting across all PC instances?
- [ ] [Optional] Are Prism Central playbooks configured for automated housekeeping at scale -- auto-tagging untagged VMs, alerting on snapshot sprawl, power-off of idle VMs, and report generation scheduling during off-peak hours?
- [ ] [Optional] Is a dedicated management cluster used to host Prism Central VMs, separating management plane resources from production workloads to prevent resource contention during PC upgrades or scale-out operations?

## Why This Matters

Prism Central is the single management plane for all Nutanix operations beyond a single cluster. At scale (10,000+ VMs, 5+ sites), PC sizing and architecture decisions have cascading effects: an undersized PC degrades API response times, delays entity synchronization across clusters, slows report generation, and can cause Flow policy propagation failures. The choice between a single centralized PC and multiple regional PC instances determines whether administrators get unified policy enforcement and reporting (single PC) or regional autonomy and WAN independence (multiple PCs). Scale-out from single-VM to 3-VM is a one-way operation that cannot be reversed, making it a critical early architectural decision. PC backup and DR are frequently overlooked -- if Prism Central is lost without a current backup, all Calm blueprints, Flow policies, Leap protection domains, category assignments, RBAC configurations, and historical metrics must be manually reconstructed. The upgrade path between sizing tiers is disruptive (new deployment + backup restore + cluster re-registration), so right-sizing at initial deployment avoids costly operational interruptions later.

## Sizing Reference

| Tier | vCPU per VM | RAM per VM | Disk per VM | Max Clusters | Max Hosts | Max VMs | Deployment |
|---|---|---|---|---|---|---|---|
| X-Small | 4 | 18 GB | 100 GB | 5 | 50 | 500 | Single VM only |
| Small | 6 | 26 GB | 500 GB | 25 | 250 | 2,500 | 1-VM or 3-VM |
| Large | 10 | 44 GB | 2,500 GB | 75 | 750 | 7,500 | 1-VM or 3-VM |
| X-Large | 14 | 60 GB | 2,500 GB | 150 | 1,500 | 25,000 | 1-VM or 3-VM |

**Scale-out (3-VM) deployment** doubles the VM management capacity of a given tier (e.g., Small 3-VM supports ~5,000 VMs, X-Large 3-VM supports ~25,000 VMs) and provides n+1 fault tolerance.

**Feature resource overhead**: Enabling optional features (Calm/Self-Service, Flow Network Security, Disaster Recovery/Leap, Intelligent Operations) automatically allocates additional vCPU and memory to the PC VM(s) beyond the base tier specifications. Plan for 20-30% overhead when multiple features are active.

## Scale-Out Architecture

- Scale-out deploys 3 PC VMs with shared-nothing microservices architecture; services are distributed across all 3 VMs with leader election for singleton services.
- Anti-affinity rules should be configured to ensure PC VMs run on separate physical hosts within the hosting cluster for true HA.
- Scale-out tolerates the failure of 1 PC VM (n+1). If 2 VMs fail, PC becomes unavailable. The failed VM is automatically respawned on another host if AHV Node HA is enabled.
- Scale-out is a one-way operation: once expanded from 1 VM to 3 VMs, you cannot revert to a single-VM deployment.
- All 3 PC VMs must reside on the same PE cluster; they cannot be split across clusters or sites.

## Multi-Site Deployment Patterns

### Single Centralized PC (Scale-Out)

Best for: up to 25,000 VMs, consistent policy enforcement, unified reporting.

- All clusters across all sites register to one scale-out PC instance.
- Provides single pane of glass for Flow policies, Calm blueprints, Leap DR, categories, and RBAC.
- Requires reliable WAN connectivity (port 9440) from all remote sites to the PC hosting site.
- WAN latency above 200 ms degrades UI responsiveness and API performance.
- Single point of failure at the site level (mitigated by PC backup to remote clusters and S3).

### Multiple Regional PCs

Best for: 25,000+ VMs, high WAN latency between sites, regulatory data sovereignty, regional autonomy requirements.

- Each region or major site gets its own PC instance managing local clusters.
- Nutanix Central (Service Central) provides aggregated dashboard across all PC instances.
- Flow policies, Calm blueprints, and categories must be maintained independently per PC (no native cross-PC policy sync).
- Leap DR between sites requires both source and target PCs to be configured as Availability Zones with each other.
- Increases operational overhead: multiple upgrade cycles, multiple backup configurations, potential policy drift.

### Decision Framework: 12,000+ VMs Across 5+ Sites

| Factor | Single Centralized PC | Multiple Regional PCs |
|---|---|---|
| VM count under 25,000 | Preferred | Unnecessary complexity |
| VM count over 25,000 | Not supported | Required |
| WAN reliability > 99.9% | Viable | Not required |
| WAN latency < 100 ms | Viable | Not required |
| Latency 100-200 ms | Acceptable with caveats | Preferred |
| Latency > 200 ms | Not recommended | Required |
| Data sovereignty per region | Cannot satisfy | Satisfies |
| Unified Flow policies | Native | Requires manual sync |
| Leap DR across sites | Single config | Each PC pair configured separately |
| Operational team per region | Overkill | Good fit |

## Backup and DR

### Continuous Backup (IDF Replication)
- Replicates Prism Central configuration database (Insights Data Fabric) to up to 3 registered PE clusters every 30 minutes.
- RPO: 30 minutes. RTO: 2 hours.
- Backup targets should be geographically distributed; all must run AOS 6.0+ (at least one at AOS 6.5.3.1+).
- Replication traffic uses port 9440 (TCP).
- NTP synchronization required between PC and all backup target clusters.

### Point-in-Time Backup (S3)
- Backs up to AWS S3 or Nutanix Objects (S3-compatible) for offsite/air-gapped protection.
- RPO: 2 hours. RTO: 2 hours.
- Retention: restorable for up to 1 month.
- Recommended for ransomware protection and site-loss scenarios.

### What Gets Backed Up
- Intelligent Operations configurations, Flow Virtual Networking, Flow Network Security policies, Nutanix Disaster Recovery (Leap) configurations, access policies, categories, virtual networks, IAMv2 policies, and 90 days of metrics.

### What Does NOT Get Backed Up
- NCM Self-Service (Calm) blueprints and marketplace items, Catalog, Images, VM Templates, and metrics older than 90 days. These must be version-controlled or backed up independently.

### Restore Process
- From any surviving backup PE cluster, deploy a new PC instance (downloads latest installer from Nutanix portal or uses dark-site bundle).
- Restore from IDF backup; re-seeds configuration and metrics.
- If original PC comes back online, it must be shut down or deleted before resuming operations on the restored instance to avoid split-brain.

## Feature Scaling Considerations

### Flow Network Security
- Requires X-Large PC for Flow Virtual Networking features.
- At 10,000+ VMs, carefully plan category-based policy groups to avoid overly broad rules that generate excessive rule tables on each AHV host.
- Flow policies are pushed to AHV hosts via Open vSwitch (OVS) rules; thousands of fine-grained rules per host can impact network performance.
- Test policy propagation time in staging before deploying at scale.

### NCM Self-Service (Calm)
- Calm blueprints and marketplace items are NOT included in PC backup; store blueprints in Git.
- Large numbers of concurrent blueprint launches can strain PC API; stagger bulk deployments.
- Calm audit logs grow significantly at scale; monitor PC disk utilization.

### Leap (Disaster Recovery)
- Protection domains and recovery plans are managed per PC; multi-PC environments require separate Leap configurations per PC pair.
- At scale, large numbers of protection domains (100+) increase entity sync time and PC resource consumption.
- Validate RPO adherence with NCC (Nutanix Cluster Check) health checks.

### Reporting and Analytics
- Report generation on 10,000+ entities is resource-intensive; schedule reports during off-peak hours.
- Entity sync interval between PE clusters and PC is typically 1-5 minutes; during network disruptions, sync backlog can temporarily show stale data.
- Custom dashboards with many widgets querying large entity sets can cause UI slowness.

### API and Automation
- PC API (v3/v4) handles concurrent requests but can throttle under heavy load from multiple automation tools.
- Implement retry logic with exponential backoff in all API clients.
- Use batch/list APIs with pagination (limit/offset) rather than fetching all entities in a single call.
- Monitor PC API response times via Prism Central metrics; sustained p99 latency above 5 seconds indicates capacity pressure.

## Upgrade Path

| From | To | Method |
|---|---|---|
| X-Small | Small/Large/X-Large | Contact Nutanix Support for assisted resize |
| Small (1-VM) | Small (3-VM) | Scale-out via PC UI (adds 2 VMs, one-way) |
| Small (1-VM) | Large/X-Large | Deploy new PC at target size, restore from backup, re-register clusters |
| Large (1-VM) | Large (3-VM) | Scale-out via PC UI (adds 2 VMs, one-way) |
| Large (1-VM) | X-Large | Deploy new PC at target size, restore from backup, re-register clusters |
| Any (3-VM) | Larger tier (3-VM) | Deploy new PC at target size, restore from backup, re-register clusters |
| Any | X-Small | Not supported (downgrade) |

**Key constraint**: In-place tier changes (e.g., Small to Large) are not supported natively. The process requires deploying a new PC instance at the desired size, restoring configuration from backup, and re-registering all PE clusters. Plan for a maintenance window of 2-4 hours depending on environment size.

## Networking Requirements

- **Management network**: All PC VMs need IP addresses on the management network with Layer 3 reachability to all managed PE clusters (port 9440 TCP/HTTPS).
- **iSCSI data services network**: Required if PC is hosted on a cluster using iSCSI-based storage (Volume Groups). Not required for standard AHV deployments.
- **DNS**: Forward and reverse DNS records for all PC VMs. PC uses FQDN for cluster registration.
- **NTP**: Synchronized time across PC and all PE clusters (critical for backup replication and Leap DR).
- **Firewall rules**: Port 9440 (HTTPS/API), port 80/443 (LCM updates), port 8443 (MSP/microservices platform). See Nutanix Port Reference for complete list.
- **Bandwidth**: For multi-site with centralized PC, minimum 10 Mbps sustained between PC and remote PE clusters; 100 Mbps recommended for environments with 50+ remote clusters.

## Common Decisions (ADR Triggers)

- **PC sizing tier** -- Small (2,500 VMs) vs Large (7,500 VMs) vs X-Large (25,000 VMs) based on current count, growth, and feature requirements (Flow Virtual Networking forces X-Large)
- **Single-VM vs scale-out** -- Single VM (simpler, lower resource cost) vs 3-VM scale-out (HA, doubled capacity, one-way commitment)
- **Centralized vs distributed PC** -- Single scale-out PC (unified management, WAN-dependent) vs multiple regional PCs (autonomous, operational overhead, requires Nutanix Central for aggregation)
- **PC hosting location** -- Dedicated management cluster (isolation, predictable resources) vs co-hosted on production cluster (fewer clusters to manage, resource contention risk)
- **Backup strategy** -- Continuous-only to PE clusters (simpler, 30-min RPO) vs continuous + point-in-time to S3 (defense-in-depth, ransomware protection, offsite)
- **Calm blueprint management** -- Git-based version control (recommended, survives PC loss) vs PC-only storage (lost if PC is destroyed without separate backup)
- **Category taxonomy** -- Pre-defined enforced taxonomy (consistent, scalable) vs organic growth (flexible, policy drift at scale)

## Reference Links

- [Prism Central sizing guide](https://portal.nutanix.com/page/documents/details?targetId=Prism-Central-Guide:mul-pc-sizing-requirements-pc-r.html) -- VM sizing, scale limits, and deployment recommendations for Prism Central
- [Prism Central administration guide](https://portal.nutanix.com/page/documents/details?targetId=Prism-Central-Guide:Prism-Central-Guide) -- deployment, configuration, and multi-cluster management

## See Also

- `providers/nutanix/infrastructure.md` -- core Nutanix cluster sizing, AHV, and AOS
- `providers/nutanix/platform-services.md` -- Calm, Flow, Objects, Files, NDB
- `providers/nutanix/data-protection.md` -- Leap DR, snapshots, protection domains
- `providers/nutanix/networking.md` -- Flow Virtual Networking, AHV networking
- `providers/nutanix/security.md` -- Flow Network Security, microsegmentation
- `providers/nutanix/observability.md` -- Prism Central monitoring and alerting
