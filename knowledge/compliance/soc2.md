# SOC 2 Trust Service Criteria - Cloud Control Mapping

## Scope

Covers SOC 2 Trust Service Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy) mapped to cloud services, including audit preparation, evidence collection, and common audit findings. Does not cover SOX IT General Controls (see `compliance/sox.md`) or general governance patterns (see `general/governance.md`).

## Overview

SOC 2 (System and Organization Controls 2) is an auditing framework developed by the AICPA (American Institute of Certified Public Accountants). It evaluates an organization's information systems based on five Trust Service Criteria (TSC): Security, Availability, Processing Integrity, Confidentiality, and Privacy.

**Report Types:**
- **Type I:** Evaluates the design of controls at a point in time.
- **Type II:** Evaluates both the design and operating effectiveness of controls over a period (typically 6-12 months).

**Applicability:** SOC 2 is not a regulatory requirement but is often demanded by enterprise customers as assurance of service provider security. It is especially relevant for SaaS, PaaS, and managed service providers.

**Security (Common Criteria) is required.** The other four criteria (Availability, Processing Integrity, Confidentiality, Privacy) are optional and included based on the nature of the service.

---

## Security (Common Criteria) - Required

### CC1: Control Environment

**Purpose:** The foundation of all other controls. Demonstrates that the organization is committed to integrity, ethical values, and effective governance.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Governance structure | AWS Organizations, Control Tower | Management Groups, Azure Lighthouse | Resource Manager, Organization Policy |
| Policy enforcement | SCPs, Config Rules | Azure Policy, Blueprints | Organization Policy, Assured Workloads |
| Compliance evidence | Audit Manager, AWS Artifact | Compliance Manager, Service Trust Portal | Compliance Reports, Assured Workloads |

#### Architect Checklist

- [ ] **[Recommended]** Organizational structure and reporting lines for security are documented
- [ ] **[Recommended]** Board/management oversight of security program is evidenced
- [ ] **[Recommended]** Code of conduct and ethics policy covers technology and data handling
- [ ] **[Recommended]** Cloud governance framework (Organizations, Management Groups, Resource Manager hierarchy) is implemented
- [ ] **[Critical]** Compliance monitoring dashboards are configured (Audit Manager, Compliance Manager)

---

### CC2: Communication and Information

**Purpose:** The organization obtains, generates, and uses relevant quality information to support internal controls. Internal and external communication supports controls.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Security notifications | SNS, Security Hub findings | Service Health, Defender alerts | Cloud Monitoring alerts, Advisory Notifications |
| Documentation | Internal wikis, runbooks | Internal wikis, runbooks | Internal wikis, runbooks |
| Status communication | Health Dashboard | Azure Status, Service Health | Google Cloud Status Dashboard |

#### Architect Checklist

- [ ] **[Recommended]** Security policies are documented, approved, and distributed to relevant personnel
- [ ] **[Recommended]** Security alert notifications are configured and routed to appropriate teams
- [ ] **[Recommended]** External communication channels exist for security disclosures and incident notifications
- [ ] **[Recommended]** System changes are communicated to affected stakeholders
- [ ] **[Recommended]** Cloud provider security bulletins and advisories are monitored

---

### CC3: Risk Assessment

**Purpose:** The organization identifies and assesses risks to the achievement of its objectives, including fraud risk.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Risk identification | Security Hub, Inspector, GuardDuty | Defender for Cloud, Secure Score | Security Command Center, Security Health Analytics |
| Vulnerability assessment | Inspector, ECR scanning | Defender Vulnerability Management | Artifact Analysis, Web Security Scanner |
| Threat intelligence | GuardDuty threat feeds | Threat Intelligence (Sentinel) | Chronicle Threat Intelligence |
| Configuration risk | AWS Config, Trusted Advisor | Azure Advisor, Policy compliance | Security Health Analytics, IAM Recommender |

#### Architect Checklist

