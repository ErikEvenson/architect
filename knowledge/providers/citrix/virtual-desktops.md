# Citrix Virtual Apps and Desktops

## Scope

This document covers Citrix Virtual Apps and Desktops (CVAD) architecture, including Delivery Controller design, StoreFront and Workspace configuration, Citrix ADC (NetScaler) and Gateway for external access, Machine Creation Services (MCS) vs Provisioning Services (PVS) for image management, profile management (Citrix UPM, FSLogix), Citrix Cloud DaaS (Desktop as a Service), Workspace app client, migration from on-premises CVAD to Citrix Cloud, and licensing models (per-user/per-device, on-premises vs cloud service).

## Checklist

- [ ] **[Critical]** Is the Delivery Controller infrastructure designed with N+1 redundancy (minimum 2 controllers per site) with appropriate SQL Server backend (AlwaysOn AG or mirroring for production) and site database sizing?
- [ ] **[Critical]** Is StoreFront (on-premises) or Workspace (cloud) configured with store aggregation, optimal gateway routing, and beacon points for internal/external detection?
- [ ] **[Critical]** Is Citrix ADC (NetScaler) or Gateway deployed for external access with proper SSL certificates, ICA proxy configuration, session policies, and endpoint analysis scans?
- [ ] **[Critical]** Is the image provisioning strategy defined -- MCS (simpler, cloud-friendly, identity disk management) vs PVS (network-boot streaming, higher density, more complex infrastructure)?
- [ ] **[Critical]** Is the hosting connection configured for the target hypervisor or cloud platform (vSphere, Nutanix AHV, Azure, AWS, GCP) with appropriate service account permissions and resource location sizing?
- [ ] **[Recommended]** Is the user profile strategy defined -- Citrix Profile Management (UPM) vs FSLogix Profile Containers vs Citrix Profile Management with container-based profiles -- with profile storage location and sizing?
- [ ] **[Recommended]** Is Citrix Policy configuration designed for HDX protocol optimization, including adaptive transport (EDT over UDP), display quality settings, multimedia redirection, and client drive mapping based on user segment?
- [ ] **[Recommended]** Are Zones configured for multi-site deployments with local host caches for connection brokering resiliency during WAN outages or cloud control plane disruptions?
- [ ] **[Recommended]** Is the application delivery strategy defined -- published desktops vs published applications vs a combination, with FlexCast model (pooled, dedicated, remote PC access) per user segment?
- [ ] **[Recommended]** Is Citrix Cloud DaaS evaluated for control plane migration (cloud-hosted Delivery Controllers, monitoring, and management) while keeping workloads on-premises or in any cloud resource location?
- [ ] **[Optional]** Is Workspace Environment Management (WEM) deployed for user environment optimization, including CPU/memory management, logon optimization, and profile-based actions?
- [ ] **[Optional]** Is App Layering (formerly Unidesk) evaluated for OS, platform, and application layer separation in complex image management scenarios?
- [ ] **[Optional]** Is Session Recording configured for compliance-sensitive environments requiring audit trails of user desktop/application sessions?

## Why This Matters

Citrix Virtual Apps and Desktops is the most feature-rich and flexible virtual desktop and application delivery platform, supporting the widest range of hypervisors, cloud platforms, and deployment models. The architecture complexity, however, is significantly higher than competing platforms -- a full on-premises CVAD deployment involves Delivery Controllers, StoreFront, Citrix ADC, SQL databases, provisioning infrastructure (MCS or PVS), and profile management, each requiring separate design decisions. SQL Server database design is particularly critical: a failed site database without proper HA configuration causes a full site outage, though Local Host Cache provides limited brokering continuity.

Citrix Cloud DaaS (the cloud-managed version) substantially reduces on-premises infrastructure complexity by moving the control plane to Citrix-managed cloud services, while workloads remain in the customer's datacenter or cloud. This hybrid model is Citrix's strategic direction and simplifies patching, monitoring, and management. However, it introduces dependency on Citrix Cloud availability and requires reliable internet connectivity from resource locations. The licensing model (per-user/per-device, Universal hybrid-rights licenses) and Citrix's transition from perpetual to subscription licensing are important cost-planning factors.

## Common Decisions (ADR Triggers)

- **MCS vs PVS** -- MCS (simpler, cloud-native support, storage-based) vs PVS (network streaming, higher density, requires PVS infrastructure), or both for different workload types
- **On-premises vs Citrix Cloud DaaS** -- self-managed control plane vs cloud-managed, connectivity requirements, compliance constraints
- **Citrix ADC vs alternative gateway** -- dedicated Citrix ADC (full HDX optimization, EPA, nFactor auth) vs simplified gateway, ADC sizing (VPX/MPX/SDX)
- **Profile management** -- Citrix UPM vs FSLogix vs UPM with container technology, profile storage (file share vs Azure Files vs NetApp)
- **Published apps vs published desktops** -- application-centric delivery vs full desktop, user experience and management tradeoffs
- **HDX transport** -- EDT (UDP-based, optimized for high-latency/lossy networks) vs TCP, Rendezvous protocol for Citrix Cloud direct path
- **Multi-site design** -- Zones with satellite controllers vs independent sites, GSLB on Citrix ADC for global load distribution
- **Licensing model** -- per-user vs per-device, Universal license (hybrid rights for on-premises + cloud), subscription vs perpetual (legacy)

## See Also

- `general/vdi-migration-strategy.md` -- VDI migration planning patterns
- `providers/citrix/adc.md` -- Citrix ADC (NetScaler) architecture
