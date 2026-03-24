# Managed Cloud Services

## Scope

This file covers the **managed cloud services model** where a managed services provider (MSP) operates cloud-hosted infrastructure on behalf of a customer in public cloud platforms (Azure, AWS, GCP). The provider manages workloads, optimizes costs, and maintains operational responsibility while the customer retains business ownership. Distinct from private cloud as-a-service where the provider owns physical hardware -- here the infrastructure lives in a public cloud platform. For on-premises provider-owned models, see `patterns/private-cloud-as-a-service.md`. For managed services operational scoping, see `general/managed-services-scoping.md`. For pursuit methodology, see `general/pursuit-methodology.md`.

## Checklist

### Commercial Model

- [ ] **[Critical]** Is the commercial model explicitly defined? (Cost-plus: provider passes through cloud spend + management fee as percentage or flat rate. Fixed fee: provider charges a predictable monthly amount regardless of actual cloud spend. Consumption-based: customer pays for what they use plus per-resource management fee. Hybrid: fixed base fee + consumption overage. Each model creates different incentive structures -- cost-plus incentivizes the provider to increase spend, fixed fee incentivizes the provider to reduce spend.)
- [ ] **[Critical]** Is the management fee structure transparent? (Percentage of cloud spend, per-resource fee, per-VM fee, tiered pricing by environment, or flat monthly retainer. Percentage-of-spend models typically range 8-20% depending on scope. Ensure the customer understands what the fee covers vs. what incurs additional charges.)
- [ ] **[Critical]** Is the minimum commitment defined? (Monthly minimum spend, minimum number of managed resources, minimum contract value. Minimum commitments protect the provider's operational investment. Without them, a customer can scale down to near-zero and the provider still carries staffing costs.)
- [ ] **[Recommended]** Are professional services (projects, migrations, architecture redesign) priced separately from ongoing managed services? (Mixing project work into the monthly fee obscures costs and creates scope disputes. T&M or fixed-price SOWs for project work alongside the managed services agreement.)
- [ ] **[Recommended]** Is the pricing model aligned with the customer's consumption patterns? (Steady-state workloads suit fixed fee. Variable or seasonal workloads suit consumption-based. Rapid growth environments suit cost-plus with caps. Misalignment causes either customer overpayment or provider margin erosion.)
- [ ] **[Optional]** Is a comparable engagement referenced? (Prior managed cloud deals with similar scope, cloud platform, and customer size. Validates pricing assumptions and operational staffing model.)

### Subscription Ownership

- [ ] **[Critical]** Is the subscription/account ownership model defined? (Provider-owned: MSP holds the cloud subscription under their tenant, customer has no direct cloud relationship. Customer-owned: customer holds the subscription, grants provider delegated access. Each model has fundamentally different implications for billing, governance, exit strategy, and cloud provider relationship.)
- [ ] **[Critical]** If provider-owned subscription, is the billing relationship with the cloud vendor clearly documented? (Provider is the billing entity. Customer has no direct cloud invoice. Provider marks up or passes through cloud costs. Customer cannot independently verify actual cloud spend without provider transparency tools.)
- [ ] **[Critical]** If customer-owned subscription, are the delegated administration boundaries defined? (Azure Lighthouse, AWS Organizations delegated admin, cross-account IAM roles. What can the provider do? What requires customer approval? Who controls subscription-level settings, billing alerts, and resource locks?)
- [ ] **[Recommended]** Is the subscription structure designed for eventual independence? (Even in a long-term managed relationship, the customer should be able to operate independently if the relationship ends. Avoid architectural decisions that create lock-in to the provider's tooling or management plane.)

### MACC/EA Interaction

- [ ] **[Critical]** If the customer has a Microsoft Azure Consumption Commitment (MACC) or Enterprise Agreement (EA), is the spend attribution model defined? (Customer's MACC credits may only decrement against spend in the customer's own enrollment. If the provider operates workloads under the provider's enrollment, the customer's MACC does not benefit. This is a common and costly mistake.)
- [ ] **[Critical]** If the customer has AWS Enterprise Discount Program (EDP) credits, is the account linkage verified? (AWS EDP discounts apply to the payer account and linked accounts. Provider-operated accounts must be linked to the customer's organization to inherit EDP pricing.)
- [ ] **[Recommended]** Is there a strategy to maximize the customer's existing cloud commitments? (If the customer already has MACC/EA/EDP, the managed services architecture should be designed to keep spend within those agreements. Moving workloads to provider-owned subscriptions can forfeit committed discounts worth millions.)
- [ ] **[Recommended]** Are the EA/CSP billing implications documented? (Azure EA and CSP are mutually exclusive billing models for a given subscription. A subscription cannot simultaneously be under EA and CSP. Migrating a customer from EA to provider's CSP forfeits EA pricing and MACC attribution.)

### Licensing and Cost Optimization

- [ ] **[Critical]** Is the Reserved Instance / Savings Plan strategy defined? (Provider purchases RI/SP commitments to reduce cloud costs, charges customer at a rate between RI and on-demand pricing. The delta is the provider's margin. Alternatively, customer purchases their own RI/SP and provider manages them. Ownership of the commitment determines who bears the risk of underutilization.)
- [ ] **[Critical]** Is the BYOL (Bring Your Own License) vs. provider-procured licensing strategy defined? (Customer may have existing SQL Server, Windows Server, or other licenses with Software Assurance eligible for Azure Hybrid Benefit or AWS License Manager. Using BYOL can reduce costs 40-80% for Windows/SQL workloads. If the provider procures licenses, they should be priced competitively against the customer's BYOL option.)
- [ ] **[Critical]** Is the Azure Hybrid Benefit / AWS License Included vs. BYOL decision documented per workload? (This is not a one-size-fits-all decision. Some workloads benefit from BYOL, others from license-included pricing. The decision depends on the customer's existing EA, Software Assurance coverage, and the specific SKU.)
- [ ] **[Recommended]** Is there a continuous cost optimization program? (Rightsizing recommendations, orphaned resource cleanup, storage tier optimization, dev/test shutdown schedules, spot/preemptible instance usage for batch workloads. The provider should demonstrate ongoing value through cost reduction, not just cost management.)
- [ ] **[Recommended]** Is the savings sharing model defined? (When the provider identifies cost savings, how are those savings distributed? Provider keeps 100%? Split 50/50? Customer gets 100% and provider earns through the management fee? The incentive structure drives provider behavior.)
- [ ] **[Optional]** Are dev/test pricing programs applied? (Azure Dev/Test subscription pricing, AWS dev/test discounts. Significant savings for non-production workloads that are often overlooked.)

### Responsibility Matrix (RACI)

- [ ] **[Critical]** Is a RACI matrix defined across all operational domains? (Compute, storage, networking, security, identity, backup, DR, patching, monitoring, cost management, compliance, incident response. For each domain: who is Responsible, Accountable, Consulted, Informed? The RACI must cover provider, customer, and cloud vendor roles.)
- [ ] **[Critical]** Is the cloud provider's shared responsibility model mapped to the managed services RACI? (The cloud provider is responsible for physical infrastructure, hypervisor, and platform services availability. The managed services provider is responsible for workload configuration, security posture, and operational management. The customer is responsible for data classification, business requirements, and application logic. Gaps between these three create risk.)
- [ ] **[Critical]** Are the boundaries between infrastructure management and application management explicit? (Managing an Azure VM is infrastructure. Managing the SQL Server running on that VM is debatable. Managing the application connecting to that SQL Server is typically customer scope. These boundaries must be defined before contract signature.)
- [ ] **[Recommended]** Is the RACI reviewed and updated as new services are adopted? (The initial RACI covers known workloads. When the customer adopts a new cloud service -- AKS, Azure OpenAI, AWS Bedrock -- the RACI must be updated. Provider may not have operational expertise for every cloud service.)

### SLA and Service Levels

- [ ] **[Critical]** Is the managed services SLA mapped to the underlying cloud provider SLA? (The provider cannot offer a higher availability SLA than the cloud platform provides. A 99.99% managed services SLA on a single-VM workload with a 99.9% Azure SLA is a contractual liability. The managed services SLA should be at or slightly below the platform SLA.)
- [ ] **[Critical]** Are SLA measurement and reporting mechanisms defined? (Uptime percentage, response time, resolution time, MTTR, MTBF. How is uptime measured -- synthetic monitoring, customer-reported, cloud provider health signals? Who calculates SLA attainment -- provider self-reports or independent measurement?)
- [ ] **[Critical]** Are SLA exclusions documented? (Planned maintenance windows, customer-caused outages, cloud provider outages beyond provider control, force majeure. Without clear exclusions, the provider bears financial penalties for events outside their control.)
- [ ] **[Recommended]** Is there a service credit mechanism for SLA breaches? (Percentage of monthly fee credited back for each tier of SLA miss. Credits should be meaningful enough to incentivize performance but not so large that they threaten the commercial viability of the engagement.)
- [ ] **[Recommended]** Is the SLA passthrough from cloud provider to managed services customer documented? (When Azure or AWS has an outage, the cloud provider issues service credits to the subscription owner. If the provider owns the subscription, are those credits passed through to the customer? If the customer owns the subscription, does the provider's SLA credit stack on top of the cloud provider credit?)

### Operational Model

- [ ] **[Critical]** Is the NOC/SOC operating model defined? (24x7x365, 8x5 with on-call, follow-the-sun, dedicated vs. shared. The operational model must match the customer's SLA requirements. A 15-minute response time SLA requires 24x7 staffing, not on-call.)
- [ ] **[Critical]** Is the incident management process defined end-to-end? (Detection, triage, escalation, communication, resolution, post-mortem. Who opens tickets with the cloud provider? Who communicates with the customer's business stakeholders? What are the escalation thresholds?)
- [ ] **[Critical]** Is the change management process defined? (Standard changes vs. normal changes vs. emergency changes. What requires customer approval? What can the provider execute autonomously? Is there a CAB (Change Advisory Board) with customer representation?)
- [ ] **[Critical]** Is the patching strategy defined? (OS patching cadence, application patching responsibility, zero-day response process, patching windows, rollback procedures. Cloud-native services are patched by the cloud provider -- but IaaS workloads require provider or customer patching.)
- [ ] **[Recommended]** Are monitoring and alerting standards defined? (What is monitored, alerting thresholds, notification channels, auto-remediation capabilities. Provider should use cloud-native monitoring -- Azure Monitor, AWS CloudWatch -- supplemented by their own tooling for correlation and reporting.)
- [ ] **[Recommended]** Is the automation and self-healing strategy defined? (Infrastructure as Code for provisioning, auto-scaling policies, auto-remediation runbooks, ChatOps integration. Mature managed services operations should automate repetitive tasks to reduce human error and response times.)

### Management Plane Architecture

- [ ] **[Critical]** Is the management plane multi-tenant or dedicated? (Multi-tenant: provider uses a single management platform across all customers, with logical separation. Dedicated: customer gets their own management instance. Multi-tenant is more cost-effective but raises data isolation concerns. Dedicated is more expensive but provides stronger isolation.)
- [ ] **[Critical]** Is the management tooling integrated with the cloud provider's native capabilities? (Azure Arc, AWS Systems Manager, Azure Policy, AWS Config. Provider tooling that duplicates cloud-native capabilities adds cost and complexity. Provider tooling that extends cloud-native capabilities adds value.)
- [ ] **[Recommended]** Is the customer portal and reporting capability defined? (Self-service dashboards, cost reporting, ticket submission, SLA reporting, change request submission. Customers expect visibility into their managed environment. Portal maturity is a competitive differentiator.)
- [ ] **[Recommended]** Can the management plane be transitioned to the customer at contract end? (If the provider uses proprietary tooling, the customer loses operational visibility at contract end. If the provider uses cloud-native tooling with supplemental dashboards, the customer retains cloud-native capabilities.)

### Contract Structure

- [ ] **[Critical]** Is the contract term length defined and aligned with the commercial model? (1-year terms suit consumption-based models. 3-year terms suit fixed-fee models with RI/SP commitments. Longer terms justify provider investment in automation and tooling. Shorter terms increase provider risk of losing the engagement before recovering setup costs.)
- [ ] **[Critical]** Are auto-renewal and termination notice terms defined? (Typical: 30-90 day notice to terminate, automatic 1-year renewal if no notice given. Termination for cause vs. termination for convenience -- different notice periods and financial implications.)
- [ ] **[Critical]** Is the burst capacity model defined? (Can the customer exceed the minimum commitment? Is burst capacity priced at a premium, at the same rate, or at a discount for sustained overages? Burst provisions prevent the customer from being blocked during growth periods.)
- [ ] **[Recommended]** Is the contract structured to accommodate scope changes? (New workloads, new cloud services, increased/decreased resource counts. A rigid contract that requires amendments for every change creates friction. A framework agreement with flexible SOWs is more adaptable.)
- [ ] **[Recommended]** Are benchmarking and market rate adjustment clauses included? (For long-term contracts, the customer should have the right to benchmark pricing against market rates periodically. The provider should have the right to adjust pricing if the customer's environment materially changes in complexity.)

### Cost Transparency

- [ ] **[Critical]** Is the showback/chargeback model defined? (Showback: customer can see costs by department/project/application but does not pay internally. Chargeback: costs are allocated and billed to individual business units. The provider must deliver cost data in a format that supports the customer's internal financial processes.)
- [ ] **[Critical]** Is the cloud provider's actual cost visible to the customer? (In cost-plus models, the customer needs to see actual cloud spend to verify the management fee calculation. In fixed-fee models, cost transparency builds trust even though the customer pays the same regardless. In provider-owned subscription models, the customer has no native cost visibility -- the provider must provide it.)
- [ ] **[Recommended]** Is the margin structure disclosed or opaque? (Some customers require open-book pricing where the provider's margin is visible. Others accept closed-book where the total price is compared against market alternatives. Government and public sector contracts often require open-book.)
- [ ] **[Recommended]** Are cost allocation tags and naming conventions enforced? (Cloud resources must be tagged consistently to enable accurate cost reporting. The tagging taxonomy should be defined collaboratively and enforced through policy. Untagged resources cannot be allocated to business units.)

### Governance and Access Control

- [ ] **[Critical]** Is the RBAC model defined for the cloud subscription? (Who has Owner, Contributor, Reader roles? Does the provider have standing privileged access or just-in-time access? Are Privileged Identity Management (PIM) or AWS IAM Identity Center used for elevation? Standing admin access for the provider is a security risk; JIT elevation with audit logging is the standard.)
- [ ] **[Critical]** Is the Azure Policy / AWS Service Control Policy framework defined? (Who creates policies? Who can override them? Are policies enforced by the provider to maintain operational standards, or by the customer to maintain governance standards? Policy conflicts between provider operational needs and customer governance requirements are common.)
- [ ] **[Critical]** Are spending limits and budget alerts configured? (Who sets budget thresholds? Who receives alerts? Can the provider provision new resources without customer financial approval? An unconstrained provider can accidentally generate significant cloud bills. Budget governance prevents bill shock.)
- [ ] **[Recommended]** Is the landing zone / account structure designed collaboratively? (Azure Management Groups, AWS Organizations OUs. The structure determines governance boundaries, policy inheritance, cost allocation, and network topology. The provider and customer must agree on the structure before workload deployment.)
- [ ] **[Recommended]** Is there a defined process for customer self-service within governance guardrails? (The customer may need to deploy resources independently for development or testing. Governance guardrails -- approved regions, approved SKUs, cost limits -- enable self-service without operational risk.)

### Exit Strategy

- [ ] **[Critical]** Is the exit plan defined before contract signature? (What happens when the managed services contract ends? Customer takes over operations, transitions to another MSP, or moves workloads elsewhere. The exit plan should be a contract exhibit, not an afterthought.)
- [ ] **[Critical]** If provider-owned subscription, is the workload migration plan defined? (Workloads must move from provider subscription to customer subscription. This is a migration project with its own timeline, cost, and risk. IP addresses change, DNS updates are needed, identity and access must be reconfigured. Plan 3-6 months for a complex exit.)
- [ ] **[Critical]** Is knowledge transfer included in the exit plan? (Runbooks, architecture documentation, monitoring configurations, automation scripts, incident history, known issues. Without knowledge transfer, the customer or successor MSP starts from zero.)
- [ ] **[Recommended]** Are data portability and format requirements defined? (Monitoring data, log archives, configuration management databases, ticket history. What data does the customer receive at exit? In what format? What retention period applies?)
- [ ] **[Recommended]** Is there a transition assistance period in the contract? (Typically 90-180 days where the incumbent provider supports the transition to the customer or successor. Priced at standard rates or at a premium. Without this, the incumbent has no incentive to cooperate during exit.)

### Partner Programs and Cloud Provider Relationships

- [ ] **[Critical]** Is the provider's cloud partner status defined? (Azure: CSP Direct, CSP Indirect, Solutions Partner. AWS: Consulting Partner, Technology Partner, MSP Partner. Google: Premier Partner, MSP Partner. Partner tier determines access to technical resources, co-sell incentives, and customer support escalation paths.)
- [ ] **[Critical]** Is the billing model aligned with partner program requirements? (Azure CSP provides the provider with a margin on cloud consumption but removes the customer's EA pricing. AWS partner programs may require specific billing configurations. The partner program choice affects the customer's effective cloud cost.)
- [ ] **[Recommended]** Are co-sell and partner incentive programs leveraged? (Microsoft co-sell eligible solutions, AWS ISV Accelerate, Google partner incentives. These programs can provide marketing support, technical resources, and financial incentives that improve the commercial model for both provider and customer.)
- [ ] **[Recommended]** Is the cloud provider's field team engaged? (Cloud provider account teams -- Microsoft, AWS, Google -- can support the managed services engagement with technical architecture reviews, proof-of-concept funding, and migration credits. Engaging them early improves outcomes and may reduce costs.)

### Managed Dedicated Infrastructure (NC2/AVS/Dedicated Hosts)

- [ ] **[Critical]** If the engagement includes cloud-hosted dedicated infrastructure (Azure VMware Solution, Nutanix Cloud Clusters on Azure/AWS, Azure Dedicated Host, AWS Outposts), is the operational model for dedicated nodes defined separately from standard cloud IaaS? (Dedicated infrastructure requires different patching, monitoring, and capacity management processes. The provider must manage the dedicated nodes as infrastructure, not just the workloads on them.)
- [ ] **[Critical]** Is the capacity planning model for dedicated nodes defined? (Dedicated nodes have fixed capacity. Unlike standard cloud, you cannot auto-scale beyond the provisioned node count. Capacity planning must account for peak demand, N+1 redundancy, and growth projections. Underprovisioning causes outages; overprovisioning wastes committed spend.)
- [ ] **[Critical]** Is the licensing model for dedicated infrastructure correct? (AVS includes VMware licensing in the node cost. NC2 includes Nutanix licensing. Azure Dedicated Host enables BYOL for Windows Server and SQL Server. Licensing is fundamentally different from standard VM-based cloud and must be modeled separately.)
- [ ] **[Recommended]** Is the stretch cluster / multi-AZ architecture for dedicated nodes designed for the required availability? (AVS supports stretch clusters across availability zones. NC2 supports multi-AZ deployments. These architectures double the node count and cost but provide zone-level resilience. The availability requirement must justify the cost.)
- [ ] **[Recommended]** Is the network connectivity between dedicated nodes and standard cloud resources designed? (AVS and NC2 clusters connect to Azure/AWS networking via ExpressRoute or VPC peering. Bandwidth, latency, and security group rules between dedicated and standard environments require explicit design.)

### Security and Compliance

- [ ] **[Critical]** Is the shared responsibility model explicitly mapped for managed cloud services? (Cloud provider: physical security, hypervisor, platform availability. Managed services provider: workload security configuration, patch management, access control enforcement, monitoring. Customer: data classification, regulatory compliance decisions, application security. Each party must understand where their responsibility begins and ends.)
- [ ] **[Critical]** Is the provider's access to customer data governed by contract and technical controls? (Provider operations staff will have access to customer systems and potentially customer data. Data processing agreements, background checks, access logging, and technical least-privilege controls are required. Regulated industries -- healthcare, financial services, government -- have specific requirements.)
- [ ] **[Critical]** Is the compliance evidence collection and audit support model defined? (Who generates compliance evidence -- cloud provider, managed services provider, or customer? Who responds to auditor requests? SOC 2 Type II, ISO 27001, HIPAA, PCI DSS, FedRAMP -- each framework has specific evidence requirements that must be mapped to the responsible party.)
- [ ] **[Recommended]** Is the security incident response plan jointly defined? (Provider detects a potential breach in the customer's environment -- what is the communication protocol? Who leads the investigation? Who engages law enforcement or regulators? Incident response must be coordinated across provider and customer with clear roles and defined timelines.)
- [ ] **[Recommended]** Is the provider's own security posture validated? (The customer is trusting the provider with access to their cloud environment. The provider should demonstrate their own security maturity -- SOC 2 report, penetration testing results, security awareness training, background check policy. A compromised MSP is a supply chain attack on all their customers.)

### Staffing Model

- [ ] **[Critical]** Is the staffing model defined? (Dedicated team: named resources assigned exclusively to this customer. Shared team: resources shared across multiple customers with allocation ratios. Hybrid: dedicated lead engineer with shared operations support. The staffing model must match the customer's complexity, criticality, and SLA requirements.)
- [ ] **[Critical]** Are the skill requirements defined for the managed services team? (Cloud platform certifications, infrastructure-as-code proficiency, security competency, automation capability. The team must have depth in the customer's specific cloud platform and the workload types being managed -- VMware, Kubernetes, databases, networking.)
- [ ] **[Recommended]** Is the knowledge retention strategy defined? (Key-person risk in managed services is high. If the primary engineer leaves, institutional knowledge goes with them. Documentation, cross-training, and rotation policies mitigate this risk. Dedicated models are more vulnerable than shared models.)
- [ ] **[Recommended]** Is the escalation and specialization model defined? (L1 monitoring and triage, L2 operational engineering, L3 architecture and complex problem resolution. Does the provider have in-house L3 capability or do they escalate to the cloud provider? Escalation SLAs should be defined per tier.)
- [ ] **[Optional]** Is the customer's retained team scoped for their responsibilities? (Even with fully managed cloud services, the customer needs staff for application management, business requirements, vendor management, and strategic planning. Customers who eliminate their entire IT team create a single point of dependency on the provider.)

## Why This Matters

Managed cloud services are the dominant delivery model for organizations that want cloud benefits without building cloud operations expertise in-house. The provider brings operational maturity, tooling, and economies of scale. The customer gets predictable costs, SLA-backed availability, and access to skills they cannot recruit or retain.

The most common failure: **misaligned commercial model.** A cost-plus model where the provider has no incentive to optimize costs erodes customer trust. A fixed-fee model where the customer's environment grows 300% erodes provider margin. The commercial model must align incentives -- the provider should benefit when the customer's environment is well-run, not when it is large.

The second most common failure: **subscription ownership confusion.** When the provider operates workloads under their own subscription, the customer's MACC, EA discounts, and EDP credits do not apply. A customer with a $5M MACC who moves workloads to a provider's CSP subscription forfeits that commitment -- and may still owe Microsoft the $5M. This is not a theoretical risk; it happens regularly and is extremely difficult to reverse.

The third most common failure: **exit strategy as an afterthought.** When the managed services relationship ends -- and it will eventually end -- the customer needs to operate independently or transition to another provider. If the architecture is built around the provider's proprietary tooling, the customer faces a second migration project just to become operationally independent. Exit planning at contract inception prevents this.

## Common Decisions (ADR Triggers)

- **Commercial model** -- cost-plus, fixed fee, consumption-based, or hybrid; determines incentive alignment and customer satisfaction trajectory
- **Subscription ownership** -- provider-owned vs. customer-owned; determines MACC/EA applicability, governance model, and exit complexity
- **RI/SP purchasing strategy** -- provider-purchased (arbitrage) vs. customer-purchased (direct savings); determines who bears commitment risk and who captures margin
- **BYOL vs. license-included** -- per workload decision; can reduce licensing costs 40-80% for Windows/SQL workloads but requires Software Assurance
- **Management plane architecture** -- multi-tenant vs. dedicated; determines cost, data isolation, and customization capability
- **Staffing model** -- dedicated vs. shared vs. hybrid; determines cost, knowledge depth, and key-person risk profile
- **SLA tier** -- must align with cloud provider platform SLAs; setting SLAs above platform capability creates unmitigatable contractual liability
- **Governance model** -- provider-controlled vs. customer-controlled vs. collaborative; determines agility, security posture, and operational friction
- **Partner program** -- CSP vs. EA passthrough; determines billing relationship, cloud provider support tier, and effective pricing
- **Dedicated infrastructure** -- AVS, NC2, Dedicated Hosts vs. standard IaaS; determines licensing model, capacity planning approach, and cost structure

## See Also

- `patterns/private-cloud-as-a-service.md` -- Provider-owned on-premises infrastructure model
- `patterns/hybrid-cloud.md` -- Hybrid cloud architecture patterns
- `patterns/multi-cloud.md` -- Multi-cloud architecture patterns
- `general/managed-services-scoping.md` -- Managed services operational and commercial scoping
- `general/pursuit-methodology.md` -- Pursuit process and commercial framing
- `general/cost-cloud.md` -- Cloud cost modeling and optimization
