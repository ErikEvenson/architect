# VDI Migration Strategy

## Scope

This file covers **VDI platform migration**: decision frameworks for moving between hypervisors and broker platforms, cloud VDI alternatives, image and profile migration, GPU considerations, licensing, and performance validation. For general workload migration (6 Rs, wave planning), see `general/workload-migration.md`. For compute sizing, see `general/hardware-sizing.md`.

## Checklist

### Platform Decision

- [ ] **[Critical]** Has a decision tree been applied? (re-platform on new hypervisor vs cloud VDI vs hybrid)
- [ ] **[Critical]** Are current VDI workload profiles documented? (user types, session counts, resource consumption per persona)
- [ ] **[Critical]** Has the target connection broker been selected? (Omnissa Horizon, Citrix CVAD, Azure Virtual Desktop, Windows 365, Dizzion Frame)
- [ ] **[Recommended]** Is a hybrid VDI architecture evaluated? (on-prem for persistent power users, cloud for task workers and burst)
- [ ] **[Optional]** Has a multi-broker strategy been considered? (Citrix for on-prem, AVD for cloud — common in phased migrations)

### Hypervisor and Broker Compatibility

- [ ] **[Critical]** Is the target hypervisor supported by the chosen broker? (Horizon on AHV requires 2512+, Citrix on AHV requires Prism Central plugin)
- [ ] **[Critical]** Are vGPU/GPU passthrough requirements validated on the target hypervisor? (NVIDIA vGPU driver support varies by hypervisor)
- [ ] **[Recommended]** Has the connection broker version matrix been checked against the target hypervisor version?
- [ ] **[Recommended]** Are published application requirements validated? (RDSH farms, App Volumes, App Layering support on target platform)

### Image and Profile Migration

- [ ] **[Critical]** Is the desktop image strategy defined for the target platform? (MCS, PVS, linked clones, full clones, Redirect-on-Write)
- [ ] **[Critical]** Is user profile migration planned? (FSLogix, Omnissa DEM, Citrix UPM — container format compatibility)
- [ ] **[Recommended]** Are application layers portable? (Citrix App Layering, Omnissa App Volumes — may require rebuild on new hypervisor)
- [ ] **[Recommended]** Is print and peripheral redirection tested on the target platform? (USB redirection, printer mapping, scanner support)

### Performance and Licensing

- [ ] **[Critical]** Are performance baselines captured before migration? (Login VSI, Lakeside SysTrack, ControlUp)
- [ ] **[Critical]** Are licensing implications mapped? (Windows VDA, RDS CALs, Horizon subscription, Citrix Universal, Microsoft 365 E3/E5 for AVD)
- [ ] **[Recommended]** Is a proof of concept planned with representative user personas? (minimum 2-week pilot per persona)
- [ ] **[Optional]** Has hardware BOM impact been assessed? (cloud VDI eliminates on-prem compute; on-prem VDI may require new GPU hosts)

## Why This Matters

VDI migrations are high-visibility, high-disruption projects. Unlike server workloads, VDI directly affects every end user's daily experience. A poorly executed VDI migration creates immediate, visible productivity loss — login storms, profile corruption, broken printers, and degraded graphics performance.

The VDI landscape shifted significantly after Broadcom's acquisition of VMware. Organizations previously locked into VMware vSphere + Horizon are now evaluating alternatives due to licensing changes, and the market has responded: Omnissa Horizon now runs on Nutanix AHV (GA as of Horizon 2512, late 2025), Citrix has deepened AHV integration via Prism Central, and Microsoft has expanded Azure Virtual Desktop and Windows 365 capabilities. The result is that organizations have more platform choices than ever, but the migration paths between them are complex.

## Decision Tree: VDI Platform Strategy

