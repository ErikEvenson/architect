# GCP IAM and Resource Hierarchy

## Scope

GCP's resource hierarchy and identity model is structured differently from AWS Organizations or Azure tenants — it has a four-level hierarchy (Organization → Folder → Project → Resource) where IAM bindings can be applied at any level and inherit downward. Covers the resource hierarchy and how IAM inheritance works, predefined vs custom roles, conditional IAM bindings, service accounts and impersonation, workload identity federation for OIDC workloads (the GCP equivalent of AWS IRSA / Azure federated credentials), Organization Policies (the GCP analog to AWS SCPs / Azure Policy), the audit characteristics of cross-project service account use, and the diagnostic patterns for over-permissive IAM. Does not cover Cloud Identity directory management in depth (see `providers/gcp/iam.md` for the user-facing IAM service overview).

## The Resource Hierarchy

```
Organization
├── Folder (optional, can be nested)
│   ├── Folder
│   │   ├── Project
│   │   │   └── Resources (Compute Engine, BigQuery, Cloud Storage, etc.)
│   │   └── Project
│   └── Project
└── Project
```

- **Organization** — the root of the hierarchy, tied to a Cloud Identity or Workspace domain. There is exactly one organization per domain.
- **Folder** — optional grouping container, can be nested up to 10 levels deep. Used to group projects by department, business unit, environment, or any other axis.
- **Project** — the unit that owns resources, billing, IAM policies, and quotas. Every resource belongs to exactly one project.
- **Resource** — the individual things that consume CPU, storage, or network (VMs, buckets, datasets, etc.).

IAM bindings can be applied at any level in the hierarchy and **inherit downward**. A binding at the organization level applies to every project in every folder. A binding at a folder level applies to every project in that folder and its subfolders. A binding at a project level applies to every resource in that project. This is the equivalent of AWS Organizations OU inheritance for SCPs, but for IAM allow policies (not just deny policies).

## Predefined vs Custom Roles

### Predefined Roles

GCP publishes ~2,500 predefined roles covering most permission patterns. The naming convention is `roles/<service>.<action>`, e.g.:

- `roles/storage.objectViewer` — read access to objects in Cloud Storage
- `roles/bigquery.dataViewer` — read access to BigQuery datasets
- `roles/cloudkms.cryptoKeyEncrypterDecrypter` — encrypt and decrypt with KMS keys
- `roles/compute.instanceAdmin.v1` — manage Compute Engine instances

The standard pattern is to find the most specific predefined role that matches the workload's needs and bind it. Most common access patterns are covered by predefined roles.

### Custom Roles

Custom roles are created when no predefined role matches the actual permission set. Custom roles add management overhead (versioning, organization-level vs project-level scope) and should be rare.

When custom roles are needed:

- Create them at the **organization** level if they will be used in multiple projects
- Create them at the **project** level if they will only be used in one project
- Document the role with a clear description of why it exists and which workload uses it
- Review custom roles annually for unused permissions

### "Basic" Roles (Owner, Editor, Viewer)

GCP also has three legacy "basic" roles: `roles/owner`, `roles/editor`, and `roles/viewer`. These are pre-IAM, very broad, and should generally be avoided:

- **Owner** — can do anything in the project, including IAM management. Equivalent to AWS root account access scoped to the project.
- **Editor** — can do anything except IAM management. Still very broad (creates, updates, deletes any resource).
- **Viewer** — can read everything. Still broad (reads sensitive resource configuration, including secret metadata).

The basic roles are convenient and dangerous. They should not be used in production. Use predefined roles instead.

## Service Accounts and Impersonation

A **service account** is a non-human identity that workloads use to authenticate to GCP services. Service accounts are owned by a project and identified by an email address (`<name>@<project>.iam.gserviceaccount.com`).

### Service account keys (DO NOT USE)

Service accounts can have JSON key files generated for them, which are downloaded and used by the workload to authenticate. **This is the wrong pattern in 2024/2025** for the same reasons as long-lived AWS access keys: the key is a long-lived credential that can leak, gets stored in places it should not be, and is hard to rotate.

Disable service account key creation at the org level via Organization Policy:

```
gcloud resource-manager org-policies enable-enforce \
  iam.disableServiceAccountKeyCreation \
  --organization=<org-id>
```

### Service account impersonation (the right pattern)

