# AWS Storage (Block, File, and Hybrid)

## Scope

AWS storage services beyond S3 object storage. Covers EBS (volume types, snapshots, Multi-Attach), EFS (performance modes, throughput modes, lifecycle), FSx family (Windows File Server, Lustre, NetApp ONTAP, OpenZFS), Storage Gateway (S3 File Gateway, FSx File Gateway, Volume Gateway, Tape Gateway), DataSync (on-premises, cross-region, cross-account), Transfer Family (SFTP/FTPS/FTP), and encryption patterns across storage services.

## Checklist

- [ ] **[Critical]** Is the correct EBS volume type selected for the workload? (gp3 for general purpose with 3,000 baseline IOPS and 125 MiB/s independently tunable up to 16,000 IOPS/1,000 MiB/s; io2 for sustained high IOPS up to 64,000 per volume with 99.999% durability; io2 Block Express for up to 256,000 IOPS and 4,000 MiB/s on Nitro instances; st1 for throughput-intensive sequential workloads like data warehouses at up to 500 MiB/s; sc1 for cold infrequent-access data at lowest cost)
- [ ] **[Critical]** Is EBS volume sizing planned for both capacity and performance? (gp3 IOPS and throughput are provisioned independently of size; io2 is capped at 500 IOPS per GiB; st1 and sc1 throughput scales with volume size; undersized volumes may bottleneck IOPS or throughput regardless of instance capability)
- [ ] **[Recommended]** Are EBS snapshot lifecycle policies configured using Amazon Data Lifecycle Manager (DLM)? (automated creation, retention, and cross-region copy schedules; archive tier reduces snapshot costs by up to 75% for snapshots accessed less than once per 90 days with 24-72 hour restore time)
- [ ] **[Recommended]** Is io2 Multi-Attach configured for shared block storage use cases? (allows a single io2 volume to attach to up to 16 Nitro instances in the same AZ; requires a cluster-aware filesystem like GFS2 or OCFS2; not a replacement for shared file systems in most cases)
- [ ] **[Critical]** Is the correct EFS configuration selected? (General Purpose performance mode for latency-sensitive workloads, Max I/O for highly parallelized big data/media processing; Bursting throughput for variable workloads, Provisioned throughput for consistent performance, Elastic throughput for unpredictable spiky workloads that auto-scales up to 10 GiB/s)
- [ ] **[Recommended]** Are EFS lifecycle policies configured to transition infrequently accessed files to Infrequent Access (IA) storage class? (up to 92% cost savings; configurable transition after 1, 7, 14, 30, 60, 90, or 180 days of no access; Intelligent-Tiering moves files back to Standard on next access)
- [ ] **[Recommended]** Is the EFS deployment model selected based on availability requirements? (Regional for multi-AZ redundancy and highest availability; One Zone for single-AZ workloads like dev/test at ~47% cost savings; One Zone does not survive AZ failure)
- [ ] **[Critical]** Is the appropriate FSx file system selected for the workload? (FSx for Windows File Server for SMB/NTFS with Active Directory integration; FSx for Lustre for HPC and ML training with S3 integration; FSx for NetApp ONTAP for multi-protocol NFS/SMB/iSCSI with data tiering; FSx for OpenZFS for Linux workloads needing ZFS snapshots and clones)
- [ ] **[Recommended]** Is the correct Storage Gateway type deployed for hybrid storage? (S3 File Gateway for NFS/SMB to S3; FSx File Gateway for low-latency SMB access to FSx for Windows; Volume Gateway for iSCSI block storage with cached or stored modes and EBS snapshots; Tape Gateway for virtual tape library backup to S3 Glacier)
- [ ] **[Recommended]** Is AWS DataSync configured for data transfer workloads? (on-premises to AWS via agent on NFS/SMB/HDFS sources; cross-region and cross-account transfers without an agent; bandwidth throttling, scheduling, data integrity verification, and filtering; up to 10x faster than open-source tools)
- [ ] **[Optional]** Is AWS Transfer Family deployed for managed file transfer requirements? (fully managed SFTP, FTPS, FTP, and AS2 endpoints backed by S3 or EFS; integrates with existing identity providers via custom authentication or AWS Directory Service; eliminates self-managed file transfer server infrastructure)
- [ ] **[Critical]** Is encryption at rest configured across all storage services? (EBS: default encryption per region using aws/ebs KMS key or customer-managed CMK; EFS: encryption at creation only, cannot be enabled after; FSx: KMS encryption, configured at creation; enforce encryption via SCPs or AWS Config rules to prevent unencrypted volume creation)
- [ ] **[Recommended]** Has a storage decision framework been applied to select block vs file vs object storage? (block/EBS for single-instance low-latency databases and boot volumes; file/EFS/FSx for shared access across instances, containers, or Serverless; object/S3 for unstructured data, archives, and data lakes; avoid using EBS for shared access or EFS for database storage)

## Why This Matters

