# GCP Storage

## Checklist

- [ ] **[Critical]** Is the appropriate Cloud Storage class selected per data access pattern? (Standard for frequent access, Nearline for <1/month, Coldline for <1/quarter, Archive for <1/year)
- [ ] **[Recommended]** Are Cloud Storage lifecycle policies configured to automatically transition objects between storage classes and delete expired objects, with age, creation date, and custom time conditions?
- [ ] **[Critical]** Is uniform bucket-level access enabled on all buckets (enforced via organization policy) to prevent ACL-based access and simplify IAM management?
- [ ] **[Recommended]** Is object versioning enabled on buckets requiring data protection, with lifecycle rules to limit the number of retained noncurrent versions or delete them after a set period?
- [ ] **[Critical]** Are retention policies and bucket locks configured for compliance workloads, understanding that locked retention policies are irreversible and prevent object deletion?
- [ ] **[Recommended]** Is dual-region or multi-region storage configured for high-availability workloads, with turbo replication (15-minute RPO) enabled for dual-region buckets requiring fast geo-redundancy?
- [ ] **[Recommended]** Are signed URLs or signed policy documents used for time-limited access to private objects, with V4 signatures and appropriate expiration times (max 7 days)?
- [ ] **[Recommended]** Is the correct Persistent Disk type selected for Compute Engine and GKE workloads? (pd-balanced for general use, pd-ssd for high IOPS, pd-extreme for >100K IOPS with provisioned throughput, pd-standard for cost-sensitive batch)
- [ ] **[Recommended]** Is Filestore configured with the appropriate tier (Basic HDD, Basic SSD, Zonal, Regional, Enterprise) for NFS workloads, with capacity planned for performance scaling?
- [ ] **[Optional]** Are Cloud Storage FUSE mounts used only for appropriate workloads (ML training data, batch processing), understanding POSIX compliance limitations and caching behavior?
- [ ] **[Optional]** Are Storage Transfer Service or Transfer Appliance configured for large-scale data migrations, with bandwidth and scheduling policies to avoid network saturation?
- [ ] **[Optional]** Are bucket-level notifications configured via Pub/Sub for event-driven processing of object creates, deletes, and metadata updates?
- [ ] **[Optional]** Is requestor-pays enabled on shared data buckets to shift egress and operation costs to data consumers rather than the bucket owner?

## Why This Matters

GCP Cloud Storage is the foundational object store with a uniquely tiered pricing model: storage class transitions are free when moving to colder tiers, but retrieval costs increase significantly (Archive retrieval is $0.05/GB vs $0 for Standard). Lifecycle policies are essential for cost control but must be designed carefully because class transitions are one-way (Standard to Nearline, never Nearline to Standard automatically). Persistent Disk performance scales linearly with disk size for pd-balanced and pd-ssd, meaning undersized disks deliver poor IOPS -- a common surprise for teams migrating from AWS EBS where performance tiers are more explicit. Filestore pricing is based on provisioned capacity, and performance scales with tier and size, making right-sizing critical.

## Common Decisions (ADR Triggers)

- **Storage class strategy** -- single class vs autoclass (automatic class management) vs manual lifecycle rules, cost modeling for access patterns
- **Replication model** -- single-region (cheapest) vs dual-region (specific region pair, turbo replication option) vs multi-region (US/EU/ASIA)
- **Block storage type** -- pd-balanced (default) vs pd-ssd vs pd-extreme (provisioned IOPS), regional persistent disk for HA
- **File storage tier** -- Filestore Basic vs Zonal/Regional vs Enterprise (snapshots, replication), Filestore vs Cloud Storage FUSE vs Parallelstore for HPC
- **Access control model** -- uniform bucket-level access (IAM only) vs fine-grained ACLs, signed URLs for external sharing
- **Data protection** -- object versioning vs bucket retention policies vs Object Lock, soft delete (default 7-day recovery)
- **Data transfer method** -- gsutil/gcloud CLI vs Storage Transfer Service vs Transfer Appliance (offline, 100TB+), interconnect transfer
- **Cost optimization** -- autoclass vs manual lifecycle rules, requestor-pays for shared datasets, committed use discounts on Persistent Disk

## Reference Architectures

- [Google Cloud Architecture Center: Storage](https://cloud.google.com/architecture#storage) -- reference architectures for object storage, file systems, and data lake patterns
- [Google Cloud Architecture Framework: Cost optimization - Storage](https://cloud.google.com/architecture/framework/cost-optimization/storage) -- best practices for storage class selection, lifecycle management, and cost control
- [Google Cloud: Best practices for Cloud Storage](https://cloud.google.com/storage/docs/best-practices) -- reference patterns for naming, access control, retry handling, and performance optimization
- [Google Cloud: Persistent Disk deep dive](https://cloud.google.com/compute/docs/disks/performance) -- reference for disk performance characteristics, IOPS scaling by size, and throughput limits per machine type
- [Google Cloud: Data transfer options](https://cloud.google.com/storage-transfer/docs/overview) -- reference architecture for selecting the right transfer mechanism based on data volume, network bandwidth, and timeline
