# Amazon WorkMail

## Scope

AWS managed business email and calendaring service. Covers migration from on-premises Exchange or Google Workspace, directory integration, mobile device policies, encryption with KMS, journaling and eDiscovery, SES integration for mail routing, and end-of-support planning (March 31, 2027).

> **End of Support Notice:** AWS will end support for Amazon WorkMail on **March 31, 2027**. After this date, the WorkMail console and all WorkMail resources will no longer be available. Any new adoption must include a migration-off plan. Existing deployments should begin planning their exit strategy now.

## Checklist

### End-of-Support Planning

- [ ] **[Critical]** Is there a documented migration-off plan with a target completion date before March 31, 2027?
- [ ] **[Critical]** Has a replacement platform been selected (Microsoft 365, Google Workspace, self-hosted Exchange, etc.) and validated against organizational requirements?
- [ ] **[Recommended]** Are mailbox export procedures tested, including calendar events, contacts, and shared resources?
- [ ] **[Recommended]** Is there a communication plan for end users about the platform transition?

### Directory and Identity

- [ ] **[Critical]** Is the WorkMail organization linked to the correct directory type (AWS Simple AD, AWS Managed AD, or AD Connector to on-premises AD)?
- [ ] **[Critical]** If using AD Connector, is the VPN or Direct Connect link to on-premises AD reliable and monitored for authentication availability?
- [ ] **[Recommended]** Are only required users enabled for WorkMail (not the entire directory)?
- [ ] **[Recommended]** Is there a documented process for user provisioning and deprovisioning that stays in sync with the corporate directory?

### Encryption and Data Protection

- [ ] **[Critical]** Is the WorkMail organization configured with a customer-managed KMS key rather than the AWS-managed default key?
- [ ] **[Critical]** Is the KMS key policy scoped to only the WorkMail service and authorized administrators?
- [ ] **[Recommended]** Is the data residency region selected to meet compliance and data sovereignty requirements?
- [ ] **[Recommended]** Are KMS key rotation policies enabled?

### Mail Flow and SES Integration

- [ ] **[Critical]** Are MX records correctly configured for the custom domain, pointing to the WorkMail inbound endpoint?
- [ ] **[Critical]** Are SPF, DKIM, and DMARC records configured for the custom domain to prevent spoofing and improve deliverability?
- [ ] **[Recommended]** Are email flow rules configured for required routing scenarios (e.g., compliance scanning, external gateway integration)?
- [ ] **[Recommended]** Is outbound email volume monitored through SES to detect anomalies or compromised accounts?
- [ ] **[Optional]** Are SES sending limits reviewed and increased if the organization sends bulk notifications through WorkMail addresses?

### Mobile Device Management

- [ ] **[Critical]** Is a mobile device access policy configured that enforces device encryption and password requirements?
- [ ] **[Recommended]** Is remote wipe capability tested and documented in the incident response runbook?
- [ ] **[Recommended]** Are device access rules configured to allow only approved device types and OS versions?
- [ ] **[Optional]** Is there a BYOD policy that aligns WorkMail mobile device policies with corporate security standards?

### Journaling, Retention, and eDiscovery

- [ ] **[Critical]** If subject to regulatory retention requirements, is journaling enabled with a third-party archiving solution?
- [ ] **[Recommended]** Is the journaling destination mailbox or service monitored for availability and storage capacity?
- [ ] **[Recommended]** Are retention policies documented and aligned with legal hold and records management requirements?
- [ ] **[Optional]** Has the eDiscovery workflow been tested end-to-end with the third-party archiving provider?

### Migration (Inbound)

- [ ] **[Recommended]** Has a migration tool been selected (audriga, Transend Migrator, or manual IMAP migration)?
- [ ] **[Recommended]** Is a pilot migration planned with a subset of users before full rollout?
- [ ] **[Recommended]** Are shared mailboxes, distribution groups, and meeting room resources included in the migration plan?
- [ ] **[Optional]** Has Amazon-subsidized migration support been requested for qualified projects?

