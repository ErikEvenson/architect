# Cross-Cloud Service Mapping

## Checklist

- [ ] **[Critical]** Map every AWS service in use to the target cloud equivalent — identify gaps before migration planning begins
- [ ] **[Critical]** Identify services with NO direct equivalent (Lambda, DynamoDB, Aurora Serverless) and document workaround strategy
- [ ] **[Critical]** Validate S3 API compatibility layer (Swift s3api, Ceph RGW, MinIO) against actual S3 features used (versioning, lifecycle, events)
- [ ] **[Critical]** Assess IAM/identity model differences (AWS IAM accounts vs OpenStack Keystone projects vs Entra ID (formerly Azure AD) tenants)
- [ ] **[Critical]** Complete feature gap analysis for each mapped service with risk assessment and workaround documentation
- [ ] **[Recommended]** Test API compatibility layers with production-like workloads, not just basic operations
- [ ] **[Recommended]** Map monitoring and observability stack (CloudWatch → Prometheus/Grafana, X-Ray → Jaeger, CloudTrail → CADF)
- [ ] **[Recommended]** Evaluate managed database service gaps (RDS → Trove: check engine availability, version support, HA options)
- [ ] **[Recommended]** Document networking model differences (VPC peering vs Neutron router, security groups syntax, CIDR overlap handling)
- [ ] **[Recommended]** Plan for missing CDN/WAF/edge services — these require external vendor selection (Cloudflare, Akamai, Fastly)
- [ ] **[Optional]** Evaluate serverless replacement strategy: rehost Lambda functions as containers or adopt OpenFaaS/Fission/Knative
- [ ] **[Optional]** Map CI/CD pipeline dependencies on cloud-native services (CodePipeline, CodeBuild → GitLab CI, Jenkins, Tekton)
- [ ] **[Optional]** Assess compliance and certification differences between cloud providers (SOC 2, HIPAA, FedRAMP availability)
- [ ] **[Optional]** Document cost model differences (on-demand vs reserved vs spot pricing, egress costs, storage tiers)

## Why This Matters

Cloud migrations fail most often not because of infrastructure differences but because of service-level assumptions baked into application code and operational procedures. An application built on AWS Lambda, DynamoDB, and SQS cannot be "lifted and shifted" — each service must be mapped to an equivalent or replaced with a fundamentally different architecture. Missing a service mapping means discovering a gap in production, when the cost of remediation is 10x what it would have been during planning.

The most dangerous gaps are partial equivalents — services that exist on the target cloud but lack specific features the application depends on. Swift's s3api middleware implements the S3 API but does not support S3 Select, S3 Event Notifications to Lambda, or S3 Object Lock. Trove provides database-as-a-service but may not support the specific PostgreSQL extensions or engine versions that RDS provides. These partial gaps create subtle failures that pass basic testing but break under production workloads.

OpenStack environments in particular require a "build vs buy" decision for many services that are fully managed in AWS. There is no CloudWatch, no WAF, no CDN, no serverless compute. Each gap must be filled with self-hosted open-source alternatives (Prometheus, ModSecurity, OpenFaaS) or external SaaS vendors, and each of those decisions carries operational cost.

## Common Decisions (ADR Triggers)

### ADR: S3 API Compatibility Layer Selection
**Context:** Application uses AWS S3 API. Target environment needs S3-compatible object storage.
**Options:**
- **Swift with s3api middleware** — Built into OpenStack Swift. Provides S3 API endpoint alongside native Swift API. Good for environments already running Swift. Partial S3 compatibility: supports basic CRUD, multipart upload, ACLs. Does NOT support: S3 Select, S3 Event Notifications, Object Lock, Storage Classes, Requester Pays.
- **Ceph RGW (RADOS Gateway)** — S3 and Swift compatible. Higher S3 API coverage than Swift s3api. Supports bucket versioning, lifecycle policies, multipart upload, server-side encryption. Operates as a separate service on top of Ceph RADOS cluster.
- **MinIO** — Lightweight, high-performance S3-compatible storage. Kubernetes-native. Full S3 API compatibility including bucket notifications, versioning, object locking, server-side encryption. Can run as a gateway in front of other storage backends.

