# NetApp Cloud Volumes (CVO, ANF, FSx for ONTAP, Google Cloud NetApp Volumes)

## Scope

NetApp's portfolio of cloud-resident ONTAP services and design decisions for hybrid cloud and cloud-native deployments. Covers Cloud Volumes ONTAP (CVO -- self-managed ONTAP on AWS EC2, Azure VMs, and GCP VMs), Azure NetApp Files (ANF -- native first-party Azure service), Amazon FSx for NetApp ONTAP (FSx ONTAP -- native first-party AWS service), Google Cloud NetApp Volumes (native first-party GCP service), BlueXP (formerly Cloud Manager) as the unified management plane, hybrid SnapMirror replication patterns between on-prem and cloud, multi-AZ HA configurations, service tier selection, pricing models (capacity-based, performance-tier-based, reserved capacity), and integration with cloud-native services (VMware Cloud on AWS, Azure VMware Solution, Kubernetes via Trident).

## Checklist

- [ ] **[Critical]** Is the correct NetApp cloud offering selected for the target cloud and use case? (FSx for NetApp ONTAP for AWS-native managed ONTAP with NFS/SMB/iSCSI; Azure NetApp Files for Azure-native managed NFS/SMB with sub-millisecond latency; Google Cloud NetApp Volumes for GCP-native managed NFS; Cloud Volumes ONTAP for full ONTAP feature parity and customer control across AWS/Azure/GCP)
- [ ] **[Critical]** Is the deployment topology designed for HA where required? (FSx for ONTAP and ANF support multi-AZ deployments; CVO offers Single Node, HA Pair within an AZ, and HA Pair across AZs; single-AZ deployments are not protected against AZ failure and should not be used for production unless DR is handled by cross-region replication)
- [ ] **[Critical]** Is the network topology correctly designed for the cloud provider? (FSx for ONTAP and ANF require dedicated subnets in the consumer VPC/VNet; CVO requires VPC/VNet placement and may need additional subnets for HA mediator and replication; cross-AZ HA introduces inter-AZ data transfer costs that can be significant)
- [ ] **[Critical]** Is BlueXP (formerly NetApp Cloud Manager) deployed as the management plane for fleet-level operations across CVO, FSx for ONTAP, and on-premises ONTAP clusters? (BlueXP unifies provisioning, replication setup, and cost reporting across hybrid deployments; required for many advanced features like SnapMirror to/from on-prem)
- [ ] **[Critical]** Are SnapMirror relationships configured for hybrid replication between on-premises ONTAP and the cloud target with appropriate RPO and bandwidth planning? (initial baseline transfer can take days for large datasets; ongoing incremental updates use bandwidth proportional to change rate; egress charges apply when replicating from cloud back to on-prem)
- [ ] **[Critical]** Is the service tier or instance class sized for both capacity and performance requirements? (ANF: Standard / Premium / Ultra service levels with throughput proportional to allocated capacity -- 16 / 64 / 128 KiB/s per GiB respectively; FSx for ONTAP: file system throughput tiers from 128 MB/s up to 4 GB/s independent of capacity; CVO: instance type drives both compute throughput and licensing tier)
- [ ] **[Recommended]** Is the pricing model selected with explicit cost forecasting? (ANF charges per allocated capacity per service level; FSx for ONTAP charges separately for SSD storage, capacity pool storage, throughput, and backups; CVO charges underlying cloud instance + EBS/managed disk + Cloud Volumes ONTAP licensing fees -- BYOL or Pay-As-You-Go)
- [ ] **[Recommended]** Are storage efficiency features (inline deduplication, compression, compaction, thin provisioning) verified to apply to the chosen offering? (CVO supports the full ONTAP efficiency feature set; FSx for ONTAP applies efficiency on the SSD tier; ANF applies efficiency transparently but does not surface ratios to the customer; capacity sizing should not assume optimistic data reduction without workload validation)
- [ ] **[Recommended]** Is encryption at rest configured with customer-managed keys when compliance requires customer control of key material? (FSx for ONTAP supports AWS KMS CMK; ANF supports Azure-managed and customer-managed keys via Azure Key Vault; CVO supports both cloud KMS integration and ONTAP-native NVE/NAE)
- [ ] **[Recommended]** Are FlexClone-based zero-copy volumes used for dev/test, CI/CD, and ephemeral workloads instead of full data copies? (FlexClone is supported on CVO and FSx for ONTAP; ANF supports cross-region replication clones; significant cost reduction for dev/test environments that need production-like data)
- [ ] **[Recommended]** Is FabricPool tiering configured (where supported) to move cold blocks from the performance tier to a cloud capacity tier (S3, Azure Blob, GCS)? (CVO supports FabricPool natively; FSx for ONTAP supports tiering to a capacity pool storage tier with lower per-GB cost; ANF tiering is more limited)
- [ ] **[Recommended]** Are application-consistent snapshots integrated via SnapCenter or BlueXP Backup and Recovery for databases and virtualization platforms? (crash-consistent storage snapshots are not equivalent to application-consistent backups for databases)
- [ ] **[Recommended]** Is the chosen offering verified as the right tool for the workload, rather than reflexively choosing CVO for ONTAP feature parity when a managed cloud-native offering would suffice? (CVO offers maximum control and feature parity with on-prem ONTAP but adds operational overhead; ANF and FSx for ONTAP eliminate ONTAP administration entirely for customers who only need NFS/SMB on cloud)
- [ ] **[Optional]** Is the offering integrated with the cloud's managed VMware service when in scope? (FSx for ONTAP is supported as a supplemental datastore for VMware Cloud on AWS, providing significant cost savings vs vSAN for capacity-heavy workloads; ANF is supported as a datastore for Azure VMware Solution)
- [ ] **[Optional]** Is BlueXP Copy and Sync used for one-time or scheduled data migration into the cloud, when SnapMirror is not available (non-ONTAP source) or when a simpler one-shot copy is preferred?
- [ ] **[Optional]** Is the Trident CSI driver deployed for Kubernetes persistent volume provisioning against CVO, ANF, FSx for ONTAP, or Google Cloud NetApp Volumes, with storage classes mapped to the appropriate backend?

