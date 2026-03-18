# Data Classification Frameworks and Handling Requirements

## Scope

This file covers **data classification frameworks, labeling standards, and per-level handling requirements** -- the decision framework for selecting classification levels, applying labels consistently, enforcing handling controls (encryption, access, DLP, audit), and managing data through its lifecycle based on sensitivity. This is cloud-agnostic and applies to on-premises, hybrid, and multi-cloud environments. For general data architecture, see `general/data.md`. For security architecture, see `general/security.md`. For compliance-specific requirements that drive classification (PCI, HIPAA, GDPR), see the relevant file in `compliance/`. For identity and access management that enforces classification-based access, see `general/identity.md`.

## Checklist

### Classification Framework Selection

- [ ] **[Critical]** Is a classification framework selected and formally adopted? Options: organizational custom (most flexibility, most effort to maintain), government standard such as NIST SP 800-60 or FIPS 199 (required for federal work, well-defined), industry-driven such as PCI DSS data categories (required for cardholder data), or a hybrid that maps organizational levels to regulatory requirements. The framework must be documented, approved by leadership, and enforceable -- not aspirational.
- [ ] **[Critical]** Are classification levels defined with clear, unambiguous criteria? A typical four-tier model: **Public** (no impact if disclosed), **Internal** (minor business impact), **Confidential** (significant business or legal impact), **Restricted** (severe regulatory, legal, or safety impact -- includes PII under GDPR, PHI under HIPAA, cardholder data under PCI, classified data under government standards). Each level must have concrete examples so that data owners can classify without guessing.
- [ ] **[Recommended]** Is a data owner assigned for every data asset or data domain? Classification decisions belong to data owners (business stakeholders), not IT. IT enforces the controls; the business decides the sensitivity. Without clear ownership, data defaults to the lowest classification and is undertreated, or defaults to the highest and is overtreated (driving up cost and friction).

### Labeling and Discovery

- [ ] **[Critical]** Is a labeling standard defined that specifies how classification is expressed? Options: metadata tags on files and database columns, document headers/footers and watermarks, email subject-line prefixes, storage container naming conventions, or API response headers. The standard must be machine-readable (not just visual) so that automated tools can enforce handling rules.
- [ ] **[Recommended]** Are automated classification and discovery tools evaluated or deployed? Options: Microsoft Purview (Azure-native, supports sensitivity labels across M365 and Azure), AWS Macie (S3-focused, PII/financial data detection), Google Cloud DLP (API-driven, supports structured and unstructured data), or third-party tools such as BigID, Varonis, or Spirion. Automated tools catch data that humans miss -- especially unstructured data in file shares, email, and collaboration platforms.
- [ ] **[Optional]** Is there a process for reclassification? Data sensitivity changes over time -- quarterly earnings are Restricted before public release and Public afterward. A merger target list is Restricted during negotiations and Internal after announcement. The framework must support reclassification with an audit trail.

### Handling Requirements Per Level

- [ ] **[Critical]** Are encryption requirements defined per classification level? At minimum: Confidential and Restricted data must be encrypted at rest (AES-256 or equivalent) and in transit (TLS 1.2+). Restricted data may require additional controls such as customer-managed encryption keys (CMEK), hardware security modules (HSM), or envelope encryption. Public and Internal data should still use encryption in transit as a baseline.
- [ ] **[Critical]** Are access control requirements defined per classification level? Restricted data requires role-based access with least privilege, multi-factor authentication, and periodic access reviews. Confidential data requires role-based access and documented authorization. Internal data requires authentication. Public data has no access restrictions but still requires integrity controls to prevent tampering.
- [ ] **[Critical]** Are audit and logging requirements defined per classification level? Restricted data requires full access logging (who accessed what, when, from where), with tamper-evident log storage and real-time alerting on anomalous access. Confidential data requires access logging with periodic review. Internal and Public data require standard operational logging.
- [ ] **[Recommended]** Are data loss prevention (DLP) controls mapped to classification levels? DLP policies should block or alert on Restricted data leaving approved boundaries (e.g., emailing Restricted data externally, copying to USB, uploading to unapproved cloud storage). Confidential data should trigger alerts but may not block. DLP is only effective if classification labels are applied consistently -- DLP without labeling is guesswork.

### Data Sovereignty, Lifecycle, and Cross-Boundary Flows

- [ ] **[Critical]** Are data residency and sovereignty requirements documented per classification level? Restricted data may be legally required to remain within specific geographic boundaries (GDPR for EU personal data, data localization laws in Russia, China, India, etc.). Even without legal mandates, organizational policy may restrict where Confidential data can be stored or processed. Cloud region selection, backup replication targets, and CDN edge caches must all comply.
- [ ] **[Recommended]** Are data lifecycle requirements defined per classification level? Retention: how long must data be kept (regulatory minimums for financial records, healthcare records, etc.)? Archival: when does data move to cold storage and under what access restrictions? Disposal: how is data destroyed (cryptographic erasure, physical destruction of media, certificate of destruction)? Restricted data disposal typically requires documented proof of destruction.
- [ ] **[Recommended]** Are cross-classification data flow rules defined? When Restricted data is ingested by a system that also handles Internal data, the entire system inherits the highest classification (high-water mark principle) unless data is properly segmented. Define rules for: data aggregation that changes classification (individual records are Internal, aggregated dataset is Confidential), data transformation that strips sensitive fields (Restricted source becomes Internal derivative), and data sharing across trust boundaries.

