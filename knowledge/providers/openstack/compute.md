# OpenStack Compute (Nova)

## Checklist

- [ ] Is the compute driver selected appropriately? (libvirt/KVM for production virtualization, libvirt/QEMU for nested/dev environments, Ironic for bare metal provisioning, VMware vCenter for ESXi integration)
- [ ] Are Nova flavors defined with deliberate sizing tiers (m1.small, c1.xlarge, etc.) including CPU, RAM, disk, and ephemeral storage, with flavor access restricted per project where needed?
- [ ] Is CPU pinning (`hw:cpu_policy=dedicated`) configured for latency-sensitive workloads, and are shared (floating) CPUs allocated for general-purpose instances to avoid CPU overcommit conflicts?
- [ ] Is NUMA topology awareness enabled (`hw:numa_nodes`, `hw:numa_cpus`, `hw:numa_mem`) for workloads requiring memory locality, and are compute hosts validated for consistent NUMA geometry?
- [ ] Are huge pages configured (`hw:mem_page_size=large` or `1GB`) for high-throughput workloads (DPDK, databases), and is the host reserved memory (`reserved_host_memory_mb`) adjusted accordingly?
- [ ] Are PCI passthrough devices (GPUs, SR-IOV NICs, FPGAs) configured in `nova.conf` with `[pci] alias` and `passthrough_whitelist`, and are corresponding flavor extra specs (`pci_passthrough:alias`) defined?
- [ ] Are availability zones defined to represent physical failure domains (power, network, cooling) and are hosts assigned to zones via host aggregates with `availability_zone` metadata?
- [ ] Are host aggregates configured with metadata keys (e.g., `ssd=true`, `gpu=nvidia-a100`) and matching flavor extra specs (`aggregate_instance_extra_specs`) to direct workloads to appropriate hardware?
- [ ] Are server groups used to enforce placement policy? (`affinity` for co-location of tightly coupled services, `anti-affinity` for HA distribution, `soft-anti-affinity` for best-effort separation)
- [ ] Is live migration enabled and tested? (shared storage or block migration, `live_migration_uri`, `live_migration_tunnelled`, timeout and completion settings in `nova.conf`)
- [ ] Is the Nova cells v2 architecture properly configured? (single cell for small deployments, multiple cells for scale beyond ~500 compute nodes, separate cell databases and message queues)
- [ ] Are compute overcommit ratios set intentionally? (`cpu_allocation_ratio` default 16:1, `ram_allocation_ratio` default 1.5:1, `disk_allocation_ratio` default 1.0 -- production often uses lower CPU ratios like 4:1 or 2:1)
- [ ] Is the Nova scheduler configured with appropriate filters and weights? (`AggregateInstanceExtraSpecsFilter`, `NUMATopologyFilter`, `PciPassthroughFilter`, `ServerGroupAntiAffinityFilter`)
- [ ] Are Nova quota limits set per project for instances, cores, RAM, key pairs, server groups, and server group members to prevent resource exhaustion?

## Why This Matters

Nova is the core of OpenStack compute and every decision -- from driver selection to CPU pinning policy -- directly affects workload performance, density, and reliability. Incorrect NUMA configuration can cause performance degradation of 30-50% for memory-intensive workloads. Overcommit ratios set too aggressively lead to noisy-neighbor problems and OOM kills. Missing PCI passthrough configuration blocks GPU and SR-IOV workloads entirely. Without properly defined availability zones, anti-affinity rules cannot guarantee fault tolerance across physical failure domains. Cells architecture decisions are difficult to change later and affect the operational ceiling of the deployment. Flavor design without host aggregates leads to unpredictable instance placement and inconsistent tenant experience.

## Common Decisions (ADR Triggers)

