# Kubernetes Security

## Checklist

- [ ] **[Critical]** Implement RBAC with least-privilege: create namespace-scoped Roles (not ClusterRoles) for application teams, bind to groups (not individual users) via RoleBindings
- [ ] **[Recommended]** Enforce Pod Security Standards (PSS): apply restricted profile to production namespaces, baseline to development, privileged only to system namespaces
- [ ] **[Recommended]** Deploy a policy engine (OPA/Gatekeeper or Kyverno) for custom admission policies beyond PSS: image registry allowlists, label requirements, resource limit enforcement
- [ ] **[Recommended]** Design secrets management strategy: external-secrets-operator (sync from Vault/AWS SM/GCP SM), sealed-secrets (encrypted in Git), or CSI secrets store driver (mount from Vault)
- [ ] **[Recommended]** Configure image signing and verification: Cosign for signing, Kyverno/Connaisseur/Sigstore Policy Controller for admission-time verification
- [ ] **[Recommended]** Plan admission controller pipeline: validating webhooks before mutating webhooks, ensure failure mode is understood (fail-open vs fail-closed)
- [ ] **[Recommended]** Implement runtime security monitoring: Falco for syscall-based threat detection, Tetragon for eBPF-based enforcement, or cloud-native equivalents
- [ ] **[Recommended]** Configure audit logging: set audit policy to capture authentication, authorization, and resource modification events; ship to SIEM
- [ ] **[Recommended]** Plan service account token management: disable automounting of default service account tokens, use bound service account tokens (audience-scoped, time-limited)
- [ ] **[Recommended]** Implement network segmentation: namespace-level NetworkPolicies with default-deny, allow only required pod-to-pod and egress flows
- [ ] **[Recommended]** Evaluate image scanning in CI/CD (Trivy, Grype, Snyk) and runtime (continuous scanning of running images for new CVEs)
- [ ] **[Recommended]** Plan etcd encryption at rest: configure EncryptionConfiguration for Secrets, use KMS provider for key management (AWS KMS, GCP KMS, Azure Key Vault)
- [ ] **[Recommended]** Design break-glass procedures: emergency access methods that bypass normal RBAC for incident response, with audit trail

## Why This Matters

Kubernetes defaults are permissive: pods run as root, all pods can communicate with all other pods, service account tokens are auto-mounted, and secrets are stored as base64 (not encrypted) in etcd. A compromised pod in a default Kubernetes cluster can escalate privileges, move laterally to any namespace, read all secrets, and potentially escape to the host. Each checklist item addresses a specific attack vector. RBAC limits blast radius of credential compromise. Pod Security Standards prevent container escape techniques (privileged containers, hostPath mounts, host networking). Policy engines enforce organizational standards that PSS does not cover. External secrets management eliminates secrets from Git history and provides rotation. Runtime security detects attacks in progress that static configuration cannot prevent.

## Common Decisions (ADR Triggers)

- **OPA/Gatekeeper vs Kyverno**: Gatekeeper uses Rego (a dedicated policy language) which is powerful but has a learning curve. Kyverno uses YAML-native policies that are easier to write and understand for Kubernetes-focused teams. Gatekeeper is more mature for complex cross-resource policies. Kyverno is simpler for common use cases (require labels, restrict image registries, generate default resources). Choose Kyverno for Kubernetes-focused teams; Gatekeeper for teams with Rego expertise or complex policy requirements.
- **Secrets management approach**: External-secrets-operator syncs secrets from external stores (Vault, AWS Secrets Manager) into Kubernetes Secrets, making them available via standard env vars and volume mounts. CSI Secrets Store Driver mounts secrets directly as volumes without creating Kubernetes Secret objects (more secure but less compatible). Sealed-secrets encrypts secrets in Git for GitOps workflows. Use external-secrets-operator for most teams; CSI driver for high-security environments; sealed-secrets for small teams starting with GitOps.
- **Pod Security Standards vs custom policies**: PSS provides three predefined profiles (privileged, baseline, restricted) enforced natively without third-party tools. Custom policy engines (Kyverno/Gatekeeper) offer granular control beyond PSS. Use PSS as the baseline for all namespaces; add Kyverno/Gatekeeper for organization-specific policies (image registries, label requirements, resource quotas).
- **Image signing enforcement**: Cosign signs images with keyless signing (Fulcio + Rekor) or key-based signing. Enforcement at admission requires a policy engine (Kyverno verifyImages, Sigstore Policy Controller). The trade-off is between security (all images must be signed) and developer velocity (signing adds CI/CD steps and admission failures block deployment). Start with audit mode, then enforce.
- **Falco vs Tetragon for runtime security**: Falco uses kernel module or eBPF probes for syscall monitoring with a rule-based detection engine. Tetragon (from Cilium) uses eBPF for both detection and enforcement (can kill processes, not just alert). Falco has a larger rule library and community. Tetragon provides enforcement capabilities. Use Falco for detection-focused deployments; Tetragon when enforcement at the kernel level is required.

