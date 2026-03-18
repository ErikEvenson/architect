# PCI DSS v4.0.1 - Cloud Control Mapping

## Scope

Covers PCI DSS v4.0.1 requirements for protecting cardholder data in cloud environments, including network segmentation, encryption, access control, logging, vulnerability management, and the shared responsibility model. Does not cover general encryption strategy (see `general/security.md`) or provider-specific networking details (see `providers/` files).

## Overview

PCI DSS (Payment Card Industry Data Security Standard) v4.0.1 applies to any entity that stores, processes, or transmits cardholder data. In cloud environments, responsibility is shared between the cloud provider and the customer. The provider typically covers physical security and infrastructure controls; the customer is responsible for configuration, application security, and data handling.

**Current Version:** PCI DSS v4.0.1 (June 2024) -- a limited revision of v4.0 with clarifications and corrections to guidance; no new or removed requirements. Organizations validated against v4.0 remain compliant.

**Effective Date:** PCI DSS v4.0 became mandatory March 31, 2024. Future-dated requirements became mandatory March 31, 2025. All assessments should now reference v4.0.1.

**Scope:** Any system component that stores, processes, or transmits cardholder data (CHD) or sensitive authentication data (SAD), plus any component that could affect the security of those systems.

---

## Requirement 1: Install and Maintain Network Security Controls

**Purpose:** Network security controls (firewalls, security groups, NACLs) restrict traffic between trusted and untrusted networks to protect cardholder data environments.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Network segmentation | VPC, Subnets | VNet, Subnets | VPC, Subnets |
| Firewall / traffic filtering | Security Groups, NACLs, AWS Network Firewall | NSGs, Azure Firewall | VPC Firewall Rules, Cloud Armor |
| Web application firewall | AWS WAF | Azure WAF | Cloud Armor WAF |
| Network monitoring | VPC Flow Logs, Traffic Mirroring | NSG Flow Logs, Network Watcher | VPC Flow Logs, Packet Mirroring |
| Private connectivity | PrivateLink, VPC Endpoints | Private Link, Service Endpoints | Private Service Connect |
| DNS security | Route 53 Resolver DNS Firewall | Azure DNS Private Resolver | Cloud DNS Response Policies |

### Architect Checklist

- [ ] **[Critical]** Cardholder Data Environment (CDE) is isolated in dedicated VPC/VNet with no direct internet ingress
- [ ] **[Recommended]** Security groups follow least-privilege: only required ports/protocols are open
- [ ] **[Critical]** NACLs or firewall rules provide defense-in-depth at the subnet level
- [ ] **[Recommended]** All inbound and outbound traffic rules are documented with business justification
- [ ] **[Critical]** Network segmentation is validated (CDE separated from non-CDE workloads)
- [ ] **[Recommended]** VPC Flow Logs / NSG Flow Logs are enabled and retained for at least 12 months
- [ ] **[Critical]** WAF is deployed in front of all public-facing payment applications
- [ ] **[Recommended]** Network architecture diagram is current and reviewed at least annually
- [ ] **[Critical]** All wireless networks connected to the CDE use strong encryption (WPA3 or equivalent)
- [ ] **[Critical]** Internal and external network penetration testing is performed at least annually

---

## Requirement 2: Apply Secure Configurations to All System Components

**Purpose:** Defaults shipped by vendors (passwords, settings, services) are well-known and exploitable. Systems must be hardened before deployment.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Configuration management | AWS Config, Systems Manager | Azure Policy, Azure Automation | Organization Policy, OS Config |
| Hardened images | EC2 Image Builder, CIS AMIs | Azure Image Builder, CIS images | Custom Images, Shielded VMs |
| Secrets management | Secrets Manager, Parameter Store | Key Vault | Secret Manager |
| Configuration compliance | AWS Config Rules, Security Hub | Azure Policy, Defender for Cloud | Security Command Center |
| Inventory management | AWS Config, Systems Manager Inventory | Azure Resource Graph | Cloud Asset Inventory |

### Architect Checklist

