# Zoho Mail

## Scope

Zoho Mail is a business email hosting platform offering custom domain email, calendar, contacts, tasks, and notes with deep integration into the Zoho Workplace productivity suite. Covers migration from Amazon WorkMail (an AWS-recommended migration destination post-WorkMail EOL), directory and SSO integration via SAML 2.0 and Active Directory sync, security features including S/MIME encryption and two-factor authentication, compliance certifications (SOC 2, GDPR, HIPAA, ISO 27001), eDiscovery and email retention policies, data residency options across US, EU, India, and Australia data centers, REST API and integration capabilities, and mobile device management. Pricing spans five tiers from a free plan through Mail Lite, Mail Premium, Workplace Standard, Workplace Professional, and Workplace Enterprise.

## Checklist

### Migration from Amazon WorkMail

- [ ] **[Critical]** Has the WorkMail mailbox export been completed (email, calendar, contacts, shared resources) before the March 31, 2027 end-of-support deadline?
- [ ] **[Critical]** Is the migration method selected -- Zoho one-click migration tool, IMAP migration, or third-party migration tool (audriga, Transend Migrator)?
- [ ] **[Critical]** Are MX records, SPF, DKIM, and DMARC DNS records planned for cutover to Zoho Mail endpoints?
- [ ] **[Recommended]** Is a pilot migration planned with a subset of users to validate folder structure preservation, calendar events, and contact fidelity?
- [ ] **[Recommended]** Are shared mailboxes, distribution groups, and meeting room resources mapped to Zoho equivalents (group aliases, resource booking)?
- [ ] **[Recommended]** Is there a coexistence plan for the transition period (e.g., mail forwarding from WorkMail to Zoho during phased migration)?
- [ ] **[Optional]** Has a rollback plan been documented in case of migration issues?

### Email, Calendar, Contacts, and Tasks

- [ ] **[Critical]** Are custom domain email addresses configured with proper DNS verification?
- [ ] **[Critical]** Are email authentication records (SPF, DKIM, DMARC) configured for all sending domains?
- [ ] **[Recommended]** Are shared calendars and resource booking (meeting rooms, equipment) configured for organizational use?
- [ ] **[Recommended]** Are contact sharing policies defined (private contacts vs organization-wide directory)?
- [ ] **[Recommended]** Are email delegation and shared mailbox permissions configured for teams that require them?
- [ ] **[Optional]** Are Zoho Streams (collaborative email discussions) enabled for teams that benefit from threaded email conversations?
- [ ] **[Optional]** Are tasks and notes integrated with calendar for project tracking workflows?

### Zoho Workplace Suite Integration

- [ ] **[Recommended]** Has the appropriate tier been selected based on suite requirements -- Mail-only (Lite/Premium) vs Workplace (Standard/Professional/Enterprise)?
- [ ] **[Recommended]** Are Zoho WorkDrive file storage quotas planned for Workplace tier deployments (100 GB team storage for Standard, 1 TB for Professional)?
- [ ] **[Recommended]** Are collaborative document tools (Writer, Sheet, Show) evaluated against existing office suite requirements?
- [ ] **[Optional]** Is Zoho Cliq (team chat) configured for real-time communication alongside email?
- [ ] **[Optional]** Is Zoho Meeting integrated for video conferencing workflows?
- [ ] **[Optional]** Is Zoho Vault (password manager) deployed for credential management in Workplace tiers?

### Directory and SSO Integration

- [ ] **[Critical]** Is SAML 2.0 SSO configured with the organization's identity provider (Okta, Azure AD/Entra ID, Ping Identity)?
- [ ] **[Critical]** Is Active Directory synchronization configured for automated user provisioning and deprovisioning?
- [ ] **[Recommended]** Is multi-factor authentication enforced organization-wide through Zoho's built-in TFA or the identity provider?
- [ ] **[Recommended]** Is SCIM provisioning configured for automated user lifecycle management?
- [ ] **[Recommended]** Are group memberships and distribution lists synchronized from the corporate directory?
- [ ] **[Optional]** Is OAuth 2.0 configured for third-party application access to Zoho Mail APIs?

### Security Features

