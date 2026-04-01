# Zoom Mail

## Scope

Zoom Mail and Calendar is a business email and calendaring service bundled within the Zoom Workplace platform. Covers migration from Amazon WorkMail and other email platforms, end-to-end encryption for emails between Zoom Mail accounts, integration with the broader Zoom Workplace suite (Meetings, Team Chat, Phone, Whiteboard, Docs), directory and SSO integration via SAML 2.0 and SCIM provisioning, AI Companion features for email composition and scheduling, and multi-platform access across desktop, web, and mobile clients. Zoom Mail can operate as a standalone email service or as a unified client connecting to Gmail or Microsoft 365 backends.

## Checklist

### Migration Planning

- [ ] **[Critical]** Has a migration approach been selected (bulk migration tool, IMAP migration, or manual cutover) with a tested rollback plan?
- [ ] **[Critical]** Are mailbox export procedures validated for the source platform, including calendar events, contacts, distribution lists, and shared resources?
- [ ] **[Critical]** Is there a documented MX record cutover plan with DNS TTL pre-reduction and a defined maintenance window?
- [ ] **[Recommended]** Has a pilot migration been conducted with a subset of users to validate data fidelity and client experience?
- [ ] **[Recommended]** Are shared mailboxes, aliases, and distribution groups mapped to their Zoom Mail equivalents?
- [ ] **[Recommended]** Is there a communication plan for end users covering client installation, credential setup, and feature differences?
- [ ] **[Optional]** Has coexistence routing been planned for phased migrations where both platforms receive mail simultaneously?

### Amazon WorkMail Migration (Specific)

- [ ] **[Critical]** Is the migration timeline aligned with the Amazon WorkMail end-of-support date (March 31, 2027)?
- [ ] **[Critical]** Have WorkMail mailbox exports been tested using the AWS mailbox export API before the service end date?
- [ ] **[Recommended]** Has the Zoom step-by-step migration guide for WorkMail customers been reviewed and validated against organizational requirements?
- [ ] **[Recommended]** Are SPF, DKIM, and DMARC records updated to reflect Zoom Mail endpoints before MX cutover?
- [ ] **[Optional]** Has Zoom sales been engaged for migration assistance or volume pricing for WorkMail displacement deals?

### Email and Calendar Features

- [ ] **[Critical]** Have feature gaps been assessed between the current platform and Zoom Mail (e.g., server-side rules, public folders, delegate access, shared calendars)?
- [ ] **[Recommended]** Are email scheduling, snooze, and custom template features evaluated against organizational workflows?
- [ ] **[Recommended]** Is the calendar integration tested for scheduling Zoom Meetings, Zoom Phone calls, and room resources directly from the calendar?
- [ ] **[Optional]** Are email translation capabilities (30+ languages) relevant and tested for multilingual teams?

### Zoom Workplace Suite Integration

- [ ] **[Critical]** Is the organization on a Zoom Workplace plan that includes Zoom Mail Service, or is Zoom Mail being used only as a client for Gmail or Microsoft 365?
- [ ] **[Recommended]** Is the workflow validated for forwarding emails to Zoom Team Chat channels and initiating meetings from the inbox?
- [ ] **[Recommended]** Are Zoom Whiteboard, Docs, and Clips integrations evaluated for collaboration use cases?
- [ ] **[Optional]** Are Zoom Apps marketplace integrations reviewed for project management and document collaboration tools?

### Directory and SSO Integration

- [ ] **[Critical]** Is SAML 2.0 SSO configured and tested with the organization's identity provider (Okta, Entra ID, Ping, etc.)?
- [ ] **[Critical]** Is SCIM provisioning enabled for automated user lifecycle management (create, update, deactivate)?
- [ ] **[Recommended]** Are group-based policies configured to control feature access (AI Companion, external sharing, etc.) at the account, group, and user levels?
- [ ] **[Recommended]** Is Active Directory or LDAP synchronization validated if the organization requires on-premises directory integration?

