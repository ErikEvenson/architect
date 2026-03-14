# Azure Identity

## Checklist

- [ ] Is Microsoft Entra ID (formerly Azure AD) configured as the sole identity provider with legacy Azure AD endpoints migrated to the Entra ID branding?
- [ ] Are managed identities (system-assigned or user-assigned) used for all Azure resource-to-resource authentication, eliminating stored credentials and connection strings?
- [ ] Are conditional access policies enforced requiring MFA, compliant devices, and trusted locations for all privileged and sensitive application access?
- [ ] Is Privileged Identity Management (PIM) enabled for just-in-time (JIT) activation of Azure AD roles and Azure resource roles with approval workflows and time-bound access?
- [ ] Are app registrations and service principals configured with certificate or federated credentials (not client secrets), and are unused registrations identified and cleaned up?
- [ ] Is Azure AD B2C (or Azure AD External Identities) deployed for customer-facing identity with custom user flows, branded sign-in pages, and social identity provider federation?
- [ ] Are RBAC assignments following least-privilege with custom role definitions scoped to specific actions rather than broad built-in roles where needed?
- [ ] Are Azure AD security groups and dynamic membership rules used to automate role assignments and conditional access targeting based on user attributes?
- [ ] Is MFA enforced for all users via security defaults (small orgs) or conditional access policies (enterprise), with phishing-resistant methods (FIDO2, Windows Hello, certificate-based) preferred over SMS?
- [ ] Is identity governance configured with access reviews on a quarterly cadence for privileged roles, group memberships, and application assignments?
- [ ] Are emergency access (break-glass) accounts created, excluded from conditional access, monitored with alerts, and tested periodically?
- [ ] Is cross-tenant access configured with Entra ID cross-tenant access settings for B2B collaboration, restricting which external organizations can be trusted?
- [ ] Are sign-in and audit logs streaming to Log Analytics with Microsoft Sentinel analytics rules for impossible-travel, suspicious MFA, and credential-stuffing detection?

## Why This Matters

Microsoft Entra ID is the identity control plane for all Azure resources, Microsoft 365, and thousands of SaaS applications. Unlike AWS IAM (which is per-account), Entra ID operates at the tenant level and governs access across all subscriptions. Managed identities eliminate the most common source of credential leaks in Azure -- connection strings and client secrets stored in app configuration. Conditional access policies are the primary enforcement mechanism for Zero Trust, and PIM is essential for preventing standing admin access. Azure RBAC is separate from Entra ID roles; both must be governed together.

## Common Decisions (ADR Triggers)

- **System-assigned vs user-assigned managed identity** -- lifecycle tied to resource vs shared across multiple resources with independent lifecycle management
- **Entra ID P1 vs P2 licensing** -- P1 provides conditional access and self-service password reset; P2 adds PIM, identity governance, and risk-based conditional access
- **Security defaults vs conditional access** -- simple MFA enforcement for small organizations vs granular policy-based access control for enterprise
- **App registration credential type** -- certificates (more secure, auto-rotatable) vs federated credentials (workload identity federation for GitHub Actions, Kubernetes) vs client secrets (least secure, avoid)
- **Azure AD B2C vs External Identities** -- separate tenant for consumer-scale CIAM with custom policies vs simpler B2B guest access within the main tenant
- **Custom RBAC roles vs built-in** -- operational overhead of maintaining custom role definitions vs overly broad built-in roles; scoping at management group, subscription, or resource group level
- **Identity provider federation** -- Entra ID as primary IdP vs federating with on-premises AD FS vs third-party IdP (Okta, Ping) with Entra ID as the broker

## Reference Architectures

- [Azure Architecture Center: Identity architecture design](https://learn.microsoft.com/en-us/azure/architecture/identity/identity-start-here) -- decision tree for identity integration patterns including hybrid, cloud-only, and B2C
- [Microsoft Entra ID deployment guide](https://learn.microsoft.com/en-us/entra/fundamentals/concept-secure-remote-workers) -- phased deployment of conditional access, MFA, and identity protection
- [Azure Landing Zone: Identity and access management](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/identity-access) -- Cloud Adoption Framework guidance for enterprise identity design
- [Azure Well-Architected Framework: Identity and access management](https://learn.microsoft.com/en-us/azure/well-architected/security/identity-access) -- security pillar guidance for authentication, authorization, and identity governance
- [Zero Trust identity and access management](https://learn.microsoft.com/en-us/security/zero-trust/deploy/identity) -- Microsoft Zero Trust deployment guide for identity verification, least-privilege access, and breach assumption
