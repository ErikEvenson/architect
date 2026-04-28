# Cisco-Anchored Hybrid Cloud Architecture

## Scope

This file covers **Cisco-anchored hybrid cloud architecture** -- the connecting layer between the generic hybrid pattern (`patterns/hybrid-cloud.md`) and the Cisco platform files (`providers/cisco/ucs.md`, `routing.md`, `switching.md`, `meraki.md`, `wireless.md`). Topics: Intersight as the cross-environment management plane, Catalyst SD-WAN (formerly Viptela) as the WAN backbone with cloud onramps, UCS X-Series + Intersight as the cloud-managed-on-prem pattern, ThousandEyes for cross-environment network observability, AppDynamics for application observability across environments, and ISE federation. For generic hybrid patterns (vendor-neutral), see `patterns/hybrid-cloud.md`. For HPE-anchored hybrid (closest peer pattern), see `patterns/hpe-hybrid-cloud.md`.

## Checklist

- [ ] **[Critical]** Is **Intersight** designated as the cross-environment management plane -- Intersight Infrastructure Service (server / fabric / storage management), Intersight Workload Optimizer (cross-environment cost / performance / placement), Intersight Cloud Orchestrator (workflow automation across on-prem + AWS / Azure / GCP) -- with the strategic shift from UCS Manager (per-domain, on-prem) to Intersight (cloud-managed, multi-domain) made explicit? UCS Manager is the historical management plane; Intersight is the strategic direction and the prerequisite for most Cisco hybrid integrations.
- [ ] **[Critical]** Is **Catalyst SD-WAN** (formerly Viptela / vManage) chosen as the WAN backbone -- single SD-WAN dashboard, cloud onramps to AWS Transit Gateway / Azure Virtual WAN / Google Cloud Network Connectivity Center, Cisco Meraki SD-WAN as a lighter alternative for branch use cases -- and is the choice between Catalyst SD-WAN (enterprise / large-branch) and Meraki SD-WAN (cloud-managed / mid-market) made based on operator preference and existing footprint?
- [ ] **[Critical]** Is **identity bridging** designed end-to-end -- Cisco ISE (Identity Services Engine) for on-prem network access policy, federated with the customer's enterprise IdP (AD / Entra ID / Okta) and bridged to cloud-side IAM (AWS IAM Identity Center / Entra ID / Workload Identity Federation), Duo (Cisco-acquired) for MFA across environments, single audit trail aggregated to a SIEM?
- [ ] **[Critical]** Is **UCS X-Series + Intersight** evaluated as the cloud-managed-on-prem hardware platform -- UCS X-Series replaces UCS B-Series and C-Series for new deployments, designed from the ground up for Intersight-managed lifecycle, with composable I/O and X-Fabric architecture; the design implication is that Intersight is no longer optional for new UCS deployments?
- [ ] **[Critical]** Is the **DR direction** explicit -- on-prem-primary with cloud standby, cloud-primary with on-prem standby, or active-active; Cisco does not have a captive cross-environment DR product equivalent to HPE Zerto, so the DR layer typically uses VMware Live Site Recovery (formerly SRM), Veeam, Commvault, Rubrik, or vendor-native cloud DR (Azure Site Recovery, AWS Elastic DR) and the choice composes with the WAN-and-identity story?
- [ ] **[Critical]** Are **data-residency and sovereignty** constraints mapped per workload -- Cisco's on-prem footprint is compute-and-network-anchored rather than storage-anchored, so the storage-residency story typically depends on a separate storage vendor (NetApp, Pure, Dell, Hitachi); the hybrid pattern should be honest that "Cisco-anchored" means compute / network / observability, with storage residency owned by the chosen storage partner?
- [ ] **[Recommended]** Is **ThousandEyes** scoped as the cross-environment network observability layer -- end-to-end visibility across on-prem networks, the public internet, cloud provider networks, and SaaS endpoints; ThousandEyes is Cisco-native (acquired) and integrates with Intersight; covers the "is the cloud slow or is my SaaS slow or is the WAN slow" question that hybrid postures generate constantly?
- [ ] **[Recommended]** Is **AppDynamics** scoped for application observability across environments -- distributed-trace and business-transaction monitoring for applications spanning on-prem and cloud, integration with Intersight Workload Optimizer for placement decisions; AppDynamics is the application-layer counterpart to ThousandEyes (which is the network layer)?
- [ ] **[Recommended]** Are the **Cisco-Microsoft hybrid integrations** considered -- Azure Arc enrolling Intersight-managed servers as Azure resources for Microsoft-side governance (Defender, Sentinel, Azure Policy), Catalyst SD-WAN integrated with Azure Virtual WAN for cloud onramp; this is appropriate when the cloud side is Microsoft Azure and the customer wants Microsoft-native governance over the Cisco infrastructure?
- [ ] **[Recommended]** Are the **Cisco-AWS hybrid integrations** considered -- Catalyst SD-WAN cloud onramp to AWS Transit Gateway, AWS Outposts under Intersight management, ThousandEyes test agents in AWS regions for end-to-end visibility, IAM Identity Center federated with Cisco ISE / Duo?
- [ ] **[Recommended]** Is the **Kubernetes-across-environments** decision explicit -- Cisco does not have a captive Kubernetes management plane equivalent to OpenShift or Anthos; Cisco Container Platform was discontinued; Hybrid Cloud Network customers typically use EKS Anywhere / AKS / GKE / OpenShift / Rancher with Cisco infrastructure underneath, with Intersight Kubernetes Service providing limited Kubernetes lifecycle for some scenarios?
- [ ] **[Recommended]** Is **secrets management** unified across environments -- HashiCorp Vault as the cross-environment secrets layer (most common), or cloud-native secrets managers federated to on-prem; Cisco does not have a captive secrets-management product?
- [ ] **[Recommended]** Is **CI/CD consistency** designed -- same pipeline tooling targeting both environments, IaC modules tested against both targets (Terraform with Cisco Intersight provider + AWS / Azure / GCP providers in the same plan), build artifacts in a single registry, deployment-promotion model crossing the boundary documented?
- [ ] **[Optional]** Is **HyperFlex** treated correctly in the hybrid story -- HyperFlex is end-of-sale (EoS announced; lifecycle support continues for existing customers); new hybrid designs should not anchor on HyperFlex; existing HyperFlex deployments should be on a migration path to UCS X-Series or to a non-Cisco HCI platform; treating HyperFlex as a strategic anchor in a new hybrid design is the most common mistake in legacy-Cisco engagements?
- [ ] **[Optional]** Is **Cisco Catalyst Center** (formerly DNA Center) considered for campus / branch network management as part of the hybrid posture -- the campus and branch networks are part of the hybrid story even when the spotlight is on data-center-to-cloud connectivity, and Catalyst Center provides the cloud-managed / on-prem-managed campus controller that integrates with Catalyst SD-WAN?

