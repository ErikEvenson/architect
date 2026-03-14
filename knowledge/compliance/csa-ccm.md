# CSA CCM v4 — Cloud Security Alliance Cloud Controls Matrix

Reference: Cloud Controls Matrix (CCM) v4.0
Published by: Cloud Security Alliance (CSA)
Scope: Cloud service providers and cloud service customers. The CCM provides a controls framework specifically designed for cloud computing environments and maps to other standards (ISO 27001, NIST SP 800-53, PCI DSS, GDPR, etc.).

---

## Why This Matters

The CSA CCM is the de facto cloud security controls framework. Unlike general-purpose standards adapted for cloud (ISO 27001, NIST), the CCM was built from the ground up for cloud environments. It explicitly addresses the shared responsibility model, mapping each control to whether it applies to the cloud service provider (CSP), the cloud service customer (CSC), or both.

CSA STAR (Security, Trust, Assurance, and Risk) certification is based on the CCM and is increasingly requested in cloud procurement. Cloud architects who design against CCM controls can demonstrate security posture to customers through a recognized, cloud-specific framework.

The CCM v4 organizes 197 controls into 17 domains. Each control has a unique identifier (e.g., IAM-01) that can be referenced in Architecture Decision Records, risk assessments, and compliance documentation.

---

## Common Decisions (ADR Triggers)

The following architectural decisions should be captured as Architecture Decision Records when CSA CCM compliance is a goal:

- **Shared responsibility mapping** — Document which CCM controls are the CSP's responsibility, which are the CSC's, and which are shared, for each cloud service in use.
- **API security architecture** — Authentication, authorization, rate limiting, input validation, and versioning strategy for all cloud APIs.
- **Multi-tenancy isolation model** — How tenant data and processing are isolated in shared infrastructure.
- **Key management architecture** — Who generates, stores, rotates, and can access encryption keys (CSP-managed, CSC-managed, or external KMS).
- **Logging and monitoring strategy** — What events are logged, where logs are stored, retention periods, and who has access.
- **Incident response integration** — How CSP security events are integrated into the organization's incident response process.
- **Business continuity and DR architecture** — RPO/RTO targets, failover regions, data replication strategy.
- **Supply chain security model** — How third-party dependencies (libraries, container images, SaaS integrations) are assessed and monitored.
- **Network security architecture** — Microsegmentation, zero-trust network access, and east-west traffic inspection strategy.
- **Identity federation model** — How identities from the organization's IdP are federated to cloud providers and how authorization is managed.
- **Data classification and handling** — How data is classified, and what controls apply at each classification level across cloud services.
- **Vulnerability management program** — Scanning coverage, remediation SLAs, and exception handling across cloud workloads.

---

## Checklist

### AIS — Application & Interface Security

#### AIS-01: Application and Interface Security Policy

- [ ] Define an application security policy covering cloud-hosted applications and APIs
- [ ] Include security requirements for application design, development, deployment, and operation
- [ ] Align application security policy with the organization's overall information security policy

#### AIS-02: Application Security Baseline

- [ ] Establish security baselines for all cloud-hosted applications
- [ ] Include OWASP Top 10 mitigations in the baseline
- [ ] Implement automated compliance checking against the baseline

#### AIS-03: Application Security Metrics

- [ ] Define and track application security metrics (vulnerability density, mean time to remediate, scan coverage)
- [ ] Report application security metrics to management at planned intervals

#### AIS-04: Secure Application Design and Development

- [ ] Implement a secure SDLC for cloud-hosted applications
- [ ] Conduct threat modeling for new applications and major changes
- [ ] Integrate SAST, DAST, and SCA into CI/CD pipelines
- [ ] Implement secure API design (authentication, authorization, input validation, output encoding, rate limiting)

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| API gateway security | API Gateway (API keys, usage plans, Lambda authorizers, WAF integration, request validation) | Azure API Management (OAuth, JWT validation, rate limiting, IP filtering) | Apigee API Management (OAuth, API keys, rate limiting, threat protection policies) |
| API authentication | Cognito (OAuth 2.0/OIDC), IAM for service-to-service | Entra ID (OAuth 2.0/OIDC), Managed Identities | Identity Platform (OAuth 2.0/OIDC), Service Accounts, Workload Identity |
| WAF protection | AWS WAF (managed rule groups, custom rules, rate-based rules, Bot Control) | Azure WAF (OWASP rulesets, custom rules, bot protection) | Cloud Armor (preconfigured WAF rules, custom rules, bot management, adaptive protection) |
| Input validation / injection prevention | WAF SQL injection rules, CodeGuru Reviewer | WAF OWASP rulesets, GitHub Advanced Security | Cloud Armor OWASP rules, Web Security Scanner |

#### AIS-05: Automated Application Security Testing

- [ ] Automate security testing in the CI/CD pipeline
- [ ] Fail builds that contain critical or high-severity vulnerabilities (unless explicitly accepted via risk exception)
- [ ] Scan container images before deployment

#### AIS-06: Automated Secure Application Deployment

- [ ] Implement infrastructure as code with security controls baked in
- [ ] Use immutable deployment patterns (blue/green, canary) where feasible
- [ ] Enforce deployment approvals and audit trails

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Secure deployment | CodePipeline with approval stages, CodeDeploy (blue/green, rolling) | Azure DevOps Pipelines with gates, App Service deployment slots | Cloud Deploy with promotion approvals, Cloud Run revisions |
| Container deployment security | ECS/EKS with ECR image scanning, Signer for image signing | AKS with ACR, Notation for image signing | GKE with Binary Authorization, Artifact Analysis |

#### AIS-07: Application Vulnerability Remediation

