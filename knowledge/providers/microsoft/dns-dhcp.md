# Microsoft DNS and DHCP

## Scope

Microsoft DNS and DHCP services on Windows Server: DNS zone design (Active Directory-integrated vs standard primary/secondary), DNS scavenging and stale record cleanup, conditional forwarders and forwarding policies, DHCP failover (hot standby vs load balance) and split-scope configurations, Windows IPAM (IP Address Management) role for unified DNS/DHCP management, migration strategies to and from third-party DDI platforms such as Infoblox, and integration with Active Directory Sites and Services for site-aware resource records.

## Checklist

- [ ] [Critical] Are DNS zones configured as Active Directory-integrated with secure dynamic updates to leverage multi-master replication, eliminate single points of failure, and prevent unauthorized record registration?
- [ ] [Critical] Is DNS scavenging enabled with appropriate no-refresh (default 7 days) and refresh (default 7 days) intervals on both the zone and the DNS server to prevent stale records from accumulating?
- [ ] [Critical] Is DHCP failover configured between at least two DHCP servers using either hot standby mode (primary/secondary with state switchover interval) or load balance mode (active/active) for every production scope?
- [ ] [Critical] Are forward and reverse lookup zones maintained in sync, with PTR record registration enabled in DHCP scope options to ensure reverse DNS resolution for all dynamically assigned addresses?
- [ ] [Recommended] Are conditional forwarders configured for partner domains, cloud DNS zones, or split-horizon scenarios rather than relying on root hints or blanket forwarding to external resolvers?
- [ ] [Recommended] Is Windows IPAM deployed for centralized visibility across all Microsoft DNS and DHCP servers, with role-based access control configured for delegated administration of zones and scopes?
- [ ] [Recommended] Are DHCP scopes designed with appropriate lease durations (shorter for wireless/guest networks, longer for wired/server networks) and are DHCP reservations documented for infrastructure devices?
- [ ] [Recommended] Are DNS policies or query resolution policies configured to support split-brain DNS, geo-location-based resolution, or traffic management where required?
- [ ] [Recommended] Is DHCP option configuration standardized across scopes using server-level or policy-based options (DNS servers, default gateway, NTP, TFTP) rather than per-scope manual configuration?
- [ ] [Recommended] Is a DNS migration plan documented for transitions to or from third-party platforms, including zone export/import procedures, TTL lowering before cutover, and parallel operation during validation?
- [ ] [Optional] Is DNSSEC configured for zones requiring authenticated DNS responses, with key rollover procedures documented and trust anchors distributed?
- [ ] [Optional] Are DNS logging and analytical events enabled for security monitoring, with DNS query logs forwarded to the SIEM for threat detection (DNS tunneling, DGA domain queries)?

## Why This Matters

DNS and DHCP are foundational network services that every device depends on. A DNS outage effectively takes down the entire network -- users cannot resolve hostnames, applications cannot find services, and Active Directory authentication fails because domain controllers are located via DNS SRV records. DHCP failures prevent new devices from obtaining addresses and can cause IP conflicts when leases expire without renewal.

Active Directory-integrated DNS zones provide significant advantages over standard zones: multi-master replication eliminates the single-master bottleneck of traditional zone transfers, secure dynamic updates prevent rogue record registration, and replication follows the existing AD topology. However, DNS scavenging must be explicitly enabled and carefully tuned -- without it, stale records accumulate indefinitely, causing name resolution conflicts and complicating IP address management.

## Common Decisions (ADR Triggers)

- **Zone type** -- AD-integrated (multi-master, secure updates, AD replication) vs standard primary/secondary (zone transfer-based, interoperable with non-Windows DNS)
- **DHCP failover mode** -- Hot standby (simple primary/secondary, one server idle) vs load balance (active/active, both servers serve clients)
- **DNS forwarding** -- Conditional forwarders (targeted per-domain) vs root hints (full recursion) vs external resolver forwarding (cloud DNS, ISP)
- **IPAM platform** -- Windows IPAM (free with Windows Server, Microsoft-only) vs Infoblox (multi-vendor, advanced features) vs open-source (NetBox, phpIPAM)
- **DDI migration** -- Phased migration with parallel operation vs hard cutover vs hybrid (split authority between platforms)
- **DNS security** -- DNSSEC (authenticated responses, complex key management) vs DNS over HTTPS/TLS (encrypted transport) vs Response Policy Zones (threat blocking)

## See Also

- `providers/microsoft/active-directory.md` -- Active Directory integration and AD-integrated zones
- `providers/infoblox/ddi.md` -- Infoblox DDI platform for DNS, DHCP, and IPAM
- `general/hybrid-dns.md` -- hybrid and multi-cloud DNS resolution patterns

## Reference Links

- [DNS Server on Windows Server](https://learn.microsoft.com/windows-server/networking/dns/dns-top) -- DNS zone types, AD-integrated DNS, conditional forwarders, and scavenging
- [DHCP Server on Windows Server](https://learn.microsoft.com/windows-server/networking/technologies/dhcp/dhcp-top) -- DHCP failover, split-scope, reservations, and policies
- [IPAM Overview](https://learn.microsoft.com/windows-server/networking/technologies/ipam/ipam-top) -- Windows IPAM for unified DNS, DHCP, and IP address management
