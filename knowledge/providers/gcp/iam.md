# GCP IAM (Identity and Access Management)

## Scope

GCP IAM roles and bindings, Workload Identity Federation, service account strategy, organization policies, VPC Service Controls, IAM Conditions, Policy Analyzer, Cloud Audit Logs, and IAM deny policies.


## Checklist

- [ ] **[Critical]** Apply the principle of least privilege using predefined roles instead of basic roles (Owner, Editor, Viewer); basic roles grant thousands of permissions across all services and are almost never appropriate for production workloads; use IAM Recommender to identify and right-size over-privileged bindings
- [ ] **[Recommended]** Create custom roles only when no predefined role matches requirements: custom roles require ongoing maintenance as new permissions are added to GCP services; use predefined roles as a starting point and remove unwanted permissions; custom roles can be created at organization or project level
- [ ] **[Critical]** Configure Workload Identity Federation for external workloads (GitHub Actions, GitLab CI, AWS, Azure) to access GCP resources without service account keys: OIDC or SAML federation with attribute mappings and conditions; eliminates long-lived credential management entirely
- [ ] **[Critical]** Implement service account key hygiene: prefer attached service accounts (Compute Engine, GKE, Cloud Run) and Workload Identity Federation over service account keys; if keys are unavoidable, enforce rotation (90-day maximum), use IAM Recommender to identify unused keys, and monitor key creation events with Cloud Audit Logs
- [ ] **[Recommended]** Use short-lived service account credentials: generateAccessToken for OAuth tokens (1-hour max), generateIdToken for identity tokens, signBlob/signJwt for signing operations; short-lived credentials via impersonation (iam.serviceAccounts.getAccessToken) are preferred over key distribution
- [ ] **[Critical]** Configure organization policies for security guardrails: constraints/iam.disableServiceAccountKeyCreation (prevent key creation), constraints/iam.allowedPolicyMemberDomains (domain-restricted sharing), constraints/compute.requireOsLogin (enforce OS Login), constraints/iam.disableServiceAccountCreation (control service account proliferation)
- [ ] **[Critical]** Enable VPC Service Controls for data exfiltration protection: define service perimeters around projects containing sensitive data; control which identities, projects, and IP ranges can access services within the perimeter; use access levels for context-aware access (device trust, IP range, identity)
- [ ] **[Recommended]** Apply IAM Conditions for context-aware access control: restrict access by time (scheduling), resource attributes (resource name, type, tags), and request attributes (IP address, device); conditions are evaluated on every API call and support CEL (Common Expression Language)
- [ ] **[Recommended]** Use Policy Analyzer to verify who has access to what: query effective permissions across the organization, simulate access scenarios, and identify all principals with a specific permission on a resource; essential for security audits and compliance reporting
- [ ] **[Critical]** Implement domain-restricted sharing using organization policy (constraints/iam.allowedPolicyMemberDomains): prevent IAM bindings to external identities (gmail.com, non-corporate domains); critical for preventing accidental data exposure to personal accounts
- [ ] **[Recommended]** Design service account strategy: one service account per application/microservice (not per VM or per developer), meaningful naming convention (sa-appname-environment@project.iam.gserviceaccount.com), limit to 100 service accounts per project, use impersonation chains instead of distributing keys
- [ ] **[Critical]** Enable and review Cloud Audit Logs: Admin Activity logs (always on, free, 400-day retention), Data Access logs (must be enabled, charged, configurable per service), System Event logs (always on, free); export to BigQuery or Cloud Storage for long-term retention and analysis
- [ ] **[Recommended]** Configure IAM deny policies for explicit permission blocking: deny policies override allow policies and are evaluated before allow bindings; use for high-privilege operations that should be restricted regardless of role assignments (e.g., deny billing account modifications except for finance team)

## Why This Matters

IAM is the foundational security control in GCP. Every API call is authorized through IAM, making misconfiguration the most common path to data breaches. GCP's resource hierarchy (organization -> folders -> projects -> resources) means IAM bindings inherit downward -- an Editor role granted at the folder level propagates to every project and resource underneath. This inheritance model is powerful for administration but dangerous when over-privileged bindings are applied too high in the hierarchy.

Service account keys are the GCP equivalent of AWS long-lived access keys and represent the highest-risk credential type. Unlike attached service accounts (which use instance metadata tokens with automatic rotation), service account keys are exportable, do not expire by default, and can be exfiltrated from CI/CD systems, developer laptops, or source control. Workload Identity Federation and short-lived credentials eliminate this risk entirely for most use cases.

VPC Service Controls provide a second security boundary beyond IAM. Even if an attacker obtains a valid IAM credential, VPC Service Controls can prevent data exfiltration by restricting API access to defined perimeters. This is particularly critical for BigQuery, Cloud Storage, and other data services where a single compromised credential could export entire datasets.

