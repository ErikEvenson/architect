# Nutanix Cloud Clusters (NC2) on Azure

## Scope

Nutanix Cloud Clusters (NC2) on Microsoft Azure: bare-metal host selection and sizing, Azure networking requirements (VNet architecture, delegated subnets, NAT gateways, Flow Gateway), ExpressRoute and VPN connectivity to on-premises, licensing and pricing models, Prism Central management, disaster recovery patterns (NMST, Leap), migration workflows from on-premises to NC2, Entra ID integration, and Azure-specific constraints and limitations.

## Checklist

- [ ] **[Critical]** Is the correct bare-metal SKU selected based on workload requirements -- AN36 (36-core, 576 GB RAM, 18.56 TB SATA SSD + NVMe) for legacy regions, AN36P (36-core, 768 GB RAM, 20.7 TB Optane + NVMe) for most regions, or AN64 (64-core, 1 TB RAM, 38.4 TB NVMe) for compute-dense workloads?
- [ ] **[Critical]** Is the target Azure region confirmed to support the selected SKU -- AN36 (East US, West US 2 only), AN36P (16 regions), AN64 (8 regions including East US 2, North Central US, UK South, Germany West Central)?
- [ ] **[Critical]** Is the cluster sized with minimum 3 nodes and maximum 28 nodes, with capacity planning accounting for Nutanix RF2/RF3 overhead and N+1 node failure tolerance?
- [ ] **[Critical]** Are delegated subnets created in separate VNets (minimum 2, typically 3-4) -- one for the bare-metal cluster, one for Prism Central, optionally a hub VNet for connectivity, and an FGW VNet for S2S VPN -- since Azure allows only 1 delegated subnet per VNet?
- [ ] **[Critical]** Are all delegated subnets configured with the delegation type `Microsoft.BareMetal/AzureHostedService`, and is it understood that NSGs, service endpoints, and private endpoints are NOT supported on these subnets?
- [ ] **[Critical]** Are two NAT gateways provisioned with the tag `fastpathenabled` set to `true` before deployment -- the NC2 portal validates this and blocks deployment without it?
- [ ] **[Critical]** Is custom DNS configured on every VNet before cluster deployment -- deployments to VNets using Azure-provided default DNS will fail?
- [ ] **[Critical]** Is full-mesh VNet peering established between all VNets (cluster, Prism Central, hub, FGW) before cluster creation?
- [ ] **[Recommended]** Is Flow Virtual Networking (FVN) evaluated for overlay networking -- FVN creates up to 500+ subnets while consuming only 1 Azure VNet, abstracting Azure's delegated subnet constraints?
- [ ] **[Recommended]** If using FVN in scale-out mode (2-4 Flow Gateway instances), is Azure Route Server (ARS) deployed for BGP peering, with awareness that each FGW consumes 2 BGP sessions and ARS has a soft limit of 8 sessions (max 4 FGW)?
- [ ] **[Recommended]** Are Flow Gateway VMs sized appropriately -- Standard_D4v4 for small deployments (10-16 Gbps single-mode) or Standard_D32_v4 for large deployments, with 2-4 active-active instances for scale-out?
- [ ] **[Recommended]** Is on-premises connectivity established via ExpressRoute (preferred) or Site-to-Site VPN -- noting that Active/Active VPN gateways, Active/Active Zone Redundant gateways, and ExpressRoute FastPath are NOT supported with NC2?
- [ ] **[Recommended]** Is the licensing model selected -- BYOL (portable capacity-based licenses, 1-5 year terms), Azure Marketplace PAYG (per-node hourly billing), or 30-day free trial (one-time, non-pausable, non-resettable)?
- [ ] **[Recommended]** Are Azure Reserved Instances evaluated for cost optimization -- 36% discount for 1-year commitment, 57% discount for 3-year commitment on bare-metal hosts?
- [ ] **[Recommended]** Is Microsoft Azure Consumption Commitment (MACC) eligibility confirmed -- NC2 infrastructure costs count toward existing MACC agreements?
- [ ] **[Recommended]** Is the Azure subscription allowlisted for NC2, with a Microsoft Entra ID app registration created with Contributor role on the subscription?
- [ ] **[Recommended]** Is Nutanix Move deployed for VM migration from on-premises Nutanix, VMware, Hyper-V, or AWS to NC2 Azure -- supporting lift-and-shift without application refactoring?
- [ ] **[Recommended]** Is the DR strategy selected -- zero-compute cold DR (snapshots to Azure Blob, cluster deployed on-demand, lowest cost, longest RTO) vs pilot-light warm DR (minimum 3-node NC2 cluster running NMST, fast RTO for tier-1 apps)?
- [ ] **[Recommended]** Are Nutanix Leap protection policies configured with appropriate RPO targets -- Asynchronous (1-24 hour RPO), Near-Synchronous (1-15 minute RPO), or Synchronous (zero RPO) for replication between on-premises and NC2 Azure?
- [ ] **[Optional]** Is Nutanix Unified Storage (NUS) evaluated as an add-on for Files and Objects workloads on NC2 Azure ($0.112/TiB, first 1 TiB free)?
- [ ] **[Optional]** Is Azure Hybrid Benefit applied to reuse existing Windows Server and SQL Server licenses with Software Assurance, including free Extended Security Updates (ESUs) for Windows Server VMs on NC2?
- [ ] **[Optional]** Is cross-region connectivity evaluated using Azure vWAN (supported for transit connectivity and NVA traffic inspection) since cross-region VNet peering without vWAN is NOT supported for NC2?

