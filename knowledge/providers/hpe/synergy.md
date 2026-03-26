# HPE Synergy Composable Infrastructure

## Scope

HPE Synergy composable infrastructure platform: frame architecture, compute modules, Image Streamer for stateless provisioning, fabric modules and Virtual Connect, storage integration, and composable workload management. Covers initial deployment, workload composition, and lifecycle operations for software-defined datacenter designs.

## Checklist

- [ ] [Critical] Is the Synergy frame count and layout planned for the workload? (each frame holds up to 12 half-height or 6 full-height compute modules, interconnect bays for fabric modules, and management appliance bays)
- [ ] [Critical] Is HPE OneView deployed as the management plane for Synergy, with server profile templates defining compute, storage, network, and firmware configurations for all module types?
- [ ] [Critical] Are Synergy Virtual Connect SE fabric modules configured correctly for the network topology? (uplink sets, network sets, logical interconnect groups, and redundant module pairs for HA)
- [ ] [Critical] Is the Synergy Composer (management appliance) deployed in a redundant pair across frames, and is the Composer's IP address and credentials secured on the management network?
- [ ] [Critical] Are logical enclosures configured to group frames that share interconnect and management domains, with firmware baselines applied at the logical enclosure level?
- [ ] [Critical] Is the fabric module uplink bandwidth sufficient? (each Virtual Connect SE 100Gb module provides multiple 100GbE uplinks -- plan for N+1 uplink redundancy and oversubscription ratios)
- [ ] [Recommended] Is HPE Image Streamer deployed for stateless compute? (OS volumes are streamed from golden images, enabling rapid provisioning and eliminating per-server OS state)
- [ ] [Recommended] Are Image Streamer deployment plans and golden images versioned and tested, with a rollback strategy for failed image updates?
- [ ] [Recommended] Is Synergy storage configured appropriately? (direct-attach SAS via D3940 storage module for local storage workloads, or SAN-boot via Fibre Channel fabric modules for shared storage)
- [ ] [Recommended] Are compute module types selected based on workload requirements? (SY480 Gen10+ for general compute, SY660 Gen10+ for GPU-accelerated workloads, SY380 Gen10+ for storage-dense configurations)
- [ ] [Recommended] Is the firmware update strategy tested with rolling updates across compute modules in a logical enclosure to avoid full-frame outages?
- [ ] [Recommended] Is power delivery planned at the frame level? (each frame requires redundant power supplies, and total frame power draw must account for fully populated compute and interconnect bays)
- [ ] [Optional] Is Synergy integrated with HPE GreenLake for consumption-based billing and cloud-like operations management?
- [ ] [Optional] Is the composable API (OneView REST API) integrated into the provisioning pipeline for infrastructure-as-code workflows using Terraform, Ansible, or custom scripts?
- [ ] [Optional] Is multi-frame link topology planned for large deployments? (master/satellite frame relationships, inter-frame link modules for east-west traffic between frames)

## Why This Matters

Synergy is HPE's composable infrastructure platform, designed to treat compute, storage, and networking as fluid resource pools that can be composed on demand. The key differentiator is Image Streamer, which enables truly stateless compute modules that boot from streamed golden images -- eliminating OS drift and enabling rapid repurposing of hardware. However, Synergy has a steep initial planning curve: frame layout, interconnect module selection, and logical enclosure design must be right from the start because changing the fabric topology later requires disruptive reconfiguration. Virtual Connect fabric modules create a software-defined networking layer inside the frame, which simplifies downstream switch configuration but requires careful uplink planning to avoid bandwidth bottlenecks. Synergy is being positioned alongside GreenLake for cloud-like operations, but the on-premises management model through OneView Composer remains the operational core.

## Common Decisions (ADR Triggers)

- **Frame topology** -- single frame (up to 12 compute modules) vs multi-frame (up to 21 frames per management domain) based on scale requirements
- **Compute module selection** -- SY480 (2-socket general purpose) vs SY660 (GPU-capable) vs SY380 (storage-dense) per workload type
- **Boot strategy** -- Image Streamer (stateless, streamed OS) vs SAN boot (FC-attached LUNs) vs local disk boot (D3940 storage module)
- **Fabric module type** -- Virtual Connect SE 100Gb (Ethernet) vs Fibre Channel fabric modules vs mixed, based on storage connectivity requirements
- **Storage architecture** -- D3940 direct-attach storage modules vs external SAN (3PAR/Alletra/Nimble) via FC fabric modules vs hyperconverged (vSAN on Synergy)
- **Management model** -- OneView on-premises Composer vs GreenLake for Compute Ops Management (cloud-managed)
- **Image lifecycle** -- Image Streamer golden image pipeline with CI/CD vs traditional per-server OS patching

## Reference Links

- [HPE Synergy Planning Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=c05117790) -- frame layout, power, cooling, and network planning for Synergy deployments
- [HPE Synergy Image Streamer User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00001116en_us) -- deployment plan creation, golden image management, and OS streaming configuration
- [HPE Virtual Connect SE 100Gb F32 Module Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00001750en_us) -- fabric module configuration, uplink sets, and logical interconnect groups
- [HPE OneView for Synergy](https://www.hpe.com/us/en/integrated-systems/software.html) -- composable management platform for server profiles, firmware, and network configuration
- [HPE Synergy Reference Architecture for VMware](https://www.hpe.com/psnow/doc/a00056052enw) -- validated design for running VMware vSphere on Synergy frames

## See Also

- `providers/hpe/proliant.md` -- ProLiant rack server management and iLO
- `providers/hpe/greenlake.md` -- HPE GreenLake cloud services
- `providers/hpe/nimble-alletra.md` -- Nimble/Alletra storage for Synergy SAN integration
- `general/compute.md` -- general compute architecture patterns
- `general/hardware-sizing.md` -- hardware sizing methodology
