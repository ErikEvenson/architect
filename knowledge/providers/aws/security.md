# AWS Security

## Scope

AWS security services beyond IAM. Covers GuardDuty (threat detection), Security Hub (posture management), Inspector (vulnerability scanning), Macie (sensitive data discovery), AWS WAF (application firewall), Shield / Shield Advanced (DDoS protection), Detective (investigation), Config Rules (compliance), Firewall Manager (multi-account policy), Security Lake (OCSF data lake), Verified Access (zero-trust application access), and cross-account security architecture patterns. For identity and access management, see `iam.md`.

## Checklist

- [ ] **[Critical]** Is Amazon GuardDuty enabled in all accounts and all active regions, with a delegated administrator account aggregating findings? (GuardDuty detects reconnaissance, instance compromise, credential exfiltration, and cryptocurrency mining; enable S3 Protection, EKS Audit Log Monitoring, Runtime Monitoring, RDS Login Activity, and Malware Protection features based on workload types)
- [ ] **[Critical]** Is AWS Security Hub enabled with the AWS Foundational Security Best Practices (FSBP) standard and CIS AWS Foundations Benchmark, with a delegated administrator aggregating findings across all member accounts and regions? (Security Hub normalizes findings from GuardDuty, Inspector, Macie, Firewall Manager, and third-party tools into ASFF format; configure automated suppression rules for accepted risks)
- [ ] **[Critical]** Is Amazon Inspector enabled for EC2 instance scanning, ECR container image scanning, and Lambda function scanning to detect software vulnerabilities and unintended network exposure? (Inspector v2 is agentless for ECR and Lambda; EC2 scanning uses the SSM agent; findings feed into Security Hub automatically)
- [ ] **[Recommended]** Is Amazon Macie enabled to discover and classify sensitive data (PII, financial data, credentials) in S3 buckets, with automated discovery jobs scheduled for buckets containing customer data? (Macie uses managed data identifiers plus custom data identifiers for organization-specific patterns; integrate findings with Security Hub for unified remediation)
- [ ] **[Critical]** Is AWS WAF deployed on all internet-facing resources (CloudFront, ALB, API Gateway, AppSync) with at minimum the AWSManagedRulesCommonRuleSet, AWSManagedRulesKnownBadInputsRuleSet, and rate-based rules? (evaluate Bot Control and ATP managed rule groups for login and API endpoints; use custom rules for application-specific patterns; log all requests to S3 or CloudWatch for forensics)
- [ ] **[Recommended]** Is AWS Shield Advanced enabled for business-critical internet-facing resources, and is the Shield Response Team (SRT) authorized with an IAM role to assist during active DDoS events? (Shield Advanced provides DDoS cost protection, advanced attack visibility, health-based detection, and 24/7 SRT access at $3,000/month per organization; evaluate whether standard Shield protection is sufficient for lower-risk workloads)
- [ ] **[Recommended]** Is Amazon Detective enabled and integrated with GuardDuty to accelerate security investigations with entity behavior graphs, CloudTrail log analysis, VPC Flow Log correlation, and EKS audit log analysis? (Detective automatically builds a graph model from log data; use entity profiles to determine blast radius of compromised credentials or instances)
- [ ] **[Critical]** Are AWS Config rules enabled across all accounts with conformance packs aligned to compliance frameworks (CIS, PCI-DSS, NIST 800-53), and are non-compliant resources triggering automated remediation via SSM Automation or Lambda? (Config records resource configuration history and evaluates compliance continuously; use organization-level Config rules deployed from the management account)
- [ ] **[Recommended]** Is AWS Firewall Manager used to centrally manage WAF rules, Security Group policies, Shield Advanced protections, Network Firewall policies, and Route 53 Resolver DNS Firewall rules across all accounts in the organization? (requires AWS Organizations with all features enabled; Firewall Manager ensures consistent security policy even as new accounts and resources are created)
- [ ] **[Recommended]** Is Amazon Security Lake configured to aggregate security logs from AWS services, custom sources, and third-party tools into a centralized S3 data lake using the Open Cybersecurity Schema Framework (OCSF)? (Security Lake normalizes CloudTrail, VPC Flow Logs, Route 53 DNS logs, Security Hub findings, and S3 data events into a queryable format; configure subscriber access for SIEM and analytics tools)
- [ ] **[Optional]** Is AWS Verified Access deployed for zero-trust access to internal applications, replacing or supplementing VPN-based access with identity-provider and device-trust policy evaluation at the network edge? (integrates with IAM Identity Center, Okta, JumpCloud, CrowdStrike, and Jamf for identity and device posture; evaluates Cedar-based policies per request)
- [ ] **[Critical]** Is a cross-account security architecture implemented with a dedicated Security Tooling account (delegated admin for GuardDuty, Security Hub, Inspector, Macie, Detective) and a Log Archive account (immutable CloudTrail, Config, and access logs), following the AWS Security Reference Architecture? (separate security tooling from workload accounts to prevent compromised workloads from disabling detection)