```
Current VDI Platform
    |
    ├── Happy with broker, unhappy with hypervisor?
    |       |
    |       ├── Horizon shop → Re-platform Horizon on AHV (2512+) or Hyper-V
    |       ├── Citrix shop → Re-platform Citrix on AHV or Hyper-V (hypervisor-agnostic)
    |       └── Need to shed VMware entirely → Evaluate broker change too
    |
    ├── Happy with hypervisor, unhappy with broker?
    |       |
    |       ├── Want cloud-native → Azure Virtual Desktop or Windows 365
    |       ├── Want on-prem control → Citrix CVAD (broadest hypervisor support)
    |       └── Want DaaS simplicity → Dizzion Frame or Windows 365
    |
    ├── Unhappy with both?
    |       |
    |       ├── Cloud-first strategy → AVD (multi-session) + Windows 365 (dedicated)
    |       ├── Hybrid strategy → Citrix on AHV (on-prem) + Citrix DaaS (cloud)
    |       └── Simplification → Windows 365 (eliminates infrastructure management)
    |
    └── Staying put but need burst/DR?
            |
            ├── Horizon on-prem + Horizon Cloud → Hybrid Horizon
            ├── Citrix on-prem + Citrix DaaS on Azure → Hybrid Citrix
            └── On-prem VDI + AVD for burst → Hybrid multi-broker
```

### Key Selection Factors

| Factor | Horizon | Citrix CVAD | AVD | Windows 365 |
|--------|---------|-------------|-----|-------------|
| **Hypervisor flexibility** | vSphere, AHV (2512+) | vSphere, AHV, Hyper-V, cloud | Azure only | Azure only (SaaS) |
| **Multi-session Windows** | Yes (RDSH) | Yes (RDSH + multi-session W10/11) | Yes (native) | No (dedicated) |
| **GPU support** | Strong (vGPU, passthrough) | Strong (vGPU, passthrough) | NVxx series VMs | GPU SKUs available |
| **Management complexity** | Medium-High | High | Medium | Low |
| **On-prem deployment** | Yes | Yes | No | No |
| **Per-user cost model** | Subscription | Universal subscription | Consumption-based | Per-user fixed |
| **Best for** | Existing Horizon shops, AHV migration | Multi-hypervisor, complex enterprise | Azure-first orgs, multi-session | Simple deployments, <300 users |

## Omnissa Horizon on Non-VMware Hypervisors

### Horizon on Nutanix AHV (GA: Horizon 2512, December 2025)

Omnissa Horizon 8 version 2512 achieved General Availability on Nutanix AHV, making AHV a first-class platform for production Horizon environments.

**Supported capabilities:**
- Automated provisioning via Prism Central
- Desktop pools and RDSH farms
- Power management policies
- vGPU support for GPU-accelerated desktops
- App Volumes and DEM integration
- FIPS mode for compliance environments
- Cloud Pod Architecture for multi-site
- Redirect-on-Write (RoW) cloning (replaces linked clones)
- AHV-native Unified Access Gateway (UAG) appliance
- Horizon on AHV in Nutanix NC2 (hybrid cloud)

**Limitations and considerations:**
- Requires Horizon 2512 or later — earlier versions do not support AHV
- Linked clone workflows replaced by Redirect-on-Write recovery points
- Instant clone support status must be verified per release
- No vSphere-specific features (vSAN integration, vMotion-aware operations)
- Existing vSphere-based Horizon pools cannot be live-migrated to AHV — requires new pool creation

### Horizon on Hyper-V

- Limited support historically; not a primary platform for Horizon
- Check current Omnissa compatibility matrix for supported Hyper-V versions

## Citrix on Nutanix AHV

Citrix Virtual Apps and Desktops has mature AHV support, deepened in 2025 with Prism Central integration.

**Current status (CVAD 2507 LTSR CU1+):**
- Native host connection to Nutanix AHV via Prism Central (no separate plugin install on Cloud Connectors)
- MCS provisioning on AHV (machine catalogs with power-managed and MCS-provisioned VDAs)
- MCS master VM sharing across AHV clusters via template versioning
- Simplified certificate trust on host connection
- Multi-cluster support through single Prism Central connection

**Requirements:**
- Prism Central version pc.2024.3 or later (up to pc.7.3.x)
- AOS version 6.10 or later
- AHV clusters registered to Prism Central

