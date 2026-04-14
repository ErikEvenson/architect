# Okta SAML and OIDC Configuration

## Scope

This file covers **the actual configuration patterns** for wiring cloud apps up to Okta via SAML 2.0 and OIDC — metadata exchange, attribute/claim mapping, signing and encryption choices, group claim delivery, assertion vs session duration, the IdP-initiated vs SP-initiated tradeoff, and JIT provisioning. For the broader Okta platform architecture and decision between protocols, see `providers/okta/identity.md`. For lifecycle provisioning via SCIM, see `providers/okta/lifecycle-management.md`. For sign-on policies and MFA, see `providers/okta/mfa-and-policies.md`.

## Checklist

- [ ] **[Critical]** Is the protocol chosen per application based on what the app actually supports -- SAML 2.0 for most legacy enterprise SaaS, OIDC for modern apps and anything on mobile/SPA, WS-Federation only when the app supports nothing else -- not based on a default preference?
- [ ] **[Critical]** Is the SAML assertion signed with SHA-256 or stronger (never SHA-1), and is the Okta signing certificate rotated on a tracked schedule with the SP notified before rotation -- surprise certificate rotations are the most common Okta-side outage?
- [ ] **[Critical]** Is the SAML `NameID` format chosen intentionally (`EmailAddress` for most SaaS, `Persistent` for apps that need a stable opaque identifier even if email changes, `Unspecified` only when the SP explicitly requires it) and matched to what the SP expects in its ACS configuration?
- [ ] **[Critical]** Are group claims delivered correctly -- for SAML, as a multi-valued `groups` attribute filtered by regex or explicit list; for OIDC, as a `groups` claim in the ID token or UserInfo response -- with a filter so only groups the SP actually needs are sent (not every group the user is in)?
- [ ] **[Critical]** Is the OIDC client type chosen correctly -- `Web` (confidential client with client secret) for server-rendered apps, `SPA` (PKCE, no secret) for browser apps, `Native` (PKCE) for mobile, `Service` (client credentials) for backend-to-backend -- and is the grant type set to match?
- [ ] **[Recommended]** Is assertion encryption enabled on SAML integrations where the assertion carries sensitive attributes (user profile, group membership, PII) -- not just signed, but encrypted with the SP's public key so intermediaries cannot read the assertion?
- [ ] **[Recommended]** Is the Okta sign-on policy duration coordinated with the SAML/OIDC session lifetime at the SP -- short Okta session with long SP session means re-auth still takes the user back to the app; long Okta session with short SP session means a session-refresh loop?
- [ ] **[Recommended]** Is IdP-initiated vs SP-initiated login chosen per app -- SP-initiated is preferred (better deep-linking, CSRF protection), IdP-initiated is fine for dashboard-launch apps but requires `RelayState` handling at the SP?
- [ ] **[Recommended]** Is JIT (Just-In-Time) provisioning configured on apps that support it, so first-time users are created at the SP without a pre-seeded account -- paired with SCIM deprovisioning to avoid orphan accounts?
- [ ] **[Recommended]** Are OIDC refresh tokens configured intentionally -- offline access for apps that legitimately need it, rotation enabled, revocation tested on session termination -- and is the access-token lifetime kept short (5-60 min) with refresh handling the long-lived session?
- [ ] **[Optional]** Is a custom authorization server used for OIDC apps that need app-specific claims, scopes, or token lifetimes beyond what the default Okta authorization server provides?
- [ ] **[Optional]** Are SAML attribute transformations used to reshape attributes at assertion time (concatenation, substring, lookup) rather than trying to reshape in Universal Directory, keeping the UD clean?

## Why This Matters

SAML and OIDC misconfiguration is the single most common source of federation outages, and the problems cluster in predictable places. Certificate rotation is the most reliably surprising: an Okta signing certificate expires, nobody told the SP, and every app behind that IdP stops working at the same moment. A rotation playbook -- scheduled, pre-notified to SP owners, with overlap periods -- turns this from an outage into a non-event.

