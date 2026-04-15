# Kyndryl Private Cloud (KPC)

## Scope

Kyndryl Private Cloud (KPC) as a managed infrastructure service: service tiers (IaaS, PaaS, AI Private Cloud, Distributed Cloud for Azure Stack), consumption-based pricing models, supported hypervisors and hardware platforms, deployment options (Kyndryl-hosted vs customer-hosted), management and operations model, capacity planning for KPC engagements, and migration considerations when moving workloads onto KPC. This file covers the KPC platform itself -- for specific hypervisor or hardware decisions within a KPC deployment, see the relevant provider files (e.g., `providers/nutanix/infrastructure.md`, `providers/vmware/hypervisor.md`, `providers/microsoft/azure-stack-hci.md`). For migration patterns to KPC, see `patterns/datacenter-relocation.md` and `patterns/hypervisor-migration.md`.

## Checklist

### Service Model Selection

- [ ] **[Critical]** Is the KPC service tier selected based on workload requirements -- KPC IaaS (compute, storage, networking as-a-service), KPC PaaS (managed platform layer), KPC AI Private Cloud (dedicated AI/ML infrastructure), or Kyndryl Distributed Cloud for Azure Stack (Azure Stack HCI with Azure Arc management)?
- [ ] **[Critical]** Is the deployment model confirmed -- Kyndryl-hosted (infrastructure in a Kyndryl data center) vs customer-hosted (Kyndryl manages infrastructure at customer premises)? This determines facility responsibility, physical security ownership, and network connectivity requirements.
- [ ] **[Critical]** Is the billing model agreed -- pay-per-use consumption (monthly billing for actual usage), reserved capacity (committed tiers with discounts), or hybrid (reserved baseline + burst capacity on demand)? KPC eliminates CapEx by converting infrastructure to OpEx.
- [ ] **[Critical]** Is the scope boundary between Kyndryl-managed and customer-managed responsibilities documented? KPC is fully managed, but integration points (AD, DNS, monitoring, backup targets, network connectivity) require clear RACI definition.

### Platform and Hypervisor

- [ ] **[Critical]** Is the hypervisor platform selected for the KPC deployment? KPC supports multiple platforms including VMware vSphere, Nutanix AHV, Microsoft Azure Stack HCI, and Red Hat OpenShift Virtualization. The choice affects licensing costs (especially post-Broadcom VMware pricing), operational tooling, migration complexity, and available ecosystem integrations.
- [ ] **[Critical]** Is the hardware platform selected -- Dell PowerEdge, HPE ProLiant, Cisco UCS, Lenovo ThinkSystem, or Nutanix NX/Dell XC? Hardware selection must align with the chosen hypervisor and any existing vendor relationships, support contracts, or procurement agreements.
- [ ] **[Recommended]** If VMware is the current hypervisor, is a VMware optimization or alternative hypervisor assessment being conducted? Kyndryl offers VMware modernization services that evaluate alternatives (Nutanix AHV, Azure Stack HCI, Red Hat OpenShift) to control TCO and reduce vendor lock-in under Broadcom's new licensing model.
- [ ] **[Recommended]** Is the management platform defined -- vCenter (VMware), Prism Central (Nutanix), Windows Admin Center/Azure Arc (Azure Stack HCI), or a Kyndryl unified management layer? This determines operational workflows, monitoring integration, and automation capabilities.
- [ ] **[Optional]** Is multi-hypervisor operation required? KPC can support dual-platform environments (e.g., Nutanix AHV for general workloads + Azure Stack HCI for security-critical Tier 0) but this adds operational complexity and requires skills in both platforms.

### Capacity and Sizing

- [ ] **[Critical]** Is capacity planning based on actual workload metrics (vCPU, memory, storage IOPS, network throughput) rather than current host specifications? KPC consumption billing means right-sizing directly impacts monthly cost.
- [ ] **[Critical]** Is storage tiering defined -- performance tier (NVMe/SSD for databases, OLTP), standard tier (SSD for general workloads), and archive tier (HDD/object storage for backup, cold data)? KPC offers multiple storage tiers with different price points.
- [ ] **[Recommended]** Is a growth buffer included in capacity planning? KPC pay-per-use allows scaling, but lead time for physical hardware provisioning (if Kyndryl-hosted) may require pre-positioned capacity for burst scenarios.
- [ ] **[Recommended]** Is the network bandwidth between KPC and customer environments (offices, other data centers, public cloud) sized for both steady-state operations and peak migration periods?
- [ ] **[Optional]** Is a capacity governance model defined to prevent uncontrolled consumption growth? Without CapEx constraints, OpEx consumption models can grow faster than budgeted if not actively managed.

