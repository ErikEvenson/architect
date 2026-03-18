# Networking Failure Patterns

## Scope

Covers common networking failure patterns including misconfigured security groups, NAT gateway single points of failure, CIDR exhaustion, DNS failover gaps, TLS misconfiguration, and missing network segmentation. Does not cover general network architecture design (see `general/networking.md`) or provider-specific networking services (see `providers/` files).

## Checklist

- [ ] **[Critical]** **Misconfigured security groups allowing 0.0.0.0/0 ingress** — Goes wrong: database or internal services are exposed to the internet, leading to unauthorized access or data exfiltration. Happens because: engineers copy permissive rules from development environments or use overly broad rules to "get things working." Prevent by: enforcing least-privilege security group rules via IaC with automated policy checks (e.g., AWS Config rules, OPA policies), and scanning for public-facing resources continuously.

- [ ] **[Critical]** **Single NAT gateway serving all availability zones** — Goes wrong: when the AZ hosting the NAT gateway fails, all private subnets in other AZs lose internet connectivity, causing cascading application failures. Happens because: teams deploy one NAT gateway to save cost without considering the blast radius. Prevent by: deploying one NAT gateway per AZ so that an AZ failure only affects workloads in that AZ.

- [ ] **[Critical]** **No DNS failover or health-check-based routing** — Goes wrong: when a primary region or endpoint goes down, DNS continues sending traffic to the failed endpoint, causing full outage even when healthy replicas exist. Happens because: DNS is configured with simple routing and no health checks. Prevent by: configuring health-check-based failover routing policies (e.g., Route 53 health checks) and testing failover regularly.

- [ ] **[Critical]** **CIDR range exhaustion in VPC or subnets** — Goes wrong: new instances, pods, or ENIs cannot be launched because the IP address space is full, blocking scaling and deployments. Happens because: initial CIDR blocks are too small, or teams do not plan for growth in container/serverless workloads that consume many IPs. Prevent by: sizing VPC CIDRs generously (/16 or larger), using secondary CIDR blocks, and monitoring IP utilization with alerts at 70% capacity.

- [ ] **[Recommended]** **Unplanned cross-AZ data transfer costs** — Goes wrong: monthly bills spike dramatically due to high-volume cross-AZ traffic between application tiers or between services and databases. Happens because: services are deployed across AZs without considering data transfer charges, or chatty microservices make frequent cross-AZ calls. Prevent by: co-locating tightly coupled services in the same AZ where possible, using AZ-affinity routing, and monitoring cross-AZ data transfer metrics.

- [ ] **[Critical]** **Single load balancer without redundancy or health checks** — Goes wrong: the load balancer becomes a single point of failure, or it continues routing traffic to unhealthy backends causing user-facing errors. Happens because: health check intervals are too long, thresholds are too lenient, or custom health check endpoints do not verify actual service readiness. Prevent by: using managed load balancers with proper health check configuration (short intervals, realistic thresholds, deep health endpoints that verify downstream dependencies).

- [ ] **[Recommended]** **Missing VPC flow logs or network monitoring** — Goes wrong: security incidents go undetected, troubleshooting network issues takes hours instead of minutes, and compliance audits fail. Happens because: flow logs are seen as a cost item and disabled, or they are enabled but never analyzed. Prevent by: enabling flow logs on all VPCs, shipping them to a centralized logging platform, and setting up alerts for anomalous traffic patterns.

- [ ] **[Critical]** **Overlapping CIDR ranges between VPCs or with on-premises networks** — Goes wrong: VPC peering, transit gateway connections, or VPN tunnels fail to route traffic correctly, making multi-network connectivity impossible without redesigning the network. Happens because: teams provision VPCs independently without a central IP address management (IPAM) strategy. Prevent by: maintaining a centralized IPAM registry, using non-overlapping ranges from RFC 1918 space, and validating CIDR allocations in IaC CI checks.

- [ ] **[Recommended]** **No private endpoints for cloud services (S3, DynamoDB, etc.)** — Goes wrong: traffic to cloud services traverses the NAT gateway and public internet, increasing latency, cost, and attack surface. Happens because: teams are unaware of VPC endpoint options or deprioritize setting them up. Prevent by: deploying gateway endpoints (free) and interface endpoints for frequently accessed services, and routing policies that prefer private paths.

- [ ] **[Critical]** **TLS termination misconfigured or certificates expired** — Goes wrong: users see browser security warnings and abandon the site, or internal service-to-service traffic is unencrypted, allowing interception. Happens because: certificate renewal is manual, or TLS configuration uses weak ciphers and outdated protocols. Prevent by: using managed certificate services (ACM, Let's Encrypt) with auto-renewal, enforcing TLS 1.2+ with strong cipher suites, and alerting on certificate expiry 30 days in advance.

- [ ] **[Recommended]** **DNS TTL set too high for failover scenarios** — Goes wrong: after a failover event, clients continue using cached stale DNS records for hours, directing traffic to the failed endpoint. Happens because: high TTLs are set for performance and never revisited for failover use cases. Prevent by: using low TTLs (60-300 seconds) for records involved in failover, and testing that clients respect TTL values during failure drills.

- [ ] **[Critical]** **No network segmentation between application tiers** — Goes wrong: a compromised web server can directly access the database tier, enabling lateral movement and data exfiltration. Happens because: flat network architecture is simpler to set up and manage. Prevent by: implementing tiered subnets (public, private-app, private-data) with security groups and NACLs restricting traffic between tiers to only required ports and protocols.

- [ ] **[Critical]** **Transit gateway or peering connection without route table updates** — Goes wrong: connectivity between VPCs or to on-premises appears established but traffic does not flow, causing silent failures in cross-network communication. Happens because: the peering or transit gateway attachment is created but route tables in each VPC are not updated to direct traffic through the connection. Prevent by: automating route propagation in IaC, and including connectivity validation tests in the deployment pipeline.

- [ ] **[Recommended]** **Relying on public IPs for inter-service communication** — Goes wrong: traffic between internal services traverses the public internet unnecessarily, introducing latency, cost, and security risk. Happens because: services are configured with public DNS names or IPs instead of private addresses. Prevent by: using private DNS zones and service discovery so inter-service traffic stays within the VPC, and auditing for unnecessary public IP allocations.

## Why This Matters

Network failures are among the most disruptive and hardest to diagnose in production. A single misconfigured security group can expose sensitive data. A missing NAT gateway in one AZ can cascade into a full application outage. IP exhaustion can silently block scaling right when you need it most. These failures are preventable with deliberate design, but they compound rapidly when overlooked.

## Common Decisions (ADR Triggers)

- **NAT gateway topology** — one per AZ vs shared, cost vs resilience trade-off
- **CIDR planning strategy** — initial sizing, secondary CIDR policy, IPAM tool selection
- **DNS failover model** — active-passive vs active-active, TTL policy for failover records
- **Network segmentation depth** — flat vs tiered subnets, microsegmentation for zero-trust
- **VPC endpoint strategy** — which services get private endpoints, gateway vs interface endpoints
- **Cross-AZ traffic policy** — AZ-affinity routing vs even distribution, cost monitoring approach

## See Also

- `general/networking.md` — Network architecture design and segmentation patterns
- `general/security.md` — Security controls including firewall and access management
- `failures/security.md` — Security failure patterns related to network misconfiguration
- `general/tls-certificates.md` — TLS certificate management and renewal
