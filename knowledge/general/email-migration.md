# Email Migration

## Scope

This document covers email platform migration patterns and strategies, including migration approaches (cutover, staged, hybrid, IMAP), mailbox migration tooling (native and third-party), MX record cutover planning, coexistence and split delivery during migration, calendar and contacts migration, shared mailbox and distribution list handling, public folder migration, mail routing during transition periods, resource calendar migration, user communication and change management, DNS TTL preparation, rollback planning, and post-migration validation.

## Checklist

- [ ] **[Critical]** Is the migration approach selected (cutover, staged, hybrid, or phased) based on mailbox count, source platform, acceptable downtime window, and coexistence requirements?
- [ ] **[Critical]** Is a complete mailbox inventory documented -- including mailbox count, total size, largest mailboxes, shared mailboxes, resource mailboxes (rooms/equipment), distribution lists, mail-enabled security groups, and public folders?
- [ ] **[Critical]** Is the migration tool selected and validated with a pilot batch -- native tools (GWMME, Exchange hybrid move requests, IMAP migration) vs third-party tools (BitTitan MigrationWiz, Quest On Demand Migration, AvePoint, Binary Tree)?
- [ ] **[Critical]** Is the MX record cutover strategy documented with DNS TTL reduced to 300 seconds (5 minutes) at least 48 hours before cutover, and is the cutover sequence (MX change, autodiscover, SPF/DKIM/DMARC update) scripted and rehearsed?
- [ ] **[Critical]** Are SPF, DKIM, and DMARC records planned for the target platform, with a transition plan that avoids breaking email authentication during the coexistence period (e.g., including both source and target SPF includes)?
- [ ] **[Critical]** Is a coexistence strategy defined for the migration window -- mail routing between platforms (split delivery, forwarding, transport rules), calendar free/busy sharing (federation or third-party interop), and Global Address List (GAL) synchronization?
- [ ] **[Critical]** Is the user communication plan defined with migration schedule notifications, pre-migration instructions (Outlook profile reconfiguration, mobile device setup), day-of support plan (war room, help desk staffing), and post-migration verification steps?
- [ ] **[Recommended]** Are shared mailboxes and their delegates inventoried, with a mapping to the target platform's equivalent (shared mailbox, collaborative inbox, Google Group, M365 shared mailbox) and delegate permissions recreated?
- [ ] **[Recommended]** Are distribution lists and mail-enabled groups inventoried with membership, and is the migration strategy defined (recreate in target, migrate via tool, convert to target-native groups)?
- [ ] **[Recommended]** Is calendar migration validated -- recurring meetings, meeting invitations with external attendees, resource calendar bookings, and calendar permissions/delegates tested in the target platform?
- [ ] **[Recommended]** Is contacts migration planned -- personal contacts, organizational contacts (GAL), and shared/public contact lists mapped to the target platform's contact model?
- [ ] **[Recommended]** Are mail flow rules, transport rules, journaling rules, and compliance policies (retention, legal holds, DLP) inventoried from the source platform and recreated or mapped to equivalent target platform features?
- [ ] **[Recommended]** Is a rollback plan documented in case of migration failure -- including MX record revert procedure, re-enabling source mailboxes, and communication templates for users?
- [ ] **[Recommended]** Are mail-enabled applications and service accounts inventoried -- applications that send email via SMTP relay, scan-to-email devices (MFPs/copiers), monitoring systems, and CRM/ERP integrations that use the current mail platform?
- [ ] **[Recommended]** Is a post-migration validation checklist defined -- mail flow testing (internal and external send/receive), calendar accuracy, contacts availability, mobile device connectivity, shared mailbox access, and distribution list delivery?
- [ ] **[Recommended]** Are email client configuration changes planned -- Outlook profile updates (autodiscover changes), mobile device mail app reconfiguration, and desktop client version compatibility with the target platform?
- [ ] **[Optional]** Is email archival migration addressed -- PST files, on-premises archive mailboxes, third-party archives (Enterprise Vault, Barracuda) with a strategy to import historical mail into the target platform or maintain a separate archive?
- [ ] **[Optional]** Is public folder migration planned if the source environment uses Exchange public folders -- mapping to target equivalents (shared mailboxes, shared drives, SharePoint, Google Groups)?
- [ ] **[Optional]** Is a throttling and bandwidth plan in place for large migrations -- understanding target platform API throttling limits, scheduling large mailbox migrations during off-hours, and network bandwidth allocation?
- [ ] **[Optional]** Are email signatures and disclaimers migrated or recreated -- organizational signature templates, legal disclaimers, and transport rule-based signature injection reconfigured for the target platform?

