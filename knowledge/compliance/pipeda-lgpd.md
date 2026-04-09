# PIPEDA and LGPD — Canadian and Brazilian Privacy Laws

## Scope

This page covers two non-EU privacy regimes that frequently surface in cross-border engagements when GDPR coverage is the starting assumption but the actual jurisdiction is different: **PIPEDA** (the Canadian Personal Information Protection and Electronic Documents Act, in force since 2000 with substantial amendments under Bill C-27 still pending as of late 2025) and **LGPD** (the Brazilian Lei Geral de Proteção de Dados, in force since September 2020). Both are GDPR-influenced but have important differences from GDPR and from each other. Covers each law's applicability, the rights granted to data subjects, the obligations on controllers and processors, the cross-border transfer rules, the breach notification requirements, the cloud-relevant practical implementation patterns, and the relationship to GDPR for organizations that already handle GDPR compliance.

## PIPEDA (Canada)

### Applicability

PIPEDA applies to private-sector organizations that collect, use, or disclose personal information **in the course of commercial activities**. It applies federally and in provinces without substantially similar legislation. Quebec, BC, and Alberta have their own provincial laws (PIPA and Quebec's Law 25) that supersede PIPEDA for organizations operating only within those provinces.

PIPEDA also applies to **federally regulated private-sector organizations** (banks, telecommunications companies, airlines, broadcasters) regardless of province.

For an international organization with Canadian customers or Canadian operations, PIPEDA almost certainly applies — there is no minimum size threshold, and the "commercial activities" criterion is broadly interpreted.

### The 10 Fair Information Principles

PIPEDA is built around 10 principles drawn from the OECD privacy guidelines:

1. **Accountability** — the organization is responsible for personal information under its control
2. **Identifying purposes** — purposes for collection must be identified before or at collection
3. **Consent** — knowledge and consent of the individual are required
4. **Limiting collection** — collection is limited to what is necessary for the identified purposes
5. **Limiting use, disclosure, and retention** — use only for the identified purposes; retain only as long as necessary
6. **Accuracy** — personal information should be accurate, complete, and up-to-date
7. **Safeguards** — protect personal information appropriate to its sensitivity
8. **Openness** — make policies and practices regarding personal information available
9. **Individual access** — individuals can access and correct their personal information
10. **Challenging compliance** — individuals can challenge an organization's compliance

The principles are operationalized through written policies, training, and technical controls. PIPEDA does not prescribe specific technical safeguards (unlike GLBA's Safeguards Rule), but expects them to be commensurate with the sensitivity of the information.

### Breach Notification

PIPEDA requires notification of breaches that pose a **real risk of significant harm** (RROSH) to:

- The Office of the Privacy Commissioner of Canada (OPC) — as soon as feasible
- Affected individuals — as soon as feasible after the determination of RROSH
- Other organizations that may be able to mitigate the harm

The "real risk of significant harm" threshold means not every breach triggers notification — only those where the harm is meaningful (financial loss, identity theft, damage to reputation, loss of employment, negative effect on credit). The organization must conduct a risk assessment and document the result.

### Cross-Border Transfers

PIPEDA does not have explicit cross-border restrictions like GDPR's Chapter V. The Office of the Privacy Commissioner has issued guidance that:

- Personal information transferred to a third party (including a foreign one) for processing remains the responsibility of the original organization
- The original organization must ensure comparable protection by the third party (typically via contract)
- Individuals should be informed that their information may be transferred for processing

The practical effect is that an organization can transfer Canadian personal information to a US-based cloud provider for processing as long as it has a contract with the provider that provides comparable protection. This is a much simpler regime than GDPR's adequacy / SCC / BCR framework.

### Bill C-27 (pending)

Bill C-27, the Digital Charter Implementation Act, is pending in the Canadian Parliament as of late 2025. If enacted, it will:

- Replace PIPEDA with a more GDPR-aligned **Consumer Privacy Protection Act (CPPA)**
- Add monetary penalties (up to $25M CAD or 5% of global revenue for serious violations)
- Add a private right of action
- Strengthen the OPC's enforcement powers
- Add the Artificial Intelligence and Data Act (AIDA) for AI governance

The exact form of the final legislation has been in flux. Organizations subject to PIPEDA should monitor the C-27 status and prepare for the additional obligations, particularly the monetary penalty regime.

## LGPD (Brazil)

### Applicability

LGPD applies to any processing of personal data:

- Carried out within Brazilian territory
- For the purpose of offering or providing goods or services to individuals in Brazil
- Of personal data collected in Brazil

This is a broad extraterritorial scope similar to GDPR. An organization based outside Brazil but with Brazilian customers is subject to LGPD.

LGPD applies to natural persons and legal entities that process personal data, with an exception for processing for personal, journalistic, artistic, academic, or strictly defensive purposes.

### Legal Bases for Processing

LGPD lists 10 legal bases for processing personal data — broader than GDPR's 6 bases:

1. **Consent** of the data subject
2. **Compliance with a legal obligation** of the controller
3. **Public administration** for the execution of public policies
4. **Studies by a research entity** (with anonymization where possible)
5. **Execution of a contract** or preliminary procedures related to a contract
6. **Regular exercise of rights** in legal, administrative, or arbitration proceedings
7. **Protection of life or physical safety** of the data subject or third party
8. **Health protection** in procedures performed by health professionals
9. **Legitimate interests** of the controller or third party (subject to balancing test)
10. **Credit protection**

The "credit protection" basis is unique to LGPD and reflects the importance of credit reporting in the Brazilian financial system.

### Data Subject Rights

LGPD grants data subjects rights similar to GDPR:

- **Confirmation** that data is being processed
- **Access** to the data
- **Correction** of inaccurate or incomplete data
- **Anonymization, blocking, or deletion** of unnecessary or non-compliant data
- **Portability** of the data to another service or product provider
- **Deletion** of data processed with consent (with some exceptions)
- **Information** about public and private entities with which the data has been shared
- **Information** about the possibility of denying consent and the consequences
- **Revocation of consent**

### Cross-Border Transfers

LGPD restricts international transfers of personal data, with several mechanisms allowed:

- **Adequacy decision** by the Brazilian National Data Protection Authority (ANPD) — similar to GDPR adequacy
- **Specific safeguards** — standard contractual clauses, binding corporate rules, certifications, or codes of conduct (not yet published by the ANPD as of late 2025)
- **Consent** of the data subject
- **Necessity for contract execution** with the data subject
- **Necessity for life or physical safety** protection
- **International cooperation** between public bodies
- **Specific authorization** from the ANPD

The mechanism most commonly used in practice is **standard contractual clauses**, even though the ANPD has not yet finalized the model clauses — most organizations use clauses that mirror GDPR SCCs.

### Breach Notification

LGPD requires notification of breaches that pose risk or relevant damage to data subjects:

- **To the ANPD** — within a "reasonable" timeframe (the ANPD has indicated 2 business days as the expectation, though this is not codified)
- **To affected data subjects** — within a "reasonable" timeframe

The notification must include the nature of the affected data, the data subjects involved, the technical and security measures used, the risks, the reasons for delay (if any), and the measures adopted in response.

### Penalties

LGPD penalties are imposed by the ANPD:

- **Warning** with a corrective action deadline
- **Simple fine** up to 2% of revenue from the previous year (capped at R$50M per violation, ~$10M USD)
- **Daily fine** for ongoing violations
- **Public disclosure** of the violation
- **Blocking or deletion** of the personal data
- **Suspension or prohibition** of processing activities

The first significant LGPD enforcement actions occurred in 2022–2023 and have been escalating since.

## Comparison Table

| Aspect | PIPEDA (current) | LGPD |
|---|---|---|
| Effective | 2000 (amended periodically) | September 2020 |
| Extraterritorial scope | Limited (commercial activities in Canada) | Yes (broad, similar to GDPR) |
| Legal bases for processing | Consent-centric | 10 bases including legitimate interests |
| Data subject rights | 9 (access, correction, withdrawal of consent) | 9 (similar to GDPR) |
| Breach notification timeline | "As soon as feasible" with RROSH threshold | "Reasonable" (~2 business days expected) |
| Cross-border transfer mechanism | Contract with comparable protection | Adequacy / SCC / consent / specific authorization |
| Penalties (current) | None for PIPEDA violations specifically; OPC can name and shame | Up to 2% of revenue, R$50M cap per violation |
| Penalties (pending C-27) | Up to $25M CAD or 5% of global revenue | (no change pending) |
| GDPR alignment | Less aligned (especially without C-27) | More aligned, but distinctly Brazilian |

## Architect Checklist

- [ ] **[Critical]** **Determine which laws apply** based on data subjects' locations and the organization's commercial activities. Many international organizations are subject to GDPR + PIPEDA + LGPD + state-level US laws simultaneously.
- [ ] **[Critical]** **Maintain a records of processing activities** that satisfies the most stringent applicable framework (typically GDPR Article 30). The same records can be used for LGPD and PIPEDA.
- [ ] **[Critical]** **Document the legal basis for each processing activity** under each applicable law. The legal basis can differ between GDPR, LGPD, and PIPEDA for the same processing.
- [ ] **[Critical]** **Implement data subject rights workflows** that handle access, correction, deletion, and portability requests within the deadlines required by each law. A unified workflow is more efficient than per-law workflows.
- [ ] **[Critical]** **Establish breach notification capability** that can produce notifications within the timelines required by each law. The shortest timeline (typically GDPR 72 hours, LGPD ~2 business days) is the operational target.
- [ ] **[Critical]** **Document cross-border transfers** with the legal mechanism for each. Use SCC-equivalent contracts for GDPR + LGPD + PIPEDA transfers from EU/Canada/Brazil to other jurisdictions.
- [ ] **[Recommended]** **Use a single privacy program** that satisfies the most stringent applicable framework rather than maintaining separate compliance programs. The cost of overlap is lower than the cost of distinct programs.
- [ ] **[Recommended]** **Appoint a Data Protection Officer (DPO)** if required by GDPR; the same individual can serve as the LGPD DPO (Encarregado).
- [ ] **[Recommended]** **Train staff on the privacy obligations** with examples relevant to their role. Generic privacy training is less effective than role-specific.
- [ ] **[Optional]** **Subscribe to ANPD and OPC announcements** for regulatory updates. Both authorities publish guidance and enforcement actions periodically.

## Cloud Service Mapping

| Privacy Obligation | AWS | Azure | GCP |
|---|---|---|---|
| Data residency | Regional services, data residency commitments | Regional services, data residency add-ons | Regional services, dual-region storage |
| Encryption at rest | KMS with customer-managed keys | Key Vault with customer-managed keys | Cloud KMS with customer-managed keys |
| Access control | IAM, IAM Identity Center | Entra ID with Conditional Access | Cloud IAM, IAP |
| Audit trail | CloudTrail, Config | Activity Log, Defender | Cloud Audit Logs, SCC |
| Data subject access | DynamoDB / RDS / S3 query patterns | SQL / Cosmos DB query patterns | BigQuery / Cloud SQL query patterns |
| Data deletion | S3 lifecycle rules, RDS delete, Glue retention | Storage lifecycle, SQL DELETE, Purview retention | Storage lifecycle, BigQuery DELETE, time travel |
| Cross-border transfer agreements | AWS Data Processing Addendum | Microsoft Data Protection Addendum | Google Cloud Data Processing Addendum |

## Common Decisions (ADR Triggers)

- **Single privacy program vs per-jurisdiction programs** — single program built around the most stringent requirements is the right answer for most multi-jurisdictional organizations.
- **Use GDPR as the baseline** — for organizations subject to GDPR + LGPD + PIPEDA, GDPR is typically the most stringent and serves as the implementation baseline. LGPD and PIPEDA are then satisfied via the GDPR controls with minor additions.
- **Data residency strategy** — for highly sensitive data, store it in the jurisdiction of the data subject (EU data in EU, Canadian data in Canada, Brazilian data in Brazil). For less sensitive data, the cross-border transfer mechanisms may make multi-region storage acceptable.
- **DPO appointment** — required by GDPR for some organizations, by LGPD for all controllers (though enforcement is loose), and not required by PIPEDA. A single DPO can serve all three roles.
- **Vendor due diligence depth** — annual questionnaires for low-risk processors, formal audit reports for high-risk processors. Apply the same standard regardless of the underlying privacy regime.

## Reference Links

- [PIPEDA (Office of the Privacy Commissioner of Canada)](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/)
- [Bill C-27 (Digital Charter Implementation Act)](https://www.parl.ca/legisinfo/en/bill/44-1/c-27)
- [LGPD official text (Portuguese)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13709.htm)
- [LGPD English translation (IAPP)](https://iapp.org/resources/article/brazilian-data-protection-law-lgpd-english-translation/)
- [Brazilian National Data Protection Authority (ANPD)](https://www.gov.br/anpd/pt-br)

## See Also

- `compliance/gdpr.md` — GDPR, the framework most commonly used as the implementation baseline
- `compliance/ccpa.md` — California Consumer Privacy Act, the US state-level equivalent
- `frameworks/nist-csf-2.0.md` — NIST CSF as the underlying security framework
- `failures/compliance.md` — compliance failure patterns
- `general/data-classification.md` — data classification as the foundation for privacy controls
