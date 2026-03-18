# Pursuit Methodology and Intake Process

## Scope

This file covers the **structured process for working infrastructure pursuits (bids/proposals)** from initial context through proposal-ready artifacts. Addresses intake, competitive positioning, commercial framing, solution design at varying confidence levels, and artifact management. Distinct from architecture design sessions (`WORKFLOW.md`) which assume requirements are known -- pursuits operate with incomplete information and competitive pressure. For migration-specific planning, see `general/workload-migration.md`. For inventory analysis, see `general/inventory-analysis.md`. For managed services scoping, see `general/managed-services-scoping.md`.

## Checklist

### Intake -- Before Creating Any Artifacts

- [ ] **[Critical]** Is the engagement type documented? (Unsolicited bid, RFP response, incumbent renewal, competitive displacement, sole-source) The type determines tone, depth, and what can be assumed.
- [ ] **[Critical]** Is the existing relationship documented? (Net-new customer, existing managed services, existing project engagement, partner referral) If the provider already operates the environment, the pursuit has fundamentally different data access and credibility than a competitive bid.
- [ ] **[Critical]** Is the customer's primary driver identified? There is usually ONE driver that makes the engagement non-optional (lease expiration, licensing cliff, compliance deadline, acquisition/divestiture, end-of-support). Secondary drivers reinforce but do not set the timeline.
- [ ] **[Critical]** Is the ownership model defined? (Customer owns assets / provider operates; provider owns assets / delivers as-a-service; hybrid; cloud consumption) This determines capital structure, commercial model, and who procures hardware.
- [ ] **[Critical]** Are hard constraints documented? (Deadlines, regulatory requirements, existing contracts, facility limitations, budget ceilings) Hard constraints are non-negotiable and shape the entire solution.
- [ ] **[Critical]** What work is already in flight? (Active migrations, ongoing modernization, parallel projects) Pursuits that build on existing work have a different narrative than greenfield proposals.
- [ ] **[Critical]** Are security enclaves or special environments identified? (Tier 0, classified, PCI zones, air-gapped networks) These often have different platform requirements, change control processes, and migration constraints.
- [ ] **[Critical]** Is the facility strategy known? (Stay in current facilities, exit to provider facilities, consolidate sites, move to cloud) This is the difference between a hypervisor migration and a datacenter relocation.
- [ ] **[Recommended]** Is the competitive landscape understood? (Sole-source, competitive with known incumbents, competitive blind) Knowing who else might bid shapes positioning and win themes.
- [ ] **[Recommended]** Are vendor relationships and deal registration requirements identified? (Partner credits, procurement discounts, registration deadlines) Deal registration is time-sensitive -- first to register typically gets the credit.
- [ ] **[Recommended]** Is the commercial model framework known? (Per-VM, per-core, fixed fee, tiered, consumption-based) The model affects architecture decisions (e.g., per-VM pricing discourages many small VMs).
- [ ] **[Optional]** Is the customer's decision-making process known? (Technical evaluation, commercial evaluation, board approval, procurement process, timeline to decision)

### Solution Development -- Confidence Levels

- [ ] **[Critical]** Is every estimate tagged with a confidence level? Use: **Measured** (from actual data), **Calculated** (derived from measured data with stated assumptions), **Estimated** (industry ratios applied to incomplete data), **Assumed** (no data, placeholder for planning). Never present an estimate without its confidence level.
- [ ] **[Critical]** Are data gaps identified and their impact on estimate accuracy documented? (e.g., "Node count is storage-based only; CPU/memory data required for accurate sizing" vs. "Node count from Nutanix Sizer with full resource data")
- [ ] **[Critical]** Are assumptions documented as ADRs with explicit "risk if wrong" statements? Every assumption is a risk -- the pursuit team and customer should understand what changes if an assumption proves incorrect.
- [ ] **[Recommended]** Are estimates presented as ranges, not point values? A range (113-172 nodes) communicates uncertainty honestly. A point value (142 nodes) implies false precision.
- [ ] **[Recommended]** Is the solution design structured to survive scope changes? Pursuits operate with incomplete information -- the design should identify which decisions are stable (platform choice) vs. which will change (node count, facility locations).

### Artifact Management

- [ ] **[Critical]** Is there a single source of truth for quantitative data? (One document holds VM counts, storage figures, site details; all other artifacts reference it, not duplicate it) Duplicated numbers across documents become inconsistent.
- [ ] **[Critical]** Are artifacts timestamped in their content? Pursuit artifacts circulate via email, print, and screenshots -- the document itself must show when it was last updated.
- [ ] **[Critical]** Are artifacts free of tooling attribution? (No "generated by" tags, no AI references, no tool names) Pursuit deliverables are professional documents.
- [ ] **[Recommended]** Are artifacts structured for the audience? (Summary for executives, solution design for technical evaluators, discovery questions for workshop facilitation) Different audiences need different depths.
- [ ] **[Recommended]** Is the artifact dependency chain documented? (Summary depends on Solution Design depends on Site Analysis depends on Inventory Data) Updates should flow top-down from the data.
- [ ] **[Optional]** Is version control in place for pursuit artifacts? Pursuits iterate rapidly -- the team should know which version of a document was shared with the customer.

### Competitive Positioning

- [ ] **[Recommended]** Are win themes documented? (3-5 reasons this provider wins over alternatives) Win themes should be evidence-based, not aspirational.
- [ ] **[Recommended]** Are differentiators specific and verifiable? ("We manage this environment today" is verifiable. "We have deep expertise" is not.)
- [ ] **[Recommended]** Is the "why now" narrative clear? What makes this the right time for the customer to act, and why this provider is best positioned at this moment.
- [ ] **[Optional]** Are competitor weaknesses identified without naming competitors? Frame as "risks of alternative approaches" rather than attacking specific vendors.