### Operations and SLAs

- [ ] **[Critical]** Are SLA targets defined for the KPC engagement -- VM uptime (e.g., 99.95%, 99.99%), storage durability, backup RPO/RTO, patching cadence, and incident response times? KPC SLAs should be contractually documented in the managed services agreement.
- [ ] **[Critical]** Is the patching and maintenance model agreed -- Kyndryl-managed patching windows, customer-approved change windows, or automated rolling updates? This affects uptime guarantees and compliance posture.
- [ ] **[Recommended]** Is monitoring and alerting integrated between KPC infrastructure and the customer's existing ITSM/observability stack (ServiceNow, Splunk, Datadog, etc.)? Kyndryl provides infrastructure monitoring, but application-level observability typically remains customer-owned.
- [ ] **[Recommended]** Is a disaster recovery strategy defined for KPC-hosted workloads -- cross-site replication to a second KPC location, replication to public cloud, or backup-based DR with defined RTO?
- [ ] **[Optional]** Is a cloud exit strategy documented? While KPC is consumption-based with no long-term commitment, data gravity and operational dependencies can create de facto lock-in. Document the process and timeline for migrating workloads off KPC if needed.

### Migration to KPC

- [ ] **[Critical]** Is the migration approach defined -- lift-and-shift (same hypervisor, Kyndryl relocates), hypervisor conversion during migration (e.g., VMware to AHV), or re-platform (rebuild on KPC)?
- [ ] **[Critical]** Is the network connectivity between source environment and target KPC established before migration begins? Options: dedicated circuit (MPLS, point-to-point), VPN, ExpressRoute/Direct Connect (if KPC integrates with public cloud), or physical data transport for bulk seeding.
- [ ] **[Recommended]** Is the migration wave plan aligned with KPC capacity provisioning? Hardware must be racked, cabled, and commissioned at the KPC facility before workloads can migrate -- confirm lead times with Kyndryl.
- [ ] **[Recommended]** Are application dependency groups identified so that tightly coupled VMs (app tier + database + load balancer) migrate together within the same wave?
- [ ] **[Optional]** Is a parallel-run or pilot phase planned before full migration -- migrate a non-critical site or workload group first to validate KPC operations, monitoring, and connectivity?

### Compliance and Security

- [ ] **[Critical]** Is the KPC deployment location compliant with data residency requirements? If workloads have geographic constraints (GDPR, data sovereignty), confirm the Kyndryl data center location satisfies those requirements.
- [ ] **[Critical]** Is the security boundary between KPC tenants confirmed as single-tenant (dedicated hardware)? KPC IaaS is single-tenant by design, but verify this extends to network isolation, storage isolation, and management plane separation.
- [ ] **[Recommended]** Is the compliance certification scope confirmed -- does the KPC facility and Kyndryl operations hold required certifications (SOC 2, ISO 27001, PCI DSS, HIPAA) applicable to the customer's workloads?
- [ ] **[Recommended]** Is encryption at rest and in transit configured for all KPC storage and network paths? Confirm key management ownership -- Kyndryl-managed keys vs customer-managed keys (BYOK).

### Integration with Public Cloud

- [ ] **[Recommended]** If the customer has existing public cloud presence (Azure, AWS, GCP), is hybrid connectivity between KPC and public cloud established? KPC can complement public cloud for workloads requiring dedicated infrastructure while maintaining connectivity to cloud-native services.
- [ ] **[Recommended]** Is Kyndryl Distributed Cloud for Azure Stack evaluated for workloads requiring Azure consistency? This provides Azure Stack HCI managed by Kyndryl with Azure Arc for unified management across on-premises and Azure.
- [ ] **[Optional]** Is a cloud-adjacent KPC deployment evaluated -- Kyndryl facilities co-located with or directly connected to public cloud regions for low-latency hybrid architectures?

## Why This Matters

