# GDPR — General Data Protection Regulation

Reference: Regulation (EU) 2016/679
Effective: 25 May 2018
Scope: Any organization processing personal data of EU/EEA residents, regardless of where the organization is established.

## Scope

Covers GDPR compliance requirements for cloud architectures, including data residency, cross-border transfers, right to erasure, consent management, breach notification, and Data Protection Impact Assessments. Does not cover general data architecture patterns (see `general/data.md`) or non-EU privacy frameworks.

---

## Why This Matters

GDPR carries fines of up to 4% of global annual turnover or EUR 20 million (whichever is higher). Beyond financial penalties, enforcement actions damage customer trust and can halt cross-border data flows entirely. Cloud architecture decisions made early — region selection, encryption strategy, data lifecycle design — determine whether an organization can demonstrate compliance at audit time or faces months of remediation.

Every architectural choice involving personal data storage, processing, or transfer has a GDPR dimension. Retrofitting privacy controls into an existing cloud deployment is far more expensive and error-prone than building them in from the start.

---

## Common Decisions (ADR Triggers)

The following architectural decisions should be captured as Architecture Decision Records when GDPR is in scope:

- **Data residency strategy** — Whether to restrict all personal data processing to EU regions, or allow processing elsewhere with transfer safeguards.
- **Encryption and key management model** — Customer-managed keys vs. provider-managed keys, and who holds the decryption authority.
- **Data deletion pipeline design** — How to implement right-to-erasure across primary stores, replicas, backups, caches, and analytics pipelines.
- **Consent management platform selection** — Build vs. buy, integration pattern with downstream processing systems.
- **Pseudonymization strategy** — Tokenization vs. hashing vs. format-preserving encryption, and where re-identification keys are stored.
- **Breach detection and notification architecture** — Tooling, alert routing, and escalation paths to meet the 72-hour notification window.
- **Cross-border data transfer mechanism** — Standard Contractual Clauses (SCCs) vs. adequacy decisions vs. Binding Corporate Rules (BCRs).
- **Data Processing Agreement (DPA) review process** — How cloud provider DPAs are evaluated and tracked.
- **Backup retention vs. erasure conflict resolution** — How to reconcile backup retention policies with deletion requests.
- **Logging and monitoring scope** — What personal data appears in logs, how long it is retained, and how it is protected.

---

## Checklist

### Data Residency and Cross-Border Transfers

Articles 44-49, Schrems II (CJEU Case C-311/18)

- [ ] **[Recommended]** Identify all cloud regions where personal data is stored, processed, or transited
- [ ] **[Recommended]** Confirm selected cloud regions are within the EU/EEA or in countries with an EU adequacy decision (Andorra, Argentina, Canada (commercial), Faroe Islands, Guernsey, Israel, Isle of Man, Japan, Jersey, New Zealand, Republic of Korea, Switzerland, UK, Uruguay, and the EU-US Data Privacy Framework)
- [ ] **[Recommended]** Where data is transferred to non-adequate countries, implement Standard Contractual Clauses (SCCs) — use the June 2021 modular version
- [ ] **[Recommended]** Conduct Transfer Impact Assessments (TIAs) for each non-adequate country transfer, documenting local surveillance laws and supplementary measures
- [ ] **[Critical]** Implement supplementary technical measures where TIAs identify risks (encryption with EU-held keys, pseudonymization before transfer, split processing)
- [ ] **[Recommended]** Configure cloud provider settings to prevent data replication to non-approved regions
- [ ] **[Critical]** Document data flow maps showing all cross-border transfers, including sub-processor chains
- [ ] **[Recommended]** Review cloud provider sub-processor lists and set up change notifications
- [ ] **[Recommended]** Verify that cloud provider support and operations staff access from non-adequate countries is covered by appropriate safeguards
- [ ] **[Recommended]** Establish a process to re-evaluate transfers when adequacy decisions change or are invalidated

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| EU region selection | eu-west-1 (Ireland), eu-west-2 (London), eu-west-3 (Paris), eu-central-1 (Frankfurt), eu-south-1 (Milan), eu-south-2 (Spain), eu-north-1 (Stockholm), eu-central-2 (Zurich) | West Europe, North Europe, France Central, Germany West Central, Switzerland North, Sweden Central, Italy North, Poland Central, Spain Central | europe-west1 (Belgium), europe-west2 (London), europe-west3 (Frankfurt), europe-west4 (Netherlands), europe-west6 (Zurich), europe-west8 (Milan), europe-west9 (Paris), europe-north1 (Finland), europe-southwest1 (Madrid), europe-central2 (Warsaw) |
| Region restriction enforcement | AWS Organizations SCPs to deny non-EU regions; IAM condition keys `aws:RequestedRegion` | Azure Policy to restrict allowed locations | Organization Policy `constraints/gcp.resourceLocations` |
| Data residency commitment | AWS EU Sovereign Cloud (planned), AWS Digital Sovereignty Pledge | EU Data Boundary, Azure Confidential Computing | Assured Workloads for EU, Data Residency commitments |
| Encryption with customer keys | AWS KMS (CMK), CloudHSM | Azure Key Vault, Managed HSM, Customer-managed keys | Cloud KMS, Cloud HSM, Customer-managed encryption keys (CMEK) |