### Commercial Framing

- [ ] **[Recommended]** Are capital offsets identified? (Hardware buyback, license reclamation, lease termination savings, avoided renewal costs) These reduce the customer's perceived cost of the transformation.
- [ ] **[Recommended]** Is the total cost of ownership (TCO) comparison framed correctly? Compare current state costs (including hidden costs like VMware licensing increases, facility costs, operational overhead) against proposed state.
- [ ] **[Recommended]** Are deal registration and vendor credits factored in? Partner discounts can be 15-30% on hardware and licensing -- material to the commercial model.
- [ ] **[Optional]** Is the contract structure aligned with the solution? (Contract duration matches hardware amortization, pricing model matches consumption pattern, SLA structure matches architecture redundancy)

## Why This Matters

Pursuits fail for process reasons more often than technical reasons. The most common failures:

1. **Incomplete intake.** The solution team builds artifacts based on partial context, then discovers critical constraints (facility exit, security enclaves, active migrations) that require complete rework. A 15-minute structured intake prevents hours of rework.

2. **False precision.** Presenting a node count calculated from incomplete data (storage only, no CPU/memory) as if it were accurate. When the customer runs the numbers through their own sizing tool and gets a different answer, credibility is damaged. Confidence levels and ranges prevent this.

3. **Duplicated data across artifacts.** VM counts, storage figures, and site details appear in five documents. When one number changes, three documents get updated and two don't. The customer finds the inconsistency. A single source of truth prevents this.

4. **Missing the driver.** The solution design optimizes for technical elegance when the customer's actual driver is "get out of these buildings by the lease end." Understanding the primary driver -- and framing the entire proposal around it -- is the difference between a winning bid and a technically impressive document that doesn't address the customer's problem.

5. **No competitive differentiation.** The proposal describes what will be done but not why this provider should do it. In competitive situations, the "why us" narrative must be explicit, evidence-based, and woven throughout -- not just a bullet point on the last slide.

## Pursuit Intake Template

Use this template at the start of every pursuit to capture context before creating artifacts:

```
PURSUIT INTAKE
==============
Customer:
Engagement type:    [ ] Unsolicited bid  [ ] RFP response  [ ] Renewal  [ ] Competitive displacement
Existing relationship:
Primary driver:
Hard deadline:
Ownership model:    [ ] Customer-owned/provider-operated  [ ] Provider-owned as-a-service  [ ] Cloud  [ ] Hybrid
Work already in flight:
Security enclaves:
Facility strategy:  [ ] Stay in place  [ ] Exit to provider facilities  [ ] Consolidate  [ ] Cloud
Competitive landscape:
Vendor deal registration needed:
Commercial model:
Available data sources:
Key contacts:
Decision timeline:
```

## Artifact Dependency Chain

For infrastructure transformation pursuits, artifacts should be created in this order:

```
1. Inventory Data (raw data -- uploaded files, exports)
       |
2. Site and Workload Analysis (single source of truth for all numbers)
       |
   +---+---+
   |       |
3a. Discovery Questions    3b. Proposed Solution Design
   (what we need to know)     (what we propose, with confidence levels)
       |                           |
   +---+---------------------------+
   |                               |
4. Summary                    5. NBIE (Non-Binding Indicative Estimate)
   (written last, read first)     (internal: effort, roles, hours, timeline)
```

The Summary should be the last customer-facing artifact created but the first one the customer reads. It should be generatable from the other artifacts without independent data.

The NBIE is an internal artifact that derives effort estimates from the Solution Design and Inventory Data. It is never shared with the customer. See `general/nbie.md` for structure and methodology.

## Confidence Level Definitions

| Level | Definition | When to Use | How to Present |
|-------|-----------|-------------|----------------|
| **Measured** | Directly from data (inventory export, monitoring, billing) | VM counts from hypervisor export, storage from datastore reports | State as fact with source citation |
| **Calculated** | Derived from measured data using stated formula | Data transfer time from measured storage volume and assumed bandwidth | State formula and assumptions explicitly |
| **Estimated** | Industry ratios applied to incomplete data | Node count from storage only (no CPU/memory) | Present as range with caveats |
| **Assumed** | No supporting data, placeholder for planning | SLA targets before customer input, facility readiness timeline | Label clearly as assumption with "risk if wrong" |

## Common Decisions (ADR Triggers)

- **Pursuit scope boundary** -- what is in the proposal vs. what is explicitly excluded; prevents scope creep during pursuit and sets customer expectations
- **Data confidence threshold** -- minimum data quality before committing to estimates in the proposal; determines whether to present numbers or flag as "requires discovery"
- **Artifact audience mapping** -- which documents go to which stakeholders; prevents technical deep-dives reaching executives or high-level summaries reaching evaluators
- **Competitive positioning strategy** -- lead with relationship (if incumbent) vs. lead with technical approach (if challenger) vs. lead with commercial model (if cost-advantaged)
- **Intake completeness gate** -- at what point is enough context gathered to begin artifact creation; prevents premature writing and repeated rework

## See Also

- `general/workload-migration.md` -- Migration strategy and execution planning
- `general/inventory-analysis.md` -- Infrastructure inventory analysis methodology
- `general/managed-services-scoping.md` -- Managed services commercial and operational scoping
- `general/capacity-planning.md` -- Capacity planning methodology
- `general/nbie.md` -- Non-Binding Indicative Estimate structure and methodology
- `general/multi-site-migration-sequencing.md` -- Multi-site migration wave planning