- [ ] **[Recommended]** Formal risk assessment process is established and conducted at least annually
- [ ] **[Recommended]** Risk register includes cloud-specific risks (misconfiguration, data exposure, account compromise)
- [ ] **[Critical]** Vulnerability scanning is automated and continuous
- [ ] **[Recommended]** Threat detection services are enabled across all accounts/subscriptions/projects
- [ ] **[Recommended]** Risk tolerance levels are defined and drive control implementation decisions
- [ ] **[Recommended]** Third-party and supply chain risks are assessed (including cloud provider risk)

---

### CC4: Monitoring Activities

**Purpose:** The organization monitors internal controls and evaluates their effectiveness on an ongoing basis.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Continuous monitoring | Security Hub, Config, CloudWatch | Defender for Cloud, Monitor, Policy | Security Command Center, Cloud Monitoring |
| Compliance monitoring | Audit Manager | Compliance Manager | Assured Workloads |
| Deficiency tracking | Security Hub findings, Jira/ticketing | Defender recommendations, ticketing | SCC findings, ticketing |
| Control effectiveness | Config conformance packs | Policy compliance state | Organization Policy audit |

#### Architect Checklist

- [ ] **[Recommended]** Continuous monitoring is implemented across all cloud environments
- [ ] **[Recommended]** Security Hub / Defender for Cloud / Security Command Center aggregates findings
- [ ] **[Recommended]** Control deficiencies are tracked in a ticketing system with SLAs for remediation
- [ ] **[Critical]** Compliance drift is detected and alerted upon
- [ ] **[Recommended]** Management reviews monitoring results at defined intervals
- [ ] **[Recommended]** Independent evaluations (internal audit, external assessments) supplement ongoing monitoring

---

### CC5: Control Activities

**Purpose:** The organization designs and implements control activities to mitigate risks to acceptable levels.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Infrastructure as code | CloudFormation, CDK, Terraform | ARM/Bicep, Terraform | Deployment Manager, Terraform |
| CI/CD controls | CodePipeline, CodeBuild | Azure DevOps, GitHub Actions | Cloud Build, Cloud Deploy |
| Change management | CloudFormation change sets, CodePipeline approvals | Azure DevOps approvals, ARM what-if | Cloud Build approvals |
| Segregation of duties | Separate accounts (dev/staging/prod), IAM | Separate subscriptions, RBAC | Separate projects, IAM |

#### Architect Checklist

- [ ] **[Recommended]** Infrastructure is deployed via code (IaC) with version control and peer review
- [ ] **[Recommended]** CI/CD pipelines enforce quality gates (testing, security scanning, approval)
- [ ] **[Recommended]** Change management process requires approval before production deployment
- [ ] **[Critical]** Segregation of duties is enforced (developers cannot deploy to production unilaterally)
- [ ] **[Recommended]** Environment separation (dev, staging, production) prevents unauthorized access to production data
- [ ] **[Recommended]** Automated controls are preferred over manual controls for consistency
- [ ] **[Recommended]** Technology controls are mapped to specific risks they mitigate

---

### CC6: Logical and Physical Access Controls

**Purpose:** The organization restricts logical and physical access to authorized users and protects system boundaries.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Identity management | IAM, IAM Identity Center, Cognito | Entra ID, Entra External ID (formerly Azure AD B2C) | Cloud Identity, Identity Platform |
| MFA | IAM MFA, Identity Center MFA | Entra MFA, Conditional Access | 2-Step Verification, Titan Keys |
| SSO / federation | IAM Identity Center (SAML, OIDC) | Entra ID (SAML, OIDC, WS-Fed) | Cloud Identity (SAML, OIDC) |
| Network access controls | Security Groups, NACLs, VPC | NSGs, Azure Firewall, VNet | Firewall Rules, Cloud Armor |
| Encryption at rest | KMS, CloudHSM | Key Vault, Managed HSM | Cloud KMS, Cloud HSM |
| Encryption in transit | ACM, ALB/CloudFront TLS | Key Vault certs, App Gateway TLS | Certificate Manager, LB TLS |
| Physical security | AWS data center certifications | Azure data center certifications | Google data center certifications |
| Secrets management | Secrets Manager, Parameter Store | Key Vault | Secret Manager |

