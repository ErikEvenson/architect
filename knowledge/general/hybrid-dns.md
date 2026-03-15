# Hybrid DNS Resolution

## Checklist

- [ ] **[Critical]** Are DNS resolver endpoints deployed in each cloud environment for cross-environment name resolution? (AWS Route 53 Resolver inbound/outbound, Azure Private DNS Resolver, GCP Cloud DNS inbound policy)
- [ ] **[Critical]** Are conditional forwarding rules configured so on-prem DNS forwards cloud-specific domains (amazonaws.com, azure.internal, internal) to cloud resolver endpoints, and cloud forwards on-prem domains (corp.company.local, ad.company.com) to on-prem DNS?
- [ ] **[Critical]** Are security groups / firewall rules on resolver endpoints permitting both UDP and TCP on port 53? (TCP is required for responses over 512 bytes and zone transfers)
- [ ] **[Critical]** Is split-horizon DNS implemented correctly so internal clients resolve private IPs and external clients resolve public IPs for the same domain names?
- [ ] **[Critical]** Are resolver endpoints deployed across at least 2 availability zones for redundancy?
- [ ] **[Recommended]** Is Active Directory DNS integrated with cloud DNS via conditional forwarders rather than zone delegation, to avoid replication complexity?
- [ ] **[Recommended]** Are DNS forwarding loops prevented? (cloud forwards to on-prem, on-prem forwards back to cloud for the same domain creates a loop that silently fails or causes SERVFAIL)
- [ ] **[Recommended]** Are DNS TTLs set appropriately for failover scenarios? (TTL 60s or less for records involved in DR; higher TTLs reduce query cost but delay failover)
- [ ] **[Recommended]** Is Resolver query logging enabled for troubleshooting and security auditing? (AWS Route 53 Resolver query logs, Azure DNS analytics, GCP Cloud DNS logging)
- [ ] **[Recommended]** Are Private DNS zones associated with all VPCs/VNets that need to resolve private endpoints? (privatelink.database.windows.net, privatelink.blob.core.windows.net, etc.)
- [ ] **[Recommended]** Is the cost of resolver endpoints budgeted? (AWS: ~$0.125/hr per ENI, minimum 2 per endpoint = ~$180/mo per endpoint direction; Azure: ~$0.18/hr per endpoint; a typical bidirectional setup costs $360-$500/mo)
- [ ] **[Optional]** Are DNS forwarding rules shared across accounts using AWS RAM or Azure DNS resolver policy links to avoid duplicated configuration?
- [ ] **[Optional]** Is a centralized DNS hub pattern used for multi-cloud, where on-prem DNS acts as the forwarding nexus between AWS, Azure, and GCP?
- [ ] **[Optional]** Is DNSSEC enabled on public-facing zones and validated on resolvers to prevent DNS spoofing in transit between environments?

## Why This Matters

DNS is the first thing that breaks in hybrid environments and the last thing anyone thinks to test. When a workload in AWS cannot resolve an on-prem Active Directory domain controller, authentication fails, applications crash, and the root cause is invisible to application-level monitoring. When on-prem clients cannot resolve AWS PrivateLink endpoints, the private connectivity you paid for is useless and traffic may silently fall back to public internet paths.

Hybrid DNS resolution requires explicit infrastructure -- resolver endpoints, forwarding rules, and security group configurations -- that does not exist by default in any cloud provider. Unlike most networking components, DNS failures manifest as application errors (connection timeouts, authentication failures, "host not found") rather than network errors, making them hard to diagnose. A well-designed hybrid DNS architecture is the foundation that makes every other hybrid service (identity, database replication, monitoring) actually work.

The cost is non-trivial. A single AWS Route 53 Resolver setup with inbound and outbound endpoints (4 ENIs minimum) costs approximately $360/month before query charges. Organizations running multiple accounts or regions can see DNS infrastructure costs reach thousands per month. This is worth understanding upfront rather than discovering after deployment.

## Common Decisions (ADR Triggers)

