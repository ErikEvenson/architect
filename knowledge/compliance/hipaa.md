# HIPAA Security Rule - Cloud Control Mapping

## Overview

The HIPAA Security Rule (45 CFR Part 160 and Subparts A and C of Part 164) establishes standards for protecting electronic Protected Health Information (ePHI). It requires covered entities and business associates to implement administrative, physical, and technical safeguards.

**Applicability:** Covered entities (health plans, healthcare clearinghouses, healthcare providers who transmit health information electronically) and their business associates.

**Key Principle:** HIPAA safeguards are categorized as "required" (R) or "addressable" (A). Addressable does not mean optional -- it means the entity must implement the safeguard, implement an equivalent alternative, or document why neither is reasonable and accept the risk.

**Cloud Considerations:** A Business Associate Agreement (BAA) must be in place with any cloud provider handling ePHI. AWS, Azure, and GCP all offer HIPAA BAAs, but only for specific eligible services.

---

## Administrative Safeguards (45 CFR 164.308)

### 164.308(a)(1) - Security Management Process (R)

**Purpose:** Implement policies and procedures to prevent, detect, contain, and correct security violations.

#### Implementation Specifications

**Risk Analysis (R):** Conduct an accurate and thorough assessment of risks to ePHI.
**Risk Management (R):** Implement security measures to reduce risks to a reasonable level.
**Sanction Policy (R):** Apply sanctions against workforce members who violate policies.
**Information System Activity Review (R):** Regularly review system activity records (audit logs, access reports).

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Risk assessment | Security Hub, Trusted Advisor, Inspector | Defender for Cloud (Secure Score), Compliance Manager | Security Command Center, Security Health Analytics |
| Compliance posture | Audit Manager (HIPAA framework) | Compliance Manager (HIPAA assessment) | Assured Workloads |
| Activity review | CloudTrail, CloudWatch | Activity Log, Log Analytics | Cloud Audit Logs, Cloud Logging |
| Policy enforcement | Organizations SCPs, Config Rules | Azure Policy, Management Groups | Organization Policy |

#### Architect Checklist

- [ ] Risk analysis covering all ePHI is documented and updated at least annually
- [ ] Risk management plan addresses identified risks with specific mitigation measures
- [ ] AWS Audit Manager / Azure Compliance Manager / Assured Workloads is configured with HIPAA assessment
- [ ] Security Hub / Defender for Cloud / Security Command Center provides continuous compliance monitoring
- [ ] System activity logs are reviewed regularly (automated alerting preferred)
- [ ] Sanction policy is documented and enforceable

---

### 164.308(a)(2) - Assigned Security Responsibility (R)

**Purpose:** Designate a security official responsible for developing and implementing security policies.

#### Architect Checklist

- [ ] A Security Officer is designated with documented responsibilities
- [ ] Security responsibilities for cloud environments are clearly assigned (cloud team, security team, DevOps)
- [ ] Cloud provider's shared responsibility model is documented and gaps are assigned to internal teams

---

### 164.308(a)(3) - Workforce Security (A)

**Purpose:** Ensure workforce members have appropriate access to ePHI and prevent unauthorized access.

#### Implementation Specifications

**Authorization and/or Supervision (A):** Ensure workforce access is appropriate.
**Workforce Clearance Procedure (A):** Determine if access is appropriate before granting.
**Termination Procedures (A):** Revoke access when employment ends or role changes.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Identity lifecycle | IAM Identity Center, IAM | Entra ID, Lifecycle Workflows | Cloud Identity, Cloud IAM |
| Access reviews | IAM Access Analyzer | Entra Access Reviews | IAM Recommender |
| Automated deprovisioning | IAM Identity Center (SCIM) | Entra ID (SCIM, Lifecycle Workflows) | Cloud Identity (SCIM) |

#### Architect Checklist

- [ ] Onboarding process includes access approval workflow before granting ePHI access
- [ ] Access reviews are conducted periodically (at least quarterly for ePHI systems)
- [ ] Offboarding process includes automated revocation of all cloud access within 24 hours
- [ ] SCIM provisioning is enabled for automated identity lifecycle management
- [ ] Role changes trigger access re-evaluation

