# Azure Security

## Checklist

- [ ] Is Microsoft Entra ID (Azure AD) configured as the identity provider with Conditional Access policies enforcing MFA, device compliance, and location-based access?
- [ ] Are managed identities (system-assigned or user-assigned) used for Azure resource-to-resource authentication instead of service principal secrets?
- [ ] Is Azure Key Vault deployed for secret, key, and certificate management, with RBAC-based access control (not legacy access policies)?
- [ ] Is Key Vault configured with soft-delete and purge protection enabled to prevent accidental or malicious secret deletion?
- [ ] Is Azure RBAC applied following least-privilege with custom roles where built-in roles are too broad?
- [ ] Is Microsoft Defender for Cloud enabled with at least Defender for Servers, Defender for SQL, and Defender for Key Vault plans?
- [ ] Is Secure Score monitored and used to prioritize security improvements across the environment?
- [ ] Are NSG Flow Logs (version 2) enabled for all NSGs and flowing to Log Analytics with Traffic Analytics for threat detection?
- [ ] Is Azure Policy used to enforce organizational standards (e.g., require encryption, deny public IPs, enforce tagging)?
- [ ] Is Privileged Identity Management (PIM) configured for just-in-time elevation of privileged roles with approval workflows?
- [ ] Are diagnostic settings configured to send Entra ID sign-in and audit logs to Log Analytics and/or a SIEM?
- [ ] Is Azure Private Link used for all PaaS services to eliminate public endpoint exposure?
- [ ] Are management groups and Azure Policy used to enforce guardrails across subscriptions in a landing zone architecture?
- [ ] Is Microsoft Sentinel deployed as the SIEM/SOAR for security event aggregation, detection rules, and automated response playbooks?

## Why This Matters

Azure security is deeply integrated with Microsoft Entra ID, making identity configuration the most critical security control. Managed identities eliminate the credential management problem entirely for Azure-to-Azure communication. Key Vault without purge protection can result in permanent secret loss. Defender for Cloud provides unified threat detection but must be enabled per-plan. Azure Policy is the enforcement mechanism for security guardrails at scale.

## Common Decisions (ADR Triggers)

- **Identity model** -- Entra ID only vs federated with on-premises AD, B2C vs B2B for external identities
- **Key Vault topology** -- per-environment vs per-application vs shared, HSM-backed (Premium) vs software-backed (Standard)
- **Defender for Cloud plans** -- which workload protection plans to enable, cost vs coverage trade-offs
- **SIEM selection** -- Microsoft Sentinel vs Splunk vs third-party, data connector selection
- **PIM vs standing access** -- just-in-time elevation for all privileged roles vs standing access for break-glass accounts
- **Azure Policy scope** -- management group level enforcement vs subscription level, audit vs deny effect
- **Network security model** -- NSGs with ASGs vs Azure Firewall with network rules vs microsegmentation

## Reference Architectures

- [Azure Architecture Center: Security architectures](https://learn.microsoft.com/en-us/azure/architecture/security/) -- curated security reference architectures including identity, network security, and threat protection
- [Azure Landing Zone: Security](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/security) -- Cloud Adoption Framework enterprise security design with management groups, policies, and Defender for Cloud
- [Azure Well-Architected Framework: Security pillar](https://learn.microsoft.com/en-us/azure/well-architected/security/) -- security best practices for identity, data protection, and governance
- [Microsoft Cybersecurity Reference Architectures (MCRA)](https://learn.microsoft.com/en-us/security/adoption/mcra) -- comprehensive reference architecture for Microsoft security services including Entra ID, Defender, and Sentinel
- [Azure Architecture Center: Identity and access management](https://learn.microsoft.com/en-us/azure/architecture/identity/) -- reference architectures for Entra ID, hybrid identity, and conditional access
