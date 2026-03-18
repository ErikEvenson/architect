# AWS Observability

## Scope

AWS monitoring, logging, and tracing services. Covers CloudWatch metrics/alarms/dashboards, CloudTrail, X-Ray, GuardDuty, AWS Config, VPC Flow Logs, Application Signals, Amazon Managed Prometheus/Grafana, and centralized logging patterns.

## Checklist

- [ ] **[Critical]** Is CloudWatch configured with custom metrics, dashboards, and composite alarms for application-specific health signals?
- [ ] **[Critical]** Are CloudWatch metric alarms set with appropriate thresholds, evaluation periods, and SNS notification targets for all critical resources?
- [ ] **[Critical]** Is CloudTrail enabled in all regions with a multi-region trail, management events logging, and optional data events for S3/Lambda?
- [ ] **[Critical]** Is CloudTrail log file integrity validation enabled and logs shipped to a centralized security account S3 bucket?
- [ ] **[Recommended]** Is AWS X-Ray instrumented for distributed tracing across services (Lambda, ECS, API Gateway, SDK-instrumented apps)?
- [ ] **[Critical]** Is Amazon GuardDuty enabled in all accounts and regions with findings flowing to Security Hub?
- [ ] **[Recommended]** Is AWS Config enabled with conformance packs or custom rules to detect configuration drift and non-compliant resources?
- [ ] **[Recommended]** Are VPC Flow Logs enabled for all VPCs, shipping to CloudWatch Logs or S3, with traffic analysis configured?
- [ ] **[Recommended]** Is a centralized logging account receiving CloudTrail, Config, GuardDuty, and application logs via cross-account delivery?
- [ ] **[Recommended]** Are CloudWatch Log Groups configured with appropriate retention periods (not infinite) to control storage costs?
- [ ] **[Optional]** Is CloudWatch Logs Insights or Amazon OpenSearch used for log analysis and search across distributed services?
- [ ] **[Optional]** Are CloudWatch Contributor Insights rules configured to identify top-N contributors to operational issues?
- [ ] **[Recommended]** Is AWS Health Dashboard (formerly Personal Health Dashboard) integrated with EventBridge for automated incident response?
- [ ] **[Recommended]** Are CloudWatch Synthetics canaries configured for endpoint monitoring and SLA measurement?
- [ ] **[Recommended]** Is CloudWatch Application Signals enabled for automatic SLO monitoring and service health dashboards across application services (supports Java, Python, .NET on EKS, ECS, EC2)?
- [ ] **[Optional]** Is Amazon Managed Service for Prometheus (AMP) configured for Prometheus-compatible metric collection from containerized workloads (EKS, ECS)?
- [ ] **[Optional]** Is Amazon Managed Grafana (AMG) deployed for centralized visualization and dashboarding across CloudWatch, Prometheus, X-Ray, and third-party data sources with SSO integration via IAM Identity Center?

## Why This Matters

Without comprehensive observability, outages are detected by customers instead of engineers. Missing CloudTrail logs make security incident investigation impossible. Disabled GuardDuty means threats go undetected. VPC Flow Logs are essential for network forensics. Infinite log retention accumulates significant storage costs. Siloed logging across accounts creates blind spots.

## Common Decisions (ADR Triggers)

- **Observability platform** -- native AWS tools vs third-party (Datadog, New Relic, Splunk, Grafana Cloud)
- **Centralized logging strategy** -- cross-account CloudWatch vs S3 aggregation vs OpenSearch vs third-party SIEM
- **Tracing approach** -- X-Ray vs OpenTelemetry with X-Ray backend vs third-party APM; CloudWatch Application Signals for automatic SLO-based monitoring
- **Managed Prometheus/Grafana vs self-managed** -- AMP/AMG for serverless Prometheus and Grafana without operational overhead vs self-hosted for full control and customization; AMP supports HA ingestion and 150-day retention; AMG integrates with IAM Identity Center for SSO
- **Alert routing** -- SNS to PagerDuty/Opsgenie vs ChatOps vs custom Lambda-based routing
- **Log retention policy** -- per-environment retention periods, archival to S3 Glacier for compliance
- **Config rules scope** -- AWS managed rules vs custom rules, remediation automation
- **GuardDuty findings workflow** -- Security Hub aggregation, automated remediation via EventBridge and Lambda

## Reference Architectures

- [AWS Architecture Center: Management & Governance](https://aws.amazon.com/architecture/management-governance/) -- reference architectures for centralized logging, monitoring, and compliance
- [AWS Observability Best Practices](https://aws-observability.github.io/observability-best-practices/) -- comprehensive guide to CloudWatch, X-Ray, and OpenTelemetry architectures
- [AWS Well-Architected Labs: Operational Excellence](https://www.wellarchitectedlabs.com/operational-excellence/) -- hands-on labs for building observability dashboards, alarms, and automated response
- [AWS Security Reference Architecture (SRA): Logging and monitoring](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/log-archive.html) -- centralized logging account design with CloudTrail, Config, and GuardDuty aggregation
- [AWS Solutions: Centralized Logging with OpenSearch](https://aws.amazon.com/solutions/implementations/centralized-logging-with-opensearch/) -- deployable solution for cross-account log aggregation and analysis

---

## See Also

- `general/observability.md` -- General observability patterns including metrics, logs, and traces
- `providers/aws/multi-account.md` -- Centralized logging account architecture for cross-account monitoring
- `providers/aws/vpc.md` -- VPC Flow Logs for network traffic analysis
