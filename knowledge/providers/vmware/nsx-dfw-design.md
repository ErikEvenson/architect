# NSX Distributed Firewall Policy Design

## Scope

NSX Distributed Firewall (DFW) policy design: security posture selection (default deny vs allow), policy category ordering (Emergency, Infrastructure, Environment, Application), tag-based grouping, NSX Intelligence traffic analysis, Identity Firewall, and DFW rule lifecycle management.


## Checklist

- [ ] **[Critical]** Define the target security posture: default deny (zero-trust) or default allow with planned transition to deny
- [ ] **[Critical]** Place NSX Manager, vCenter, and nested ESXi on the DFW exclusion list to prevent management plane lockout
- [ ] **[Critical]** Use tag-based groups for all VM-to-VM rules — avoid static IP-based groups for dynamic workloads
- [ ] **[Critical]** Implement rules in the correct policy category order: Emergency, Infrastructure, Environment, Application
- [ ] **[Critical]** Enable logging on all drop/reject rules and on allow rules for sensitive segments (PCI, HIPAA)
- [ ] **[Recommended]** Deploy infrastructure rules first (DNS, NTP, AD, monitoring) before enabling any deny rules
- [ ] **[Recommended]** Use NSX Intelligence to baseline traffic flows before writing application microsegmentation rules
- [ ] **[Recommended]** Establish a tag taxonomy and naming convention before creating any groups (e.g., `env:prod`, `app:payroll`, `tier:web`)
- [ ] **[Recommended]** Test all rule changes in a non-production environment or use DFW draft/publish workflow to stage changes
- [ ] **[Recommended]** Set "Applied To" scope on every rule to limit DFW resource consumption per host
- [ ] **[Recommended]** Document each policy category's purpose and ownership (network team vs. security team vs. app team)
- [ ] **[Optional]** Implement Identity Firewall (IDFW) with Active Directory groups for user-based microsegmentation on VDI/RDS
- [ ] **[Optional]** Configure time-based rules for emergency access (auto-expire after defined window)
- [ ] **[Optional]** Integrate DFW logs with Aria Operations for Logs (formerly vRealize Log Insight) for centralized analysis and alerting
- [ ] **[Optional]** Monitor DFW rule hit counts and remove unused rules quarterly to prevent rule sprawl

## Why This Matters

The NSX Distributed Firewall enforces security policy at the vNIC level of every virtual machine, making it the foundation of east-west microsegmentation in VMware environments. Unlike perimeter firewalls that only inspect north-south traffic, the DFW inspects every packet between VMs — even VMs on the same host, same segment, and same VLAN. This is the primary mechanism for stopping lateral movement after an attacker breaches the perimeter.

A poorly designed DFW policy creates one of two problems: either it is too permissive (rules are allow-any or IP-based and stale) and provides no real security, or it is too restrictive without proper planning and causes production outages when legitimate traffic is blocked. Both outcomes erode trust in the microsegmentation program.

Policy category ordering is the single most important concept to understand. NSX processes rules in a strict category hierarchy — Emergency first, then Infrastructure, then Environment, then Application. A rule in a higher category always takes precedence over a rule in a lower category, regardless of the rule's position within that category. Placing a rule in the wrong category is one of the most common and difficult-to-diagnose mistakes.

## Common Decisions (ADR Triggers)

### ADR: Default Rule Action — Deny vs. Allow

**Context:** The default rule at the bottom of the DFW rule table determines what happens to traffic that matches no explicit rule.

**Options:**
- **Default deny (zero-trust):** All traffic is blocked unless explicitly allowed. Maximum security. Requires comprehensive rule set before enabling — any missing rule causes an outage.
- **Default allow (permissive):** All traffic is permitted unless explicitly blocked. Easy initial deployment. Provides no protection against lateral movement until rules are added.
- **Phased transition (recommended):** Start with default allow + logging on all traffic. Use NSX Intelligence or log analysis to discover actual traffic flows over 2-4 weeks. Write allow rules for discovered flows. Switch to default deny.

