# CCPA/CPRA — California Consumer Privacy Act / California Privacy Rights Act

Reference: California Civil Code 1798.100-1798.199.100
CCPA Effective: 1 January 2020
CPRA Amendments Effective: 1 January 2023 (enforcement from 1 July 2023)
Scope: For-profit businesses that collect personal information of California residents and meet any threshold: (a) annual gross revenue exceeding $25 million, (b) annually buy, sell, or share personal information of 100,000 or more consumers or households, or (c) derive 50% or more of annual revenue from selling or sharing consumers' personal information.

## Scope

Covers CCPA/CPRA compliance requirements for cloud architectures, including consumer rights implementation (access, deletion, correction, opt-out of sale/sharing), service provider and contractor obligations, data inventory and mapping, sensitive personal information handling, automated decision-making disclosures, privacy-by-design architecture patterns, and CPRA enforcement by the California Privacy Protection Agency (CPPA). Does not cover general data architecture patterns (see `general/data.md`) or EU privacy frameworks (see `compliance/gdpr.md`).

---

## Why This Matters

The CCPA, as amended by the CPRA, is the most comprehensive consumer privacy law in the United States and has become the de facto standard that other US state privacy laws follow. Penalties include up to $2,500 per unintentional violation and $7,500 per intentional violation or violation involving minors — with no cap on aggregate penalties. The California Privacy Protection Agency (CPPA) has dedicated enforcement authority and has signaled aggressive enforcement priorities.

Beyond direct fines, the CCPA provides a private right of action for data breaches involving unencrypted or non-redacted personal information, with statutory damages of $100-$750 per consumer per incident. A breach affecting millions of California residents can result in class action exposure in the billions of dollars. Architecture decisions around encryption, access controls, data minimization, and retention directly determine breach exposure.

The CPRA introduced new concepts — sensitive personal information, contractor obligations, automated decision-making disclosures, and purpose limitation requirements — that require specific technical controls in cloud architectures. Retrofitting these controls after deployment is far more expensive and error-prone than building them in from the start.

---

## Common Decisions (ADR Triggers)

The following architectural decisions should be captured as Architecture Decision Records when CCPA/CPRA is in scope:

- **Consumer request fulfillment pipeline design** — How to implement verifiable consumer requests across all data stores for access, deletion, correction, and opt-out within the 45-day response window.
- **Personal information inventory and data mapping strategy** — How to discover, catalog, and maintain an accurate map of all personal information across cloud services, databases, caches, logs, and third-party integrations.
- **Sensitive personal information processing controls** — Whether to process sensitive personal information (SPI) beyond what is necessary to provide the requested service, and how to implement purpose limitation controls if SPI is collected.
- **Sale/sharing signal processing architecture** — How to detect and honor opt-out signals including Global Privacy Control (GPC), cookie consent preferences, and direct opt-out requests across all sharing/sale touchpoints.
- **Service provider vs. contractor vs. third-party classification** — How data recipients are classified, what contractual and technical controls apply to each, and how data flows are restricted accordingly.
- **Data retention and minimization policy enforcement** — Technical controls to enforce disclosed retention periods and purpose limitation requirements across all data stores.
- **Automated decision-making transparency** — Whether profiling or automated decision-making is used, and how to implement access-to-information and opt-out rights for consumers.
- **Privacy-by-design architecture pattern selection** — Data minimization, pseudonymization, and access control patterns chosen to reduce personal information exposure.
- **Breach notification and encryption strategy** — Encryption and security controls to avoid triggering the private right of action, and notification procedures for the 72-hour AG notification window.
- **Cross-context behavioral advertising controls** — How to implement technical controls for cross-context behavioral advertising opt-out, including integration with ad tech partners.
- **Minor consumer data handling** — Whether data from consumers under 16 is collected, and how to implement opt-in consent requirements (parental consent for under 13, consumer consent for 13-15).

---

## Checklist

### Personal Information Inventory and Data Mapping

Civil Code 1798.100, 1798.110, 1798.115; CPPA Regulations 7001-7002

