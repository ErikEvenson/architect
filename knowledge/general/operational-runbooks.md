# Operational Runbooks

## Scope

This file covers operational runbook and playbook design decisions: runbook structure and standardization, incident response playbooks, automated vs. manual execution, runbook-as-code tooling, on-call documentation, post-incident review practices, runbook maintenance, integration with monitoring and alerting, game day validation, and SRE operational practices. For alerting and monitoring tool selection, see `general/observability.md`. For disaster recovery runbooks specifically, see `general/disaster-recovery.md`.

## Checklist

- [ ] **[Critical]** Define a standard runbook structure that every runbook follows — trigger condition (what alert or symptom initiates the runbook), prerequisites (access, tools, permissions required), step-by-step procedure (numbered, unambiguous actions with expected output at each step), rollback procedure (how to undo changes if the fix causes regression), verification steps (how to confirm the issue is resolved), and escalation path (who to contact if the runbook does not resolve the issue within a defined time window)
- [ ] **[Critical]** Create incident response playbooks for the most common failure scenarios — disk full (identify consumer, clean or expand, set threshold alerts), certificate expiry (identify affected services, renew or rotate, update trust stores, verify TLS handshake), service crash loops (check logs, identify root cause, restart or roll back deployment, verify health checks pass), memory leak (identify leaking process, capture heap dump if safe, restart service, schedule root cause analysis), and database failover (verify replication state, promote replica, update connection strings, validate data integrity)
- [ ] **[Critical]** Define severity levels with clear, objective criteria that remove ambiguity from incident classification — SEV1 (complete service outage or data loss affecting customers, all hands on deck, executive notification), SEV2 (degraded service or partial outage affecting a subset of users, on-call engineer plus backup), SEV3 (minor issue with workaround available, on-call engineer during business hours), SEV4 (cosmetic or low-impact issue, backlog ticket); each severity level must specify expected response time, communication cadence, and who is authorized to declare that severity
- [ ] **[Critical]** Establish escalation paths that are unambiguous and account for unavailability — define primary on-call, secondary on-call, team lead, engineering manager, and VP-level escalation with specific timeouts at each level (e.g., escalate to secondary if primary does not acknowledge within 5 minutes); include out-of-band contact methods (phone numbers, not just Slack) for when primary communication channels are part of the outage
- [ ] **[Critical]** Determine which runbooks should be automated vs. remain manual — automate runbooks that are executed frequently (more than once per week), have well-understood steps with no ambiguity, carry low risk of making the situation worse, and involve repetitive toil; keep runbooks manual when they require human judgment (e.g., deciding whether to fail over a database), involve destructive actions (e.g., data deletion), or are rarely executed and the automation maintenance cost exceeds the manual execution cost
- [ ] **[Recommended]** Implement runbook-as-code using orchestration tooling — AWS Systems Manager Automation documents, Azure Automation Runbooks, Ansible playbooks triggered by alerting, or Rundeck jobs with approval gates; store runbook code in version control alongside application code so changes are reviewed, tested, and auditable; include human-in-the-loop approval steps for destructive or high-risk actions even in automated runbooks
- [ ] **[Recommended]** Define post-incident review (blameless postmortem) process and structure — every SEV1 and SEV2 incident must have a postmortem within 5 business days; structure includes timeline of events, root cause analysis (using 5 Whys or fishbone diagram), what went well, what could be improved, and action items with owners and due dates; track action item completion and report on closure rates; assess SLO impact and error budget consumption from the incident
- [ ] **[Recommended]** Integrate runbooks with monitoring and alerting systems so that the correct runbook is linked directly from each alert — configure PagerDuty, Opsgenie, or Grafana OnCall to include a runbook URL in every alert notification; for automated runbooks, configure alert-triggered execution (e.g., CloudWatch Alarm triggers SSM Automation, Prometheus alert triggers Ansible playbook via webhook) with safeguards against repeated execution during alert flapping
- [ ] **[Recommended]** Establish a runbook maintenance cadence — review every runbook at least quarterly for accuracy (infrastructure changes may invalidate steps), assign an owner to each runbook who is responsible for keeping it current, retire runbooks for decommissioned services, and version-control all runbooks so changes are auditable; stale runbooks are worse than no runbooks because they create false confidence
- [ ] **[Recommended]** Conduct game days and chaos engineering exercises to validate runbooks under realistic conditions — schedule quarterly game days that simulate real failure scenarios (inject failures using Chaos Monkey, Litmus, Gremlin, or manual fault injection), time the response, and identify gaps in runbooks, tooling, or team knowledge; use game day findings to update runbooks and close coverage gaps before actual incidents expose them
- [ ] **[Recommended]** Define SLIs, SLOs, and error budgets that drive operational priorities — establish SLIs for each service (availability, latency, throughput), set SLOs below 100% to create an error budget that funds experimentation and deployments, and use error budget burn rate to trigger operational responses (e.g., when error budget is 50% consumed mid-month, freeze non-critical deployments and focus on reliability); connect error budget status to on-call workload and runbook priorities
- [ ] **[Optional]** Implement communication templates for incident response — pre-written templates for status page updates, internal Slack announcements, customer-facing emails, and executive briefings at each severity level; templates reduce cognitive load during high-stress incidents and ensure consistent, professional communication; include templates for incident declaration, periodic updates, resolution notification, and postmortem summary
- [ ] **[Optional]** Build a knowledge base that complements runbooks — distinguish between runbooks (step-by-step procedures for known problems with specific triggers) and knowledge base articles (reference documentation for understanding systems, troubleshooting novel issues, and onboarding); use a searchable platform (Confluence, GitBook, internal wiki) and cross-link between knowledge base articles and runbooks; measure knowledge base effectiveness by tracking time-to-resolution trends for on-call engineers
- [ ] **[Optional]** Implement toil measurement and reduction tracking aligned with SRE practices — define toil as manual, repetitive, automatable operational work that scales with service size; measure toil hours per on-call rotation, identify top toil sources, and set targets for toil reduction (e.g., automate top 3 toil sources per quarter); track toil reduction over time as a team health metric alongside incident frequency and MTTR

