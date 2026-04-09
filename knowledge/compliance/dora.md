# DORA — Digital Operational Resilience Act

## Scope

The Digital Operational Resilience Act (DORA, Regulation (EU) 2022/2554) is an EU regulation effective from 17 January 2025 that establishes a uniform digital operational resilience framework for the financial sector. DORA applies to financial entities (banks, insurance companies, investment firms, payment service providers, crypto-asset service providers, etc.) and to the **critical third-party ICT providers** they depend on — which usually means the major cloud providers, SaaS vendors, and managed service providers. Covers the five DORA pillars (ICT risk management, ICT-related incident management, digital operational resilience testing, ICT third-party risk, information sharing), the 24-hour incident reporting requirement, the threat-led penetration testing (TLPT) requirement, the critical third-party provider designation process, and the cloud-relevant practical implementation patterns.

## Applicability

DORA applies to ~22,000 financial entities and their ICT third-party providers across the EU. The financial entity scope includes:

- Credit institutions, payment institutions, electronic money institutions
- Investment firms, central counterparties, trade repositories
- Insurance and reinsurance undertakings
- Crypto-asset service providers, account information service providers
- Crowdfunding service providers, audit firms (limited scope)
- Trading venues
- Critical third-party ICT providers (designated by the European Supervisory Authorities)

The **critical third-party ICT provider** designation is the most consequential element for cloud providers. The European Supervisory Authorities (ESAs — EBA, EIOPA, ESMA) can designate specific ICT providers as "critical" based on their systemic importance to the financial sector. Once designated, the critical provider is subject to direct EU-level oversight, on-site inspections, and the ability for the ESAs to impose remediation requirements. The major cloud providers (AWS, Azure, GCP) are likely to be designated under DORA as critical third-party providers.

For financial entities, DORA's obligations flow downstream — they must impose DORA-aligned contractual terms on their ICT providers and demonstrate that their providers meet DORA requirements.

## The Five Pillars

### 1. ICT Risk Management (Articles 5–16)

Requires financial entities to establish a comprehensive ICT risk management framework that:

- Identifies and classifies ICT-related business functions and the supporting ICT systems
- Continuously identifies sources of ICT risk
- Implements protective and preventive measures
- Detects anomalous activities
- Has business continuity and disaster recovery plans
- Has learning and evolving processes

The risk management framework must be approved by the management body and reviewed at least annually.

### 2. ICT-related Incident Management (Articles 17–23)

Requires financial entities to establish an incident management process and to report **major ICT-related incidents** to the competent authority on a strict timeline:

| Phase | Deadline | Content |
|---|---|---|
| **Initial notification** | Within 4 hours of classification, no later than 24 hours after detection | Entity, incident description, type, severity, impact |
| **Intermediate report** | Within 72 hours of the initial notification | Updated information, including indicators of compromise |
| **Final report** | Within 1 month of the incident | Detailed analysis, root cause, remediation, lessons learned |

A "major incident" is defined by quantitative thresholds (number of affected clients, financial impact, duration, service criticality).

DORA's 4-hour initial notification is faster than NIS2's 24-hour early warning. Financial entities subject to both must align on the shorter timeline.

### 3. Digital Operational Resilience Testing (Articles 24–27)

Requires financial entities to test their digital operational resilience on a defined cadence:

- **All financial entities** must perform basic testing (vulnerability assessments, scenario-based testing, performance testing, end-to-end testing) at least annually
- **Significant financial entities** (designated by the competent authority based on size and criticality) must perform **threat-led penetration testing (TLPT)** at least every three years

TLPT is a specific form of testing that simulates a real attacker's tactics, techniques, and procedures (TTPs), conducted by qualified external testers under the supervision of the competent authority. It is closer to a red team engagement than a traditional vulnerability scan.

### 4. ICT Third-Party Risk Management (Articles 28–44)

Requires financial entities to:

- Maintain a **register of all ICT third-party arrangements** (a complete inventory of every third-party ICT relationship, with risk assessment)
- Conduct **due diligence** before entering into ICT third-party arrangements, including assessment of the provider's information security, business continuity, and substitutability
- Include specific **contractual provisions** in ICT third-party contracts, including:
  - Description of services
  - Service levels
  - Data location and processing
  - Security requirements and reporting obligations
  - Audit rights for the financial entity and the competent authority
  - Termination rights
  - Exit strategies
- Categorize functions as supported by ICT services as **critical or important**, with stricter requirements for the critical category
- Conduct **concentration risk assessments** when multiple critical functions depend on the same provider

### 5. Information Sharing (Article 45)

Encourages voluntary information sharing about cyber threats between financial entities. Provides a legal framework for the sharing while respecting GDPR and other data protection requirements.

## Cloud Service Mapping