#### Architect Checklist

- [ ] **[Recommended]** Identity provider is centralized (SSO/federation for all cloud accounts)
- [ ] **[Critical]** MFA is enforced for all human users (phishing-resistant methods preferred)
- [ ] **[Critical]** Least privilege is enforced -- permissions are scoped to specific resources and actions
- [ ] **[Critical]** Service accounts use short-lived credentials (STS, managed identities, workload identity)
- [ ] **[Critical]** Network access follows defense-in-depth (security groups + NACLs/firewall rules)
- [ ] **[Critical]** All data is encrypted at rest using customer-managed keys for sensitive workloads
- [ ] **[Recommended]** All data in transit uses TLS 1.2+
- [ ] **[Recommended]** Secrets are stored in dedicated services and rotated automatically
- [ ] **[Recommended]** Access is reviewed and recertified at least quarterly
- [ ] **[Recommended]** Physical access is managed by cloud provider (verify SOC 2 report from provider)
- [ ] **[Recommended]** Deprovisioning removes access within defined SLA (same day recommended)
- [ ] **[Critical]** Root/global admin accounts are secured with hardware MFA and monitored for usage

---

### CC7: System Operations

**Purpose:** The organization detects and responds to security incidents and other anomalies.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Threat detection | GuardDuty | Defender for Cloud, Sentinel | Security Command Center, Chronicle |
| Vulnerability management | Inspector, ECR scanning | Defender Vulnerability Management | Artifact Analysis |
| Incident response | Security Hub, Detective, EventBridge | Sentinel, Defender for Cloud | Chronicle, Security Command Center |
| Monitoring and alerting | CloudWatch, CloudTrail | Monitor, Activity Log | Cloud Monitoring, Cloud Logging |
| Patch management | Systems Manager Patch Manager | Azure Update Manager | OS Patch Management |
| Anti-malware | GuardDuty Malware Protection | Defender for Endpoint | Security Command Center |

#### Architect Checklist

- [ ] **[Recommended]** Threat detection is enabled in all environments (GuardDuty, Defender, SCC)
- [ ] **[Critical]** Vulnerability scanning covers infrastructure, containers, and application dependencies
- [ ] **[Recommended]** Patch management process ensures critical patches are applied within defined SLAs
- [ ] **[Critical]** Incident response plan is documented, includes escalation procedures, and is tested at least annually
- [ ] **[Recommended]** Security events are correlated in a SIEM for real-time analysis
- [ ] **[Recommended]** Alerting thresholds are tuned to minimize false positives while catching true threats
- [ ] **[Recommended]** On-call rotation ensures 24/7 coverage for security incidents
- [ ] **[Recommended]** Post-incident reviews are conducted and lessons learned are implemented

---

### CC8: Change Management

**Purpose:** The organization manages changes to infrastructure and software in a controlled manner.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| IaC and version control | CloudFormation, CDK, CodeCommit | ARM/Bicep, Azure Repos | Deployment Manager, Cloud Source Repositories |
| Deployment pipelines | CodePipeline, CodeDeploy | Azure DevOps, GitHub Actions | Cloud Build, Cloud Deploy |
| Change tracking | CloudTrail, Config | Activity Log, Change Analysis | Cloud Audit Logs, Cloud Asset Inventory |
| Rollback | CloudFormation rollback, CodeDeploy rollback | ARM rollback, App Service slots | Cloud Deploy rollback |
| Testing | CodeBuild, Device Farm | Azure Test Plans, Azure DevOps | Cloud Build |

#### Architect Checklist

