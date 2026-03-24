# Azure Commercial Programs

## Scope

This file covers Microsoft Azure commercial and procurement programs that affect architecture decisions: Enterprise Agreement (EA) structure and pricing, Microsoft Azure Consumption Commitment (MACC), Reserved Instances and Savings Plans, Azure Hybrid Benefit (AHB), Extended Security Updates (ESUs), Engineering Support Funding (ESF) and ECIF, partner programs (CSP vs EA), and co-sell incentives. These programs directly influence which services are selected, how workloads are deployed, and how contracts are structured. For Azure compute sizing and SKU selection, see `providers/azure/compute.md`. For VMware licensing (including BYOL to hyperscalers), see `providers/vmware/licensing.md`. For Nutanix NC2 on Azure, see `providers/nutanix/infrastructure.md`.

## Checklist

### Enterprise Agreement (EA)

- [ ] **[Critical]** Is the EA enrollment structure documented — enrollment number, departments, accounts, subscriptions — and do all Azure subscriptions roll up correctly for billing and MACC tracking?
- [ ] **[Critical]** Is the EA renewal date identified and tracked? EA terms are typically 3 years, and renewal negotiations should begin 6-12 months in advance to avoid auto-renewal at unfavorable terms.
- [ ] **[Critical]** Has the impact of EA pricing tier elimination (effective November 1, 2025) been assessed? All EA customers now pay Level A pricing for online services regardless of volume — organizations previously at Levels B, C, or D face increases of approximately 6%, 9%, or 12% respectively.
- [ ] **[Recommended]** Is the Azure Prepayment (formerly Monetary Commitment) sized appropriately? Over-commitment locks up capital; under-commitment results in overage charges billed at pay-as-you-go rates.
- [ ] **[Recommended]** Has the EA vs CSP decision been evaluated for each workload? CSP now offers 3-year terms and pricing parity, with greater flexibility to adjust license counts monthly.

### Microsoft Azure Consumption Commitment (MACC)

- [ ] **[Critical]** Is the MACC balance, start date, end date, and remaining commitment tracked in Cost Management + Billing? Architecture decisions should prioritize MACC-eligible services when the commitment deadline is approaching.
- [ ] **[Critical]** Are marketplace purchases made through the Azure portal (not directly via credit card on marketplace.microsoft.com) to ensure they count toward MACC?
- [ ] **[Critical]** For partner-managed services (NC2 on Azure, Azure VMware Solution), has MACC eligibility been confirmed? NC2 Azure infrastructure counts toward MACC, but Nutanix software licenses purchased separately from the marketplace may not. AVS host charges count toward MACC.
- [ ] **[Recommended]** Are all Azure benefit-eligible marketplace offers identified using the "Azure benefit eligible" badge in the Azure portal marketplace filter?
- [ ] **[Recommended]** Is the MACC burn-down rate projected to ensure the commitment is fully consumed before expiration? Unspent MACC is forfeited.

### Reserved Instances (RIs)

- [ ] **[Critical]** Are Reserved Instances evaluated for all steady-state compute workloads? RIs offer up to 72% savings over pay-as-you-go for 3-year terms (up to 40% for 1-year terms).
- [ ] **[Critical]** Is instance size flexibility enabled? RI discounts can apply to other VMs in the same size group and region, reducing the risk of stranded reservations.
- [ ] **[Recommended]** Is the RI scope set appropriately — single subscription, resource group, shared across enrollment, or management group — to maximize utilization?
- [ ] **[Recommended]** Are RI exchange and cancellation policies understood? Exchanges are permitted indefinitely (the planned January 2024 end date was extended indefinitely) with prorated refunds applied to new reservations.
- [ ] **[Optional]** Is RI utilization monitored and right-sized? Under-utilized reservations should be exchanged for better-fitting SKUs.

### Savings Plans

