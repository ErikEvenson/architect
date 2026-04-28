# Dell APEX

## Scope

Dell APEX as-a-service and multicloud portfolio: APEX Cloud Platform (VCF-based), APEX Private Cloud, APEX Block Storage (PowerStore-as-a-service), APEX File Storage (PowerScale-as-a-service), APEX Backup Services, APEX Console for unified management, APEX Navigator for multicloud Kubernetes, and consumption model considerations (subscription, pay-per-use, committed capacity).

## Checklist

- [ ] [Critical] Is the correct APEX service tier selected for the workload? (APEX Cloud Platform for full VCF SDDC, APEX Private Cloud for general-purpose IaaS, APEX Block Storage for SAN workloads, APEX File Storage for NAS workloads, APEX Backup Services for SaaS data protection)
- [ ] [Critical] Is the APEX deployment model understood? (APEX infrastructure is Dell-owned and Dell-managed on customer premises or in a colocation facility -- customer provides power, cooling, network, and physical space but Dell retains hardware ownership)
- [ ] [Critical] Are the minimum commitment terms and capacity floors reviewed? (APEX typically requires 1-year or 3-year terms with minimum capacity commitments -- early termination may incur penalties)
- [ ] [Critical] Is the APEX Console configured with appropriate role-based access for ordering, provisioning, monitoring, and managing APEX services across the organization?
- [ ] [Critical] Is network connectivity between the APEX on-premises infrastructure and Dell's management plane (cloud-based) planned and secured? (APEX requires outbound HTTPS connectivity to Dell cloud services for management, telemetry, and billing)
- [ ] [Recommended] Is the APEX consumption model (elastic vs committed) analyzed against workload patterns? (committed capacity is cheaper per TB/core but inflexible, elastic allows bursting but at higher unit cost)
- [ ] [Recommended] Is APEX Cloud Platform evaluated against standalone VxRail/VCF for total cost of ownership? (APEX shifts CapEx to OpEx but may cost more over 3-5 years -- run a detailed TCO comparison including Dell management services value)
- [ ] [Recommended] Is APEX Navigator evaluated for multicloud Kubernetes if the organization runs workloads across on-premises and public cloud? (provides consistent Kubernetes management across Dell on-prem, AWS, Azure, and GCP)
- [ ] [Recommended] Are data sovereignty and compliance requirements validated against APEX management architecture? (telemetry and management data flows to Dell cloud -- verify this meets data residency and regulatory requirements)
- [ ] [Recommended] Is the APEX service level agreement (SLA) reviewed for uptime guarantees, response times, and remediation processes? (Dell manages hardware lifecycle, but customer retains OS, application, and data management responsibilities)
- [ ] [Recommended] Is the decommissioning process understood? (at end of term, Dell reclaims hardware -- data destruction procedures and transition planning must be agreed upon before deployment)
- [ ] [Optional] Is APEX Backup Services evaluated for Microsoft 365 and SaaS application backup as part of a broader data protection strategy?
- [ ] [Optional] Is APEX Managed Services (formerly Dell Technologies Services) layered on top of APEX infrastructure for customers who want Dell to manage the OS, hypervisor, and application layers?
- [ ] [Optional] Is the APEX ordering workflow tested end-to-end through the APEX Console, including capacity expansion and service modification requests?
- [ ] [Optional] Are chargeback/showback models designed to allocate APEX subscription costs to business units or projects within the organization?

## Why This Matters

APEX represents Dell's shift to as-a-service consumption, competing with HPE GreenLake and Lenovo TruScale. The key value proposition is CapEx-to-OpEx transformation with Dell handling hardware lifecycle management. However, APEX is not simply "renting hardware" -- the management model, ownership structure, and connectivity requirements fundamentally change how infrastructure is operated. The most common misconception is that APEX eliminates all infrastructure management; in reality, Dell manages the hardware layer while the customer retains full responsibility for software, applications, and data. Network connectivity to Dell's cloud management plane is mandatory and creates a dependency that must be evaluated for air-gapped or highly regulated environments. Minimum commitment terms mean APEX is not suitable for short-term or unpredictable workloads -- overcommitting capacity locks in cost while undercommitting limits scalability.

## Common Decisions (ADR Triggers)

- **APEX vs traditional purchase** -- as-a-service subscription (OpEx, Dell-managed hardware lifecycle) vs capital purchase (CapEx, customer-managed) based on financial model, operational maturity, and workload predictability
- **APEX Cloud Platform vs APEX Private Cloud** -- full VCF SDDC capabilities (NSX, SDDC Manager, Aria) vs simplified IaaS -- VCF adds network virtualization and automation but increases complexity
- **Consumption model** -- committed capacity (lower unit cost, fixed) vs elastic (higher unit cost, burst capability) vs hybrid (committed baseline + elastic burst) based on workload variability
- **Deployment location** -- customer datacenter (customer provides facility) vs colocation (APEX in colo, Dell or customer manages facility relationship) -- affects latency, data sovereignty, and operational model
- **Multicloud management** -- APEX Navigator for consistent Kubernetes across on-prem and cloud vs separate management tools per environment -- Navigator adds value for multi-cluster Kubernetes operations
- **Contract term** -- 1-year (flexibility, higher cost) vs 3-year (lower cost, longer commitment) -- align with organizational budget cycles and workload lifespan
- **Management boundary** -- Dell manages hardware only vs Dell manages through hypervisor layer vs Dell manages full stack (Managed Services addon) -- each tier changes operational responsibility and cost

## Reference Links

- [Dell APEX Overview](https://www.dell.com/en-us/dt/apex/index.htm) -- APEX portfolio overview and service descriptions
- [APEX Cloud Platform Documentation](https://infohub.delltechnologies.com/en-us/t/apex-cloud-platform/) -- Dell InfoHub with deployment and administration guides
- [APEX Console](https://www.dell.com/en-us/dt/apex/apex-console.htm) -- unified management console for all APEX services
- [APEX Navigator for Multicloud](https://www.dell.com/en-us/dt/apex/apex-navigator.htm) -- multicloud Kubernetes management with APEX
- [Dell APEX Pricing and Packaging](https://www.dell.com/en-us/dt/apex/index.htm) -- subscription options and service tiers
- [APEX Cloud Platform for VCF Reference Architecture](https://infohub.delltechnologies.com/en-us/t/apex-cloud-platform/) -- validated designs for APEX Cloud Platform deployments

## See Also

- `providers/dell/vxrail.md` -- VxRail HCI (underlies APEX Cloud Platform)
- `providers/dell/powerstore.md` -- PowerStore (underlies APEX Block Storage)
- `providers/dell/powerscale.md` -- PowerScale (underlies APEX File Storage)
- `providers/vmware/vcf-sddc-manager.md` -- VCF lifecycle management
- `patterns/private-cloud-as-a-service.md` -- as-a-service infrastructure patterns
- `patterns/dell-hybrid-cloud.md` -- Dell-anchored hybrid cloud pattern: APEX Console as cross-environment control plane, Dell-Microsoft alliance, PowerProtect / Cyber Recovery, CloudIQ
- `patterns/hybrid-cloud.md` -- generic vendor-neutral hybrid cloud pattern (the layer above)
- `general/cost.md` -- cost modeling and CapEx vs OpEx considerations
- `general/finops.md` -- FinOps practices for consumption-based infrastructure
