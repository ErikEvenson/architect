# GLBA — Gramm-Leach-Bliley Act

## Scope

The Gramm-Leach-Bliley Act (GLBA, also known as the Financial Services Modernization Act of 1999) is a US federal law that requires financial institutions to protect the security and confidentiality of consumer financial information. GLBA has three principal rules: the **Privacy Rule** (notification and opt-out requirements), the **Safeguards Rule** (information security program requirements), and the **Pretexting Provisions** (prohibition on social engineering to obtain customer information). The Safeguards Rule is the most relevant for cloud workloads — it was significantly updated by the FTC in 2021 and now includes specific technical and organizational requirements that mirror many other frameworks (encryption, MFA, access controls, vendor oversight). Covers GLBA applicability, the Safeguards Rule requirements, the relationship to other frameworks (PCI-DSS, SOC 2, NY DFS), the cloud service mapping, and the practical implementation patterns. Often paired with PCI-DSS for financial services workloads handling card data.

## Applicability

GLBA applies to **financial institutions** as defined under federal law:

- **Banks, savings institutions, credit unions** (regulated by federal banking agencies)
- **Insurance companies** (regulated by state insurance regulators)
- **Securities firms, broker-dealers, investment advisers** (regulated by SEC and FINRA)
- **Mortgage lenders, finance companies, payday lenders** (regulated by the FTC under GLBA)
- **Tax preparation firms, debt collectors, real estate appraisers** (also regulated by the FTC)
- **"Significantly engaged in" providing financial products or services** (a broad catch-all that the FTC has used to bring fintech and adjacent businesses into scope)

The FTC has broad authority over GLBA enforcement for non-bank financial institutions, while federal banking agencies (OCC, FDIC, FRB) enforce GLBA for banks.

## The Safeguards Rule (16 CFR Part 314)

The Safeguards Rule requires financial institutions to develop, implement, and maintain a **comprehensive written information security program** (WISP) that includes administrative, technical, and physical safeguards appropriate to the institution's size, complexity, and the nature of its activities.

The 2021 update added specific elements that the WISP must address:

### Required elements (post-2021)

1. **Designate a qualified individual** to oversee the information security program
2. **Conduct a written risk assessment** identifying foreseeable risks to customer information
3. **Design and implement safeguards** to control identified risks, including:
   - **Access controls** based on least privilege
   - **Asset inventory** of systems handling customer information
   - **Encryption** of customer information in transit over external networks and at rest
   - **Secure development practices** for in-house developed applications
   - **Multi-factor authentication** for any individual accessing customer information
   - **Data disposal** procedures for customer information no longer needed
   - **Change management** procedures
   - **Monitoring and logging** of authorized user activity
4. **Regularly test or monitor** the safeguards (continuous monitoring or periodic penetration testing and vulnerability assessment)
5. **Train staff** on the safeguards
6. **Oversee service providers** through:
   - Due diligence in selection
   - Contractual requirements for safeguards
   - Periodic assessment of provider security
7. **Establish written incident response plan** for unauthorized access or use of customer information
8. **Submit annual reports to the board** on the state of the information security program

The 2021 update made GLBA significantly more prescriptive than the original 2003 version. Many of the new requirements parallel the PCI-DSS Requirement 1–12 structure or the NIST CSF Functions, which means an organization that is already PCI-compliant or NIST CSF-aligned has a head start on GLBA compliance.

## The Privacy Rule (16 CFR Part 313)

The Privacy Rule is less technical than the Safeguards Rule but has its own requirements:

- **Privacy notice** at the start of the customer relationship and annually
- **Opt-out** rights for customers who do not want their nonpublic personal information shared with non-affiliated third parties
- **Restrictions on disclosure** to non-affiliated third parties (with some exceptions)
- **Reuse and re-disclosure** restrictions on third parties that receive information

The Privacy Rule does not impose specific technical requirements; it is mostly about disclosures and operational handling.

## Cloud Service Mapping

| Safeguards Rule Element | AWS | Azure | GCP |
|---|---|---|---|
| Encryption at rest | KMS, S3 SSE, EBS encryption, RDS encryption | Key Vault, Storage SSE, SQL TDE, Disk Encryption | Cloud KMS, Cloud Storage CMEK, BigQuery CMEK, Persistent Disk CMEK |
| Encryption in transit | ACM, ELB TLS termination | Front Door TLS, Application Gateway TLS | Cloud Load Balancing TLS |
| MFA | IAM Identity Center MFA enforcement | Entra ID MFA via Conditional Access | Cloud Identity 2-step verification |
| Access controls | IAM with PIM-equivalent (Identity Center sessions) | Azure RBAC with PIM | IAM with conditional bindings |
| Logging and monitoring | CloudTrail, Security Hub, GuardDuty | Activity Log, Defender for Cloud, Sentinel | Cloud Audit Logs, Security Command Center |
| Asset inventory | AWS Config, Resource Explorer | Azure Resource Graph, Defender for Cloud | Cloud Asset Inventory |
| Secure development | CodeGuru, Inspector for Lambda | Defender for DevOps, GitHub Advanced Security | Software Delivery Shield, Container Analysis |
| Vendor oversight | AWS Marketplace, AWS Audit Manager | Microsoft Compliance Manager | Compliance Reports Manager |
| Incident response | GuardDuty, Detective | Sentinel, Defender for Cloud | Security Command Center, Chronicle |