| DORA Requirement | AWS | Azure | GCP |
|---|---|---|---|
| ICT risk management framework | AWS Audit Manager, Trusted Advisor, Well-Architected Tool | Microsoft Defender for Cloud, Compliance Manager | Security Command Center, Compliance Reports Manager |
| Incident detection | GuardDuty, Detective, Security Hub | Defender for Cloud, Sentinel | Security Command Center, Chronicle |
| Business continuity | AWS Backup, Cross-region replication, AWS Resilience Hub | Azure Backup, Site Recovery, Business Continuity Center | Cloud Backup, regional persistent disks |
| Continuous monitoring | CloudWatch, CloudTrail | Azure Monitor, Activity Log | Cloud Monitoring, Cloud Audit Logs |
| Penetration testing support | AWS pen testing policy | Azure pen testing rules of engagement | GCP penetration testing notification |
| Concentration risk reduction | Multi-region, multi-account | Multi-region, paired regions | Multi-region, multi-project |

## Architect Checklist

- [ ] **[Critical]** **Determine if DORA applies** to the organization (financial entity) or to the organization's customers (third-party ICT provider serving financial entities). Both create DORA obligations.
- [ ] **[Critical]** **Maintain a register of ICT third-party arrangements** with the required fields (provider, service, criticality, location, contract reference, exit strategy). The register is the audit artifact for the third-party risk management requirement.
- [ ] **[Critical]** **Establish the incident reporting process** with the 4-hour initial notification capability. Define classification criteria, the workflow, the named individuals, and the alternate notification path if the primary individual is unavailable.
- [ ] **[Critical]** **Document the contractual provisions** required by DORA in every new ICT third-party contract. Audit existing contracts and renegotiate or amend them to add the required terms.
- [ ] **[Critical]** **Assess concentration risk** annually. If a single ICT provider supports multiple critical functions, document the risk and the mitigation (multi-cloud, multi-region, alternate provider).
- [ ] **[Critical]** **Define exit strategies** for every critical ICT provider relationship. The exit strategy must cover data extraction, system migration, and operational continuity during the exit. Untested exit strategies are not acceptable.
- [ ] **[Recommended]** **Conduct annual digital operational resilience testing** including vulnerability assessments, scenario-based exercises, and end-to-end testing. Document the results and the remediation actions.
- [ ] **[Recommended]** **For significant entities**, prepare for TLPT every three years. TLPT requires significant lead time — engage qualified testers 6 months before the planned test.
- [ ] **[Recommended]** **Train management bodies** on DORA obligations and risk management. Document the training as evidence of the management body's involvement.
- [ ] **[Optional]** **Subscribe to threat intelligence** from financial sector ISACs and from the national CSIRT.

## Penalties

DORA penalties are not as quantitatively defined as GDPR or NIS2, but the regulation provides for:

- **Administrative fines** imposed by the national competent authority, with the amount calibrated to the severity of the breach and the size of the entity
- **Periodic penalty payments** for ongoing non-compliance
- **Public statements** identifying the non-compliant entity

For critical third-party providers, the EU-level oversight can also impose remediation orders backed by the same penalty regime.

## Common Decisions (ADR Triggers)

- **Critical vs important function classification** — drives the contractual requirements and the audit rights. Document the classification per function.
- **Single-cloud vs multi-cloud for concentration risk** — single-cloud is operationally simpler but creates concentration risk for critical functions. Multi-cloud is the DORA-friendly answer for the most critical functions.
- **Exit strategy depth** — tabletop exercise vs full migration test. Tabletop is the minimum; full migration test is the only way to actually verify the strategy works.
- **TLPT scope** — for significant entities, decide whether the TLPT covers the full estate or specific critical systems. The competent authority typically expects coverage of all critical functions over time.
- **In-house vs outsourced TLPT** — outsourced is required (the testers must be qualified third parties). Choose providers with TLPT experience and DORA familiarity.

## Reference Links

- [Regulation (EU) 2022/2554 (DORA official text)](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)
- [ESA technical standards under DORA](https://www.eba.europa.eu/regulation-and-policy/operational-resilience-cyber-security)
- [TIBER-EU framework (DORA reference for TLPT)](https://www.ecb.europa.eu/paym/cyber-resilience/tiber-eu/html/index.en.html)

## See Also

- `compliance/nis2.md` — NIS2 has overlapping scope (cybersecurity for essential entities) but DORA is more specific to financial sector
- `compliance/gdpr.md` — GDPR breach notification is parallel to DORA incident reporting
- `frameworks/nist-csf-2.0.md` — NIST CSF is acceptable as the underlying framework for DORA risk management
- `failures/operations.md` — operational resilience failure patterns
- `failures/dependencies.md` — third-party / supply chain failure patterns
- `general/disaster-recovery.md` — disaster recovery as a DORA requirement
