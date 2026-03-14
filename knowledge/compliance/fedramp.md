# FedRAMP Control Families - Cloud Control Mapping

## Overview

FedRAMP (Federal Risk and Authorization Management Program) provides a standardized approach for security assessment, authorization, and continuous monitoring of cloud products and services used by U.S. federal agencies. It is based on NIST SP 800-53 (currently Rev. 5).

**Impact Levels:**
- **Low:** 125 controls. For systems where loss of confidentiality, integrity, or availability would have limited adverse effect.
- **Moderate:** 325 controls. For systems where loss would have serious adverse effect. Most common level for federal cloud deployments.
- **High:** 421 controls. For systems where loss would have severe or catastrophic adverse effect (law enforcement, emergency services, financial, health).

**Authorization Paths:**
- **Agency ATO:** Sponsored by a specific federal agency.
- **JAB P-ATO:** Provisional authorization from the Joint Authorization Board (DoD, DHS, GSA).

**Key Requirement:** Only FedRAMP authorized cloud services may be used for federal data. The FedRAMP Marketplace lists all authorized services.

---

## Access Control (AC)

**Purpose:** Limit system access to authorized users, processes, and devices, and limit the types of transactions and functions that authorized users are permitted to execute.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| AC-1 | Policy and Procedures | Establish access control policy and procedures |
| AC-2 | Account Management | Manage system accounts (create, enable, modify, disable, remove) |
| AC-3 | Access Enforcement | Enforce approved authorizations for logical access |
| AC-4 | Information Flow Enforcement | Enforce approved authorizations for controlling information flow |
| AC-5 | Separation of Duties | Define and enforce separation of duties |
| AC-6 | Least Privilege | Employ principle of least privilege |
| AC-7 | Unsuccessful Logon Attempts | Enforce limit on consecutive invalid logon attempts |
| AC-11 | Device Lock | Prevent access after period of inactivity |
| AC-14 | Permitted Actions Without Identification | Identify actions permitted without identification/authentication |
| AC-17 | Remote Access | Establish usage restrictions for remote access |
| AC-18 | Wireless Access | Establish usage restrictions for wireless access |
| AC-20 | Use of External Systems | Establish terms and conditions for use of external systems |
| AC-22 | Publicly Accessible Content | Designate and review publicly accessible content |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Account management | IAM, IAM Identity Center, Organizations | Entra ID, Management Groups | Cloud Identity, Cloud IAM, Resource Manager |
| Access enforcement | IAM Policies, SCPs, Resource Policies | RBAC, Conditional Access, Azure Policy | IAM Policies, Organization Policy |
| Information flow | Security Groups, NACLs, Network Firewall | NSGs, Azure Firewall, Private Link | Firewall Rules, VPC Service Controls |
| Separation of duties | Separate accounts, IAM conditions | Separate subscriptions, PIM | Separate projects, IAM conditions |
| Least privilege | IAM Access Analyzer, permission boundaries | PIM, Access Reviews | IAM Recommender, Policy Analyzer |
| Remote access | Client VPN, Systems Manager Session Manager | VPN Gateway, Bastion | Cloud VPN, IAP (Identity-Aware Proxy) |
| Session controls | STS session policies, console timeout | Conditional Access session controls | Session controls, BeyondCorp |

### Architect Checklist

- [ ] Account management procedures cover the full lifecycle: creation, modification, disabling, removal
- [ ] Automated account management enforces inactive account disabling (90 days for Moderate/High)
- [ ] Least privilege is enforced -- IAM Access Analyzer / Access Reviews / IAM Recommender are enabled
- [ ] Separation of duties prevents single individuals from controlling entire critical processes
- [ ] Information flow enforcement uses VPC Service Controls, NACLs, security groups, and firewalls
- [ ] Remote access requires MFA and encrypted connections (VPN, Session Manager, IAP)
- [ ] Session lock activates after 15 minutes of inactivity (AC-11)
- [ ] Failed logon attempts are limited (3 attempts for High, lockout for 30 minutes minimum)
- [ ] Privileged accounts are managed separately from regular user accounts
- [ ] Service accounts follow least privilege and are reviewed quarterly
- [ ] Publicly accessible resources are reviewed monthly and authorized explicitly

