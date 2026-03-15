# Azure VMware Solution (AVS)

Microsoft-operated VMware private cloud running on dedicated Azure bare-metal nodes. Provides full VMware stack (vSphere, vSAN, NSX-T, vCenter, HCX) with native Azure service and identity integration.

## Checklist

- [ ] **[Critical]** Node type selection: AV36P (36 cores, 576GB RAM, 15.4TB NVMe, current standard), AV52 (memory-optimized, 52 cores, 768GB RAM), or AV36 (older, limited availability)?
- [ ] **[Critical]** Private cloud sizing: minimum 3 nodes per cluster, up to 16 nodes per cluster, max 12 clusters per private cloud?
- [ ] **[Critical]** Networking: ExpressRoute connection to Azure VNet (required, dedicated circuit), ExpressRoute Global Reach for on-prem connectivity?
- [ ] **[Critical]** Migration plan: HCX (included with AVS) for bulk migration, vMotion, or replication-assisted vMotion?
- [ ] **[Critical]** Pricing model: pay-as-you-go (per-node hourly) or 1yr/3yr reserved instances (up to 60% savings)?
- [ ] **[Critical]** Azure region selection: verify AVS availability and compliance requirements (FedRAMP, HIPAA on Azure Government)?
- [ ] **[Recommended]** Storage expansion: vSAN only, or add Azure NetApp Files / Azure Elastic SAN for additional capacity?
- [ ] **[Recommended]** Azure service integration: which Azure services (Azure SQL, Blob Storage, AKS, Azure Functions) will VMware VMs consume?
- [ ] **[Recommended]** Identity integration: Azure AD for vCenter SSO, RBAC roles mapped to Azure AD groups?
- [ ] **[Recommended]** NSX-T network design: segments, distributed firewall rules, T0/T1 gateway topology, DNS forwarding?
- [ ] **[Recommended]** Monitoring strategy: Azure Monitor integration, Azure Arc-enabled VMware VMs, or VMware Aria?
- [ ] **[Recommended]** DR strategy: VMware SRM, Azure Site Recovery, JetStream DR, or cross-region AVS?
- [ ] **[Optional]** Run Command for day-2 operations: automated scripts executed on AVS private cloud via Azure portal?
- [ ] **[Optional]** Placement policies: VM-VM affinity/anti-affinity, VM-host affinity for licensing or compliance?
- [ ] **[Optional]** Internet connectivity method: AVS-managed SNAT, Azure public IP to NSX-T edge, or route through Azure VNet NVA?

## Why This Matters

AVS provides a path to Azure for VMware-dependent workloads without re-platforming. The minimum 3-node requirement means a baseline cost of ~$30K+/month — under-utilizing nodes is extremely expensive. ExpressRoute is the only connectivity option to Azure VNets (no VPN gateway support), so networking design is non-negotiable. Azure AD integration is a differentiator: if the organization already uses Azure AD, AVS provides seamless identity across VMware and Azure-native workloads. Not planning external storage early leads to vSAN capacity crunches since node storage is fixed.

## Common Decisions (ADR Triggers)

| Decision | When to Create ADR |
|----------|-------------------|
| Node type selection | Always — AV36P vs. AV52 determines compute/memory ratio and cost |
| vSAN-only vs. external storage | When storage needs exceed vSAN capacity — ANF adds NFS datastores without adding nodes |
| ExpressRoute topology | Always — Global Reach for on-prem, FastPath for high-throughput Azure service access |
| Azure AD integration scope | Always — determines vCenter access model and RBAC strategy |
| DR approach selection | When DR is required — SRM vs. ASR vs. JetStream have different RPO/RTO and cost profiles |
| Internet connectivity method | When VMs need internet — managed SNAT is simplest, Azure public IP is most flexible |
| Monitoring tooling | When observability is scoped — Azure Monitor vs. VMware Aria vs. hybrid approach |
| Reserved instance commitment | Always — pay-as-you-go vs. 1yr vs. 3yr is a major cost decision |

## Reference Architectures

- **Azure Hybrid Extension**: on-prem vSphere + AVS connected via ExpressRoute Global Reach, Azure AD SSO across both, Azure services via ExpressRoute to VNet
- **Windows Workload Modernization**: Windows Server VMs on AVS with Azure AD integration, Azure SQL as managed database, Azure Blob for file storage
- **Oracle on AVS**: Oracle databases on VMware VMs (preserving Oracle licensing terms), Azure services for application tier, ExpressRoute for low-latency connectivity
- **DR to Azure**: on-prem primary site, AVS as DR target using SRM or JetStream, Azure Blob for backup storage via Azure Backup
- **Regulated Workloads**: AVS on Azure Government for FedRAMP/HIPAA compliance, NSX-T microsegmentation, Azure Policy for governance, Azure Sentinel for SIEM

## Key Constraints

- Minimum 3 nodes per cluster (no single-node dev option like VMC on AWS)
- ExpressRoute is mandatory for Azure VNet connectivity — no VPN alternative
- Microsoft manages the underlying infrastructure — no direct ESXi host access
- vCenter admin credentials available but CloudAdmin role (not root); some operations require Run Command
- HCX is included at no additional cost (unlike VMC where it is an add-on)
- Quota request required — AVS nodes must be requested and approved per Azure subscription per region