**Recommendation:** Phased transition. The risk of immediate default deny in a brownfield environment is production outages from unknown dependencies. The risk of permanent default allow is that microsegmentation provides no actual security.

**Implementation steps for phased transition:**
1. Enable DFW with default allow
2. Turn on logging for the default rule (expect high log volume — size syslog accordingly)
3. Run NSX Intelligence flow analysis for 14-30 days
4. Create allow rules for all observed legitimate flows
5. Switch default rule to deny in a maintenance window
6. Monitor for blocked traffic and add missing rules

### ADR: Group Strategy — Tags vs. IP Sets vs. Segments

**Context:** DFW rules reference source and destination groups. The group membership mechanism determines how dynamic and maintainable the policy is.

**Options:**

| Group Type | Membership | Pros | Cons | Best For |
|---|---|---|---|---|
| Tag-based | VMs with matching NSX tag | Dynamic — new VMs auto-join when tagged; follows vMotion | Requires tagging discipline in provisioning workflow | All VM-to-VM rules |
| IP-based | Static IP addresses or ranges | Works for physical devices, external systems | Stale when IPs change; does not follow DHCP | Physical servers, external devices |
| Segment-based | All VMs on a segment | Simple for broad rules | Too coarse for microsegmentation | Infrastructure rules (allow all VMs on mgmt segment) |
| AD group-based (IDFW) | Users in Active Directory group | User-follows-VM policy | Requires AD integration, Guest Introspection | VDI, RDS, shared workstations |

**Recommendation:** Use tag-based groups as the default. Reserve IP-based groups for physical devices and external systems that cannot be tagged. Use segment-based groups only for broad infrastructure rules.

### ADR: Tag Taxonomy Design

**Context:** Tags are the foundation of group membership. A poor taxonomy leads to tag sprawl and inconsistent policy.

**Recommended taxonomy (multi-axis):**

| Axis | Tag Scope | Example Tags | Purpose |
|---|---|---|---|
| Environment | `env` | `env:prod`, `env:staging`, `env:dev` | Environment isolation rules |
| Application | `app` | `app:payroll`, `app:crm`, `app:inventory` | Application microsegmentation |
| Tier | `tier` | `tier:web`, `tier:app`, `tier:db` | Intra-app tiering rules |
| Compliance | `compliance` | `compliance:pci`, `compliance:hipaa` | Compliance zone rules |
| OS | `os` | `os:linux`, `os:windows` | OS-specific infra rules |

**Tagging enforcement:** Integrate tagging into the VM provisioning workflow (vRA, Terraform, Ansible). A VM without tags gets only infrastructure-level access and default deny for application traffic — this incentivizes proper tagging.

### ADR: Rule Logging Strategy

**Context:** DFW can log every rule hit, but logging all traffic generates enormous volume and impacts syslog infrastructure.

**Options:**
- **Log all:** Complete visibility. Extremely high volume (thousands of log events per second in large environments). Requires dedicated syslog infrastructure.
- **Log drops only:** Captures blocked traffic for troubleshooting and security analysis. Moderate volume. Misses allowed-but-suspicious flows.
- **Log drops + sensitive segment allows:** Log all drops globally; additionally log allows on PCI, HIPAA, and other compliance-scoped segments. Best balance.
- **No logging:** No visibility. Not recommended under any circumstances.

**Recommendation:** Log all drops globally. Log allows on compliance-scoped segments. Send to Aria Operations for Logs or external SIEM. Size syslog at 5,000-10,000 events/second for a 500-VM environment with default deny.

### ADR: Policy Category Ownership

**Context:** Multiple teams need to manage DFW rules. Category-based delegation prevents conflicts.

**Recommended ownership model:**

| Category | Owner | Purpose | Change Frequency |
|---|---|---|---|
| Emergency | Security / SOC team | Incident response, lockdown | Rare (during incidents) |
| Infrastructure | Network / platform team | DNS, NTP, AD, monitoring, vMotion | Low (quarterly review) |
| Environment | Security / compliance team | Zone isolation (prod/dev/staging) | Low (new environments) |
| Application | Application teams (delegated) | Per-app microsegmentation | Moderate (deployments) |