- [ ] **[Recommended]** All default vendor passwords are changed before deployment (databases, OS, middleware)
- [ ] **[Recommended]** Only one primary function per server (or container) to minimize attack surface
- [ ] **[Recommended]** Hardened base images (CIS benchmarks) are used for all compute instances
- [ ] **[Recommended]** Unnecessary services, protocols, and ports are disabled
- [ ] **[Recommended]** Configuration baselines are enforced via policy-as-code (AWS Config Rules, Azure Policy, OPA)
- [ ] **[Recommended]** Secrets are stored in dedicated secrets management services, never in code or config files
- [ ] **[Recommended]** System inventory is maintained and automatically updated
- [ ] **[Recommended]** TLS 1.2+ is required for all administrative and data access; TLS 1.0/1.1 are disabled
- [ ] **[Recommended]** Configuration drift detection is enabled and alerts on non-compliant changes

---

## Requirement 3: Protect Stored Account Data

**Purpose:** Cardholder data must be rendered unreadable wherever it is stored. If you do not need to store it, do not store it.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Encryption at rest | KMS, CloudHSM | Key Vault, Managed HSM, Azure Disk Encryption | Cloud KMS, Cloud HSM |
| Key management | KMS (CMK), CloudHSM | Key Vault (HSM-backed keys) | Cloud KMS, Cloud EKM |
| Tokenization | Payment Cryptography service | Azure Payment HSM | Custom (third-party) |
| Data classification | Macie | Purview Information Protection | DLP API, Sensitive Data Protection |
| Database encryption | RDS encryption, DynamoDB encryption | TDE, Azure Disk Encryption | Cloud SQL encryption, AlloyDB encryption |
| Storage encryption | S3 SSE-KMS, EBS encryption | Storage Service Encryption | Cloud Storage default encryption, CMEK |

### Architect Checklist

- [ ] **[Critical]** Primary Account Numbers (PANs) are rendered unreadable wherever stored (encryption, hashing, truncation, or tokenization)
- [ ] **[Critical]** Sensitive Authentication Data (SAD) is never stored after authorization
- [ ] **[Critical]** Customer-managed keys (CMK/CMEK) are used for encrypting cardholder data, not provider-managed keys
- [ ] **[Critical]** Key rotation is automated (at least annually for data-encrypting keys)
- [ ] **[Critical]** Split knowledge and dual control are enforced for key management operations
- [ ] **[Recommended]** HSM is used for key storage in environments processing high volumes of transactions
- [ ] **[Critical]** Data retention policies are defined and enforced -- cardholder data is deleted when no longer needed
- [ ] **[Critical]** Data discovery scans (Macie, Purview, DLP API) run regularly to detect unprotected cardholder data
- [ ] **[Recommended]** Masking is applied when displaying PANs (show only first 6 / last 4 digits)
- [ ] **[Critical]** Backups containing cardholder data are encrypted with the same rigor as primary data

---

## Requirement 4: Protect Cardholder Data with Strong Cryptography During Transmission Over Open, Public Networks

**Purpose:** Data in transit over public networks is vulnerable to interception. Strong cryptography must protect it.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| TLS termination | ALB, CloudFront, API Gateway | Application Gateway, Front Door, API Management | Cloud Load Balancer, Cloud CDN |
| Certificate management | ACM (Certificate Manager) | App Service Certificates, Key Vault | Certificate Manager |
| VPN / private transit | Site-to-Site VPN, Direct Connect | VPN Gateway, ExpressRoute | Cloud VPN, Cloud Interconnect |
| Service mesh TLS | App Mesh, EKS + Istio | AKS + Istio, Open Service Mesh | GKE + Istio / Anthos Service Mesh |
| API encryption | API Gateway (TLS enforcement) | API Management (TLS enforcement) | Apigee, API Gateway |

### Architect Checklist

- [ ] **[Critical]** TLS 1.2 or higher is enforced on all connections transmitting cardholder data
- [ ] **[Recommended]** SSL/TLS certificates use trusted Certificate Authorities and are not self-signed in production
- [ ] **[Recommended]** Certificate rotation is automated via ACM, Key Vault, or Certificate Manager
- [ ] **[Recommended]** Internal service-to-service communication uses mTLS (mutual TLS) in the CDE
- [ ] **[Critical]** VPN or private connectivity (Direct Connect, ExpressRoute, Interconnect) is used for backend data transfers
- [ ] **[Recommended]** Weak cipher suites (RC4, DES, 3DES, MD5) are explicitly disabled
- [ ] **[Recommended]** HSTS headers are enabled on all web-facing payment applications
- [ ] **[Critical]** End-to-end encryption is verified -- no unencrypted hops between services

