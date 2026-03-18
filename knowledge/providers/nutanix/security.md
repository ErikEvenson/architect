# Nutanix Security

## Scope

Security controls for Nutanix infrastructure: identity and access management (RBAC, AD/SAML, MFA), network security (Flow microsegmentation), data-at-rest encryption (software and SED with external KMS), infrastructure hardening (STIG, cluster lockdown, TLS), workload security, and audit/compliance.

## Checklist

- [ ] [Critical] Is Prism Central RBAC configured with least-privilege roles -- Cluster Admin, Prism Central Admin, and custom roles scoped to specific clusters, projects, or categories rather than granting Super Admin broadly?
- [ ] [Critical] Is Active Directory or SAML 2.0 integration configured for Prism Central and Prism Element authentication, eliminating local admin accounts for day-to-day operations?
- [ ] [Critical] Are Flow microsegmentation policies enforcing zero-trust network security between application tiers, using categories (AppType, AppTier, Environment) to define allowed traffic flows?
- [ ] [Critical] Is data-at-rest encryption enabled -- software-based encryption (AOS native, managed via Prism) for standard deployments, or Self-Encrypting Drives (SEDs) with external KMS (SafeNet, Thales CipherTrust, KMIP-compliant) for FIPS 140-2 requirements?
- [ ] [Critical] Is the external Key Management Server (KMS) deployed in HA configuration for SED encryption, since KMS unavailability prevents node reboots from unlocking drives?
- [ ] [Recommended] Is STIG (Security Technical Implementation Guide) hardening applied to AHV hosts and CVMs using the Nutanix-published STIG guide, with automated compliance checking via Prism Central Security Dashboard?
- [ ] [Recommended] Is audit logging enabled with syslog forwarding from Prism Central and Prism Element to a centralized SIEM (Splunk, QRadar, ArcSight) for security event correlation and compliance reporting?
- [ ] [Recommended] Is Nutanix Security Central (Prism Pro feature) enabled to continuously assess the security posture of the cluster, identifying configuration drift, unpatched CVEs, and policy violations?
- [ ] [Recommended] Are VM-level antivirus and endpoint protection agents deployed inside guest VMs, since AHV does not support agentless antivirus scanning (unlike VMware's vShield/NSX Guest Introspection)?
- [ ] [Recommended] Is Nutanix Files Analytics enabled on all Nutanix Files deployments to detect anomalous file access patterns, potential ransomware activity (mass file renames/encryptions), and generate audit trails for compliance?
- [ ] [Recommended] Is cluster lockdown mode enabled in production, disabling SSH access to CVMs and AHV hosts and requiring explicit unlock through Prism for troubleshooting?
- [ ] [Recommended] Are SSL/TLS certificates on Prism Element and Prism Central replaced with organization-signed certificates, and is the minimum TLS version set to 1.2 to disable weak cipher suites?
- [ ] [Recommended] Is two-factor authentication (client certificate or TOTP) configured for Prism Central administrative access as a second layer beyond AD/SAML authentication?
- [ ] [Optional] Are Prism Central projects used to enforce multi-tenancy boundaries, limiting user visibility and resource consumption to their assigned project scope?

## Why This Matters

Nutanix security spans multiple layers: infrastructure hardening (STIG, cluster lockdown, TLS), identity and access (RBAC, AD/SAML integration), network security (Flow microsegmentation), data protection (encryption at rest), and workload security (guest-level controls). The most common security gaps are overly broad admin access (everyone using the default admin account), no microsegmentation (flat network with unrestricted east-west traffic), and unencrypted data at rest. Flow microsegmentation is particularly valuable because it operates at the hypervisor level, making it impossible for a compromised VM to bypass network policies -- unlike guest-based firewalls. However, Flow only controls network traffic; it does not inspect payloads, so deep packet inspection still requires a virtual firewall appliance via network function chaining. Data-at-rest encryption with an external KMS adds operational complexity but is required for many compliance frameworks (HIPAA, PCI-DSS, FedRAMP). Cluster lockdown mode prevents direct SSH access to CVMs and hosts, which is essential for audit compliance but requires planning for break-glass troubleshooting scenarios.

## Common Decisions (ADR Triggers)

- **Encryption method** -- AOS software encryption (no special hardware, simpler) vs Self-Encrypting Drives with external KMS (FIPS 140-2 compliant, higher operational complexity)
- **Key management** -- Nutanix native KMS (simple, single-cluster) vs external KMIP server (SafeNet, Thales CipherTrust, Entrust (formerly HyTrust) -- enterprise-grade, HA, multi-cluster key management)
- **Network security model** -- Flow microsegmentation only (built-in, no cost) vs Flow + virtual firewall appliance (deep packet inspection, IDS/IPS) vs external physical firewall only
- **Identity provider** -- Active Directory (Kerberos/LDAP, most common) vs SAML 2.0 (Okta, Entra ID, Ping -- modern SSO) vs local accounts (only for break-glass)
- **Hardening standard** -- Nutanix STIG (CIS-aligned, vendor-supported) vs custom CIS benchmark vs DoD STIG (strictest, may break features), automation of compliance scanning
- **Guest security** -- Traditional AV agents per VM vs lightweight EDR (CrowdStrike, Carbon Black) vs no in-guest security (relying on network-level controls only)
- **Cluster access model** -- Lockdown mode (SSH disabled, Prism-only management) vs restricted SSH (key-based, bastion host) vs open SSH (least secure, development only)

## See Also

- `general/security.md` -- general security architecture patterns
- `providers/nutanix/networking.md` -- Flow microsegmentation configuration
- `providers/nutanix/infrastructure.md` -- cluster hardening and lockdown
- `general/stig-hardening.md` -- STIG hardening guidance