- [ ] Define remediation SLAs by severity (e.g., Critical: 24h, High: 7d, Medium: 30d, Low: 90d)
- [ ] Track remediation progress and escalate overdue items
- [ ] Re-scan after remediation to verify fixes

### AAC — Audit & Assurance

#### AAC-01: Audit and Assurance Policy

- [ ] Define an audit policy covering cloud environments
- [ ] Include requirements for internal and external audits
- [ ] Define audit scope, frequency, and reporting requirements

#### AAC-02: Independent Assessments

- [ ] Conduct independent assessments of cloud security controls at planned intervals
- [ ] Verify cloud provider compliance certifications (SOC 2 Type II, ISO 27001, CSA STAR)
- [ ] Review cloud provider audit reports and assess findings relevant to the organization

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Compliance reports | AWS Artifact (SOC 1/2/3, ISO 27001, ISO 27017, ISO 27018, PCI DSS, CSA STAR) | Service Trust Portal (SOC 1/2/3, ISO 27001, ISO 27017, ISO 27018, PCI DSS, CSA STAR) | Compliance Reports Manager (SOC 1/2/3, ISO 27001, ISO 27017, ISO 27018, PCI DSS, CSA STAR) |

#### AAC-03: Risk-Based Planning Assessment

- [ ] Base audit planning on risk assessment results
- [ ] Prioritize audit areas based on risk level and business impact
- [ ] Include cloud-specific risks in audit planning (misconfiguration, data exposure, access control gaps)

#### AAC-04: Audit and Assurance Requirement Compliance

- [ ] Map audit requirements to specific CCM controls
- [ ] Track audit findings and corrective actions to closure
- [ ] Share relevant audit results with cloud service customers (for CSPs)

#### AAC-05: Audit Management Process

- [ ] Manage the audit lifecycle (planning, execution, reporting, follow-up)
- [ ] Maintain independence of audit function from operations
- [ ] Protect audit evidence and reports

#### AAC-06: Internal Audit Planning

- [ ] Develop an internal audit plan covering cloud environments
- [ ] Ensure auditors have access to necessary cloud management tools and logs
- [ ] Use cloud-native compliance tools to support continuous auditing

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Continuous compliance monitoring | Security Hub compliance standards, AWS Audit Manager | Defender for Cloud regulatory compliance, Azure Policy compliance | Security Command Center compliance reports, Security Health Analytics |
| Audit evidence collection | AWS Audit Manager (automated evidence collection) | Microsoft Purview Compliance Manager | Assured Workloads compliance monitoring |

### BCR — Business Continuity Management & Operational Resilience

#### BCR-01: Business Continuity Management Policy

- [ ] Define a business continuity policy covering cloud-hosted workloads
- [ ] Include RPO/RTO targets for each workload tier
- [ ] Define roles and responsibilities for business continuity management

#### BCR-02: Risk Assessment

- [ ] Conduct business impact analysis (BIA) for cloud-hosted workloads
- [ ] Identify single points of failure in cloud architecture
- [ ] Assess cloud provider availability SLAs against business requirements

#### BCR-03: Business Continuity Strategy

- [ ] Design cloud architecture to meet RPO/RTO targets (multi-AZ, multi-region, multi-cloud as appropriate)
- [ ] Document recovery procedures for each critical workload
- [ ] Implement automated failover where RPO/RTO targets require it

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Multi-AZ resilience | Multi-AZ RDS, S3 cross-AZ replication (automatic), ELB cross-AZ | Availability Zones for VMs/databases, Zone-redundant storage (ZRS) | Regional managed instance groups, Cloud SQL HA (regional), Cloud Spanner |
| Multi-region DR | S3 Cross-Region Replication, Aurora Global Database, DynamoDB Global Tables, Route 53 failover | Azure Site Recovery, Cosmos DB multi-region writes, Traffic Manager | Cloud SQL cross-region replicas, Spanner multi-region, Cloud DNS failover |
| Backup | AWS Backup (centralized), EBS snapshots, RDS automated backups | Azure Backup, Recovery Services Vault | Cloud Storage backups, Persistent Disk snapshots, Cloud SQL backups |

#### BCR-04: Business Continuity Planning

- [ ] Develop recovery plans for all critical cloud workloads
- [ ] Include communication plans for stakeholders during disruption
- [ ] Address data integrity verification after recovery

#### BCR-05: Documentation

- [ ] Document all business continuity plans, procedures, and contact information
- [ ] Store documentation in a location accessible during outage (not solely in the cloud environment being recovered)

#### BCR-06: Business Continuity Exercises

- [ ] Test business continuity plans at least annually
- [ ] Include cloud-specific failure scenarios (region outage, service degradation, API throttling)
- [ ] Document test results and update plans based on findings
- [ ] Conduct chaos engineering exercises for critical workloads

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Chaos engineering | AWS Fault Injection Service (FIS) | Azure Chaos Studio | Fault injection capabilities via Litmus/Gremlin on GKE |

#### BCR-07: Communication

- [ ] Define communication procedures during business continuity events
- [ ] Include cloud provider communication channels (status pages, support tickets, TAM escalation)

#### BCR-08: Backup

- [ ] Implement automated backup for all critical data and configurations
- [ ] Store backups in a separate region or account from the primary workload
- [ ] Test backup restoration regularly
- [ ] Encrypt backups at rest and in transit
- [ ] Define backup retention periods aligned with business and regulatory requirements

#### BCR-09: Disaster Recovery Plan

- [ ] Develop DR plans for cloud workloads based on BIA results
- [ ] Implement automated DR runbooks where possible
- [ ] Test DR procedures at least annually with documented results

#### BCR-11: Equipment Redundancy

