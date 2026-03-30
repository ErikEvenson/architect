# CJIS Security Policy - Cloud Control Mapping

## Scope

Covers CJIS Security Policy requirements for cloud and infrastructure environments handling Criminal Justice Information (CJI), including advanced authentication, FIPS 140-2/140-3 encryption, personnel security screening, audit logging, access control, media protection, physical protection, and network security. Does not cover general security architecture (see `general/security.md`) or FedRAMP authorization process (see `compliance/fedramp.md`).

## Overview

The **CJIS Security Policy** (currently v5.9.5) is published by the FBI's Criminal Justice Information Services Division and establishes the minimum security requirements for access to FBI CJIS systems and data. It applies to every individual — law enforcement, private contractors, cloud providers, and IT personnel — who has access to, or operates in support of, Criminal Justice Information (CJI).

**Applicability:** Any organization that accesses, stores, processes, or transmits CJI. This includes law enforcement agencies, courts, corrections departments, prosecutors, IT contractors providing services to those agencies, and cloud service providers hosting CJI workloads. CJIS compliance flows down through all subcontractors and third parties.

**Key Sections:**
- **Policy Area 1:** Information Exchange Agreements — formal agreements required before sharing CJI
- **Policy Area 2:** Security Awareness Training — all personnel with CJI access must complete training within 6 months, then biennially
- **Policy Area 3:** Incident Response — capability to detect, report, and respond to security incidents
- **Policy Area 4:** Auditing and Accountability — logging of all access to CJI systems
- **Policy Area 5:** Access Control — role-based access, least privilege, and account management
- **Policy Area 6:** Identification and Authentication — advanced authentication (multi-factor) for all CJI access
- **Policy Area 7:** Configuration Management — hardened configurations and change control
- **Policy Area 8:** Media Protection — encryption and handling of media containing CJI
- **Policy Area 9:** Physical Protection — physical security of facilities housing CJI systems
- **Policy Area 10:** Systems and Communications Protection — encryption in transit and at rest, boundary protection
- **Policy Area 11:** Formal Audits — triennial audits by the FBI CJIS Division or state CSA
- **Policy Area 12:** Personnel Security — fingerprint-based background checks for all individuals with access to CJI
- **Policy Area 13:** Mobile Devices — additional controls for mobile access to CJI

**CJIS in the Cloud:** Cloud service providers hosting CJI must sign a CJIS Security Addendum and meet all CJIS Security Policy requirements. The cloud provider's personnel who can access unencrypted CJI must undergo fingerprint-based background checks. Major cloud providers (AWS GovCloud, Azure Government, Google Cloud) offer CJIS-compliant environments, but the customer retains responsibility for configuring access controls, encryption, and personnel screening.

---

## Checklist

- [ ] **[Critical]** Is a CJIS Security Addendum signed with every entity that accesses, stores, or transmits CJI? (cloud providers, contractors, subcontractors)
- [ ] **[Critical]** Is advanced authentication (multi-factor) required for all users accessing CJI? (something you know + something you have/are)
- [ ] **[Critical]** Are all cryptographic modules FIPS 140-2 or FIPS 140-3 validated? (encryption at rest and in transit)
- [ ] **[Critical]** Have all personnel with access to unencrypted CJI completed fingerprint-based background checks? (state and national)
- [ ] **[Critical]** Is CJI encrypted at rest using AES 256-bit (or equivalent FIPS-validated) encryption?
- [ ] **[Critical]** Is CJI encrypted in transit using TLS 1.2+ with FIPS-approved cipher suites?
- [ ] **[Critical]** Are audit logs maintained for all access to CJI systems? (who, what, when, where, outcome)
- [ ] **[Critical]** Is audit log retention set to minimum 1 year?
- [ ] **[Recommended]** Are session timeouts enforced at 30 minutes of inactivity?
- [ ] **[Critical]** Are unsuccessful login attempts limited and accounts locked after a maximum of 5 consecutive failures?
- [ ] **[Recommended]** Is security awareness training completed within 6 months of access and biennially thereafter?
- [ ] **[Critical]** Are mobile devices accessing CJI encrypted and remotely wipeable?
- [ ] **[Recommended]** Is a formal incident response plan documented and tested annually?
- [ ] **[Recommended]** Are media containing CJI sanitized or destroyed using NIST SP 800-88 guidelines before disposal?
- [ ] **[Critical]** Is the cloud environment physically located within the United States?
- [ ] **[Recommended]** Are triennial CJIS audit findings tracked and remediated?

