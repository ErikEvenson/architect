# Azure Stack HCI on Azure (Cloud-Hosted HCI)

## Scope

Running Azure Local (formerly Azure Stack HCI) on Azure bare-metal infrastructure rather than on customer-owned on-premises hardware. Covers Tier 0 security enclaves, sovereign and air-gapped workloads in Azure datacenters, coexistence with Nutanix Cloud Clusters (NC2) on shared bare-metal infrastructure, networking isolation, failover clustering, licensing, and comparison with standard Azure VMs and on-premises Azure Local deployments.

This pattern addresses scenarios where organizations need the security properties of dedicated, non-hypervisor-shared hardware within Azure datacenters — for example, Active Directory domain controllers, PKI infrastructure, or classified workloads that cannot run on shared multi-tenant hypervisors — while still consuming Azure as the hosting platform.

## Checklist

- [ ] **[Critical]** Confirm that Azure BareMetal Infrastructure SKUs are available in the target Azure region; availability varies by region and bare-metal capacity is provisioned on request with lead times
- [ ] **[Critical]** Define the security classification and isolation requirements that justify bare-metal HCI over standard Azure VMs; document why Hyper-V on dedicated hardware is required (e.g., Tier 0 AD, PKI, HSM-dependent workloads, FIPS 140-2 Level 3 boundary)
- [ ] **[Critical]** Design network isolation: provision dedicated VNets and subnets for the HCI cluster; plan for air-gapped segments where no internet egress is permitted; understand that NSGs operate at the VNet/subnet level and do not filter traffic at the bare-metal NIC layer
- [ ] **[Critical]** Plan failover clustering: configure Windows Server Failover Clustering (WSFC) across bare-metal nodes with a cloud witness (Azure Storage Account) for quorum; validate that bare-metal node-to-node latency meets sub-1ms requirements for Storage Spaces Direct heartbeat
- [ ] **[Critical]** Configure Storage Spaces Direct (S2D) across bare-metal nodes: select NVMe/SSD drive tiers, plan volume layout for cluster shared volumes (CSVs), and validate storage network bandwidth (RDMA or high-speed Ethernet between nodes)
- [ ] **[Critical]** Register the HCI cluster with Azure Arc for management plane integration; in air-gapped scenarios, plan for Azure Arc gateway or periodic connected windows for registration and billing heartbeat
- [ ] **[Critical]** Plan Active Directory topology: if hosting Tier 0 domain controllers on HCI, ensure the AD site design, replication topology, and FSMO role placement account for the cloud-hosted bare-metal location as a distinct AD site
- [ ] **[Recommended]** Evaluate coexistence with Nutanix Cloud Clusters (NC2) on Azure if the organization also runs NC2; both consume Azure BareMetal Infrastructure and share the same underlying physical infrastructure pool — coordinate capacity planning and rack placement
- [ ] **[Recommended]** Deploy Windows Admin Center (WAC) for cluster management; in cloud-hosted scenarios, WAC can run as a VM on the HCI cluster or on a management jump box within the same isolated VNet; plan for access via Azure Bastion or VPN if internet-facing access is prohibited
- [ ] **[Recommended]** Configure Microsoft Defender for Cloud with the Defender for Servers plan on all HCI nodes and guest VMs; enable Secured-core server features (Secure Boot, TPM 2.0, DRTM, VBS) on bare-metal nodes where hardware supports it
- [ ] **[Recommended]** Enable BitLocker volume encryption on all cluster shared volumes (infrastructure and workload); store BitLocker recovery keys in a secure location outside the HCI cluster (e.g., Azure Key Vault in a separate subscription if connectivity permits)
- [ ] **[Recommended]** Plan Azure Monitor integration: deploy Azure Monitor Agent on HCI nodes and guest VMs; configure Log Analytics workspace for security event collection; set up syslog forwarding (CEF format) to a SIEM if required by compliance
- [ ] **[Recommended]** Design backup strategy using Azure Backup for VM-level protection; for air-gapped segments, plan for local backup targets (S2D volumes or attached storage) with periodic data export when connectivity windows allow
- [ ] **[Recommended]** Document the licensing model: Azure Local subscription billing (per physical core per month) applies; BareMetal Infrastructure hosting fees are separate; Windows Server guest licensing is included in the Azure Local subscription; model total cost against standard Azure VM alternatives
- [ ] **[Optional]** Plan Azure Site Recovery (ASR) for DR between the cloud-hosted HCI cluster and a secondary Azure region or on-premises site; in air-gapped scenarios, ASR may not be viable and manual VM export/import procedures may be required
- [ ] **[Optional]** Deploy AKS hybrid on the HCI cluster if containerized workloads are in scope alongside traditional VMs; evaluate whether the security isolation requirements permit Kubernetes control plane components
- [ ] **[Optional]** Configure Application Control (WDAC) policies in Enforcement mode on HCI nodes to restrict executable code to a validated allowlist; this is enabled by default on Azure Local but verify policies are not set to Audit-only in high-security deployments
- [ ] **[Optional]** Plan for secret rotation and certificate management: Azure Local autorotates internal certificates before expiry; integrate with an enterprise PKI if guest workloads require certificates from a specific CA chain

