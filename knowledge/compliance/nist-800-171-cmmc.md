# NIST 800-171 & CMMC 2.0 - Cloud Control Mapping

## Scope

Covers NIST SP 800-171 security requirements for Controlled Unclassified Information (CUI) and CMMC 2.0 certification levels, including CUI enclave design patterns, control family mappings, and cloud provider FedRAMP/IL status. Does not cover FedRAMP authorization process details (see `compliance/fedramp.md`) or general identity architecture (see `general/identity.md`).

## Overview

**NIST SP 800-171** defines security requirements for protecting Controlled Unclassified Information (CUI) in non-federal systems. It is the foundation for the **Cybersecurity Maturity Model Certification (CMMC 2.0)**, which the Department of Defense uses to assess contractor cybersecurity posture.

**NIST 800-171 Revision 3** (May 2024) restructured the control families and updated requirements to align more closely with NIST SP 800-53 Rev. 5. Rev. 3 reorganizes the 110 controls from Rev. 2 into a different structure with updated control text and new organization-defined parameters (ODPs). The DoD has confirmed that CMMC 2.0 Level 2 assessments will continue to reference Rev. 2 until a future rulemaking formally adopts Rev. 3. Organizations should begin gap analysis against Rev. 3 now but maintain compliance with Rev. 2 for current CMMC assessments.

**CMMC 2.0 Levels:**
- **Level 1 (Foundational):** 17 practices — basic cyber hygiene (self-assessment)
- **Level 2 (Advanced):** 110 practices — aligned 1:1 with NIST 800-171 Rev. 2 (third-party assessment for critical contracts)
- **Level 3 (Expert):** 110+ practices — NIST 800-171 plus subset of NIST 800-172 (government-led assessment)

**CMMC Phase 2 Timeline:** CMMC Phase 1 (began 2025) requires Level 1 and Level 2 self-assessments in applicable contracts. **Phase 2** is scheduled for **November 2026**, when Level 2 third-party (C3PAO) assessments become a requirement in applicable DoD contracts. Organizations expecting to bid on contracts requiring Level 2 certification should begin C3PAO assessment preparation well in advance of the November 2026 deadline.

**Applicability:** Required for any organization handling CUI under DoD contracts. Increasingly adopted by other federal agencies and as a general cybersecurity framework.

**Cloud Provider Status:**
| Provider | FedRAMP | IL (Impact Level) | CUI Environment |
|----------|---------|-------------------|-----------------|
| **AWS** | High (GovCloud), Moderate (commercial) | IL2, IL4, IL5 (GovCloud), IL6 (Secret region) | AWS GovCloud |
| **Azure** | High (Government), Moderate (commercial) | IL2, IL4, IL5 (Government), IL6 (Secret) | Azure Government |
| **GCP** | High (Assured Workloads), Moderate (commercial) | IL2, IL4, IL5 (Assured Workloads) | GCP Assured Workloads |

---

## Checklist

- [ ] **[Critical]** Is CUI identified and categorized across all systems? (know what you are protecting and where it resides)
- [ ] **[Critical]** Is the CUI boundary (enclave) defined and documented? (system security plan, network diagrams)
- [ ] **[Critical]** Is the cloud environment deployed in a FedRAMP-authorized region? (GovCloud, Azure Government, or Assured Workloads for IL4+)
- [ ] **[Critical]** Is multi-factor authentication enforced for all users accessing CUI? (FIPS 140-2 validated MFA)
- [ ] **[Critical]** Are audit logs comprehensive and tamper-evident? (who accessed what CUI, when, from where)
- [ ] **[Critical]** Is encryption FIPS 140-2 validated for data at rest and in transit? (not just enabled — validated modules)
- [ ] **[Critical]** Is a System Security Plan (SSP) documented? (maps each of the 110 controls to implementation)
- [ ] **[Recommended]** Is a Plan of Action and Milestones (POA&M) maintained? (for controls not yet fully implemented)
- [ ] **[Critical]** Are incident response procedures defined and tested? (72-hour DoD reporting requirement)
- [ ] **[Recommended]** Is media sanitization handled per NIST 800-88? (before reuse or disposal of storage)
- [ ] **[Critical]** Is access control based on least privilege with separation of duties? (role-based, regularly reviewed)
- [ ] **[Recommended]** Are personnel security requirements met? (background checks, CUI handling training)
- [ ] **[Critical]** Is there a continuous monitoring program? (ongoing assessment, not point-in-time)