### Right to Erasure (Article 17)

- [ ] **[Recommended]** Inventory all data stores containing personal data (databases, object storage, caches, search indices, data warehouses, message queues, logs)
- [ ] **[Critical]** Design deletion pipelines that propagate erasure requests to all stores, including replicas and read-replicas
- [ ] **[Critical]** Address backup retention conflicts — document whether backups are excluded from erasure (with legal justification) or whether backup-level deletion is implemented
- [ ] **[Critical]** Implement soft-delete with configurable retention periods before hard deletion
- [ ] **[Critical]** Handle cascading deletions in relational data (foreign key references, derived data, aggregated data)
- [ ] **[Critical]** Ensure deletion from analytics and machine learning training datasets
- [ ] **[Critical]** Implement verification mechanisms to confirm deletion completeness
- [ ] **[Critical]** Document exceptions to erasure (legal hold, regulatory retention requirements, freedom of expression) per Article 17(3)
- [ ] **[Critical]** Design for deletion in event-sourced or append-only architectures (crypto-shredding as an alternative)
- [ ] **[Critical]** Set up automated deletion for data that exceeds its defined retention period
- [ ] **[Critical]** Test deletion pipelines regularly and document test results

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Object storage lifecycle | S3 Lifecycle Policies, S3 Object Lock (for retention) | Blob Storage Lifecycle Management, Immutable Storage | Cloud Storage Object Lifecycle Management, Retention policies |
| Database record deletion | RDS, DynamoDB (TTL), Redshift | Azure SQL, Cosmos DB (TTL), Synapse | Cloud SQL, Firestore (TTL), BigQuery (row-level deletion, table expiration) |
| Search index management | OpenSearch index management | Azure AI Search index management | Vertex AI Search index management |
| Cache invalidation | ElastiCache, CloudFront invalidation | Azure Cache for Redis, Front Door cache purge | Memorystore, Cloud CDN cache invalidation |
| Crypto-shredding | KMS key deletion scheduling (7-30 day waiting period) | Key Vault soft-delete and purge | Cloud KMS key version destruction |

### Right of Access / Data Portability (Articles 15, 20)

- [ ] **[Recommended]** Build data export mechanisms that can produce a machine-readable copy of all personal data for a given data subject
- [ ] **[Recommended]** Support common portable formats (JSON, CSV, XML) for data portability
- [ ] **[Recommended]** Implement identity verification for access requests to prevent unauthorized disclosure
- [ ] **[Recommended]** Design export to include data from all processing systems (not just the primary database)
- [ ] **[Recommended]** Set response time targets (one month, extendable by two months for complex requests)
- [ ] **[Recommended]** Handle large dataset exports efficiently (streaming, async generation with notification)
- [ ] **[Critical]** Include metadata about processing purposes, recipients, retention periods, and data sources in access responses
- [ ] **[Recommended]** Redact third-party personal data from access request responses where disclosure would adversely affect others' rights

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Data export automation | Step Functions for orchestration, S3 pre-signed URLs for delivery | Logic Apps for orchestration, Blob SAS tokens for delivery | Cloud Workflows for orchestration, Cloud Storage signed URLs for delivery |
| Data discovery and cataloging | AWS Glue Data Catalog, Macie for PII discovery | Microsoft Purview Data Catalog, Purview Information Protection | Data Catalog, Cloud DLP (Sensitive Data Protection) for PII discovery |
| Notification of export readiness | SNS, SES | Event Grid, Communication Services | Pub/Sub, Cloud Tasks |

