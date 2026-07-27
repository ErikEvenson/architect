# Change-Window Alert Suppression

## Scope

This file covers the **pattern that suppresses the predictable alert storm a planned infrastructure change window generates** -- host migrations and evacuations, firmware and hardware swaps, and platform/version/storage upgrades all cycle hosts and services in ways that trip alerts that are *expected*, not *actionable*. The pattern ties the change record to the monitoring layer: it derives the suppression scope from the change's affected-CI list, suppresses at the parent CI and lets dependency/inhibition rules cascade, brackets the window with raise/remove tasks owned by the operating team, and preserves a baseline so a genuine failure still surfaces above the suppressed noise.

It is provider-agnostic. The **suppression layer** is whatever enforces the blackout -- ServiceNow Event Management maintenance suppression, Prometheus AlertManager inhibition/silences, or SolarWinds dependency-based suppression and maintenance mode -- and the pattern applies the same regardless of which one (or which combination) is in use; apply it wherever it can be **audited against the change record**. This file is the **synthesis layer**: it does not duplicate the change-classification and maintenance-window process (`general/change-management.md`), the per-operation OpenStack day-2 procedures that generate the alerts (`providers/openstack/operations.md`), the exporter taxonomy that defines the alert types (`providers/openstack/observability.md`), or the per-tool suppression mechanics that implement it (`providers/servicenow/itsm.md`, `providers/prometheus-grafana/observability.md`, `providers/solarwinds/monitoring.md`). It is the layer that ties those together into one decision-pattern.

## Overview

A planned change and the monitoring system each have their own view of the same hosts. The change record knows which CIs are in scope, when the window opens and closes, and what operation is being performed. The monitoring system knows only that a host went unreachable, an instance's state churned, or an OSD's latency spiked -- it cannot tell a planned evacuation from a real failure. Nothing inherently connects the two: opening a change does not quiet the monitors, and the monitors do not know the window exists. The space between is where the alert storm lives -- a recurring upgrade or migration calendar generates large, predictable, suppressible alert volume that buries the few alerts that matter and trains operators to ignore the channel.

The pattern has four moving parts: a **scope derivation** that reads the suppression target (which host CIs / VMs) from the change's affected-CI list rather than a manual guess; a **cascade** that suppresses at the parent host CI and lets dependency/inhibition rules quiet the child VM and service alerts; a **bracket** -- a raise-suppression task at change-start and a remove-suppression task at completion, both owned by the operating team and pre-attached to the repeatable change models so the blackout is automatic; and a **baseline** that records the normal alert volume per operation so an abnormal spike still surfaces. The hard design choices are how scope is derived (affected-CI list vs manual), where suppression is applied (parent-cascade vs flat per-VM list), how aggressively to suppress per change tier, and how to keep the blackout from blinding a genuine failure.

## Checklist

