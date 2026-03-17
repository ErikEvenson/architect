# Physical Network Design for On-Premises Infrastructure

## Checklist

- [ ] **[Critical]** Are VLANs segmented by traffic type -- management (VLAN 10-19), VM/workload (VLAN 20-99), storage/iSCSI/NFS (VLAN 100-109), vMotion/live migration (VLAN 110-119), backup (VLAN 120-129), DMZ (VLAN 200-209) -- with inter-VLAN routing controlled by firewall or L3 switch ACLs?
- [ ] **[Critical]** Is every host connected to dual Top-of-Rack (ToR) switches with redundant NIC paths, so that a single switch or NIC failure does not isolate any host from the network?
- [ ] **[Critical]** Is MTU configured consistently end-to-end for each network -- 9000 (jumbo frames) on storage VLANs from NIC to switch to storage target, 1500 on management VLANs -- with no intermediate device silently fragmenting or dropping oversized frames?
- [ ] **[Critical]** Is out-of-band management (IPMI/iDRAC/iLO/BMC) on a dedicated management VLAN with restricted access, enabling remote power cycling and console access even when the host OS is unresponsive?
- [ ] **[Recommended]** Is NIC bonding configured with the appropriate mode for each traffic type -- active-backup for management (simple failover, no switch config), LACP/802.3ad for high-throughput VM traffic (requires switch-side LAG configuration), or balance-slb for Nutanix/OVS environments?
- [ ] **[Recommended]** Are ToR switches configured with MLAG/vPC (Multi-Chassis Link Aggregation) so that host LAGs can span both switches, providing both bandwidth aggregation and switch-level redundancy?
- [ ] **[Recommended]** Is the network topology appropriate for the scale -- hierarchical (access/distribution/core) for small-medium deployments (<10 racks), spine-leaf for medium-large deployments (10+ racks) that need consistent east-west bandwidth?
- [ ] **[Recommended]** Are uplinks from ToR to spine/core switches sized at minimum 4x the access port speed (e.g., 4x25GbE uplinks for 48x10GbE access ports) to prevent oversubscription bottlenecks?
- [ ] **[Recommended]** Is firewall placement designed for both north-south traffic (perimeter firewall at internet edge) and east-west traffic (microsegmentation via distributed firewall or VLAN ACLs between workload segments)?
- [ ] **[Optional]** Is BGP or OSPF configured for multi-site WAN connectivity, with route summarization and appropriate timers for convergence requirements (OSPF hello 10s/dead 40s default, tune for faster failover)?
- [ ] **[Optional]** Are network monitoring and flow analysis tools (SNMP polling, NetFlow/sFlow, port mirroring) deployed to provide visibility into bandwidth utilization, top talkers, and anomalous traffic patterns?
- [ ] **[Optional]** Is 25GbE or 100GbE adopted for new deployments instead of 10GbE, providing headroom for storage-intensive workloads (NVMe-oF, high-IOPS databases) at marginal cost premium?
- [ ] **[Recommended]** Are spanning tree settings hardened -- PortFast/edge ports on host-facing ports, BPDU guard to prevent rogue switches, root bridge priority explicitly set on core switches?

## Why This Matters

Physical network design is the foundation that all virtualization, storage, and application layers depend on, yet it is the most difficult to change post-deployment. A VLAN design error forces either disruptive re-cabling/re-configuration or permanent workarounds. Inconsistent MTU settings on storage networks cause silent performance degradation: iSCSI traffic with 9000 MTU hitting a switch port configured for 1500 MTU results in fragmentation that cuts storage throughput by 30-50% and increases latency, but the storage "works" so the issue goes undetected until production load hits. NIC bonding mode mismatches between host and switch silently degrade to single-link throughput. Without MLAG/vPC, host LAGs can only connect to a single switch, making that switch a single point of failure despite having redundant NICs. Out-of-band management is a recovery-critical capability: without iDRAC/iLO on a reachable network, a hung host requires physical datacenter access for remediation, turning a 5-minute fix into a multi-hour event.

## Common Decisions (ADR Triggers)

- **10GbE vs 25GbE vs 100GbE** -- 10GbE is mature and cheap ($200-$500/port), sufficient for most virtualization workloads. 25GbE costs ~20-30% more than 10GbE but provides 2.5x bandwidth and uses the same SFP28 form factor (forward-compatible with 100GbE via breakout cables). 100GbE is standard for spine/uplink connections and increasingly used for storage-intensive workloads (NVMe-oF, GPU clusters). New deployments should prefer 25GbE access with 100GbE uplinks for 5-year lifespan.
- **Spine-leaf vs hierarchical (three-tier)** -- Hierarchical (access + distribution + core) is simpler for small deployments (<10 racks) with primarily north-south traffic patterns. Spine-leaf provides consistent latency and bandwidth for east-west traffic (critical for distributed storage like Nutanix, vSAN, Ceph) and scales linearly by adding spines or leaves. Spine-leaf requires more cables and switch ports but eliminates spanning tree complexity.
- **Switch vendor** -- Cisco Nexus (dominant enterprise install base, NX-OS, ACI for SDN, premium pricing $8K-$30K+ per ToR), Arista (dominant in modern datacenter/cloud, EOS with Linux underpinnings, strong automation/API, $5K-$20K per ToR), Dell/SONiC (open networking OS, competitive pricing $3K-$10K per ToR), Juniper QFX (Junos reliability, EVPN-VXLAN strengths). Decision often driven by existing team expertise and vendor support agreements.
- **NIC bonding mode** -- Active-backup: one NIC active, one standby, no switch configuration, provides redundancy but not aggregation. LACP (802.3ad): true link aggregation with switch coordination, provides both redundancy and combined throughput, but requires matching switch-side configuration. Balance-SLB (OVS): load-balances by source MAC without switch config, useful for Nutanix AHV/OVS environments. Balance-TCP (OVS LACP): best throughput for OVS but requires LACP on switch.
- **Microsegmentation approach** -- VLAN ACLs on L3 switch (simple, limited scale), distributed firewall in hypervisor (VMware NSX, Nutanix Flow), or network-based microsegmentation (Cisco ACI, Arista MSS). Distributed firewall is most granular (per-VM rules) but adds hypervisor overhead and vendor lock-in. VLAN ACLs are sufficient for zone-based segmentation (web/app/DB tiers).
- **WAN connectivity** -- MPLS (guaranteed SLA, expensive $500-$5000+/mo per site), SD-WAN over internet (cost-effective, vendor-managed overlay, broadband + LTE failover), direct internet with VPN (cheapest, variable quality). Trend is SD-WAN replacing MPLS for branch/remote offices while keeping MPLS or dedicated circuits for datacenter-to-datacenter replication traffic.