## Why This Matters

Email migration is one of the highest-visibility infrastructure changes an organization undertakes because it directly affects every user, every day. A failed or poorly planned email migration results in lost emails, broken calendars, inaccessible shared resources, and significant productivity loss. The technical complexity is compounded by the operational challenge: users expect zero downtime, perfect data fidelity, and seamless client reconfiguration.

The migration approach selection is critical. Cutover migrations (all mailboxes moved in a single window) are simplest but only practical for small organizations (typically under 150 mailboxes). Staged migrations move users in batches over days or weeks, requiring coexistence between platforms. Hybrid configurations (Exchange hybrid, split delivery) enable extended coexistence but introduce ongoing routing complexity. Each approach has different implications for DNS changes, mail routing, calendar interoperability, and GAL synchronization.

Common failures include: MX record changes propagating unevenly (causing mail delivery to wrong platform), broken SPF/DKIM causing legitimate email to be rejected, calendar meetings losing recurrence patterns or timezone data, shared mailbox permissions not transferring, distribution lists missing members, and mail-enabled applications (MFPs, monitoring, CRM) continuing to relay through the decommissioned platform. Thorough inventory, pilot migration, and post-migration validation prevent these failures.

## Common Decisions (ADR Triggers)

- **Cutover vs staged vs hybrid migration** -- mailbox count thresholds, acceptable downtime, coexistence requirements, and organizational change tolerance
- **Native vs third-party migration tools** -- cost, source/target platform combinations, feature requirements (delta sync, scheduling, reporting), and support needs
- **Coexistence duration** -- minimal cutover weekend vs extended multi-week coexistence with full calendar interop and GAL sync
- **Mail routing during coexistence** -- split delivery (MX to target, forwarding for unmigrated) vs centralized routing through source or gateway
- **Archive migration scope** -- migrate all historical email vs only recent (e.g., last 2 years) vs maintain legacy archive read-only
- **Public folder strategy** -- migrate to shared mailboxes, shared drives, or SharePoint/Google Groups vs decommission with export
- **Third-party email security retention** -- keep existing Proofpoint/Mimecast/Barracuda gateway vs switch to target platform native security
- **Client reconfiguration approach** -- manual user instructions vs scripted Outlook profile reconfiguration vs new profile deployment via MDM/GPO

## See Also

- `providers/google/workspace.md` -- Google Workspace architecture and Gmail migration specifics
- `providers/microsoft/m365.md` -- Microsoft 365 tenant architecture and Exchange Online migration
- `providers/microsoft/exchange-onprem.md` -- on-premises Exchange Server as migration source
- `general/workload-migration.md` -- general workload migration patterns and planning
- `general/change-management.md` -- organizational change management for IT migrations
- `patterns/migration-cutover.md` -- migration cutover patterns and scheduling

## Reference Links

- [Microsoft Exchange Migration Methods](https://learn.microsoft.com/exchange/mailbox-migration/mailbox-migration) -- cutover, staged, hybrid, and IMAP migration to Exchange Online
- [Google Workspace Migration Tools](https://support.google.com/a/answer/6251069) -- overview of migration paths into Google Workspace
- [BitTitan MigrationWiz](https://www.bittitan.com/migrationwiz/) -- third-party SaaS migration tool for mailbox, document, and archive migration
- [Quest On Demand Migration](https://www.quest.com/products/on-demand-migration/) -- tenant-to-tenant and cross-platform migration tooling
- [Exchange Hybrid Deployment](https://learn.microsoft.com/exchange/exchange-hybrid) -- Exchange hybrid configuration for extended coexistence
- [DMARC.org](https://dmarc.org/) -- DMARC specification and deployment guides for email authentication
- [MX Toolbox](https://mxtoolbox.com/) -- DNS and mail flow diagnostic tools for migration validation
