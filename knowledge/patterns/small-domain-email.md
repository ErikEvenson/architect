# Small/Personal Domain Email Architecture

## Scope

Covers email architecture decisions for small domains (1-5 users), including personal vanity domains, family domains, freelancer domains, and very small business domains. Addresses the decision framework for selecting between forwarding services, free-tier mailboxes, budget mailbox providers, and full business email platforms. Includes cost comparison across provider tiers, feature requirements analysis (IMAP/POP, SMTP send-as, storage, mobile access, calendar/contacts, catch-all), DNS and email authentication configuration (SPF, DKIM, DMARC) for small domains, common delivery architectures (forwarding to personal Gmail, IMAP polling, native web clients, dedicated mail apps), registrar-bundled email evaluation, migration patterns between small-scale providers, privacy and data ownership considerations, and triggers for upgrading from personal to business email infrastructure.

## Checklist

### Decision Framework

- [ ] **[Critical]** Is the primary use case defined -- receive-only (forwarding), send-and-receive with personal client, or full mailbox with native web UI?
- [ ] **[Critical]** Is the required user count established (1 user, family/household 2-5 users, or small team 3-5 users) and is there a growth trajectory that may exceed 5 users within 2 years?
- [ ] **[Critical]** Has the decision between forwarding-only, free-tier mailbox, budget mailbox, and full business email been made based on feature requirements and budget?
- [ ] **[Recommended]** Are compliance or professional requirements evaluated -- do clients, partners, or regulators expect business-grade email (audit trails, retention, encryption)?
- [ ] **[Recommended]** Is the total cost of ownership calculated including domain registration, DNS hosting, and email service fees?
- [ ] **[Optional]** Has vendor lock-in risk been evaluated -- can mailbox data be exported via IMAP or standard formats (MBOX, PST) if the provider changes pricing or shuts down?

### Cost Comparison (1-5 Users)

- [ ] **[Critical]** Have free options been evaluated for viability?
    - Zoho Mail Free: up to 5 users, 5 GB/user, web-only access (no IMAP/POP/ActiveSync), 25 MB attachment limit
    - Cloudflare Email Routing: forwarding-only (no mailbox), unlimited aliases, free with Cloudflare DNS
- [ ] **[Critical]** Have budget options been evaluated if free tiers are insufficient?
    - Zoho Mail Lite: ~$1/user/month (annual), 5 GB storage, IMAP/POP/ActiveSync enabled
    - ImprovMX: $10/month flat (unlimited aliases, SMTP send-as, forwarding), no mailbox storage
    - Kopano Cloud: EUR 2.99/user/month, 5 GB storage, full groupware (calendar, contacts, tasks)
- [ ] **[Recommended]** Have standard business options been evaluated for comparison?
    - Google Workspace Business Starter: $7/user/month, 30 GB storage, full Gmail + Workspace suite
    - Microsoft 365 Business Basic: $6/user/month, 50 GB mailbox, Exchange Online + Office web apps
    - Fastmail: $5/user/month (Standard), 30 GB storage, IMAP/JMAP, calendar/contacts, custom domains
- [ ] **[Recommended]** Is annual vs monthly billing considered (most providers offer 15-20% discount for annual commitment)?
- [ ] **[Optional]** Has the registrar-bundled email option been evaluated?
    - Namecheap Private Email: starts at ~$1/month per mailbox
    - Hover: email included with domain (forwarding free, full mailbox ~$20/year)
    - Porkbun: email forwarding included free with domain registration

### Feature Requirements

- [ ] **[Critical]** Is IMAP or POP access required for use with desktop or mobile email clients (Thunderbird, Apple Mail, Outlook)?
- [ ] **[Critical]** Is SMTP send-as capability required (sending email from the custom domain, not just receiving)?
- [ ] **[Recommended]** Is calendar and contacts sync required (CalDAV/CardDAV or Exchange ActiveSync)?
- [ ] **[Recommended]** Is mobile device access required via native mail apps (ActiveSync or IMAP)?
- [ ] **[Recommended]** Is catch-all or wildcard addressing needed (route all unmatched addresses to a single mailbox)?
- [ ] **[Recommended]** Is adequate storage capacity planned for expected email volume (5 GB is sufficient for light personal use, 15-30 GB for moderate use, 50 GB+ for business use)?
- [ ] **[Optional]** Are email aliases required (multiple addresses delivered to one mailbox)?
- [ ] **[Optional]** Is shared calendar or address book functionality needed for family or small team coordination?
- [ ] **[Optional]** Is an integrated web-based email client required, or is a third-party client acceptable?

### DNS and Email Authentication