Kyndryl Private Cloud converts infrastructure from a capital expenditure to an operational expense with consumption-based billing, but the choice of service tier, hypervisor, and deployment model has long-term implications for cost, operational complexity, and migration flexibility. Selecting the wrong hypervisor platform locks the organization into a vendor ecosystem that may not align with strategic direction -- particularly relevant as VMware licensing under Broadcom shifts to subscription-based pricing that can increase costs 2-5x. Under-sizing capacity creates performance issues that are visible to end users, while over-sizing wastes budget on a consumption model where every allocated resource has a direct monthly cost. The SLA and operations model must be contractually precise: "fully managed" means different things to different parties, and ambiguity in patching windows, incident response, or change management creates friction during production incidents. Migration to KPC carries the same risks as any datacenter relocation -- application dependency mapping, network cutover planning, and rollback procedures are essential regardless of the managed service wrapper. Finally, while KPC's pay-per-use model offers flexibility, organizations must implement consumption governance to prevent OpEx sprawl that exceeds the CapEx costs it was meant to replace.

## Common Decisions (ADR Triggers)

- **Service tier** -- KPC IaaS (infrastructure only, maximum flexibility) vs KPC PaaS (platform management included, less operational burden) vs KPC AI Private Cloud (specialized AI/ML workloads) vs Distributed Cloud for Azure Stack (Azure ecosystem alignment)
- **Hypervisor platform** -- VMware vSphere (ecosystem continuity, higher licensing cost) vs Nutanix AHV (HCI-native, competitive licensing) vs Azure Stack HCI (Azure integration, Hyper-V based) vs Red Hat OpenShift Virtualization (container-first, VM support)
- **Deployment location** -- Kyndryl data center (Kyndryl owns facility) vs customer premises (Kyndryl manages, customer owns facility) vs co-located with public cloud region (hybrid connectivity)
- **Pricing model** -- Pay-per-use consumption (flexibility, no commitment) vs reserved capacity (discount, committed spend) vs hybrid baseline + burst
- **Migration approach** -- Same-hypervisor relocation (lowest risk) vs hypervisor conversion during migration (consolidates two changes) vs phased conversion then relocation (lower risk, longer timeline)
- **Dual-platform operation** -- Single hypervisor for all workloads (simpler operations) vs dedicated platform for security-critical workloads (e.g., Azure Stack HCI for Tier 0 AD + AHV for general workloads)
- **DR strategy** -- Cross-KPC-site replication (Kyndryl-managed DR) vs replication to public cloud (hybrid DR) vs backup-based DR (lowest cost, longest RTO)

## Reference Links

- [Kyndryl Private Cloud Services](https://www.kyndryl.com/us/en/services/cloud/private) -- Main KPC product page with service tier overview
- [Kyndryl Managed Private Cloud IaaS](https://www.kyndryl.com/us/en/services/modernize-it/managed-private-cloud-iaas) -- IaaS-specific managed services detail
- [Kyndryl VMware Cloud Modernization](https://www.kyndryl.com/us/en/about-us/alliances/vmware/cloud-modernization) -- VMware optimization and alternative hypervisor assessment
- [Kyndryl Private Cloud Datasheet (PDF)](https://www.kyndryl.com/content/dam/kyndrylprogram/cs_ar_as/Kyndryl-private-cloud.pdf) -- KPC overview datasheet
- [Kyndryl Private Cloud Hybrid Transformation (PDF)](https://www.kyndryl.com/content/dam/kyndrylprogram/en/services/modernized-infrastructure/managed-cloud_mainframes/QYMGZ4N0_AS_USEN.pdf) -- Pay-per-use model details

---

## See Also

- `providers/kyndryl/bridge.md` -- Kyndryl Bridge, the managed-services delivery / AIOps platform (separate product layer from KPC)
- `providers/nutanix/infrastructure.md` -- Nutanix HCI platform decisions (if KPC uses Nutanix AHV)
- `providers/nutanix/nc2-azure.md` -- NC2 on Azure (alternative to KPC for Nutanix workloads in Azure)
- `providers/vmware/hypervisor.md` -- VMware hypervisor decisions (if KPC uses vSphere)
- `patterns/hypervisor-migration.md` -- Hypervisor conversion patterns during migration to KPC
- `patterns/datacenter-relocation.md` -- Datacenter relocation mechanics applicable to KPC migration
- `patterns/onprem-to-nc2-migration.md` -- NC2 migration pattern (alternative or complement to KPC)
- `general/capacity-planning.md` -- General capacity planning methodology for KPC sizing
- `general/disaster-recovery.md` -- DR strategy patterns applicable to KPC deployments
