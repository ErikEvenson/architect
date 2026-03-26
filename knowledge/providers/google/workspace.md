# Google Workspace

## Scope

This document covers Google Workspace architecture and administration, including Gmail (mail flow, routing, compliance), Google Drive (shared drives, DLP, storage management), Google Calendar, Google Meet, identity integration (Google Cloud Directory Sync, SAML SSO, LDAP), Admin Console configuration, Google Vault (eDiscovery, retention, legal holds), endpoint management (device policies, mobile management, context-aware access), Security Center (investigation tool, security dashboard, alert center), migration from Exchange/M365 to Google Workspace, and Workspace licensing tiers (Business Starter/Standard/Plus, Enterprise Standard/Plus, Frontline, Education).

## Checklist

- [ ] **[Critical]** Is the Google Workspace domain verified with correct DNS TXT records, and is the organizational unit (OU) hierarchy designed to reflect the organization's administrative delegation model?
- [ ] **[Critical]** Is identity integration configured -- Google Cloud Directory Sync (GCDS) for provisioning from on-premises Active Directory, SAML 2.0 SSO with the enterprise IdP (Okta, Entra ID, Ping), and password synchronization or federation strategy documented?
- [ ] **[Critical]** Are Gmail MX records configured correctly, and is SPF, DKIM, and DMARC published for all sending domains to prevent spoofing and ensure deliverability?
- [ ] **[Critical]** Is Gmail mail routing designed for the organization's requirements -- inbound gateway (e.g., Proofpoint, Mimecast before Gmail), outbound relay, split delivery during migration coexistence, and compliance routing rules for journaling or archival?
- [ ] **[Critical]** Is the licensing tier selected (Business vs Enterprise) with a clear understanding of feature gaps -- Enterprise Plus includes S/MIME, DLP, Vault, advanced endpoint management, security investigation tool, and client-side encryption?
- [ ] **[Critical]** Is multi-factor authentication enforced via 2-Step Verification policies, with security keys required for high-privilege admin accounts and phishing-resistant methods (FIDO2) preferred organization-wide?
- [ ] **[Critical]** Is the migration strategy from Exchange/M365 defined, including tool selection (Google Workspace Migration for Microsoft Exchange/GWMME, Google Workspace Migrate, or third-party tools like BitTitan/Quest), batch scheduling, and user communication plan?
- [ ] **[Recommended]** Is Google Vault configured with retention rules covering Gmail, Drive, Chat, Meet recordings, and Groups -- with litigation hold procedures documented for legal/compliance requirements?
- [ ] **[Recommended]** Are data loss prevention (DLP) rules configured for Gmail and Drive to detect and prevent sharing of sensitive data (PII, financial data, health records), with appropriate actions (block, quarantine, warn)?
- [ ] **[Recommended]** Is Google Drive architecture planned with shared drive structure, membership policies, external sharing controls (domain allowlists, link sharing restrictions), and storage quota management?
- [ ] **[Recommended]** Is endpoint management configured with device policies (screen lock, encryption requirements, OS version minimums), mobile device management (basic vs advanced), and context-aware access policies that restrict access based on device posture, IP range, and location?
- [ ] **[Recommended]** Is the Google Workspace Security Center configured with custom alerts, security dashboard monitoring, and investigation tool access granted to security operations staff?
- [ ] **[Recommended]** Are Google Groups designed for mail distribution, shared drive access, and application-level permissions -- with naming conventions, group creation policies (admin-only vs user self-service), and external membership controls defined?
- [ ] **[Recommended]** Is Google Meet governance defined including recording policies, external participant controls, live streaming restrictions, and meeting safety settings (host controls, quick access vs knock)?
- [ ] **[Optional]** Is client-side encryption (CSE) evaluated for Gmail, Drive, Calendar, and Meet if the organization requires control over encryption keys beyond Google's default encryption (Enterprise Plus required)?
- [ ] **[Optional]** Is Google Workspace Add-ons and Marketplace app governance configured with allowlisting policies to control which third-party applications can access organizational data?
- [ ] **[Optional]** Are Google Workspace audit logs forwarded to the organization's SIEM (Splunk, Sentinel, Chronicle) via the Reports API or BigQuery export for centralized security monitoring?
- [ ] **[Optional]** Is AppSheet or Google Apps Script governance defined if the organization uses low-code/no-code automation within Workspace?

## Why This Matters