---

### 164.308(a)(4) - Information Access Management (R)

**Purpose:** Implement policies for authorizing access to ePHI consistent with the minimum necessary standard.

#### Implementation Specifications

**Isolating Healthcare Clearinghouse Functions (R):** Clearinghouse isolation if applicable.
**Access Authorization (A):** Policies for granting access to ePHI.
**Access Establishment and Modification (A):** Policies for establishing, documenting, reviewing, and modifying access.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| RBAC | IAM Roles, Policies | Azure RBAC, Entra Roles | Cloud IAM Roles |
| Least privilege | IAM Access Analyzer, permission boundaries | PIM, Conditional Access | IAM Recommender, IAM Conditions |
| Resource isolation | Separate accounts (Organizations), VPCs | Separate subscriptions, VNets | Separate projects, VPCs |
| Data access controls | S3 policies, RDS IAM auth, Lake Formation | Storage ACLs, SQL RBAC, Purview | IAM, BigQuery column-level security |

#### Architect Checklist

- [ ] ePHI workloads are isolated in dedicated accounts/subscriptions/projects
- [ ] RBAC roles are defined for each job function with minimum necessary access
- [ ] No wildcard (*) permissions exist for resources containing ePHI
- [ ] Access to ePHI datasets uses fine-grained controls (row-level, column-level where applicable)
- [ ] Access authorization is documented and approved by data owner
- [ ] Minimum necessary standard is applied -- users access only the ePHI they need

---

### 164.308(a)(5) - Security Awareness and Training (A)

**Purpose:** Implement a security awareness and training program for all workforce members.

#### Implementation Specifications

**Security Reminders (A):** Periodic security updates.
**Protection from Malicious Software (A):** Procedures for guarding against malware.
**Log-in Monitoring (A):** Procedures for monitoring log-in attempts.
**Password Management (A):** Procedures for creating, changing, and safeguarding passwords.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Login monitoring | CloudTrail (ConsoleLogin events), GuardDuty | Entra Sign-in Logs, Risky Sign-ins | Cloud Audit Logs, BeyondCorp |
| Malware protection | GuardDuty Malware Protection | Defender for Endpoint | Security Command Center |
| Password policy | IAM password policy | Entra ID password protection | Cloud Identity password policies |

#### Architect Checklist

- [ ] Security awareness training includes cloud-specific topics (phishing, credential handling, MFA)
- [ ] Failed login alerts are configured in GuardDuty / Entra / Cloud Audit Logs
- [ ] Password policies enforce strong passwords (minimum 12 characters recommended)
- [ ] Anti-malware is deployed on all systems that process ePHI
- [ ] Periodic security reminders are distributed to all personnel with ePHI access

---

### 164.308(a)(6) - Security Incident Procedures (R)

**Purpose:** Implement policies and procedures to address security incidents.

#### Implementation Specifications

**Response and Reporting (R):** Identify, respond to, and mitigate security incidents; document and outcomes.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Threat detection | GuardDuty, Security Hub | Sentinel, Defender for Cloud | Chronicle, Security Command Center |
| Incident investigation | Detective, CloudTrail Lake | Sentinel Investigation, Log Analytics | Chronicle SIEM |
| Automated response | EventBridge + Lambda, Security Hub actions | Sentinel Playbooks (Logic Apps) | Cloud Functions + Pub/Sub, Chronicle SOAR |
| Forensics | EC2 snapshot + analysis, CloudTrail | Disk snapshots, Activity Log | Disk snapshots, Audit Logs |

#### Architect Checklist

- [ ] Incident response plan specifically addresses ePHI breaches
- [ ] HIPAA Breach Notification Rule requirements are incorporated (60-day notification window)
- [ ] Automated threat detection is enabled (GuardDuty, Sentinel, Chronicle)
- [ ] Incident response playbooks are defined for common cloud scenarios (credential compromise, data exposure, ransomware)
- [ ] Forensic capabilities are pre-configured (snapshot automation, log preservation)
- [ ] Incidents are documented with root cause analysis and remediation tracking