## Why This Matters

CJIS non-compliance can result in **immediate termination of access** to FBI CJIS systems (NCIC, III, NICS, and state criminal justice databases), effectively shutting down an agency's ability to run background checks, access warrant information, or query criminal history records. Consequences include:

- **Loss of CJIS access** — the FBI or state CJIS Systems Agency (CSA) can suspend access for non-compliant agencies or their contractors
- **Contract termination** — IT vendors and cloud providers lose contracts with law enforcement agencies
- **Criminal liability** — unauthorized access to or disclosure of CJI can result in federal and state criminal charges
- **Public safety impact** — inability to query criminal databases directly affects officer safety and public protection

CJIS audits are conducted triennially by the FBI CJIS Audit Unit or delegated to the state CSA. Audit findings require remediation plans with defined timelines. Repeated non-compliance can escalate to permanent access revocation.

---

## Policy Area 4: Auditing and Accountability

### Control Objectives

Generate, protect, and retain audit records for all CJI system events to support detection, investigation, and reporting of unauthorized activity.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Event logging | CloudTrail (management + data events) | Activity Log, Diagnostic Logs | Cloud Audit Logs (Admin + Data Access) |
| Log storage | S3 with Object Lock, CloudWatch Logs | Immutable Blob Storage, Log Analytics | Cloud Logging with locked retention |
| Log analysis | CloudTrail Lake, Athena, OpenSearch | Log Analytics (KQL), Sentinel | Cloud Logging queries, Chronicle |
| Alerting | CloudWatch Alarms, EventBridge | Azure Monitor Alerts, Sentinel | Cloud Monitoring Alerts |
| Time synchronization | Amazon Time Sync Service | Azure NTP | Google NTP |
| SIEM integration | Security Hub, third-party SIEM | Sentinel | Chronicle |

### Architect Checklist

- [ ] **[Critical]** Audit logs capture: user ID, event type, date/time, success/failure, affected data/component
- [ ] **[Critical]** Audit logs are protected from unauthorized modification (immutable storage, Object Lock)
- [ ] **[Critical]** Audit log retention is minimum 1 year (365 days)
- [ ] **[Recommended]** Audit logs are reviewed at minimum weekly for anomalies
- [ ] **[Recommended]** Automated alerts fire on suspicious access patterns (failed logins, off-hours access, privilege escalation)
- [ ] **[Critical]** Time synchronization uses authoritative NTP sources
- [ ] **[Recommended]** Centralized log aggregation across all CJI-hosting accounts/subscriptions/projects

---

## Policy Area 5: Access Control

### Control Objectives

Ensure only authorized individuals access CJI, with least privilege and role-based access controls.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Role-based access | IAM Roles, IAM Identity Center | Entra ID RBAC, PIM | Cloud IAM Roles |
| Least privilege | IAM Access Analyzer, permission boundaries | Entra Access Reviews, PIM | IAM Recommender, Policy Analyzer |
| Account management | IAM Identity Center lifecycle, Organizations | Entra Lifecycle Workflows | Cloud Identity lifecycle |
| Privileged access | SSO with elevated permission sets | PIM (just-in-time elevation) | Time-bound IAM bindings |
| Session management | STS session policies, console timeout | Conditional Access session controls | Session controls |

### Architect Checklist