**Decision criteria:** If running OpenStack with Swift already deployed, s3api middleware is the lowest-effort option for basic S3 compatibility. If high S3 feature parity is required (versioning, lifecycle, notifications), Ceph RGW or MinIO provide better coverage. MinIO is preferred for Kubernetes-native deployments and greenfield environments.

### ADR: Serverless Compute Replacement Strategy
**Context:** Application uses AWS Lambda functions. Target environment has no equivalent managed serverless service.
**Options:**
- **Rehost as containers** — Package Lambda handler code into container images, deploy on Kubernetes (or Nova VMs with Docker). Loses serverless scaling but simplest code migration. Use Knative Serving for scale-to-zero if needed.
- **OpenFaaS** — Open-source functions-as-a-service platform. Runs on Kubernetes or Docker Swarm. Supports multiple languages. Auto-scaling, metrics, CLI for deployment. Closest operational model to Lambda.
- **Fission** — Kubernetes-native serverless framework. Fast cold starts (pre-warmed environments). Supports triggers (HTTP, message queue, timer). Lower community adoption than OpenFaaS.
- **Knative** — Kubernetes-based platform for serverless workloads. Scale-to-zero, event-driven, revision management. More infrastructure overhead to operate but most feature-complete.

**Decision criteria:** For small number of Lambda functions (< 10) with simple triggers (API Gateway → Lambda), rehosting as containers is fastest. For larger serverless architectures with event-driven patterns, OpenFaaS provides the best balance of simplicity and Lambda-like operational model. Knative is appropriate if the team is already invested in Kubernetes and wants a broader serverless platform.

### ADR: Monitoring and Observability Stack Replacement
**Context:** Application uses AWS CloudWatch (metrics, logs, alarms), X-Ray (tracing), and CloudTrail (audit). Target environment has no equivalent managed services.
**Options:**
- **Prometheus + Grafana + Loki + Tempo** — Full open-source stack. Prometheus for metrics (replaces CloudWatch Metrics), Loki for logs (replaces CloudWatch Logs), Tempo for distributed tracing (replaces X-Ray), Grafana for dashboards and alerting (replaces CloudWatch Dashboards + Alarms).
- **Datadog / New Relic (SaaS)** — External SaaS monitoring. Unified metrics, logs, traces, and alerting. Higher cost but zero operational overhead. Works across any cloud or on-prem.
- **ELK Stack (Elasticsearch, Logstash, Kibana)** — Established log aggregation. Can handle metrics via Metricbeat. Higher resource consumption than Loki. Strong search and analytics capabilities.

**Decision criteria:** For self-hosted OpenStack environments, Prometheus + Grafana + Loki is the standard choice: mature, well-integrated, low resource overhead. If the team lacks monitoring operational expertise or wants to avoid self-hosting, Datadog/New Relic SaaS is worth the cost. ELK is appropriate if log search and analytics are the primary requirement and the team already has Elasticsearch expertise.

### ADR: Managed Database Service Gap Strategy
**Context:** Application uses AWS RDS. Target cloud's managed database service (Trove, Azure SQL) may not support the required engine, version, or features.
**Options:**
- **Target cloud managed service (Trove, Cloud SQL, Azure Database)** — If the engine and version are supported, this is the simplest option. Check: HA (multi-AZ), automated backups, point-in-time recovery, read replicas, supported extensions.
- **Self-hosted database on VMs** — Install and operate the database engine on Nova VMs or Kubernetes. Full control over version, extensions, configuration. Requires operational expertise for backups, HA (Patroni for PostgreSQL, Galera for MySQL), monitoring.
- **Managed database from third-party (Aiven, CrunchyData, Percona)** — External managed database service. Can connect to any cloud/on-prem via VPN or peering. Trades operational overhead for vendor cost.

