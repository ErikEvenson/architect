# HPE GreenLake Cloud Services

## Scope

HPE GreenLake cloud platform: consumption-based infrastructure, GreenLake Central management, hybrid cloud services, on-premises cloud experience, and service catalog. Covers deployment models, metering and billing, workload services (compute, storage, containers, VDI, ML), and integration with existing datacenter infrastructure.

## Checklist

- [ ] [Critical] Is the GreenLake consumption model understood by all stakeholders? (HPE owns and manages hardware on-premises, customer pays based on metered usage with a committed buffer capacity -- this changes CapEx to OpEx but requires minimum commitment periods, typically 3-5 years)
- [ ] [Critical] Is the buffer capacity (headroom) sized correctly? (GreenLake pre-deploys capacity above the committed baseline to handle burst demand -- undersized buffer causes provisioning delays, oversized buffer increases minimum commitment costs)
- [ ] [Critical] Are data sovereignty and physical security requirements compatible with the GreenLake model? (HPE-owned hardware resides in the customer's datacenter but HPE retains asset ownership -- verify compliance with data residency regulations, facility access policies, and audit requirements)
- [ ] [Critical] Is GreenLake Central (or the GreenLake platform portal) configured for unified management, cost visibility, and compliance reporting across all GreenLake services?
- [ ] [Critical] Is the network connectivity between on-premises GreenLake infrastructure and HPE cloud management plane documented and approved by security? (GreenLake requires outbound connectivity to HPE for metering, management, and support -- firewall rules, proxy configuration, and data-in-transit encryption must be reviewed)
- [ ] [Recommended] Are GreenLake workload services selected based on the actual need? (Compute Ops Management for server fleet, Data Services Cloud Console for storage, Private Cloud Enterprise for full VMware private cloud, Containers for managed Kubernetes)
- [ ] [Recommended] Is the metering and billing model validated with finance? (GreenLake meters by compute cores, storage TB, or VM instances depending on the service -- understand the billing unit, overcommit pricing, and true-up cycle)
- [ ] [Recommended] Is the GreenLake SLA aligned with business requirements? (GreenLake offers availability SLAs for managed services -- verify SLA covers the full stack including hardware replacement time, not just software uptime)
- [ ] [Recommended] Is the exit strategy documented? (GreenLake contracts have minimum terms -- understand early termination costs, data migration obligations, and hardware return logistics at contract end)
- [ ] [Recommended] Is GreenLake for Private Cloud Enterprise evaluated if the goal is a VMware-based private cloud with cloud-like operations? (includes vSphere, vCenter, and optional NSX/vSAN managed by HPE with consumption billing)
- [ ] [Recommended] Is GreenLake for Containers (managed Kubernetes via HPE Ezmeral) evaluated for containerized workloads, with cluster lifecycle management and integration with existing CI/CD pipelines?
- [ ] [Optional] Is GreenLake for ML Ops evaluated for machine learning workloads that require GPU compute with consumption-based scaling?
- [ ] [Optional] Is GreenLake for VDI (Citrix or VMware Horizon on GreenLake) evaluated for virtual desktop workloads that benefit from on-premises performance with cloud-like billing?
- [ ] [Optional] Is GreenLake integrated with public cloud providers (AWS Outposts, Azure Arc) for a multi-cloud control plane with unified policy management?
- [ ] [Optional] Is HPE Financial Services engaged for custom financing structures (lease-to-own, technology refresh cycles, asset return programs) that complement the GreenLake subscription model?

## Why This Matters

GreenLake is HPE's strategic direction for delivering infrastructure as a service in customer datacenters. It shifts the procurement model from CapEx hardware purchases to OpEx consumption, but this shift has significant implications that are often underestimated. The minimum commitment period (typically 3-5 years) with pre-deployed buffer capacity means organizations are committing to a vendor relationship that is difficult to exit. Metering is based on peak usage, not average, which can surprise finance teams accustomed to fixed infrastructure costs. The management plane requires persistent connectivity to HPE's cloud, which conflicts with some air-gapped or highly regulated environments. Organizations considering GreenLake must involve procurement, finance, security, and facilities teams early because the model crosses traditional organizational boundaries. The value proposition is strongest when an organization wants cloud-like agility and consumption economics but cannot or will not move workloads to public cloud due to data sovereignty, latency, or compliance constraints.

## Common Decisions (ADR Triggers)

- **Delivery model** -- GreenLake consumption (OpEx, HPE-managed) vs traditional purchase (CapEx, self-managed) vs lease (CapEx-like with refresh cycle)
- **Service tier** -- GreenLake Compute Ops Management (server management only) vs Private Cloud Enterprise (full managed private cloud) vs individual workload services
- **Kubernetes platform** -- GreenLake for Containers (HPE Ezmeral managed K8s) vs self-managed Kubernetes on GreenLake compute vs public cloud Kubernetes
- **Storage service** -- GreenLake for Block Storage (Alletra-based) vs GreenLake for File Storage vs traditional array purchase with GreenLake billing overlay
- **Hybrid cloud integration** -- GreenLake as standalone private cloud vs GreenLake + AWS/Azure hybrid with unified management via GreenLake Central
- **Contract structure** -- standard GreenLake terms (3-5 year) vs custom HPE Financial Services agreement with technology refresh options
- **Management boundary** -- HPE fully managed (HPE operates the infrastructure) vs customer-managed with GreenLake billing (customer operates, HPE bills on consumption)

## Reference Links

- [HPE GreenLake Platform Overview](https://www.hpe.com/us/en/greenlake.html) -- service catalog, consumption model, and platform capabilities
- [HPE GreenLake Central User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00092451en_us) -- unified dashboard for cost, compliance, and resource management
- [HPE GreenLake for Private Cloud Enterprise](https://www.hpe.com/us/en/greenlake/private-cloud-enterprise.html) -- managed VMware private cloud with consumption billing
- [HPE GreenLake for Containers](https://www.hpe.com/us/en/greenlake/containers.html) -- managed Kubernetes service based on HPE Ezmeral
- [HPE GreenLake Metering and Billing](https://support.hpe.com/hpesc/public/docDisplay?docId=a00092453en_us) -- metering methodology, billing units, and consumption reporting
- [HPE GreenLake SLA Documentation](https://www.hpe.com/us/en/greenlake/service-descriptions.html) -- service-level agreements, response times, and availability guarantees

## See Also

- `providers/hpe/proliant.md` -- ProLiant servers that underpin GreenLake compute services
- `providers/hpe/synergy.md` -- Synergy composable infrastructure available via GreenLake
- `providers/hpe/nimble-alletra.md` -- Nimble/Alletra storage arrays available via GreenLake
- `general/cost.md` -- general cost optimization patterns
- `patterns/private-cloud-as-a-service.md` -- private cloud as-a-service delivery pattern
- `patterns/hpe-hybrid-cloud.md` -- HPE-anchored hybrid cloud pattern: GreenLake-to-AWS/Azure/GCP integration, Aruba SD-WAN backbone, Azure Arc, identity bridging, Zerto/Morpheus/OpsRamp
- `patterns/hybrid-cloud.md` -- generic vendor-neutral hybrid cloud pattern (the layer above)
