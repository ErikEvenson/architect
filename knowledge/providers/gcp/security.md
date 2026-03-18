# GCP Security

## Scope

Security Command Center (Standard, Premium, Enterprise), VPC Service Controls, Cloud Audit Logging, Binary Authorization, Secret Manager, Cloud KMS (CMEK, CSEK, EKM), organization policies, Shielded VM. For IAM, identity, and access management details, see `iam.md` if available; this file covers security operations, threat detection, data protection, and compliance controls.

## Checklist

- [ ] [Critical] Are dedicated service accounts created per workload with minimal IAM roles, replacing the default Compute Engine and App Engine service accounts?
- [ ] [Critical] Is Workload Identity Federation configured for external workloads (CI/CD, AWS, Azure) to eliminate service account key files?
- [ ] [Recommended] Are IAM Conditions used to scope permissions by resource, time, or request attributes where fine-grained access is needed?
- [ ] [Critical] Is organization policy service used to enforce constraints across the organization? (e.g., restrict public IP creation, enforce uniform bucket-level access, disable service account key creation)
- [ ] [Critical] Is Secret Manager used for all application secrets, API keys, and certificates, with automatic replication and IAM-based access control?
- [ ] [Recommended] Are secrets versioned in Secret Manager with the application pinned to a specific version or using the "latest" alias with rotation?
- [ ] [Critical] Is Security Command Center (SCC) enabled at the organization level? Select the appropriate tier: Standard (free, basic vulnerability findings), Premium (threat detection, vulnerability scanning, compliance monitoring), or Enterprise (SIEM/SOAR integration, attack path simulation, Mandiant threat intelligence, case management)
- [ ] [Recommended] Is SCC integrated with Cloud Asset Inventory for real-time resource change tracking and policy compliance?
- [ ] [Critical] Are VPC Service Controls perimeters configured around sensitive projects to prevent data exfiltration via Google APIs?
- [ ] [Recommended] Is Cloud Audit Logging configured for all services with Admin Activity (always on), Data Access (must be enabled), and System Event logs?
- [ ] [Recommended] Is Binary Authorization enabled for GKE to enforce container image signing and verification before deployment?
- [ ] [Recommended] Are IAM recommender and Policy Analyzer used to identify overly permissive roles and unused permissions?
- [ ] [Recommended] Is Cloud KMS used with customer-managed encryption keys (CMEK) for regulated workloads, with key rotation policies configured?
- [ ] [Critical] Are service account keys disabled via organization policy, with Workload Identity and impersonation used instead?

## Why This Matters

GCP IAM is fundamentally different from AWS and Azure: it operates at the project, folder, and organization level with inherited permissions. The default service accounts have overly broad permissions (Editor role). Service account key files are the most common source of credential leaks. VPC Service Controls provide a unique data exfiltration prevention mechanism not available in other clouds. Organization policies are the primary mechanism for preventive guardrails.

Security Command Center has three tiers with significant capability differences. Standard (free) provides basic security findings. Premium adds Event Threat Detection (detecting crypto-mining, data exfiltration, brute force), Container Threat Detection, and compliance reporting (CIS, PCI-DSS, NIST). Enterprise (newest tier) adds Chronicle SIEM/SOAR integration, attack path simulation showing how vulnerabilities could be exploited, Mandiant threat intelligence feeds, and case management for security incidents. Most production environments should use Premium at minimum; Enterprise is appropriate for organizations with dedicated security operations teams.

## Common Decisions (ADR Triggers)

- **Identity model** -- Google Workspace vs Cloud Identity vs federated SAML/OIDC, workforce identity pools
- **Service account strategy** -- per-workload accounts vs shared accounts, key-less (Workload Identity) vs key-based
- **Organization policy scope** -- organization-wide constraints vs folder-level exceptions, custom constraints
- **VPC Service Controls** -- which projects in perimeters, access levels, ingress/egress rules, dry-run mode
- **SCC tier** -- Standard (free, limited findings) vs Premium (threat detection, compliance, vulnerability scanning) vs Enterprise (SIEM/SOAR, attack path simulation, Mandiant intelligence, case management)
- **Encryption model** -- Google-managed keys vs CMEK (Cloud KMS) vs CSEK (customer-supplied), EKM for external keys
- **Secret management** -- Secret Manager vs HashiCorp Vault, replication policy (automatic vs user-managed regions)

## Reference Architectures

- [Google Cloud Architecture Center: Security](https://cloud.google.com/architecture#security) -- reference architectures for IAM, encryption, and security operations
- [Google Cloud Architecture Framework: Security, privacy, and compliance](https://cloud.google.com/architecture/framework/security) -- comprehensive security best practices for identity, data protection, and incident response
- [Google Cloud: Enterprise foundations blueprint](https://cloud.google.com/architecture/security-foundations) -- reference architecture for organization structure, IAM, VPC Service Controls, and logging
- [Google Cloud: Best practices for using VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs) -- reference patterns for data exfiltration prevention and service perimeter design
- [Google Cloud: Security Command Center architecture](https://cloud.google.com/security-command-center/docs/concepts-security-command-center-overview) -- reference design for centralized vulnerability management and threat detection

## See Also

- `general/security.md` -- general security architecture patterns
- `providers/gcp/iam.md` -- GCP IAM roles, policies, and Workload Identity Federation
- `providers/gcp/networking.md` -- VPC Service Controls and Cloud Armor
- `providers/gcp/observability.md` -- Cloud Audit Logs and monitoring