- [ ] **[Recommended]** All changes go through a formal change management process (request, review, approve, deploy, verify)
- [ ] **[Recommended]** Changes are tracked in version control with meaningful commit messages
- [ ] **[Recommended]** Infrastructure changes are deployed via IaC -- no manual console changes in production
- [ ] **[Recommended]** Peer review (pull request) is required for all code and infrastructure changes
- [ ] **[Recommended]** Automated testing validates changes before production deployment
- [ ] **[Recommended]** Rollback procedures are documented and tested
- [ ] **[Recommended]** Emergency change procedures exist with post-facto review and approval
- [ ] **[Critical]** CloudTrail / Activity Log / Audit Logs capture all infrastructure changes
- [ ] **[Recommended]** Unauthorized changes are detected and alerted via Config / Policy / Asset Inventory

---

### CC9: Risk Mitigation

**Purpose:** The organization identifies, selects, and develops risk mitigation activities, including vendor management.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Vendor risk assessment | AWS Artifact (SOC reports, certifications) | Service Trust Portal | Compliance Reports Manager |
| Business continuity | Multi-AZ, Multi-Region, AWS Backup | Availability Zones, Azure Site Recovery | Multi-region, Cloud Storage dual-region |
| Insurance / transfer | Cyber insurance (organizational) | Cyber insurance (organizational) | Cyber insurance (organizational) |

#### Architect Checklist

- [ ] **[Recommended]** Risk mitigation strategies are defined for each identified risk (accept, mitigate, transfer, avoid)
- [ ] **[Recommended]** Cloud provider's SOC 2 Type II report is reviewed at least annually
- [ ] **[Recommended]** Complementary User Entity Controls (CUECs) from provider SOC reports are implemented
- [ ] **[Recommended]** Vendor risk assessments are conducted for all critical third-party services
- [ ] **[Critical]** Business continuity and disaster recovery plans are maintained and tested
- [ ] **[Recommended]** Cyber insurance coverage aligns with identified residual risks
- [ ] **[Recommended]** Risk acceptance decisions are documented and approved by management

---

## Availability (A1)

### A1.1, A1.2, A1.3: Availability Commitments

**Purpose:** The system is available for operation and use as committed or agreed (SLAs).

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| High availability | Multi-AZ deployments, Auto Scaling, ELB | Availability Zones, Scale Sets, Load Balancer | Regional MIGs, Cloud Load Balancing |
| Disaster recovery | Multi-Region, Elastic Disaster Recovery, AWS Backup | Azure Site Recovery, Geo-Redundant Storage | Multi-region storage, Cross-region replication |
| Monitoring | CloudWatch, Health Dashboard | Monitor, Service Health | Cloud Monitoring, Status Dashboard |
| Capacity planning | Auto Scaling, Compute Optimizer | Autoscale, Advisor | Autoscaler, Recommender |
| DDoS protection | Shield, Shield Advanced | DDoS Protection | Cloud Armor |
| CDN / edge | CloudFront | Front Door, CDN | Cloud CDN |
| DNS failover | Route 53 health checks, failover routing | Traffic Manager, Front Door | Cloud DNS, Traffic Director |

#### Architect Checklist

- [ ] **[Recommended]** SLAs are defined and documented for all customer-facing services
- [ ] **[Recommended]** Architecture supports the committed SLA (Multi-AZ minimum for 99.9%+)
- [ ] **[Recommended]** Auto-scaling is configured with appropriate min/max/desired settings
- [ ] **[Critical]** Health checks and automated failover are configured
- [ ] **[Recommended]** DDoS protection is enabled (Shield/DDoS Protection/Cloud Armor)
- [ ] **[Critical]** Disaster recovery plan defines RPO and RTO and is tested at least annually
- [ ] **[Critical]** Backup and restore procedures are documented and tested
- [ ] **[Recommended]** Capacity planning is reviewed quarterly to prevent resource exhaustion
- [ ] **[Recommended]** Incident communication procedures include customer notification for availability events
- [ ] **[Recommended]** Dependencies are identified and monitored (third-party services, APIs)
- [ ] **[Critical]** Runbooks exist for common availability scenarios (failover, scaling, recovery)

