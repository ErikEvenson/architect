# HPE Nimble / Alletra Storage

## Scope

HPE Nimble Storage and Alletra storage arrays: platform selection (Alletra 5000/6000/9000/MP), InfoSight AI-driven operations, data protection and replication, performance tiering, multi-protocol access, and cloud integration. Covers initial deployment, ongoing operations, and data lifecycle management for block, file, and converged storage workloads.

## Checklist

- [ ] [Critical] Is the correct Alletra/Nimble platform selected for the workload? (Alletra 5000 for hybrid flash value tier, Alletra 6000 for all-NVMe mid-range, Alletra 9000/MP for mission-critical all-flash with guaranteed availability)
- [ ] [Critical] Is HPE InfoSight connected and active? (InfoSight provides predictive analytics, automated case creation, performance recommendations, and cross-stack visibility -- it must have cloud connectivity or be configured for on-premises proxy mode)
- [ ] [Critical] Are protection schedules configured with appropriate RPO? (snapshot schedules for local protection, replication schedules to secondary array or cloud for DR, with retention policies that account for ransomware recovery windows)
- [ ] [Critical] Is the array sized correctly for the workload IOPS, throughput, and capacity requirements, including headroom for snapshots, replication overhead, and future growth? (use HPE Nimble Storage Sizer tool)
- [ ] [Critical] Is multi-pathing configured correctly on all hosts? (MPIO with ALUA for iSCSI, or FC zoning with redundant fabric paths, with HPE Connection Manager or host integration toolkit installed)
- [ ] [Critical] Is the iSCSI or Fibre Channel network designed with dedicated storage VLANs, jumbo frames (9000 MTU for iSCSI), and redundant switches with no spanning tree on storage paths?
- [ ] [Recommended] Are volume collections used to group related volumes for application-consistent snapshots? (VMware integration via VASA/VVols or vCenter plugin, SQL/Oracle via application-aware snapshot orchestration)
- [ ] [Recommended] Is performance tiering configured? (Nimble hybrid arrays use adaptive flash caching with SSD and HDD tiers; Alletra all-flash arrays benefit from inline deduplication and compression tuning)
- [ ] [Recommended] Is deduplication and compression enabled with workload-appropriate settings? (always enabled on Alletra all-flash; on hybrid Nimble, test compression ratios and ensure SSD cache is sized for working set)
- [ ] [Recommended] Is the array management integrated into HPE GreenLake or Data Services Cloud Console for centralized fleet management, firmware updates, and capacity planning?
- [ ] [Recommended] Is encryption at rest enabled? (Nimble/Alletra supports self-encrypting drives and array-managed encryption keys -- plan for key management lifecycle and escrow)
- [ ] [Recommended] Are array firmware updates planned using InfoSight-recommended update paths, with non-disruptive controller failover tested before production upgrades?
- [ ] [Optional] Is HPE Cloud Volumes (cloud-based block storage) or Alletra MP cloud tiering evaluated for bursting capacity to AWS/Azure without array expansion?
- [ ] [Optional] Is NimbleOS file access (SMB/NFS) configured on supported models for converged block-and-file workloads, reducing the need for a separate NAS platform?
- [ ] [Optional] Is the array integrated with VMware vVols for per-VM storage policies, snapshot management, and granular QoS enforcement?

## Why This Matters

HPE Nimble and Alletra arrays are differentiated by InfoSight, which uses telemetry from the installed base to predict failures, recommend firmware updates, and identify performance issues before they impact workloads. Organizations that disable or ignore InfoSight lose the primary operational advantage of the platform. Nimble hybrid arrays rely heavily on their adaptive flash caching algorithm -- undersizing the SSD tier relative to the working set causes dramatic performance degradation. Alletra all-flash arrays eliminate this concern but require careful deduplication ratio planning to avoid overcommitting capacity based on optimistic data reduction assumptions. Replication between Nimble/Alletra arrays is straightforward but requires matching array families (Nimble-to-Nimble or Alletra-to-Alletra) for full feature compatibility. The transition from Nimble branding to Alletra is ongoing, and some environments run mixed fleets that complicate unified management.

## Common Decisions (ADR Triggers)

- **Platform tier** -- Alletra 5000 (hybrid, value) vs Alletra 6000 (all-NVMe, mid-range) vs Alletra 9000/MP (mission-critical, guaranteed availability SLA)
- **Protocol selection** -- iSCSI (lower cost, Ethernet-based) vs Fibre Channel (lower latency, dedicated fabric) vs NVMe-oF (Alletra 6000/9000, ultra-low latency)
- **Data protection strategy** -- local snapshots + remote replication vs third-party backup (Veeam, Commvault with array-integrated snapshots) vs cloud tiering for long-term retention
- **Replication topology** -- active-passive (async replication to DR site) vs synchronous replication (Alletra 9000/MP Peer Persistence for zero-RPO) vs 3-site fan-out
- **Data reduction** -- always-on dedupe + compression (Alletra all-flash) vs selective compression (Nimble hybrid, workload-dependent) vs disabled for latency-sensitive workloads
- **Management plane** -- array-local management (NimbleOS GUI) vs HPE Data Services Cloud Console (centralized SaaS) vs GreenLake integration
- **VMware integration** -- traditional VMFS on LUNs vs vVols with per-VM storage policies vs NFS datastores for specific workloads

## Reference Links

- [HPE Alletra Storage Product Page](https://www.hpe.com/us/en/alletra.html) -- platform comparison, specifications, and positioning for Alletra 5000/6000/9000/MP
- [HPE InfoSight for Storage](https://www.hpe.com/us/en/storage/infosight.html) -- AI-driven predictive analytics, telemetry, and cross-stack recommendations
- [HPE Nimble Storage Best Practices Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00112682en_us) -- iSCSI and FC network design, host integration, and performance tuning
- [HPE Data Services Cloud Console](https://www.hpe.com/us/en/storage/data-services-cloud-console.html) -- centralized SaaS management for Alletra and Nimble arrays
- [HPE Nimble Storage / Alletra Replication Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00002305en_us) -- snapshot replication, synchronous replication, and DR orchestration
- [HPE Nimble Storage Sizer](https://sizer.nimblestorage.com/) -- capacity and performance sizing tool for Nimble and Alletra arrays

## See Also

- `general/storage.md` -- general storage architecture patterns
- `general/disaster-recovery.md` -- DR strategy and RPO/RTO planning
- `providers/hpe/proliant.md` -- ProLiant servers that host Nimble/Alletra-connected workloads
- `providers/hpe/synergy.md` -- Synergy composable infrastructure with Nimble/Alletra SAN
- `providers/hpe/greenlake.md` -- GreenLake consumption model for storage
