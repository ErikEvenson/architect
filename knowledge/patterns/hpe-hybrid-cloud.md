# HPE Hybrid Cloud Architecture

## Scope

This file covers **HPE-anchored hybrid cloud architecture** -- the connecting layer between the generic hybrid pattern (`patterns/hybrid-cloud.md`) and the HPE platform files (`providers/hpe/greenlake.md`, `synergy.md`, `nimble-alletra.md`, `proliant.md`). Topics: GreenLake Central as the cross-environment control plane, Aruba SD-WAN as the hybrid backbone, GreenLake-to-AWS / GreenLake-to-Azure / GreenLake-to-GCP connectivity patterns, identity bridging (HPE GreenLake IAM ↔ AD / Entra ID / Okta), workload mobility (HPE Zerto, HPE Morpheus), data mobility (Alletra cloud tiering, GreenLake Backup and Recovery), and observability across the boundary (InfoSight, OpsRamp, cloud-native monitors). For generic hybrid patterns (vendor-neutral), see `patterns/hybrid-cloud.md`. For GreenLake platform decisions, see `providers/hpe/greenlake.md`. For Aruba campus / SD-WAN design specifically, see `providers/aruba/` (or the Aruba sections of `general/networking.md` if not yet split out).

## Checklist

- [ ] **[Critical]** Is **GreenLake Central** designated as the cross-environment control plane, with role mappings, cost dashboards, and compliance reports federated across GreenLake-managed on-prem infrastructure and registered public-cloud accounts (AWS Outposts, Azure Arc, GCP Anthos)? -- a hybrid posture without a chosen control plane usually defaults to "the cloud console for the cloud, the on-prem console for on-prem, and a spreadsheet for the boundary," which is the failure mode the pattern is meant to prevent.
- [ ] **[Critical]** Is the **WAN backbone** between GreenLake sites and public-cloud regions chosen explicitly -- Aruba EdgeConnect (Silver Peak) SD-WAN with cloud onramps to AWS / Azure / GCP, customer-provided MPLS or SD-WAN with private peering, or vendor-neutral SD-WAN -- and is the choice driven by latency-sensitivity, throughput, and the existing WAN footprint rather than by reflex?
- [ ] **[Critical]** Is **identity bridging** designed end-to-end -- HPE GreenLake IAM federated to the customer's enterprise IdP (AD / Entra ID / Okta), role mapping documented per environment (a "platform admin" role in GreenLake maps to specific cloud-side roles), service-account strategy for cross-environment automation, audit-trail unification (GreenLake Central audit log + cloud-side CloudTrail / Activity Log / Audit Logs aggregated to a single SIEM)?
- [ ] **[Critical]** Is the **workload-placement decision matrix** documented -- which workloads stay on GreenLake (data-residency, latency-sensitive, regulated, large-storage), which move to public cloud (elastic, AI/ML burst, customer-facing edge), and which span both (CI/CD with on-prem build runners and cloud deployment, observability data flowing to a cloud-side analysis layer) -- and is the matrix tied to specific HPE product surfaces (e.g., "AI/ML training workloads burst from GreenLake for Compute to a cloud GPU pool via Morpheus orchestration")?
- [ ] **[Critical]** Is the **DR direction** explicit -- on-prem-primary with public-cloud standby (GreenLake -> AWS / Azure as DR target, typically via Zerto continuous replication or GreenLake Backup and Recovery), public-cloud-primary with GreenLake standby (rarer; appropriate when cloud is the system-of-record and on-prem is a regulatory-hold or air-gap copy), or active-active across both (highest cost, requires latency-tolerant workloads and bidirectional data sync)?
- [ ] **[Critical]** Are **data-residency and sovereignty** constraints mapped per workload -- some data must stay on GreenLake (regulatory, contractual, latency); some data can move freely; some data has tiered residency (hot tier on Alletra on GreenLake, cold tier on cloud object storage with encryption-at-rest under customer-managed keys) -- so the architecture does not silently violate data-flow restrictions?
- [ ] **[Recommended]** Is **GreenLake-to-AWS** integration sized correctly -- AWS Direct Connect from a GreenLake-hosting facility (1Gbps / 10Gbps / 100Gbps per usage), AWS Outposts under GreenLake Central management for AWS-native services on-prem, Aruba EdgeConnect cloud onramp to AWS Transit Gateway for SD-WAN-style connectivity, IAM Identity Center federated with HPE GreenLake IAM for cross-platform RBAC -- and are the cost trade-offs (Direct Connect port + circuit + egress vs cloud-onramp data transfer pricing) understood?
- [ ] **[Recommended]** Is **GreenLake-to-Azure** integration sized correctly -- Azure ExpressRoute from the GreenLake-hosting facility (Standard vs Premium SKU; Premium for global reach), **Azure Arc** registering GreenLake-managed servers and Kubernetes clusters as Azure resources for unified policy/observability/Defender coverage, **GreenLake Private Cloud Business Edition** vs Azure Stack HCI as the on-prem-Microsoft-stack option (different commercial model and different operational stack), Entra ID federation for identity, and Azure Monitor / Sentinel as the cloud-side observability/SIEM target?
- [ ] **[Recommended]** Is **GreenLake-to-GCP** integration sized correctly -- Cloud Interconnect (Dedicated or Partner) from the GreenLake-hosting facility, **Anthos clusters on bare-metal** running on GreenLake-managed compute for GCP-managed Kubernetes on-prem, Workload Identity Federation for identity, Cloud Logging / Operations as the cloud-side observability target?
- [ ] **[Recommended]** Is **HPE Zerto** positioned for the cross-environment DR / migration workload -- continuous block-level replication from VMware-on-GreenLake to AWS / Azure (or vice versa), journal-based recovery for sub-minute RPO and ransomware rollback, support for VMware-to-VMware, VMware-to-AWS-native, VMware-to-Azure-native, with the orchestration handled inside Zerto's UI rather than at the hypervisor layer? See `providers/zerto/dr-migration.md` for product depth.
- [ ] **[Recommended]** Is **HPE Morpheus** considered for the cross-environment workload-orchestration layer -- self-service catalog spanning GreenLake / vSphere / AWS / Azure / GCP / Kubernetes, IaC integration (Terraform, Ansible), policy enforcement (cost, quota, approval), single-pane-of-glass provisioning -- with awareness that Morpheus is one of several cross-environment orchestrators (alongside vRealize / VMware Aria Automation, ServiceNow Cloud Provisioning, Hashicorp portfolio) and the choice depends on existing tooling and operator preferences? See `providers/morpheus/cloud-management.md` for product depth.
- [ ] **[Recommended]** Is **observability unification** designed -- HPE InfoSight for HPE-managed compute and storage telemetry, HPE OpsRamp (HPE-acquired hybrid observability) as a cross-environment monitoring and AIOps layer, integration with cloud-native monitors (CloudWatch, Azure Monitor, Cloud Operations) via OpsRamp ingest, and a defined "single pane of glass" target tool? Hybrid postures fail most often at observability -- the team that solves this last spends the most time hunting incidents across siloed dashboards.
- [ ] **[Recommended]** Is **data mobility** designed per data class -- Alletra dHCI / Alletra Storage MP cloud tiering for cold data (block to S3 / Azure Blob), GreenLake Backup and Recovery as a cross-environment backup target with on-prem and cloud copies, application-layer replication for hot data (database replication, message-queue mirroring), Zerto continuous replication for crash-consistent block-level mobility?
- [ ] **[Recommended]** Is **secrets management** unified across environments -- HashiCorp Vault as the cross-environment secrets layer (most common), or cloud-native secrets managers federated to on-prem (AWS Secrets Manager / Azure Key Vault with on-prem accessor patterns) -- with a clear answer for "where does an on-prem application running on GreenLake retrieve a credential to a cloud-side service"?
- [ ] **[Recommended]** Is the **Kubernetes-across-environments** decision explicit -- HPE Ezmeral / GreenLake for Containers on-prem with no cluster spanning to cloud, EKS Anywhere / AKS on Azure Stack HCI / Anthos on bare metal as cloud-vendor on-prem variants, vendor-neutral Rancher / Tanzu federating clusters across environments, or Kubernetes-as-target-platform with workload portability via standard manifests? Each choice has different operator experience and different cloud-vendor lock-in.
- [ ] **[Recommended]** Is **CI/CD consistency** designed -- same pipeline tooling (GitLab / GitHub Actions / Azure DevOps) targeting both environments, IaC modules tested against both targets (Terraform with HPE / AWS / Azure providers in the same plan), build artifacts in a single registry (Harbor on GreenLake or cloud-native registry with on-prem replication), and the deployment-promotion model crossing the boundary (dev on cloud, prod on-prem; or any other split) is documented?
- [ ] **[Optional]** Is the **GreenLake exit strategy** for the hybrid posture documented -- GreenLake contracts have minimum terms (typically 3-5 years), and the workloads currently spanning on-prem and cloud need a defined target state if GreenLake is exited (re-host on customer-owned hardware, fully migrate to cloud, move to a different on-prem vendor with comparable hybrid integration); without this, the hybrid posture is a soft form of vendor lock-in?
- [ ] **[Optional]** Is **HPE Financial Services** engaged for the hybrid bundle -- some hybrid postures are easier to fund as a unified HPE-financed package (GreenLake commitment + technology refresh + Aruba SD-WAN + Zerto licensing) than as separate procurement actions; this is more about deal economics than architecture but materially affects the executable design?
- [ ] **[Optional]** Is **air-gap or partial-air-gap operation** considered for regulated workloads -- some GreenLake services require persistent connectivity to HPE management plane and are inappropriate for air-gapped environments; the hybrid posture for these workloads degenerates to "on-prem only with manual data-export-to-cloud" and the architecture should be honest about where the boundary is?

