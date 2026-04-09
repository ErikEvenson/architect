# AWS S3 Files

## Scope

AWS S3 Files is a shared file system interface to Amazon S3 that exposes bucket contents with full file system semantics. Data remains in S3 as objects but is simultaneously accessible to applications using standard file system operations (open/read/write/seek, directory listings, POSIX-style metadata) without copying or syncing to a separate file system. An EFS-based intelligent cache holds the active working set on high-performance storage; cold data is read directly from S3 and inactive data ages out automatically. Covers when to choose S3 Files over Mountpoint for S3, EFS, FSx, and Storage Gateway, plus cache sizing, performance envelope, security, and cost trade-offs.

## Checklist

- [ ] **[Critical]** Confirm the workload genuinely needs file system semantics (POSIX paths, partial writes, rename, directory listings, file locking) rather than object semantics; if object APIs suffice, prefer plain S3 or Mountpoint for S3 to avoid the cache cost layer
- [ ] **[Critical]** Document the decision rationale vs alternatives (Mountpoint for S3, EFS, FSx for Lustre/OpenZFS/NetApp ONTAP, Storage Gateway File Gateway) as an ADR; the choice is rarely obvious and is hard to reverse cleanly
- [ ] **[Critical]** Size the cache expiry window (1-365 days, default 30) to the working-set re-access pattern; too short causes repeated cold reads from S3 (latency + request cost), too long inflates EFS cache cost for data that will not be reused
- [ ] **[Critical]** Verify the per-bucket performance ceiling (up to 4 TB/s aggregate read, 10M+ IOPS, 25,000 concurrent compute resources) is sufficient for peak workload; design for shard/bucket fan-out if a single workload would exceed it
- [ ] **[Critical]** Ensure data resident in S3 Files is governed by the same bucket-level controls as object access: Block Public Access, bucket policy, encryption (SSE-S3/SSE-KMS), versioning, Object Lock, and replication; the file interface does not bypass S3 security
- [ ] **[Recommended]** Model cost against the alternatives explicitly: S3 storage + S3 Files cache + request charges vs. (EFS or FSx) standalone vs. (S3 + Mountpoint) for the realistic working-set size; the "up to 90% cheaper" claim depends on cold-to-hot ratio
- [ ] **[Recommended]** Plan VPC/network access: which VPCs, accounts, and on-prem networks mount the file system; document mount targets, security groups, and any cross-account access via bucket policy
- [ ] **[Recommended]** Establish observability: cache hit ratio, cold-read latency to S3, throughput, IOPS, evictions, and cost per GB cached; alert on cache thrash (high evictions + high cold reads)
- [ ] **[Recommended]** Validate consistency expectations for workloads that mix file-interface writers and object-API readers (or vice versa) against AWS-documented semantics; do not assume strong cross-interface ordering for the same key
- [ ] **[Recommended]** For HPC, ML training, genomics, or media workflows, benchmark the actual job against S3 Files vs. FSx for Lustre on representative data before committing; cache warm-up cost matters for short-lived clusters
- [ ] **[Optional]** Document the migration path for any existing EFS or FSx mounts being replaced, including cutover, dual-mount validation, and rollback
- [ ] **[Optional]** Where the same bucket serves both file-interface and object-interface consumers, define naming/prefix conventions so file paths remain stable as object lifecycles run

## Why This Matters

Workloads that need POSIX semantics on top of S3 data have historically required either copying data into a separate file system (EFS, FSx) -- duplicating storage cost, adding sync complexity, and creating a second source of truth -- or accepting the limitations of Mountpoint for S3 (no random writes, limited rename/append support, no file locking). S3 Files removes the duplication: there is one copy of the data in S3, and both file and object consumers see it simultaneously. For HPC, ML training, genomics pipelines, media post-production, and lift-and-shift of file-oriented applications, this can collapse a multi-tier storage architecture into a single tier.

The trade-off is the EFS-based cache layer: performance and cost depend heavily on whether the active working set fits in the cache window. A workload that re-reads the same files repeatedly within the cache window approaches EFS-like latency at S3-like storage cost. A workload with a large, cold tail or short cache window pays cold-read latency and S3 GET request costs on every miss. Misjudging the working-set profile is the most common way an S3 Files deployment turns out more expensive or slower than the alternative it replaced. The cache window, the per-bucket throughput ceiling, and the alternatives comparison are the decisions that drive that outcome and belong in an ADR.

