# Active Directory

## Scope

Active Directory Domain Services (AD DS) architecture: domain and forest design, site topology and replication, FSMO role placement, Group Policy design and management, AD replication troubleshooting, migration and consolidation using ADMT, trust relationships (forest, external, shortcut), AD hardening with tiered administration (Tier 0/1/2), Privileged Access Workstations (PAW), Local Administrator Password Solution (LAPS), hybrid identity with Entra Connect (formerly Azure AD Connect), AD backup and recovery (authoritative/non-authoritative restore), and Domain Controller sizing and placement.

## Checklist

- [ ] [Critical] Is the domain and forest functional level set to the minimum of Windows Server 2016 to enable modern security features (Privileged Access Management, Credential Guard support), and is there a plan to raise it as legacy DCs are decommissioned?
- [ ] [Critical] Are FSMO roles (Schema Master, Domain Naming Master, PDC Emulator, RID Master, Infrastructure Master) placed on reliable, well-connected DCs with documented role holders and a seizure/transfer procedure?
- [ ] [Critical] Is a tiered administration model implemented (Tier 0 for identity/AD, Tier 1 for servers/applications, Tier 2 for workstations) with separate admin accounts per tier and no credential exposure across tiers?
- [ ] [Critical] Is AD backup performed using a system state or bare-metal backup tool that supports authoritative restore, with at least two DCs backed up and tested recovery procedures documented?
- [ ] [Critical] Are Domain Controllers placed in each AD site that has user populations or applications requiring local authentication, with site links and replication schedules configured to match network topology and bandwidth?
- [ ] [Recommended] Is LAPS (Local Administrator Password Solution) or Windows LAPS deployed to manage unique local administrator passwords on all domain-joined servers and workstations, with password retrieval restricted to authorized administrators?
- [ ] [Recommended] Is Group Policy designed with a clear OU structure, minimal GPO linking at the domain level, and WMI filters or security filtering used only when necessary to reduce logon processing time?
- [ ] [Recommended] Is Entra Connect (formerly Azure AD Connect) deployed for hybrid identity synchronization, with password hash sync or pass-through authentication configured, and is the staging server maintained for failover?
- [ ] [Recommended] Are trust relationships documented with clear justification, and are selective authentication and SID filtering enabled on all forest trusts to limit lateral movement?
- [ ] [Recommended] Is AD replication monitored using repadmin or equivalent tooling, with alerts configured for replication failures exceeding the tombstone lifetime (default 180 days)?
- [ ] [Recommended] Are Privileged Access Workstations (PAWs) or at minimum jump servers deployed for all Tier 0 administration, with no internet access and hardware-based MFA enforced?
- [ ] [Optional] Is AD migration or consolidation planned using ADMT (Active Directory Migration Tool) with SID history preservation, or is a greenfield approach with staged cutover preferred?
- [ ] [Optional] Is Microsoft Defender for Identity (formerly Azure ATP) deployed on Domain Controllers to detect pass-the-hash, pass-the-ticket, golden ticket, and reconnaissance attacks?
- [ ] [Optional] Is Microsoft Entra Copilot evaluated for identity governance — provides AI-assisted access reviews, identity risk investigation, and governance recommendations through natural language queries in the Entra admin center?

## Why This Matters

Active Directory is the identity backbone for most enterprise environments. A compromised AD means total environment compromise -- attackers who gain Domain Admin or equivalent privileges can access every system, exfiltrate any data, and deploy ransomware across the entire organization. The tiered administration model exists specifically to prevent credential theft escalation: a compromised workstation admin account should never lead to Domain Controller access.

Domain and forest design decisions made during initial deployment are extremely difficult to change later. Adding a new domain or restructuring forests requires migration tooling, application reconfiguration, and extended coexistence periods. FSMO role placement, site topology, and replication design directly affect authentication performance and resilience. DC placement in remote sites versus reliance on WAN links determines whether users can log in during network outages.

## Common Decisions (ADR Triggers)

- **Forest/domain design** -- Single forest/single domain (simplest) vs multi-domain (isolation boundaries) vs multi-forest (strongest isolation for mergers/acquisitions)
- **Hybrid identity** -- Password hash sync (resilient, enables leaked credential detection) vs pass-through authentication (passwords never leave on-premises) vs federation with AD FS (maximum control, highest complexity)
- **Admin tier model** -- Full Tier 0/1/2 with PAWs (maximum security) vs simplified jump-server model vs cloud-only privileged identity management (Entra PIM)
- **DC placement** -- DC in every site (local auth, resilient) vs hub-and-spoke with RODC at branches (reduced attack surface) vs centralized DCs with reliable WAN
- **Group Policy strategy** -- Role-based OU structure with inheritance vs flat OU with security-filtered GPOs vs Intune/MDM for modern management
- **Trust architecture** -- Forest trust (broad access) vs external domain trust (limited scope) vs no trust with selective resource sharing
- **Migration approach** -- ADMT with SID history (preserves access) vs greenfield rebuild (clean start) vs staged consolidation

## AI and GenAI Capabilities

**Microsoft Entra Copilot** — AI assistant for identity and access management within the Entra admin center. Capabilities: natural language identity queries ("which users have privileged access to production resources?"), AI-assisted access reviews (recommendations for access certification), identity risk investigation (summarize risk events and suggest remediation), and governance policy recommendations. Part of the broader Microsoft Security Copilot ecosystem. Requires appropriate Entra licensing (P2 for full governance features).

## See Also

- `providers/microsoft/windows-server.md` -- Windows Server platform and editions
- `providers/azure/identity.md` -- Entra ID (Azure AD) cloud identity services
- `general/identity.md` -- cross-platform identity and access management patterns
- `general/tier0-security-enclaves.md` -- Tier 0 security enclave design and hardening

## Reference Links

- [Active Directory Domain Services Overview](https://learn.microsoft.com/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview) -- AD DS architecture, domain/forest design, and FSMO roles
- [Securing Active Directory](https://learn.microsoft.com/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory) -- tiered administration, privileged access, and AD hardening best practices
- [Entra Connect (Azure AD Connect)](https://learn.microsoft.com/entra/identity/hybrid/connect/whatis-azure-ad-connect) -- hybrid identity synchronization with Entra ID
