# VMware Platform Services

## Checklist

- [ ] Is vSphere with Tanzu (TKGS) deployed with a Supervisor Cluster enabled on the vSphere cluster, with Workload Management configured to provide vSphere Namespaces, VM classes, and storage policies for developer self-service Kubernetes provisioning?
- [ ] Are VM classes (guaranteed vs best-effort) defined in Tanzu to control vCPU, memory, and reservation levels for Kubernetes node VMs, preventing resource overcommit in shared clusters?
- [ ] Is Tanzu Kubernetes Grid (TKG) evaluated as an alternative to TKGS for environments requiring standalone Kubernetes clusters (not tied to vSphere) or multi-cloud Kubernetes with consistent lifecycle management?
- [ ] Is VMware HCX deployed for workload migration with the appropriate migration type selected -- bulk migration (scheduled, VM powered off briefly), vMotion migration (live, zero downtime), or Replication Assisted vMotion (large VMs, minimal downtime) -- based on migration window and downtime tolerance?
- [ ] Is HCX Network Extension configured for L2 stretch between source and destination sites during migration, with Mobility Optimized Networking (MON) enabled to avoid traffic tromboning by routing locally at the destination?
- [ ] Is Aria Operations (formerly vRealize Operations) deployed for infrastructure monitoring, capacity planning, right-sizing recommendations, cost analysis, and compliance dashboards, with management packs installed for non-VMware infrastructure (storage arrays, physical switches)?
- [ ] Is Aria Automation (formerly vRealize Automation) configured for infrastructure-as-code provisioning with cloud templates (blueprints), approval policies, lease management, and day-2 operations (scale, snapshot, reconfigure) for self-service VM and Kubernetes provisioning?
- [ ] Is VMware Cloud Foundation (VCF) used as the standardized SDDC stack, bundling vSphere, vSAN, NSX, and Aria Suite with SDDC Manager for automated lifecycle management, updates, and compliance?
- [ ] Is SDDC Manager (in VCF deployments) configured to manage workload domains with appropriate sizing (management domain for infrastructure VMs, separate workload domains for tenant or application isolation)?
- [ ] Is VMware Cloud on AWS, Azure VMware Solution (AVS), or Google Cloud VMware Engine (GCVE) evaluated for hybrid cloud use cases, with HCX providing migration path and consistent networking between on-premises and cloud SDDC?
- [ ] Are Tanzu vSphere Namespaces configured with resource quotas (CPU, memory, storage) and network policies to provide multi-tenant isolation for development teams, with RBAC mapped to Active Directory groups?
- [ ] Is the Tanzu supervisor cluster's control plane sized appropriately (small/medium/large) based on the expected number of namespaces, TKG clusters, and VM service VMs, with HA enabled across three control plane nodes?
- [ ] Is Aria Automation Config (formerly SaltStack Config) evaluated for configuration management and drift remediation of VMs provisioned through the Aria Automation pipeline?

## Why This Matters

VMware's platform services transform vSphere from a virtualization layer into a private cloud platform. Tanzu bridges the operational gap between traditional VM teams and developers expecting Kubernetes self-service, but misconfigured VM classes or namespace resource quotas can either starve developers or allow runaway resource consumption. HCX enables datacenter evacuations and cloud migrations without re-IP or application changes, but Network Extension without MON creates traffic tromboning that degrades performance after migration. VCF standardizes the SDDC stack but constrains flexibility -- all components must be at VCF-validated versions, and SDDC Manager controls the upgrade sequence. Aria Operations right-sizing recommendations, if followed without validation, can undersize workloads that have seasonal peaks not captured in the analysis window. The Broadcom acquisition has significantly changed the licensing and availability of many platform services, making VCF the primary consumption model.

## Common Decisions (ADR Triggers)

