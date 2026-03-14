# SOX IT General Controls - Cloud Control Mapping

## Overview

The **Sarbanes-Oxley Act (SOX)** requires publicly traded companies to establish and maintain internal controls over financial reporting (ICFR). **IT General Controls (ITGCs)** are the technology controls that support the reliability of financial data and systems. SOX does not prescribe specific technical controls — auditors evaluate whether controls are designed effectively and operating consistently.

**Applicability:** All U.S. publicly traded companies and their subsidiaries. Also applies to foreign private issuers listed on U.S. exchanges. SOX compliance extends to any system that processes, stores, or transmits financial data that feeds into financial statements.

**Key Sections:**
- **Section 302:** CEO/CFO must certify financial statements and internal controls
- **Section 404(a):** Management must assess and report on ICFR effectiveness annually
- **Section 404(b):** External auditor must attest to management's ICFR assessment (for larger companies)

**SOX in the Cloud:** Cloud adoption does not reduce SOX obligations. It shifts some controls to the cloud provider (inherited controls) but adds new risks around cloud-specific access, change management, and data flows. Auditors increasingly scrutinize cloud configurations as part of ITGC testing.

---

## Checklist

- [ ] Are all systems that process financial data identified and in scope? (ERP, billing, revenue recognition, GL, reporting)
- [ ] Is user access provisioning tied to HR processes? (joiner-mover-leaver automation, approval workflows)
- [ ] Are access reviews conducted quarterly for financially significant applications? (recertification campaigns)
- [ ] Is privileged access managed with just-in-time elevation? (PIM/PAM, time-limited, approved, logged)
- [ ] Is segregation of duties enforced? (no single person can initiate, approve, and execute financial transactions)
- [ ] Are all changes to financial systems approved before deployment? (change advisory board, documented approval)
- [ ] Is there a separate test environment for financial applications? (changes tested before production)
- [ ] Are emergency changes documented with retrospective approval? (no uncontrolled changes)
- [ ] Are automated jobs monitored and alerted on failure? (batch processing, ETL, financial calculations)
- [ ] Are backups tested for restorability? (not just backed up — proven recoverable)
- [ ] Is there evidence of control operation for auditors? (logs, screenshots, tickets — auditors need proof)
- [ ] Are cloud provider SOC 1/SOC 2 reports reviewed annually? (complementary user entity controls identified)

## Why This Matters

SOX non-compliance can result in **personal criminal liability** for CEO and CFO (up to $5M fine and 20 years imprisonment for willful violations), delisting from stock exchanges, and destruction of investor confidence. SOX deficiencies are categorized as:

- **Deficiency:** Control weakness, may not require disclosure
- **Significant Deficiency:** Important enough to merit attention of the audit committee
- **Material Weakness:** Reasonable possibility that a material misstatement won't be prevented or detected — requires disclosure in financial filings and directly impacts stock price

IT control failures are the most common source of significant deficiencies and material weaknesses in modern SOX audits. A single missing access review or undocumented change can cascade into a material weakness finding.

---

## ITGC Domain 1: Access Management

### Control Objectives

Ensure that only authorized individuals have access to financially significant systems, and that access is appropriate for their role.

### Controls and Cloud Mapping

| Control | Description | AWS | Azure | GCP |
|---------|-------------|-----|-------|-----|
| **User Provisioning** | New access requires documented approval before granting | AWS SSO + ServiceNow/ticketing integration | Azure AD + access packages, entitlement management | Google Workspace + IAM, access request workflows |
| **Access Reviews** | Quarterly recertification of user access | AWS IAM Access Analyzer, custom reports | Azure AD Access Reviews (built-in) | IAM Recommender, Policy Analyzer |
| **Privileged Access** | Admin access is limited, time-bound, and logged | AWS SSO with elevated permission sets, CloudTrail | Azure PIM (just-in-time elevation, approval, audit) | PAM solutions, time-bound IAM bindings |
| **Segregation of Duties (SoD)** | Conflicting roles cannot be held by same person | Separate IAM roles (deploy vs approve), SCPs | Azure AD role assignments, SoD checks | Separate IAM roles, organization policy constraints |
| **Offboarding** | Access removed within 24 hours of termination | Automated via SSO + HR integration | Azure AD lifecycle workflows | Automated via directory sync |
| **Service Accounts** | Non-human accounts managed with same rigor | IAM roles (no long-lived keys), Secrets Manager | Managed identities (no passwords), Key Vault | Service account keys (minimize), Workload Identity |
| **MFA** | Required for all access to financial systems | AWS SSO MFA, IAM MFA policies | Azure AD Conditional Access (MFA required) | 2-Step Verification, context-aware access |