- [ ] Design for infrastructure redundancy (multiple availability zones, load balancing)
- [ ] Eliminate single points of failure in networking, compute, and storage layers
- [ ] Implement health checks and automated replacement of unhealthy instances

### CCC — Change Control & Configuration Management

#### CCC-01: Change Management Policy

- [ ] Define a change management policy covering cloud infrastructure and applications
- [ ] Classify changes by risk level (standard, normal, emergency)
- [ ] Define approval requirements for each change class

#### CCC-02: Quality Testing

- [ ] Implement quality testing for all changes before production deployment
- [ ] Include security testing in the change testing process
- [ ] Automate testing in CI/CD pipelines

#### CCC-03: Change Management Technology

- [ ] Use infrastructure as code (IaC) for all cloud resource changes
- [ ] Implement version control for all configuration and infrastructure code
- [ ] Use deployment pipelines with automated testing and approval gates

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| IaC | CloudFormation, CDK, Terraform | ARM Templates, Bicep, Terraform | Deployment Manager, Terraform |
| Change deployment | CodePipeline, CodeDeploy | Azure DevOps, GitHub Actions | Cloud Build, Cloud Deploy |
| Configuration drift detection | AWS Config, CloudFormation drift detection | Azure Policy compliance, Azure Automanage | Security Command Center, Cloud Asset Inventory |

#### CCC-04: Unauthorized Change Protection

- [ ] Implement controls to detect and prevent unauthorized changes
- [ ] Alert on configuration changes that bypass the approved change process
- [ ] Implement guardrails to prevent non-compliant resource creation

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Preventive guardrails | SCPs (Organizations), IAM permission boundaries, Control Tower guardrails | Azure Policy (deny effect), Management Group policies | Organization policies (constraints), IAM deny policies |
| Detective guardrails | AWS Config rules, Security Hub findings | Azure Policy compliance, Defender for Cloud | Organization Policy compliance, Security Health Analytics |

#### CCC-05: Change Agreements

- [ ] Include change notification requirements in cloud provider agreements
- [ ] Monitor cloud provider change notifications (API changes, deprecations, feature changes)
- [ ] Assess impact of cloud provider changes on the organization

#### CCC-06: Change Management Baseline

- [ ] Maintain configuration baselines for all cloud environments
- [ ] Detect and report deviation from baselines
- [ ] Remediate unauthorized deviations

#### CCC-07: Detection of Baseline Deviation

- [ ] Implement continuous monitoring for configuration baseline deviations
- [ ] Automate remediation of common deviations where safe to do so
- [ ] Escalate deviations that cannot be auto-remediated

#### CCC-09: Change Restoration

- [ ] Implement rollback capabilities for cloud infrastructure changes
- [ ] Test rollback procedures as part of change management
- [ ] Document rollback procedures in change records

### CEK — Cryptography, Encryption & Key Management

#### CEK-01: Encryption and Key Management Policy

- [ ] Define a cryptographic policy covering algorithms, key lengths, and key management
- [ ] Specify approved algorithms (AES-256 for symmetric, RSA-2048+ or ECDSA P-256+ for asymmetric)
- [ ] Define key lifecycle management (generation, distribution, storage, rotation, revocation, destruction)

#### CEK-02: CEK Roles and Responsibilities

- [ ] Assign roles and responsibilities for cryptographic key management
- [ ] Separate key management duties from data access duties where feasible

#### CEK-03: Data Encryption

- [ ] Encrypt data at rest for all cloud storage services
- [ ] Encrypt data in transit using TLS 1.2 or higher
- [ ] Evaluate encryption in use (confidential computing) for sensitive workloads

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Encryption at rest | Default encryption for S3, EBS, RDS; CMEK via KMS | Azure Storage Service Encryption (SSE), Azure Disk Encryption, TDE; CMEK via Key Vault | Default encryption for Cloud Storage, Persistent Disk, Cloud SQL; CMEK via Cloud KMS |
| Encryption in transit | TLS enforcement on ALB/NLB, S3 bucket policies requiring HTTPS, RDS force SSL | TLS enforcement on App Gateway, Storage account secure transfer required | TLS enforcement on load balancers, Cloud Storage HTTPS-only |
| Encryption in use | Nitro Enclaves, Clean Rooms | Confidential Computing (DCsv2/3, confidential containers, Always Encrypted with enclaves) | Confidential VMs, Confidential GKE |

#### CEK-04: Encryption Algorithm

- [ ] Use only approved cryptographic algorithms and key lengths
- [ ] Plan for post-quantum cryptography migration where applicable
- [ ] Prohibit use of deprecated algorithms (DES, 3DES, RC4, MD5, SHA-1 for signing)

#### CEK-05: Key Generation

- [ ] Generate cryptographic keys using approved random number generators
- [ ] Generate keys within hardware security modules (HSMs) for high-sensitivity use cases
- [ ] Document key generation procedures

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| HSM key generation | CloudHSM (FIPS 140-2 Level 3), KMS (FIPS 140-2 Level 2 or 3) | Managed HSM (FIPS 140-2 Level 3), Key Vault (FIPS 140-2 Level 2) | Cloud HSM (FIPS 140-2 Level 3), Cloud KMS (FIPS 140-2 Level 1+) |

#### CEK-06: Key Rotation

- [ ] Implement automated key rotation for encryption keys
- [ ] Define rotation periods (e.g., annually for master keys, per-use for data encryption keys)
- [ ] Ensure key rotation does not cause data unavailability

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Automated key rotation | KMS automatic key rotation (annual), custom rotation via Lambda | Key Vault key auto-rotation, rotation policies | Cloud KMS automatic key rotation (configurable period) |

#### CEK-07: Key Revocation

