# CyberArk Privileged Access Manager

## Scope

CyberArk Privileged Access Manager (PAM) architecture: Digital Vault server design and hardening (vault high availability, disaster recovery vault), Central Policy Manager (CPM) for automated credential rotation, Privileged Session Manager (PSM) for session isolation and recording, Privileged Session Manager for SSH (PSMP), Privileged Threat Analytics (PTA) for behavioral analytics, CyberArk Conjur for DevOps secrets management, CyberArk Cloud (Privilege Cloud SaaS), CyberArk Identity for workforce identity and SSO, Application Access Manager (AAM) / Secrets Manager for application-to-application credential retrieval, privilege escalation controls, vault infrastructure sizing, safe and platform design, and integration with SIEM, ITSM, and identity governance platforms.

## Checklist

- [ ] [Critical] Is the Digital Vault server deployed on a hardened, standalone server (no domain join, no additional roles, CyberArk-provided OS hardening script applied) with the Vault firewall restricting inbound connections to only the PVWA, CPM, PSM, and DR Vault on port 1858?
- [ ] [Critical] Is a Disaster Recovery (DR) Vault configured in a separate site with real-time replication from the primary Vault, and are failover/failback procedures documented and tested at least annually, including verification that the DR Vault can promote to primary within the defined RTO?
- [ ] [Critical] Are the Vault Master Key and recovery keys stored in a physical safe (not digitally) with split-knowledge procedures requiring multiple custodians, and is the Master Key CD/USB stored separately from the Vault server infrastructure?
- [ ] [Critical] Is the Central Policy Manager (CPM) configured to rotate credentials for all managed accounts on a defined schedule (30 days maximum for service accounts, 90 days for less sensitive), with reconciliation accounts defined for every platform to recover from out-of-sync passwords?
- [ ] [Critical] Are all privileged sessions routed through PSM (RDP) or PSMP (SSH) with full session recording enabled, stored in the Vault with tamper-proof integrity, and retained for the period required by compliance (typically 1-7 years)?
- [ ] [Critical] Is safe architecture designed with clear naming conventions, ownership assignment, and access control (safe members) following least privilege, with separate safes for different account types (Windows domain admins, Unix root, database, application, cloud IAM)?
- [ ] [Critical] Are break-glass (emergency access) procedures documented and tested, including dual-control or exclusive access workflows for the most privileged accounts (domain admins, root), with all break-glass usage generating immediate alerts?
- [ ] [Recommended] Is CyberArk Privileged Threat Analytics (PTA) deployed to detect credential theft, unauthorized privileged access, and anomalous behavior patterns (unusual logon times, access from new sources, privilege escalation attempts)?
- [ ] [Recommended] Are application credentials (database connection strings, API keys, service account passwords) managed through CyberArk Secrets Manager (formerly AAM/CCP) with Credential Provider (agent) or Central Credential Provider (agentless REST API) retrieval, eliminating hardcoded credentials in application code and configuration files?
- [ ] [Recommended] Is the PVWA (Password Vault Web Access) deployed behind a load balancer with at least two instances, configured with HTTPS, integrated with the organization's SSO/MFA solution, and are PVWA sessions restricted to authorized administrative networks?
- [ ] [Recommended] Are platforms (target system types) configured with accurate connection components, including correct prompts, password change commands, and verification scripts, and are custom platforms tested in a lab environment before production deployment?
- [ ] [Recommended] Is CyberArk integrated with ITSM (ServiceNow) for ticketed access requests with approval workflows, ensuring all privileged access is tied to a change ticket or incident, with automatic access revocation after the ticket closes?
- [ ] [Recommended] Are CPM and PSM components deployed in a distributed architecture for large environments, with dedicated CPM instances per platform type or site to manage credential rotation load and avoid rotation queue backlogs?
- [ ] [Recommended] Is the CyberArk Vault database sized appropriately for the expected number of managed accounts and session recordings, with storage growth projections for 3-5 years, and are session recording archives offloaded to secondary storage to manage primary Vault disk usage?
- [ ] [Optional] Is CyberArk Conjur evaluated for managing secrets in DevOps pipelines (Kubernetes, Ansible, Terraform, Jenkins), providing dynamic secrets injection without exposing credentials in CI/CD configuration, environment variables, or container images?
- [ ] [Optional] Is CyberArk Privilege Cloud (SaaS) evaluated as an alternative to self-hosted Vault for organizations seeking reduced infrastructure management, with hybrid connectivity to on-premises systems via Privilege Cloud connectors?
- [ ] [Optional] Is CyberArk Identity (formerly Idaptive) deployed for workforce SSO and adaptive MFA, providing a unified platform for both privileged and standard user identity management under a single CyberArk tenant?
- [ ] [Optional] Are just-in-time (JIT) privileged access policies configured to grant temporary group membership (e.g., Domain Admins) for a defined duration rather than persistent privileged group membership, with automatic removal after the access window expires?

