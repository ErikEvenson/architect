# AWS RDS / Aurora

## Scope

AWS managed relational databases. Covers Aurora vs standard RDS, Multi-AZ, read replicas, Global Database, Aurora Serverless v2, I/O-Optimized, Limitless Database, Performance Insights, security group patterns, and Extended Support pricing.

## Checklist

- [ ] **[Critical]** Is Aurora chosen over standard RDS for production workloads that benefit from distributed storage, faster failover, and read scaling?
- [ ] **[Critical]** Is Multi-AZ enabled for all production databases? (Aurora: automatic across 3 AZs; RDS: synchronous standby in a second AZ)
- [ ] **[Recommended]** Are read replicas configured to offload read-heavy workloads, and is the application using the reader endpoint?
- [ ] **[Recommended]** Is Aurora Global Database configured for cross-region disaster recovery with RPO under 1 second?
- [ ] **[Recommended]** Is Aurora Serverless v2 evaluated for variable or unpredictable workloads to reduce cost during idle periods?
- [ ] **[Recommended]** Are DB parameter groups and cluster parameter groups customized and version-controlled rather than using defaults?
- [ ] **[Recommended]** Is Performance Insights enabled with at least 7 days retention for query-level performance analysis?
- [ ] **[Critical]** Is automated backup retention set to an appropriate window (7-35 days) with point-in-time recovery tested?
- [ ] **[Critical]** Are database credentials stored in Secrets Manager with automatic rotation enabled?
- [ ] **[Critical]** Is the database deployed in private subnets with security groups restricting access to only application-tier security groups?
- [ ] **[Recommended]** Is IAM database authentication enabled for services that support it, eliminating password management?
- [ ] **[Critical]** Is encryption at rest enabled using a customer-managed KMS key, and is encryption in transit enforced (ssl_mode = verify-full)?
- [ ] **[Recommended]** Is the maintenance window scheduled during low-traffic periods, and are minor version upgrades tested before enabling auto-upgrade?
- [ ] **[Recommended]** Are CloudWatch alarms configured for CPU, free storage, replica lag, connection count, and deadlocks?
- [ ] **[Recommended]** Is the instance class right-sized using Performance Insights data and CloudWatch metrics, with Graviton (db.r7g) instances evaluated for cost savings?
- [ ] **[Optional]** Evaluate Aurora Limitless Database for horizontally scaling Aurora PostgreSQL beyond single-writer limits; distributes data across multiple DB shard groups with distributed query processing for workloads exceeding single-instance write throughput (millions of write transactions per second)
- [ ] **[Recommended]** Understand RDS Extended Support pricing for major engine versions past community end-of-life; AWS charges additional per-vCPU-hour fees (Year 1: $0.10, Year 2: $0.20, Year 3: $0.40) -- plan engine version upgrades before EOL to avoid escalating costs
- [ ] **[Recommended]** Evaluate Aurora I/O-Optimized cluster configuration for I/O-intensive workloads where I/O costs exceed 25% of total Aurora spend; eliminates per-I/O charges in exchange for ~30% higher compute and storage pricing, providing predictable costs for high-I/O applications

## Why This Matters

Database misconfiguration causes data loss, performance bottlenecks, and security breaches. Single-AZ deployments fail completely during AZ outages. Missing encryption violates most compliance frameworks. Untuned parameter groups lead to connection exhaustion and query performance issues. Aurora's architecture differs significantly from standard RDS and changes operational patterns.

## Common Decisions (ADR Triggers)

- **Aurora vs standard RDS** -- distributed storage and fast failover vs simpler pricing and broader engine support
- **Aurora Serverless v2 vs provisioned** -- variable workloads and cost optimization vs predictable performance
- **Global Database vs cross-region read replicas** -- sub-second RPO vs eventual consistency with manual promotion
- **Engine version and upgrade strategy** -- in-place upgrade vs blue-green deployment vs Aurora blue-green switchover
- **Instance class selection** -- Graviton vs Intel, memory-optimized vs general purpose, right-sizing cadence
- **Proxy layer** -- RDS Proxy for connection pooling with Lambda and serverless vs application-level connection pooling
- **Backup and retention strategy** -- automated backups vs manual snapshots, cross-region snapshot copy
- **Aurora I/O-Optimized vs Standard** -- I/O-Optimized eliminates per-I/O charges at ~30% higher compute/storage cost; cost-effective when I/O exceeds 25% of Aurora bill; Standard is better for low-I/O workloads
- **Aurora Limitless Database vs sharding alternatives** -- managed horizontal scaling for Aurora PostgreSQL vs application-level sharding vs Citus vs moving to DynamoDB for extreme write throughput needs
- **RDS Extended Support vs engine upgrade** -- accepting extended support surcharges for delayed upgrades vs planning timely major version upgrades; balance upgrade risk against escalating Year 1/2/3 per-vCPU costs

## Reference Architectures

