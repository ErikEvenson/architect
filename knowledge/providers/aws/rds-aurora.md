# AWS RDS / Aurora

## Checklist

- [ ] Is Aurora chosen over standard RDS for production workloads that benefit from distributed storage, faster failover, and read scaling?
- [ ] Is Multi-AZ enabled for all production databases? (Aurora: automatic across 3 AZs; RDS: synchronous standby in a second AZ)
- [ ] Are read replicas configured to offload read-heavy workloads, and is the application using the reader endpoint?
- [ ] Is Aurora Global Database configured for cross-region disaster recovery with RPO under 1 second?
- [ ] Is Aurora Serverless v2 evaluated for variable or unpredictable workloads to reduce cost during idle periods?
- [ ] Are DB parameter groups and cluster parameter groups customized and version-controlled rather than using defaults?
- [ ] Is Performance Insights enabled with at least 7 days retention for query-level performance analysis?
- [ ] Is automated backup retention set to an appropriate window (7-35 days) with point-in-time recovery tested?
- [ ] Are database credentials stored in Secrets Manager with automatic rotation enabled?
- [ ] Is the database deployed in private subnets with security groups restricting access to only application-tier security groups?
- [ ] Is IAM database authentication enabled for services that support it, eliminating password management?
- [ ] Is encryption at rest enabled using a customer-managed KMS key, and is encryption in transit enforced (ssl_mode = verify-full)?
- [ ] Is the maintenance window scheduled during low-traffic periods, and are minor version upgrades tested before enabling auto-upgrade?
- [ ] Are CloudWatch alarms configured for CPU, free storage, replica lag, connection count, and deadlocks?
- [ ] Is the instance class right-sized using Performance Insights data and CloudWatch metrics, with Graviton (db.r7g) instances evaluated for cost savings?

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

## Reference Architectures

- [AWS Architecture Center: Databases](https://aws.amazon.com/architecture/databases/) -- reference architectures for Aurora, RDS Multi-AZ, and read replica topologies
- [AWS Well-Architected Labs: Reliability - RDS and Aurora](https://www.wellarchitectedlabs.com/reliability/) -- hands-on labs for building resilient database architectures with failover testing
- [AWS Prescriptive Guidance: Database migration and modernization](https://docs.aws.amazon.com/dms/latest/userguide/) -- patterns for migrating to Aurora and RDS including blue-green deployments
- [Aurora Global Database reference architecture](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html) -- cross-region disaster recovery design with sub-second RPO
- [AWS Database Blog: Aurora Serverless v2 architecture](https://aws.amazon.com/blogs/database/) -- design patterns for Aurora Serverless v2 scaling and cost optimization
