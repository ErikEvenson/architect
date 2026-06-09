# Backup Lifecycle Synchronization

## Scope

This file covers the **cross-system process that synchronizes a source system's resource lifecycle with a backup tool's data lifecycle** -- the integration glue that ensures backups are reclaimed (or deliberately retained) when the resource they protect is deleted. It is provider-agnostic: the "source system" is any platform that creates and destroys protected resources (an OpenStack project deleting a VM, a vCenter deleting a guest, a cloud account terminating an instance, a database platform dropping an instance), and the "backup tool" is any data-protection product (Commvault, Cohesity, Rubrik, Veeam, Zerto, cloud-native snapshot services). The pattern resolves a three-way tension between cost governance, the GDPR Article 17 right-to-erasure, and legal hold.

This file is the **end-to-end pattern**. It does not duplicate the failure mode (orphaned snapshots/backups accumulating -- see `failures/data.md`), the regulatory rule it must satisfy (`compliance/gdpr.md`), the inventory-side disposition of orphans (`general/inventory-analysis.md`), the CMDB reconciliation mechanics (`providers/servicenow/cmdb.md`), or the per-vendor delete/retention mechanics that implement it (`providers/commvault/backup.md`, `providers/cohesity/backup.md`, `providers/rubrik/backup.md`, `providers/veeam/backup.md`). It is the layer that ties those together.

## Overview

A source system and a backup tool each maintain their own lifecycle for the same logical object. The source system knows when a VM is created, renamed, and deleted. The backup tool knows when that VM was last protected, how many recovery points exist, and when they age out. Nothing inherently connects the two: deleting the VM does not delete its backups, and deleting the backups does not stop the source system from re-presenting the VM. The space between these two lifecycles is where orphaned backups accumulate -- driving storage cost, retention-policy drift, and right-to-erasure exposure -- and, in the opposite failure, where a backup is deleted while a legal hold still requires it.

The pattern has three moving parts: a **discovery/diff mechanism** that detects when a protected resource no longer exists at the source, a set of **governance gates** that decide whether and when reclamation is allowed, and an **action path** that executes the soft or hard reclamation against the backup tool. The hard design choices are how diff is detected (event-driven vs reconciliation vs hybrid), what stable join key correlates the two systems, and which gates must pass before a backup is destroyed.

## Checklist