**Advantages over Horizon on AHV:**
- Longer track record on AHV (years of production deployments vs Horizon GA in late 2025)
- Hypervisor-agnostic architecture — same broker manages vSphere, AHV, Hyper-V, and cloud
- MCS and PVS both supported (PVS requires network boot support validation)
- NetScaler VPX supported on AHV for gateway/load balancing

## Nutanix Frame / Dizzion Frame

Nutanix sold its Frame DaaS business to Dizzion (via LLR Partners) in June 2023. Frame is no longer a Nutanix product.

**Current status:**
- Dizzion Frame operates as an independent DaaS platform
- Recognized as a Visionary in 2024 Gartner Magic Quadrant for DaaS
- Continues to support Nutanix infrastructure as a deployment target
- Joint Nutanix + Dizzion Frame deployments available for hybrid multicloud DaaS

**When to consider Dizzion Frame:**
- Organization wants fully managed DaaS without broker infrastructure management
- Nutanix HCI is already the infrastructure standard
- Desire for multi-cloud DaaS (Frame supports multiple cloud backends)

**When to avoid:**
- Need for deep on-prem broker customization
- Existing heavy investment in Citrix or Horizon skill sets
- Requirements for published application farms (evaluate current Frame capabilities)

## Azure Virtual Desktop (AVD)

**Architecture:**
- Control plane managed by Microsoft (no infrastructure to deploy for brokering)
- Session hosts run as Azure VMs (customer-managed or autoscaled)
- Multi-session Windows 10/11 Enterprise (unique to AVD — not available on-prem)
- FSLogix profile containers on Azure Files or Azure NetApp Files

**Best fit:**
- Microsoft 365 E3/E5 licensed organizations (AVD entitlement included)
- Multi-session pooled desktops for task workers
- Organizations consolidating on Azure
- Remote/hybrid workforce without on-prem data center dependency

**Limitations:**
- Azure-only — no on-prem or multi-cloud deployment
- Limited GPU VM availability in some regions
- Network latency to Azure region matters for user experience
- No offline/disconnected mode

## Windows 365

**Architecture:**
- Fully managed Cloud PC — Microsoft manages infrastructure, patching, scaling
- Dedicated VM per user (no multi-session)
- Fixed monthly per-user pricing (predictable cost)
- Managed via Microsoft Intune

**Best fit:**
- Small-to-medium deployments (<300 users)
- Organizations wanting zero VDI infrastructure management
- Predictable budgeting requirements
- Users needing a persistent, personal desktop in the cloud

**Limitations:**
- No multi-session — higher per-user cost at scale
- Limited customization compared to AVD, Citrix, or Horizon
- GPU SKUs available but limited
- No on-prem option

## GPU and vGPU Requirements

### Hypervisor Support Matrix

| GPU Feature | vSphere | AHV | Hyper-V | Azure |
|-------------|---------|-----|---------|-------|
| **NVIDIA vGPU (GRID)** | Full support | Supported (AOS 6.x+) | Supported (DDA + vGPU) | NVxx series VMs |
| **GPU passthrough** | Yes | Yes | Discrete Device Assignment | N/A (managed) |
| **AMD MxGPU (SR-IOV)** | Limited | Check vendor support | Supported | N/A |
| **Intel Data Center GPU Flex** | Yes | Check vendor support | Yes | N/A |
| **vGPU profiles (time-sliced)** | Full range | Supported | Supported | Predefined SKUs |

### Migration Considerations

- NVIDIA vGPU licensing is hypervisor-independent — licenses transfer to new platform
- vGPU manager version must match hypervisor — reinstall required on platform change
- GPU host hardware may need replacement if moving hypervisors (driver/firmware compatibility)
- Azure GPU VMs (NVadsA10, NCasT4) have region availability constraints — validate before committing
- vGPU profile sizing must be re-validated on new platform (performance characteristics may differ)

## User Profile Migration

### Profile Technology Mapping