### Monitoring and Administration

- [ ] **[Recommended]** Is CloudTrail enabled and monitored for WorkMail API calls (CreateUser, DeleteUser, ResetPassword)?
- [ ] **[Recommended]** Are administrative actions performed through the SDK or CLI rather than manual console operations, to support auditability and repeatability?
- [ ] **[Optional]** Are Exchange Web Services (EWS) push notifications used for integration with internal tools that need mailbox event awareness?

### Cost

- [ ] **[Recommended]** Is user count reviewed periodically to deactivate unused mailboxes (pricing is per active user per month)?
- [ ] **[Recommended]** Are mailbox sizes monitored against the 50 GB default limit to avoid unexpected storage issues?

## Why This Matters

Amazon WorkMail provides a managed email service that avoids the operational burden of running Exchange on-premises. However, the announced end of support (March 2027) means any new adoption carries migration risk, and existing deployments must plan an exit. Directory integration failures cause authentication outages for all users. Missing email authentication records (SPF/DKIM/DMARC) lead to deliverability problems and phishing exposure. Unmanaged mobile device policies allow data leakage on lost or compromised devices. Journaling gaps create compliance violations for regulated industries.

## Common Decisions (ADR Triggers)

- **WorkMail vs Microsoft 365 vs Google Workspace** -- managed AWS-native simplicity vs richer collaboration suite; end-of-support timeline makes this decision urgent for new projects
- **Directory strategy** -- Simple AD (standalone) vs Managed AD (full AD features) vs AD Connector (extend on-premises AD); impacts authentication, group policy, and operational complexity
- **KMS key ownership** -- AWS-managed key vs customer-managed key; affects cross-account access, audit requirements, and key rotation control
- **Journaling architecture** -- direct journaling to S3 via third-party vs dedicated archiving service (Barracuda, Mimecast, Proofpoint); driven by eDiscovery and compliance requirements
- **Mail flow routing** -- direct WorkMail delivery vs external gateway (e.g., Mimecast, Proofpoint) for advanced threat protection and DLP scanning
- **Migration tooling** -- audriga (cloud-based, no software install) vs Transend Migrator (batch, on-premises agent) vs manual IMAP migration for small deployments
- **Migration-off strategy** -- given end-of-support (March 31, 2027), selection of target platform and timeline; AWS-recommended destinations are Kopano Cloud, Zoho Mail, and Zoom Mail; other common targets include Microsoft 365, Google Workspace, and self-hosted Exchange

## Reference Architectures

- [Amazon WorkMail Administrator Guide](https://docs.aws.amazon.com/workmail/latest/adminguide/what_is.html) -- setup, directory integration, and domain configuration
- [Amazon WorkMail API Reference](https://docs.aws.amazon.com/workmail/latest/APIReference/Welcome.html) -- programmatic user and resource management
- [AWS SES Developer Guide](https://docs.aws.amazon.com/ses/latest/dg/Welcome.html) -- outbound email configuration and deliverability best practices
- [AWS KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html) -- encryption key management for WorkMail data at rest
- [Amazon WorkMail End of Support](https://docs.aws.amazon.com/workmail/latest/adminguide/workmail-end-of-support.html) -- EOL timeline, AWS-recommended migration destinations (Kopano Cloud, Zoho Mail, Zoom Mail), and mailbox export guidance
- [Amazon WorkMail Mailbox Export](https://docs.aws.amazon.com/workmail/latest/adminguide/mail-export.html) -- exporting mailbox content before service end

---

## See Also

- `providers/aws/security.md` -- IAM policies and security best practices for AWS services
- `providers/aws/secrets-manager.md` -- managing credentials for service integrations
- `compliance/hipaa.md` -- HIPAA compliance considerations including email encryption
- `general/email-migration.md` -- email platform migration patterns, coexistence, MX cutover, and rollback planning
- `general/data-migration-tools.md` -- general migration planning patterns
