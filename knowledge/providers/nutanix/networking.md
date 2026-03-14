# Nutanix Networking (AHV and Flow)

## Checklist

- [ ] Are AHV virtual switches configured with appropriate uplink assignments -- separate virtual switches (or at minimum separate VLANs) for management, VM production traffic, storage (iSCSI/backplane), and backup traffic?
- [ ] Is the bond mode on each virtual switch selected based on infrastructure capabilities -- active-backup for management (simple failover), balance-slb for VM traffic (no switch config needed), LACP (802.3ad) where switch LAG configuration is available?
- [ ] Are VLANs configured on AHV virtual switches with trunk ports carrying tagged traffic, and are VLAN IDs consistent with the physical switch configuration to prevent silent packet drops?
- [ ] Is Flow microsegmentation enabled in Prism Central with application-centric security policies using categories (AppType, AppTier, Environment) rather than IP-based rules?
- [ ] Are Flow isolation policies configured to enforce hard boundaries between environments (e.g., Production vs Development) where no traffic should cross regardless of application rules?
- [ ] Are Flow application policies configured in Monitor mode first to observe traffic patterns before switching to Apply mode, preventing accidental service disruption?
- [ ] Is the CVM backplane network (192.168.5.0/24 by default) on a dedicated VLAN or isolated subnet, never exposed to VM or external traffic?
- [ ] Are jumbo frames (MTU 9000) configured end-to-end for storage and CVM backplane traffic -- on AHV host NICs, physical switches, and any iSCSI-connected hosts -- to reduce CPU overhead and improve throughput?
- [ ] Is network function chaining configured in Flow to steer traffic through virtual security appliances (Palo Alto VM-Series, Fortinet FortiGate-VM) for north-south inspection before reaching VMs?
- [ ] Are load balancing requirements addressed using in-guest solutions (HAProxy, NGINX, Keepalived) or Nutanix-integrated options, since AHV does not include a native L4/L7 load balancer?
- [ ] Is VPN connectivity to the Nutanix cluster established through a dedicated virtual router appliance or physical firewall, with route tables ensuring management and VM traffic use appropriate gateways?
- [ ] Is AHV host networking using at least 2x 10GbE (or 2x 25GbE for all-NVMe clusters) per host, with separate bond groups for management+CVM and VM+storage where port count allows?
- [ ] Are IP address management (IPAM) settings configured in AHV for VM networks where DHCP relay is not available, using Nutanix-managed IPAM for automatic IP assignment from defined pools?
- [ ] Is DNS resolution configured for both Prism Element and Prism Central, with A records and PTR records for CVM IPs, host IPs, cluster virtual IP, and iSCSI data services IP?

## Why This Matters

AHV networking is built on Open vSwitch (OVS), providing VLAN trunking, bonding, and port mirroring capabilities without requiring VMware's distributed switches or additional licensing. However, OVS bond modes behave differently from physical switch bonding -- balance-slb hashes by source MAC and rebalances every 10 seconds, which is effective for many-to-many communication patterns but suboptimal for single-flow throughput. Flow microsegmentation is implemented at the OVS level on every AHV host, meaning policies follow VMs during live migration without requiring re-configuration. Category-based policies decouple security intent from infrastructure details, but poor category taxonomy leads to policy sprawl. The CVM backplane network carries all storage replication traffic and must never be congested -- a saturated backplane directly degrades storage performance for the entire cluster. Misconfigured MTU (jumbo frames on one side but not the other) causes silent packet fragmentation or drops that are difficult to diagnose.

## Common Decisions (ADR Triggers)

- **Bond mode selection** -- active-backup (simplest, no switch config) vs balance-slb (OVS load distribution without switch changes) vs LACP (best throughput, requires switch LAG groups and matching hash policy)
- **Network segmentation model** -- VLAN-based (traditional, requires physical switch config per VLAN) vs Flow microsegmentation (category-based, software-defined, follows VM) vs combination
- **Microsegmentation approach** -- Flow (built-in, no additional cost, category-driven) vs third-party virtual firewall appliance (Palo Alto VM-Series, Fortinet) with network function chaining for deeper inspection
- **Load balancing** -- In-guest load balancer (HAProxy, NGINX) vs dedicated load balancer VM appliance (F5 BIG-IP VE, Citrix ADC VPX) vs external physical load balancer
- **MTU configuration** -- Standard 1500 MTU (safe, no switch changes) vs jumbo frames 9000 MTU (better throughput for storage/replication, requires end-to-end switch configuration)
- **IP management** -- External DHCP server with relay vs Nutanix-managed IPAM (built into AHV, no external dependency) vs static IP assignment
- **Physical NIC allocation** -- All NICs in one bond (simple, shared bandwidth) vs split bonds (dedicated bandwidth for management/CVM vs VM/storage, requires 4+ NICs per host)