## Why This Matters

Operational runbooks are the bridge between alerting systems that detect problems and engineers who fix them. Without well-structured runbooks, incident response depends entirely on tribal knowledge — whichever engineer happens to remember how to fix a particular problem. This creates single points of failure in the on-call rotation, extends mean time to resolution (MTTR) when the knowledgeable engineer is unavailable, and makes onboarding new team members unnecessarily painful. A 15-minute fix becomes a 2-hour investigation when the engineer has never seen the problem before and has no documented procedure to follow.

The distinction between automated and manual runbooks is a critical cost-benefit decision. Automating every runbook sounds appealing but carries real risks: automated remediation for a misdiagnosed problem can make things worse (restarting a service that is crash-looping due to a configuration error just restarts the crash loop faster), and maintaining automation for rarely-triggered runbooks costs more in engineering time than the manual execution it replaces. The most effective approach is to automate high-frequency, low-risk remediations (disk cleanup, certificate renewal, service restart) while keeping human judgment in the loop for destructive actions, complex failovers, and novel failure modes.

Post-incident review is where operational maturity compounds. Organizations that rigorously conduct blameless postmortems, track action items to completion, and feed findings back into runbooks and architecture decisions experience fewer repeat incidents over time. Organizations that skip postmortems or treat them as blame exercises repeat the same incidents, burn out their on-call engineers, and accumulate operational debt that eventually manifests as a major outage. The postmortem is also the primary mechanism for connecting incidents to SLO impact — without this feedback loop, error budgets are just numbers on a dashboard rather than operational decision-making tools.

## Common Decisions (ADR Triggers)

