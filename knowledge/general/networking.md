# Networking

## Scope

Network topology, segmentation, addressing, load balancing, connectivity, and security for cloud, on-premises, and hybrid architectures. This file covers **what** networking decisions need to be made and the trade-offs involved. For provider-specific **how**, see the provider networking files. For DNS-specific hybrid design, see `general/hybrid-dns.md`.

## Checklist

- [ ] **[Critical]** What is the network topology and how many tiers does segmentation require? (classic 3-tier with public, private-app, private-data subnets vs. micro-segmented zero-trust with per-workload isolation vs. flat network with security groups only — 3-tier is well-understood and maps to compliance frameworks; micro-segmentation adds operational complexity but limits blast radius; flat networks are simpler but one compromised host can reach everything)
- [ ] **[Critical]** What CIDR ranges are allocated, and have they been validated against all connected networks? (plan for non-overlapping RFC 1918 space across all VPCs/VNets, on-prem networks, VPN peers, and acquired company networks; use a /16 per VPC for growth headroom and subdivide into /24 subnets per AZ per tier; overlapping CIDRs prevent VPC peering and VPN connectivity and require NAT translation layers that add latency and complexity — maintain a central IPAM registry)
- [ ] **[Critical]** How many availability zones does the network span, and is multi-region required? (minimum 2 AZs for HA, 3 recommended to survive an AZ failure while maintaining N+1 capacity; multi-region adds cross-region data transfer costs at $0.01-0.02/GB, requires global load balancing, and introduces data sovereignty questions; subnet-per-AZ design ensures AZ isolation so a subnet failure maps to exactly one AZ)
- [ ] **[Critical]** What load balancing strategy is required at each tier? (L4/TCP load balancer for non-HTTP protocols, database proxies, and east-west service traffic; L7/HTTP load balancer for path-based routing, header inspection, TLS termination, and WAF integration; internal LB for service-to-service traffic vs. external/internet-facing for user traffic — L7 adds 1-2ms latency but enables content-based routing, A/B testing, and connection draining; consider service mesh for fine-grained east-west traffic control in microservices architectures)
- [ ] **[Critical]** What are the firewall and security group rules between tiers? (default-deny with explicit allow rules per service port and source; separate security groups per application tier — web SG allows 443 from internet/WAF only, app SG allows traffic from web SG only, data SG allows traffic from app SG only; use prefix lists or security group references rather than IP-based rules to simplify management; review rules quarterly and remove unused rules — overly permissive rules accumulate over time and are the most common audit finding)
- [ ] **[Critical]** Is a WAF required, and where is it placed? (at CDN edge for volumetric attack mitigation closest to source; at load balancer for application-specific rules and tighter integration with backend; or both in layered defense — OWASP Core Rule Set for baseline protection, add custom rules for application-specific patterns; managed rule sets from AWS/Azure/Cloudflare reduce operational burden but may cause false positives that require tuning; WAF logging and monitoring are essential for ongoing rule refinement)
- [ ] **[Recommended]** How is DNS managed, and what failover strategy is used? (cloud-native DNS for simplicity — Route 53, Azure DNS, Cloud DNS; third-party DNS like Cloudflare or NS1 for multi-cloud or advanced traffic management; weighted routing for blue-green deployments; latency-based routing for multi-region; health-check-driven failover for active-passive DR — set TTLs to 60s or less on records involved in failover; DNS propagation delay means failover is never instantaneous regardless of TTL)
- [ ] **[Recommended]** How do private subnets access the internet for outbound traffic? (NAT gateway per AZ for high availability at ~$32/mo per gateway plus $0.045/GB processed; shared NAT gateway across AZs saves cost but creates cross-AZ traffic charges and a single point of failure; NAT instances for cost savings in dev/test; VPC endpoints / Private Link for AWS/Azure service access without traversing NAT — S3 gateway endpoints are free and should always be configured; evaluate egress-only internet gateways for IPv6 workloads)
- [ ] **[Recommended]** Is VPN or dedicated private connectivity needed to on-premises or other clouds? (site-to-site VPN for quick setup and low bandwidth needs — 1.25 Gbps per tunnel typical, use multiple tunnels with ECMP for higher throughput; dedicated connectivity — AWS Direct Connect, Azure ExpressRoute, GCP Cloud Interconnect — for consistent latency, higher bandwidth of 1-100 Gbps, and avoiding public internet; dedicated connectivity requires 1-3 month lead time and cross-connect fees; many architectures start with VPN and add dedicated connectivity when bandwidth or latency requirements demand it)
- [ ] **[Recommended]** Is a CDN needed for content delivery, and what caching strategy applies? (CDN for static assets, API acceleration, and DDoS absorption; CloudFront, Azure Front Door, Cloudflare, or Fastly — evaluate PoP locations relative to user base; cache static content aggressively with long TTLs; cache dynamic content carefully with short TTLs and cache keys that include relevant headers/cookies; CDN origin shield reduces origin load by consolidating cache misses through a single mid-tier PoP)
- [ ] **[Recommended]** Is network traffic inspection or monitoring required? (VPC flow logs for connection-level visibility — enable at minimum on VPC or subnet level for security auditing and troubleshooting; traffic mirroring for deep packet inspection by IDS/IPS appliances; managed network firewall services — AWS Network Firewall, Azure Firewall Premium — for TLS inspection and IDPS; flow log storage costs scale with traffic volume — filter to reject-only logs if full capture is cost-prohibitive)
- [ ] **[Recommended]** How is service discovery handled for internal services? (DNS-based discovery with private hosted zones for simple architectures; cloud-native service discovery — AWS Cloud Map, Azure Private DNS with AKS — for dynamic workloads; service mesh — Istio, Linkerd, Consul Connect — for microservices with mTLS, traffic splitting, and observability needs; Kubernetes kube-dns/CoreDNS for in-cluster discovery; avoid hardcoded IPs or hostnames in application configuration — use service discovery or configuration management)
- [ ] **[Optional]** Is IPv6 required or planned? (dual-stack preferred for new deployments to future-proof; IPv6-only supported on newer instance types and reduces NAT complexity; some services and third-party integrations do not yet support IPv6 — audit all dependencies before committing; government and education sectors increasingly mandate IPv6; ELBs and CloudFront support dual-stack natively)
- [ ] **[Optional]** Is network segmentation enforced beyond security groups, such as with a centralized inspection VPC or transit gateway? (hub-and-spoke with transit gateway for multi-VPC architectures — centralizes routing, firewall inspection, and shared services; transit gateway costs $0.05/GB processed which adds up at scale; spoke-to-spoke traffic through the hub adds latency; consider direct VPC peering for high-bandwidth, latency-sensitive spoke-to-spoke flows and transit gateway for everything else)

