# VMware Cloud Foundation / SDDC Manager

## Scope

This document covers VMware Cloud Foundation (VCF) deployment and lifecycle management via SDDC Manager, including bring-up, workload domain design, upgrade orchestration, certificate management, multi-site strategy, and backup/recovery of the management plane.

## Checklist

- [ ] **[Critical]** Is the physical network pre-configured for VCF bring-up, including management VLAN, vMotion VLAN, vSAN VLAN, and NSX Host Overlay (TEP) VLAN, with MTU 9000 (jumbo frames) confirmed end-to-end on vSAN and TEP VLANs?
- [ ] **[Critical]** Has the Cloud Builder deployment parameter workbook (Excel) been completed with DNS records (forward and reverse), NTP servers, IP pools, credentials, and license keys — and validated with Cloud Builder's pre-check tool before initiating bring-up?
- [ ] **[Critical]** Is the management domain sized correctly with a minimum of 4 ESXi hosts (for vSAN), running vCenter, SDDC Manager, NSX Manager cluster (3 nodes), and VCF management suite (formerly Aria Suite), with sufficient headroom so management workloads do not contend with workload domain resources?
- [ ] **[Critical]** Are SDDC Manager backups configured and scheduled (daily recommended), including database backup, and stored on external storage (NFS/SFTP) separate from the management domain — because SDDC Manager is the single point of truth for the entire VCF instance?
- [ ] **[Critical]** Is the VCF compatibility matrix (kb.vmware.com) checked before any hardware purchase or upgrade to confirm that server model, ESXi version, vSAN version, NSX version, and NIC firmware are all validated for the target VCF release? (verify URL -- VMware documentation consolidated under Broadcom post-acquisition)
- [ ] **[Recommended]** Are workload domains designed with clear separation of concerns — management domain for VMware infrastructure services only, VI workload domains for general compute, and VVS workload domains (with NSX) for workloads requiring microsegmentation?
- [ ] **[Recommended]** Is the SDDC Manager upgrade lifecycle planned with a maintenance window that accounts for sequential component upgrades (vCenter → ESXi → vSAN → NSX) and mandatory pre-check validation, typically requiring 4-8 hours per workload domain?
- [ ] **[Recommended]** Is certificate management strategy decided — SDDC Manager as intermediate CA (simplest), Microsoft AD CS integration (enterprise standard), or external CA with manual certificate replacement — and documented before initial bring-up?
- [ ] **[Recommended]** Are vCenter, NSX Manager, and VCF management suite (formerly Aria Suite) backups coordinated with SDDC Manager backups so that a full restore scenario can recover the entire management domain to a consistent state?
- [ ] **[Recommended]** For VCF 9.0 deployments, is non-vSAN principal storage (external SAN/NAS as primary storage for workload domains) evaluated where independent compute and storage scaling is required?
- [ ] **[Recommended]** Is host commissioning/decommissioning handled exclusively through SDDC Manager (not directly in vCenter) to maintain SDDC Manager's inventory consistency and prevent drift between SDDC Manager state and actual infrastructure?
- [ ] **[Recommended]** Has multi-site strategy been decided: VCF stretched clusters (vSAN stretched + NSX multi-site, requires witness host and <5ms RTT between sites) vs separate VCF instances per site with Enhanced Linked Mode (operationally simpler, allows independent upgrades)?
- [ ] **[Optional]** Is SDDC Manager API integration planned for infrastructure-as-code workflows (Terraform, Ansible), using the documented REST API for workload domain creation, cluster expansion, and lifecycle operations?
- [ ] **[Optional]** Is Cloud Builder VM retained post-deployment for future management domain rebuilds, or is the deployment parameter workbook archived securely so a fresh Cloud Builder can recreate the environment if needed?
- [ ] **[Optional]** Are SDDC Manager user accounts integrated with Active Directory (via vCenter SSO) with role-based access, rather than relying on the default local admin account for day-to-day operations?

## Why This Matters

