# Windows Server

## Scope

Windows Server platform decisions: edition selection (Standard vs Datacenter), installation mode (Server Core vs Desktop Experience), management tooling (Windows Admin Center, RSAT), update infrastructure (WSUS, Windows Update for Business), Windows Firewall with Advanced Security, Hyper-V role, Storage Spaces Direct (S2D), licensing model (per-core with 16-core minimum, CALs), Windows Server 2025 features, Extended Security Updates (ESU) for legacy versions, and migration strategies from older releases (2012 R2, 2016, 2019).

## Checklist

- [ ] [Critical] Is the correct Windows Server edition selected based on workload requirements? (Standard for general workloads with up to 2 VMs per license, Datacenter for unlimited VMs, dense virtualization, S2D, Shielded VMs, and Software-Defined Networking)
- [ ] [Critical] Is Server Core the default installation option unless a specific application requires Desktop Experience? (Server Core reduces attack surface, patching footprint, and reboot frequency)
- [ ] [Critical] Is the licensing model correctly calculated using per-core licensing with the 16-core minimum per physical server and 8-core minimum per physical processor, including Client Access Licenses (CALs) for every user or device?
- [ ] [Critical] Are servers running Windows Server 2012 R2 or older identified for migration or ESU enrollment before end-of-support dates, with an upgrade path documented?
- [ ] [Critical] Is Windows Firewall with Advanced Security enabled on all servers with explicit inbound/outbound rules, and are Group Policy-managed firewall profiles configured for domain, private, and public networks?
- [ ] [Recommended] Is Windows Admin Center deployed as a gateway server for centralized browser-based management of Server Core and Desktop Experience instances?
- [ ] [Recommended] Is WSUS or Windows Update for Business configured for controlled patch deployment with approval workflows, maintenance windows, and staged rollout rings?
- [ ] [Recommended] Is Hyper-V role deployment planned with host clustering (Windows Server Failover Clustering), live migration networking, and VM placement rules for high availability?
- [ ] [Recommended] Is Storage Spaces Direct (S2D) evaluated for hyperconverged or disaggregated storage, with correct disk tier configuration (NVMe cache, SSD/HDD capacity) and cluster validation completed?
- [ ] [Recommended] Are Windows Server 2025 features evaluated for new deployments, including hotpatching (Azure Arc-enabled), SMB over QUIC, delegated Managed Service Accounts (dMSA), and Credential Guard enabled by default?
- [ ] [Recommended] Is a consistent baseline security configuration applied via Group Policy or Desired State Configuration (DSC), including SMBv1 disabled, TLS 1.0/1.1 disabled, and NTLMv1 blocked?
- [ ] [Optional] Is Windows Server Insider or Long-Term Servicing Channel (LTSC) vs Annual Channel evaluated based on workload stability requirements?
- [ ] [Optional] Are Shielded VMs configured for sensitive workloads running on Hyper-V with Host Guardian Service (HGS) attestation (Datacenter edition only)?

## Why This Matters

Windows Server is the foundation for Active Directory, file services, SQL Server, and many line-of-business applications. Edition and licensing mistakes are expensive and difficult to reverse -- selecting Standard edition for a dense Hyper-V host means purchasing additional licenses for every pair of VMs, while Datacenter provides unlimited virtualization rights. Server Core should be the default for security and operational efficiency, but many organizations default to Desktop Experience out of habit, increasing patch burden and attack surface across every server.

Migration planning from legacy versions is equally important. Windows Server 2012 R2 reached end of extended support in October 2023, and running unsupported operating systems creates compliance and security risks. ESU programs provide a bridge but at increasing annual cost, making in-place upgrades or rebuilds on current versions the preferred long-term strategy.

## Common Decisions (ADR Triggers)

- **Edition selection** -- Standard (cost-effective for physical or lightly virtualized) vs Datacenter (unlimited VMs, S2D, SDN, Shielded VMs)
- **Installation mode** -- Server Core (reduced surface, headless) vs Desktop Experience (GUI, legacy app compatibility)
- **Management approach** -- Windows Admin Center (modern, browser-based) vs RSAT (traditional MMC snap-ins) vs System Center (enterprise-scale)
- **Patch infrastructure** -- WSUS (on-premises, full control) vs Windows Update for Business (cloud-managed rings) vs SCCM/Intune
- **Virtualization platform** -- Hyper-V (included with Windows Server) vs VMware vSphere vs Nutanix AHV
- **Hyperconverged storage** -- Storage Spaces Direct (native S2D) vs Nutanix vs VMware vSAN
- **Legacy OS strategy** -- In-place upgrade vs side-by-side migration vs ESU enrollment vs application modernization

## See Also

- `providers/microsoft/active-directory.md` -- Active Directory domain services and identity
- `providers/azure/azure-local.md` -- Azure Local (formerly Azure Stack HCI) for hybrid cloud
- `providers/azure/certifications.md` -- Azure certification and compliance requirements
