# NIS2 Directive — Cloud Control Mapping

## Scope

Covers the EU Network and Information Security Directive 2 (NIS2, formally Directive (EU) 2022/2555), the EU-wide cybersecurity regulation effective from October 2024. NIS2 expanded the scope of the original NIS Directive (2016) substantially: it now applies to "essential" and "important" entities across 18 sectors, with mandatory cybersecurity risk management measures, incident reporting obligations, governance accountability for management bodies, and significant penalties for non-compliance. Covers the entity classification (essential vs important), the 10 risk management measures required by Article 21, the 24-hour incident notification requirement, the supply chain security obligations, the enforcement and penalty regime, and the practical implementation patterns for cloud workloads. Does not cover the original NIS Directive (superseded) or sector-specific implementations beyond NIS2 itself.

## Applicability

NIS2 applies to two categories of entities:

### Essential Entities (Annex I sectors)

- **Energy** — electricity, district heating and cooling, oil, gas, hydrogen
- **Transport** — air, rail, water, road
- **Banking** — credit institutions
- **Financial market infrastructures** — trading venues, central counterparties
- **Health** — healthcare providers, EU reference laboratories, pharmaceutical manufacturers
- **Drinking water** — suppliers and distributors
- **Wastewater** — collection, disposal, treatment
- **Digital infrastructure** — IXPs, DNS service providers (excluding root name servers), TLD registries, cloud computing service providers, data centre service providers, content delivery networks, trust service providers, public electronic communications networks/services
- **ICT service management** — managed service providers, managed security service providers
- **Public administration** — central and regional government entities
- **Space** — operators of ground-based infrastructure

### Important Entities (Annex II sectors)

- **Postal and courier services**
- **Waste management**
- **Manufacture, production and distribution of chemicals**
- **Production, processing and distribution of food**
- **Manufacturing** — medical devices, computer/electronic/optical products, electrical equipment, machinery, motor vehicles
- **Digital providers** — online marketplaces, online search engines, social networking platforms
- **Research organisations**

### Size thresholds

- **Essential**: applies to large entities (≥250 employees OR €50M turnover) in Annex I sectors. Some entities are essential regardless of size (DNS providers, TLDs, public electronic communications, trust service providers, etc.).
- **Important**: applies to medium-sized entities (50–250 employees OR €10–50M turnover) in Annex I sectors, AND to large entities in Annex II sectors.
- **Excluded**: micro and small entities (<50 employees and <€10M turnover), unless explicitly designated.

If a customer or partner is an essential or important entity, the supply chain security obligations (below) flow through to suppliers — including cloud providers, SaaS vendors, and managed service providers — even if those suppliers are not themselves NIS2 entities.

## The 10 Risk Management Measures (Article 21)

NIS2 requires entities to implement "appropriate and proportionate technical, operational and organisational measures". Article 21 enumerates 10 minimum measures:

1. **Risk analysis and information system security policies** — formal risk assessment and documented security policies
2. **Incident handling** — incident response procedures, including detection, analysis, containment, eradication, recovery
3. **Business continuity** — backup management, disaster recovery, crisis management
4. **Supply chain security** — assessment of suppliers' security practices, including direct suppliers and service providers
5. **Security in network and information systems acquisition, development and maintenance** — including vulnerability handling and disclosure
6. **Policies and procedures to assess the effectiveness of cybersecurity risk-management measures**
7. **Basic cyber hygiene practices and cybersecurity training**
8. **Policies and procedures regarding the use of cryptography and, where appropriate, encryption**
9. **Human resources security, access control policies and asset management**
10. **The use of multi-factor authentication or continuous authentication solutions, secured voice, video and text communications and secured emergency communication systems within the entity, where appropriate**

These are the minimum baseline. Each member state may impose additional requirements via national transposition.

## Incident Reporting Obligations

NIS2 requires entities to report **significant incidents** to their national CSIRT or competent authority on a strict timeline:

| Phase | Deadline | Content |
|---|---|---|
| **Early warning** | Within 24 hours of becoming aware | Initial notification, including whether the incident is suspected to be malicious or could have cross-border impact |
| **Incident notification** | Within 72 hours of becoming aware | Updated assessment with severity, impact, indicators of compromise |
| **Final report** | Within 1 month of the incident notification | Detailed description, root cause analysis, mitigation measures applied, cross-border impact (if any) |

A "significant incident" is one that has caused or is capable of causing severe operational disruption, financial loss, or material damage to individuals or organisations.

The 24-hour clock is the most operationally consequential element of NIS2 — it requires a defined incident response process that can produce an authoritative report within hours of detection, not days. This is faster than GDPR's 72-hour breach notification requirement.

## Supply Chain Security (Article 21(2)(d))

NIS2 explicitly requires entities to assess the security practices of their suppliers and service providers, including:

- **Direct suppliers** — software vendors, hardware vendors, cloud providers, managed service providers
- **Service providers** — including cloud computing services, data centres, content delivery networks
- **Open source dependencies** — to the extent that the entity relies on open source software for critical functions

The assessment should consider:

- The supplier's security posture (certifications, audit reports, security testing)
- The supplier's incident response capabilities
- The supplier's known vulnerabilities and patches
- The criticality of the supplier to the entity's operations

This obligation flows downstream — a NIS2-regulated entity will require its cloud provider and SaaS vendors to provide evidence of their own security practices, and will likely include NIS2-related clauses in contracts.

## Governance Accountability (Article 20)

NIS2 places direct accountability for cybersecurity on the **management bodies** of entities. Specifically:

- Management bodies must approve the cybersecurity risk management measures
- Management bodies must oversee implementation
- Management bodies must follow training to gain sufficient knowledge to identify risks and assess cybersecurity risk-management practices
- **Members of management bodies can be held personally liable** for failures to comply

