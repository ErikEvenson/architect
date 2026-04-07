# AWS Networking

## Scope

AWS networking services beyond VPC fundamentals. Covers Transit Gateway (multi-VPC, multi-account, multi-region, peering, route tables), Direct Connect (dedicated vs hosted, LAG, redundancy, MACsec), PrivateLink and VPC Endpoints (interface vs gateway, endpoint policies, producer-side endpoint services, Gateway Load Balancer endpoints), Network Firewall (stateful inspection, IDS/IPS, rule groups), Global Accelerator (anycast, endpoint groups), Route 53 Resolver (hybrid DNS forwarding), VPC Lattice (application-layer service-to-service), VPC peering vs Transit Gateway decision framework, NACLs vs Security Groups design philosophy, multi-account networking patterns, and IPv6 dual-stack adoption.

## Checklist

- [ ] **[Critical]** Is Transit Gateway used as the central hub for multi-VPC and multi-account connectivity, with route tables segmented by domain (production, non-production, shared services, edge) to enforce traffic isolation and prevent unintended lateral movement?
- [ ] **[Critical]** Is Direct Connect configured with redundant connections at diverse locations (at minimum, two connections at separate DX locations for production workloads; four connections across two locations for maximum resiliency per the AWS Well-Architected Framework)?
- [ ] **[Critical]** Are VPC Interface Endpoints and Gateway Endpoints deployed for frequently accessed AWS services (S3, DynamoDB, ECR, CloudWatch, STS, KMS, Secrets Manager), with endpoint policies restricting access to specific resources rather than using the default allow-all policy?
- [ ] **[Critical]** Is AWS Network Firewall deployed in a dedicated inspection VPC with Transit Gateway routing configured to force traffic through the firewall (east-west between VPCs, north-south to/from internet), using stateful rule groups for IDS/IPS and domain filtering?
- [ ] **[Recommended]** Is the Transit Gateway vs VPC Peering decision documented? (Transit Gateway for 3+ VPCs, centralized routing, traffic inspection, and multi-account; VPC Peering for 1-2 high-throughput point-to-point connections where no transitive routing or centralized inspection is needed)
- [ ] **[Recommended]** Is AWS Global Accelerator configured for latency-sensitive global applications, with endpoint groups in each active region, health checks tuned for rapid failover, and client affinity settings appropriate for the application's statefulness?
- [ ] **[Recommended]** Are PrivateLink-powered services (interface endpoints) deployed in each required AZ with DNS private hosted zone integration, and are endpoint security groups restricting access to authorized consumers only?
- [ ] **[Critical]** Are VPC endpoint policies applied to interface and gateway endpoints to restrict which IAM principals, accounts, and resources (e.g., specific S3 buckets, KMS keys, Secrets Manager secrets) can be accessed through the endpoint, forming part of a data-perimeter control to prevent exfiltration to attacker-controlled accounts?
- [ ] **[Recommended]** When exposing internal services to other VPCs or accounts via PrivateLink, is an endpoint service configured behind an NLB (or GWLB for inspection appliances) with explicit allowed principals, manual acceptance for cross-account consumers where appropriate, private DNS name verification via Route 53, and per-AZ availability matching consumer requirements?
- [ ] **[Recommended]** Where centralized traffic inspection is required for third-party NVAs (Palo Alto, Fortinet, Check Point), is a Gateway Load Balancer endpoint (GWLBe) pattern evaluated as an alternative to Network Firewall, with GWLB fronting an Auto Scaling group of appliances and GWLBe inserted into spoke VPC route tables for transparent inspection?
- [ ] **[Recommended]** Is Route 53 Resolver configured for hybrid DNS with inbound endpoints (on-premises resolves AWS private zones) and outbound endpoints (VPCs forward queries to on-premises DNS), with forwarding rules shared via AWS RAM across accounts?
- [ ] **[Recommended]** Is multi-account networking centralized in a dedicated network account, with Transit Gateway shared via AWS Resource Access Manager (RAM), Direct Connect gateway associated to the Transit Gateway, and Network Firewall inspection managed centrally?
- [ ] **[Recommended]** Is NACLs vs Security Groups design intentional? (Security Groups as the primary stateful firewall at the ENI level with source-SG references; NACLs as a stateless secondary layer for subnet-level broad deny rules, emergency blocking, and compliance requirements that mandate defense-in-depth)
- [ ] **[Optional]** Is VPC Lattice evaluated for service-to-service communication across VPCs and accounts? (L7 routing with path-based and weighted rules, IAM auth policies, built-in observability, eliminates Transit Gateway for east-west application traffic; best for microservice architectures)
- [ ] **[Optional]** Is IPv6 dual-stack planned for workloads that require it? (egress-only internet gateway for IPv6 outbound, dual-stack subnets, Security Groups and NACLs must include IPv6 rules, verify all services in the path support IPv6 — ALB, NLB, CloudFront, S3, and API Gateway do; some services have limited IPv6 support)
- [ ] **[Optional]** Is Direct Connect MACsec encryption enabled for connections that require link-layer encryption? (available on dedicated 10 Gbps and 100 Gbps connections at supported locations; provides wire-speed encryption without throughput penalty; not available on hosted connections)