- **Centralized hub vs. per-VPC resolver endpoints** -- hub model reduces cost and complexity but creates a single point of failure and a network hop; per-VPC is resilient but expensive at scale
- **Split-horizon implementation strategy** -- separate public/private hosted zones vs. DNS views (BIND) vs. provider-native split-horizon; affects operational complexity and consistency
- **Active Directory DNS integration model** -- conditional forwarders on AD DNS servers vs. AD-integrated stub zones vs. secondary zones in cloud; each has different replication and security trade-offs
- **Multi-cloud DNS hub topology** -- on-prem DNS as hub (simple, adds latency to cross-cloud) vs. direct cloud-to-cloud forwarding (faster, more complex forwarding rules) vs. third-party DNS service (Infoblox, NS1)
- **Private DNS zone management** -- manually create zones for each PaaS service vs. Azure Policy / AWS Config auto-creation; manual is error-prone at scale, automation requires governance
- **DNS failover TTL strategy** -- low TTL (5-60s) enables fast failover but increases query volume and cost; high TTL (300s+) reduces cost but delays failover; different records may warrant different TTLs

## Reference Architectures

### Architecture 1: AWS Hybrid DNS with On-Prem Active Directory

This is the most common pattern for enterprises extending Active Directory into AWS.

```
┌─────────────────────────────────────────────────────────────┐
│  On-Premises Data Center                                    │
│                                                             │
│  ┌──────────────────┐     ┌──────────────────┐              │
│  │ AD DNS Server 1  │     │ AD DNS Server 2  │              │
│  │ dc1.corp.local   │     │ dc2.corp.local   │              │
│  │ 10.0.1.10        │     │ 10.0.1.11        │              │
│  └────────┬─────────┘     └────────┬─────────┘              │
│           │  Conditional Forwarder:                          │
│           │  *.amazonaws.com → 10.100.1.10, 10.100.2.10     │
│           │  *.aws.company.com → 10.100.1.10, 10.100.2.10   │
│           │                                                  │
│  ─────────┼──────────────────────────────────────────────── │
│           │  Direct Connect / VPN                            │
└───────────┼─────────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────────┐
│  AWS VPC  │  (10.100.0.0/16)                                │
│           │                                                  │
│  ┌────────▼─────────────────────────────────────────────┐   │
│  │  Route 53 Resolver Inbound Endpoint                   │   │
│  │  (on-prem → AWS resolution)                           │   │
│  │  ENI: 10.100.1.10 (AZ-a)                              │   │
│  │  ENI: 10.100.2.10 (AZ-b)                              │   │
│  │  SG: allow UDP/TCP 53 from 10.0.0.0/8                 │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Route 53 Resolver Outbound Endpoint                  │   │
│  │  (AWS → on-prem resolution)                           │   │
│  │  ENI: 10.100.1.11 (AZ-a)                              │   │
│  │  ENI: 10.100.2.11 (AZ-b)                              │   │
│  │  SG: allow UDP/TCP 53 outbound                        │   │
│  └──────────────────────┬────────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼────────────────────────────────┐   │
│  │  Forwarding Rules                                     │   │
│  │  corp.local        → 10.0.1.10, 10.0.1.11             │   │
│  │  ad.company.com    → 10.0.1.10, 10.0.1.11             │   │
│  │  10.in-addr.arpa   → 10.0.1.10, 10.0.1.11             │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Route 53 Private Hosted Zone                         │   │
│  │  aws.company.com (associated with VPC)                │   │
│  │  app.aws.company.com → 10.100.10.50 (ALB)             │   │
│  │  db.aws.company.com  → 10.100.20.30 (RDS)             │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**DNS query flows:**

1. **On-prem client → AWS resource**: Client queries `app.aws.company.com` → AD DNS has conditional forwarder → forwards to Resolver inbound ENI (10.100.1.10) → Route 53 resolves from private hosted zone → returns 10.100.10.50
2. **AWS instance → on-prem resource**: Instance queries `dc1.corp.local` → VPC DNS (AmazonProvidedDNS) → matches forwarding rule → Resolver outbound endpoint → on-prem AD DNS → returns 10.0.1.10
3. **AWS instance → AWS resource**: Instance queries `app.aws.company.com` → VPC DNS resolves directly from private hosted zone → returns 10.100.10.50 (no resolver endpoints involved)

**Key Terraform configuration (AWS):**

```hcl
# Inbound endpoint -- allows on-prem to resolve AWS private zones
resource "aws_route53_resolver_endpoint" "inbound" {
  name      = "onprem-to-aws"
  direction = "INBOUND"

  security_group_ids = [aws_security_group.dns_inbound.id]

  ip_address {
    subnet_id = aws_subnet.private_a.id
    ip        = "10.100.1.10"
  }
  ip_address {
    subnet_id = aws_subnet.private_b.id
    ip        = "10.100.2.10"
  }
}

