# CIS Benchmarks

## Scope

The Center for Internet Security (CIS) Benchmarks are a set of consensus-based, prescriptive security configuration baselines for over 100 technologies, including operating systems, cloud providers, container platforms, databases, network devices, and applications. CIS Benchmarks are the line-item baseline most audits use as the starting point for "what does a hardened configuration look like for X". They are widely cited by FedRAMP, PCI-DSS, ISO 27001, SOC 2, HIPAA, and many other compliance regimes as the implementation reference for hardening controls. Covers the per-cloud benchmarks (AWS, Azure, GCP, OCI), the operating system benchmarks (Windows, Linux distributions), the container and Kubernetes benchmarks, the level 1 vs level 2 distinction, the relationship to AWS Foundational Security Best Practices and Azure Security Benchmark / Microsoft Cloud Security Benchmark, the CIS Critical Security Controls (the broader CIS framework), and the practical adoption patterns. Does not cover the CIS Hardened Images program (paid hardened machine images).

## The CIS Benchmark Format

Each CIS Benchmark is a structured document organized into:

- **Sections** by functional area (e.g., for AWS: IAM, Storage, Logging, Monitoring, Networking, Data Protection)
- **Recommendations** within each section, each numbered (e.g., 1.5 — Ensure MFA is enabled for the root user)
- **Description** explaining what the recommendation does and why it matters
- **Rationale** explaining the security benefit
- **Impact** describing what changes for users when the recommendation is implemented
- **Audit procedure** explaining how to verify the recommendation is in place (typically a CLI command, API call, or console check)
- **Remediation procedure** explaining how to implement the recommendation
- **References** to the CIS Critical Security Controls and other frameworks that map to the recommendation

The audit and remediation procedures are explicit and copy-pastable, which is what makes CIS Benchmarks usable for actual implementation rather than just for reference.

## Level 1 vs Level 2

Each recommendation in a CIS Benchmark is tagged with a **Profile**:

- **Level 1** — practical and prudent recommendations that can be implemented in most environments without significant operational impact. The "obvious" hardening that any reasonable organization should adopt.
- **Level 2** — additional recommendations for environments with higher security requirements (regulated workloads, internet-facing systems, systems handling sensitive data). Level 2 may have operational impact and may require explicit acceptance by the organization.

The two levels are cumulative — Level 2 includes all Level 1 recommendations plus additional Level 2-only recommendations.

A typical CIS Benchmark for a cloud provider has ~50–100 Level 1 recommendations and ~30–50 additional Level 2 recommendations, for a total of 80–150 individual checks.

## Cloud Provider Benchmarks

### CIS AWS Foundations Benchmark

The most widely-used cloud benchmark. Currently at v4.0 (released 2024). Sections cover:

1. **Identity and Access Management** — root account hardening, IAM password policy, MFA, access keys, password reuse
2. **Storage** — S3 bucket public access blocking, S3 default encryption, EBS encryption, RDS encryption
3. **Logging** — CloudTrail enabled, multi-region trail, log file validation, S3 bucket access logging, KMS key rotation, VPC Flow Logs
4. **Monitoring** — CloudWatch alarms for unauthorized API calls, root account usage, IAM policy changes, CloudTrail config changes, S3 bucket policy changes
5. **Networking** — security group rules (no SSH/RDP from 0.0.0.0/0), default VPC not in use, route table inspection
6. **Data Protection** — S3 Block Public Access, EBS default encryption, RDS automated backups

Most checks are Level 1; the Level 2 checks add more aggressive monitoring, more restrictive access patterns, and additional defense-in-depth controls.

### CIS Microsoft Azure Foundations Benchmark

Currently at v3.0. Sections cover:

1. **Identity and Access Management** — Entra ID configuration, MFA, role assignments, guest user controls
2. **Microsoft Defender for Cloud** — Defender plans enabled, automatic provisioning, security alerts
3. **Storage Accounts** — public access blocking, encryption at rest, secure transfer required, shared key access disabled
4. **Database Services** — SQL audit, threat detection, transparent data encryption, Cosmos DB firewall
5. **Logging and Monitoring** — Activity Log archival, diagnostic settings on key resources, alerts on critical changes
6. **Networking** — NSG rules (no inbound RDP/SSH from internet), Network Watcher, Azure Firewall
7. **Virtual Machines** — VM extensions, disk encryption, just-in-time access, OS update assessment