---

## Requirement 5: Protect All Systems and Networks from Malicious Software

**Purpose:** Malware can compromise systems that store or process cardholder data. Anti-malware solutions must be deployed and maintained.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Malware detection | GuardDuty Malware Protection | Defender for Endpoint, Defender for Cloud | Security Command Center, Chronicle |
| Container scanning | ECR image scanning, Inspector | Defender for Containers | Artifact Analysis (Container Scanning) |
| Runtime protection | GuardDuty (EKS, EC2) | Defender for Servers | Security Command Center Premium |
| Email/phishing protection | SES (with scanning) | Defender for Office 365 | Workspace security (third-party) |
| File integrity monitoring | CloudWatch + custom, Inspector | Defender for Servers (FIM) | Security Command Center |

### Architect Checklist

- [ ] **[Recommended]** Anti-malware solutions are deployed on all systems commonly affected by malware (Windows, Linux servers)
- [ ] **[Recommended]** Anti-malware signatures are updated automatically and frequently (at least daily)
- [ ] **[Recommended]** Container images are scanned for malware and vulnerabilities before deployment
- [ ] **[Recommended]** Periodic full-system scans are configured in addition to real-time scanning
- [ ] **[Recommended]** Anti-malware logs are sent to centralized logging and reviewed
- [ ] **[Recommended]** Users cannot disable or alter anti-malware mechanisms
- [ ] **[Recommended]** Phishing protection mechanisms are deployed for email and messaging systems
- [ ] **[Recommended]** File integrity monitoring (FIM) is enabled for critical system files and configuration files

---

## Requirement 6: Develop and Maintain Secure Systems and Software

**Purpose:** Vulnerabilities in software can be exploited to access cardholder data. Secure development practices and timely patching are essential.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Vulnerability scanning | Inspector, ECR scanning | Defender for Cloud, Qualys integration | Artifact Analysis, Web Security Scanner |
| Patch management | Systems Manager Patch Manager | Azure Update Manager | OS Patch Management |
| Code analysis | CodeGuru Reviewer, third-party (Snyk, SonarQube) | DevOps (GitHub Advanced Security) | Cloud Build + third-party |
| Dependency scanning | Inspector SBOM, CodeArtifact | GitHub Dependabot, Defender for DevOps | Artifact Analysis |
| Change management | CloudFormation, CodePipeline | Azure DevOps, ARM/Bicep | Cloud Build, Cloud Deploy |
| WAF for application protection | AWS WAF (managed rules) | Azure WAF | Cloud Armor |

### Architect Checklist

- [ ] **[Recommended]** All custom and third-party software is inventoried and tracked
- [ ] **[Recommended]** Critical and high vulnerabilities are patched within 30 days of release; all others within 90 days
- [ ] **[Critical]** Automated vulnerability scanning runs at least weekly on all CDE components
- [ ] **[Recommended]** Secure coding practices are followed (OWASP Top 10 mitigated)
- [ ] **[Recommended]** Code reviews are performed before production deployment (manual or automated)
- [ ] **[Recommended]** SAST (static analysis) and DAST (dynamic analysis) are integrated into CI/CD pipelines
- [ ] **[Recommended]** Software composition analysis (SCA) is used to track third-party library vulnerabilities
- [ ] **[Recommended]** Change management processes require testing, approval, and rollback procedures
- [ ] **[Recommended]** Production and development/test environments are separated
- [ ] **[Critical]** Public-facing web applications are protected by a WAF or undergo application security assessments at least annually
- [ ] **[Recommended]** Bespoke and custom software undergoes security review before release

---

## Requirement 7: Restrict Access to System Components and Cardholder Data by Business Need to Know

**Purpose:** Access to cardholder data must be limited to personnel whose job requires it.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Identity and access management | IAM, IAM Identity Center (SSO) | Entra ID (formerly Azure AD), Conditional Access | Cloud IAM, Identity Platform |
| Role-based access control | IAM Roles, Policies | Azure RBAC, PIM | IAM Roles, Conditions |
| Privileged access management | IAM Identity Center, third-party (CyberArk) | Privileged Identity Management (PIM) | PAM (third-party), IAM Conditions |
| Access reviews | IAM Access Analyzer | Entra Access Reviews | IAM Recommender, Policy Analyzer |
| Attribute-based access | IAM Conditions, ABAC tags | ABAC via Entra ID | IAM Conditions, Tags |

