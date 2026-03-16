# Facility Lifecycle

## Scope

This file covers **data center facility lifecycle management**: lease-driven migration timelines, site sequencing, decommission planning, asset disposition, and facility handback. For workload migration execution, see `general/workload-migration.md`. For disaster recovery during transitions, see `general/disaster-recovery.md`. For cost analysis of on-premises vs cloud, see `general/cost-onprem.md`.

## Checklist

- [ ] [Critical] Are all facility lease expiry dates documented with at least 18 months of lead time before the earliest expiry?
- [ ] [Critical] Are sites sequenced for migration based on lease urgency, with earliest-expiring leases migrated first?
- [ ] [Critical] Is there a contingency plan if migration cannot complete before a lease expires? (extension, temporary colocation, staged decommission)
- [ ] [Critical] Are lease extension negotiation timelines identified? (most leases require 6-12 months notice for extension)
- [ ] [Critical] Is the decommission timeline aligned with the lease end date, including buffer for handback activities?
- [ ] [Critical] Are insurance and liability policies reviewed for the transition period? (coverage gaps between facility exit and cloud operational state)
- [ ] [Recommended] Is a cost comparison completed for lease extension vs accelerated migration?
- [ ] [Recommended] Is a formal data center exit plan documented? (phased approach, stakeholder sign-off, regulatory notifications)
- [ ] [Recommended] Are asset disposition requirements defined? (ITAD vendor selection, chain-of-custody documentation, certificates of destruction)
- [ ] [Recommended] Are e-waste compliance obligations mapped to applicable jurisdictions? (WEEE, R2, e-Stewards, state-level regulations)
- [ ] [Recommended] Are facility handback requirements documented? (clean room condition, cable removal, raised floor restoration, environmental remediation)
- [ ] [Optional] Is a facility handback walkthrough scheduled with the landlord before decommission begins?
- [ ] [Optional] Are historical maintenance records and environmental reports compiled for handback documentation?

## Why This Matters

Facility leases are the hardest deadline in any migration program. Unlike technical milestones, lease expiry dates are contractual obligations with financial penalties. A migration program that ignores lease timelines risks either paying for empty facilities or rushing workloads into an unprepared cloud environment.

The most expensive failure mode is a lease that expires before migration completes, forcing an unplanned extension at unfavorable rates. Landlords know you have no leverage when your equipment is still in their building. The second most expensive failure is an incomplete decommission that triggers handback penalties or ongoing liability.

Facility lifecycle management turns a real estate deadline into a structured engineering program with clear milestones, fallback options, and cost-controlled outcomes.

## Lease-Driven Migration Timeline

### Working Backward from Lease Expiry

Every facility migration timeline starts from the lease end date and works backward:

| Milestone | Timing Before Lease End | Activities |
|-----------|------------------------|------------|
| **Handback complete** | Lease end date (T-0) | Facility returned to landlord in agreed condition |
| **Final inspection** | T - 2 weeks | Walkthrough with landlord, punch list resolution |
| **Facility handback prep** | T - 1 to 2 months | Cable removal, floor restoration, cleaning, environmental |
| **Asset disposition** | T - 2 to 4 months | Hardware removal, ITAD processing, e-waste disposal |
| **Last workload migrated** | T - 3 to 6 months | All workloads running in target environment, source decommissioned |
| **Migration execution** | T - 6 to 18 months | Wave-based migration per workload migration plan |
| **Migration planning** | T - 12 to 24 months | Assessment, wave planning, target environment build |
| **Decision point** | T - 18 to 24 months | Migrate, extend lease, or renegotiate — decision must be made |

### Lead Time Reality

- **Lease extension notice**: Most commercial leases require 6-12 months written notice for renewal or extension
- **Migration planning**: 3-6 months minimum for assessment and target design
- **Migration execution**: 6-18 months depending on workload count and complexity
- **Decommission and handback**: 2-4 months after last workload migrates
- **Total minimum lead time**: 18-24 months before lease expiry

## Site Sequencing

### Prioritization Criteria

Sites should be sequenced for migration using a weighted scoring model:

| Factor | Weight | Rationale |
|--------|--------|-----------|
| **Lease expiry date** | Highest | Contractual deadline is non-negotiable |
| **Extension feasibility** | High | Some leases cannot be extended (building demolition, landlord plans) |
| **Workload criticality** | High | Sites with lower-risk workloads are better early candidates |
| **Workload complexity** | Medium | Simpler sites build team confidence for harder migrations |
| **Site interdependencies** | Medium | Sites with cross-site dependencies may need coordinated migration |
| **Cost of continued operation** | Medium | High-cost sites yield faster ROI when migrated |

### Sequencing Strategy

1. **Earliest expiry, lowest complexity first** — Build migration muscle on simpler sites before tackling complex ones
2. **Group interdependent sites** — Sites that share data or services should migrate in adjacent waves
3. **Reserve buffer for the hardest site** — The most complex site should not be the last one with the tightest deadline
4. **Parallel execution when teams allow** — Multiple sites can migrate simultaneously if staffing permits

