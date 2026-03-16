# Physical Server Scope Assessment

## Scope

This file covers **handling physical (bare-metal) servers in virtualization and migration projects**: P2V assessment, workloads that must remain physical, storage and network appliance scope boundaries, bare-metal database server decisions, GPU/HPC server handling, and asset disposition planning. For virtual machine migration, see `general/workload-migration.md`. For facility lifecycle and decommission, see `general/facility-lifecycle.md`. For inventory analysis, see `general/inventory-analysis.md`.

## Checklist

- [ ] **[Critical]** Complete physical server inventory compiled: hostname, role, make/model, serial number, location (rack/row/datacenter), age, and current workload
- [ ] **[Critical]** Each server classified by disposition: retain physical, P2V (physical to virtual), P2C (physical to cloud), or decommission
- [ ] **[Critical]** Workloads that must remain physical identified with documented justification (hardware dongles, licensing restrictions, performance requirements, regulatory mandates)
- [ ] **[Critical]** Storage appliances inventoried: NAS/SAN systems (NetApp, Dell EMC, Pure Storage, HPE Nimble), capacity utilization, protocol exposure (NFS, iSCSI, FC), and migration path defined
- [ ] **[Critical]** Network appliances inventoried: physical firewalls, switches, load balancers, WAN optimizers, and IDS/IPS devices with roles and replacement strategy documented
- [ ] **[Critical]** Bare-metal database servers assessed for virtualization candidacy based on IOPS requirements, licensing model, and latency sensitivity
- [ ] **[Critical]** Warranty and support contract expiration dates cataloged for all physical assets; contracts aligned with migration timeline
- [ ] **[Recommended]** P2V candidate assessment performed: CPU utilization, memory usage, disk I/O profile, and network throughput measured over 30+ days to right-size target VMs
- [ ] **[Recommended]** GPU/HPC servers inventoried with workload classification (ML training, inference, rendering, simulation) and target platform identified (cloud GPU instances, on-prem GPU virtualization, retain physical)
- [ ] **[Recommended]** Legacy OS instances identified: out-of-support operating systems (Windows Server 2008/2012, RHEL 5/6, Solaris, AIX) with driver dependencies and upgrade/replacement path documented
- [ ] **[Recommended]** Physical server decommission timeline created with dependency mapping (DNS records, certificates, monitoring integrations, backup jobs, scheduled tasks)
- [ ] **[Recommended]** Rack and power impact analysis completed: power draw and rack unit consumption of retained physical servers vs freed capacity from decommissioned servers
- [ ] **[Recommended]** Asset tracking and disposal procedures defined: ITAD vendor selected, chain of custody documented, certificate of destruction required for storage media
- [ ] **[Optional]** P2C assessment performed as alternative to P2V for workloads that benefit from cloud-native services (managed databases, GPU-as-a-service, managed file storage)
- [ ] **[Optional]** Physical server consolidation opportunities identified: underutilized servers that can be combined before or instead of virtualization
- [ ] **[Optional]** Colocation contract terms reviewed for retained physical servers: power, space, cross-connect costs, and contract renewal alignment with migration timeline

## Why This Matters

Physical server scope determines the boundary of every infrastructure project. Without a complete inventory and clear disposition for each server, migrations stall, budgets overrun, and orphaned hardware accumulates ongoing costs. A server left out of the initial assessment will surface later as an emergency, forcing reactive decisions instead of planned ones.

The decision to retain, virtualize, or migrate each physical server has cascading effects. A bare-metal database server running Oracle with per-socket licensing may cost significantly more when virtualized on a multi-socket host due to licensing rules that require licensing every core in the cluster. A server with a USB hardware dongle for a legacy application cannot be virtualized without a network-attached dongle solution. A storage appliance with hundreds of terabytes of data on Fibre Channel cannot be replaced overnight -- it needs a parallel-run migration measured in weeks or months.

Physical server decommissioning is not just an IT task. It involves asset management, financial depreciation schedules, lease returns, secure data destruction with auditable chain of custody, and environmental disposal compliance. Servers that are powered off but not formally decommissioned continue to incur rack space, power reservation, and asset tracking costs. Organizations that skip formal disposal procedures risk data breaches from improperly wiped storage media.

Warranty and support contract alignment prevents paying for support on servers scheduled for decommission, or worse, running production workloads on servers with expired warranties and no spare parts availability.