## Why This Matters

A hybrid cloud anchored on HPE infrastructure is one of the most common shapes of a real consulting engagement: the customer has substantial on-prem investment (often historical, often financially material), wants cloud-like agility for new workloads, has data-residency or latency or compliance constraints that prevent a pure cloud migration, and is being asked by leadership to "have a hybrid story." The vendor-neutral pattern (`patterns/hybrid-cloud.md`) gives the right framing -- connectivity, identity, workload placement, DR -- but does not name the products, integration points, or trade-offs that exist when HPE is the on-prem anchor. The HPE platform file (`providers/hpe/greenlake.md`) covers the platform decisions but treats hybrid as a single `[Optional]` checklist item.

The connecting layer matters because the design choices interact. **Aruba SD-WAN as the backbone** changes how the cloud-side connectivity is provisioned (cloud onramps in the Aruba EdgeConnect / EdgeConnect SD-WAN catalog vs raw Direct Connect / ExpressRoute) and changes the operator experience (single SD-WAN dashboard vs per-cloud connectivity management). **GreenLake Central as the control plane** changes how cost reporting works (federated vs siloed) and changes the procurement story (single bill via HPE or multi-bill via each cloud). **Azure Arc** registering GreenLake-managed servers as Azure resources changes the Microsoft-side governance and security story (Defender for Cloud coverage, Azure Policy enforcement, Entra ID identity for on-prem servers) -- arguably the single highest-leverage hybrid integration for Microsoft-shop customers, and routinely missed in HPE engagements that treat the cloud side as out-of-scope.