## Reference Architectures

### Architecture 1: Standard Enterprise DFW Policy Stack

**Scenario:** 500-VM VMware environment with production, staging, and development zones. Compliance requirement for PCI-scoped workloads. Default deny target state.

```
DFW Policy Processing Order (top to bottom):
==============================================

EMERGENCY CATEGORY (Security Team)
+------------------------------------------------------------------+
| Rule 1001 | Src: Security-Admin-IPs | Dst: Any        | SSH/22  |
|           | Action: ALLOW  | Applied To: All | Log: Yes          |
|           | Note: Break-glass admin access during incidents       |
+------------------------------------------------------------------+
| Rule 1002 | Src: Compromised-IPs   | Dst: Any         | Any     |
|           | Action: DROP   | Applied To: All | Log: Yes          |
|           | Note: Block known-bad IPs (updated by SOC)            |
+------------------------------------------------------------------+

INFRASTRUCTURE CATEGORY (Network Team)
+------------------------------------------------------------------+
| Rule 2001 | Src: All-VMs           | Dst: DNS-Servers  | 53     |
|           | Action: ALLOW  | Applied To: All | Log: No           |
+------------------------------------------------------------------+
| Rule 2002 | Src: All-VMs           | Dst: NTP-Servers  | 123    |
|           | Action: ALLOW  | Applied To: All | Log: No           |
+------------------------------------------------------------------+
| Rule 2003 | Src: All-VMs           | Dst: AD-Servers   | 389,636|
|           | Action: ALLOW  | Applied To: All | Log: No           |
|           | Note: LDAP and LDAPS for domain-joined VMs            |
+------------------------------------------------------------------+
| Rule 2004 | Src: Monitoring-Servers | Dst: All-VMs     | 161,   |
|           |                        |                   | 9100   |
|           | Action: ALLOW  | Applied To: All | Log: No           |
|           | Note: SNMP and Prometheus node_exporter                |
+------------------------------------------------------------------+
| Rule 2005 | Src: All-VMs           | Dst: Syslog-Servers| 514   |
|           | Action: ALLOW  | Applied To: All | Log: No           |
+------------------------------------------------------------------+
| Rule 2006 | Src: Backup-Servers    | Dst: All-VMs      | 443,   |
|           |                        |                    | 902    |
|           | Action: ALLOW  | Applied To: All | Log: No           |
|           | Note: Backup agent and VADP NBD transport              |
+------------------------------------------------------------------+

ENVIRONMENT CATEGORY (Security Team)
+------------------------------------------------------------------+
| Rule 3001 | Src: Env-Prod          | Dst: Env-Dev      | Any    |
|           | Action: DROP   | Applied To: DFW | Log: Yes          |
|           | Note: Prod cannot initiate to dev                     |
+------------------------------------------------------------------+
| Rule 3002 | Src: Env-Dev           | Dst: Env-Prod     | Any    |
|           | Action: DROP   | Applied To: DFW | Log: Yes          |
|           | Note: Dev cannot initiate to prod                     |
+------------------------------------------------------------------+
| Rule 3003 | Src: Env-Staging       | Dst: Env-Prod     | Any    |
|           | Action: DROP   | Applied To: DFW | Log: Yes          |
|           | Note: Staging cannot initiate to prod                  |
+------------------------------------------------------------------+
| Rule 3004 | Src: PCI-Zone          | Dst: Non-PCI-Zone | Any    |
|           | Action: DROP   | Applied To: DFW | Log: Yes          |
|           | Note: PCI isolation — only allowed flows via app rules |
+------------------------------------------------------------------+

APPLICATION CATEGORY (Application Teams)
+------------------------------------------------------------------+
| Rule 4001 | Src: App-Payroll-Web   | Dst: App-Payroll-App | 8443 |
|           | Action: ALLOW  | Applied To: App-Payroll | Log: Yes  |
|           | Note: Web tier to app tier (TLS)                      |
+------------------------------------------------------------------+
| Rule 4002 | Src: App-Payroll-App   | Dst: App-Payroll-DB  | 5432 |
|           | Action: ALLOW  | Applied To: App-Payroll | Log: Yes  |
|           | Note: App tier to PostgreSQL                          |
+------------------------------------------------------------------+
| Rule 4003 | Src: App-Payroll-Web   | Dst: App-Payroll-DB  | Any  |
|           | Action: DROP   | Applied To: App-Payroll | Log: Yes  |
|           | Note: Explicit deny — web must never reach DB directly|
+------------------------------------------------------------------+
| ...       | Additional application rule sets                      |
+------------------------------------------------------------------+

DEFAULT RULE
+------------------------------------------------------------------+
| Rule 9999 | Src: Any               | Dst: Any           | Any   |
|           | Action: DROP   | Applied To: DFW | Log: Yes          |
|           | Note: Default deny — zero trust baseline               |
+------------------------------------------------------------------+
```