# Outbound endpoint -- allows AWS to resolve on-prem domains
resource "aws_route53_resolver_endpoint" "outbound" {
  name      = "aws-to-onprem"
  direction = "OUTBOUND"

  security_group_ids = [aws_security_group.dns_outbound.id]

  ip_address {
    subnet_id = aws_subnet.private_a.id
  }
  ip_address {
    subnet_id = aws_subnet.private_b.id
  }
}

# Forwarding rule -- send corp.local queries to on-prem DNS
resource "aws_route53_resolver_rule" "onprem_forward" {
  domain_name          = "corp.local"
  name                 = "forward-to-onprem-dns"
  rule_type            = "FORWARD"
  resolver_endpoint_id = aws_route53_resolver_endpoint.outbound.id

  target_ip {
    ip = "10.0.1.10"
  }
  target_ip {
    ip = "10.0.1.11"
  }
}

# Associate rule with VPC
resource "aws_route53_resolver_rule_association" "onprem_forward" {
  resolver_rule_id = aws_route53_resolver_rule.onprem_forward.id
  vpc_id           = aws_vpc.main.id
}

# Security group for inbound endpoint
resource "aws_security_group" "dns_inbound" {
  name   = "dns-resolver-inbound"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["10.0.0.0/8"]
  }
  ingress {
    from_port   = 53
    to_port     = 53
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}

# Share forwarding rules across accounts via RAM
resource "aws_ram_resource_share" "dns_rules" {
  name                      = "dns-forwarding-rules"
  allow_external_principals = false
}

resource "aws_ram_resource_association" "dns_rule_share" {
  resource_arn       = aws_route53_resolver_rule.onprem_forward.arn
  resource_share_arn = aws_ram_resource_share.dns_rules.arn
}

# Resolver query logging
resource "aws_route53_resolver_query_log_config" "main" {
  name            = "dns-query-log"
  destination_arn = aws_cloudwatch_log_group.dns_logs.arn
}

resource "aws_route53_resolver_query_log_config_association" "main" {
  resolver_query_log_config_id = aws_route53_resolver_query_log_config.main.id
  resource_id                  = aws_vpc.main.id
}
```

### Architecture 2: Azure Hybrid DNS with Private Endpoints

Azure Private DNS Resolver replaces the legacy pattern of running DNS forwarder VMs (BIND/Windows DNS) in Azure.

```
┌─────────────────────────────────────────────────────────────┐
│  On-Premises Data Center                                    │
│                                                             │
│  ┌──────────────────┐     ┌──────────────────┐              │
│  │  DNS Server 1    │     │  DNS Server 2    │              │
│  │  10.0.1.10       │     │  10.0.1.11       │              │
│  └────────┬─────────┘     └────────┬─────────┘              │
│           │  Conditional Forwarders:                         │
│           │  *.privatelink.database.windows.net              │
│           │    → 10.200.1.10 (resolver inbound)              │
│           │  *.privatelink.blob.core.windows.net             │
│           │    → 10.200.1.10 (resolver inbound)              │
│           │  *.azure.company.com                             │
│           │    → 10.200.1.10 (resolver inbound)              │
│           │                                                  │
│  ─────────┼──────────────────────────────────────────────── │
│           │  ExpressRoute / VPN                              │
└───────────┼─────────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────────┐
│  Azure    │  Hub VNet (10.200.0.0/16)                       │
│           │                                                  │
│  ┌────────▼─────────────────────────────────────────────┐   │
│  │  Azure Private DNS Resolver                           │   │
│  │                                                       │   │
│  │  Inbound Endpoint (10.200.1.0/28 delegated subnet)    │   │
│  │    IP: 10.200.1.10                                    │   │
│  │    (on-prem queries arrive here)                      │   │
│  │                                                       │   │
│  │  Outbound Endpoint (10.200.2.0/28 delegated subnet)   │   │
│  │    IP: 10.200.2.10                                    │   │
│  │    (Azure queries to on-prem leave here)              │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  DNS Forwarding Ruleset                               │   │
│  │  (linked to Hub VNet and Spoke VNets)                 │   │
│  │                                                       │   │
│  │  corp.local      → 10.0.1.10, 10.0.1.11               │   │
│  │  ad.company.com  → 10.0.1.10, 10.0.1.11               │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Private DNS Zones (linked to Hub + Spoke VNets)      │   │
│  │                                                       │   │
│  │  privatelink.database.windows.net                     │   │
│  │    sqlserver1.privatelink.database.windows.net         │   │
│  │    → 10.201.5.4                                       │   │
│  │                                                       │   │
│  │  privatelink.blob.core.windows.net                    │   │
│  │    storage1.privatelink.blob.core.windows.net          │   │
│  │    → 10.201.5.5                                       │   │
│  │                                                       │   │
│  │  azure.company.com                                    │   │
│  │    app1.azure.company.com → 10.201.10.20               │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Spoke VNet (10.201.0.0/16) -- peered to Hub          │   │
│  │  App workloads, Private Endpoints                     │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**Critical Azure Private DNS zone list for common PaaS services:**