This is a significant change from previous frameworks where cybersecurity was treated as a CISO responsibility. Under NIS2, the CISO advises but the board owns the decisions.

## Cloud Service Mapping

| NIS2 Measure | AWS | Azure | GCP |
|---|---|---|---|
| Risk analysis | AWS Audit Manager, Trusted Advisor | Microsoft Defender for Cloud, Microsoft Purview | Security Command Center, Compliance Reports Manager |
| Incident handling | GuardDuty, Detective, Security Hub | Microsoft Sentinel, Defender for Cloud | Security Command Center, Chronicle |
| Business continuity | AWS Backup, Cross-region replication, Disaster recovery patterns | Azure Backup, Site Recovery, paired regions | Cloud Backup, regional persistent disks |
| Supply chain security | AWS Marketplace vetting, Inspector for software composition | Microsoft Supply Chain Security, Defender for DevOps | Software Delivery Shield, Container Analysis |
| Cryptography | KMS, ACM, Secrets Manager | Key Vault, Managed HSM | Cloud KMS, Secret Manager |
| MFA / continuous auth | IAM Identity Center, Verified Access | Entra ID with Conditional Access | Cloud Identity, Identity-Aware Proxy |
| Network security | VPC, Security Groups, Network Firewall, WAF | NSG, Azure Firewall, Front Door WAF | VPC firewall rules, Cloud Armor, Cloud NGFW |
| Logging and monitoring | CloudTrail, CloudWatch, GuardDuty, Security Hub | Activity Log, Monitor, Sentinel | Cloud Audit Logs, Cloud Logging, SCC |

## Architect Checklist

- [ ] **[Critical]** **Determine if NIS2 applies.** Check sector (Annex I or II), size (large vs medium), and country of operation. Most cloud-heavy organizations are now in scope due to NIS2's expanded sectoral coverage.
- [ ] **[Critical]** **Identify the competent authority** for the country of primary establishment. NIS2 is implemented per member state with local CSIRTs and regulators.
- [ ] **[Critical]** **Document the risk management measures** that satisfy each of the 10 Article 21 requirements. Map existing controls (from CIS Benchmarks, NIST CSF, ISO 27001, SOC 2) onto the NIS2 measures.
- [ ] **[Critical]** **Establish the 24-hour incident reporting capability.** Define the incident classification, the reporting workflow, and the named individuals responsible for the early warning notification. Test it with a fire drill.
- [ ] **[Critical]** **Conduct supply chain security assessments** for all critical third-party providers. Document the assessment, the findings, and the contractual flow-down clauses.
- [ ] **[Critical]** **Train management bodies** on cybersecurity risk management. Document the training (date, content, attendees) as evidence of compliance with Article 20.
- [ ] **[Recommended]** **Implement multi-factor authentication** for all privileged access and for any remote access to information systems handling regulated data. NIS2 explicitly mentions MFA in Article 21(2)(j).
- [ ] **[Recommended]** **Enable cryptographic protection** for data at rest and in transit, with a documented key management policy.
- [ ] **[Recommended]** **Maintain an incident register** documenting all significant incidents, the response actions, and the lessons learned. This is the audit artifact that demonstrates the incident handling control is operating.
- [ ] **[Recommended]** **Subscribe to the national CSIRT's threat intelligence feed** if available. NIS2 promotes information sharing between entities and CSIRTs as a key mechanism for collective cybersecurity.
- [ ] **[Optional]** **Map NIS2 measures to ISO 27001 / SOC 2 / NIST CSF** if the organization is already certified against one of those frameworks. The mapping reduces duplication of evidence and reuses existing controls.

## Penalties

NIS2 introduces significant administrative fines:

- **Essential entities**: up to **€10M** or **2% of annual worldwide turnover**, whichever is higher
- **Important entities**: up to **€7M** or **1.4% of annual worldwide turnover**, whichever is higher
- **Personal liability**: members of management bodies can be temporarily prohibited from exercising managerial functions in the entity

The penalty regime is aligned with GDPR in terms of magnitude and is designed to make non-compliance materially costly.

## Common Decisions (ADR Triggers)

- **Determine entity classification** — essential vs important vs out-of-scope. The classification drives the obligation severity.
- **Choose the competent authority** — for entities operating in multiple member states, NIS2 specifies that the entity is supervised by the member state of its main establishment. Document the choice.
- **Adopt an existing framework as the implementation baseline** — ISO 27001, NIST CSF 2.0, or CIS Critical Security Controls are common starting points. NIS2 does not prescribe a specific framework but accepts compliance via demonstration of risk management measures.
- **Centralized vs federated incident response** — centralized (a single incident response team handling all incidents across the org) for organizations with consistent processes. Federated (per-business-unit IR teams with central oversight) for larger organizations.
- **Supply chain assessment depth** — annual questionnaires for low-criticality suppliers, formal audits for high-criticality. Document the criteria for tiering.

## Reference Links

- [Directive (EU) 2022/2555 (NIS2 official text)](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)
- [ENISA NIS2 guidance](https://www.enisa.europa.eu/topics/nis-directive)
- [Member state implementation status](https://www.enisa.europa.eu/topics/nis-directive/nis-visual-tool)

## See Also

- `compliance/gdpr.md` — GDPR has parallel breach notification requirements and overlapping scope
- `compliance/iso-27001.md` — ISO 27001 is a common framework for satisfying NIS2 risk management measures
- `frameworks/nist-csf-2.0.md` — NIST CSF maps onto NIS2 measures and is acceptable as the implementation framework
- `failures/compliance.md` — compliance failure patterns
- `failures/operations.md` — incident handling failure patterns
