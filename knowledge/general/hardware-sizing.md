# Physical Server Hardware Selection

## Checklist

- [ ] **[Critical]** Server role defined (control plane, compute, storage, converged) with corresponding resource requirements documented
- [ ] **[Critical]** CPU selected with appropriate core count and clock speed for the workload (more cores for VM density, higher clock for latency-sensitive workloads)
- [ ] **[Critical]** RAM sized per role with ECC memory; DIMM slots populated evenly across all memory channels for maximum bandwidth
- [ ] **[Critical]** Disk layout planned: NVMe for high-IOPS roles (Ceph OSD journals, databases), SSD for OS/boot, HDD only for cold storage
- [ ] **[Critical]** Storage controller mode verified: HBA/JBOD passthrough for Ceph and software-defined storage; hardware RAID only for OS disks
- [ ] **[Critical]** NIC speed meets requirements: 25GbE recommended minimum for production; dual-port NICs for bonding and redundancy
- [ ] **[Recommended]** IPMI/BMC network planned: dedicated management NIC, out-of-band access verified (iDRAC, iLO, XCC), Redfish API tested for automation
- [ ] **[Recommended]** Dual redundant PSUs specified; total rack power budget calculated (sum of server TDP + switches + overhead, typically 5-10 kW per rack)
- [ ] **[Recommended]** Server vendor selected based on support tier requirements, spare parts availability, and hardware management tooling
- [ ] **[Recommended]** Firmware and BIOS settings documented: virtualization extensions enabled (VT-x/AMD-V, VT-d/AMD-Vi for IOMMU), boot mode (UEFI), power profile (performance vs balanced)
- [ ] **[Recommended]** Thermal and airflow requirements validated: 1U servers have tighter thermal limits; GPU servers require 2U with enhanced cooling
- [ ] **[Optional]** SR-IOV capable NICs selected if high-performance networking (NFV, low-latency) is required
- [ ] **[Optional]** GPU support planned if needed: verify PCIe slot count, power connectors, and cooling in 2U chassis
- [ ] **[Optional]** Hardware burn-in and acceptance testing procedure defined (memtest, fio, stress-ng) before production deployment
- [ ] **[Optional]** Spare parts strategy defined: cold spares on-site for disks, PSUs, and NICs; vendor next-business-day or 4-hour support contract

## Why This Matters

Hardware selection decisions are locked in for 4-7 years (typical server lifecycle). Choosing the wrong CPU, insufficient RAM, or slow disks creates bottlenecks that cannot be fixed without replacing hardware. Undersized infrastructure leads to poor VM performance, tenant complaints, and premature capacity additions. Oversized infrastructure wastes capital expenditure.

The interaction between components matters as much as individual specs. A server with 128 cores but only 256 GB RAM will be memory-constrained for most VM workloads. Fast NVMe disks behind a hardware RAID controller in RAID mode will prevent Ceph from managing them directly. A 100GbE NIC is pointless if the top-of-rack switch only supports 25GbE uplinks.

Physical infrastructure also determines operational patterns. Servers without functional IPMI require physical console access for troubleshooting, which is unacceptable in remote data centers. Servers without dual PSUs have a single point of failure at the power supply level.

## Common Decisions (ADR Triggers)

### ADR: Server Vendor Selection
**Trigger:** Procuring new server hardware for a deployment.
**Considerations:**
- **Dell PowerEdge** (R660 1U, R760 2U): Most popular in enterprise. iDRAC is mature and well-documented. OpenManage provides fleet management. Strong channel partner network for procurement. Broad OS certification.
- **HPE ProLiant** (DL360 1U, DL380 2U): Enterprise-grade with iLO for management. OneView for fleet management. Strong in regulated industries. Slightly higher price point.
- **Lenovo ThinkSystem** (SR630 1U, SR650 2U): Competitive pricing. XClarity Controller (XCC) for management. Good value for mid-size deployments.
- **Supermicro**: Lowest cost, whitebox-style. Basic IPMI (improving with newer models). Popular for hyperscale and cost-sensitive deployments. Less polished management tooling. Wide range of motherboard configurations.
- Support contract tiers matter: 4-hour on-site parts replacement vs next-business-day vs depot repair. Factor this into total cost of ownership.