## Common Decisions (ADR Triggers)

### ADR: P2V vs P2C vs Retain Physical
**Trigger:** Determining the disposition of each physical server during infrastructure assessment.
**Considerations:**
- **P2V (Physical to Virtual):** Best for general-purpose workloads (application servers, web servers, file servers) with moderate resource requirements. Tools like VMware vCenter Converter, Veeam, or Carbonite perform live or offline conversions. Right-size the target VM based on actual utilization, not original physical specs.
- **P2C (Physical to Cloud):** Best when the workload benefits from managed services (RDS instead of self-managed database), elastic scaling, or geographic distribution. AWS Application Migration Service (MGN), Azure Migrate, and Google Migrate for Compute Engine support lift-and-shift. Consider refactoring to cloud-native services instead of just re-hosting.
- **Retain Physical:** Required when hardware dependencies exist (dongles, FPGA cards, specialized NICs), when licensing prohibits virtualization (some per-socket licenses), when bare-metal performance is non-negotiable (ultra-low-latency trading, real-time systems), or when regulatory requirements mandate physical isolation.
- Document the justification for every "retain physical" decision. This list should be short and shrink over time.

### ADR: Storage Appliance Migration Strategy
**Trigger:** NAS/SAN appliances (NetApp, Dell EMC, Pure Storage) exist in the environment and must be accounted for.
**Considerations:**
- **Migrate data off the appliance:** Move data to software-defined storage (Ceph, MinIO), cloud storage (S3, EFS, Azure Files), or virtual storage appliances. Requires parallel-run period for validation. Best for reducing vendor lock-in and hardware costs.
- **Replace with newer appliance:** Vendor-supported upgrade path (NetApp ONTAP migration, EMC data mobility). Keeps the operational model intact but continues hardware dependency and support contract costs.
- **Retain existing appliance:** Acceptable when the appliance is under warranty, utilization is high, and migration risk outweighs benefit. Must have a documented end-of-life plan.
- Fibre Channel SAN environments require special attention: FC switch zoning, HBA compatibility, and multipath configuration must be mapped before any changes.
- Data migration duration depends on dataset size and available bandwidth. Budget 1-2 TB per hour over 10GbE for bulk migration; less for random-access workloads.

### ADR: Network Appliance Replacement vs Retain
**Trigger:** Physical network appliances (firewalls, load balancers, switches) must be assessed for the target architecture.
**Considerations:**
- **Replace with virtual/cloud-native:** Physical firewalls (Palo Alto, Fortinet, Cisco ASA) can often be replaced with virtual appliances (VM-Series, FortiGate-VM) or cloud-native security groups and WAF. Physical load balancers (F5 BIG-IP, Citrix ADC) can be replaced with software load balancers (HAProxy, NGINX, cloud ALB/NLB).
- **Retain physical:** Required when throughput exceeds virtual appliance capacity (40Gbps+ firewall throughput), when hardware-accelerated SSL offload is critical, or when the appliance provides connectivity that cannot be replicated virtually (WAN links, MPLS termination, physical network segmentation).
- **Hybrid approach:** Keep physical switches and routers for underlay network, virtualize overlay services (firewalls, load balancers). Common in on-prem virtualization and private cloud deployments.
- Top-of-rack switches are almost always retained as physical devices. Spine/leaf fabric is physical infrastructure regardless of compute virtualization.

### ADR: Bare-Metal Database Server Disposition
**Trigger:** Production database servers running on dedicated physical hardware must be assessed.
**Considerations:**
- **Virtualize:** Acceptable for most databases when the VM is properly sized and storage provides sufficient IOPS. Pin vCPUs, use huge pages, and assign dedicated NVMe-backed storage. Works well for PostgreSQL, MySQL, SQL Server Standard Edition.
- **Migrate to managed service:** Cloud-managed databases (RDS, Cloud SQL, Azure SQL) eliminate OS and engine patching burden. Best for standard configurations without exotic extensions or custom patches.
- **Retain physical:** Consider when database licensing penalizes virtualization (Oracle Database licensing on VMware requires licensing all cores in the cluster unless using Oracle VM or hard partitioning with approved technologies), when sub-millisecond latency is required (high-frequency trading), or when dataset size makes migration windows impractical.
- Measure actual IOPS, query latency, and connection count under peak load before deciding. A database that uses 10% of a 96-core server is a clear virtualization candidate regardless of the DBA team's objections.

