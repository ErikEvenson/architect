# Non-Binding Indicative Estimate (NBIE)

## Scope

This file covers the **structure and methodology for creating Non-Binding Indicative Estimates** -- internal, directional cost/effort estimates used during the pursuit phase before detailed solutioning. An NBIE provides enough fidelity to evaluate commercial viability, allocate pursuit resources, and develop a Preliminary Cost Indication (PCI). Distinct from a Statement of Work (SOW) or detailed proposal -- an NBIE is internal, non-binding, and based on incomplete information with documented assumptions. For pursuit process, see `general/pursuit-methodology.md`. For managed services scoping, see `general/managed-services-scoping.md`.

## Checklist

### Structure

- [ ] **[Critical]** Does the NBIE include a Pursuit Context section? (Customer, engagement type, primary driver, existing relationship, deal size, key contacts, comparable engagements)
- [ ] **[Critical]** Is the Scope of Estimate clearly defined? (What workstreams are included, what is explicitly excluded, who owns excluded workstreams) An NBIE that does not define its boundaries will be misinterpreted.
- [ ] **[Critical]** Is the Solution Approach summarized at a level sufficient to justify the effort estimate? (Reference the Solution Design artifact -- do not duplicate it, but the reader must understand what work is being estimated)
- [ ] **[Critical]** Are roles defined with clear responsibilities? (Solution Architect, Senior Consultant, Consultant, Project Manager, SME -- or whatever role taxonomy the organization uses)
- [ ] **[Critical]** Is effort broken down by phase AND by role? The two dimensions serve different audiences: phase breakdown shows timeline, role breakdown shows staffing and cost.
- [ ] **[Critical]** Does the NBIE include an Assumptions section listing every assumption that, if wrong, would change the estimate? Each assumption should state the impact if wrong.
- [ ] **[Critical]** Does the NBIE include a Confidence Level for each major estimate component? Use the standard confidence levels: Measured, Calculated, Estimated, Assumed (see `general/pursuit-methodology.md`).
- [ ] **[Recommended]** Is peak staffing documented? (Maximum concurrent headcount by role during the most resource-intensive phase) This drives recruiting/staffing lead time.
- [ ] **[Recommended]** Is the timeline estimate included with dependency on other workstreams? (e.g., "Build phase cannot start until target facilities are ready")
- [ ] **[Recommended]** Are risks to the estimate documented with their potential impact on hours? (Not project risks -- specifically risks that the estimate itself is wrong)
- [ ] **[Optional]** Is there a comparison to similar past engagements? (Comparable pursuits, similar VM counts or site counts, actual vs estimated hours) This is the strongest validation of an NBIE.

### Effort Estimation Methodology

- [ ] **[Critical]** Is the effort model documented? Common approaches: (a) Activity-based: list activities, estimate hours per activity. (b) Ratio-based: effort per VM, per site, per migration wave. (c) Analogous: based on comparable past engagements. (d) Hybrid: activity-based for known work, ratio-based for repetitive work. Document which method is used and why.
- [ ] **[Critical]** For migration engagements, is the effort-per-VM ratio documented with its source? Typical ranges: 0.1-0.3 hrs/VM for simple rehost (automated tooling), 0.5-1.0 hrs/VM for platform migration with validation, 2-4 hrs/VM for complex migrations with application dependencies. The ratio should account for pre-migration checks, seeding, cutover, and post-migration validation.
- [ ] **[Recommended]** Are fixed costs (per-site setup, per-phase overhead) separated from variable costs (per-VM, per-TB)? This allows the estimate to scale if scope changes.
- [ ] **[Recommended]** Is the migration velocity assumption documented? (VMs per day, per stream, per site) This drives both the timeline and the peak staffing requirement.

### Quality Gates

- [ ] **[Critical]** Has the NBIE been reviewed against the actual data? (VM counts, site counts, storage volumes should match the Source VM Inventory artifact exactly)
- [ ] **[Recommended]** Do the phase subtotals sum to the total? (Arithmetic check -- surprisingly common source of errors in large estimates)
- [ ] **[Recommended]** Is the hours-per-VM implied ratio reasonable? (Total implementation hours / total VMs = implied ratio. If this is far outside the 0.1-1.0 range, investigate.)
- [ ] **[Recommended]** Is the FTE-month calculation correct? (Total hours / 160 hrs per month = FTE-months. Does the resulting team size feel reasonable for the scope?)

## Standard NBIE Sections

