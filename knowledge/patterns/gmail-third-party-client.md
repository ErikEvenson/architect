# Gmail as Third-Party Email Client

## Scope

Using Gmail (personal or Google Workspace) as a unified client for reading and sending email from third-party mailbox providers such as Zoho Mail, Amazon WorkMail, Fastmail, and others. Covers the "Check mail from other accounts" feature (IMAP/POP polling for inbound mail), the "Send mail as" feature (SMTP relay for outbound mail), authentication requirements including 2FA and app-specific passwords on both the Gmail side and the third-party provider side, SPF/DKIM/DMARC alignment implications for each sending approach, polling latency trade-offs, and common failure modes. This pattern applies to individuals and small teams consolidating multiple mailboxes into Gmail without migrating to Google Workspace as a primary mail platform.

## Checklist

### Inbound Mail (Check Mail from Other Accounts)

- [ ] **[Critical]** Is the third-party provider's IMAP or POP server address, port, and encryption method documented (e.g., `imap.zoho.com:993/SSL`, `imap.mail.us-east-1.awsapps.com:993/SSL`, `imap.fastmail.com:993/SSL`)?
- [ ] **[Critical]** Are credentials for the third-party provider configured -- either the account password or an app-specific password if the provider enforces 2FA?
- [ ] **[Critical]** Is the polling latency acceptable for the use case? Gmail's "Check mail from other accounts" polls on an interval (typically 1-60 minutes depending on volume), not in real-time via IMAP IDLE.
- [ ] **[Recommended]** Has Gmailify been evaluated as an alternative to POP-based polling? Gmailify provides tighter integration (labels, spam filtering, search) for supported providers but does not support all third-party services.
- [ ] **[Recommended]** Is POP vs IMAP behavior understood? Gmail's "Check mail from other accounts" fetches via POP by default for some configurations; IMAP-based linking (Gmailify) is only available for specific providers (Yahoo, Outlook/Hotmail, AOL).
- [ ] **[Recommended]** Is the "leave a copy on the server" option configured correctly to avoid data loss or duplication when accessing the same mailbox from multiple clients?
- [ ] **[Optional]** Are Gmail labels or filters configured to automatically categorize incoming mail from different third-party accounts?
- [ ] **[Optional]** Has the maximum number of external accounts been verified? Gmail allows up to 5 POP accounts via "Check mail from other accounts."

### Outbound Mail (Send Mail As)

- [ ] **[Critical]** Has the sending approach been decided: send through Gmail's SMTP servers or send through the third-party provider's SMTP servers?
- [ ] **[Critical]** If sending via the third-party provider's SMTP, are the SMTP server, port, and encryption settings documented (e.g., `smtp.zoho.com:465/SSL`, `smtp.mail.us-east-1.awsapps.com:465/SSL`, `smtp.fastmail.com:465/SSL`)?
- [ ] **[Critical]** If sending via the third-party provider's SMTP, are valid SMTP credentials (username + password or app-specific password) configured in Gmail's "Send mail as" settings?
- [ ] **[Critical]** Are SPF/DKIM alignment implications understood for the chosen sending approach (see "Sending Approach Comparison" below)?
- [ ] **[Recommended]** Has the Gmail verification email been completed? Gmail sends a confirmation code to the third-party address to prove ownership before enabling "Send mail as."
- [ ] **[Recommended]** Is the "Reply from the same address the message was sent to" option enabled in Gmail settings to prevent accidentally replying from the wrong address?
- [ ] **[Optional]** Has a default sending address been configured if the third-party address should be the primary identity?

### Sending Approach Comparison

- [ ] **[Critical]** **Via Gmail SMTP (simpler setup):** Gmail sends on behalf of the third-party address using Google's SMTP infrastructure. SPF and DKIM will reflect Google's domain (`_spf.google.com`), not the custom domain. The `Return-Path` header will show the Gmail address. DMARC alignment will fail for the custom domain unless the domain's SPF record includes Google's SPF and DKIM is configured for the custom domain in Google Workspace (not available for personal Gmail). This approach is acceptable for casual use but degrades deliverability for custom domains with strict DMARC policies (`p=reject` or `p=quarantine`).
- [ ] **[Critical]** **Via third-party SMTP (proper authentication):** Gmail connects to the provider's SMTP server and sends through their infrastructure. SPF, DKIM, and `Return-Path` all align with the custom domain, preserving DMARC compliance. Requires valid SMTP credentials and the provider must allow authenticated relay. This is the recommended approach for any domain with DMARC enforcement or where deliverability matters.
- [ ] **[Recommended]** If the third-party domain has a DMARC policy of `p=reject` or `p=quarantine`, sending via Gmail SMTP will cause delivery failures to recipients whose providers enforce DMARC. Use the third-party SMTP approach instead.