- **Compute driver** -- libvirt/KVM (standard production) vs Ironic (bare metal for HPC/ML) vs VMware (brownfield ESXi integration) -- affects feature availability and operational model
- **Overcommit strategy** -- aggressive ratios (16:1 CPU, 1.5:1 RAM for dev/test) vs conservative (2:1 CPU, 1:1 RAM for production) vs no overcommit (1:1 for latency-sensitive) -- directly trades density for performance predictability
- **NUMA and CPU pinning** -- dedicated CPUs for NFV/telco workloads vs shared CPUs for general compute -- determines host utilization ceiling and scheduling complexity
- **PCI passthrough vs virtio** -- GPU passthrough (1 GPU per instance) vs vGPU (GPU sharing via NVIDIA GRID/MIG) vs SR-IOV (NIC hardware offload) vs virtio-net (software networking) -- affects hardware utilization and workload capability
- **Cells architecture** -- single cell (simpler operations, ~500 node limit) vs multi-cell (scales further but adds DB/MQ complexity per cell) -- difficult to change post-deployment
- **Placement and scheduling** -- custom host aggregates with metadata-driven scheduling vs simple AZ-based placement -- complexity vs precision trade-off
- **Live migration model** -- shared storage live migration (faster, requires shared filesystem) vs block migration (no shared storage, slower, higher network load) vs disabling migration entirely (simplest but no host maintenance without downtime)
- **Flavor governance** -- small curated flavor list (simpler capacity planning) vs large permutational matrix (tenant flexibility) vs per-project private flavors (controlled but operationally heavier)

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cells v2 | Optional (upgrade path) | Mandatory (single cell minimum) | GA (multi-cell) | GA | GA | GA | GA | GA | GA | GA | GA | GA (improved cross-cell) | GA | GA (improved cell listing) | GA |
| Placement service | In-tree (nova-placement) | In-tree | Extracted to standalone service | Standalone required | GA standalone | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Libvirt driver | libvirt 3.x | libvirt 4.x | libvirt 4.x | libvirt 5.x | libvirt 5.x | libvirt 6.x | libvirt 6.x | libvirt 7.x | libvirt 7.x | libvirt 8.x | libvirt 8.x | libvirt 9.x | libvirt 9.x | libvirt 10.x | libvirt 10.x |
| QEMU version support | QEMU 2.x | QEMU 2.x | QEMU 3.x | QEMU 3.x | QEMU 4.x | QEMU 4.x | QEMU 5.x | QEMU 5.x | QEMU 6.x | QEMU 6.x | QEMU 7.x | QEMU 8.x | QEMU 8.x | QEMU 8.x+ | QEMU 9.x |
| Ironic (bare metal) | GA (driver composition) | GA (BIOS config) | GA (deploy steps) | GA (fast-track deploy) | GA (deploy templates) | GA (UEFI boot) | GA (TLS boot) | GA (JSON-RPC) | GA (firmware interface) | GA (BIOS/UEFI) | GA (improved cleaning) | GA (sharding, firmware updates) | GA (improved inspection) | GA (improved multi-tenant) | GA (runbooks) |
| vGPU support | Not available | Not available | Not available | Introduced (NVIDIA GRID) | GA (basic placement) | GA (multiple vGPU types) | GA (improved reporting) | GA (improved allocation) | GA (MIG support) | GA | GA (improved MIG) | GA (live migration with vGPU) | GA | GA (improved placement) | GA |
| Cyborg (accelerators) | Not available | Not available | Not available | Not available | Introduced (spec only) | Tech Preview | Tech Preview | GA (GPU, FPGA) | GA | GA | GA | GA (improved lifecycle) | GA | GA (SmartNIC support) | GA |
| Secure Boot | Not available | Not available | Not available | Not available | Not available | Tech Preview | GA | GA | GA | GA | GA | GA (improved enrollment) | GA | GA | GA |
| vTPM (virtual TPM) | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Tech Preview | Tech Preview | GA | GA | GA | GA | GA |
| CPU overcommit (allocation ratio) | nova.conf global | nova.conf global | nova.conf global | Placement-aware (initial) | Placement-aware | Placement-aware | Placement-aware | Placement-aware | Placement-aware | Configurable | Configurable | Placement-based per aggregate | Placement-based | Placement-based | Placement-based |
| Live migration (post-copy) | Tech Preview | GA | GA | GA | GA (QEMU native TLS) | GA | GA | GA | GA | GA | GA | GA (improved timeout) | GA | GA | GA |
| Server groups (soft policies) | GA (soft-affinity added) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA (improved scheduling) | GA |
| Nova metadata service | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA (HTTPS support) | GA | GA (HTTPS default option) | GA |
| Evacuate improvements | GA | GA | GA | GA | GA | GA (improved reporting) | GA | GA | GA | GA | GA | GA (improved rebuild) | GA | GA (force options) | GA |
| Emulated NUMA topology | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA (improved validation) | GA |
| nova-manage improvements | Basic | DB migration tools | DB archiving | Placement sync | Placement audit | Improved cell mgmt | Cell mapping tools | Placement heal | Archive improvements | GA | GA | GA | GA | GA | GA |

**Key changes across releases:**
- **Cells v2 mandatory (Queens):** Cells v2 became mandatory in Queens. All deployments require at least a single cell (cell0 + cell1). Pike provided the upgrade path from cells v1. Multi-cell deployments (for scaling beyond ~500 compute nodes) use separate databases and message queues per cell. Cross-cell operations (resize, migrate) improved significantly in 2023.1+.
- **Placement service extraction (Stein):** The Placement service was extracted from Nova into a standalone project in Stein (Rocky began the separation). All deployments from Stein onward must run placement as an independent service with its own endpoint. This enables other services (Neutron, Cyborg) to report resource inventories.
- **Libvirt and QEMU updates:** Each OpenStack release tracks newer libvirt and QEMU versions, bringing improved device emulation, security fixes, and performance. QEMU 8.x adds improved virtio device performance and new machine types. Ensure compute node OS packages are updated to match supported libvirt/QEMU versions.
- **Ironic evolution:** Ironic introduced driver composition reform in Pike, allowing modular hardware interfaces. Fast-track deployment in Stein dramatically reduced provisioning time. Sharding in 2023.1 enabled scaling Ironic conductors across large deployments. 2024.1 improved multi-tenant bare metal isolation. Ironic is increasingly used for AI/ML workloads requiring direct GPU access.
- **vGPU support (Stein+):** vGPU support was introduced in Stein with NVIDIA GRID. MIG (Multi-Instance GPU) support arrived in Xena. Starting with 2023.1, Nova supports live migration of instances with vGPU devices, enabling maintenance operations on GPU hosts without instance downtime. Requires compatible NVIDIA driver versions.
- **Cyborg for accelerators (Train+):** Cyborg was introduced in Train for managing accelerator devices (GPUs, FPGAs, SmartNICs). It reached GA in Wallaby and integrates with Nova scheduling via Placement to allocate accelerator resources to instances.
- **vTPM support:** Virtual TPM reached GA in Zed, enabling instances to use TPM 2.0 for measured boot, disk encryption (BitLocker, LUKS), and attestation. Requires libvirt 9.x+ and swtpm on compute hosts.
- **Placement-based allocation ratios:** Starting from Stein, overcommit ratio configuration moved from nova.conf to the Placement service, enabling per-host-aggregate overcommit ratios rather than a global setting. This allows different overcommit policies for different hardware tiers.