1. **Pursuit Context** -- customer (internal reference only), engagement type, driver, deal size, key roles
2. **Scope of Estimate** -- what workstreams are in/out, who owns what
3. **Solution Approach Summary** -- high-level reference to solution design (do not duplicate)
4. **Role Definitions** -- roles used in the estimate with responsibilities
5. **Effort Estimate** -- broken down by phase, then by activity within each phase, with hours per role
6. **Effort Summary** -- totals by phase and by role, FTE-months, peak staffing
7. **Timeline Estimate** -- phase durations, overlaps, dependencies on other workstreams
8. **Assumptions** -- numbered list with "impact if wrong" for each
9. **Risks to Estimate** -- what could change the numbers, likelihood, and impact in hours
10. **Estimate Confidence** -- per-component confidence level (Measured/Calculated/Estimated/Assumed)
11. **Next Steps** -- what happens with this estimate (rate cards, PCI, integration with other workstreams)

## Typical Phase Structure for Infrastructure Engagements

For infrastructure transformation pursuits (hypervisor migration, datacenter relocation, platform modernization), the NBIE typically covers three consulting phases:

### Advise
Discovery, assessment, architecture design, recommendations. Architect-heavy. Produces design documents, migration strategy, and discovery questions for the customer.

### Build
Platform deployment and configuration at target environment. Senior Consultant-heavy. Covers everything after hardware is racked and vendor-configured: management platform setup, cluster configuration, networking, storage, automation, data protection.

### Implementation
Migration execution. Consultant-heavy (scales with VM count). Site-by-site or wave-by-wave migration including pre-migration checks, data seeding, cutover, validation, and hypercare. Handoff to steady-state operations team at completion.

### Cross-Phase Project Management
Planning, scheduling, governance, risk management, stakeholder reporting, cross-workstream coordination. Runs the full duration of the engagement.

## Effort Ratios (Rules of Thumb)

These ratios are starting points for NBIE estimation. Refine with engagement-specific data.

| Activity | Ratio | Unit | Notes |
|----------|-------|------|-------|
| Advise phase | 300-600 hours | Per engagement | Relatively fixed; scales modestly with site count |
| Build phase | 80-160 hours | Per target site/region | Scales with cluster count and configuration complexity |
| Migration (automated tool, simple) | 0.10-0.20 hrs | Per VM | Nutanix Move, Zerto -- automated seeding + cutover |
| Migration (with validation) | 0.15-0.30 hrs | Per VM | Includes pre/post checks, infrastructure validation |
| Migration setup | 40-80 hours | Per site | Move appliance deployment, connectivity validation |
| Hypercare | 80-160 hours | Per site | 1-2 weeks post-cutover monitoring |
| Virtual appliance re-deploy | 4-8 hours | Per appliance instance | Fresh deploy from vendor image + config import |
| Project management | 8-12% | Of total effort | Higher % for multi-workstream, multi-site engagements |

## Why This Matters

The NBIE serves three critical functions in a pursuit:

1. **Commercial viability.** Before investing in detailed solutioning, the pursuit team needs to know if the deal makes financial sense. The NBIE provides the labor component of the PCI. If the hours are too high relative to expected revenue, the pursuit may not be worth pursuing.

2. **Resource planning.** The NBIE identifies when and how many people are needed. For large engagements (12+ months, multiple FTEs), staffing lead time is 4-8 weeks. An early NBIE lets resource management begin sourcing while solutioning continues.

3. **Scope control.** A documented NBIE with clear assumptions and exclusions prevents scope creep during the pursuit. When someone asks "can we also include X?", the impact on hours is visible and discussable.

The most common NBIE failure: **not documenting assumptions.** An estimate without assumptions becomes a commitment. When the customer reveals information that invalidates an assumption, the estimate should change -- but only if the assumption was documented. Undocumented assumptions become surprise cost overruns.

## Common Decisions (ADR Triggers)

- **Estimate methodology** -- activity-based vs ratio-based vs analogous; determines estimate fidelity and the effort required to produce the estimate itself
- **Phase boundaries** -- where does Advise end and Build begin? Where does Build end and Implementation begin? Clear handoff points prevent double-counting or gaps
- **Scope boundary with other workstreams** -- what the consulting estimate includes vs what other teams (managed services, network, facilities) estimate separately; prevents duplicate or missing effort
- **Migration velocity assumption** -- VMs per day drives both timeline and peak staffing; too aggressive creates delivery risk, too conservative inflates the estimate
- **Confidence threshold for submission** -- at what confidence level is the NBIE "good enough" to base a PCI on? Typically Estimated is sufficient for NBIE; Calculated is expected for SOW

## See Also

- `general/pursuit-methodology.md` -- Pursuit process, intake, confidence levels, artifact management
- `general/managed-services-scoping.md` -- Managed services commercial and operational scoping
- `general/workload-migration.md` -- Migration strategy and execution planning
- `general/multi-site-migration-sequencing.md` -- Multi-site wave planning