### ADR: Runbook Hosting and Tooling

**Context:** The organization needs to decide where runbooks are authored, stored, and executed.

**Options:**

| Criterion | Wiki/Docs (Confluence, GitBook) | Git Repository (Markdown) | Runbook-as-Code (SSM, Ansible, Rundeck) | Integrated Platform (PagerDuty Runbook Automation, Shoreline) |
|---|---|---|---|---|
| Authoring Experience | Rich editor, non-engineers can contribute | Plain text, requires git workflow | Code/YAML, requires engineering skills | Guided UI with code blocks |
| Version Control | Built-in but limited diff/review | Full git history, PR review | Full git history, PR review | Platform-managed versioning |
| Execution | Manual (copy-paste commands) | Manual (copy-paste commands) | Automated or semi-automated | Automated with approval gates |
| Alert Integration | Link from alert to wiki page | Link from alert to repo page | Trigger from alert webhook | Native alert-to-runbook binding |
| Searchability | Full-text search built in | Requires separate search tooling | Searchable via platform | Built-in search and tagging |
| Maintenance Burden | Low authoring effort, high staleness risk | Moderate (PR process enforces review) | Higher (code must be tested and maintained) | Moderate (platform manages execution) |
| Best Fit | Small teams, simple operations | Engineering-heavy teams, GitOps culture | Mature SRE teams automating remediation | Organizations wanting turnkey automation |

**Decision drivers:** Team size and technical depth, frequency of runbook execution (manual is fine for rare events, automation is essential for frequent ones), existing tooling ecosystem (GitOps shop vs. wiki-centric), and budget for dedicated runbook platforms.

### ADR: Incident Severity Classification Model

**Context:** The team must define severity levels that determine response urgency, staffing, communication requirements, and escalation timing.

**Options:**
- **4-level model (SEV1-SEV4):** Most common. SEV1 for total outage, SEV2 for degraded service, SEV3 for minor issues with workarounds, SEV4 for cosmetic or backlog items. Simple to understand, sufficient for most organizations.
- **5-level model with P0:** Adds a P0/SEV0 for existential threats (data breach, complete platform failure, safety-critical systems). Useful for organizations where the distinction between "major outage" and "company-threatening event" drives materially different responses.
- **Impact/urgency matrix (ITIL-style):** Classifies incidents on two dimensions (impact: how many users affected; urgency: how quickly must it be resolved) to derive priority. More nuanced but more complex to apply under pressure. Common in enterprises with ITSM processes.

**Decision drivers:** Organizational complexity, number of on-call teams that need a shared classification language, regulatory requirements for incident classification, and whether the model must integrate with an existing ITSM platform (ServiceNow, Jira Service Management).

### ADR: Post-Incident Review Process

**Context:** The organization needs a structured process for learning from incidents and preventing recurrence.

**Options:**
- **Lightweight postmortem (template in Slack/doc):** Fill out a brief template (what happened, root cause, action items) within 48 hours. Low overhead, high completion rate. Risk of shallow analysis that misses systemic issues.
- **Formal blameless postmortem (dedicated meeting + document):** Scheduled meeting with all responders, structured timeline reconstruction, 5 Whys root cause analysis, action items with owners and due dates, published to the organization. Higher overhead but deeper analysis. Standard SRE practice.
- **Learning review (resilience engineering approach):** Focuses on what went right in addition to what went wrong, examines how the system adapted, and identifies systemic contributors rather than single root causes. Most thorough analysis. Requires facilitator training and organizational maturity.

**Decision drivers:** Incident frequency (high-frequency environments need lightweight processes to avoid postmortem fatigue), organizational culture (blameless culture is a prerequisite for effective postmortems), and whether action item completion is tracked and enforced.

### ADR: Automated Remediation Strategy

**Context:** The team must decide which operational responses to automate and what safeguards to implement.

