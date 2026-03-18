# GCP Networking

## Scope

VPC (custom-mode, Shared VPC), subnets and IP management, Cloud Load Balancing (global and regional), Cloud CDN, Cloud Armor (Standard and Enterprise), Cloud NGFW Enterprise (formerly Cloud Firewall Plus), Cloud NAT, Cloud Interconnect, Cloud VPN, Private Service Connect, Private Google Access, VPC flow logs, hierarchical firewall policies.

## Checklist

- [ ] [Critical] Is the VPC configured as a custom-mode VPC (not auto-mode) with explicitly planned subnets per region and secondary ranges for GKE pods/services?
- [ ] [Recommended] Are firewall rules using service accounts or network tags for targeting instead of IP-based rules, following least-privilege with explicit deny rules logged?
- [ ] [Recommended] Is Cloud CDN enabled on the external HTTP(S) Load Balancer for static content, with cache modes (CACHE_ALL_STATIC, USE_ORIGIN_HEADERS, FORCE_CACHE_ALL) configured per backend?
- [ ] [Recommended] Is Cloud Armor configured with security policies on the load balancer, including preconfigured WAF rules (OWASP Top 10), rate limiting, and adaptive protection?
- [ ] [Critical] Is the appropriate load balancer type selected? (external global HTTP(S) for web apps, internal regional TCP/UDP for internal services, external regional network for non-HTTP)
- [ ] [Recommended] Is Private Google Access enabled on subnets hosting VMs without external IPs to allow access to Google APIs and services?
- [ ] [Recommended] Are Private Service Connect endpoints configured for managed services (Cloud SQL, Memorystore, Vertex AI) to avoid public IP exposure?
- [ ] [Recommended] Is Cloud NAT configured per region for outbound internet access from private VMs, with minimum ports per VM and endpoint-independent mapping?
- [ ] [Recommended] Is Shared VPC used for multi-project networking, with host and service projects correctly configured and IAM permissions scoped?
- [ ] [Recommended] Is Cloud Interconnect (Dedicated or Partner) or Cloud VPN configured for hybrid connectivity with redundant tunnels?
- [ ] [Optional] Are VPC flow logs enabled on subnets with appropriate aggregation intervals and sampling rates for cost control?
- [ ] [Recommended] Is DNS managed via Cloud DNS with private zones for internal resolution and forwarding zones for hybrid DNS?
- [ ] [Recommended] Are hierarchical firewall policies applied at the organization or folder level for centralized security controls?

## Why This Matters

GCP networking uses a global VPC model that differs fundamentally from AWS and Azure. Subnets are regional (not zonal), and VPCs are global, eliminating the need for VPC peering within a project. However, Shared VPC complexity increases with multi-project setups. GCP firewall rules are stateful and global, which is powerful but requires careful management to avoid overly permissive configurations. Cloud Armor is the only way to get WAF protection and must be attached to a load balancer.

## Common Decisions (ADR Triggers)

- **Shared VPC vs standalone VPCs** -- centralized network management vs project autonomy, IAM complexity
- **Load balancer type** -- global external (Envoy-based) vs classic vs regional, proxy vs passthrough
- **Cloud Armor tier** -- Standard (pay-per-policy) vs Cloud Armor Enterprise (adaptive protection, DDoS response team, threat intelligence, managed rules; replaces Managed Protection Plus)
- **Hybrid connectivity** -- Dedicated Interconnect (10/100 Gbps) vs Partner Interconnect vs HA VPN
- **Private access model** -- Private Google Access vs Private Service Connect vs VPC Service Controls
- **Firewall management** -- VPC firewall rules vs hierarchical policies vs Cloud NGFW Enterprise (L7 inspection with TLS interception, IDS/IPS; formerly Cloud Firewall Plus)
- **CDN strategy** -- Cloud CDN on load balancer vs Media CDN for streaming vs third-party CDN

## Pricing Links

### GCP Pricing Pages

