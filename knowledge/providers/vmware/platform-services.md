# VMware Platform Services

## Scope

This document covers VMware platform services including Tanzu Kubernetes (TKGS/TKG), HCX workload migration, VCF Operations (formerly Aria Operations), VCF Automation (formerly Aria Automation), VMware Cloud Foundation lifecycle, SDDC Manager, and hybrid cloud options (VMC on AWS, AVS, GCVE).

## Checklist

- [ ] **[Recommended]** Is vSphere with Tanzu (TKGS) deployed with a Supervisor Cluster enabled on the vSphere cluster, with Workload Management configured to provide vSphere Namespaces, VM classes, and storage policies for developer self-service Kubernetes provisioning?
- [ ] **[Recommended]** Are VM classes (guaranteed vs best-effort) defined in Tanzu to control vCPU, memory, and reservation levels for Kubernetes node VMs, preventing resource overcommit in shared clusters?
- [ ] **[Optional]** Is Tanzu Kubernetes Grid (TKG) evaluated as an alternative to TKGS for environments requiring standalone Kubernetes clusters (not tied to vSphere) or multi-cloud Kubernetes with consistent lifecycle management?
- [ ] **[Optional]** Is VMware HCX deployed for workload migration with the appropriate migration type selected -- bulk migration (scheduled, VM powered off briefly), vMotion migration (live, zero downtime), or Replication Assisted vMotion (large VMs, minimal downtime) -- based on migration window and downtime tolerance?
- [ ] **[Recommended]** Is HCX Network Extension configured for L2 stretch between source and destination sites during migration, with Mobility Optimized Networking (MON) enabled to avoid traffic tromboning by routing locally at the destination?
- [ ] **[Recommended]** Is VCF Operations (formerly Aria Operations / vRealize Operations) deployed for infrastructure monitoring, capacity planning, right-sizing recommendations, cost analysis, and compliance dashboards, with management packs installed for non-VMware infrastructure (storage arrays, physical switches)?
- [ ] **[Optional]** Is VCF Automation (formerly Aria Automation / vRealize Automation) configured for infrastructure-as-code provisioning with cloud templates (blueprints), approval policies, lease management, and day-2 operations (scale, snapshot, reconfigure) for self-service VM and Kubernetes provisioning?
- [ ] **[Critical]** Is VMware Cloud Foundation (VCF) used as the standardized SDDC stack, bundling vSphere, vSAN, NSX, and the VCF management suite with SDDC Manager for automated lifecycle management, updates, and compliance?
- [ ] **[Critical]** Is SDDC Manager (in VCF deployments) configured to manage workload domains with appropriate sizing (management domain for infrastructure VMs, separate workload domains for tenant or application isolation)?
- [ ] **[Optional]** Is VMware Cloud on AWS, Azure VMware Solution (AVS), or Google Cloud VMware Engine (GCVE) evaluated for hybrid cloud use cases, with HCX providing migration path and consistent networking between on-premises and cloud SDDC?
- [ ] **[Recommended]** Are Tanzu vSphere Namespaces configured with resource quotas (CPU, memory, storage) and network policies to provide multi-tenant isolation for development teams, with RBAC mapped to Active Directory groups?
- [ ] **[Recommended]** Is the Tanzu supervisor cluster's control plane sized appropriately (small/medium/large) based on the expected number of namespaces, TKG clusters, and VM service VMs, with HA enabled across three control plane nodes?
- [ ] **[Optional]** Is VCF Automation Config (formerly Aria Automation Config / SaltStack Config) evaluated for configuration management and drift remediation of VMs provisioned through the VCF Automation pipeline?

## Why This Matters

VMware's platform services transform vSphere from a virtualization layer into a private cloud platform. Tanzu bridges the operational gap between traditional VM teams and developers expecting Kubernetes self-service, but misconfigured VM classes or namespace resource quotas can either starve developers or allow runaway resource consumption. HCX enables datacenter evacuations and cloud migrations without re-IP or application changes, but Network Extension without MON creates traffic tromboning that degrades performance after migration. VCF standardizes the SDDC stack but constrains flexibility -- all components must be at VCF-validated versions, and SDDC Manager controls the upgrade sequence. VCF Operations (formerly Aria Operations) right-sizing recommendations, if followed without validation, can undersize workloads that have seasonal peaks not captured in the analysis window. The Broadcom acquisition has significantly changed the licensing and availability of many platform services, making VCF the primary consumption model. In VCF 9.0, all Aria-branded products have been renamed to VCF-prefixed names (VCF Operations, VCF Automation, VCF Operations for Logs, VCF Automation Config). HCX continues to be available but is being consolidated into the VCF platform.

## Common Decisions (ADR Triggers)