| Service | Private DNS Zone |
|---------|-----------------|
| Azure SQL | privatelink.database.windows.net |
| Blob Storage | privatelink.blob.core.windows.net |
| Key Vault | privatelink.vaultcore.azure.net |
| Azure Cache for Redis | privatelink.redis.cache.windows.net |
| Cosmos DB | privatelink.documents.azure.com |
| Azure Monitor | privatelink.monitor.azure.com |
| Container Registry | privatelink.azurecr.io |

Each Private DNS zone must be linked to every VNet that contains clients needing to resolve those endpoints. Missing a VNet link is the most common cause of "private endpoint not working" issues.

### Architecture 3: GCP Hybrid DNS

```
┌─────────────────────────────────────────────────────────────┐
│  On-Premises Data Center                                    │
│                                                             │
│  ┌──────────────────┐                                       │
│  │  DNS Server       │                                       │
│  │  10.0.1.10        │                                       │
│  └────────┬─────────┘                                       │
│           │  Conditional Forwarder:                          │
│           │  *.gcp.company.com                               │
│           │    → 35.199.192.0/19 (GCP inbound forwarding)   │
│           │                                                  │
│  ─────────┼──────────────────────────────────────────────── │
│           │  Cloud Interconnect / VPN                        │
└───────────┼─────────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────────┐
│  GCP      │  Shared VPC (10.128.0.0/16)                     │
│           │                                                  │
│  ┌────────▼─────────────────────────────────────────────┐   │
│  │  Cloud DNS Inbound Server Policy                      │   │
│  │  (applied to VPC network)                             │   │
│  │                                                       │   │
│  │  Enables inbound DNS forwarding                       │   │
│  │  On-prem forwards to 35.199.192.0/19                  │   │
│  │  (GCP automatically assigns inbound forwarder IPs     │   │
│  │   from this range in each region with subnets)        │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Cloud DNS Forwarding Zone                            │   │
│  │  (GCP → on-prem resolution)                           │   │
│  │                                                       │   │
│  │  corp.local → 10.0.1.10                                │   │
│  │  ad.company.com → 10.0.1.10                            │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Cloud DNS Private Zone                               │   │
│  │  gcp.company.com (visible to VPC)                     │   │
│  │  app.gcp.company.com → 10.128.10.5                    │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Cloud DNS Peering Zone (cross-project)               │   │
│  │  Allows project-B VPC to resolve zones                │   │
│  │  hosted in project-A VPC without duplication           │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**GCP-specific considerations:**
- GCP inbound DNS forwarding uses the reserved range `35.199.192.0/19` -- on-prem DNS must forward to IPs in this range, and firewall rules on the Cloud Interconnect/VPN must allow this traffic
- DNS peering zones let one VPC delegate resolution to another VPC's DNS, useful in Shared VPC or multi-project architectures
- GKE clusters create DNS entries in `cluster.local` by default; to expose GKE services to on-prem, create corresponding records in a Cloud DNS private zone

### Architecture 4: Split-Horizon DNS

Same domain resolves differently depending on where the query originates.

```
External client                    Internal client (on-prem or cloud)
    │                                        │
    │ app.company.com?                       │ app.company.com?
    ▼                                        ▼
