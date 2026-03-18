# AWS Migration Services

## Scope

AWS services for workload and data migration to the cloud. Covers Application Migration Service (MGN) for server rehost, DataSync for high-performance data transfer, Transfer Family for managed file transfer protocols, Migration Hub for centralized tracking, and Application Discovery Service.

AWS provides a suite of purpose-built migration services that address different phases and patterns of workload and data movement to the cloud. This file covers Application Migration Service (MGN) for server rehost (lift-and-shift) to EC2, DataSync for high-performance data transfer between on-premises storage and AWS, Transfer Family for managed file transfer protocols (SFTP/FTPS/FTP/AS2) fronting S3 and EFS, and Migration Hub for centralized discovery and tracking across all migration tools. Cross-reference with `general/workload-migration.md` for migration strategy patterns, `general/data-migration-tools.md` for database-layer migration (DMS), `providers/aws/ec2-asg.md` for target compute design, `providers/aws/s3.md` for storage destinations, and `patterns/migration-cutover.md` for cutover planning.

## Checklist

- [ ] [Critical] Select the correct migration service for each workload: MGN for server rehost (OS + applications lifted to EC2), DataSync for bulk or ongoing data transfer to S3/EFS/FSx, Transfer Family for partner/customer file exchange over SFTP/FTPS/FTP/AS2, and DMS for database migration (separate knowledge file) — mismatching the tool to the workload pattern causes unnecessary complexity and cost
- [ ] [Critical] Deploy and validate MGN replication agents on all source servers before scheduling any cutover window (agents perform continuous block-level replication; initial sync can take hours to days depending on disk size and bandwidth — the replication lag must reach zero before cutover is safe)
- [ ] [Critical] Configure MGN launch templates with the correct target instance type, subnet, security groups, and IAM instance profile — these settings determine the network position and permissions of the migrated server in AWS and cannot be easily changed mid-cutover
- [ ] [Recommended] Run MGN test launches for every server before the production cutover (test launches create isolated EC2 instances from the replicated data without disrupting replication; validate application functionality, network connectivity, and DNS resolution in the test environment)
- [ ] [Recommended] Define MGN post-launch actions to automate post-cutover tasks: uninstalling source-platform agents (e.g., VMware Tools), installing AWS-specific agents (CloudWatch, SSM), updating configuration files with new endpoints, and running application-level smoke tests — manual post-cutover steps are error-prone under time pressure
- [ ] [Recommended] Deploy the DataSync agent as a VMware VM, Hyper-V VM, KVM VM, or EC2 instance with network access to both source storage (NFS, SMB, HDFS, or object storage) and the AWS DataSync service endpoint; verify the agent can sustain the required throughput by running a test task before committing to a migration schedule
- [ ] [Recommended] Configure DataSync task scheduling and bandwidth throttling to avoid saturating production network links during business hours (DataSync supports cron-based scheduling and bytes-per-second throttling; set throttle limits based on measured available bandwidth minus headroom for production traffic)
- [ ] [Recommended] Enable DataSync data verification to validate transferred data integrity (options: verify only transferred data, verify entire dataset, or skip verification — skipping is faster but risks undetected corruption; full verification adds a scan pass after transfer)
- [ ] [Recommended] Register all migration tools (MGN, DMS, DataSync) with Migration Hub to maintain a single tracking dashboard — without centralized tracking, migration status is scattered across multiple consoles and teams lose visibility into overall progress
- [ ] [Recommended] Run Application Discovery Service before migration planning: agentless discovery (via vCenter connector) captures VM inventory, configuration, and utilization metrics; agent-based discovery adds network dependency mapping and running process information — the agent-based data is essential for grouping servers into migration waves
- [ ] [Optional] Configure Transfer Family with a VPC endpoint (instead of a public endpoint) when file transfer partners connect over Direct Connect or VPN — VPC endpoints keep traffic off the public internet and allow security group restrictions on the endpoint
- [ ] [Optional] Integrate Transfer Family with an external identity provider (Active Directory via AWS Directory Service, or a custom Lambda-backed provider) to authenticate users against existing credentials rather than managing SSH keys or service-managed users separately
- [ ] [Optional] Use Migration Hub Orchestrator for multi-step migration workflows that coordinate across MGN, DMS, and custom scripts — Orchestrator provides predefined templates for common migration patterns (e.g., SAP, SQL Server Always On) and tracks step-by-step execution with rollback points
- [ ] [Optional] Configure MGN source server tags and wave groupings in Migration Hub to organize servers into migration waves aligned with application dependencies — migrating interdependent servers together in a single wave reduces the risk of partial-migration failures

## Why This Matters

Migration failures rarely stem from the replication technology itself. They stem from insufficient testing, missing post-launch automation, and poor coordination across tools. MGN replicates blocks reliably, but if the launch template puts the server in the wrong subnet, or the application configuration still points to on-premises database endpoints, the migrated server starts up and immediately fails. Every hour of cutover-window troubleshooting erodes stakeholder confidence and risks a rollback decision that wastes weeks of preparation.

