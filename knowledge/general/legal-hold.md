# Legal Hold and Preservation Integration

## Scope

Covers the **infrastructure-side architecture for integrating an authoritative legal-hold / preservation source into a retention and deletion pipeline** -- the override that every automated aging, erasure, or reclamation process must consult before deleting anything. Topics: the authoritative hold system-of-record and how downstream processes query it; hold propagation across the full protection stack (primary, snapshots, backups, replicas, images, archives); conflict precedence between legal hold, scheduled retention aging, and the GDPR Article 17 right-to-erasure; and the controlled release workflow plus the immutable audit trail that proves what was held, by whom, when, and why nothing was deleted.

This file is the **integration architecture behind the legal-hold gate**, not a legal guide. It does not cover the email/eDiscovery product mechanics (Microsoft Purview eDiscovery / litigation hold, Google Vault, AWS WorkMail) -- those are per-provider. It is the cross-cutting capability those tools and any custom hold registry feed into. It applies to *any* automated deletion, not just backup: it is named as a deletion gate in `patterns/backup-lifecycle-synchronization.md`, as a retention tier in `providers/vmware/data-protection.md` and `providers/openstack/data-protection.md`, and as an erasure exception in `compliance/gdpr.md` -- this file is where those references resolve to an actual design.

## Overview

A legal hold (litigation hold / preservation order) is a directive that specified data must not be altered or deleted because it is relevant to anticipated or active litigation, investigation, audit, or regulatory inquiry. It is not a retention policy: it is an *override* that suspends retention, aging, and erasure for the data in scope, for as long as the hold is in force, regardless of what any schedule or data-subject request would otherwise dictate. The duty to preserve attaches when litigation is reasonably anticipated, and spoliation (destroying data under a duty to preserve) carries court sanctions independent of any other compliance regime.

The architecture has four parts. An **authoritative hold source** is the single system of record for "what is currently held and why." **Hold propagation** is the mechanism that makes the hold effective across every copy of the data, not just the primary. **Conflict precedence** is the encoded rule that legal hold wins over both scheduled aging and right-to-erasure. The **release workflow and audit trail** govern controlled removal of a hold and produce the evidence that the organization both preserved what it should have and deleted nothing it should not have. The failure this prevents is a deletion or reclamation pipeline that ages out, erases, or reclaims an object that was under an active hold -- a spoliation event that no amount of downstream backup hygiene can undo.

## Checklist