**Decision criteria:** Always check Trove (or equivalent) first — if it supports the engine, version, and required features (HA, backup, replicas), use it. If not, self-hosted on VMs with Patroni (PostgreSQL) or Galera (MySQL) is the proven approach, but budget for operational overhead. Third-party managed services are a good middle ground when the team needs managed database but the cloud doesn't provide it.

## Reference Architectures

### AWS to OpenStack Service Mapping

| AWS Service | OpenStack Equivalent | Compatibility | Key Differences |
|---|---|---|---|
| EC2 | Nova | Direct | Instance types → flavors. No equivalent to instance store (use Cinder ephemeral). No Spot Instances. |
| VPC | Neutron | Direct | Subnets, routers, security groups map directly. No VPC peering (use router-based connectivity). No Transit Gateway. |
| EBS | Cinder | Direct | Volume types may differ (SSD, HDD mapped to Cinder volume types). Snapshots available. No io2 Block Express equivalent. |
| ALB (L7) | Octavia (L7) | Direct | Octavia supports HTTP/HTTPS listeners with L7 rules. Uses amphora VMs or OVN provider. No native WAF integration. |
| NLB (L4) | Octavia (L4) | Direct | TCP/UDP listeners. Health checks. Floating IP as VIP. |
| RDS | Trove | Partial | Not all engines supported. Check specific engine/version. No Aurora equivalent. HA depends on Trove deployment. |
| S3 | Swift (s3api) or Ceph RGW | Partial | S3 API compatible via middleware. Not 100% feature parity. See S3 compatibility ADR above. |
| Lambda | No equivalent | Gap | Rehost as containers or adopt OpenFaaS/Fission/Knative. See Serverless ADR above. |
| CloudFront | No equivalent | Gap | Use external CDN: Cloudflare, Akamai, Fastly, AWS CloudFront (can front non-AWS origins). |
| WAF | No equivalent | Gap | HAProxy + ModSecurity, or external WAF (Cloudflare WAF, AWS WAF in front of external origin). |
| Route 53 | Designate | Partial | DNS-as-a-service. No health-check-based routing. No weighted/geolocation routing policies. |
| CloudWatch | No equivalent | Gap | Prometheus (metrics) + Grafana (dashboards/alerts) + Loki (logs). See Observability ADR. |
| CloudTrail | Keystone audit + CADF | Partial | API audit logging via CADF format. Less integrated than CloudTrail. No S3/Lambda integration. |
| Secrets Manager | Barbican | Partial | Key management and secret storage. Less feature-rich. No automatic rotation equivalent. |
| KMS | Barbican | Partial | Encryption key management. Supports symmetric and asymmetric keys. No CloudHSM equivalent without dedicated hardware. |
| IAM | Keystone | Partial | Identity and RBAC. Projects (tenants) vs AWS accounts. No service-linked roles. No IAM policies — uses role-based assignments. |
| SQS | Zaqar | Partial | Message queue service. Less mature than SQS. Alternative: self-hosted RabbitMQ or Kafka. |
| SNS | No equivalent | Gap | Self-hosted alternatives: NATS, RabbitMQ with topic exchanges, or external service. |
| ECS/EKS | Magnum | Partial | Container orchestration. Magnum deploys Kubernetes clusters. No Fargate equivalent. |
| CloudFormation | Heat | Direct | Infrastructure-as-code orchestration. HOT templates. Alternatively, use Terraform with OpenStack provider. |
| ElastiCache | No equivalent | Gap | Self-hosted Redis or Memcached on Nova VMs or Kubernetes. |
| ECR | No equivalent | Gap | Self-hosted Harbor, Quay, or GitLab Container Registry. All implement Docker Registry V2 API. |

### AWS to Azure Service Mapping