## Why This Matters

A hybrid cloud anchored on Cisco is structurally different from one anchored on a full-stack vendor like HPE or Dell. Cisco's primary hybrid surface is **network and compute observability** -- Catalyst SD-WAN provides the WAN backbone, ThousandEyes provides cross-environment network visibility, AppDynamics provides cross-environment application visibility, Intersight provides cross-environment infrastructure management. The on-prem storage layer is typically a separate vendor (NetApp / Pure / Dell), so the Cisco-anchored hybrid composes with a storage-side decision rather than owning it.

The **Intersight-vs-UCS-Manager transition** matters because most Cisco-customer hybrid engagements start with an existing UCS Manager footprint and need a strategic decision about whether to migrate. UCS Manager is per-domain, on-prem, and does not federate to cloud or to other UCS domains; Intersight is the multi-domain, cloud-managed strategic direction and is required for new UCS X-Series deployments. The hybrid pattern should treat Intersight as the strategic anchor and provide guidance on the UCS-Manager-to-Intersight migration as a prerequisite, not as a side project.

The **Catalyst-SD-WAN-vs-Meraki-SD-WAN choice** matters because both are Cisco SD-WAN products with different operating models. Catalyst SD-WAN (formerly Viptela / vManage) is the enterprise / large-branch product with rich feature set and on-prem or cloud-hosted management. Meraki SD-WAN is cloud-managed-only, simpler operator experience, narrower feature set, mid-market positioning. Choosing the wrong one for the customer's complexity tier produces either an underused enterprise product (over-investment) or a feature-constrained mid-market product (under-investment).

**HyperFlex's end-of-sale status** is the most consequential lifecycle issue in legacy-Cisco engagements. New hybrid designs should not anchor on HyperFlex; existing HyperFlex deployments need a migration path to UCS X-Series or to a non-Cisco HCI alternative (Nutanix, VxRail, Azure Stack HCI). Treating HyperFlex as a strategic anchor produces a hybrid design that is wrong on day one and worse every year afterward.

**ThousandEyes and AppDynamics together** are Cisco's strongest hybrid differentiator. Customers running a hybrid posture struggle constantly with attribution -- "is the application slow because of the on-prem database, the WAN, the cloud-side load balancer, the SaaS endpoint, or the user's home network?" ThousandEyes plus AppDynamics gives a defensible answer; competitors require multiple third-party products to assemble equivalent visibility. The hybrid pattern should make these `[Recommended]` rather than `[Optional]` for any customer with cross-environment latency-sensitive workloads.