## Common Decisions (ADR Triggers)

- **S3 Files vs Mountpoint for S3** -- Mountpoint is free, requires no cache, and is sufficient for sequential read-heavy workloads (ML training data loaders, log scanning, ETL reads) that can tolerate its write limitations. Choose S3 Files when the workload requires random writes, file locking, rename, append, low-latency repeated reads of the same files, or when many clients need shared coherent access. Mountpoint is the right default for read-mostly batch; S3 Files is the right default for interactive or write-heavy workloads on S3 data.
- **S3 Files vs EFS** -- EFS is the right answer when the entire data set is hot, latency must be predictable, and the data does not also need to be accessed via S3 object APIs. S3 Files wins when the data also has object-API consumers (analytics, lifecycle to Glacier, replication, lambda triggers), when the cold tail is large relative to the hot working set, or when the data already lives in S3 and copying it would be operationally painful.
- **S3 Files vs FSx for Lustre** -- FSx for Lustre remains the right answer for HPC workloads with extreme parallel throughput requirements, sub-millisecond latency expectations, and well-defined job durations where the link-to-S3 import/export model fits. S3 Files is more appropriate when the workload is long-running or interactive, when many independent jobs share a working set, or when the operational overhead of Lustre filesystem lifecycle management is unwanted.
- **Cache window sizing** -- The window must be longer than the longest meaningful re-access interval for hot data, but short enough that genuinely cold data evicts before it accumulates EFS cost. Workloads with weekly cycles need at least 7 days; ML training that re-reads the same shards across epochs over days needs the full epoch span; one-shot ETL jobs may run fine at the 1-day minimum. Document the chosen window with a justification tied to the access pattern.
- **Single bucket vs sharded buckets for scale-out** -- A single bucket is simpler but bounded by the per-bucket throughput and concurrency ceiling. Workloads expected to approach those ceilings should be sharded across multiple buckets at design time, with a routing or naming convention that keeps related data co-located within a shard. Re-sharding later is operationally expensive.
- **Cross-account and cross-VPC access model** -- Decide up-front whether the file system is mounted only from the owning account/VPC or shared across accounts/VPCs. Cross-account access goes through bucket policies and (where applicable) Access Points; cross-VPC access requires explicit network design. Retrofitting cross-account access after data has been written is harder than designing for it.

## Reference Architectures

### ML Training on Shared Datasets
S3 bucket holds training shards (versioned, SSE-KMS, lifecycle to IA for old versions). S3 Files exposes the bucket to a GPU training cluster (up to thousands of nodes) with a cache window sized to the full training run. Trainers read shards via the file interface; checkpoints are written back through the same interface and become S3 objects immediately, picked up by an evaluation pipeline that reads them via the object API. No separate FSx filesystem to provision per job.

### Genomics / HPC Pipeline
Reference data and intermediate results live in S3. The HPC cluster mounts S3 Files; pipeline stages read inputs and write outputs as files. Long-tail reference data stays cold in S3 and is paid for at S3 prices; the active working set per run is cached. Object-API consumers (audit, archive, downstream analytics in Athena) read the same data without a copy step.

### Lift-and-Shift File Application onto S3
A legacy application that requires a POSIX filesystem mounts an S3 Files file system instead of provisioning EFS. Existing object-storage consumers of the same bucket (backup, analytics, replication) continue to work unchanged. The application gains S3 features (versioning, Object Lock, CRR, lifecycle) it could not get on EFS. Cache window is tuned to the application's actual working set after a baseline period.

### Media Post-Production Shared Storage
Editors and render nodes mount S3 Files; raw footage and project files live in S3. Active project files stay in cache; finished projects age out and remain in S3 (transitioned to Glacier Instant Retrieval by lifecycle policy). New project ingest from S3 upload tools is immediately visible to the file mount without a sync step.

---

## Reference Links

- [Amazon S3 Files product page](https://aws.amazon.com/s3/features/files/) -- feature overview, performance envelope, and positioning vs other file storage options

## See Also

- `providers/aws/s3.md` -- Object-interface S3: storage classes, encryption, replication, lifecycle, Object Lock
- `providers/aws/storage.md` -- AWS block, file, and hybrid storage services (EBS, EFS, FSx, Storage Gateway, DataSync)
- `providers/aws/ai-ml-services.md` -- ML training and inference workloads that may benefit from file-interface access to S3 data
- `general/data.md` -- General data architecture and storage tier selection