| Technology | Vendor | Portability | Migration Path |
|------------|--------|-------------|----------------|
| **FSLogix Profile Container** | Microsoft | High — VHD/VHDX on SMB | Copy VHD files to new storage; works across Citrix, Horizon, AVD |
| **FSLogix Office Container** | Microsoft | High | Same as profile container; separate VHD for Office cache |
| **Omnissa DEM (Dynamic Environment Manager)** | Omnissa | Medium | DEM config files export/import; tied to Horizon ecosystem |
| **Citrix UPM (User Profile Manager)** | Citrix | Medium | Profile store migration; may need reconfiguration on new broker |
| **Citrix Profile Management + WEM** | Citrix | Medium | WEM policies export; profile store relocate |
| **Liquidware ProfileUnity** | Liquidware | High | Broker-agnostic; works on Citrix, Horizon, AVD |

### Migration Best Practices

- **FSLogix is the safest cross-platform choice** — works with Citrix, Horizon, and AVD; VHD containers are portable
- If migrating from Citrix UPM to FSLogix, use the FSLogix Profile Migration Tool (frx.exe)
- If migrating from Omnissa DEM to another platform, export personalization settings; application settings may need manual mapping
- Always test profile migration with a pilot group before mass migration
- Profile container storage must be sized for the new platform (Azure Files for AVD, SMB shares for on-prem)
- Profile container storage performance matters — IOPS per user varies by persona (5-20 IOPS for task workers, 20-50+ for power users)

## Desktop Image Management

### Image Strategy by Platform

| Strategy | Platform Support | How It Works | Best For |
|----------|-----------------|--------------|----------|
| **MCS (Machine Creation Services)** | Citrix on vSphere, AHV, Hyper-V, Azure | Master image + differencing disks | Citrix environments, pooled/dedicated |
| **PVS (Provisioning Services)** | Citrix on vSphere, Hyper-V | Network-streamed vDisk | Large-scale Citrix, shared image |
| **Linked Clones** | Horizon on vSphere | Replica + delta disks | Legacy Horizon (being replaced) |
| **Instant Clones** | Horizon on vSphere | Fork from running parent VM | Horizon non-persistent, fast provisioning |
| **Redirect-on-Write (RoW)** | Horizon on AHV (2512+) | AHV-native cloning via recovery points | Horizon on AHV environments |
| **Full Clones** | All platforms | Complete copy of master | Persistent desktops, GPU passthrough |
| **Azure Managed Images / Compute Gallery** | AVD, Windows 365 | Azure-native image management | Cloud VDI |

### Migration Considerations

- Image provisioning technology does NOT transfer between platforms — images must be rebuilt
- Master/gold images can often be exported as VMDK/VHDX and imported to new hypervisor, but provisioning config must be recreated
- Application layering (Citrix App Layering, Omnissa App Volumes) reduces image rebuild effort — layers may be portable
- Automate image builds with Packer or similar tooling to make images platform-independent at the source level
- Antivirus, agents, and optimization tools (Citrix Optimizer, VMware OS Optimization Tool) may differ per target platform

## Print and Peripheral Redirection

### Compatibility Considerations

| Feature | Horizon | Citrix | AVD | Windows 365 |
|---------|---------|--------|-----|-------------|
| **USB redirection** | Full (USB-R) | Generic + vendor-specific | Limited (via RDP) | Limited (via RDP) |
| **Printer redirection** | ThinPrint (integrated) | Citrix Universal Print Driver | Universal Print / RDP printing | Universal Print |
| **Scanner redirection** | TWAIN/WIA redirection | TWAIN redirection | Limited | Limited |
| **Webcam redirection** | RTAV (Real-Time Audio-Video) | HDX webcam | AVD media optimization | Teams optimization |
| **Multi-monitor** | Up to 4 (protocol dependent) | Up to 8 | Up to 16 | Up to 4 |
| **Smart card** | Yes | Yes | Yes | Yes |

### Migration Risks

- USB redirection policies differ significantly between brokers — test all peripherals
- Printer drivers may need rebuilding on the target platform (universal drivers reduce this risk)
- Specialty peripherals (barcode scanners, signature pads, medical devices) require explicit testing
- Protocol differences (Blast vs HDX vs RDP) affect peripheral performance — especially for real-time devices

