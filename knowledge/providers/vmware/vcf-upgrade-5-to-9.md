# VMware Cloud Foundation: Upgrading from VCF 5.x to VCF 9.0

## Scope

Upgrade planning and execution for VMware Cloud Foundation from version 5.x to version 9.0. Covers supported upgrade paths, required intermediate versions, component upgrade sequencing (SDDC Manager, NSX, vCenter, ESXi, vSAN), irreversible transitions (vLCM baselines to images, vSAN on-disk format, ELM removal), Aria-to-VCF Operations renaming, NSX Manager-to-Policy promotion, licensing model changes (perpetual to subscription), hardware compatibility gates, pre-upgrade checks, known issues, estimated timelines, and rollback constraints.

## Checklist

- [ ] **[Critical]** Is the current VCF version confirmed and is the supported upgrade path documented? VCF 5.1/5.2 can upgrade directly to 9.0 (14 steps, 3-6 weeks). VCF 5.0 must first upgrade to 5.2 before upgrading to 9.0 (15 steps, 4-8 weeks). VCF 4.x must upgrade to 5.2 first. There is NO direct path from VCF 5.0 to 9.0.
- [ ] **[Critical]** Is the VCF 9.0 Bill of Materials reviewed against the current hardware? ESX 9.0 requires minimum 1 GB boot-bank size (up from 500 MB) and minimum 32 GB system disk. New CPU support includes Intel Sapphire Rapids (HWP enabled), AMD EPYC 5th gen (Turin), and Intel Granite Rapids. The vSAN HCL database must be updated before upgrade.
- [ ] **[Critical]** Is the mandatory component upgrade sequence documented and understood? The required order is: Aria Suite Lifecycle (patch to 8.18p2) -> VCF Operations + Fleet Management -> VCF Automation -> VCF Operations for Networks -> VCF Operations for Logs (fresh install, no upgrade path) -> SDDC Manager -> NSX -> vCenter (via RDU) -> VCF Identity Broker -> Supervisor/vSAN Witness -> ESXi -> Post-upgrade (NSX finalize, VMware Tools, virtual hardware, vSAN on-disk format).
- [ ] **[Critical]** Are Aria components at the required minimum versions before starting? Aria Operations must be at 8.14+ (8.18 recommended). Aria Suite Lifecycle must be at 8.18 Patch 2. Aria Operations for Networks must be at 6.13+. Aria Operations for Logs has NO upgrade path to 9.0 -- requires fresh install with 90-day data migration window.
- [ ] **[Critical]** Is the NSX Manager-to-Policy object promotion completed before the upgrade? VCF 9.0 removes Manager APIs (logical networking and security). The Policy promotion tool must be used to migrate Manager objects to Policy equivalents. Mixed-mode configurations (Policy + Manager objects) require intermediate upgrade to NSX 4.2.1+ first, then promotion, before VCF 9.0.
- [ ] **[Critical]** Is multi-NSX topology disabled before upgrading? Multi-NSX topology is deprecated in VCF 9.0. Must turn off the multi-NSX feature for all registered compute managers or map NSX Manager instances to individual vCenter instances. Failure to do this causes silent upgrade cancellation.
- [ ] **[Critical]** Are NSX version incompatibilities checked? NSX 4.2.1.4 and NSX 4.2.2.x are NOT compatible with upgrade to 9.0.0.0 -- the upgrade is blocked to prevent back-in-time issues.
- [ ] **[Critical]** Is the licensing model converted from perpetual to subscription BEFORE upgrading? VCF 9.0 is subscription-only with per-core pricing and a single unified license file. Perpetual licenses must be converted before the upgrade. Customers should remain on VCF 5.2 until Broadcom subscription pricing is in place.
- [ ] **[Critical]** Are all irreversible transitions identified and stakeholders informed? The following cannot be rolled back: (1) vLCM baseline-to-image transition, (2) vSAN on-disk format upgrade, (3) Enhanced Linked Mode (ELM) removal, (4) NSX Manager-to-Policy promotion. Each requires explicit go/no-go approval.
- [ ] **[Critical]** Is a backup taken before each upgrade phase (SDDC Manager, NSX, vCenter, ESXi) with validated restore procedures? There is no single "easy button" rollback for a complete VCF environment -- each component must be backed up and restored independently.
- [ ] **[Recommended]** Is a temporary IP address provisioned for each vCenter server for the Reduced Downtime Upgrade (RDU)? VCF 9.0 uses RDU exclusively for vCenter upgrades, deploying a new appliance alongside the existing one. VCF 9.0.1+ auto-assigns link-local IPs (169.254.x.x), eliminating this requirement.
- [ ] **[Recommended]** Is the vCenter Reduced Downtime Upgrade (RDU) process understood? RDU deploys a temporary vCenter appliance, migrates configuration and inventory while the environment runs, then decommissions the old appliance. Downtime is reduced to minutes for the final cutover.
- [ ] **[Recommended]** Are VCF Operations, VCF Operations Fleet Management, and VCF Automation planned for deployment? These are MANDATORY in VCF 9.0 (they were optional in 5.x). They deploy automatically during upgrade even if not previously installed.
- [ ] **[Recommended]** Is the SDDC Manager UI deprecation accounted for in operational runbooks? The SDDC Manager UI is being deprecated; lifecycle management functions are moving to VCF Operations console under fleet management.
- [ ] **[Recommended]** Is the VMware Identity Manager (vIDM) to VCF Identity Broker (VIDB) transition planned? There is NO migration path from vIDM to VIDB -- it requires a greenfield deployment. vIDM continues to be managed by Aria Suite Lifecycle 8.x during the transition period.
- [ ] **[Recommended]** Are NSX Edge admin passwords verified as not expired, and is DNS configured on NSX edges? Expired passwords and missing DNS configuration cause precheck failures and prevent NSX edges from downloading upgrade bundles.
- [ ] **[Recommended]** Is the Aria Operations for Logs fresh installation planned with a 90-day data migration window? There is no upgrade path from Aria Operations for Logs 8.x to VCF Operations for Logs 9.0. Plan for parallel operation during the migration window.
- [ ] **[Recommended]** Are WCP (Workload Control Plane) clusters upgraded before NSX? NSX 9.0 requires minimum WCP 9.0.0.0. Incompatible WCP clusters block the upgrade.
- [ ] **[Optional]** Is the vSAN on-disk format upgrade deferred until after validation? The on-disk format upgrade is irreversible -- once upgraded, older hosts cannot be added to the cluster and software cannot be rolled back. Defer this to the final post-upgrade step after all validation is complete.
- [ ] **[Optional]** Is the deprecated guest OS list reviewed? ESX 9.0 drops support for Windows Server 2000/2003/2008, Windows XP/Vista, Oracle Linux 5.x, RHEL 4-5, CentOS 6-8, and other legacy operating systems. Inventory VMs running deprecated guest OSes before upgrading.