---

## Audit and Accountability (AU)

**Purpose:** Create, protect, and retain system audit records to enable monitoring, analysis, investigation, and reporting of unauthorized activity.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| AU-1 | Policy and Procedures | Establish audit and accountability policy |
| AU-2 | Event Logging | Identify events that need to be logged |
| AU-3 | Content of Audit Records | Ensure records contain sufficient information |
| AU-4 | Audit Log Storage Capacity | Allocate sufficient storage for audit records |
| AU-5 | Response to Audit Logging Process Failures | Alert on audit processing failures |
| AU-6 | Audit Record Review, Analysis, and Reporting | Review and analyze audit records |
| AU-7 | Audit Record Reduction and Report Generation | Support on-demand audit review and reporting |
| AU-8 | Time Stamps | Use internal clocks for audit record timestamps |
| AU-9 | Protection of Audit Information | Protect audit records from unauthorized access or modification |
| AU-11 | Audit Record Retention | Retain audit records for defined period |
| AU-12 | Audit Record Generation | Generate audit records for defined events |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Event logging | CloudTrail (management + data events) | Activity Log, Diagnostic Logs | Cloud Audit Logs (Admin + Data Access) |
| Audit content | CloudTrail (who, what, when, where, outcome) | Activity Log (caller, operation, time, status) | Audit Logs (principal, method, resource, time) |
| Log storage | S3 (with lifecycle), CloudWatch Logs | Log Analytics, Storage Account | Cloud Logging buckets, Cloud Storage |
| Storage capacity | S3 (unlimited), CloudWatch retention config | Log Analytics retention (up to 730 days) | Cloud Logging retention (configurable) |
| Failure alerting | CloudTrail + CloudWatch Alarms | Activity Log alerts, Diagnostic settings | Cloud Monitoring alerts on logging pipeline |
| Log analysis | CloudTrail Lake, Athena, OpenSearch | Log Analytics (KQL), Sentinel | Cloud Logging queries, BigQuery, Chronicle |
| Time synchronization | Amazon Time Sync Service (NTP) | Azure NTP | Google NTP |
| Log protection | S3 Object Lock, CloudTrail integrity validation | Immutable blob storage | Locked retention policies, bucket lock |
| Log retention | S3 Lifecycle (configurable) | Log Analytics retention, Archive tier | Cloud Logging retention, Cloud Storage lifecycle |
| SIEM integration | Security Hub, OpenSearch, third-party | Sentinel | Chronicle |

### Architect Checklist

- [ ] CloudTrail / Activity Log / Audit Logs are enabled in all regions and accounts/subscriptions/projects
- [ ] Data access events (S3/Storage/Cloud Storage reads/writes) are logged for systems with federal data
- [ ] Audit records include: who, what, when, where, source, outcome for every event
- [ ] Log storage uses immutable storage (Object Lock, immutable blobs, locked retention)
- [ ] CloudTrail log file integrity validation is enabled
- [ ] Audit log retention meets FedRAMP requirements (minimum 1 year, 90 days immediately accessible for Moderate; 1 year immediately accessible for High)
- [ ] Alerts fire on audit processing failures (logging pipeline errors, storage failures)
- [ ] SIEM is deployed for automated log analysis and correlation
- [ ] Audit records are reviewed at least weekly (daily for High)
- [ ] Time synchronization uses authoritative NTP sources (provider-managed NTP)
- [ ] Log access is restricted to authorized security personnel via IAM
- [ ] Cross-account/cross-project logging aggregation is configured

---

## Security Assessment and Authorization (CA)