## Performance Benchmarking Methodology

### Tools

| Tool | Vendor | What It Measures | When to Use |
|------|--------|-----------------|-------------|
| **Login VSI** | Login VSI | Simulated user load, VSImax, response times | Pre-migration baseline and post-migration validation |
| **Lakeside SysTrack** | Lakeside Software | Real user experience, resource utilization, sentiment | Continuous monitoring, before/during/after migration |
| **ControlUp** | ControlUp | Real-time session metrics, logon duration breakdown | Operational monitoring, troubleshooting |
| **Goliath Performance Monitor** | Goliath | End-to-end VDI performance, proactive alerting | Enterprise monitoring across broker platforms |

### Benchmarking Process

1. **Baseline (pre-migration):** Deploy monitoring on current platform for minimum 2 weeks; capture login times, app launch times, protocol latency, CPU/RAM/IOPS per session
2. **Define personas:** Task worker, knowledge worker, power user, developer — each has different resource and performance profiles
3. **Pilot (target platform):** Deploy representative users on target platform; run same monitoring for minimum 2 weeks
4. **Compare:** Login time, app launch time, session responsiveness, protocol frame rate, user sentiment scores
5. **Load test:** Use Login VSI to simulate peak concurrent sessions on target platform; validate VSImax meets capacity requirements
6. **Acceptance criteria:** Define pass/fail thresholds before testing (e.g., login time <30s, app launch <5s, no degradation >10% from baseline)

## Licensing Implications

### Windows Desktop Licensing for VDI

| Scenario | Required License | Notes |
|----------|-----------------|-------|
| **On-prem VDI (any broker)** | Windows VDA per-device or Windows E3/E5 per-user SA | VDA required for thin clients and BYOD accessing VDI |
| **RDS multi-session (on-prem)** | Windows Server CAL + RDS CAL (per user or per device) | Applies to RDSH-based published desktops and apps |
| **AVD** | Microsoft 365 E3/E5, Windows E3/E5, or VDA per-user | Multi-session Windows 10/11 only on AVD |
| **Windows 365** | Windows 365 subscription (includes Windows license) | All-inclusive per-user pricing |
| **Citrix on Azure** | Microsoft 365 E3/E5 + Citrix Universal subscription | Citrix license is additive to Microsoft entitlement |
| **Horizon on Azure** | Microsoft 365 E3/E5 + Omnissa Horizon subscription | Horizon license is additive to Microsoft entitlement |

### Broker Licensing

| Broker | License Model | Key Consideration |
|--------|--------------|-------------------|
| **Omnissa Horizon** | Per-named-user or per-concurrent-user subscription | Post-Broadcom: subscription-only; perpetual licenses no longer sold |
| **Citrix CVAD** | Universal subscription (per-user) | Includes on-prem and cloud (DaaS) entitlements |
| **AVD** | Included with qualifying Microsoft 365 / Windows licenses | No additional broker cost; pay only for Azure compute/storage |
| **Windows 365** | Per-user monthly subscription | Includes compute, storage, and Windows license |
| **Dizzion Frame** | Per-user DaaS subscription | Infrastructure cost bundled or separate depending on deployment |

### License Migration Traps

- Moving from on-prem VDI to AVD may not require new Windows licenses if Microsoft 365 E3/E5 is already owned
- Moving from Horizon to Citrix (or vice versa) requires new broker licenses — no cross-vendor portability
- RDS CALs are version-specific — moving to newer Windows Server may require new CALs
- NVIDIA vGPU licenses are hypervisor-independent but GPU hardware changes may require different vGPU editions
- Broadcom/VMware licensing changes may significantly alter Horizon TCO — model carefully before deciding to stay or leave

## Hardware BOM Impact

### On-Prem VDI Sizing Changes