## Why This Matters

Privileged accounts are the primary target for advanced attackers and the vector through which ransomware propagates across environments. A single compromised Domain Admin or root account can give an attacker complete control of the infrastructure. CyberArk PAM exists to eliminate persistent privileged credentials, isolate privileged sessions, and create an auditable record of all privileged activity.

The Digital Vault is architecturally unique -- it is a proprietary, hardened data store designed to be the most protected system in the environment. This means it has specific infrastructure requirements that deviate from standard enterprise patterns: no domain membership, proprietary firewall, dedicated hardware or VM, and restricted network access. Organizations that treat the Vault like a standard application server will encounter security and operational issues.

Session recording through PSM provides both security value (forensic investigation after an incident) and compliance value (proof that privileged actions were authorized and appropriate). Without session isolation, privileged users authenticate directly to target systems, leaving credentials exposed to keyloggers, pass-the-hash attacks, and credential harvesting malware. PSM eliminates this by proxying the session -- the user never sees or handles the actual credential.

Credential rotation failures are the most common operational issue in CyberArk deployments. When CPM cannot rotate a password (network issue, permission problem, custom platform bug), the stored credential becomes out of sync with the target system, causing lockouts. Reconciliation accounts and monitoring for failed rotations are essential operational controls.

## Common Decisions (ADR Triggers)

- **Deployment model** -- Self-hosted Digital Vault (maximum control, infrastructure responsibility) vs CyberArk Privilege Cloud SaaS (reduced operations, cloud connectivity required) vs hybrid (Vault on-prem, PSM/CPM with cloud management)
- **Session management** -- PSM with HTML5 gateway (browser-based, no client install) vs PSM with RDP/SSH client (native experience) vs transparent connection via PSM for SSH proxy
- **Credential retrieval for applications** -- Credential Provider agent on application server (cached, resilient) vs Central Credential Provider REST API (agentless, network-dependent) vs Conjur for containerized and DevOps workloads
- **Safe architecture** -- By technology platform (Windows safe, Unix safe, database safe) vs by business unit/application (App1 safe, App2 safe) vs by environment (production safe, non-production safe) vs combination
- **Vault HA strategy** -- Primary + DR Vault with manual failover (simplest, most common) vs clustered Vault with automatic failover (requires CyberArk Cluster Vault Manager license) vs Privilege Cloud (vendor-managed HA)
- **Discovery and onboarding** -- Manual account onboarding (controlled, slower) vs CyberArk Discovery & Audit (DNA) for bulk discovery vs accounts feed from Active Directory or CMDB with automatic onboarding
- **Secrets management for DevOps** -- CyberArk Conjur (enterprise, CyberArk-native) vs HashiCorp Vault (open-source option, broader ecosystem) vs cloud-native secrets (AWS Secrets Manager, Azure Key Vault) with CyberArk as the master
- **Integration depth** -- PAM-only deployment (vaulting and session management) vs PAM + Endpoint Privilege Manager (least privilege on workstations) vs PAM + CyberArk Identity (unified privileged and workforce identity)

## See Also

- `general/identity.md` -- cross-platform identity and access management patterns
- `general/tier0-security-enclaves.md` -- Tier 0 security enclave design and hardening
- `providers/hashicorp/vault.md` -- HashiCorp Vault for secrets management (alternative/complementary)
- `providers/microsoft/active-directory.md` -- AD privileged account management and tiered administration
- `patterns/zero-trust.md` -- zero trust architecture patterns
- `providers/servicenow/itsm.md` -- ITSM integration for privileged access request workflows

## Reference Links

- [CyberArk PAM Documentation](https://docs.cyberark.com/pam-self-hosted/latest/en/Content/Resources/_TopNav/cc_Home.htm) -- Digital Vault, CPM, PSM, and PVWA administration guides
- [CyberArk Privilege Cloud Documentation](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/Content/Resources/_TopNav/cc_Home.htm) -- SaaS PAM deployment, connector setup, and cloud administration
- [CyberArk Conjur Documentation](https://docs.cyberark.com/conjur-enterprise/latest/en/Content/Resources/_TopNav/cc_Home.htm) -- Conjur secrets management for DevOps, Kubernetes, and CI/CD integration
- [CyberArk Secrets Manager Documentation](https://docs.cyberark.com/credential-providers/latest/en/Content/Resources/_TopNav/cc_Home.htm) -- Credential Provider and Central Credential Provider for application credential retrieval
- [CyberArk Security Hardening Guide](https://docs.cyberark.com/pam-self-hosted/latest/en/Content/PAS%20SysReq/Recommended-Server-Configurations.htm) -- Vault server hardening, network requirements, and infrastructure sizing
- [CyberArk Marketplace](https://cyberark-customers.force.com/mplace/s/#/) -- community-contributed platforms, integrations, and custom connection components
