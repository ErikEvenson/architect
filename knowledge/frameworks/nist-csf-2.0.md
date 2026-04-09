# NIST Cybersecurity Framework 2.0

## Scope

The NIST Cybersecurity Framework 2.0 (CSF 2.0, released February 2024) is a voluntary framework that organizes cybersecurity activities into six high-level Functions: **Govern**, **Identify**, **Protect**, **Detect**, **Respond**, and **Recover**. CSF 2.0 added the Govern function to CSF 1.1's five functions, reflecting the recognition that cybersecurity requires top-down accountability and risk management as a primary control. CSF 2.0 is the most common framework cited by non-regulated US enterprise security teams as their primary reference, partly because it is voluntary (no compliance obligation), partly because it is high-level enough to be applicable across industries, and partly because it maps cleanly onto more prescriptive frameworks (SP 800-53, ISO 27001, CIS Controls). Covers the six Functions, the Categories and Subcategories within each, the Implementation Tiers, the Profile mechanism for organization-specific tailoring, and the relationship between CSF and the more prescriptive control catalogs.

## The Six Functions

### GV — Govern (new in 2.0)

Establishes and monitors the organization's cybersecurity risk management strategy, expectations, and policy. Govern is the function that makes the rest of CSF actionable at the organizational level rather than the technical level.

Categories:
- **GV.OC** — Organizational Context (mission, stakeholders, legal/regulatory requirements)
- **GV.RM** — Risk Management Strategy (risk tolerance, risk appetite, decision-making processes)
- **GV.RR** — Roles, Responsibilities, and Authorities (cybersecurity roles, accountability)
- **GV.PO** — Policy (cybersecurity policies as the basis for technical controls)
- **GV.OV** — Oversight (monitoring of the cybersecurity program by leadership)
- **GV.SC** — Cybersecurity Supply Chain Risk Management (third-party risk, supply chain controls)

### ID — Identify

Develops the organizational understanding to manage cybersecurity risk to systems, people, assets, data, and capabilities.

Categories:
- **ID.AM** — Asset Management (inventory of hardware, software, data, systems, services)
- **ID.RA** — Risk Assessment (threat identification, vulnerability identification, likelihood and impact)
- **ID.IM** — Improvement (lessons learned, continuous improvement)

### PR — Protect

Develops and implements appropriate safeguards to ensure delivery of critical services.

Categories:
- **PR.AA** — Identity Management, Authentication, and Access Control
- **PR.AT** — Awareness and Training
- **PR.DS** — Data Security (data at rest, data in transit, data in use)
- **PR.PS** — Platform Security (configuration management, hardening, patching)
- **PR.IR** — Technology Infrastructure Resilience

### DE — Detect

Develops and implements appropriate activities to identify the occurrence of a cybersecurity event.

Categories:
- **DE.CM** — Continuous Monitoring (network monitoring, endpoint monitoring, user activity monitoring)
- **DE.AE** — Adverse Event Analysis (event correlation, alert management, threat intelligence integration)

### RS — Respond

Develops and implements appropriate activities to take action regarding a detected cybersecurity incident.

Categories:
- **RS.MA** — Incident Management (incident response process, roles, communication)
- **RS.AN** — Incident Analysis (forensic analysis, attribution, scope determination)
- **RS.CO** — Incident Response Reporting and Communication (internal and external communication)
- **RS.MI** — Incident Mitigation (containment, eradication)

### RC — Recover

Develops and implements appropriate activities to maintain plans for resilience and to restore any capabilities or services impaired due to a cybersecurity incident.

Categories:
- **RC.RP** — Incident Recovery Plan Execution (recovery procedures, testing)
- **RC.CO** — Incident Recovery Communication (status updates, post-recovery communication)

## Implementation Tiers

CSF 2.0 defines four Tiers describing the rigor and sophistication of the organization's cybersecurity practices:

- **Tier 1: Partial** — risk management is ad-hoc, not formalized, and reactive
- **Tier 2: Risk Informed** — risk management practices are approved by management but not formally established as organizational-wide policy
- **Tier 3: Repeatable** — risk management practices are formally approved and expressed as policy, with regular updates
- **Tier 4: Adaptive** — the organization adapts its cybersecurity practices based on lessons learned and predictive indicators

Tiers are not target maturity levels — an organization should choose its target tier based on its risk tolerance, available resources, and the criticality of the systems being protected. A Tier 4 organization is not "better" than a Tier 2 organization; it is appropriate for a different risk context.

## Profiles

A CSF Profile is an organization's specific selection of Functions, Categories, and Subcategories from the framework, with priorities and target outcomes. Profiles let an organization tailor CSF to its specific situation:

- **Current Profile** — what the organization is currently doing for each Subcategory
- **Target Profile** — what the organization wants to be doing
- **Gap analysis** — the difference between current and target, which becomes the cybersecurity improvement roadmap

