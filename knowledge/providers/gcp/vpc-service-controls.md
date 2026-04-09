# GCP VPC Service Controls

## Scope

VPC Service Controls (VPC SC) is GCP's data perimeter equivalent — a network-layer enforcement mechanism that constrains GCP API access to specific perimeters, regardless of what IAM allows. Covers service perimeters, perimeter bridges, ingress and egress policies, the dry-run vs enforced modes, the relationship to IAM, the supported services list, the per-service nuances, and the audit characteristics of perimeters that are misconfigured or in dry-run mode indefinitely. VPC SC is the load-bearing primitive for organizations subject to data exfiltration risk (regulated workloads, multi-tenant SaaS, organizations with strict data residency). Mirrors the role of `patterns/aws-data-perimeter.md` in AWS and the network access controls + private endpoints in Azure.

## What problem does it solve

The threat model is "compromised workload (or compromised IAM credentials) reaching GCP resources outside the organization's control". The classic version is data exfiltration: an attacker with credentials from a compromised GCE instance copies data from a Cloud Storage bucket in the corporate project to a Cloud Storage bucket in an attacker-controlled project. Both calls are valid GCS API calls. Both succeed because the IAM credentials grant `storage.objects.get` and `storage.objects.create` and there is no other layer that knows the destination bucket is "wrong".

VPC Service Controls add that other layer. A **service perimeter** defines a boundary around a set of GCP resources (typically projects or specific resources within projects) and a set of GCP services (Cloud Storage, BigQuery, Cloud KMS, Pub/Sub, etc.). Inside the perimeter, the resources can be accessed normally. Crossing the perimeter — either reading data out or writing data in — requires explicit ingress or egress policies.

The mechanism is enforced at the **API layer**, not the network layer. A request to `storage.googleapis.com` is evaluated against the perimeter regardless of whether it came from inside the corporate VPC, from an on-premises network via Cloud Interconnect, or from a developer laptop. The perimeter is the policy decision point.

## Service perimeters

A service perimeter has:

- **Resources** — the projects (and optionally specific resources within projects) that are inside the perimeter
- **Restricted services** — the GCP services that are protected by the perimeter. Calls to restricted services from outside the perimeter (or to outside the perimeter from inside) are blocked unless an explicit policy allows them.
- **Accessible services** — the services that resources inside the perimeter can call to outside-perimeter destinations. Defaults to "all services" but can be restricted.
- **Ingress policies** — explicit rules allowing specific external sources to access perimeter resources (e.g., a partner project that should be allowed to read a specific bucket)
- **Egress policies** — explicit rules allowing perimeter resources to access specific external destinations (e.g., a managed service in another project that the workload depends on)
- **Access levels** — conditional rules based on context (source IP range, device posture, identity)

A typical perimeter for a regulated workload might include:

- All projects in the workload's folder
- Restricted services: Cloud Storage, BigQuery, Cloud KMS, Pub/Sub, Cloud SQL, Secret Manager, AI Platform
- No ingress policies (no external access)
- A small set of egress policies for specific managed services the workload depends on
- An access level that requires source IP from the corporate network OR Google Cloud network

## Perimeter bridges

When two perimeters need to share specific resources without merging, a **perimeter bridge** can be created. Bridges are bidirectional — both perimeters can access the shared resources — but they do not extend the perimeter boundary itself.

Bridges are appropriate for:

- A "shared services" perimeter holding resources that multiple workload perimeters need to access (e.g., a shared Cloud KMS key ring, a shared logging bucket)
- A "data exchange" perimeter where two business units share a specific dataset

Bridges should be used sparingly. Every bridge is a hole in the perimeter that needs to be justified and audited.

## Dry-run vs enforced mode

When a perimeter is created, it can start in **dry-run mode**. In dry-run, the perimeter is evaluated against every request and the result is logged, but the request is not actually blocked. This allows the team to see what would have been blocked before enforcing the perimeter.

The transition from dry-run to enforced is the key decision. Dry-run is the right initial state for tuning the perimeter (identifying legitimate cross-perimeter access patterns and adding ingress/egress policies for them). The transition to enforced should happen on a defined timeline (typically 2–4 weeks of dry-run, then enforce). A perimeter that has been in dry-run for 18 months is the same anti-pattern as a WAF in detection mode for 18 months — the team has paid for the perimeter and gets none of the protection.

## Relationship to IAM

VPC Service Controls are **layered with IAM**, not a replacement for it:

- IAM determines **whether** a principal has the permission to perform an action
- VPC SC determines **from where** that action can be performed

Both must succeed for the action to be allowed. A principal with IAM permission to read a bucket but who is making the request from outside the perimeter will be blocked by VPC SC. A principal making the request from inside the perimeter but without IAM permission will be blocked by IAM.

This is the same layering as the AWS data perimeter pattern (where IAM + endpoint policies + bucket policies all participate in the decision) and as the Azure private endpoint + RBAC + Conditional Access model.

## Supported services

VPC Service Controls supports a substantial but not complete subset of GCP services. As of late 2024, the supported services include:

- **Storage**: Cloud Storage, Filestore, Persistent Disk
- **Analytics**: BigQuery, Dataflow, Dataproc, Pub/Sub, Datastream, Composer
- **Compute**: Compute Engine, GKE, Cloud Functions, Cloud Run, App Engine
- **Database**: Cloud SQL, Spanner, Firestore, Bigtable, Memorystore
- **Security**: Cloud KMS, Secret Manager
- **Networking**: VPC, Cloud DNS
- **Operations**: Cloud Logging, Cloud Monitoring, Cloud Trace, Error Reporting
- **AI / ML**: Vertex AI, Document AI, Translation, Vision API
- **Identity**: Cloud Identity (some endpoints)

Services **not** supported by VPC SC (as of late 2024) include some marketing and developer tools (Firebase, Apigee for some operations, Cloud Build for some operations). Check the current support matrix at the official documentation before designing the perimeter.

## Common Implementation Patterns

### Perimeter for a regulated workload

1. **Identify the resources** — which projects hold the regulated data and the workloads that process it
2. **List the services** — which GCP services the workload uses
3. **Identify external dependencies** — what the workload needs to access outside the perimeter (managed services in other projects, third-party APIs, on-premises systems)
4. **Create the perimeter in dry-run** — perimeter resources, restricted services, no ingress, no egress
5. **Tune for two weeks** — review the dry-run logs, identify the legitimate cross-perimeter calls, add ingress/egress policies for them
6. **Enforce** — flip the perimeter to enforced
7. **Continuous monitoring** — alerts on perimeter violations, regular review of ingress/egress policies

### Shared services perimeter

1. **Create a perimeter** for the shared services (Cloud KMS keys, logging buckets, monitoring dashboards)
2. **Create bridges** between the shared services perimeter and each workload perimeter that needs access
3. **Each workload perimeter** is independently enforced and bridged only to the shared services it needs

### Multi-tenant SaaS perimeter

1. **One perimeter per tenant** — strict isolation
2. **Shared services perimeter** for tenant-shared infrastructure (the platform's own services)
3. **Bridges** from each tenant perimeter to the shared services perimeter
4. **Ingress policies** in the shared services perimeter restrict which tenant projects can access which shared resources

## Common Decisions (ADR Triggers)

- **Per-project perimeter vs per-folder perimeter** — per-folder for groups of projects with the same compliance posture (e.g., all production regulated workloads in one perimeter). Per-project when each project has unique constraints.
- **Single perimeter vs multiple perimeters with bridges** — single perimeter when all the resources have the same access requirements. Multiple perimeters with bridges when different resources have different external access patterns.
- **Dry-run duration** — 2–4 weeks for most perimeters. Longer only when the workload has unusual or hard-to-discover cross-perimeter access patterns. Set a calendar reminder for the transition.
- **Access level: IP-based vs identity-based vs both** — both for the strongest control. IP-only is acceptable when the workload has stable network sources. Identity-only is appropriate when the workload moves between networks but the identity is reliable.
- **Ingress and egress policies as code vs portal** — as code (Terraform, gcloud scripts) for auditability and reproducibility. The portal is acceptable for emergency adjustments but the change should be backported to code.

## Reference Architectures

### Single regulated workload perimeter

```
Perimeter "regulated-workload"
├── Resources
│   ├── projects/regulated-prod-001
│   └── projects/regulated-prod-002
├── Restricted services
│   ├── storage.googleapis.com
│   ├── bigquery.googleapis.com
│   ├── cloudkms.googleapis.com
│   ├── pubsub.googleapis.com
│   └── secretmanager.googleapis.com
├── Ingress (none — no external access)
├── Egress (allow specific managed service in shared project)
│   └── To shared-monitoring project, monitoring.googleapis.com
└── Access level
    └── IP from corporate network OR Google Cloud network
```

### Multi-tenant SaaS with shared services bridge

```
Perimeter "tenant-001"
├── Resources: tenant-001 projects
├── Restricted services: Storage, BigQuery, KMS
├── Bridge to: shared-services
└── Access level: tenant-001 service accounts only

Perimeter "tenant-002" (same shape)

Perimeter "shared-services"
├── Resources: shared-kms, shared-monitoring
├── Restricted services: KMS, Monitoring
└── Accessible from: tenant-001, tenant-002 (via bridges)
```

---

## Reference Links

- [VPC Service Controls overview](https://cloud.google.com/vpc-service-controls/docs/overview)
- [Service perimeter configuration](https://cloud.google.com/vpc-service-controls/docs/create-service-perimeters)
- [Ingress and egress policies](https://cloud.google.com/vpc-service-controls/docs/ingress-egress-rules)
- [Dry-run mode](https://cloud.google.com/vpc-service-controls/docs/dry-run-mode)
- [Supported products](https://cloud.google.com/vpc-service-controls/docs/supported-products)

## See Also

- `providers/gcp/networking.md` — broader GCP networking
- `providers/gcp/iam-organizations.md` — IAM as the layered companion to VPC SC
- `providers/gcp/firewall-rules.md` — VPC firewall rules (network-layer, distinct from VPC SC)
- `providers/gcp/cloud-storage.md` — Cloud Storage as a perimeter-protected service
- `providers/gcp/kms.md` — Cloud KMS as a perimeter-protected service
- `patterns/aws-data-perimeter.md` — equivalent pattern in AWS