**Purpose:** Periodically assess security controls, authorize system operation, and monitor controls on an ongoing basis.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| CA-1 | Policy and Procedures | Establish security assessment policy |
| CA-2 | Control Assessments | Assess controls to determine effectiveness |
| CA-3 | Information Exchange | Approve and manage information exchange connections |
| CA-5 | Plan of Action and Milestones (POA&M) | Develop and update POA&M for identified weaknesses |
| CA-6 | Authorization | Authorize system before operation |
| CA-7 | Continuous Monitoring | Develop and implement continuous monitoring strategy |
| CA-8 | Penetration Testing | Conduct penetration testing |
| CA-9 | Internal System Connections | Authorize and document internal connections |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Control assessment | Audit Manager, Security Hub | Compliance Manager, Defender for Cloud | Assured Workloads, Security Command Center |
| Continuous monitoring | Config, Security Hub, GuardDuty | Policy, Defender for Cloud, Sentinel | Organization Policy, SCC, Chronicle |
| Penetration testing | Permitted (AWS pen test policy) | Permitted (Azure pen test policy) | Permitted (GCP pen test policy) |
| POA&M tracking | Audit Manager findings, Security Hub | Compliance Manager actions | SCC findings, Assured Workloads |
| Connection management | VPC Peering, Transit Gateway, PrivateLink | VNet Peering, Virtual WAN, Private Link | VPC Peering, Shared VPC, Private Service Connect |

### Architect Checklist

- [ ] Security controls are assessed at least annually (or per FedRAMP ConMon requirements)
- [ ] Continuous monitoring plan covers all FedRAMP controls with monthly OS/database scans and annual assessments
- [ ] POA&M is maintained with milestones, responsible parties, and completion dates
- [ ] High-risk POA&M items are remediated within 30 days, Moderate within 90 days, Low within 180 days
- [ ] Penetration testing is conducted annually by an independent assessor (3PAO)
- [ ] All system interconnections are documented and authorized
- [ ] Significant changes trigger reassessment per FedRAMP Significant Change Request process
- [ ] Monthly vulnerability scan results are submitted to FedRAMP PMO
- [ ] Annual assessment report is submitted per FedRAMP ConMon requirements

---

## Configuration Management (CM)

**Purpose:** Establish and maintain baseline configurations and inventories of systems and enforce security configuration settings.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| CM-1 | Policy and Procedures | Establish configuration management policy |
| CM-2 | Baseline Configuration | Develop, document, and maintain baseline configurations |
| CM-3 | Configuration Change Control | Implement change control process |
| CM-4 | Impact Analysis | Analyze changes for security impact |
| CM-5 | Access Restrictions for Change | Define and enforce access restrictions associated with changes |
| CM-6 | Configuration Settings | Establish and enforce security configuration settings |
| CM-7 | Least Functionality | Configure systems to provide only essential capabilities |
| CM-8 | System Component Inventory | Develop and maintain system component inventory |
| CM-9 | Configuration Management Plan | Develop and implement a configuration management plan |
| CM-10 | Software Usage Restrictions | Use software consistent with licensing agreements |
| CM-11 | User-Installed Software | Control and monitor user-installed software |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Baseline configuration | AMI baselines, CloudFormation, Config | VM images, ARM/Bicep templates, Azure Policy | Custom images, Deployment Manager, Organization Policy |
| Change control | CloudFormation change sets, CodePipeline | ARM what-if, Azure DevOps | Terraform plan, Cloud Build |
| Configuration settings | Config Rules, Systems Manager State Manager | Azure Policy (guest configuration) | Organization Policy, OS Config |
| Least functionality | Security Groups (minimal ports), hardened AMIs | NSGs (minimal ports), hardened images | Firewall rules (minimal ports), hardened images |
| Component inventory | Config, Systems Manager Inventory | Resource Graph, Azure Inventory | Cloud Asset Inventory |
| Drift detection | Config (compliance), CloudFormation drift | Policy compliance, ARM what-if | Organization Policy audit, Asset Inventory |
| CIS benchmarks | Inspector (CIS), Config conformance packs | Defender for Cloud (CIS) | Security Health Analytics (CIS) |

### Architect Checklist

- [ ] Baseline configurations are established using CIS benchmarks or DISA STIGs
- [ ] Configuration baselines are enforced via policy-as-code (Config Rules, Azure Policy, Organization Policy)
- [ ] Configuration drift is detected automatically and triggers alerts
- [ ] Change control process includes security impact analysis before approval
- [ ] Only authorized personnel can make production changes (enforce via IAM, pipeline controls)
- [ ] System component inventory is automated and continuously updated
- [ ] Least functionality: only required ports, protocols, and services are enabled
- [ ] Hardened base images (CIS, STIG) are used for all compute instances
- [ ] Software allow-lists restrict installation to approved software
- [ ] Configuration management plan documents roles, responsibilities, and processes
- [ ] FIPS 140-2/140-3 validated cryptographic modules are used (required for FedRAMP)

