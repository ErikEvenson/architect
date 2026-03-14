# GCP Security

## Checklist

- [ ] Are dedicated service accounts created per workload with minimal IAM roles, replacing the default Compute Engine and App Engine service accounts?
- [ ] Is Workload Identity Federation configured for external workloads (CI/CD, AWS, Azure) to eliminate service account key files?
- [ ] Are IAM Conditions used to scope permissions by resource, time, or request attributes where fine-grained access is needed?
- [ ] Is organization policy service used to enforce constraints across the organization? (e.g., restrict public IP creation, enforce uniform bucket-level access, disable service account key creation)
- [ ] Is Secret Manager used for all application secrets, API keys, and certificates, with automatic replication and IAM-based access control?
- [ ] Are secrets versioned in Secret Manager with the application pinned to a specific version or using the "latest" alias with rotation?
- [ ] Is Security Command Center (SCC) enabled at the organization level with Premium tier for vulnerability scanning, threat detection, and compliance monitoring?
- [ ] Is SCC integrated with Cloud Asset Inventory for real-time resource change tracking and policy compliance?
- [ ] Are VPC Service Controls perimeters configured around sensitive projects to prevent data exfiltration via Google APIs?
- [ ] Is Cloud Audit Logging configured for all services with Admin Activity (always on), Data Access (must be enabled), and System Event logs?
- [ ] Is Binary Authorization enabled for GKE to enforce container image signing and verification before deployment?
- [ ] Are IAM recommender and Policy Analyzer used to identify overly permissive roles and unused permissions?
- [ ] Is Cloud KMS used with customer-managed encryption keys (CMEK) for regulated workloads, with key rotation policies configured?
- [ ] Are service account keys disabled via organization policy, with Workload Identity and impersonation used instead?

## Why This Matters

GCP IAM is fundamentally different from AWS and Azure: it operates at the project, folder, and organization level with inherited permissions. The default service accounts have overly broad permissions (Editor role). Service account key files are the most common source of credential leaks. VPC Service Controls provide a unique data exfiltration prevention mechanism not available in other clouds. Organization policies are the primary mechanism for preventive guardrails.

## Common Decisions (ADR Triggers)

- **Identity model** -- Google Workspace vs Cloud Identity vs federated SAML/OIDC, workforce identity pools
- **Service account strategy** -- per-workload accounts vs shared accounts, key-less (Workload Identity) vs key-based
- **Organization policy scope** -- organization-wide constraints vs folder-level exceptions, custom constraints
- **VPC Service Controls** -- which projects in perimeters, access levels, ingress/egress rules, dry-run mode
- **SCC tier** -- Standard (free, limited findings) vs Premium (threat detection, compliance, vulnerability scanning)
- **Encryption model** -- Google-managed keys vs CMEK (Cloud KMS) vs CSEK (customer-supplied), EKM for external keys
- **Secret management** -- Secret Manager vs HashiCorp Vault, replication policy (automatic vs user-managed regions)

## Reference Architectures

- [Google Cloud Architecture Center: Security](https://cloud.google.com/architecture#security) -- reference architectures for IAM, encryption, and security operations
- [Google Cloud Architecture Framework: Security, privacy, and compliance](https://cloud.google.com/architecture/framework/security) -- comprehensive security best practices for identity, data protection, and incident response
- [Google Cloud: Enterprise foundations blueprint](https://cloud.google.com/architecture/security-foundations) -- reference architecture for organization structure, IAM, VPC Service Controls, and logging
- [Google Cloud: Best practices for using VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs/best-practices) -- reference patterns for data exfiltration prevention and service perimeter design
- [Google Cloud: Security Command Center architecture](https://cloud.google.com/security-command-center/docs/concepts-security-command-center-overview) -- reference design for centralized vulnerability management and threat detection
