# Azure DNS (Azure DNS, Traffic Manager, Front Door, Private DNS)

## Checklist

- [ ] Choose zone type: Azure DNS public zones for internet-facing resolution vs Azure Private DNS zones for VNet-scoped name resolution; private zones support auto-registration of VM DNS records within linked VNets
- [ ] Configure Traffic Manager routing method based on requirements: priority (active/passive failover with ordered endpoints), weighted (traffic splitting by percentage, 1-1000 weights), geographic (route by user continent/country/state), performance (lowest-latency endpoint based on internet latency tables), subnet (map specific client IP ranges to endpoints), multivalue (return multiple healthy endpoints for client-side selection)
- [ ] Set up Traffic Manager health probes: HTTP/HTTPS/TCP, configurable interval (default 30s, fast interval 10s), tolerated failures (default 3), and custom path/port; endpoints marked degraded after exceeding failure threshold and removed from DNS responses
- [ ] Configure Azure Front Door routing rules for global HTTP load balancing: path-based routing, host-based routing, redirect rules, and URL rewrite; Front Door operates at Layer 7 with anycast and provides sub-second failover compared to Traffic Manager's DNS-TTL-dependent failover
- [ ] Enable DNSSEC for Azure DNS public zones: zone signing is managed by Azure, but you must establish a chain of trust by adding the DS record to the parent zone (registrar); verify DNSSEC validation is working with external tools
- [ ] Set appropriate TTL values on DNS records: lower TTL (30-60s) for records involved in failover or deployment rotation; higher TTL (300-3600s) for stable records to reduce query volume; Traffic Manager DNS responses use a configurable TTL (default 60s) separate from individual record TTLs
- [ ] Design Private DNS zones for internal service discovery: link zones to VNets with auto-registration enabled for VM name resolution; link without auto-registration for resolution-only access from spoke VNets; use privatelink zones for Private Endpoint resolution
- [ ] Configure custom domain verification for Azure services (App Service, Front Door, Static Web Apps) using TXT or CNAME validation records; plan for certificate management with Azure-managed certificates or Key Vault-stored certificates
- [ ] Implement DNS-based failover patterns: Traffic Manager nested profiles for multi-tier routing (geographic outer profile -> performance inner profiles), Front Door origin groups with health probes for HTTP workloads, or combine both for DNS-level and application-level failover
- [ ] Plan for hybrid DNS resolution: configure Azure DNS Private Resolver with inbound endpoints (on-premises resolves Azure private zones) and outbound endpoints (VNets resolve on-premises DNS via forwarding rulesets); Private Resolver replaces the need for custom DNS forwarder VMs
- [ ] Monitor DNS with Azure Monitor: Traffic Manager endpoint health, Front Door origin health, DNS zone query volume metrics; configure alerts on Traffic Manager endpoint status changes and Front Door origin health percentage drops
- [ ] Use alias record sets in Azure DNS to point zone apex to Azure resources (Traffic Manager, Front Door, public IP, CDN); alias records resolve at the DNS server side and support automatic target IP tracking without manual record updates

## Why This Matters

DNS is the first hop in every request path and a misconfiguration can silently route traffic to unhealthy endpoints or expose internal services. Azure provides multiple DNS and traffic routing services at different layers -- Azure DNS for authoritative hosting, Traffic Manager for DNS-level global load balancing, Front Door for Layer 7 global routing, and Private DNS for internal resolution. Choosing the wrong service or misconfiguring failover leads to outages, latency increases, or split-brain scenarios.

Traffic Manager operates at the DNS layer with TTL-dependent failover (30-60 seconds typical), making it suitable for non-HTTP workloads and multi-cloud routing. Front Door operates at Layer 7 with anycast and can failover in under a second, but only supports HTTP/HTTPS. Many architectures combine both: Traffic Manager for cross-cloud or non-HTTP failover, and Front Door for HTTP workload routing with WAF and caching.

Private DNS zones are essential for Private Endpoint (Private Link) resolution. Without properly linked privatelink.* zones, VNet resources cannot resolve the private IP of PaaS services accessed via Private Endpoint. This is one of the most common networking issues in Azure enterprise architectures.