VMware Cloud Foundation is Broadcom's prescribed architecture for deploying the full VMware stack. VCF 9.0 unifies all component version numbers to 9.x (vSphere 9, ESXi 9, vSAN 9, NSX 9) and renames all Aria products to VCF-prefixed names. VCF 9.0 also introduces support for non-vSAN principal storage, allowing external SAN/NAS arrays as the primary storage for workload domains -- a significant change from earlier VCF versions that required vSAN. SDDC Manager acts as the lifecycle and configuration authority — it controls which ESXi, vCenter, NSX, and vSAN versions run together, enforces validated upgrade paths, and prevents unsupported component combinations that would void support. This is fundamentally different from manually deploying vSphere components, where an administrator can mix any versions and configurations. In VCF, SDDC Manager "owns" the infrastructure: hosts must be commissioned through it, workload domains must be created through it, and upgrades must be orchestrated through it. Bypassing SDDC Manager (e.g., upgrading ESXi directly via vLCM) causes inventory drift that can break future lifecycle operations and may void support entitlements. The Cloud Builder initial bring-up process is a one-shot automated deployment that configures the management domain from bare-metal hosts. If the deployment parameter workbook has errors (wrong VLANs, bad DNS records, incorrect IP ranges), the bring-up will fail partway through and may require a complete restart including re-imaging hosts. The management domain is the control plane for the entire VCF instance — if SDDC Manager or the management vCenter is lost without backup, recovering the environment requires Broadcom support engagement and potentially a full rebuild. VCF stretched clusters provide site resilience but introduce significant complexity (witness host management, network latency requirements, asymmetric storage performance) that many organizations underestimate.

## Common Decisions (ADR Triggers)

- **VCF vs manual vSphere deployment** — VCF for validated, opinionated full-stack deployment with lifecycle management (required for Broadcom support on bundled components) vs manual deployment for maximum flexibility and simpler environments that only need vSphere/vCenter without vSAN or NSX
- **Management domain sizing: 4 hosts vs 5+ hosts** — 4 hosts is the minimum for vSAN but leaves little headroom for management workload growth (VCF management suite, Tanzu Supervisor); 5+ hosts provides N+1 availability and capacity for adding VCF Operations, VCF Automation, and Tanzu services
- **vSAN vs non-vSAN principal storage (VCF 9.0+)** — vSAN for hyperconverged simplicity and tight VCF integration vs external SAN/NAS principal storage for independent compute/storage scaling, existing array investments, and specialized storage features; non-vSAN principal storage is newly supported in VCF 9.0
- **Workload domain strategy: few large vs many small** — fewer large workload domains (multiple clusters per domain) simplifies management and NSX configuration vs many small domains provides stronger tenant isolation and independent upgrade schedules; regulatory requirements may mandate separate domains
- **Stretched cluster vs separate VCF instances** — stretched clusters for active-active workload placement with automatic failover (requires <5ms RTT, dedicated witness host, uniform network config) vs separate instances for independent lifecycle management, different hardware generations, or sites with >5ms latency
- **SDDC Manager CA vs external enterprise CA** — SDDC Manager CA for simplest certificate management (auto-renewal, no external dependencies) vs Microsoft AD CS or external CA integration for organizations with mandatory PKI policies; external CA adds operational overhead for certificate renewal coordination
- **Upgrade cadence: every release vs LTS** — upgrading every VCF release for latest features and security patches vs waiting for Long-Term Support releases for stability; VCF upgrade paths sometimes require stepping through intermediate versions, making deferred upgrades more time-consuming. Note: VCF jumped from 5.x to 9.0 (no 6.x/7.x/8.x); verify supported upgrade paths from your current version.
- **Cloud Builder retention vs archive** — retaining Cloud Builder VM consumes resources but enables rapid redeployment vs archiving the workbook and deploying fresh Cloud Builder only when needed; environments with frequent management domain changes benefit from keeping Cloud Builder available

## Reference Architectures

### VCF Management Domain — Standard Deployment
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Management Domain (4-host min)                    │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ ESXi-01  │  │ ESXi-02  │  │ ESXi-03  │  │ ESXi-04  │            │
│  │          │  │          │  │          │  │          │            │
│  │ vCenter  │  │ NSX Mgr  │  │ NSX Mgr  │  │ NSX Mgr  │            │
│  │ SDDC Mgr │  │ Node-1   │  │ Node-2   │  │ Node-3   │            │
│  │ VCF Ops  │  │ VCF Logs │  │ VCF Auto │  │          │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
│                                                                     │
│  vSAN Datastore (management)     NSX Overlay (management)           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│               Workload Domain "Production" (4+ hosts)               │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ ESXi-05  │  │ ESXi-06  │  │ ESXi-07  │  │ ESXi-08  │            │
│  │ Tenant   │  │ Tenant   │  │ Tenant   │  │ Tenant   │            │
│  │ VMs      │  │ VMs      │  │ VMs      │  │ VMs      │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
│                                                                     │
│  vSAN Datastore (workload)       NSX Overlay (workload)             │
└─────────────────────────────────────────────────────────────────────┘
```

### VCF Bring-Up Process Flow
```
Phase 1: Physical Prep
  ├── Rack and cable servers (management + ToR switches)
  ├── Configure ToR switches: VLANs (mgmt, vMotion, vSAN, TEP)
  ├── Verify MTU 9000 end-to-end on vSAN and TEP VLANs
  ├── Configure DNS records (forward + reverse) for all components
  └── Configure NTP accessible from management VLAN