- [ ] **[Critical]** Maintain a comprehensive inventory of all categories of personal information collected, stored, processed, and shared across all cloud services and data stores
- [ ] **[Critical]** Document the business or commercial purpose for collecting each category of personal information
- [ ] **[Critical]** Map data flows showing where personal information is collected, where it is stored, which internal systems process it, and which external parties receive it
- [ ] **[Critical]** Identify all categories of sources from which personal information is collected (directly from consumers, from third parties, from publicly available sources, from service providers)
- [ ] **[Critical]** Identify all categories of third parties, service providers, and contractors with whom personal information is shared or to whom it is sold
- [ ] **[Recommended]** Implement automated data discovery and classification to detect personal information in unstructured stores (object storage, logs, data lakes)
- [ ] **[Recommended]** Tag data assets with metadata indicating the category of personal information, collection source, processing purpose, and retention period
- [ ] **[Recommended]** Re-inventory data flows at least annually and upon any material change in processing activities
- [ ] **[Critical]** Distinguish between selling, sharing (for cross-context behavioral advertising), and disclosing personal information to service providers — each has different obligations

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Data discovery and classification | Macie (S3 PII discovery), Glue Data Catalog | Microsoft Purview Data Catalog, Purview Information Protection | Cloud DLP (Sensitive Data Protection), Data Catalog |
| Data flow mapping | VPC Flow Logs, CloudTrail data events | Azure Monitor, Network Watcher | VPC Flow Logs, Cloud Audit Logs (data access) |
| Metadata tagging | Resource tagging, S3 object tags, Glue table properties | Azure resource tags, Purview classification labels | Resource labels, Data Catalog tags |

### Consumer Right to Know / Access (Civil Code 1798.100, 1798.110, 1798.115)

- [ ] **[Critical]** Build a data export mechanism that can produce all personal information collected about a specific consumer across all data stores
- [ ] **[Critical]** Include in access responses: categories of personal information collected, categories of sources, business purposes for collection, categories of third parties with whom information is shared, and the specific pieces of personal information collected
- [ ] **[Critical]** Cover the 12-month lookback period (or longer if the business disclosed a longer retention period)
- [ ] **[Critical]** Implement identity verification for access requests that is proportional to the sensitivity of the data — must use reasonable security measures to verify the consumer is who they claim to be
- [ ] **[Recommended]** Support machine-readable portable formats (JSON, CSV) for data portability
- [ ] **[Recommended]** Design export pipelines to query across all systems (primary databases, data warehouses, analytics platforms, CRM, marketing platforms, logs)
- [ ] **[Critical]** Respond within 45 calendar days (extendable by an additional 45 days with consumer notification)
- [ ] **[Recommended]** Handle large dataset exports asynchronously with consumer notification when ready
- [ ] **[Recommended]** Redact other consumers' personal information from access request responses
- [ ] **[Critical]** Do not disclose Social Security numbers, financial account numbers, account passwords, or security questions/answers in access responses — provide a category-level description instead

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Export orchestration | Step Functions, Lambda for aggregation | Logic Apps, Azure Functions | Cloud Workflows, Cloud Functions |
| Cross-system data retrieval | Athena (query S3), Glue ETL, RDS queries | Synapse Analytics, Azure SQL queries | BigQuery (query Cloud Storage), Cloud SQL queries |
| Delivery mechanism | S3 pre-signed URLs with expiration | Blob Storage SAS tokens with expiration | Cloud Storage signed URLs with expiration |
| Identity verification | Cognito (user pools), custom verification flows | Azure AD B2C, custom verification flows | Identity Platform, custom verification flows |

### Right to Delete (Civil Code 1798.105)