---

## Processing Integrity (PI1)

### PI1.1 - PI1.5: Processing Integrity Commitments

**Purpose:** System processing is complete, valid, accurate, timely, and authorized.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Input validation | API Gateway validation, Lambda input validation | API Management validation, Function validation | Apigee validation, Cloud Functions validation |
| Data quality | Glue Data Quality, DynamoDB conditions | Data Factory data flows, SQL constraints | Dataflow, BigQuery constraints |
| Processing monitoring | CloudWatch metrics, Step Functions | Monitor metrics, Logic Apps | Cloud Monitoring, Workflows |
| Queue / messaging integrity | SQS (exactly-once), SNS | Service Bus (exactly-once), Event Grid | Pub/Sub (exactly-once) |
| Transaction integrity | RDS/Aurora transactions, DynamoDB transactions | SQL Database transactions, Cosmos DB transactions | Cloud SQL transactions, Spanner |
| Error handling | Dead letter queues (SQS, SNS), CloudWatch Alarms | Dead letter queues (Service Bus), Monitor Alerts | Dead letter topics (Pub/Sub), Monitoring Alerts |

#### Architect Checklist

- [ ] **[Recommended]** Input validation is enforced at all system boundaries (API gateway, application layer)
- [ ] **[Recommended]** Data processing outputs are verified against expected results (reconciliation)
- [ ] **[Recommended]** Error handling captures and reports processing failures without data loss
- [ ] **[Recommended]** Dead letter queues capture failed messages for investigation and reprocessing
- [ ] **[Recommended]** Processing completeness is monitored (record counts, checksums, reconciliation reports)
- [ ] **[Recommended]** Transaction integrity is enforced for multi-step operations (ACID where applicable)
- [ ] **[Recommended]** Processing SLAs (timeliness) are defined and monitored
- [ ] **[Recommended]** Batch processing includes validation checkpoints and rollback capability
- [ ] **[Recommended]** Data lineage is tracked for critical processing pipelines
- [ ] **[Recommended]** Customers are notified of processing errors that affect their data

---

## Confidentiality (C1)

### C1.1, C1.2: Confidentiality Commitments

**Purpose:** Confidential information is protected throughout its lifecycle as committed or agreed.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Data classification | Macie, resource tagging | Purview Information Protection, resource tagging | Sensitive Data Protection (DLP), resource labels |
| Encryption at rest | KMS (CMK), CloudHSM, S3 SSE | Key Vault, Managed HSM, Storage Encryption | Cloud KMS, Cloud HSM, CMEK |
| Encryption in transit | ACM, TLS enforcement | Key Vault certificates, TLS enforcement | Certificate Manager, TLS enforcement |
| Data loss prevention | Macie (S3), CloudWatch + custom | Purview DLP, Defender for Cloud Apps | Sensitive Data Protection API |
| Access controls | IAM, S3 policies, Lake Formation | RBAC, Storage ACLs, Purview | IAM, BigQuery ACLs, VPC Service Controls |
| Data masking | DynamoDB client-side, custom | Dynamic Data Masking (SQL) | BigQuery column-level security, Data Catalog |
| Secure deletion | S3 lifecycle, KMS key deletion | Blob lifecycle, Key Vault soft delete + purge | Cloud Storage lifecycle, KMS key destruction |
| Network isolation | VPC, PrivateLink, VPC Endpoints | VNet, Private Link, Service Endpoints | VPC, Private Service Connect, VPC Service Controls |

#### Architect Checklist