AWS offers distinct storage services for block, file, and hybrid workloads, each with significantly different performance characteristics, pricing models, and operational constraints. EBS volume type selection directly impacts database performance and cost -- gp3 provides 3,000 IOPS free at any size while io2 can deliver up to 64,000 IOPS but at $0.065 per provisioned IOPS-month. Choosing st1 for a random I/O workload or gp3 for a throughput-heavy sequential workload leads to either poor performance or wasted spend.

EFS costs $0.30/GB/month for Standard storage but only $0.025/GB/month for Infrequent Access. Without lifecycle policies, organizations routinely overspend by 5-10x on file storage containing predominantly cold data. The choice between Regional and One Zone EFS affects both cost and resilience -- One Zone is cheaper but cannot survive an availability zone failure.

FSx selection errors are particularly costly to reverse because file system migrations require full data copies. Choosing FSx for Windows File Server when the workload is Linux-native, or deploying FSx for Lustre for persistent file sharing rather than HPC burst workloads, creates operational complexity and unnecessary cost. Storage Gateway and DataSync fill critical hybrid roles but require understanding of caching behavior, bandwidth requirements, and endpoint placement to avoid performance bottlenecks during migration or ongoing hybrid operations.

## Common Decisions (ADR Triggers)

- **EBS volume type: gp3 vs io2 vs io2 Block Express** -- gp3 is the default for most workloads with independent IOPS/throughput tuning at lower cost; io2 for sustained high IOPS with 99.999% durability (vs 99.8-99.9% for gp3); io2 Block Express for extreme performance on Nitro instances (up to 256K IOPS, 4 GiB/s); st1/sc1 only for sequential throughput workloads
- **EFS throughput mode: Bursting vs Provisioned vs Elastic** -- Bursting scales throughput with storage size (50 MiB/s per TiB) and is free but unpredictable for small file systems; Provisioned guarantees consistent throughput at additional cost; Elastic auto-scales throughput on demand up to 10 GiB/s with pay-per-use pricing, ideal for spiky workloads
- **EFS deployment: Regional vs One Zone** -- Regional provides multi-AZ durability and is required for production workloads with high availability requirements; One Zone saves ~47% and is suitable for dev/test, reproducible data, or workloads already confined to a single AZ
- **FSx file system selection** -- Windows File Server for SMB/DFS/AD environments; Lustre for HPC/ML with transparent S3 data repository integration; NetApp ONTAP for multi-protocol (NFS+SMB+iSCSI) with automatic capacity tiering to S3; OpenZFS for Linux workloads needing instant snapshots, clones, and compression
- **Hybrid storage: Storage Gateway vs DataSync** -- Storage Gateway provides ongoing hybrid access (cache on-premises, store in AWS); DataSync is for one-time or scheduled data transfer tasks with verification; both can be used together (DataSync for initial migration, Storage Gateway for ongoing access)
- **Storage Gateway mode: File vs Volume vs Tape** -- File Gateway for NFS/SMB access to S3 objects; Volume Gateway cached mode for primary data in S3 with local cache; Volume Gateway stored mode for primary data on-premises with async snapshots to EBS; Tape Gateway replaces physical tape infrastructure with S3 Glacier backend
- **Encryption key management** -- AWS-managed keys (default, zero operational overhead) vs customer-managed CMKs in KMS (key policy control, rotation, cross-account access, compliance auditing via CloudTrail); some services require encryption at creation time and cannot be changed later

## Reference Links

- [Amazon EBS volume types](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html) -- detailed comparison of gp3, io2, io2 Block Express, st1, and sc1 performance and pricing
- [Amazon EBS Snapshots](https://docs.aws.amazon.com/ebs/latest/userguide/EBSSnapshots.html) -- snapshot creation, lifecycle management, cross-region copy, and archive tier
- [Amazon EFS performance](https://docs.aws.amazon.com/efs/latest/ug/performance.html) -- throughput modes, performance modes, and scaling characteristics
- [Amazon FSx documentation](https://docs.aws.amazon.com/fsx/) -- overview of all FSx file system types with comparison matrix
- [AWS Storage Gateway](https://docs.aws.amazon.com/storagegateway/latest/userguide/) -- deployment guides for File, Volume, and Tape Gateway types
- [AWS DataSync](https://docs.aws.amazon.com/datasync/latest/userguide/) -- transfer agent deployment, task configuration, and filtering
- [AWS Transfer Family](https://docs.aws.amazon.com/transfer/latest/userguide/) -- managed SFTP/FTPS/FTP endpoint setup and identity provider integration
- [AWS Storage Blog: Choosing the right storage](https://aws.amazon.com/blogs/storage/) -- decision frameworks and best practices for block, file, and object storage selection

---

## See Also

- `providers/aws/s3.md` -- AWS S3 object storage including storage classes, lifecycle, replication, and encryption
- `providers/aws/ec2-asg.md` -- EC2 instance types and EBS-optimized instance considerations
- `providers/aws/containers.md` -- EFS and EBS CSI drivers for EKS persistent volumes
- `providers/aws/migration-services.md` -- DataSync and Storage Gateway in the context of cloud migration
- `general/data.md` -- General data architecture including block vs file vs object storage patterns