- **TKGS vs TKG vs upstream Kubernetes** -- TKGS (vSphere-native, supervisor cluster, tightest integration, requires vSphere 7+/8) vs TKG standalone (multi-cloud consistent, runs on AWS/Azure/vSphere) vs upstream (Rancher, OpenShift, Kubeadm) for existing Kubernetes investment or multi-vendor strategy
- **VCF vs a la carte** -- VCF for standardized, validated SDDC stack with automated lifecycle management vs individual vSphere + vSAN + NSX licensing for flexibility in component versions and upgrade timing; Broadcom has made VCF the primary licensing model
- **VMware Cloud on AWS vs Azure VMware Solution** -- VMC on AWS (longest track record, joint engineering, elastic scaling) vs AVS (Azure-native integration, RI pricing, ExpressRoute connectivity) vs GCVE (Google Cloud integration); choice often driven by existing cloud provider relationship
- **HCX migration type** -- bulk migration (simplest, brief downtime) vs vMotion (zero downtime, slower for large VMs) vs RAV (best for large VMs, switchover downtime <1 minute); HCX also enables ongoing bidirectional mobility. Note: HCX is being consolidated into VCF platform services.
- **VCF Automation vs Terraform/Ansible** -- VCF Automation (formerly Aria Automation) for GUI-driven self-service with approval workflows and lease management vs Terraform (VMware provider) + Ansible for infrastructure-as-code with pipeline integration; many organizations use both
- **Management domain sizing** -- consolidated (management + workload on same cluster, fewer hosts) vs dedicated management domain (isolation, independent scaling); VCF recommends dedicated management domain for production
- **Tanzu VM Service vs traditional VMs** -- VM Service for developers deploying VMs via kubectl and YAML within namespaces vs traditional vCenter VM provisioning for infrastructure teams; VM Service enables consistent developer experience across VMs and containers

## Version Notes

| Feature | vSphere 7 / TKGs 1.x / VCF 4.x | vSphere 8 / TKGs 2.x / VCF 5.x | vSphere 9 / VCF 9.0 |
|---|---|---|---|
| Tanzu Kubernetes Grid Service | TKGs 1.x (TKC API) | TKGs 2.x (ClusterClass API) | TKGs (ClusterClass, continued) |
| TKG standalone (multi-cloud) | TKG 1.x (management cluster) | TKG 2.x (ClusterClass, unified CLI) | Consolidated into VCF |
| Supervisor cluster | vSphere 7 U2+ (NSX or VDS networking) | vSphere 8 (VDS networking simplified) | vSphere 9 (continued) |
| VM Service | GA (vSphere 7 U2a+) | GA (improved, cloud-init support) | GA |
| VCF lifecycle (SDDC Manager) | VCF 4.x (vSphere 7, NSX-T 3.x) | VCF 5.x (vSphere 8, NSX 4.x) | VCF 9.0 (vSphere 9, NSX 9.x) |
| VCF Operations (monitoring) | vRealize Operations 8.x | Aria Operations 8.12+ (rebranded) | **VCF Operations** (renamed from Aria) |
| VCF Automation (provisioning) | vRealize Automation 8.x | Aria Automation 8.12+ (rebranded) | **VCF Automation** (renamed from Aria) |
| VCF Operations for Logs | vRealize Log Insight 8.x | Aria Operations for Logs (rebranded) | **VCF Operations for Logs** (renamed) |
| VCF Automation Config | SaltStack Config | Aria Automation Config (rebranded) | **VCF Automation Config** (renamed) |
| VMware Cloud Foundation | VCF 4.x (async component updates) | VCF 5.x (unified lifecycle, Broadcom model) | VCF 9.0 (unified versioning, all components 9.x) |
| HCX | HCX 4.x | HCX 4.8+ (improved migration, MON) | HCX (consolidated into VCF platform) |
| Tanzu Mission Control | SaaS only | SaaS (Broadcom licensing changes) | Consolidated into VCF |

**Key changes in VCF 9.0:**
- **Version number jump (5.x to 9.0):** VCF jumped directly from version 5.x to 9.0 to align all component version numbers. There is no VCF 6.x, 7.x, or 8.x. All components now share the 9.x version: vSphere 9, ESXi 9, vSAN 9, NSX 9, and the VCF management suite.
- **Aria renamed to VCF:** All Aria-branded products have been renamed to VCF-prefixed names in VCF 9.0. Aria Operations is now VCF Operations, Aria Automation is now VCF Automation, Aria Operations for Logs is now VCF Operations for Logs, and Aria Automation Config is now VCF Automation Config. The underlying technology continues to evolve; the rebranding aligns all products under the VCF umbrella.
- **HCX consolidation:** HCX continues to provide workload migration capabilities but is being consolidated into the VCF platform rather than remaining a standalone product. Verify current HCX licensing and availability within your VCF entitlement.
- **Tanzu consolidation:** Tanzu products (TKG standalone, Tanzu Mission Control) are being consolidated into VCF. Verify current Tanzu entitlements and product availability.

**Key changes across earlier versions:**
- **Tanzu Kubernetes versions:** TKGs 1.x used the TanzuKubernetesCluster (TKC) API for creating Kubernetes clusters on vSphere. TKGs 2.x migrated to the upstream Cluster API ClusterClass model, providing better conformance with the CNCF ecosystem. Existing TKC-based clusters must be migrated to ClusterClass. TKG 2.x also unified the standalone and supervisor-based experiences.
- **VCF 4.x vs 5.x:** VCF 5.x bundles vSphere 8, NSX 4.x, and vSAN 8. SDDC Manager in VCF 5.x provides more unified lifecycle management with fewer manual steps. VCF 5.x is the primary licensing model under Broadcom, with per-core subscription pricing replacing perpetual licenses for many customers.
- **Aria suite rebranding from vRealize (2023):** VMware rebranded the entire vRealize suite to Aria. vRealize Operations became Aria Operations, vRealize Automation became Aria Automation, vRealize Log Insight became Aria Operations for Logs, and SaltStack Config became Aria Automation Config. This intermediate branding has now been superseded by VCF-prefixed names in VCF 9.0.
- **Broadcom acquisition impact:** The Broadcom acquisition (completed late 2023) significantly changed VMware licensing. Many standalone products were bundled into VCF. Perpetual licenses transitioned to subscription. Tanzu and Aria products were consolidated. Customers should verify current licensing entitlements and availability of individual products vs VCF bundles.