- [AWS Architecture Center: Databases](https://aws.amazon.com/architecture/databases/) -- reference architectures for Aurora, RDS Multi-AZ, and read replica topologies
- [AWS Well-Architected Labs: Reliability - RDS and Aurora](https://www.wellarchitectedlabs.com/reliability/) -- hands-on labs for building resilient database architectures with failover testing
- [AWS Prescriptive Guidance: Database migration and modernization](https://docs.aws.amazon.com/dms/latest/userguide/) -- patterns for migrating to Aurora and RDS including blue-green deployments
- [Aurora Global Database reference architecture](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html) -- cross-region disaster recovery design with sub-second RPO
- [AWS Database Blog: Aurora Serverless v2 architecture](https://aws.amazon.com/blogs/database/) -- design patterns for Aurora Serverless v2 scaling and cost optimization

## Security Group Patterns

### Security Group Referencing (Recommended)

Allow inbound traffic on port 5432 (PostgreSQL) or 3306 (MySQL) from the application-tier security group **by security group ID**, not by CIDR block. This is the recommended pattern because if instances change IP addresses (scaling events, replacements, failovers), access rules remain valid.

```
RDS Security Group:
  Inbound Rule:
    Type: PostgreSQL (TCP 5432)
    Source: sg-0abc1234def56789 (application security group)
```

This is more maintainable and more secure than CIDR-based rules, which break when IPs change and may inadvertently allow access from unintended sources.

### Private Subnet Pattern

RDS should always be deployed in private subnets (subnets with no route to an internet gateway):

- **Private subnets**: No internet gateway route in the subnet's route table. RDS instances are unreachable from the internet.
- **Security group as additional layer**: Even in a private subnet, restrict inbound traffic to only the security groups that need access.
- **Public accessibility = false**: Always set `PubliclyAccessible` to `false`. Even in a private subnet, setting this to `true` allocates a public IP and creates a DNS resolution path from the internet.
- Defense in depth: private subnet + security group + `PubliclyAccessible=false` together provide layered protection.

### EKS Pod to RDS

When using Amazon VPC CNI with **Security Groups for Pods (SGP)**, pods receive their own ENI with a dedicated security group:

- Assign a security group to pods via `SecurityGroupPolicy` CRD.
- Reference the pod security group ID in the RDS security group's inbound rules.
- This provides pod-level network isolation -- only pods with the designated security group can reach the database.
- Without SGP, all pods share the node's security group, meaning any pod on the node can reach RDS if the node SG is allowed.

### Lambda to RDS

VPC-attached Lambda functions receive a security group that can be referenced in RDS security group rules:

- Attach the Lambda function to the VPC and assign it a security group.
- Add an inbound rule to the RDS security group allowing the Lambda security group on port 5432/3306.
- **Use RDS Proxy**: Lambda functions can create many concurrent database connections due to rapid scaling. RDS Proxy pools and shares connections, preventing connection exhaustion. The Lambda security group is allowed to the RDS Proxy, and the Proxy's security group is allowed to the RDS instance.

### Bastion / SSM Access

For administrative database access:

- **Bastion host**: Deploy a bastion in a public or private subnet with its own security group. Add an inbound rule to the RDS security group allowing the bastion's security group on the database port. Connect via SSH tunnel.
- **SSM Session Manager port forwarding**: No security group rule is needed for SSM itself -- SSM communicates outbound to the SSM service endpoint. Use `aws ssm start-session --document-name AWS-StartPortForwardingSessionToRemoteHost` to tunnel to the RDS endpoint. The RDS security group must allow inbound from the instance running the SSM agent (its security group or the VPC CIDR).
- SSM is preferred over bastion hosts because it eliminates the need to manage SSH keys and expose port 22.

### Cross-Account Access

For multi-account architectures where an application in one AWS account needs to reach RDS in another:

- Establish **VPC peering** (or Transit Gateway) between the two accounts' VPCs.
- Security group referencing works across accounts when the peering connection ID is specified: the RDS security group can reference a security group in the peered VPC using the format `account-id/sg-id` (requires the peering connection to be active and routes configured).
- Ensure CIDR ranges do not overlap between the peered VPCs.
- DNS resolution across the peering connection must be enabled for RDS endpoint resolution to work.

### Common Security Group Mistakes

- **0.0.0.0/0 on RDS security group**: Never allow all inbound traffic to a database. This is the most common and most dangerous misconfiguration.
- **Public accessibility enabled**: Setting `PubliclyAccessible=true` allocates a public IP and makes the RDS endpoint resolvable from the internet, even if the security group is restrictive. A future SG rule change could expose the database.
- **CIDR-based rules that break when IPs change**: Using specific IP CIDRs instead of security group references means rules become stale during scaling events, instance replacements, or failovers.
- **Forgetting CI/CD access for migrations**: Database migration tools (Flyway, Liquibase, Alembic) running in CI/CD pipelines need database access. Allow the CI/CD runner's security group (or use SSM port forwarding from the pipeline).
- **Overly broad VPC CIDR rules**: Allowing the entire VPC CIDR (e.g., 10.0.0.0/16) grants access to every resource in the VPC. Prefer security group references for least-privilege access.

---

## See Also

- `general/data.md` -- General data architecture patterns and database selection criteria
- `providers/aws/secrets-manager.md` -- Credential rotation for RDS/Aurora database passwords
- `providers/aws/vpc.md` -- Private subnet deployment and security group patterns for databases
- `providers/aws/dynamodb.md` -- DynamoDB as a NoSQL alternative for key-value workloads
