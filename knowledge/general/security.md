# Security

## Scope

This file covers **what** security controls an architecture must address — compliance, identity, secrets, encryption, network security, access management, audit, and incident response — regardless of cloud provider or on-premises platform. For provider-specific **how** (IAM policies, security groups, managed services), see the provider security files linked in See Also.

## Checklist

- [ ] **[Critical]** Identify applicable compliance standards (PCI DSS, HIPAA, SOC 2, GDPR, FedRAMP, NIST 800-53) and map each to specific technical controls — do not assume "we'll handle compliance later" because retroactive compliance reshapes architecture
- [ ] **[Critical]** Design the IAM strategy around least privilege: define role hierarchy, enforce service account separation per workload, require short-lived credentials (OIDC federation, instance profiles, workload identity) over long-lived API keys, and establish a periodic access review cadence
- [ ] **[Critical]** Select a secrets management platform (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, CyberArk) and define how secrets reach workloads — mounted files or sidecar injection are preferred over environment variables, which leak into process tables, crash dumps, and orchestrator APIs
- [ ] **[Critical]** Enforce encryption at rest for all data stores (databases, object storage, block volumes, backups) — decide between provider-managed keys (SSE-S3, Azure SSE), customer-managed keys in a KMS, or HSM-backed keys based on compliance requirements and key rotation obligations
- [ ] **[Critical]** Enforce encryption in transit (TLS) for all connections including internal service-to-service traffic — set minimum TLS 1.2 (TLS 1.3 preferred), disable weak cipher suites, and decide whether to terminate TLS at the load balancer, at each service (end-to-end), or via a service mesh (mTLS)
- [ ] **[Critical]** Design firewall and security group rules using default-deny with explicit allow lists between network tiers — define rules per application tier (web, app, data), restrict source CIDR ranges, and document every exception with a business justification
- [ ] **[Critical]** Define the administrative access model: bastion host (dedicated jump box in a hardened subnet), cloud-native session manager (AWS SSM, Azure Bastion), VPN with MFA, or zero trust network access (ZTNA) — each has different audit trail depth, credential exposure risk, and operational overhead
- [ ] **[Critical]** Enable comprehensive audit logging for all API calls, data access, authentication events, and privilege escalation — send logs to a tamper-resistant destination (separate account, WORM storage) with retention aligned to compliance requirements (typically 1-7 years)
- [ ] **[Critical]** Establish a security incident response plan: define severity levels, escalation paths, communication templates, containment procedures, and forensic evidence preservation — test the plan with tabletop exercises at least annually
- [ ] **[Recommended]** Define patch management SLAs by severity: critical CVEs within 24-72 hours, high within 7 days, medium within 30 days — automate patch deployment for OS and container base images, and track patching compliance with a dashboard
- [ ] **[Recommended]** Implement vulnerability scanning across the full stack: container image scanning in CI/CD pipelines (Trivy, Snyk, Prisma), OS-level scanning (Qualys, Nessus, Rapid7), dependency scanning (Dependabot, Renovate), and runtime vulnerability detection
- [ ] **[Recommended]** Deploy a WAF with appropriate rule sets (OWASP Top 10, bot mitigation, rate limiting) and DDoS protection (cloud-native shield services or CDN-based mitigation) — decide between managed rule sets vs. custom rules based on application risk profile
- [ ] **[Recommended]** Design network segmentation beyond basic tier separation: evaluate micro-segmentation for east-west traffic, zero trust architecture principles (verify every request, assume breach), and whether a service mesh (Istio, Linkerd, Consul Connect) should enforce mTLS and authorization policies between services
- [ ] **[Recommended]** Implement automatic secret rotation with defined rotation periods (90 days recommended, 30 days for high-sensitivity) — ensure applications handle rotation gracefully without downtime using dual-secret or lazy-refresh patterns
- [ ] **[Optional]** Deploy intrusion detection and threat detection systems (AWS GuardDuty, Azure Defender, GCP Security Command Center, or third-party SIEM) with automated response playbooks for common attack patterns

## Why This Matters

