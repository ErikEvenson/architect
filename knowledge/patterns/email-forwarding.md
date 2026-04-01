# Email Forwarding Services

## Scope

Email forwarding services provide custom-domain email addresses that relay inbound messages to an existing mailbox (Gmail, Outlook, etc.) without requiring a full hosted mailbox. This file covers the three major forwarding-only or forwarding-first providers -- Cloudflare Email Routing, ImprovMX, and Forward Email -- including their feature tiers, authentication implications (SPF/DKIM/DMARC/ARC), send-as configuration for replying from a custom domain, privacy trade-offs, and decision criteria for choosing forwarding over a full mailbox provider such as Google Workspace or Microsoft 365.

## Checklist

### Provider Selection

- [ ] **[Critical]** Has the team evaluated whether forwarding-only is sufficient, or whether full mailbox hosting (IMAP/POP/SMTP send) is required?
- [ ] **[Critical]** Is there a requirement to send outbound email as the custom domain (send-as), and if so, does the selected provider support SMTP relay or an alternative send path?
- [ ] **[Recommended]** Has a cost comparison been performed across providers for the required number of domains, aliases, and daily forwarding volume?
- [ ] **[Recommended]** Has the provider's privacy policy been reviewed to confirm they do not store, index, or monetize forwarded email content?
- [ ] **[Optional]** Is open-source self-hosting a requirement? If so, Forward Email is the only provider in this category that publishes its full source code.

### DNS and Authentication

- [ ] **[Critical]** Are MX records pointed to the forwarding provider's mail servers for each custom domain?
- [ ] **[Critical]** Is an SPF record published that includes the forwarding provider's sending IP ranges (and excludes providers no longer in use)?
- [ ] **[Critical]** Is DKIM signing configured for the custom domain, either through the provider's dashboard or via DNS TXT records?
- [ ] **[Critical]** Is a DMARC policy published for the custom domain (at minimum `p=none` during rollout, progressing to `p=quarantine` or `p=reject`)?
- [ ] **[Critical]** Does the forwarding provider support ARC (Authenticated Received Chain) header sealing to preserve authentication results across forwarding hops?
- [ ] **[Recommended]** Has DMARC alignment been tested end-to-end by sending test messages from external domains and verifying that forwarded messages pass SPF and DKIM checks at the destination?
- [ ] **[Recommended]** If using Cloudflare Email Routing, have the auto-provisioned MX, SPF, and DKIM records been verified in the Cloudflare DNS dashboard?

### Forwarding Rules and Aliases

- [ ] **[Critical]** Is catch-all forwarding explicitly enabled or disabled, and is the decision documented (catch-all increases spam exposure but prevents missed mail)?
- [ ] **[Recommended]** Are explicit aliases preferred over catch-all to limit attack surface and allow per-alias tracking of where an address was shared?
- [ ] **[Recommended]** If using regex-based aliases (ImprovMX Premium/Pro), are the patterns tested against edge cases to avoid unintended matches?
- [ ] **[Optional]** Are webhook forwarding rules configured for any aliases that feed into automation pipelines (ImprovMX, Forward Email)?

### Send-As (Outbound from Custom Domain)

