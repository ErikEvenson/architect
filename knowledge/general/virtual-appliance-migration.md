# Virtual Appliance Migration

## Scope

This file covers **migration of vendor virtual appliances between hypervisor platforms**: hypervisor compatibility verification, license portability, configuration export/import, HA pair sequencing, and re-deployment planning. For general workload migration strategy (6 Rs, wave planning, cutover), see `general/workload-migration.md`. For network infrastructure design, see `general/networking.md`.

## Checklist

- [ ] **[Critical]** Has every virtual appliance been inventoried with vendor, product version, and current hypervisor?
- [ ] **[Critical]** Has the vendor support matrix been verified for the target hypervisor and appliance version?
- [ ] **[Critical]** Has license portability been assessed per vendor? (hypervisor-tied vs agnostic, re-licensing cost estimated)
- [ ] **[Critical]** Has the HA pair migration sequence been documented? (standby-first with failover)
- [ ] **[Critical]** Has a full configuration backup/export been performed and validated for each appliance?
- [ ] **[Critical]** Have appliance-specific network requirements been confirmed on the target hypervisor? (promiscuous mode, VLAN trunking, jumbo frames)
- [ ] **[Recommended]** Has a re-deployment vs in-place migration decision been made for each appliance?
- [ ] **[Recommended]** Has a test deployment been performed on the target hypervisor before production migration?
- [ ] **[Recommended]** Has the vendor TAC/support been engaged to confirm migration path and support coverage?
- [ ] **[Recommended]** Has version compatibility been confirmed? (some appliance versions require upgrade before migration)
- [ ] **[Recommended]** Has a re-licensing budget been estimated and approved?
- [ ] **[Optional]** Has the migration been used as an opportunity to consolidate or right-size appliance tiers?
- [ ] **[Optional]** Has automation been prepared for bulk re-deployment? (Terraform, Ansible, vendor-specific APIs)

## Why This Matters

Virtual appliances are not generic VMs. They are vendor-controlled images with specific hypervisor dependencies, licensing models, and network requirements that do not transfer automatically between platforms. A standard VM migration tool (MGN, Azure Migrate, Move) cannot migrate an F5 BIG-IP or Palo Alto VM-Series the way it migrates a Linux application server.

Treating virtual appliances as regular VMs during a hypervisor migration leads to three common failures: license activation failures on the target platform, missing network capabilities (promiscuous mode, VLAN trunking) that break appliance functionality, and unsupported configurations that void vendor support. Each of these can cause extended outages on critical infrastructure services like load balancing, DNS/DHCP, and firewalling.

The correct approach is always **re-deploy on the target hypervisor using vendor-provided images**, import the configuration, and validate before cutover.

## Common Decisions (ADR Triggers)

- **Re-deploy vs in-place migration** -- whether to perform fresh deployment with config import or attempt image conversion (re-deploy is almost always correct)
- **License strategy** -- re-license on new hypervisor vs negotiate portable licenses vs switch to subscription model
- **HA migration approach** -- standby-first failover vs parallel deployment with traffic shift
- **Version upgrade timing** -- upgrade before migration, during migration, or after migration
- **Appliance consolidation** -- whether to reduce appliance count or change tiers during migration
- **Vendor support engagement** -- whether to open proactive support cases before migration

## Vendor Hypervisor Compatibility Matrix

The following matrix reflects documented vendor support as of early 2026. **Always verify against the vendor's current compatibility matrix before migration planning** -- support changes with each appliance software release.

