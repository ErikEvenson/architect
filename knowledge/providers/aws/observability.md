# AWS Observability

## Checklist

- [ ] Is CloudWatch configured with custom metrics, dashboards, and composite alarms for application-specific health signals?
- [ ] Are CloudWatch metric alarms set with appropriate thresholds, evaluation periods, and SNS notification targets for all critical resources?
- [ ] Is CloudTrail enabled in all regions with a multi-region trail, management events logging, and optional data events for S3/Lambda?
- [ ] Is CloudTrail log file integrity validation enabled and logs shipped to a centralized security account S3 bucket?
- [ ] Is AWS X-Ray instrumented for distributed tracing across services (Lambda, ECS, API Gateway, SDK-instrumented apps)?
- [ ] Is Amazon GuardDuty enabled in all accounts and regions with findings flowing to Security Hub?
- [ ] Is AWS Config enabled with conformance packs or custom rules to detect configuration drift and non-compliant resources?
- [ ] Are VPC Flow Logs enabled for all VPCs, shipping to CloudWatch Logs or S3, with traffic analysis configured?
- [ ] Is a centralized logging account receiving CloudTrail, Config, GuardDuty, and application logs via cross-account delivery?
- [ ] Are CloudWatch Log Groups configured with appropriate retention periods (not infinite) to control storage costs?
- [ ] Is CloudWatch Logs Insights or Amazon OpenSearch used for log analysis and search across distributed services?
- [ ] Are CloudWatch Contributor Insights rules configured to identify top-N contributors to operational issues?
- [ ] Is AWS Health Dashboard (Personal Health Dashboard) integrated with EventBridge for automated incident response?
- [ ] Are CloudWatch Synthetics canaries configured for endpoint monitoring and SLA measurement?

## Why This Matters

Without comprehensive observability, outages are detected by customers instead of engineers. Missing CloudTrail logs make security incident investigation impossible. Disabled GuardDuty means threats go undetected. VPC Flow Logs are essential for network forensics. Infinite log retention accumulates significant storage costs. Siloed logging across accounts creates blind spots.

## Common Decisions (ADR Triggers)

- **Observability platform** -- native AWS tools vs third-party (Datadog, New Relic, Splunk, Grafana Cloud)
- **Centralized logging strategy** -- cross-account CloudWatch vs S3 aggregation vs OpenSearch vs third-party SIEM
- **Tracing approach** -- X-Ray vs OpenTelemetry with X-Ray backend vs third-party APM
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
