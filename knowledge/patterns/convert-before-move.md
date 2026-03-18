# Convert-Before-Move vs Convert-After-Move Strategy

## Scope

This file covers the **strategic timing decision for in-place hypervisor conversion when a datacenter relocation is also planned**. Specifically: when ESX VMs run on Nutanix hardware and the environment is relocating to a new facility, should the hypervisor conversion (ESXi → AHV) happen at the source site before relocation, or at the target site after relocation? This decision affects migration effort, timeline, risk profile, and maintenance window requirements. For in-place conversion mechanics, see `providers/nutanix/in-place-conversion.md`. For datacenter relocation, see `patterns/datacenter-relocation.md`. For migration tooling, see `providers/nutanix/migration-tools.md`.

## Checklist

### Strategy Selection

- [ ] **[Critical]** Is the convert-before-move vs convert-after-move decision documented as an ADR with rationale? (This is not a default -- both approaches have trade-offs that must be evaluated per engagement.)
- [ ] **[Critical]** Is the effort comparison quantified? (In-place conversion: hours per cluster, rolling process. Nutanix Move for same VMs: weeks of seeding per cluster, per-VM cutover. The difference can be 10-50x for large clusters.)
- [ ] **[Critical]** Are the prerequisites for in-place conversion validated per cluster? (Nutanix-certified hardware, compatible AOS version, no vDS, no NSX, no physical RDMs, no PCIe passthrough, healthy CVMs, sufficient N-1 capacity. If prerequisites fail, the cluster falls back to Move.)
- [ ] **[Recommended]** Is the maintenance window availability at the source site assessed? (In-place conversion requires a rolling maintenance window -- approximately 30-60 minutes per node. If the source environment has strict change freeze periods, conversion may not fit the schedule.)
- [ ] **[Recommended]** Is Nutanix Support availability confirmed? (In-place conversion typically requires Nutanix Support involvement or a certified partner. Engage early -- support scheduling may have lead times.)

### Convert-Before-Move (Recommended Default)

- [ ] **[Critical]** Is VirtIO driver pre-installation planned for all Windows VMs on the cluster before conversion? (Linux VMs have in-kernel VirtIO support. Windows VMs need Nutanix VirtIO drivers installed before the host hypervisor changes -- otherwise they will not boot on AHV.)
- [ ] **[Critical]** Is VM network mapping prepared? (ESXi port groups must map to AHV virtual networks. The conversion process needs this mapping to reconnect VMs after node re-imaging.)
- [ ] **[Recommended]** Is the conversion sequence planned per cluster? (One node at a time. VMs evacuate via vMotion to remaining nodes. Node is re-imaged to AHV. Node rejoins cluster. Next node. Verify all VMs running after final node.)
- [ ] **[Recommended]** Is the post-conversion validation plan defined? (All VMs booted, network connectivity verified, application health checked, backup jobs updated to AHV-compatible methods. Do not proceed to relocation until conversion is validated.)

### Convert-After-Move (Alternative)

- [ ] **[Recommended]** Is the rationale for deferring conversion documented? (Common reasons: no maintenance window available at source, source environment in change freeze, conversion prerequisites not met, customer preference to minimize source-site changes.)
- [ ] **[Recommended]** Is the additional Move effort quantified? (These VMs will be migrated via Nutanix Move as ESX VMs -- weeks of seeding + per-VM cutover. Then at the target, the clusters must still be converted from ESXi to AHV, requiring the same maintenance windows and prerequisites. Total effort is higher.)

### Hybrid Approach

- [ ] **[Optional]** Is a per-cluster decision appropriate? (Some clusters may meet conversion prerequisites while others do not. Convert eligible clusters at source, Move the rest. Document the decision per cluster.)

## Decision Matrix

| Factor | Convert-Before-Move | Convert-After-Move |
|--------|--------------------|--------------------|
| **Total effort** | Lower -- conversion replaces Move migration for these VMs | Higher -- Move migration + conversion at target |
| **Timeline** | Faster -- conversion is hours per cluster vs weeks of Move seeding | Slower -- Move seeding for ESX VMs, then conversion |
| **Risk at source** | Higher -- changes production environment | Lower -- source unchanged |
| **Risk at target** | Lower -- relocation is simple AHV-to-AHV | Higher -- must convert at unfamiliar target |
| **Maintenance windows** | Required at source | Required at target |
| **Prerequisites** | Must be validated at source | Must be validated at target |
| **Nutanix Support** | Engaged at source | Engaged at target |
| **Network transfer** | Less data (converted VMs relocate as AHV-to-AHV with Prism replication, potentially more efficient) | More data (ESX VMs seeded via Move, full VM data transfer) |

**Default recommendation:** Convert-before-move. The effort savings are significant (hours vs weeks per cluster), the source environment is known and proven, and the conversion de-risks the relocation by making it a simpler same-hypervisor move.

**Exception:** If the source environment is in a change freeze, has strict maintenance window constraints, or if specific clusters fail prerequisite checks, those clusters should use Move (convert-after-move or remain on ESXi at target).

## Effort Comparison Example

For a cluster with 200 VMs and 50 TB of data:

| Approach | Conversion Effort | Migration Effort | Total |
|----------|-------------------|------------------|-------|
| Convert-before-move | ~4-6 hours (8-node cluster, 30-45 min/node) | AHV-to-AHV relocation (Prism replication or Move) | ~1-2 weeks total |
| Convert-after-move | N/A (deferred) | ESX-to-AHV via Move: ~2-4 weeks seeding + cutover | ~3-5 weeks total, then still need conversion at target |

## Why This Matters

The convert-before-move vs convert-after-move decision can be the difference between weeks and months of migration effort for large ESX-on-Nutanix estates. In environments with thousands of VMs on Nutanix hardware running ESXi, in-place conversion eliminates the most time-consuming step (Move seeding) for those VMs.

The most common failure: **not realizing the option exists.** Teams default to Nutanix Move for all ESX VMs without distinguishing between ESX-on-VMware-hardware (Move is the only option) and ESX-on-Nutanix-hardware (in-place conversion is available and dramatically faster).

The second most common failure: **attempting in-place conversion on clusters with unsupported configurations.** vDS port groups, NSX overlay networks, physical RDMs, and PCIe passthrough devices all block conversion. These must be identified and remediated before conversion -- or the cluster must fall back to Move.

## Common Decisions (ADR Triggers)

- **Convert-before-move vs convert-after-move** -- per-engagement or per-cluster decision; document rationale and effort comparison
- **Hybrid approach** -- which clusters convert at source, which use Move; based on prerequisite validation results
- **Maintenance window scheduling** -- at source or target; coordinate with change management
- **VirtIO driver deployment** -- pre-install on all Windows VMs before conversion; requires access and a deployment method (SCCM, manual, or Nutanix Guest Tools)

## Reference Links

- [Nutanix In-Place Conversion Guide](https://portal.nutanix.com/page/documents/list?type=software) -- Nutanix documentation for in-place hypervisor conversion from ESXi to AHV
- [Nutanix VirtIO Drivers](https://portal.nutanix.com/page/downloads?product=virtio) -- Nutanix VirtIO driver downloads required for Windows VMs before hypervisor conversion

## See Also

- `providers/nutanix/in-place-conversion.md` -- In-place conversion prerequisites and process
- `providers/nutanix/migration-tools.md` -- Nutanix Move capabilities and limitations
- `patterns/datacenter-relocation.md` -- Datacenter relocation planning
- `patterns/hypervisor-migration.md` -- Hypervisor migration strategy