### Architect Checklist

- [ ] **[Critical]** Access to cardholder data is restricted to individuals with documented business need
- [ ] **[Recommended]** RBAC is implemented -- roles are defined and assigned based on job function
- [ ] **[Critical]** Least privilege is enforced for all accounts (no wildcard permissions in CDE)
- [ ] **[Critical]** Access control lists are reviewed at least every six months
- [ ] **[Recommended]** IAM Access Analyzer / Entra Access Reviews / IAM Recommender are enabled
- [ ] **[Recommended]** Privileged access requires just-in-time elevation (PIM or equivalent)
- [ ] **[Recommended]** Default "deny all" access policy is in place -- access is explicitly granted
- [ ] **[Recommended]** Service accounts have minimal permissions and are reviewed regularly

---

## Requirement 8: Identify Users and Authenticate Access to System Components

**Purpose:** Every individual with access must be uniquely identified. Shared accounts obscure accountability.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Identity management | IAM Users, IAM Identity Center | Entra ID | Cloud Identity, Cloud IAM |
| Multi-factor authentication | IAM MFA, Identity Center MFA | Entra MFA, Conditional Access | 2-Step Verification, BeyondCorp |
| SSO | IAM Identity Center, Cognito | Entra ID SSO | Cloud Identity SSO, Identity Platform |
| Password policies | IAM password policy | Entra ID password protection | Cloud Identity password policies |
| Session management | STS (temporary credentials) | Managed Identities, SAS tokens | Service Account keys (short-lived) |

### Architect Checklist

- [ ] **[Critical]** Every user has a unique ID -- no shared or group accounts for CDE access
- [ ] **[Critical]** Multi-factor authentication (MFA) is required for all access to the CDE
- [ ] **[Critical]** MFA is required for all non-console administrative access
- [ ] **[Critical]** MFA is required for all remote network access
- [ ] **[Recommended]** Password policies enforce minimum 12 characters (or 8 characters with additional complexity)
- [ ] **[Recommended]** Passwords are changed at least every 90 days (v4.0 allows longer with risk analysis)
- [ ] **[Recommended]** Failed login attempts lock accounts after no more than 10 attempts
- [ ] **[Recommended]** Session timeout is enforced after 15 minutes of inactivity
- [ ] **[Critical]** Service accounts and application credentials use short-lived tokens where possible
- [ ] **[Critical]** Federated identity (SSO) is used to centralize authentication

---

## Requirement 9: Restrict Physical Access to Cardholder Data

**Purpose:** Physical access to systems or hardcopies of cardholder data must be controlled.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Data center physical security | AWS data center compliance (SOC 2, ISO 27001) | Azure data center compliance | Google data center compliance |
| Media handling | S3 lifecycle policies, EBS snapshots | Blob lifecycle, Managed Disk snapshots | Cloud Storage lifecycle, Persistent Disk snapshots |
| Secure destruction | AWS data destruction policies (per shared responsibility) | Azure data destruction | Google data destruction |
| Physical access logging | CloudTrail (API access logging) | Azure Activity Log | Cloud Audit Logs |

### Architect Checklist

- [ ] **[Critical]** Cloud provider's physical security certifications are verified (SOC 2 Type II, ISO 27001)
- [ ] **[Critical]** Data center locations are documented and aligned with data residency requirements
- [ ] **[Critical]** Media (disk snapshots, backups) containing cardholder data are encrypted and access-controlled
- [ ] **[Recommended]** Decommissioned storage (EBS, disks) is securely wiped per provider's data destruction policy
- [ ] **[Recommended]** Visitor access to on-premises components (if any) is logged and escorted
- [ ] **[Critical]** Point-of-interaction (POI) devices are inventoried and inspected for tampering (if applicable)
- [ ] **[Critical]** Paper records containing cardholder data are stored securely and destroyed via cross-cut shredding

---

## Requirement 10: Log and Monitor All Access to System Components and Cardholder Data

