# AWS VPC Design

## Scope

AWS Virtual Private Cloud network design. Covers CIDR planning, subnet tiers, NAT Gateways, VPC Endpoints (Gateway and Interface), Security Groups, NACLs, Transit Gateway, Flow Logs, VPC Lattice, and Verified Access.

## Checklist

- [ ] **[Critical]** What CIDR block size for the VPC? (Plan for growth; /16 gives 65K IPs, avoid overlaps with peered VPCs and on-premises ranges)
- [ ] **[Critical]** How many tiers of subnets? (public, private-app, private-data, private-management is a common four-tier model)
- [ ] **[Critical]** Are subnets sized correctly per AZ? (each subnet loses 5 IPs to AWS; ensure room for ENIs, Lambda, EKS pods)
- [ ] **[Recommended]** Is a NAT Gateway deployed per AZ for high availability, or is a shared NAT Gateway acceptable for cost savings?
- [ ] **[Recommended]** Are VPC Endpoints (Gateway and Interface) configured for S3, DynamoDB, ECR, CloudWatch, STS, and other frequently used services to avoid NAT costs and improve security?
- [ ] **[Critical]** Are Security Groups following least-privilege with source-based references (other SGs, prefix lists) rather than broad CIDR rules?
- [ ] **[Optional]** Are NACLs used as a secondary stateless defense layer at subnet boundaries, with explicit deny rules for known bad ranges?
- [ ] **[Recommended]** Is VPC Flow Logs enabled and shipping to CloudWatch Logs or S3 for network forensics and anomaly detection?
- [ ] **[Recommended]** Is Transit Gateway used for multi-VPC or multi-account connectivity instead of a mesh of VPC peering connections?
- [ ] **[Critical]** Are route tables correctly segmented so public subnets route through IGW, private subnets through NAT, and isolated subnets have no internet route?
- [ ] **[Recommended]** Is DNS resolution enabled (enableDnsSupport, enableDnsHostnames) for private hosted zone and VPC endpoint DNS?
- [ ] **[Optional]** Are secondary CIDR blocks planned if the primary range may be exhausted (e.g., high-density EKS workloads)?
- [ ] **[Optional]** Is IPv6 dual-stack needed for any workloads, and are egress-only internet gateways configured accordingly?
- [ ] **[Optional]** Are prefix lists used for managing CIDR groups referenced across multiple security groups and route tables?
- [ ] **[Optional]** Evaluate VPC Lattice for application-layer service-to-service networking; provides service discovery, traffic management, and access controls across VPCs and accounts without Transit Gateway or VPC peering; supports weighted routing, HTTP/gRPC path-based routing, and IAM auth policies at the service network level
- [ ] **[Optional]** Evaluate AWS Verified Access for zero-trust access to corporate applications without a VPN; validates user identity and device posture against trust providers (IAM Identity Center, Okta, CrowdStrike, Jamf) before granting access to internal applications behind a Verified Access endpoint

## Why This Matters

VPC design is the foundation of every AWS deployment and is extremely costly to change after resources are provisioned. Undersized CIDRs force painful migrations. Missing VPC endpoints leak traffic through NAT Gateways at $0.045/GB. Overly permissive security groups are the most common audit finding. Poor subnet planning blocks future EKS or Lambda scaling.

## Common Decisions (ADR Triggers)

- **CIDR allocation strategy** -- centralized IPAM vs per-team allocation, RFC 1918 vs 100.64.0.0/10 for non-routable ranges
- **NAT Gateway topology** -- per-AZ (resilient) vs shared (cheaper), NAT Gateway vs NAT instance for dev environments
- **VPC Endpoint selection** -- which services justify Interface endpoints ($7.20/mo each) vs Gateway endpoints (free)
- **Transit Gateway vs VPC Peering** -- centralized hub-spoke vs point-to-point for small account counts
- **Security Group management** -- Terraform modules vs AWS Firewall Manager policies across accounts
- **Multi-account VPC strategy** -- shared VPC (RAM) vs dedicated VPCs per account with Transit Gateway
- **Service-to-service networking** -- VPC Lattice (application-layer, L7 routing, IAM auth) vs Transit Gateway (network-layer, L3/L4) vs VPC peering (simple point-to-point); VPC Lattice is ideal for microservice connectivity across VPCs and accounts with built-in observability
- **Corporate application access** -- AWS Verified Access (zero-trust, no VPN, identity+device posture) vs Client VPN vs Direct Connect for internal application access

## Pricing Links

### AWS Pricing Pages

