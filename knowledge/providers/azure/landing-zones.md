# Azure Landing Zones

## Scope

Azure Landing Zones (ALZ) are Microsoft's prescriptive multi-subscription Azure architecture that combines management group hierarchy, policy assignments, subscription vending, identity baseline, networking topology, security baseline, and workload landing patterns into a deployable foundation. Covers the Cloud Adoption Framework (CAF) reference architecture, the Enterprise-Scale Landing Zone implementation, the AzOps and ALZ Bicep / Terraform deployment paths, the management group hierarchy, the platform vs application landing zone split, the identity / management / connectivity / corp / online subscriptions, hub-spoke vs vWAN topology, the subscription vending pattern, and the audit characteristics of accounts that have legacy "flat subscription" architecture vs ALZ-aligned architecture.

## Checklist

- [ ] **[Critical]** Establish a management group hierarchy that mirrors organizational structure and policy boundaries — at minimum: Tenant Root → "Top" → Platform → (Identity, Management, Connectivity) and Landing Zones → (Corp, Online, Sandbox, Decommissioned). The default "Tenant Root → all subscriptions flat" structure does not allow per-OU policy targeting and forces every policy to be assigned at the tenant root, which is too coarse.
- [ ] **[Critical]** Assign Azure Policy at the management group level, not the subscription level. Policy assigned at a management group inherits to all child management groups and subscriptions, so a single assignment at the Top management group enforces a control across the entire tenant. Policy assigned per-subscription is the same maintenance burden as no policy at all.
- [ ] **[Critical]** Use a dedicated **Identity** subscription for the Active Directory Domain Services / Entra Domain Services / hybrid identity components. Identity is a tenant-wide concern, not a workload concern, and it needs the strictest policy boundaries (no resource provisioning by workload teams, no public network exposure for domain controllers, immutable diagnostic settings).
- [ ] **[Critical]** Use a dedicated **Connectivity** subscription for the network platform: hub VNet, ExpressRoute / VPN gateways, Azure Firewall / third-party NVAs, DNS private zones, and the Private DNS Resolver. The connectivity subscription is where the network team has owner permissions and where every workload landing zone connects via VNet peering or vWAN attachment.
- [ ] **[Critical]** Use a dedicated **Management** subscription for centralized monitoring and management: Log Analytics workspace (the central one that all subscriptions forward to), Azure Monitor, Update Management, Azure Automation, the Azure Arc resource bridge if used. This subscription holds the data that the entire tenant's observability depends on.
- [ ] **[Critical]** Implement **subscription vending** as a code-driven process, not a portal-click. New workload subscriptions should be created via a pipeline that places them in the right management group, applies the right policies, configures the network attachment, registers diagnostic settings, and assigns the right RBAC roles. Manual subscription creation is the source of "snowflake" subscriptions that diverge from the rest of the tenant over time.
- [ ] **[Critical]** Choose a network topology — **hub-spoke** (traditional VNet peering with a central hub VNet) or **virtual WAN (vWAN)** (Microsoft-managed transit hub with vHub-to-vHub global routing). Hub-spoke is the right answer for tenants with predictable topology, fewer than 20 spokes per hub, and a desire for fine-grained control. vWAN is the right answer for tenants with global presence, many spokes, and a preference for managed routing. Mixing the two within a single tenant is operationally painful.
- [ ] **[Critical]** Enable **diagnostic settings** centrally via policy. Every Azure resource type that supports diagnostic settings should be configured to forward platform logs and metrics to the central Log Analytics workspace in the Management subscription. Policy with `DeployIfNotExists` effect can enforce this automatically as resources are created.
- [ ] **[Recommended]** Distinguish **Corp** landing zones (workloads that require corporate network connectivity, typically internal applications) from **Online** landing zones (workloads that are internet-facing and do not need on-prem connectivity). The two have different network attachments, different egress patterns, and different policy requirements. Mixing them in the same management group makes per-workload policy harder to express.
- [ ] **[Recommended]** Use **Azure Policy initiatives** (policy sets) rather than individual policy assignments when enforcing a baseline. The CAF / ALZ team publishes a baseline initiative covering ~100 controls; assign that initiative at the Top management group and add organization-specific policies as supplementary initiatives.
- [ ] **[Recommended]** Implement **Privileged Identity Management (PIM)** for any role assignment with write or owner permissions on shared resources. PIM converts a standing role assignment into a request-and-approve elevation, with audit trail and time-bound activation.
- [ ] **[Recommended]** Use a separate subscription for each application environment (production / non-production / sandbox) within a workload, rather than relying on resource group separation within a single subscription. Subscription is the strongest blast radius boundary in Azure — quotas, policy, RBAC, networking, billing all align to the subscription. Resource group separation is a much weaker boundary.
- [ ] **[Recommended]** Use **deny assignments** sparingly but deliberately for "no exceptions" controls. Deny assignments are stronger than `Deny` policy because they cannot be overridden — useful for blocking specific actions that should never happen (e.g., creating public IPs in the production subscription, deleting log retention policies).
- [ ] **[Optional]** Implement a **Decommissioned** management group with a deny-everything policy and move retired subscriptions there before deletion. This gives a controlled cooldown period during which the subscription cannot be used but can be recovered if a dependency was missed.
- [ ] **[Optional]** Use **Azure Lighthouse** for cross-tenant management of customer subscriptions when running an MSP-style architecture. Lighthouse delegates specific roles from the customer tenant to the MSP tenant without requiring guest user accounts.