┌──────────────┐                    ┌──────────────────┐
│ Public DNS   │                    │ Internal DNS     │
│ (Route 53    │                    │ (AD DNS / Route  │
│  public zone)│                    │  53 private zone)│
│              │                    │                  │
│ app.company  │                    │ app.company      │
│ .com →       │                    │ .com →           │
│ 203.0.113.50 │                    │ 10.100.10.50     │
│ (public ALB) │                    │ (internal ALB)   │
└──────────────┘                    └──────────────────┘
```

**Implementation per provider:**

| Provider | External Zone | Internal Zone | How Split Works |
|----------|--------------|---------------|-----------------|
| AWS | Route 53 public hosted zone | Route 53 private hosted zone (same domain, associated with VPC) | VPC DNS resolver checks private zone first; external resolvers only see public zone |
| Azure | Azure DNS public zone | Azure Private DNS zone (same domain, linked to VNet) | VNet DNS checks private zone first; external resolvers query public zone |
| GCP | Cloud DNS public zone | Cloud DNS private zone (same domain, bound to VPC) | VPC metadata server checks private zone first |
| BIND | Same server, different views | `view "internal"` and `view "external"` with `match-clients` ACLs | BIND selects view based on client source IP |

**BIND split-horizon example:**

```
acl "internal-networks" {
    10.0.0.0/8;
    172.16.0.0/12;
    192.168.0.0/16;
};

view "internal" {
    match-clients { internal-networks; };
    zone "company.com" {
        type master;
        file "/etc/bind/zones/internal.company.com.zone";
        # Contains A record: app.company.com → 10.100.10.50
    };
};

view "external" {
    match-clients { any; };
    zone "company.com" {
        type master;
        file "/etc/bind/zones/external.company.com.zone";
        # Contains A record: app.company.com → 203.0.113.50
    };
};
```

### Architecture 5: Multi-Cloud DNS via On-Prem Hub

When workloads span AWS, Azure, and GCP, on-prem DNS acts as the central forwarding hub.

```
┌────────────────────────────────────────────────────────────────────┐
│  On-Premises DNS Hub                                               │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  DNS Servers (BIND / Windows DNS / Infoblox)               │    │
│  │                                                            │    │
│  │  Authoritative:                                            │    │
│  │    corp.local                                              │    │
│  │    company.internal                                        │    │
│  │                                                            │    │
│  │  Conditional Forwarders:                                   │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ AWS domains:                                         │  │    │
│  │  │   aws.company.com       → 10.100.1.10 (R53 inbound) │  │    │
│  │  │   *.amazonaws.com       → 10.100.1.10                │  │    │
│  │  │   compute.internal      → 10.100.1.10                │  │    │
│  │  ├──────────────────────────────────────────────────────┤  │    │
│  │  │ Azure domains:                                       │  │    │
│  │  │   azure.company.com     → 10.200.1.10 (resolver in) │  │    │
│  │  │   *.privatelink.*.net   → 10.200.1.10                │  │    │
│  │  │   *.internal.cloudapp.net → 10.200.1.10              │  │    │
│  │  ├──────────────────────────────────────────────────────┤  │    │
│  │  │ GCP domains:                                         │  │    │
│  │  │   gcp.company.com       → 35.199.192.x (GCP inbound)│  │    │
│  │  │   *.internal            → 35.199.192.x               │  │    │
│  │  └──────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                    │
│      ┌──────────┬──────────────────┬──────────────┐               │
│      │          │                  │              │               │
└──────┼──────────┼──────────────────┼──────────────┼───────────────┘
       │          │                  │              │
    DX/VPN    DX/VPN          ExpressRoute    Interconnect
       │          │                  │              │
  ┌────▼───┐ ┌────▼───┐      ┌──────▼──┐    ┌─────▼────┐
  │ AWS    │ │ AWS    │      │ Azure   │    │ GCP      │
  │ Acct 1 │ │ Acct 2 │      │ Sub 1   │    │ Proj 1   │
  │        │ │        │      │         │    │          │
  │ Each   │ │ Each   │      │ Fwd     │    │ Fwd zone │
  │ has    │ │ has    │      │ ruleset │    │ to on-   │
  │ outbnd │ │ outbnd │      │ to on-  │    │ prem for │
  │ resolv │ │ resolv │      │ prem    │    │ corp.*   │
  │ er →   │ │ er →   │      │ for     │    │          │
  │ on-prem│ │ on-prem│      │ corp.*  │    │          │
  └────────┘ └────────┘      └─────────┘    └──────────┘
