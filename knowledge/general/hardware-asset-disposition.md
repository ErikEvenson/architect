# Hardware Asset Disposition

## Scope

This file covers **end-of-life hardware disposition** -- lease buyback programs, residual value estimation, data sanitization, decommission logistics, and factoring asset disposition into commercial models. Applies when infrastructure is being replaced, consolidated, or exited. For hardware procurement and sizing, see `general/hardware-sizing.md`. For facility exit planning, see `general/facility-lifecycle.md`. For datacenter relocation, see `patterns/datacenter-relocation.md`.

## Checklist

### Inventory and Valuation

- [ ] **[Critical]** Is a complete hardware inventory available with make, model, serial number, age, and original purchase/lease terms? Buyback value depends on specific model and age -- a 2-year-old node is worth far more than a 5-year-old one.
- [ ] **[Critical]** Is the ownership model documented per asset? (Customer-owned, leased from vendor, leased from financial services company, provider-owned) Disposition options differ by ownership.
- [ ] **[Critical]** Is the lease status documented? (Active lease with buyback option, lease expired and owned, lease expiring with return obligation, month-to-month holdover) Some leases require hardware return regardless of preference.
- [ ] **[Recommended]** Is residual value estimated before engaging vendor financial services? Residual value decreases with age -- a rough estimate prevents wasted negotiation time on low-value hardware. Rule of thumb: 3-year-old enterprise servers retain 15-30% of original value; 5-year-old servers retain 5-15%.
- [ ] **[Recommended]** Are warranty and support contract statuses documented? Hardware under active warranty or support contract may have higher buyback value or different return logistics.
- [ ] **[Optional]** Are non-server assets inventoried? (Network switches, storage arrays, PDUs, cables, rack accessories) These have disposition value or return obligations too.

### Data Sanitization

- [ ] **[Critical]** Is a data sanitization standard selected and documented? Common standards: NIST SP 800-88 Rev 1 (Clear, Purge, Destroy), DoD 5220.22-M, customer-specific policy. The standard must be agreed with the data owner before sanitization begins.
- [ ] **[Critical]** Are all drives (HDD, SSD, NVMe) identified for sanitization? Include boot drives, cache drives, and capacity drives. Self-encrypting drives (SED) can be cryptographically erased.
- [ ] **[Critical]** Is a sanitization certificate generated for each drive? Document: drive serial number, sanitization method, date, operator. This is an audit artifact.
- [ ] **[Recommended]** Are drives that cannot be sanitized identified for physical destruction? SSDs with wear-leveling may not be fully sanitizable via software. Failed drives that cannot be erased must be physically destroyed (shredding, degaussing for HDDs).
- [ ] **[Recommended]** Is the sanitization process performed before hardware leaves the secure facility? Data should not leave the building on unsanitized drives.
- [ ] **[Optional]** Is a third-party sanitization/destruction service contracted for large volumes? Companies specializing in ITAD (IT Asset Disposition) provide certified sanitization with chain-of-custody documentation.

### Vendor Buyback Programs

- [ ] **[Critical]** Is the hardware vendor's financial services team engaged? Major vendors offer buyback programs: Dell Financial Services, HPE Financial Services, Lenovo Financial Services. Engage early -- buyback processes take 4-8 weeks from quote to payment.
- [ ] **[Critical]** Is the buyback timeline aligned with the decommission schedule? Hardware must be powered down, sanitized, and ready for pickup by the buyback date. Delays reduce value and may void quotes.
- [ ] **[Recommended]** Are buyback quotes obtained before finalizing commercial models? Buyback value is a capital offset in the business case. An unsigned estimate is not a commitment -- get a formal quote with validity period.
- [ ] **[Recommended]** Is the buyback scope maximized? Include all eligible hardware: servers, switches, storage controllers, expansion shelves. Vendors sometimes offer better per-unit pricing for larger volumes.
- [ ] **[Optional]** Are alternative disposition channels evaluated? (Secondary market resellers, auction, donation) In some cases, secondary market value exceeds vendor buyback -- especially for recently released models.

