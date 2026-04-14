# Okta MFA and Policies

## Scope

This file covers **Okta sign-on policies, authentication policies, and factor enrollment** — the layer that determines who can authenticate, with what factors, from where, and how often. Topics: global session policy, app-level authentication policy, factor enrollment policy, network zones, device trust signals, FastPass, FIDO2/WebAuthn deployment, the SMS/voice deprecation path, step-up authentication, and the interaction with Okta ThreatInsight. For Okta platform architecture, see `providers/okta/identity.md`. For SAML/OIDC session lifetime coordination, see `providers/okta/saml-and-oidc-config.md`. For group-based policy targeting, see `providers/okta/lifecycle-management.md`.

## Checklist

- [ ] **[Critical]** Are phishing-resistant factors (FIDO2/WebAuthn security keys, Okta FastPass with device binding, platform authenticators like Touch ID / Windows Hello) enrolled as the primary MFA for all users -- not just available as an option alongside push and TOTP?
- [ ] **[Critical]** Are SMS and voice factors disabled or restricted to fallback-only for specific risk-accepted populations -- SMS-based MFA is defeated by SIM-swap attacks and is no longer a defensible control for any sensitive workload?
- [ ] **[Critical]** Is the authentication policy tiered by application sensitivity -- high-sensitivity apps (admin consoles, financial systems, PII repositories) require phishing-resistant MFA every session; medium-sensitivity apps allow FastPass or push; low-sensitivity apps use the default session -- rather than a single global policy applied to everything?
- [ ] **[Critical]** Is the Super Admin role protected with a separate, stricter authentication policy -- phishing-resistant factor required, short session duration, restricted network zone, device trust required -- and audited quarterly for role membership?
- [ ] **[Recommended]** Are network zones configured to define trusted locations (corporate ranges, approved VPN egress) and untrusted locations (high-risk countries, known bad ASNs), with authentication policies that require step-up MFA or block access from untrusted zones?
- [ ] **[Recommended]** Is device trust integrated via Okta Verify device signals or via endpoint-management integration (Jamf, Intune, CrowdStrike Falcon Device Control, VMware Workspace ONE) so policies can require "managed device" as a condition, not just successful MFA?
- [ ] **[Recommended]** Is Okta FastPass deployed as the primary factor where possible -- passwordless, phishing-resistant, device-bound, and user-friendly -- with FIDO2 security keys as the break-glass factor for FastPass failures?
- [ ] **[Recommended]** Is factor enrollment itself protected -- enrollment requires an existing strong factor, is not allowed from untrusted networks, and enrollment events are logged and alerted on?
- [ ] **[Recommended]** Is Okta ThreatInsight enabled and tuned -- it blocks IPs with confirmed credential-stuffing activity, and its default "log only" mode is insufficient; should be set to "block" with an audit period to confirm no false positives?
- [ ] **[Recommended]** Are session durations set intentionally per policy -- global session typically 2-8 hours for normal apps, 30-60 minutes for admin access, single-session (re-auth every login) for high-sensitivity apps -- not left at the Okta default for everything?
- [ ] **[Optional]** Is step-up authentication configured for sensitive operations within an app (re-auth required at the point of transaction, admin action, or data export) rather than relying on the session-entry auth to carry the whole session?
- [ ] **[Optional]** Is the `Sign-on Policy` evaluation order documented and understood -- policies are evaluated in order, first-match wins, and policy ordering is a frequent source of "this policy should apply but does not"?

## Why This Matters

MFA configuration is the layer where most real-world account takeovers are stopped or not stopped. The single largest step in the last five years was the move from "MFA enabled with any factor" to "MFA enrolled with phishing-resistant factors" -- SMS and push-based MFA are both defeated by attackers at scale now (SIM swap, push fatigue). An Okta deployment that says "MFA is enabled" but lets users enroll SMS as their only factor is delivering a materially weaker control than the organization thinks. The enrollment policy is where this is fixed: allowed factor types, required factor types, and minimum factor strength are all configurable, and "FIDO2 or platform authenticator required" is the current defensible default.

Tiered authentication policies are what distinguish a mature deployment from an "MFA on everything" deployment. A single global policy applied to every app is either too strict (users hit MFA 50 times a day for low-sensitivity apps and train themselves to click through) or too loose (admin consoles get the same protection as the cafeteria menu). Tiering by application sensitivity -- typically three to five tiers -- lets the control scale with the risk.

