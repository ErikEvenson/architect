# HPE ProLiant Servers

## Scope

HPE ProLiant rack and tower servers: model selection (DL, ML, DL Gen11), iLO (Integrated Lights-Out) management, firmware lifecycle, HPE OneView integration, server profiles, and hardware configuration for datacenter deployments. Covers initial provisioning, ongoing management, and capacity expansion.

## Checklist

- [ ] [Critical] Is the correct ProLiant platform selected for the workload? (DL series for rack-dense compute, ML series for tower/edge, DL Gen11 for latest Intel/AMD with PCIe Gen5 and DDR5)
- [ ] [Critical] Is iLO firmware updated to the latest revision and configured with a dedicated management network (not shared with production traffic)?
- [ ] [Critical] Are iLO accounts configured with role-based access control, Active Directory/LDAP integration, and default credentials changed before deployment?
- [ ] [Critical] Is HPE OneView deployed for fleet management when managing more than a handful of servers, with server profiles defining BIOS, boot, firmware, and network configurations as code?
- [ ] [Critical] Is the firmware baseline established and managed via HPE OneView or iLO Amplifier Pack, with Service Pack for ProLiant (SPP) tested in a staging environment before production rollout?
- [ ] [Critical] Is the RAID controller configured correctly? (HPE Smart Array or MR controller with appropriate RAID level, write cache policy, and battery/capacitor-backed cache for write-intensive workloads)
- [ ] [Recommended] Are server profiles in OneView used to template BIOS settings, boot order, firmware levels, and logical network connections for repeatable provisioning?
- [ ] [Recommended] Is Intelligent Provisioning used for initial OS deployment, or is a PXE/image-based deployment pipeline (e.g., Ansible with Redfish) established for fleet-scale provisioning?
- [ ] [Recommended] Is HPE Agentless Management (AMS) or iLO-based agentless monitoring configured to report hardware health to management tools without in-OS agents?
- [ ] [Recommended] Is the power supply configuration N+1 redundant with the correct input power (AC vs DC, single-phase vs three-phase), and are power capping policies configured for dense deployments?
- [ ] [Recommended] Are thermal and fan policies reviewed for the installation environment? (ProLiant Gen11 supports extended ambient temperature up to 40C/45C in specific configurations)
- [ ] [Recommended] Is the Redfish API used for automation instead of legacy RIBCL/SMASH, with scripts or Ansible modules targeting the iLO Redfish endpoint for firmware updates, power control, and configuration?
- [ ] [Recommended] Is HPE InfoSight for Servers enabled to provide predictive analytics, firmware recommendations, and proactive support case generation?
- [ ] [Optional] Is HPE Trusted Platform Module (TPM 2.0) enabled for measured boot, BitLocker/LUKS key sealing, and attestation in security-sensitive environments?
- [ ] [Optional] Is Silicon Root of Trust verified as active? (Gen10+ ProLiant servers embed a hardware root of trust in the iLO ASIC that validates firmware integrity on every boot)
- [ ] [Optional] Is Persistent Memory (Intel Optane PMem or CXL-attached memory) evaluated for latency-sensitive database or caching workloads on supported Gen10/Gen11 models?

## Why This Matters

ProLiant servers are one of the most widely deployed x86 server platforms in enterprise datacenters. iLO management is central to the operational model -- misconfigured iLO (default passwords, shared networks, outdated firmware) is a common attack vector and operational liability. HPE's Service Pack for ProLiant bundles firmware, drivers, and agents into a tested baseline, but applying SPP to production without staging has caused outages from BIOS setting resets and NIC firmware regressions. OneView server profiles are the key to treating bare-metal configuration as infrastructure-as-code, but they require careful planning around logical enclosures, network sets, and firmware baselines. Gen11 introduces PCIe Gen5 and DDR5, which changes NIC and GPU compatibility assumptions from Gen10 designs.

## Common Decisions (ADR Triggers)

- **Server tier** -- DL360 (1U dense) vs DL380 (2U expandable) vs DL560 (4-socket) based on workload density and expansion requirements
- **Management platform** -- iLO standalone vs HPE OneView vs HPE GreenLake for Compute Ops Management (cloud-managed)
- **Firmware lifecycle** -- SPP-based updates via OneView (scheduled, staged) vs manual iLO updates vs GreenLake cloud-managed firmware
- **RAID controller** -- HPE Smart Array (hardware RAID) vs software RAID vs pass-through for hyperconverged/SDS (VMware vSAN, Nutanix)
- **Deployment method** -- Intelligent Provisioning (interactive) vs PXE + Kickstart/Preseed vs Ansible Redfish automation vs OneView server profiles
- **Out-of-band network** -- Dedicated iLO NIC on isolated management VLAN vs shared NIC (not recommended for production)
- **Security posture** -- Silicon Root of Trust + TPM + Secure Boot full chain vs selective enablement based on compliance requirements

## Reference Links

- [HPE ProLiant Gen11 QuickSpecs](https://www.hpe.com/psnow/doc/a50002942enw) -- detailed specifications for Gen11 DL and ML server models
- [HPE iLO 6 User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00002244en_us) -- complete iLO 6 (Gen11) configuration and management reference
- [HPE OneView User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00001116en_us) -- server profile templates, firmware management, and fleet operations
- [HPE Service Pack for ProLiant (SPP)](https://support.hpe.com/connect/s/softwaredetails?language=en_US&softwareId=MTX_eed59a3188d84e3ea8de543e05) -- firmware and driver bundle release notes and download
- [HPE Redfish API Reference](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00001423en_us) -- RESTful API for iLO automation, configuration, and monitoring
- [HPE InfoSight for Servers](https://www.hpe.com/us/en/servers/infosight.html) -- AI-driven predictive analytics for ProLiant server fleet

## See Also

- `general/compute.md` -- general compute architecture patterns
- `general/hardware-sizing.md` -- hardware sizing methodology
- `general/hardware-vendor-partnerships.md` -- vendor partnership considerations
- `providers/hpe/synergy.md` -- HPE Synergy composable infrastructure
- `providers/hpe/greenlake.md` -- HPE GreenLake cloud services
