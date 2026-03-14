# Kubernetes Secrets Management

## Checklist

- [ ] **[Critical]** Are secrets NEVER committed to git in plain text or base64-encoded form? (base64 is encoding, NOT encryption)
- [ ] **[Critical]** Is etcd encryption at rest configured via EncryptionConfiguration if using native K8s Secrets in any non-dev environment?
- [ ] **[Critical]** Is RBAC configured to restrict who can read Secrets (get, list, watch) in each namespace?
- [ ] **[Critical]** Are secrets rotated on a defined schedule, and is the rotation mechanism automated?
- [ ] **[Recommended]** Is a secrets management strategy chosen and documented in an ADR before the first secret is created?
- [ ] **[Recommended]** Are secrets scoped to individual namespaces rather than shared across namespaces?
- [ ] **[Recommended]** Is Sealed Secrets or External Secrets Operator used for GitOps workflows so encrypted/referenced secrets can be stored in git?
- [ ] **[Recommended]** Is an external secret store (Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) used for production workloads?
- [ ] **[Recommended]** Are secret access patterns audited via Kubernetes audit logging or the external store's audit log?
- [ ] **[Recommended]** Is the refresh interval for External Secrets Operator configured appropriately (balancing freshness vs API rate limits)?
- [ ] **[Optional]** Are dynamic secrets (database credentials with TTL) used via Vault for high-security workloads?
- [ ] **[Optional]** Is the CSI Secrets Store driver evaluated for workloads that should never materialize secrets as K8s Secret objects?
- [ ] **[Optional]** Is Vault Agent Injector configured for workloads requiring sidecar-based secret injection with automatic renewal?
- [ ] **[Optional]** Are secret management costs (Vault license, cloud secret store API calls) tracked and budgeted?

## Why This Matters

Secrets are the keys to every system -- database credentials, API tokens, TLS certificates, encryption keys. A leaked secret can compromise an entire environment. Kubernetes Secrets are base64-encoded by default, which provides zero security; anyone with API access can decode them instantly. Committing secrets to git (even "temporarily") creates a permanent record in git history that is difficult to fully remove. The right secrets management approach depends on team size, compliance requirements, and operational maturity, but every team must make a deliberate choice rather than defaulting to plain K8s Secrets in production.

## Decision Matrix

| Approach | Security | GitOps Safe | Complexity | Cost | Best For |
|----------|----------|-------------|------------|------|----------|
| K8s Secrets | Low | No | Low | Free | Dev/POC |
| Sealed Secrets | Medium | Yes | Low | Free | Small teams, GitOps |
| External Secrets | High | Yes | Medium | Free + store cost | Multi-cloud, teams using cloud SM |
| Vault Agent | Highest | Yes | High | Vault license | Enterprise, dynamic secrets |
| CSI Driver | High | N/A | Medium | Store cost | AWS-native, EKS |

## Approaches in Detail

### Kubernetes Secrets (Built-in)

Native K8s Secrets are base64-encoded, NOT encrypted by default. They are stored in etcd and accessible to anyone with the appropriate RBAC permissions.

- **Encoding is not encryption**: `echo "password" | base64` is trivially reversible. Do not treat base64 as a security measure.
- **etcd encryption at rest**: Configure `EncryptionConfiguration` on the API server to encrypt Secret data in etcd using AES-CBC, AES-GCM, or a KMS provider. Without this, secrets are stored in plaintext in etcd.
- **RBAC controls**: Restrict `get`, `list`, and `watch` on Secrets to only the service accounts and users that need them.
- **Acceptable for**: Dev, POC, learning environments.
- **Risk**: Anyone with API access (or etcd access) can read all secrets in a namespace.

### Sealed Secrets (Bitnami)

Encrypted secrets that are safe to store in git. A cluster-side controller decrypts them into regular K8s Secrets.

- **One-way encryption**: You encrypt locally using `kubeseal` with the cluster's public key. The sealed secret can only be decrypted by the controller in the target cluster.
- **GitOps safe**: The SealedSecret resource can be committed to git -- it is encrypted and useless without the cluster's private key.
- **Cannot read back**: Once sealed, you cannot extract the original value from the SealedSecret manifest. Keep the original secret values in a secure location.
- **Cluster-scoped key**: If the controller's private key is lost (e.g., cluster rebuild), all SealedSecrets become unreadable. Back up the key.
- **Best for**: Small teams adopting GitOps, environments where an external secret store is overkill.

### External Secrets Operator (ESO)