- [ ] **[Critical]** Is the **diff mechanism** chosen deliberately -- reconciliation-loop (periodically list source resources, list backup-tool protected objects, compute the set difference of "protected but no longer at source") vs event-driven (consume a source-system deletion event and act on it) vs the **hybrid** (events flag a candidate immediately, the reconciliation loop is the authority that enforces) -- rather than defaulting to naive event-driven delete, which loses any event dropped during an outage and has no backstop?
- [ ] **[Critical]** Is the **join key** a stable immutable identifier (source-system UUID / instance-id / MoRef), never a mutable display name or IP? A name-based or IP-based join silently mismatches after a rename, re-IP, or name reuse, and a name-reuse collision can cause the new resource's backups to be reclaimed against the old resource's deletion -- a data-loss bug, not just a cost bug.
- [ ] **[Critical]** Is there a **grace period** between detecting source-resource absence and reclaiming its backups -- long enough to recover from accidental deletion and to let transient states settle (a VM that is migrating, rebuilding, or briefly absent from the API during a control-plane event must not be read as "deleted")? Reclamation that fires the instant a resource disappears will eventually destroy backups for a resource that was only temporarily gone.
- [ ] **[Critical]** Are **legal-hold and compliance-lock** gates checked before any reclamation -- so that a resource under litigation hold, regulatory retention (SEC 17a-4, HIPAA, tax), or immutable/WORM lock is never reclaimed even when the source resource is gone and the cost-governance logic wants it deleted? This is the gate that resolves the right-to-erasure-vs-legal-hold conflict in favor of hold (GDPR Article 17(3) exempts data retained for legal claims).
- [ ] **[Critical]** Are **do-not-delete tags / data-classification** signals honored as a gate -- a `retain=true`, `data-classification=regulated`, or equivalent tag (propagated from the source resource or the CMDB) blocks automated reclamation and routes the object to manual review instead of silent deletion?
- [ ] **[Critical]** Is the **soft vs hard action path** distinguished explicitly -- soft = deconfigure/unprotect the source object at the backup tool and let existing recovery points age out under the retention policy (no recovery points destroyed early; cost recedes gradually as data ages); hard = explicitly delete the backup data now (immediate cost reclamation and right-to-erasure satisfaction, but irreversible)? Defaulting to hard for cost reasons creates erasure-vs-recovery risk; defaulting to soft for safety reasons fails to satisfy a right-to-erasure deadline.
- [ ] **[Recommended]** Is **risk-based approval** wired into the hard path -- low-risk objects (dev/test, untagged, below a size/value threshold) reclaim automatically after the grace period; high-risk objects (production, regulated, large, or recently active) require human approval before hard deletion -- so that the automation handles the bulk volume without putting a human in the loop for every object, while still gating the consequential deletes?
- [ ] **[Recommended]** Is every reclamation decision **audited** -- which resource, which join key, which gate results, soft-or-hard, who/what approved, and the backup-tool job id that executed it -- so that "why was this backup deleted" and "why is this orphan still costing money" are both answerable months later, and so the audit trail survives a right-to-erasure or e-discovery request?
- [ ] **[Recommended]** Is the **CMDB / source-of-truth reconciled** as part of the loop -- the same `install_status = decommissioned` / retired-CI signal that drives other decommission automation should drive (or at least cross-check) backup reclamation, so the backup tool, the source platform, and the CMDB do not disagree about whether a resource exists? (See `providers/servicenow/cmdb.md` for IRE/reconciliation mechanics.)
- [ ] **[Recommended]** Is the **reverse drift** also reconciled -- backup-tool protected objects that the source system has no record of *and* the backup tool's own catalog cannot explain (ghost subclients, stale protection jobs pointing at re-IP'd hosts) -- so the loop catches both "source deleted, backups orphaned" and "backups configured, source never existed / long gone"?
- [ ] **[Recommended]** Does the action path **fail safe** -- on any ambiguity (join-key collision, gate-evaluation error, backup-tool API error, CMDB unreachable), the loop must default to *not deleting* and routing to review, never to deleting on incomplete information? A reconciliation loop that deletes when it cannot confirm a gate is more dangerous than the orphan it was built to clean up.
- [ ] **[Optional]** Is there a **dry-run / report-only mode** for the reconciliation loop -- so a new join-key mapping or gate change can be validated against what it *would* delete before it is allowed to act, and so the steady-state orphan inventory is visible as a report even when auto-reclamation is disabled?
- [ ] **[Optional]** Are **bulk events** (project/account/tenant deletion that destroys hundreds of resources at once) rate-limited and batched into a single approval, so a tenant offboarding does not flood the backup tool with thousands of individual delete jobs or trip a runaway-deletion safety limit?

## Why This Matters

The space between a source system's lifecycle and a backup tool's lifecycle is invisible until it is expensive. No single component is broken: the source platform correctly deletes the VM, the backup tool correctly retains the data it was told to protect, and neither was ever told that the deletion of the former should affect the latter. The result is a steady, quiet accumulation -- a few orphaned recovery points per week, never enough to notice in any one month, cumulatively enough that after a year a meaningful fraction of backup storage protects resources that no longer exist. This is the orphaned-backup failure mode documented in `failures/data.md`, seen from the process side rather than the symptom side.

The naive fix -- "delete the backups when the source emits a delete event" -- is worse than the disease, for two reasons. First, events are lossy: any deletion event dropped during a message-bus outage, a consumer crash, or a maintenance window leaves an orphan that the event-only design will *never* reclaim, because there is no second mechanism that re-checks. Second, events are premature: a resource that briefly disappears from the source API during a control-plane event, a live migration, or a rebuild looks identical to a deletion at the instant the event fires, and acting immediately destroys backups for a resource that was only transiently gone. This is why the durable design is the **hybrid**: events provide low-latency *flagging* of candidates, and a **reconciliation loop** -- which lists both sides and computes the actual set difference -- is the *authority* that enforces, with a grace period in between. The reconciliation loop is also self-healing: an orphan missed in one cycle is caught in the next, because the loop re-derives ground truth every time rather than depending on a one-shot event.