Group claim delivery is the second cluster. An app that expects a `groups` claim but gets nothing -- because the Okta integration's group attribute is unfiltered and Okta silently drops claims that exceed size limits -- produces a user who can authenticate but cannot see anything. Explicit group filters (regex or enumeration) and testing with a user who is in many groups are what catch this. For OIDC, the ID token vs UserInfo decision matters: putting large group lists in the ID token bloats every request, while moving them to UserInfo adds a second call but keeps tokens small.

Protocol choice by "what the app supports" rather than "what the identity team prefers" avoids the other common trap -- trying to use OIDC with a legacy app that has partial OIDC support but was designed for SAML, or vice versa. The integration is only as solid as the less-capable side; matching the protocol to the app's actual support profile is cheaper than fighting it.

Session-lifetime coordination between Okta and the SP is the third cluster. Users who re-authenticate at Okta but are still bounced back to login at the app, or users who stay logged into the app long after the Okta session ended -- both are coordination problems between the Okta sign-on policy and the SP's session configuration. Documenting both sides of the session and testing the expected expiry behavior is what catches this.

## Common Decisions (ADR Triggers)

- **SAML vs OIDC for a new integration** -- SAML has broader legacy enterprise support, richer assertion/attribute semantics, and is the default in older SaaS. OIDC is simpler (JSON instead of XML), better suited to mobile and SPA, supports access-token-based API access cleanly, and is the default in modern SaaS. Choose based on what the app supports; prefer OIDC when both are available.
- **`EmailAddress` vs `Persistent` NameID format** -- `EmailAddress` is stable for most users and integrates cleanly with email-as-username apps, but changes when the user's email changes (marriage, rebrand) and breaks the link to SP-side data. `Persistent` provides a stable opaque identifier that survives email changes but requires the SP to handle identifier-to-email lookup. Default to `EmailAddress` unless email changes are expected and the SP supports `Persistent`.
- **Group claim delivery: ID token vs UserInfo (OIDC) or signed vs encrypted assertion (SAML)** -- ID token / signed assertion is simpler and more performant but exposes group membership to anything that inspects the token. UserInfo / encrypted assertion keeps group data server-to-server but adds a round trip or requires SP key management. Default to the simpler choice unless group membership is sensitive.
- **Default authorization server vs custom authorization server (OIDC)** -- The default (org authorization server) is sufficient for most apps, includes the standard OIDC scopes, and requires no configuration. Custom authorization servers are appropriate when the app needs custom scopes, custom claims beyond Okta's defaults, or different token lifetimes. The custom authorization server is a licensed feature (API Access Management); do not enable it without confirming the license.
- **JIT provisioning vs SCIM pre-provisioning** -- JIT creates the SP account on first login, avoiding stale accounts for users who never log in. SCIM pre-provisioning creates the account when the user is assigned to the app, enabling pre-populated permissions and immediate access on first login. Prefer SCIM for apps with pre-configured roles or license costs per account; JIT for apps where first-login is acceptable and account costs are low.

## See Also

- `providers/okta/identity.md` -- Okta platform architecture, Universal Directory, and protocol-selection decisions
- `providers/okta/lifecycle-management.md` -- SCIM provisioning and deprovisioning, group rules, JIT provisioning
- `providers/okta/mfa-and-policies.md` -- sign-on policies, factor enrollment, FastPass, FIDO2, session duration
- `general/identity.md` -- general identity and federation patterns

## Reference Links

- [Okta SAML](https://developer.okta.com/docs/concepts/saml/) -- SAML assertion structure, signing, NameID formats
- [Okta OIDC / OAuth 2.0](https://developer.okta.com/docs/concepts/oauth-openid/) -- OIDC client types, flows, token lifetimes
- [Okta custom authorization servers](https://developer.okta.com/docs/concepts/auth-servers/) -- when to use the default vs a custom authorization server
- [Okta SAML attribute statements](https://developer.okta.com/docs/guides/saml-application-setup/main/) -- attribute mapping and group filtering
- [Okta certificate rotation](https://help.okta.com/en-us/content/topics/security/certificate-management.htm) -- signing certificate rotation and pre-rotation
