# Colocation Facility Constraints for Infrastructure Migration

## Scope

This file covers **colocation facility constraints that must be addressed when planning hardware deployments, migrations, or expansions** in third-party data centers (Equinix, NTT, Digital Realty, CyrusOne, QTS, and similar providers). These constraints are frequently overlooked during architecture design and can introduce weeks or months of delay if not identified early. Applies to any project involving physical hardware in a colocation facility, whether greenfield deployment, migration from one colo to another, or expansion within an existing facility. For facility lifecycle management, see `general/facility-lifecycle.md`. For physical server assessment, see `general/physical-server-scope.md`.

## Checklist

- [ ] **[Critical]** Has available rack space been confirmed with the colocation provider for staging new hardware alongside existing equipment, including the number of racks, their power density (kW per rack), and whether contiguous placement is available within the same cage or suite?
- [ ] **[Critical]** Has power capacity been validated for temporary dual-stack operation -- both old and new hardware running simultaneously during migration -- including total amperage per rack (typically 20A-30A per circuit at 208V), redundant power feeds (A+B), and facility-level power availability (some facilities are fully subscribed)?
- [ ] **[Critical]** Has cooling capacity been assessed for the additional heat load during dual-stack operation, including confirmation that the facility's cooling infrastructure (CRAH/CRAC units, hot/cold aisle containment) can handle the peak combined load without exceeding temperature thresholds (ASHRAE A1: 18-27C intake)?
- [ ] **[Critical]** Have cross-connect provisioning lead times been factored into the project timeline -- typical lead times range from 5-15 business days for intra-facility fiber cross-connects and 30-90 days for new carrier circuit installations or inter-facility connections?
- [ ] **[Critical]** Are facility access procedures documented and integrated into the migration plan, including badge/escort requirements, access request lead times (24-72 hours for some facilities), after-hours access policies, and authorized personnel lists?
- [ ] **[Critical]** Has the colocation contract been reviewed for provisions related to the migration, including temporary capacity increases, early termination clauses, and minimum commitment periods?
- [ ] **[Recommended]** Has the colocation contract been reviewed for provisions to temporarily increase capacity (additional racks, power circuits) during migration, including amendment lead times (2-6 weeks typical), minimum commitment periods, and early termination clauses for temporary space?
- [ ] **[Recommended]** Is a cable management and network patching plan documented for the transition period, covering patch panel allocation, fiber/copper runs between old and new racks, labeling standards, and a cutover sequence that maintains connectivity throughout migration?
- [ ] **[Recommended]** Have hardware delivery logistics been coordinated with the facility, including loading dock scheduling (some facilities require 24-48 hour advance booking), freight elevator availability, cage access for large deliveries, and staging area for unpacking and inventory?
- [ ] **[Recommended]** Are decommission procedures defined for returning or removing old hardware, including data destruction requirements (NIST 800-88 media sanitization), rack teardown scheduling, cable removal, provider notification for power/space release, and asset disposal or return logistics?
- [ ] **[Recommended]** Have remote hands service requirements and costs been estimated for tasks that do not justify sending on-site staff, including hourly rates (typically $75-$200/hour), response time SLAs (15 minutes to 4 hours depending on tier), and scope of services available (cabling, power cycling, visual inspections, hardware swaps)?
- [ ] **[Recommended]** Have colocation provider SLAs been reviewed for the migration period, including power uptime guarantees (99.99% or higher for Tier III+), cooling SLAs, network availability for provider-supplied connectivity, and maintenance window notifications that could conflict with migration activities?
- [ ] **[Recommended]** Is meet-me room (MMR) access and Internet Exchange (IX) connectivity planned, including available MMR ports, demarcation point locations, carrier presence verification, IX membership requirements and fees, and peering policy decisions (open vs selective)?
- [ ] **[Optional]** Has a secondary or overflow facility been identified in case the primary colocation cannot accommodate temporary dual-stack capacity, including inter-facility dark fiber or wavelength availability and latency implications?
- [ ] **[Optional]** Are environmental monitoring extensions planned for the new racks during migration, including temperature/humidity sensors, cabinet door sensors, and integration with existing DCIM or monitoring platforms?
- [ ] **[Optional]** Has a physical security audit of the colocation been conducted or reviewed, including SOC 2 Type II compliance, mantrap entry, biometric access controls, CCTV coverage, and visitor escort policies?