### ADR: GPU/HPC Server Strategy
**Trigger:** Physical servers with GPUs or specialized HPC hardware exist in the environment.
**Considerations:**
- **Retain physical with GPU passthrough:** Use PCI passthrough (VFIO) to assign physical GPUs to VMs while virtualizing the rest of the server. Requires IOMMU support and careful NUMA alignment. Works for dedicated ML training workloads.
- **Migrate to cloud GPU instances:** AWS P4d/P5 (A100/H100), Azure NDv5 (H100), GCP A3 (H100) provide on-demand GPU capacity without hardware ownership. Best for burst training workloads and organizations without GPU operations expertise.
- **Retain as bare-metal:** Required for multi-GPU training jobs that need NVLink/NVSwitch interconnect bandwidth, or when custom CUDA kernels depend on specific driver versions and hardware configurations.
- GPU server power consumption is significant (2-4 kW per server with 4-8 GPUs). Factor this into rack power and cooling assessments.

### ADR: Legacy OS Physical Server Handling
**Trigger:** Servers running end-of-life or out-of-support operating systems on physical hardware.
**Considerations:**
- **Upgrade OS then virtualize:** Preferred path. Upgrade to a supported OS version, validate application compatibility, then P2V. Eliminates both the legacy OS risk and the physical hardware dependency.
- **P2V as-is with extended support:** Virtualize the legacy OS without upgrading. Purchase extended security updates (ESU) where available (Windows Server 2012 R2 ESU, RHEL ELS). Buys time but does not eliminate the technical debt.
- **Encapsulate and isolate:** For applications that cannot be upgraded or migrated, P2V the server, place it on an isolated network segment, and add compensating security controls (host-based firewall, application-layer gateway). Document the risk acceptance.
- **Rewrite or replace the application:** The most thorough solution but also the most expensive and time-consuming. Requires business case justification.
- Physical drivers are the most common blocker for P2V of legacy OS. Windows Server 2003 and earlier may not have drivers for modern virtual hardware. Use legacy virtual hardware profiles (IDE instead of virtio, e1000 instead of virtio-net) as a workaround.

### ADR: Decommission and Asset Disposal Process
**Trigger:** Physical servers are identified for decommission as workloads migrate.
**Considerations:**
- **ITAD vendor selection:** Choose a certified IT Asset Disposition vendor (R2, e-Stewards, NAID AAA certified) for secure hardware disposal. Require certificate of destruction for all storage media (HDDs, SSDs, NVMe drives).
- **Data sanitization method:** NIST 800-88 guidelines define Clear, Purge, and Destroy. SSDs and NVMe require cryptographic erase (not just overwrite). Physical destruction (shredding) is required for highest-sensitivity data.
- **Timeline coordination:** Servers cannot be decommissioned until all workloads are migrated, DNS records updated, monitoring removed, backup retention periods expired, and a rollback window has passed (typically 30-90 days post-migration).
- **Financial impact:** Decommissioned servers reduce power, cooling, rack space, and support contract costs. Quantify these savings to build the business case for migration. Leased equipment has return deadlines with penalties for late return.
- **Environmental compliance:** WEEE (EU), state e-waste laws (US), and organizational sustainability policies may dictate disposal methods. Document compliance for audit.

## P2V Assessment Methodology

### Performance Data Collection

Before converting any physical server to a virtual machine, collect at least 30 days of performance data:

| Metric | Tool | What to Look For |
|--------|------|-----------------|
| CPU utilization | Performance Monitor, sar, top | Average and peak utilization; sustained peaks > 70% may need larger VM |
| Memory usage | Performance Monitor, free, vmstat | Working set size vs installed RAM; right-size VM to working set + 20% |
| Disk I/O (IOPS) | iostat, perfmon, fio | Peak IOPS determines storage tier on target platform |
| Disk throughput (MB/s) | iostat, perfmon | Sustained throughput for backup, batch, and ETL workloads |
| Network throughput | netstat, iftop, perfmon | Peak bandwidth determines NIC type and count on VM |
| Process list | ps, tasklist, Process Monitor | Identify all running services for post-migration validation |

### Right-Sizing During P2V

Physical servers are almost always over-provisioned relative to their actual usage. P2V is an opportunity to right-size:

```
Physical Server                    Virtual Machine (right-sized)
  32 cores (8% avg utilization)  →   8 vCPU (32% avg utilization)
  128 GB RAM (40 GB used)        →   48 GB RAM (83% utilized)
  2 TB disk (600 GB consumed)    →   800 GB disk (75% utilized)
  4x 1GbE NIC (1 active)        →   1x vmxnet3/virtio NIC

Result: 75% reduction in compute allocation
        62% reduction in memory allocation
        60% reduction in storage allocation
```

**Caution:** Do not right-size so aggressively that peak workloads suffer. Use P95 or P99 peaks, not averages, for sizing. Include headroom for growth (typically 20-30%).

## Scope Boundary Definitions

### What Is In Scope for a Virtualization Project

| Category | In Scope | Out of Scope |
|----------|----------|-------------|
| **Application servers** | Web, app, middleware, batch processing | Only if general-purpose x86 workloads |
| **Database servers** | SQL, NoSQL, data warehouse (with licensing review) | Mainframe databases, proprietary platforms |
| **File servers** | Windows file shares, NFS exports, FTP | Dedicated NAS/SAN appliances (assessed separately) |
| **Infrastructure servers** | DNS, DHCP, AD, NTP, monitoring | These are typically already virtual |
| **Storage appliances** | Assessed but migration path separate | Controller-level migration is vendor-specific |
| **Network appliances** | Assessed but replacement path separate | Physical switches, routers are infrastructure |
| **Development servers** | All dev/test physical servers | Unless hardware-dependent development |
| **Legacy/specialty** | Assessed case-by-case | Mainframes, midrange (AS/400, AIX) |

### Establishing Scope Early

Document what is and is not in scope at the project kickoff:

1. **Enumerate all physical assets** -- every server, appliance, and device in every rack
2. **Classify each asset** -- compute (candidate for P2V/P2C), storage (separate workstream), network (separate workstream), or out-of-scope (mainframe, specialty)
3. **Get stakeholder agreement** -- before planning begins, confirm the scope boundary with all stakeholders
4. **Track scope changes** -- any additions to scope after kickoff must go through change control with timeline and budget impact assessment

## Warranty and Support Contract Management

### Alignment with Migration Timeline

```
Server A: Warranty expires March 2026
Server B: Warranty expires September 2027
Server C: Warranty expires December 2025 (EXPIRED)

Migration planned: Q2-Q4 2026

Server A: Must migrate before March 2026 or extend warranty
Server B: Safe -- warranty covers the migration period
Server C: Risk -- no vendor support if hardware fails during migration prep
```

### Support Contract Optimization

- **Do not renew support contracts** for servers scheduled for decommission within the contract period
- **Extend support contracts** for servers that must remain operational past the current expiry but before migration completes
- **Negotiate short-term extensions** (month-to-month or quarterly) instead of annual renewals when migration is imminent
- **Maintain spare parts** for servers without active support contracts but still in production -- at minimum, keep spare disks, power supplies, and DIMMs

## Rack and Power Analysis

### Calculating Physical Impact

For each rack containing physical servers, document:

| Attribute | How to Measure | Migration Impact |
|-----------|---------------|-----------------|
| Rack units used | Count U height of each device | Freed U space can accommodate target hardware or be released to colo |
| Power draw (actual) | PDU metering, UPS load reports | Freed power capacity reduces utility costs |
| Power draw (rated) | Server spec sheets | Worst-case for capacity planning |
| Cooling load | Approximate from power draw (1 kW = 3,412 BTU/hr) | Reduced cooling load may allow facility changes |
| Network ports consumed | Patch panel and switch audit | Freed ports may be needed for target environment |
| Cross-connects | Facility records | May need to be maintained, relocated, or terminated |

### Retained Physical Footprint Planning

After migration, some physical servers will remain. Plan for the retained footprint:

- Can retained servers be consolidated into fewer racks? (reduces colo cost)
- Are retained servers co-located with the new virtual infrastructure? (simplifies management)
- Is the remaining power and cooling adequate for the retained servers? (do not leave servers on overloaded circuits after other servers are removed)
- Update facility documentation to reflect the new layout

## See Also

- `general/workload-migration.md` -- Migration strategy, wave planning, cutover procedures
- `general/inventory-analysis.md` -- Inventory analysis methodology
- `general/facility-lifecycle.md` -- Facility decommission and handback
- `general/colocation-constraints.md` -- Physical facility constraints for migrations
- `general/hardware-sizing.md` -- Target environment capacity planning