### CIS Google Cloud Platform Foundations Benchmark

Currently at v3.0. Sections cover:

1. **Identity and Access Management** — minimum service account privileges, no service account user-managed keys, audit log configuration
2. **Logging and Monitoring** — log sinks, log retention, alert policies on key changes
3. **Networking** — VPC firewall rules, default network not in use, Private Google Access
4. **Virtual Machines** — confidential computing, OS Login, shielded VMs
5. **Storage** — bucket public access blocking, uniform bucket-level access, retention policies
6. **Cloud SQL Database Services** — public IP, SSL required, automated backups, audit logging
7. **BigQuery** — dataset-level access controls, customer-managed encryption keys

## Operating System Benchmarks

CIS publishes benchmarks for:

- **Windows** — Windows Server 2016/2019/2022, Windows 10/11
- **Linux distributions** — Red Hat Enterprise Linux, CentOS, Ubuntu, Debian, SUSE, Amazon Linux, Oracle Linux, Rocky Linux, AlmaLinux
- **macOS** — most recent macOS versions
- **Network OSes** — Cisco IOS, Juniper, F5

OS benchmarks are extensive (often 200+ recommendations) and cover account policies, audit configuration, file system permissions, service hardening, kernel parameters, network configuration, and software inventory.

## Container and Kubernetes Benchmarks

- **CIS Docker Benchmark** — Docker daemon configuration, container hardening, image hardening, host configuration
- **CIS Kubernetes Benchmark** — control plane configuration, etcd configuration, worker node configuration, policies, network policy
- **CIS Amazon EKS Benchmark** — EKS-specific hardening (in addition to the generic Kubernetes benchmark)
- **CIS Azure AKS Benchmark** — AKS-specific hardening
- **CIS GKE Benchmark** — GKE-specific hardening

The container and Kubernetes benchmarks are critical for any containerized workload because the default configurations of most container platforms are not hardened for production use.

## Relationship to Other Cloud-Native Benchmarks

### AWS Foundational Security Best Practices (FSBP)

AWS publishes its own security best practices via Security Hub. AWS FSBP and CIS AWS Foundations Benchmark have substantial overlap but are not identical:

- **CIS** is consensus-based, slower to update, more conservative, framework-agnostic
- **AWS FSBP** is AWS-specific, faster to update, includes service-level recommendations CIS does not (e.g., specific Lambda hardening)

Most organizations enable both standards in Security Hub and accept the duplicate findings — the union of the two gives broader coverage.

### Microsoft Cloud Security Benchmark (MCSB)

Microsoft publishes the MCSB (formerly Azure Security Benchmark) as its cloud-native security baseline. Like AWS FSBP, it has overlap with the CIS Azure benchmark. Defender for Cloud uses MCSB as its primary compliance dashboard, with CIS as a secondary standard.

### CIS Critical Security Controls (CIS Controls)

The CIS Controls (currently v8.1) are the broader CIS framework that covers cybersecurity practices at the organizational level. The Controls are at the same level of abstraction as NIST CSF — high-level practices for the whole organization, not configuration recommendations for specific technologies. The CIS Benchmarks are the implementation reference for the Controls in many cases.

There are 18 CIS Controls, organized into Implementation Groups (IG1, IG2, IG3) by organizational maturity:

- **IG1** — basic cyber hygiene, appropriate for small organizations
- **IG2** — appropriate for organizations with moderate cybersecurity resources
- **IG3** — appropriate for organizations with high security requirements

## Common Implementation Patterns

### Adopting a CIS Benchmark for cloud accounts

