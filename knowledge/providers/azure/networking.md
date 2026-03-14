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