The **join key** is where this pattern produces data-loss bugs instead of cost savings. Correlating source resources to backup objects by display name or IP address feels natural because that is what humans use, but both are mutable and reusable. A VM renamed after its backup was configured no longer matches; worse, a *name reused* for a brand-new resource matches the old resource's deletion record, and a name-based reconciliation loop will happily reclaim the new resource's backups in response to the old resource's deletion. The join key must be the stable, immutable identifier each side assigns (source UUID / instance-id / managed-object-reference), carried as the correlation token in both the backup tool's metadata and the audit trail. This is the same join-key discipline that the CMDB's Identification and Reconciliation Engine enforces for exactly the same reason (`providers/servicenow/cmdb.md`).

The pattern implicitly resolves a **three-way tension**, and the governance gates are where that resolution lives. **Cost governance** pulls toward deleting orphaned backups as fast as possible. The **GDPR Article 17 right-to-erasure** pulls toward propagating deletions all the way into backups on a deadline, not leaving personal data in recovery points indefinitely (`compliance/gdpr.md`). **Legal hold and regulatory retention** pull the opposite way -- some data *must not* be deleted even though the source resource is gone and both cost and erasure logic want it removed. No single default satisfies all three. The gates encode the priority order: legal-hold and compliance-lock win over both cost and erasure (Article 17(3) explicitly exempts data retained for legal claims); a grace period protects against accidental and transient deletion; do-not-delete tags and risk-based approval keep a human in the loop for the consequential cases; and the soft-vs-hard action choice lets cost reclamation (soft, age-out) and erasure satisfaction (hard, explicit delete) be selected per object rather than globally. A design that hard-codes "always delete" optimizes cost and erasure at the cost of a legal-hold violation; one that hard-codes "never delete" is safe but never satisfies an erasure deadline and never reclaims the cost. The gates exist so the choice is made per object, on evidence, and is auditable.

## Common Decisions (ADR Triggers)

### ADR: Diff Mechanism -- Event-Driven vs Reconciliation vs Hybrid

**Context:** The synchronization must detect when a protected resource no longer exists at the source. The detection mechanism determines latency, completeness, and resilience to outages.

**Options:**

| Criterion | Event-driven only | Reconciliation-loop only | Hybrid (events flag, loop enforces) |
|---|---|---|---|
| Latency to detect | Low (near-real-time) | High (poll interval) | Low to flag, poll to enforce |
| Resilience to dropped events | None -- missed event = permanent orphan | Full -- re-derives truth each cycle | Full -- loop backstops the events |
| Load on source/backup APIs | Low | Higher (periodic full listing) | Moderate |
| Handles transient absence | Poorly (acts immediately) | Well (grace period built in) | Well |
| Recommended for | Augmentation only | Small/static estates | **Default for production** |

**Decision factors:** Whether the source system emits reliable deletion events; the acceptable orphan-detection latency; the cost of a missed deletion (cost-only vs erasure-deadline); estate size and API rate limits. Default to hybrid; use reconciliation-only when no event bus exists; never use event-only as the sole mechanism where erasure or cost-governance guarantees matter.

### ADR: Soft vs Hard Reclamation Action

**Context:** Once a resource is confirmed deleted at the source and all gates pass, the backup data can be reclaimed by deconfiguring protection and letting recovery points age out (soft) or by explicitly deleting the backup data now (hard).

**Decision factors:** Whether a right-to-erasure deadline applies (forces hard within the deadline); the recoverability requirement (soft preserves the ability to restore until age-out; hard is irreversible); the urgency of cost reclamation (hard frees storage immediately, soft frees it gradually); data classification and approval risk. A common policy is soft-by-default with hard reserved for erasure requests and explicitly tagged data, selected per object rather than globally.

