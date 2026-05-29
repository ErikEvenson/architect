# OpenStack Controller Lifecycle & Day-2 Operations

## Scope

This file covers the **planned-change day-2 operations** that take an OpenStack controller in and out of service safely: single-node hardware maintenance and chassis replacement, Pacemaker/Corosync + STONITH operation (for Pacemaker-managed estates such as director-based deployments), and TripleO/director + Ironic baremetal day-2 management. It is the lifecycle counterpart to the design content in `providers/openstack/control-plane-ha.md` (HA topology, quorum, fencing *design*) and the incident-triage content in `providers/openstack/operations.md` (unplanned outage diagnosis). The distinction: `control-plane-ha.md` answers "how should HA be built," `operations.md` answers "something broke, what do I check," and this file answers "I need to deliberately take a controller down, work on it, and bring it back without dropping the cluster below quorum."

Topics: clustered-controller standby/return runbook with quorum pre-checks; VIP/HAProxy migration impact; Galera IST/SST and RabbitMQ rejoin **return-verification**; `pcs` node standby vs cluster-wide maintenance-mode; STONITH/fence-agent operation and reconfiguration after a BMC/iDRAC IP change; the live-vs-persisted-config distinction; Ironic baremetal node driver-info and port (NIC MAC) management; the undercloud-as-power-manager relationship; director node-replacement flow; and the BMC-IP-change "triad" that spans Ironic, Pacemaker STONITH, and deployment templates.

For deployment-tool selection and the day-1 deploy flow, see `providers/openstack/deployment-tools.md`. For unplanned failure triage (split-brain, agent flapping, token-key drift), see `providers/openstack/operations.md`. For HA *design* decisions (keepalived vs Pacemaker, queue type, SST method), see `providers/openstack/control-plane-ha.md`.

## Checklist