- [ ] **[Critical]** Is there a single **authoritative hold source** (system of record) that every deletion/aging/reclamation process must consult, rather than holds tracked ad hoc in spreadsheets, ticket comments, or per-tool flags? Without one authoritative source, "is this object held?" has no reliable answer at delete time, and the safe default (never delete) and the compliant default (delete on schedule) conflict with no way to resolve them.
- [ ] **[Critical]** Does every automated deletion path -- scheduled retention aging, GDPR erasure fulfilment, orphan/backup reclamation, storage lifecycle rules, log rotation -- **query the hold source (or a propagated hold marker) before deleting**, and **fail safe to no-delete-and-escalate** on any ambiguity (hold source unreachable, identity unresolved, marker missing)? A pipeline that deletes when it cannot confirm hold status is the spoliation risk this entire pattern exists to remove.
- [ ] **[Critical]** Is the **conflict-precedence order** explicit and encoded: legal hold overrides scheduled retention aging **and** the GDPR Article 17 right-to-erasure (Art. 17(3)(e) exempts data needed to establish, exercise, or defend legal claims)? When a data subject requests erasure of data under hold, the architecture must suppress the erasure, record the exception with its legal justification, and (where required) queue the erasure to complete automatically on hold release.
- [ ] **[Critical]** Does the hold **propagate across the full protection stack** -- primary store, replicas/read-replicas, Cinder/array snapshots, backups, Nova→Glance / VM images, archives, analytics and ML training copies -- so that aging and erasure skip held objects *everywhere*, not just in the primary? A hold honored on the primary but not on the backup or the snapshot tree still loses the evidence when the unheld copy ages out.
- [ ] **[Critical]** Is the **join key** between the hold source and the protected objects a stable immutable identifier (custodian id, matter id, resource UUID), never a mutable name or path, so that a rename, re-IP, or name-reuse cannot cause a held object to be missed or an unheld object to be falsely held? (Same join-key discipline as `patterns/backup-lifecycle-synchronization.md`.)
- [ ] **[Recommended]** Is the **hold-application mechanism** chosen deliberately -- per-object tag/lock written onto every copy (durable, survives source outage, but must be reliably stamped on new copies) vs query-time check against the hold source at delete time (always current, but a hard dependency on the source being reachable) vs the hybrid (tag for durability, periodic reconciliation against the source for correctness)? Each has a different failure mode; the hybrid is the safe default for high-stakes data.
- [ ] **[Recommended]** Is the hold backed by a **technical preservation control where the data lives** -- WORM / object-lock in legal-hold mode (S3 Object Lock legal-hold, Azure immutable blob legal-hold, Ceph RGW object-lock, Swift with object-lock), repository immutability, or snapshot locks -- so the hold is enforced by storage, not merely by the politeness of the deletion code? Legal-hold-mode locks (indefinite, no retention date) differ from compliance-mode retention locks (fixed expiry) and are the correct primitive for an open-ended hold.
- [ ] **[Recommended]** Is there a **controlled release workflow** -- holds are released only by authorized custodians/legal, with a reason, and release triggers re-evaluation so that data which was *only* preserved by the hold becomes eligible for its normal retention/erasure disposition (including completing any erasure that was suppressed during the hold)? An object should not silently remain preserved forever after its hold ends, nor be deleted the instant a hold lifts without re-checking other holds.
- [ ] **[Recommended]** Is every hold action **immutably audited** -- hold placed/modified/released, scope, custodian, matter id, who, when, why; every suppressed deletion (which object, which hold, the legal justification); and every release-triggered disposition -- in a tamper-evident trail that itself is retained for the life of the matter plus its own retention? The audit trail is the evidence of defensible preservation *and* of defensible deletion; both are discoverable.
- [ ] **[Recommended]** Is **hold scope granularity** defined -- custodian-level (all data for a person), matter-level (all data relevant to a case), data-set / system-level, or object-level -- and does the propagation mechanism resolve coarse scopes (e.g., "custodian X") down to the concrete objects across every store? Over-broad holds preserve far more than necessary (cost, and more data exposed in discovery); over-narrow holds miss relevant evidence.
- [ ] **[Optional]** Is there a **periodic reconciliation / hold-coverage report** that lists every active hold and verifies that each in-scope object across every store actually carries an effective preservation control, surfacing any held object that a lifecycle rule could still reach? This is the completeness check that catches a new backup target or storage tier that was never wired into the propagation.
- [ ] **[Optional]** Are **bulk hold events** (a matter placing thousands of custodians on hold, or a mass release) rate-limited, batched, and reversible-by-audit, so a large hold application does not silently miss objects under load and a mass release does not trigger an unreviewed deletion stampede?

## Why This Matters

The legal-hold gate is the one override where the failure is asymmetric and irreversible in the dangerous direction. Retaining data slightly too long costs storage and widens discovery exposure -- recoverable problems. Deleting data under an active preservation duty is **spoliation**: courts sanction it with adverse-inference instructions, monetary penalties, or default judgment, and the destroyed evidence cannot be recovered by any backup process. Every automated deletion path an organization builds -- retention aging, GDPR erasure, orphan/backup reclamation, storage lifecycle policies, log rotation -- is a potential spoliation engine the moment it runs without consulting an authoritative hold source. This is why "does this pipeline check for holds, and does it fail safe when it cannot" is the first question to ask of any deletion automation, and why the answer must be designed in, not bolted on after the first preservation order arrives.

