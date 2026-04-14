# Okta Identity

## Scope

Okta Workforce Identity Cloud architecture: Universal Directory design and attribute mapping, SSO federation (SAML 2.0, OIDC, WS-Federation), adaptive multi-factor authentication (MFA) policies, lifecycle management with provisioning and deprovisioning workflows, Okta Integration Network (OIN) application catalog, custom integrations via SCIM and API, Okta Identity Governance (OIG) for access certification and entitlement management, Okta Privileged Access, device trust and endpoint management integration, Okta Workflows for identity orchestration, rate limiting and API token management, high availability and disaster recovery, and tenant architecture for multi-org deployments.

## Checklist

- [ ] [Critical] Is Okta Universal Directory configured as the authoritative source for identity attributes, with clear attribute mastering rules defined for each source (HR system, AD, LDAP) to prevent attribute conflicts and ensure a single source of truth per attribute?
- [ ] [Critical] Are SSO integration protocols (SAML 2.0 vs OIDC) selected per application based on application support, with SAML assertions or OIDC claims mapped to include required attributes (groups, roles, entitlements) and signed with SHA-256 or stronger?
- [ ] [Critical] Is adaptive MFA enforced for all users with phishing-resistant factors (Okta Verify with device-bound push, FIDO2/WebAuthn) as the primary authenticator, and are SMS/voice factors disabled or restricted to fallback-only with documented risk acceptance?
- [ ] [Critical] Are lifecycle management policies configured to automatically deprovision (disable or remove) application access within a defined SLA (ideally real-time or within 1 hour) when a user is terminated in the HR source system, and is this tested regularly?
- [ ] [Critical] Are Okta API tokens scoped to least-privilege with defined rotation schedules (90 days maximum), stored in a secrets manager rather than application code, and is token usage monitored via the System Log for anomalous activity?
- [ ] [Critical] Is the Okta org configured with a custom domain (e.g., login.company.com) with TLS certificate management, and is the Okta sign-in page branded to reduce phishing susceptibility?
- [ ] [Recommended] Is Okta Identity Governance (OIG) deployed for access certification campaigns, with quarterly (minimum) access reviews for privileged applications and automated revocation of access that is not re-certified?
- [ ] [Recommended] Are group rules and dynamic group membership configured to automatically assign application access based on user attributes (department, role, location), reducing manual access request burden and ensuring consistent policy enforcement?
- [ ] [Recommended] Is Okta Workflows used to automate complex identity lifecycle events (onboarding checklists, offboarding cleanup, cross-system attribute sync) rather than relying on custom scripts or manual processes?
- [ ] [Recommended] Are rate limits understood and monitored, with application integrations designed to stay within Okta rate limit thresholds (default: 600 requests/min for most endpoints), and are retry-with-backoff patterns implemented in all API consumers?
- [ ] [Recommended] Is the Okta System Log forwarded to a SIEM (Splunk, Sentinel, etc.) via the System Log API or Event Hook, with detection rules configured for suspicious events (MFA bypass, impossible travel, admin role grants, policy changes)?
- [ ] [Recommended] Is device trust configured to restrict application access to managed devices using Okta Verify device signals or integration with endpoint management (Jamf, Intune, CrowdStrike) for zero-trust posture assessment?
- [ ] [Recommended] Are network zones configured to define trusted/untrusted locations, with authentication policies that require step-up MFA or block access from untrusted zones for sensitive applications?
- [ ] [Optional] Is Okta Privileged Access evaluated for managing access to servers and infrastructure, replacing traditional PAM for cloud-native workloads with just-in-time privilege elevation and session recording?
- [ ] [Optional] Is a multi-org strategy evaluated for environments requiring strong isolation (subsidiaries, regulated environments, dev/test separation), with Okta Hub providing centralized management across child orgs?
- [ ] [Optional] Are Okta Event Hooks or Inline Hooks configured for real-time integration with external systems during authentication flows (e.g., risk scoring from a third-party service, custom claim enrichment, registration validation)?

## Why This Matters