## Why This Matters

Colocation facility constraints are the most common source of "invisible" project delays because they involve physical-world lead times that cannot be compressed with additional engineering effort. A cross-connect that takes 10 business days to provision cannot be accelerated by working overtime. A facility that has no available power circuits requires either waiting for infrastructure upgrades (months) or finding alternative space. During migrations, the dual-stack period -- where both old and new environments must run simultaneously -- doubles power and cooling requirements temporarily, and many colocation contracts do not include provisions for temporary capacity increases. Hardware delivery to a colocation facility is not the same as delivery to an office: loading docks may be shared across multiple tenants, freight elevators have scheduled availability, and cage access may require escort by facility staff. Remote hands costs can escalate quickly during intensive migration periods if on-site staff presence is not planned, as even simple tasks like power-cycling a server or reseating a cable incur per-incident fees. Failing to account for these constraints during the architecture phase results in migration timelines that are technically correct but operationally impossible.

## Common Decisions (ADR Triggers)

- **Same-facility migration vs facility change** -- Migrating within the same colocation facility (rack-to-rack or cage-to-cage) eliminates WAN latency concerns and allows direct fiber cross-connects between old and new environments, but is constrained by facility capacity. Changing facilities provides an opportunity to renegotiate contracts and adopt better infrastructure but introduces inter-facility connectivity complexity and longer dual-stack periods. Same-facility is strongly preferred when capacity exists.
- **Remote hands vs dedicated on-site staff during migration** -- Remote hands (provider-supplied technicians) are cost-effective for occasional tasks ($75-$200/hour, billed per incident) but introduce response time delays (15 min to 4 hours) and may lack familiarity with your specific hardware. Dedicated on-site staff (your own or contracted) cost more in travel and labor but provide immediate response and continuity. For migrations spanning more than 2-3 days of active rack work, dedicated on-site presence is typically more cost-effective and reliable.
- **Direct carrier cross-connects vs meet-me room patching** -- Direct cross-connects to a carrier's cage are simpler and lower-latency but lock you to that carrier. Meet-me room patching allows access to multiple carriers and IX connections from a single demarcation point but adds a patch panel hop. For redundancy, most deployments use cross-connects to at least two carriers via the MMR, with IX peering for high-traffic public-facing services.
- **Full rack vs partial rack (caged colo vs shared colo)** -- Full racks in a private cage provide maximum physical security, flexible power configurations, and unrestricted access but carry higher costs ($800-$2500+/month per rack depending on market and power). Shared or partial-rack colocation is cheaper but limits power density, restricts physical access scheduling, and may impose neighbor noise or vibration concerns. Migrations are significantly easier with full-rack private cage access.
- **Power redundancy: 2N vs N+1 vs single feed** -- 2N (fully redundant, dual independent power paths) provides the highest availability and is standard for production workloads in Tier III+ facilities. N+1 (single path with redundant components) is cheaper and sufficient for non-critical or dev/staging workloads. Single feed is only appropriate for equipment that tolerates brief outages. During migration, ensure new racks match or exceed the redundancy level of existing infrastructure.
- **Contract structure: committed vs burst capacity** -- Long-term committed capacity (1-3 year terms) provides the best per-unit pricing but requires accurate capacity forecasting. Burst or flex capacity provisions allow temporary increases during migrations but at premium pricing (20-50% above committed rates). Negotiating burst provisions into the base contract before migration begins is significantly cheaper than requesting ad-hoc capacity increases.

## Rack Space and Power Planning

| Consideration | Typical Values | Migration Impact |
|---|---|---|
| Standard rack height | 42U-48U | Plan for 30-36U usable after PDU, cable management, airflow |
| Power per rack (standard) | 4-8 kW | Verify sufficient for modern high-density servers (1-2 kW each) |
| Power per rack (high density) | 10-20+ kW | May require liquid cooling or rear-door heat exchangers |
| Single circuit capacity | 20A or 30A at 208V single-phase | 20A circuit = ~3.3 kW usable at 80% derating |
| Three-phase power | 30A at 208V three-phase | ~8.6 kW usable at 80% derating, more efficient for dense racks |
| Dual-stack overhead | 2x normal power/cooling | Budget for full overlap period, negotiate temporary circuits |
| Rack monthly cost | $800-$2500+ | Varies heavily by market (NoVA/Ashburn cheapest, NYC/SF premium) |

