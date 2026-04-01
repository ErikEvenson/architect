# Kopano Cloud

## Scope

European-hosted groupware platform providing email, calendar, contacts, tasks, and notes as a managed cloud service. Covers migration from Amazon WorkMail (dedicated import tooling), directory integration via LDAP/AD sync agent, native Outlook and ActiveSync connectivity, IMAP/POP3 and EWS protocol support, GDPR-compliant EU data residency, multi-tenant container-based architecture, and self-service administration. Kopano Cloud is an AWS-recommended migration destination for organizations leaving Amazon WorkMail before its March 31, 2027 end of support.

## Checklist

### WorkMail Migration Planning

- [ ] **[Critical]** Has the WorkMail migration timeline been established with a target completion date well before March 31, 2027?
- [ ] **[Critical]** Has the Kopano Cloud import service been authorized in the AWS console for user account and mailbox data migration?
- [ ] **[Critical]** Have MX records, SPF, DKIM, and DMARC been planned for cutover from WorkMail to Kopano Cloud?
- [ ] **[Recommended]** Has a pilot migration been performed with a subset of users using Outlook export/import before full migration?
- [ ] **[Recommended]** Are shared mailboxes, distribution groups, aliases, and meeting room resources included in the migration plan?
- [ ] **[Recommended]** Has a rollback plan been documented in case the migration encounters issues during the cutover window?
- [ ] **[Recommended]** Is there a communication plan for end users about the platform transition, including new login URLs and client reconfiguration steps?
- [ ] **[Optional]** Has the option to retain Amazon SES for MX delivery and spam filtering (forwarding to Kopano Cloud via Lambda) been evaluated?

### Email, Calendar, and Contacts

- [ ] **[Critical]** Are custom domains configured and verified in Kopano Cloud with correct DNS records (MX, autodiscover)?
- [ ] **[Critical]** Has Outlook autodiscovery been tested to confirm native client connectivity without manual configuration?
- [ ] **[Recommended]** Are email aliases and distribution groups recreated in Kopano Cloud to match the existing WorkMail configuration?
- [ ] **[Recommended]** Are shared calendars, shared contacts, and shared email folders configured for teams that require collaborative access?
- [ ] **[Recommended]** Are auto-reply rules, mail forwarding rules, and folder structures validated after migration?
- [ ] **[Optional]** Are calendar resource rooms and equipment configured with auto-response booking policies?

### Directory Integration

- [ ] **[Critical]** If the organization uses Active Directory or LDAP, has the Kopano Cloud LDAP/AD sync agent been deployed and tested?
- [ ] **[Critical]** Is there a documented process for user provisioning and deprovisioning that stays in sync with the corporate directory?
- [ ] **[Recommended]** Are only required users synced to Kopano Cloud (not the entire directory)?
- [ ] **[Recommended]** Is the sync agent monitored for connectivity failures and sync errors?
- [ ] **[Optional]** Has the REST API been evaluated for automated user lifecycle management as an alternative or complement to LDAP sync?

### Security and Encryption

- [ ] **[Critical]** Is the data hosting region selected to meet organizational data sovereignty and compliance requirements?
- [ ] **[Critical]** Are administrator accounts secured with strong passwords and limited to authorized personnel?
- [ ] **[Recommended]** Is TLS enforced for all client connections (Outlook, ActiveSync, IMAP, web interface)?
- [ ] **[Recommended]** Are email authentication records (SPF, DKIM, DMARC) configured for all custom domains to prevent spoofing?
- [ ] **[Optional]** Has end-to-end email encryption (S/MIME or PGP) been evaluated for sensitive communications?

### Mobile Device Support and Protocols

- [ ] **[Critical]** Has ActiveSync connectivity been tested on all supported mobile device platforms (iOS, Android)?
- [ ] **[Recommended]** Is a mobile device access policy defined that enforces device encryption and passcode requirements?
- [ ] **[Recommended]** Are IMAP/POP3 access policies configured to allow or restrict third-party client access based on organizational security standards?
- [ ] **[Recommended]** Has EWS (Exchange Web Services) connectivity been validated for calendar clients and integrations that depend on it?
- [ ] **[Optional]** Is remote wipe capability documented for lost or compromised mobile devices?

### Compliance and Data Residency

