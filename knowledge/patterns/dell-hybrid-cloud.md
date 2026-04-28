# Dell-Anchored Hybrid Cloud Architecture

## Scope

This file covers **Dell-anchored hybrid cloud architecture** -- the connecting layer between the generic hybrid pattern (`patterns/hybrid-cloud.md`) and the Dell platform files (`providers/dell/apex.md`, `poweredge.md`, `powerstore.md`, `powerscale.md`, `vxrail.md`). Topics: APEX Console as cross-environment control plane, APEX Cloud Services delivery model, Dell-Microsoft alliance specifics (APEX Cloud Platform for Microsoft Azure / Azure Stack HCI on Dell, Azure Arc enrollment), Dell-VMware integration during the post-spinoff era, cross-environment DR via PowerProtect Data Manager and PowerProtect Cyber Recovery, observability via CloudIQ, and identity bridging. For generic hybrid patterns (vendor-neutral), see `patterns/hybrid-cloud.md`. For Dell APEX product depth, see `providers/dell/apex.md`. For HPE-anchored hybrid (the closest peer pattern), see `patterns/hpe-hybrid-cloud.md`.

## Checklist

- [ ] **[Critical]** Is **APEX Console** designated as the cross-environment control plane -- unified visibility across APEX-delivered on-prem services, registered public-cloud accounts, and PowerProtect / CloudIQ telemetry -- with explicit role mappings, cost dashboards, and compliance reporting? Without a designated control plane, the team defaults to per-cloud consoles plus the on-prem CloudIQ tab, and the boundary between environments has no owner.
- [ ] **[Critical]** Is the **APEX delivery model** chosen explicitly -- APEX Cloud Services (Dell-managed, consumption-based, fixed-term commitment) vs APEX Flex on Demand (CapEx-style with variable consumption tail) vs traditional purchase with CloudIQ overlay -- and aligned with the customer's commercial preference (OpEx vs CapEx) and operational preference (Dell-managed vs self-managed)?
- [ ] **[Critical]** Is **identity bridging** designed end-to-end -- APEX identity federated to the customer's enterprise IdP (AD / Entra ID / Okta), PowerProtect / CloudIQ / OpenManage SSO, role mapping per environment, service-account strategy for cross-environment automation, audit-trail unification (APEX audit log + cloud-side CloudTrail / Activity Log / Audit Logs aggregated to a single SIEM)?
- [ ] **[Critical]** Is the **Dell-Microsoft hybrid variant** considered specifically -- APEX Cloud Platform for Microsoft Azure (Dell's Azure Stack HCI offering, Dell-managed hardware with Microsoft governance plane), Azure Arc enrolling Dell-managed PowerEdge servers and AKS-on-prem clusters, Defender for Cloud / Sentinel / Azure Policy coverage of on-prem Dell infrastructure, Entra ID federation for identity? This is the highest-leverage hybrid integration for Microsoft-shop customers and is routinely missed in Dell engagements that treat the cloud side as out-of-scope.
- [ ] **[Critical]** Is the **DR direction** explicit -- on-prem-primary with cloud standby (Dell -> AWS / Azure as DR target via PowerProtect Data Manager replication or Druva-managed cloud DR), cloud-primary with Dell standby (rarer; appropriate for regulatory-hold or air-gap copies), or active-active across both? PowerProtect Cyber Recovery adds an isolated, immutable copy on the same path, addressing ransomware-resilience as a separate concern from DR.
- [ ] **[Critical]** Are **data-residency and sovereignty** constraints mapped per workload -- some data must stay on Dell on-prem (regulatory, contractual, data-gravity), some can move freely, some has tiered residency (hot tier on PowerStore on-prem, cold tier on cloud object storage); PowerScale OneFS supports cloud tiering for unstructured data and creates a defensible "hot on-prem, cold in cloud" pattern for file workloads?
- [ ] **[Recommended]** Is **WAN backbone choice** documented -- private connectivity via existing customer SD-WAN (Cisco / VMware / Fortinet / Versa), Direct Connect / ExpressRoute / Cloud Interconnect from the on-prem facility, or new SD-WAN to anchor the hybrid? Dell does not have a captive SD-WAN product equivalent to Aruba EdgeConnect, so the WAN side typically composes with the customer's existing networking vendor.
- [ ] **[Recommended]** Is **Dell-VMware** positioning understood for VMware-on-Dell hybrid -- VxRail with VCF as the on-prem hyperconverged stack, vSphere-on-PowerEdge as a more flexible non-HCI alternative, VMware Cloud Foundation upgrade path (see `providers/vmware/vcf-upgrade-5-to-9.md`); since VMware is no longer Dell-owned, the integration story is now closer to a partnership than a co-engineered stack and the licensing model has changed substantially?
- [ ] **[Recommended]** Is **PowerProtect Data Manager** scoped for cross-environment backup and DR -- on-prem backup of VMware / Hyper-V / physical / Kubernetes / SaaS workloads, cloud-tier copy to AWS S3 / Azure Blob / GCP Object, Cyber Recovery vault for ransomware-resilience, integration with Druva (Dell's cloud-native backup partner) for SaaS workload backup -- and is the retention/RPO/RTO configured per data class?
- [ ] **[Recommended]** Is **CloudIQ** scoped as the cross-environment observability and predictive-analytics layer -- proactive health, capacity, and performance analytics across PowerStore / PowerMax / PowerScale / PowerProtect / VxRail / PowerEdge / connectrix-fabric, with API integration to OpenManage Enterprise on the server side and to cloud-native monitors on the cloud side -- with awareness that CloudIQ is Dell-infrastructure-scoped and a separate cross-environment observability layer (Datadog / Dynatrace / OpsRamp / Splunk Observability) is needed for the application layer?
- [ ] **[Recommended]** Is the **Kubernetes-across-environments** decision explicit -- Dell does not have a captive Kubernetes management plane equivalent to OpenShift or Anthos; options are EKS Anywhere / AKS on APEX Cloud Platform for Microsoft Azure / Anthos on bare metal / Rancher / vendor-neutral; Dell's container-platform play is via partnerships (Tanzu, Rancher, Red Hat OpenShift) rather than a captive product?
- [ ] **[Recommended]** Is **secrets management** unified across environments -- HashiCorp Vault as the cross-environment secrets layer (most common), or cloud-native secrets managers federated to on-prem with a clear answer for "where does an on-prem application running on Dell retrieve a credential to a cloud-side service"?
- [ ] **[Recommended]** Is **CI/CD consistency** designed -- same pipeline tooling targeting both environments, IaC modules tested against both targets (Terraform with Dell APEX provider + AWS/Azure providers in the same plan), build artifacts in a single registry, and the deployment-promotion model crossing the boundary documented?
- [ ] **[Optional]** Is the **APEX exit strategy** documented -- APEX Cloud Services contracts have minimum terms, and the workloads currently spanning on-prem and cloud need a defined target state if APEX is exited (re-host on customer-owned PowerEdge, fully migrate to cloud, move to a different on-prem vendor); this is a soft form of vendor lock-in if not planned?
- [ ] **[Optional]** Is **Dell Financial Services** engaged for the hybrid bundle -- some hybrid postures are easier to fund as a unified Dell-financed package (APEX commitment + technology refresh + PowerProtect licensing) than as separate procurement actions?

## Why This Matters

A hybrid cloud anchored on Dell is the most common shape of a Dell-customer engagement: substantial on-prem PowerEdge / PowerStore / VxRail investment, customer pressure for cloud-like agility, and data-gravity or compliance constraints that prevent a pure cloud migration. The vendor-neutral pattern (`patterns/hybrid-cloud.md`) gives the right framing -- connectivity, identity, workload placement, DR -- but does not name the products, integration points, or trade-offs that exist when Dell is the on-prem anchor. The Dell platform files cover the platform decisions but treat hybrid as adjacent rather than central.

The **Dell-Microsoft hybrid variant** is the highest-leverage integration that is most often missed. APEX Cloud Platform for Microsoft Azure is Dell's Azure Stack HCI offering with Dell-managed hardware delivery; combined with Azure Arc enrolling all Dell-managed PowerEdge servers as Azure resources, it produces a "Microsoft-governance over Dell-hardware" posture that addresses the compliance, security, and identity-unification concerns that drive most Microsoft-shop hybrid initiatives. Dell engagements that treat the cloud side as the customer's problem leave this integration on the table and ship a less-valuable architecture.

The **PowerProtect-Cyber Recovery distinction** matters because customers conflate "DR" and "ransomware recovery" and end up with neither. Standard PowerProtect Data Manager replication addresses DR (an off-prem copy that can be restored if the primary is lost). PowerProtect Cyber Recovery adds an isolated, air-gapped vault that ransomware cannot reach -- which is required as a regulatory or insurance gating control in many enterprises. The two are sized differently (DR copy is the working data set, Cyber Recovery vault is a curated subset) and the design needs both as separate line items.

The **post-spinoff Dell-VMware** story matters because the historical "Dell-VMware co-engineered stack" framing is no longer accurate. VxRail with VCF still works; vSphere licensing has changed materially; the future of VxRail-VCF integration depends on the VMware-by-Broadcom roadmap, not on a Dell-controlled engineering plan. Hybrid architectures that depend on this integration as a foundation should explicitly call out the licensing and roadmap risk.

## Common Decisions (ADR Triggers)

### ADR: Cross-Environment Control Plane

**Context:** The hybrid posture needs a designated control plane.

**Options:**
- **APEX Console** -- Dell-native, federates APEX-delivered services with public-cloud accounts. Best when APEX is the strategic on-prem anchor.
- **Cloud-native (Azure Arc / AWS Systems Manager / GCP Anthos Hub)** -- best when the cloud side is primary and Dell on-prem is being managed into the cloud-vendor's governance model.
- **Vendor-neutral (Morpheus / vRealize / ServiceNow)** -- highest licensing cost, best when neither side is clearly primary or when multi-cloud breadth is in scope.

### ADR: Microsoft Hybrid Variant

**Context:** Specifically when the cloud side is Microsoft Azure.

**Options:**
- **APEX Cloud Platform for Microsoft Azure** -- Dell-managed Azure Stack HCI hardware with Microsoft governance. Same general intent as Lenovo ThinkAgile MX or HPE GreenLake Private Cloud Business Edition (Microsoft variant). Different commercial models per vendor.
- **Azure Stack HCI on PowerEdge (without APEX)** -- traditional purchase, customer-managed, Microsoft-supported.
- **Dell PowerEdge with Azure Arc only (no Azure Stack HCI)** -- Azure governance over generic Dell servers without the HCI commitment. Lighter integration; appropriate when Azure governance is the goal but the operational stack is not Microsoft-stack.

### ADR: Backup / DR Architecture

**Context:** Cross-environment data protection.

**Options:**
- **PowerProtect Data Manager + Cyber Recovery** -- Dell-native, on-prem-anchored, cloud copy as a tier. Best when Dell is the strategic data-protection vendor.
- **Druva for cloud-anchored / SaaS workloads, PowerProtect for on-prem** -- partnership model, cloud-native backup for SaaS (M365, Salesforce, Workday) and PowerProtect for traditional on-prem workloads.
- **Vendor-neutral (Veeam / Commvault / Rubrik)** -- best when the customer has an existing backup investment that should not be displaced.

## Reference Architecture: Dell-Anchored Hybrid with Microsoft Azure (Microsoft-Shop Variant)

```
[On-prem Dell datacenter]                                 [Azure region(s)]
- PowerEdge servers under APEX delivery                  - VMs, AKS, App Services
- PowerStore / PowerMax storage                          - Storage Accounts, Cosmos DB
- APEX Cloud Platform for Microsoft Azure (Azure         - Azure Sentinel (SIEM)
  Stack HCI on Dell hardware) for Microsoft-stack        - Azure Monitor + Log Analytics
  workloads                                              - Defender for Cloud
- VxRail + VCF for VMware-stack workloads                       ^
- PowerProtect Data Manager + Cyber Recovery vault              |
        |   ExpressRoute (Standard or Premium)                  |
        +---------------- WAN backbone -------------------------+
        |
[Identity, Observability, Mobility]
- Entra ID as enterprise IdP, federated with APEX identity
- Azure Arc enrolls all Dell PowerEdge servers + AKS-on-APEX-Cloud-Platform
- CloudIQ for Dell infrastructure observability + Azure Monitor for cloud
- Dell-side cross-environment monitor: third-party (Datadog/Dynatrace/Splunk)
- PowerProtect Data Manager: on-prem primary backup + Azure Blob cold tier +
  Cyber Recovery vault (isolated, immutable, ransomware-resilient)
- HashiCorp Vault for cross-environment secrets
```

## Reference Links

- [Dell APEX overview](https://www.dell.com/en-us/dt/apex/index.htm) -- service catalog and delivery models
- [APEX Cloud Platform for Microsoft Azure](https://www.dell.com/en-us/dt/apex/cloud-platforms/microsoft-azure.htm) -- Azure Stack HCI on Dell hardware
- [Dell PowerProtect Data Manager](https://www.dell.com/en-us/dt/data-protection/powerprotect-data-manager.htm) -- enterprise data-protection product
- [Dell PowerProtect Cyber Recovery](https://www.dell.com/en-us/dt/data-protection/cyber-recovery-solution.htm) -- isolated immutable backup vault
- [Dell CloudIQ](https://www.dell.com/en-us/dt/storage/cloudiq.htm) -- Dell infrastructure observability and predictive analytics
- [Azure Arc-enabled servers](https://learn.microsoft.com/en-us/azure/azure-arc/servers/overview) -- Microsoft governance for non-Azure infrastructure including Dell PowerEdge

## See Also

- `patterns/hybrid-cloud.md` -- generic vendor-neutral hybrid pattern
- `patterns/hpe-hybrid-cloud.md` -- HPE-anchored hybrid pattern (closest peer)
- `patterns/multi-cloud.md` -- multi-cloud architecture
- `providers/dell/apex.md` -- Dell APEX platform decisions
- `providers/dell/poweredge.md` -- PowerEdge servers
- `providers/dell/powerstore.md` -- PowerStore storage
- `providers/dell/powerscale.md` -- PowerScale (OneFS) for unstructured data
- `providers/dell/vxrail.md` -- VxRail HCI with VCF
- `providers/vmware/vcf-sddc-manager.md` -- VCF on Dell VxRail
- `general/networking.md` -- general hybrid networking
- `general/disaster-recovery.md` -- DR strategy patterns
- `general/observability.md` -- observability tool selection across environments