- [ ] **[Critical]** Access to CJI is role-based and follows least privilege
- [ ] **[Critical]** Account provisioning requires documented approval from an authorized official
- [ ] **[Critical]** Accounts are disabled within 24 hours of personnel termination or role change
- [ ] **[Recommended]** Access is reviewed at least annually and recertified
- [ ] **[Critical]** Session lock activates after no more than 30 minutes of inactivity
- [ ] **[Critical]** Account lockout occurs after no more than 5 consecutive failed login attempts
- [ ] **[Recommended]** Privileged accounts use just-in-time elevation with approval workflows
- [ ] **[Recommended]** Shared accounts are prohibited; all access is individually attributable
- [ ] **[Critical]** Remote access to CJI requires VPN or equivalent encrypted tunnel with advanced authentication

---

## Policy Area 6: Identification and Authentication

### Control Objectives

Uniquely identify and authenticate all users before granting access to CJI, using advanced authentication (multi-factor) at the point of access.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| MFA / advanced authentication | IAM MFA (TOTP, FIDO2, hardware tokens) | Entra MFA (Authenticator, FIDO2, phone) | 2-Step Verification (Titan, FIDO2) |
| Identifier management | IAM Identity Center, unique user IDs | Entra ID, unique UPNs | Cloud Identity, unique accounts |
| Password management | IAM password policy (min 8 chars, complexity) | Entra ID password policies | Google Workspace password policies |
| Federation | SAML 2.0, OIDC via Identity Center | SAML 2.0, OIDC via Entra | SAML 2.0, OIDC via Cloud Identity |
| Certificate-based auth | Certificate-based mutual TLS | Entra certificate-based auth | Certificate-based auth |

### Architect Checklist

- [ ] **[Critical]** Advanced authentication (multi-factor) is required for ALL access to CJI — no exceptions
- [ ] **[Critical]** Advanced authentication is enforced at the point of CJI access (not just at network perimeter)
- [ ] **[Recommended]** MFA mechanisms include something you know (password/PIN) plus something you have (token/phone) or something you are (biometric)
- [ ] **[Critical]** Passwords meet CJIS minimum requirements: 8 characters minimum, complexity enforced
- [ ] **[Critical]** Passwords are changed at maximum every 90 calendar days
- [ ] **[Recommended]** All users have unique identifiers — no shared or generic accounts
- [ ] **[Recommended]** Service accounts are managed with equivalent rigor (short-lived credentials, no shared secrets)
- [ ] **[Critical]** Authentication feedback does not reveal whether username or password was incorrect

---

## Policy Area 8: Media Protection

### Control Objectives

Protect CJI stored on digital and physical media through encryption, access controls, and secure disposal.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Encryption at rest | KMS (CMK, FIPS 140-2 L2), CloudHSM (L3) | Key Vault (FIPS 140-2 L2), Managed HSM (L3) | Cloud KMS (FIPS 140-2 L2), Cloud HSM (L3) |
| Key management | KMS key rotation, key policies | Key Vault rotation, access policies | Cloud KMS rotation, IAM policies |
| Storage encryption | S3 SSE-KMS, EBS encryption | Storage Service Encryption, Disk Encryption | Default encryption, CMEK |
| Database encryption | RDS encryption, Aurora encryption | Azure SQL TDE, Cosmos DB encryption | Cloud SQL encryption, Spanner encryption |
| Media sanitization | EBS volume deletion (crypto-erase) | Disk deletion (crypto-erase) | Persistent disk deletion (crypto-erase) |

### Architect Checklist

- [ ] **[Critical]** All CJI at rest is encrypted using AES 256-bit (or equivalent) with FIPS-validated modules
- [ ] **[Critical]** Customer-managed keys (CMK/CMEK) are used for CJI encryption
- [ ] **[Critical]** Key management follows NIST SP 800-57 guidance (generation, distribution, rotation, destruction)
- [ ] **[Recommended]** Automatic key rotation is enabled (annually at minimum)
- [ ] **[Recommended]** Media containing CJI is sanitized per NIST SP 800-88 before disposal or reuse
- [ ] **[Recommended]** Encryption keys are stored separately from encrypted data
- [ ] **[Critical]** Backup media containing CJI receives the same encryption and access controls as primary storage