- [ ] **[Recommended]** Data classification scheme is defined (public, internal, confidential, restricted)
- [ ] **[Recommended]** All resources are tagged/labeled with their data classification
- [ ] **[Recommended]** Automated data discovery scans identify unclassified confidential data
- [ ] **[Critical]** Encryption at rest uses customer-managed keys for confidential data
- [ ] **[Critical]** Encryption in transit uses TLS 1.2+ for all confidential data flows
- [ ] **[Recommended]** DLP controls prevent unauthorized exfiltration of confidential data
- [ ] **[Recommended]** VPC Service Controls / PrivateLink / Private Link restricts data access to authorized networks
- [ ] **[Recommended]** Data masking is applied when full access to confidential data is not required
- [ ] **[Critical]** Data retention and deletion policies are enforced automatically via lifecycle rules
- [ ] **[Critical]** Confidential data is purged when no longer needed (crypto-shredding via key deletion is acceptable)
- [ ] **[Recommended]** Confidentiality obligations are defined in customer contracts and enforced technically

---

## Privacy (P1 - P8)

### P1: Notice and Communication of Objectives

**Purpose:** The entity provides notice about its privacy practices.

#### Architect Checklist

- [ ] **[Recommended]** Privacy notice is accessible to data subjects before or at the time of data collection
- [ ] **[Critical]** Notice includes types of data collected, purposes, retention, sharing, and individual rights

### P2: Choice and Consent

**Purpose:** The entity communicates choices available and obtains consent.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Consent management | Cognito (custom attributes), custom | Entra External ID (custom flows), custom | Identity Platform, custom |
| Preference storage | DynamoDB, RDS | Cosmos DB, SQL Database | Firestore, Cloud SQL |

#### Architect Checklist

- [ ] **[Recommended]** Consent mechanisms are implemented for data collection (opt-in where required)
- [ ] **[Recommended]** Consent preferences are stored and enforced programmatically
- [ ] **[Recommended]** Consent withdrawal mechanisms are functional and trigger data handling changes

### P3: Collection

**Purpose:** Personal information is collected only for identified purposes.

#### Architect Checklist

- [ ] **[Recommended]** Data collection is limited to what is necessary for stated purposes (data minimization)
- [ ] **[Recommended]** Collection methods are documented and consistent with privacy notice

### P4: Use, Retention, and Disposal

**Purpose:** Personal information is used, retained, and disposed of in accordance with objectives.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Retention policies | S3 Lifecycle, DynamoDB TTL, RDS snapshot retention | Blob lifecycle, Cosmos DB TTL | Cloud Storage lifecycle, BigQuery partition expiration |
| Automated deletion | S3 Lifecycle rules, Lambda-based cleanup | Azure Functions + lifecycle | Cloud Functions + lifecycle, Cloud Scheduler |
| Data inventory | Macie, Config | Purview Data Map | Data Catalog, Cloud Asset Inventory |

#### Architect Checklist

- [ ] **[Critical]** Data retention periods are defined for each category of personal information
- [ ] **[Critical]** Automated deletion enforces retention policies (lifecycle rules, TTL)
- [ ] **[Recommended]** Personal information is not used for purposes beyond those stated in the privacy notice
- [ ] **[Recommended]** Data inventory tracks where personal information is stored across all systems

### P5: Access

**Purpose:** Data subjects can access their personal information for review and update.

#### Architect Checklist

- [ ] **[Recommended]** Self-service mechanisms allow data subjects to view their personal information
- [ ] **[Recommended]** Data subject access requests (DSARs) can be fulfilled within required timeframes
- [ ] **[Critical]** Authentication verifies data subject identity before granting access to their data

### P6: Disclosure and Notification

**Purpose:** Personal information is disclosed to third parties only as authorized, with notification.

#### Architect Checklist

- [ ] **[Recommended]** Third-party data sharing is documented and aligned with privacy notice
- [ ] **[Recommended]** Data processing agreements are in place with third parties receiving personal information
- [ ] **[Critical]** Breach notification procedures comply with applicable privacy laws (GDPR 72 hours, CCPA, etc.)

### P7: Quality

**Purpose:** Personal information is accurate and complete for its intended purpose.

#### Architect Checklist

