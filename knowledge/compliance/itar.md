# ITAR - Cloud Control Mapping

## Scope

Covers International Traffic in Arms Regulations (ITAR) requirements for cloud and infrastructure environments handling defense articles and technical data, including data sovereignty, US-person-only access, encryption, cloud provider compliance (GovCloud requirements), physical security, audit logging, and export control. Does not cover FedRAMP authorization process (see `compliance/fedramp.md`) or general security architecture (see `general/security.md`).

## Overview

The **International Traffic in Arms Regulations (ITAR)**, administered by the U.S. Department of State Directorate of Defense Trade Controls (DDTC), controls the export and temporary import of defense articles and defense services listed on the United States Munitions List (USML). ITAR requires that access to controlled technical data be restricted to **U.S. persons** (U.S. citizens, permanent residents, or protected individuals) unless a license or exemption is obtained.

**Applicability:** Defense contractors, subcontractors, manufacturers, and any organization that stores, processes, or transmits ITAR-controlled technical data or defense articles. This includes engineering firms, research institutions, and cloud service providers hosting ITAR workloads. ITAR obligations flow down through the entire supply chain.

**Key Sections:**
- **ITAR Part 120:** Purpose, definitions, and general provisions (defines defense articles, technical data, U.S. person)
- **ITAR Part 121:** The United States Munitions List (USML) — 21 categories of defense articles
- **ITAR Part 122:** Registration requirements for manufacturers and exporters
- **ITAR Part 123:** Licenses for export of defense articles
- **ITAR Part 124:** Agreements for technical data and defense services
- **ITAR Part 125:** Licenses for export of technical data and classified defense articles
- **ITAR Part 126:** General policies and provisions (country restrictions, prohibited exports)
- **ITAR Part 127:** Violations and penalties

**ITAR in the Cloud:** Storing ITAR data in the cloud constitutes an export if the data could be accessed by non-U.S. persons. Cloud environments must ensure that all physical infrastructure is located in the United States, all personnel (cloud provider and customer) with access to unencrypted ITAR data are U.S. persons, and technical data remains within U.S. borders at all times. AWS GovCloud, Azure Government, and Google Cloud Assured Workloads offer ITAR-eligible environments with U.S.-person-only operations staff and U.S.-only data centers.

---

## Checklist

- [ ] **[Critical]** Is all ITAR-controlled technical data stored exclusively on infrastructure physically located in the United States?
- [ ] **[Critical]** Is access to unencrypted ITAR data restricted to verified U.S. persons only? (U.S. citizens, lawful permanent residents, protected individuals)
- [ ] **[Critical]** Is the cloud environment ITAR-eligible? (AWS GovCloud, Azure Government, or equivalent with U.S.-person-only operations)
- [ ] **[Critical]** Is ITAR data encrypted at rest using FIPS 140-2/140-3 validated modules with customer-managed keys?
- [ ] **[Critical]** Is ITAR data encrypted in transit using TLS 1.2+ with FIPS-approved cipher suites?
- [ ] **[Critical]** Are access controls enforced to prevent any non-U.S.-person access to unencrypted ITAR data? (includes cloud provider support, operations, and administrative personnel)
- [ ] **[Critical]** Is there a documented ITAR Technology Control Plan (TCP) governing handling, storage, and access to controlled technical data?
- [ ] **[Recommended]** Are audit logs maintained for all access to ITAR-controlled data? (who, what, when, where, outcome)
- [ ] **[Recommended]** Are data flows mapped to ensure ITAR data does not traverse non-U.S. infrastructure? (including CDN edge nodes, DNS, backups)
- [ ] **[Critical]** Is the organization registered with DDTC as required under ITAR Part 122?
- [ ] **[Critical]** Are all required export licenses obtained before sharing ITAR data with foreign persons or entities?
- [ ] **[Recommended]** Is personnel citizenship/residency status verified and documented before granting access to ITAR data?
- [ ] **[Recommended]** Are subcontractors and third-party vendors assessed for ITAR compliance before granting access?
- [ ] **[Recommended]** Is there an incident response plan that addresses unauthorized disclosure of ITAR data to non-U.S. persons?

## Why This Matters

ITAR violations carry **severe criminal and civil penalties**:

- **Criminal penalties:** Up to $1 million per violation and up to 20 years imprisonment for willful violations
- **Civil penalties:** Up to $1,213,423 per violation (adjusted for inflation; ITAR Part 127)
- **Debarment:** Individuals and organizations can be barred from future defense contracts and export privileges
- **Loss of export privileges:** DDTC can revoke or suspend export licenses
- **Consent agreements:** Formal agreements requiring remediation, compliance monitoring, and often substantial fines (recent settlements have exceeded $100M)