### Security and Encryption

- [ ] **[Critical]** Is end-to-end encryption (E2EE) for Zoom Mail understood to apply only between Zoom Mail Service accounts, not to external recipients?
- [ ] **[Critical]** Are encryption-at-rest and encryption-in-transit configurations validated for compliance requirements?
- [ ] **[Recommended]** Are phishing detection and anti-spam filtering capabilities tested and tuned for the organization's threat profile?
- [ ] **[Recommended]** Are admin controls configured to manage AI Companion data usage policies (Zoom does not use customer content to train AI models)?
- [ ] **[Optional]** Is a third-party email security gateway (Mimecast, Proofpoint, etc.) being retained or integrated with Zoom Mail for advanced threat protection?

### Compliance and Certifications

- [ ] **[Critical]** Has the Zoom Trust Center been reviewed to confirm that required compliance certifications (SOC 2 Type II, ISO 27001, ISO 27018) cover Zoom Mail Service?
- [ ] **[Critical]** If HIPAA compliance is required, has a Business Associate Agreement (BAA) been executed with Zoom?
- [ ] **[Critical]** If FedRAMP is required, has Zoom for Government (FedRAMP Moderate authorized) been evaluated instead of commercial Zoom?
- [ ] **[Recommended]** Are data retention and legal hold policies configured to meet regulatory requirements?
- [ ] **[Recommended]** Is journaling or archiving configured with a third-party compliance archiving solution if required by regulation?

### Data Residency

- [ ] **[Critical]** Has the Zoom data residency configuration been reviewed to ensure email data at rest is stored in the required geographic region?
- [ ] **[Recommended]** Are data residency settings validated for all Zoom Workplace services, not just Mail, to avoid unintended cross-border data flows?

### Pricing and Licensing

- [ ] **[Critical]** Is the per-user cost ($4/user/month for standalone Zoom Mail with 50 GB storage) validated against the current email platform cost?
- [ ] **[Recommended]** Has the bundled Zoom Workplace plan pricing been compared against standalone Zoom Mail pricing to determine the most cost-effective approach?
- [ ] **[Recommended]** Are inactive mailbox counts reviewed to right-size the license order?

### API and Automation

- [ ] **[Recommended]** Are Zoom REST API capabilities for mail and calendar management evaluated against automation requirements?
- [ ] **[Recommended]** Are webhook and event notification integrations reviewed for workflow automation (e.g., new mail triggers, calendar event changes)?
- [ ] **[Optional]** Are Zoom Apps SDK capabilities evaluated for custom integrations with internal tools?

### Mobile Device Support

- [ ] **[Recommended]** Is the Zoom Workplace mobile app tested on required device platforms (iOS, Android) for email and calendar access?
- [ ] **[Recommended]** Are mobile device management (MDM) policies validated for the Zoom Workplace app, including app configuration and data protection?
- [ ] **[Optional]** Is the mobile experience validated for offline access and push notification reliability?

### Platform Maturity Considerations

- [ ] **[Critical]** Has the organization assessed the risk of adopting Zoom Mail as a relatively newer entrant compared to established email platforms (Microsoft 365, Google Workspace)?
- [ ] **[Recommended]** Are feature roadmap commitments from Zoom reviewed, particularly for AI-powered scheduling and meeting automation features?
- [ ] **[Recommended]** Is a feature gap analysis documented, including any missing enterprise email capabilities (e.g., advanced mail flow rules, public folders, in-place eDiscovery)?
- [ ] **[Optional]** Is a contract exit clause negotiated in case the platform does not meet evolving requirements?

## Why This Matters