### Key Evidence for Auditors

- User access provisioning tickets with approval documentation
- Quarterly access review completion reports with remediation evidence
- Privileged access elevation logs (who, when, why, duration)
- Terminated user access removal evidence (timestamp within SLA)
- SoD conflict reports and exception approvals

### Segregation of Duties Matrix (Example)

| Function | Role A (Developer) | Role B (Approver) | Role C (Deployer) |
|----------|-------------------|-------------------|-------------------|
| Write code | Yes | No | No |
| Approve change | No | Yes | No |
| Deploy to production | No | No | Yes |
| Access production data | No | No | Read-only |
| Modify IAM policies | No | No | No (Security team only) |

---

## ITGC Domain 2: Change Management

### Control Objectives

Ensure that changes to financially significant systems are authorized, tested, and implemented in a controlled manner.

### Controls and Cloud Mapping

| Control | Description | AWS | Azure | GCP |
|---------|-------------|-----|-------|-----|
| **Change Approval** | All changes approved before production deployment | CI/CD with approval gates (CodePipeline, GitHub Actions) | Azure DevOps approval gates, ServiceNow integration | Cloud Build with approval steps, GitHub Actions |
| **Testing Requirements** | Changes tested in non-production before deployment | Separate AWS accounts for dev/staging/prod | Separate Azure subscriptions, deployment slots | Separate GCP projects for each environment |
| **Deployment Controls** | Automated, repeatable deployments with audit trail | CodePipeline/CodeDeploy, CloudTrail logging | Azure DevOps Pipelines, Activity Log | Cloud Build, Cloud Deploy, Audit Logs |
| **Emergency Changes** | Expedited process with retrospective approval | Pipeline bypass with mandatory post-change review | Break-glass process with retroactive approval ticket | Emergency access with mandatory post-mortem |
| **Infrastructure Changes** | IaC changes follow same approval process | Terraform plans reviewed in PR, applied via pipeline | ARM/Bicep changes via PR approval + pipeline | Terraform/Deployment Manager via PR + pipeline |
| **Database Changes** | Schema changes approved and tested | RDS snapshot before migration, approved change ticket | Azure SQL snapshot, approved migration script | Cloud SQL backup before migration, approved script |
| **Rollback Capability** | Ability to revert changes if issues detected | Blue/green deployments, CodeDeploy rollback | Deployment slots (swap back), rollback in pipeline | Traffic splitting, rollback in Cloud Deploy |

### Change Management Process

```
Developer → Code Change → Pull Request → Code Review → Approval
                                                          │
                                                          ▼
                                              Automated Testing
                                              (unit, integration, security)
                                                          │
                                                          ▼
                                              Deploy to Staging
                                                          │
                                                          ▼
                                              QA/UAT Validation
                                                          │
                                                          ▼
                                              Change Approval (CAB or auto)
                                                          │
                                                          ▼
                                              Deploy to Production
                                                          │
                                                          ▼
                                              Post-Deploy Validation
                                                          │
                                                          ▼
                                              Evidence Retained (tickets,
                                              logs, approvals, test results)
```

### Key Evidence for Auditors

- Change request tickets with approval before deployment timestamp
- CI/CD pipeline logs showing approval gates
- Test execution results (automated test reports)
- Deployment logs with timestamps and deployer identity
- Emergency change log with retrospective approval documentation
- Rollback evidence when changes were reverted

### Emergency Change Process

1. Engineer requests emergency access via break-glass procedure
2. On-call manager provides verbal/chat approval (documented)
3. Change is implemented with enhanced logging
4. Within 24-48 hours: formal change ticket created retrospectively
5. Change reviewed and approved by change advisory board
6. Root cause analysis for why emergency was needed

---

## ITGC Domain 3: IT Operations

### Control Objectives