Instead of generating a key, grant a human user (or another service account) the `roles/iam.serviceAccountTokenCreator` role on the target service account. The user can then call `gcloud auth print-access-token --impersonate-service-account=<sa>` to get a short-lived token without ever holding a long-lived credential.

### Workload Identity Federation

For workloads outside GCP that need to authenticate to GCP services (CI/CD pipelines, on-premises workloads, AWS or Azure workloads calling GCP APIs), use **Workload Identity Federation**. This is the canonical replacement for service account keys:

1. Create a Workload Identity Pool (a container for external identity providers)
2. Add a Workload Identity Provider (configures the trust relationship with the external IdP — GitHub, AWS, Azure, OIDC, SAML)
3. Grant the external identity the `roles/iam.workloadIdentityUser` role on the target service account
4. The external workload exchanges its native token (e.g., GitHub Actions OIDC token) for a GCP access token

The exchange happens via STS (`sts.googleapis.com`), produces a short-lived token, and requires no long-lived secret on the workload side.

### GKE Workload Identity

For Kubernetes workloads running in GKE, use **GKE Workload Identity** to bind a Kubernetes service account to a GCP service account. The pod uses the Kubernetes service account; GKE projects a token; the GKE metadata server exchanges the token for a GCP access token. This eliminates the need for service account JSON keys mounted in the pod.

## IAM Conditions

IAM bindings can have **conditions** that constrain when the binding is in effect:

- **Time-based** — only between specific dates or specific times of day
- **Resource-based** — only for resources matching a specific name pattern or tag
- **Request-based** — only when the request comes from a specific IP range or with specific request attributes

Conditions are useful for:

- **Time-bound emergency access** — grant a role for 4 hours during an incident, automatic expiration after
- **Resource-scoped access** — grant `roles/storage.objectViewer` only on buckets with a specific name prefix
- **Network-scoped access** — grant access only from the corporate IP ranges

The condition expression language (CEL) is documented in the IAM conditions reference. Conditions add complexity but enable patterns that are hard to express otherwise.

## Organization Policies

Organization Policies are the GCP analog to AWS SCPs — they enforce constraints on resource configuration that workloads cannot override. They are applied at the organization, folder, or project level and inherit downward.

Common Organization Policies:

- **`compute.requireOsLogin`** — require OS Login for SSH access (replaces metadata-based SSH keys)
- **`iam.disableServiceAccountKeyCreation`** — prevent service account key generation
- **`storage.publicAccessPrevention`** — prevent making Cloud Storage buckets public
- **`compute.vmExternalIpAccess`** — restrict which VMs can have external IPs (allowlist or deny)
- **`gcp.resourceLocations`** — restrict which regions resources can be created in (data residency)
- **`compute.skipDefaultNetworkCreation`** — prevent creation of the default network in new projects
- **`iam.allowedPolicyMemberDomains`** — restrict which Cloud Identity domains can be IAM members (prevents accidentally granting access to a personal Gmail account)

Organization Policies are deny-only — they prevent actions but cannot grant them. The combination of Organization Policies (deny) at the org/folder level and IAM (allow) at the project level produces the effective permission set, similar to the SCP + IAM model in AWS.

## Common Implementation Patterns

### CI/CD pipeline deploying to GCP via OIDC (GitHub Actions example)

1. Create a Workload Identity Pool: `gcloud iam workload-identity-pools create github --location=global`
2. Create a Workload Identity Provider for GitHub: `gcloud iam workload-identity-pools providers create-oidc github --location=global --workload-identity-pool=github --issuer-uri=https://token.actions.githubusercontent.com --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"`
3. Create a service account with the permissions the pipeline needs (e.g., `roles/run.developer`, `roles/storage.admin`)
4. Bind the GitHub workflow to the service account: `gcloud iam service-accounts add-iam-policy-binding <sa> --role=roles/iam.workloadIdentityUser --member="principalSet://iam.googleapis.com/projects/<project-num>/locations/global/workloadIdentityPools/github/attribute.repository/<org>/<repo>"`
5. In the GitHub Actions workflow, use the `google-github-actions/auth` action with `workload_identity_provider` and `service_account` parameters

No service account JSON key anywhere. Rotation is implicit (tokens are short-lived).

### GKE pod accessing Cloud Storage