## Why This Matters

VCF 5.x to 9.0 is described by Broadcom as "a major architectural shift, not just an update." The version jump from 5.x to 9.0 (skipping 6/7/8) reflects the scope of change: unified version numbering, mandatory Aria-to-VCF Operations conversion, subscription-only licensing, NSX Manager API removal, SDDC Manager UI deprecation, and new hardware requirements. The upgrade involves multiple irreversible transitions that cannot be rolled back once committed -- vLCM baselines to images, vSAN on-disk format, ELM removal, and NSX Manager-to-Policy promotion. Each of these is a one-way door that requires explicit approval before proceeding. The mandatory conversion from perpetual to subscription licensing is a commercial prerequisite that must be resolved before the technical upgrade can begin. Organizations that defer the licensing conversation until upgrade day will be blocked. The 14-19 step upgrade sequence takes 3-8 weeks depending on starting version, with each component requiring its own backup, upgrade, and validation cycle. Attempting to shortcut the sequence (e.g., upgrading NSX before SDDC Manager, or skipping Aria component pre-upgrades) will cause failures that are difficult to recover from. The NSX Manager-to-Policy promotion is particularly high-risk: organizations with years of accumulated Manager-API objects must migrate them all to Policy equivalents before the Manager APIs are removed in NSX 9.0.

## Common Decisions (ADR Triggers)

- **Upgrade timing** -- Upgrade now to VCF 9.0 for latest features and unified management vs remain on VCF 5.2 (last pre-9.0 version) for stability while the 9.0 ecosystem matures; VCF 5.2 receives security patches but no new features
- **Intermediate stepping** -- VCF 5.0 must go through 5.2 first; evaluate whether to stabilize on 5.2 before proceeding to 9.0 or treat 5.2 as a pass-through
- **vSAN architecture** -- Stay on vSAN OSA (Original Storage Architecture, not deprecated) vs migrate to vSAN ESA (Express Storage Architecture, different hardware requirements) vs adopt non-vSAN principal storage (new in 9.0, external SAN/NAS as primary)
- **NSX Manager-to-Policy promotion strategy** -- Promote all objects before upgrade (required) vs clean up unused Manager objects first to reduce promotion scope; mixed-mode configurations require NSX 4.2.1+ intermediate step
- **Aria Operations for Logs** -- Fresh install VCF Operations for Logs 9.0 with 90-day data migration vs decommission Aria Logs and adopt a third-party SIEM (Splunk, Sentinel)
- **Identity Broker** -- Deploy VCF Identity Broker (VIDB) as greenfield replacement for vIDM vs continue with vIDM managed by Aria Suite Lifecycle 8.x during transition
- **Licensing** -- Convert perpetual licenses to Broadcom subscription before upgrade (required) vs evaluate alternative platforms (Nutanix, Azure, AWS) before committing to VCF 9.0 subscription model
- **vSAN on-disk format upgrade timing** -- Upgrade immediately after ESXi upgrade for full feature support vs defer to a later maintenance window to maintain rollback ability longer