- [ ] **[Critical]** If Gmail send-as is required, has the SMTP relay been configured in Gmail settings (Settings > Accounts > Send mail as) with the provider's SMTP credentials?
- [ ] **[Critical]** Does the SMTP relay provider (ImprovMX Premium at $9/month, Forward Email paid plans) enforce DKIM signing on outbound messages so replies pass authentication?
- [ ] **[Recommended]** Has the Gmail send-as configuration been tested by sending a message to an external recipient and verifying DKIM and SPF pass in the received headers?
- [ ] **[Recommended]** If using Cloudflare Email Routing (which has no SMTP relay), has an alternative outbound path been identified (e.g., Amazon SES, Mailgun, or a paid forwarding provider's SMTP)?
- [ ] **[Optional]** For Apple Mail or Thunderbird users, has the SMTP account been added to the mail client's outgoing server list?

### Cloudflare Email Routing (Specific)

- [ ] **[Critical]** Is the domain using Cloudflare as the authoritative DNS provider (required for Email Routing)?
- [ ] **[Critical]** Is it understood that Cloudflare Email Routing is forwarding-only with no outbound SMTP capability ("Cloudflare does not process outbound email, and does not have an SMTP server")?
- [ ] **[Recommended]** Are Email Workers evaluated for advanced routing logic (conditional forwarding, blocklists, Slack notifications, auto-replies)?
- [ ] **[Recommended]** Is the 25 MB message size limit acceptable for the expected email traffic?
- [ ] **[Optional]** Are Email Workers used to integrate with other Cloudflare services (KV, R2, Queues) for email-triggered workflows?

### ImprovMX (Specific)

- [ ] **[Critical]** Is the selected tier sufficient for the required daily forwarding volume (Free: 500/day, Premium: 5,000/day, Pro: 15,000/day)?
- [ ] **[Critical]** If SMTP send-as is needed, is the plan at Premium ($9/month) or higher (Free tier has no SMTP relay)?
- [ ] **[Recommended]** Are alias limits per domain acceptable (Free: 25, Premium: 100, Pro: 200)?
- [ ] **[Recommended]** Is the API used for programmatic alias management in multi-domain setups?
- [ ] **[Optional]** Are webhook forwarding rules used to pipe specific aliases into external systems?

### Forward Email (Specific)

- [ ] **[Critical]** If IMAP/POP mailbox access is required, is a paid plan selected ($3/month or higher for 10 GB encrypted storage per alias)?
- [ ] **[Recommended]** Has the quantum-resistant encryption (ChaCha20-Poly1305) been evaluated against organizational security requirements?
- [ ] **[Recommended]** Is MTA-STS configured for the custom domain to enforce TLS on inbound connections?
- [ ] **[Optional]** Is the self-hosted deployment option evaluated for organizations that require full control over the email processing pipeline?

### Privacy and Compliance

- [ ] **[Critical]** Has the organization confirmed that the forwarding provider's data processing location meets data residency requirements?
- [ ] **[Recommended]** Is logging retention configured appropriately (ImprovMX Free: 7 days, Premium/Pro: up to 180 days)?
- [ ] **[Recommended]** For GDPR-regulated organizations, has a Data Processing Agreement (DPA) been obtained from the forwarding provider?
- [ ] **[Optional]** Has the provider's SOC 2 or equivalent audit posture been reviewed?

### Monitoring and Operations

- [ ] **[Recommended]** Are forwarding delivery rates monitored via the provider's analytics dashboard (Cloudflare, ImprovMX logs, Forward Email logs)?
- [ ] **[Recommended]** Are bounce-back and drop notifications reviewed periodically to detect forwarding failures?
- [ ] **[Optional]** Are alerts configured for forwarding quota exhaustion (ImprovMX daily limits)?

## Why This Matters

Email forwarding services offer a low-cost way to use professional custom-domain addresses without the operational overhead or per-user licensing of a full mailbox provider. However, forwarding introduces authentication complexity: when a message is forwarded, the original sender's SPF alignment breaks because the forwarding server's IP is not in the sender's SPF record. Without proper ARC header sealing and DKIM pass-through, legitimate messages can be flagged as spam or rejected by the destination mailbox. Choosing the wrong tier or provider can also leave an organization without outbound send-as capability, forcing workarounds that confuse recipients or break reply chains. Understanding the trade-offs between free forwarding-only services and paid providers with SMTP relay is essential to avoid deliverability failures and a poor sender reputation.

## Common Decisions (ADR Triggers)

- **Forwarding-only vs full mailbox provider** -- forwarding services cost $0-$9/month per domain vs $6-$12/month per user for Google Workspace or Microsoft 365; driven by whether users need shared calendars, contacts, or a dedicated inbox
- **Cloudflare Email Routing vs ImprovMX vs Forward Email** -- Cloudflare is free but forwarding-only with no SMTP relay and requires Cloudflare DNS; ImprovMX adds SMTP relay at $9/month; Forward Email adds IMAP/POP storage at $3/month and is fully open source
- **Catch-all vs explicit aliases** -- catch-all ensures no missed mail but increases spam exposure and prevents per-alias tracking; explicit aliases provide granular control and disposability
- **SMTP relay provider for send-as** -- ImprovMX Premium, Forward Email paid, Amazon SES, or Mailgun; driven by volume, cost, and whether the forwarding provider's built-in SMTP is sufficient
- **ARC sealing strategy** -- whether the forwarding provider seals ARC headers to preserve authentication across hops; critical for domains with `p=reject` DMARC policies
- **Email Workers for programmable routing** -- Cloudflare-specific decision to use Workers for conditional forwarding, auto-replies, or integration with other Cloudflare services vs simple static rules
- **Open-source self-hosting vs managed service** -- Forward Email can be self-hosted for full control; driven by compliance, data sovereignty, or air-gapped environment requirements
- **Single provider vs split inbound/outbound** -- using Cloudflare for inbound forwarding but a separate SMTP provider (SES, Mailgun) for outbound send-as; adds DNS complexity but avoids vendor lock-in

## Reference Architectures

- [Cloudflare Email Routing Documentation](https://developers.cloudflare.com/email-routing/) -- setup, DNS configuration, Email Workers, and analytics
- [Cloudflare Email Routing Product Page](https://www.cloudflare.com/products/email-routing/) -- feature overview and privacy guarantees
- [Cloudflare Email Workers](https://developers.cloudflare.com/email-routing/email-workers/) -- programmable email processing with Workers runtime
- [ImprovMX](https://improvmx.com/) -- email forwarding with SMTP relay, regex aliases, and webhook support
- [ImprovMX Pricing](https://improvmx.com/pricing/) -- tier comparison (Free, Premium $9/month, Pro $24/month)
- [Forward Email](https://forwardemail.net/) -- open-source email forwarding with optional IMAP/POP/SMTP hosting
- [Forward Email GitHub](https://github.com/forwardemail) -- source code for the entire platform
- [Google: Send mail from a different address](https://support.google.com/mail/answer/22370) -- Gmail send-as configuration for use with SMTP relay providers
- [RFC 8617: ARC Protocol](https://datatracker.ietf.org/doc/html/rfc8617) -- Authenticated Received Chain specification for preserving authentication across forwarding
- [DMARC.org FAQ on Forwarding](https://dmarc.org/wiki/FAQ#Why_is_DMARC_potentially_dangerous_for_mailing_lists_and_forwarding_services.3F) -- DMARC alignment issues with email forwarding

---

## See Also

- `general/email-migration.md` -- email platform migration patterns, coexistence, MX cutover, and rollback planning
- `providers/aws/workmail.md` -- AWS managed email service (end-of-support March 2027)
- `providers/cloudflare/cdn-dns.md` -- Cloudflare DNS and CDN configuration (required for Email Routing)
- `providers/cloudflare/workers.md` -- Cloudflare Workers platform (used by Email Workers)
- `providers/google/workspace.md` -- Google Workspace as a full mailbox alternative
- `providers/microsoft/m365.md` -- Microsoft 365 as a full mailbox alternative
- `providers/zoho/mail.md` -- Zoho Mail as a budget full mailbox alternative
- `providers/zoom/mail.md` -- Zoom Mail as a full mailbox alternative
- `general/security.md` -- general security practices including email authentication
