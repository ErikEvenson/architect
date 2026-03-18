# AWS Route 53

## Scope

AWS managed DNS and traffic routing. Covers public/private hosted zones, routing policies (simple, weighted, latency, failover, geolocation, geoproximity, multi-value), health checks, DNSSEC, Resolver endpoints for hybrid DNS, and DNS Firewall.

## Checklist

- [ ] **[Critical]** Choose hosted zone type: public (resolves from the internet) vs private (resolves only within associated VPCs); a domain can have both for split-horizon DNS serving different records internally vs externally
- [ ] **[Recommended]** Use alias records instead of CNAME for zone apex (naked domain) pointing to AWS resources (ALB, CloudFront, S3, API Gateway, Global Accelerator); alias records are free (no query charges) and resolve faster than CNAME
- [ ] **[Critical]** Select routing policy based on requirements: simple (single resource), weighted (traffic splitting for canary/blue-green, 0-255 weights), latency-based (nearest region), failover (active/passive DR), geolocation (country/continent routing), geoproximity (bias-adjustable), multi-value answer (up to 8 healthy random records)
- [ ] **[Critical]** Configure health checks for all failover and routing policy records: endpoint checks (HTTP/HTTPS/TCP, 10 or 30 second intervals, from 8+ global locations), calculated checks (combine multiple checks with AND/OR logic), CloudWatch alarm-based checks (for non-IP resources)
- [ ] **[Recommended]** Set health check thresholds appropriately: failure threshold (1-10, default 3 consecutive failures), request interval (10 seconds at $1/month or 30 seconds at $0.50/month), and regions to check from (minimum 3 recommended)
- [ ] **[Recommended]** Enable DNSSEC signing for public hosted zones to protect against DNS spoofing; requires a KMS key (asymmetric, ECC_NIST_P256) in us-east-1 for the Key Signing Key (KSK); establish a chain of trust with DS record at the registrar
- [ ] **[Critical]** Configure Route 53 Resolver for hybrid DNS: inbound endpoints (on-premises resolves AWS private hosted zones, $0.125/hour per ENI) and outbound endpoints (VPC resolves on-premises DNS via forwarding rules, $0.125/hour per ENI)
- [ ] **[Critical]** Set appropriate TTL values: lower TTL (60s) for records that may change during failover or deployment; higher TTL (300-3600s) for stable records to reduce query costs and improve resolution speed; alias records inherit the target resource's TTL
- [ ] **[Optional]** Use Route 53 domain registration for automatic hosted zone creation and DNS management; supports domain transfer with transfer lock and privacy protection (WHOIS redaction free for supported TLDs)
- [ ] **[Recommended]** Configure Resolver DNS Firewall to block DNS queries to known malicious domains or allow-list only approved domains; operates on VPC-level with rule group associations and priority ordering
- [ ] **[Recommended]** Enable query logging for public hosted zones (to CloudWatch Logs) or Resolver query logging for VPC DNS queries (to CloudWatch Logs, S3, or Kinesis Data Firehose) for security analysis and troubleshooting
- [ ] **[Recommended]** Design for multi-account DNS: centralized hosted zones in a shared services account with cross-account IAM roles for record management, or Route 53 Resolver rules shared via AWS RAM for consistent hybrid DNS across accounts

## Why This Matters

DNS is the entry point for every application and a single point of failure if misconfigured. Route 53 is designed for 100% availability SLA -- one of the few AWS services with this guarantee -- but improper health check configuration, missing failover records, or incorrect TTL settings can still cause outages from the application's perspective. DNS propagation delays mean that mistakes take minutes to hours to fully resolve depending on TTL values cached by resolvers worldwide.

Route 53 pricing is based on hosted zones ($0.50/month per zone), queries ($0.40 per million standard queries, $0.60 for latency/geo), and health checks ($0.50-$1.00/month each). For most architectures DNS costs are minimal, but the operational impact of DNS misconfiguration is severe -- routing traffic to unhealthy endpoints, exposing internal records publicly, or failing to resolve entirely can take down an entire application stack.

Hybrid DNS (connecting on-premises DNS with AWS VPC DNS) is one of the most common sources of connectivity issues in hybrid cloud architectures. Resolver endpoints bridge this gap but require proper security group configuration and understanding of DNS forwarding direction.

## Common Decisions (ADR Triggers)