## Why This Matters

CMMC is a **contract requirement**, not optional. Without the required CMMC level, organizations cannot bid on or continue DoD contracts. Non-compliance can result in loss of contracts, False Claims Act liability, and reputational damage.

The 2024 CMMC final rule made third-party assessments mandatory for Level 2 on contracts involving critical CUI. Self-assessment is no longer sufficient for many contractors. Cloud architects must design CUI enclaves that are assessable and defensible.

---

## NIST 800-171 Control Families (14 Families, 110 Controls)

### 1. Access Control (AC) — 22 Controls

**Purpose:** Limit system access to authorized users and transactions.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| AC 3.1.1 | Limit system access to authorized users | IAM policies, RBAC, identity federation (AWS IAM, Entra ID (formerly Azure AD), GCP IAM) |
| AC 3.1.2 | Limit access to authorized transactions/functions | Least privilege policies, service control policies, conditional access |
| AC 3.1.3 | Control CUI flow per authorizations | VPC flow controls, network segmentation, DLP policies |
| AC 3.1.5 | Employ least privilege | Scoped IAM roles, no wildcard permissions, regular access reviews |
| AC 3.1.7 | Prevent non-privileged users from executing privileged functions | Separate admin roles, PIM/PAM (Azure PIM, AWS SSO with elevated roles) |
| AC 3.1.8 | Limit unsuccessful logon attempts | Account lockout policies, failed login monitoring, CloudTrail/Sign-in logs |
| AC 3.1.12 | Monitor and control remote access sessions | VPN with MFA, bastion hosts, session recording (AWS SSM, Azure Bastion) |
| AC 3.1.22 | Control CUI posted to publicly accessible systems | S3 Block Public Access, Azure Storage firewall, prevent public exposure |

### 2. Awareness and Training (AT) — 3 Controls

**Purpose:** Ensure personnel are aware of security risks and trained in their responsibilities.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| AT 3.2.1 | Ensure awareness of security risks | Security awareness training program, phishing simulations |
| AT 3.2.2 | Ensure training for roles with security responsibilities | Cloud-specific training (AWS/Azure/GCP security certifications) |
| AT 3.2.3 | Provide insider threat awareness training | Insider threat program, monitoring privileged user activity |

### 3. Audit and Accountability (AU) — 9 Controls

**Purpose:** Create, protect, and retain audit records.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| AU 3.3.1 | Create and retain audit records | CloudTrail, Azure Activity Log, GCP Audit Logs — all API calls logged |
| AU 3.3.2 | Ensure individual accountability via audit | User-level logging (no shared accounts), correlation of identity to action |
| AU 3.3.4 | Alert on audit process failure | Monitoring for logging pipeline failures, CloudWatch alarms |
| AU 3.3.5 | Correlate audit review and reporting | SIEM integration (Splunk, Sentinel, Chronicle), centralized log analysis |
| AU 3.3.8 | Protect audit information from unauthorized access | Immutable log storage (S3 Object Lock, WORM storage), separate log account |
| AU 3.3.9 | Limit audit log management to authorized individuals | Separate security account, restricted IAM for log deletion |

### 4. Configuration Management (CM) — 9 Controls

**Purpose:** Establish and maintain baseline configurations and inventories.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| CM 3.4.1 | Establish and maintain baseline configurations | AMI/image baselines, IaC (Terraform/CloudFormation), AWS Config |
| CM 3.4.2 | Establish security configuration settings | CIS Benchmarks, AWS Config Rules, Azure Policy, hardened images |
| CM 3.4.5 | Define and enforce access restrictions for change | CI/CD approval gates, branch protection, change management process |
| CM 3.4.6 | Employ least functionality | Disable unnecessary services/ports, minimal container images, remove unused packages |
| CM 3.4.8 | Apply deny-by-exception (blacklisting) | Security groups default deny, NACLs, application whitelisting |

### 5. Identification and Authentication (IA) — 11 Controls

