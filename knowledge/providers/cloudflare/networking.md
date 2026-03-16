# Cloudflare Networking

## Scope

Covers Cloudflare Tunnel, Magic Transit, Magic WAN, Spectrum, WARP client, WARP Connector, Network Interconnect (CNI), Gateway, SSL for SaaS, and ZTNA. These services are part of the Cloudflare One SASE platform. Use alongside `security.md` for Zero Trust Access policies and `cdn-dns.md` for DNS and proxy configuration.

## Checklist

- [ ] Determine whether Cloudflare Tunnel (formerly Argo Tunnel) or traditional DNS/IP exposure is appropriate for origin connectivity
- [ ] Evaluate Magic Transit for L3 DDoS protection on own IP prefixes (requires /24 minimum for BGP advertisement)
- [ ] Decide on Magic WAN for branch-to-branch and branch-to-cloud connectivity replacing traditional SD-WAN appliances
- [ ] Assess Spectrum for proxying non-HTTP TCP/UDP traffic (SSH, gaming, MQTT, custom protocols) through Cloudflare edge
- [ ] Plan Cloudflare Tunnel architecture: number of connectors, redundancy (multiple cloudflared instances per origin), named tunnels vs legacy tunnels
- [ ] Configure WARP client deployment strategy for endpoint traffic routing (split tunnel vs full tunnel, managed device enrollment)
- [ ] Evaluate Network Interconnect (CNI) for private, dedicated connectivity to Cloudflare edge (vs public internet paths)
- [ ] Design Cloudflare Gateway policies for DNS filtering, HTTP inspection, and egress traffic control
- [ ] Plan IP address management: Cloudflare-assigned IPs, BYOIP for Magic Transit, static IPs for egress (Gateway)
- [ ] Determine tunnel health-check intervals, failover behavior, and load balancing across multiple origin connectors
- [ ] Assess Cloudflare for SaaS (SSL for SaaS) if serving traffic on customer-owned vanity domains
- [ ] Plan Zero Trust Network Access (ZTNA) integration between Tunnel, Gateway, and Access policies

## Why This Matters

Cloudflare's networking portfolio replaces traditional hardware (firewalls, VPN concentrators, SD-WAN appliances, DDoS scrubbing boxes) with a globally distributed software-defined network. The key architectural shift is moving from castle-and-moat perimeter security to a model where every connection is authenticated and proxied through Cloudflare's edge. Incorrect design leads to exposed origins, latency penalties from suboptimal routing, or gaps in DDoS protection coverage. Cloudflare Tunnel eliminates the need for public inbound firewall rules entirely, while Magic Transit and Spectrum extend protection beyond HTTP to arbitrary IP traffic.

## Common Decisions (ADR Triggers)

- **Cloudflare Tunnel vs traditional reverse proxy**: Tunnel removes the need for public IPs and inbound firewall rules but adds a dependency on the cloudflared daemon. Use Tunnel for new deployments; keep DNS-based for legacy systems with strict change control.
- **Magic Transit vs upstream DDoS provider**: Magic Transit requires BGP prefix advertisement (/24 minimum) and Letter of Authorization. Best for organizations that own IP space and need always-on L3/L4 DDoS mitigation with sub-3-second detection.
- **Magic WAN vs third-party SD-WAN**: Magic WAN integrates natively with Cloudflare security stack (Gateway, Access) but lacks some advanced SD-WAN features (application-aware routing, WAN optimization). Evaluate based on whether security integration or WAN optimization is the priority.
- **Spectrum vs origin-side proxy**: Spectrum proxies arbitrary TCP/UDP but charges per-GB. For high-bandwidth non-HTTP services, compare cost against self-managed proxies with Cloudflare DNS-only protection.
- **Split tunnel vs full tunnel (WARP)**: Split tunnel reduces latency for trusted destinations but creates visibility gaps. Full tunnel provides complete traffic inspection but requires careful Gateway policy design to avoid breaking SaaS applications.
- **CNI vs public internet paths**: CNI provides predictable latency and private connectivity but adds cost and provisioning lead time. Use for latency-sensitive or compliance-driven workloads.

## Reference Architectures

### Zero Trust Remote Access
```
[Remote User + WARP Client] --> [Cloudflare Edge / Gateway] --> [Cloudflare Tunnel] --> [Private Origin]
                                        |
                                  [Access Policies]
                                  [DLP Inspection]
                                  [DNS Filtering]
```
Replace VPN concentrators with Cloudflare Tunnel + Access. WARP client routes traffic to nearest Cloudflare PoP. Gateway applies DNS and HTTP policies. Tunnel connector on origin side creates outbound-only connections (no inbound firewall rules). Access enforces identity-aware policies per application.

### Multi-Site Connectivity with Magic WAN
```
[Branch Office A] --IPsec/GRE--> [Cloudflare Edge] <--IPsec/GRE-- [Branch Office B]
                                        |
                                  [Magic Firewall]
                                  [Gateway Policies]
                                        |
                                  [Cloud Egress / Internet]
```
Each branch establishes IPsec or GRE tunnels to Cloudflare. Magic Firewall applies L3/L4 rules. Gateway applies L7 inspection. Inter-branch traffic routes through Cloudflare without hairpinning through a central data center. Cloudflare CNI optionally provides private on-ramps for data center sites.

### DDoS-Protected Infrastructure (Magic Transit)
```
[Internet Traffic] --> [Cloudflare Edge (BGP Anycast)] --> [Magic Transit / GRE|IPsec] --> [Origin Network]
                              |
                        [L3/L4 DDoS Mitigation]
                        [Magic Firewall Rules]
                        [Flow-based Analytics]
```
Cloudflare advertises customer IP prefixes via BGP. All traffic to those prefixes flows through Cloudflare's scrubbing infrastructure. Clean traffic is forwarded via GRE or IPsec tunnels to origin. Always-on mode provides sub-second mitigation; on-demand mode reduces tunnel bandwidth costs but adds failover delay.
