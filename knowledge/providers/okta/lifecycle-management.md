# Okta Lifecycle Management

## Scope

This file covers **lifecycle management mechanics** in Okta — group design, group rules, SCIM provisioning and deprovisioning, profile masters and attribute mastering, Okta Workflows orchestration for non-SCIM apps, and the operational details that determine whether joiner / mover / leaver events actually propagate in time. For the broader Okta platform architecture, see `providers/okta/identity.md`. For SAML/OIDC federation config, see `providers/okta/saml-and-oidc-config.md`. For sign-on and MFA policies, see `providers/okta/mfa-and-policies.md`.

## Checklist

- [ ] **[Critical]** Is the profile master designated explicitly per attribute -- HR system for employment status and manager, AD for on-prem-only attributes, Okta for app-specific attributes -- so conflicting writes from multiple sources have a defined winner rather than a race condition?
- [ ] **[Critical]** Is SCIM provisioning enabled on every supported app, with push new users, push profile updates, push group memberships, and push account deactivation all turned on -- the deactivation push is the single most important one and is often left off by default?
- [ ] **[Critical]** Is deprovisioning tested end-to-end -- a test user flagged as terminated in HR, Okta receives the event, SCIM pushes deactivation to every assigned app, and access actually fails at each app within the target SLA (ideally under an hour) -- not just assumed to work because SCIM is configured?
- [ ] **[Critical]** For apps without SCIM support, is deprovisioning handled explicitly via Okta Workflows (API-based disable or account-delete), a scheduled reconciliation job, or a manual checklist -- and is the chosen path documented so nothing falls through?
- [ ] **[Recommended]** Are group rules used to express "who gets what" declaratively based on user attributes (department, location, job code) rather than explicit group membership -- group rules are reevaluated when attributes change, so a move between departments automatically updates access?
- [ ] **[Recommended]** Is the group-to-app assignment pattern standardized -- one group per app role (e.g., `App-Salesforce-Admin`, `App-Salesforce-User`) -- and are app assignments done via group, never direct user assignment, so access changes are always visible in group membership history?
- [ ] **[Recommended]** Are Okta Workflows used for cross-system orchestration that SCIM cannot express -- onboarding tasks (mailbox creation, distribution list adds, Slack invites), offboarding cleanup (reassign manager, forward email, revoke API tokens), and cross-tenant attribute sync?
- [ ] **[Recommended]** Is the attribute-mastering hierarchy documented and visible to the identity team -- when the HR system says "terminated" but AD still says "active", the team needs to know which Okta treats as authoritative and why?
- [ ] **[Recommended]** Are contractor and non-employee accounts handled with a defined lifecycle -- sponsor attribute, expiry date, auto-disable on expiry, sponsor re-certification before extension -- not just provisioned the same as employees and left to accumulate?
- [ ] **[Recommended]** Is the group rule evaluation delay understood (typically seconds to minutes, not instant) and documented, so onboarding processes do not depend on immediate group membership after a profile change?
- [ ] **[Optional]** Are Okta import schedules tuned per source -- HR system frequent (every 15-60 min for employment status changes), directory source less frequent, with conflict handling configured so imports do not bounce attributes between sources?
- [ ] **[Optional]** Is group membership size monitored -- very large groups (thousands of members) degrade SCIM performance and can exceed SP-side size limits, and are the bloated ones identified for splitting?

## Why This Matters

Lifecycle management is where Okta's identity-provider role becomes an identity-governance role. The protocol-level federation (SAML/OIDC) gets a user into an app; lifecycle management determines whether that user should have access in the first place, and -- more importantly -- whether access goes away when it should. The deprovisioning SLA is the measurable outcome: terminated-in-HR to access-denied-at-app in under an hour is the typical compliance target (SOC 2, ISO 27001, most managed-services contracts). Hitting that target requires SCIM on every app that supports it, Workflows or scheduled jobs for apps that do not, and end-to-end testing that catches the gaps.