### ADR: Intel Xeon vs AMD EPYC
**Trigger:** Selecting CPU platform for new servers.
**Considerations:**
- **Intel Xeon Scalable (4th gen Sapphire Rapids / 5th gen Emerald Rapids):** Up to 60 cores per socket. Strong single-thread performance. Better for workloads that need high clock speed (databases, single-threaded apps). Mature ecosystem, broad software certification. AMX for AI inference.
- **AMD EPYC (Genoa / Bergamo):** Up to 128 cores (Genoa) or 128 c-cores (Bergamo) per socket. Better core density and performance per dollar. NUMA topology differs (multiple CCDs per socket, which can affect latency-sensitive workloads). Excellent for VM density where core count matters most.
- For OpenStack compute nodes, AMD EPYC typically provides better value due to higher core count per dollar.
- For database servers or latency-sensitive workloads, Intel's higher per-core clock speed may be preferable.
- Socket count: 1S (single socket) reduces cost and is sufficient for many workloads. 2S (dual socket) doubles cores and memory channels but adds cost and complexity.

### ADR: DDR4 vs DDR5 Memory
**Trigger:** Specifying memory for new server purchases.
**Considerations:**
- DDR5 offers higher bandwidth (4800-5600 MT/s vs DDR4 3200 MT/s) and higher density per DIMM (up to 256 GB per DIMM).
- DDR5 costs more per GB but the premium is shrinking.
- New platforms (Intel 4th/5th gen, AMD Genoa) support DDR5 only. DDR4 is only relevant for older platforms.
- For new builds, DDR5 is the only option on current-generation CPUs.
- RDIMM (Registered) for most servers; LRDIMM (Load-Reduced) for maximum capacity configurations where all DIMM slots are populated.

### ADR: NVMe vs SSD vs HDD for Storage Tier
**Trigger:** Planning disk layout for different server roles.
**Considerations:**
- NVMe: 500K-1M+ IOPS, sub-100us latency. Required for Ceph BlueStore OSD WAL/DB devices, database servers, and any latency-sensitive storage. U.2 or M.2 form factor. More expensive per TB.
- SATA/SAS SSD: 50K-100K IOPS. Good for OS/boot disks, general-purpose storage, moderate-performance Ceph OSDs. Lower cost than NVMe.
- HDD: 100-200 IOPS. Only suitable for cold storage, backups, and archival. 3.5" form factor, high capacity (up to 22 TB per disk). Lowest cost per TB.
- Ceph OSD best practice: NVMe for WAL/DB (small, fast), SSD or HDD for data (large, capacity-focused). Pure NVMe Ceph clusters for high-performance but at higher cost.

### ADR: Network Speed Selection
**Trigger:** Specifying NIC and switch speeds for the deployment.
**Considerations:**
- **10GbE:** Minimum acceptable for production. Sufficient for small deployments with moderate storage traffic. Lower cost for switches and optics.
- **25GbE:** Recommended standard for new deployments. Good balance of performance and cost. Single-lane (SFP28), so cabling is the same as 10GbE (just different optics and switches).
- **100GbE:** Required for large Ceph clusters with high aggregate throughput, or when storage and compute traffic share the same physical network. QSFP28 form factor, higher switch cost.
- NIC selection: Intel E810 (25/100GbE, strong Linux support, good for SR-IOV), NVIDIA/Mellanox ConnectX-6 (25/100GbE, best performance, excellent RDMA support, higher cost).

## Reference Architectures

### Control Plane Node

Control plane nodes run API services, database (Galera), message queue (RabbitMQ), and scheduling services. They are CPU and memory moderate, with fast disk for database I/O.

| Component | Specification |
|---|---|
| Form factor | 1U (e.g., Dell R660, HPE DL360) |
| CPU | 1x Intel Xeon Gold 5415+ (8 cores, 2.9 GHz) or 1x AMD EPYC 9124 (16 cores) |
| RAM | 128-256 GB DDR5 ECC RDIMM (populate all channels evenly) |
| Boot/OS disk | 2x 480 GB SATA SSD in RAID-1 (hardware RAID or mdadm) |
| Database disk | 2x 1.92 TB NVMe U.2 (for MariaDB Galera data, high IOPS) |
| NIC | 2x 25GbE dual-port (4 ports total: 2 for management bond, 2 for tenant/storage bond) |
| BMC | Dedicated 1GbE management port (iDRAC/iLO/XCC) |
| PSU | Dual redundant 800W |
| Quantity | 3 (minimum for HA quorum) |

**Notes:** Control plane nodes are not particularly resource-hungry individually, but database and message queue performance is critical for overall cloud responsiveness. NVMe for the database ensures low-latency Galera replication and fast query response.

### Compute Node

Compute nodes run the hypervisor (KVM/libvirt) and host tenant VMs. They need maximum cores and RAM.