## Why This Matters

Azure tenants tend to start as a single subscription with no management group hierarchy and no policy. As workloads multiply, additional subscriptions get created ad hoc, each with its own networking, its own policy state, its own diagnostic configuration, and its own RBAC model. Two years later, the same tenant has 30 subscriptions where every subscription is a snowflake, the network team cannot describe the topology in one diagram, the security team cannot answer "are diagnostic logs being collected from every subscription", and the cost team cannot attribute spend to a specific business unit because tagging is inconsistent.

The Cloud Adoption Framework / Azure Landing Zones architecture exists to prevent that outcome. It is opinionated, prescriptive, and largely deployable as code. The opinions are not the only correct ones — some organizations have legitimate reasons to deviate from the reference architecture — but starting from the reference and customizing is much cheaper than building bottom-up and discovering the same architectural needs as the tenant grows.

The single highest-value adoption decision is whether subscription creation goes through code (vending) or through manual portal action. Code-driven vending makes the rest of the landing zone architecture possible to enforce. Manual creation makes it impossible.

The audit consequence of legacy flat-subscription architecture is that almost every per-subscription control needs to be checked individually. The audit consequence of well-implemented ALZ is that the controls are visible at the management group level and can be verified once for the entire tenant. The cost difference between a clean ALZ audit and a flat-subscription audit is usually 5x in reviewer time.

## Common Decisions (ADR Triggers)

- **Hub-spoke vs vWAN topology** — hub-spoke for tenants with predictable, regional topology and a preference for explicit control. vWAN for tenants with global presence (multiple regions, multiple ExpressRoute circuits, multiple VPN gateways) where Microsoft-managed transit routing simplifies the operational model. The choice is hard to reverse once workloads are attached.
- **CAF Bicep vs Terraform vs ARM templates for ALZ deployment** — Bicep for organizations standardizing on Microsoft tooling and ARM under the hood. Terraform for organizations with multi-cloud or with existing Terraform investment. ARM templates only for legacy or for specific scenarios where Bicep does not yet support a feature. The deployment path matters less than picking one and sticking with it.
- **Subscription per environment vs subscription per application** — subscription per (application × environment) for high-isolation workloads. Subscription per application with resource group per environment for lower-isolation workloads where the operational simplicity of fewer subscriptions outweighs the blast radius benefit. ALZ Online and Corp landing zones default to subscription per application.
- **Management group depth** — 4 levels is the practical maximum (Tenant Root → Top → Platform/Landing Zones → Specific). Deeper hierarchies become hard to reason about and policy inheritance gets surprising. If you need more than 4 levels, the hierarchy probably has the wrong axis.
- **Single Log Analytics workspace vs per-region workspaces** — single workspace is simpler and is the right answer for most tenants. Multiple workspaces are appropriate when data residency requirements force regional separation, when the single workspace exceeds the daily ingestion limit (~6 TB / day), or when different teams need different retention policies on different log sources.
- **PIM for everything vs PIM for sensitive roles only** — PIM for everything that can write or own shared resources is the right answer for security-mature organizations. PIM for sensitive roles only (subscription owner, network contributor, key vault administrator) is the practical starting point for organizations new to PIM.