- [ ] **[Critical]** Before placing any controller in standby for maintenance, is the **surviving-cluster quorum pre-check** performed and recorded — Galera `wsrep_cluster_size` equals the full node count and `wsrep_local_state_comment=Synced` on every *remaining* node, RabbitMQ `rabbitmqctl cluster_status` shows all other members joined with no partitions, and `pcs status` (if Pacemaker-managed) shows no failed/stopped resources? The "resources move gracefully to the other controllers" property only holds if the surviving cluster is quorate; taking one node of three into standby while a *second* is already degraded drops Galera/RabbitMQ below majority and the control plane stops accepting writes — so the pre-check is the load-bearing step, not a formality.
- [ ] **[Critical]** Is the **planned single-node maintenance sequence** documented as an ordered runbook — (1) quorum/health pre-check on the survivors, (2) drain the node (HAProxy disable + `pcs node standby <node>` or `nova/neutron`-agent disable depending on stack), (3) confirm resources/VIP have moved and survivors are still quorate, (4) graceful service stop and OS shutdown, (5) physical maintenance / chassis swap, (6) power on, (7) **return to service** with explicit resync verification, (8) unstandby / re-enable in HAProxy? An unordered "just reboot it" approach skips the pre-check and the return-verification, which are where data-plane damage and silent under-replication originate.
- [ ] **[Critical]** Is the **return-to-service verification** explicit and resync-aware — confirm the returning Galera node actually re-joined and re-synced (`wsrep_local_state_comment=Synced`, `wsrep_cluster_size` back to full count, and whether it did IST or a full SST), confirm RabbitMQ shows the node rejoined with queues replicated (not just the process up), and `pcs status` shows resources started AND monitored? "Resources started" is not the same as "the datastore re-synced" — a node can rejoin Pacemaker while Galera is still doing an SST or stuck in `Donor/Desynced`, leaving the cluster effectively at N-1 redundancy while appearing healthy.
- [ ] **[Critical]** Is the **`pcs node standby` vs `pcs property set maintenance-mode=true` distinction** understood and the correct one chosen — `standby` moves all resources *off one node* (correct for single-node maintenance: the VIP and services relocate to survivors), while `maintenance-mode=true` stops Pacemaker *monitoring cluster-wide* without moving anything (correct only when you are touching the cluster software itself and want resources left running un-managed)? These are routinely confused; using `maintenance-mode` when you meant `standby` leaves services running on a node you are about to power off — an outage — and using `standby` when you meant `maintenance-mode` triggers unwanted failovers during a Pacemaker config change.
- [ ] **[Critical]** When a controller's **BMC/iDRAC IP changes** (typically after a chassis swap), is the **three-place update** performed — (1) the Ironic IPMI driver-info if the node is undercloud/Ironic-managed (`openstack baremetal node set --driver-info ipmi_address=…`), (2) the Pacemaker STONITH fence agent (`pcs stonith update <agent> ipaddr=…` / `ip=…`), and (3) the deployment templates / inventory so the change survives the next redeploy? Missing (2) means Pacemaker cannot fence the affected node (a fencing failure blocks failover and can hang the cluster); missing (1) means the undercloud can no longer power-manage the node; missing (3) means the next `overcloud deploy` / config run silently reverts (1) and (2).
- [ ] **[Critical]** Is the **live-vs-persisted distinction** respected for every cluster change — a live `pcs stonith update`, `pcs resource` edit, or `openstack baremetal node set` fixes the *running* cluster, but on a director/TripleO or config-managed estate the deployment templates (e.g. the fencing environment file, node-registration inventory) and/or Kolla `globals.yml`/host-vars must also be updated, or the next deploy/redeploy reverts the live change? Treating a live fix as "done" without persisting it is the classic regression that re-breaks fencing or IPMI access weeks later when an unrelated deploy runs.
- [ ] **[Recommended]** Is the **VIP/HAProxy failover blip** during standby anticipated and communicated — when the node holding the VIP (keepalived MASTER or the Pacemaker VIP resource) goes into standby, the VIP relocates and in-flight API connections to it are reset, producing a brief (sub-second to a few seconds) API blip and dropped long-lived connections? For maintenance during business hours this should be a scheduled, announced window; draining HAProxy backends first reduces, but does not eliminate, the VIP-move reset.
- [ ] **[Recommended]** Are the **core `pcs` operations** documented for the on-call runbook — `pcs status` (cluster + resource + node state), `pcs node standby <node>` / `pcs node unstandby <node>`, `pcs resource move`/`clear` (and the caveat that `move` creates a location constraint that must be cleared afterward or the resource will not rebalance), `pcs cluster stop`/`start`, and `pcs stonith status` — so operators are not improvising cluster commands during a maintenance window?
- [ ] **[Recommended]** Is **STONITH/fencing operation** understood beyond "it's configured" — `pcs stonith status` and `pcs stonith config` to inspect, `fence_ipmilan` as the typical agent for IPMI/iDRAC/iLO BMCs, `pcs stonith fence <node>` to manually fence, and `stonith_admin --history` / `pcs stonith history` to see fencing events — and is it known that a controller whose fence device is unreachable (wrong BMC IP, BMC down) cannot be fenced, which **blocks** failover for resources that require fencing confirmation rather than failing over?
- [ ] **[Recommended]** For Ironic/undercloud-managed estates, is **Ironic baremetal node day-2** covered — `openstack baremetal node list`/`show`, `openstack baremetal node set --driver-info ipmi_address=… --driver-info ipmi_username=… --driver-info ipmi_password=…` to correct power-management credentials/address, `openstack baremetal node validate <node>` to confirm the power/management/boot interfaces pass, and `openstack baremetal node power on/off <node>` — and is it understood that stale Ironic driver-info is the usual reason the undercloud "can't control" a node after a hardware change?
- [ ] **[Recommended]** Is the **undercloud-as-power-manager relationship** documented — on a director/TripleO estate the undercloud's Ironic service is what performs power management (and, during deploy/scale, provisioning) against overcloud nodes via their BMCs, so the Ironic IPMI driver-info must be current for the undercloud to power-cycle, reprovision, or replace a node? This is why a BMC IP change that is fixed only in Pacemaker still leaves the undercloud unable to manage the node.
- [ ] **[Recommended]** Is the **director controller node-replacement flow** captured at a high level — scale the failed node out / mark it for replacement, register the replacement's hardware (Ironic node + ports), run the targeted `overcloud deploy` (or `openstack overcloud node` replacement workflow for the release in use), then verify Galera/RabbitMQ/Pacemaker membership — with the explicit note that the node-registration inventory and the pacemaker-fencing environment file are part of the templates and must reflect the replacement, or the redeploy will not register/fence the new node?
- [ ] **[Optional]** Are the **NIC-MAC implications of a chassis swap** handled — Ironic ports and `os-net-config` / predictable interface naming may be keyed to MAC addresses, so a replacement chassis with different NIC MACs may need `openstack baremetal port` updates (set the new MAC) and/or net-config template adjustments before the node provisions and networks correctly? A chassis swap that updates the BMC IP but forgets the NIC MACs produces a node that powers on but fails to PXE/provision or comes up with mis-mapped interfaces.
- [ ] **[Optional]** Is the **RHOSO (control plane on OpenShift) successor model** noted for forward-looking estates — TripleO/director is retired (Epoxy 2025.1) and its successor RHOSO runs control-plane services as operators on OpenShift, so the "edit a Heat/TripleO template" persistence step becomes "edit the operator custom resources (CRs)"; existing director-based estates still need the director runbooks above, but new RHOSP work should target the RHOSO operator model? (See `providers/openstack/deployment-tools.md` for the deployment-tool comparison.)