Security breaches are existential risks that extend far beyond technical remediation. A single compromised credential, unpatched vulnerability, or misconfigured security group can lead to data exfiltration, ransomware deployment, or regulatory action. The average cost of a data breach exceeds $4 million, and regulated industries face additional penalties — HIPAA violations carry fines up to $2 million per incident category, PCI DSS non-compliance can result in transaction processing bans, and GDPR fines can reach 4% of global annual revenue.

The most common security architecture failures are not exotic zero-day exploits but fundamental design gaps: overly permissive IAM roles that grant admin access to application workloads, secrets stored in environment variables or committed to source control, security groups that allow 0.0.0.0/0 inbound access "temporarily" and never get tightened, and audit logging that is either disabled or sends logs to a destination the attacker can delete. These gaps persist because security controls are often treated as a post-deployment checklist rather than an integral part of the architecture design.

A well-designed security architecture assumes breach (zero trust), limits blast radius through segmentation and least privilege, detects anomalies through comprehensive logging and monitoring, and enables rapid response through pre-planned incident procedures. Security decisions made during architecture design — IAM model, network topology, secrets management approach, encryption strategy — are extremely expensive to change after deployment, making it critical to get them right early.

## Common Decisions (ADR Triggers)

### ADR: Compliance Framework Selection

**Context:** The organization must identify which compliance standards apply and how they shape the technical architecture.

**Options:**

| Framework | Applicability | Key Technical Requirements | Certification Effort |
|---|---|---|---|
| SOC 2 Type II | SaaS companies, any org handling customer data | Access controls, logging, encryption, change management, availability monitoring | 6-12 months initial, annual audit |
| PCI DSS | Any system that stores, processes, or transmits cardholder data | Network segmentation, encryption, access logging, vulnerability scanning, penetration testing | 3-6 months, annual assessment (QSA or SAQ) |
| HIPAA | Healthcare data (PHI) | Encryption at rest and in transit, access controls, audit trails, BAAs with vendors, breach notification | Ongoing, no formal certification — OCR audits |
| GDPR | Any system processing EU personal data | Data minimization, right to erasure, consent management, DPO appointment, cross-border transfer controls | Ongoing, supervisory authority enforcement |
| FedRAMP | Cloud services used by US federal agencies | NIST 800-53 controls, continuous monitoring, boundary definition, 3PAO assessment | 12-18 months, continuous monitoring |

**Decision drivers:** Customer requirements, data classification, geographic scope (EU data requires GDPR), industry vertical, and whether the organization plans to sell to government or regulated industries in the future.

### ADR: Secrets Management Approach

**Context:** Application workloads need access to database credentials, API keys, TLS certificates, and encryption keys without exposing them in code, config files, or environment variables.

**Options:**
- **HashiCorp Vault:** Platform-agnostic, supports dynamic secrets (generates short-lived credentials on demand), integrates with Kubernetes via sidecar injector or CSI driver. Requires operating and securing the Vault cluster itself (or using HCP Vault managed service). Best for multi-cloud or on-premises environments.
- **Cloud-native secrets manager (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager):** Fully managed, integrates with provider IAM, supports automatic rotation for supported secret types (RDS credentials, service account keys). Simplest to operate. Creates provider lock-in for the secrets layer.
- **Kubernetes Secrets with external sync (External Secrets Operator):** Syncs secrets from an external source (Vault, AWS SM, Azure KV) into Kubernetes Secrets. Applications consume standard K8s secrets without knowing the backend. Adds a reconciliation layer that must be monitored.
- **Mounted files from sealed secrets or SOPS:** Secrets encrypted in Git (Sealed Secrets, Mozilla SOPS), decrypted at deploy time and mounted as files. Enables GitOps workflow for secrets. Rotation requires redeployment.

**Decision drivers:** Multi-cloud vs. single-cloud, whether dynamic/short-lived secrets are needed, team operational capacity to manage Vault, compliance requirements for secret auditability, and whether a GitOps workflow is in use.

### ADR: Administrative Access Model

**Context:** Engineers and operators need secure access to production infrastructure for troubleshooting and maintenance without exposing management interfaces to the internet.

