# Private Cloud As-a-Service

## Scope

This file covers the **provider-owned, provider-operated infrastructure model** where the managed services provider owns hardware, licensing, and facility contracts, and delivers compute/storage/network to the customer as a service. The customer consumes infrastructure with no asset ownership -- pure OpEx. Distinct from traditional managed services where the customer owns assets and the provider operates them. For managed services operational scoping, see `general/managed-services-scoping.md`. For facility lifecycle, see `general/facility-lifecycle.md`. For pursuit methodology, see `general/pursuit-methodology.md`.

## Checklist

### Commercial Model

- [ ] **[Critical]** Is the ownership model explicitly defined? (Provider owns: hardware, hypervisor licensing, facility contracts. Customer owns: nothing -- consumes as a service. Clearly delineate what is included vs excluded.)
- [ ] **[Critical]** Is the pricing unit defined? (Per-VM/month, per-vCPU/month, per-TB/month, fixed monthly fee, tiered by environment, consumption-based with metering) The pricing unit affects architecture decisions -- per-VM pricing discourages many small VMs.
- [ ] **[Critical]** Is the contract duration aligned with hardware amortization? (3-year hardware lifecycle = minimum 3-year contract. 5-year = 5-year. Shorter contracts require higher monthly pricing to recover hardware investment.)
- [ ] **[Critical]** Is the hardware refresh strategy defined? (Provider refreshes on a cycle -- 3 or 5 years. Customer gets current-generation hardware without capital outlay. Refresh cost is built into the monthly service fee.)
- [ ] **[Recommended]** Are capital offsets documented? (Existing customer hardware buyback, vendor trade-in programs, lease termination savings, avoided license renewals) These reduce the provider's net capital investment and can improve the commercial model.
- [ ] **[Recommended]** Is the CapEx-to-OpEx value proposition articulated for the customer? (Customer eliminates: hardware procurement cycles, depreciation management, technology refresh planning, facility contracts, hardware disposal. Customer gains: predictable monthly cost, technology currency, operational simplicity.)
- [ ] **[Recommended]** Is vendor deal registration completed for major hardware/software procurement? (Nutanix, Dell, HPE, Cisco -- partner deal registration provides procurement discounts that materially affect the commercial model. First to register typically gets the credit. Time-sensitive.)
- [ ] **[Optional]** Is a comparable engagement referenced? (Prior as-a-service deals with similar scope, customer size, and platform. Validates pricing model and operational assumptions.)

### Facility Strategy

- [ ] **[Critical]** Is the facility ownership model defined? (Provider-owned datacenter, provider-leased colo, customer datacenter with provider equipment, or hybrid) Each has different cost structures and lead times.
- [ ] **[Critical]** If provider-leased colo, are lease terms aligned with customer contract duration? (Provider takes colo lease risk. If customer terminates early, provider is stuck with facility costs.)
- [ ] **[Recommended]** Is facility procurement lead time factored into the project timeline? (New colo contracts: 3-6 months. Provider-owned buildout: 6-18 months. This is often the critical path.)
- [ ] **[Recommended]** Is the site strategy defined? (1:1 mapping from customer sites, consolidated to fewer provider sites, or greenfield) Consolidation saves facility costs but adds migration complexity and may violate data residency requirements.

### Transition (Customer-Owned to Provider-Owned)

- [ ] **[Critical]** Is the asset transfer or replacement plan defined? (Does the provider buy existing customer hardware, or procure new hardware and the customer disposes of old? Or does the provider lease-back existing customer hardware during transition?)
- [ ] **[Critical]** Is the transition timeline defined? (When does the customer stop paying CapEx and start paying OpEx? Is there an overlap period where both models run?)
- [ ] **[Recommended]** Are hardware buyback/trade-in programs engaged? (Dell Financial Services, HPE Financial Services, Nutanix trade-in -- buyback value decreases with hardware age. Timing matters.)
- [ ] **[Recommended]** Is license transfer or replacement planned? (VMware licenses may not transfer to provider-owned hardware. Nutanix licenses may need re-procurement under provider's agreement. Microsoft SPLA may apply instead of customer's EA.)
- [ ] **[Optional]** Is a managed transition fee modeled? (One-time project cost for migration + ongoing monthly service fee. Some engagements bundle migration cost into the monthly fee over the contract term.)

### Operational Boundaries

- [ ] **[Critical]** Is the provider's operational scope explicitly defined? (Infrastructure only -- compute, storage, network, hypervisor, backup, patching, monitoring? Or does it extend to OS, middleware, database, application?) The most common dispute in as-a-service contracts is scope ambiguity.
- [ ] **[Critical]** Are application-level responsibilities clearly assigned to the customer? (Application deployment, application monitoring, application patching, application troubleshooting, application performance -- if the provider does not manage applications, this must be explicit.)
- [ ] **[Recommended]** Is the escalation path defined for issues that span provider and customer scope? (Infrastructure issue causing application impact -- who diagnoses, who fixes, what is the SLA?)
- [ ] **[Recommended]** Is the customer's retained IT team sized for their remaining responsibilities? (Customers sometimes reduce IT staff assuming the provider handles everything. If applications remain customer-managed, the customer needs application operations staff.)

### Risk

- [ ] **[Recommended]** Is the provider's capital exposure quantified? (Total hardware + licensing + facility investment. What is the breakeven point against monthly service revenue?)
- [ ] **[Recommended]** Is early termination modeled? (If customer terminates at year 2 of a 5-year contract, what is the provider's unrecovered capital? Are termination penalties sufficient?)
- [ ] **[Optional]** Is technology obsolescence risk addressed? (Provider owns hardware -- if technology shifts mid-contract (e.g., customer moves to public cloud), provider holds depreciating assets.)

## Why This Matters

The as-a-service model is increasingly common for on-premises infrastructure. Customers want public-cloud-like consumption (OpEx, no hardware ownership, predictable costs) without moving to public cloud (data residency, latency, regulatory, or cost reasons). For the provider, it creates long-term revenue stickiness but requires significant capital investment.

The most common failure: **underestimating the capital commitment.** The provider must procure hardware, licensing, and facility capacity before revenue begins. If the customer delays or reduces scope, the provider absorbs the cost. Hardware buyback programs and vendor deal registration are critical to managing this exposure.

The second most common failure: **ambiguous operational scope.** "We'll run your infrastructure" means different things to different stakeholders. If the contract says "infrastructure management" but the customer expects application support, the provider delivers at a loss. The operational boundary must be explicit, documented, and agreed before contract signature.

## Common Decisions (ADR Triggers)

- **Ownership model** -- provider-owned vs customer-owned vs hybrid; determines capital structure, tax treatment, and contract structure
- **Facility strategy** -- provider facility vs customer facility vs colo; determines lead time, cost structure, and data residency compliance
- **Pricing model** -- per-VM, per-core, fixed fee, consumption-based; affects architecture decisions and customer behavior
- **Contract duration** -- must align with hardware amortization; shorter contracts = higher monthly fee or provider capital risk
- **Operational boundary** -- infrastructure-only vs full-stack; the single most important scope decision in the contract
- **Hardware refresh cycle** -- 3-year vs 5-year; affects pricing, technology currency, and contract renewal dynamics

## See Also

- `general/managed-services-scoping.md` -- Managed services operational and commercial scoping
- `general/facility-lifecycle.md` -- Facility lease management and datacenter exit planning
- `general/hardware-asset-disposition.md` -- Hardware buyback, trade-in, and disposal
- `general/pursuit-methodology.md` -- Pursuit process and commercial framing
- `general/cost-onprem.md` -- On-premises cost modeling