## Why This Matters

AWS networking services form the connective tissue between every workload, account, and region. A poorly designed Transit Gateway topology creates routing black holes or allows lateral movement between environments that should be isolated. Missing Direct Connect redundancy means a single fiber cut takes down hybrid connectivity to an entire region. Overly permissive VPC endpoint policies allow any principal in the VPC to access services they should not reach, bypassing IAM policies that assume traffic arrives from the public endpoint.

Network Firewall fills the gap between Security Groups (which cannot inspect payload content) and third-party appliances (which require managing EC2 instances, licensing, and scaling). Without centralized traffic inspection, east-west traffic between VPCs traverses Transit Gateway without any deep packet inspection, meaning a compromised workload in one VPC can communicate freely with resources in another.

The Transit Gateway vs VPC Peering decision has long-term cost and operational implications. Transit Gateway charges $0.02/GB for data processing, which is significant at high throughput, but VPC Peering does not support transitive routing or centralized inspection. Choosing the wrong model early leads to a painful re-architecture as the network grows. Similarly, skipping Global Accelerator for latency-sensitive global applications forces traffic through the public internet, adding 50-200ms of latency that a global anycast network eliminates.

## Common Decisions (ADR Triggers)

- **Transit Gateway vs VPC Peering** -- Transit Gateway provides centralized routing, transitive connectivity, traffic inspection insertion, and scales to thousands of VPCs but charges $0.02/GB data processing; VPC Peering is free for data transfer (same-region), lower latency, but non-transitive and unmanageable beyond a handful of connections
- **Direct Connect dedicated vs hosted** -- dedicated connections (1/10/100 Gbps) provide a physical port you own with MACsec encryption support and LAG aggregation; hosted connections (50 Mbps-10 Gbps) are provisioned by a partner with lower commitment but no MACsec and shared infrastructure
- **Direct Connect redundancy model** -- single connection (dev/test only), dual connections at one location (tolerates device failure), dual connections at two locations (tolerates facility failure, recommended minimum for production), four connections at two locations (maximum resiliency)
- **Network Firewall vs third-party NVA** -- managed service with AWS-native integration, auto-scaling, and Suricata-compatible rules vs Palo Alto, Fortinet, or Check Point for teams with existing rule sets, advanced features (SSL/TLS decryption with custom CAs), or multi-cloud consistency
- **Centralized vs distributed inspection** -- centralized inspection VPC with Transit Gateway routing (simpler management, single chokepoint) vs distributed firewall endpoints per VPC (lower latency, higher throughput, more complex management)
- **VPC endpoint strategy** -- deploy interface endpoints in every VPC (simple routing, higher cost) vs centralized endpoints in a shared services VPC accessed via Transit Gateway (lower cost, adds Transit Gateway data processing charges and latency)
- **PrivateLink producer pattern** -- expose internal services to consumers via NLB-backed endpoint service (L4, TLS passthrough, allowed-principals authorization, no transitive networking required) vs VPC peering / Transit Gateway (full L3 reachability, requires non-overlapping CIDRs, broader blast radius); PrivateLink is preferred for SaaS-style one-to-many exposure and cross-account boundaries where the producer wants no routing relationship to consumer VPCs
- **Centralized inspection: Network Firewall vs Gateway Load Balancer** -- Network Firewall is AWS-managed with Suricata rules and no appliance management; GWLB + GWLBe enables third-party NVAs (Palo Alto, Fortinet, Check Point) with existing rule sets, SSL/TLS decryption with custom CAs, and multi-cloud rule consistency, at the cost of managing the appliance fleet
- **Global Accelerator vs CloudFront** -- Global Accelerator for non-HTTP/TCP/UDP workloads, gaming, IoT, and static IP requirements; CloudFront for HTTP/S content delivery with caching; both use the AWS global edge network
- **VPC Lattice vs Transit Gateway for service mesh** -- VPC Lattice for L7 service-to-service with IAM auth and path-based routing (application team-managed); Transit Gateway for L3/L4 network connectivity (network team-managed); can coexist
- **IPv6 adoption strategy** -- dual-stack from day one (avoids retrofit), IPv6-only for new workloads (simplifies addressing, reduces NAT costs), or IPv4-only with future migration plan

## Pricing Links

### AWS Pricing Pages