Phase 2: Cloud Builder
  ├── Deploy Cloud Builder OVA on a temporary network or management VLAN
  ├── Complete deployment parameter workbook (Excel)
  │     ├── Management network: IPs, VLANs, gateway, DNS, NTP
  │     ├── ESXi host credentials and IP assignments
  │     ├── vCenter, NSX, SDDC Manager names and IPs
  │     ├── License keys (VCF, vSAN, NSX)
  │     └── vSAN configuration (disk groups, storage policy)
  ├── Run Cloud Builder validation (pre-check)
  └── Initiate bring-up (2-4 hours automated)

Phase 3: Post-Bring-Up
  ├── Verify management domain health in SDDC Manager
  ├── Configure SDDC Manager backup (NFS/SFTP target)
  ├── Commission additional hosts for workload domains
  ├── Create workload domains via SDDC Manager UI or API
  └── Deploy VCF management suite (VCF Operations, VCF Operations for Logs, VCF Automation) if licensed
```

### VCF Upgrade Lifecycle (SDDC Manager Orchestrated)
```
┌─────────────────────────────────────────────────────────────────┐
│                  SDDC Manager Upgrade Workflow                   │
│                                                                 │
│  1. Download bundle ──→ 2. Pre-check ──→ 3. Stage update       │
│                                                                 │
│  Upgrade Order (sequential, per domain):                        │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │
│  │ SDDC    │──→│ vCenter │──→│  NSX    │──→│  ESXi   │       │
│  │ Manager │   │ Server  │   │ Manager │   │ (rolling)│       │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘       │
│                                                                 │
│  Management domain first ──→ then each workload domain          │
│                                                                 │
│  Rollback: snapshot-based for vCenter/NSX; ESXi rollback        │
│  requires manual intervention; vSAN on-disk format upgrades     │
│  are NOT reversible                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Site VCF — Stretched Cluster vs Separate Instances
```
Option A: Stretched Cluster (active-active)
┌──────────────┐    <5ms RTT    ┌──────────────┐
│   Site A      │◄─────────────►│   Site B      │
│   ESXi hosts  │               │   ESXi hosts  │
│   vSAN data   │               │   vSAN data   │
│   (preferred) │               │   (secondary) │
└──────────────┘               └──────────────┘
        │                              │
        └──────────┬───────────────────┘
                   │
           ┌───────────────┐
           │  Witness Host  │
           │  (Site C)      │
           └───────────────┘
Requires: uniform network, witness host, <5ms latency,
identical hardware across sites

Option B: Separate VCF Instances
┌──────────────────┐          ┌──────────────────┐
│  VCF Instance 1   │          │  VCF Instance 2   │
│  Site A            │          │  Site B            │
│  ┌──────────────┐ │          │ ┌──────────────┐  │
│  │ SDDC Manager │ │   ELM    │ │ SDDC Manager │  │
│  │ vCenter      │◄├─────────►┤ │ vCenter      │  │
│  │ NSX Manager  │ │          │ │ NSX Manager  │  │
│  └──────────────┘ │          │ └──────────────┘  │
└──────────────────┘          └──────────────────┘
Allows: independent upgrades, different hardware,
higher latency tolerance, simpler operations
```

## Reference Links

- [VMware Cloud Foundation documentation](https://docs.vmware.com/en/VMware-Cloud-Foundation/index.html) -- VCF deployment, SDDC Manager, workload domains, and lifecycle management
- [VCF planning and preparation guide](https://docs.vmware.com/en/VMware-Cloud-Foundation/5.2/vcf-planning/GUID-C4974C6F-B2D4-4E21-8B77-FE6D3F51622D.html) -- Cloud Builder prerequisites, parameter workbook, and network requirements
- [VCF operations and administration](https://docs.vmware.com/en/VMware-Cloud-Foundation/5.2/vcf-operations/GUID-B3B1B522-A2A8-4705-A85E-3A5E9C5E7B1A.html) -- SDDC Manager backup, certificate management, and upgrade orchestration

## See Also

- `providers/vmware/infrastructure.md` -- VMware infrastructure overview
- `providers/vmware/licensing.md` -- VCF edition selection and licensing
- `providers/vmware/networking.md` -- NSX deployment within VCF workload domains
- `providers/vmware/storage.md` -- vSAN configuration in VCF