- [ ] **[Critical]** Is an SPF record configured for the sending domain that includes only authorized sending sources (provider's include mechanism or IP ranges)?
- [ ] **[Critical]** Is DKIM signing configured with the email provider's published public key in DNS?
- [ ] **[Critical]** Is a DMARC record published, starting with `p=none` for monitoring and progressing to `p=quarantine` or `p=reject` after validation?
- [ ] **[Critical]** Are MX records correctly configured and pointing to the email provider's mail servers?
- [ ] **[Recommended]** If using a forwarding service, is the forwarding provider's SPF mechanism included alongside the destination provider (e.g., both Cloudflare and Gmail SPF includes)?
- [ ] **[Recommended]** Is DNS hosted on a reliable provider with low TTL support for easy migration (Cloudflare, Route 53, or registrar DNS)?
- [ ] **[Recommended]** Has email authentication been tested using a validation tool (MXToolbox, mail-tester.com, Google Postmaster Tools) to confirm SPF/DKIM/DMARC alignment?
- [ ] **[Optional]** Is a DMARC reporting address configured to receive aggregate reports (`rua` tag) for monitoring unauthorized use of the domain?

### Architecture Patterns

- [ ] **[Recommended]** Is the selected delivery architecture documented?
    - **Forwarding to personal Gmail/Outlook.com**: Cloudflare Email Routing or ImprovMX forwards inbound mail to a free personal mailbox; send-as configured in Gmail via SMTP relay or alias
    - **IMAP polling by Gmail**: Gmail fetches mail from provider's IMAP server on a schedule (5-60 minute delay); send-as configured via provider's SMTP
    - **Native web client**: use provider's own web interface (Zoho, Fastmail, Google Workspace) as primary access method
    - **Dedicated mail app**: IMAP/JMAP configured in Thunderbird, Apple Mail, Spark, or mobile native client; provider serves as backend only
- [ ] **[Recommended]** If using forwarding, is the forwarding chain tested end-to-end including SPF/DKIM alignment at the final destination?
- [ ] **[Recommended]** If using Gmail send-as with a third-party SMTP relay, is the relay authenticated and the SMTP credentials stored securely?
- [ ] **[Optional]** Is a backup delivery method configured (e.g., secondary MX or catch-all forwarding) in case the primary provider has an outage?

### Registrar-Bundled Email

- [ ] **[Recommended]** If using registrar-bundled email, are the limitations understood?
    - Pros: simple setup, single vendor for domain + email, low cost, included forwarding
    - Cons: limited storage (often 1-5 GB), minimal spam filtering, no advanced features (retention, eDiscovery), difficult migration if changing registrars, support quality varies
- [ ] **[Recommended]** Is registrar-bundled email evaluated as a temporary solution with a migration path to a dedicated provider if needs grow?
- [ ] **[Optional]** Is domain transfer flexibility preserved (email tied to registrar makes registrar transfers more complex)?

### Migration Between Small Providers

- [ ] **[Recommended]** Is the migration approach selected based on source and target provider capabilities?
    - IMAP-to-IMAP migration: use imapsync, Thunderbird copy, or provider-built migration tool
    - Export/import: MBOX export from source, import at target (supported by Fastmail, Thunderbird)
    - Forwarding coexistence: run forwarding from old provider to new during transition, then cut over MX records
- [ ] **[Recommended]** Is DNS TTL reduced to 300 seconds at least 24 hours before MX record cutover?
- [ ] **[Recommended]** Are calendar and contacts exported separately (ICS and VCF formats) and imported at the new provider?
- [ ] **[Optional]** Is a brief coexistence period planned where both old and new providers are active (forwarding from old to new) to catch straggler mail?

### Growth Triggers (When to Upgrade)

- [ ] **[Recommended]** Are upgrade triggers documented for moving from personal to business-grade email?
    - User count exceeding 5 (most free/budget tiers cap at 5 users)
    - Compliance requirements emerge (HIPAA, SOC 2, legal hold, eDiscovery)
    - Need for shared calendars, booking resources, or team collaboration features
    - SSO or directory integration required (SAML, SCIM, Active Directory)
    - Storage needs exceed budget tier limits (>5-10 GB/user)
    - Professional support SLA required (guaranteed response times)
    - Custom retention policies or audit logging needed
- [ ] **[Recommended]** Is the upgrade path evaluated before initial provider selection (choosing a provider with both personal and business tiers simplifies future migration)?

### Privacy and Data Ownership

- [ ] **[Recommended]** Is the provider's data privacy policy reviewed -- does the provider scan email content for advertising or analytics purposes?
- [ ] **[Recommended]** Is data portability confirmed -- can all email, calendar, and contacts be exported in standard formats (MBOX/EML, ICS, VCF)?
- [ ] **[Recommended]** Is the provider's jurisdiction and data residency understood for privacy-sensitive use cases?
- [ ] **[Optional]** Has a privacy-focused provider been evaluated if data sovereignty is a concern (Fastmail in Australia, Zoho in user-selected region, Proton Mail in Switzerland)?
- [ ] **[Optional]** Is account recovery and inheritance planning considered for personal/family domains (what happens if the domain owner is incapacitated)?

### Family/Personal vs Small Business

- [ ] **[Recommended]** Is the use case clearly categorized?
    - **Family/personal domain**: vanity email for household members, low volume, cost sensitivity is primary, no compliance needs
    - **Freelancer/sole proprietor**: professional appearance, moderate volume, may need invoicing/CRM integration, basic professionalism expected
    - **Small business (2-5 employees)**: shared calendars, potential compliance needs, client-facing email, support SLA may matter
- [ ] **[Recommended]** Is the selected provider appropriate for the category (free/budget for family, budget/standard for freelancer, standard/business for small business)?

## Why This Matters

Small domain email is deceptively simple -- the decision between a free forwarding service and a paid mailbox seems trivial, but the wrong choice leads to deliverability failures, lost emails, or unnecessary cost. Domains without proper SPF, DKIM, and DMARC records -- even personal ones -- are increasingly rejected or spam-filtered by major providers (Gmail, Outlook.com, Yahoo). Forwarding architectures can break DKIM alignment and cause legitimate email to be flagged as spam. Free tiers that lack IMAP access lock users into web-only workflows, which may be acceptable initially but become frustrating as usage grows. Choosing a provider without data export capability creates lock-in risk. And for domains that start personal but grow into business use, selecting a provider with no upgrade path means a disruptive migration later. The cost difference between options is often less than $5/month per user, making the feature and reliability trade-offs more important than raw price.

## Common Decisions (ADR Triggers)

- **Forwarding vs mailbox** -- forwarding (Cloudflare Email Routing, ImprovMX) for receive-only or send-via-Gmail use cases vs dedicated mailbox (Zoho, Fastmail) for full email independence; driven by send-as requirements, DKIM alignment needs, and client access preferences
- **Free tier vs paid tier** -- Zoho Mail Free (5 users, web-only) vs Zoho Mail Lite ($1/user/month with IMAP) vs budget alternatives; driven by IMAP/mobile access requirements and storage needs
- **Consolidated vs independent email** -- forwarding to existing Gmail/Outlook.com account (single inbox) vs separate mailbox per domain (email independence); driven by workflow preference and privacy posture
- **Provider selection for 1-2 users** -- Cloudflare forwarding + Gmail send-as ($0/month) vs Zoho Free ($0/month) vs Fastmail ($5/month) vs ImprovMX ($10/month); driven by feature needs, client access, and willingness to manage SMTP relay configuration
- **Registrar-bundled vs standalone email** -- convenience of single-vendor management vs flexibility and feature richness of a dedicated email provider
- **Privacy-first vs ecosystem-integrated** -- Fastmail or Proton Mail (privacy-focused, no content scanning) vs Google Workspace or Microsoft 365 (deep ecosystem integration, content may be processed); driven by privacy requirements and existing tool dependencies
- **Calendar/contacts platform** -- separate CalDAV/CardDAV provider vs integrated email+calendar suite; driven by whether users need shared calendars or just personal scheduling
- **Growth planning** -- start minimal and migrate later vs invest in a scalable provider from day one; driven by confidence in future user count and feature requirements

## Reference Architectures

- [Cloudflare Email Routing](https://developers.cloudflare.com/email-routing/) -- free email forwarding with Cloudflare DNS, unlimited custom addresses, no mailbox storage
- [Zoho Mail Free Plan](https://www.zoho.com/mail/zohomail-pricing.html) -- up to 5 users, 5 GB/user, web-only (no IMAP/POP on free tier)
- [Fastmail Custom Domains](https://www.fastmail.com/help/receive/domains.html) -- custom domain email with JMAP/IMAP, calendar, and contacts
- [ImprovMX](https://improvmx.com/) -- email forwarding and SMTP send-as for custom domains
- [Kopano Cloud](https://kopano.com/kopano-cloud/) -- open-source groupware with email, calendar, and contacts (AWS-recommended WorkMail migration target)
- [Gmail Send Mail As](https://support.google.com/mail/answer/22370) -- configuring Gmail to send from a custom domain address via SMTP relay
- [Google Postmaster Tools](https://postmaster.google.com/) -- monitor email deliverability and domain reputation
- [MXToolbox](https://mxtoolbox.com/) -- DNS and email authentication diagnostic tools
- [DMARC.org](https://dmarc.org/) -- DMARC specification and deployment guides
- [mail-tester.com](https://www.mail-tester.com/) -- email deliverability testing for SPF/DKIM/DMARC alignment

---

## See Also

- `general/email-migration.md` -- email platform migration patterns, coexistence, MX cutover, and rollback planning
- `providers/zoho/mail.md` -- Zoho Mail architecture, pricing tiers, and migration from Amazon WorkMail
- `providers/aws/workmail.md` -- Amazon WorkMail end-of-support planning and migration-off strategy
- `providers/kopano/cloud.md` -- Kopano Cloud groupware as budget email alternative
- `providers/cloudflare/cdn-dns.md` -- Cloudflare DNS and CDN (Email Routing uses Cloudflare DNS)
- `providers/google/workspace.md` -- Google Workspace as upgrade path for growing domains
- `providers/microsoft/m365.md` -- Microsoft 365 as upgrade path for growing domains
- `compliance/gdpr.md` -- GDPR data protection considerations for email data residency