---

### 164.308(a)(7) - Contingency Plan (R)

**Purpose:** Establish policies and procedures for responding to emergencies that damage systems containing ePHI.

#### Implementation Specifications

**Data Backup Plan (R):** Create and maintain retrievable exact copies of ePHI.
**Disaster Recovery Plan (R):** Procedures to restore lost data.
**Emergency Mode Operation Plan (R):** Enable continuation of critical processes during emergencies.
**Testing and Revision Procedures (A):** Periodically test and revise contingency plans.
**Applications and Data Criticality Analysis (A):** Assess the relative criticality of applications and data.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Backup | AWS Backup, RDS automated backups, S3 versioning | Azure Backup, Azure Site Recovery | Cloud Storage versioning, Persistent Disk snapshots |
| Disaster recovery | Multi-AZ, Multi-Region, Elastic Disaster Recovery | Availability Zones, Azure Site Recovery, Geo-Redundant Storage | Multi-region, Regional Persistent Disk |
| High availability | Auto Scaling, ELB, Multi-AZ RDS | Availability Sets/Zones, Load Balancer | Managed Instance Groups, Cloud Load Balancing |
| Infrastructure as code | CloudFormation, Terraform | ARM/Bicep, Terraform | Deployment Manager, Terraform |

#### Architect Checklist

- [ ] Automated backups are configured for all systems storing ePHI
- [ ] Backups are encrypted and stored in a separate region/zone
- [ ] Backup restoration is tested at least annually
- [ ] RPO (Recovery Point Objective) and RTO (Recovery Time Objective) are defined for ePHI systems
- [ ] Disaster recovery plan is documented and tested at least annually
- [ ] Multi-AZ or multi-region deployment is used for critical ePHI systems
- [ ] Infrastructure as code enables rapid environment reconstruction
- [ ] Emergency mode operations are documented (degraded-mode procedures)
- [ ] Application and data criticality analysis is completed and drives DR priorities

---

### 164.308(a)(8) - Evaluation (R)

**Purpose:** Perform periodic technical and non-technical evaluations to confirm compliance.

#### Architect Checklist

- [ ] Technical evaluations (vulnerability scans, penetration tests) are conducted at least annually
- [ ] Non-technical evaluations (policy reviews, process audits) are conducted at least annually
- [ ] Evaluations are triggered by environmental or operational changes
- [ ] Findings are documented with remediation plans and timelines

---

### 164.308(b)(1) - Business Associate Contracts and Other Arrangements (R)

**Purpose:** Ensure business associates provide satisfactory assurance of ePHI protection.

#### Architect Checklist

- [ ] BAA is executed with the cloud provider (AWS, Azure, GCP) before any ePHI is stored or processed
- [ ] Only BAA-eligible services are used for ePHI workloads
- [ ] BAAs are in place with all third-party services that access, store, or transmit ePHI
- [ ] BAA-eligible service list is reviewed when adopting new cloud services
- [ ] Subcontractor chains are documented (cloud provider subprocessors)

---

## Physical Safeguards (45 CFR 164.310)

### 164.310(a)(1) - Facility Access Controls (A)

**Purpose:** Limit physical access to electronic information systems and the facilities in which they are housed.

#### Implementation Specifications

**Contingency Operations (A):** Procedures for facility access during disaster recovery.
**Facility Security Plan (A):** Policies to safeguard the facility and equipment.
**Access Control and Validation Procedures (A):** Control and validate access based on role.
**Maintenance Records (A):** Document repairs and modifications to physical components.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Data center security | AWS compliance certifications (SOC 2, ISO 27001, HITRUST) | Azure compliance certifications | Google compliance certifications |
| Region selection | Region selection with data residency | Region selection with data residency | Region selection with data residency |
| Dedicated hosting | Dedicated Hosts, Outposts | Dedicated Hosts, Azure Stack | Sole-tenant Nodes |

#### Architect Checklist