- **TKGS vs TKG vs upstream Kubernetes** -- TKGS (vSphere-native, supervisor cluster, tightest integration, requires vSphere 7+/8) vs TKG standalone (multi-cloud consistent, runs on AWS/Azure/vSphere) vs upstream (Rancher, OpenShift, Kubeadm) for existing Kubernetes investment or multi-vendor strategy
- **VCF vs a la carte** -- VCF for standardized, validated SDDC stack with automated lifecycle management vs individual vSphere + vSAN + NSX licensing for flexibility in component versions and upgrade timing; Broadcom is pushing VCF as the primary licensing model
- **VMware Cloud on AWS vs Azure VMware Solution** -- VMC on AWS (longest track record, joint engineering, elastic scaling) vs AVS (Azure-native integration, RI pricing, ExpressRoute connectivity) vs GCVE (Google Cloud integration); choice often driven by existing cloud provider relationship
- **HCX migration type** -- bulk migration (simplest, brief downtime) vs vMotion (zero downtime, slower for large VMs) vs RAV (best for large VMs, switchover downtime <1 minute); HCX also enables ongoing bidirectional mobility
- **Aria Automation vs Terraform/Ansible** -- Aria Automation for GUI-driven self-service with approval workflows and lease management vs Terraform (VMware provider) + Ansible for infrastructure-as-code with pipeline integration; many organizations use both
- **Management domain sizing** -- consolidated (management + workload on same cluster, fewer hosts) vs dedicated management domain (isolation, independent scaling); VCF recommends dedicated management domain for production
- **Tanzu VM Service vs traditional VMs** -- VM Service for developers deploying VMs via kubectl and YAML within namespaces vs traditional vCenter VM provisioning for infrastructure teams; VM Service enables consistent developer experience across VMs and containers

## Version Notes

| Feature | vSphere 7 / TKGs 1.x / VCF 4.x | vSphere 8 / TKGs 2.x / VCF 5.x |
|---|---|---|
| Tanzu Kubernetes Grid Service | TKGs 1.x (TKC API) | TKGs 2.x (ClusterClass API) |
| TKG standalone (multi-cloud) | TKG 1.x (management cluster) | TKG 2.x (ClusterClass, unified CLI) |
| Supervisor cluster | vSphere 7 U2+ (NSX or VDS networking) | vSphere 8 (VDS networking simplified) |
| VM Service | GA (vSphere 7 U2a+) | GA (improved, cloud-init support) |
| VCF lifecycle (SDDC Manager) | VCF 4.x (vSphere 7, NSX-T 3.x) | VCF 5.x (vSphere 8, NSX 4.x) |
| Aria Operations (monitoring) | vRealize Operations 8.x | Aria Operations 8.12+ (rebranded) |
| Aria Automation (provisioning) | vRealize Automation 8.x | Aria Automation 8.12+ (rebranded) |
| Aria Operations for Logs | vRealize Log Insight 8.x | Aria Operations for Logs (rebranded) |
| Aria Automation Config | SaltStack Config | Aria Automation Config (rebranded) |
| VMware Cloud Foundation | VCF 4.x (async component updates) | VCF 5.x (unified lifecycle, Broadcom model) |
| HCX | HCX 4.x | HCX 4.8+ (improved migration, MON) |
| Tanzu Mission Control | SaaS only | SaaS (Broadcom licensing changes) |

**Key changes across versions:**
- **Tanzu Kubernetes versions:** TKGs 1.x used the TanzuKubernetesCluster (TKC) API for creating Kubernetes clusters on vSphere. TKGs 2.x migrated to the upstream Cluster API ClusterClass model, providing better conformance with the CNCF ecosystem. Existing TKC-based clusters must be migrated to ClusterClass. TKG 2.x also unified the standalone and supervisor-based experiences.
- **VCF 4.x vs 5.x:** VCF 5.x bundles vSphere 8, NSX 4.x, and vSAN 8. SDDC Manager in VCF 5.x provides more unified lifecycle management with fewer manual steps. VCF 5.x is the primary licensing model under Broadcom, with per-core subscription pricing replacing perpetual licenses for many customers.
- **Aria suite rebranding from vRealize:** In 2023, VMware rebranded the entire vRealize suite to Aria. vRealize Operations became Aria Operations, vRealize Automation became Aria Automation, vRealize Log Insight became Aria Operations for Logs, and SaltStack Config became Aria Automation Config. The underlying technology is largely the same; the rebranding aligned products under the Aria multi-cloud management brand. Upgrade paths exist from vRealize 8.x to Aria 8.12+.
- **Broadcom acquisition impact:** The Broadcom acquisition (completed late 2023) significantly changed VMware licensing. Many standalone products were bundled into VCF or VMware Cloud Foundation for VMware Cloud. Perpetual licenses transitioned to subscription. Tanzu and Aria products were consolidated. Customers should verify current licensing entitlements and availability of individual products vs VCF bundles.