---

## Policy Area 10: Systems and Communications Protection

### Control Objectives

Protect CJI during transmission and at system boundaries through encryption, network segmentation, and boundary protection.

### Cloud Service Mapping

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Encryption in transit | ALB/NLB TLS 1.2+, VPN (IPsec) | App Gateway/Front Door TLS 1.2+, VPN | Load Balancer TLS 1.2+, Cloud VPN |
| Boundary protection | Network Firewall, WAF, Security Groups | Azure Firewall, WAF, NSGs | Cloud Firewall, Cloud Armor |
| Network segmentation | VPC, Subnets, PrivateLink | VNet, Subnets, Private Link | VPC, Subnets, VPC Service Controls |
| DDoS protection | Shield, Shield Advanced | DDoS Protection | Cloud Armor |
| Intrusion detection | GuardDuty, Network Firewall IPS | Defender for Cloud, Azure Firewall Premium | Chronicle, Cloud IDS |
| FIPS endpoints | FIPS endpoints (--use-fips-endpoint) | FIPS 140-2 validated modules | BoringCrypto (FIPS validated) |

### Architect Checklist

- [ ] **[Critical]** All CJI in transit is encrypted using TLS 1.2 or higher with FIPS-approved cipher suites
- [ ] **[Critical]** FIPS 140-2/140-3 validated cryptographic modules are used for all encryption operations
- [ ] **[Critical]** FIPS endpoints are enabled for all cloud provider API calls
- [ ] **[Critical]** CJI systems are segmented from non-CJI systems at the network level (dedicated VPC/VNet)
- [ ] **[Recommended]** Boundary protection includes firewall, IDS/IPS at network boundaries
- [ ] **[Recommended]** VPN connections use FIPS-validated encryption (AES 256, IKEv2)
- [ ] **[Recommended]** Public-facing applications are protected by WAF
- [ ] **[Recommended]** Network architecture diagram documents all CJI data flows and boundary controls
- [ ] **[Critical]** Wireless networks accessing CJI use FIPS-validated encryption (WPA2-Enterprise minimum with AES)
- [ ] **[Recommended]** DDoS protection is enabled for internet-facing CJI services

---

## Policy Area 12: Personnel Security

### Control Objectives

Ensure all individuals with access to unencrypted CJI have undergone appropriate background screening.

### Requirements

| Requirement | Description |
|-------------|-------------|
| **Fingerprint-based background check** | State and national fingerprint-based record check required before access to unencrypted CJI |
| **Screening for cloud personnel** | Cloud provider staff with logical or physical access to unencrypted CJI must be screened |
| **Security Addendum** | All personnel must sign the CJIS Security Addendum acknowledging responsibilities |
| **Ongoing screening** | Personnel must be re-screened when new information warrants or per agency policy |
| **Contractor and vendor staff** | Third-party personnel (managed service providers, subcontractors) are subject to the same screening |

### Architect Checklist

- [ ] **[Critical]** All personnel with access to unencrypted CJI have completed fingerprint-based background checks (state and national)
- [ ] **[Critical]** CJIS Security Addendum is signed by all personnel and entities with CJI access
- [ ] **[Recommended]** Cloud provider's CJIS compliance documentation is reviewed and current (verify provider offers CJIS-eligible services)
- [ ] **[Critical]** Cloud provider personnel who could access unencrypted CJI are screened or access is architecturally prevented (encryption with customer-held keys)
- [ ] **[Recommended]** Personnel screening status is tracked and access is revoked if screening fails or expires
- [ ] **[Recommended]** Visitor access to areas containing CJI systems requires escort and logging

---

## Policy Area 13: Mobile Devices

### Control Objectives

Apply additional security controls to mobile devices that access CJI.

### Architect Checklist