| Vendor / Product | VMware ESXi | KVM | Microsoft Hyper-V | Nutanix AHV | AWS | Azure | GCP |
|---|---|---|---|---|---|---|---|
| **F5 BIG-IP VE** | Yes | Yes | Yes (Gen 1) | Yes (AOS 5.20+, 6.5 LTS) | Yes | Yes | Yes |
| **Infoblox vNIOS** | Yes | Yes | Yes | Yes (AHV 5.11+, 6.x LTS) | Yes | Yes | No |
| **Palo Alto VM-Series** | Yes | Yes | Yes | Yes (uses KVM qcow2 base) | Yes | Yes | Yes |
| **Zscaler (App Connector, PSE)** | Yes | Yes | No | Yes | Yes | Yes | Yes |
| **Cisco ISE** | Yes | Yes | Yes | Yes (ISO-based deploy only) | No (cloud-native variant) | No | No |
| **Check Point CloudGuard** | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

### Key Platform Notes

**F5 BIG-IP VE on AHV:** F5 provides official documentation and migration guides for VMware-to-Nutanix migration. Requires minimum 2 vCPU and 4 GB memory, with 2 GB additional memory per additional vCPU. Deploy using vendor-provided QCOW2 image.

**Infoblox vNIOS on AHV:** Supported with specific model mappings (not all vNIOS models are available on every hypervisor). Infoblox provides a Nutanix-specific deployment guide. Nutanix Calm blueprints are available for orchestrated DDI provisioning.

**Zscaler on AHV:** Zscaler supports App Connector, Private Service Edge, and Decoy Connector deployment on AHV. These are lightweight connector appliances, not full proxy appliances -- the Zscaler cloud performs the heavy processing.

**Cisco ISE on AHV:** Must be deployed from the standard ISE .iso image. OVA templates are not supported on AHV. Requires careful NIC and resource mapping per the Cisco installation guide.

**Palo Alto VM-Series on AHV:** Uses the KVM base image (qcow2 format). Deployed as a standard KVM guest on AHV. Requires promiscuous mode or VLAN trunking for inline deployment.

## License Portability Assessment

### License Models by Vendor

| Vendor | License Model | Hypervisor-Tied? | Migration Impact |
|---|---|---|---|
| **F5 BIG-IP VE** | Registration key (perpetual or subscription) | Tied to VM identity, not hypervisor | Revoke and reactivate on new VM (v12.1.3.3+ / v13.1.0.2+). Contact F5 support for "Allow Move" if original VM is inaccessible. |
| **Infoblox vNIOS** | Per-appliance license, tied to hardware ID | Tied to virtual hardware ID | New license typically required. Engage Infoblox support for license transfer. |
| **Palo Alto VM-Series** | Auth code + capacity license | Not hypervisor-tied | Deactivate on source, reactivate on target via Palo Alto support portal. Capacity (credits) licensing simplifies portability. |
| **Zscaler** | Cloud subscription | Not appliance-tied | Connectors are provisioned from the Zscaler portal with provisioning keys. No re-licensing needed -- deploy new connector, decommission old. |
| **Cisco ISE** | Smart Licensing (device-based) | Not hypervisor-tied | Register new VM with Cisco Smart Account. Deregister old VM. |
| **Check Point CloudGuard** | BYOL or PAYG | Not hypervisor-tied | Re-deploy with same license via SmartConsole or Check Point user center. |

### Re-Licensing Budget Estimation

When planning a hypervisor migration involving virtual appliances, estimate re-licensing costs early:

1. **Inventory all appliance licenses** -- registration keys, support contracts, add-on modules
2. **Contact each vendor** -- confirm whether existing licenses transfer or require new purchases
3. **Identify subscription conversion opportunities** -- some vendors offer perpetual-to-subscription conversion during migration
4. **Account for support contract alignment** -- migrated appliances may need support contract updates to cover the new hypervisor
5. **Budget 10-15% contingency** -- unexpected licensing issues are common during platform migrations

## Configuration Export/Import Procedures

### General Workflow

```
1. Document current running configuration (screenshot + export)
2. Export configuration using vendor-specific method
3. Validate export file is complete and parseable
4. Deploy fresh appliance on target hypervisor using vendor image
5. Perform base configuration (management IP, licensing)
6. Import configuration
7. Validate imported configuration matches source
8. Test functionality before traffic cutover
```

