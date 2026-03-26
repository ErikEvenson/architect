# Exchange Server (On-Premises)

## Scope

This document covers on-premises Exchange Server architecture, including Database Availability Groups (DAGs), mail flow design and transport rules, namespace planning, certificate management, hybrid configuration with Exchange Online, migration strategies (cutover, staged, hybrid, third-party tools), decommissioning on-premises Exchange after migration, and Exchange Server 2019 as the current supported version. Exchange Server Subscription Edition (SE), announced as the successor to Exchange 2019, is also covered.

## Checklist

- [ ] **[Critical]** Is the Database Availability Group (DAG) configured with appropriate number of mailbox database copies (minimum 3 for production), witness server placement, and activation preference order?
- [ ] **[Critical]** Is the namespace plan documented with split-brain DNS or distinct internal/external namespaces, including Autodiscover (autodiscover.domain.com), mail flow (mail.domain.com), and OWA/ECP endpoints?
- [ ] **[Critical]** Are TLS certificates (SAN or wildcard) provisioned from a trusted CA for all Exchange namespaces, with proper binding to IIS and SMTP services, and renewal procedures documented?
- [ ] **[Critical]** Is the mail flow design documented, including receive connectors, send connectors, transport rules, accepted domains (authoritative vs relay), and any smart host or mail gateway (Proofpoint, Mimecast) integration?
- [ ] **[Critical]** If hybrid with Exchange Online, is the Hybrid Configuration Wizard (HCW) run, OAuth configured for cross-premises free/busy and mailbox moves, and the hybrid agent or Exchange hybrid server sized and maintained?
- [ ] **[Recommended]** Is Exchange Server 2019 (or SE when available) deployed on supported Windows Server versions with latest cumulative and security updates applied within vendor-recommended timelines?
- [ ] **[Recommended]** Is the migration strategy to Exchange Online defined with batch sizing, scheduling (off-hours, weekends), user communication, Outlook profile reconfiguration, and rollback procedures?
- [ ] **[Recommended]** Are Exchange virtual directories (OWA, ECP, EWS, ActiveSync, MAPI, OAB) configured with correct internal and external URLs matching the namespace plan and load balancer configuration?
- [ ] **[Recommended]** Is the on-premises Exchange decommissioning plan documented, including retaining at least one hybrid server for recipient management (until full cloud management is available), removing DNS records, and uninstalling Exchange?
- [ ] **[Recommended]** Are anti-spam and anti-malware protections configured (Exchange Online Protection for hybrid, or third-party gateway) with quarantine policies and end-user notification?
- [ ] **[Optional]** Is Exchange Server resource sizing validated (CPU, RAM, disk IOPS per mailbox database) using the Exchange Server Role Requirements Calculator or equivalent sizing methodology?
- [ ] **[Optional]** Are public folders migrated to M365 Groups, shared mailboxes, or Exchange Online public folders, with a documented migration and decommission plan?

## Why This Matters

On-premises Exchange Server remains in production at many organizations, but the strategic direction is migration to Exchange Online. Exchange 2019 is in mainstream support, with Exchange Server SE announced as a subscription-based successor providing an on-premises option for organizations with regulatory or data sovereignty requirements. DAG misconfiguration is the leading cause of mail outage in on-premises Exchange -- insufficient database copies, incorrect witness configuration, or network partitioning can cause mailbox database failover failures. Certificate expiration is another frequent cause of service disruption, affecting Autodiscover, Outlook connectivity, and hybrid mail flow simultaneously.

Hybrid configuration is the most common migration approach for organizations with more than 150 mailboxes, enabling coexistence with Exchange Online during a phased migration. However, the hybrid server must be maintained and patched even after all mailboxes are migrated, as it serves as the management endpoint for recipient objects until Microsoft fully supports cloud-only management. Decommissioning on-premises Exchange prematurely breaks recipient management and address book synchronization. Organizations must plan the full lifecycle from hybrid setup through final decommission.

## Common Decisions (ADR Triggers)

- **Migration strategy** -- cutover (small orgs, <150 mailboxes) vs staged vs hybrid (coexistence) vs third-party tool (BitTitan, Quest) for large/complex migrations
- **Hybrid type** -- full hybrid (on-premises Exchange server with public endpoint) vs hybrid agent (no inbound firewall rules, simpler but limited)
- **Namespace strategy** -- split-brain DNS (same namespace internal/external) vs distinct namespaces, impact on certificate requirements
- **Mail routing during migration** -- MX to on-premises vs MX to Exchange Online Protection, centralized vs decentralized transport
- **Exchange decommission timing** -- retain hybrid server indefinitely vs decommission after migration (requires understanding of management dependency)
- **Exchange SE adoption** -- upgrade to Exchange SE for continued on-premises support vs accelerate migration to Exchange Online
- **Public folder strategy** -- migrate to M365 Groups vs Exchange Online public folders vs SharePoint, depends on usage patterns and user expectations
- **Certificate management** -- per-service SAN certificates vs wildcard, internal CA vs public CA, automated renewal (ACME/Let's Encrypt for external)

## See Also

- `providers/microsoft/m365.md` -- Microsoft 365 tenant and Exchange Online architecture
- `providers/microsoft/active-directory.md` -- Active Directory identity architecture
- `general/tls-certificates.md` -- TLS certificate management patterns

## Reference Links

- [Exchange Server Documentation](https://learn.microsoft.com/exchange/exchange-server) -- architecture, DAG configuration, mail flow, and namespace planning
- [Exchange Hybrid Deployments](https://learn.microsoft.com/exchange/exchange-hybrid) -- hybrid configuration wizard, migration paths, and coexistence scenarios
- [Exchange Server Build Numbers](https://learn.microsoft.com/exchange/new-features/build-numbers-and-release-dates) -- version history, cumulative updates, and security updates