## Why This Matters

The single most common way a *planned* maintenance window turns into an *unplanned* outage is taking a controller into standby without first proving the survivors are quorate. The whole premise of "I can pull one of three controllers for a chassis swap" rests on the other two forming a Galera/RabbitMQ majority. If a second controller is silently degraded — a Galera node stuck in `Donor/Desynced` from a prior incident, a RabbitMQ node that never fully rejoined, a failed Pacemaker resource — then standby on the third drops the cluster to one live datastore node, which loses quorum and stops accepting writes. Every API write begins to fail (500s), and the operator who initiated a "routine" maintenance is now in an outage they caused. The quorum pre-check is therefore not paperwork; it is the step that distinguishes a safe drain from a self-inflicted control-plane outage. It must be performed against the *remaining* nodes specifically, and recorded, before standby.

The **return-to-service verification** is the mirror-image trap. Pacemaker reporting a resource "Started" on the returned node, or RabbitMQ showing the process up, says nothing about whether the *datastore* re-synced. A Galera node can rejoin the Pacemaker cluster and present as healthy while it is still streaming a multi-gigabyte SST, or worse, stuck mid-transfer. During that window the cluster is at N-1 redundancy while the dashboard is green — so the next single failure becomes a quorum loss that nobody expected because "all three controllers are up." The return step must explicitly confirm `wsrep_local_state_comment=Synced` and full `wsrep_cluster_size`, and confirm RabbitMQ queue replication, not merely that processes and resources started.

The **`standby` vs `maintenance-mode` confusion** is a Pacemaker-specific foot-gun with opposite failure modes. `pcs node standby <node>` is "evict this node's resources to the survivors" — exactly what single-node hardware maintenance wants. `pcs property set maintenance-mode=true` is "stop monitoring everything, leave it running un-managed" — what you want when patching Pacemaker/Corosync itself, and catastrophic if you then power the node off (you just killed services Pacemaker was told to ignore). Operators reach for whichever they remember; the runbook must name the correct one for the task and explain the difference, because the wrong choice is an outage in one direction and unwanted failovers in the other.

The **BMC-IP-change triad** is where chassis swaps go wrong weeks after the fact. A new chassis often means a new BMC/iDRAC IP. The obvious update — point Pacemaker's `fence_ipmilan` at the new address — fixes fencing. But on a director-managed estate, Ironic *also* holds that BMC address in driver-info for power management, and *both* the STONITH config and the Ironic registration live in deployment templates that a future `overcloud deploy` will re-assert. Fix only the live Pacemaker config and: (a) the undercloud still can't power-manage the node, and (b) the next deploy reverts your fence-agent fix and re-breaks fencing. Fencing failures are insidious because they are silent until the moment you need a failover — the cluster cannot fence a node it can't reach, so it refuses to fail its resources over, and a routine node failure becomes a hung cluster. The triad — Ironic driver-info, Pacemaker STONITH, deployment templates — must be updated together, and the live-vs-persisted discipline applies to every one of them.

## Common Decisions (ADR Triggers)

### ADR: Single-Node Maintenance — Drain Mechanism (Pacemaker standby vs service-level disable)
**Trigger:** Planning a hardware-maintenance window for one controller in an HA cluster.
**Considerations:**
- On a **Pacemaker-managed** estate (typically director/RHOSP), `pcs node standby <node>` is the correct drain — it relocates the VIP and managed resources to the survivors atomically and Pacemaker prevents resources from returning until `unstandby`.
- On a **keepalived + service-level** estate (typical Kolla-Ansible / OSA), there is no Pacemaker; drain by disabling the node's HAProxy backends and lowering its keepalived priority (or stopping keepalived to move the VIP), plus `openstack compute service set --disable` for any co-located compute role, then stopping services gracefully.
- Either way the **quorum pre-check on survivors** and the **return-verification** are mandatory and identical; only the drain mechanism differs.
- Decision driver: which HA stack the deployment actually runs (see the keepalived-vs-Pacemaker ADR in `control-plane-ha.md`). Do not assume Pacemaker — most community deployments use keepalived and have no `pcs` at all.