## Why This Matters

Standard Azure VMs run on a shared multi-tenant hypervisor. For most workloads this is acceptable, but certain security-sensitive systems — Active Directory Tier 0, PKI root CAs, hardware security module integrations, and classified or sovereign workloads — require dedicated hardware where the organization controls the hypervisor layer. Running Azure Local on Azure BareMetal Infrastructure provides this: the customer gets dedicated physical servers within an Azure datacenter, runs Hyper-V under their own control, and manages VMs through the familiar HCI/Azure Arc management plane.

This pattern avoids the cost and complexity of maintaining on-premises datacenters while still meeting the isolation requirements that prevent these workloads from running on shared Azure compute. It is particularly relevant for organizations that have consolidated most infrastructure into Azure but retain a small number of workloads that cannot tolerate shared hypervisor tenancy.

The trade-off is operational complexity. BareMetal nodes require the customer to manage the OS, hypervisor, clustering, storage, and patching — responsibilities that Azure handles transparently for standard VMs. The customer must also navigate BareMetal-specific networking constraints, where NSGs and certain Azure networking features do not apply at the physical NIC level the same way they do for standard VMs.

## Common Decisions (ADR Triggers)

### Azure Stack HCI on Azure vs. standard Azure VMs for Tier 0 workloads
Standard Azure VMs run on shared hypervisors managed by Microsoft. If the security model requires dedicated hardware, hypervisor control, and no co-tenancy, Azure VMs are disqualified regardless of VM isolation features (Dedicated Hosts, Confidential VMs). HCI on BareMetal provides full hypervisor ownership. Record the specific security requirement (regulation, policy, or threat model) that drives this decision, as the operational and cost overhead is significant.

### Azure Stack HCI on Azure vs. on-premises Azure Local
On-premises Azure Local places hardware in customer-owned facilities, giving full physical security control. Cloud-hosted HCI on BareMetal places hardware in Microsoft-operated Azure datacenters, trading physical access for the benefits of Azure datacenter infrastructure (power, cooling, physical security, network backbone). Choose on-premises when physical access, physical security chain-of-custody, or data sovereignty laws require customer-controlled facilities. Choose cloud-hosted when the goal is to eliminate on-premises datacenter operations while retaining hypervisor-level isolation.

### Air-gapped isolation vs. connected deployment
Fully air-gapped segments within Azure require careful planning for Azure Arc registration, billing heartbeat, OS updates, and backup. Azure Local requires periodic Azure connectivity for subscription billing validation (30-day grace period). If continuous air-gap is mandatory, document the connectivity window strategy and the impact on Azure management plane features. Connected deployments get full Azure portal management, Azure Monitor, Defender for Cloud, and Azure Backup integration out of the box.

### Cloud witness vs. file share witness for quorum
In Azure-hosted HCI, a cloud witness (Azure Storage Account) is the natural choice for cluster quorum since the nodes are already in Azure and have access to Azure Storage endpoints. File share witness is only needed if the HCI cluster is in a fully air-gapped segment that cannot reach any Azure Storage endpoint. Document the quorum strategy and ensure the witness storage account is in a different availability zone or region from the HCI nodes.

### Coexistence with NC2 on Azure
If the organization also runs Nutanix Cloud Clusters (NC2) on Azure, both solutions draw from the same Azure BareMetal Infrastructure capacity pool. Coordinate with Microsoft and Nutanix on capacity reservations to avoid contention. Document whether the HCI and NC2 workloads share the same VNet (with subnet-level isolation) or use separate VNets with peering. This decision affects network security boundaries and blast radius.