Ensure that IT operations supporting financial systems are reliable, monitored, and recoverable.

### Controls and Cloud Mapping

| Control | Description | AWS | Azure | GCP |
|---------|-------------|-----|-------|-----|
| **Job Scheduling** | Automated jobs monitored for completion/failure | EventBridge Scheduler, Step Functions, CloudWatch alarms | Azure Automation, Logic Apps, Azure Monitor alerts | Cloud Scheduler, Cloud Tasks, Cloud Monitoring |
| **Batch Processing** | Financial batch jobs have success/failure tracking | Step Functions with error handling, SNS alerts | Azure Data Factory monitoring, alert rules | Cloud Composer (Airflow), Dataflow monitoring |
| **Backup and Recovery** | Regular backups with tested restore procedures | RDS automated backups, S3 versioning, AWS Backup | Azure Backup, geo-redundant storage, recovery services | Cloud SQL backups, snapshot schedules |
| **Backup Testing** | Quarterly restore tests with documented results | Restore to test instance, validate data integrity | Restore to test database, validate | Restore to test instance, validate |
| **Incident Management** | Incidents tracked, prioritized, and resolved | PagerDuty/OpsGenie + CloudWatch, incident timeline | Azure Monitor + ServiceNow, incident records | Cloud Monitoring + PagerDuty, incident tracking |
| **Capacity Monitoring** | Systems sized to handle financial processing loads | CloudWatch metrics, auto-scaling, capacity alarms | Azure Monitor, auto-scaling, capacity alerts | Cloud Monitoring, auto-scaling, capacity alerts |
| **Availability Monitoring** | Financial system uptime tracked and reported | CloudWatch synthetic canaries, health checks | Application Insights, availability tests | Uptime checks, synthetic monitoring |
| **Patch Management** | OS and application patches applied within SLA | SSM Patch Manager, maintenance windows | Azure Update Management, maintenance configurations | OS patch management, maintenance windows |

### Job Monitoring Requirements

Financial batch jobs (month-end close, revenue calculations, reconciliations) require:

1. **Success/failure alerting** — immediate notification on failure
2. **Completion verification** — confirm job produced expected output
3. **Re-run procedures** — documented steps to re-execute failed jobs
4. **Dependency tracking** — jobs that depend on other jobs' completion
5. **Audit trail** — start time, end time, status, output record count

### Key Evidence for Auditors

- Job execution logs with success/failure status
- Backup completion reports and quarterly restore test results
- Incident tickets for system outages affecting financial systems
- Capacity monitoring dashboards showing adequate headroom
- Patch compliance reports showing timely application

---

## ITGC Domain 4: SDLC (Systems Development Life Cycle)

### Control Objectives

Ensure that new systems and modifications are developed with appropriate controls, testing, and approval.

### Controls and Cloud Mapping

| Control | Description | AWS | Azure | GCP |
|---------|-------------|-----|-------|-----|
| **Development Standards** | Coding standards documented and enforced | Linting in CI, code style checks, security scanning | Azure DevOps policies, code analysis | Cloud Build checks, linting, security scanning |
| **Code Review** | All code changes reviewed by someone other than the author | GitHub/GitLab PR reviews (required reviewers) | Azure Repos PR policies (required reviewers) | GitHub/GitLab PR reviews |
| **Security Testing** | Application security testing before deployment | CodeGuru, Snyk, SAST/DAST in pipeline | DevSecOps in Azure DevOps, SAST/DAST | Container analysis, SAST/DAST in pipeline |
| **UAT (User Acceptance)** | Business users validate changes before production | Staging environment with business user access | Deployment slots for UAT, test subscriptions | Staging project for UAT |
| **Documentation** | System documentation maintained for financial apps | Architecture docs, runbooks, API specs | Same | Same |
| **Data Migration** | Data migrations validated for completeness/accuracy | Pre/post row counts, checksum validation | Same | Same |

### Key Evidence for Auditors

- Code review records (PR history with reviewer approvals)
- Test plans and execution results for significant changes
- UAT sign-off documentation
- Security scan results and remediation evidence
- System documentation and architecture diagrams

---

## SOX-Relevant Cloud Services

### Services Most Commonly in SOX Scope