- [ ] **[Critical]** Implement deletion pipelines that propagate deletion requests to all data stores containing the consumer's personal information (databases, object storage, caches, search indices, data warehouses, message queues, logs)
- [ ] **[Critical]** Direct service providers and contractors to delete the consumer's personal information from their records
- [ ] **[Critical]** Document and implement the enumerated exceptions to deletion (complete a transaction, detect security incidents, exercise free speech, comply with legal obligations, internal uses reasonably aligned with consumer expectations, comply with a legal obligation, otherwise use internally in a lawful manner compatible with the context)
- [ ] **[Critical]** Notify the consumer if an exception applies and specify which exception
- [ ] **[Recommended]** Implement soft-delete with configurable retention before hard deletion to allow for exception evaluation
- [ ] **[Critical]** Address deletion in backups — document the approach (exclusion from future restores, crypto-shredding, or delayed deletion upon backup expiration)
- [ ] **[Critical]** Handle deletion in event-sourced or append-only architectures (crypto-shredding as an alternative)
- [ ] **[Recommended]** Implement verification mechanisms to confirm deletion completeness across all systems
- [ ] **[Recommended]** Maintain a deletion log recording when requests were received, which systems were purged, and completion timestamps
- [ ] **[Critical]** Respond within 45 calendar days (extendable by an additional 45 days with consumer notification)

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Database record deletion | RDS, DynamoDB (TTL), Redshift | Azure SQL, Cosmos DB (TTL), Synapse | Cloud SQL, Firestore (TTL), BigQuery (row-level deletion) |
| Object storage deletion | S3 object deletion, S3 Lifecycle Policies | Blob Storage soft-delete, Lifecycle Management | Cloud Storage Object Lifecycle Management |
| Cache invalidation | ElastiCache flush, CloudFront invalidation | Azure Cache for Redis, Front Door cache purge | Memorystore, Cloud CDN cache invalidation |
| Search index deletion | OpenSearch document deletion | Azure AI Search document deletion | Vertex AI Search document deletion |
| Crypto-shredding | KMS key deletion scheduling | Key Vault key deletion | Cloud KMS key version destruction |

### Right to Correct (Civil Code 1798.106 — CPRA addition)

- [ ] **[Critical]** Implement correction mechanisms that allow consumers to request correction of inaccurate personal information
- [ ] **[Critical]** Propagate corrections to all downstream systems, service providers, and contractors that received the inaccurate data
- [ ] **[Recommended]** Use commercially reasonable efforts to verify the accuracy of the corrected information based on the totality of circumstances, including the nature and source of the data
- [ ] **[Recommended]** Maintain an audit trail of corrections showing the original value, corrected value, and timestamp
- [ ] **[Critical]** Respond within 45 calendar days (extendable by an additional 45 days with consumer notification)
- [ ] **[Recommended]** Implement correction propagation to analytics and derived datasets where feasible

### Right to Opt-Out of Sale/Sharing (Civil Code 1798.120, 1798.135)

- [ ] **[Critical]** Implement a "Do Not Sell or Share My Personal Information" mechanism accessible from the homepage
- [ ] **[Critical]** Honor the Global Privacy Control (GPC) browser signal as a valid opt-out of sale/sharing request — this is legally required under CPPA regulations
- [ ] **[Critical]** Propagate opt-out signals to all downstream recipients who received personal information for sale or sharing purposes
- [ ] **[Critical]** Cease selling or sharing the consumer's personal information within 15 business days of receiving the opt-out request
- [ ] **[Critical]** Do not ask the consumer to re-authorize sale/sharing for at least 12 months after the consumer opts out
- [ ] **[Recommended]** Implement a consent management platform (CMP) that integrates with ad tech, analytics, and data sharing pipelines
- [ ] **[Recommended]** Maintain a real-time or near-real-time opt-out status check at all sale/sharing touchpoints
- [ ] **[Critical]** For consumers under 16, do not sell or share personal information unless the consumer (age 13-15) or the consumer's parent/guardian (under 13) has opted in

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Consent/opt-out data store | DynamoDB (low-latency lookups), RDS | Cosmos DB, Azure SQL | Firestore, Cloud Spanner |
| Real-time opt-out propagation | EventBridge, SNS/SQS, Kinesis | Event Grid, Service Bus | Pub/Sub, Eventarc |
| GPC signal processing | CloudFront Functions (header inspection), Lambda@Edge | Azure Front Door Rules Engine | Cloud CDN custom headers, Cloud Functions |

### Right to Limit Use of Sensitive Personal Information (Civil Code 1798.121 — CPRA addition)