**Purpose:** Identify and authenticate users, processes, and devices.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| IA 3.5.1 | Identify system users, processes, devices | Unique user accounts, service accounts, device certificates |
| IA 3.5.2 | Authenticate identities before access | SSO with MFA (Okta, Entra ID, AWS SSO), SAML/OIDC federation |
| IA 3.5.3 | Use MFA for privileged and network access | FIPS 140-2 validated MFA (hardware tokens, FIDO2, PIV/CAC) |
| IA 3.5.7 | Enforce minimum password complexity | Password policies, prefer passwordless (FIDO2), minimum 12 characters |
| IA 3.5.10 | Store and transmit only cryptographically protected passwords | Secrets Manager, no plaintext credentials, bcrypt/scrypt hashing |

### 6. Incident Response (IR) — 3 Controls

**Purpose:** Establish incident handling capability.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| IR 3.6.1 | Establish incident handling capability | IR plan, GuardDuty/Defender/SCC for detection, automated response playbooks |
| IR 3.6.2 | Track, document, and report incidents | Incident tracking system, DFARS 252.204-7012 72-hour reporting to DIBNet |
| IR 3.6.3 | Test incident response capability | Tabletop exercises, simulation drills, automated IR playbook testing |

### 7. Maintenance (MA) — 6 Controls

**Purpose:** Perform maintenance on organizational systems.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| MA 3.7.1 | Perform maintenance on systems | Patch management (SSM Patch Manager, Azure Update Management), maintenance windows |
| MA 3.7.2 | Control maintenance tools | Approved bastion access, recorded sessions, no unauthorized remote tools |
| MA 3.7.5 | Require MFA for remote maintenance | MFA-gated bastion/SSM access, PIV/CAC for privileged sessions |

### 8. Media Protection (MP) — 9 Controls

**Purpose:** Protect CUI on digital and physical media.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| MP 3.8.1 | Protect CUI on system media | Encryption at rest (KMS, Azure Key Vault, Cloud KMS), FIPS 140-2 validated |
| MP 3.8.3 | Sanitize media before disposal/reuse | EBS/disk encryption with key deletion, NIST 800-88 procedures |
| MP 3.8.6 | Implement cryptographic mechanisms for CUI during transport | TLS 1.2+ (FIPS endpoints), encrypted VPN tunnels, private connectivity |

### 9. Personnel Security (PS) — 2 Controls

**Purpose:** Screen individuals and protect CUI upon personnel actions.

### 10. Physical Protection (PE) — 6 Controls

**Purpose:** Limit physical access to systems (largely inherited from cloud provider in FedRAMP).

### 11. Risk Assessment (RA) — 3 Controls

**Purpose:** Assess risk to operations, assets, and individuals.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| RA 3.11.1 | Periodically assess risk | Regular vulnerability scanning (Inspector, Qualys), penetration testing |
| RA 3.11.2 | Scan for vulnerabilities periodically and on new threats | Automated scanning (Inspector, Defender for Cloud, SCC), CVE monitoring |
| RA 3.11.3 | Remediate vulnerabilities per risk assessments | Patching SLAs, vulnerability management program, risk-based prioritization |

### 12. Security Assessment (CA) — 4 Controls

**Purpose:** Assess, monitor, and correct deficiencies.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| CA 3.12.1 | Periodically assess security controls | Annual assessment, continuous monitoring (AWS Config, Defender, SCC) |
| CA 3.12.2 | Develop and implement POA&Ms | Track unimplemented controls, remediation timeline, milestone tracking |
| CA 3.12.3 | Monitor security controls continuously | Security Hub, Defender for Cloud, SCC dashboards, automated compliance checks |
| CA 3.12.4 | Develop and update SSP | System Security Plan covering all 110 controls, updated with changes |

### 13. System and Communications Protection (SC) — 16 Controls

**Purpose:** Monitor, control, and protect communications.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| SC 3.13.1 | Monitor and protect communications at system boundaries | WAF, network firewalls, VPC boundaries, TLS termination |
| SC 3.13.4 | Prevent unauthorized transfer of information | DLP policies (Macie, Purview, DLP), egress filtering, VPC endpoints |
| SC 3.13.8 | Implement cryptographic mechanisms for CUI in transit | FIPS 140-2 TLS endpoints, VPN encryption, private connectivity |
| SC 3.13.11 | Employ FIPS-validated cryptography | FIPS endpoints for AWS/Azure/GCP, FIPS-validated key management |
| SC 3.13.16 | Protect CUI confidentiality at rest | AES-256 encryption, KMS-managed keys, FIPS 140-2 Level 2+ HSMs |

### 14. System and Information Integrity (SI) — 7 Controls