### Vendor-Specific Export/Import

| Vendor | Export Method | Import Method | Caveats |
|---|---|---|---|
| **F5 BIG-IP** | UCS archive (`tmsh save sys ucs`) | `tmsh load sys ucs <file>` | UCS includes certificates/keys. Platform-specific settings (MAC, UUID) are excluded on cross-platform restore. Use `no-platform-check` flag. |
| **Infoblox** | Database backup via Grid Manager or CLI (`set backup`) | Restore via Grid Manager or CLI | Grid Master must be restored first. Member restores follow. Ensure NIOS version matches between source and target. |
| **Palo Alto VM-Series** | `export named-config running-config.xml` via CLI or API | `import named-config` then `load config` | Panorama-managed devices: push config from Panorama to new VM after registration. Standalone: export/import XML config. |
| **Zscaler** | Configuration lives in Zscaler cloud portal | Re-provision connector with same provisioning key | No config migration needed. Deploy new connector, assign to same connector group. |
| **Cisco ISE** | Configuration backup via GUI or CLI (`backup`) | Restore on new deployment (`restore`) | Repository (SFTP/FTP) must be accessible from both source and target. Restore preserves all policies, certificates, and node configuration. |
| **Check Point** | `migrate export` or SmartConsole backup | `migrate import` on new installation | Security policy and objects export via SmartConsole. Gateway-specific settings require manual configuration. |

### Critical Export Validation Steps

- **Verify file integrity** -- checksum or hash comparison
- **Confirm certificate/key inclusion** -- TLS certificates, CA chains, private keys
- **Document manual configurations** -- some settings are not captured in exports (e.g., VLAN interface mappings, route table entries that reference hypervisor-specific adapters)
- **Test restore on a lab instance** -- never perform first restore directly in production

## Re-Deployment vs In-Place Migration Decision

Virtual appliance migration is almost always a **re-deployment** rather than an in-place migration. The decision tree below captures the rare exceptions.

```
Is the source and target the same hypervisor family?
  |
  +-- No --> RE-DEPLOY (always)
  |          Different hypervisors require vendor-provided images.
  |          Image conversion (vmdk-to-qcow2) is unsupported by vendors.
  |
  +-- Yes --> Is it a minor version change (e.g., ESXi 7 to 8)?
                |
                +-- Yes --> Does the vendor support in-place hypervisor upgrade?
                |             |
                |             +-- Yes --> IN-PLACE MIGRATION may be viable
                |             |          (vMotion, live migration)
                |             |
                |             +-- No --> RE-DEPLOY
                |
                +-- No --> RE-DEPLOY
```

### Why Re-Deployment Is Preferred

- Vendor support requires deployment from official images -- converted images void support
- Clean deployment eliminates accumulated configuration drift
- Provides opportunity to upgrade appliance software version
- Avoids hypervisor-specific driver and tooling incompatibilities
- Configuration import validates that all settings are explicitly documented

### When In-Place Migration Works

- Same hypervisor family (e.g., ESXi host upgrade within the same major version)
- Vendor explicitly documents support for the migration path
- No hypervisor-specific driver changes between versions
- Example: vMotion between ESXi hosts running the same version

## HA Pair Migration Sequencing

HA pairs require careful sequencing to maintain service availability. The standard approach is **standby-first migration**.

### Standard HA Migration Sequence