The **identity-bridging layer** is the one most likely to be designed last and to break first. An HPE-anchored hybrid posture without a unified identity strategy reliably produces: a cloud-side admin who cannot administer GreenLake, a GreenLake-side admin who cannot administer cloud-side resources, a service account in one environment with no audit trail in the other, and a partial-failure mode where the team can operate on-prem fine while the cloud side is running on six-month-old credentials nobody remembers how to rotate. The pattern needs identity to be a `[Critical]` item, with the role-mapping table called out as a deliverable.

The **observability layer** is where hybrid most reliably fails operationally. HPE's acquisition of OpsRamp specifically positions the company to compete in the cross-environment observability market, and an HPE-anchored hybrid that does not consider OpsRamp (or an equivalent third-party cross-environment monitor) ends up with siloed dashboards -- InfoSight for HPE infrastructure, CloudWatch / Azure Monitor / Cloud Operations for cloud, no joined-up view of an application that spans both. The pattern needs observability sized at design time, not added after the first cross-environment incident has already burned operator confidence.

## Common Decisions (ADR Triggers)

### ADR: Cross-Environment Control Plane

**Context:** The hybrid posture needs a designated control plane that owns multi-environment operations.

**Options:**
- **GreenLake Central** -- HPE-native, federates GreenLake managed services with public-cloud accounts via Outposts / Arc / Anthos. Lock-in to HPE management model. Best when GreenLake is the strategic on-prem anchor and the cloud-side workloads are secondary.
- **Cloud-native control plane (Azure Arc / AWS Systems Manager / GCP Anthos Hub)** -- cloud-vendor-native, treats on-prem as the secondary environment. Best when the cloud side is the primary and on-prem is being managed into the cloud-vendor's governance model.
- **Vendor-neutral control plane (Morpheus / vRealize / Aria / ServiceNow)** -- not tied to either side, integrates both. Highest licensing cost. Best when neither side is clearly primary or when the customer has multi-cloud beyond just AWS or Azure.

**Decision drivers:** Strategic direction (HPE-strategic, cloud-strategic, vendor-neutral), existing tooling investment, RBAC/audit requirements, multi-cloud breadth.

### ADR: WAN Backbone Choice

**Context:** Connectivity between GreenLake sites and public cloud regions.