### Consent Management (Articles 6, 7)

- [ ] **[Recommended]** Implement granular consent collection — separate consent for each distinct processing purpose
- [ ] **[Recommended]** Record consent with timestamp, version of privacy notice, IP address, and specific purposes consented to
- [ ] **[Recommended]** Provide a mechanism for data subjects to withdraw consent as easily as they gave it
- [ ] **[Recommended]** Propagate consent withdrawal to all downstream processing systems in near-real-time
- [ ] **[Recommended]** Implement purpose limitation — technical controls to prevent data processing beyond the consented purposes
- [ ] **[Recommended]** Version consent records so that processing can be traced back to the consent that was in effect at the time
- [ ] **[Recommended]** Handle pre-checked boxes prohibition — ensure no default-on consent
- [ ] **[Recommended]** Implement age verification for consent where processing children's data (Article 8, age thresholds vary by member state: 13-16)
- [ ] **[Recommended]** Design consent flows that meet the "freely given, specific, informed, and unambiguous" standard
- [ ] **[Recommended]** Integrate consent management with marketing platforms, analytics, and third-party data sharing

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Consent data store | DynamoDB (low-latency consent lookups), RDS (relational consent records) | Cosmos DB, Azure SQL | Firestore, Cloud Spanner |
| Event-driven consent propagation | EventBridge, SNS/SQS | Event Grid, Service Bus | Pub/Sub, Eventarc |
| Consent audit trail | CloudTrail (API-level), application-level audit logging to S3 | Azure Monitor, application-level audit to Blob Storage | Cloud Audit Logs, application-level audit to Cloud Storage |

### Data Protection Impact Assessments (Article 35)

- [ ] **[Recommended]** Identify processing activities that require a DPIA (systematic monitoring, large-scale processing of special categories, automated decision-making with legal effects, new technologies)
- [ ] **[Recommended]** Conduct DPIAs before processing begins, not retrospectively
- [ ] **[Recommended]** Include the following in each DPIA: systematic description of processing, necessity and proportionality assessment, risk assessment for data subjects, measures to mitigate risks
- [ ] **[Recommended]** Consult the Data Protection Officer (DPO) during DPIA preparation
- [ ] **[Recommended]** Consult the supervisory authority (Article 36) when residual risk remains high after mitigation
- [ ] **[Recommended]** Review and update DPIAs when processing changes materially
- [ ] **[Recommended]** Document DPIA outcomes and link them to Architecture Decision Records
- [ ] **[Recommended]** Maintain a DPIA register tied to the processing activities register (Article 30)

### Data Processing Agreements (Article 28)

- [ ] **[Critical]** Review cloud provider DPAs for Article 28(3) mandatory clauses: processing only on documented instructions, confidentiality obligations, security measures, sub-processor management, assistance with data subject rights, deletion/return at end of contract, audit rights, information provision
- [ ] **[Recommended]** Verify that cloud provider DPA covers all services in use (some providers have different DPAs for different service tiers)
- [ ] **[Recommended]** Track sub-processor lists and subscribe to change notifications from cloud providers
- [ ] **[Recommended]** Evaluate new sub-processors within the objection window defined in the DPA
- [ ] **[Recommended]** Maintain a register of all data processing agreements
- [ ] **[Critical]** Ensure DPAs with cloud providers include provisions for cross-border transfers (SCCs as appropriate)
- [ ] **[Recommended]** Confirm DPA covers incident notification obligations and timeframes

**Cloud Provider DPA References:**

| Provider | DPA Location |
|---|---|
| AWS | AWS GDPR Data Processing Addendum (part of AWS Service Terms) |
| Azure | Microsoft Products and Services Data Protection Addendum (DPA) |
| GCP | Google Cloud Data Processing Addendum |

### Privacy by Design and by Default (Article 25)