## Why This Matters

The NetApp cloud portfolio is broad and easy to get wrong. Choosing CVO when ANF or FSx for ONTAP would suffice creates unnecessary operational overhead -- the customer is now running ONTAP themselves on cloud infrastructure, with all the upgrade, monitoring, and tuning responsibilities of an on-premises array. Conversely, choosing a managed offering when full ONTAP feature parity is required (SnapMirror Synchronous, MetroCluster IP, FabricPool to a specific tier) blocks the customer from features they may have built workflows around. The right answer depends on what the workload actually needs from ONTAP, not on which offering is most familiar.

Pricing surprises are common because the cost model differs across the four offerings. ANF charges per allocated GiB at the chosen service level regardless of utilization, so over-provisioning is expensive even if the volume is empty. FSx for ONTAP charges separately for SSD, capacity pool, throughput, and backups, so a sizing decision in one dimension does not predict total cost. CVO has the most variables (cloud instance, EBS or managed disk, Cloud Volumes ONTAP license, SnapMirror relationships, FabricPool egress) and is the easiest to misforecast. Cost modeling should be done in the cloud's native pricing calculator, not extrapolated from on-prem ONTAP capex.

Multi-AZ HA configuration is non-default for CVO and adds inter-AZ data transfer charges that scale with write volume. For write-heavy workloads, the inter-AZ transfer cost can exceed the storage cost. Single-AZ HA Pairs are appropriate for workloads where AZ-level resilience is provided by application-level replication or by a separate DR target in another region.

SnapMirror to and from cloud is the most powerful hybrid feature in the portfolio but is bandwidth- and egress-bound. Initial baseline transfers of multi-terabyte datasets can take days over a typical Direct Connect or ExpressRoute link, and repeated re-baselining due to broken relationships is expensive in both time and cloud egress charges. SnapMirror relationships should be designed once and monitored, not torn down and rebuilt casually.

Network placement constraints are stricter than they appear in the marketing material. ANF and FSx for ONTAP both require dedicated subnets that cannot be shared with general workloads, and ANF in particular has restrictions on subnet delegation that often surprise architects who try to reuse existing subnets. Network design should account for these constraints during VPC/VNet planning, not as an afterthought.

## Common Decisions (ADR Triggers)