**Purpose:** Logging enables detection of and forensic response to security incidents.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| API / control plane logging | CloudTrail | Azure Activity Log, Monitor | Cloud Audit Logs |
| Application logging | CloudWatch Logs | Azure Monitor Logs, Log Analytics | Cloud Logging |
| SIEM / analytics | Security Hub, Detective, OpenSearch | Microsoft Sentinel | Chronicle, Security Command Center |
| Log storage | S3, CloudWatch Logs | Storage Account, Log Analytics | Cloud Storage, Cloud Logging buckets |
| Time synchronization | Amazon Time Sync Service | Azure NTP | Google NTP |
| Alerting | CloudWatch Alarms, EventBridge | Azure Monitor Alerts | Cloud Monitoring Alerts |
| Log integrity | CloudTrail log file validation | Immutable storage (WORM) | Locked retention policies |

### Architect Checklist

- [ ] **[Critical]** All access to cardholder data is logged (who, what, when, where, success/failure)
- [ ] **[Critical]** CloudTrail / Activity Log / Audit Logs are enabled in all regions and accounts
- [ ] **[Recommended]** Logs are stored centrally and retained for at least 12 months (3 months immediately accessible)
- [ ] **[Critical]** Log integrity is protected (CloudTrail validation, immutable storage, locked retention)
- [ ] **[Recommended]** SIEM or equivalent is deployed for log correlation and alerting
- [ ] **[Recommended]** Alerts are configured for critical security events (privilege escalation, failed logins, config changes)
- [ ] **[Recommended]** Time synchronization is enforced across all systems (NTP from authoritative source)
- [ ] **[Recommended]** Logs are reviewed at least daily (automated review is acceptable)
- [ ] **[Recommended]** Automated mechanisms detect and alert on anomalies and suspicious activity
- [ ] **[Recommended]** Log access is restricted to authorized personnel only

---

## Requirement 11: Test Security of Systems and Networks Regularly

**Purpose:** Regular testing validates that security controls remain effective over time.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Vulnerability scanning | Inspector | Defender for Cloud | Security Command Center, Web Security Scanner |
| Penetration testing | Permitted per AWS policy (no pre-approval needed for most services) | Permitted per Azure policy (no pre-approval needed) | Permitted per GCP policy (no pre-approval needed) |
| IDS/IPS | GuardDuty, Network Firewall (IPS mode) | Defender for Cloud, Azure Firewall Premium (IPS) | Cloud IDS, Cloud Armor |
| File integrity monitoring | CloudWatch agent, Inspector | Defender for Servers (FIM) | Security Command Center |
| Wireless detection | N/A (cloud-native) | N/A (cloud-native) | N/A (cloud-native) |
| Change detection | AWS Config, CloudTrail | Azure Policy, Activity Log | Security Command Center, Cloud Asset Inventory |

### Architect Checklist

- [ ] **[Critical]** Internal vulnerability scans are run at least quarterly and after significant changes
- [ ] **[Critical]** External vulnerability scans are performed quarterly by an ASV (Approved Scanning Vendor)
- [ ] **[Critical]** Internal and external penetration tests are conducted at least annually and after significant changes
- [ ] **[Critical]** Segmentation testing validates CDE isolation at least annually (every 6 months for service providers)
- [ ] **[Critical]** IDS/IPS is deployed to monitor traffic at the CDE perimeter and critical internal points
- [ ] **[Recommended]** File integrity monitoring (FIM) detects unauthorized changes to critical files
- [ ] **[Recommended]** Change detection mechanisms alert on unauthorized modifications to payment pages (Requirement 11.6.1)
- [ ] **[Recommended]** All identified vulnerabilities are ranked by risk and remediated per defined timelines

---

## Requirement 12: Support Information Security with Organizational Policies and Programs

**Purpose:** A strong security program requires governance, policies, risk management, and security awareness.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Policy enforcement | AWS Organizations SCPs, Config Rules | Azure Policy, Management Groups | Organization Policy, Assured Workloads |
| Risk assessment | Security Hub, Trusted Advisor | Defender for Cloud (Secure Score) | Security Command Center (Security Health Analytics) |
| Security awareness | N/A (organizational) | N/A (organizational) | N/A (organizational) |
| Incident response | GuardDuty, Detective, Security Hub | Sentinel, Defender for Cloud | Chronicle, Security Command Center |
| Third-party risk | AWS Artifact (compliance reports) | Service Trust Portal | Compliance Reports Manager |
| Compliance reporting | Audit Manager | Compliance Manager | Assured Workloads, Compliance Reports |