- [ ] Cloud provider's physical security certifications (SOC 2 Type II, ISO 27001, HITRUST) are verified
- [ ] Data residency requirements are met through region selection
- [ ] On-premises components (if any) have documented facility access controls
- [ ] Dedicated/isolated compute is used if required by organizational policy

---

### 164.310(b) - Workstation Use (R)

**Purpose:** Specify proper use of and access to workstations that access ePHI.

#### Architect Checklist

- [ ] Workstation policies cover remote access to cloud-hosted ePHI
- [ ] Virtual desktop infrastructure (VDI) is considered for accessing ePHI (WorkSpaces, Azure Virtual Desktop, Chrome Remote Desktop)
- [ ] Screen lock and timeout policies are enforced on workstations accessing ePHI

---

### 164.310(c) - Workstation Security (R)

**Purpose:** Implement physical safeguards for workstations that access ePHI.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Virtual desktops | WorkSpaces | Azure Virtual Desktop | Chrome Remote Desktop, third-party |
| Endpoint management | Systems Manager | Intune, Endpoint Manager | BeyondCorp Enterprise, third-party |
| Zero trust access | Verified Access | Conditional Access | BeyondCorp Enterprise |

#### Architect Checklist

- [ ] Endpoint management (MDM/MAM) is deployed on devices accessing ePHI
- [ ] Zero trust access (Verified Access, Conditional Access, BeyondCorp) is used for ePHI applications
- [ ] Device compliance policies are enforced (encryption, OS version, anti-malware)

---

### 164.310(d)(1) - Device and Media Controls (R)

**Purpose:** Govern receipt and removal of hardware and electronic media containing ePHI.

#### Implementation Specifications

**Disposal (R):** Policies for final disposition of ePHI and hardware.
**Media Re-use (R):** Procedures for removing ePHI before media re-use.
**Accountability (A):** Maintain records of hardware and media movements.
**Data Backup and Storage (A):** Create retrievable copies before moving equipment.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Data destruction | AWS data handling practices (NIST 800-88) | Azure data destruction (NIST 800-88) | Google data destruction (NIST 800-88) |
| Encryption at rest | KMS, EBS encryption, S3 SSE | Key Vault, Azure Disk Encryption, Storage Encryption | Cloud KMS, default encryption, CMEK |
| Media lifecycle | S3 Lifecycle, EBS snapshot lifecycle | Blob lifecycle, Managed Disk lifecycle | Cloud Storage lifecycle, snapshot scheduling |
| Asset inventory | AWS Config, Systems Manager | Azure Resource Graph | Cloud Asset Inventory |

#### Architect Checklist

- [ ] All storage volumes containing ePHI are encrypted at rest using customer-managed keys
- [ ] Cloud provider's data destruction procedures align with NIST 800-88
- [ ] Snapshot and backup lifecycle policies automatically delete expired ePHI copies
- [ ] Asset inventory tracks all resources that store or process ePHI
- [ ] Decommissioning procedures ensure ePHI is wiped before releasing resources

---

## Technical Safeguards (45 CFR 164.312)

### 164.312(a)(1) - Access Control (R)

**Purpose:** Implement technical policies and procedures to allow only authorized persons to access ePHI.

#### Implementation Specifications

**Unique User Identification (R):** Assign a unique name/number for identifying and tracking user identity.
**Emergency Access Procedure (R):** Procedures for obtaining ePHI during emergencies.
**Automatic Logoff (A):** Electronic procedures that terminate sessions after inactivity.
**Encryption and Decryption (A):** Implement mechanism to encrypt and decrypt ePHI.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Unique user IDs | IAM Users, IAM Identity Center | Entra ID | Cloud Identity, Cloud IAM |
| MFA | IAM MFA, Identity Center MFA | Entra MFA | 2-Step Verification |
| SSO | IAM Identity Center | Entra ID SSO | Cloud Identity SSO |
| Session management | STS temporary credentials, session policies | Token lifetime, Conditional Access | Short-lived service account keys |
| Break-glass access | Root account (secured), break-glass IAM users | Emergency access accounts | Break-glass accounts |
| Encryption | KMS, CloudHSM | Key Vault, Managed HSM | Cloud KMS, Cloud HSM |

