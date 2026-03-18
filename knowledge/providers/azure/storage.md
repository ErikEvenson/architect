# Azure Storage

## Scope

Azure storage services including Blob Storage, Azure Files, and Data Lake Gen2. Covers redundancy tiers (LRS/ZRS/GRS/GZRS), access tiers (Hot/Cool/Cold/Archive), lifecycle management, Private Endpoints, immutability policies, and Entra ID authorization.

## Checklist

- [ ] **[Critical]** Is the storage account redundancy level selected based on durability and availability requirements -- LRS (3 copies, single datacenter), ZRS (3 copies, 3 availability zones), GRS (6 copies, 2 regions), GZRS (zone-redundant + geo-redundant)?
- [ ] **[Recommended]** Are Blob Storage access tiers assigned appropriately -- Hot for frequent access, Cool for infrequent (30+ day), Cold for rare (90+ day), Archive for compliance/backup (180+ day, hours to rehydrate)?
- [ ] **[Recommended]** Are lifecycle management policies configured to automatically transition blobs between tiers and delete expired objects based on last-modified or last-accessed time?
- [ ] **[Critical]** Are private endpoints configured for storage accounts, disabling public network access and restricting traffic to specific VNets and subnets?
- [ ] **[Recommended]** Is Azure Data Lake Storage Gen2 (hierarchical namespace) enabled for analytics workloads requiring directory-level ACLs and high-throughput data processing?
- [ ] **[Recommended]** Are immutability policies (time-based retention or legal hold) configured for compliance data to meet WORM (Write Once Read Many) requirements?
- [ ] **[Recommended]** Is soft delete enabled for blobs (and containers) with an appropriate retention period (7-365 days) to protect against accidental deletion?
- [ ] **[Optional]** Is blob versioning enabled for data that requires point-in-time recovery and audit trails of all changes?
- [ ] **[Critical]** Are storage firewalls configured with allowed IP ranges, VNet rules, and resource instance rules, with exceptions only for trusted Microsoft services?
- [ ] **[Recommended]** Is Azure Files deployed with the correct protocol (SMB 3.x for Windows, NFS 4.1 for Linux) and tier (Premium SSD for IOPS-intensive, Standard for general purpose)?
- [ ] **[Critical]** Is Microsoft Entra ID authorization used for blob and queue access (Azure RBAC: Storage Blob Data Reader/Contributor/Owner) instead of shared access keys?
- [ ] **[Recommended]** Are storage account access keys rotated on a schedule, or preferably disabled entirely in favor of Entra ID and managed identity authentication?
- [ ] **[Optional]** Is AzCopy or Azure Data Factory configured for large-scale data migration and scheduled data movement with appropriate concurrency and bandwidth limits?
- [ ] **[Recommended]** Are storage account diagnostics enabled, streaming blob read/write/delete metrics and logs to Log Analytics for access auditing and cost analysis?

## Why This Matters

Azure Storage is the foundational data service underpinning blobs, files, queues, tables, and Data Lake. Unlike AWS S3 (single object store), Azure separates Blob Storage, Azure Files, and Data Lake Gen2 as distinct capabilities within a storage account. Redundancy is selected at account creation and affects both cost and disaster recovery capability -- changing from LRS to GRS requires data migration. Access tiers provide significant cost savings (Archive is ~$0.00099/GB/month vs Hot at ~$0.018/GB/month) but Archive rehydration can take up to 15 hours. Storage accounts default to publicly accessible endpoints, making private endpoints and firewall rules essential for security.

## Common Decisions (ADR Triggers)

- **Redundancy tier** -- LRS (lowest cost, single datacenter risk) vs ZRS (zone resilience, ~25% more) vs GRS/GZRS (regional failover, ~2x cost); RA-GRS adds read access to secondary region
- **Blob Storage vs Data Lake Gen2** -- flat namespace for simple object storage vs hierarchical namespace for analytics with directory-level POSIX ACLs
- **Azure Files vs third-party NAS** -- native SMB/NFS with Entra ID integration vs Azure NetApp Files (ANF) for enterprise NAS features and sub-millisecond latency
- **Access key vs Entra ID vs SAS tokens** -- shared keys (simple but risky) vs RBAC with managed identities (recommended) vs scoped SAS tokens (time-limited, delegated)
- **Lifecycle management strategy** -- rule-based tier transitions based on age vs last-access-time tracking (requires enabling access time tracking)
- **Standard vs Premium storage** -- HDD-backed (cost-optimized, GPv2) vs SSD-backed (performance-optimized, BlockBlobStorage or FileStorage) with different billing models
- **Encryption** -- Microsoft-managed keys (default, zero config) vs customer-managed keys in Key Vault (compliance requirement, key rotation responsibility)

## Reference Architectures

- [Azure Architecture Center: Storage architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/storage/storage-start-here) -- decision tree for selecting storage services based on workload requirements
- [Azure Storage redundancy](https://learn.microsoft.com/en-us/azure/storage/common/storage-redundancy) -- detailed comparison of LRS, ZRS, GRS, GZRS, RA-GRS, and RA-GZRS with failover behavior
- [Azure Well-Architected Framework: Data storage](https://learn.microsoft.com/en-us/azure/well-architected/) -- best practices for storage account configuration, security, and cost optimization
- [Azure Landing Zone: Storage](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/data-management/best-practices/data-lake-overview) -- Cloud Adoption Framework guidance for enterprise data lake and storage design
- [Azure Architecture Center: Big data with Data Lake Gen2](https://learn.microsoft.com/en-us/azure/architecture/data-guide/scenarios/data-lake) -- reference architecture for analytics workloads using hierarchical namespace storage

---

## See Also

- `general/data.md` -- General data architecture including storage tier selection
- `providers/azure/security.md` -- Key Vault for customer-managed encryption keys and managed identity authentication
- `providers/azure/disaster-recovery.md` -- Storage redundancy tiers and geo-failover behavior
- `providers/azure/networking.md` -- Private Endpoints and storage firewall configuration