1. Enable Workload Identity on the GKE cluster: `gcloud container clusters update <cluster> --workload-pool=<project>.svc.id.goog`
2. Create a Kubernetes service account in the workload namespace
3. Create a GCP service account with `roles/storage.objectAdmin` on the target bucket
4. Bind the Kubernetes SA to the GCP SA: `gcloud iam service-accounts add-iam-policy-binding <gsa> --role=roles/iam.workloadIdentityUser --member="serviceAccount:<project>.svc.id.goog[<namespace>/<ksa>]"`
5. Annotate the Kubernetes SA: `kubectl annotate serviceaccount <ksa> -n <namespace> iam.gke.io/gcp-service-account=<gsa>`
6. Pods using the Kubernetes SA automatically get GCP credentials via the metadata server

### Time-bound emergency access

1. Engineer requests emergency access via the access management tool
2. Approver grants `roles/owner` on the affected project with a condition: `request.time < timestamp("2026-01-15T18:00:00Z")` (4 hours from now)
3. Engineer performs the emergency action
4. The IAM binding automatically expires; nothing to revoke manually
5. The activity is logged in Cloud Audit Logs with the elevated context

## Common Decisions (ADR Triggers)

- **Predefined role vs custom role** — predefined for any access pattern that maps to an existing role. Custom only when no predefined role matches.
- **Service account key vs impersonation vs Workload Identity Federation** — Workload Identity Federation for any external workload that supports OIDC. Impersonation for human users authenticating via gcloud. Service account keys never (disable creation at org level).
- **GKE Workload Identity vs node-level service account** — Workload Identity for any pod that needs GCP access. Node-level service account only when the entire node should have the same access (rare in practice).
- **IAM at project level vs folder level vs org level** — project level for workload-specific access. Folder level for environment-wide patterns (e.g., "the security team gets read access on all production projects"). Organization level for tenant-wide patterns only.
- **Conditional bindings vs separate roles** — conditional bindings for time-bound, resource-scoped, or network-scoped access. Separate roles when the access pattern is permanent and the role granularity is the right model.
- **Organization Policy enforcement** — start with the high-confidence policies (`disableServiceAccountKeyCreation`, `publicAccessPrevention`, `requireOsLogin`) and add more as the team becomes comfortable with the constraint model.

## Reference Architectures

### Standard org structure for a mid-sized organization

```
Organization (acme.com)
├── Production folder
│   ├── prod-payments project
│   ├── prod-analytics project
│   └── prod-platform project
├── Non-Production folder
│   ├── dev-payments project
│   ├── staging-payments project
│   └── ...
├── Shared folder
│   ├── shared-network project (Shared VPC host)
│   ├── shared-security project (Cloud KMS, Secret Manager)
│   └── shared-logging project (Log Sink destination)
├── Sandbox folder
│   └── sandbox projects per engineer
└── Suspended folder
    └── projects pending deletion
```

Org-level IAM bindings: very few (Org Admin, Billing Admin, Security Admin)
Folder-level IAM bindings: per-environment access patterns (production access, non-prod access)
Project-level IAM bindings: workload-specific access for each project

### Org-wide security baseline

- Organization Policies enforced at the org level:
  - `iam.disableServiceAccountKeyCreation`
  - `compute.requireOsLogin`
  - `storage.publicAccessPrevention`
  - `gcp.resourceLocations` constrained to approved regions
  - `iam.allowedPolicyMemberDomains` restricted to the corporate domain
- Cloud Identity Premium for SSO with the corporate IdP
- Mandatory MFA on all human users
- Privileged Access Manager (PAM) for time-bound elevation

---

## Reference Links

- [Cloud IAM documentation](https://cloud.google.com/iam/docs)
- [Resource Manager hierarchy](https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GKE Workload Identity](https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity)
- [Organization Policy Service](https://cloud.google.com/resource-manager/docs/organization-policy/overview)
- [IAM Conditions](https://cloud.google.com/iam/docs/conditions-overview)

## See Also

- `providers/gcp/iam.md` — broader GCP IAM coverage including Cloud Identity
- `providers/gcp/security.md` — broader GCP security service set
- `providers/gcp/kms.md` — Cloud KMS access control via IAM
- `providers/aws/iam.md` — equivalent service in AWS
- `providers/azure/rbac-and-managed-identities.md` — equivalent in Azure
- `frameworks/aws-security-reference-architecture.md` — AWS SRA, similar shape to GCP folder-based hierarchy