- [ ] **[Recommended]** Data validation ensures accuracy at point of collection
- [ ] **[Recommended]** Mechanisms exist for data subjects to correct inaccurate information
- [ ] **[Recommended]** Data quality checks are performed periodically

### P8: Monitoring and Enforcement

**Purpose:** The entity monitors compliance with its privacy commitments and has procedures for inquiries and disputes.

#### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Privacy monitoring | Macie, CloudWatch | Purview, Compliance Manager | Sensitive Data Protection, SCC |
| Access logging | CloudTrail, S3 access logs | Activity Log, storage analytics | Cloud Audit Logs |

#### Architect Checklist

- [ ] **[Critical]** Privacy compliance is monitored continuously (automated scanning for PII exposure)
- [ ] **[Recommended]** Access to personal information is logged and auditable
- [ ] **[Recommended]** Privacy impact assessments (PIAs) are conducted for new systems processing personal information
- [ ] **[Recommended]** Complaint and dispute resolution procedures are documented and accessible
- [ ] **[Recommended]** Privacy program effectiveness is reviewed at least annually

---

## SOC 2 Audit Preparation Checklist

### Evidence Collection

- [ ] **[Critical]** Cloud provider's SOC 2 Type II report is obtained (available via AWS Artifact, Azure Service Trust Portal, GCP Compliance Reports)
- [ ] **[Recommended]** CUECs (Complementary User Entity Controls) from provider report are mapped to customer controls
- [ ] **[Recommended]** All controls are documented with evidence of design and operating effectiveness
- [ ] **[Recommended]** Policy documents are current (reviewed and approved within the audit period)
- [ ] **[Recommended]** Access review evidence is collected (quarterly reviews with approvals)
- [ ] **[Recommended]** Change management records demonstrate consistent process adherence
- [ ] **[Critical]** Incident response testing evidence is available (tabletop exercises, simulations)
- [ ] **[Critical]** Vulnerability scan and penetration test reports cover the audit period
- [ ] **[Recommended]** Business continuity / DR test results are documented
- [ ] **[Critical]** Training completion records are available for all in-scope personnel

### Common Audit Findings to Prevent

- [ ] **[Recommended]** No orphaned accounts (terminated employee access still active)
- [ ] **[Recommended]** No overly permissive IAM policies (wildcard permissions)
- [ ] **[Critical]** No unencrypted data at rest or in transit
- [ ] **[Critical]** No missing MFA on privileged accounts
- [ ] **[Recommended]** No gaps in logging (all regions, all accounts)
- [ ] **[Recommended]** No undocumented exceptions to security policies
- [ ] **[Recommended]** No missing evidence for control operation during the audit period

## Common Decisions (ADR Triggers)

- **TSC scope selection** — which Trust Service Criteria beyond Security (Availability, Processing Integrity, Confidentiality, Privacy) to include
- **Audit period and type** — Type I vs Type II, audit period length (6 vs 12 months), auditor selection
- **Evidence collection architecture** — automated evidence collection tooling, continuous compliance monitoring, screenshot vs API-based evidence
- **Access review process** — quarterly review scope, approval workflow, access recertification tooling
- **Change management process** — CAB structure, emergency change policy, evidence of approval for every change
- **Incident response program** — incident classification, escalation procedures, tabletop exercise frequency
- **Vendor management** — cloud provider SOC report review cadence, CUEC mapping, subservice organization monitoring
- **Logging and monitoring architecture** — centralized logging, retention policy, alerting thresholds, anomaly detection
- **Business continuity and DR** — BCP/DR testing frequency, test documentation, recovery time validation

## See Also

- `general/security.md` — General security controls and architecture patterns
- `general/governance.md` — Cloud governance, tagging, and policy enforcement
- `compliance/sox.md` — SOX IT General Controls (complementary for publicly traded companies)
- `compliance/iso-27001.md` — ISO 27001 ISMS (often pursued alongside SOC 2)
