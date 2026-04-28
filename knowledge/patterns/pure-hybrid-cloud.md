# Pure-Storage-Anchored Hybrid Cloud Architecture

## Scope

This file covers **Pure-Storage-anchored hybrid cloud architecture** -- a **storage-led** hybrid pattern that composes with whatever compute-side hybrid story the customer has chosen. It is the connecting layer between the generic hybrid pattern (`patterns/hybrid-cloud.md`) and the Pure platform files (`providers/purestorage/flasharray.md`, `flashblade.md`, `portworx.md`). Topics: Pure-as-a-Service consumption model, Cloud Block Store as the cloud-side replication target, FlashArray / FlashBlade replication across the boundary, Portworx for Kubernetes-storage portability, Pure1 as cross-environment control plane and observability, ActiveCluster for synchronous replication, and data-tiering patterns. **Pure-anchored hybrid composes with -- it does not replace -- a compute-anchored hybrid story (HPE / Dell / Cisco / Lenovo / VMware on whatever hardware).** For generic hybrid patterns (vendor-neutral), see `patterns/hybrid-cloud.md`. For full-stack-anchored hybrid patterns, see `patterns/hpe-hybrid-cloud.md`, `patterns/dell-hybrid-cloud.md`, `patterns/cisco-hybrid-cloud.md`, `patterns/lenovo-hybrid-cloud.md`.

## Checklist