- [ ] Define procedures for key revocation (compromised keys, personnel changes)
- [ ] Implement key revocation that takes effect promptly across all systems using the key
- [ ] Maintain revocation records

#### CEK-08: Key Destruction

- [ ] Define procedures for key destruction at end of lifecycle
- [ ] Implement cryptographic key destruction that prevents key recovery
- [ ] Use scheduled destruction with a waiting period to prevent accidental data loss

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Key destruction | KMS key deletion with 7-30 day waiting period | Key Vault soft-delete (7-90 day retention) and purge protection | Cloud KMS key version destruction with 24-hour waiting period |

#### CEK-09: Encryption and Key Management Audit Logging

- [ ] Log all key management operations (creation, rotation, access, deletion)
- [ ] Log all encryption/decryption operations for audit-sensitive data
- [ ] Alert on anomalous key usage patterns

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Key operation logging | CloudTrail logs for KMS API calls | Key Vault diagnostic logs, Azure Monitor | Cloud KMS audit logs in Cloud Audit Logs |

#### CEK-14: Certificate and Key Management

- [ ] Implement automated certificate lifecycle management (issuance, renewal, revocation)
- [ ] Monitor certificate expiration and alert before expiry
- [ ] Use managed certificate services where possible

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Certificate management | ACM (auto-renewal for AWS services), ACM Private CA | Key Vault certificates (auto-renewal), App Service Managed Certificates | Certificate Manager (auto-renewal), Certificate Authority Service |

### DSP — Data Security & Privacy Lifecycle Management

#### DSP-01: Security and Privacy Policy and Procedures

- [ ] Define data security and privacy policies covering cloud-hosted data
- [ ] Address the data lifecycle: creation, storage, use, sharing, archival, and destruction
- [ ] Align with applicable privacy regulations (GDPR, CCPA, etc.)

#### DSP-02: Secure Disposal

- [ ] Implement data disposal procedures for cloud environments
- [ ] Verify cloud provider data disposal mechanisms (cryptographic erasure, physical destruction)
- [ ] Implement automated data retention and disposal via lifecycle policies

#### DSP-03: Data Inventory

- [ ] Maintain an inventory of data stored and processed in cloud environments
- [ ] Classify data by sensitivity level (public, internal, confidential, restricted)
- [ ] Map data flows between cloud services, regions, and third parties

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Data discovery and classification | Macie (S3 data discovery and classification), Glue Data Catalog | Microsoft Purview Data Catalog, Purview Information Protection | Data Catalog, Dataplex, Cloud DLP / Sensitive Data Protection |
| Data flow mapping | VPC Flow Logs, CloudTrail data events | NSG flow logs, Purview Data Lineage | VPC Flow Logs, Data Lineage (Dataplex) |

#### DSP-04: Data Classification

- [ ] Implement a data classification scheme with at least 3-4 levels
- [ ] Tag cloud resources with classification labels
- [ ] Automate data classification where possible using content inspection

#### DSP-05: Data Flow Documentation

- [ ] Document all data flows into, within, and out of cloud environments
- [ ] Include data flows to third parties and sub-processors
- [ ] Update data flow documentation when architecture changes

#### DSP-07: Data Protection by Design and Default

- [ ] Apply data minimization principles to cloud workloads
- [ ] Implement privacy-enhancing technologies (pseudonymization, anonymization, differential privacy)
- [ ] Default to the most restrictive data access settings

#### DSP-08: Data Privacy by Design and Default

- [ ] Integrate privacy requirements into the system design process
- [ ] Conduct privacy impact assessments for new cloud workloads processing personal data
- [ ] Implement consent management and purpose limitation controls

#### DSP-10: Sensitive Data Transfer

- [ ] Encrypt sensitive data in transit
- [ ] Implement access controls for data transfer mechanisms (APIs, file transfers, database exports)
- [ ] Log all sensitive data transfers

#### DSP-11: Personal Data Access, Reversal, Rectification and Deletion

- [ ] Implement mechanisms for data subjects to access their personal data
- [ ] Support data portability in machine-readable formats
- [ ] Implement data correction and deletion mechanisms across all cloud data stores
- [ ] Verify deletion completeness (primary stores, replicas, backups, caches)

#### DSP-14: Data Retention and Deletion

- [ ] Define data retention periods based on legal, regulatory, and business requirements
- [ ] Implement automated retention enforcement through lifecycle policies
- [ ] Delete data when the retention period expires

#### DSP-16: Data Geographical Restrictions

- [ ] Implement controls to enforce data residency requirements
- [ ] Use cloud provider region restriction capabilities (organization policies, SCPs)
- [ ] Monitor for data replication or transfer outside approved regions

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Region restriction | SCPs to deny non-approved regions, S3 bucket policies | Azure Policy to restrict locations | Organization Policy `gcp.resourceLocations` constraint |
| Data residency | AWS data residency commitments by region | EU Data Boundary, data residency commitments | Data Residency commitments, Assured Workloads |

#### DSP-17: Non-Production Data

- [ ] Prohibit use of production personal data in non-production environments
- [ ] Implement data masking or synthetic data generation for non-production use
- [ ] Apply equivalent security controls if production data must be used in non-production (with justification)

### GRC — Governance, Risk Management and Compliance

#### GRC-01: Governance Program

- [ ] Establish an information security governance program covering cloud environments
- [ ] Define governance structure, roles, and reporting lines
- [ ] Include cloud security in board-level reporting

#### GRC-02: Risk Management Program

- [ ] Implement a risk management program that includes cloud-specific risks
- [ ] Conduct risk assessments at planned intervals and when significant changes occur
- [ ] Maintain a risk register with cloud-specific risks (vendor lock-in, data exposure, misconfiguration, service outage)
- [ ] Define risk acceptance criteria and escalation procedures