## Common Decisions (ADR Triggers)

- **Basic vs predefined vs custom roles** -- Basic roles (Owner, Editor, Viewer) are legacy roles granting broad access across all services. Predefined roles are service-specific with curated permissions (e.g., roles/storage.objectViewer, roles/cloudsql.client). Custom roles allow exact permission selection but require maintenance. Always start with predefined roles; create custom roles only when predefined roles grant too many or too few permissions for a specific use case.
- **Service account keys vs Workload Identity Federation vs attached service accounts** -- Attached service accounts (for Compute Engine, GKE, Cloud Run) use metadata server tokens that rotate automatically. Workload Identity Federation maps external identities (GitHub, AWS, Entra ID) to GCP service accounts without keys. Service account keys are downloadable JSON credentials that do not expire. Prefer attached > Workload Identity Federation > impersonation > keys. Keys should be a last resort with compensating controls (rotation, monitoring, scope).
- **Project-level vs organization-level IAM** -- Project-level bindings scope access to a single project and its resources. Organization/folder-level bindings inherit to all child projects. Grant at the lowest hierarchy level that meets requirements. Central platform teams need folder/org-level access. Application teams should receive project-level access only. Use IAM deny policies at org level to enforce universal restrictions.
- **VPC Service Controls perimeter design** -- Single perimeter (all projects in one boundary) is simpler but provides no internal isolation. Multiple perimeters (per-environment, per-data-classification) provide segmentation but require perimeter bridges for legitimate cross-perimeter access. Use a single perimeter for small organizations. Use multiple perimeters for large organizations with distinct data sensitivity levels (e.g., production PII perimeter separate from analytics perimeter).
- **Workload Identity (GKE) vs node service account** -- Workload Identity maps Kubernetes service accounts to GCP service accounts, providing pod-level IAM (different pods can have different GCP permissions). Node-level service account grants the same GCP permissions to all pods on the node. Workload Identity is strongly recommended for all GKE clusters. Node-level service accounts are a security anti-pattern for multi-tenant clusters.
- **IAM Conditions vs separate projects for access control** -- IAM Conditions provide attribute-based access control within a project (e.g., grant access only to Cloud Storage buckets with a specific prefix). Separate projects provide complete resource isolation with independent IAM policies. Conditions add flexibility but complexity. Separate projects are simpler to reason about and audit. Use projects for environment separation (dev/staging/prod). Use conditions for fine-grained access within an environment.

## Reference Architectures

### Enterprise IAM Foundation
Organization-level: domain-restricted sharing policy, disable service account key creation policy, Cloud Audit Logs exported to centralized logging project in BigQuery. Folder-level: per-business-unit folders with team-specific predefined role bindings. Project-level: one project per application per environment (app-a-prod, app-a-dev), application service accounts with predefined roles scoped to project. Workload Identity Federation configured for GitHub Actions CI/CD. IAM Recommender running weekly to identify unused permissions.

### Zero-Trust Data Access with VPC Service Controls
VPC Service Controls perimeter around data projects (BigQuery datasets, Cloud Storage with PII). Access levels defined: corporate network IP range + managed device. Ingress rules: data engineering team can access BigQuery from corporate network. Egress rules: BigQuery jobs can write results to approved Cloud Storage buckets within the perimeter. All data access logged via Data Access audit logs exported to SIEM. External access requests go through Access Context Manager with approval workflow.

### GKE Workload Identity Architecture
GKE cluster with Workload Identity enabled. Each microservice has a dedicated Kubernetes service account annotated with the corresponding GCP service account (iam.gke.io/gcp-service-account). GCP service accounts have minimum predefined roles: order-service-sa gets roles/cloudsql.client + roles/pubsub.publisher, payment-service-sa gets roles/secretmanager.secretAccessor. IAM binding: Kubernetes service account is WorkloadIdentityUser on the GCP service account. No service account keys in the cluster.

### CI/CD with Workload Identity Federation
GitHub Actions workflow uses google-github-actions/auth action with Workload Identity Federation. Workload Identity Pool maps GitHub repository (attribute.repository == "org/repo") to a GCP service account. Service account has roles/artifactregistry.writer for pushing images and roles/run.developer for deploying to Cloud Run. Attribute conditions restrict to specific branches (attribute.ref == "refs/heads/main" for production). Separate service accounts per environment with different permission sets.

## See Also

- `general/identity.md` -- general identity and access management patterns
- `providers/gcp/security.md` -- GCP security operations, threat detection, and data protection
- `providers/gcp/networking.md` -- VPC Service Controls network context