**Group definitions for this architecture:**

| Group Name | Membership Criteria | Type |
|---|---|---|
| All-VMs | All virtual machines (built-in) | System |
| DNS-Servers | Tag: `role:dns` | Tag-based |
| NTP-Servers | Tag: `role:ntp` | Tag-based |
| AD-Servers | Tag: `role:ad` | Tag-based |
| Monitoring-Servers | Tag: `role:monitoring` | Tag-based |
| Syslog-Servers | Tag: `role:syslog` | Tag-based |
| Backup-Servers | Tag: `role:backup` | Tag-based |
| Security-Admin-IPs | IP Set: 10.1.50.0/24 | IP-based |
| Compromised-IPs | IP Set: (dynamically updated) | IP-based |
| Env-Prod | Tag: `env:prod` | Tag-based |
| Env-Dev | Tag: `env:dev` | Tag-based |
| Env-Staging | Tag: `env:staging` | Tag-based |
| PCI-Zone | Tag: `compliance:pci` | Tag-based |
| Non-PCI-Zone | NOT Tag: `compliance:pci` | Tag-based (negated) |
| App-Payroll-Web | Tags: `app:payroll` AND `tier:web` | Tag-based (AND) |
| App-Payroll-App | Tags: `app:payroll` AND `tier:app` | Tag-based (AND) |
| App-Payroll-DB | Tags: `app:payroll` AND `tier:db` | Tag-based (AND) |

### Architecture 2: Phased Migration from Default Allow to Default Deny

**Scenario:** Brownfield environment with 300 VMs, no existing microsegmentation. Goal is zero-trust within 90 days without production outages.

**Phase 1 — Foundation (Weeks 1-2):**
```
Actions:
  - Add NSX Manager, vCenter, ESXi management VMkernel to exclusion list
  - Deploy infrastructure rules (DNS, NTP, AD, monitoring, backup)
  - Set default rule to ALLOW with logging enabled
  - Configure syslog destination (Aria Operations for Logs or SIEM)
  - Validate: all VMs can still reach infrastructure services
```

**Phase 2 — Discovery (Weeks 3-6):**
```
Actions:
  - Enable NSX Intelligence (requires NSX 3.2+ or NSX 4.x)
  - Collect traffic flow data for 21-30 days
  - NSX Intelligence generates recommended rule sets per application
  - Review auto-discovered application boundaries
  - Validate: application owners confirm discovered flows are legitimate
  - Begin tagging VMs: env, app, tier, compliance axes
```

**Phase 3 — Environment Isolation (Weeks 7-8):**
```
Actions:
  - Create environment groups (prod, staging, dev)
  - Deploy environment isolation rules (block cross-env traffic)
  - Default rule remains ALLOW (catches intra-environment traffic)
  - Monitor for blocked cross-env traffic that should be allowed
  - Create exception rules for legitimate cross-env flows (e.g., CI/CD)
  - Validate: no production impact, cross-env isolation confirmed
```