#### GRC-03: Organizational Policy

- [ ] Develop and maintain information security policies covering cloud usage
- [ ] Review policies at planned intervals (at least annually)
- [ ] Communicate policies to all relevant personnel

#### GRC-05: Information Security Program

- [ ] Implement an information security program that covers cloud environments
- [ ] Define security metrics and KPIs for cloud workloads
- [ ] Report security program status to management

#### GRC-06: Governance Responsibility Model

- [ ] Document the shared responsibility model for each cloud provider and service
- [ ] Map responsibilities to organizational roles
- [ ] Verify that no responsibilities fall through gaps between CSP and CSC

#### GRC-08: Special Interest Groups

- [ ] Participate in relevant cloud security communities and information sharing groups (CSA, ISAC)
- [ ] Monitor cloud security threat intelligence from industry groups

### HRS — Human Resources

#### HRS-01: Background Screening Policy

- [ ] Define background screening requirements for personnel with cloud access
- [ ] Scale screening depth to privilege level and data sensitivity
- [ ] Include cloud administrators and DevOps engineers in enhanced screening

#### HRS-02: Acceptable Use of Technology Policy

- [ ] Define acceptable use policies for cloud services and resources
- [ ] Include personal use restrictions, approved service lists, and data handling rules
- [ ] Cover BYOD policies for devices accessing cloud environments

#### HRS-03: Clean Desk Policy

- [ ] Implement clean desk policies for workstations accessing cloud management tools
- [ ] Include clean screen requirements (screen lock, session timeout)

#### HRS-04: Return of Assets

- [ ] Ensure all cloud access credentials and tokens are revoked upon termination
- [ ] Revoke VPN and remote access immediately upon termination
- [ ] Remove terminated users from all cloud IAM systems

#### HRS-06: Security Awareness Training

- [ ] Deliver cloud security awareness training to all personnel
- [ ] Include phishing awareness, credential security, and cloud-specific risks
- [ ] Conduct role-specific training for cloud administrators and developers
- [ ] Test training effectiveness through assessments and simulated attacks

#### HRS-09: Personnel Roles and Responsibilities

- [ ] Define and document security responsibilities for all roles interacting with cloud environments
- [ ] Include cloud security responsibilities in job descriptions

### IAM — Identity & Access Management

#### IAM-01: Identity and Access Management Policy

- [ ] Define an IAM policy covering cloud environments
- [ ] Include authentication, authorization, and account management requirements
- [ ] Address service accounts, API keys, and machine identities

#### IAM-02: Strong Password Policy

- [ ] Enforce strong password requirements (minimum length, complexity, rotation)
- [ ] Implement account lockout after failed authentication attempts
- [ ] Prohibit password reuse

#### IAM-03: Identity Inventory

- [ ] Maintain an inventory of all identities (human and non-human) with cloud access
- [ ] Include service accounts, API keys, OAuth tokens, and machine identities
- [ ] Review identity inventory regularly and remove stale entries

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Identity inventory | IAM Credential Report, IAM Access Analyzer, Organizations | Entra ID user/app inventory, Access Reviews | IAM Policy Analyzer, Policy Intelligence, Cloud Identity reports |
| Stale identity detection | IAM Access Analyzer (unused access), Credential Report (last used) | Entra ID Access Reviews, sign-in logs analysis | IAM Recommender (excess permissions), Policy Analyzer |

#### IAM-04: Separation of Duties

- [ ] Enforce separation of duties through cloud IAM roles
- [ ] Prevent single individuals from having end-to-end control over critical processes
- [ ] Implement multi-person approval for high-risk operations

#### IAM-05: Least Privilege

- [ ] Apply least privilege for all cloud IAM assignments
- [ ] Regularly review and right-size permissions
- [ ] Use cloud-native tools to identify and remove excessive permissions

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Permission right-sizing | IAM Access Analyzer (policy generation from CloudTrail), IAM Access Advisor | Entra ID Access Reviews, Permissions Management (CIEM) | IAM Recommender, Policy Analyzer, Permissions Insights |

#### IAM-06: User Access Provisioning

- [ ] Implement formal user access provisioning and deprovisioning processes
- [ ] Automate provisioning through IdP integration (SCIM, SAML JIT)
- [ ] Implement approval workflows for access requests

#### IAM-07: User Access Review

- [ ] Conduct periodic access reviews for all cloud environments (at least quarterly for privileged access)
- [ ] Remove or adjust access that is no longer appropriate
- [ ] Document access review results

#### IAM-08: User Access Revocation

- [ ] Revoke access promptly upon termination or role change
- [ ] Automate access revocation through IdP lifecycle management
- [ ] Verify revocation completeness across all cloud accounts and services

#### IAM-09: Multi-Factor Authentication

- [ ] Require MFA for all human access to cloud management consoles and APIs
- [ ] Require MFA for all privileged access
- [ ] Enforce phishing-resistant MFA (FIDO2, hardware tokens) for administrative access

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| MFA enforcement | IAM MFA (virtual, hardware, FIDO2), SCPs to require MFA | Entra ID Conditional Access MFA, security defaults | Cloud Identity MFA enforcement, Context-aware access |

#### IAM-10: Privileged Access Management

- [ ] Implement privileged access management (PAM) for cloud environments
- [ ] Use just-in-time access for privileged roles
- [ ] Monitor and record privileged access sessions
- [ ] Require approval workflows for privilege elevation

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| PAM | IAM roles with session policies, SSO with temporary credentials, Systems Manager Session Manager | Entra ID PIM (just-in-time, approval workflows, access reviews) | Privileged Access Manager (just-in-time, approval-based, time-bound) |