Profile mastering is the other high-risk area. When multiple sources can write the same attribute, the outcome depends on which one writes last, and "last" is often an import schedule quirk. Explicitly designating a master per attribute -- HR for employment status, AD for on-prem-only attributes, Okta for app-specific attributes -- turns the race into a defined winner. The documentation of this hierarchy matters as much as the configuration: when something is wrong, the team needs to know which source to fix.

Group design is the declarative layer on top of this. Group rules that express access as a function of user attributes -- "everyone in department X with job code Y gets app Z" -- scale better than manual group adds, and they self-correct when attributes change. The common anti-pattern is manual group membership maintained alongside HR changes, which inevitably drifts. Group rules plus a single profile master plus SCIM is the combination that makes joiner / mover / leaver events propagate without human intervention.

SCIM is the mechanism but not a guarantee. SCIM configuration that pushes new users and profile updates but does not push deactivation is common and is exactly the failure mode that produces orphan accounts. The deactivation path is what auditors look at. Testing deactivation -- not just provisioning -- is what proves the configuration.

## Common Decisions (ADR Triggers)

- **Profile master: HR system vs AD vs Okta** -- HR is authoritative for employment status, manager, cost center, and similar business attributes; it is the right master when integrated. AD is authoritative for on-prem attributes and can be the right master for hybrid environments where HR integration is not yet complete. Okta as master is appropriate for app-specific attributes and for organizations without HR integration. Default to HR-mastered for business attributes, AD-mastered for directory attributes, Okta-mastered for app-specific attributes.
- **SCIM vs Okta Workflows for lifecycle** -- SCIM is the right mechanism when the app supports it: standards-based, bidirectional for supported apps, and the lightest-weight configuration. Okta Workflows are the right mechanism when the app has no SCIM (legacy apps, custom internal apps) or when the lifecycle action is more complex than attribute sync (onboarding checklist, cross-tenant coordination). Use SCIM first, Workflows as the complement.
- **Group rules vs manual group membership** -- Group rules are declarative, self-correcting, and the right default for any access pattern expressible as "users with these attributes get this access." Manual membership is appropriate for exception-based access (specific named users for a specific project) and for access that is not attribute-derivable. Default to rules; audit manual memberships quarterly.
- **Contractor lifecycle: same as employees vs separate** -- Same-as-employees is simpler but produces contractor accounts that outlive contracts when the HR system does not track contractor status. Separate lifecycle with sponsor and expiry is more work but catches contractor access that should have ended. For any organization with a meaningful contractor population, separate is the right choice.
- **JIT provisioning vs pre-provisioning via SCIM** -- JIT avoids stale accounts for users who never log in but delays first login and does not work for apps that require pre-configured roles or licenses. SCIM pre-provisioning creates the account when access is assigned, enabling pre-populated permissions but accumulating accounts for users who never log in. Prefer SCIM for apps with pre-configured roles or license costs per account; JIT for apps where first-login delay is acceptable.

## See Also

- `providers/okta/identity.md` -- Okta platform architecture, Universal Directory, and lifecycle-related decisions at the platform level
- `providers/okta/saml-and-oidc-config.md` -- federation protocol configuration; JIT provisioning sits at the intersection
- `providers/okta/mfa-and-policies.md` -- sign-on policies and factor policies that depend on group membership
- `general/identity.md` -- general identity lifecycle patterns
- `general/managed-services-scoping.md` -- deprovisioning SLA expectations in managed-services engagements

## Reference Links

- [Okta Universal Directory](https://help.okta.com/en-us/content/topics/directory/about-universal-directory.htm) -- profile mastering, attribute sources, and conflict handling
- [Okta SCIM provisioning](https://developer.okta.com/docs/concepts/scim/) -- SCIM protocol, supported operations, and troubleshooting
- [Okta group rules](https://help.okta.com/en-us/content/topics/users-groups-profiles/usgp-group-rules.htm) -- rule syntax, evaluation, and group membership updates
- [Okta Workflows](https://help.okta.com/en-us/content/topics/workflows/workflows-main.htm) -- no-code orchestration for identity events
- [Okta import and provisioning behavior](https://help.okta.com/en-us/content/topics/directory/app-provisioning-settings.htm) -- per-app provisioning settings and their effects