- [VPC Pricing](https://cloud.google.com/vpc/pricing) -- VPC itself is free; charges for egress, Cloud NAT, and network features
- [Network Egress Pricing](https://cloud.google.com/vpc/network-pricing) -- internet egress, inter-region, and inter-zone transfer rates
- [Cloud NAT Pricing](https://cloud.google.com/nat/pricing) -- $0.044/hr per gateway + $0.045/GB data processed
- [Cloud Load Balancing Pricing](https://cloud.google.com/vpc/network-pricing#lb) -- forwarding rules ($0.025/hr) + data processed ($0.008-$0.012/GB)
- [Cloud CDN Pricing](https://cloud.google.com/cdn/pricing) -- cache egress ($0.02-$0.08/GB by region) + cache fill + cache lookup fees
- [Cloud Armor Pricing](https://cloud.google.com/armor/pricing) -- Standard: $0.75/policy/mo + $0.60/rule/mo + $0.60/10K requests; Enterprise: per-project subscription
- [Cloud Interconnect Pricing](https://cloud.google.com/interconnect/pricing) -- Dedicated: $1,700/mo (10 Gbps), Partner: varies by provider
- [Cloud VPN Pricing](https://cloud.google.com/network-connectivity/pricing#vpn-pricing) -- $0.075/hr per tunnel (Classic) or HA VPN
- [Private Service Connect Pricing](https://cloud.google.com/vpc/pricing#private-service-connect-pricing) -- $0.01/hr per endpoint + data processing
- [VPC Flow Logs Pricing](https://cloud.google.com/vpc/network-pricing#flow-logs-pricing) -- charged via Cloud Logging ingestion ($0.50/GB)
- [Network Intelligence Center Pricing](https://cloud.google.com/network-intelligence-center/pricing) -- connectivity tests, performance dashboard, firewall insights
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator) -- interactive cost estimation tool

### Common Cost Surprises

1. **Inter-zone egress within the same region** -- GCP charges $0.01/GB for traffic between zones in the same region. AWS does this too, but GCP's global VPC model means all subnets are regional and traffic between zones is common. Multi-zone GKE clusters with chatty services can accumulate significant costs. A GKE cluster doing 5 TB/mo inter-zone pays ~$50/mo.

2. **Internet egress is more expensive than AWS** -- GCP standard tier internet egress starts at $0.085/GB (first 1 TB), but premium tier (default) is $0.12/GB for many regions. 10 TB/mo of premium egress costs ~$1,100/mo vs ~$850 on AWS.

3. **Cloud NAT per-VM minimum port allocation** -- Cloud NAT charges per gateway ($0.044/hr) plus $0.045/GB processed. But the minimum port allocation (64 ports per VM) can require multiple NAT gateways for large clusters, multiplying the hourly cost.

4. **Cloud Armor Enterprise** -- Cloud Armor Enterprise tier (adaptive protection, DDoS response team, threat intelligence) is a per-project subscription. Standard tier is usage-based but charges per policy, per rule, and per request -- a complex setup with many rules and high traffic can approach Enterprise pricing.

5. **Load balancer forwarding rule charges** -- each forwarding rule costs $0.025/hr (~$18/mo). Services with many ports or protocols need separate rules. A deployment with 10 forwarding rules pays ~$180/mo before any data processing.

6. **Premium vs Standard network tier** -- GCP defaults to Premium tier (global anycast, Google backbone). Standard tier uses ISP routing and is ~20-30% cheaper for egress but has higher latency and no global load balancing. Many teams pay Premium prices without realizing Standard tier exists.

## Reference Architectures

- [Google Cloud Architecture Center: Networking](https://cloud.google.com/architecture#networking) -- reference architectures for VPC design, hybrid connectivity, and load balancing
- [Google Cloud Architecture Framework: System design - Networking](https://cloud.google.com/architecture/framework/system-design/networking) -- best practices for VPC, firewall, and DNS design
- [Google Cloud: Hub-and-spoke network architecture](https://cloud.google.com/architecture/networking) -- reference design for multi-project networking with Shared VPC and VPC peering
- [Google Cloud: Best practices for Cloud Armor](https://cloud.google.com/armor/docs/best-practices) -- reference patterns for WAF, DDoS protection, and rate limiting at the edge
- [Google Cloud: Hybrid and multi-cloud network topologies](https://cloud.google.com/architecture/hybrid-and-multi-cloud-network-topologies) -- reference architectures for Cloud Interconnect, VPN, and hybrid DNS

## See Also

- `general/networking.md` -- general networking architecture patterns
- `providers/gcp/security.md` -- Cloud Armor, VPC Service Controls, and network security
- `providers/gcp/dns.md` -- Cloud DNS and service mesh DNS
- `providers/gcp/compute.md` -- Compute Engine network configuration