ITAR enforcement is strict. An **unauthorized export** occurs any time ITAR-controlled technical data is disclosed to a non-U.S. person, even if the disclosure happens within the United States (a "deemed export"). Cloud misconfigurations that allow non-U.S.-person access to ITAR data constitute violations regardless of intent. The Department of State considers companies responsible for ensuring their cloud architectures prevent unauthorized access.

---

## Data Sovereignty and US-Person Access

### Control Objectives

Ensure all ITAR-controlled data remains within U.S. borders and is accessible only by verified U.S. persons.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| US-only infrastructure | GovCloud (us-gov-west-1, us-gov-east-1) | Azure Government (US Gov Virginia, US Gov Arizona, US Gov Texas) | Assured Workloads (US regions with ITAR controls) |
| US-person-only operations | GovCloud (US-person-screened staff) | Azure Government (screened US citizens) | Assured Workloads (Access Transparency, personnel controls) |
| Data residency enforcement | SCPs restricting regions, S3 bucket policies | Azure Policy (allowed locations) | Organization Policy (resource location constraint) |
| Data replication controls | S3 replication restricted to GovCloud regions | Geo-redundant storage within US Gov regions | Cloud Storage restricted to US regions |
| Network path controls | GovCloud VPC (isolated from commercial) | Azure Government (isolated from commercial) | VPC Service Controls (perimeter enforcement) |

### Architect Checklist

- [ ] **[Critical]** All compute, storage, and networking resources are deployed in ITAR-eligible US regions only
- [ ] **[Critical]** Service Control Policies (SCPs), Azure Policy, or Organization Policy constraints prevent resource creation outside approved US regions
- [ ] **[Critical]** Data replication and backup targets are restricted to US-only locations
- [ ] **[Critical]** CDN, DNS, and edge services do not cache or process ITAR data outside the United States
- [ ] **[Recommended]** Cloud provider's ITAR eligibility documentation is reviewed and current
- [ ] **[Critical]** Cloud provider support access is restricted to US-person-only support channels (GovCloud support, Azure Government support)
- [ ] **[Recommended]** All APIs use region-specific endpoints that resolve to US infrastructure
- [ ] **[Critical]** VPN and direct connect paths do not route through non-US points of presence

---

## Encryption and Key Management

### Control Objectives

Encrypt ITAR data at rest and in transit using FIPS-validated cryptographic modules, with keys under customer control to prevent unauthorized access by cloud provider personnel.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Encryption at rest | KMS (CMK, FIPS 140-2 L2), CloudHSM (L3) | Key Vault (FIPS 140-2 L2), Managed HSM (L3) | Cloud KMS (FIPS 140-2 L2), Cloud HSM (L3) |
| Encryption in transit | TLS 1.2+ (FIPS endpoints), VPN (IPsec AES-256) | TLS 1.2+ (FIPS modules), VPN (IPsec AES-256) | TLS 1.2+ (BoringCrypto FIPS), VPN (IPsec AES-256) |
| Customer-managed keys | KMS CMK with key policy, CloudHSM | Key Vault BYOK, Managed HSM | Cloud KMS CMEK, Cloud EKM, Cloud HSM |
| External key management | CloudHSM, External Key Store (XKS) | Managed HSM, Azure Key Vault Managed HSM | Cloud EKM (External Key Manager) |
| Key access auditing | CloudTrail KMS events | Key Vault diagnostic logs | Cloud KMS audit logs |

### Architect Checklist

- [ ] **[Critical]** All ITAR data at rest is encrypted using customer-managed keys (CMK/CMEK) backed by FIPS 140-2/140-3 validated modules
- [ ] **[Critical]** Encryption in transit uses TLS 1.2+ with FIPS-approved cipher suites
- [ ] **[Critical]** FIPS endpoints are enabled for all cloud API calls
- [ ] **[Recommended]** CloudHSM, Managed HSM, or Cloud HSM (FIPS 140-2 Level 3) is used for the most sensitive ITAR key material
- [ ] **[Recommended]** External Key Store (XKS) or Cloud EKM is evaluated for keys that must remain outside the cloud provider's infrastructure
- [ ] **[Recommended]** Automatic key rotation is enabled (annually at minimum)
- [ ] **[Critical]** Key access is logged and monitored — alerts fire on unauthorized key usage attempts
- [ ] **[Recommended]** Key management procedures are documented, including generation, rotation, revocation, and destruction

---

## Access Control

### Control Objectives

