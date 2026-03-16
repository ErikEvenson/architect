# HashiCorp Vault

## Checklist

- [ ] **[Critical]** Vault is deployed in HA mode with Raft storage (integrated) or Consul backend; single-node Vault is never acceptable for production
- [ ] **[Critical]** Auto-unseal is configured using a cloud KMS (AWS KMS, Azure Key Vault, GCP Cloud KMS) to eliminate manual unseal key management and enable automated restarts
- [ ] **[Critical]** Unseal key shares and recovery keys are distributed according to Shamir's Secret Sharing threshold (e.g., 5 shares, 3 required); root token is revoked after initial setup
- [ ] **[Critical]** Auth methods are configured for each consumer type: AppRole for CI/CD and applications, Kubernetes auth for pods, OIDC for human operators, AWS IAM for EC2/Lambda
- [ ] **[Critical]** Policies follow least privilege: each application role has a policy granting access only to its specific secret paths with minimum required capabilities (read, list, create, update, delete)
- [ ] **[Recommended]** KV v2 secrets engine is used (not v1) for versioning, soft-delete, metadata, and check-and-set operations; max versions and delete_version_after are configured per mount
- [ ] **[Recommended]** Dynamic secrets are used for databases (PostgreSQL, MySQL, MongoDB), AWS IAM, and cloud credentials; static credentials are eliminated wherever dynamic alternatives exist
- [ ] **[Recommended]** Lease TTLs and max TTLs are set appropriately: short-lived database credentials (1 hour default, 24 hour max), longer for less sensitive secrets; applications handle lease renewal
- [ ] **[Recommended]** PKI secrets engine is configured with an offline root CA; intermediate CAs are mounted in Vault and issue short-lived certificates (30-90 days) with automated renewal
- [ ] **[Optional]** Transit secrets engine is used for encryption-as-a-service when applications need to encrypt data without managing encryption keys directly; key rotation is scheduled
- [ ] **[Critical]** Audit logging is enabled on at least two audit devices (file + syslog, or file + socket); Vault refuses to process requests if all audit devices fail (security property)
- [ ] **[Recommended]** Vault Agent or Vault Sidecar Injector is deployed for Kubernetes workloads to handle authentication, secret retrieval, and lease renewal without application-level Vault SDK integration
- [ ] **[Recommended]** Is the Vault Secrets Operator (VSO) evaluated for Kubernetes-native secret syncing as an alternative to Agent/Sidecar Injector?
- [ ] **[Optional]** Namespaces (Enterprise) isolate tenants or teams with independent auth, policies, and secrets engines; root namespace is reserved for platform administration
- [ ] **[Critical]** Disaster recovery and performance replication (Enterprise) or regular Raft snapshots (OSS) are configured and tested with documented RTO/RPO

## Why This Matters

Vault is the system that protects every other system's credentials. If Vault is unavailable, applications cannot retrieve secrets and new deployments stall. If Vault is compromised, every secret it manages is exposed. Auto-unseal eliminates the operational burden of manual unsealing (which blocks automated recovery) but transfers trust to the cloud KMS, which must be separately secured. Dynamic secrets eliminate the credential rotation problem entirely: a leaked database password expires in an hour without any intervention. But applications must handle credential rotation during their lifetime, or connections fail mid-request. Audit logging is a security invariant: Vault will halt operations if it cannot write audit logs, which means an audit backend failure causes an outage unless redundant backends are configured.

## License

HashiCorp transitioned all products from MPL 2.0 to BSL 1.1 in August 2023. The BSL restricts competitive use of the software — you cannot use it to build a product that competes with HashiCorp's commercial offerings. For internal infrastructure use, the BSL is functionally equivalent to open source. Community forks under MPL 2.0 exist: OpenTofu (Terraform fork) and OpenBao (Vault fork). Evaluate license terms for your specific use case before adoption.

## Common Decisions (ADR Triggers)

- **Storage backend: Integrated Raft vs Consul**: Raft (integrated since Vault 1.4) eliminates the Consul dependency, simplifies operations, and is now HashiCorp's recommended backend. Consul storage makes sense if Consul is already deployed for service discovery and the team has Consul operational expertise. New deployments should default to Raft unless there is a specific reason to use Consul.
- **Auth method per consumer type**: AppRole (role_id + secret_id) is versatile for CI/CD and applications. Kubernetes auth validates service account tokens against the cluster's API server. OIDC delegates to an external identity provider (Okta, Azure AD) for human access. AWS IAM auth lets EC2 instances and Lambda functions authenticate using their IAM role. Each auth method has different security properties and operational requirements; document which is used where and why.
- **Static vs dynamic secrets**: Dynamic secrets (Vault generates short-lived credentials on demand) are strictly superior to static secrets from a security perspective but require application support for credential rotation. Start with dynamic secrets for databases and cloud providers; fall back to KV for third-party API keys that cannot be dynamically generated.
- **Vault Agent vs application-native SDK**: Vault Agent runs as a sidecar or daemon, handles auth, caches secrets, and renders templates to files. Applications read secrets from files or environment variables without any Vault awareness. Native SDK integration gives finer control (explicit lease renewal, dynamic secret rotation in connection pools) but couples the application to Vault. Agent is simpler; SDK is more capable.
- **PKI architecture (certificate authority)**: Mount an offline root CA (never in Vault) and use Vault as an intermediate CA for issuing leaf certificates. Decide certificate lifetimes (shorter is more secure but requires reliable automation), allowed domains (restrict with `allowed_domains` and `enforce_hostname`), and whether to use Vault for mTLS between services or only for external-facing TLS.
- **Enterprise namespaces vs OSS path-based isolation**: Namespaces provide true multi-tenancy with independent auth, policies, and secrets engines. OSS can approximate isolation with path prefixes and carefully scoped policies, but cross-path leaks are possible with policy mistakes. For regulated environments or multi-team platforms, Enterprise namespaces are strongly preferred.
- **Secrets sprawl management**: As teams onboard, secret paths proliferate without governance. Decide on a path naming convention (e.g., `secret/data/{team}/{env}/{app}/{key}`), who can create new mounts, and how to audit unused secrets. Vault's `sys/leases` and audit logs help identify stale credentials.