### Power Planning for Migration

During a migration, both old and new infrastructure must run concurrently. Plan power accordingly:

1. **Inventory existing power draw** -- Measure actual draw per rack via PDU metering, not rated capacity
2. **Estimate new hardware power requirements** -- Use vendor power calculators (Dell, HPE, Lenovo) for accurate per-server estimates
3. **Calculate total concurrent draw** -- Old + new must not exceed available circuits
4. **Request temporary circuits** from the provider if needed -- lead time is typically 2-4 weeks for additional circuits within an existing cage
5. **Plan power surrender schedule** -- As old racks are decommissioned, notify the provider to release circuits and reduce billing

## Cross-Connect and Connectivity Lead Times

| Connection Type | Typical Lead Time | Notes |
|---|---|---|
| Intra-facility copper cross-connect | 3-7 business days | Within same building, MMR to cage |
| Intra-facility fiber cross-connect | 5-15 business days | Single-mode LC/SC, verify MMR port availability first |
| Inter-facility dark fiber | 15-45 business days | Between buildings on same campus, requires strand availability |
| New carrier circuit (metro ethernet) | 30-60 business days | Carrier must have presence in facility or provision last-mile |
| New carrier circuit (wavelength/DWDM) | 45-90 business days | Long-haul or inter-market connectivity |
| IX port provisioning | 5-20 business days | Requires IX membership approval, port availability |
| Temporary migration cross-connect | 5-10 business days | Request removal scheduling at time of order to avoid orphaned connections |

**Key point:** Always order cross-connects as early as possible in the migration timeline. They are on the critical path and cannot be parallelized with other preparation work.

## Facility Access and Security Procedures

### Access Models by Provider

| Provider Type | Access Model | Typical Requirements |
|---|---|---|
| Premium (Equinix IBX, Digital Realty) | Badge access, 24/7, self-service for authorized personnel | Photo ID, background check, NDA, access request 24h in advance for new personnel |
| Standard (regional providers) | Escorted access during business hours, badge after-hours | Escort fee ($50-$100/visit), advance booking required |
| Shared colo | Scheduled access windows only | Reservation required, limited to 2-4 hour windows |

### Access Planning for Migration

- **Build the authorized personnel list early** -- adding new personnel can take 3-5 business days at some facilities
- **Book loading dock time** for hardware delivery -- 24-48 hours advance notice is standard
- **Coordinate with other tenants** if shared loading dock -- avoid conflicts during heavy delivery periods
- **Plan escort coverage** for contractors -- facility staff escorts may need to be pre-booked
- **Document after-hours access procedures** -- migration cutovers often happen on weekends or overnight

## Hardware Delivery and Staging Logistics

```
Vendor Ships Hardware
        |
        v
Loading Dock Receiving ───── Requires: dock scheduling (24-48h advance)
        |                           freight elevator booking
        v                           receiving contact on authorized list
Staging Area Unpacking ───── Requires: staging space (may be limited/shared)
        |                           inventory verification
        v                           asset tagging
Cage/Suite Transport ─────── Requires: cage access (badge + escort if needed)
        |                           cart or dolly availability
        v
Rack Mounting ────────────── Requires: rail kits, cage nuts, power cables
        |                           PDU port allocation
        v                           cable management plan
Cabling and Patching ─────── Requires: patch panel ports
        |                           labeled cables (both ends)
        v                           cross-connect completion
Power-On and Burn-In ─────── Requires: power circuit activation
        |                           IPMI/BMC network configuration
        v                           remote access verification
Production Ready
```

**Common pitfalls:**
- Hardware delivered to wrong dock or without advance scheduling sits in limbo
- Rail kits and power cables not ordered with servers (different SKUs, often forgotten)
- PDU outlets already fully allocated in existing racks
- Cage nuts and mounting hardware missing from rack kit
- Staging area too small for palletized server shipments