#### IAM-12: User ID Management

- [ ] Enforce unique user IDs (no shared accounts)
- [ ] Implement naming conventions for user IDs and service accounts
- [ ] Prohibit use of root/global admin accounts for day-to-day operations

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Root account protection | Root account MFA, SCPs to restrict root usage, alarm on root login | Global Admin PIM, break-glass accounts with monitoring | Super admin account protection, Organization policy constraints |

#### IAM-13: Identity Federation

- [ ] Implement identity federation with the organization's IdP for cloud access
- [ ] Use standards-based federation (SAML 2.0, OIDC)
- [ ] Minimize use of cloud-native IAM users in favor of federated identities

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Federation | IAM Identity Center (SAML/SCIM), IAM SAML/OIDC providers | Entra ID (SAML/OIDC/WS-Fed), B2B for external identities | Workforce Identity Federation (SAML/OIDC), Cloud Identity |

#### IAM-14: Workload Identity Management

- [ ] Use managed identities for workload-to-service authentication (no long-lived credentials)
- [ ] Implement workload identity federation for cross-platform authentication
- [ ] Rotate any long-lived credentials that cannot be replaced with managed identities

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Managed identities | IAM Roles for EC2/ECS/Lambda (instance profiles, task roles, execution roles) | Managed Identities (system-assigned, user-assigned) | Service accounts with Workload Identity (GKE), attached service accounts |
| Cross-platform identity | IAM OIDC providers for GitHub Actions/GitLab CI | Workload Identity Federation (GitHub, AWS, GCP) | Workload Identity Federation (AWS, Azure, GitHub, GitLab) |

### IVS — Infrastructure & Virtualization Security

#### IVS-01: Infrastructure and Virtualization Security Policy

- [ ] Define an infrastructure security policy covering cloud environments
- [ ] Address network security, compute security, and storage security

#### IVS-02: Capacity and Resource Planning

- [ ] Plan capacity for security workloads (logging, monitoring, scanning)
- [ ] Implement resource quotas and limits to prevent resource exhaustion
- [ ] Monitor resource utilization and set alerts for thresholds

#### IVS-03: Network Security

- [ ] Implement network segmentation using cloud-native constructs (VPCs, subnets, security groups)
- [ ] Apply zero-trust network principles (verify explicitly, least privilege access, assume breach)
- [ ] Restrict network access to management interfaces
- [ ] Implement private endpoints for cloud service access where available

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Network segmentation | VPC, subnets, security groups, NACLs, Transit Gateway | VNet, subnets, NSGs, ASGs, Virtual WAN | VPC, subnets, firewall rules, Shared VPC |
| Private service access | VPC Endpoints (gateway and interface), PrivateLink | Private Endpoints, Service Endpoints | Private Service Connect, Private Google Access |
| Network inspection | Network Firewall, Traffic Mirroring, GuardDuty | Azure Firewall, Network Watcher, Defender for Cloud | Cloud NGFW, Packet Mirroring, Cloud IDS |

#### IVS-04: OS Hardening and Base Controls

- [ ] Harden operating system configurations using industry benchmarks (CIS Benchmarks)
- [ ] Use hardened machine images (golden images) for cloud compute instances
- [ ] Implement automated compliance checking for OS configurations

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Hardened images | EC2 Image Builder (CIS hardened AMIs), AWS Marketplace CIS images | Azure Compute Gallery (hardened images), Azure Marketplace CIS images | Custom images with Packer, GCP Marketplace CIS images |
| OS compliance | Systems Manager Compliance, Inspector CIS checks | Azure Automanage, Guest Configuration (Azure Policy) | OS Config Management (OS policy compliance) |

#### IVS-05: Production and Non-Production Environments

- [ ] Separate production and non-production environments using different cloud accounts/subscriptions/projects
- [ ] Apply production-grade security controls to environments containing production data
- [ ] Restrict network connectivity between production and non-production environments

#### IVS-06: Segmentation and Segregation

- [ ] Implement microsegmentation for workloads requiring isolation
- [ ] Isolate management networks from application networks
- [ ] Implement service mesh for workload-to-workload security where applicable

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Microsegmentation | Security groups (per-ENI), VPC Lattice | NSGs (per-NIC), Azure Service Fabric | Firewall rules (per-tag/SA), GKE Network Policy, Traffic Director |

#### IVS-09: Network Defense

- [ ] Implement DDoS protection for internet-facing workloads
- [ ] Deploy web application firewalls for web-facing applications
- [ ] Implement intrusion detection for cloud networks

### LOG — Logging and Monitoring

#### LOG-01: Logging and Monitoring Policy

- [ ] Define a logging and monitoring policy covering all cloud environments
- [ ] Specify which events must be logged (authentication, authorization, data access, configuration changes, security events)
- [ ] Define log retention periods

#### LOG-02: Security Monitoring and Alerting

- [ ] Implement real-time security monitoring for cloud environments
- [ ] Define alert thresholds and notification procedures
- [ ] Implement automated response for high-confidence alerts where appropriate
- [ ] Integrate cloud security alerts with the organization's SIEM or security operations center

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| SIEM integration | Security Hub (aggregation), integration with Splunk/Sumo Logic/Datadog/Chronicle | Microsoft Sentinel (native SIEM), integration with third-party SIEMs | Chronicle Security Operations (native SIEM), SCC integration with third-party SIEMs |
| Automated response | EventBridge rules + Lambda, Security Hub automated response | Sentinel Playbooks (Logic Apps), Defender automated response | Security Command Center muting/automated response, Cloud Functions |

#### LOG-03: Security Monitoring and Alerting Access