---

## Contingency Planning (CP)

**Purpose:** Establish, implement, and maintain plans for emergency response, backup operations, and post-disaster recovery.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| CP-1 | Policy and Procedures | Establish contingency planning policy |
| CP-2 | Contingency Plan | Develop and maintain a contingency plan |
| CP-3 | Contingency Training | Train personnel in contingency roles |
| CP-4 | Contingency Plan Testing | Test the contingency plan |
| CP-6 | Alternate Storage Site | Establish alternate storage site for backup |
| CP-7 | Alternate Processing Site | Establish alternate processing site |
| CP-8 | Telecommunications Services | Establish alternate telecommunications services |
| CP-9 | System Backup | Conduct backups of system-level and user-level information |
| CP-10 | System Recovery and Reconstitution | Provide for recovery and reconstitution to known state |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Contingency planning | Well-Architected Framework (Reliability) | Azure Resiliency guidance | Reliability pillar guidance |
| Backup | AWS Backup, S3 Cross-Region Replication, RDS snapshots | Azure Backup, Geo-Redundant Storage, SQL geo-replication | Cloud Storage dual-region, Cross-region replication |
| Alternate storage | S3 Cross-Region Replication | RA-GRS, GRS | Cloud Storage dual-region/multi-region |
| Alternate processing | Multi-Region deployment, Elastic Disaster Recovery | Azure Site Recovery, paired regions | Multi-region deployment, Cross-region load balancing |
| Recovery | CloudFormation, Elastic Disaster Recovery | Azure Site Recovery, ARM templates | Terraform, Deployment Manager |
| DR testing | GameDay framework, Chaos Engineering (FIS) | Azure Chaos Studio | Chaos Engineering (custom) |

### Architect Checklist

- [ ] Contingency plan is documented and covers all FedRAMP-required elements
- [ ] Contingency plan is tested at least annually (functional exercise for Moderate/High)
- [ ] RPO and RTO are defined and validated through testing
- [ ] Backups are performed according to defined schedule (at least daily for Moderate/High)
- [ ] Backups are stored at an alternate site (different region) with equivalent security controls
- [ ] Backup integrity is verified through periodic restoration testing
- [ ] Alternate processing site (secondary region) can resume operations within defined RTO
- [ ] Multi-region or cross-region architectures support failover
- [ ] Infrastructure as code enables rapid environment reconstruction
- [ ] Contingency training is provided to key personnel at least annually
- [ ] Alternate telecommunications paths exist for critical connectivity
- [ ] Recovery procedures restore the system to a known, secure state

---

## Identification and Authentication (IA)

**Purpose:** Identify and authenticate users, processes, and devices before allowing access to systems.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| IA-1 | Policy and Procedures | Establish identification and authentication policy |
| IA-2 | Identification and Authentication (Organizational Users) | Uniquely identify and authenticate organizational users |
| IA-3 | Device Identification and Authentication | Identify and authenticate devices |
| IA-4 | Identifier Management | Manage identifiers (user IDs, PIV) |
| IA-5 | Authenticator Management | Manage authenticators (passwords, tokens, PKI) |
| IA-6 | Authentication Feedback | Obscure authentication feedback |
| IA-7 | Cryptographic Module Authentication | Use FIPS-validated cryptographic modules |
| IA-8 | Identification and Authentication (Non-Organizational Users) | Identify and authenticate non-organizational users |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| User identification | IAM Users, IAM Identity Center | Entra ID | Cloud Identity, Cloud IAM |
| MFA (IA-2 enhancements) | IAM MFA (virtual, hardware, FIDO2) | Entra MFA (Authenticator, FIDO2, phone) | 2-Step Verification (Titan, FIDO2) |
| PIV/CAC authentication | IAM Identity Center + third-party IdP | Entra certificate-based auth (PIV) | Cloud Identity + third-party IdP |
| Device authentication | IoT Core (X.509), managed certificates | Entra device registration | IoT Core (X.509) |
| Identifier lifecycle | IAM user lifecycle, Identity Center SCIM | Entra Lifecycle Workflows | Cloud Identity SCIM |
| FIPS crypto modules | FIPS endpoints (--use-fips-endpoint), CloudHSM (FIPS 140-2 L3) | FIPS 140-2 validated modules | FIPS 140-2 validated (BoringCrypto) |
| Federation | SAML 2.0, OIDC via Identity Center | SAML 2.0, OIDC, WS-Fed via Entra | SAML 2.0, OIDC via Cloud Identity |

