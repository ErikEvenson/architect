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