### Network security model for bare-metal nodes
Azure NSGs apply to VNet-attached NICs but bare-metal nodes connect to the network differently than standard VMs. Plan for host-based firewall rules (Windows Firewall with Advanced Security) as the primary network access control on bare-metal nodes, supplemented by VNet-level NSGs on subnets. Document whether Azure Firewall or a third-party NVA is placed in the path for east-west and north-south traffic inspection.

### Management access model
Decide how administrators access the HCI cluster: Azure Bastion into a jump box VM, site-to-site VPN, ExpressRoute private peering, or Azure Arc-based remote management. For air-gapped segments, physical or KVM-over-IP console access through the BareMetal management plane may be required. Record the access method and its compliance with the security classification of hosted workloads.

## Reference Architectures

### Tier 0 Active Directory enclave on Azure BareMetal
Two or three Azure BareMetal nodes running Azure Local with WSFC and S2D. Dedicated VNet with no internet egress (UDR forcing all traffic through Azure Firewall with deny-all outbound rules). Domain controllers, PKI subordinate CAs, and AD Connect health agents run as Hyper-V VMs on the HCI cluster. Cloud witness for quorum using a storage account accessible via private endpoint. Azure Arc registration performed during an initial connected window, then connectivity restricted to billing heartbeat only. Windows Admin Center runs on a management VM within the enclave VNet, accessed via Azure Bastion. Azure Monitor Agent forwards security events to a dedicated Log Analytics workspace. Defender for Cloud monitors the nodes and guest VMs with Defender for Servers Plan 2.

### Sovereign workload cluster with NC2 coexistence
Organization operates both Azure Local HCI and NC2 on Azure in the same region. HCI cluster (two nodes) hosts Windows-based sovereign workloads (AD, file services, legacy .NET applications). NC2 cluster hosts Linux-based workloads on AHV. Each solution occupies a separate VNet peered through a hub VNet containing Azure Firewall for traffic inspection. BareMetal capacity is reserved under a single Azure subscription with resource groups separating HCI and NC2 resources. Both clusters use Azure Arc for management plane integration. Backup for HCI VMs uses Azure Backup with a Recovery Services vault; NC2 workloads use Nutanix-native backup tooling.

### Security-sensitive application platform
Four-node Azure Local cluster on BareMetal running a mix of Tier 0 infrastructure (domain controllers, certificate services) and Tier 1 application servers (SQL Server Always On FCI, IIS web farms). S2D with all-NVMe drives for SQL IOPS requirements. Network segmentation via Hyper-V virtual switches with separate VLANs for Tier 0 and Tier 1 traffic. Azure Firewall in the hub VNet inspects all north-south traffic. No direct internet access from any guest VM. Azure Update Manager handles OS patching through a connected maintenance window. Azure Site Recovery replicates Tier 1 application VMs to a secondary Azure region for DR; Tier 0 DCs rely on AD-native replication to DCs in standard Azure VMs in the DR region.

---

## Reference Links

- [Azure Local documentation](https://learn.microsoft.com/en-us/azure/azure-local/) -- cluster deployment, Storage Spaces Direct, and Azure Arc management
- [Azure BareMetal Infrastructure documentation](https://learn.microsoft.com/en-us/azure/baremetal-infrastructure/) -- bare-metal provisioning, SKUs, and networking for dedicated hardware in Azure datacenters
- [Azure Arc overview](https://learn.microsoft.com/en-us/azure/azure-arc/overview) -- hybrid and multi-cloud management plane for servers, Kubernetes, and data services

## See Also

- `providers/azure/azure-local.md` -- On-premises Azure Local (Azure Stack HCI) deployment and management
- `providers/azure/compute.md` -- Azure VM SKU families including Dedicated Host and Confidential VMs
- `providers/azure/networking.md` -- Azure VNet design, NSGs, Azure Firewall, and ExpressRoute
- `providers/azure/security.md` -- Azure security services including Defender for Cloud and Key Vault
- `providers/azure/identity.md` -- Azure AD and Active Directory hybrid identity patterns
- `providers/azure/disaster-recovery.md` -- Azure Site Recovery and backup strategies
- `patterns/hybrid-cloud.md` -- Hybrid cloud architecture patterns
