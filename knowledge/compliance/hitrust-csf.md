# HITRUST CSF — Common Security Framework

## Scope

The HITRUST Common Security Framework (CSF) is a certifiable, prescriptive cybersecurity framework that aggregates requirements from multiple sources (HIPAA, ISO 27001, NIST 800-53, PCI-DSS, GDPR, and many others) into a single set of controls. It is widely adopted in the US healthcare sector as a one-stop alternative to maintaining separate audit programs for each underlying framework. Covers the HITRUST control categories, the assessment levels (e1, i1, r2), the certification process, the relationship to HIPAA and other underlying frameworks, the role of HITRUST in customer security reviews, the cloud-relevant controls, and the practical implementation patterns. Does not cover the HITRUST Threat Catalog or HITRUST de-identification framework in depth.

## Why HITRUST exists

Healthcare organizations face an unusual compliance burden because they are subject to many overlapping frameworks: HIPAA for PHI, PCI-DSS if they process payments, ISO 27001 for international operations, NIST 800-53 if they serve government customers, GDPR if they have EU patients, and many more. Maintaining separate audit programs for each is expensive and produces overlapping evidence collection without clear benefit.

HITRUST CSF was created to consolidate these into a single framework. A HITRUST CSF assessment maps the organization's controls onto the requirements of every underlying framework simultaneously, producing certification that satisfies multiple audit requirements in one engagement.

The most important practical consequence: many healthcare customers (large hospital systems, payers, device manufacturers, pharma) require their vendors to be HITRUST-certified as a condition of doing business. For a vendor selling into healthcare, HITRUST certification is increasingly the table-stakes credential.

## The HITRUST CSF Structure

HITRUST CSF v11 is organized into **14 control categories**:

| Category | Focus |
|---|---|
| 0. Information Security Management Program | Governance, policies, organizational structure |
| 01. Access Control | User access management, authentication, privilege management |
| 02. Human Resources Security | Personnel screening, training, termination |
| 03. Risk Management | Risk assessment, treatment, acceptance |
| 04. Security Policy | Documented policies, exceptions, review cadence |
| 05. Organization of Information Security | Roles, responsibilities, third-party access |
| 06. Compliance | Regulatory compliance, audit, intellectual property |
| 07. Asset Management | Inventory, classification, handling |
| 08. Physical and Environmental Security | Facility security, equipment protection |
| 09. Communications and Operations Management | Operational procedures, change management, malware protection, backup, monitoring |
| 10. Information Systems Acquisition, Development and Maintenance | Secure development, vulnerability management, cryptography |
| 11. Information Security Incident Management | Incident response, evidence collection, lessons learned |
| 12. Business Continuity Management | BCP, DR, testing |
| 13. Privacy Practices | Privacy program, data subject rights, breach notification |

Each category contains **objectives** and **control specifications** with implementation requirements that vary by the organization's size, system criticality, and regulatory environment.

## Assessment Levels

HITRUST offers three assessment levels with increasing rigor:

### e1 — Essentials, 1-Year (introduced 2023)

The lightest-weight assessment, focused on **44 controls** addressing the most critical cybersecurity practices. Designed for organizations starting their HITRUST journey or for low-risk vendors. The certification is valid for 1 year.

### i1 — Implemented, 1-Year

A moderate assessment focused on **~180 controls**. Verifies that the controls are documented and implemented but does not require evidence of operating effectiveness over time. Valid for 1 year.

### r2 — Risk-based, 2-Year

The most comprehensive assessment, with **300+ controls** tailored to the organization's specific risk factors. Verifies that the controls are documented, implemented, and operating effectively. Valid for 2 years (with an interim assessment after the first year).

The right assessment level depends on customer requirements. Most healthcare enterprise customers require r2; smaller customers may accept i1; e1 is typically not sufficient for customer requirements but may be the right starting point for self-assessment.

## Certification Process

A HITRUST certification engagement typically includes:

1. **Scoping** — define which systems, business units, and data are in scope
2. **Risk factor selection** — identify the organizational, regulatory, and system risk factors that drive control selection
3. **Control selection** — based on the risk factors, identify which controls apply
4. **Self-assessment** — score each control on the HITRUST PRISMA scale (Policy, Process, Implemented, Measured, Managed)
5. **Validated assessment** — an external HITRUST authorized assessor reviews the self-assessment, conducts testing, and submits to HITRUST
6. **HITRUST quality review** — HITRUST reviews the assessor's submission
7. **Certification report** — HITRUST issues the report and the certification badge

The total engagement typically takes 6–12 months for a first-time r2 assessment, less for renewal.

## Cloud Service Mapping

HITRUST controls map onto cloud services in much the same way as HIPAA, NIST 800-53, and ISO 27001. The major cloud providers (AWS, Azure, GCP) all support HITRUST workloads via:

- **HIPAA-eligible services** — the same services that are eligible under a HIPAA BAA are eligible under HITRUST
- **Inherited controls** — physical security, environmental controls, and other infrastructure controls are inherited from the cloud provider's own HITRUST or SOC 2 / ISO 27001 certification
- **Customer responsibility matrix** — published by AWS, Azure, GCP for each service, describing which HITRUST controls the customer must implement

For a HITRUST workload on cloud, the typical division of responsibility:

- **Cloud provider implements**: physical, environmental, network infrastructure, host hypervisor security, hardware patching
- **Customer implements**: application security, IAM, data classification and protection, application logging, incident response for application-layer events, business continuity testing

## Relationship to HIPAA

HITRUST CSF includes the HIPAA Security Rule and HIPAA Breach Notification Rule requirements as a subset. A HITRUST r2 certification includes a HIPAA-specific module that maps the HITRUST controls onto the HIPAA Security Rule safeguards. For organizations subject to HIPAA, HITRUST certification can serve as the primary evidence of HIPAA compliance.

The reverse is not true — a HIPAA risk analysis is not equivalent to a HITRUST assessment. HITRUST is more prescriptive and more comprehensive.

## Architect Checklist

- [ ] **[Critical]** **Determine if HITRUST applies** to the organization. Check whether customers require it (most healthcare enterprise customers do) or whether the organization wants it for competitive positioning.
- [ ] **[Critical]** **Choose the assessment level** (e1, i1, r2) based on customer requirements and current maturity. r2 is the standard for healthcare enterprise sales.
- [ ] **[Critical]** **Identify the in-scope systems** explicitly. HITRUST scope creep is a common audit finding — define the boundary at the start and enforce it.
- [ ] **[Critical]** **Select a HITRUST authorized external assessor** early in the process. Assessors have varying experience and approach; select one with prior experience in the organization's specific industry and cloud architecture.
- [ ] **[Critical]** **Document each control implementation** at the level required by the PRISMA scale. Aim for "Implemented" or higher on every applicable control. "Policy only" controls are findings.
- [ ] **[Recommended]** **Start with a self-assessment** before engaging an external assessor. The self-assessment identifies gaps and lets the team remediate before the formal assessment, reducing cost and risk.
- [ ] **[Recommended]** **Use the cloud provider's HITRUST mapping** to identify inherited vs customer-implemented controls. Do not re-document inherited controls.
- [ ] **[Recommended]** **Maintain continuous compliance** between assessments. Drift between assessments produces "interim assessment" findings that complicate renewal.
- [ ] **[Optional]** **Map HITRUST controls to existing controls** from other frameworks the organization is already certified against (ISO 27001, SOC 2). The mapping reduces duplication of evidence collection.

## Common Decisions (ADR Triggers)

- **Assessment level (e1 vs i1 vs r2)** — driven by customer requirements. r2 is the default for healthcare enterprise. i1 for smaller customers or as an interim step.
- **Scope (full organization vs specific systems)** — narrower scope is faster and cheaper but provides less customer assurance. Most certifications scope to "the platform that handles customer data".
- **External assessor selection** — experience in the specific industry matters more than firm size. Get references from similar organizations.
- **Continuous compliance vs annual scramble** — continuous compliance (with the controls operating year-round) is more sustainable. Annual scramble (controls implemented in the months before assessment) produces brittle certifications and difficult renewals.
- **HITRUST as the primary framework vs HITRUST as the customer-facing certification** — for most healthcare-focused organizations, HITRUST as primary is the right answer because it consolidates the audit burden. For organizations in multiple sectors, HITRUST may be one of several certifications.

## Reference Links

- [HITRUST Alliance](https://hitrustalliance.net/)
- [HITRUST CSF](https://hitrustalliance.net/product-tool/hitrust-csf/)
- [HITRUST e1, i1, r2 assessment levels](https://hitrustalliance.net/product-tool/assessments/)
- [AWS HITRUST eligibility](https://aws.amazon.com/compliance/hitrust/)
- [Azure HITRUST guidance](https://learn.microsoft.com/azure/compliance/offerings/offering-hitrust)
- [GCP HITRUST guidance](https://cloud.google.com/security/compliance/hitrust)

## See Also

- `compliance/hipaa.md` — HIPAA Security Rule, which is a subset of HITRUST
- `compliance/iso-27001.md` — ISO 27001, which is mapped within HITRUST
- `compliance/soc2.md` — SOC 2, often paired with HITRUST for financial reporting customers
- `compliance/nist-800-171-cmmc.md` — NIST 800-171, which is mapped within HITRUST for federal customers
- `frameworks/nist-sp-800-53.md` — NIST 800-53, the underlying control catalog HITRUST builds on
- `failures/compliance.md` — compliance failure patterns