Syncs secrets from external stores into K8s Secrets using CRDs.

- **Supported stores**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, and many others.
- **CRDs**: `SecretStore` (namespaced) or `ClusterSecretStore` (cluster-wide) defines the connection to the external store. `ExternalSecret` defines which secrets to sync and how to map them.
- **Refresh intervals**: Configurable per ExternalSecret. Secrets are periodically re-synced from the external store. Balance freshness against API rate limits and cost (cloud providers charge per API call).
- **GitOps safe**: ExternalSecret manifests contain references (secret names/paths), not values. Safe to commit to git.
- **Best for**: Teams already using a cloud secret manager, multi-cloud environments, organizations with centralized secret management.

### Vault Agent Injector (HashiCorp Vault)

Sidecar container injects secrets as files into pod filesystems. The most feature-rich but most complex option.

- **Sidecar pattern**: A Vault Agent init container authenticates and fetches secrets; a sidecar container handles renewal. Secrets are written to a shared volume.
- **Dynamic secrets**: Vault can generate database credentials with a TTL -- credentials are unique per pod and automatically expire. This is the strongest pattern for database access.
- **PKI certificates**: Vault's PKI engine issues short-lived TLS certificates for service-to-service communication.
- **Audit logging**: Vault provides detailed audit logs of every secret access, meeting compliance requirements.
- **Complexity**: Requires running and operating Vault itself (or using HCP Vault). Authentication, policies, and secret engines must be configured.
- **Best for**: Enterprise environments, compliance-heavy workloads, dynamic secret requirements.

### AWS Secrets Manager + CSI Driver

Mounts secrets directly as files in pods via the Secrets Store CSI driver. Secrets never materialize as K8s Secret objects.

- **SecretProviderClass**: CRD that defines which secrets to mount from AWS Secrets Manager (or SSM Parameter Store).
- **No K8s Secret created**: By default, secrets are only available as mounted files -- they never exist as K8s Secret resources. (Optional sync to K8s Secrets is available but reduces the security benefit.)
- **IAM-based access**: Uses IRSA (IAM Roles for Service Accounts) on EKS for fine-grained access control.
- **Best for**: AWS-native workloads on EKS, organizations wanting to minimize K8s Secret surface area.

## Common Mistakes

- **Committing secrets to git**: Even if removed in a later commit, secrets persist in git history. Use `git filter-branch` or BFG Repo-Cleaner, and rotate the compromised secret immediately.
- **Treating base64 as encryption**: `base64` is a reversible encoding. It provides zero confidentiality.
- **Not rotating secrets**: Secrets should be rotated regularly. Automation (Vault dynamic secrets, Secrets Manager rotation) is strongly preferred.
- **Sharing secrets across namespaces**: Copying the same secret into multiple namespaces increases blast radius. Use per-namespace secrets with distinct credentials where possible.
- **Forgetting to back up Sealed Secrets keys**: If the cluster is rebuilt without the controller's private key, all SealedSecrets are lost.
- **Over-broad RBAC**: Granting `get secrets` at the cluster level rather than the namespace level exposes secrets across all namespaces.

## Common Decisions (ADR Triggers)

- **Native K8s Secrets vs external secret store** -- simplicity vs security posture; almost always choose an external store for production
- **Sealed Secrets vs External Secrets Operator** -- self-contained GitOps vs integration with an existing cloud secret manager
- **Vault vs cloud-native secret manager** -- feature richness and dynamic secrets vs lower operational overhead
- **CSI driver vs K8s Secret sync** -- secrets-as-files with no K8s Secret object vs compatibility with workloads expecting K8s Secrets
- **Secret rotation strategy** -- manual rotation with runbooks vs automated rotation (Vault, Secrets Manager auto-rotate)
- **Namespace isolation vs shared secrets** -- per-namespace credentials vs a shared secret store with cross-namespace access

## Reference Architectures

- [Kubernetes Documentation: Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) -- native Secret resource, types, and best practices
- [Kubernetes Documentation: Encrypting Secrets at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) -- EncryptionConfiguration for etcd
- [Bitnami Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) -- encrypting secrets for safe git storage
- [External Secrets Operator](https://external-secrets.io/) -- syncing secrets from external stores into K8s
- [Vault Agent Injector](https://developer.hashicorp.com/vault/docs/platform/k8s/injector) -- sidecar-based secret injection for Kubernetes
- [AWS Secrets Store CSI Driver](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html) -- mounting AWS secrets directly into pods
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) -- general secrets management guidance