### Decommission Logistics

- [ ] **[Critical]** Is a decommission sequence defined that avoids disrupting workloads still running at the source? Don't power down racks that contain active VMs. Decommission follows migration waves, not precedes them.
- [ ] **[Critical]** Is physical removal coordinated with facility management? Rack removal may require loading dock scheduling, freight elevator access, and building management approval. Some colo facilities charge for decommission labor.
- [ ] **[Recommended]** Is the environmental/e-waste compliance documented for hardware that can't be sold or returned? Electronic waste regulations vary by jurisdiction (WEEE in EU, state laws in US). Ensure compliant disposal.
- [ ] **[Recommended]** Is cable and accessory removal included in the decommission plan? Abandoned cables and rack hardware complicate facility handback and may incur penalties.
- [ ] **[Optional]** Are rack elevation drawings updated to reflect decommissioned equipment? Keeping facility documentation current during progressive decommission prevents confusion.

### Commercial Integration

- [ ] **[Critical]** Is hardware disposition factored into the business case as a capital offset? Buyback value reduces the net investment for replacement hardware. Present as: "New hardware cost minus buyback credit = net capital required."
- [ ] **[Recommended]** Is the timing of buyback revenue aligned with new hardware procurement payment terms? Ideally, buyback payment arrives before or concurrent with new hardware invoices.
- [ ] **[Recommended]** Is the tax treatment of buyback revenue documented? In some jurisdictions, buyback revenue is treated as asset sale (capital gain/loss) which has different tax implications than operating expense. Engage finance.
- [ ] **[Optional]** Is a sensitivity analysis performed on buyback estimates? Buyback quotes have validity periods (typically 30-60 days) and actual value may differ from estimate. Model the business case at both estimated and conservative (50% of estimate) values.

## Why This Matters

Hardware asset disposition is the most commonly overlooked financial lever in infrastructure transformation projects. The typical failure modes:

1. **Forgotten buyback opportunity.** Old hardware sits in a cage for years after migration because no one planned for its removal. The buyback window closes and hardware that was worth six figures becomes e-waste.

2. **Data sanitization after the fact.** Hardware leaves the facility without sanitized drives. The data owner discovers this months later and the entire chain of custody is compromised. This is a compliance and reputational risk, not just an operational one.

3. **Lease return surprise.** The team assumes old hardware is owned outright, but it was leased. The lease requires return in good condition by a specific date. Missing the date triggers penalties or holdover charges.

4. **Decommission blocks facility exit.** The last migration wave completes but hardware removal takes 4 weeks and the lease expires in 2 weeks. Rushed decommission leads to left-behind equipment and lease penalty negotiations.

5. **Buyback not in the business case.** New hardware procurement is approved based on full capital cost. After the fact, someone realizes the old hardware had buyback value that could have offset 10-20% of the new procurement. The business case was sound either way, but the missed offset reduces ROI unnecessarily.

## Common Decisions (ADR Triggers)

- **Disposition channel** -- vendor buyback vs. secondary market vs. donation vs. destruction; depends on hardware age, model, and volume
- **Data sanitization standard** -- NIST 800-88 Clear vs. Purge vs. Destroy; depends on data classification and customer policy
- **Decommission timing** -- immediate after each migration wave vs. batch at end; affects facility costs and buyback value
- **Who performs sanitization** -- in-house team vs. ITAD vendor; depends on volume, tooling, and audit requirements
- **Lease vs. own for new hardware** -- informed by the experience of disposing the old hardware; leasing simplifies future disposition

## See Also

- `general/hardware-sizing.md` -- Hardware procurement and sizing for new infrastructure
- `general/facility-lifecycle.md` -- Facility lease management and exit planning
- `patterns/datacenter-relocation.md` -- Full datacenter relocation pattern
- `general/cost-onprem.md` -- On-premises cost modeling (includes hardware amortization)