- [ ] **[Critical]** Is two-factor authentication (TFA) enforced for all user accounts?
- [ ] **[Critical]** Is encryption at rest and in transit verified as enabled (enabled by default in Zoho Mail)?
- [ ] **[Recommended]** Is S/MIME email encryption configured for users handling sensitive communications (available in Mail Premium and Workplace Professional)?
- [ ] **[Recommended]** Are anti-spam and anti-phishing policies tuned, including quarantine review procedures?
- [ ] **[Recommended]** Is data loss prevention (DLP) configured for outbound email scanning (available in Mail Premium)?
- [ ] **[Recommended]** Are email recall and undo-send features enabled and users trained on their limitations?
- [ ] **[Optional]** Are IP-based access restrictions configured to limit admin console and mailbox access to corporate networks?
- [ ] **[Optional]** Are allowed/blocked sender lists maintained at the organization level?

### Compliance Certifications

- [ ] **[Critical]** Has the organization confirmed that Zoho Mail's compliance certifications (SOC 2 Type II, ISO 27001, GDPR, HIPAA) meet regulatory requirements?
- [ ] **[Critical]** If HIPAA compliance is required, is a Business Associate Agreement (BAA) executed with Zoho?
- [ ] **[Recommended]** Are Zoho's SOC 2 Type II and SOC 1 Type II audit reports reviewed annually?
- [ ] **[Recommended]** Is the organization aware of additional certifications -- ISO 27017 (cloud security), ISO 27018 (PII protection), ISO 27701 (privacy management), PCI DSS?
- [ ] **[Optional]** Are regional certifications verified for applicable jurisdictions (Cyber Essentials Plus for UK, NCA for Saudi Arabia, ENS for Spain, Tx-RAMP for Texas)?

### eDiscovery and Retention Policies

- [ ] **[Critical]** Are email retention policies configured to meet regulatory and legal hold requirements (available in Mail Premium and Workplace Professional)?
- [ ] **[Critical]** Is the eDiscovery portal configured with appropriate admin access for legal and compliance teams?
- [ ] **[Recommended]** Are retention storage quotas planned (50 GB/user for Mail Premium, 100 GB/user for Workplace Professional)?
- [ ] **[Recommended]** Is the eDiscovery search workflow tested end-to-end, including export of discovered emails?
- [ ] **[Optional]** Are retention policies differentiated by department or user group based on regulatory requirements?

### Pricing and Licensing

- [ ] **[Critical]** Is the correct tier selected based on feature requirements -- Mail Lite (basic email), Mail Premium (retention, eDiscovery, S/MIME), Workplace Standard (collaboration suite), Workplace Professional (full suite with retention), Workplace Enterprise (custom limits, VPC)?
- [ ] **[Recommended]** Are per-user costs evaluated against current WorkMail spend ($4/user/month) -- Mail Premium at $4/user/month, Workplace Standard at ~$3.17/user/month, Workplace Professional at $6/user/month?
- [ ] **[Recommended]** Is annual billing selected for the approximately 20% discount over monthly billing?
- [ ] **[Optional]** Has Workplace Enterprise been evaluated for organizations exceeding 100,000 users requiring virtual private cloud deployment?

### Data Residency

- [ ] **[Critical]** Is the appropriate data center region selected to meet data sovereignty requirements (US, EU - Netherlands/Ireland, India, Australia)?
- [ ] **[Recommended]** Is the data residency selection documented in compliance records for audit purposes?
- [ ] **[Recommended]** Are data handling and cross-border transfer policies reviewed against GDPR and local privacy regulations?

### API and Integration Capabilities

- [ ] **[Recommended]** Are Zoho Mail REST APIs evaluated for integration with internal tools (mailbox access, send, folder management)?
- [ ] **[Recommended]** Is IMAP/POP/ActiveSync access configured for users requiring third-party email client support (not available on free tier)?
- [ ] **[Recommended]** Are Zoho CRM and other Zoho application integrations configured where applicable?
- [ ] **[Optional]** Are webhook integrations configured for mailbox event notifications?
- [ ] **[Optional]** Is Zoho Flow or Zapier integration evaluated for workflow automation across email and other business tools?

### Mobile Device Support

- [ ] **[Critical]** Is a mobile device access policy configured enforcing device encryption, passcode, and remote wipe capability?
- [ ] **[Recommended]** Are Zoho Mail mobile apps (iOS and Android) deployed via MDM for managed devices?
- [ ] **[Recommended]** Is ActiveSync configured for users requiring native mail client access on mobile devices?
- [ ] **[Recommended]** Are mobile access management controls evaluated (available in Mail Premium and above)?
- [ ] **[Optional]** Is a BYOD policy defined that aligns Zoho mobile device policies with corporate security standards?