### ADR: Director-Based Estate — Repair-in-Place vs Node Replacement vs Migrate to RHOSO/Community
**Trigger:** A director/TripleO controller needs significant hardware work or has failed, on an estate already flagged by TripleO retirement.
**Considerations:**
- **Repair-in-place** (chassis swap, same node identity): lowest churn; requires the BMC-IP triad and NIC-MAC handling but no overcloud topology change. Preferred for a single failed component.
- **Node replacement** via the director replacement workflow: register new Ironic node + ports, update the node-registration inventory and pacemaker-fencing environment file, run the targeted deploy. Heavier; correct when the node identity/hardware generation changes.
- **Migrate off director**: since TripleO is retired (Epoxy 2025.1), a major hardware refresh is a natural decision point to evaluate moving to RHOSO (OpenShift-based, Red Hat) or a community tool (Kolla-Ansible) rather than investing further in director runbooks — weigh existing OpenShift investment and support posture (see `deployment-tools.md`).
- Decision driver: scope of the hardware change, remaining director support horizon, and whether an OpenShift platform already exists.

### ADR: Fence-Agent Configuration Source of Truth (live pcs vs templates)
**Trigger:** A BMC IP/credential change must be applied to STONITH on a director-managed cluster.
**Considerations:**
- Applying via **live `pcs stonith update`** restores fencing immediately but is reverted by the next `overcloud deploy`.
- Applying via **the fencing environment template** then redeploying is durable but slower and runs a full deploy.
- Correct practice is **both**: live update to restore fencing now (fencing gaps are an active risk), then persist to the template so the fix survives. The ADR exists to make the "persist it too" step non-optional, because the live-only fix is the common regression.

## Operational Runbooks

### Runbook: Planned Single-Node Controller Hardware Maintenance / Chassis Replacement

Assumes a 3-controller HA cluster. Adjust node counts for larger clusters (the quorum rule is: survivors must remain a strict majority of the Galera/RabbitMQ membership throughout).

**1. Pre-check — prove the survivors are quorate (load-bearing, do not skip):**
```bash
# On EACH surviving controller (not the one going down):
mysql -e "SHOW STATUS LIKE 'wsrep_cluster_size';"          # = full node count (e.g. 3)
mysql -e "SHOW STATUS LIKE 'wsrep_local_state_comment';"   # = Synced
rabbitmqctl cluster_status                                  # all members joined, no partitions
pcs status                                                  # (Pacemaker estates) no Failed/Stopped resources
```
Abort the window if any survivor is not fully synced/joined — fix that first. Taking a node down now would drop below quorum.

**2. Drain the target node:**
- *Pacemaker estate:* `pcs node standby <node>` — verify with `pcs status` that resources (incl. the VIP) have moved to survivors.
- *Keepalived estate:* disable the node's HAProxy backends (or stop HAProxy on it), stop keepalived so the VIP moves, and `openstack compute service set --disable --disable-reason "maintenance" <host> nova-compute` if it is also a compute host.

**3. Confirm post-drain state:** survivors still show full Galera `wsrep_cluster_size` for the *cluster minus the drained node's writes*, RabbitMQ healthy, VIP responding via the survivors. Expect a brief API blip as the VIP relocates.

**4. Graceful stop + shutdown:** stop OpenStack services on the node, then stop MariaDB/RabbitMQ cleanly (a clean RabbitMQ stop records the node as the last-stopped state; a clean Galera stop updates `grastate.dat`), then OS shutdown.

**5. Physical maintenance / chassis swap.** If the chassis (and thus BMC and/or NICs) changes, see the BMC-IP-change triad and NIC-MAC runbooks below *before* returning to service.

**6. Power on, boot OS, start datastores first**, then OpenStack services.

**7. Return-to-service verification (resync-aware):**
```bash
mysql -e "SHOW STATUS LIKE 'wsrep_local_state_comment';"   # Synced (not Donor/Desynced/Joining)
mysql -e "SHOW STATUS LIKE 'wsrep_cluster_size';"          # back to full count
rabbitmqctl cluster_status                                  # node rejoined, queues replicated
pcs status                                                  # (Pacemaker) resources Started AND monitored
```
Confirm whether Galera did IST (fast) or SST (full transfer) — a long SST means redundancy is reduced until it completes.

**8. Un-drain:** `pcs node unstandby <node>` (Pacemaker) or re-enable HAProxy backends / restart keepalived and `openstack compute service set --enable … nova-compute` (keepalived). Verify the node takes traffic and the cluster is at full redundancy.