- [ ] **[Critical]** Are Azure Savings Plans for Compute evaluated for dynamic or evolving workloads? Savings Plans offer up to 65% savings with an hourly spend commitment for 1-year or 3-year terms.
- [ ] **[Critical]** Is the relationship between RIs and Savings Plans understood? RIs are applied first (higher discount, less flexible), then Savings Plans cover remaining eligible usage, then pay-as-you-go rates apply.
- [ ] **[Recommended]** Is the hourly commitment amount right-sized based on historical usage? Unused commitment in any hour is forfeited — it does not roll over.
- [ ] **[Recommended]** Are all eligible services identified? Savings Plans cover VMs, Azure Virtual Desktop, Azure Kubernetes Service, Azure Red Hat OpenShift, Azure Machine Learning compute, and other compute services. They do not cover Windows software costs (only the compute portion).

### Azure Hybrid Benefit (AHB)

- [ ] **[Critical]** Are existing Windows Server and SQL Server licenses with active Software Assurance or qualifying subscriptions identified for Azure Hybrid Benefit? AHB eliminates the OS/SQL license cost on Azure VMs, stacking with RI or Savings Plan discounts.
- [ ] **[Critical]** Is the 180-day dual-use right understood? AHB allows Windows Server and SQL Server licenses to run simultaneously on-premises and in Azure during migration, providing a migration overlap window.
- [ ] **[Critical]** For SQL Server workloads, has AHB been evaluated across deployment targets — Azure VMs, Azure SQL Database, Azure SQL Managed Instance, and Azure VMware Solution — since AHB applies to all of these?
- [ ] **[Recommended]** Are Extended Security Updates (ESUs) factored into migration planning? Windows Server and SQL Server workloads running in Azure receive free ESUs, saving up to 76% compared to purchasing ESU licenses for on-premises deployments.
- [ ] **[Recommended]** Is AHB applied at the resource level in Azure and tracked for compliance? Licenses used for AHB cannot be simultaneously used on-premises (except during the 180-day migration window).
- [ ] **[Optional]** Has the Windows Server 2025 Azure Arc pay-as-you-go licensing option been evaluated as an alternative to traditional license purchasing for hybrid scenarios?

### Engineering Support Funding (ESF) and ECIF

- [ ] **[Recommended]** Has Engineering Support Funding (ESF) eligibility been confirmed with the Microsoft account team? ESF provides funded technical resources from Microsoft to assist with complex deployments, migrations, and architecture reviews.
- [ ] **[Recommended]** Are End Customer Investment Funds (ECIF) being leveraged? ECIF funds a Microsoft partner to cover part of the solution implementation cost for cloud adoption and digital transformation projects.
- [ ] **[Recommended]** Is Azure Accelerate funding evaluated for migration and modernization projects? Azure Accelerate provides expert resources and financial investments to reduce barriers to cloud and AI adoption.
- [ ] **[Optional]** Are Advanced Specialization designations pursued by the delivery partner? Advanced Specializations unlock the highest-value Microsoft funding and co-sell incentives.

### Partner Programs and Co-Sell

- [ ] **[Recommended]** Is the CSP vs EA decision documented as an ADR? CSP offers monthly flexibility and partner-managed billing; EA offers direct Microsoft relationship and Azure Prepayment. With the November 2025 EA tier elimination, CSP is increasingly competitive.
- [ ] **[Recommended]** For CSP engagements, does the partner meet the direct-bill threshold ($1M trailing 12-month revenue) or operate as an indirect reseller ($25K TTM per solution area)?
- [ ] **[Optional]** Is co-sell status leveraged for marketplace offers? Microsoft co-sell eligible solutions receive sales team engagement and marketplace visibility.
- [ ] **[Optional]** Are Partner Earned Credit (PEC) implications considered? PEC provides partners with a credit for managing Azure services, which can reduce the customer's effective cost in CSP arrangements.

## Why This Matters

Azure commercial programs directly influence architecture decisions in ways that go beyond simple cost optimization. A MACC commitment nearing expiration can shift service selection toward MACC-eligible marketplace offers (such as NC2 on Azure or third-party solutions). The elimination of EA pricing tiers in November 2025 reset pricing for large enterprises, making CSP a viable alternative for organizations that previously relied on Level C or D discounts. Reserved Instances and Savings Plans stack with Azure Hybrid Benefit, and choosing the right combination for a workload can reduce compute costs by 80% or more. Engineering support funding and ECIF can subsidize migration costs but must be requested proactively through the Microsoft account team or partner. Failing to account for these programs during architecture design leads to missed savings, forfeited commitments, and suboptimal procurement structures.