```
Phase 1: Preparation
  - Verify HA pair health (both nodes active/standby, sync current)
  - Document current failover configuration (preemptive vs non-preemptive)
  - Confirm failover triggers and timers
  - Identify all floating/virtual IPs, VLAN interfaces, and monitored objects

Phase 2: Standby Node Migration
  - Deploy new appliance on target hypervisor
  - Import configuration to new node
  - License and activate new node
  - Join new node to HA pair as standby (if supported)
    OR: Build as standalone, prepare for failover swap
  - Validate standby node is synchronized and healthy

Phase 3: Controlled Failover
  - Schedule maintenance window
  - Force failover to new standby node (now active on target hypervisor)
  - Validate all services are running on new active node
  - Monitor for 15-30 minutes minimum before proceeding

Phase 4: Primary Node Migration
  - Old primary is now standby (or decommissioned)
  - Deploy second new appliance on target hypervisor
  - Import configuration, license, join as new standby
  - Validate HA pair health on target hypervisor

Phase 5: Validation
  - Test failover in both directions
  - Verify all monitored objects and health checks
  - Confirm sync status between nodes
  - Update monitoring systems with new node identities
```

### Vendor-Specific HA Considerations

| Vendor | HA Model | Migration Notes |
|---|---|---|
| **F5 BIG-IP** | Active/Standby, Active/Active (DSC) | Config sync between nodes. New node joins device group. Use `tmsh run cm config-sync` after join. Traffic groups must be reassigned. |
| **Infoblox** | Grid with Grid Master + Members | Migrate members first, Grid Master last. Grid Master candidate can be promoted if Grid Master migration fails. |
| **Palo Alto VM-Series** | Active/Passive, Active/Active | HA link requires Layer 2 adjacency. Verify HA heartbeat and data link connectivity on target hypervisor. Session sync may require dedicated interface. |
| **Cisco ISE** | Distributed deployment (PAN, MnT, PSN nodes) | Migrate PSN nodes first (they handle authentication). PAN (admin) node last. Secondary PAN provides redundancy during migration. |
| **Check Point** | ClusterXL (Active/Standby, Active/Active, VRRP) | Migrate standby member first. Use `cphaprob stat` to verify cluster health. Sync requires Layer 2 or Layer 3 connectivity depending on mode. |

### HA Migration Anti-Patterns

- **Never migrate both HA nodes simultaneously** -- this eliminates all redundancy
- **Never skip failover testing** on the target hypervisor before migrating the second node
- **Never assume HA will "just work"** across hypervisor boundaries during migration -- most HA protocols require Layer 2 adjacency that may not exist between source and target platforms
- **Never migrate the primary/active node first** -- always migrate the standby to minimize service impact

## Appliance-Specific Network Requirements

Virtual appliances often require network capabilities beyond what standard VMs need. Verify these on the target hypervisor before migration.

### Network Feature Requirements by Appliance Type

| Requirement | Load Balancers (F5) | Firewalls (PA, CP) | DNS/DHCP (Infoblox) | NAC (Cisco ISE) |
|---|---|---|---|---|
| **Promiscuous mode** | Required for L2 bridging | Required for inline/TAP mode | Not required | May be required for profiling |
| **VLAN trunking (802.1Q)** | Required for multi-VLAN | Required for zone-based | Required for multi-subnet | Required for multi-VLAN auth |
| **Jumbo frames (MTU 9000)** | Recommended for performance | Depends on transit traffic | Not typically needed | Not required |
| **Multiple NICs** | Minimum 3 (mgmt + internal + external) | Minimum 3 (mgmt + trust + untrust) | Minimum 2 (mgmt + service) | Minimum 2 (mgmt + service) |
| **MAC address preservation** | Important for VRRP/failover | Important for HA | Not critical | Not critical |
| **SR-IOV support** | Recommended for high throughput | Recommended for high throughput | Not needed | Not needed |

### Hypervisor-Specific Network Configuration

**VMware ESXi:**
- Promiscuous mode: Enabled per port group on vSwitch or Distributed Switch
- VLAN trunking: Supported via VLAN ID 4095 (trunk all) or specific VLAN ranges
- Multiple NICs: Standard vmxnet3 adapters