| AWS Service | Azure Equivalent | Notes |
|---|---|---|
| EC2 | Virtual Machines | Similar instance families. Azure uses VM Scale Sets for auto-scaling groups. |
| VPC | Virtual Network (VNet) | Subnets, NSGs, route tables. VNet peering available. |
| EBS | Managed Disks | Ultra, Premium SSD, Standard SSD, Standard HDD tiers. |
| ALB | Application Gateway | L7 load balancing with WAF integration (Application Gateway WAF). |
| NLB | Azure Load Balancer | L4 load balancing. Standard and Basic SKUs. |
| RDS | Azure SQL, Azure Database for PostgreSQL/MySQL | Flexible Server deployment. Hyperscale (Citus) for PostgreSQL. |
| S3 | Blob Storage | Containers (not buckets). Hot/Cool/Archive tiers. S3 API NOT compatible — requires code changes. |
| Lambda | Azure Functions | Consumption plan (serverless), Premium plan, Dedicated plan. |
| CloudFront | Azure Front Door / Azure CDN | Front Door includes WAF, global load balancing, and CDN. |
| Route 53 | Azure DNS + Traffic Manager | Azure DNS for hosting. Traffic Manager for routing policies. |
| CloudWatch | Azure Monitor | Metrics, logs (Log Analytics), alerts, Application Insights for APM. |
| IAM | Entra ID + RBAC | Different model: Entra ID for identity, RBAC for authorization, Managed Identities for service auth. |
| SQS | Azure Queue Storage / Service Bus | Queue Storage for simple queues. Service Bus for advanced (topics, sessions, transactions). |
| ECS/EKS | AKS / Container Instances | AKS for Kubernetes. Container Instances for serverless containers (like Fargate). |

### AWS to GCP Service Mapping

| AWS Service | GCP Equivalent | Notes |
|---|---|---|
| EC2 | Compute Engine | Predefined and custom machine types. Preemptible VMs (Spot equivalent). |
| VPC | VPC | Global VPC (not regional like AWS). Shared VPC for multi-project. |
| EBS | Persistent Disk | pd-standard, pd-ssd, pd-balanced. Regional persistent disks for HA. |
| ALB | Cloud Load Balancing (HTTP/S) | Global HTTP(S) LB. Integrated with Cloud CDN and Cloud Armor (WAF). |
| NLB | Cloud Load Balancing (TCP/UDP) | Regional or global network LB. |
| RDS | Cloud SQL | PostgreSQL, MySQL, SQL Server. HA with regional instances. |
| S3 | Cloud Storage | Buckets with Standard, Nearline, Coldline, Archive classes. S3 API compatible via interoperability mode. |
| Lambda | Cloud Functions / Cloud Run | Cloud Functions for event-driven. Cloud Run for containerized serverless. |
| CloudFront | Cloud CDN | Integrated with Cloud Load Balancing. |
| Route 53 | Cloud DNS | Managed DNS. No built-in health-check routing (use Cloud Load Balancing). |
| CloudWatch | Cloud Monitoring + Cloud Logging | Operations Suite (formerly Stackdriver). |
| IAM | Cloud IAM | Resource-based hierarchy (org → folder → project). Service accounts for workload identity. |
| SQS | Cloud Pub/Sub | Pub/Sub is more like SNS+SQS combined. Pull and push subscriptions. |
| ECS/EKS | GKE | Google Kubernetes Engine. Autopilot mode for serverless K8s. |
| DynamoDB | Firestore / Bigtable | Firestore for document DB. Bigtable for wide-column (high throughput). Neither is a direct equivalent. |

### Services with No Direct Cross-Cloud Equivalent

**AWS-specific (difficult to migrate):**
- **Aurora Serverless** — Auto-scaling relational DB. No equivalent elsewhere. Migrate to standard PostgreSQL/MySQL with connection pooling (PgBouncer).
- **DynamoDB** — Proprietary NoSQL with unique consistency model. Alternatives: MongoDB, ScyllaDB, Cassandra — none are drop-in replacements. Application code changes required.
- **Kinesis** — Managed data streaming. Alternative: self-hosted Kafka, or GCP Pub/Sub, Azure Event Hubs.
- **SageMaker** — ML platform. Alternatives: Kubeflow, MLflow, Azure ML, Vertex AI — significant rework.
- **Step Functions** — Serverless workflow orchestration. Alternatives: Apache Airflow, Temporal, Azure Logic Apps.