**Purpose:** Identify, report, and correct system flaws.

| Key Controls | Description | Cloud Implementation |
|--------------|-------------|---------------------|
| SI 3.14.1 | Identify and correct system flaws in a timely manner | Patch management, automated remediation, CVE tracking |
| SI 3.14.2 | Provide protection from malicious code | Endpoint protection, container scanning, malware detection (GuardDuty) |
| SI 3.14.6 | Monitor systems for unauthorized access | SIEM, IDS/IPS, anomaly detection, GuardDuty/Defender/SCC |
| SI 3.14.7 | Identify unauthorized use of systems | User behavior analytics, impossible travel detection, anomaly alerts |

---

## CUI Enclave Patterns

### AWS GovCloud CUI Enclave

```
AWS GovCloud (US)
┌─────────────────────────────────────────────┐
│  AWS Organizations + SCPs                    │
│  ┌────────────────────────────────────────┐  │
│  │  CUI VPC                               │  │
│  │  ├── Private subnets only              │  │
│  │  ├── VPC endpoints for AWS services    │  │
│  │  ├── No internet gateway               │  │
│  │  ├── Flow logs → S3 (WORM)            │  │
│  │  │                                     │  │
│  │  │  Compute: EC2/ECS/EKS              │  │
│  │  │  (FIPS endpoints, hardened AMIs)    │  │
│  │  │                                     │  │
│  │  │  Data: RDS/S3/DynamoDB             │  │
│  │  │  (KMS CMK, FIPS 140-2 validated)   │  │
│  │  │                                     │  │
│  │  │  Identity: AWS SSO + MFA           │  │
│  │  │  (PIV/CAC via SAML federation)     │  │
│  │  └────────────────────────────────────┘  │
│  │                                           │
│  │  Logging Account (separate, restricted)   │
│  │  ├── CloudTrail (org-wide, S3 Object Lock)│
│  │  ├── VPC Flow Logs                        │
│  │  └── GuardDuty findings                   │
│  └───────────────────────────────────────────┘
└─────────────────────────────────────────────┘
```

### Key Enclave Design Principles

1. **Use FedRAMP High authorized services only** — Not all cloud services are authorized
2. **FIPS endpoints everywhere** — `*.fips.us-gov-west-1.amazonaws.com`
3. **No public internet access** — VPC endpoints for AWS services, no IGW
4. **Encrypt everything with CMKs** — Customer-managed keys in CloudHSM (FIPS 140-2 Level 3) or KMS (Level 2)
5. **Immutable audit logs** — S3 Object Lock in Governance or Compliance mode
6. **Separate accounts** for logging, security tooling, and workloads
7. **Continuous compliance monitoring** — AWS Config + Security Hub with NIST 800-171 standards

### Azure Government CUI Enclave

- Deploy in Azure Government regions (US Gov Virginia, US Gov Arizona)
- Use Azure Policy with NIST 800-171 built-in initiative
- Azure Defender for Cloud with regulatory compliance dashboard
- Azure Key Vault with HSM backing (FIPS 140-2 Level 2/3)
- Entra ID with Conditional Access + FIDO2/PIV MFA

### GCP Assured Workloads CUI Enclave

- Create Assured Workloads folder with IL4/IL5 compliance regime
- Restricts services to FedRAMP High authorized only
- Enforces data residency (US-only regions)
- CMEK with Cloud HSM (FIPS 140-2 Level 3)
- VPC Service Controls for data exfiltration prevention

## Common Decisions (ADR Triggers)

- **CUI boundary definition** — what systems are in scope, where CUI flows
- **Cloud region selection** — GovCloud vs commercial with FedRAMP, IL level requirements
- **MFA technology** — PIV/CAC vs FIDO2 vs software MFA (FIPS 140-2 validation required)
- **Encryption key management** — KMS managed vs CloudHSM (Level 2 vs Level 3)
- **Logging architecture** — centralized logging account, retention period (3+ years recommended)
- **CMMC assessment scope** — which systems, Level 1 vs Level 2 vs Level 3
- **SSP and POA&M ownership** — who maintains, review cadence, assessment preparation

## See Also

- `compliance/fedramp.md` — FedRAMP authorization process and controls
- `general/security.md` — General security controls
- `general/identity.md` — IAM and authentication architecture
- `general/governance.md` — Cloud governance and policy-as-code