**Options:**
- **Aruba EdgeConnect (Silver Peak) SD-WAN with cloud onramps** -- HPE-native, single SD-WAN dashboard, cloud onramps simplify per-cloud private connectivity, integrates with Aruba CX campus. Best for customers already using or willing to adopt Aruba networking.
- **Customer-existing SD-WAN (Cisco / VMware / Fortinet / Versa)** -- preserves SD-WAN investment, less HPE-side integration. Best when the existing SD-WAN is performing and replacement is not justified.
- **Direct Connect / ExpressRoute / Cloud Interconnect (per cloud, no SD-WAN)** -- raw private connectivity per cloud, simplest model. Best for two-environment hybrids (on-prem + one cloud) where SD-WAN complexity is unjustified.

**Decision drivers:** Existing WAN footprint, multi-site complexity, latency-sensitivity, cloud breadth (one cloud vs multi-cloud), Aruba relationship.

### ADR: Microsoft Hybrid Variant

**Context:** Specifically when the cloud side is Microsoft Azure.

**Options:**
- **GreenLake + Azure Arc (Arc-enabled GreenLake servers)** -- Azure governance applied to on-prem, Defender for Cloud / Sentinel / Azure Policy coverage, Entra ID identity for on-prem servers. HPE owns the hardware management, Microsoft owns the governance plane.
- **GreenLake Private Cloud Business Edition (Microsoft variant)** -- HPE-managed Microsoft stack on-prem, billed via GreenLake. Different product than Azure Stack HCI; same general intent.
- **Azure Stack HCI on HPE hardware (no GreenLake)** -- Microsoft-managed stack on HPE-certified hardware with traditional purchase. Less hybrid integration, more Microsoft-native.

**Decision drivers:** Operator preference (HPE-side vs Microsoft-side management), commercial model (consumption vs capex), governance posture (HPE-led vs Microsoft-led).

### ADR: Cross-Environment Workload Orchestrator

**Context:** Self-service provisioning, IaC integration, policy enforcement across both environments.

**Options:**
- **HPE Morpheus** -- HPE-strategic, broad cloud and on-prem support, Terraform/Ansible integration. Acquired by HPE; strong fit for HPE-anchored hybrids. See `providers/morpheus/cloud-management.md`.
- **VMware Aria Automation (vRealize)** -- VMware-native, deep vSphere integration, multi-cloud support added later. Best when VMware is the on-prem hypervisor and Aria is already in use.
- **ServiceNow Cloud Provisioning** -- ITSM-integrated, strong approval/governance, weaker IaC. Best when ServiceNow is the strategic ITSM platform and provisioning is part of the broader ticket flow.
- **Direct Terraform / Ansible without an orchestrator** -- IaC-only, no self-service catalog, lowest licensing cost. Best for engineering-heavy organizations with strong IaC discipline.

**Decision drivers:** Existing tooling, self-service requirements, governance/approval depth, operator skill mix.

## Reference Architectures

### HPE-Anchored Hybrid with Azure (Microsoft-Shop Variant)

```
[GreenLake site (customer datacenter)]                    [Azure region(s)]
- HPE compute (ProLiant / Synergy)                       - VMs, AKS, App Services
- Alletra storage with cloud tiering                     - Storage Accounts, Cosmos DB
- VMware on GreenLake (Private Cloud Enterprise)         - Azure Sentinel (SIEM)
- HPE Ezmeral / GreenLake for Containers                 - Azure Monitor + Log Analytics
- Aruba CX campus + EdgeConnect SD-WAN edge              - Defender for Cloud
        |                                                       ^
        |   ExpressRoute (Standard or Premium SKU)               |
        |   via Aruba EdgeConnect cloud onramp                   |
        +---------------- WAN backbone -------------------------+
        |
[Identity, Observability, Mobility]
- Entra ID as enterprise IdP, federated with GreenLake IAM
- Azure Arc registers GreenLake-managed servers + AKS-on-prem
- HPE OpsRamp ingests CloudWatch/Azure Monitor + InfoSight + on-prem agents
- HPE Zerto for cross-environment DR (VMware-on-GreenLake -> Azure-native VMs)
- HPE Morpheus for cross-environment workload provisioning
- HashiCorp Vault for cross-environment secrets
```

### HPE-Anchored Hybrid with AWS (Cloud-Native AWS Workload + On-Prem Data Anchor)