## Reference Architectures

### Production HA Deployment (AWS)

```
                    +---------------------+
                    |   AWS KMS Key        |
                    |   (auto-unseal)      |
                    +----------+----------+
                               |
          +--------------------+--------------------+
          |                    |                     |
+---------v------+   +---------v------+   +---------v------+
| Vault Node 1   |   | Vault Node 2   |   | Vault Node 3   |
| (Raft Leader)  |<->| (Raft Follower)|<->| (Raft Follower)|
| m5.xlarge      |   | m5.xlarge      |   | m5.xlarge      |
| AZ: us-east-1a |   | AZ: us-east-1b |   | AZ: us-east-1c |
+-------+--------+   +-------+--------+   +-------+--------+
        |                     |                     |
        +----------+----------+----------+----------+
                   |                     |
          +--------v--------+   +--------v--------+
          | NLB (port 8200) |   | NLB (port 8201) |
          | (API traffic)   |   | (cluster traffic)|
          +-----------------+   +-----------------+

Storage: Raft integrated (data on encrypted EBS gp3)
Audit: CloudWatch Logs + S3 (dual audit devices)
Snapshots: Raft auto-snapshots to S3 every 4 hours
TLS: ACM cert on NLB, self-signed Vault-to-Vault
```

### Kubernetes Integration

```
Kubernetes Cluster
  |
  +-- Vault Agent Injector (Deployment in vault namespace)
  |     Mutating webhook intercepts pod creation
  |     Injects vault-agent init + sidecar containers
  |
  +-- Application Pod (annotated)
  |     Annotations:
  |       vault.hashicorp.com/agent-inject: "true"
  |       vault.hashicorp.com/role: "app-frontend"
  |       vault.hashicorp.com/agent-inject-secret-db: "database/creds/app-frontend"
  |       vault.hashicorp.com/agent-inject-template-db: |
  |         {{- with secret "database/creds/app-frontend" -}}
  |         postgresql://{{ .Data.username }}:{{ .Data.password }}@db:5432/app
  |         {{- end }}
  |
  |     Init container (vault-agent):
  |       Authenticates via Kubernetes auth method
  |       Retrieves secrets, writes to /vault/secrets/db
  |
  |     Sidecar (vault-agent):
  |       Renews lease before expiration
  |       Re-renders template when credentials rotate
  |
  |     App container:
  |       Reads /vault/secrets/db (file-based, no SDK needed)
  |       Watches file for changes (inotify) or periodic re-read

Vault Server (external or in-cluster):
  |-- Auth: kubernetes (bound to cluster's SA token reviewer API)
  |-- Role: app-frontend
  |     bound_service_account_names: ["app-frontend"]
  |     bound_service_account_namespaces: ["production"]
  |     policies: ["app-frontend-policy"]
  |-- Policy: app-frontend-policy
  |     path "database/creds/app-frontend" { capabilities = ["read"] }
  |     path "secret/data/app-frontend/*"  { capabilities = ["read", "list"] }
```

### Multi-Environment Secrets Organization

```
Vault Secret Paths:

secret/
  |-- data/
       |-- platform/
       |    |-- dev/
       |    |    |-- database        (host, port, name)
       |    |    |-- redis           (host, port, auth token)
       |    |-- prod/
       |         |-- database
       |         |-- redis
       |
       |-- app-frontend/
       |    |-- dev/
       |    |    |-- api-keys        (stripe-test, sendgrid-sandbox)
       |    |    |-- oauth           (client-id, client-secret)
       |    |-- prod/
       |         |-- api-keys        (stripe-live, sendgrid-prod)
       |         |-- oauth
       |
       |-- shared/
            |-- ssl-certs            (wildcard cert for *.example.com)
            |-- encryption-keys      (transit key references)

database/                            (dynamic secrets engine)
  |-- creds/
       |-- app-frontend-readonly     (SELECT only, 1hr TTL)
       |-- app-backend-readwrite     (SELECT/INSERT/UPDATE/DELETE, 1hr TTL)
       |-- migration-admin           (ALL PRIVILEGES, 15min TTL)

pki/                                 (intermediate CA)
  |-- issue/
       |-- internal-service          (*.internal.example.com, 30-day cert)
       |-- external-web              (www.example.com, 90-day cert)

transit/
  |-- encrypt/app-encryption-key     (AES-256-GCM, auto-rotate every 90 days)
  |-- decrypt/app-encryption-key
```