## Decommission Procedures

1. **Data destruction** -- All storage media must be sanitized per NIST 800-88 (Clear, Purge, or Destroy) before hardware leaves the facility. Maintain chain-of-custody documentation with serial numbers, sanitization method, and verification signatures.
2. **Cable removal** -- Remove all patch cables and label/bundle for reuse or disposal. Request cross-connect removal from the provider (typically 3-5 business day lead time, billed as a disconnect fee).
3. **Power release** -- Notify the provider of circuits to be released. Power circuits on committed contracts may continue to incur charges until the contract term ends or is amended.
4. **Rack teardown** -- Remove all equipment, shelves, and cable management. If returning rack space to the provider, schedule a walkthrough for condition verification.
5. **Asset disposition** -- Arrange for pickup by ITAD (IT Asset Disposition) vendor, internal logistics, or provider disposal service. Schedule loading dock and freight elevator for outbound shipment.
6. **Contract amendment** -- Submit formal request to reduce committed capacity. Lead time for contract amendments is typically 30-60 days, and reductions may not take effect until the next billing cycle.

## Remote Hands Service Tiers

| Service Level | Response Time | Typical Cost | Use Case |
|---|---|---|---|
| Standard | 2-4 hours | $75-$125/hour | Non-urgent: cable audits, visual inspections |
| Priority | 30-60 minutes | $125-$175/hour | Moderate urgency: power cycling, cable reseating |
| Emergency | 15-30 minutes | $175-$250/hour | Critical: hardware failure response, emergency power |
| Dedicated technician | On-site, continuous | $500-$1500/day | Extended migration work, multi-day deployments |

**Tips:**
- Pre-authorize specific remote hands tasks with the provider to avoid approval delays during incidents
- Maintain a detailed rack diagram and cable schedule that remote hands technicians can follow without verbal guidance
- Some providers offer "smart hands" (higher-skill technicians for OS-level or network tasks) at premium rates
- Budget for 20-40 remote hands hours during a typical multi-rack migration

## Colocation Provider Comparison Factors

When evaluating or comparing colocation providers, especially during a facility migration:

| Factor | What to Assess |
|--------|---------------|
| **Carrier neutrality** | Number of carriers in MMR, IX presence, ease of provisioning new circuits |
| **Power density options** | Maximum kW per rack, availability of high-density (15-20+ kW) racks |
| **Contract flexibility** | Minimum commitment terms, burst provisions, early termination penalties |
| **Geographic proximity** | Distance to users, other facilities, and cloud on-ramps |
| **Compliance certifications** | SOC 2 Type II, ISO 27001, PCI DSS, HIPAA, FedRAMP |
| **Interconnection ecosystem** | Cloud direct connect (AWS, Azure, GCP) availability within facility |
| **Expansion capacity** | Ability to add racks/cages without changing facilities |
| **Remote hands quality** | Response time SLAs, technician skill level, cost structure |

## Reference Resources

- **Uptime Institute Tier Standards**: [uptimeinstitute.com](https://uptimeinstitute.com/) -- Tier I-IV facility classification, redundancy requirements, and availability targets (Tier III: 99.982%, Tier IV: 99.995%)
- **ASHRAE TC 9.9**: Data center cooling and environmental guidelines -- recommended temperature ranges (18-27C intake), humidity guidelines, and allowable envelopes for server hardware
- **NIST SP 800-88 Rev. 1**: Guidelines for Media Sanitization -- required reading for decommission planning, defines Clear/Purge/Destroy methods by media type
- **TIA-942**: Data center infrastructure standard -- rack layout, cable pathway, and grounding/bonding requirements for colocation environments
- **PeeringDB**: [peeringdb.com](https://www.peeringdb.com/) -- verify IX presence and peering participants at specific facilities before signing contracts

## See Also

- `general/facility-lifecycle.md` -- Lease management, decommission, and handback
- `general/physical-server-scope.md` -- Physical server assessment and disposition
- `general/networking-physical.md` -- Physical network design
- `general/hardware-sizing.md` -- Hardware specification and capacity planning