Super Admin protection is the single-highest-leverage policy. A compromised Super Admin can pivot to everything; the policy for that role is where the organization should spend its strictness budget. Separate policy, phishing-resistant factor only, short session, restricted network zone, device-trust-required, and quarterly membership audit -- this is the minimum defensible configuration for an Okta tenant of any size.

Network zones and device trust are what move the policy from "was MFA used" to "was MFA used from a trusted posture." The user who logs in from a managed laptop on the corporate network with FastPass is a different risk than the user who logs in from an unmanaged device on a public network with a one-time code -- and the policy should reflect that even when the MFA factor is nominally the same. ThreatInsight is the low-effort addition to this: Okta's IP-reputation data is high-quality and blocking known-bad IPs at the edge is cheap protection.

## Common Decisions (ADR Triggers)

- **Factor strategy: phishing-resistant primary vs push/TOTP primary** -- Phishing-resistant factors (FIDO2, FastPass, platform authenticators) are the current defensible default and are what most frameworks (CISA, PCI 4.0, SOC 2 at Type 2 maturity) now expect. Push and TOTP are acceptable as fallbacks but should not be the primary factor. SMS and voice should be disabled. The migration from push-primary to FastPass-primary is the single highest-value change in most existing Okta deployments.
- **Global sign-on policy vs per-app authentication policy** -- Global sign-on policy covers the "did the user authenticate to Okta" question; per-app authentication policy covers the "is this session allowed to access this specific app" question. Use both: the global policy sets the baseline, per-app policies step up for sensitive apps. Apps left on the default policy are the common gap.
- **Device trust: Okta Verify signals vs endpoint-management integration** -- Okta Verify device signals (device registered, biometric present) are the low-effort path and sufficient for many deployments. Endpoint-management integration (Jamf, Intune, CrowdStrike) gives richer signals (device compliance, posture, threat detection) but requires the endpoint-management deployment as a prerequisite. For organizations with mature endpoint management, the integration pays off; for organizations without, Okta Verify signals are the right starting point.
- **ThreatInsight: log-only vs block** -- Log-only produces visibility but does not actually prevent the attack. Block stops credential stuffing at the edge but requires a tuning period to confirm the false-positive rate is acceptable. Most deployments should move to block after 2-4 weeks of log-only observation.
- **Session duration: long for UX vs short for risk** -- Long sessions (8-16 hours) reduce re-auth friction but extend the blast radius of a stolen session cookie. Short sessions (30-60 min) for admin access and sensitive apps limit blast radius but increase re-auth frequency. Default: 8 hours for normal apps, 60 min for admin, single-session for the most sensitive (privilege elevation, financial transaction authorization).

## See Also

- `providers/okta/identity.md` -- Okta platform architecture, factor types, and the overall MFA strategy
- `providers/okta/saml-and-oidc-config.md` -- SAML/OIDC session lifetime coordination with Okta session duration
- `providers/okta/lifecycle-management.md` -- group-based policy targeting; policies are typically scoped to groups
- `general/identity.md` -- general MFA and authentication policy patterns
- `general/cloud-workload-hardening.md` -- defense-in-depth beyond the identity layer

## Reference Links

- [Okta authentication policies](https://help.okta.com/en-us/content/topics/security/policies/configure-app-auth-policies.htm) -- app-level policy configuration and rule evaluation
- [Okta FastPass](https://help.okta.com/en-us/content/topics/identity-engine/devices/fastpass-main.htm) -- passwordless, phishing-resistant primary factor
- [Okta FIDO2 / WebAuthn](https://help.okta.com/en-us/content/topics/security/mfa/webauthn.htm) -- security-key enrollment and fallback policy
- [Okta ThreatInsight](https://help.okta.com/en-us/content/topics/security/threat-insight/about-threatinsight.htm) -- IP reputation, detection modes, and block configuration
- [Okta network zones](https://help.okta.com/en-us/content/topics/security/network/network-zones.htm) -- trusted/untrusted zone configuration
- [Okta global session policy](https://help.okta.com/en-us/content/topics/security/policies/configure-session-policy.htm) -- session duration, MFA requirements, and factor-strength rules
