# Azure RBAC and Managed Identities

## Scope

Azure role-based access control (RBAC) at depth and the workload identity model that depends on it. Covers role definitions, scope inheritance (management group → subscription → resource group → resource), built-in vs custom roles, role assignment vs deny assignment, ABAC condition expressions, system-assigned vs user-assigned managed identities, federated identity credentials for OIDC workloads (GitHub Actions, GitLab CI, AKS workload identity), Privileged Identity Management (PIM) for just-in-time elevation, the cross-tenant access model (Entra B2B and B2C), and the audit characteristics of standing role assignments vs eligible-via-PIM. Does not cover Entra ID directory roles (admin roles like Global Administrator), which are a separate role catalog managed at the directory layer rather than the Azure Resource Manager layer.

## Checklist

- [ ] **[Critical]** Use **built-in roles** wherever they fit. Azure publishes ~150 built-in roles covering most common access patterns. Custom roles should be created only when no built-in role matches the actual permission set, because custom roles are versioned per subscription and require explicit management.
- [ ] **[Critical]** Apply role assignments at the **lowest scope that works**. A role assignment at the management group level inherits to every child subscription, resource group, and resource — which is appropriate for "this role applies everywhere" but is over-broad for workload-specific permissions. Default to resource group scope, escalate to subscription only when needed.
- [ ] **[Critical]** Avoid the **`Owner`** and **`Contributor`** built-in roles for workload identities. `Owner` includes the ability to assign roles (which means the workload can grant itself any permission). `Contributor` excludes role assignment but still includes write on every resource type. Use a more specific role (e.g., `Storage Blob Data Contributor`, `Key Vault Secrets User`) that grants only what the workload actually needs.
- [ ] **[Critical]** Use **managed identities** for every Azure resource that calls another Azure resource. Managed identities eliminate the need to store credentials anywhere — the identity is bound to the resource (system-assigned) or to a named identity that can be referenced from multiple resources (user-assigned). Anything that uses a connection string or a service principal client secret to talk to another Azure resource is a finding waiting to happen.
- [ ] **[Critical]** For CI/CD pipelines that deploy to Azure (GitHub Actions, GitLab CI, Bitbucket, Jenkins), use **federated identity credentials** on a user-assigned managed identity instead of a service principal client secret. Federated credentials let the pipeline exchange its OIDC token for an Azure access token without any long-lived secret in the pipeline configuration. This is the canonical pattern that replaces "service principal with a client secret in a GitHub Actions secret".
- [ ] **[Critical]** Enable **Privileged Identity Management (PIM)** for any role assignment with write or owner permissions on shared resources. PIM converts a standing role assignment into an eligible-only assignment that requires explicit activation, with optional approval, MFA challenge, justification, and a configurable maximum duration. The audit posture of "all writes were activated through PIM" is dramatically better than "all writes were possible at all times".
- [ ] **[Critical]** Audit standing **`Owner`** assignments at the subscription and management group level. Standing Owner is the broadest possible permission set and is the easiest single misconfiguration to lateral-move from. PIM-eligible Owner is acceptable for break-glass; standing Owner is almost never the right answer outside of break-glass.
- [ ] **[Recommended]** Use **deny assignments** for "no exceptions" controls that should never be bypassed. Deny assignments are stronger than `Deny` policy because they cannot be overridden by even the subscription Owner. Useful for blocking specific actions on specific resources (e.g., "no one can delete the central Log Analytics workspace").
- [ ] **[Recommended]** Use **ABAC conditions** on role assignments where the access pattern is conditional. Example: "Storage Blob Data Reader, but only on blobs with the `DataClassification=public` tag". ABAC reduces the number of role assignments needed when access is otherwise data-driven.
- [ ] **[Recommended]** Prefer **user-assigned managed identities** over system-assigned for any identity that is referenced from multiple resources or from infrastructure-as-code. User-assigned identities have a stable identity ID that survives resource recreation, which makes IaC and disaster recovery cleaner. System-assigned identities are tied to the lifecycle of a single resource and are recreated (with a new identity ID) when the resource is recreated.
- [ ] **[Recommended]** Use **AKS workload identity** (the federated credential model for pods) instead of the deprecated AAD pod-managed identity. Workload identity uses the same federated credential mechanism as GitHub Actions OIDC and is the supported pattern going forward.
- [ ] **[Recommended]** Document the role assignment for every workload identity in the IaC that creates it. The role assignment should be created from the same Bicep / Terraform that creates the managed identity, not added manually after the fact.
- [ ] **[Recommended]** Audit **guest user accounts** in Entra ID. Guest accounts (B2B) often accumulate over time as external collaborators are added and never removed. Quarterly access reviews via Entra ID Access Reviews are the right control.
- [ ] **[Optional]** For workloads that need cross-tenant access, use **Entra B2B direct connect** or **Cross-tenant access settings** with explicit trust configuration. Avoid the older "guest user with manual role assignment" pattern, which is hard to audit.
- [ ] **[Optional]** Use **Conditional Access policies** to require specific conditions (compliant device, MFA, location, sign-in risk) for high-privilege role activation in PIM. The combination of PIM + Conditional Access is the strongest practical access control for privileged operations.

## Why This Matters

Azure RBAC is the foundation of every other access control in Azure. A misconfigured RBAC posture undermines every other control: Key Vault access policies / RBAC, Storage account access, SQL access, Cosmos DB access, AKS access, and so on. Three failure modes drive most of the high-value findings:

1. **Standing high-privilege assignments.** A user or workload identity with `Owner` or `Contributor` at the subscription level is one compromise away from full subscription control. PIM eliminates the standing-assignment failure mode by requiring explicit, time-bound activation. The fact that PIM is a paid feature (Entra ID P2) is the most common reason it is not deployed, and the cost is almost always justified by the audit posture improvement.
2. **Service principals with client secrets.** Every secret stored in a CI/CD system, in a configuration file, in a Key Vault that is itself accessed via a secret, in environment variables, or in any other persistent location is a credential exposure waiting to happen. Federated identity credentials and managed identities eliminate this category entirely by replacing the secret with a token exchange that happens at runtime.
3. **Roles that are too broad.** `Contributor` is the role that gets assigned when no one wants to think about what permissions are actually needed. It works, but it grants write on every resource type in the scope, which is almost always more than the workload needs. The fix is one-time work — figure out what permissions the workload actually needs, find or create a role that grants exactly that, assign it. The result is a role that documents the workload's intended permission set, which is the difference between RBAC as a checkbox and RBAC as a control.

A secondary failure mode that compounds the first three: role assignments that were appropriate when created but became inappropriate as the organization changed. People leave teams, projects end, contractors finish, but the role assignments persist. The fix is **periodic access reviews** — Entra ID Access Reviews can be scheduled per role assignment, per group, or per resource scope, and require an explicit reaffirmation (or removal) on a defined cadence.

## Common Decisions (ADR Triggers)

- **Built-in role vs custom role** — built-in for any access pattern that maps to an existing role definition. Custom only when no built-in role matches. Custom roles add management overhead (versioning per subscription, JSON definition files, separate update path) and should be rare.
- **System-assigned vs user-assigned managed identity** — user-assigned for IaC-managed identities, identities referenced from multiple resources, and identities that need to survive resource recreation. System-assigned for one-off workloads where the identity is conceptually owned by the resource and should not outlive it.
- **Federated identity vs service principal with secret** — federated identity for any CI/CD pipeline that supports OIDC (GitHub Actions, GitLab CI, Bitbucket Pipelines, Buildkite, modern Jenkins). Service principal with secret only for legacy systems that do not yet support OIDC, and only as a temporary measure.
- **PIM eligible vs standing assignment** — PIM eligible for any role assignment with write or owner permissions on shared resources. Standing assignment for read-only roles where the operational friction of activation outweighs the security benefit. Document the reasoning per assignment.
- **Subscription-scope vs resource group-scope role assignment** — resource group is the right default for workload-specific permissions. Subscription scope is appropriate for cross-cutting roles (Reader for monitoring tooling, Network Contributor for the network team). Avoid management group scope for anything that is not strictly tenant-wide.

## Reference Architectures

### CI/CD pipeline deploying to Azure via OIDC (GitHub Actions example)

- User-assigned managed identity in the workload subscription, named after the pipeline (`uami-github-deploy-prod-app`)
- Federated identity credential on the UAMI, with `subject` set to `repo:org/repo:environment:production` and `issuer` set to `https://token.actions.githubusercontent.com`
- RBAC assignment: UAMI gets `Contributor` on the resource group it deploys to (or a more specific role if possible)
- GitHub Actions workflow uses `azure/login@v2` with `client-id`, `tenant-id`, `subscription-id` from secrets (not the client secret) and the OIDC token is exchanged for an Azure access token at runtime
- No client secret anywhere. Rotation is implicit (tokens are short-lived).

### Workload identity for AKS pod accessing Key Vault

- AKS cluster has OIDC issuer enabled and workload identity feature enabled
- User-assigned managed identity in the workload subscription
- Federated identity credential on the UAMI with `subject` set to `system:serviceaccount:<namespace>:<service-account-name>` and `issuer` set to the AKS OIDC issuer URL
- Kubernetes service account in the namespace, annotated with the UAMI client ID
- Pod uses the service account; the Azure SDK exchanges the projected service account token for an Azure access token automatically
- Key Vault RBAC grants the UAMI `Key Vault Secrets User` on the specific secret (or vault)

### Privileged operation via PIM

- Engineer has `Eligible` assignment for `Network Contributor` on the connectivity subscription
- Engineer requests activation in the Entra portal, providing justification and (if configured) requesting approval
- Approver receives notification, approves
- Engineer's role assignment becomes active for a configurable duration (default 8 hours, max usually 24)
- Engineer performs the operation; the operation is logged in Azure Activity Log with the activated role context
- Role assignment auto-expires; the engineer returns to read-only state

### Standing break-glass account

- A small number (typically 2) of standing global administrator accounts in Entra ID, used only for break-glass recovery
- Accounts are excluded from Conditional Access (so they work even when CA is misconfigured) — this is intentional and is the only legitimate exclusion
- Credentials are stored in a physical safe, not in a password manager
- Sign-ins are alerted on (any sign-in to a break-glass account is an incident)
- Activity is reviewed quarterly

---

## Reference Links

- [Azure RBAC documentation](https://learn.microsoft.com/azure/role-based-access-control/)
- [Built-in role definitions](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles)
- [Managed identities for Azure resources](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Workload identity federation](https://learn.microsoft.com/entra/workload-id/workload-identity-federation)
- [Privileged Identity Management](https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure)
- [ABAC conditions for role assignments](https://learn.microsoft.com/azure/role-based-access-control/conditions-overview)

## See Also

- `providers/azure/identity.md` — broader Entra ID and identity service coverage
- `providers/azure/key-vault.md` — RBAC permission model for Key Vault
- `providers/azure/landing-zones.md` — RBAC baseline as part of the landing zone deployment
- `providers/azure/security.md` — Defender for Cloud and Microsoft Sentinel
- `providers/aws/iam.md` — equivalent identity service in AWS