## Common Decisions (ADR Triggers)

- **EA vs CSP** -- EA (direct Microsoft relationship, Azure Prepayment, single invoice) vs CSP (partner-managed billing, monthly license flexibility, partner support). Post-November 2025, EA lost volume pricing tiers for online services, reducing its cost advantage for large deployments.
- **Reserved Instances vs Savings Plans vs Pay-As-You-Go** -- RIs (up to 72% savings, specific VM family/region, best for stable workloads) vs Savings Plans (up to 65% savings, flexible across regions/sizes/services, best for dynamic workloads) vs PAYG (no commitment, highest cost, best for unpredictable or short-lived workloads). RIs and Savings Plans can be combined.
- **RI term length** -- 1-year (lower savings, more flexibility to change direction) vs 3-year (maximum savings, longer lock-in risk if workload changes).
- **RI payment model** -- All upfront (lowest total cost) vs monthly (preserves cash flow, same total discount).
- **Azure Hybrid Benefit scope** -- Apply AHB to Azure VMs (IaaS) vs Azure SQL Managed Instance (PaaS) vs Azure VMware Solution (hybrid). License inventory determines what can be covered.
- **MACC burn-down strategy** -- Organic consumption vs accelerated marketplace purchases vs partner-managed services (NC2, AVS) to meet commitment deadlines.
- **ESF/ECIF utilization** -- Apply funding to migration execution vs architecture review vs proof-of-concept development. Funding is time-limited and must be planned into project timelines.

## Version Notes

| Change | Previous | Current |
|---|---|---|
| EA pricing tiers | Levels A-D based on volume (500-15,000+ seats) | All customers at Level A pricing (effective November 1, 2025) |
| RI exchange policy | Planned end January 2024 | Extended indefinitely |
| CSP direct-bill threshold | Lower threshold | $1M trailing 12-month revenue (FY26) |
| Windows Server licensing | Traditional license purchase only | Azure Arc pay-as-you-go option (Windows Server 2025+) |
| VMware BYOL to hyperscalers | Hyperscaler-provided licensing only | BYOL permitted (effective November 1, 2025) |

## See Also

- [EA billing administration](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/ea-portal-get-started) -- Azure portal management for Enterprise Agreement enrollments
- [MACC overview and tracking](https://learn.microsoft.com/en-us/azure/cost-management-billing/benefits/macc/track-consumption-commitment) -- Track Azure Consumption Commitment balance and eligible spend
- [Azure Consumption Commitment Benefit](https://learn.microsoft.com/en-us/marketplace/azure-consumption-commitment-benefit) -- Marketplace purchases eligible for MACC
- [Azure Reserved VM Instances pricing](https://azure.microsoft.com/en-us/pricing/reserved-vm-instances/) -- RI pricing, terms, and savings calculator
- [Azure Savings Plans for Compute](https://azure.microsoft.com/en-us/pricing/offers/savings-plan-compute/) -- Savings Plan pricing and eligible services
- [Azure Hybrid Benefit for Windows Server](https://learn.microsoft.com/en-us/windows-server/get-started/azure-hybrid-benefit) -- License portability and ESU benefits
- [Azure Hybrid Benefit for SQL Server](https://learn.microsoft.com/en-us/azure/azure-sql/azure-hybrid-benefit?view=azuresql) -- SQL license portability to Azure SQL services
- [Microsoft partner incentives guide](https://www.aicloudpartners.com/guides/microsoft-partner-incentives.html) -- FY26 partner incentive programs and co-sell overview
- [EA pricing tier elimination](https://redresscompliance.com/microsoft-ea-pricing-changes-2025-all-customers-move-to-level-a-pricing/) -- Analysis of November 2025 EA pricing changes
- `providers/azure/compute.md` -- Azure VM SKU selection and compute architecture
- `providers/vmware/licensing.md` -- VMware/Broadcom licensing including BYOL to Azure VMware Solution
- `providers/vmware/avs-azure.md` -- Azure VMware Solution architecture and MACC implications
- `general/cost-onprem.md` -- On-premises cost modeling for hybrid comparison