## Why This Matters

NC2 on Azure extends on-premises Nutanix clusters to Azure bare-metal infrastructure, providing a consistent management experience through Prism Central across hybrid environments. This eliminates the need to refactor applications or retrain operations teams when migrating workloads to Azure. However, Azure's delegated subnet model imposes significant networking constraints -- the requirement for separate VNets per delegated subnet, the prohibition on NSGs for bare-metal subnets, and the IPv4-only limitation create a fundamentally different network architecture than native Azure deployments. Poor planning of the multi-VNet topology and Flow Gateway sizing leads to throughput bottlenecks and connectivity failures that are difficult to remediate post-deployment. The licensing model choice has major cost implications: PAYG pricing for AN36P is $3.744-$4.716/hr per node ($32,770-$41,292/yr), while 3-year reserved instances reduce this by 57%. Organizations with existing Nutanix capacity-based licenses can use BYOL to avoid double-paying. The DR capabilities (NMST with zero-compute or pilot-light patterns) provide cost-effective cloud DR without maintaining always-on infrastructure, but the 30-day trial limitation means DR testing must be carefully planned. AHV is the only supported hypervisor on NC2 Azure -- organizations currently running Nutanix on ESXi must plan for hypervisor conversion before migrating to NC2.

## Common Decisions (ADR Triggers)

- **Bare-metal SKU** -- AN36P (balanced, broadest region availability, 768 GB RAM) vs AN64 (compute-dense, 1 TB RAM, 128 vCPUs, fewer regions) vs AN36 (legacy, only 2 regions, avoid for new deployments)
- **Connectivity model** -- ExpressRoute (preferred, can share PC VNet) vs Site-to-Site VPN (requires dedicated FGW VNet, no Active/Active support) vs Azure vWAN (transit connectivity, supports NVA inspection)
- **Overlay networking** -- Flow Virtual Networking (abstracts Azure constraints, 500+ subnets from 1 VNet, requires FGW VMs) vs native Azure VNet peering (simpler, limited by 1 delegated subnet per VNet)
- **FGW deployment mode** -- Single-mode (1 FGW, 10-16 Gbps, simpler) vs scale-out mode (2-4 FGW, requires Azure Route Server, higher throughput, BGP session limits)
- **Licensing** -- BYOL (portable CBLs, predictable cost) vs PAYG via Azure Marketplace (operational expense, no commitment) vs Reserved Instances (36-57% discount, commitment required)
- **DR pattern** -- Zero-compute cold DR (NMST snapshots to Blob, cheapest, longest RTO) vs pilot-light warm DR (3-node cluster running, fast RTO for tier-1 apps, higher cost) vs always-on active-active (Synchronous Leap, zero RPO, highest cost)
- **Hybrid cloud strategy** -- NC2 on Azure (consistent Nutanix management across hybrid) vs Azure native VMs (Azure-native tools, no Nutanix licensing) vs VMware Cloud on Azure (VMware ecosystem continuity)
- **Hypervisor conversion** -- Pre-migration conversion to AHV on-premises (Move tool, test before cloud move) vs migrate-and-convert to AHV on NC2 (single step, less pre-testing)