## Why This Matters

Network architecture is the hardest infrastructure decision to change after deployment. Re-numbering CIDR ranges, adding subnets, or changing segmentation models requires application downtime, configuration updates across every connected system, and coordination with every team that references network addresses. A VPC or VNet redesign is measured in weeks of effort and carries high risk of outages during migration. Getting the network right at design time avoids painful and expensive retrofits.

Poor network segmentation is the most common finding in cloud security audits and the primary enabler of lateral movement in breaches. A compromised web server in a flat network can reach the database directly. In a properly segmented architecture with security group chaining and private subnets, the same compromise is contained to the web tier with no direct path to data. The difference between these outcomes is entirely determined by decisions made during architecture design, not during incident response.

Network costs are often the most surprising line item in cloud bills. Cross-AZ data transfer ($0.01/GB in AWS), NAT gateway processing ($0.045/GB), and cross-region transfer ($0.02/GB) seem trivial per-gigabyte but compound rapidly at scale. A microservices architecture with chatty cross-AZ communication can generate thousands of dollars per month in transfer costs alone. Understanding these cost drivers at design time — and placing communicating services in the same AZ where possible — prevents budget surprises.

## Common Decisions (ADR Triggers)

### ADR: Network Topology and Segmentation Model

**Context:** The architecture requires network isolation between workload tiers with appropriate access controls.