### ADR: Grace Period and Transient-State Settling

**Context:** A resource absent from the source API may be deleted or only transiently gone (migrating, rebuilding, control-plane outage). Reclaiming too early destroys backups for a resource that still exists; too late leaves orphans costing money and holds personal data past an erasure deadline.

**Decision factors:** The platform's transient-absence behavior (how long a healthy resource can be missing from the API); the accidental-deletion recovery window the business requires; any erasure-deadline ceiling that bounds how long the grace period can be. The grace period must be longer than the worst-case transient absence and shorter than any erasure deadline; if those two constraints conflict, the conflict itself is an ADR.

### ADR: Reclamation Authorization -- Automated vs Risk-Based Approval

**Context:** Hard deletion of backup data is irreversible. Requiring human approval for every object does not scale; approving none of them is reckless for production and regulated data.

**Decision factors:** Object risk tier (dev/test vs production vs regulated); size/value thresholds; recency of last activity; data classification tags. Typical resolution: automatic reclamation for low-risk objects after the grace period, mandatory approval for high-risk objects, and fail-safe-to-review on any gate ambiguity.

### ADR: Join-Key Strategy

**Context:** Correlating source resources to backup-tool protected objects requires a key present and stable on both sides.

**Decision factors:** Availability of a stable immutable identifier on both sides (source UUID/instance-id/MoRef vs backup-tool client/subclient/object id); whether that identifier is carried into the backup tool's metadata at protection time; the consequences of a mismatch (name-reuse collision causing wrong-object deletion). Always use the immutable identifier; never name or IP. If the backup tool only records names, the remediation (recording the UUID as a property/tag at protection time) is itself an ADR and a prerequisite for safe automation.

## Reference Links

- [GDPR Article 17 -- Right to erasure](https://gdpr-info.eu/art-17-gdpr/) -- the erasure obligation and its 17(3) exemptions (legal claims, regulatory retention) that the legal-hold gate encodes
- [OpenStack Nova notifications](https://docs.openstack.org/nova/latest/reference/notifications.html) -- example source-system lifecycle event bus (`instance.delete.end`) that drives the event-flagging side of the hybrid
- [AWS Backup -- delete and lifecycle](https://docs.aws.amazon.com/aws-backup/latest/devguide/deleting-backups.html) -- cloud-native example of retention-age (soft) vs explicit recovery-point deletion (hard)
- [ITIL Service Asset and Configuration Management](https://www.axelos.com/certifications/itil-service-management) -- decommissioning and CMDB reconciliation framing for the source-of-truth gate

## See Also

- `failures/data.md` -- the orphaned-snapshot/backup failure mode this pattern prevents (symptom side)
- `compliance/gdpr.md` -- Right to erasure (Article 17), backup-retention-vs-erasure conflict, soft-delete-before-hard-delete
- `general/inventory-analysis.md` -- orphaned-resource identification and disposition; decommission-candidate criteria (inventory side)
- `general/enterprise-backup.md` -- backup strategy, retention models, 3-2-1-1-0, and product selection that this pattern operates on top of
- `providers/servicenow/cmdb.md` -- IRE/reconciliation and stable-identifier discipline; the CMDB source-of-truth gate
- `providers/commvault/backup.md`, `providers/cohesity/backup.md`, `providers/rubrik/backup.md`, `providers/veeam/backup.md` -- per-vendor day-2 mechanics (deconfigure, retention aging, explicit delete, auto-discovery rules) that implement the action path
- `providers/openstack/operations.md` -- consuming the Nova lifecycle notification bus to drive the event-flagging side
- `providers/openstack/data-protection.md` -- the OpenStack-native (Cinder snapshot / Glance image) artifacts this reclamation must also handle, dependent vs independent
- `general/legal-hold.md` -- the integration architecture behind the legal-hold/compliance-lock gate this pattern enforces
- `patterns/event-driven.md` -- delivery guarantees, idempotency, and dead-letter handling for the event-driven half of the hybrid