Enforce US-person-only access to ITAR data through identity management, access controls, and personnel verification.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Identity management | IAM Identity Center, GovCloud IAM | Entra ID (Azure Government tenant) | Cloud Identity (Assured Workloads) |
| Role-based access | IAM Roles, permission boundaries | Entra RBAC, Conditional Access | Cloud IAM Roles, IAM Conditions |
| Privileged access | SSO with elevated permission sets | PIM (just-in-time elevation) | Time-bound IAM bindings |
| MFA | IAM MFA (hardware tokens, FIDO2) | Entra MFA (phishing-resistant) | 2-Step Verification (Titan keys) |
| Access reviews | IAM Access Analyzer | Entra Access Reviews | IAM Recommender |
| Conditional access | IAM conditions (IP, time) | Conditional Access (location, device, risk) | Context-aware access, BeyondCorp |

### Architect Checklist

- [ ] **[Critical]** All users with access to ITAR data are verified U.S. persons with documented citizenship/residency status
- [ ] **[Critical]** Access to ITAR data requires multi-factor authentication
- [ ] **[Critical]** Role-based access controls enforce least privilege — only personnel with a need to know can access ITAR data
- [ ] **[Recommended]** Access reviews are conducted at least quarterly to verify continued need-to-know and US-person status
- [ ] **[Recommended]** Privileged access uses just-in-time elevation with approval workflows and audit logging
- [ ] **[Critical]** Conditional access policies restrict ITAR data access to approved locations and devices
- [ ] **[Recommended]** Service accounts accessing ITAR data use short-lived credentials and are restricted to specific workloads
- [ ] **[Critical]** Third-party and contractor access is restricted to verified U.S. persons under appropriate agreements (TAAs, subcontracts with ITAR flow-down)
- [ ] **[Recommended]** Break-glass access procedures exist with enhanced logging and mandatory review

---

## Audit Logging and Monitoring

### Control Objectives

Maintain comprehensive audit trails for all access to ITAR-controlled data to support compliance verification and incident investigation.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| API logging | CloudTrail (all regions, all events) | Activity Log, Diagnostic Logs | Cloud Audit Logs |
| Data access logging | S3 access logs, CloudTrail data events | Storage analytics, diagnostic logs | Data Access audit logs |
| Log protection | S3 Object Lock, CloudTrail integrity validation | Immutable Blob Storage | Locked retention policies |
| SIEM / analysis | Security Hub, CloudTrail Lake, Athena | Sentinel, Log Analytics | Chronicle, BigQuery |
| Alerting | CloudWatch Alarms, EventBridge | Azure Monitor, Sentinel alerts | Cloud Monitoring, Chronicle alerts |
| Access transparency | N/A (GovCloud US-person operations) | Customer Lockbox (Azure Government) | Access Transparency, Access Approval |

### Architect Checklist

- [ ] **[Critical]** All access to ITAR data is logged with: user identity, action, resource, timestamp, source IP, and outcome
- [ ] **[Critical]** Audit logs are stored in immutable storage (Object Lock, immutable blobs, locked retention)
- [ ] **[Recommended]** Audit log retention is minimum 5 years (aligned with ITAR record-keeping requirements under Part 122.5)
- [ ] **[Recommended]** Automated alerts fire on: access from unexpected locations, non-US IP addresses, failed access attempts, bulk data exports
- [ ] **[Recommended]** Cloud provider access transparency logs are reviewed (Access Transparency, Customer Lockbox)
- [ ] **[Recommended]** SIEM aggregates logs from all ITAR-hosting environments for centralized analysis
- [ ] **[Critical]** Log access is restricted to authorized US-person security personnel

---

## Physical Security

### Control Objectives

Ensure physical infrastructure hosting ITAR data is located in the United States with appropriate physical access controls.

### Architect Checklist

- [ ] **[Critical]** All data centers hosting ITAR data are physically located in the United States
- [ ] **[Recommended]** Cloud provider data center physical security certifications are verified (SOC 2 Type II, FedRAMP)
- [ ] **[Recommended]** On-premises facilities housing ITAR data have access controls, surveillance, and visitor logging
- [ ] **[Recommended]** Physical access to ITAR systems is restricted to verified U.S. persons
- [ ] **[Recommended]** Visitor access to areas containing ITAR data requires escort by cleared U.S. persons
- [ ] **[Recommended]** Physical security controls are documented in the Technology Control Plan (TCP)

---

## Technology Control Plan (TCP)

### Purpose

A TCP is a documented plan that describes how an organization physically and logically protects ITAR-controlled technical data from unauthorized access, particularly by non-U.S. persons.

### TCP Requirements

| Element | Description |
|---------|-------------|
| **Scope** | Identifies all ITAR programs, data, and systems covered |
| **Physical controls** | Describes facility access restrictions, secure areas, visitor policies |
| **IT controls** | Documents network segmentation, encryption, access controls, monitoring |
| **Personnel controls** | Defines US-person verification process, access authorization, training |
| **Incident procedures** | Outlines response process for unauthorized access or disclosure |
| **Audit and review** | Describes periodic review schedule and compliance verification |