```

**Cross-cloud resolution flow (AWS workload → Azure resource):**

1. AWS instance queries `sqlserver1.privatelink.database.windows.net`
2. No match in AWS private hosted zones
3. Route 53 Resolver forwarding rule matches `*.privatelink.*.windows.net` → forwards to on-prem DNS (10.0.1.10)
4. On-prem DNS conditional forwarder matches `*.privatelink.*.windows.net` → forwards to Azure Private DNS Resolver inbound (10.200.1.10)
5. Azure resolver resolves from Private DNS zone → returns 10.201.5.4
6. Response flows back: Azure → on-prem DNS → AWS Resolver → AWS instance

This adds latency (two extra hops through on-prem) but avoids the complexity of direct cloud-to-cloud DNS forwarding, which requires VPC/VNet peering or transit connectivity between clouds.

### Common Mistakes and Troubleshooting

**Mistake 1: Missing resolver endpoints entirely.**
Symptom: `nslookup corp.local` from an EC2 instance returns NXDOMAIN. Teams assume "DNS just works" because it works on-prem.
Fix: Deploy Route 53 Resolver outbound endpoint + forwarding rule for `corp.local`.

**Mistake 2: Security group blocks on resolver ENIs.**
Symptom: On-prem DNS forwards to Resolver inbound endpoint IPs but queries time out.
Fix: Ensure the security group on the inbound endpoint allows inbound UDP *and* TCP port 53 from on-prem CIDR ranges. TCP is required for DNS responses exceeding 512 bytes (common with DNSSEC or large record sets).

**Mistake 3: DNS forwarding loops.**
Symptom: SERVFAIL responses, or DNS queries take 5+ seconds and then fail.
Cause: Cloud forwards `company.com` to on-prem, on-prem forwards `company.com` back to cloud (or to a root hint that loops back). Each side thinks the other is authoritative.
Fix: Be precise with forwarding rules. On-prem should only forward specific cloud subdomains (`aws.company.com`), not the parent domain. Cloud should only forward specific on-prem domains.

**Mistake 4: Missing Private DNS zone VNet/VPC links.**
Symptom: Azure VM in spoke VNet cannot resolve `sqlserver1.privatelink.database.windows.net`, but VMs in hub VNet can.
Fix: Link the `privatelink.database.windows.net` Private DNS zone to every VNet that needs resolution, or use DNS forwarding from spoke to hub.

**Mistake 5: High TTLs on failover records.**
Symptom: Disaster recovery failover happens, DNS records update, but clients continue connecting to the old (failed) site for minutes.
Fix: Set TTL to 60 seconds or lower for records involved in DR failover. Accept the increased query cost. Note that some clients and intermediate resolvers ignore low TTLs -- Java's default DNS cache is 30 seconds (was infinite before JDK 9), browsers cache DNS for 60 seconds regardless of TTL.

**Mistake 6: Forgetting reverse DNS (PTR) records for hybrid.**
Symptom: Services that perform reverse DNS lookups (logging, security tools, some authentication protocols) fail or show IP addresses instead of hostnames for cross-environment resources.
Fix: Create forwarding rules for `in-addr.arpa` zones corresponding to the remote environment's CIDR ranges. For example, AWS should forward `10.0.in-addr.arpa` to on-prem DNS if on-prem uses 10.0.0.0/16.

### Cost Reference

| Component | Provider | Unit Cost | Typical Monthly |
|-----------|----------|-----------|-----------------|
| Resolver inbound endpoint | AWS | $0.125/hr per ENI (min 2) | ~$180/mo |
| Resolver outbound endpoint | AWS | $0.125/hr per ENI (min 2) | ~$180/mo |
| Resolver queries (outbound) | AWS | $0.40 per million queries | Variable |
| Private DNS Resolver inbound | Azure | ~$0.18/hr per endpoint | ~$131/mo |
| Private DNS Resolver outbound | Azure | ~$0.18/hr per endpoint | ~$131/mo |
| DNS forwarding ruleset | Azure | Included with endpoint | $0 |
| Private DNS zone | Azure | $0.50/mo per zone | $0.50/zone |
| Cloud DNS forwarding queries | GCP | $0.40 per million queries | Variable |
| Cloud DNS managed zone | GCP | $0.20/mo per zone | $0.20/zone |
| Inbound DNS policy | GCP | No additional charge | $0 |

**Typical scenario -- single-cloud hybrid (AWS):** 2 inbound ENIs + 2 outbound ENIs = 4 x $0.125/hr = $360/mo baseline, plus query charges.

**Typical scenario -- multi-cloud hub:** AWS ($360) + Azure ($262) + GCP (~$0 fixed + queries) = ~$622/mo baseline for resolver infrastructure alone, plus on-prem DNS server costs.

## See Also

- `general/networking.md` -- VPC/VNet design, segmentation, and connectivity
- `general/dns-dev-patterns.md` -- nip.io, sslip.io for dev/POC environments
- `general/identity.md` -- Active Directory integration that depends on DNS
- `general/disaster-recovery.md` -- DNS failover strategies for DR