## Reference Architectures

### Standard CAF / ALZ deployment

- **Tenant Root** management group
- **Top** management group (with the baseline policy initiative assigned)
  - **Platform** management group
    - **Identity** subscription — ADDS / Entra Domain Services
    - **Management** subscription — Log Analytics, Azure Monitor, Automation
    - **Connectivity** subscription — hub VNet, ExpressRoute, Azure Firewall, Private DNS zones
  - **Landing Zones** management group
    - **Corp** management group — internal workloads with on-prem connectivity
      - One subscription per (application × environment)
    - **Online** management group — internet-facing workloads
      - One subscription per (application × environment)
  - **Sandbox** management group — exploration / dev / poc, isolated from corp networking
  - **Decommissioned** management group — retired subscriptions awaiting deletion

### Subscription vending pipeline

- Pull request triggers a Bicep/Terraform deployment
- The pipeline creates the subscription via the EA / MCA billing API or the Azure Lighthouse API
- The subscription is moved into the requested management group
- Network attachment is configured (VNet peering to the hub or vWAN connection)
- Diagnostic settings are applied via policy `DeployIfNotExists`
- RBAC role assignments are created for the workload owner (with PIM eligibility, not standing assignment)
- Tags are applied (CostCenter, Owner, Environment, BusinessUnit)
- Output is the subscription ID, the network attachment details, and the deployment audit trail

### Hub-spoke connectivity (traditional)

- **Hub VNet** in the Connectivity subscription, with: ExpressRoute Gateway, VPN Gateway (optional), Azure Firewall (or third-party NVA), shared services subnet, GatewaySubnet, AzureFirewallSubnet
- **Spoke VNets** peered to the hub, one per workload subscription
- Spoke-to-spoke traffic is forced through the hub firewall via UDR (user-defined routes) on each spoke
- DNS resolution via the Private DNS Resolver in the hub or via custom DNS servers in the shared services subnet
- All spoke subscriptions inherit the same network architecture via policy

### vWAN connectivity (global)

- **Virtual WAN** resource in the Connectivity subscription
- **vHub** in each region where workloads exist, with optional secured vHub (Azure Firewall or third-party NVA inside the hub)
- Spoke VNets connected to the regional vHub
- ExpressRoute and VPN gateways attached to vHubs as needed
- vHub-to-vHub global transit is built-in, no manual UDRs needed
- Same policy assignments as hub-spoke at the management group level

---

## Reference Links

- [Cloud Adoption Framework: Azure landing zones](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/)
- [Enterprise-Scale Landing Zone reference implementation](https://github.com/Azure/Enterprise-Scale)
- [Azure Landing Zones Bicep](https://github.com/Azure/ALZ-Bicep)
- [Azure Landing Zones Terraform](https://github.com/Azure/terraform-azurerm-caf-enterprise-scale)
- [Azure Policy initiatives for landing zones](https://learn.microsoft.com/azure/governance/policy/samples/built-in-initiatives)

## See Also

- `providers/azure/identity.md` — Entra ID and identity baseline for the Identity subscription
- `providers/azure/networking.md` — hub-spoke and vWAN networking primitives
- `providers/azure/security.md` — Defender for Cloud, Microsoft Sentinel, the security baseline
- `providers/azure/key-vault.md` — Key Vault as part of the platform baseline
- `providers/aws/multi-account.md` — equivalent multi-account architecture in AWS, similar shape
- `general/governance.md` — broader cloud governance patterns