### Architect Checklist

- [ ] All users are uniquely identified (no shared accounts)
- [ ] MFA is required for all privileged access (IA-2(1))
- [ ] MFA is required for all non-privileged access (IA-2(2)) for Moderate/High
- [ ] MFA uses phishing-resistant mechanisms (FIDO2, PIV/CAC) for High baseline
- [ ] PIV/CAC authentication is supported for federal users (IA-2(12))
- [ ] Password complexity meets FedRAMP requirements (minimum 12 characters for Moderate/High per NIST 800-63B)
- [ ] Authenticator management includes secure distribution, verification, and revocation
- [ ] FIPS 140-2/140-3 validated cryptographic modules are used for authentication
- [ ] FIPS endpoints are enabled for AWS API calls (--use-fips-endpoint)
- [ ] Service accounts use managed identities or short-lived credentials
- [ ] Identifier reuse is prevented (unique IDs, no reassignment for minimum period)
- [ ] Non-organizational users (contractors, partners) are identified and authenticated with equivalent rigor

---

## Incident Response (IR)

**Purpose:** Establish and maintain an incident response capability including preparation, detection, analysis, containment, eradication, and recovery.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| IR-1 | Policy and Procedures | Establish incident response policy |
| IR-2 | Incident Response Training | Train personnel in incident response |
| IR-3 | Incident Response Testing | Test incident response capability |
| IR-4 | Incident Handling | Implement incident handling capability |
| IR-5 | Incident Monitoring | Track and document incidents |
| IR-6 | Incident Reporting | Report incidents to appropriate authorities |
| IR-7 | Incident Response Assistance | Provide incident response support resources |
| IR-8 | Incident Response Plan | Develop and maintain an incident response plan |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Detection | GuardDuty, Security Hub, CloudTrail Insights | Sentinel, Defender for Cloud, Defender XDR | Chronicle, Security Command Center |
| Investigation | Detective, CloudTrail Lake, Athena | Sentinel Investigation, Log Analytics | Chronicle Investigation, Cloud Logging |
| Automated response | EventBridge + Lambda, Security Hub auto-remediation | Sentinel Playbooks (Logic Apps), Defender automation | Cloud Functions, Chronicle SOAR |
| Forensics | EC2 snapshots, memory dumps, CloudTrail | VM snapshots, disk export, Activity Log | VM snapshots, disk export, Audit Logs |
| Incident tracking | Security Hub findings, integration with ITSM | Sentinel incidents, integration with ITSM | Chronicle cases, integration with ITSM |
| Threat intelligence | GuardDuty threat feeds, IP reputation | Sentinel TI connectors, STIX/TAXII | Chronicle Threat Intelligence |

### Architect Checklist

- [ ] Incident response plan is documented and covers FedRAMP-required elements
- [ ] Incident response plan addresses federal-specific reporting requirements (US-CERT within 1 hour for High, 1 hour for data breaches)
- [ ] Incident response team roles and responsibilities are defined
- [ ] Incident response training is provided to all personnel at least annually
- [ ] Incident response testing (tabletop or functional exercise) is conducted at least annually
- [ ] Automated threat detection is enabled across all environments (GuardDuty, Sentinel, Chronicle)
- [ ] Automated response playbooks handle common incident types (compromised credentials, malware, data exposure)
- [ ] Forensic capabilities are pre-configured (automated snapshots, log preservation, isolated analysis environment)
- [ ] Incidents are tracked from detection through resolution with documented lessons learned
- [ ] FedRAMP PMO and authorizing agency are notified per required timelines
- [ ] Evidence preservation procedures maintain chain of custody for federal investigations
- [ ] Post-incident analysis feeds into continuous improvement of security controls

