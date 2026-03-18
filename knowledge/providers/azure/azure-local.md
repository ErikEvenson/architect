# Azure Local (formerly Azure Stack HCI)

## Scope

Azure hyper-converged infrastructure for running Azure services on-premises. Covers cluster sizing, Storage Spaces Direct, Network ATC, AKS hybrid, AVD on-premises, stretch clustering, and subscription-based licensing.

Hyper-converged infrastructure (HCI) solution that runs Azure services on-premises using validated hardware. Delivers Azure Arc-enabled management, AKS hybrid clusters, and native Azure service integration on customer-owned infrastructure. Renamed from Azure Stack HCI to Azure Local in late 2024 to reflect its positioning as a local extension of the Azure cloud.

## Checklist

- [ ] **[Critical]** Select validated hardware nodes from Dell, HPE, Lenovo, or other Azure Local Integrated System partners; confirm CPU, memory, and NVMe/SSD requirements for target workloads
- [ ] **[Critical]** Plan cluster sizing: minimum 1 node (single-node) up to 16 nodes per cluster; account for N+1 node fault tolerance for production workloads
- [ ] **[Critical]** Design networking topology: choose between Network ATC (simplified intent-based) and manual SDN configuration; plan for management, compute, and storage traffic separation
- [ ] **[Critical]** Configure Storage Spaces Direct (S2D): select drive tiers (NVMe cache + SSD capacity or all-NVMe), plan volume layout, enable thin provisioning for efficient capacity utilization
- [ ] **[Critical]** Register the cluster with Azure Arc and verify Azure subscription linkage for billing and management
- [ ] **[Recommended]** Deploy AKS hybrid (AKS on Azure Local) if running containerized workloads: plan control plane sizing, node pool configuration, and container networking (Calico or Flannel)
- [ ] **[Optional]** Plan Azure Virtual Desktop (AVD) session host deployment on Azure Local if delivering virtual desktops from on-premises infrastructure
- [ ] **[Critical]** Configure Azure Backup and Azure Site Recovery for VM protection; set up Azure Monitor and Azure Defender for Cloud for observability and security posture management
- [ ] **[Recommended]** Set up Lifecycle Manager (formerly Windows Admin Center updates) for coordinated firmware, driver, and OS updates with rolling node-by-node upgrades
- [ ] **[Optional]** Design stretch clustering across two sites if multi-site HA is required: configure synchronous replication (up to ~5ms RTT between sites) and a cloud witness in Azure for quorum
- [ ] **[Recommended]** Plan for disconnected or partially connected scenarios: understand which features require continuous Azure connectivity (billing heartbeat, Arc agent check-in) versus those that operate offline
- [ ] **[Optional]** Evaluate SQL Managed Instance on Azure Local for on-prem managed SQL with Azure parity features (automated patching, point-in-time restore)
- [ ] **[Recommended]** Document licensing model: Azure Local uses a per-physical-core/month subscription model billed through Azure; Windows Server guest licensing is included in the subscription

## Why This Matters

Organizations with data residency requirements, latency-sensitive workloads, or existing datacenter investments need a path to consume Azure services without moving all workloads to public cloud. Azure Local provides a consistent Azure management plane (Arc, portal, ARM templates, Azure Policy) over on-prem infrastructure. This avoids the operational bifurcation of managing separate on-prem and cloud toolchains. Without it, teams maintain parallel skill sets and pipelines for VMware/Hyper-V on-prem and Azure in the cloud. Azure Local collapses that gap while keeping data physically on-premises.

The subscription model also shifts from CapEx-heavy perpetual licensing to OpEx-aligned billing, which simplifies budgeting and aligns with cloud financial practices. However, the ongoing Azure subscription cost must be modeled carefully against traditional licensing, especially for long-lived clusters.

## Common Decisions (ADR Triggers)

### Single-node vs. multi-node cluster
Single-node Azure Local is supported for edge locations and smaller footprints. It eliminates S2D replication overhead and reduces hardware cost but sacrifices host-level HA. Record whether your availability requirements permit single-node deployment or mandate multi-node with live migration capability.

### Network ATC vs. manual SDN
Network ATC simplifies configuration by declaring intents (management, compute, storage) and letting the OS configure adapters, VLANs, and QoS. Manual SDN provides finer control but requires deeper networking expertise. Document which approach is selected and the reasoning, especially if integrating with existing network automation.

