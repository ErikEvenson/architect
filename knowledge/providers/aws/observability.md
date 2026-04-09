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

## CloudWatch Logs Insights Query Patterns

CloudWatch Logs Insights is the query layer over CloudWatch Logs and is the load-bearing operational tool for any review where the question is "is this thing actually working in production". The syntax has a small surface area (`fields`, `filter`, `parse`, `stats`, `sort`, `limit`, `bin`, `dedup`) and the query patterns reviewers need are reusable across engagements.

### Cost characteristics

Insights charges per GB of log data scanned. Time range and log group selection both matter — a query against a multi-month range over a high-volume log group can cost real money. Two practical rules: narrow the time range first, then narrow the log group, then write the query. And avoid `parse` over very large datasets where the parsed field could be precomputed at ingestion time (use a metric filter or a parsed log destination instead).

### Common query patterns

#### Per-ENI flow log query — what did this ENI talk to in the last hour

```
fields @timestamp, srcAddr, dstAddr, srcPort, dstPort, protocol, action, bytes
| filter interfaceId = "eni-0123456789abcdef0"
| sort @timestamp desc
| limit 200
```

Replace the ENI ID. Useful when you need to know what a specific instance is connecting to, or whether it has been blocked by SGs/NACLs (filter on `action = "REJECT"`).

#### Per-CIDR flow log query — who is talking to a specific destination CIDR

```
fields @timestamp, interfaceId, srcAddr, dstAddr, dstPort, action
| filter dstAddr like /^203\.0\.113\./
| stats count(*) as flows, sum(bytes) as totalBytes by interfaceId, dstAddr, dstPort
| sort flows desc
| limit 50
```

Use this to triangulate questions like "who is sending traffic to this external IP range" or "is anything in our VPC still talking to the retired vendor". Rough CIDR matching with regex is usually good enough; for precise CIDR matching use a more elaborate `parse` + arithmetic.

#### CloudTrail unauthorized API call query

```
fields @timestamp, userIdentity.arn, eventSource, eventName, errorCode, sourceIPAddress, awsRegion
| filter errorCode = "AccessDenied" or errorCode = "UnauthorizedOperation"
| sort @timestamp desc
| limit 100
```

This is the canonical "who is being denied" query and is a good first cut after any IAM policy change. A surge in `AccessDenied` from a specific principal is the symptom of a too-tight policy or an upstream change to the role's effective permissions.

#### CloudTrail IAM policy change query

```
fields @timestamp, userIdentity.arn, eventName, requestParameters.policyArn, requestParameters.userName, requestParameters.roleName
| filter eventSource = "iam.amazonaws.com"
| filter eventName like /^(Create|Update|Put|Delete|Attach|Detach)/
| sort @timestamp desc
```

Catches policy creates, updates, deletes, attaches, and detaches across users, groups, and roles. Useful as a daily review query in environments where IAM changes should be infrequent and reviewable.

#### CloudTrail console login from new source query

```
fields @timestamp, userIdentity.userName, sourceIPAddress, additionalEventData.MFAUsed, errorMessage
| filter eventName = "ConsoleLogin"
| sort @timestamp desc
| limit 200
```

Pair with a list of expected source IPs (your office VPN, your VPC NAT gateway, etc.) and treat anything outside the list as a candidate for follow-up.

#### Lambda errors by function over the last 24h

```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count(*) as errors by bin(1h), @log
| sort @timestamp desc
```

Coarse first-cut for "which functions are misbehaving and when". `@log` gives the log group name, which for Lambda is `/aws/lambda/<function-name>`.

#### KMS Decrypt by principal — who used this CMK

```
fields @timestamp, userIdentity.arn, eventName, resources.0.ARN, sourceIPAddress
| filter eventSource = "kms.amazonaws.com"
| filter eventName in ["Decrypt", "GenerateDataKey", "GenerateDataKeyWithoutPlaintext"]
| filter resources.0.ARN = "arn:aws:kms:us-east-1:123456789012:key/abcd1234-..."
| stats count(*) as ops by userIdentity.arn
| sort ops desc
```

Requires CloudTrail data events for KMS to be enabled (default is management events only — see `providers/aws/kms.md`). Without data events, this query returns nothing.

#### Cross-log-group query — finding a request across multiple services

```
fields @timestamp, @log, @message
| filter @message like /request-id-12345/
| sort @timestamp asc
```

Run with multiple log groups selected (the Insights UI lets you select up to 50). Useful for tracing a single request through API Gateway, Lambda, and downstream services when you have a correlation ID.

### Saving queries and integrating with dashboards

- Save commonly used queries to **Saved Queries** in the Insights UI. Name them clearly (`flow-logs-by-eni`, `cloudtrail-access-denied`) and store them in version control if the team is large enough to need shared queries.
- Pin Insights query results to a CloudWatch dashboard widget. The widget re-runs the query on dashboard load and is a useful way to surface ongoing operational signals (unauthorized API calls, recent IAM changes) on a single pane.
- Schedule Insights queries via EventBridge + Lambda for daily or hourly review of saved queries that should produce zero results in a healthy environment.

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
- `providers/aws/vpc.md` -- VPC Flow Logs configuration, destination strategy, traffic type capture
- `providers/aws/security-groups.md` -- SG rules referenced by flow log REJECT investigations
- `providers/aws/kms.md` -- KMS data events required for the Decrypt-by-principal query
- `general/aws-readonly-audit.md` -- read-only audit methodology that uses these query patterns
