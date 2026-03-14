# Nutanix Compute (AHV and VM Management)

## Checklist

- [ ] Is the vCPU to pCPU ratio appropriate for the workload? (1:1 to 4:1 for general workloads, 1:1 for latency-sensitive applications like databases, up to 8:1 for VDI with careful monitoring)
- [ ] Are VM CPU and memory reservations configured for critical workloads to prevent resource contention during cluster degradation (N+1 or N+2 scenarios)?
- [ ] Is AHV CPU scheduling set correctly, using CPU pinning for latency-sensitive VMs and NUMA alignment for memory-intensive applications (SQL Server, SAP HANA)?
- [ ] Are VM affinity rules configured to co-locate dependent VMs on the same host (e.g., app + local cache), and anti-affinity rules to separate redundant VMs (e.g., HA pairs, domain controllers)?
- [ ] Is GPU passthrough configured using AHV's vGPU support (NVIDIA GRID/vGPU profiles) for VDI, AI/ML, or rendering workloads, with appropriate GPU driver management?
- [ ] Is VM High Availability (HA) enabled at the cluster level with host reservation capacity guaranteeing that all VMs can restart on surviving hosts after node failure?
- [ ] Are live migrations tested and confirmed working for all production VMs, with VM compatibility checks ensuring no host-specific CPU feature dependencies?
- [ ] Is the AHV host networking configured with appropriate bond modes -- active-backup for management traffic, balance-slb or LACP (802.3ad) for VM traffic -- on OVS bridges?
- [ ] Are VM images managed through Prism Central image service (not uploaded per-cluster), with image placement policies controlling which clusters cache which images?
- [ ] Is CVM (Controller VM) resource allocation adequate -- minimum 12 vCPUs and 32 GB RAM for general workloads, increased to 16+ vCPUs and 48+ GB for heavy storage I/O or dedup/compression workloads?
- [ ] Are VM boot configurations using UEFI with Secure Boot for Windows Server 2016+ and modern Linux distributions, with vTPM enabled where required?
- [ ] Is the AHV scheduler host capacity reservation (HA reservation) configured to tolerate the loss of at least one host without VM resource starvation?
- [ ] Are VM hardware clocks set to the correct timezone and NTP sources, with Nutanix Guest Tools (NGT) installed for VSS-consistent snapshots and cross-hypervisor migration support?

## Why This Matters

AHV is a KVM-based hypervisor tightly integrated with the Nutanix Distributed Storage Fabric, meaning compute and storage performance are deeply coupled. CVM resource starvation directly degrades storage I/O for the entire host. Overcommitting vCPUs beyond safe ratios causes CPU ready times to spike, which manifests as application latency rather than obvious failures. NUMA misalignment for large VMs forces remote memory access with 2-3x latency penalty. Without affinity rules, HA restart can land redundant VMs on the same host, creating a single point of failure. Bond mode selection on OVS bridges directly impacts throughput and failover behavior -- balance-slb provides basic load balancing without switch configuration, while LACP requires switch support but provides true link aggregation. GPU passthrough requires careful host-level planning since vGPU profiles consume fixed GPU memory and cannot be overcommitted.

## Common Decisions (ADR Triggers)

- **CPU overcommit ratio** -- Conservative (2:1) vs aggressive (6:1+), depends on workload burstiness and acceptable CPU ready percentages
- **NUMA alignment strategy** -- Automatic NUMA balancing vs explicit NUMA pinning for large VMs, cross-socket vs single-socket placement
- **Bond mode for VM traffic** -- active-backup (simple, no switch config) vs balance-slb (OVS-native load balancing) vs LACP (requires switch support, highest throughput)
- **GPU virtualization** -- Full GPU passthrough (1 VM per GPU) vs vGPU profiles (multiple VMs per GPU), NVIDIA GRID licensing model
- **VM HA reservation** -- Reserve capacity for 1 host failure (N+1) vs 2 host failures (N+2), impacts usable cluster capacity by 25-40%
- **Image management** -- Per-cluster image upload vs Prism Central centralized image management with placement policies
- **Guest tools** -- NGT (Nutanix-native, VSS integration, self-service restore) vs VMware Tools compatibility layer, impact on snapshot consistency