- [ ] **[Critical]** Identify all sensitive personal information (SPI) categories collected: Social Security / driver's license / state ID / passport numbers, account log-in credentials, precise geolocation, racial or ethnic origin, religious beliefs, union membership, mail/email/text content (unless directed to the business), genetic data, biometric data, health information, sex life or sexual orientation information, and financial account information
- [ ] **[Critical]** Implement a "Limit the Use of My Sensitive Personal Information" link accessible from the homepage (may be combined with the opt-out link)
- [ ] **[Critical]** When a consumer exercises this right, restrict SPI processing to only what is necessary to perform the services or provide the goods reasonably expected by an average consumer
- [ ] **[Recommended]** Implement purpose-limitation controls at the data layer to technically enforce SPI use restrictions (row-level security, column-level access, API-level filtering)
- [ ] **[Recommended]** Segregate SPI into separate data stores or encrypted partitions with distinct access controls
- [ ] **[Critical]** Do not use SPI for inferring characteristics about the consumer after they exercise the right to limit
- [ ] **[Recommended]** Maintain a register of all processing activities involving SPI, including the specific purpose for each

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| SPI segregation | Separate RDS instances/schemas, S3 buckets with distinct policies | Separate Azure SQL databases, Storage accounts with distinct RBAC | Separate Cloud SQL instances, Storage buckets with distinct IAM |
| Column-level access control | Lake Formation column-level security, DynamoDB fine-grained access | Azure SQL dynamic data masking, Row-Level Security | BigQuery column-level security, authorized views |
| Purpose limitation enforcement | IAM condition keys, Lambda authorizers with purpose checks | Azure Policy, Function-based authorization | Organization Policy, Cloud Functions authorization |

### Automated Decision-Making (Civil Code 1798.185(a)(16) — CPRA addition)

- [ ] **[Critical]** Identify all processing activities that involve automated decision-making technology, including profiling
- [ ] **[Critical]** Provide consumers with meaningful information about the logic involved in automated decision-making processes
- [ ] **[Recommended]** Implement a right for consumers to opt out of automated decision-making technology where it produces legal or similarly significant effects
- [ ] **[Recommended]** Provide a mechanism for consumers to access information about the automated decision-making process and the likely outcome with respect to the consumer
- [ ] **[Recommended]** Conduct risk assessments (as required by CPPA regulations) for automated decision-making that involves profiling consumers
- [ ] **[Recommended]** Maintain audit logs of automated decisions, including the inputs, model version, and outputs, for a period sufficient to respond to consumer inquiries
- [ ] **[Optional]** Implement human review mechanisms for automated decisions that significantly affect consumers

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| ML model tracking | SageMaker Model Registry, SageMaker Experiments | Azure ML Model Registry, ML Experiments | Vertex AI Model Registry, Vertex AI Experiments |
| Decision audit logging | CloudTrail, CloudWatch Logs, S3 (model inference logs) | Azure Monitor, Blob Storage (inference logs) | Cloud Audit Logs, Cloud Storage (inference logs) |
| Model explainability | SageMaker Clarify | Azure ML Responsible AI dashboard | Vertex AI Explainability |

### Service Provider, Contractor, and Third-Party Obligations (Civil Code 1798.100(d), 1798.140(ag), (j))

- [ ] **[Critical]** Classify all data recipients as service providers, contractors, or third parties based on the CCPA/CPRA definitions
- [ ] **[Critical]** Execute CCPA-compliant contracts with all service providers that include: specific business purpose limitations, prohibition on selling/sharing the personal information, prohibition on retaining/using/disclosing personal information outside the direct business relationship, certification of understanding of restrictions, and obligation to notify if unable to comply
- [ ] **[Critical]** Execute CCPA-compliant contracts with all contractors that include all service provider requirements plus: certification of compliance, right to take reasonable steps to ensure compliance, and right to remediate unauthorized use
- [ ] **[Recommended]** Implement technical controls to restrict service provider and contractor access to only the personal information necessary for the contracted purpose
- [ ] **[Critical]** Require service providers and contractors to cooperate with consumer rights requests (deletion, access, correction) and to delete personal information upon instruction
- [ ] **[Recommended]** Maintain a register of all service providers, contractors, and third parties with whom personal information is shared, including the categories of information and the business purpose
- [ ] **[Recommended]** Conduct due diligence on downstream service providers and contractors to verify they have adequate privacy and security controls
- [ ] **[Critical]** For third-party data sharing, ensure consumers have been notified and have not opted out (or have opted in, for sale/sharing)

### Privacy by Design and Data Minimization (Civil Code 1798.100(c), (d))