### Runbook: Pacemaker / Corosync Day-2 Quick Reference

```bash
pcs status                          # cluster, node, and resource state
pcs node standby <node>             # evict this node's resources to survivors (single-node maintenance)
pcs node unstandby <node>           # return the node to eligibility
pcs property set maintenance-mode=true   # stop monitoring CLUSTER-WIDE, leave resources running un-managed
pcs property set maintenance-mode=false  # resume monitoring
pcs resource move <rsc> <node>      # relocate a resource (creates a location constraint!)
pcs resource clear <rsc>            # remove the constraint left by 'move' so it can rebalance
pcs stonith status                  # fence device state
pcs stonith config                  # inspect fence-agent parameters
pcs stonith fence <node>            # manually fence a node
pcs stonith history                 # fencing events
```
Key distinctions: `standby` moves resources off **one node**; `maintenance-mode` stops monitoring **everywhere** — never power a node off while it is only in `maintenance-mode`. After `pcs resource move`, always `pcs resource clear` or the resource is pinned and won't rebalance.

### Runbook: BMC/iDRAC IP-Change Triad (after a chassis swap on a director-managed estate)

When a controller's BMC IP changes, update **all three** and persist:
```bash
# 1. Ironic driver-info (undercloud power management) — run against the undercloud:
openstack baremetal node set <node> \
  --driver-info ipmi_address=<new-bmc-ip> \
  --driver-info ipmi_username=<user> --driver-info ipmi_password=<pass>
openstack baremetal node validate <node>     # power/management interfaces must pass

# 2. Pacemaker STONITH fence agent (live, restores fencing now) — on a controller:
pcs stonith update <fence-agent-for-node> ipaddr=<new-bmc-ip>   # param may be 'ip=' depending on agent
pcs stonith status

# 3. Deployment templates (persist, or the next deploy reverts 1 and 2):
#    - update the pacemaker-fencing environment file (fence_ipmilan ipaddr for this node)
#    - update the node-registration / instackenv inventory (ipmi address)
#    then re-run the targeted overcloud deploy.
```
Skipping (2) blocks failover (cluster can't fence an unreachable node). Skipping (1) leaves the undercloud unable to power-manage. Skipping (3) silently reverts (1) and (2) on the next deploy.

### Runbook: NIC-MAC Handling on Chassis Swap

If the replacement chassis has different NIC MAC addresses:
```bash
openstack baremetal port list --node <node>             # current ports/MACs
openstack baremetal port set <port-uuid> --address <new-mac>   # or create new ports for the new NICs
```
Also review `os-net-config` / predictable-interface-naming templates if interfaces are keyed by MAC. A swap that fixes the BMC IP but leaves stale NIC MACs typically fails to PXE/provision or comes up with mis-mapped interfaces.

## Reference Links

- [OpenStack Operations Guide — maintenance/availability](https://docs.openstack.org/operations-guide/ops-maintenance.html) — routine maintenance, controller/compute/storage node procedures
- [ClusterLabs Pacemaker documentation](https://clusterlabs.org/pacemaker/doc/) — Pacemaker concepts, `pcs`/`crm` operation, fencing/STONITH
- [Red Hat — Configuring and managing high availability clusters (RHEL HA Add-On)](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/index) — `pcs`, standby vs maintenance-mode, `fence_ipmilan`
- [OpenStack Ironic documentation](https://docs.openstack.org/ironic/latest/) — baremetal node/port management, driver-info, validate, power management
- [Red Hat OpenStack Platform director docs](https://docs.redhat.com/en/documentation/red_hat_openstack_platform/) — Director Installation and Usage; High Availability Deployment and Usage; Replacing Controller Nodes
- [Galera Cluster crash recovery](https://galeracluster.com/library/documentation/crash-recovery.html) — IST/SST, bootstrap, resync verification

## See Also

- `providers/openstack/control-plane-ha.md` — HA *design*: quorum, fencing strategy, keepalived-vs-Pacemaker ADR, Galera/RabbitMQ configuration (this file is the lifecycle counterpart)
- `providers/openstack/operations.md` — *unplanned* incident triage: split-brain, agent flapping, token-key drift, Galera quorum-loss recovery
- `providers/openstack/deployment-tools.md` — deployment-tool selection, TripleO retirement, RHOSO successor, day-1 deploy flow
- `general/operational-runbooks.md` — runbook framework: structure, severity, change-control, postmortem process
