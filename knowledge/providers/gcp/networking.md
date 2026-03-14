# GCP Networking

## Checklist

- [ ] Is the VPC configured as a custom-mode VPC (not auto-mode) with explicitly planned subnets per region and secondary ranges for GKE pods/services?
- [ ] Are firewall rules using service accounts or network tags for targeting instead of IP-based rules, following least-privilege with explicit deny rules logged?
- [ ] Is Cloud CDN enabled on the external HTTP(S) Load Balancer for static content, with cache modes (CACHE_ALL_STATIC, USE_ORIGIN_HEADERS, FORCE_CACHE_ALL) configured per backend?
- [ ] Is Cloud Armor configured with security policies on the load balancer, including preconfigured WAF rules (OWASP Top 10), rate limiting, and adaptive protection?
- [ ] Is the appropriate load balancer type selected? (external global HTTP(S) for web apps, internal regional TCP/UDP for internal services, external regional network for non-HTTP)
- [ ] Is Private Google Access enabled on subnets hosting VMs without external IPs to allow access to Google APIs and services?
- [ ] Are Private Service Connect endpoints configured for managed services (Cloud SQL, Memorystore, Vertex AI) to avoid public IP exposure?
- [ ] Is Cloud NAT configured per region for outbound internet access from private VMs, with minimum ports per VM and endpoint-independent mapping?
- [ ] Is Shared VPC used for multi-project networking, with host and service projects correctly configured and IAM permissions scoped?
- [ ] Is Cloud Interconnect (Dedicated or Partner) or Cloud VPN configured for hybrid connectivity with redundant tunnels?
- [ ] Are VPC flow logs enabled on subnets with appropriate aggregation intervals and sampling rates for cost control?
- [ ] Is DNS managed via Cloud DNS with private zones for internal resolution and forwarding zones for hybrid DNS?
- [ ] Are hierarchical firewall policies applied at the organization or folder level for centralized security controls?

## Why This Matters

GCP networking uses a global VPC model that differs fundamentally from AWS and Azure. Subnets are regional (not zonal), and VPCs are global, eliminating the need for VPC peering within a project. However, Shared VPC complexity increases with multi-project setups. GCP firewall rules are stateful and global, which is powerful but requires careful management to avoid overly permissive configurations. Cloud Armor is the only way to get WAF protection and must be attached to a load balancer.

## Common Decisions (ADR Triggers)

- **Shared VPC vs standalone VPCs** -- centralized network management vs project autonomy, IAM complexity
- **Load balancer type** -- global external (Envoy-based) vs classic vs regional, proxy vs passthrough
- **Cloud Armor tier** -- Standard (pay-per-policy) vs Managed Protection Plus (DDoS, adaptive protection, $3K/mo)
- **Hybrid connectivity** -- Dedicated Interconnect (10/100 Gbps) vs Partner Interconnect vs HA VPN
- **Private access model** -- Private Google Access vs Private Service Connect vs VPC Service Controls
- **Firewall management** -- VPC firewall rules vs hierarchical policies vs Cloud Firewall Plus (L7 inspection)
- **CDN strategy** -- Cloud CDN on load balancer vs Media CDN for streaming vs third-party CDN