**Options:**

| Criterion | 3-Tier Subnet Model | Micro-Segmented (Zero Trust) | Flat with Security Groups |
|---|---|---|---|
| Isolation level | Subnet-level with NACLs + SGs | Per-workload with identity-based policy | Security group only, shared subnets |
| Blast radius | Contained to tier (web/app/data) | Contained to individual workload | Entire network reachable on compromise |
| Operational complexity | Low — well-understood pattern | High — requires policy engine (Calico, NSX, Prisma) | Lowest — minimal network infrastructure |
| Compliance fit | Maps to PCI DSS, SOC 2 zone requirements | Exceeds most compliance frameworks | May not satisfy auditors for regulated data |
| Cost | Moderate — more subnets, more NAT gateways | Highest — overlay network, policy management | Lowest — fewer subnets and gateways |
| Best fit | Most production workloads | High-security, multi-tenant, container platforms | Dev/test, internal tools, small deployments |

**Decision drivers:** Compliance requirements (PCI, HIPAA, FedRAMP), number of distinct application tiers, team network expertise, and tolerance for operational complexity.

### ADR: Load Balancing Strategy

**Context:** The architecture must distribute traffic across compute instances with appropriate health checking and routing.

**Options:**
- **L4 (TCP/UDP) load balancer:** Passes connections without inspecting payload. Lowest latency, highest throughput, supports any TCP protocol. Cannot route based on HTTP path, host header, or content. Use for: database proxies, non-HTTP services, east-west traffic with extreme throughput requirements.
- **L7 (HTTP/HTTPS) load balancer:** Inspects HTTP headers and payload. Enables path-based routing (/api to backend, /static to CDN origin), host-based routing (api.example.com vs. www.example.com), header-based routing, WAF integration, and connection draining. Adds 1-2ms latency. Use for: web applications, API gateways, any HTTP-based service.
- **Global load balancer:** Distributes traffic across regions based on latency, geography, or health. Examples: AWS Global Accelerator, Azure Front Door, GCP Global LB. Provides anycast IPs, cross-region failover, and DDoS absorption. Use for: multi-region deployments, global user base.
- **Service mesh:** Sidecar proxy (Envoy) handles service-to-service load balancing with mTLS, retries, circuit breaking, and traffic splitting. High operational overhead. Use for: microservices architectures with 10+ services needing fine-grained traffic control.

**Decision drivers:** Protocol requirements (HTTP vs. TCP vs. gRPC), routing complexity, latency sensitivity, number of backend services, and whether WAF or TLS termination is needed at the load balancer.

### ADR: NAT Strategy for Private Subnet Egress

**Context:** Workloads in private subnets need outbound internet access for OS updates, API calls, and SaaS integrations.

**Options:**
- **NAT gateway per AZ:** Highest availability — AZ failure does not affect other AZs' egress. Cost: ~$32/month per gateway + $0.045/GB processed. Recommended for production.
- **Single shared NAT gateway:** Lower cost. Cross-AZ data transfer charges apply ($0.01/GB). Single point of failure — if the NAT gateway's AZ fails, all private subnet egress fails. Acceptable for dev/test.
- **NAT instances (self-managed):** EC2 instance with IP forwarding enabled. Cheapest option (t3.micro ~$8/month). Must manage HA, patching, and scaling manually. Suitable for cost-sensitive dev environments.
- **VPC endpoints / Private Link:** Bypass NAT entirely for cloud provider services (S3, DynamoDB, SQS, etc.) and supported SaaS products. Gateway endpoints (S3, DynamoDB) are free; interface endpoints cost ~$7/month per AZ plus $0.01/GB processed. Always configure free gateway endpoints; evaluate interface endpoints for high-volume service access.