- [ ] Restrict access to security logs and monitoring tools to authorized personnel
- [ ] Implement role-based access to logging and monitoring systems
- [ ] Protect the integrity of log data

#### LOG-04: Audit Logging

- [ ] Enable audit logging for all cloud services in scope
- [ ] Capture at minimum: who, what, when, where, outcome for each event
- [ ] Store audit logs in a centralized, tamper-resistant location

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Audit logging | CloudTrail (management and data events), organization trail | Azure Monitor activity logs, resource diagnostic logs | Cloud Audit Logs (admin activity, data access, system event, policy denied) |
| Centralized log store | S3 (central logging account) with Object Lock, CloudWatch Logs | Log Analytics workspace (central), Blob with immutable storage | Cloud Logging (organization sinks), Cloud Storage with retention locks |

#### LOG-05: Audit Log Monitoring and Response

- [ ] Monitor audit logs for security-relevant events
- [ ] Implement correlation rules to detect attack patterns
- [ ] Respond to detected events per incident management procedures

#### LOG-06: Clock Synchronization

- [ ] Ensure all cloud resources use synchronized time sources
- [ ] Verify that cloud provider time synchronization meets audit requirements
- [ ] Include timestamps in all log entries using UTC

#### LOG-07: Encryption Monitoring and Reporting

- [ ] Monitor encryption status for all data stores
- [ ] Alert on unencrypted resources
- [ ] Report encryption compliance status

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Encryption monitoring | Security Hub (encryption checks), Config rules for encryption compliance | Defender for Cloud (encryption recommendations), Azure Policy | Security Health Analytics (encryption checks), Organization Policy |

#### LOG-09: Log Protection

- [ ] Protect logs from unauthorized modification and deletion
- [ ] Implement write-once-read-many (WORM) storage for critical logs
- [ ] Implement access controls on log storage

#### LOG-13: Failures and Anomalies Detection

- [ ] Implement anomaly detection for cloud workloads
- [ ] Monitor for unusual API call patterns, data access patterns, and resource usage
- [ ] Alert on deviations from established baselines

### SEF — Security Incident Management, E-Discovery & Cloud Forensics

#### SEF-01: Security Incident Management Policy

- [ ] Define an incident management policy covering cloud environments
- [ ] Include incident classification, escalation, and notification procedures
- [ ] Define roles and responsibilities for incident response

#### SEF-02: Service Management Policy

- [ ] Integrate cloud service management with incident management
- [ ] Include cloud provider support escalation procedures
- [ ] Define SLAs for incident response and resolution

#### SEF-03: Incident Response Plans

- [ ] Develop incident response plans for cloud-specific scenarios (credential compromise, data exposure, ransomware, supply chain attack, cryptomining)
- [ ] Include containment, eradication, and recovery procedures
- [ ] Define communication plans for stakeholders, customers, and regulators

#### SEF-04: Incident Response Testing

- [ ] Test incident response plans at least annually through tabletop exercises
- [ ] Conduct technical response exercises (red team, purple team, game days)
- [ ] Update plans based on test results

#### SEF-05: Incident Response Metrics

- [ ] Define and track incident response metrics (MTTD, MTTR, number of incidents by severity)
- [ ] Report metrics to management at planned intervals

#### SEF-06: Event Triage Processes

- [ ] Define event triage procedures for cloud security events
- [ ] Implement automated triage for high-volume, low-complexity events
- [ ] Escalate events that meet incident criteria

#### SEF-07: Evidence Management

- [ ] Define evidence collection procedures for cloud environments
- [ ] Implement forensic-ready logging (sufficient detail, tamper-proof storage)
- [ ] Address cloud-specific forensic challenges (ephemeral resources, shared infrastructure, provider cooperation)

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Forensic data collection | EBS snapshots, memory acquisition (via EC2 serial console), CloudTrail logs, VPC Flow Logs, Detective | VM disk snapshots, Azure Monitor logs, Network Watcher packet capture, Sentinel investigation | Persistent Disk snapshots, Cloud Audit Logs, VPC Flow Logs, Packet Mirroring |
| Forensic analysis | Detective (investigation graphs), Athena (log analysis) | Sentinel (investigation and hunting), Data Explorer (log analysis) | Chronicle (investigation and hunting), BigQuery (log analysis) |

### STA — Supply Chain Management, Transparency and Accountability

#### STA-01: Supply Chain Management Policy

- [ ] Define a supply chain risk management policy
- [ ] Include cloud providers, SaaS applications, and open source dependencies
- [ ] Define vendor assessment requirements and frequency

#### STA-02: Supply Chain Risk Management

- [ ] Assess supply chain risks for all critical cloud dependencies
- [ ] Include sub-processor risk in cloud provider assessments
- [ ] Monitor supply chain threat intelligence (dependency vulnerabilities, provider security incidents)

#### STA-03: Third-Party Assessment

- [ ] Conduct or obtain security assessments for cloud providers and third-party services
- [ ] Review SOC 2 Type II reports, ISO 27001 certificates, and CSA STAR reports
- [ ] Assess third-party controls against the organization's security requirements

#### STA-04: Supply Chain Agreements

- [ ] Include security requirements in cloud provider contracts
- [ ] Define incident notification requirements
- [ ] Include audit rights and compliance reporting requirements

#### STA-05: Supply Chain Monitoring and Review

- [ ] Monitor cloud provider security posture on an ongoing basis
- [ ] Subscribe to cloud provider security bulletins and advisories
- [ ] Review cloud provider compliance certifications when renewed

#### STA-07: Supply Chain Data Security Assessment

- [ ] Assess cloud provider data security controls
- [ ] Verify data encryption, access controls, and data segregation
- [ ] Assess data recovery and backup capabilities