- **Routing policy selection** -- Simple routing for single-endpoint applications. Weighted routing for gradual traffic migration (canary deployments: 1% to new version, 99% to old). Latency-based routing for multi-region deployments where users should reach the nearest region. Failover routing for active/passive disaster recovery with a primary and secondary endpoint. Geolocation for compliance requirements mandating users in specific countries reach specific endpoints. Multi-value answer as a basic client-side load balancer returning up to 8 healthy IPs.
- **Active/passive vs active/active failover** -- Active/passive uses failover routing with a primary record (health-checked) and a secondary record (standby). Simple to implement but wastes standby resources and has DNS TTL-dependent failover time. Active/active uses latency-based or weighted routing with health checks on all records; unhealthy endpoints are automatically removed from responses. Active/active is more efficient but requires all regions to handle production traffic independently.
- **Public vs private hosted zone (split-horizon DNS)** -- Split-horizon DNS serves different records for the same domain depending on whether the query originates from within the VPC (private zone) or from the internet (public zone). Internal services resolve to private IPs; external users resolve to public-facing load balancers. This avoids hairpinning traffic through NAT gateways and simplifies internal service discovery. Requires associated VPCs on the private hosted zone.
- **Route 53 Resolver vs custom DNS servers in VPC** -- Route 53 Resolver endpoints are managed, highly available (deploy ENIs in 2+ AZs), and integrate with AWS RAM for multi-account sharing. Custom DNS servers (BIND, Unbound on EC2) provide more flexibility (custom zones, complex forwarding logic) but require instance management and HA design. Use Resolver endpoints for straightforward hybrid DNS; custom DNS only for edge cases requiring advanced DNS features.
- **Centralized vs decentralized DNS management** -- Centralized: one account owns the parent hosted zone, creates subdomains, and delegates via NS records to other accounts. Provides control, consistency, and easier auditing. Decentralized: each team/account manages its own hosted zone. Provides autonomy but risks inconsistency and makes global DNS changes harder. Most organizations use a hybrid: centralized parent zone with delegated subdomains per team.
- **DNSSEC enablement** -- DNSSEC protects against DNS cache poisoning and man-in-the-middle attacks by cryptographically signing DNS responses. Required for some compliance frameworks (FedRAMP, government). Adds operational complexity: key rotation, chain of trust management with registrar, and risk of DNSSEC-related outages if signing breaks. Not needed for purely internal applications using private hosted zones.

## Reference Architectures

### Multi-Region Active/Active with Automatic Failover
Route 53 latency-based routing -> ALBs in us-east-1 and eu-west-1. Health checks on each ALB endpoint (HTTPS, /health, 10-second interval, failure threshold 2). If one region fails health checks, Route 53 stops returning that region's IP. Low TTL (60s) on latency records for faster failover. CloudWatch alarm on Route 53 HealthCheckStatus metric for alerting.

### Hybrid DNS (AWS + On-Premises)
Route 53 Resolver: inbound endpoints (2 ENIs in private subnets) for on-premises DNS servers to forward AWS domain queries. Outbound endpoints (2 ENIs) with forwarding rules for on-premises domain queries (e.g., corp.internal -> on-premises DNS). Forwarding rules shared via AWS RAM to all VPCs in the organization. Private hosted zones associated with all VPCs needing resolution.

### Blue/Green Deployment with DNS
Route 53 weighted routing: blue environment at 100%, green at 0%. After green deployment validated, shift weights gradually (0/100 -> 10/90 -> 50/50 -> 100/0). Health checks on both environments. TTL set to 60 seconds to limit stale cache impact. Rollback by shifting weight back to blue. Works across regions, accounts, and even cloud providers.

### Global Application with Compliance Routing
Route 53 geolocation routing: EU users -> eu-west-1 (GDPR-compliant region), US users -> us-east-1, Asia users -> ap-southeast-1. Default record for unmatched locations pointing to nearest region via latency-based routing. Health checks on all endpoints with failover to the geographically next-closest region. DNSSEC enabled for the public hosted zone. Query logging enabled for audit trail of geographic routing decisions.

---

## See Also

- `general/hybrid-dns.md` -- Hybrid DNS patterns for on-premises and cloud integration
- `providers/aws/cloudfront-waf.md` -- CloudFront distributions using Route 53 alias records
- `providers/aws/vpc.md` -- VPC DNS resolution and Route 53 Resolver endpoint configuration