#### Architect Checklist

- [ ] Every user has a unique identifier -- no shared accounts for ePHI access
- [ ] MFA is required for all human access to systems containing ePHI
- [ ] Session timeout is enforced (15 minutes recommended)
- [ ] ePHI is encrypted at rest using AES-256 or equivalent
- [ ] Customer-managed encryption keys (CMK/CMEK) are used for ePHI
- [ ] Break-glass (emergency access) procedures are documented and tested
- [ ] Break-glass account usage triggers immediate alerts
- [ ] Temporary/short-lived credentials are used instead of long-lived keys
- [ ] Federated SSO centralizes authentication for all ePHI systems

---

### 164.312(b) - Audit Controls (R)

**Purpose:** Implement mechanisms to record and examine access and activity in systems containing ePHI.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| API audit logging | CloudTrail | Activity Log | Cloud Audit Logs |
| Data access logging | S3 access logs, RDS audit logs, CloudTrail data events | Storage analytics, SQL auditing | Cloud Storage audit logs, BigQuery audit logs |
| Centralized logging | CloudWatch Logs, S3, OpenSearch | Log Analytics, Monitor | Cloud Logging, BigQuery |
| SIEM | Security Hub, Detective, third-party | Sentinel | Chronicle |
| Log retention | S3 Glacier, CloudWatch retention | Log Analytics retention, Storage tiers | Cloud Logging retention, Cloud Storage |

#### Architect Checklist

- [ ] CloudTrail / Activity Log / Audit Logs capture all management and data access events for ePHI systems
- [ ] Data access logging is enabled (S3 access logs, database audit logs, storage analytics)
- [ ] Logs are centralized in a dedicated, access-restricted logging account/project
- [ ] Log retention meets organizational and regulatory requirements (minimum 6 years recommended for HIPAA)
- [ ] Logs are immutable (write-once, no delete permissions for operational accounts)
- [ ] SIEM is deployed for real-time monitoring and alerting
- [ ] Audit log review procedures are documented and followed
- [ ] Log access is restricted to authorized security personnel

---

### 164.312(c)(1) - Integrity Controls (A)

**Purpose:** Implement policies and procedures to protect ePHI from improper alteration or destruction.

#### Implementation Specifications

**Mechanism to Authenticate Electronic Protected Health Information (A):** Corroborate that ePHI has not been altered or destroyed improperly.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Data integrity verification | S3 checksums, S3 Object Lock | Immutable blob storage | Cloud Storage retention policies, Object versioning |
| Database integrity | RDS Multi-AZ, DynamoDB checksums | SQL Database integrity checks | Cloud SQL, AlloyDB |
| Backup integrity | AWS Backup vault lock | Azure Backup immutability | Backup retention locks |
| File integrity monitoring | CloudWatch agent + FIM, Inspector | Defender for Servers FIM | Security Command Center |
| Version control | S3 versioning, DynamoDB point-in-time recovery | Blob versioning, Cosmos DB PITR | Cloud Storage versioning, Firestore PITR |

#### Architect Checklist

- [ ] Object versioning is enabled on all storage containing ePHI
- [ ] Object Lock / Immutable storage is used for ePHI that must not be modified
- [ ] Database integrity checks (checksums, consistency validation) are enabled
- [ ] Point-in-time recovery is enabled for databases containing ePHI
- [ ] File integrity monitoring detects unauthorized changes to ePHI application files
- [ ] Backup vault lock / immutability prevents deletion of ePHI backups
- [ ] Digital signatures or checksums verify ePHI integrity during processing

---

### 164.312(d) - Person or Entity Authentication (R)

**Purpose:** Implement procedures to verify that a person or entity seeking access to ePHI is the one claimed.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Authentication | IAM, Cognito | Entra ID, Azure AD B2C | Identity Platform, Firebase Auth |
| MFA methods | Virtual MFA, hardware tokens, FIDO2 | Authenticator app, FIDO2, phone | Google Authenticator, Titan keys, FIDO2 |
| Certificate-based auth | IAM SSL/TLS client certs, Private CA | Entra certificate-based auth | mTLS, Certificate Authority Service |
| API authentication | IAM Signature V4, Cognito tokens | Entra tokens, API Management | OAuth 2.0, API keys, IAM |