### When Lease Dates Conflict with Technical Readiness

If the earliest-expiring site is also the most complex:

- Negotiate a short-term extension for that site (6-12 months)
- Migrate a simpler site first to build capability
- Return to the complex site with proven processes and a trained team

## Contingency Planning

### When Migration Cannot Complete Before Lease Expiry

| Option | Cost Impact | Risk | When to Use |
|--------|-----------|------|-------------|
| **Lease extension** | Monthly rent continues, often at premium rates | Low technical risk, high cost risk | Migration is 1-6 months behind schedule |
| **Temporary colocation** | Move hardware to colocation facility | Medium — adds an extra physical move | Landlord will not extend, workloads not ready for cloud |
| **Partial migration** | Migrate critical workloads, retire or repurchase the rest | Medium — forces rapid decisions on remaining workloads | Most workloads are migrated, stragglers remain |
| **Accelerated migration** | Staff augmentation, extended hours, vendor support | High — compressed timelines increase error rates | Migration is weeks behind, not months |
| **Workload retirement** | Decommission workloads that cannot migrate in time | Varies — acceptable for non-critical workloads | Legacy workloads with low business value |

### Red Flag Triggers for Contingency Activation

- Migration is more than 20% behind schedule at the halfway point
- Critical path workloads have not started migration with less than 6 months to lease end
- Target environment has unresolved blockers (security, compliance, connectivity)
- Key migration staff have departed or been reassigned
- Vendor tooling is not performing to expected throughput

## Lease Extension Analysis

### Cost of Extension vs Accelerated Migration

| Cost Category | Lease Extension | Accelerated Migration |
|---------------|----------------|----------------------|
| **Facility costs** | Monthly rent, power, cooling, maintenance | None (migration completes on time) |
| **Staffing** | Standard migration team | Premium rates for surge staffing, overtime, contractors |
| **Risk premium** | Landlord may demand above-market rates for short extensions | Higher error rates, potential rework, incident risk |
| **Dual-running costs** | Extended period of paying for both environments | Shorter dual-running but higher cloud costs from rushed sizing |
| **Opportunity cost** | Delays cloud-native benefits, team tied to legacy | Team burnout, reduced quality on other initiatives |

### Extension Negotiation Considerations

- **Start early** — Notify the landlord of potential extension need as soon as risk is identified
- **Request month-to-month** — Avoid committing to a full term extension; negotiate holdover or month-to-month rates
- **Understand holdover clauses** — Many leases have automatic holdover at 125-150% of the last monthly rate
- **Document everything** — Extension agreements must be in writing, even if informal conversations occur
- **Factor in all costs** — Rent, CAM (common area maintenance), insurance, taxes, utilities, and staffing
- **Negotiate decommission-friendly terms** — Ensure the extension period allows for phased equipment removal

## Data Center Exit Planning

### Exit Plan Structure

A formal data center exit plan should include:

1. **Executive summary** — Business case, timeline, cost summary, risk summary
2. **Workload inventory** — Every workload in the facility with its migration disposition (6 Rs)
3. **Migration wave plan** — Sequenced waves with dependencies, dates, and owners
4. **Decommission sequence** — Order of rack decommission, power circuit surrender, network disconnection
5. **Asset disposition plan** — What happens to every physical asset (return to lessor, ITAD, transfer, dispose)
6. **Facility handback plan** — Condition requirements, remediation work, inspection schedule
7. **Stakeholder communication plan** — Who is notified at each milestone
8. **Risk register** — Identified risks with mitigations and contingency triggers
9. **Budget** — Migration costs, decommission costs, extension contingency, asset recovery credits

### Decommission Sequence

Decommission racks in reverse dependency order:

1. **Non-production environments** — Dev, test, staging (lowest impact)
2. **Batch and analytics workloads** — Can tolerate scheduled downtime
3. **Internal applications** — HR, finance, collaboration (migrate during maintenance windows)
4. **Customer-facing applications** — Require zero-downtime migration
5. **Shared infrastructure** — DNS, Active Directory, monitoring (last to leave)
6. **Network equipment** — Routers, switches, firewalls (after all workloads are migrated)
7. **Power and cooling** — Coordinate with facility management for staged power-down

## Asset Disposition

### IT Asset Disposition (ITAD) Process

| Phase | Activities | Documentation |
|-------|-----------|---------------|
| **Inventory** | Tag and catalog all assets (servers, storage, network, cabling, accessories) | Asset register with serial numbers, locations, and ownership |
| **Data sanitization** | Wipe or destroy all storage media per NIST 800-88 guidelines | Certificates of sanitization per device |
| **Valuation** | Assess resale value of reusable equipment | Appraisal report |
| **Remarketing** | Sell or donate reusable equipment through certified channels | Bill of sale, donation receipts |
| **Destruction** | Physically destroy non-reusable or classified storage media | Certificates of destruction with witness signatures |
| **Recycling** | Process remaining materials through certified e-waste recycler | Recycling certificates, downstream vendor documentation |

### Data Sanitization Standards