**Recommendation:** NAT gateway per AZ for production, single NAT gateway or NAT instance for dev/test, and VPC gateway endpoints for S3/DynamoDB in all environments. For workloads making heavy outbound API calls, evaluate whether Private Link to the destination service exists to avoid NAT processing charges.

### ADR: Connectivity to On-Premises or Other Clouds

**Context:** The architecture requires private connectivity to on-premises data centers, branch offices, or other cloud providers.

**Options:**
- **Site-to-site VPN over internet:** Quick to set up (hours), low cost (~$35/month per VPN connection in AWS). Bandwidth limited to 1.25 Gbps per tunnel; use multiple tunnels with ECMP for higher throughput. Latency varies with internet path quality. Encrypted by default (IPsec). Good starting point; can coexist with dedicated connectivity.
- **Dedicated connectivity (Direct Connect, ExpressRoute, Cloud Interconnect):** Consistent latency, 1-100 Gbps bandwidth, does not traverse public internet. 1-3 month provisioning lead time, requires cross-connect at colocation facility. Higher cost (port fees + partner fees + cross-connect). Recommended when bandwidth exceeds 500 Mbps sustained or latency consistency is critical (database replication, real-time applications).
- **SD-WAN overlay:** Software-defined WAN using multiple transport links (MPLS, broadband, LTE). Provides intelligent path selection and application-aware routing. Useful for branch-to-cloud connectivity at scale. Adds vendor dependency and management layer.
- **Cloud-to-cloud transit:** For multi-cloud, use a hub VPC/VNet with VPN tunnels to each cloud, or third-party transit solutions (Aviatrix, Alkira). Native options: AWS Transit Gateway peering (same provider only), Megaport/Equinix Cloud Router (multi-cloud cross-connect).

**Decision drivers:** Required bandwidth, latency sensitivity, provisioning timeline, budget (CapEx port fees vs. OpEx VPN), number of sites, and regulatory requirements for private-only connectivity.

### ADR: CIDR Planning and IP Address Management

**Context:** The architecture must allocate IP address space that supports current needs and future growth without conflicts.

**Options:**
- **Large VPC CIDR (/16) with structured subnets:** Allocate a /16 per VPC (65,536 IPs), divide into /24 subnets per AZ per tier. Provides maximum growth headroom. Risk: consumes large chunks of RFC 1918 space, may conflict with other VPCs or on-prem if not centrally managed.
- **Right-sized VPC CIDR (/20-/22) with secondary CIDRs:** Start smaller, add secondary CIDR blocks when needed. Conserves address space. Risk: secondary CIDRs have restrictions (cannot be used with some VPN configurations, peering may not route secondary CIDRs in all providers).
- **IPv6 dual-stack:** Assign /56 IPv6 prefix per VPC (virtually unlimited addresses). Eliminates address exhaustion concerns long-term. Risk: not all services and integrations support IPv6 today; requires dual-stack testing.

**Recommendation:** Use a /16 per production VPC and a /20-/22 per dev/test VPC. Maintain a central IPAM spreadsheet or tool (NetBox, Infoblox, AWS IPAM) that is the single source of truth. Reserve at least 30% of address space for growth. Validate CIDR allocations against all connected networks before deployment — retrofitting a conflicting CIDR requires full network migration.

## See Also

- `providers/aws/vpc.md` — AWS VPC, subnets, and network configuration
- `providers/azure/networking.md` — Azure VNet and network services
- `providers/gcp/networking.md` — GCP VPC and network configuration
- `general/hybrid-dns.md` — Hybrid DNS resolution for cross-environment name resolution
- `general/security.md` — Security controls including network-layer protections
- `general/cost-optimization.md` — Cloud cost management including network transfer costs
- `patterns/network-segmentation.md` — Network segmentation patterns including micro-segmentation, trust zones, and compliance-driven isolation