---

## System and Communications Protection (SC)

**Purpose:** Monitor, control, and protect communications at system boundaries and employ architectural designs and techniques to protect system confidentiality and integrity.

### Key Controls

| Control ID | Control Name | Description |
|-----------|-------------|-------------|
| SC-1 | Policy and Procedures | Establish system and communications protection policy |
| SC-5 | Denial-of-Service Protection | Protect against or limit effects of DoS attacks |
| SC-7 | Boundary Protection | Monitor and control communications at system boundaries |
| SC-8 | Transmission Confidentiality and Integrity | Protect transmission confidentiality and integrity |
| SC-12 | Cryptographic Key Establishment and Management | Establish and manage cryptographic keys |
| SC-13 | Cryptographic Protection | Implement cryptographic mechanisms per applicable laws |
| SC-17 | Public Key Infrastructure Certificates | Issue certificates from approved PKI |
| SC-20 | Secure Name/Address Resolution Service | Provide origin authentication and integrity verification for DNS |
| SC-23 | Session Authenticity | Protect session authenticity |
| SC-28 | Protection of Information at Rest | Protect information at rest |

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| DoS protection | Shield, Shield Advanced, CloudFront | DDoS Protection (Basic, Standard) | Cloud Armor |
| Boundary protection | Network Firewall, WAF, Security Groups, NACLs | Azure Firewall, WAF, NSGs | Cloud Firewall, Cloud Armor, Firewall Rules |
| Transmission encryption | ACM, ALB/NLB/CloudFront TLS, VPN | Key Vault certs, App Gateway/Front Door TLS, VPN | Certificate Manager, LB TLS, Cloud VPN |
| Key management | KMS (FIPS 140-2 L2), CloudHSM (FIPS 140-2 L3) | Key Vault (FIPS 140-2 L2), Managed HSM (FIPS 140-2 L3) | Cloud KMS (FIPS 140-2 L2), Cloud HSM (FIPS 140-2 L3) |
| FIPS cryptography | FIPS endpoints, AWS-LC (FIPS module) | FIPS 140-2 validated modules | BoringCrypto (FIPS 140-2 validated) |
| DNS security | Route 53 DNSSEC | Azure DNS DNSSEC | Cloud DNS DNSSEC |
| Encryption at rest | KMS (CMK), EBS/S3/RDS encryption | Key Vault, Azure Disk/Storage/SQL encryption | Cloud KMS (CMEK), default encryption |
| Network segmentation | VPC, Subnets, PrivateLink | VNet, Subnets, Private Link | VPC, Subnets, VPC Service Controls |
| WAF | AWS WAF (managed + custom rules) | Azure WAF | Cloud Armor (WAF policies) |

### Architect Checklist

- [ ] FIPS 140-2/140-3 validated cryptographic modules are used for all cryptographic operations
- [ ] FIPS endpoints are enabled for all cloud API calls
- [ ] Encryption at rest uses customer-managed keys (CMK/CMEK) backed by FIPS-validated HSMs
- [ ] Encryption in transit uses TLS 1.2+ with FIPS-approved cipher suites
- [ ] DDoS protection is enabled (Shield Advanced, DDoS Protection Standard, Cloud Armor)
- [ ] Boundary protection includes firewall, IDS/IPS, WAF at all network boundaries
- [ ] Network architecture implements defense-in-depth (public, DMZ, private, data tiers)
- [ ] VPC Service Controls / PrivateLink / Private Link prevents data exfiltration
- [ ] DNSSEC is enabled for authoritative DNS zones
- [ ] Session management prevents session hijacking (secure cookies, session rotation)
- [ ] Cryptographic key management follows NIST SP 800-57 guidance
- [ ] Key rotation is automated and documented
- [ ] Certificates are issued from approved Certificate Authorities
- [ ] Managed sub-networks isolate publicly accessible components from internal components