**KVM / Nutanix AHV:**
- Promiscuous mode: Requires bridge configuration or Open vSwitch with `promisc on`
- VLAN trunking: Supported via Open vSwitch trunk ports or Linux bridge VLAN filtering
- AHV-specific: Use Managed Networks with VLAN configuration in Prism

**Microsoft Hyper-V:**
- Promiscuous mode: Requires port mirroring configuration on Hyper-V Virtual Switch
- VLAN trunking: Supported via Hyper-V Virtual Switch trunk mode
- Multiple NICs: Synthetic network adapters (not legacy)

## Version Compatibility on Target Hypervisor

### Pre-Migration Version Assessment

Not all appliance software versions are supported on all hypervisor versions. Follow this process:

1. **Document current appliance software version** (e.g., BIG-IP 15.1.8, PAN-OS 10.2.5)
2. **Check vendor compatibility matrix** for that version against the target hypervisor and version
3. **If not supported:**
   - Upgrade the appliance software to a version that supports the target hypervisor
   - Perform the upgrade on the **source** hypervisor before migration (upgrade and migration are separate steps)
4. **If the required version is EOL on source:**
   - Deploy the new version directly on the target hypervisor
   - Import configuration (verify config compatibility between versions)

### Version Upgrade Timing

| Approach | When to Use | Risk |
|---|---|---|
| **Upgrade before migration** | Current version is near-EOL; target hypervisor requires newer version | Low -- upgrade in familiar environment |
| **Upgrade during migration** | Fresh deploy on target at newer version, import config | Medium -- two changes at once, harder to isolate issues |
| **Upgrade after migration** | Current version is supported on target; upgrade can wait | Low -- migrate first, stabilize, then upgrade |

**Recommended approach:** Upgrade before migration when possible. This separates the two risk events (version upgrade and platform migration) and allows independent validation of each change.

## Migration Execution Checklist

### Per-Appliance Migration Runbook Template

```
Appliance: [vendor] [product] [version]
Current Hypervisor: [platform and version]
Target Hypervisor: [platform and version]
HA Role: [standalone / active / standby]

Pre-Migration:
  [ ] Vendor support matrix verified for target hypervisor
  [ ] License portability confirmed (re-license budget approved if needed)
  [ ] Configuration exported and validated
  [ ] Network requirements confirmed on target (VLANs, promiscuous mode, NIC count)
  [ ] Target hypervisor image obtained from vendor
  [ ] Test deployment completed in lab/non-production
  [ ] Vendor TAC case opened (if applicable)
  [ ] Rollback plan documented

Migration:
  [ ] New appliance deployed on target hypervisor from vendor image
  [ ] Base configuration applied (management IP, DNS, NTP)
  [ ] License activated on new appliance
  [ ] Full configuration imported
  [ ] Configuration validation passed (diff source vs target)
  [ ] HA join/sync completed (if applicable)
  [ ] Functional testing passed (traffic processing, policy enforcement)

Post-Migration:
  [ ] Monitoring updated with new appliance identity
  [ ] DNS/IP records updated if management addresses changed
  [ ] Old appliance decommissioned after validation period
  [ ] License deactivated/revoked on old appliance
  [ ] Documentation updated with new platform details
```

## Reference Links

- [F5 BIG-IP VE Compatibility](https://my.f5.com/manage/s/article/K9476)
- [Infoblox vNIOS Deployment](https://docs.infoblox.com/)
- [Palo Alto VM-Series Compatibility](https://docs.paloaltonetworks.com/compatibility-matrix/vm-series-firewalls)
- [Cisco ISE Installation Guide](https://www.cisco.com/c/en/us/support/security/identity-services-engine/series.html)

## See Also

- `general/workload-migration.md` -- General workload migration strategy and wave planning
- `general/networking.md` -- Cloud and hybrid networking patterns
- `general/load-balancing-onprem.md` -- On-premises load balancer design
- `general/disaster-recovery.md` -- DR planning for migrated infrastructure
- `general/networking-physical.md` -- Physical network requirements