```
[GreenLake site (customer datacenter)]                    [AWS region(s)]
- HPE compute + Alletra (system-of-record databases)     - EC2, EKS, S3, RDS
- VMware on GreenLake                                    - AWS Outposts (extends AWS into the on-prem rack)
- AWS Outposts (HPE-housed)                              - Direct Connect Gateway, Transit Gateway
- Aruba EdgeConnect SD-WAN                               - CloudWatch + CloudTrail
        |                                                       ^
        |   AWS Direct Connect (1G or 10G) from a              |
        |   colocation facility, plus a hot-standby             |
        |   site-to-site VPN as fallback                        |
        +---------------- WAN backbone -------------------------+
        |
[Identity, Observability, Mobility]
- Okta or Entra ID as enterprise IdP
- AWS IAM Identity Center federated with HPE GreenLake IAM via SAML
- HPE OpsRamp ingests CloudWatch + InfoSight + on-prem agents
- HPE Zerto for cross-environment DR (VMware-on-GreenLake -> AWS Elastic DR target)
- HPE Morpheus for cross-environment workload provisioning
- HashiCorp Vault for cross-environment secrets
- AWS Outposts under GreenLake Central management gives an "AWS-in-the-on-prem-rack" footprint with consistent AWS APIs
```

### Cloud-Bursting AI/ML on GreenLake-Anchored Hybrid

```
[GreenLake site -- training data lives here]
- Alletra Storage MP for the training dataset (data-residency / data-gravity reasons)
- GreenLake for Compute (small static GPU cluster for routine training)

        |   When training workload exceeds local GPU capacity:
        |   Morpheus orchestrates burst to cloud-side GPU pool
        v

[AWS or Azure GPU pool]
- p5 / H100 / ND-series on demand for burst training jobs
- Training data is copied to the cloud (or read directly via S3-front-end Alletra cloud tier)
- Trained model artifact is pulled back to GreenLake registry for inference serving

[Inference serving stays on GreenLake]
- Latency-sensitive inference at edge; Alletra-resident model artifacts; static GPU pool
- Cloud-side burst is for training only; inference does not span the boundary
```

## Reference Links

- [HPE GreenLake Platform Overview](https://www.hpe.com/us/en/greenlake.html) -- service catalog including hybrid integration points
- [HPE GreenLake Central](https://support.hpe.com/hpesc/public/docDisplay?docId=a00092451en_us) -- unified dashboard across GreenLake-managed environments
- [HPE OpsRamp](https://www.opsramp.com/) -- HPE-acquired hybrid observability and AIOps platform
- [HPE Aruba EdgeConnect (Silver Peak) SD-WAN](https://www.arubanetworks.com/products/sd-wan/edgeconnect/) -- SD-WAN with cloud onramps to AWS / Azure / GCP
- [HPE Zerto for cross-environment DR](https://www.hpe.com/us/en/zerto-software.html) -- VMware-to-cloud-native and cloud-to-cloud DR
- [HPE Morpheus cross-environment orchestration](https://morpheusdata.com/) -- self-service catalog and policy enforcement across clouds
- [Azure Arc-enabled servers](https://learn.microsoft.com/en-us/azure/azure-arc/servers/overview) -- Microsoft governance applied to non-Azure infrastructure including GreenLake-managed servers
- [AWS Outposts](https://aws.amazon.com/outposts/) -- AWS services on-prem; deployable in HPE-hosted facilities under GreenLake Central management
- [Anthos on bare metal](https://cloud.google.com/anthos/clusters/docs/bare-metal/latest) -- GCP Kubernetes management for on-prem clusters running on GreenLake-managed compute

## See Also

- `patterns/hybrid-cloud.md` -- generic, vendor-neutral hybrid cloud pattern (this file is the HPE-anchored variant)
- `patterns/multi-cloud.md` -- multi-cloud (multiple public clouds, less on-prem emphasis)
- `patterns/private-cloud-as-a-service.md` -- private cloud as a service delivery pattern (GreenLake fits this model)
- `providers/hpe/greenlake.md` -- HPE GreenLake platform decisions: consumption model, service tiers, contract structure
- `providers/hpe/synergy.md` -- HPE Synergy composable infrastructure under GreenLake
- `providers/hpe/nimble-alletra.md` -- HPE Alletra storage with cloud tiering for hybrid data mobility
- `providers/hpe/proliant.md` -- HPE ProLiant servers underpinning GreenLake compute services
- `providers/zerto/dr-migration.md` -- Zerto product depth (cross-environment DR and migration)
- `providers/morpheus/cloud-management.md` -- Morpheus product depth (cross-environment orchestration)
- `general/networking.md` -- general networking design including SD-WAN and hybrid connectivity
- `general/disaster-recovery.md` -- DR strategy patterns including cross-environment DR direction
- `general/identity.md` -- identity federation across environments
- `general/observability.md` -- observability tool selection including hybrid / cross-environment monitors