## Version Notes

| Feature | NC2 on Azure GA (2023) | Current (2025-2026) |
|---|---|---|
| SKUs | AN36 (2 regions) | AN36, AN36P (16 regions), AN64 (8 regions) |
| Max cluster size | 28 nodes | 28 nodes |
| Flow Virtual Networking | Limited | GA (FGW active-active, scale-out with ARS) |
| NMST (Multicloud Snapshots) | Preview | GA (Azure Blob, AWS S3 targets) |
| Nutanix Leap | Async replication | Async, Near-Sync, Synchronous replication |
| vWAN support | Not available | GA (transit connectivity, Secure vWAN) |
| NUS (Unified Storage) | Not available | GA (Files/Objects add-on) |
| Azure Portal deployment | Not available | GA (deploy/manage via Azure Portal, CLI, PowerShell) |

**Key changes:**
- **AN64 SKU:** Newest addition with Intel 8462Y+ 64-core processors, 1 TB RAM, and 38.4 TB all-NVMe storage. Available in 8 regions. Best for compute-dense workloads (databases, analytics) that previously required multiple AN36P nodes.
- **Flow Virtual Networking:** Matured from limited overlay networking to full FGW active-active with scale-out mode. AOS 6.7+ supports 2-4 FGW instances with Azure Route Server for BGP-based routing. Eliminates most Azure delegated subnet constraints for overlay traffic.
- **NMST:** Nutanix Multicloud Snapshot Technology enables cost-effective DR to Azure Blob Storage without maintaining a running NC2 cluster. NMST Engine runs alongside Prism Central and manages snapshot replication schedules.
- **Azure Portal integration:** NC2 clusters can now be provisioned and managed through Azure Portal, CLI, and PowerShell in addition to the NC2 Console and Prism Central, improving integration with Azure governance workflows.

## Responsibility Matrix

| Area | Microsoft | Nutanix | Customer |
|---|---|---|---|
| Bare-metal hardware | Manages | -- | -- |
| Underlay network and data/control plane | Manages | -- | -- |
| Nutanix software lifecycle (AOS, AHV, PC) | -- | Manages | -- |
| Nutanix licenses | -- | Manages | Purchases |
| Azure networking (VNet, NAT, peering, vWAN) | Supports | -- | Configures |
| Flow Gateway and overlay networking | -- | Supports | Configures |
| Workload VMs and applications | -- | -- | Manages |

## See Also

- [Microsoft Learn: NC2 on Azure Architecture](https://learn.microsoft.com/en-us/azure/baremetal-infrastructure/workloads/nc2-on-azure/architecture) -- official Azure architecture documentation
- [Microsoft Learn: NC2 Available Regions and SKUs](https://learn.microsoft.com/en-us/azure/baremetal-infrastructure/workloads/nc2-on-azure/available-regions-skus) -- current region and SKU availability
- [Microsoft Learn: NC2 on Azure Getting Started](https://learn.microsoft.com/en-us/azure/baremetal-infrastructure/workloads/nc2-on-azure/get-started) -- prerequisites and deployment guide
- [Nutanix Bible: NC2 on Azure](https://www.nutanixbible.com/10b-book-of-nutanix-clusters-azure.html) -- comprehensive technical deep-dive
- [Nutanix NC2 Pricing](https://www.nutanix.com/products/nutanix-cloud-clusters/pricing) -- PAYG, reserved instance, and add-on pricing
- `providers/nutanix/platform-services.md` -- Nutanix platform services including NC2 overview
- `providers/nutanix/infrastructure.md` -- core Nutanix infrastructure sizing and configuration
- `providers/nutanix/networking.md` -- AHV networking and Flow microsegmentation
- `providers/nutanix/migration-tools.md` -- Nutanix Move and migration workflows
- `providers/nutanix/data-protection.md` -- Leap, NMST, and replication policies
- `providers/azure/compute.md` -- Azure compute for comparison with NC2 bare-metal
- `providers/azure/networking.md` -- Azure VNet, ExpressRoute, and vWAN
- `patterns/hybrid-cloud.md` -- hybrid cloud architecture patterns
- `patterns/hypervisor-migration.md` -- hypervisor conversion strategies