| Classification | Method | Standard |
|---------------|--------|----------|
| **Public/Internal** | Software overwrite (3-pass minimum) | NIST 800-88 Clear |
| **Confidential** | Cryptographic erase or degaussing | NIST 800-88 Purge |
| **Highly Confidential / Regulated** | Physical destruction (shredding, incineration) | NIST 800-88 Destroy |

### E-Waste Compliance

- **R2 (Responsible Recycling)** — Downstream accountability, focus tracking, data security
- **e-Stewards** — Zero landfill, no export to developing countries, worker safety
- **WEEE Directive** (EU) — Producer responsibility for collection and recycling
- **State-level regulations** (US) — Many states have specific e-waste disposal laws; check per jurisdiction
- **Chain of custody** — Document every handoff from your facility to final disposition
- **Audit your ITAD vendor** — Verify certifications, visit processing facilities, check downstream vendors

## Facility Handback

### Common Handback Requirements

| Requirement | Description | Typical Timeline |
|-------------|-------------|-----------------|
| **Equipment removal** | All tenant-owned equipment must be removed | 2-4 weeks |
| **Cable removal** | All tenant-installed cabling (network, power, fiber) removed from raised floor and overhead | 1-3 weeks |
| **Raised floor restoration** | Floor tiles replaced, pedestals adjusted, cutouts filled | 1-2 weeks |
| **Patch and paint** | Walls, columns, and surfaces restored to baseline condition | 1-2 weeks |
| **Environmental remediation** | Battery acid cleanup (UPS), coolant disposal, fuel tank draining | 1-4 weeks |
| **Fire suppression** | Restore or remove tenant-installed suppression systems | 1-2 weeks |
| **Security system removal** | Remove tenant access controls, cameras, and monitoring | 1 week |
| **Documentation** | As-built drawings, maintenance records, environmental reports | Compile throughout |

### Handback Process

1. **Review lease terms** — Identify specific handback obligations (these vary significantly by lease)
2. **Pre-inspection walkthrough** — Walk the space with the landlord 3-6 months before handback to agree on scope
3. **Remediation planning** — Scope and schedule all required restoration work
4. **Execute remediation** — Complete all physical work before the final inspection
5. **Final inspection** — Formal walkthrough with landlord, document condition, resolve punch list items
6. **Handback certificate** — Obtain written confirmation that the facility has been accepted
7. **Security deposit recovery** — Submit for return of security deposit per lease terms

### Cost Estimation for Handback

Budget for handback costs separately from migration costs. Common ranges:

- **Cable removal**: Varies significantly by density and facility size
- **Raised floor restoration**: Per-tile or per-square-foot, depending on condition
- **Environmental remediation**: Highly variable based on what systems were installed
- **General restoration**: Depends on lease terms — some require "broom clean," others require original condition

**Always get a landlord walk-through early** to avoid surprises. Handback disputes can delay security deposit return and create ongoing liability.

## Insurance and Liability

### Transition Period Risks

| Risk | Coverage Needed | Notes |
|------|----------------|-------|
| **Equipment damage during removal** | Inland marine / transit insurance | Covers equipment in transit to ITAD or new location |
| **Data breach from disposed assets** | Cyber liability | Extends to data on decommissioned hardware |
| **Environmental liability** | Environmental impairment liability | Battery acid, coolant, diesel fuel contamination |
| **Worker injury** | Workers compensation, general liability | Decommission work involves physical hazards |
| **Third-party property damage** | General liability | Damage to landlord property during equipment removal |
| **Gaps in service availability** | Business interruption | Coverage during cutover windows |

### Liability Considerations

- **Maintain facility insurance through handback** — Do not cancel insurance before the landlord accepts the space
- **Verify ITAD vendor insurance** — Your vendor should carry their own liability, data breach, and environmental coverage
- **Indemnification clauses** — Ensure contracts with decommission vendors include indemnification for data breaches and environmental incidents
- **Tail coverage** — Some liabilities (environmental, data breach) can emerge years after facility exit; ensure tail coverage is in place
- **Document everything** — Photographs, video, and written records of facility condition at handback protect against future claims

## Common Decisions (ADR Triggers)

- **Site migration sequence** — which facilities migrate first, based on lease dates and complexity
- **Lease extension vs accelerated migration** — cost-risk tradeoff when timelines are tight
- **Contingency strategy** — what happens if migration falls behind schedule (extend, colocate, retire)
- **ITAD vendor selection** — certified vendor choice, destruction vs remarketing policy
- **Data sanitization standard** — which NIST 800-88 level per data classification
- **Handback scope** — negotiated restoration requirements with landlord
- **Insurance strategy during transition** — coverage types, tail coverage duration, vendor requirements
- **Decommission sequencing** — order of rack and infrastructure removal within each facility

## See Also

- `general/workload-migration.md` — Migration execution strategy and wave planning
- `general/disaster-recovery.md` — DR planning during facility transitions
- `general/cost-onprem.md` — On-premises cost modeling for extension vs migration analysis
- `general/hardware-sizing.md` — Hardware inventory and assessment for asset disposition
- `general/governance.md` — Compliance and regulatory requirements for facility operations
