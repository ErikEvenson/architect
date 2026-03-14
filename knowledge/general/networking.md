# Networking

## Scope

This file covers **what** networking decisions need to be made. For provider-specific **how**, see the provider networking files.

## Checklist

- [ ] **[Critical]** How many availability zones should the architecture span? (2 minimum, 3 recommended)
- [ ] **[Recommended]** Is multi-region required for resilience or latency?
- [ ] **[Critical]** What is the network segmentation strategy? (public, private app, private data subnets)
- [ ] **[Critical]** What CIDR ranges will be used? Are there conflicts with existing networks?
- [ ] **[Recommended]** Is a CDN needed for global content delivery?
- [ ] **[Critical]** What load balancing strategy? (L4 vs L7, internal vs external)
- [ ] **[Recommended]** How do private subnets access the internet? (NAT gateway, VPC endpoints)
- [ ] **[Critical]** Is a WAF needed? What rules? (OWASP top 10, rate limiting, geo-blocking)
- [ ] **[Recommended]** How is DNS managed? What failover strategy?
- [ ] **[Recommended]** Are VPN or Direct Connect/ExpressRoute connections needed to on-premises?
- [ ] **[Recommended]** Is network traffic inspection required? (IDS/IPS, flow logs)
- [ ] **[Critical]** What are the firewall/security group rules between tiers?

## Why This Matters

Network design is the hardest thing to change after deployment. Poor segmentation exposes data tiers to the internet. Missing CDN means high latency for global users. Insufficient AZ spread means a single AZ failure takes down the application.

## Common Decisions (ADR Triggers)

- **Number of AZs/regions** — cost vs resilience trade-off
- **CDN selection** — CloudFront, Azure CDN, Cloud CDN, Cloudflare
- **WAF placement** — at CDN edge vs at load balancer
- **NAT strategy** — NAT gateway per AZ vs shared
- **DNS failover model** — active-passive vs active-active vs latency-based

## See Also

- `providers/aws/vpc.md` — AWS VPC, subnets, and network configuration
- `providers/azure/networking.md` — Azure VNet and network services
- `providers/gcp/networking.md` — GCP VPC and network configuration
