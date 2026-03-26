# VMware Horizon

## Scope

This document covers VMware Horizon virtual desktop infrastructure (VDI) architecture, including Connection Server design, Cloud Pod Architecture (CPA) for multi-site, Unified Access Gateway (UAG) for external access, instant clones vs full clones vs linked clones, App Volumes for application delivery, Dynamic Environment Manager (DEM) for user personalization, Horizon on different hypervisors (vSphere, Azure VMware Solution), Horizon Cloud on Azure, migration from on-premises to cloud-hosted Horizon, and licensing changes under Broadcom (named/concurrent users, subscription vs perpetual, VDI edition bundling).

## Checklist

- [ ] **[Critical]** Is the Connection Server pod architecture designed with appropriate redundancy (minimum 2 Connection Servers per pod, behind a load balancer) with documented failover and capacity limits (2,000 sessions per Connection Server, 12,000 per pod)?
- [ ] **[Critical]** Is Unified Access Gateway (UAG) deployed in the DMZ for external access with proper sizing (number of appliances for concurrent external sessions), TLS certificate configuration, and firewall rules documented?
- [ ] **[Critical]** Is the desktop provisioning strategy defined -- instant clones (recommended for stateless, fast provisioning) vs full clones (persistent use cases requiring individual disk management)?
- [ ] **[Critical]** Is the vSphere infrastructure sized for VDI workloads with appropriate CPU overcommit ratios (typically 8-12:1 for task workers, 4-6:1 for power users), memory (no overcommit for VDI), and storage IOPS (boot storms, login storms)?
- [ ] **[Critical]** Is the Horizon licensing model evaluated under Broadcom subscription terms, including per-named-user vs per-concurrent-user, VDI edition (Standard/Advanced/Enterprise), and VCF bundle inclusion?
- [ ] **[Recommended]** Is App Volumes configured for application delivery with writable volumes for user-installed apps and AppStacks for IT-managed applications, with a documented application packaging workflow?
- [ ] **[Recommended]** Is Dynamic Environment Manager (DEM) configured for user environment personalization, including Windows settings, application settings, mapped drives, and conditional policies based on device/location?
- [ ] **[Recommended]** Is the golden image management process documented, including image versioning, patching cadence, OSOT (OS Optimization Tool) application, and instant clone push operations with maintenance windows?
- [ ] **[Recommended]** Is Cloud Pod Architecture (CPA) configured for multi-site deployments with global entitlements, home site assignments, and inter-pod communication requirements?
- [ ] **[Recommended]** Is the display protocol strategy defined -- Blast Extreme (preferred, UDP/TCP adaptive) vs PCoIP -- with bandwidth and latency requirements documented for each user segment (LAN, WAN, mobile)?
- [ ] **[Optional]** Is GPU acceleration (vGPU with NVIDIA profiles or AMD MxGPU) evaluated for graphics-intensive workloads (CAD, 3D modeling, video editing) with appropriate GPU profile sizing?
- [ ] **[Optional]** Is migration from on-premises Horizon to Horizon Cloud on Azure or Azure Virtual Desktop evaluated, including feature parity assessment and hybrid deployment during transition?

## Why This Matters

VMware Horizon is the leading enterprise VDI platform for vSphere-based environments, providing centralized desktop management, security, and remote access capabilities. Proper Connection Server sizing and UAG deployment are critical -- undersized infrastructure causes login storms and session failures during peak hours. Instant clones have become the standard provisioning method, replacing linked clones, offering faster provisioning and simplified storage management but requiring careful golden image and OSOT optimization.

The Broadcom acquisition has significantly impacted Horizon licensing and roadmap. Horizon is now bundled within VCF editions or available as standalone subscription licenses, replacing the previous perpetual licensing model. Organizations must evaluate whether the per-named-user or per-concurrent-user model is more cost-effective for their usage patterns. Many organizations are evaluating migration to Azure Virtual Desktop, Windows 365, or Citrix DaaS as alternatives, making the Horizon licensing and feature comparison a critical architectural decision.

## Common Decisions (ADR Triggers)

- **Instant clones vs full clones** -- stateless instant clones (fast provisioning, simplified storage) vs persistent full clones (user-installed apps, unique configurations)
- **Blast Extreme vs PCoIP** -- Blast (modern, adaptive, HTML5 client support) vs PCoIP (mature, Teradici hardware offload), bandwidth and latency requirements
- **On-premises vs cloud-hosted** -- Horizon on vSphere vs Horizon Cloud on Azure vs Azure Virtual Desktop, cost model and management complexity
- **App delivery strategy** -- App Volumes vs MSIX App Attach vs application virtualization (ThinApp) vs installed in golden image
- **Profile management** -- DEM vs FSLogix (for hybrid/Azure scenarios) vs Liquidware ProfileUnity
- **GPU provisioning** -- vGPU profiles (shared GPU) vs GPU passthrough (dedicated), NVIDIA vs AMD, profile sizing per user type
- **Multi-site design** -- Cloud Pod Architecture with global entitlements vs independent pods per site, DR strategy for VDI
- **Horizon licensing** -- VCF bundle inclusion vs standalone Horizon subscription, named vs concurrent user licensing

## See Also

- `general/vdi-migration-strategy.md` -- VDI migration planning patterns
- `providers/vmware/infrastructure.md` -- VMware vSphere infrastructure architecture
- `providers/vmware/licensing.md` -- VMware/Broadcom licensing considerations