- **Cloud offering selection** -- ANF for Azure-native NFS/SMB workloads requiring sub-millisecond latency vs FSx for NetApp ONTAP for AWS-native multi-protocol (NFS/SMB/iSCSI) ONTAP-managed-by-AWS vs Google Cloud NetApp Volumes for GCP-native NFS vs CVO for full ONTAP feature parity and customer-controlled administration across any cloud
- **Managed vs self-managed** -- managed offering (ANF, FSx for ONTAP, Google Cloud NetApp Volumes) for teams that want NFS/SMB without ONTAP administration vs CVO for teams that need ONTAP feature parity with on-prem and are willing to operate it themselves
- **HA topology** -- single-AZ HA Pair (lower cost, no AZ-level resilience) vs multi-AZ HA Pair (higher cost from inter-AZ data transfer, AZ-level resilience) vs single-region with cross-region SnapMirror DR (region-level resilience, async RPO)
- **Service tier (ANF)** -- Standard for cost-sensitive workloads with low throughput requirements vs Premium for typical database and VDI workloads vs Ultra for performance-critical workloads requiring 128 KiB/s per GiB
- **Throughput tier (FSx for ONTAP)** -- size throughput tier independently from capacity based on observed IOPS and bandwidth requirements; over-provisioning throughput is more cost-effective than over-provisioning capacity to get throughput
- **Hybrid replication strategy** -- on-prem ONTAP as primary with SnapMirror to cloud as DR (cloud as warm standby) vs cloud as primary with SnapMirror back to on-prem (cloud-first with on-prem retention) vs cross-region SnapMirror entirely within cloud for DR
- **Encryption key management** -- cloud-provider-managed keys (simplest, lowest operational overhead) vs customer-managed keys via cloud KMS (compliance, key rotation control) vs ONTAP-native NVE/NAE on CVO (consistent with on-prem key management)
- **VMware integration** -- FSx for ONTAP as supplemental datastore for VMware Cloud on AWS (significant cost reduction vs vSAN-only for capacity-heavy workloads) vs ANF as datastore for Azure VMware Solution vs no integration (VMware uses its own native storage)
- **Pricing model** -- capacity-allocated (ANF) vs component-based (FSx for ONTAP: SSD + capacity pool + throughput + backup) vs cloud-instance-plus-license (CVO BYOL or PAYG) -- pick whichever model maps cleanest to the workload's cost-sensitivity dimension

## Reference Links

- [Azure NetApp Files Documentation](https://learn.microsoft.com/en-us/azure/azure-netapp-files/) -- service tiers, capacity pools, network requirements, and Azure-native integration
- [Amazon FSx for NetApp ONTAP Documentation](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/what-is-fsx-ontap.html) -- file systems, SVMs, multi-AZ, throughput tiers, and AWS-native integration
- [Cloud Volumes ONTAP Documentation](https://docs.netapp.com/us-en/cloud-volumes-ontap/) -- deployment models, HA configurations, FabricPool, and SnapMirror configuration
- [Google Cloud NetApp Volumes Documentation](https://cloud.google.com/netapp/volumes/docs/discover/overview) -- service levels, network configuration, and GCP-native integration
- [BlueXP Documentation](https://docs.netapp.com/us-en/bluexp-family/) -- unified management plane for hybrid and multi-cloud NetApp deployments
- [NetApp Hybrid Cloud Reference Architectures](https://www.netapp.com/cloud-services/) -- patterns for SnapMirror replication, cloud bursting, and hybrid disaster recovery
- [Azure NetApp Files Performance Benchmarks](https://learn.microsoft.com/en-us/azure/azure-netapp-files/performance-benchmarks-linux) -- Linux NFS and Windows SMB performance characteristics by service level
- [FSx for ONTAP with VMware Cloud on AWS](https://aws.amazon.com/blogs/storage/configuring-amazon-fsx-for-netapp-ontap-as-external-storage-for-vmware-cloud-on-aws/) -- supplemental datastore configuration and use cases

## See Also

- `providers/netapp/ontap.md` -- on-premises ONTAP fundamentals and SnapMirror source/target patterns
- `providers/aws/storage.md` -- AWS storage services including FSx variants and S3 capacity pools
- `providers/azure/storage.md` -- Azure storage services including ANF and Azure Files
- `providers/vmware/vmc-aws.md` -- VMware Cloud on AWS, where FSx for ONTAP is commonly used as supplemental storage
- `general/storage.md` -- general storage architecture patterns and protocol selection
- `general/disaster-recovery.md` -- DR strategy patterns including hybrid cloud DR
- `general/cost.md` -- cloud cost management strategies relevant to capacity-allocated and component-based pricing