- [ ] **[Critical]** Has EU data residency been confirmed as meeting organizational and regulatory requirements (GDPR compliance)?
- [ ] **[Critical]** If subject to industry-specific regulations (HIPAA, PCI DSS, SOX), has Kopano Cloud's compliance posture been validated against those requirements?
- [ ] **[Recommended]** Are email retention policies defined and aligned with legal hold and records management requirements?
- [ ] **[Recommended]** Is there a data processing agreement (DPA) in place with Kopano (NHe4a GmbH) that meets organizational procurement standards?
- [ ] **[Optional]** Has the option for on-premises or private-cloud deployment been evaluated for organizations with strict data residency controls?

### Pricing and Licensing

- [ ] **[Recommended]** Is the per-user monthly cost (Standard plan starting at EUR 2.99/user/month) acceptable within the organization's email budget?
- [ ] **[Recommended]** Has the total cost of ownership been compared against alternatives (Microsoft 365, Google Workspace, self-hosted Exchange)?
- [ ] **[Recommended]** Is the subscription reviewed periodically to deactivate unused mailboxes and avoid unnecessary costs?
- [ ] **[Optional]** Have volume pricing or enterprise licensing options been negotiated for large deployments (50,000+ users)?

### Administration and Operations

- [ ] **[Critical]** Has the self-service admin UI been configured with appropriate administrator roles and permissions?
- [ ] **[Recommended]** Is the REST API used for repeatable administrative operations (user creation, domain management) to support auditability?
- [ ] **[Recommended]** Is central branding configured (logo, colors, documentation) to match organizational identity?
- [ ] **[Recommended]** Are administrative actions (user creation, deletion, password resets) logged and auditable?
- [ ] **[Optional]** Has Kopano Cloud's professional services offering (PoC, training, infrastructure design) been evaluated for complex deployments?

## Why This Matters

Kopano Cloud is positioned as a direct migration path for organizations leaving Amazon WorkMail, with dedicated import tooling that reads from the AWS console. As a European-hosted, GDPR-compliant platform built on container-based architecture, it avoids the operational burden of running Exchange on-premises while providing native Outlook compatibility through autodiscovery, ActiveSync, and EWS. Directory sync failures cause authentication drift and orphaned accounts. Missing email authentication records lead to deliverability problems and phishing exposure. Failing to validate protocol support (ActiveSync, IMAP, EWS) before migration risks breaking mobile device connectivity and third-party integrations. Choosing data residency without confirming regulatory alignment can create compliance violations.

## Common Decisions (ADR Triggers)

- **Kopano Cloud vs Microsoft 365 vs Google Workspace** -- European-hosted GDPR compliance and lower per-user cost vs richer collaboration ecosystem; driven by data sovereignty requirements and feature needs
- **Migration approach** -- Kopano Cloud import service (bulk, AWS console authorized) vs Outlook export/import (per-mailbox, manual) vs phased migration with coexistence period
- **Directory integration strategy** -- LDAP/AD sync agent (extend on-premises directory) vs REST API provisioning (cloud-native automation) vs manual user management (small deployments)
- **Mail flow routing** -- direct MX to Kopano Cloud vs retain Amazon SES for inbound filtering and forward to Kopano Cloud; driven by existing spam/threat protection investment
- **Data residency** -- EU-hosted Kopano Cloud (GDPR-native) vs on-premises deployment option for organizations requiring physical control of email data
- **Protocol access policy** -- enable all protocols (ActiveSync, IMAP, POP3, EWS) vs restrict to ActiveSync and Outlook only for tighter security control
- **Email retention and archiving** -- rely on Kopano Cloud's native retention vs integrate with third-party archiving service for eDiscovery and compliance

## Reference Architectures

- [Kopano Cloud Homepage](https://kopano.cloud/) -- product overview, features, deployment architecture, and pricing
- [Kopano Cloud WorkMail Migration](https://kopano.cloud/workmail-migration/) -- migration steps, FAQ, and WorkMail-specific guidance
- [Kopano Cloud Documentation](https://manual.myexchange.rocks) -- end-user and administrator documentation for domain setup, Outlook configuration, and web app usage
- [Amazon WorkMail End of Support](https://docs.aws.amazon.com/workmail/latest/adminguide/workmail-end-of-support.html) -- EOL timeline and AWS-recommended migration destinations including Kopano Cloud

---

## See Also

- `providers/aws/workmail.md` -- Amazon WorkMail configuration, migration-off planning, and end-of-support details
- `general/email-migration.md` -- email platform migration patterns, coexistence, MX cutover, and rollback planning
- `general/data-migration-tools.md` -- general migration planning patterns
- `compliance/gdpr.md` -- GDPR compliance considerations for EU-hosted services
- `general/identity.md` -- directory integration and identity management patterns
- `providers/microsoft/active-directory.md` -- Active Directory integration for LDAP/AD sync agent configuration