**Phase 4 — Application Microsegmentation (Weeks 9-12):**
```
Actions:
  - Deploy application rules starting with least critical apps
  - For each application:
    1. Create tag-based groups (web, app, db tiers)
    2. Apply NSX Intelligence recommended rules
    3. Set "Applied To" scope to the application group
    4. Test in non-production first
    5. Deploy to production with allow + log
    6. After 7 days with no unexpected blocks, consider app complete
  - Validate: application-level traffic flows match expected patterns
```

**Phase 5 — Default Deny (Week 13):**
```
Actions:
  - Schedule maintenance window
  - Change default rule from ALLOW to DROP (keep logging)
  - Monitor for blocked traffic in real-time during window
  - Have rollback plan: change default rule back to ALLOW
  - Keep "break-glass" emergency allow rule ready (disabled)
  - Validate: no production impact, all legitimate traffic covered
```

### Architecture 3: DFW Capacity Planning and Performance

**Scenario:** Large environment approaching DFW scale limits. Need to understand capacity boundaries and optimization.

**NSX DFW capacity guidelines (NSX 4.x, verify against current release notes):**

| Parameter | Limit | Notes |
|---|---|---|
| Rules per transport node (host) | 10,000 | Across all categories; "Applied To" reduces per-host count |
| DFW rule sections | 10,000 | Across all categories |
| Groups (total) | 10,000 | Includes nested group members |
| IP sets per group | 4,000 | Large IP sets impact commit time |
| Tags per VM | 25 | Across all tag scopes |
| VMs per group | 500 (effective) | No hard limit, but large groups slow commit |

**Performance optimization strategies:**

- **Use "Applied To" on every rule:** A rule applied to "DFW" (all hosts) consumes memory on every host. A rule applied to a specific group only deploys to hosts running those VMs. This is the single most impactful optimization.
- **Consolidate rules with service groups:** Instead of 5 rules allowing ports 80, 443, 8080, 8443, 9090, create one service group and one rule.
- **Avoid overlapping rules:** Rules that match the same traffic in multiple categories waste processing cycles. Use the category hierarchy intentionally.
- **Review and prune quarterly:** Query rule hit counts via NSX API (`GET /policy/api/v1/infra/domains/default/security-policies/{policy-id}/rules/{rule-id}/statistics`). Rules with zero hits for 90 days are candidates for removal.
- **Limit IP-based groups:** Large IP sets (hundreds of entries) increase rule commit time. Prefer tag-based groups where possible.

**Exclusion list — VMs that must be excluded from DFW processing:**

| VM | Reason |
|---|---|
| NSX Manager (all nodes) | DFW rules could block management plane communication |
| vCenter Server | Must remain reachable for ESXi management and VADP |
| Nested ESXi (if lab) | DFW on nested ESXi causes unpredictable behavior |
| Partner service VMs | Guest Introspection, network introspection service VMs |

**Common mistakes and how to avoid them:**

| Mistake | Impact | Prevention |
|---|---|---|
| Rule in wrong category | Rule processed at wrong priority; unexpected allow or deny | Document which category each rule type belongs in; use naming conventions |
| IP-based group for dynamic VMs | VM gets new IP via DHCP; rule no longer matches | Use tag-based groups for all VMs; reserve IP groups for physical devices |
| Missing "Applied To" scope | Rule deployed to all 50 hosts instead of 3 relevant hosts | Require "Applied To" in rule review checklist; never use "DFW" for app rules |
| No logging on drop rules | Cannot troubleshoot connectivity issues; no audit trail | Enable logging on all drop/reject rules as a policy |
| Emergency rule left enabled | Broad allow rule from incident response becomes permanent backdoor | Set calendar reminder; use time-based rules if available; review emergency category weekly |
| No exclusion list for management | DFW blocks NSX Manager or vCenter; loss of management plane | Add management VMs to exclusion list before enabling any deny rules |
| Testing rules in production | Rule typo blocks production traffic | Always test in non-production; use DFW draft mode to stage and review before publish |

## See Also

- `providers/vmware/networking.md` -- NSX overlay networking and gateway design
- `providers/vmware/security.md` -- VMware security controls including microsegmentation
- `providers/vmware/observability.md` -- NSX Intelligence and DFW log analysis