The defining design choice is the **authoritative hold source**. When holds are tracked informally -- a spreadsheet, an email thread, a flag in one of several tools -- the system has no reliable way to answer "is this object held?" at the instant a deletion job is about to run, so it must choose between two bad defaults: never delete (retention and erasure collapse, cost balloons, the organization cannot meet its Article 17 obligations) or delete on schedule (spoliation roulette). A single system of record -- whether an eDiscovery/preservation platform, a GRC tool, or a purpose-built hold registry -- collapses that ambiguity into a queryable fact. The downstream pipelines do not need to understand legal nuance; they need exactly one integration: ask the source (or check a marker the source stamped) and respect the answer.

**Propagation across the full stack** is where holds quietly fail even when the source is authoritative. A hold honored on the primary database but not on its read-replicas, its nightly backups, its array snapshots, or the VM image captured last quarter preserves nothing if the unheld copy is the one that ages out -- and under discovery, the existence of *any* surviving copy is what matters, so the gap is also the exposure. The protection stack is exactly the set of copies enumerated in `patterns/backup-lifecycle-synchronization.md` and the OpenStack-native artifacts in `providers/openstack/data-protection.md`; the hold must reach every one of them. This is why the per-object-tag mechanism is attractive (the marker travels with each copy and survives a source outage) but only works if every process that *creates* a new copy reliably stamps the marker -- otherwise a fresh backup of held data is born unmarked. The hybrid (durable tags plus periodic reconciliation against the authoritative source) is the safe default precisely because the reconciliation catches the copy that the tagging missed.

**Conflict precedence** is the rule that makes the three-way tension from the backup-lifecycle pattern resolvable. Scheduled aging wants to delete on time; the GDPR right-to-erasure wants to delete on request; legal hold says *not these objects, not yet*. Article 17(3)(e) explicitly exempts data needed for legal claims from the erasure obligation, which is the legal basis for suppressing an erasure request that collides with a hold -- but the suppression must be *recorded with its justification* and, in most designs, *queued to complete on release*, so the organization can show it honored both duties in sequence rather than ignoring one. Encoding the order (hold > aging, hold > erasure) once, in the gate, keeps every individual pipeline simple: each one checks the gate and obeys, rather than each one re-implementing the precedence logic and drifting.

Finally, the **release workflow and audit trail** are what make the whole thing *defensible*, which is the actual deliverable. Preservation that no one can prove is worth little in court, and deletion that no one can justify is worth less. The audit trail must show, immutably, what was held and why, every deletion that was suppressed because of a hold, and every disposition that occurred when a hold was released -- because both the preservation and the eventual deletion are discoverable, and "we destroyed it under a documented, consistently-applied retention schedule after all holds were released" is a defense while "we don't know why that's gone" is not. Controlled release matters for the same reason: data preserved *only* by a hold must return to its normal retention/erasure disposition when the hold lifts (not linger forever, not vanish instantly without re-checking other holds), and that transition is itself an audited event.

## Common Decisions (ADR Triggers)

### ADR: Authoritative Hold Registry -- Build vs Buy

**Context:** The system of record for active holds can be an existing eDiscovery/preservation platform, a GRC/legal-operations tool, or a purpose-built hold registry that infrastructure deletion pipelines query.

**Decision factors:** Whether an eDiscovery platform already holds the custodian/matter mapping (reuse it as the source rather than duplicating); the need for infrastructure objects (volumes, snapshots, backups, images) that email-centric eDiscovery tools do not model; integration surface for deletion pipelines (a queryable API vs manual export); and ownership boundary between legal and platform teams. A purpose-built registry is warranted when holds must span infrastructure artifacts that the legal tooling cannot reference by resource UUID.

### ADR: Hold Application -- Per-Object Tag vs Query-Time Check vs Hybrid