Data migration has its own failure modes. DataSync can move petabytes efficiently, but without bandwidth throttling it can saturate a shared WAN link and disrupt production operations. Without data verification enabled, corrupted files may not be detected until weeks after the migration when an application reads them. Transfer Family simplifies file exchange but choosing the wrong endpoint type (public vs. VPC) can either expose the service unnecessarily or make it unreachable by external partners.

Migration Hub exists because large migrations involve dozens of servers, multiple databases, and terabytes of file data — all moving through different tools on different timelines. Without a single pane of glass, teams lose track of which servers have been tested, which are mid-replication, and which are ready for cutover. Discovery data from Application Discovery Service prevents the common failure of migrating a server without realizing it depends on another server that is scheduled for a later wave.

## Common Decisions (ADR Triggers)

### Rehost (MGN) vs. replatform vs. refactor [Critical]
MGN performs a lift-and-shift: the server arrives in EC2 with the same OS, applications, and configuration. This is the fastest path but carries technical debt (on-premises assumptions baked into the workload). Replatforming (e.g., moving to RDS instead of a self-managed database on EC2) adds migration effort but reduces operational burden. Refactoring (rewriting for cloud-native services) provides the most benefit but takes the most time. Document the migration strategy per workload tier and the criteria used to assign each workload to a strategy (time pressure, application complexity, vendor support, licensing).

### MGN agent-based replication vs. agentless (vCenter) [Recommended]
Agent-based replication installs a lightweight agent on each source server that performs continuous block-level replication directly to AWS. This works across all supported platforms (VMware, Hyper-V, physical, Azure VMs, GCP VMs). Agentless replication (via vCenter connector) avoids installing agents on source servers but requires VMware infrastructure and has limitations on supported OS versions and disk configurations. Choose agent-based when source servers span multiple hypervisors or include physical machines. Choose agentless when the environment is purely VMware and the organization prohibits installing third-party agents on production servers. Document the source platform mix and agent installation policy.

### DataSync vs. S3 CLI/SDK vs. Snow Family for bulk data transfer [Critical]
DataSync provides managed, high-performance transfer with scheduling, throttling, verification, and incremental sync — ideal for ongoing or large one-time transfers over network. S3 CLI (`aws s3 sync`) is simpler but lacks built-in throttling, scheduling, and verification — suitable for smaller, ad-hoc transfers. Snow Family bypasses the network entirely for multi-terabyte transfers where bandwidth is insufficient (see `providers/aws/snow-family.md`). Document the data volume, available bandwidth, transfer frequency (one-time vs. ongoing), and whether the data must be verified post-transfer.

### Transfer Family endpoint type: public vs. VPC [Recommended]
Public endpoints are accessible from the internet with an AWS-provided or custom hostname — appropriate when external partners (customers, vendors) need to upload or download files. VPC endpoints restrict access to traffic arriving over the VPC, Direct Connect, or VPN — appropriate for internal transfers or when partners connect over private circuits. A public endpoint with an allowlisted IP range via security groups is a middle ground but adds management overhead. Document the connectivity model of each file transfer partner and the organization's security policy on internet-facing services.

### Transfer Family identity provider: service-managed vs. AD vs. custom [Optional]
Service-managed users are the simplest (SSH keys or passwords stored in Transfer Family) but create a separate identity silo. AWS Directory Service integration authenticates users against an existing Active Directory — appropriate when file transfer users already have AD accounts. A custom Lambda-backed identity provider enables arbitrary authentication logic (e.g., querying an external user database, enforcing MFA) but requires developing and maintaining the Lambda function. Document the number of file transfer users, whether they already have AD accounts, and whether custom authentication logic is required.

### Discovery approach: agentless (vCenter connector) vs. agent-based [Recommended]
Agentless discovery via the Application Discovery Service vCenter connector collects VM inventory, CPU/memory/disk configuration, and utilization metrics without installing anything on guest operating systems. Agent-based discovery installs the AWS Discovery Agent on each server and additionally captures running processes, network connections, and inter-server dependencies. Agentless is faster to deploy and less intrusive but cannot map application-level dependencies. Agent-based provides the network dependency data needed to group servers into migration waves. Document the scope of the migration, whether dependency mapping is required, and whether the organization permits agent installation on production servers.

## See Also

- `general/workload-migration.md` — Migration strategy patterns (6 Rs), wave planning, cutover coordination
- `general/data-migration-tools.md` — Database Migration Service (DMS), Schema Conversion Tool (SCT)
- `providers/aws/ec2-asg.md` — Target compute instance types, placement, and scaling
- `providers/aws/s3.md` — Storage destination configuration, lifecycle policies, cross-region replication
- `providers/aws/snow-family.md` — Offline data transfer for bandwidth-constrained scenarios
- `patterns/migration-cutover.md` — Cutover planning, rollback procedures, communication plans
- `general/database-migration.md` — Database migration strategies and tooling
