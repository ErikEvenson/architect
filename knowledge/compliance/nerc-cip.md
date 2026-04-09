# NERC CIP — Critical Infrastructure Protection

## Scope

The North American Electric Reliability Corporation (NERC) Critical Infrastructure Protection (CIP) standards are a set of mandatory cybersecurity requirements for the **bulk electric system (BES)** in North America. CIP applies to entities that own or operate bulk power generation, transmission, and certain distribution assets — utility companies, independent power producers, transmission operators, balancing authorities, and reliability coordinators. CIP is enforced by NERC under FERC oversight, with substantial financial penalties for non-compliance ($1M+ per day per violation in egregious cases). Covers the CIP standard set (CIP-002 through CIP-014), the BES Cyber System categorization (low / medium / high impact), the cloud-on-CIP question (a long-standing area of ambiguity), the cloud service mapping for the CIP requirements that can be cloud-hosted, and the practical implementation patterns for utility cybersecurity programs.

## Applicability

NERC CIP applies to **registered entities** that own, operate, or use the bulk electric system. The registration is determined by NERC and the regional entity (e.g., WECC for the western US, MRO for the Midwest, NPCC for the Northeast). Registered entity functions include:

- **Generator Owner / Operator**
- **Transmission Owner / Operator**
- **Balancing Authority**
- **Reliability Coordinator**
- **Distribution Provider** (for assets that meet specific impact thresholds)
- **Interchange Authority**

Entities outside these functions (e.g., distribution-only utilities serving residential customers, independent system operators of microgrids) are typically not subject to NERC CIP, though some state-level cybersecurity requirements may apply.

## The CIP Standards

The current CIP standards (as of the late 2020s) are:

| Standard | Subject |
|---|---|
| **CIP-002** | BES Cyber System Categorization |
| **CIP-003** | Security Management Controls |
| **CIP-004** | Personnel and Training |
| **CIP-005** | Electronic Security Perimeter(s) |
| **CIP-006** | Physical Security of BES Cyber Systems |
| **CIP-007** | System Security Management |
| **CIP-008** | Incident Reporting and Response Planning |
| **CIP-009** | Recovery Plans for BES Cyber Systems |
| **CIP-010** | Configuration Change Management and Vulnerability Assessments |
| **CIP-011** | Information Protection |
| **CIP-012** | Communications between Control Centers |
| **CIP-013** | Supply Chain Risk Management |
| **CIP-014** | Physical Security of Critical Substations |

CIP-002 is the foundational standard — it defines how an entity categorizes its BES Cyber Systems by impact level, which then drives the applicability of all the other standards.

## Impact Categorization (CIP-002)

CIP-002 defines three impact categories:

- **High Impact** — BES Cyber Systems used by Reliability Coordinators, Balancing Authorities of large interconnections, large generation control centers, large transmission control centers
- **Medium Impact** — generation and transmission assets above defined MW thresholds, transmission lines above defined kV thresholds, other criteria
- **Low Impact** — all other BES Cyber Systems not categorized as High or Medium

The full list of CIP standards applies to High Impact systems. Medium Impact has a reduced scope. Low Impact has the minimum requirements (only CIP-003-7 R1 and R2, plus parts of CIP-008 and CIP-014).

## The Cloud Question

Until recently, NERC CIP standards effectively prohibited cloud hosting of BES Cyber Systems, especially at Medium and High Impact levels. The standards' language assumes physical access controls, named individuals with authorized cyber access, and an "Electronic Security Perimeter" that is typically interpreted as a network boundary the entity owns and controls.

In 2023–2024, NERC initiated a project (Project 2023-09 — Risk Management for Third-Party Cloud Services) to develop standards that would allow cloud hosting of certain BES Cyber Systems with appropriate controls. The work is ongoing as of late 2025, with phased adoption expected over the following years.

In the meantime, the practical situation is:

- **Low Impact BES Cyber Systems** can be hosted in cloud with care, applying CIP-003 controls to the cloud environment
- **Medium and High Impact BES Cyber Systems** generally cannot be cloud-hosted under current standards. Some utilities are running pilot projects with FERC and NERC awareness to demonstrate the necessary controls.
- **Non-BES systems** (corporate IT, customer-facing systems, billing) can be cloud-hosted normally — these are not in scope for CIP

The cloud restriction is one of the most cited frustrations with NERC CIP from utilities that want to modernize their IT/OT integration. The standards work in 2023–2024 is intended to address this, but the timeline is years.

## Cloud Service Mapping (where cloud is permitted)

For Low Impact BES Cyber Systems and for non-BES corporate systems that interact with BES systems:

| CIP Requirement | AWS | Azure | GCP |
|---|---|---|---|
| CIP-003 cyber security policy | AWS Audit Manager (NERC CIP framework) | Microsoft Compliance Manager | Compliance Reports Manager |
| CIP-005 electronic perimeter | VPC + Security Groups + Network Firewall | VNet + NSGs + Azure Firewall | VPC + firewall rules + Cloud NGFW |
| CIP-007 system security | Inspector, Patch Manager, GuardDuty | Defender for Cloud, Update Manager | Security Command Center, OS Patch Management |
| CIP-008 incident response | GuardDuty, Detective | Defender for Cloud, Sentinel | Security Command Center, Chronicle |
| CIP-009 recovery plans | AWS Backup, AWS Resilience Hub | Azure Backup, Site Recovery | Cloud Backup, Disaster Recovery |
| CIP-010 configuration change | AWS Config, CloudFormation drift detection | Azure Policy, Bicep what-if | Config Connector, Terraform plan |
| CIP-011 information protection | KMS, S3 SSE, Secrets Manager | Key Vault, Storage SSE | Cloud KMS, Secret Manager |
| CIP-013 supply chain | AWS Audit Manager NIST 800-161 framework | Microsoft Supply Chain Security | Software Delivery Shield |

## Architect Checklist

- [ ] **[Critical]** **Determine NERC CIP applicability**. Is the organization a registered entity with NERC? If yes, which functions are registered? The functions determine which CIP standards apply.
- [ ] **[Critical]** **Categorize BES Cyber Systems** under CIP-002. The categorization is the foundation for the entire compliance program. Most utilities have a defined process for categorization, often supported by a consulting firm.
- [ ] **[Critical]** **Avoid cloud hosting for Medium and High Impact BES Cyber Systems** until the NERC standards work permits it. The cost of getting this wrong is severe (NERC enforcement actions can be in the millions of dollars).
- [ ] **[Critical]** **Maintain Electronic Security Perimeter (ESP) controls** for all BES Cyber Systems. The ESP is typically a network boundary with documented access points, monitoring, and access control.
- [ ] **[Critical]** **Track personnel risk assessments and training** for every individual with authorized cyber access to BES Cyber Systems. Records are reviewed during audits.
- [ ] **[Critical]** **Implement configuration change management** with documented baselines, change approval, and post-change verification. Configuration changes to BES Cyber Systems are heavily audited.
- [ ] **[Critical]** **Conduct vulnerability assessments** on the cadence required by CIP-010 (varies by impact level — quarterly for High, less frequently for Medium).
- [ ] **[Critical]** **Maintain incident response plan** under CIP-008. Plan must include reporting to NERC E-ISAC for Reportable Cyber Security Incidents.
- [ ] **[Critical]** **Recovery plans under CIP-009** must include the specific steps to recover BES Cyber Systems and must be tested annually.
- [ ] **[Recommended]** **Engage with E-ISAC** (Electricity Information Sharing and Analysis Center) for threat intelligence and information sharing.
- [ ] **[Recommended]** **Use IT/OT segmentation** rigorously. The IT/OT boundary is the primary defense against IT-based attacks reaching the BES Cyber Systems.
- [ ] **[Recommended]** **Document everything**. NERC audits are evidence-driven; the entity must produce documentation showing the controls are operating. "We do this" is not sufficient — the audit needs the records.

## Penalties

NERC CIP penalties are determined by the **Risk-Based Registration Approach** and the **NERC Sanction Guidelines**:

- **Per-violation, per-day** maximum is currently around $1.4M per day per violation (adjusted annually for inflation)
- **Mitigation plans** are typically required for any violation, with specific deadlines and milestones
- **Public reporting** of violations and the entity name (with limited redaction for specific sensitive details)
- **Repeat violations** receive escalating penalties

The largest CIP enforcement actions in recent years have totaled $10M+ for individual entities with systemic compliance failures.

## Common Decisions (ADR Triggers)

- **Cloud vs on-premises for non-BES systems** — cloud is the right answer for corporate IT, customer service, billing, and other non-BES systems. The IT/OT boundary must be rigorously maintained.
- **Cloud vs on-premises for BES Cyber Systems** — on-premises is the only practical answer until the NERC standards work permits cloud. Pilot projects with NERC awareness are starting to emerge.
- **Single CIP compliance program vs federated** — single program is right for most utilities. Federated (per-business-unit programs) only when the business units are operationally independent.
- **In-house vs outsourced CIP compliance** — in-house for the day-to-day operation. External assessors and consultants for annual audits and gap assessments.
- **Vendor management depth** — annual questionnaires for low-criticality vendors. Formal audits for vendors providing software or services that touch BES Cyber Systems.

## Reference Links

- [NERC CIP standards (current version)](https://www.nerc.com/pa/Stand/Pages/CIPStandards.aspx)
- [NERC enforcement actions](https://www.nerc.com/pa/comp/CE/Pages/default.aspx)
- [E-ISAC (Electricity Information Sharing and Analysis Center)](https://www.eisac.com/)
- [NERC Project 2023-09 (Risk Management for Third-Party Cloud Services)](https://www.nerc.com/pa/Stand/Pages/Project2023-09.aspx)
- [FERC NOPR on cloud services](https://www.ferc.gov/news-events/news/ferc-issues-nopr-cloud-computing)

## See Also

- `compliance/nist-800-171-cmmc.md` — NIST 800-171 / CMMC (federal contractors), conceptually similar to CIP for energy sector
- `frameworks/nist-sp-800-53.md` — NIST 800-53 controls overlap significantly with CIP requirements
- `general/networking-physical.md` — physical infrastructure considerations relevant to CIP physical security requirements
- `failures/compliance.md` — compliance failure patterns
- `failures/operations.md` — operational resilience patterns relevant to CIP-008 and CIP-009