- [ ] **[Critical]** Is the architecture explicit that **Pure-anchored is storage-anchored, not full-stack-anchored** -- the compute-side decisions (what server vendor, what hypervisor, what container platform, what management plane) are owned by a separate vendor or vendor-neutral choice and the hybrid pattern composes? An architecture that treats Pure as if it were a full-stack vendor (a la HPE GreenLake or Dell APEX) underspecifies the compute layer and over-specifies the storage layer.
- [ ] **[Critical]** Is **Pure1** designated as the cross-environment storage control plane -- unified visibility across FlashArray / FlashBlade / Cloud Block Store / Portworx, predictive analytics (Pure1 Meta), capacity / performance dashboards, with API integration into the customer's broader observability stack? Pure1 is Pure-storage-scoped (not a cross-vendor observability layer), so a separate cross-environment monitor (Datadog / Dynatrace / Splunk / Grafana) is needed for the application and compute layers.
- [ ] **[Critical]** Is the **Pure-as-a-Service** delivery model chosen explicitly -- Pure-as-a-Service (Pure-managed, consumption-based, equivalent to HPE GreenLake or Dell APEX for storage specifically) vs Evergreen Forever (CapEx with non-disruptive upgrades) vs traditional capacity purchase -- and aligned with the customer's commercial preference (OpEx vs CapEx) and operational preference (Pure-managed vs self-managed)?
- [ ] **[Critical]** Is the **Cloud Block Store** integration scoped -- Cloud Block Store on AWS (deployed in the customer's VPC, presents FlashArray-equivalent block storage to EC2 / EKS workloads) and on Azure (in the customer's VNet, equivalent semantics for Azure VMs / AKS); replication target for on-prem FlashArray, with the same Purity OS, snapshot semantics, replication topology, and application-side integration as on-prem FlashArray? Cloud Block Store is the canonical Pure cross-environment data-mobility primitive.
- [ ] **[Critical]** Is the **DR direction** explicit and tied to specific Pure replication primitives -- async replication (RPO from minutes to days, low bandwidth, suitable for cross-region), ActiveCluster synchronous replication (RPO of zero between two on-prem sites or between on-prem and Cloud Block Store within tight latency tolerance), CloudSnap for snapshot-to-cloud (S3 / Azure Blob), or Cloud Block Store replication for full block-level cross-environment DR?
- [ ] **[Critical]** Are **data-residency and sovereignty** constraints mapped per data class -- some data must stay on FlashArray on-prem (regulatory, contractual, latency), some can replicate to Cloud Block Store (block-level, in the customer's cloud account), some can tier to cheap object storage (cold tier on S3 / Azure Blob via CloudSnap) -- with encryption-at-rest and customer-managed-key strategy explicit per tier?
- [ ] **[Recommended]** Is **Portworx** scoped as the Kubernetes-storage data plane -- Portworx provides persistent storage, replication, snapshots, backups, and disaster recovery for Kubernetes workloads spanning environments (on-prem K8s on Pure / generic, EKS / AKS / GKE in cloud); cross-environment portability is materially better than CSI-only approaches that re-implement these primitives per cloud?
- [ ] **[Recommended]** Is the **compute-side hybrid story** identified explicitly -- "Pure-on-Cisco-UCS" (compose with `patterns/cisco-hybrid-cloud.md`), "Pure-on-Dell-PowerEdge" (compose with `patterns/dell-hybrid-cloud.md`), "Pure-on-HPE-ProLiant under GreenLake" (compose with `patterns/hpe-hybrid-cloud.md`), "Pure-on-Lenovo-ThinkSystem" (compose with `patterns/lenovo-hybrid-cloud.md`), "Pure-on-VMware-on-anything" (compose with VMware-on-X) -- so the architecture has a single coherent story rather than two parallel architectures that do not reference each other?
- [ ] **[Recommended]** Is **identity bridging** designed -- Pure1 federation with the customer's enterprise IdP (AD / Entra ID / Okta), FlashArray / FlashBlade SSO, role mapping per environment, audit-trail integration with the broader SIEM; Pure's identity story is straightforward but needs to compose with the compute-side identity story?
- [ ] **[Recommended]** Are **VMware-on-Pure** integrations sized -- VMware vVols (Pure was an early vVols partner; vVols allows per-VM storage policy and snapshot management), VMware Site Recovery Manager with FlashArray replication, FlashArray-X integration with VMware Cloud on AWS as a managed-storage tier; the VMware integration is one of Pure's strongest hybrid surfaces and is appropriate when VMware is the on-prem hypervisor?
- [ ] **[Recommended]** Is the **cross-environment observability** designed across layers -- Pure1 for storage-layer telemetry, compute-side monitor for compute-and-network telemetry, application-layer monitor for application telemetry; the three layers must integrate (typically into a Datadog / Dynatrace / Splunk / OpsRamp aggregator) for end-to-end visibility?
- [ ] **[Recommended]** Is **secrets management** unified -- HashiCorp Vault as the cross-environment secrets layer (most common); Pure does not have a captive secrets-management product, so this composes with the broader cross-environment secrets strategy?
- [ ] **[Recommended]** Is **CI/CD consistency** designed -- IaC modules tested against both targets (Terraform with Pure provider for FlashArray / Cloud Block Store + cloud providers in the same plan), with awareness that Cloud Block Store is provisioned and managed via the same Purity API as on-prem FlashArray, which simplifies the IaC story?
- [ ] **[Optional]** Is the **Pure-as-a-Service exit strategy** documented -- Pure-as-a-Service contracts have minimum terms; if exited, the workloads relying on Pure storage need a defined target state (continue with Evergreen capex purchase, migrate to a different storage vendor, move to cloud-native storage); the data-mobility primitives (CloudSnap, Cloud Block Store replication) make the migration path cleaner than at most storage vendors but the application-side dependency on Purity features (ActiveCluster, vVols, snapshot semantics) needs to be assessed?
- [ ] **[Optional]** Are **specific Pure-cloud integrations** scoped per cloud -- AWS: Cloud Block Store on EC2, FlashRecover with Veeam, Pure FlashBlade S replicating to S3; Azure: Cloud Block Store on Azure VMs, FlashArray with Azure VMware Solution; the cloud-specific integrations differ in maturity (AWS is the historical first-class target, Azure followed)?

## Why This Matters

A Pure-Storage-anchored hybrid is structurally different from a compute-anchored hybrid like HPE / Dell / Cisco / Lenovo. Pure's primary hybrid surface is **data mobility and consistent storage semantics across environments**: the same Purity OS, the same APIs, the same management plane, the same snapshot semantics on Cloud Block Store as on on-prem FlashArray. This is the core differentiator that justifies a Pure-anchored hybrid pattern: an application running on Cloud Block Store in AWS sees a FlashArray, with all the operational behaviors that implies, with no custom cloud-storage adaptation.

The **storage-anchored composability** matters because Pure-anchored hybrid engagements routinely produce architectures that are over-specified on the storage side and under-specified on the compute side. The pattern needs to be explicit that the compute-side decisions (server vendor, hypervisor, container platform, management plane) are owned by a separate decision -- the architecture has both a storage-side and a compute-side story, and they need to compose. Treating "Pure" as the answer to a hybrid question without identifying the compute-side answer produces a half-architecture.

**Cloud Block Store** is the canonical Pure cross-environment primitive and is what makes the Pure-anchored hybrid story work. Other storage vendors offer cloud-side products with different operational semantics from their on-prem products; Cloud Block Store is intentionally a FlashArray in the cloud, with the same management plane and the same application integrations. This means: the same DR runbooks work cross-environment, the same Veeam / Commvault / Rubrik integrations work, the same VMware Site Recovery Manager flows work. Engagements that do not scope Cloud Block Store leave Pure's strongest hybrid asset on the table.

**Portworx for Kubernetes** is Pure's strongest forward-looking hybrid play. Customers running Kubernetes across environments hit a familiar wall: per-cloud CSI drivers re-implement persistent-storage primitives (snapshots, replication, backup, DR) with per-cloud limitations and inconsistent semantics. Portworx provides a unified storage layer for Kubernetes that works the same on-prem (on Pure or on generic infrastructure), on EKS, on AKS, on GKE -- with cross-cluster replication, application-consistent snapshots, and DR primitives that work across environments. For Kubernetes-heavy hybrid postures, Portworx is the differentiator.

The **VMware-on-Pure integration** is one of Pure's longest-standing hybrid surfaces. Pure was an early vVols partner, the SRM-on-FlashArray integration is mature, and FlashArray as a managed-storage tier in VMware Cloud on AWS / Azure VMware Solution provides a defensible "VMware-everywhere with Pure-everywhere" posture. For VMware-anchored customers, this is often the cleanest hybrid story available.

## Common Decisions (ADR Triggers)

### ADR: Cross-Environment DR Primitive

**Options:**
- **Cloud Block Store async replication** -- block-level async replication from on-prem FlashArray to Cloud Block Store in the customer's cloud account. Same management plane, same snapshot semantics, simplest operator experience. Best general-purpose Pure cross-environment DR.
- **CloudSnap to S3 / Azure Blob** -- snapshot-level offload to cheap object storage. Lower cost than Cloud Block Store, less suitable for fast recovery (snapshots must be restored to a FlashArray or Cloud Block Store before use). Best for archive and cold-DR tiers.
- **ActiveCluster synchronous** -- zero-RPO synchronous replication, suitable between two on-prem sites or between on-prem and Cloud Block Store within tight latency. Best when zero-RPO is a hard requirement and the latency budget allows.
- **Application-layer replication (database / message-queue native)** -- application-aware replication, bypasses storage-layer replication. Best when application-consistency requirements exceed what storage-layer replication provides.

### ADR: Kubernetes Storage Layer

**Options:**
- **Portworx (Pure-strategic)** -- unified storage layer across environments, application-consistent snapshots, cross-cluster DR. Best when Kubernetes-across-environments is a strategic concern.
- **CSI drivers per cloud (cloud-native EBS / Disk / PD plus FlashArray CSI on-prem)** -- per-cloud-native primitives, different semantics per environment. Acceptable when cross-environment Kubernetes is not central or when Portworx licensing is not justified.
- **Vendor-neutral data layer (Robin / StorageOS / Longhorn)** -- third-party Kubernetes storage layers with their own trade-offs.

### ADR: Compute-Side Composition

**Options:** Pure-anchored hybrid composes with (not replaces) a compute-side hybrid story. The compute-side ADR is owned elsewhere; the Pure-side ADR should reference the chosen compute-side hybrid pattern explicitly:
- Compose with `patterns/cisco-hybrid-cloud.md` (Pure on Cisco UCS)
- Compose with `patterns/dell-hybrid-cloud.md` (Pure on Dell PowerEdge)
- Compose with `patterns/hpe-hybrid-cloud.md` (Pure on HPE ProLiant under GreenLake)
- Compose with `patterns/lenovo-hybrid-cloud.md` (Pure on Lenovo ThinkSystem)
- Compose with VMware-on-X (when VMware is the abstraction layer)

## Reference Architecture: VMware-on-Pure Hybrid with Cloud Block Store on AWS

```
[On-prem datacenter (compute-vendor-anchored)]           [AWS region(s)]
- Compute: vendor-of-choice (HPE/Dell/Cisco/Lenovo)      - VMware Cloud on AWS managed environment
- Hypervisor: VMware vSphere with vVols                  - Cloud Block Store (Pure FlashArray-in-cloud)
- Storage: FlashArray with vVols + ActiveCluster pair    - EKS clusters with Portworx
- Pure1 for cross-environment storage observability      - CloudWatch + cloud-native compute monitor
- Veeam or VMware Site Recovery Manager for DR                  ^
- Compute-side management plane (Intersight / OpenManage         |
  / iLO / XClarity One) + chosen SD-WAN                          |
        |   AWS Direct Connect (1Gbps or 10Gbps)                 |
        +---------------- WAN backbone --------------------------+
        |
[Identity, Storage Mobility, Observability]
- Customer enterprise IdP federated with Pure1 + VMware + AWS IAM
- Cloud Block Store async replication from on-prem FlashArray (DR target)
- CloudSnap from FlashArray to S3 (cold backup tier)
- Portworx for any EKS / on-prem K8s persistent storage with cross-cluster DR
- Pure1 for storage observability + Datadog / cloud-native + AppDynamics
  for compute and application observability across environments
- Application-layer composition: this storage story plus the chosen
  compute-side hybrid pattern (per-vendor file referenced above)
```

## Reference Links

- [Pure-as-a-Service](https://www.purestorage.com/products/pure-as-a-service.html) -- consumption-based delivery model
- [Cloud Block Store](https://www.purestorage.com/products/cloud-block-storage.html) -- FlashArray semantics in AWS / Azure
- [Pure1 management platform](https://www.purestorage.com/products/pure1.html) -- cross-environment storage observability
- [Portworx Enterprise](https://portworx.com/products/portworx-enterprise/) -- Kubernetes storage and data services across environments
- [ActiveCluster synchronous replication](https://support.purestorage.com/Solutions/Pure_Storage_ActiveCluster) -- zero-RPO synchronous replication
- [CloudSnap](https://www.purestorage.com/products/file-and-object-storage/flashblade-data-services.html) -- snapshot-to-cloud offload
- [VMware vVols on FlashArray](https://support.purestorage.com/Solutions/VMware) -- per-VM storage policy and snapshot management

## See Also

- `patterns/hybrid-cloud.md` -- generic vendor-neutral hybrid pattern
- `patterns/hpe-hybrid-cloud.md` -- HPE-anchored compute-side hybrid (composes with this pattern)
- `patterns/dell-hybrid-cloud.md` -- Dell-anchored compute-side hybrid (composes with this pattern)
- `patterns/cisco-hybrid-cloud.md` -- Cisco-anchored compute-side hybrid (composes with this pattern)
- `patterns/lenovo-hybrid-cloud.md` -- Lenovo-anchored compute-side hybrid (composes with this pattern)
- `patterns/multi-cloud.md` -- multi-cloud architecture
- `providers/purestorage/flasharray.md` -- FlashArray block storage
- `providers/purestorage/flashblade.md` -- FlashBlade unified file and object storage
- `providers/purestorage/portworx.md` -- Portworx Kubernetes storage
- `providers/vmware/storage.md` -- VMware vVols and storage design
- `general/disaster-recovery.md` -- DR strategy patterns
- `general/observability.md` -- cross-environment observability