- [ ] **[Critical]** Is the **suppression scope derived from the change record's affected-CI list**, not entered by hand? (The set of host CIs and dependent VMs to suppress should come from the change's CI scope so the blackout matches what is actually being touched; a manual guess drifts from the real scope, over-suppresses bystanders, or misses hosts the change actually cycles. This is the join between change management and monitoring -- `general/change-management.md`, `providers/servicenow/itsm.md`.)
- [ ] **[Critical]** Is suppression applied **at the parent host CI with dependency/inhibition cascade**, rather than a flat per-VM list? (Suppress the host CI and let dependency rules -- ServiceNow Event Management correlation, AlertManager `inhibit_rules` where host-down inhibits child service alerts, SolarWinds dependency-based suppression -- quiet the VM and on-host service alerts automatically. Parent-cascade is less config and more accurate than enumerating every VM, and it stays correct as VMs move on and off the host.)
- [ ] **[Critical]** Is the suppression **time-bounded to the change window** (auto-expiring at the scheduled end), so a forgotten silence does not blind monitoring indefinitely? (A maintenance silence with no expiry is the inverse failure of the alert storm -- it suppresses *real* incidents on those hosts for days. Bound every suppression to the window; require an explicit extension if the change runs long.)
- [ ] **[Critical]** Is each suppression **tied to the change record and auditable** -- which change, which CIs, who raised it, when it expires? (Apply suppression wherever it can be reconciled against the change record so "why was this host silent at 02:00" is answerable afterward, and so a suppression with no backing approved change is itself an alertable anomaly. This is the audit discipline that keeps suppression from becoming a way to hide chronic noise.)
- [ ] **[Critical]** Is the **per-operation alert footprint** known, so the *right* alert types are suppressed and others are left live? (Suppress only what the operation legitimately generates -- a live-migration's host-saturation and instance-state churn -- while leaving unrelated alert classes active. Over-broad suppression that silences everything on the host removes the baseline the change still needs. See the footprint table below.)
- [ ] **[Critical]** Is a **change-impact tier** assigned that determines whether and how much to suppress -- not every change needs a blackout? (Tier 1 host-evacuating changes warrant full host-CI suppression; Tier 2 single-host hardware warrants targeted single-host suppression and a hot-swap may need none; Tier 3 config-only changes need none -- monitor the affected service instead. See the tiering ADR below.)
- [ ] **[Recommended]** Is the window **bracketed by a task pair** -- a raise-suppression task at change-start and a remove-suppression task at completion -- both owned by the **operating team**, with a single-owner handshake so two changes do not raise overlapping suppressions on the same CI? (The remove task is the safety mechanism: it forces the blackout closed at completion rather than relying on the time-bound expiry alone, and single-ownership prevents one change's remove-task from lifting another change's still-needed suppression.)
- [ ] **[Recommended]** Is the suppression **pre-attached to the repeatable change models (standard changes)** so it is automatic, not improvised per change? (Recurring upgrade/migration/firmware changes are standard changes -- bake the raise/remove task pair and the scope-derivation into the change model so every instance of that change carries its own blackout without an operator remembering to add it. `general/change-management.md`, `providers/servicenow/itsm.md`.)
- [ ] **[Recommended]** Is a **baseline alert volume per operation** established, so an abnormal spike surfaces above the suppressed noise? (Suppression must not blind genuine failures -- if a live-migration normally generates N instance-state events and this one generates 5N, that excess should still alert even inside the window. Record the normal per-operation footprint and alert on deviation from it, not on the raw alerts the operation always produces.)
- [ ] **[Recommended]** Are **storage and control-plane alert classes handled for upgrade changes**, not just host-down? (A major platform/version upgrade that also upgrades the storage tier -- e.g. Ceph -- generates OSD-latency and PG-state alerts and control-plane service-health alerts *in addition to* host-cycling; suppressing only host-down leaves the storage and control-plane storm live. Scope the suppression to the full footprint of the operation, including its storage and control-plane dimensions -- `providers/openstack/observability.md`, `providers/openstack/operations.md`.)
- [ ] **[Recommended]** Does the suppression **fail safe toward visibility** -- if the scope cannot be confidently derived or the suppression layer errors, does monitoring stay *on* (accept the storm) rather than apply an over-broad blanket silence? (A blackout applied on incomplete information is more dangerous than the alert noise it was meant to quiet; when in doubt, suppress less and tolerate the noise.)
- [ ] **[Optional]** Is the suppression **driven from the same CMDB dependency graph** the monitoring tool already uses for correlation, so the change's affected-CI list and the monitor's parent/child topology agree? (Reusing one dependency model -- rather than maintaining a separate suppression map -- keeps the cascade accurate as the topology changes and avoids a suppression list that silently goes stale. `providers/servicenow/itsm.md`.)
- [ ] **[Optional]** Is a **post-window reconciliation** run -- every suppression lifted, no host left silenced, alert volume back to baseline -- before the change is closed? (Closing a change while a suppression is still active or alert volume is still elevated hides whether the change actually succeeded; the reconciliation is the monitoring-side completion gate.)

## Per-Operation Alert Footprint

The suppression scope should match what the operation actually generates. Suppress these classes; leave unrelated classes live.

| Operation | Primary alert classes generated | Suppress at | Tier |
|---|---|---|---|
| Live-migration / host evacuation | Host CPU/memory saturation; instance-state churn (per-VM state transitions) | Host CI (cascade to VM alerts) | 1 |
| Firmware / hardware change, single host (reboot, fan, drive) | Host-down / agent-unreachable; IPMI hardware alerts | Single host CI (targeted) | 2 |
| Major platform / version upgrade + storage (e.g. Ceph) upgrade | Host-cycling **plus** OSD latency / PG-state **plus** control-plane service-health | Host CIs + storage + control-plane scope | 1 |
| Config-only change (API / port change) | Transient service alerts (usually none host-level) | None -- monitor the affected service | 3 |

The alert classes map to the exporter taxonomy in `providers/openstack/observability.md` (node_exporter CPU/mem, libvirt per-VM, ceph_exporter OSD/PG, ipmi hardware) and the procedures that produce them in `providers/openstack/operations.md` (`nova service-disable` + live-migration/evacuation, Galera/RabbitMQ control-plane cycling).

## Why This Matters

A change calendar is a noise generator. Managed-operations engagements run recurring upgrade, migration, and firmware change models against the same fleet, and each instance trips a wave of alerts that are entirely expected: the evacuated host saturates, the migrating instances churn through state transitions, the rebooted host goes unreachable, the upgraded Ceph cluster reports OSD latency and PG remapping. None of these are actionable -- they are the *signature* of the change succeeding -- but to a monitoring system that does not know the window exists, they are indistinguishable from a real outage. Left unsuppressed, this volume does two kinds of damage: it pages on-call for non-events, and, worse, it trains operators that the channel is noise, so the one genuine failure buried in the storm gets acknowledged-and-ignored along with the rest. ServiceNow's own guidance recommends Event Management suppression once a maintenance activity crosses ~100 alerts/day for exactly this reason.

The naive fix -- a human silences "the hosts" before the change and un-silences them after -- fails in three predictable ways. The scope is a guess, so it drifts from what the change actually touches (over-suppressing bystanders, missing hosts the change cycles indirectly). The silence is open-ended, so a forgotten un-silence blinds monitoring on those hosts for days -- the inverse failure, where the suppression hides a *real* incident. And it is per-VM and flat, so it goes stale the moment an instance migrates onto a host that was not in the list. The durable design fixes each: **scope is derived from the change's affected-CI list** so it matches reality; **suppression is time-bounded to the window** so a forgotten silence self-heals; and **suppression is applied at the parent host CI with a dependency cascade** so the child VM and service alerts are quieted by the same correlation/inhibition rules the monitoring tool already maintains -- less configuration, and correct as instances move. Parent-cascade is the same mechanic across all three suppression layers (ServiceNow Event Management correlation, AlertManager `inhibit_rules`, SolarWinds dependency-based suppression), which is why the pattern is provider-agnostic.

The pattern resolves a tension between **noise reduction** and **not going blind**. Suppress too little and the storm buries the signal; suppress too much and the blackout hides the genuine failure the change itself might cause. The resolution lives in three places. **Tiering** decides whether to suppress at all -- a host-evacuating change earns a full host-CI blackout, a single-host hot-swap may earn none, and a config-only change earns none because the right response is to *watch* the affected service, not silence it. The **per-operation footprint** decides *what* to suppress -- only the alert classes the operation legitimately generates, leaving unrelated classes live so the host is not wholly dark. And the **baseline** decides what still gets through -- by recording the normal alert volume per operation, an abnormal spike (a migration generating five times its usual instance-state churn, an OSD whose latency never recovers) surfaces *above* the suppressed noise instead of being swallowed by the blanket silence. This is the monitoring/alerting counterpart to the RHOSP day-2 runbooks (`providers/openstack/operations.md`): those describe how to *perform* the operation; this describes how to keep its predictable noise from drowning the one alert that means the operation went wrong.

## Common Decisions (ADR Triggers)

### ADR: Suppression Scope -- Affected-CI Derivation vs Manual List

**Context:** The blackout needs a set of CIs to suppress. That set can be derived from the change record's affected-CI list or entered by the operator raising the change.

**Options:**

| Criterion | Manual per-VM list | Affected-CI derivation (parent-cascade) |
|---|---|---|
| Accuracy vs actual change scope | Drifts; depends on operator memory | Matches the change record |
| Config volume | One entry per VM | One entry per host CI; cascade handles the rest |
| Correctness as VMs migrate | Goes stale immediately | Stays correct (suppress the host, not the guest) |
| Auditability against the change | Weak -- list is detached from the record | Strong -- scope *is* the record's CI list |
| Setup cost | Low per change, high cumulative | Requires CMDB dependency graph / inhibition rules once |

**Decision factors:** Whether the CMDB/monitoring tool maintains a host→VM→service dependency graph the cascade can ride on; the change volume (high recurring volume makes manual lists untenable); and the audit requirement (a regulated engagement needs suppression traceable to an approved change). Default to affected-CI derivation with parent-cascade; fall back to a manual list only for one-off changes on a fleet with no dependency model.

### ADR: Change-Impact Suppression Tier

**Context:** Not every change warrants a blackout. Over-suppressing config-only changes wastes the mechanism and risks hiding service regressions; under-suppressing host-evacuating changes leaves the storm.

**Options:**
- **Tier 1 -- host-evacuating** (migration / rebuild / version upgrade): full host-CI suppression for the window, scoped to the operation's full footprint (host + storage + control-plane where applicable).
- **Tier 2 -- single-host hardware** (reboot / fan / drive): targeted single-host suppression; a hot-swap that does not take the host down may need none.
- **Tier 3 -- config-only** (API / port change): no suppression; monitor the affected service for regression instead.

**Decision factors:** Whether the operation evacuates or cycles the host (drives Tier 1 vs 2), whether it takes the host unreachable at all (a hot-swap may not -- Tier 2-or-none), and whether the right posture is "quiet the expected noise" or "watch for an unexpected regression" (Tier 3). Encode the tier into the change model so it is assigned once per repeatable change, not argued per instance.

### ADR: Where to Enforce -- Suppression-Layer Selection

**Context:** The blackout can be enforced at the ITSM Event Management layer, the AlertManager/monitoring layer, or both, and the choice affects audit, latency, and which alerts are reachable.

**Options:**
- **ServiceNow Event Management maintenance suppression:** suppression lives next to the change record -- best auditability, ties directly to the affected-CI list and maintenance window. Requires alerts to flow through Event Management.
- **AlertManager inhibition / time-bound silences:** suppression at the alerting layer -- lowest latency, host-down inhibits child service alerts natively. Audit trail is the silence record, which must be reconciled back to the change.
- **SolarWinds dependency-based suppression + maintenance mode:** dependency suppression and time-of-day/maintenance-window awareness built into the monitor -- good for network/server estates already on Orion.
- **Layered (ITSM authoritative, monitor enforces):** Event Management owns the change-linked scope and audit; the monitor enforces the cascade. Most robust, most integration cost.

**Decision factors:** Where alerts already aggregate; the audit requirement (regulated engagements favor the ITSM-authoritative layer); and whether the estate already has a dependency/inhibition model in the monitor. Apply suppression *wherever it can be audited against the change record* -- that constraint, not the specific tool, is what makes the choice correct.

### ADR: Baseline-Preservation Strategy

**Context:** A blackout that suppresses every alert class on the in-scope hosts will also suppress the alert that means the change *failed*. The pattern must keep a genuine failure visible above the expected noise.

**Decision factors:** Whether a normal per-operation alert footprint has been measured (you cannot alert on deviation without it); whether the monitoring layer can express "alert if volume/severity exceeds the expected baseline" rather than a flat silence; and the cost of a missed real failure during the window (high for control-plane and storage upgrades). Typical resolution: suppress the *expected* alert classes per the footprint table, alert on deviation from the per-operation baseline, and leave unrelated classes fully live.

## Reference Links

- [ServiceNow Event Management -- alert suppression and maintenance](https://docs.servicenow.com/bundle/washingtondc-it-operations-management/page/product/event-management/concept/alert-management.html) -- maintenance-window suppression rules and event correlation that drive the change-linked, auditable suppression layer
- [Prometheus AlertManager -- inhibition](https://prometheus.io/docs/alerting/latest/configuration/#inhibit_rule) -- `inhibit_rules` where a host-down alert inhibits child service alerts; the parent-cascade mechanic at the alerting layer
- [Prometheus AlertManager -- silences](https://prometheus.io/docs/alerting/latest/configuration/) -- time-bound silences for bounding a blackout to the change window
- [SolarWinds Platform -- dependency-based alert suppression](https://documentation.solarwinds.com/en/success_center/orionplatform/content/core-managing-dependencies-sw1688.htm) -- network object dependencies mark children Unreachable rather than Down so child alerts do not fire when the parent node is down
- [SolarWinds Platform -- Maintenance Mode / unmanage scheduling](https://documentation.solarwinds.com/en/success_center/orionplatform/content/core-setting-device-management-states-sw2036.htm) -- suspend polling and alerting for nodes over a scheduled window
- [OpenStack Nova -- migrate and evacuate](https://docs.openstack.org/nova/latest/admin/migration.html) -- the host-evacuating operations whose alert footprint Tier 1 suppression covers

## See Also

- `general/change-management.md` -- change classification, standard/normal/emergency change models, and maintenance windows; the change-record side this pattern reads scope from and brackets with tasks
- `providers/openstack/operations.md` -- `nova service-disable` + live-migration/evacuation and control-plane cycling procedures; the operations that *generate* the alert storm (runbook side)
- `providers/openstack/observability.md` -- the exporter stack (node_exporter, libvirt, ceph_exporter, ipmi) that *is* the alert taxonomy this pattern suppresses by class
- `providers/servicenow/itsm.md` -- Event Management maintenance suppression and CMDB dependency model; the auditable, change-linked enforcement layer
- `providers/prometheus-grafana/observability.md` -- AlertManager inhibition and silences; the alerting-layer enforcement of the parent-cascade and time-bound blackout
- `providers/solarwinds/monitoring.md` -- dependency-based suppression and maintenance-window awareness; the Orion enforcement layer
- `patterns/backup-lifecycle-synchronization.md` -- sibling synthesis pattern that likewise ties a change/lifecycle event to a downstream system (backup reclamation) via stable CI identity and governance gates