#### STA-09: Third-Party Deficiency Remediation

- [ ] Track and follow up on deficiencies identified in third-party assessments
- [ ] Define escalation procedures for critical deficiencies
- [ ] Include remediation timelines in supplier agreements

#### STA-14: Supply Chain Data Security Assessment

- [ ] Conduct software composition analysis for open source dependencies
- [ ] Implement container image scanning for base image vulnerabilities
- [ ] Use trusted artifact registries and verify artifact integrity (signatures, SBOMs)

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Software supply chain | ECR image scanning, CodeGuru, Inspector for Lambda | ACR image scanning, Defender for DevOps, GitHub Advanced Security | Artifact Analysis, Binary Authorization, Software Delivery Shield |
| SBOM management | Inspector SBOM export | GitHub dependency graph, Defender for DevOps | Artifact Analysis SBOM |

### TVM — Threat & Vulnerability Management

#### TVM-01: Threat and Vulnerability Management Policy

- [ ] Define a vulnerability management policy covering cloud environments
- [ ] Define scanning requirements (scope, frequency, tools)
- [ ] Define remediation SLAs by severity

#### TVM-02: Vulnerability Management

- [ ] Implement automated vulnerability scanning for all cloud resources (VMs, containers, serverless, infrastructure configurations)
- [ ] Scan at least weekly for externally-facing resources and upon deployment for new resources
- [ ] Prioritize remediation based on risk (CVSS score, exploitability, exposure, asset criticality)

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Vulnerability scanning | Inspector (EC2, ECR, Lambda), GuardDuty | Defender for Cloud vulnerability assessment, Defender for Servers, Defender for Containers | Security Command Center (Web Security Scanner, VM Manager vulnerability reports), Artifact Analysis |
| Configuration scanning | Security Hub, AWS Config rules | Defender for Cloud CSPM, Azure Policy | Security Health Analytics, SCC Premium |

#### TVM-03: Vulnerability Remediation Procedure

- [ ] Define remediation procedures including patching, configuration changes, and compensating controls
- [ ] Track remediation progress and escalate overdue items
- [ ] Re-scan after remediation to verify fixes

#### TVM-04: Detection Updates

- [ ] Ensure vulnerability scanning tools are updated with latest detection signatures
- [ ] Subscribe to cloud provider vulnerability notifications
- [ ] Monitor CVE databases and security advisories for cloud services in use

#### TVM-06: Penetration Testing

- [ ] Conduct penetration testing of cloud environments at least annually
- [ ] Include cloud-specific attack vectors (SSRF for metadata services, IAM misconfigurations, storage bucket enumeration)
- [ ] Review cloud provider penetration testing policies and obtain authorization where required
- [ ] Remediate findings based on severity and risk

**Cloud Provider Penetration Testing Policies:**

| Provider | Policy |
|---|---|
| AWS | No prior approval required for most services; prohibited services list applies |
| Azure | No prior approval required; must follow Rules of Engagement |
| GCP | No prior approval required; must follow Acceptable Use Policy |

#### TVM-07: Vulnerability Identification and Reporting

- [ ] Implement a vulnerability disclosure program (or accept reports through a designated channel)
- [ ] Triage and respond to externally reported vulnerabilities
- [ ] Track vulnerabilities from identification through remediation

#### TVM-09: Vulnerability Management Metrics

- [ ] Track vulnerability management metrics (scan coverage, open vulnerabilities by severity, mean time to remediate, SLA compliance)
- [ ] Report metrics to management at planned intervals
- [ ] Use metrics to drive continuous improvement

### UEM — Universal Endpoint Management

#### UEM-01: Endpoint Devices Policy

- [ ] Define an endpoint security policy for devices accessing cloud environments
- [ ] Include requirements for device encryption, patching, antivirus/EDR, and screen lock
- [ ] Address BYOD and contractor device requirements

#### UEM-02: Mobile Device Management

- [ ] Implement mobile device management (MDM) for devices accessing cloud resources
- [ ] Enforce device compliance policies (encryption, PIN, OS version)
- [ ] Implement remote wipe capability for lost or stolen devices

#### UEM-03: BYOD Policy

- [ ] Define BYOD security requirements for cloud access
- [ ] Implement containerization or application-level controls for BYOD
- [ ] Restrict data download/caching on BYOD devices

#### UEM-04: Endpoint Management and Compliance

- [ ] Implement endpoint compliance checking before granting cloud access
- [ ] Integrate endpoint security posture into conditional access decisions
- [ ] Monitor endpoint compliance continuously

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Endpoint-based access control | AWS Verified Access (device posture integration), WorkSpaces (managed endpoints) | Entra ID Conditional Access (Intune device compliance), Windows 365 | BeyondCorp Enterprise (device trust, context-aware access), Chrome Enterprise |

#### UEM-06: Endpoint Operating System Security

- [ ] Enforce OS patching on endpoints accessing cloud environments
- [ ] Implement OS-level security configurations (firewall, disk encryption, secure boot)
- [ ] Monitor OS security posture

#### UEM-09: Anti-Malware Detection and Prevention

- [ ] Deploy anti-malware/EDR on all endpoints accessing cloud environments
- [ ] Ensure anti-malware signatures and detection models are updated
- [ ] Monitor and respond to endpoint security alerts

#### UEM-11: Remote Endpoint Management

- [ ] Implement remote management capabilities for endpoints (patching, configuration, wipe)
- [ ] Secure remote management channels
- [ ] Audit remote management activities

#### UEM-13: Endpoint Encryption

- [ ] Enforce full-disk encryption on all endpoints accessing cloud environments
- [ ] Manage encryption keys centrally
- [ ] Verify encryption compliance through endpoint management tools