Okta serves as the identity perimeter for the organization -- every authentication decision flows through it. A misconfigured Okta tenant can expose all connected applications to unauthorized access, while overly permissive lifecycle policies leave orphaned accounts active long after employees depart. The shift from network-based security to identity-based security (zero trust) means Okta is now the primary enforcement point for access control.

The Okta Integration Network provides pre-built integrations for thousands of applications, but each integration requires correct attribute mapping, group assignment, and provisioning configuration. Getting these wrong leads to users having too much access (privilege creep), too little access (productivity loss), or stale access (compliance violations). Adaptive MFA is the primary defense against credential-based attacks, which account for over 80% of breaches -- weak MFA configuration (SMS-only, no phishing resistance) negates much of Okta's security value.

Rate limiting is a frequently overlooked operational concern. Okta enforces strict rate limits, and applications that poll aggressively or perform bulk operations without throttling will experience authentication failures during peak usage.

## Common Decisions (ADR Triggers)

- **Directory architecture** -- Okta as master directory vs AD/LDAP mastered with Okta as broker vs hybrid mastering with per-attribute source control
- **MFA factor selection** -- Okta Verify push-only (simplest UX) vs FIDO2/WebAuthn (strongest phishing resistance) vs factor sequencing with risk-based step-up
- **SSO protocol per app** -- SAML 2.0 (broadest legacy support) vs OIDC (modern, token-based) vs SWA (for apps with no federation support, last resort)
- **Provisioning strategy** -- SCIM-based automatic provisioning (preferred) vs JIT provisioning on first SSO (simpler but no deprovisioning) vs manual provisioning with SSO-only integration
- **Lifecycle automation** -- Okta Workflows (no-code, Okta-native) vs external orchestration (ServiceNow, custom middleware) vs direct HR-to-Okta integration with Workday/BambooHR connector
- **Governance model** -- Okta Identity Governance (OIG) for access reviews vs third-party IGA (SailPoint, Saviynt) with Okta as the enforcement point
- **Tenant strategy** -- Single org (simplest management) vs multi-org with Hub (isolation for subsidiaries or compliance) vs preview + production orgs (safe change management)
- **Device trust approach** -- Okta Verify device signals only vs endpoint management integration (Intune/Jamf) vs third-party device posture (CrowdStrike, Zscaler)

## See Also

- `providers/okta/saml-and-oidc-config.md` -- SAML/OIDC configuration patterns, NameID, group claims, client types
- `providers/okta/lifecycle-management.md` -- SCIM provisioning, group rules, profile mastering, Workflows
- `providers/okta/mfa-and-policies.md` -- sign-on and authentication policies, FastPass, FIDO2, network zones
- `general/identity.md` -- cross-platform identity and access management patterns
- `general/tier0-security-enclaves.md` -- Tier 0 security enclave design and hardening
- `providers/microsoft/active-directory.md` -- Active Directory integration with Okta (AD agent)
- `providers/azure/identity.md` -- Entra ID comparison and coexistence patterns
- `patterns/zero-trust.md` -- zero trust architecture patterns

## Reference Links

- [Okta Product Documentation](https://help.okta.com/en-us/content/index.htm) -- official Okta admin and developer documentation
- [Okta Integration Network](https://www.okta.com/integrations/) -- catalog of pre-built application integrations
- [Okta Identity Governance](https://help.okta.com/en-us/content/topics/identity-governance/oig-main.htm) -- access certification, entitlement management, and governance workflows
- [Okta Workflows](https://help.okta.com/wf/en-us/content/topics/workflows/workflows-main.htm) -- no-code identity orchestration and automation
- [Okta Rate Limits](https://developer.okta.com/docs/reference/rate-limits/) -- API rate limit reference by endpoint and org type
- [Okta Security Technical Whitepaper](https://www.okta.com/resources/whitepaper-okta-security-technical-whitepaper/) -- Okta infrastructure security, SOC 2, and compliance details
- [Okta Adaptive MFA](https://help.okta.com/en-us/content/topics/security/mfa/mfa-home.htm) -- MFA factor configuration, policies, and adaptive risk scoring