**Options:**
- **Bastion host (jump box):** Dedicated hardened instance in a DMZ subnet. SSH or RDP through the bastion to reach internal resources. Requires managing the bastion instance, patching it, and controlling SSH keys. Audit trail depends on session logging configuration.
- **Cloud session manager (AWS SSM Session Manager, Azure Bastion):** No inbound ports required, no SSH keys to manage. Full session logging to CloudTrail/CloudWatch or Azure Monitor. Requires cloud provider IAM for access control. No connectivity without cloud API access.
- **VPN with MFA:** Site-to-site or client VPN (WireGuard, OpenVPN, cloud-native VPN) places users on internal network. Broader access than bastion — must be combined with strict security group rules. MFA is mandatory.
- **Zero trust network access (ZTNA):** Identity-aware proxy (Cloudflare Access, Zscaler, BeyondCorp) verifies user identity, device posture, and context before granting per-resource access. No VPN or bastion required. Highest security posture, most complex initial setup.

**Recommendation:** For cloud environments, prefer cloud session manager (SSM/Azure Bastion) for its built-in audit trail and elimination of SSH key management. For hybrid or on-premises environments, deploy a hardened bastion with session recording, or evaluate ZTNA for organizations with mature identity infrastructure.

### ADR: Encryption Key Management

**Context:** Encryption at rest requires key management — who generates keys, where they are stored, how they are rotated, and who can access them.

**Options:**
- **Provider-managed keys (default encryption):** Cloud provider generates and manages keys (SSE-S3, Azure SSE with platform keys). Zero operational overhead. No customer control over key lifecycle. Acceptable for most workloads.
- **Customer-managed keys in cloud KMS:** Customer creates keys in AWS KMS, Azure Key Vault, or GCP Cloud KMS. Full control over key rotation, access policies, and audit logging. Keys never leave the provider's HSM boundary. Small per-key and per-API-call cost.
- **Customer-managed keys in external HSM (BYOK/HYOK):** Keys generated in on-premises HSM (Thales, Entrust) and imported into cloud KMS, or used directly via HSM-as-a-service. Required by some regulatory frameworks (banking, government). Highest operational complexity.

**Decision drivers:** Regulatory requirements for key custody, whether the organization needs to revoke cloud provider access to data, multi-cloud key portability needs, and operational capacity to manage HSM infrastructure.

### ADR: Network Security Architecture

**Context:** The architecture must define how network traffic is segmented, filtered, and monitored between tiers and between services.

**Options:**
- **Traditional tier-based segmentation:** Web tier, application tier, data tier on separate subnets with security groups/NACLs controlling traffic between tiers. Well-understood, maps to compliance frameworks. Coarse-grained — all services in a tier can communicate freely.
- **Micro-segmentation with service mesh:** Per-service network policies (Kubernetes NetworkPolicy, Calico, Cilium) combined with service mesh mTLS (Istio, Linkerd). Every service-to-service connection is explicitly authorized. Fine-grained but operationally complex.
- **Zero trust with identity-aware proxy:** All access — user and service — is authenticated and authorized per request regardless of network location. Eliminates implicit trust within the network perimeter. Requires mature identity infrastructure and comprehensive policy definition.

**Decision drivers:** Number of services (micro-segmentation benefits increase with service count), compliance requirements for network isolation, team familiarity with service mesh operations, and whether east-west traffic poses a significant threat in the environment.

## Reference Links

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Trivy](https://trivy.dev/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [Snyk](https://snyk.io/)

## See Also

- `providers/aws/iam.md` — AWS IAM roles, policies, and access management
- `providers/aws/secrets-manager.md` — AWS Secrets Manager configuration
- `providers/azure/security.md` — Azure security controls and identity
- `providers/gcp/security.md` — GCP security controls and IAM
- `general/observability.md` — Audit logging overlaps with observability; coordinate log destinations and retention
- `general/networking.md` — Network segmentation, firewall design, and VPN architecture
- `patterns/zero-trust.md` — Zero trust architecture principles, identity-aware proxies, and microsegmentation
- `patterns/network-segmentation.md` — Network segmentation patterns including micro-segmentation and east-west traffic controls
- `general/ransomware-resilience.md` — Ransomware-specific resilience controls, detection, and recovery playbooks