- [ ] **[Critical]** Implement encryption at rest for all personal data stores
- [ ] **[Critical]** Implement encryption in transit (TLS 1.2+ minimum) for all data flows containing personal data
- [ ] **[Recommended]** Apply data minimization — collect and retain only the personal data necessary for each processing purpose
- [ ] **[Recommended]** Implement pseudonymization where full identification is not required for processing
- [ ] **[Recommended]** Default to the most privacy-protective settings for new services and features
- [ ] **[Critical]** Apply access controls following the principle of least privilege for personal data access
- [ ] **[Critical]** Implement data segregation between tenants in multi-tenant architectures
- [ ] **[Recommended]** Use confidential computing where processing highly sensitive personal data
- [ ] **[Recommended]** Implement automated data classification to identify and tag personal data
- [ ] **[Recommended]** Design APIs and interfaces to return only the minimum necessary personal data
- [ ] **[Critical]** Apply network segmentation to isolate personal data processing environments

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Encryption at rest | S3 SSE (SSE-S3, SSE-KMS, SSE-C), RDS encryption, EBS encryption | Azure Storage Service Encryption, Azure Disk Encryption, TDE for SQL | Default encryption at rest, CMEK, Cloud External Key Manager (EKM) |
| Encryption in transit | ALB/NLB TLS termination, ACM for certificates | Application Gateway TLS, Azure Front Door | Cloud Load Balancing TLS, Certificate Manager |
| Pseudonymization | Macie for discovery, custom tokenization with DynamoDB/KMS | Purview for discovery, Always Encrypted with Azure SQL | Cloud DLP de-identification (tokenization, format-preserving encryption, date shifting, bucketing) |
| Confidential computing | Nitro Enclaves, Nitro System attestation | Azure Confidential Computing (DCsv2/DCsv3 VMs, confidential containers, Always Encrypted with secure enclaves) | Confidential VMs, Confidential GKE nodes |
| Data classification | Macie (S3 data discovery and classification) | Microsoft Purview Information Protection (sensitivity labels, auto-classification) | Cloud DLP / Sensitive Data Protection (inspection, classification, de-identification) |
| Data minimization (field-level) | DynamoDB fine-grained access, Lake Formation column-level security | Azure SQL dynamic data masking, Row-Level Security | BigQuery column-level security, authorized views, data masking |

### Breach Notification (Articles 33, 34)

- [ ] **[Recommended]** Implement automated threat detection and anomaly monitoring for personal data stores
- [ ] **[Critical]** Design alert routing to ensure the DPO and incident response team are notified immediately upon detecting a potential breach
- [ ] **[Critical]** Build a breach assessment workflow to determine whether notification is required (risk to rights and freedoms of natural persons)
- [ ] **[Recommended]** Prepare notification templates for both supervisory authority (Article 33) and affected data subjects (Article 34)
- [ ] **[Recommended]** Implement a 72-hour notification timer that triggers escalation if the supervisory authority has not been notified
- [ ] **[Critical]** Document the breach register (Article 33(5)) — all breaches, regardless of whether they were notified, including facts, effects, and remedial actions
- [ ] **[Critical]** Test breach notification procedures through tabletop exercises at least annually
- [ ] **[Critical]** Integrate cloud provider security alerts into the breach detection pipeline
- [ ] **[Critical]** Implement forensic logging sufficient to determine the scope and impact of a breach (what data, which data subjects, what time period)
- [ ] **[Recommended]** Establish communication channels with relevant supervisory authorities in advance

**Cloud Service Mappings:**

| Control | AWS | Azure | GCP |
|---|---|---|---|
| Threat detection | GuardDuty, Security Hub, Detective | Microsoft Defender for Cloud, Microsoft Sentinel | Security Command Center (Premium), Chronicle Security Operations |
| Anomaly detection on data stores | GuardDuty S3 Protection, Macie alerts | Defender for Storage, Purview anomaly alerts | Cloud DLP discovery findings, SCC anomaly detection |
| Forensic logging | CloudTrail (management and data events), VPC Flow Logs, S3 access logs | Azure Monitor activity logs, NSG flow logs, diagnostic logs | Cloud Audit Logs (admin and data access), VPC Flow Logs |
| Alerting and escalation | CloudWatch Alarms, SNS, EventBridge rules | Azure Monitor Alerts, Action Groups, Logic Apps | Cloud Monitoring Alerting, Pub/Sub, Cloud Functions |
| Incident response automation | Systems Manager Incident Manager, Lambda-based response | Sentinel Playbooks (Logic Apps), Automated response | Security Command Center automated response, Cloud Functions |

### Data Protection Officer (Articles 37-39)