| Component | Specification |
|---|---|
| Form factor | 2U (e.g., Dell R760, HPE DL380) for more DIMM slots and disk bays |
| CPU | 2x AMD EPYC 9354 (32 cores each, 64 total) or 2x Intel Xeon Gold 6430 (32 cores each) |
| RAM | 512 GB - 1 TB DDR5 ECC RDIMM (16x 32 GB or 16x 64 GB, all channels populated) |
| Boot/OS disk | 2x 480 GB SATA SSD in RAID-1 |
| Ephemeral storage | 2x 3.84 TB NVMe (for instance local disk, if not using shared storage) |
| NIC | 2x 25GbE dual-port (management bond + tenant/storage bond) |
| BMC | Dedicated 1GbE management port |
| PSU | Dual redundant 1100W |
| Quantity | Scales with workload (start with 3-5, grow as needed) |

**Notes:** The VM-to-core overcommit ratio depends on workload. OpenStack defaults to 16:1 CPU overcommit, but 4:1 or 8:1 is more realistic for production. A 64-core compute node at 4:1 overcommit supports ~256 vCPUs. RAM is typically the binding constraint: 512 GB with 10% reserved for the hypervisor leaves ~460 GB for VMs.

### Storage Node (Ceph OSD)

Storage nodes run Ceph OSDs and need maximum disk capacity with fast journals.

| Component | Specification |
|---|---|
| Form factor | 2U with 12-24 front-loading hot-swap bays (e.g., Dell R760, Supermicro SSG) |
| CPU | 1x AMD EPYC 9124 (16 cores) — Ceph needs ~1 core per OSD |
| RAM | 128-256 GB DDR5 ECC (Ceph needs ~5 GB per OSD, plus OS overhead) |
| Boot/OS disk | 2x 480 GB SATA SSD in RAID-1 |
| OSD data disks | 10-12x 3.84 TB NVMe SSD (high performance) or 10-12x 8 TB SAS HDD (high capacity) |
| WAL/DB disks | 2x 1.6 TB NVMe (shared across HDDs as BlueStore WAL/DB; not needed if OSDs are already NVMe) |
| Storage controller | HBA mode (JBOD passthrough) — NOT hardware RAID. Ceph manages replication. |
| NIC | 2x 25GbE dual-port (minimum); 100GbE for large clusters with high throughput |
| BMC | Dedicated 1GbE management port |
| PSU | Dual redundant 1100W |
| Quantity | 3 (minimum for Ceph replication factor 3) |

**Notes:** Storage controller mode is critical. Ceph requires direct access to individual disks (HBA/JBOD mode). Hardware RAID prevents Ceph from managing replication and recovery. Most Dell PERC and HPE SmartArray controllers support HBA mode, but it must be explicitly configured. Verify before purchasing that the controller supports JBOD passthrough.

### All-in-One Lab/Development Node

A single server for testing, development, or proof-of-concept deployments.

| Component | Specification |
|---|---|
| Form factor | 2U (or tower workstation) |
| CPU | 1x AMD EPYC 9124 (16 cores) or Intel Xeon w5-2455X (12 cores) |
| RAM | 256 GB DDR5 ECC |
| Boot/OS disk | 2x 480 GB SATA SSD in RAID-1 |
| Data disks | 4x 1.92 TB NVMe (for Ceph single-node or LVM) |
| NIC | 1x 25GbE dual-port (can use VLANs instead of separate physical networks) |
| BMC | Dedicated 1GbE management port |
| PSU | Single PSU acceptable for lab |

**Notes:** An all-in-one node cannot provide HA but is useful for functional testing, development, and training. Expect 256 GB RAM to support approximately 20-30 small VMs concurrently.

### Power and Rack Planning

**Per-server power estimates:**
- 1U control/compute (moderate load): 300-500W
- 2U compute (high utilization, dual CPU): 500-800W
- 2U storage (12 spinning disks): 400-600W
- 2U GPU server (2x A100): 1500-2000W

**Rack planning:**
- Standard 42U rack with 5-10 kW power budget
- 10 kW rack: approximately 12-15 servers (2U) + 2 ToR switches + 1 PDU pair
- Leave 3-6U for network switches (top-of-rack), cable management, and airflow
- Plan for 30% growth capacity in initial rack layout

**Cooling:**
- 1 kW of power = approximately 3,412 BTU/hr of heat
- Ensure hot aisle/cold aisle containment for efficient cooling
- GPU-heavy racks may require liquid cooling or rear-door heat exchangers
