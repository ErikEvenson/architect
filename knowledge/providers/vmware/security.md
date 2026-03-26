# VMware Security

## Scope

This document covers VMware vSphere and NSX security controls including microsegmentation, host hardening, encryption, key management, RBAC, audit logging, endpoint protection, and certificate management.

## Checklist

- [ ] **[Critical]** Are NSX distributed firewall (DFW) policies configured with a zero-trust microsegmentation model, using security groups based on VM tags, attributes, or Active Directory groups rather than IP addresses for dynamic policy enforcement?
- [ ] **[Critical]** Is the NSX DFW rule base organized into categories (Ethernet, Emergency, Infrastructure, Environment, Application) with rules processed in order, and are default rules set to deny (not allow) for the Application category?
- [ ] **[Recommended]** Is identity-based firewalling (IDFW) configured in NSX for environments requiring user-identity-aware policies, with Active Directory integration via the Guest Introspection framework on Windows VMs?
- [ ] **[Critical]** Are ESXi hosts hardened according to the VMware vSphere Security Configuration Guide (formerly Hardening Guide) and DISA STIG baselines, including disabling SSH (or restricting to key-based auth), enabling lockdown mode, and configuring host firewall rules?
- [ ] **[Recommended]** Is VM encryption enabled via vSphere Native Key Provider (for simplified deployments) or external KMIP-compliant KMS (Entrust, Thales CipherTrust) for workloads requiring data-at-rest encryption, with key backup and rotation procedures documented?
- [ ] **[Recommended]** Is vTPM (virtual Trusted Platform Module) enabled for VMs running Windows 11, Windows Server 2022+, or Linux workloads requiring measured boot, with the VM encryption prerequisite satisfied?
- [ ] **[Optional]** Is vSphere Trust Authority deployed in high-security environments to attest ESXi host integrity before releasing encryption keys, preventing compromised hosts from accessing encrypted VMs?
- [ ] **[Critical]** Is role-based access control (RBAC) configured in vCenter with least-privilege roles, integrated with Active Directory or LDAP via vCenter SSO, and are predefined roles (Administrator, VM Power User, Read-Only) customized rather than granting global admin?
- [ ] **[Critical]** Is audit logging enabled with vCenter events forwarded to a SIEM (Splunk, QRadar, Sentinel) via syslog, and are ESXi host logs forwarded to a persistent log server (VCF Operations for Logs, formerly Aria Operations for Logs, or third-party) since local logs are lost on stateless or auto-deploy hosts?
- [ ] **[Recommended]** Is an endpoint detection and response (EDR) solution deployed for runtime protection of VMs, providing process monitoring, vulnerability assessment, and behavioral analysis? (Note: Broadcom cancelled the planned sale of VMware Carbon Black in 2024 and merged it with Symantec into a new Enterprise Security Group business unit within Broadcom. Carbon Black is no longer part of the VMware/VCF ecosystem. Evaluate CrowdStrike, SentinelOne, Microsoft Defender for Endpoint, or Broadcom's Enterprise Security Group offerings for VMware workload protection.)
- [ ] **[Recommended]** Is NSX Security Intelligence (formerly NSX Intelligence) enabled for traffic flow visualization and automated security policy recommendations, providing east-west traffic analysis to identify microsegmentation gaps and shadow IT communication patterns?
- [ ] **[Recommended]** Are TLS certificates for vCenter, ESXi, NSX Manager, and other VMware components replaced with enterprise CA-signed certificates using the VMware Certificate Authority (VMCA) in subordinate mode or full custom certificate mode?
- [ ] **[Critical]** Is vSphere Lifecycle Manager (vLCM) configured to enforce host compliance with a desired image including security patches, drivers, and firmware, with remediation scheduled within the organization's patch SLA?

## Why This Matters

VMware environments are high-value targets because compromising vCenter or ESXi grants access to every workload in the datacenter. The 2022-2023 ESXiArgs ransomware campaigns demonstrated that unpatched ESXi hosts exposed to the internet are actively exploited. NSX distributed firewall operates at the vNIC level (in the hypervisor kernel), meaning traffic between VMs on the same host is inspected without hairpinning through a physical firewall -- but only when policies are properly configured. Default-allow DFW rules provide visibility without protection. vCenter SSO misconfiguration (overly broad admin access, default passwords on the administrator@vsphere.local account) is a frequent audit finding and attack vector. VM encryption protects data at rest on disk and during vMotion, but encrypted VMs have operational constraints (no FT, limited snapshot behavior) that must be understood before deployment. Certificate management across VMware components is operationally complex, and expired certificates cause cascading service failures.

## Common Decisions (ADR Triggers)

- **NSX DFW vs physical firewalls** -- DFW for east-west microsegmentation at the hypervisor level (per-VM granularity, no network redesign) vs physical/virtual appliance firewalls (Palo Alto, Fortinet) for north-south and for environments requiring specific firewall vendor features or certifications
- **Default-deny vs default-allow DFW** -- default-deny for zero-trust (requires complete application flow mapping before enforcement) vs default-allow with logging (for discovery phase, gradually tightening); most production environments start with allow-and-log, then transition to deny
- **vSphere Native Key Provider vs external KMS** -- native KP for simplified single-cluster encryption without external dependencies vs external KMIP KMS (Entrust, Thales CipherTrust) for enterprise key management, multi-cluster consistency, key escrow, and compliance requirements (PCI, HIPAA). Note: HyTrust was acquired by Entrust; Vormetric is now Thales CipherTrust Manager.
- **vTPM vs no vTPM** -- required for Windows 11/Server 2025 and Credential Guard; adds VM encryption dependency and prevents some VM operations; evaluate if the security benefit justifies the operational overhead
- **VMCA subordinate mode vs custom certificates** -- VMCA subordinate (VMCA signs leaf certificates under enterprise CA) for simplified management vs full custom certificates for environments where the security team requires direct CA control over all leaf certificates
- **EDR platform selection** -- CrowdStrike, SentinelOne, or Microsoft Defender for Endpoint for VM workload protection; Broadcom cancelled the planned Carbon Black sale in 2024 and merged it with Symantec into the Enterprise Security Group. Carbon Black is no longer part of the VMware/VCF ecosystem. Evaluate EDR solutions independently of the VMware stack, including Broadcom's Enterprise Security Group offerings.
- **NSX Security Intelligence vs third-party flow analysis** -- NSX Security Intelligence (formerly NSX Intelligence) for native VMware integration and automated policy recommendations vs third-party (Guardicore/Akamai, Illumio) for multi-hypervisor or multi-cloud microsegmentation

## Reference Links

- [vSphere Security Configuration Guide](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere-security-configuration-guide/8-0/about-this-guide.html) -- ESXi and vCenter hardening baselines (formerly Hardening Guide)
- [vSphere security guide](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-security/GUID-52188148-C579-4F6A-8335-CFBCE0DD2167.html) -- encryption, key management, RBAC, certificate management, and audit logging
- [NSX security documentation](https://docs.vmware.com/en/VMware-NSX/4.2/administration/GUID-31A2D4B8-42A0-4D0F-8B85-1E3C42DD93E6.html) -- distributed firewall, microsegmentation, and IDS/IPS configuration

## See Also

- `general/security.md` -- general security architecture patterns
- `providers/vmware/nsx-dfw-design.md` -- NSX DFW microsegmentation design
- `providers/vmware/networking.md` -- NSX networking and firewall architecture
- `providers/vmware/infrastructure.md` -- vSphere host hardening and configuration
