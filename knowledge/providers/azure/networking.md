# Azure Networking

## Checklist

- [ ] Is the VNet address space planned to avoid overlaps with on-premises networks and peered VNets, with subnets sized for service delegation requirements?
- [ ] Are Network Security Groups (NSGs) applied at the subnet level with rules following least-privilege, using Application Security Groups (ASGs) for role-based grouping?
- [ ] Is Azure Front Door configured as the global entry point for web applications, providing CDN, WAF, and global load balancing in a single service?
- [ ] Is Azure Application Gateway (L7) or Azure Load Balancer (L4) deployed for internal and regional load balancing with health probes configured?
- [ ] Is Azure WAF (on Front Door or Application Gateway) configured with OWASP 3.2 managed rule set and custom rules for application-specific protection?
- [ ] Is Azure Traffic Manager configured for DNS-based global traffic routing when Front Door is not used? (priority, weighted, performance, geographic routing)
- [ ] Are Private Endpoints configured for PaaS services (Azure SQL, Storage, Key Vault, Cosmos DB) to eliminate public internet exposure?
- [ ] Is Azure Bastion deployed for secure RDP/SSH access to VMs without exposing management ports to the internet?
- [ ] Is VNet Peering or Azure Virtual WAN configured for multi-VNet connectivity with appropriate route tables and no transitive routing gaps?
- [ ] Are User-Defined Routes (UDRs) configured to force traffic through Azure Firewall or NVA for inspection where required?
- [ ] Is Azure DDoS Protection Standard enabled for VNets hosting public-facing workloads?
- [ ] Is Azure DNS Private Zones configured for name resolution of Private Endpoints and internal services?
- [ ] Are NSG Flow Logs enabled and flowing to Log Analytics for network traffic analysis and threat detection?
- [ ] Is ExpressRoute or VPN Gateway configured for hybrid connectivity with redundant circuits and appropriate SKU?

## Why This Matters

Azure networking differs significantly from AWS in subnet delegation, NSG behavior (stateful but applied at subnet level by default), and the Front Door/Application Gateway duality. Private Endpoints are essential for securing PaaS services that are otherwise publicly accessible by default. VNet peering is non-transitive, which catches teams migrating from hub-spoke AWS Transit Gateway designs.

## Common Decisions (ADR Triggers)

- **Front Door vs Application Gateway** -- global L7 with built-in CDN vs regional L7 with deeper WAF integration
- **Azure Virtual WAN vs hub-spoke VNet peering** -- managed routing and SD-WAN integration vs traditional hub-spoke with NVA
- **Azure Firewall vs third-party NVA** -- managed service with threat intelligence vs Palo Alto, Fortinet, or Check Point
- **Private Endpoints vs Service Endpoints** -- full private IP integration vs simpler but less secure VNet-scoped access
- **DDoS Protection Standard** -- $2,944/mo cost vs risk exposure for public workloads
- **Hybrid connectivity** -- ExpressRoute (dedicated circuit) vs VPN Gateway (encrypted over internet), coexistence model
- **DNS strategy** -- Azure DNS Private Zones vs custom DNS servers, conditional forwarding for hybrid

## Pricing Links

### Azure Pricing Pages

- [Virtual Network Pricing](https://azure.microsoft.com/en-us/pricing/details/virtual-network/) — VNet itself is free; charges for VNet peering, NAT Gateway, and public IPs
- [VNet Peering Pricing](https://azure.microsoft.com/en-us/pricing/details/virtual-network/#pricing) — $0.01/GB inbound + $0.01/GB outbound (same region); $0.035/GB cross-region
- [Azure NAT Gateway Pricing](https://azure.microsoft.com/en-us/pricing/details/azure-nat-gateway/) — $0.045/hr + $0.045/GB data processed
- [Bandwidth (Data Transfer) Pricing](https://azure.microsoft.com/en-us/pricing/details/bandwidth/) — egress, inter-region, and internet-bound transfer rates
- [Azure Front Door Pricing](https://azure.microsoft.com/en-us/pricing/details/frontdoor/) — base fee + per-request + data transfer + WAF rules
- [Application Gateway Pricing](https://azure.microsoft.com/en-us/pricing/details/application-gateway/) — fixed cost (v2) + capacity units consumed
- [Azure Firewall Pricing](https://azure.microsoft.com/en-us/pricing/details/azure-firewall/) — Standard: $1.25/hr (~$912/mo); Premium: $1.75/hr (~$1,277/mo) + data processing
- [Azure DDoS Protection Pricing](https://azure.microsoft.com/en-us/pricing/details/ddos-protection/) — Standard: $2,944/mo (covers up to 100 public IPs)
- [ExpressRoute Pricing](https://azure.microsoft.com/en-us/pricing/details/expressroute/) — port fees by speed + data transfer (metered or unlimited plans)
- [Azure Private Link Pricing](https://azure.microsoft.com/en-us/pricing/details/private-link/) — $0.01/hr per endpoint + $0.01/GB data processed
- [Azure VPN Gateway Pricing](https://azure.microsoft.com/en-us/pricing/details/vpn-gateway/) — by SKU (Basic to VpnGw5AZ), $0.04-$1.20/hr
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/) — interactive cost estimation tool

### Common Cost Surprises

1. **Azure Firewall always-on cost** — Azure Firewall Standard costs ~$912/mo ($1.25/hr) even with zero traffic. Premium is ~$1,277/mo. Plus $0.016/GB data processing. Many teams deploy Azure Firewall for compliance without realizing the baseline cost. Consider whether NSGs + UDRs suffice for non-regulated workloads.

2. **DDoS Protection Standard pricing** — $2,944/mo flat fee, regardless of the number of attacks or traffic volume. Covers up to 100 public IPs. Essential for public-facing workloads but expensive for small deployments. One subscription-level plan covers all VNets.

3. **VNet peering cross-region costs** — $0.035/GB each direction for global peering (vs $0.01/GB same-region). A multi-region architecture transferring 5 TB/mo cross-region pays ~$350/mo in peering alone.

4. **Application Gateway v2 minimum cost** — even at zero traffic, Application Gateway v2 costs ~$175/mo (fixed capacity units). The WAF tier adds ~$25/mo. Autoscaling can spike costs during traffic bursts.

5. **ExpressRoute data overage** — metered ExpressRoute plans charge $0.025/GB outbound after the included data. Unlimited plans cost 1.5-2x the port fee. Large data transfers can make metered plans unexpectedly expensive.

6. **Public IP address charges** — Standard SKU public IPs cost $0.004/hr (~$2.88/mo) each. Basic SKU is being retired. An account with 30 public IPs pays ~$86/mo.

## Reference Architectures

- [Azure Architecture Center: Hub-spoke network topology](https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke) -- reference architecture for enterprise hub-spoke networking with Azure Firewall and VNet peering
- [Azure Architecture Center: Networking architectures](https://learn.microsoft.com/en-us/azure/architecture/networking/) -- curated collection of network topology, hybrid connectivity, and load balancing reference designs
- [Azure Landing Zone: Network topology and connectivity](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/network-topology-and-connectivity) -- Cloud Adoption Framework guidance for enterprise-scale network design
- [Azure Well-Architected Framework: Networking](https://learn.microsoft.com/en-us/azure/well-architected/) -- best practices for VNet design, NSGs, and load balancing
- [Azure Architecture Center: Zero-trust network for web applications](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/gateway/application-gateway-before-azure-firewall) -- reference design for securing web apps with Front Door, WAF, and Azure Firewall
