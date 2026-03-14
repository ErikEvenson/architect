# Identity and Access Management

## Checklist

- [ ] What identity federation protocol is used? (SAML 2.0 for enterprise SSO, OIDC for modern apps, OAuth 2.0 for API authorization — often OIDC + OAuth 2.0 together)
- [ ] Is single sign-on (SSO) implemented? (centralized IdP like Okta, Azure AD/Entra ID, Google Workspace, PingIdentity — SAML or OIDC integration)
- [ ] How is user provisioning and deprovisioning automated? (SCIM 2.0 for cross-domain identity management, JIT provisioning, HR-system-driven lifecycle)
- [ ] What MFA methods are supported? (TOTP apps, WebAuthn/FIDO2 hardware keys for phishing resistance, push notifications, SMS as fallback only)
- [ ] How are service accounts and machine identities managed? (workload identity federation, SPIFFE/SPIRE, cloud IAM roles, short-lived credentials vs static keys)
- [ ] Is a zero trust identity model adopted? (continuous verification, device posture checks, context-aware access, BeyondCorp approach)
- [ ] What directory service is the identity source of truth? (Azure AD/Entra ID, on-prem Active Directory with sync, LDAP, cloud-native directory)
- [ ] Are conditional access policies configured? (device compliance, location, risk level, application sensitivity — block or require step-up auth)
- [ ] How is privileged access managed? (PAM tools like CyberArk or HashiCorp Vault, just-in-time access, break-glass procedures, session recording)
- [ ] Is identity governance implemented? (access reviews, certification campaigns, role mining, segregation of duties, orphaned account detection)
- [ ] How do APIs authenticate callers? (API keys for simple cases, JWT bearer tokens for services, mTLS for service-to-service, OAuth 2.0 client credentials flow)
- [ ] What is the token lifecycle? (access token expiry — 15-60 min recommended, refresh token rotation, token revocation capability)
- [ ] How are authorization decisions made? (RBAC, ABAC, ReBAC, OPA/Cedar policy engine, application-level permissions)

## Why This Matters

Identity is the new perimeter. With cloud infrastructure, remote work, and API-driven architectures, network-based security is insufficient. A compromised identity with excessive privileges is the root cause of most cloud breaches. Weak MFA (SMS-only) leaves organizations vulnerable to phishing and SIM-swapping. Unmanaged service accounts with static credentials are a top finding in every cloud security audit. Without automated provisioning/deprovisioning, terminated employees retain access for days or weeks. Privileged access without just-in-time controls and session monitoring creates unacceptable blast radius. Zero trust is not a product to buy — it is an architecture that requires identity as the foundational control plane.

## Common Decisions (ADR Triggers)

- **IdP selection** — Okta vs Azure AD/Entra ID vs Google Workspace vs PingIdentity, cost model, protocol support, directory integration
- **Federation protocol** — SAML 2.0 for legacy enterprise apps vs OIDC for modern apps, when to support both
- **MFA policy** — which methods to allow, phishing-resistant MFA (WebAuthn) mandate, MFA fatigue attack mitigation
- **Service identity model** — cloud IAM roles vs SPIFFE/SPIRE, workload identity federation, secret-zero problem
- **Zero trust implementation** — BeyondCorp model, device trust integration, continuous authentication triggers
- **Authorization architecture** — RBAC vs ABAC vs ReBAC, centralized policy engine (OPA, Cedar) vs application-embedded
- **Privileged access approach** — PAM tool selection, JIT access workflow, approval process, session recording requirements
- **Token strategy** — access token lifetime, refresh token rotation policy, token binding, cross-domain token exchange
- **Directory architecture** — cloud-only vs hybrid with on-prem AD sync, multi-directory federation, group nesting strategy
