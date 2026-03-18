# Dual-Platform Hypervisor Operations

## Scope

This file covers **operating two or more hypervisor platforms side-by-side** at the same facility or within the same managed environment. Common scenarios: Nutanix AHV alongside Azure Stack HCI (Tier 0 security enclaves), VMware ESXi alongside KVM during migration, or any environment where platform consolidation is incomplete or intentionally avoided. Distinct from hypervisor migration (`patterns/hypervisor-migration.md`) which aims to eliminate one platform. For security enclave design, see `general/tier0-security-enclaves.md`. For managed services scoping, see `general/managed-services-scoping.md`.

## Checklist

### Operational Model

- [ ] **[Critical]** Is the justification for dual-platform documented? (Security enclave isolation, legacy application dependency, licensing constraint, migration in-progress, vendor requirement) Dual-platform has ongoing costs -- the justification must outweigh them.
- [ ] **[Critical]** Are the two platforms operationally isolated or integrated? (Separate management planes, separate patching schedules, separate monitoring vs unified dashboards) The answer determines staffing and tooling.
- [ ] **[Critical]** Is the staffing model defined for both platforms? (Same team with cross-training, separate specialist teams, or primary platform team + SME for secondary) Dual-platform requires skills in both -- verify the team has or can acquire them.
- [ ] **[Recommended]** Is a platform consolidation roadmap defined, even if consolidation is deferred? (Phase 3 initiative, annual review, or intentionally permanent) Without a roadmap, dual-platform becomes permanent by default.
- [ ] **[Recommended]** Are patching and lifecycle management schedules coordinated? (Nutanix LCM for AHV/AOS, Windows Update / Azure Stack HCI updates for HCI -- maintenance windows may conflict or need sequencing)
- [ ] **[Recommended]** Is change management unified or separate? (One CAB for both platforms, or separate change processes per platform) Separate processes increase overhead; unified requires cross-platform impact assessment.
- [ ] **[Optional]** Is the dual-platform cost documented as a line item? (Incremental licensing, incremental staffing/training, incremental tooling, incremental management overhead) This quantifies what consolidation would save.

### Management Planes

- [ ] **[Critical]** Is each platform's management tooling identified and deployed? (Nutanix: Prism Central/Element. Azure Stack HCI: Windows Admin Center, Azure Arc. VMware: vCenter. KVM: libvirt, Cockpit, or Proxmox)
- [ ] **[Critical]** Is RBAC configured independently on each management plane with consistent role definitions? (Admin roles, operator roles, read-only roles -- mapped to the same AD groups where possible)
- [ ] **[Recommended]** Is monitoring consolidated into a single pane of glass? (Prism Central alerts + HCI alerts -> unified ITSM/alerting platform like ServiceNow, PagerDuty, or Prometheus/Grafana) Separate monitoring increases mean-time-to-detect.
- [ ] **[Recommended]** Is capacity planning performed per-platform? (Each platform has its own capacity runway -- do not aggregate across platforms as workloads cannot freely move between them)

### Network Isolation

- [ ] **[Critical]** Is network segmentation between platforms documented? (Air-gapped, VLAN-isolated, firewall-separated, or routable) Security enclaves typically require air-gap or strict firewall rules.
- [ ] **[Critical]** If the secondary platform hosts security-critical workloads (Tier 0, AD, PKI), is the network isolation validated by the security team -- not just the infrastructure team?
- [ ] **[Recommended]** Are shared services (DNS, NTP, SIEM, backup) accessible from both platforms without violating isolation requirements? (AD DNS may need to be reachable from both platforms even if they are otherwise isolated)

### Licensing

- [ ] **[Critical]** Are licensing implications of dual-platform documented? (Nutanix AHV is included with AOS licensing. Azure Stack HCI requires Windows Server Datacenter + Azure subscription. VMware requires VCF/VVF subscription. Running two platforms means paying for two licensing stacks.)
- [ ] **[Recommended]** Is the Windows Server licensing model correct for the HCI platform? (Azure Stack HCI uses Azure subscription billing per physical core. Standalone Hyper-V uses traditional Windows Server Datacenter licensing. These are different cost models.)
- [ ] **[Optional]** Are Microsoft Azure Hybrid Benefit credits applicable? (Existing Windows Server Datacenter licenses with Software Assurance can offset Azure Stack HCI subscription costs)

### Staffing and Training

- [ ] **[Recommended]** Is cross-training planned for the operations team? (Primary platform deep skills + secondary platform operational competency at minimum)
- [ ] **[Recommended]** Are runbooks prepared for both platforms covering common tasks? (VM provisioning, storage expansion, host patching, backup restore, DR failover -- per platform)
- [ ] **[Optional]** Is vendor support contracted for both platforms? (Nutanix support for AHV/AOS, Microsoft Premier/Unified support for Azure Stack HCI)

## Why This Matters

Dual-platform environments are common in practice but rarely planned -- they usually result from incomplete migrations, security requirements, or legacy constraints. The operational cost is real: two sets of skills, two patching cycles, two management planes, two licensing stacks, two sets of runbooks. Organizations underestimate this cost because each platform's team sees only their own overhead.

The most common failure: **assuming dual-platform is temporary when it becomes permanent.** Without a documented consolidation roadmap and executive sponsorship, the secondary platform persists indefinitely. Each year it remains, the switching cost increases as the team builds muscle memory and automation around both platforms.

The second most common failure: **staffing for one platform and expecting the team to absorb the second.** A Nutanix team can learn HCI basics, but Tier 0 security enclaves require deep Active Directory, PKI, and Windows Server expertise that most infrastructure teams do not have.

## Common Decisions (ADR Triggers)

- **Dual-platform justification** -- why two platforms instead of one; must be reviewed periodically
- **Consolidation timeline** -- when (if ever) to eliminate the secondary platform; deferred is a valid answer but must be explicit
- **Staffing model** -- cross-trained single team vs separate specialist teams; affects hiring, training budget, and on-call rotation
- **Network isolation model** -- air-gap vs firewall-separated vs routable; security team must approve for security-critical workloads
- **Monitoring strategy** -- unified alerting vs per-platform; affects MTTD and incident response

## See Also

- `general/tier0-security-enclaves.md` -- Security enclave design and migration considerations
- `patterns/azure-stack-hci-migration.md` -- Azure Stack HCI migration and disposition
- `general/managed-services-scoping.md` -- Managed services operational scoping
- `patterns/hypervisor-migration.md` -- Hypervisor migration (platform consolidation)