## Reference Architectures

### Defense-in-Depth Security Model
```
[Layer 1: CI/CD Pipeline]
  - Image scanning (Trivy/Grype)
  - Image signing (Cosign)
  - SBOM generation
  - Secret scanning (git-secrets/trufflehog)

[Layer 2: Admission Control]
  - Pod Security Standards (restricted)
  - Kyverno/Gatekeeper policies
  - Image signature verification
  - Resource requirement enforcement

[Layer 3: Runtime]
  - RBAC (namespace-scoped, least-privilege)
  - NetworkPolicies (default-deny)
  - Service mesh mTLS
  - Falco/Tetragon runtime detection

[Layer 4: Data Protection]
  - etcd encryption at rest (KMS-backed)
  - External secrets management (Vault)
  - Bound service account tokens
  - Audit logging to SIEM
```
Each layer operates independently so failure or bypass of one layer does not compromise the others. CI/CD prevents vulnerable images from being built. Admission control prevents non-compliant resources from being created. Runtime controls detect and prevent attacks in running workloads. Data protection ensures secrets and state are encrypted and auditable.

### RBAC Design Pattern
```
[ClusterRoles (cluster-wide)]
  - cluster-admin: full access (break-glass only)
  - cluster-viewer: read-only across all namespaces (SRE)
  - namespace-admin: full access within a namespace (template)

[Namespace-scoped Roles]
  - app-deployer: create/update Deployments, Services, ConfigMaps
  - app-viewer: read-only on Deployments, Pods, Services, Logs
  - secret-manager: read/write Secrets (separate from app-deployer)

[Bindings]
  - IdP Group "platform-team" --> ClusterRoleBinding to "cluster-viewer"
  - IdP Group "team-alpha"    --> RoleBinding to "app-deployer" in ns "alpha"
  - IdP Group "team-alpha"    --> RoleBinding to "app-viewer" in ns "alpha"
  - break-glass SA            --> ClusterRoleBinding to "cluster-admin" (audited)
```
Bind to IdP groups (via OIDC) not individual users. Separate secret access from deployment access. Break-glass cluster-admin access via a dedicated service account with enhanced audit logging, not granted to human users by default.

### Secrets Pipeline
```
[External Secret Store (Vault / AWS Secrets Manager)]
        |
  [External Secrets Operator]
  - ExternalSecret CR references store path
  - Syncs to Kubernetes Secret on schedule (e.g., 1 min)
  - Rotation: new versions auto-synced
        |
  [Kubernetes Secret]
  - Encrypted at rest (etcd KMS provider)
  - Namespace-scoped RBAC
        |
  +-----+------+
  |            |
[Env Var]   [Volume Mount]
(12-factor) (file-based config)

[Alternative: CSI Secrets Store Driver]
  - Vault provider mounts secrets directly as tmpfs volume
  - No Kubernetes Secret object created
  - Auto-rotation with rotation poll interval
  - Requires sidecar or init container
```
External Secrets Operator is the most common pattern: it creates standard Kubernetes Secrets from external stores, compatible with any application. CSI driver is more secure (secrets never stored in etcd) but requires application support for file-based secret consumption. Both support rotation; ESO re-syncs periodically, CSI driver polls the external store.