- [ ] **[Critical]** Collect only personal information that is reasonably necessary and proportionate to the disclosed purpose — do not collect data "just in case"
- [ ] **[Critical]** Implement and enforce retention periods aligned with disclosed purposes — delete or de-identify personal information when no longer needed
- [ ] **[Critical]** Encrypt personal information at rest in all data stores
- [ ] **[Critical]** Encrypt personal information in transit (TLS 1.2+ minimum)
- [ ] **[Critical]** Apply access controls following the principle of least privilege for personal information access
- [ ] **[Recommended]** Implement pseudonymization or de-identification where full identification is not required
- [ ] **[Recommended]** Design APIs and interfaces to return only the minimum necessary personal information
- [ ] **[Recommended]** Apply network segmentation to isolate personal information processing environments
- [ ] **[Recommended]** Implement automated data retention enforcement (TTL on records, lifecycle policies on object storage, log rotation policies)
- [ ] **[Recommended]** Use field-level encryption for sensitive personal information categories
- [ ] **[Critical]** Implement data segregation between tenants in multi-tenant architectures

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Encryption at rest | S3 SSE (SSE-S3, SSE-KMS, SSE-C), RDS encryption, EBS encryption | Azure Storage Service Encryption, Azure Disk Encryption, TDE | Default encryption, CMEK, Cloud External Key Manager (EKM) |
| Encryption in transit | ALB/NLB TLS termination, ACM | Application Gateway TLS, Azure Front Door | Cloud Load Balancing TLS, Certificate Manager |
| Retention enforcement | S3 Lifecycle Policies, DynamoDB TTL, CloudWatch log retention | Blob Lifecycle Management, Cosmos DB TTL, Log Analytics retention | Cloud Storage Lifecycle, Firestore TTL, Log Router retention |
| Field-level encryption | DynamoDB client-side encryption, S3 client-side encryption | Always Encrypted (Azure SQL), client-side encryption | Client-side encryption, Cloud KMS |
| De-identification | Comprehend Medical de-identification, custom Lambda pipelines | Presidio (open source), Azure Health De-identification | Cloud DLP de-identification (tokenization, masking, bucketing, date shifting) |

### Breach Notification and Private Right of Action (Civil Code 1798.150, 1798.82)

- [ ] **[Critical]** Implement reasonable security procedures and practices appropriate to the nature of the personal information to avoid triggering the private right of action (statutory damages of $100-$750 per consumer per incident)
- [ ] **[Critical]** Encrypt all personal information at rest and in transit — the private right of action applies only to unencrypted and non-redacted personal information
- [ ] **[Critical]** Implement automated threat detection and anomaly monitoring for personal information stores
- [ ] **[Critical]** Design incident response procedures that can assess breach scope (what data, which consumers, what time period) within hours
- [ ] **[Critical]** Notify affected California residents in the most expedient time possible and without unreasonable delay
- [ ] **[Critical]** Notify the California Attorney General if more than 500 California residents are affected
- [ ] **[Recommended]** Maintain forensic logging sufficient to determine breach scope and impact
- [ ] **[Recommended]** Conduct tabletop breach exercises at least annually
- [ ] **[Recommended]** Integrate cloud provider security alerts into the breach detection pipeline
- [ ] **[Critical]** Document security measures to demonstrate "reasonable security" in the event of litigation

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Threat detection | GuardDuty, Security Hub, Detective | Microsoft Defender for Cloud, Microsoft Sentinel | Security Command Center, Chronicle Security Operations |
| Anomaly detection | GuardDuty S3 Protection, Macie alerts | Defender for Storage, Purview anomaly alerts | SCC anomaly detection, Cloud DLP discovery findings |
| Forensic logging | CloudTrail (management and data events), VPC Flow Logs | Azure Monitor activity logs, NSG flow logs | Cloud Audit Logs (admin and data access), VPC Flow Logs |
| Alerting and escalation | CloudWatch Alarms, SNS, EventBridge | Azure Monitor Alerts, Action Groups | Cloud Monitoring Alerting, Pub/Sub |

### Privacy Risk Assessments (Civil Code 1798.185(a)(15) — CPRA addition)