## Why This Matters

AWS provides dozens of security services, but they are all opt-in and region-specific. A single unenabled region or account is a blind spot an attacker can exploit. GuardDuty disabled in one region means no threat detection there. Security Hub not aggregating from all accounts means findings are scattered across consoles nobody monitors. Inspector not scanning containers means known CVEs ship to production.

The most common failure is partial enablement: security services turned on in the primary region but not in all active regions, or enabled in production accounts but not in development accounts where attackers establish initial access. The second most common failure is enablement without operationalization -- GuardDuty generates findings that nobody triages, Security Hub shows a failing posture score that nobody acts on, and Config rules report non-compliance that nobody remediates.

Cross-account security architecture is foundational. The AWS Security Reference Architecture prescribes a dedicated Security Tooling account as delegated administrator for detection services, a separate Log Archive account with immutable storage for audit logs, and organization-wide enablement via AWS Organizations. Without this structure, security operations scale linearly with account count instead of centrally.

## Common Decisions (ADR Triggers)

- **Security Hub standards** -- which compliance standards to enable (FSBP, CIS, PCI-DSS, NIST 800-53), how to handle control failures that are accepted risks, custom actions vs automated remediation
- **GuardDuty feature selection** -- which protection plans to enable (S3, EKS, Runtime Monitoring, RDS, Malware), cost vs detection coverage trade-offs for each
- **Vulnerability scanning strategy** -- Inspector for AWS-native scanning vs third-party tools (Qualys, Rapid7, Wiz), agent-based vs agentless, scanning frequency and exception handling
- **WAF rule management** -- AWS Managed Rules vs third-party managed rules (F5, Fortinet, Imperva) vs fully custom rules, count mode burn-in period before blocking, centralized management via Firewall Manager vs per-team ownership
- **Shield Advanced adoption** -- $3K/month cost vs DDoS cost protection and SRT access, which resources to protect, health-based detection configuration
- **SIEM integration** -- Security Lake as the data lake with a third-party SIEM (Splunk, Datadog, CrowdStrike) vs native Security Hub workflows vs Amazon OpenSearch for investigation
- **Compliance automation** -- Config conformance packs vs third-party CSPM (Prisma Cloud, Wiz), auto-remediation scope (which non-compliant resources to auto-fix vs alert-only)
- **Zero-trust application access** -- Verified Access vs traditional VPN vs service mesh mTLS, identity and device posture trust providers, Cedar policy authoring model
- **Cross-account security model** -- delegated administrator per service vs centralized Security Tooling account, finding aggregation region, log retention duration and immutability controls

## Reference Links

- [AWS Security Reference Architecture (SRA)](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/) -- prescriptive multi-account security architecture with delegated admin patterns for GuardDuty, Security Hub, Inspector, and Macie
- [AWS Well-Architected Framework: Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) -- security best practices for detection, infrastructure protection, data protection, and incident response
- [AWS Security Hub documentation](https://docs.aws.amazon.com/securityhub/latest/userguide/) -- setup, standards, findings management, and cross-account aggregation
- [Amazon GuardDuty documentation](https://docs.aws.amazon.com/guardduty/latest/ug/) -- threat detection features, protection plans, and delegated administrator configuration
- [Amazon Inspector documentation](https://docs.aws.amazon.com/inspector/latest/user/) -- vulnerability scanning for EC2, ECR, and Lambda with Security Hub integration

---

## See Also

- `providers/aws/iam.md` -- IAM roles, policies, permission boundaries, SCPs, and cross-account access
- `providers/aws/vpc.md` -- VPC security groups, NACLs, VPC endpoints, and network segmentation
- `providers/aws/cloudfront-waf.md` -- CloudFront CDN configuration and WAF rules at the edge
- `providers/aws/multi-account.md` -- AWS Organizations, SCPs, and multi-account landing zone patterns
- `providers/aws/secrets-manager.md` -- Secrets Manager for credential storage and automatic rotation
- `providers/aws/observability.md` -- CloudWatch, CloudTrail, and centralized logging for security monitoring
- `general/security.md` -- General security architecture patterns including zero trust and secrets management