### Architect Checklist

- [ ] **[Recommended]** Information security policy is established, published, and reviewed at least annually
- [ ] **[Recommended]** Acceptable use policies cover all system components and technologies
- [ ] **[Recommended]** Risk assessment is performed at least annually and upon significant changes
- [ ] **[Recommended]** Security awareness training is conducted upon hire and at least annually
- [ ] **[Critical]** Incident response plan is documented, tested annually, and includes cardholder data breach procedures
- [ ] **[Recommended]** Third-party service providers are identified, risk-assessed, and monitored
- [ ] **[Critical]** Service provider compliance status (PCI DSS, SOC 2) is reviewed annually
- [ ] **[Recommended]** Responsibility matrix (RACI) between organization and cloud provider is documented
- [ ] **[Recommended]** Cloud provider's shared responsibility model is reviewed and gaps are addressed
- [ ] **[Critical]** PCI DSS scope is reviewed at least annually and after significant infrastructure changes
- [ ] **[Recommended]** Targeted risk analysis is performed for each PCI DSS requirement with flexibility (v4.0.1 customized approach)

---

## Cross-Cutting Concerns

### Shared Responsibility Model

PCI DSS compliance in the cloud requires understanding the shared responsibility boundary:

| Layer | Responsibility |
|-------|---------------|
| Physical security, hypervisor, host OS | Cloud provider |
| Network configuration (VPC, SGs, NACLs) | Customer |
| OS patching (IaaS) | Customer |
| OS patching (PaaS/managed services) | Cloud provider |
| Application security | Customer |
| Data encryption and key management | Customer |
| Identity and access management | Customer |
| Logging and monitoring configuration | Customer |

### Multi-Cloud Considerations

- [ ] **[Critical]** Each cloud provider's PCI DSS attestation of compliance (AOC) is obtained and reviewed
- [ ] **[Critical]** CDE scope includes all cloud environments where cardholder data is stored, processed, or transmitted
- [ ] **[Recommended]** Consistent security controls are applied across providers (policy-as-code recommended)
- [ ] **[Recommended]** Centralized logging aggregates events from all cloud providers
- [ ] **[Critical]** Network segmentation between cloud providers is validated

## Common Decisions (ADR Triggers)

- **CDE scope reduction** — tokenization vs encryption, network segmentation to minimize scope, point-to-point encryption
- **Network segmentation architecture** — CDE isolation design, firewall rules, microsegmentation, validation testing
- **Encryption and key management** — TDE vs application-level encryption, key custodian model, rotation policy, HSM usage
- **Vulnerability management program** — scanning tool selection, frequency (quarterly ASV + internal), remediation SLA
- **Logging and monitoring architecture** — centralized log aggregation, file integrity monitoring, event correlation, 1-year retention
- **WAF and DDoS protection** — WAF rule management, managed vs custom rules, DDoS mitigation tier
- **Access control model** — least privilege implementation, privileged access management, MFA for CDE access
- **Cloud provider responsibility mapping** — shared responsibility documentation per service, AOC review process
- **Penetration testing strategy** — application and network pen test scope, frequency, segmentation validation

## Reference Links

- [PCI SSC Document Library](https://www.pcisecuritystandards.org/document_library/) — official PCI DSS standards, SAQs, ROC templates, and supporting documents
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) — top 10 web application security risks referenced by PCI DSS Requirement 6
- [AWS PCI DSS](https://aws.amazon.com/compliance/pci-dss-level-1-faqs/) — AWS PCI DSS Level 1 compliance and shared responsibility guidance
- [Azure PCI DSS](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-pci-dss) — Azure PCI DSS compliance documentation and attestation of compliance

## See Also

- `general/security.md` — General security controls and encryption architecture
- `general/networking.md` — Network segmentation and firewall architecture
- `general/governance.md` — Cloud governance and policy enforcement
- `compliance/soc2.md` — SOC 2 criteria (complementary audit framework for service providers)
