# VMware Security

## Checklist

- [ ] Are NSX distributed firewall (DFW) policies configured with a zero-trust microsegmentation model, using security groups based on VM tags, attributes, or Active Directory groups rather than IP addresses for dynamic policy enforcement?
- [ ] Is the NSX DFW rule base organized into categories (Ethernet, Emergency, Infrastructure, Environment, Application) with rules processed in order, and are default rules set to deny (not allow) for the Application category?
- [ ] Is identity-based firewalling (IDFW) configured in NSX for environments requiring user-identity-aware policies, with Active Directory integration via the Guest Introspection framework on Windows VMs?
- [ ] Are ESXi hosts hardened according to the VMware vSphere Security Configuration Guide (formerly Hardening Guide) and DISA STIG baselines, including disabling SSH (or restricting to key-based auth), enabling lockdown mode, and configuring host firewall rules?
- [ ] Is VM encryption enabled via vSphere Native Key Provider (for simplified deployments) or external KMIP-compliant KMS (HyTrust, Thales, Vormetric) for workloads requiring data-at-rest encryption, with key backup and rotation procedures documented?
- [ ] Is vTPM (virtual Trusted Platform Module) enabled for VMs running Windows 11, Windows Server 2022+, or Linux workloads requiring measured boot, with the VM encryption prerequisite satisfied?
- [ ] Is vSphere Trust Authority deployed in high-security environments to attest ESXi host integrity before releasing encryption keys, preventing compromised hosts from accessing encrypted VMs?
- [ ] Is role-based access control (RBAC) configured in vCenter with least-privilege roles, integrated with Active Directory or LDAP via vCenter SSO, and are predefined roles (Administrator, VM Power User, Read-Only) customized rather than granting global admin?
- [ ] Is audit logging enabled with vCenter events forwarded to a SIEM (Splunk, QRadar, Sentinel) via syslog, and are ESXi host logs forwarded to a persistent log server (Aria Operations for Logs or third-party) since local logs are lost on stateless or auto-deploy hosts?
- [ ] Is VMware Carbon Black Workload Protection (or equivalent EDR) deployed for runtime protection of VMs, providing process monitoring, vulnerability assessment, and behavioral analysis without requiring in-guest agents on every VM?
- [ ] Is NSX Intelligence enabled for traffic flow visualization and automated security policy recommendations, providing east-west traffic analysis to identify microsegmentation gaps and shadow IT communication patterns?
- [ ] Are TLS certificates for vCenter, ESXi, NSX Manager, and other VMware components replaced with enterprise CA-signed certificates using the VMware Certificate Authority (VMCA) in subordinate mode or full custom certificate mode?
- [ ] Is vSphere Lifecycle Manager (vLCM) configured to enforce host compliance with a desired image including security patches, drivers, and firmware, with remediation scheduled within the organization's patch SLA?

## Why This Matters

VMware environments are high-value targets because compromising vCenter or ESXi grants access to every workload in the datacenter. The 2022-2023 ESXiArgs ransomware campaigns demonstrated that unpatched ESXi hosts exposed to the internet are actively exploited. NSX distributed firewall operates at the vNIC level (in the hypervisor kernel), meaning traffic between VMs on the same host is inspected without hairpinning through a physical firewall -- but only when policies are properly configured. Default-allow DFW rules provide visibility without protection. vCenter SSO misconfiguration (overly broad admin access, default passwords on the administrator@vsphere.local account) is a frequent audit finding and attack vector. VM encryption protects data at rest on disk and during vMotion, but encrypted VMs have operational constraints (no FT, limited snapshot behavior) that must be understood before deployment. Certificate management across VMware components is operationally complex, and expired certificates cause cascading service failures.

## Common Decisions (ADR Triggers)

- **NSX DFW vs physical firewalls** -- DFW for east-west microsegmentation at the hypervisor level (per-VM granularity, no network redesign) vs physical/virtual appliance firewalls (Palo Alto, Fortinet) for north-south and for environments requiring specific firewall vendor features or certifications
- **Default-deny vs default-allow DFW** -- default-deny for zero-trust (requires complete application flow mapping before enforcement) vs default-allow with logging (for discovery phase, gradually tightening); most production environments start with allow-and-log, then transition to deny
- **vSphere Native Key Provider vs external KMS** -- native KP for simplified single-cluster encryption without external dependencies vs external KMIP KMS for enterprise key management, multi-cluster consistency, key escrow, and compliance requirements (PCI, HIPAA)
- **vTPM vs no vTPM** -- required for Windows 11/Server 2025 and Credential Guard; adds VM encryption dependency and prevents some VM operations; evaluate if the security benefit justifies the operational overhead
- **VMCA subordinate mode vs custom certificates** -- VMCA subordinate (VMCA signs leaf certificates under enterprise CA) for simplified management vs full custom certificates for environments where the security team requires direct CA control over all leaf certificates
- **Carbon Black vs third-party EDR** -- Carbon Black Workload for tight vSphere integration and agentless options vs CrowdStrike/SentinelOne for organizations standardized on a different EDR platform across physical and virtual
- **NSX Intelligence vs third-party flow analysis** -- NSX Intelligence for native VMware integration and automated policy recommendations vs third-party (Guardicore, Illumio) for multi-hypervisor or multi-cloud microsegmentation
