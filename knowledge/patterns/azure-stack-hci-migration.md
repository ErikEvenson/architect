# Azure Stack HCI Migration to Alternative Platforms

## Scope

This file covers **migrating workloads off Azure Stack HCI** (formerly Azure Stack HCI, now branded Azure Local) to non-Microsoft platforms, primarily Nutanix AHV but applicable to VMware, KVM, or cloud. Addresses the decision framework for HCI workload disposition, tooling limitations, licensing implications, and Azure service dependencies that complicate departure. For Azure Stack HCI architecture and operations, see `providers/azure/azure-local.md`. For Nutanix migration tooling, see `providers/nutanix/migration-tools.md`. For general hypervisor migration, see `patterns/hypervisor-migration.md`.

## Checklist

### Assessment

- [ ] **[Critical]** Are all Azure Stack HCI clusters inventoried with node count, VM count, storage capacity, and Azure Arc registration status?
- [ ] **[Critical]** Are Azure services consumed through the HCI clusters identified? (Azure Kubernetes Service on HCI, Azure Virtual Desktop on HCI, Azure Arc-enabled services, Azure Backup, Azure Monitor, Azure Defender) These create dependencies that must be replaced on the target platform.
- [ ] **[Critical]** Is the Hyper-V generation (Gen 1 vs Gen 2) documented for each VM? Gen 2 VMs use UEFI and may require boot configuration changes on non-Hyper-V platforms.
- [ ] **[Critical]** Are Storage Spaces Direct (S2D) volumes and tiering configurations documented? VMs may depend on specific storage tiers (NVMe, SSD, HDD) that must be replicated on the target.
- [ ] **[Critical]** Is the Azure hybrid benefit licensing status documented? Windows Server and SQL Server licenses activated through Azure hybrid benefit may need re-licensing on the target platform.
- [ ] **[Recommended]** Are stretched clusters (multi-site S2D) identified? These have additional complexity for migration due to synchronous replication between sites.
- [ ] **[Recommended]** Are Azure Policy and Azure RBAC configurations documented? These governance controls will not transfer to non-Azure platforms and must be replaced.
- [ ] **[Recommended]** Is the Azure Stack HCI billing model documented? (per-core subscription cost) Decommissioning reduces Azure spend but may affect enterprise agreement commitments.
- [ ] **[Optional]** Are Windows Admin Center extensions and custom management workflows documented? These will need replacement on the target platform.

### Migration Tooling

- [ ] **[Critical]** Has Nutanix Move Hyper-V support been validated for the specific HCI version? Move supports Hyper-V sources via WinRM but has limitations -- test on non-production VMs first.
- [ ] **[Critical]** Is WinRM (TCP 5985/5986) enabled on all HCI nodes with CredSSP or Kerberos authentication configured for the migration tool service account?
- [ ] **[Critical]** Are alternative migration paths identified for VMs that Move cannot handle? Options: Veeam Backup & Replication (backup on HCI, restore to AHV), disk export (Export-VM / VHD copy + qemu-img convert), or re-deployment from golden images.
- [ ] **[Critical]** Is network connectivity between HCI nodes and target platform confirmed with sufficient bandwidth for data transfer? Calculate total data volume and available migration window.
- [ ] **[Recommended]** Has Veeam Backup for Azure Stack HCI been evaluated as a migration path? Backup the VM on HCI, restore to AHV -- this is often more reliable than live migration for cross-platform moves.
- [ ] **[Recommended]** Are VMs with Hyper-V Integration Services identified? These guest agents must be removed and replaced with target platform agents (e.g., Nutanix VirtIO, NGT) post-migration.
- [ ] **[Optional]** Is Azure Migrate being considered for assessment? While designed for Azure cloud targets, the assessment component can inventory HCI workloads and identify dependencies.

### Decision Framework