### Architect Checklist

- [ ] **[Critical]** A Technology Control Plan exists and covers all cloud infrastructure hosting ITAR data
- [ ] **[Recommended]** TCP is reviewed and updated at least annually or when significant changes occur
- [ ] **[Recommended]** TCP addresses cloud-specific controls: region restrictions, provider personnel screening, encryption architecture
- [ ] **[Recommended]** TCP is communicated to all personnel with ITAR data access
- [ ] **[Recommended]** TCP compliance is verified through periodic self-assessments

---

## ITAR-Eligible Cloud Environments

### AWS GovCloud (US)

AWS GovCloud is designed for ITAR workloads. Operated by U.S. persons on U.S. soil.

- [ ] **[Critical]** GovCloud (us-gov-west-1 or us-gov-east-1) is used for all ITAR workloads
- [ ] **[Critical]** FIPS endpoints are enabled for all API calls
- [ ] **[Recommended]** GovCloud account is isolated from commercial AWS accounts (separate root account)
- [ ] **[Recommended]** GovCloud service availability is verified before architecture design (not all commercial services are available)
- [ ] **[Recommended]** SCPs prevent accidental resource creation in commercial regions

### Azure Government

Azure Government supports ITAR compliance with US-person-only screened operations staff.

- [ ] **[Critical]** Azure Government regions are used for all ITAR workloads
- [ ] **[Recommended]** Azure Government tenant is separate from commercial Azure tenants
- [ ] **[Recommended]** Azure Government URLs (.us suffix) are used in all configurations and code
- [ ] **[Recommended]** Azure Policy enforces allowed locations to Azure Government regions only
- [ ] **[Recommended]** Customer Lockbox is enabled for controlled support access

### Google Cloud

Google Cloud supports ITAR workloads through Assured Workloads with ITAR control package.

- [ ] **[Recommended]** Assured Workloads is configured with the ITAR control package
- [ ] **[Recommended]** ITAR-eligible services and regions are verified
- [ ] **[Critical]** CMEK with Cloud HSM is used for all encryption
- [ ] **[Recommended]** Access Transparency and Access Approval are enabled
- [ ] **[Recommended]** Organization Policy constraints enforce data residency and service restrictions

---

## Common Decisions (ADR Triggers)

- **Cloud environment selection** — AWS GovCloud vs Azure Government vs Google Assured Workloads, cost and service availability tradeoffs
- **Encryption and key management architecture** — KMS vs CloudHSM vs External Key Store, FIPS 140-2 Level 2 vs Level 3, customer-held keys to prevent provider access
- **US-person verification process** — how citizenship/residency is verified, how often re-verified, who maintains records
- **Network architecture for data sovereignty** — VPN design, direct connect paths, ensuring no non-US transit, CDN and DNS considerations
- **Multi-cloud or hybrid strategy** — ITAR constraints on data movement between environments, interconnection design
- **Third-party and subcontractor access model** — ITAR flow-down in contracts, Technical Assistance Agreements (TAAs), access control enforcement
- **Technology Control Plan scope** — cloud-only vs hybrid, single program vs enterprise TCP
- **Audit and monitoring architecture** — SIEM selection, log retention (5+ years), alerting for non-US access attempts
- **Incident response for unauthorized disclosure** — DDTC voluntary disclosure process, internal investigation procedures

## Reference Links

- [ITAR (22 CFR Parts 120-130)](https://www.ecfr.gov/current/title-22/chapter-I/subchapter-M) — full text of the International Traffic in Arms Regulations
- [DDTC](https://www.pmddtc.state.gov/) — Directorate of Defense Trade Controls, the ITAR administering authority
- [United States Munitions List](https://www.ecfr.gov/current/title-22/chapter-I/subchapter-M/part-121) — USML categories defining controlled defense articles
- [AWS GovCloud ITAR](https://aws.amazon.com/compliance/itar/) — AWS ITAR compliance information
- [Azure Government ITAR](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-itar) — Azure ITAR compliance information
- [NIST SP 800-53 Rev 5](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final) — security controls commonly mapped to ITAR infrastructure requirements

## See Also

- `compliance/fedramp.md` — FedRAMP authorization (GovCloud environments typically carry FedRAMP High authorization)
- `compliance/nist-800-171-cmmc.md` — NIST 800-171 and CMMC (frequently co-required with ITAR for DoD contracts)
- `general/security.md` — General security controls and architecture patterns
- `general/identity.md` — IAM and authentication architecture
- `general/governance.md` — Cloud governance, tagging, and policy enforcement