## Common Decisions (ADR Triggers)

### ADR: SD-WAN Choice

**Options:**
- **Catalyst SD-WAN (Viptela / vManage)** -- enterprise / large-branch, rich feature set, complex operator experience.
- **Meraki SD-WAN** -- cloud-managed, simpler, mid-market positioning, narrower feature set.
- **Customer-existing non-Cisco SD-WAN (Versa / Aruba / Fortinet / VMware)** -- preserves existing investment, weaker Cisco-side integration.

**Decision drivers:** Branch count, branch complexity, operator-skill mix, existing SD-WAN investment.

### ADR: UCS Management Plane

**Options:**
- **Intersight** -- strategic direction, cloud-managed, required for X-Series, supports Workload Optimizer + Cloud Orchestrator across environments.
- **UCS Manager (legacy)** -- per-domain, on-prem-only, no cloud federation. Acceptable for existing UCS B/C-Series footprints not yet migrated.

**Decision drivers:** New deployment vs existing footprint, multi-domain breadth, cloud-managed acceptance.

### ADR: Cross-Environment Observability Stack

**Options:**
- **ThousandEyes + AppDynamics + Intersight Workload Optimizer** -- Cisco-native, network + application + infrastructure layers, integrated.
- **Datadog / Dynatrace / Splunk** -- third-party, broader application coverage, weaker Cisco-infrastructure integration.
- **Vendor-mixed (Cisco for network, third-party for application)** -- best-of-breed per layer, higher integration burden.

## Reference Architecture: Cisco-Anchored Hybrid with Microsoft Azure

```
[On-prem Cisco datacenter and branches]                  [Azure region(s)]
- UCS X-Series under Intersight management               - VMs, AKS, Cosmos DB
- Catalyst 9000 switches, Catalyst SD-WAN edges          - Azure Sentinel + Defender
- ISE for network access policy + Duo for MFA            - Azure Monitor + Log Analytics
- ThousandEyes test agents in datacenter and branches    - Azure Virtual WAN
- AppDynamics agents on application tier                        ^
- Storage: NetApp / Pure / Dell (separate vendor)               |
        |   Catalyst SD-WAN cloud onramp to                     |
        |   Azure Virtual WAN over ExpressRoute                 |
        +---------------- WAN backbone -------------------------+
        |
[Identity, Observability, Mobility]
- Entra ID as enterprise IdP, federated with Cisco ISE
- Duo MFA across on-prem and cloud (Cisco-acquired, integrates with Entra)
- Azure Arc enrolls Intersight-managed UCS servers as Azure resources
- ThousandEyes cross-environment network observability (on-prem + WAN + cloud)
- AppDynamics cross-environment application observability
- Intersight Workload Optimizer for placement and cost decisions
- DR via VMware Live Site Recovery or Azure Site Recovery (no captive Cisco product)
```

## Reference Links

- [Cisco Intersight](https://www.intersight.com/) -- cloud-managed infrastructure operations platform
- [Catalyst SD-WAN (Viptela)](https://www.cisco.com/site/us/en/products/networking/sdwan-routing/index.html) -- enterprise SD-WAN with cloud onramps
- [Cisco UCS X-Series](https://www.cisco.com/site/us/en/products/computing/servers-unified-computing-systems/ucs-x-series-modular-system/index.html) -- modular compute platform designed for Intersight
- [ThousandEyes](https://www.thousandeyes.com/) -- network and application visibility across environments
- [AppDynamics](https://www.appdynamics.com/) -- application performance monitoring across environments
- [Cisco ISE](https://www.cisco.com/site/us/en/products/security/identity-services-engine/index.html) -- network access policy and identity
- [Cisco Duo](https://duo.com/) -- multi-factor authentication and zero-trust access

## See Also

- `patterns/hybrid-cloud.md` -- generic vendor-neutral hybrid pattern
- `patterns/hpe-hybrid-cloud.md` -- HPE-anchored hybrid pattern (closest peer)
- `patterns/dell-hybrid-cloud.md` -- Dell-anchored hybrid pattern
- `patterns/zero-trust.md` -- zero-trust patterns where Cisco Duo / ISE / Umbrella are common components
- `providers/cisco/ucs.md` -- UCS server platform and Intersight management
- `providers/cisco/routing.md` -- Cisco routing including Catalyst SD-WAN
- `providers/cisco/switching.md` -- Cisco switching including Catalyst 9000
- `providers/cisco/meraki.md` -- Meraki cloud-managed networking
- `general/networking.md` -- general hybrid networking
- `general/observability.md` -- observability tool selection
- `general/identity.md` -- identity federation across environments