| Change | Impact on Hardware |
|--------|--------------------|
| **Hypervisor change (vSphere to AHV)** | Same server hardware may be reused; validate AHV HCL compatibility; may save on hypervisor license cost |
| **Broker change (same hypervisor)** | Minimal hardware impact; infrastructure servers (connection brokers, SQL) may differ |
| **Add GPU support** | Requires GPU-capable servers; PCIe slot availability; power and cooling changes; rack density impact |
| **Move to cloud VDI** | Eliminates on-prem VDI compute entirely; retain networking for hybrid; thin client refresh may still apply |
| **Hybrid (on-prem + cloud burst)** | Size on-prem for base load only; cloud handles peak; requires reliable WAN |

### Cloud VDI Cost Drivers

- Compute is the dominant cost in cloud VDI — right-size aggressively
- Storage (OS disk, profile container, temp disk) adds up at scale
- Egress charges apply for data leaving the cloud region
- Reserved instances or savings plans reduce compute cost 30-60%
- Autoscaling (AVD) or power management (Citrix, Horizon) reduces off-hours cost
- GPU VMs in cloud are significantly more expensive than CPU-only — use only where validated by user persona

## Connection Broker Options by Platform

| Hypervisor / Cloud | Compatible Brokers | Notes |
|--------------------|--------------------|-------|
| **VMware vSphere** | Horizon, Citrix CVAD, Parallels RAS | Broadest broker selection |
| **Nutanix AHV** | Horizon (2512+), Citrix CVAD, Parallels RAS, Dizzion Frame | Growing ecosystem post-VMware exodus |
| **Microsoft Hyper-V** | Citrix CVAD, Parallels RAS, Microsoft RDS broker | Horizon support limited — verify current matrix |
| **Microsoft Azure** | AVD, Windows 365, Citrix DaaS, Horizon Cloud, Parallels RAS | Cloud-native options dominate |
| **AWS** | Amazon WorkSpaces, Citrix DaaS, Horizon Cloud | WorkSpaces is AWS-native DaaS |
| **GCP** | Citrix DaaS, Horizon Cloud | Narrower VDI ecosystem on GCP |

## Common Decisions (ADR Triggers)

- **Target VDI platform selection** — which broker + hypervisor/cloud combination, with justification against alternatives
- **Re-platform vs re-broker vs cloud** — keep current broker on new hypervisor, change broker, or move to cloud VDI
- **Profile technology selection** — FSLogix vs broker-native profiles vs third-party (Liquidware), portability requirements
- **Image management strategy** — MCS vs PVS vs instant/linked clones vs cloud-native image management on target platform
- **GPU strategy** — vGPU profiles, GPU VM SKUs, which user personas require GPU, cost justification
- **Licensing model** — per-user vs per-device vs consumption-based, total cost comparison across platform options
- **Hybrid VDI architecture** — which workloads stay on-prem, which move to cloud, how brokers integrate across boundaries
- **Performance acceptance criteria** — quantitative thresholds for login time, responsiveness, and protocol performance
- **Peripheral and printing strategy** — universal drivers vs vendor-specific, USB redirection scope, compatibility validation plan
- **Migration sequencing** — which user groups migrate first, rollback plan per wave, coexistence duration

## Reference Links

- [Omnissa Horizon Documentation](https://docs.omnissa.com/)
- [Citrix Virtual Apps and Desktops](https://docs.citrix.com/en-us/citrix-virtual-apps-desktops)
- [Azure Virtual Desktop](https://learn.microsoft.com/en-us/azure/virtual-desktop/)
- [NVIDIA vGPU Software](https://www.nvidia.com/en-us/data-center/virtual-gpu-technology/)
- [Login VSI](https://www.loginvsi.com/)
- [Lakeside SysTrack](https://www.lakesidesoftware.com/)

## See Also

- `general/workload-migration.md` — General migration strategy, wave planning, cutover procedures
- `general/hardware-sizing.md` — Compute and storage sizing for on-prem infrastructure
- `general/compute.md` — Cloud compute instance selection
- `general/cost.md` — Cost modeling for cloud vs on-premises
- `general/identity.md` — Identity and access management (relevant for VDI authentication)