**Azure-specific:**
- **Cosmos DB** — Multi-model globally distributed DB. No direct equivalent. Closest: CockroachDB (SQL), MongoDB (document), Cassandra (wide-column).
- **Entra External ID (formerly Azure AD B2C)** — Customer identity platform. Alternatives: Auth0, Keycloak, AWS Cognito.
- **Logic Apps** — Low-code integration workflows. Alternatives: Apache Airflow, n8n, Zapier (SaaS).

**GCP-specific:**
- **Spanner** — Globally distributed SQL database with strong consistency. No direct equivalent. CockroachDB is inspired by Spanner but not identical.
- **BigQuery** — Serverless data warehouse. Alternatives: Snowflake (SaaS), self-hosted ClickHouse, AWS Redshift, Azure Synapse.
- **Anthos** — Multi-cloud Kubernetes management. Alternatives: Rancher, OpenShift, Tanzu.

### API Compatibility Layers

| API Standard | Compatible Implementations | Notes |
|---|---|---|
| S3 API | AWS S3, Ceph RGW, MinIO, Swift s3api, Wasabi, Backblaze B2 | Most common cross-cloud compatibility layer. Test specific features used (versioning, lifecycle, SSE). |
| Docker Registry V2 | Docker Hub, Harbor, Quay, GitLab Registry, ECR, ACR, GCR, GHCR | All implement OCI Distribution Spec. Private registry migration is straightforward. |
| OpenStack API | Native OpenStack, Rackspace, OVHcloud, VEXXHOST | API version compatibility varies. Check API microversion support. |
| Kubernetes API | EKS, AKS, GKE, OpenShift, Rancher, Magnum, self-hosted | Kubernetes API is the strongest cross-cloud portability layer. Workload manifests are portable; cloud-specific integrations (load balancers, storage classes, IAM) are not. |

### Feature Gap Analysis Template

Use this table for each AWS service in scope. Complete one row per feature actually used by the application.

| AWS Feature | Used? | Target Equivalent | Gap Level | Workaround | Risk | Migration Effort |
|---|---|---|---|---|---|---|
| S3 basic CRUD | Yes | Ceph RGW | None | N/A | Low | Low |
| S3 versioning | Yes | Ceph RGW | None | N/A | Low | Low |
| S3 Event Notifications → Lambda | Yes | No equivalent | Full gap | MinIO bucket notifications → webhook → container | High | High |
| S3 Select | No | N/A | N/A | N/A | N/A | N/A |
| RDS PostgreSQL 15 | Yes | Trove PostgreSQL | Verify version | Self-hosted if Trove lacks v15 | Medium | Medium |
| RDS Multi-AZ | Yes | Trove HA | Partial | Patroni on VMs if Trove HA insufficient | Medium | High |
| Lambda (Node.js) | Yes | No equivalent | Full gap | OpenFaaS or containerize | High | High |
| CloudWatch Metrics | Yes | No equivalent | Full gap | Prometheus + Grafana | Low | Medium |
| IAM roles for EC2 | Yes | Keystone app credentials | Partial | Application credential per service | Medium | Medium |

**Gap Level definitions:**
- **None** — Feature exists with equivalent functionality. Direct migration.
- **Partial** — Feature exists but with reduced functionality. Test thoroughly, may need workarounds.
- **Full gap** — No equivalent exists. Must build, buy, or re-architect.

**Risk Level definitions:**
- **Low** — Workaround is proven and well-documented. Unlikely to cause issues.
- **Medium** — Workaround exists but adds operational complexity. Needs testing.
- **High** — No clear workaround or workaround significantly changes architecture. Requires careful planning.