1. **Choose the benchmark version** — use the latest published version (CIS releases new versions annually for major benchmarks)
2. **Choose the profile** — Level 1 as the minimum target, Level 2 for production and regulated workloads
3. **Enable in the cloud provider's compliance tool** — Security Hub for AWS (CIS AWS Foundations), Defender for Cloud for Azure (CIS Azure Foundations), Security Command Center for GCP (CIS GCP Foundations)
4. **Triage findings** — many newly-enabled accounts will have dozens of findings on the first scan. Prioritize Level 1 findings and high-severity Level 2 findings first.
5. **Remediate or document exceptions** — fix the findings or document a justification for accepting the risk
6. **Continuous monitoring** — the compliance tool re-scans on a schedule and alerts on new findings
7. **Quarterly review** — review the benchmark version and adopt the new version when it is published

### Adopting a CIS Benchmark for hosts

For OS hardening, the practical adoption pattern is:

1. **Use a hardened image** — CIS publishes pre-hardened machine images for AWS, Azure, and GCP marketplaces (CIS Hardened Images, paid). The alternative is to harden a base image yourself using the CIS Benchmark as the recipe.
2. **Apply hardening at provisioning time** — use Ansible, Chef, Puppet, or cloud-init to apply CIS hardening to fresh instances. Avoid hardening in-place on existing instances because the changes may break running workloads.
3. **Continuous compliance scanning** — tools like Wazuh, OpenSCAP, Lynis, Tenable, or Qualys can scan hosts against CIS benchmarks and report drift
4. **Exception management** — some recommendations break specific workloads (e.g., disabling a service that the application depends on). Document each exception with the workload that requires it.

### Reporting on CIS adoption

A common dashboard shows:

- **Overall compliance percentage** — across all in-scope resources, what percentage of CIS recommendations are passing
- **Per-section breakdown** — IAM, Storage, Logging, Monitoring, Networking compliance percentages
- **Failed checks by severity** — high, medium, low
- **Trend over time** — compliance percentage week-over-week
- **Top failing recommendations** — the recommendations that are failing across the most resources

The dashboard is typically reviewed monthly by the security team and quarterly by leadership.

## Common Decisions

- **Level 1 vs Level 2 adoption** — Level 1 as the universal baseline. Level 2 for production and regulated workloads where the additional hardening is justified. Document the decision per environment.
- **CIS Benchmark vs cloud provider native baseline** — both. CIS for the audit-friendly framework reference; cloud-native for the provider-specific recommendations CIS does not cover. Accept the duplicate findings.
- **Hardened images vs in-place hardening** — hardened images for new deployments. In-place hardening only when image replacement is not feasible.
- **Compliance tool: Security Hub vs Defender for Cloud vs Security Command Center vs third-party** — cloud-native tools for the cloud-specific benchmarks (they have the deepest integration). Third-party tools (Wiz, Prisma Cloud, Tenable) for unified multi-cloud reporting and for non-cloud resources.
- **Exception process** — every CIS exception must have an owner, a documented reason, and a review date. Exceptions without review dates accumulate over time and erode the baseline.

## Reference Links

- [CIS Benchmarks (free download)](https://www.cisecurity.org/cis-benchmarks/)
- [CIS Critical Security Controls](https://www.cisecurity.org/controls)
- [CIS AWS Foundations Benchmark v4.0](https://www.cisecurity.org/benchmark/amazon_web_services)
- [CIS Microsoft Azure Foundations Benchmark](https://www.cisecurity.org/benchmark/azure)
- [CIS Google Cloud Platform Foundations Benchmark](https://www.cisecurity.org/benchmark/google_cloud_computing_platform)
- [CIS Hardened Images (AWS Marketplace)](https://aws.amazon.com/marketplace/seller-profile?id=dfa1e6a8-0b7b-4d35-a59c-ce272caee4fc)

## See Also

- `frameworks/nist-sp-800-53.md` — NIST control catalog that CIS Benchmarks help implement
- `frameworks/nist-csf-2.0.md` — CSF as a higher-level framework; CIS Benchmarks are implementation
- `frameworks/aws-security-reference-architecture.md` — AWS SRA, often paired with CIS AWS Foundations
- `frameworks/aws-well-architected.md` — AWS Well-Architected Security pillar
- `providers/aws/security.md` — AWS security services including Security Hub
- `providers/azure/security.md` — Azure security services including Defender for Cloud
- `general/cloud-workload-hardening.md` — workload hardening practices
- `general/stig-hardening.md` — DISA STIG hardening (alternative/complementary to CIS for federal contexts)