## Version Notes

| Path | Steps | Timeline | Key Gate |
|---|---|---|---|
| VCF 5.1/5.2 -> 9.0 | 14 | 3-6 weeks | Aria components at minimum versions |
| VCF 5.0 -> 5.2 -> 9.0 | 15 | 4-8 weeks | Must pass through 5.2 |
| VCF 4.x -> 5.2 -> 9.0 | 20+ | 6-12 weeks | NSX-V to NSX-T if on 4.x with NSX-V |
| VCF 9.0.x maintenance | 7 | 4-8 hours | Rollback via snapshot supported |

### VCF 9.0 Component BOM

| Component | Version |
|---|---|
| SDDC Manager | 9.0.0.0 |
| ESXi | 9.0.0.0 |
| vCenter | 9.0.0.0 |
| NSX | 9.0.0.0 |
| vSAN Witness (ESA/OSA) | 9.0.0.0 |
| VCF Operations | 9.0.0.0 |
| VCF Operations Fleet Management | 9.0.0.0 |
| VCF Automation | 9.0.0.0 |
| VCF Operations for Logs | 9.0.0.0 |
| VCF Operations for Networks | 9.0.0.0 |
| VCF Identity Broker | 9.0.0.0 |

### Aria-to-VCF Renaming

| VCF 5.x Name | VCF 9.0 Name | Upgrade Status |
|---|---|---|
| Aria Operations | VCF Operations | In-place upgrade (mandatory) |
| Aria Suite Lifecycle | VCF Operations Fleet Management | Patched to 8.18p2, not upgraded to 9.0 |
| Aria Automation | VCF Automation | In-place upgrade (mandatory) |
| Aria Operations for Networks | VCF Operations for Networks | In-place upgrade (optional) |
| Aria Operations for Logs | VCF Operations for Logs | Fresh install only, no upgrade path |
| VMware Identity Manager (vIDM) | VCF Identity Broker (VIDB) | Greenfield only, no migration path |

## See Also

- [Upgrading VCF 5.2 to 9.0: Top 10 Questions](https://blogs.vmware.com/cloud-foundation/2025/12/18/upgrading-vmware-cloud-foundation-5-2-to-9-0-the-top-10-questions-answered/) -- Broadcom blog covering the most common upgrade questions
- [How to Upgrade to VCF 9.0](https://blogs.vmware.com/cloud-foundation/2025/09/25/how-to-upgrade-to-vmware-cloud-foundation-9-0/) -- step-by-step upgrade walkthrough
- [VCF 9.0 Update Sequence (KB 390634)](https://knowledge.broadcom.com/external/article/390634/update-sequence-for-vcf-90-and-compatibl.html) -- Broadcom KB with exact component ordering
- [VCF 9.0 Bill of Materials](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-0/release-notes/vmware-cloud-foundation-90-release-notes/vmware-cloud-foundation-bill-of-materials.html) -- exact component versions and build numbers
- [Broadcom Interoperability Matrix](https://interopmatrix.broadcom.com/Upgrade?productId=285) -- supported upgrade paths and compatibility
- [VCF 9.0 Licensing](https://blogs.vmware.com/cloud-foundation/2025/06/24/licensing-in-vmware-cloud-foundation-9-0/) -- subscription model, per-core pricing, unified license file
- `providers/vmware/vcf-sddc-manager.md` -- VCF deployment, SDDC Manager lifecycle, workload domain design
- `providers/vmware/licensing.md` -- VMware/Broadcom licensing models and cost analysis
- `providers/vmware/infrastructure.md` -- core VMware infrastructure including VCF 9.0 changes
- `providers/vmware/networking.md` -- NSX configuration and upgrade considerations
- `providers/vmware/storage.md` -- vSAN architecture, on-disk formats, and storage policies
- `patterns/hypervisor-migration.md` -- hypervisor migration patterns including VMware-to-alternative