**Options:**
- **No automation (manual runbooks only):** All remediation requires human execution. Simplest to implement. Highest MTTR. Acceptable for small environments with low incident frequency.
- **Auto-remediation for known issues:** Automate specific, well-understood remediations (restart crashed service, clear disk space, rotate expiring certificate) triggered by alerts. Requires guardrails: cooldown periods to prevent repeated execution, circuit breakers to stop automation if the issue recurs, and audit logging of all automated actions.
- **Full autonomous remediation (AIOps):** ML-driven anomaly detection and automated response. Highest investment. Risk of unexpected automated actions. Appropriate only for very large-scale environments where manual response cannot keep pace with incident volume.

**Recommendation:** Start with manual runbooks for all scenarios. Automate the top 3-5 most frequent, lowest-risk remediations. Add human-in-the-loop approval for anything destructive. Expand automation incrementally based on confidence gained from game day testing.

## Reference Links

- [PagerDuty Incident Response Guide](https://response.pagerduty.com/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)
- [Rundeck](https://www.rundeck.com/)
- [AWS Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)
- [Azure Automation](https://learn.microsoft.com/en-us/azure/automation/)
- [Gremlin (Chaos Engineering)](https://www.gremlin.com/)
- [Litmus Chaos](https://litmuschaos.io/)
- [OpenSLO](https://openslo.com/)

## Per-Provider Operations Files

This file covers the **framework** layer of operational runbooks -- structure, severity classification, automation decisions, postmortem process. The **implementation** layer -- the concrete commands, diagnostic-capture flows, daemon-level troubleshooting, and pre-flight branching for a specific provider -- lives in per-provider operations files. When designing a runbook for a particular technology, load both the framework guidance here and the per-provider operations file alongside it.

- `providers/ceph/operations.md` -- Ceph: OSD-down branching, admin-socket flows, `noout` discipline, cephadm vs non-containerized vs Rook restart procedures
- `providers/openstack/operations.md` -- OpenStack: control-plane triage order, Galera quorum-loss recovery, RabbitMQ split-brain, Neutron agent flapping, Keystone Fernet keys
- `providers/kubernetes/operations.md` -- Kubernetes lifecycle: Helm/Kustomize, GitOps, cluster upgrades, etcd backup strategy
- `providers/kubernetes/incident-response.md` -- Kubernetes runtime: pod stuck Pending, CrashLoopBackOff, node NotReady, etcd quorum loss, control-plane recovery
- `providers/openshift/operations.md` -- OpenShift: ClusterOperator degraded, MCO degraded pools, CVO stuck upgrades, OLM subscription failures, etcd disaster recovery
- `providers/vmware/operations.md` -- VMware: VCSA File-Based Backup recovery, ESXi PSOD capture, vSAN object inaccessibility, vSphere HA cause vs effect
- `providers/nutanix/operations.md` -- Nutanix: CVM down branching, `cluster stop`/`start`, AOS upgrade rollback, Prism Central recovery, NCC-first triage
- `providers/atlassian/jsm-operations.md` -- Jira Service Management: SLA mechanics, automation rule limits, queue design, linked-issue discipline
- `providers/servicenow/itsm-operations.md` -- ServiceNow: SLA engine, `hold_reason`, Performance Analytics, state model
- `providers/okta/lifecycle-management.md` -- Okta: lifecycle states, deactivation flows, Universal Directory mappings

## See Also

- `general/observability.md` — Alerting, SLO frameworks, and on-call tooling that trigger and inform runbooks
- `general/disaster-recovery.md` — DR-specific runbooks, failover procedures, and DR testing methodology
- `general/deployment.md` — Deployment rollback procedures that runbooks may reference during incident response
- `general/ci-cd.md` — CI/CD pipeline failures that may require operational runbooks for remediation
- `general/security.md` — Security incident response overlaps with operational runbooks; coordinate playbooks for breach scenarios
- `general/tls-certificates.md` — Certificate lifecycle management and expiry remediation procedures