Google Workspace is the primary alternative to Microsoft 365 for enterprise cloud productivity, and its architecture differs significantly in identity model, administration approach, and security controls. Organizations migrating from Exchange or M365 to Google Workspace face unique challenges around identity federation (GCDS + SAML vs Entra Connect), mail routing during coexistence (split delivery), and feature parity gaps (e.g., Vault vs Purview, endpoint management vs Intune). The licensing structure is simpler than M365 but the Enterprise tier boundary is critical -- organizations on Business plans lack Vault, advanced DLP, Security Center investigation tools, and client-side encryption.

Google Workspace security relies heavily on correct Admin Console configuration: 2-Step Verification enforcement, context-aware access policies, DLP rules, and sharing restrictions. Unlike M365 where conditional access is a distinct Entra ID feature, Google Workspace bundles access controls into the Admin Console with context-aware access requiring Enterprise licensing. The migration from Exchange/M365 is operationally complex, particularly for organizations with heavy use of shared mailboxes, public folders, resource calendars, and distribution lists that require mapping to Google Workspace equivalents.

## Common Decisions (ADR Triggers)

- **Business vs Enterprise licensing** -- cost optimization vs security/compliance features, particularly Vault, DLP, Security Center, CSE, and advanced endpoint management
- **Identity federation model** -- GCDS + SAML SSO vs Google as primary IdP, password sync vs federation, MFA via Google vs external IdP
- **Third-party email security vs Gmail native** -- Proofpoint/Mimecast as inbound gateway vs relying on Gmail's built-in protections (advanced phishing/malware in Enterprise)
- **Migration tool selection** -- GWMME vs Google Workspace Migrate vs BitTitan MigrationWiz vs Quest On Demand Migration, based on source environment complexity
- **Shared drive structure** -- centralized IT-managed shared drives vs departmental self-service, external member policies, storage allocation
- **Vault vs third-party archival** -- Google Vault for retention/eDiscovery vs Barracuda/Mimecast archive, particularly for organizations with complex legal hold requirements
- **Endpoint management scope** -- Google Workspace endpoint management vs dedicated MDM/UEM (Intune, Jamf, VMware Workspace ONE)
- **Coexistence duration** -- big-bang migration vs extended coexistence with split delivery, calendar interop, and GAL sync between Exchange and Gmail

## AI and GenAI Capabilities

**Gemini for Google Workspace** -- GenAI assistant integrated across Google Workspace applications. Capabilities: draft and refine emails in Gmail, generate documents in Docs, create images and slides in Slides, organize and analyze data in Sheets, summarize and take notes in Meet, and conversational assistance across all Workspace apps via the Gemini side panel. Gemini respects existing Workspace sharing permissions and data access controls.

**Gemini Licensing:** Gemini for Workspace is available as the Gemini Business or Gemini Enterprise add-on. Gemini Enterprise includes advanced features such as Gemini in Security and Compliance tools, NotebookLM Plus, and AI meetings. Both require a base Google Workspace subscription.

## See Also

- `general/email-migration.md` -- cross-platform email migration patterns, coexistence strategies, and cutover planning
- `general/identity.md` -- identity federation and SSO architecture patterns
- `providers/microsoft/m365.md` -- Microsoft 365 architecture (common migration source)
- `providers/microsoft/exchange-onprem.md` -- on-premises Exchange Server (common migration source)
- `providers/microsoft/active-directory.md` -- Active Directory integration with GCDS

## Reference Links

- [Google Workspace Admin Help](https://support.google.com/a) -- Admin Console configuration, user management, and domain setup
- [Google Workspace Security Best Practices](https://support.google.com/a/answer/7587183) -- security checklist for administrators
- [Google Cloud Directory Sync](https://support.google.com/a/answer/106368) -- GCDS setup for Active Directory synchronization
- [Google Workspace Migrate](https://support.google.com/workspacemigrate/answer/10839818) -- migration tool for Exchange, M365, and other platforms
- [GWMME Administration Guide](https://support.google.com/workspacemigrate/answer/6055847) -- Google Workspace Migration for Microsoft Exchange
- [Google Vault Documentation](https://support.google.com/vault) -- retention rules, legal holds, eDiscovery, and audit
- [Context-Aware Access](https://support.google.com/a/answer/9275380) -- device and context-based access policies
- [Google Workspace Updates Blog](https://workspaceupdates.googleblog.com/) -- feature announcements and rollout schedules
- [Gemini for Workspace](https://workspace.google.com/solutions/ai/) -- AI capabilities and licensing for Google Workspace