- [ ] **[Critical]** Mobile devices accessing CJI have full-device encryption enabled
- [ ] **[Critical]** Mobile devices are enrolled in a Mobile Device Management (MDM) solution
- [ ] **[Critical]** Remote wipe capability is available for lost or stolen devices
- [ ] **[Recommended]** Mobile applications accessing CJI use containerization to isolate CJI data
- [ ] **[Recommended]** Mobile devices enforce screen lock after no more than 5 minutes of inactivity
- [ ] **[Recommended]** Mobile device connections to CJI systems use VPN with advanced authentication

---

## CJIS-Compliant Cloud Services

### AWS GovCloud (US)

AWS GovCloud supports CJIS workloads. AWS has signed CJIS Security Addendums with multiple states.

- [ ] **[Recommended]** GovCloud is used for CJIS workloads (provides US-only data residency, screened personnel)
- [ ] **[Critical]** FIPS endpoints are enabled for all API calls
- [ ] **[Recommended]** CloudHSM or KMS with FIPS-validated modules is used for key management
- [ ] **[Recommended]** AWS CJIS Security Addendum status is confirmed with the relevant state CSA

### Azure Government

Azure Government supports CJIS compliance. Microsoft has CJIS Security Addendums with most U.S. states.

- [ ] **[Recommended]** Azure Government is used for CJIS workloads
- [ ] **[Recommended]** Azure Government URLs (.us suffix) are used in all configurations
- [ ] **[Recommended]** Key Vault or Managed HSM with FIPS-validated modules is used for key management
- [ ] **[Recommended]** Microsoft CJIS compliance documentation and state-specific addendums are verified

### Google Cloud

Google Cloud supports CJIS workloads through Assured Workloads.

- [ ] **[Recommended]** Assured Workloads is configured for CJIS compliance
- [ ] **[Recommended]** CJIS-eligible services and regions are verified
- [ ] **[Recommended]** Customer-managed encryption keys (CMEK) with Cloud HSM are used
- [ ] **[Recommended]** Google CJIS Security Addendum status is confirmed with the relevant state CSA

---

## Common Decisions (ADR Triggers)

- **Cloud environment selection** — GovCloud vs commercial cloud with CJIS controls, state-specific addendum availability
- **Encryption architecture** — customer-managed keys vs provider-managed, CloudHSM vs KMS, FIPS 140-2 Level 2 vs Level 3
- **Personnel screening model** — screen cloud provider personnel vs architecturally prevent access via encryption with customer-held keys
- **Advanced authentication method** — hardware tokens vs soft tokens vs biometrics, PIV/CAC integration for federal interoperability
- **Network segmentation strategy** — dedicated CJIS VPC vs segmented subnets, VPN architecture for remote CJI access
- **Audit log architecture** — centralized SIEM, 1-year retention, immutable storage, real-time alerting on CJI access
- **Mobile device strategy** — MDM selection, containerization approach, BYOD vs agency-issued devices
- **Data residency** — US-only storage requirements, cross-region replication constraints

## Reference Links

- [FBI CJIS Security Policy](https://www.fbi.gov/services/cjis/cjis-security-policy-resource-center) — current CJIS Security Policy documents and resources
- [NIST SP 800-88](https://csrc.nist.gov/publications/detail/sp/800-88/rev-1/final) — guidelines for media sanitization
- [FIPS 140-3 CMVP](https://csrc.nist.gov/projects/cryptographic-module-validation-program) — validated cryptographic modules list
- [AWS CJIS](https://aws.amazon.com/compliance/cjis/) — AWS CJIS compliance information
- [Azure CJIS](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-cjis) — Azure CJIS compliance information

## See Also

- `compliance/fedramp.md` — FedRAMP authorization (CJIS environments often align with FedRAMP controls)
- `compliance/nist-800-171-cmmc.md` — NIST 800-171 controls (significant overlap with CJIS requirements)
- `general/security.md` — General security controls and architecture patterns
- `general/identity.md` — IAM and authentication architecture
- `general/governance.md` — Cloud governance, tagging, and policy enforcement