- [VPC Pricing](https://aws.amazon.com/vpc/pricing/) — VPC itself is free; charges apply for NAT Gateways, VPC Endpoints, Traffic Mirroring, and IP addresses
- [NAT Gateway Pricing](https://aws.amazon.com/vpc/pricing/) — $0.045/hr + $0.045/GB data processed
- [AWS Data Transfer Pricing](https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer) — egress, cross-AZ, cross-region, and internet-bound transfer rates
- [VPC Endpoint Pricing](https://aws.amazon.com/privatelink/pricing/) — Interface endpoints: $0.01/hr per AZ + $0.01/GB; Gateway endpoints (S3, DynamoDB): free
- [Elastic IP Pricing](https://aws.amazon.com/vpc/pricing/) — $0.005/hr for unattached EIPs; $0.005/hr for each public IPv4 address (as of Feb 2024)
- [Transit Gateway Pricing](https://aws.amazon.com/transit-gateway/pricing/) — $0.05/hr per attachment + $0.02/GB data processed
- [AWS Direct Connect Pricing](https://aws.amazon.com/directconnect/pricing/) — port-hour fees by speed + data transfer out rates
- [VPC Flow Logs Pricing](https://aws.amazon.com/cloudwatch/pricing/) — charged via CloudWatch Logs ingestion ($0.50/GB) or S3 ($0.25/GB for flow logs)
- [AWS Pricing Calculator](https://calculator.aws/) — interactive cost estimation tool

### Common Cost Surprises

1. **NAT Gateway data processing charges** — $0.045/GB on top of the $0.045/hr hourly charge. A workload pulling 1 TB/mo through NAT costs ~$78/mo (hourly + data). Use VPC Gateway Endpoints for S3/DynamoDB traffic to avoid this entirely.

2. **Cross-AZ data transfer** — $0.01/GB each way ($0.02/GB round-trip) between Availability Zones. This is invisible in most architectures but adds up with chatty microservices. A service doing 10 TB/mo cross-AZ pays ~$200/mo.

3. **Public IPv4 address charges** — since February 2024, AWS charges $0.005/hr (~$3.60/mo) for every public IPv4 address, including those on EC2, ELBs, NAT Gateways, and RDS. An account with 50 public IPs pays ~$180/mo.

4. **Interface VPC Endpoint costs** — each Interface Endpoint costs $0.01/hr per AZ (~$7.20/mo per AZ). Deploying in 3 AZs costs $21.60/mo per endpoint. With 10+ endpoints, this reaches $200+/mo. Only create endpoints for heavily-used services.

5. **Transit Gateway data processing** — $0.02/GB processed. High-throughput hub-spoke architectures can see significant charges. 10 TB/mo through Transit Gateway costs $200/mo in data processing alone.

6. **VPC Flow Logs volume** — high-traffic environments generate massive log volumes. A busy VPC can produce 100+ GB/day of flow logs. At $0.50/GB (CloudWatch) that is $1,500/mo. Use S3 destination ($0.25/GB) and sampling where possible.

## Reference Architectures

- [AWS VPC Design and Network Architecture](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-example-web-database-servers.html) -- official VPC scenarios including public/private subnet designs, NAT, and VPN connectivity
- [AWS Architecture Center: Networking & Content Delivery](https://aws.amazon.com/architecture/networking-content-delivery/) -- curated reference architectures for multi-VPC, hybrid networking, and Transit Gateway designs
- [AWS Well-Architected Labs: Networking](https://www.wellarchitectedlabs.com/reliability/) -- hands-on labs for building resilient network architectures
- [AWS Prescriptive Guidance: Network architecture for multi-account environments](https://docs.aws.amazon.com/prescriptive-guidance/latest/robust-network-design-control-tower/) -- best practices for VPC design in AWS Organizations with Control Tower
- [AWS Quick Start: VPC with public and private subnets](https://aws.amazon.com/quickstart/architecture/vpc/) -- deployable reference architecture for standard multi-tier VPC design

---

## See Also

- `general/networking.md` -- General networking patterns including segmentation and load balancing
- `providers/aws/multi-account.md` -- Transit Gateway hub-and-spoke for cross-account VPC connectivity
- `providers/aws/ec2-asg.md` -- EC2 placement in VPC subnets with security groups
- `providers/aws/route53.md` -- Route 53 Resolver for hybrid DNS with VPC integration
- `providers/aws/networking.md` -- AWS networking services beyond VPC: Transit Gateway, Direct Connect, PrivateLink, Network Firewall, Global Accelerator