- [ ] **[Critical]** Has a disposition decision been made for each HCI cluster? Options: (A) Migrate VMs to Nutanix AHV and decommission HCI, (B) Keep HCI alongside Nutanix for specific workloads, (C) Migrate VMs to Azure cloud (IaaS), (D) Keep as-is if workloads are Azure-dependent.
- [ ] **[Critical]** Are Azure-dependent workloads identified that cannot easily move off HCI? (AKS-HCI clusters, Azure Virtual Desktop session hosts, VMs using Azure Arc-enabled SQL or Azure Arc-enabled Kubernetes)
- [ ] **[Recommended]** Is the cost comparison documented? Compare: current HCI subscription cost + hardware amortization vs. target platform licensing + migration effort.
- [ ] **[Recommended]** Is the operational impact assessed? Teams managing HCI use Windows Admin Center and Azure Portal -- migrating to Nutanix means retraining to Prism Central.

### Post-Migration

- [ ] **[Critical]** Are Hyper-V Integration Services removed from all migrated VMs and replaced with target platform guest agents?
- [ ] **[Critical]** Is Azure Arc registration cleaned up for decommissioned HCI nodes? Orphaned Arc registrations continue to incur billing.
- [ ] **[Critical]** Are Azure Backup policies updated or migrated to the target platform's backup solution?
- [ ] **[Recommended]** Are Windows Server licenses re-assessed? VMs that used Azure hybrid benefit on HCI may need separate license procurement on non-Azure platforms.
- [ ] **[Optional]** Is the Azure Stack HCI subscription cancelled in the Azure portal after all workloads are migrated and validated?

## Why This Matters

Azure Stack HCI migration to non-Microsoft platforms is increasingly common due to the Broadcom-VMware disruption driving organizations to Nutanix, creating mixed environments where HCI coexists with Nutanix. The decision to consolidate onto a single platform (eliminating HCI operational overhead) or maintain both depends on Azure service dependencies, licensing economics, and operational team skills.

The most common failure is assuming Nutanix Move handles Hyper-V sources as smoothly as ESXi sources. In practice, Hyper-V-to-AHV migration via Move has more prerequisites (WinRM configuration, CredSSP authentication, firewall rules) and fewer features (no automatic driver injection on some guest OS versions). Veeam backup/restore is often the more reliable path for cross-platform migration from HCI.

The second most common failure is not accounting for Azure service dependencies. A VM running on HCI may consume Azure Defender for endpoint protection, Azure Monitor for observability, Azure Backup for data protection, and Azure Arc for governance. Migrating the VM to Nutanix means replacing all of these with non-Azure equivalents -- the VM migration itself is the easy part.

The licensing trap is the third common failure. Azure Stack HCI includes Azure hybrid benefit for Windows Server -- VMs running Windows Server on HCI may be licensed through the Azure subscription. Moving those VMs to Nutanix means procuring separate Windows Server licenses or using existing Datacenter licenses, which can be a significant cost surprise if not planned for.

## Common Decisions (ADR Triggers)

- **HCI disposition strategy** -- migrate all HCI workloads to Nutanix (single platform) vs. maintain HCI for Azure-native workloads (dual platform); cost, complexity, and operational overhead tradeoffs
- **Migration tooling selection** -- Nutanix Move (live migration, more prerequisites) vs. Veeam backup/restore (offline, more reliable) vs. manual VHD export/convert (most control, most labor); typically different tools for different VM types
- **Azure service replacement** -- which Azure services consumed through HCI need non-Azure replacements on the target platform; mapping Azure Monitor to Prometheus/Grafana, Azure Backup to Veeam, Azure Defender to CrowdStrike/etc.
- **Windows licensing strategy** -- procure new licenses, transfer existing Datacenter licenses, or use BYOL; engage Microsoft licensing specialist before migration
- **Operational training investment** -- retrain HCI operations team on Nutanix Prism vs. hire Nutanix-skilled staff vs. outsource to managed services provider; timeline and cost implications

## See Also

- `providers/azure/azure-local.md` -- Azure Stack HCI (Azure Local) architecture and operations
- `providers/nutanix/migration-tools.md` -- Nutanix Move, Veeam, Zerto for workload migration
- `patterns/hypervisor-migration.md` -- General hypervisor-to-hypervisor migration patterns
- `providers/vmware/licensing.md` -- VMware/Broadcom licensing changes driving platform consolidation