CSF 2.0 introduced **Community Profiles** — pre-built Profiles for specific sectors or use cases (e.g., manufacturing, election security, ransomware risk management). Community Profiles let an organization start from a sector-relevant baseline rather than building from scratch.

## Relationship to Other Frameworks

CSF is a high-level framework that maps onto more prescriptive control catalogs:

- **CSF Subcategories** map to **NIST SP 800-53** controls — most CSF Subcategories reference one or more 800-53 controls as the prescriptive implementation
- **CSF Functions** map to **ISO/IEC 27001** clauses and Annex A controls
- **CSF Categories** map to **CIS Critical Security Controls**
- **CSF** maps to **PCI-DSS** at a coarse level (PCI-DSS is more specific to cardholder data environments)
- **CSF** is a common cited reference in **SOC 2** Common Criteria implementations

The mapping is documented in the CSF 2.0 reference materials and is the standard way for an organization that is "doing CSF" to also satisfy the more specific framework requirements that customers or regulators care about.

## Common Implementation Patterns

### Adopting CSF 2.0 in a cloud-native organization

1. **Identify the systems in scope** — start with the most critical workloads (typically the production cloud accounts and the source code / build pipeline)
2. **Build a current profile** — for each Subcategory, document what is currently in place. This is the baseline.
3. **Build a target profile** — based on risk tolerance, decide which Subcategories should be improved and by how much
4. **Gap analysis** — the delta becomes a backlog of improvement work, prioritized by risk reduction per unit of effort
5. **Continuous improvement** — repeat the cycle annually, with the previous target becoming the new current

### Reporting on CSF to leadership

CSF Functions and Categories are at the right level of abstraction for executive reporting. A common dashboard shows:

- **Per-Function maturity score** (1–4) — how the organization rates against each Function
- **Top gaps** — the Subcategories with the largest delta from target
- **Recent improvements** — what has been implemented in the last quarter
- **Risk register** — open risks that have not yet been mitigated, with owners and expected resolution dates

The dashboard is typically reviewed quarterly with the CISO and shared with the board annually.

### Using Govern to drive accountability

The Govern function is the load-bearing part of CSF 2.0 because it makes the technical controls accountable to organizational leadership. Without Govern, the CISO can implement Protect, Detect, Respond, and Recover but cannot demonstrate that they align with the business's risk tolerance. Govern is what turns "we have controls" into "we have controls that the business has explicitly accepted as appropriate".

Practical implementation of Govern:

- **Risk appetite statement** — a written statement from the CEO/board defining how much cybersecurity risk the organization is willing to accept
- **Cybersecurity policy** — written policies derived from the risk appetite, with explicit ownership and review cadence
- **Roles and responsibilities matrix** — every cybersecurity activity has a named owner and an escalation path
- **Quarterly oversight reporting** — CISO presents to the executive team on the program's current state, gaps, and roadmap
- **Annual board reporting** — board receives a summary of the cybersecurity posture, including any material risks

## Common Decisions

- **CSF as the primary framework vs CSF as a reference** — primary when the organization wants a single high-level model that maps to others. Reference when the organization is already certified against a specific framework (ISO 27001, FedRAMP) and wants to use CSF for executive reporting only.
- **Implementation tier target** — Tier 3 (Repeatable) is the right target for most mid-to-large organizations. Tier 4 (Adaptive) is appropriate for organizations in high-threat sectors (financial services, critical infrastructure, defense). Tier 1 (Partial) is the starting state for organizations new to formal cybersecurity programs and is the natural state to grow out of, not a target.
- **Community Profile vs custom Profile** — Community Profile when one exists for the organization's sector or use case. Custom Profile when the sector-specific Profile does not fit, or when the organization has unusual risk considerations.
- **Govern function adoption** — adopt the Govern function explicitly as the bridge to executive engagement. Skipping Govern leaves the cybersecurity program technically sound but politically vulnerable.

## Reference Links

- [NIST CSF 2.0 main page](https://www.nist.gov/cyberframework)
- [NIST CSF 2.0 publication (NIST CSWP 29)](https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-20/final)
- [CSF 2.0 reference tool](https://csrc.nist.gov/Projects/Cybersecurity-Framework/Filters)
- [NIST CSF 2.0 quick start guides](https://www.nist.gov/cyberframework/getting-started)
- [Community Profiles](https://www.nist.gov/cyberframework/profiles)

## See Also

- `frameworks/nist-sp-800-53.md` — the prescriptive control catalog CSF maps to
- `frameworks/aws-well-architected.md` — AWS Well-Architected has a Security pillar that aligns with CSF Protect/Detect/Respond
- `general/security.md` — general security architecture
- `general/governance.md` — governance structures that support the CSF Govern function
- `compliance/iso-27001.md` — ISO 27001 has substantial overlap with CSF
