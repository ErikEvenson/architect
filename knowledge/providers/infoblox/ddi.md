# Infoblox DDI (DNS/DHCP/IPAM)

## Scope

Infoblox DDI platform architecture: Grid design (Grid Master, Grid Master Candidate, members, reporting members), DNS services (authoritative zones, views, Response Policy Zones for threat intelligence), DHCP services (scopes, failover associations, fingerprinting, lease management), IPAM (network container management, discovery, address allocation), NIOS appliance sizing and deployment, Grid high availability, BloxOne DDI (cloud-managed SaaS DDI), migration strategies to and from Microsoft DNS/DHCP, REST API (WAPI) automation, licensing models, and integration with cloud provider DNS services.

## Checklist

- [ ] [Critical] Is the Grid Master deployed with a Grid Master Candidate (GMC) in a separate site for automatic failover, with promotion procedures documented and tested?
- [ ] [Critical] Are Grid members sized correctly for their role (DNS-only, DHCP-only, or combined) based on query rates, zone counts, lease counts, and NIOS platform capacity guidelines?
- [ ] [Critical] Is the Grid database backed up on a scheduled basis with backups stored off-grid, and are restore procedures validated including full Grid recovery and single-member recovery?
- [ ] [Critical] Are DNS views configured to serve different responses to internal vs external clients, with view matching rules based on source network and TSIG keys?
- [ ] [Recommended] Are Response Policy Zones (RPZ) configured with threat intelligence feeds (Infoblox Threat Intelligence, SURBL, or custom feeds) to block malicious domain resolution at the DNS layer?
- [ ] [Recommended] Is DHCP failover configured as Grid-level DHCP failover associations between member pairs, with failover state monitoring and automatic failback configured?
- [ ] [Recommended] Is IPAM discovery configured to scan networks and reconcile discovered devices against managed addresses, identifying rogue devices and unmanaged address space?
- [ ] [Recommended] Is the WAPI (Web API) used for automation of record creation, network provisioning, and integration with ITSM platforms (ServiceNow, BMC) and orchestration tools (Ansible, Terraform)?
- [ ] [Recommended] Are extensible attributes defined and consistently applied to networks, ranges, and records to support organizational metadata (site, environment, owner, cost center) for reporting and automation?
- [ ] [Recommended] Is a DNS migration plan documented for absorbing Microsoft DNS zones, including zone transfer configuration (AXFR/IXFR), parallel resolution validation, and staged NS record delegation changes?
- [ ] [Optional] Is BloxOne DDI evaluated for branch offices or cloud-first deployments where on-premises appliance management overhead is undesirable?
- [ ] [Optional] Is Infoblox cloud integration configured for cloud provider DNS (AWS Route 53, Azure DNS, GCP Cloud DNS) to provide unified visibility and management across on-premises and cloud DNS zones?
- [ ] [Optional] Are DHCP fingerprinting and lease history enabled for network access control integration and forensic investigation of device activity?

## Why This Matters

Infoblox DDI provides a centralized, purpose-built platform for DNS, DHCP, and IP address management that scales to enterprise environments with hundreds of thousands of managed objects. Unlike Microsoft DNS/DHCP which distributes management across individual Windows Servers, the Infoblox Grid architecture provides a single management plane with distributed data members, making it possible to manage global DDI infrastructure from one console. The Grid Master is the single source of truth for all configuration -- its loss without a functioning Grid Master Candidate means no configuration changes can be made to any Grid member until recovery is complete.

DNS security through Response Policy Zones is a significant differentiator, providing network-wide protection against malicious domains without requiring endpoint agents. IPAM discovery fills visibility gaps by identifying devices that obtained addresses outside managed DHCP or were statically configured without documentation. For organizations migrating between Microsoft and Infoblox, the transition requires careful planning because the platforms handle failover, dynamic updates, and zone replication in fundamentally different ways.

## Common Decisions (ADR Triggers)

- **Grid topology** -- Centralized Grid Master with distributed members vs regional Grid Masters (separate Grids) with cross-Grid delegation
- **DDI platform** -- Infoblox NIOS (on-premises appliances) vs BloxOne DDI (cloud-managed SaaS) vs hybrid (NIOS on-premises with BloxOne at edge/cloud)
- **DNS security** -- Infoblox RPZ (DNS-layer blocking) vs external DNS firewall (Cisco Umbrella, Zscaler) vs endpoint-based DNS security
- **DHCP failover** -- Infoblox Grid DHCP failover (Grid-native, automatic) vs Microsoft DHCP failover (Windows-native) vs split-scope (simple, less resilient)
- **IPAM strategy** -- Infoblox IPAM (full DDI integration) vs Microsoft IPAM (Windows-only) vs open-source (NetBox, phpIPAM for visibility only)
- **Migration direction** -- Microsoft DNS/DHCP to Infoblox (centralized management) vs Infoblox to Microsoft (cost reduction) vs coexistence (phased or permanent)
- **API automation** -- WAPI direct integration vs Ansible/Terraform modules vs ServiceNow CMDB-driven provisioning
- **Licensing model** -- Perpetual licenses with support renewal vs subscription licensing vs BloxOne SaaS consumption-based

## See Also

- `general/hybrid-dns.md` -- hybrid and multi-cloud DNS resolution patterns
- `providers/microsoft/dns-dhcp.md` -- Microsoft DNS and DHCP services
- `general/networking.md` -- general network architecture patterns

## Reference Links

- [Infoblox NIOS Documentation](https://docs.infoblox.com/space/nios) -- Grid architecture, DNS/DHCP services, IPAM, and WAPI REST API
- [Infoblox BloxOne DDI](https://docs.infoblox.com/space/BloxOneDDI) -- cloud-managed DDI platform architecture and configuration
- [Infoblox Deployment Guides](https://docs.infoblox.com/) -- sizing guides, HA design, and migration from Microsoft DNS/DHCP