- [Transit Gateway Pricing](https://aws.amazon.com/transit-gateway/pricing/) — $0.05/hr per attachment + $0.02/GB data processed
- [Direct Connect Pricing](https://aws.amazon.com/directconnect/pricing/) — port-hour fees by speed (1 Gbps: ~$0.30/hr, 10 Gbps: ~$1.50/hr) + data transfer out rates by region
- [PrivateLink / VPC Endpoint Pricing](https://aws.amazon.com/privatelink/pricing/) — interface endpoints: $0.01/hr per AZ + $0.01/GB data processed; Gateway endpoints (S3, DynamoDB): free
- [AWS Network Firewall Pricing](https://aws.amazon.com/network-firewall/pricing/) — $0.395/hr per firewall endpoint + $0.065/GB data processed
- [Global Accelerator Pricing](https://aws.amazon.com/global-accelerator/pricing/) — $0.025/hr per accelerator + $0.015-$0.035/GB data transfer premium (varies by region)
- [VPC Peering Pricing](https://aws.amazon.com/vpc/pricing/) — no charge for peering connection; standard cross-AZ ($0.01/GB) and cross-region data transfer rates apply
- [VPC Lattice Pricing](https://aws.amazon.com/vpc/lattice/pricing/) — $0.025/hr per service + $0.025/GB data processed
- [AWS Pricing Calculator](https://calculator.aws/) — interactive cost estimation tool

### Common Cost Surprises

1. **Transit Gateway data processing at scale** — $0.02/GB applies to all traffic traversing the Transit Gateway. A hub-spoke architecture with 20 TB/mo of east-west traffic pays $400/mo in data processing alone. VPC Peering for high-throughput same-region connections avoids this charge entirely.

2. **Network Firewall always-on cost** — each firewall endpoint costs $0.395/hr (~$288/mo) regardless of traffic volume. Deploying in 3 AZs across an inspection VPC costs ~$864/mo before any data processing charges. Plus $0.065/GB processed. A production deployment inspecting 10 TB/mo pays ~$1,514/mo.

3. **Interface endpoint multiplication** — each interface endpoint costs $0.01/hr per AZ (~$7.20/mo per AZ). Deploying 10 endpoints across 3 AZs costs $216/mo. In a multi-account environment with endpoints per VPC, costs multiply rapidly. Centralizing endpoints in a shared VPC reduces cost but adds Transit Gateway charges.

4. **Direct Connect data transfer asymmetry** — inbound data over Direct Connect is free, but outbound data transfer rates vary by region ($0.02-$0.08/GB). A workload sending 10 TB/mo outbound over Direct Connect in US East pays ~$200/mo in transfer charges alone, on top of port fees.

5. **Global Accelerator data transfer premium** — Global Accelerator charges a DT premium on top of standard EC2 data transfer. For US/EU traffic this adds ~$0.015/GB. An application serving 50 TB/mo globally pays ~$750/mo in accelerator DT premium plus the $18/mo base fee.

6. **Transit Gateway inter-region peering** — inter-region peering connections incur standard cross-region data transfer rates ($0.02/GB) in addition to the per-attachment hourly charge. Multi-region architectures with significant cross-region traffic should evaluate whether direct inter-region VPC peering is cheaper for specific high-throughput paths.

## Reference Links

- [AWS Transit Gateway Documentation](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html) — architecture, route tables, multicast, peering, and Connect attachments
- [AWS Direct Connect User Guide](https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html) — connection types, LAG, virtual interfaces, MACsec, and resiliency recommendations
- [AWS PrivateLink Documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) — interface endpoints, gateway endpoints, endpoint services, and endpoint policies
- [Create an endpoint service (PrivateLink producer)](https://docs.aws.amazon.com/vpc/latest/privatelink/create-endpoint-service.html) — NLB/GWLB-backed endpoint services, allowed principals, acceptance settings, and private DNS name verification
- [VPC endpoint policies](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-access.html) — resource-policy syntax for restricting principals, actions, and resources reachable through interface and gateway endpoints (data-perimeter pattern)
- [Gateway Load Balancer Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/introduction.html) — GENEVE-encapsulated traffic insertion to third-party security appliances via PrivateLink (GWLBe)
- [AWS Network Firewall Documentation](https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html) — deployment models, stateful/stateless rule groups, Suricata-compatible rules, and logging
- [AWS Global Accelerator Documentation](https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html) — standard vs custom routing accelerators, endpoint groups, and health checks
- [Amazon VPC Lattice Documentation](https://docs.aws.amazon.com/vpc-lattice/latest/ug/what-is-vpc-lattice.html) — service networks, services, target groups, listeners, auth policies, and observability
- [AWS Architecture Center: Networking & Content Delivery](https://aws.amazon.com/architecture/networking-content-delivery/) — curated reference architectures for multi-VPC, hybrid, and global networking
- [AWS Prescriptive Guidance: Multi-account network architecture](https://docs.aws.amazon.com/prescriptive-guidance/latest/robust-network-design-control-tower/) — Transit Gateway hub-spoke with centralized inspection for AWS Organizations
- [AWS Direct Connect Resiliency Recommendations](https://aws.amazon.com/directconnect/resiliency-recommendation/) — interactive tool for selecting the appropriate redundancy model

---

## See Also

- `providers/aws/vpc.md` — VPC fundamentals: CIDR planning, subnets, NAT Gateways, Security Groups, and route tables
- `providers/aws/route53.md` — Route 53 hosted zones, routing policies, health checks, DNSSEC, and Resolver endpoints
- `providers/aws/multi-account.md` — AWS Organizations, Transit Gateway sharing via RAM, and centralized network account patterns
- `providers/aws/cloudfront-waf.md` — CloudFront CDN and WAF for edge protection (complements Global Accelerator)
- `general/networking.md` — Cloud-agnostic networking patterns including segmentation and load balancing