### Organizational Readiness

- [ ] **[Recommended]** Is a training and awareness program in place for data classification? Classification is only effective if the people creating and handling data understand it. Training must cover: how to classify new data, how to recognize misclassified data, what handling rules apply at each level, and how to report suspected mishandling. Annual training with role-specific modules (developers, data engineers, executives, third-party contractors).
- [ ] **[Recommended]** Are incident response procedures differentiated by classification level? A breach of Public data is a non-event. A breach of Internal data is an operational incident. A breach of Confidential data triggers legal review and potential notification. A breach of Restricted data triggers regulatory notification (72 hours under GDPR, state breach notification laws), executive escalation, forensic investigation, and potentially public disclosure. The incident response plan must map classification levels to response severity.

## Why This Matters

Data classification is the foundation that every other security control depends on. Encryption policies, access control rules, DLP configurations, backup retention periods, incident response severity levels, and compliance audit scopes all derive from how data is classified. Without a functioning classification framework, organizations apply controls inconsistently -- over-protecting low-value data (wasting money and creating friction) while under-protecting high-value data (creating breach risk). The most common failure mode is having a classification policy on paper that nobody follows in practice.

The second most common failure is treating classification as a one-time labeling exercise rather than an operational discipline. Data is created continuously, and new data must be classified at creation. Automated discovery tools find existing sensitive data, but they cannot replace the organizational habit of classifying data as part of the creation workflow. Organizations that deploy Purview or Macie without also training their people to classify data at the source end up in a perpetual catch-up cycle where the tools find misclassified data faster than humans can remediate it.

Cross-classification data flows are where most architectural mistakes happen. A developer builds a reporting dashboard that pulls from a Restricted database and publishes aggregated metrics to an Internal wiki. The developer assumes aggregation removes sensitivity, but the aggregated data reveals patterns that are themselves Restricted (e.g., patient volume trends at a hospital, transaction patterns at a financial institution). The high-water mark principle exists precisely for this scenario: when in doubt, the output inherits the input's classification. Architects must identify these cross-boundary flows during design and document explicit declassification rules when aggregation or transformation genuinely reduces sensitivity.

## Common Decisions (ADR Triggers)

- **Classification framework selection** -- adopt an existing standard (NIST, ISO 27001 Annex A) vs. build a custom framework. Standards provide defensibility in audits and regulatory inquiries; custom frameworks align better with organizational language and culture. Most organizations adopt a standard and customize the level names and examples.
- **Number of classification levels** -- three levels (Public, Internal, Restricted) vs. four (adding Confidential between Internal and Restricted) vs. five or more (adding sub-levels like Secret and Top Secret). More levels provide finer-grained control but increase complexity and classification errors. Four levels is the most common enterprise choice.
- **Labeling enforcement model** -- advisory (labels are recommended, not enforced) vs. mandatory (data cannot be stored or transmitted without a label) vs. default-and-override (unlabeled data defaults to a specified level, owners can reclassify). Mandatory labeling is most secure but creates friction; default-and-override balances security with usability.
- **Automated classification tool selection** -- cloud-native tools (Purview, Macie, Google DLP) vs. third-party (BigID, Varonis) vs. build custom. Cloud-native tools integrate tightly with their platform but create vendor lock-in and may not cover multi-cloud or on-premises data stores. Third-party tools provide cross-platform coverage at additional licensing cost.
- **Encryption key management per classification** -- platform-managed keys vs. customer-managed keys (CMEK) vs. customer-supplied keys (CSEK) vs. HSM-backed keys. Higher classification levels typically require more customer control over keys, but customer-managed keys increase operational complexity (key rotation, backup, disaster recovery).
- **Cross-boundary data flow governance** -- architect-enforced (data flows are reviewed during design) vs. runtime-enforced (DLP and network policies block unauthorized flows) vs. both. Architect-enforced catches flows early but misses runtime surprises; runtime-enforced catches everything but generates false positives. Most mature organizations use both.

## See Also

- `general/data.md` -- General data architecture and storage patterns
- `general/security.md` -- Security architecture and controls
- `general/identity.md` -- Identity and access management (enforces classification-based access)
- `general/governance.md` -- Change management and data governance processes
- `compliance/gdpr.md` -- GDPR requirements for personal data classification and handling
- `compliance/pci-dss.md` -- PCI DSS cardholder data classification requirements
- `compliance/hipaa.md` -- HIPAA protected health information classification
- `compliance/nist-800-171-cmmc.md` -- NIST/CMMC controlled unclassified information handling