- [ ] **[Recommended]** Determine whether a DPO appointment is mandatory (public authority, core activities involving large-scale systematic monitoring, or large-scale processing of special categories)
- [ ] **[Recommended]** Ensure the DPO has access to all cloud monitoring and audit tools relevant to personal data processing
- [ ] **[Critical]** Provide the DPO with the ability to generate compliance reports from cloud-native tools
- [ ] **[Critical]** Configure DPO as a contact point in breach notification workflows
- [ ] **[Recommended]** Ensure DPO is involved in DPIA processes and architecture reviews involving personal data
- [ ] **[Recommended]** Publish DPO contact details and communicate them to the supervisory authority

### Legitimate Interest Assessments (Article 6(1)(f))

- [ ] **[Recommended]** Document the legitimate interest assessment (LIA) for each processing activity relying on this lawful basis
- [ ] **[Recommended]** Structure LIAs with three tests: purpose test (is the interest legitimate?), necessity test (is the processing necessary for that interest?), balancing test (do the individual's interests override?)
- [ ] **[Recommended]** Link LIA documentation to the relevant data processing activities in the Article 30 register
- [ ] **[Critical]** Review LIAs when processing scope changes or when new data categories are introduced
- [ ] **[Critical]** Implement technical safeguards identified in the balancing test (e.g., additional pseudonymization, access restrictions, retention limits)
- [ ] **[Critical]** Provide a mechanism for data subjects to exercise their right to object to processing based on legitimate interest (Article 21)

### Records of Processing Activities (Article 30)

- [ ] **[Recommended]** Maintain a register of all processing activities as controller (Article 30(1)) and processor (Article 30(2))
- [ ] **[Critical]** Include in each record: purposes, data subject categories, personal data categories, recipient categories, transfers to third countries, retention periods, technical and organizational security measures
- [ ] **[Recommended]** Link processing activity records to the cloud infrastructure (which services, which regions, which data stores)
- [ ] **[Recommended]** Review and update the register at least annually and upon any material change to processing
- [ ] **[Recommended]** Make the register available to the supervisory authority on request

---

## Regulatory Updates

### EU Digital Omnibus Package (November 2025)

The European Commission published the Digital Omnibus Directive in November 2025, proposing targeted amendments to GDPR and related digital regulations. Key proposed changes relevant to cloud architecture:

- **Simplified record-keeping** for SMEs (fewer than 250 employees) -- reduced documentation burden for organizations that process personal data only incidentally
- **Streamlined DPO requirements** -- raised threshold for mandatory DPO appointment, potentially reducing obligations for smaller organizations
- **Cross-border enforcement reform** -- new mechanisms to accelerate cross-border complaint handling between supervisory authorities
- **Alignment with AI Act** -- clarifications on how GDPR obligations interact with the EU AI Act for AI systems processing personal data

Architects should monitor the legislative process as the Omnibus package progresses through the European Parliament and Council. Final adoption is expected no earlier than late 2026 or 2027.

### UK Data Use and Access Act (DUAA) -- June 2025

The UK Data Use and Access Act received Royal Assent in June 2025, replacing certain aspects of UK GDPR and the Data Protection Act 2018. Key changes affecting cloud architecture:

- **Recognized legitimate interests** -- specific processing activities (e.g., fraud prevention, network security) are explicitly recognized as legitimate interests without requiring a balancing test
- **Reduced cookie consent requirements** -- consent is no longer required for analytics and similar non-intrusive cookies, though tracking cookies still require consent
- **Smart Data schemes** -- new framework enabling sector-specific data portability (similar to Open Banking), requiring API-based data sharing infrastructure
- **Automated decision-making** -- refined rules replacing GDPR Article 22, with new safeguards and transparency requirements
- **International transfers** -- new "data protection test" replacing adequacy decisions for certain transfers, potentially simplifying UK-to-third-country data flows

For organizations processing both EU and UK personal data, cloud architectures must accommodate the divergence between EU GDPR and the UK DUAA. Consider separate data processing configurations where requirements differ.

## Reference Links

- [EUR-Lex GDPR Full Text](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — official published text of Regulation (EU) 2016/679
- [Standard Contractual Clauses](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/standard-contractual-clauses-scc_en) — EU Commission SCCs for international data transfers
- [EU Adequacy Decisions](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en) — list of countries with adequate data protection as determined by the EU Commission

## See Also

- `general/security.md` — General security controls including encryption and access management
- `general/governance.md` — Cloud governance and policy enforcement
- `general/data.md` — Data architecture patterns and data lifecycle management
- `compliance/hipaa.md` — HIPAA compliance (complementary when health data involves EU residents)