#### Architect Checklist

- [ ] Multi-factor authentication is enforced for all ePHI access (something you know + something you have/are)
- [ ] Phishing-resistant MFA (FIDO2/WebAuthn) is preferred over SMS-based MFA
- [ ] Service-to-service authentication uses mutual TLS or signed tokens (not shared secrets)
- [ ] Patient-facing portals use strong authentication (MFA for patient access to ePHI)
- [ ] Authentication mechanisms are centralized (SSO/federation)

---

### 164.312(e)(1) - Transmission Security (R)

**Purpose:** Implement technical security measures to guard against unauthorized access to ePHI during electronic transmission.

#### Implementation Specifications

**Integrity Controls (A):** Ensure ePHI is not improperly modified during transmission.
**Encryption (A):** Encrypt ePHI whenever transmitted over electronic networks.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| TLS enforcement | ALB, CloudFront, API Gateway (TLS 1.2+) | Application Gateway, Front Door (TLS 1.2+) | Cloud Load Balancer (TLS 1.2+) |
| Private connectivity | PrivateLink, Direct Connect, VPC Peering | Private Link, ExpressRoute, VNet Peering | Private Service Connect, Interconnect |
| VPN | Site-to-Site VPN, Client VPN | VPN Gateway, Point-to-Site VPN | Cloud VPN |
| Service mesh encryption | App Mesh (mTLS), EKS + Istio | AKS + Istio | GKE + Istio / Anthos Service Mesh |
| Email encryption | SES (TLS), WorkMail | Exchange Online (TLS, S/MIME) | Workspace (TLS, S/MIME) |

#### Architect Checklist

- [ ] TLS 1.2 or higher is enforced on all ePHI transmission channels
- [ ] Internal service-to-service communication uses mTLS within the ePHI environment
- [ ] Private connectivity (PrivateLink, Private Link, Private Service Connect) is used instead of public internet where possible
- [ ] VPN encryption is used for administrative access to ePHI environments
- [ ] Email containing ePHI is encrypted (TLS at minimum, end-to-end encryption preferred)
- [ ] HSTS is enabled on all web applications handling ePHI
- [ ] API endpoints enforce HTTPS-only (HTTP is rejected, not redirected)
- [ ] ePHI transmitted to external parties uses end-to-end encryption
- [ ] Weak cipher suites and protocols (SSL 3.0, TLS 1.0, TLS 1.1) are disabled

---

## BAA-Eligible Services Reference

### AWS HIPAA Eligible Services

AWS maintains a list of HIPAA-eligible services. Before using any AWS service for ePHI:

- [ ] Verify the service is on the current HIPAA Eligible Services list
- [ ] Confirm BAA is in place via AWS Artifact
- [ ] Review the service-specific security configuration guidance

### Azure HIPAA/HITRUST Services

Azure offers HITRUST CSF compliance for many services:

- [ ] Verify the service is covered under the Microsoft BAA
- [ ] Review Azure compliance documentation on the Service Trust Portal
- [ ] Use Azure Policy HIPAA/HITRUST initiative for automated compliance checking

### GCP HIPAA Covered Services

GCP maintains a list of HIPAA-covered services:

- [ ] Verify the service is on the current GCP HIPAA covered services list
- [ ] Confirm BAA is in place via GCP console
- [ ] Review the GCP HIPAA implementation guide

---

## Key Differences from Other Frameworks

- HIPAA does not prescribe specific technologies -- it requires "reasonable and appropriate" safeguards
- Addressable specifications still require action (implement, implement alternative, or document rationale)
- Breach Notification Rule (45 CFR 164 Subpart D) requires notification within 60 days of discovery
- Penalties range from $100 to $50,000 per violation, up to $1.5 million per year per violation category
- State laws may impose stricter requirements (e.g., CCPA, state breach notification laws)