- [ ] **[Critical]** Conduct cybersecurity audits for processing activities that present significant risk to consumer privacy or security (as defined by CPPA regulations)
- [ ] **[Critical]** Conduct risk assessments for processing activities involving: selling or sharing personal information, processing sensitive personal information, and use of automated decision-making technology
- [ ] **[Recommended]** Include in risk assessments: description of processing, purpose, consumer benefits, risks to consumer privacy, safeguards to mitigate risks
- [ ] **[Recommended]** Submit risk assessments to the CPPA upon request
- [ ] **[Recommended]** Review and update risk assessments when processing activities change materially
- [ ] **[Recommended]** Link risk assessment findings to Architecture Decision Records and remediation tracking

### Notice and Transparency (Civil Code 1798.100(a), 1798.130)

- [ ] **[Critical]** Provide a privacy policy at or before the point of collection that includes: categories of personal information collected, purposes for each category, categories of third parties to whom information is disclosed, retention period for each category, and a description of consumer rights
- [ ] **[Critical]** Disclose whether personal information is sold or shared, and the categories involved
- [ ] **[Critical]** Provide at least two methods for submitting consumer requests (at minimum, a toll-free telephone number and a website address; online-only businesses may provide only a web-based method)
- [ ] **[Critical]** If collecting personal information offline, provide notice at the point of offline collection
- [ ] **[Recommended]** Implement a privacy policy versioning system and archive prior versions
- [ ] **[Recommended]** Update the privacy policy whenever processing activities change materially
- [ ] **[Critical]** Provide notice of financial incentive programs (if applicable) including the terms, how to opt in/out, and why the incentive is permitted

---

## Regulatory Updates

### CPPA Enforcement Priorities (2024-2026)

The California Privacy Protection Agency has signaled the following enforcement priorities:

- **Global Privacy Control (GPC) enforcement** — Businesses must honor GPC signals as valid opt-out of sale/sharing requests. Several enforcement actions have already resulted from failure to honor GPC.
- **Dark patterns** — The CPPA is actively targeting manipulative consent interfaces that subvert consumer choice, including confusing opt-out flows and multi-step processes that discourage consumers from exercising rights.
- **Data broker registration** — California's Delete Act (SB 362, effective 2024) requires data brokers to register with the CPPA and will eventually require participation in a one-stop deletion mechanism (expected 2026).
- **Automated decision-making regulations** — The CPPA has been developing regulations for automated decision-making technology under CPRA authority. Draft regulations have been circulated and finalization is expected.
- **Cybersecurity audit and risk assessment regulations** — The CPPA is developing detailed requirements for mandatory cybersecurity audits and risk assessments under CPRA authority.

### Other US State Privacy Laws

Numerous US states have enacted comprehensive privacy laws modeled on the CCPA/CPRA, including Virginia (VCDPA), Colorado (CPA), Connecticut (CTDPA), Utah (UCPA), Texas (TDPSA), Oregon (OCPA), Montana (MCDPA), and others. Cloud architectures serving consumers across the US should implement privacy controls that satisfy the most stringent requirements — in most cases, CCPA/CPRA compliance provides a strong baseline for other state laws.

---

## Reference Links

- [CCPA Full Text (California Legislative Information)](https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?division=3.&part=4.&lawCode=CIV&title=1.81.5) — official statutory text of Civil Code 1798.100-1798.199.100
- [CPRA Ballot Initiative Text (Proposition 24)](https://vig.cdn.sos.ca.gov/2020/general/pdf/topl-prop24.pdf) — full text of the CPRA as approved by California voters in November 2020
- [CPPA Official Regulations](https://cppa.ca.gov/regulations/) — California Privacy Protection Agency regulations implementing the CCPA/CPRA
- [CPPA Enforcement Actions](https://cppa.ca.gov/enforcement/) — published enforcement actions and case summaries
- [California Attorney General CCPA Page](https://oag.ca.gov/privacy/ccpa) — Attorney General guidance and resources on CCPA compliance
- [Global Privacy Control Specification](https://globalprivacycontrol.org/) — technical specification for the GPC browser signal that must be honored under CPRA

## See Also

- `general/security.md` — General security controls including encryption and access management
- `general/governance.md` — Cloud governance and policy enforcement
- `general/data.md` — Data architecture patterns and data lifecycle management
- `compliance/gdpr.md` — GDPR compliance (complementary when processing data of both California and EU residents)
- `compliance/hipaa.md` — HIPAA compliance (complementary when health data is involved)
- `compliance/soc2.md` — SOC 2 controls that overlap with CCPA security requirements