## Typical VLAN Layout

| VLAN ID Range | Purpose | MTU | Routable | Security |
|---|---|---|---|---|
| 1 | Native/default (unused) | 1500 | No | Disabled -- never use VLAN 1 |
| 10-19 | Host management (ESXi/AHV mgmt, iDRAC) | 1500 | Yes (restricted) | ACL: admin access only |
| 20-99 | VM/workload networks | 1500 | Yes (via firewall) | Per-zone ACLs |
| 100-109 | Storage (iSCSI, NFS, SMB) | 9000 | No (L2 only) | Isolated, no default gateway |
| 110-119 | vMotion / live migration | 9000 | No (L2 only) | Isolated, no default gateway |
| 120-129 | Backup traffic | 1500/9000 | Yes (restricted) | ACL: backup servers only |
| 130-139 | Replication (sync/async DR) | 9000 | Yes (to DR site) | ACL: replication targets only |
| 200-209 | DMZ (public-facing services) | 1500 | Yes (via firewall) | Strict ingress/egress filtering |
| 250-259 | Out-of-band management (IPMI/BMC) | 1500 | Yes (restricted) | ACL: jump host access only |

## Network Redundancy Architecture

```
          Internet / WAN
               │
        ┌──────┴──────┐
        │   Firewall   │  (HA pair)
        │   Pair       │
        └──────┬──────┘
               │
    ┌──────────┴──────────┐
    │   Core / Spine       │
    │  Switch A    Switch B │  (MLAG/vPC peer-link between A-B)
    └───┬──────────────┬───┘
        │              │
   ┌────┴────┐    ┌────┴────┐
   │  ToR 1A │    │  ToR 1B │   Rack 1 (MLAG/vPC pair)
   └──┬──┬───┘    └───┬──┬──┘
      │  │             │  │
    ┌─┴──┴─────────────┴──┴─┐
    │  Host 1 (dual NIC)     │   LACP bond spanning both ToRs
    │  Host 2 (dual NIC)     │
    │  Host 3 (dual NIC)     │
    └────────────────────────┘
```

**Key points:**
- Each host has minimum 2 NICs, one to each ToR switch
- ToR switches are MLAG/vPC paired so host bonds span both switches
- ToR-to-spine links provide redundant uplink paths
- Firewall HA pair provides stateful failover for north-south traffic

## Jumbo Frame Verification

Before enabling MTU 9000, test end-to-end on every path:

```bash
# From host, test to storage target (Linux)
ping -M do -s 8972 <storage_target_ip>
# -M do = don't fragment, -s 8972 = 8972 payload + 28 header = 9000

# If this fails, an intermediate device has MTU < 9000
# Check: host NIC, host bond, switch access port, switch trunk, storage NIC
```

Common failure points: switch trunk ports defaulting to 1500, intermediate firewall or router with 1500 MTU, virtual switches with default MTU.

## Reference Architectures

- **Arista Design Guides**: [arista.com/en/solutions/design-guides](https://www.arista.com/en/solutions/design-guides) -- spine-leaf reference designs, MLAG configuration, EVPN-VXLAN for overlay networking
- **Cisco Nexus Validated Designs**: [cisco.com/go/designzone](https://www.cisco.com/c/en/us/solutions/design-zone.html) -- NX-OS vPC configuration, FabricPath, and ACI deployment guides
- **Nutanix Network Best Practices**: [Nutanix Bible - Networking](https://www.nutanixbible.com/) -- AHV OVS bond modes, VLAN configuration, and recommended network architecture for HCI
- **Dell Networking with PowerEdge**: [Dell Deployment Guides](https://infohub.delltechnologies.com/) -- OS10 switch configuration, VLT (Dell's MLAG), and SmartFabric for automated leaf-spine
- **IEEE 802.3ad (LACP)**: Standard specification for link aggregation -- understanding LACP timers (fast: 1s, slow: 30s), system/port priority, and hash algorithms
- **VMware NSX Design Guide**: [VMware Validated Designs](https://core.vmware.com/vmware-validated-solutions) -- microsegmentation, distributed firewall rules, and network overlay architecture (reference even for non-VMware environments) (verify URL -- VMware documentation consolidated under Broadcom post-acquisition)