---

## FedRAMP Authorized Cloud Services

### AWS GovCloud (US)

AWS GovCloud regions (us-gov-west-1, us-gov-east-1) are FedRAMP High authorized.

- [ ] GovCloud is used for FedRAMP High workloads
- [ ] Standard AWS regions are used only for FedRAMP Moderate (with appropriate controls)
- [ ] FIPS endpoints are enabled for all API calls
- [ ] GovCloud-specific service availability is verified before architecture design

### Azure Government

Azure Government regions are FedRAMP High authorized. Azure DoD regions provide IL4/IL5.

- [ ] Azure Government is used for FedRAMP High workloads
- [ ] Azure Government service availability is verified (not all commercial services are available)
- [ ] Azure Government URLs (.us suffix) are used in all configurations
- [ ] Azure Government is used for DoD workloads requiring IL4/IL5

### Google Cloud (FedRAMP)

GCP has FedRAMP High authorization for select services. Assured Workloads provides compliance guardrails.

- [ ] Assured Workloads is configured for FedRAMP workloads
- [ ] FedRAMP-authorized GCP services are verified on the FedRAMP Marketplace
- [ ] Assured Workloads enforces data residency and access controls
- [ ] Organization Policy constraints align with FedRAMP requirements

---

## Continuous Monitoring (ConMon) Requirements

FedRAMP requires ongoing monitoring activities after authorization:

### Monthly Requirements

- [ ] Vulnerability scans (OS, database, web application) are performed monthly
- [ ] Scan results are submitted to the FedRAMP PMO or authorizing agency
- [ ] POA&M is updated with new findings and remediation progress
- [ ] Unique vulnerability count and remediation statistics are reported

### Quarterly Requirements

- [ ] Quarterly POA&M deliverable is submitted
- [ ] Deviation requests are submitted for any overdue POA&M items

### Annual Requirements

- [ ] Annual security assessment by a 3PAO (Third-Party Assessment Organization)
- [ ] Penetration testing is conducted by the 3PAO
- [ ] Security Authorization Package (SAP, SAR, POA&M) is updated
- [ ] Contingency plan is tested
- [ ] Incident response plan is tested
- [ ] Security awareness training is completed by all personnel

### Significant Change Process

- [ ] Significant changes are identified per FedRAMP guidance (new services, architecture changes, data flow changes)
- [ ] Significant Change Request is submitted to authorizing agency before implementation
- [ ] Security impact analysis is performed for all significant changes
- [ ] 3PAO assessment may be required for significant changes

---

## Cross-Cutting FedRAMP Requirements

### FIPS 140-2/140-3 Compliance

FIPS-validated cryptography is mandatory for FedRAMP at all impact levels.

- [ ] All cryptographic modules are FIPS 140-2 or 140-3 validated
- [ ] Cloud provider FIPS validation certificates are documented (CMVP certificate numbers)
- [ ] FIPS endpoints are used for all API calls to cloud providers
- [ ] TLS configurations use only FIPS-approved algorithms
- [ ] HSMs used for key management are FIPS 140-2 Level 3 or higher

### Data Residency

Federal data must remain within the United States (including territories) unless explicitly authorized.

- [ ] All data storage is configured in US regions only
- [ ] Replication does not cross US borders
- [ ] CDN edge locations are restricted to US territories where required
- [ ] Data residency constraints are enforced via Organization Policy / SCPs / Azure Policy

### Personnel Security

- [ ] All personnel with access to federal data have completed background investigations
- [ ] Personnel screening requirements are met for the system's impact level
- [ ] Access is revoked within 24 hours of personnel termination
- [ ] Contractor and third-party personnel meet equivalent screening requirements

### Supply Chain Risk Management (SR)

NIST 800-53 Rev. 5 added supply chain controls, relevant for FedRAMP.

- [ ] Supply chain risk management plan is documented
- [ ] Third-party components and services are assessed for supply chain risk
- [ ] Software Bill of Materials (SBOM) is maintained for custom applications
- [ ] Provenance of software artifacts is verified (signed images, verified sources)
- [ ] Acquisition strategies include security requirements