Zoom Mail provides a unified communications experience by embedding email and calendar into the same platform used for meetings, chat, and phone. For organizations migrating from Amazon WorkMail (end of support March 2027), Zoom Mail offers a migration path with straightforward pricing and integrated collaboration tools. However, as a newer entrant in the business email market, Zoom Mail lacks the decades of enterprise email feature depth found in Microsoft 365 Exchange or Google Workspace. End-to-end encryption between Zoom Mail accounts is a differentiator, but it does not extend to external recipients. Organizations must carefully evaluate feature gaps, compliance coverage, and long-term platform viability against the benefits of suite consolidation and simplified licensing.

## Common Decisions (ADR Triggers)

- **Zoom Mail Service vs Zoom Mail Client** -- standalone Zoom-hosted email vs using Zoom as a client for Gmail or Microsoft 365; determines data sovereignty, encryption model, and feature set
- **Zoom Mail vs Microsoft 365 vs Google Workspace** -- full-featured established platform vs unified Zoom Workplace experience; driven by collaboration priorities, compliance requirements, and existing platform investments
- **Standalone Zoom Mail vs bundled Zoom Workplace plan** -- $4/user/month standalone vs bundled pricing that includes Meetings, Phone, Chat, and other services; depends on whether the organization already uses Zoom for other services
- **End-to-end encryption scope** -- E2EE available only between Zoom Mail accounts; organizations with heavy external email may not benefit; drives decision on whether to use Zoom Mail Service or external backend
- **Email security gateway retention** -- keep existing third-party email security (Mimecast, Proofpoint) vs rely on Zoom native spam and phishing filtering; driven by threat model and regulatory requirements
- **Compliance archiving strategy** -- Zoom native retention vs third-party journaling and archiving solution (Barracuda, Proofpoint Archive, Veritas); driven by eDiscovery and regulatory hold requirements
- **Migration approach** -- big-bang MX cutover vs phased coexistence with mail routing between old and new platforms; driven by organizational size and risk tolerance
- **FedRAMP vs commercial Zoom** -- Zoom for Government (FedRAMP Moderate) vs commercial Zoom Workplace; required for federal agencies and some regulated industries

## Reference Architectures

- [Zoom Mail and Calendar Product Page](https://www.zoom.com/en/products/email-calendar/) -- feature overview, supported integrations, and platform capabilities
- [Zoom Amazon WorkMail Migration Guide](https://www.zoom.com/en/lp/amazon-workmail/) -- step-by-step migration guidance and pricing for WorkMail displacement
- [Zoom Trust Center](https://www.zoom.com/en/trust/) -- compliance certifications, security architecture, privacy controls, and data residency options
- [Zoom Trust Legal & Compliance](https://www.zoom.com/en/trust/legal-compliance/) -- SOC 2, ISO 27001, HIPAA BAA, FedRAMP authorization details
- [Zoom REST API Documentation](https://developers.zoom.us/docs/api/) -- API reference for programmatic management and automation
- [Zoom Apps Marketplace](https://marketplace.zoom.us/) -- third-party integrations and custom app capabilities
- [Zoom for Government](https://www.zoom.com/en/industry/government/) -- FedRAMP Moderate authorized deployment for federal and regulated use cases
- [Amazon WorkMail End of Support](https://docs.aws.amazon.com/workmail/latest/adminguide/workmail-end-of-support.html) -- EOL timeline and AWS-recommended migration destinations including Zoom Mail

---

## See Also

- `providers/aws/workmail.md` -- Amazon WorkMail service details, end-of-support planning, and migration-off guidance
- `general/email-migration.md` -- email platform migration patterns, coexistence, MX cutover, and rollback planning
- `general/data-migration-tools.md` -- general migration planning patterns
- `general/identity.md` -- SSO, SAML, SCIM, and directory integration patterns
- `compliance/hipaa.md` -- HIPAA compliance considerations including email encryption
- `compliance/soc2.md` -- SOC 2 compliance requirements for SaaS email services
- `compliance/fedramp.md` -- FedRAMP authorization requirements for government email services
- `providers/microsoft/m365.md` -- Microsoft 365 as an alternative email platform
- `providers/google/workspace.md` -- Google Workspace as an alternative email platform