## Common Decisions (ADR Triggers)

- **Traffic Manager vs Front Door for global routing** -- Traffic Manager is DNS-based, works with any protocol (TCP/UDP), supports non-Azure and on-premises endpoints, and costs $0.36 per million queries. Front Door is Layer 7 (HTTP/HTTPS only), provides sub-second failover, includes WAF and caching, uses anycast for lowest latency, and costs based on data transfer plus requests. Use Traffic Manager for non-HTTP workloads, multi-cloud, or hybrid. Use Front Door for web applications needing WAF, caching, or fast failover. They can be combined: Front Door behind Traffic Manager for multi-cloud HTTP routing.
- **Traffic Manager routing method selection** -- Priority for simple active/passive DR. Weighted for canary deployments or traffic migration (gradually shift 5% -> 25% -> 100%). Performance for multi-region apps where users should reach the closest healthy region. Geographic for data sovereignty or compliance requirements routing users by country. Subnet for overriding routing for specific known client networks (VPN, office IPs). Multivalue for returning multiple healthy IPs to DNS queries, enabling client-side selection.
- **Azure DNS Private Resolver vs custom DNS forwarder VMs** -- Private Resolver is a managed service ($0.18/hour per endpoint) with built-in high availability, no VM patching, and integration with forwarding rulesets. Custom DNS VMs (BIND, Windows DNS) provide full flexibility for complex conditional forwarding, DHCP, and advanced DNS features but require HA design (2+ VMs, load balancer) and ongoing maintenance. Use Private Resolver for standard hybrid DNS forwarding. Use custom DNS only for advanced requirements like Active Directory-integrated DNS.
- **Nested vs flat Traffic Manager profiles** -- Flat profiles use a single routing method. Nested profiles chain multiple routing methods (e.g., geographic -> performance -> priority) for sophisticated routing. Nested profiles add DNS resolution latency (one additional DNS lookup per nesting level) and complexity. Use nested profiles when a single routing method cannot express the routing requirements.
- **Azure-managed vs bring-your-own-domain DNS** -- Azure-managed domains (azurewebsites.net, azurefd.net) require no DNS configuration but limit branding and portability. Custom domains require DNS zone management, certificate provisioning, and validation records but provide branding and cloud portability. Always use custom domains for production workloads.

## Reference Architectures

### Multi-Region Active/Active Web Application
Azure Front Door (global entry point, WAF, caching) -> origin groups with health probes pointing to App Service or AKS in East US and West Europe. Front Door performs Layer 7 routing with priority or weighted load balancing across origins. Automatic failover in under 1 second when origin health drops below threshold. Custom domain with Azure-managed TLS certificate. Azure DNS public zone hosting the custom domain with CNAME to Front Door endpoint.

### Hybrid DNS with On-Premises Integration
Azure DNS Private Resolver deployed in a hub VNet: inbound endpoint (10.0.0.4) receives queries from on-premises DNS servers forwarding azure.contoso.com. Outbound endpoint with forwarding ruleset sends queries for onprem.contoso.com to on-premises DNS servers (192.168.1.10, 192.168.1.11). Private DNS zones (privatelink.database.windows.net, privatelink.blob.core.windows.net) linked to hub VNet for Private Endpoint resolution. Spoke VNets linked to Private Resolver forwarding ruleset via VNet links.

### Multi-Cloud DNS Failover
Traffic Manager profile with priority routing: primary endpoint pointing to Azure Front Door (priority 1), secondary endpoint pointing to AWS CloudFront or GCP load balancer (priority 2). Health probes on both endpoints using HTTPS on /health path. TTL set to 30 seconds for faster failover. Nested profile option: outer geographic profile for compliance routing, inner priority profiles for failover within each geography.

### Private Endpoint DNS Architecture
Private DNS zones for each PaaS service (privatelink.database.windows.net, privatelink.blob.core.windows.net, privatelink.vaultcore.azure.net) centralized in a hub/connectivity subscription. Zones linked to hub VNet and all spoke VNets needing resolution. Private Endpoints in spoke VNets auto-register A records in the centralized privatelink zones. Azure Policy to enforce Private DNS zone group creation on Private Endpoint deployment for consistent DNS registration.