## Architect Checklist

- [ ] **[Critical]** **Determine GLBA applicability**. Cloud workloads holding customer financial information for a financial institution are in scope. Note that the FTC's expanded interpretation can bring fintech, prop-tech, and other adjacent businesses into scope.
- [ ] **[Critical]** **Designate the qualified individual** responsible for the information security program. This is typically the CISO or equivalent. Document the designation in writing.
- [ ] **[Critical]** **Conduct a written risk assessment** covering foreseeable risks to customer information. Update annually or when significant changes occur.
- [ ] **[Critical]** **Implement encryption** for customer information in transit (TLS 1.2+) and at rest (AES-256 or equivalent). Customer-managed keys are not required by GLBA but are recommended for the audit trail benefit.
- [ ] **[Critical]** **Enforce MFA** for any individual accessing customer information. The 2021 update made this explicit and is one of the most common findings in GLBA examinations.
- [ ] **[Critical]** **Maintain an asset inventory** of every system that handles customer information. Cloud-native asset inventory tools (AWS Config, Azure Resource Graph, GCP Cloud Asset Inventory) provide the data; the inventory is the artifact.
- [ ] **[Critical]** **Establish written incident response plan** with the specific elements GLBA requires (response to unauthorized access or use of customer information). Test annually.
- [ ] **[Critical]** **Oversee service providers** with due diligence at selection and periodic re-assessment. Document the assessment criteria and the results. Cloud providers themselves are service providers and should be assessed.
- [ ] **[Recommended]** **Conduct annual penetration testing** and continuous monitoring. The Safeguards Rule allows either continuous monitoring or periodic testing; continuous monitoring is the modern best practice.
- [ ] **[Recommended]** **Train staff annually** on information security responsibilities. Document the training (date, content, attendees).
- [ ] **[Recommended]** **Submit annual board reports** on the information security program. The board's involvement is required by the Safeguards Rule.
- [ ] **[Optional]** **Align with NIST CSF or ISO 27001** as the underlying framework. GLBA does not prescribe a specific framework but maps cleanly onto either.

## Penalties

GLBA enforcement is split between agencies:

- **FTC** can bring civil enforcement actions for violations, with penalties up to ~$50K per violation (adjusted for inflation; per-violation can be calculated per consumer affected, leading to large totals)
- **Federal banking agencies** can impose enforcement actions including civil money penalties, cease-and-desist orders, and director removals
- **State attorneys general** can also enforce GLBA in many states

The 2023 amendment added breach notification requirements: financial institutions must notify the FTC of a "notification event" (unauthorized acquisition of unencrypted customer information of 500+ consumers) within 30 days.

## Common Decisions (ADR Triggers)

- **Single-framework approach (GLBA only) vs multi-framework approach** — multi-framework is the right answer for most financial institutions because GLBA requirements largely overlap with PCI-DSS, SOC 2, and NIST CSF. Pick a primary framework and demonstrate GLBA compliance via the primary framework's controls.
- **Customer information classification** — define "customer information" explicitly. The definition includes financial transaction data, PII collected during the financial relationship, and information derived from those.
- **Encryption scope** — encrypt all customer information at rest, even if the regulation does not strictly require it for internal storage. The audit posture of "everything is encrypted" is dramatically simpler than "encryption is selective".
- **Service provider depth of assessment** — annual questionnaire for low-risk service providers, formal audit reports (SOC 2 Type II) for high-risk service providers. Document the criteria for tiering.
- **Penetration testing cadence** — annual is the minimum. Quarterly is more typical for higher-risk environments. Internal penetration testing supplemented by annual external testing is the typical pattern.

## Reference Links

- [Gramm-Leach-Bliley Act (15 USC §6801 et seq.)](https://www.law.cornell.edu/uscode/text/15/chapter-94)
- [FTC Safeguards Rule (16 CFR Part 314)](https://www.ftc.gov/legal-library/browse/rules/safeguards-rule)
- [FTC Privacy Rule (16 CFR Part 313)](https://www.ftc.gov/legal-library/browse/rules/financial-privacy-rule)
- [Federal banking agency interagency guidelines](https://www.fdic.gov/resources/supervision-and-examinations/consumer-compliance-examination-manual/documents/8/viii-1-1.pdf)
- [FTC Safeguards Rule Final Rule (2021 amendment)](https://www.ftc.gov/news-events/news/press-releases/2021/10/ftc-strengthens-security-safeguards-consumer-financial-information)

## See Also

- `compliance/pci-dss.md` — PCI-DSS, often paired with GLBA for payment card data
- `compliance/sox.md` — SOX, the financial reporting controls framework, often paired with GLBA
- `compliance/soc2.md` — SOC 2, the standard service provider attestation
- `frameworks/nist-csf-2.0.md` — NIST CSF as the implementation framework for GLBA
- `failures/compliance.md` — compliance failure patterns
