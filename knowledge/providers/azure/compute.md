# Azure Compute

## Checklist

- [ ] **[Critical]** Are Virtual Machine Scale Sets (VMSS) with Flexible orchestration used instead of standalone VMs for production workloads requiring auto-scaling?
- [ ] **[Critical]** Are availability zones used for zone-redundant deployments, with VMs spread across at least 2 zones (3 recommended)?
- [ ] **[Critical]** Is the VM SKU selected from the appropriate family? (D-series general purpose, E-series memory-optimized, F-series compute-optimized, L-series storage-optimized, DCas/ECas Confidential VMs for TEE workloads, Cobalt 100 Dps/Eps Arm-based for cost-efficient Linux)
- [ ] **[Recommended]** Are managed disks used for all VMs with the appropriate tier? (Premium SSD v2 for performance, Premium SSD for production, Standard SSD for dev/test)
- [ ] **[Recommended]** Is Azure Bastion deployed for secure administrative access, eliminating public IP addresses on VMs?
- [ ] **[Recommended]** Are VM images built via a pipeline using Azure Image Builder or Packer with Azure Compute Gallery (formerly Shared Image Gallery) for distribution?
- [ ] **[Recommended]** Is accelerated networking enabled on supported VM SKUs for lower latency and higher throughput?
- [ ] **[Optional]** Are Spot VMs evaluated for fault-tolerant workloads with eviction policies and max price configured?
- [ ] **[Recommended]** Is Azure Autoscale configured with appropriate metrics (CPU, memory, queue depth) and scale-in protection for in-flight work?
- [ ] **[Optional]** Are proximity placement groups used for latency-sensitive workloads that need VMs co-located in the same datacenter?
- [ ] **[Recommended]** Is boot diagnostics enabled and serial console access configured for VM troubleshooting?
- [ ] **[Critical]** Are OS and data disks encrypted with Azure Disk Encryption (ADE) or server-side encryption (SSE) with customer-managed keys?
- [ ] **[Recommended]** Is Azure Update Management or Update Manager configured for automated OS patching with maintenance windows?
- [ ] **[Recommended]** Is the Azure VM Agent installed and healthy, with VM extensions (monitoring, antimalware, custom script) managed via policy?

## Why This Matters

Azure compute has unique concepts like VMSS orchestration modes, availability sets (legacy), and Azure Compute Gallery (formerly Shared Image Gallery) that differ from AWS equivalents. Standalone VMs without scale sets cannot auto-scale or self-heal. Missing accelerated networking leaves significant performance on the table. Azure Bastion eliminates the need to manage jump boxes but must be planned into the network architecture. Confidential VMs (DCasv5/ECasv5 series) provide hardware-based trusted execution environments using AMD SEV-SNP or Intel TDX for workloads requiring VM memory encryption. Cobalt 100 Arm-based VMs (Dpsv6/Dpdsv6/Epsv6 series) provide a cost-effective, high-performance alternative for Linux workloads with up to 50% better price-performance than comparable x86 instances.

## Common Decisions (ADR Triggers)

- **VMSS Flexible vs Uniform** -- mixed VM sizes and zone spreading vs homogeneous instances with faster scaling
- **VM SKU family** -- Cobalt 100 Arm-based (Dpsv6/Epsv6, best price-performance for Linux) vs Intel vs AMD, generation selection; Confidential VMs (DCasv5/ECasv5) for TEE-protected workloads
- **Purchase model** -- pay-as-you-go vs Azure Reserved VM Instances (1 or 3 year) vs Azure Savings Plan
- **Spot VM strategy** -- eviction type (deallocate vs delete), max price, Spot priority mix in VMSS
- **Disk strategy** -- Premium SSD v2 (configurable IOPS) vs Premium SSD (fixed tiers), ephemeral OS disks for stateless
- **Image management** -- Azure Image Builder vs Packer, Azure Compute Gallery (formerly Shared Image Gallery) distribution, image lifecycle
- **Patching strategy** -- Azure Update Manager with maintenance configurations vs custom automation

## Reference Architectures

- [Azure Architecture Center: Virtual Machines architectures](https://learn.microsoft.com/en-us/azure/architecture/browse/?azure_categories=compute) -- reference architectures for VM-based workloads including N-tier, high availability, and scale sets
- [Azure Architecture Center: Run a Linux/Windows VM on Azure](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/n-tier/linux-vm) -- baseline reference architecture for single-VM and multi-tier VM deployments
- [Azure Well-Architected Framework: Virtual Machines](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/virtual-machines) -- reliability, security, and performance best practices for Azure VMs
- [Azure Landing Zone: Compute](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/) -- Cloud Adoption Framework guidance for compute platform selection and scaling
- [Azure Architecture Center: VMSS autoscaling design](https://learn.microsoft.com/en-us/azure/architecture/best-practices/auto-scaling) -- reference patterns for autoscaling Virtual Machine Scale Sets