**Context:** A deletion process can determine hold status by reading a marker/lock written onto the object, or by querying the authoritative source at delete time.

| Criterion | Per-object tag/lock | Query-time check | Hybrid (tag + reconcile) |
|---|---|---|---|
| Survives source outage | Yes | No (hard dependency) | Yes |
| Always current | No (stale if source changes) | Yes | Yes (reconciliation closes the gap) |
| Risk on new copies | Unmarked copy is unprotected | None (source is truth) | Reconciliation catches misses |
| Enforced by storage | Yes (WORM/object-lock) | No (only by code) | Yes |
| Recommended for | Immutable archives | Small, always-online estates | **High-stakes default** |

**Decision factors:** Reachability guarantees for the hold source; whether every copy-creating process can be trusted to stamp the marker; the value of storage-enforced WORM. Default to hybrid for litigation-grade data.

### ADR: Conflict Precedence Encoding

**Context:** Legal hold, scheduled retention aging, and the GDPR right-to-erasure can target the same object with opposite intents.

**Decision factors:** The fixed precedence (legal hold > aging; legal hold > erasure, per Art. 17(3)(e)); whether suppressed erasures are queued to auto-complete on hold release; how the suppression and its legal justification are recorded for the data-subject response. Encode precedence once in the gate; never let individual pipelines re-derive it.

### ADR: Hold Scope Granularity

**Context:** Holds can be scoped at custodian, matter, system/data-set, or object level, and coarse scopes must resolve to concrete objects across stores.

**Decision factors:** How the authoritative source expresses scope; the propagation mechanism's ability to expand a coarse scope (e.g., "custodian X") into every in-scope object; the cost and discovery-exposure trade-off of over-broad holds vs the spoliation risk of over-narrow ones. Prefer the narrowest scope that provably covers all relevant evidence, with reconciliation to confirm coverage.

### ADR: Release and Disposition Workflow

**Context:** When a hold is released, data preserved only by that hold must return to normal disposition without being deleted prematurely or preserved indefinitely.

**Decision factors:** Authorization for release (legal/custodian, not platform); re-evaluation against any *other* active holds before deletion; completion of erasure requests that were suppressed during the hold; and the audited transition. A release must trigger re-check, not immediate delete.

## Reference Links

- [GDPR Article 17 -- Right to erasure](https://gdpr-info.eu/art-17-gdpr/) -- 17(3)(e) exempts data needed to establish, exercise, or defend legal claims (the legal basis for hold-over-erasure precedence)
- [The Sedona Conference -- Commentary on Legal Holds](https://thesedonaconference.org/publication/Commentary_on_Legal_Holds) -- widely cited guidance on the duty to preserve and defensible hold practice
- [US FRCP Rule 37(e)](https://www.law.cornell.edu/rules/frcp/rule_37) -- sanctions for failure to preserve electronically stored information (spoliation)
- [AWS S3 Object Lock -- legal hold](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html) -- legal-hold mode (indefinite, no retention date) vs retention-period mode, as a storage-enforced preservation primitive

## See Also

- `patterns/backup-lifecycle-synchronization.md` -- the deletion/reclamation pipeline that consumes this gate before reclaiming any backup
- `compliance/gdpr.md` -- Right to erasure (Article 17) and the backup-retention-vs-erasure conflict this precedence resolves
- `general/ransomware-resilience.md` -- immutable/WORM storage and failure-domain isolation that the technical preservation control reuses
- `general/data-classification.md` -- classification that drives which data is hold-eligible and how holds are scoped
- `general/governance.md` -- policy-as-code and guardrails that enforce the deletion-must-check-holds rule
- `providers/openstack/data-protection.md` -- OpenStack-native snapshot/image/backup artifacts the hold must propagate across
- `providers/vmware/data-protection.md` -- legal-hold as an indefinite, immutable retention tier in a VMware estate