### Storage Spaces Direct drive configuration
All-NVMe deployments deliver the highest IOPS but at higher cost. NVMe-cache plus SSD-capacity tiers provide a cost-performance balance. HDD capacity tiers are generally not recommended for Azure Local due to performance requirements. Record the drive tier strategy and expected IOPS/throughput targets.

### AKS hybrid vs. traditional VM workloads
Determine whether workloads will run as VMs, containers on AKS hybrid, or a mix. AKS hybrid introduces Kubernetes operational complexity but enables cloud-native deployment patterns and portability. This decision affects cluster sizing, networking, and operational runbooks.

### Stretch clustering vs. separate clusters per site
Stretch clustering provides automatic VM failover between two sites with synchronous storage replication. Separate clusters per site are simpler and work when application-level HA (e.g., SQL Always On, Kubernetes multi-cluster) handles failover. Stretch clustering requires low-latency interconnects (sub-5ms RTT) and doubles storage capacity consumption. Document site topology and RPO/RTO requirements.

### Cloud witness vs. file share witness
Cloud witness (Azure Blob-based) eliminates the need for a third site for quorum. File share witness may be required for fully disconnected deployments. Document the connectivity model and quorum strategy.

### Lifecycle Manager update cadence
Azure Local receives monthly quality updates and periodic feature updates. Lifecycle Manager can stage and apply updates with rolling restarts. Decide on a maintenance window strategy and whether to track the "latest" channel or defer updates. Record the patching SLA and change control integration.

## Reference Architectures

### Branch office / remote site
Two-node or three-node Azure Local cluster at each branch, registered to a central Azure subscription. Azure Arc manages all clusters from a single portal view. VMs run line-of-business applications locally. Azure Backup vaults in the nearest Azure region protect VM data nightly. Azure Monitor workspace aggregates logs and metrics across all branches. Network ATC simplifies branch networking with a single intent for converged management+compute traffic and a separate storage intent.

### AKS hybrid for cloud-native workloads
Four-node Azure Local cluster running AKS hybrid with a highly available control plane (3 control plane VMs). Multiple node pools separate system workloads from application workloads. GitOps (Flux) via Azure Arc for Kubernetes delivers continuous deployment. Azure Container Registry (cloud) or a local registry cache serves container images. Azure Monitor managed Prometheus and Grafana provide observability. This pattern suits development teams migrating from cloud-hosted Kubernetes who need on-prem deployment for data sovereignty.

### Azure Virtual Desktop on-premises
Azure Local cluster sized for AVD session hosts (CPU/RAM heavy, moderate storage). Session hosts registered with the AVD service in Azure. Users connect via AVD gateway endpoints in Azure, with RDP traffic routed to on-prem session hosts. Profile containers stored on S2D volumes or Azure NetApp Files on the cluster. This architecture keeps desktop rendering and user data on-prem while leveraging the Azure AVD control plane for brokering and diagnostics.

### Multi-site HA with stretch clustering
Two-node-per-site stretch cluster across two datacenters within 5ms RTT. Synchronous block-level replication via Storage Replica ensures zero data loss (RPO=0). Cloud witness in Azure provides quorum tie-breaking. VMs automatically fail over to the surviving site during a site outage. This pattern is appropriate for small, critical workloads (file servers, domain controllers, single-instance databases) where application-level clustering is not available or practical.

### SQL Managed Instance on Azure Local
Deploy SQL Managed Instance (Azure Arc-enabled) on an Azure Local cluster for on-prem managed SQL with automated patching, backup to Azure, and Azure Active Directory authentication. Suitable for regulated industries that cannot place SQL databases in public cloud but want managed-service operational benefits. Pair with Azure Defender for SQL for vulnerability assessment and threat detection.

---

## See Also

- `patterns/hybrid-cloud.md` -- Hybrid cloud architecture patterns including on-premises extensions
- `providers/azure/azure-stack-edge.md` -- Edge appliances for smaller or ruggedized on-premises deployments
- `providers/azure/containers.md` -- AKS hybrid running on Azure Local clusters
- `providers/azure/compute.md` -- VM SKU families and compute patterns for Azure workloads