## Why This Matters

Zoho Mail is one of three AWS-recommended migration destinations for organizations leaving Amazon WorkMail before its March 2027 end-of-support date. Selecting the wrong pricing tier leads to missing critical compliance features -- retention and eDiscovery are only available in Mail Premium and above, while S/MIME encryption requires Premium or Professional tiers. Directory integration failures during migration cause authentication outages across the organization. Missing email authentication records (SPF/DKIM/DMARC) after MX record cutover result in deliverability failures and phishing exposure. Organizations subject to data sovereignty regulations must select the correct data center region at deployment time, as migration between regions requires a full mailbox re-migration.

## Common Decisions (ADR Triggers)

- **Mail-only vs Workplace suite** -- Mail Lite/Premium for email-only needs vs Workplace Standard/Professional for integrated collaboration (documents, chat, video, file storage); drives per-user cost and feature availability
- **Zoho Mail vs Microsoft 365 vs Google Workspace** -- cost, compliance certifications, existing ecosystem integrations, and collaboration tool requirements; Zoho offers lower per-user pricing but a smaller third-party integration ecosystem
- **Pricing tier selection** -- Mail Lite (basic email at 5-10 GB), Mail Premium (50 GB with retention/eDiscovery/S/MIME), Workplace Standard (30 GB with collaboration suite), Workplace Professional (100 GB with full compliance), Workplace Enterprise (custom, VPC for 100K+ users)
- **Data residency region** -- US, EU (Netherlands/Ireland), India, or Australia; driven by data sovereignty regulations and user proximity; cannot be changed without re-migration
- **Directory integration strategy** -- SAML 2.0 SSO with existing IdP vs Active Directory sync vs Zoho Directory as standalone; impacts user lifecycle management and authentication flow
- **Migration approach from WorkMail** -- Zoho one-click migration vs IMAP migration vs third-party tools (audriga); phased batch migration vs big-bang cutover; driven by mailbox count, downtime tolerance, and calendar/contact fidelity requirements
- **eDiscovery and retention architecture** -- built-in Zoho eDiscovery (Mail Premium/Workplace Professional) vs third-party archiving service (Barracuda, Mimecast, Proofpoint); driven by legal hold complexity and cross-platform search requirements
- **Mobile device management** -- Zoho built-in mobile access management vs external MDM (Intune, Jamf) with ActiveSync; driven by existing MDM investment and BYOD policy

## Reference Architectures

- [Zoho Mail Product Overview](https://www.zoho.com/mail/) -- feature overview, security highlights, and plan comparison
- [Zoho Mail Pricing](https://www.zoho.com/mail/pricing.html) -- detailed plan comparison (Free, Mail Lite, Mail Premium, Workplace Standard, Workplace Professional, Workplace Enterprise)
- [Zoho Workplace as AWS WorkMail Alternative](https://www.zoho.com/workplace/lp/aws-workmail-alternative.html) -- migration features, comparison with WorkMail, and one-click migration details
- [Zoho Mail Admin Guide](https://www.zoho.com/mail/help/adminconsole/) -- administration, user management, and domain configuration
- [Zoho Mail API Documentation](https://www.zoho.com/mail/help/api/) -- REST API reference for mailbox operations and integrations
- [Zoho Compliance Certifications](https://www.zoho.com/compliance.html) -- SOC 2, ISO 27001, GDPR, HIPAA, and regional certifications
- [Zoho Mail Security Overview](https://www.zoho.com/mail/security.html) -- encryption, TFA, S/MIME, anti-spam, and DLP features
- [Zoho Directory](https://www.zoho.com/directory/) -- SSO, SAML 2.0, Active Directory sync, and SCIM provisioning

---

## See Also

- `providers/aws/workmail.md` -- Amazon WorkMail end-of-support planning and migration-off strategy
- `general/email-migration.md` -- email platform migration patterns, coexistence, MX cutover, and rollback planning
- `general/data-migration-tools.md` -- general migration planning patterns
- `general/identity.md` -- identity and SSO architecture patterns
- `compliance/hipaa.md` -- HIPAA compliance considerations including email encryption
- `compliance/gdpr.md` -- GDPR data protection and data residency requirements
- `compliance/soc2.md` -- SOC 2 compliance audit and reporting requirements
- `providers/microsoft/m365.md` -- Microsoft 365 as alternative email/collaboration platform
- `providers/google/workspace.md` -- Google Workspace as alternative email/collaboration platform