| Category | Services | Why in Scope |
|----------|----------|-------------|
| **ERP/Financial** | SAP on EC2/Azure VMs, Oracle Cloud, NetSuite, Workday | Directly process financial transactions |
| **Databases** | RDS, Aurora, Azure SQL, Cloud SQL | Store financial data (GL, AP, AR, billing) |
| **Data Warehouses** | Redshift, Synapse, BigQuery | Financial reporting and analytics |
| **ETL/Integration** | Glue, Data Factory, Dataflow | Move financial data between systems |
| **Identity** | AWS SSO, Azure AD, Google Workspace | Control who accesses financial systems |
| **Compute** | EC2, Azure VMs, Compute Engine, ECS/EKS/AKS/GKE | Run financial applications |
| **Storage** | S3, Azure Blob, Cloud Storage | Store financial documents and backups |
| **CI/CD** | CodePipeline, Azure DevOps, Cloud Build | Deploy changes to financial systems |

### Cloud Provider Compliance Reports

| Report | Purpose | How to Obtain |
|--------|---------|---------------|
| **SOC 1 Type II** | Controls relevant to financial reporting (directly maps to SOX) | AWS Artifact, Azure Service Trust Portal, GCP Compliance Reports |
| **SOC 2 Type II** | Trust service criteria (security, availability) | Same portals |
| **Bridge Letter** | Covers gap between SOC report end date and your audit date | Request from provider |

### Complementary User Entity Controls (CUECs)

Cloud provider SOC 1 reports list controls that the **customer** must implement. These are your SOX obligations:

- Configure IAM and access controls (provider secures the platform, you secure your configuration)
- Enable and protect audit logging (provider offers the service, you must turn it on)
- Manage encryption keys (provider offers KMS, you must use it appropriately)
- Implement network security (provider offers VPCs/NSGs, you must configure them)
- Manage patching for your workloads (provider patches infrastructure, you patch OS and applications)

---

## Audit Trail Architecture for SOX

```
Financial Application
    │
    ├── Application Logs → CloudWatch/Azure Monitor/Cloud Logging
    │                           │
    ├── Database Audit Logs → RDS/Azure SQL/Cloud SQL audit logs
    │                           │
    ├── API Call Logs → CloudTrail/Activity Log/Audit Log
    │                           │
    ├── Access Logs → IAM events, SSO events, login events
    │                           │
    └── Change Logs → CI/CD pipeline logs, deployment records
                                │
                                ▼
                        Centralized Log Store
                    (S3/Blob Storage with immutability)
                                │
                                ▼
                        SIEM / Log Analytics
                    (Splunk, Sentinel, Chronicle)
                                │
                                ▼
                    Audit Reports & Dashboards
                    (retained per retention policy,
                     typically 7 years for SOX)
```

### Log Retention for SOX

- **Minimum:** 7 years (SOX record retention requirement)
- **Recommended:** Move to cold storage after 1 year (S3 Glacier, Azure Cool/Archive, Cloud Storage Nearline/Coldline)
- **Immutability:** Use WORM storage or object lock for audit logs (prevent tampering)
- **Access:** Auditors need query access to historical logs — ensure cold storage is searchable

## Common Decisions (ADR Triggers)

- **SOX scope definition** — which cloud systems are in scope for ITGCs (any system that feeds financial statements)
- **Access review tooling** — built-in cloud tools vs third-party IGA (SailPoint, Saviynt) vs custom
- **Change management process** — fully automated CI/CD gates vs CAB-based approval vs hybrid
- **Emergency change process** — break-glass procedure design, retrospective approval SLA
- **Segregation of duties model** — role design, SoD conflict matrix, exception process
- **Log retention architecture** — hot/warm/cold tiers, 7-year retention, immutability mechanism
- **Evidence collection** — manual evidence gathering vs automated GRC platform (ServiceNow GRC, AuditBoard)
- **Cloud SOC 1 review process** — who reviews, when, how CUECs are tracked and implemented

## See Also

- `compliance/soc2.md` — SOC 2 Trust Service Criteria (complementary to SOX ITGC controls)
- `general/security.md` — Security controls applicable to financial systems
- `general/identity.md` — IAM and access management architecture
- `general/governance.md` — Cloud governance, tagging, and policy enforcement
- `general/deployment.md` — CI/CD and change management patterns
