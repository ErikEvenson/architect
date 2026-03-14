# AWS VPC Design

## Checklist

- [ ] What CIDR block size for the VPC? (Plan for growth; /16 gives 65K IPs, avoid overlaps with peered VPCs and on-premises ranges)
- [ ] How many tiers of subnets? (public, private-app, private-data, private-management is a common four-tier model)
- [ ] Are subnets sized correctly per AZ? (each subnet loses 5 IPs to AWS; ensure room for ENIs, Lambda, EKS pods)
- [ ] Is a NAT Gateway deployed per AZ for high availability, or is a shared NAT Gateway acceptable for cost savings?
- [ ] Are VPC Endpoints (Gateway and Interface) configured for S3, DynamoDB, ECR, CloudWatch, STS, and other frequently used services to avoid NAT costs and improve security?
- [ ] Are Security Groups following least-privilege with source-based references (other SGs, prefix lists) rather than broad CIDR rules?
- [ ] Are NACLs used as a secondary stateless defense layer at subnet boundaries, with explicit deny rules for known bad ranges?
- [ ] Is VPC Flow Logs enabled and shipping to CloudWatch Logs or S3 for network forensics and anomaly detection?
- [ ] Is Transit Gateway used for multi-VPC or multi-account connectivity instead of a mesh of VPC peering connections?
- [ ] Are route tables correctly segmented so public subnets route through IGW, private subnets through NAT, and isolated subnets have no internet route?
- [ ] Is DNS resolution enabled (enableDnsSupport, enableDnsHostnames) for private hosted zone and VPC endpoint DNS?
- [ ] Are secondary CIDR blocks planned if the primary range may be exhausted (e.g., high-density EKS workloads)?
- [ ] Is IPv6 dual-stack needed for any workloads, and are egress-only internet gateways configured accordingly?
- [ ] Are prefix lists used for managing CIDR groups referenced across multiple security groups and route tables?

## Why This Matters

VPC design is the foundation of every AWS deployment and is extremely costly to change after resources are provisioned. Undersized CIDRs force painful migrations. Missing VPC endpoints leak traffic through NAT Gateways at $0.045/GB. Overly permissive security groups are the most common audit finding. Poor subnet planning blocks future EKS or Lambda scaling.

## Common Decisions (ADR Triggers)

- **CIDR allocation strategy** -- centralized IPAM vs per-team allocation, RFC 1918 vs 100.64.0.0/10 for non-routable ranges
- **NAT Gateway topology** -- per-AZ (resilient) vs shared (cheaper), NAT Gateway vs NAT instance for dev environments
- **VPC Endpoint selection** -- which services justify Interface endpoints ($7.20/mo each) vs Gateway endpoints (free)
- **Transit Gateway vs VPC Peering** -- centralized hub-spoke vs point-to-point for small account counts
- **Security Group management** -- Terraform modules vs AWS Firewall Manager policies across accounts
- **Multi-account VPC strategy** -- shared VPC (RAM) vs dedicated VPCs per account with Transit Gateway