### Authentication and Security

- [ ] **[Critical]** If the Gmail account has 2FA enabled, does the third-party application or configuration require a Google app-specific password? (Note: "Check mail from other accounts" and "Send mail as" are configured within Gmail's own UI, so they do not require a Google app password. However, if the third-party provider requires IMAP/SMTP access and enforces 2FA, an app-specific password from that provider is needed.)
- [ ] **[Critical]** If the third-party provider enforces 2FA (e.g., Zoho, Fastmail), has an app-specific password been generated on the provider side for use in Gmail's configuration?
- [ ] **[Recommended]** Are app-specific passwords stored securely and documented for rotation purposes? App passwords bypass 2FA and should be tracked as credentials.
- [ ] **[Recommended]** Has "suspicious login" or "unusual activity" blocking been anticipated? Some providers (especially Zoho and WorkMail) may block Gmail's polling connections from Google's IP ranges as suspicious until explicitly allowed.
- [ ] **[Optional]** Is there a process for rotating app-specific passwords periodically, especially when team members change?

### DNS and Deliverability

- [ ] **[Critical]** If sending via Gmail SMTP for a custom domain, does the domain's SPF record include `include:_spf.google.com`? Without this, SPF checks will fail for mail sent through Gmail's servers.
- [ ] **[Critical]** If sending via the third-party provider's SMTP, does the domain's SPF record include the provider's SPF mechanism (e.g., `include:zoho.com`, `include:amazonses.com`, `include:messagingengine.com`)?
- [ ] **[Recommended]** Is DKIM signing configured at the third-party provider for the custom domain? DKIM alignment is the most reliable path to DMARC compliance regardless of sending approach.
- [ ] **[Recommended]** Is there a DMARC record for the custom domain, and has the chosen sending approach been validated against it?
- [ ] **[Optional]** Is DMARC reporting (`rua` tag) enabled to monitor authentication pass/fail rates after configuration?

### Personal Gmail vs Google Workspace

- [ ] **[Recommended]** Is it understood that personal Gmail accounts cannot configure DKIM signing for custom domains? Only Google Workspace allows DKIM key generation for domains the organization owns.
- [ ] **[Recommended]** Is it understood that Google Workspace accounts have additional "Send mail as" options, including domain-level aliases that do not require SMTP configuration?
- [ ] **[Optional]** For organizations already on Google Workspace, has direct domain hosting been evaluated as an alternative to the third-party client pattern? Workspace can host the domain natively, eliminating the need for IMAP polling and SMTP relay.

### Common Third-Party Provider Settings

- [ ] **[Recommended]** Are the correct IMAP/SMTP settings documented for the specific provider?
    - **Zoho Mail:** IMAP `imap.zoho.com:993/SSL`, SMTP `smtp.zoho.com:465/SSL` -- requires app-specific password when 2FA is enabled; must enable IMAP access in Zoho settings
    - **Amazon WorkMail:** IMAP `imap.mail.<region>.awsapps.com:993/SSL`, SMTP `smtp.mail.<region>.awsapps.com:465/SSL` -- uses WorkMail credentials; note WorkMail end-of-support March 2027
    - **Fastmail:** IMAP `imap.fastmail.com:993/SSL`, SMTP `smtp.fastmail.com:465/SSL` -- requires app-specific password; supports JMAP as alternative
    - **Microsoft 365 / Outlook.com:** IMAP `outlook.office365.com:993/SSL`, SMTP `smtp.office365.com:587/STARTTLS` -- may require OAuth2 or app password depending on tenant configuration; Microsoft has deprecated basic auth for Exchange Online
    - **Yahoo Mail:** IMAP `imap.mail.yahoo.com:993/SSL`, SMTP `smtp.mail.yahoo.com:465/SSL` -- requires app-specific password; Gmailify supported as alternative
    - **Proton Mail:** Does not support standard IMAP/SMTP without the Proton Mail Bridge application running locally; not directly compatible with Gmail's "Check mail from other accounts"

### Limitations and When This Pattern Breaks Down

- [ ] **[Recommended]** Is the account count within Gmail's limit of 5 external POP accounts? Organizations with many mailboxes should consider domain-level migration instead.
- [ ] **[Recommended]** Is polling latency acceptable? For time-sensitive workflows (support ticketing, incident response), the multi-minute polling delay may be unacceptable. Consider direct IMAP client access or provider-side forwarding as alternatives.
- [ ] **[Recommended]** Are mobile clients considered? Gmail's mobile app will show consolidated mail, but push notifications depend on Gmail's polling schedule, not the third-party provider's real-time delivery.
- [ ] **[Optional]** Has calendar and contacts integration been considered? This pattern only consolidates email; calendar (CalDAV) and contacts (CardDAV) from the third-party provider are not integrated through Gmail's mail features.
- [ ] **[Optional]** Has the impact of Google's periodic deprecation of "less secure app" access been considered? Google has progressively restricted third-party app access; configurations relying on basic passwords may break during policy changes.

## Why This Matters

Using Gmail as a third-party client is a common pattern for individuals and small teams who want a single interface for multiple mailboxes without fully migrating to Google Workspace. However, the choice between sending via Gmail's SMTP and the provider's SMTP has significant deliverability consequences -- sending through Gmail SMTP for a custom domain with DMARC enforcement will cause delivery failures that are difficult to diagnose. Polling latency means inbound mail is not real-time, which creates operational risk for time-sensitive workflows. App-specific password management introduces credential sprawl that must be tracked. Understanding these trade-offs prevents silent email delivery failures, missed messages, and authentication lockouts that are difficult to troubleshoot after the fact.

## Common Decisions (ADR Triggers)

- **Send via Gmail SMTP vs provider SMTP** -- simplicity and no provider SMTP dependency vs proper SPF/DKIM/DMARC alignment; the DMARC policy on the custom domain is the deciding factor
- **POP polling vs forwarding** -- Gmail's built-in polling vs configuring server-side forwarding at the third-party provider to push mail to Gmail; forwarding is faster but creates two copies and complicates reply-from-address behavior
- **Gmail as client vs full migration to Workspace** -- consolidation without platform change vs adopting Google Workspace as the primary mail platform; driven by cost, team size, and need for native calendar/contacts integration
- **App-specific passwords vs OAuth** -- not all providers support OAuth for IMAP/SMTP; when app passwords are the only option, credential rotation and storage processes must be defined
- **Single consolidated inbox vs per-account labels** -- all external mail in the primary inbox vs automatic label/filter separation; affects triage workflow and notification behavior
- **Polling interval tolerance vs real-time requirement** -- if sub-minute delivery is required, this pattern is not suitable; alternatives include direct IMAP clients (Thunderbird, Apple Mail with IMAP IDLE) or provider-side forwarding rules

## Reference Architectures

- [Gmail Help: Check email from other accounts](https://support.google.com/mail/answer/21289) -- configuring POP-based mail fetching and Gmailify
- [Gmail Help: Send emails from a different address or alias](https://support.google.com/mail/answer/22370) -- configuring "Send mail as" with SMTP settings
- [Google Help: Sign in with app passwords](https://support.google.com/accounts/answer/185833) -- creating and managing app-specific passwords for 2FA-enabled accounts
- [Google Workspace Admin: Set up DKIM](https://support.google.com/a/answer/174124) -- DKIM configuration for Google Workspace domains
- [Google Workspace Admin: SPF record](https://support.google.com/a/answer/33786) -- SPF configuration for domains sending through Google
- [DMARC.org Overview](https://dmarc.org/overview/) -- understanding DMARC alignment and policy enforcement

---

## See Also

- `general/email-migration.md` -- email platform migration patterns, coexistence, MX cutover, and rollback planning
- `providers/aws/workmail.md` -- Amazon WorkMail configuration, including IMAP/SMTP settings and end-of-support timeline
- `providers/zoho/mail.md` -- Zoho Mail configuration, app passwords, and IMAP/SMTP access
- `providers/google/workspace.md` -- Google Workspace as a primary email platform, including native DKIM/SPF management
- `providers/microsoft/m365.md` -- Microsoft 365 email configuration, OAuth requirements, and basic auth deprecation
- `general/security.md` -- credential management and authentication patterns
