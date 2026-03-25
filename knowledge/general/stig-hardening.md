# STIG (Security Technical Implementation Guide) Hardening

## Scope

This file covers **STIG compliance and security hardening** including STIG discovery, SCAP scanning, remediation workflows, VMware ESXi hardening, FIPS 140-2 mode, and continuous compliance. It does not cover general security architecture or threat modeling; for those, see `general/security.md`.

## Checklist

- [ ] **[Critical]** Have all applicable STIGs been identified and downloaded from cyber.mil for every component in the environment (OS, hypervisor, database, application server, network device, container platform), and are they the current published versions?
- [ ] **[Critical]** Are all CAT I (Critical) findings remediated or documented with an approved POA&M (Plan of Action and Milestones) before the system receives an ATO (Authority to Operate)?
- [ ] **[Critical]** Is STIG remediation tested in a non-production environment first, since applying STIG settings blindly can break application functionality, disable management interfaces, or cause boot failures?
- [ ] **[Critical]** Are FIPS 140-2/140-3 validated cryptographic modules enabled where required (federal/DoD systems), including TLS cipher suite restrictions, SSH algorithm restrictions, and key management changes that impact connectivity between components?
- [ ] **[Critical]** Is a SCAP scanning tool deployed (DISA SCC, OpenSCAP, Nessus with STIG audit files) and are baseline scans completed before and after remediation to document compliance posture with auditable evidence?
- [ ] **[Recommended]** Are VMware-specific STIGs (ESXi 8, vCenter 8, NSX, vSAN) remediated using PowerCLI automation scripts rather than manual console changes, ensuring consistency across all hosts and repeatability during rebuilds?
- [ ] **[Recommended]** Is ESXi lockdown mode enabled (Normal or Strict) per STIG requirements, with the exception users list documented and limited to service accounts that require direct host access (backup agents, monitoring)?
- [ ] **[Recommended]** Are vSphere Configuration Profiles (or Host Profiles in older versions) used to enforce STIG-required ESXi settings at the cluster level, with drift detection alerting when hosts deviate from the compliant baseline?
- [ ] **[Recommended]** Is continuous compliance scanning scheduled (weekly minimum, daily recommended) with automated alerting on drift, rather than treating STIG compliance as a point-in-time assessment?
- [ ] **[Recommended]** Are POA&M entries maintained for every STIG finding that cannot be remediated, with documented operational justification, compensating controls, risk acceptance authority signature, and a timeline for remediation?
- [ ] **[Recommended]** Is the STIG remediation process integrated into the infrastructure-as-code pipeline, so new deployments are STIG-compliant from first boot rather than hardened after deployment?
- [ ] **[Optional]** Is an automated remediation capability deployed (Ansible STIG roles, Chef InSpec, Puppet modules) that can re-apply STIG settings on drift detection, reducing manual effort for continuous compliance?
- [ ] **[Optional]** Are STIG Viewer checklists (.ckl files) maintained per system and stored in a configuration management database or artifact repository for audit evidence and historical compliance tracking?
- [ ] **[Optional]** Is a STIG exception review board (or equivalent governance process) established to evaluate POA&M entries, approve risk acceptances, and track remediation timelines across the portfolio?

## Why This Matters

STIGs are the DoD's mandatory security configuration baselines, published by DISA (Defense Information Systems Agency). For any system operating on a DoD network or processing government data, STIG compliance is required for receiving an Authority to Operate (ATO). Beyond government requirements, STIGs represent well-researched security hardening baselines that many private-sector organizations adopt as best practice. Each STIG contains hundreds of individual checks (findings) categorized by severity: CAT I findings represent vulnerabilities that directly enable unauthorized access or system compromise and must be remediated; CAT II findings are significant security weaknesses that should be remediated; CAT III findings are lower-risk configuration improvements. A typical ESXi 8 STIG contains 100+ findings covering SSH configuration, password policies, logging, NTP, SNMP, lockdown mode, TLS settings, and dozens of advanced kernel parameters. Applying all STIG settings without testing frequently breaks functionality — for example, disabling all TLS versions except 1.2+ can break legacy management tools, enabling FIPS mode changes available cipher suites and may prevent communication between components, and restricting SSH access can lock administrators out of emergency troubleshooting paths. The most common STIG implementation failure is treating hardening as a one-time activity: systems drift from compliance within weeks as patches are applied, configurations are changed for troubleshooting, and new software is installed. Continuous compliance scanning with automated remediation is essential for maintaining the hardened state. SCAP (Security Content Automation Protocol) provides standardized machine-readable STIG content that enables automated scanning, but SCAP benchmarks may lag behind the latest STIG release by weeks or months.

## Common Decisions (ADR Triggers)

- **Full STIG compliance vs risk-based subset** — full compliance (all CAT I/II/III) for DoD/government systems requiring ATO vs risk-based approach (CAT I mandatory, CAT II evaluated, CAT III optional) for commercial environments using STIGs as a security baseline; full compliance requires significantly more testing and documentation effort
- **Automated vs manual STIG remediation** — automated remediation (Ansible STIG roles, PowerCLI scripts, SCAP remediation) for consistent, repeatable hardening across large environments vs manual remediation for small environments or when automation scripts are not available for the specific STIG version; automation requires initial development investment but pays off at scale
- **FIPS 140-2 mode: enable vs exception** — enable FIPS mode on all components for full cryptographic compliance (required for most federal systems) vs document exception with compensating controls for environments where FIPS mode breaks critical functionality (legacy integrations, specific vendor products that fail under FIPS); FIPS mode impacts TLS, SSH, IPsec, and certificate algorithms
- **Lockdown mode: Normal vs Strict** — Normal lockdown mode (DCUI access for users on exception list, no direct SSH/API to host) vs Strict lockdown mode (DCUI also disabled, vCenter-only management); Strict provides maximum security but eliminates emergency console access if vCenter is unavailable
- **STIG scanning tool selection** — DISA SCC (official DoD tool, free, Windows-only scanner) vs OpenSCAP (open-source, Linux-native, integrates with Red Hat Satellite/Ansible) vs commercial scanners (Nessus/Tenable with STIG audit files, Rapid7) for broader vulnerability management integration; DoD environments often require SCC scan results specifically
- **Point-in-time vs continuous compliance** — point-in-time scanning (pre-ATO assessment, periodic audits) vs continuous compliance (scheduled scans, drift detection, automated remediation); continuous compliance is operationally more expensive but prevents compliance decay between audits
- **STIG-first deployment vs post-deployment hardening** — integrate STIG settings into golden images, kickstart files, and IaC templates so systems are compliant at first boot vs deploy standard images and harden afterward; STIG-first reduces the window of vulnerability but requires more upfront template engineering

## Reference Architectures

### STIG Severity Categories and Response Requirements

```
┌──────────┬────────────────┬────────────────────────────────────────┐
│ Category │   Severity     │   Response Requirement                 │
├──────────┼────────────────┼────────────────────────────────────────┤
│ CAT I    │ Critical       │ Must remediate before ATO.             │
│          │ (CVSS 7.0+)   │ No POA&M allowed in most               │
│          │                │ authorization frameworks.              │
│          │                │ Represents direct path to              │
│          │                │ system compromise.                     │
├──────────┼────────────────┼────────────────────────────────────────┤
│ CAT II   │ High           │ Should remediate before ATO.           │
│          │ (CVSS 4.0-6.9) │ POA&M acceptable with                  │
│          │                │ compensating controls and              │
│          │                │ remediation timeline.                  │
├──────────┼────────────────┼────────────────────────────────────────┤
│ CAT III  │ Medium          │ Recommended remediation.               │
│          │ (CVSS 0-3.9)   │ POA&M acceptable. Often                │
│          │                │ addressed during regular               │
│          │                │ maintenance cycles.                    │
└──────────┴────────────────┴────────────────────────────────────────┘
```

### STIG Implementation Workflow

```
Phase 1: Discovery and Planning
  ├── Inventory all system components (OS, hypervisor, DB, apps)
  ├── Download applicable STIGs from cyber.mil
  ├── Download SCAP benchmarks (if available) from cyber.mil
  ├── Identify STIG Viewer version and install
  ├── Map STIGs to components (e.g., RHEL 9 STIG → all Linux VMs)
  └── Estimate remediation effort per STIG (CAT I first)

Phase 2: Baseline Assessment
  ├── Run SCAP scan (SCC or OpenSCAP) against current state
  ├── Import results into STIG Viewer, generate .ckl checklists
  ├── Categorize findings: auto-remediable vs manual vs exception
  ├── Identify CAT I findings for immediate remediation
  └── Document initial compliance percentage per component

Phase 3: Remediation (Non-Production First)
  ├── Apply CAT I remediations in test environment
  │     ├── Verify application functionality after each change
  │     ├── Document any broken functionality
  │     └── Develop rollback procedures
  ├── Apply CAT II remediations in test environment
  ├── Apply CAT III remediations (if required)
  ├── Re-scan to verify remediation effectiveness
  └── Create automation scripts for repeatable application

Phase 4: Production Remediation
  ├── Schedule maintenance window
  ├── Take snapshots/backups before changes
  ├── Apply automated remediation scripts
  ├── Verify application functionality
  ├── Run validation SCAP scan
  └── Generate compliance report

Phase 5: Continuous Compliance
  ├── Schedule recurring SCAP scans (daily/weekly)
  ├── Configure drift alerting (email, SIEM, ticketing)
  ├── Automate re-remediation for known-safe settings
  ├── Review and update POA&Ms quarterly
  └── Update STIGs when new versions are published
```

### VMware STIG Remediation — ESXi 8 Key Areas

```
┌─────────────────────────────────────────────────────────────────┐
│              ESXi 8 STIG — Common Remediation Areas             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SSH Configuration (CAT I/II):                                  │
│    • Disable SSH service (or restrict to key-based auth)        │
│    • Set idle timeout: UserVars.ESXiShellInteractiveTimeOut     │
│    • Set session timeout: UserVars.ESXiShellTimeOut             │
│    • Disable root SSH login if lockdown mode is enabled         │
│                                                                 │
│  Lockdown Mode (CAT II):                                        │
│    • Enable Normal lockdown mode                                │
│    • Configure exception users (backup, monitoring agents)      │
│    • Verify DCUI access for emergency troubleshooting           │
│                                                                 │
│  Logging (CAT II):                                              │
│    • Configure remote syslog: Syslog.global.logHost             │
│    • Set log level: Config.HostAgent.log.level = info           │
│    • Verify persistent log storage (/scratch/log)               │
│                                                                 │
│  NTP (CAT II):                                                  │
│    • Configure NTP servers (minimum 2, DoD NTP preferred)       │
│    • Enable ntpd service, set to start with host                │
│                                                                 │
│  SNMP (CAT II):                                                 │
│    • Disable SNMP if not used                                   │
│    • If used: SNMPv3 only, no default community strings         │
│                                                                 │
│  TLS/SSL (CAT I/II):                                            │
│    • Disable TLS 1.0 and 1.1                                    │
│    • Configure approved cipher suites only                      │
│    • Replace default self-signed certificates                   │
│                                                                 │
│  Password Policy (CAT II):                                      │
│    • Security.PasswordQualityControl: min length, complexity    │
│    • Security.AccountLockFailures: lockout after N failures     │
│    • Security.AccountUnlockTime: lockout duration               │
│                                                                 │
│  Firewall (CAT II):                                             │
│    • Configure ESXi firewall rules (esxcli network firewall)    │
│    • Default deny for inbound, allow only required services     │
│    • Restrict management access to specific IP ranges           │
│                                                                 │
│  PowerCLI Automation Example:                                   │
│    Get-VMHost | ForEach-Object {                                │
│      $_ | Get-AdvancedSetting -Name UserVars.ESXiShell*         │
│         | Set-AdvancedSetting -Value 900 -Confirm:$false        │
│      $_ | Get-VMHostService | Where Key -eq "TSM-SSH"           │
│         | Stop-VMHostService -Confirm:$false                    │
│      $_ | Get-VMHostService | Where Key -eq "TSM-SSH"           │
│         | Set-VMHostService -Policy Off                         │
│    }                                                            │
└─────────────────────────────────────────────────────────────────┘
```

### SCAP Scanning Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCAP Scanning Workflow                        │
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │  SCAP Content │     │  Scanner     │     │  Targets     │   │
│  │  (XCCDF +    │────►│  (SCC,       │────►│  (ESXi,      │   │
│  │   OVAL)      │     │   OpenSCAP,  │     │   Linux,     │   │
│  │  from        │     │   Nessus)    │     │   Windows)   │   │
│  │  cyber.mil   │     └──────┬───────┘     └──────────────┘   │
│  └──────────────┘            │                                  │
│                              ▼                                  │
│                    ┌──────────────────┐                          │
│                    │  Scan Results     │                          │
│                    │  (XCCDF XML,     │                          │
│                    │   ARF, HTML)     │                          │
│                    └────────┬─────────┘                          │
│                             │                                    │
│                    ┌────────▼─────────┐                          │
│                    │  STIG Viewer     │                          │
│                    │  Import results  │                          │
│                    │  Generate .ckl   │                          │
│                    │  Track status    │                          │
│                    └────────┬─────────┘                          │
│                             │                                    │
│                    ┌────────▼─────────┐                          │
│                    │  Compliance      │                          │
│                    │  Dashboard       │                          │
│                    │  (eMASS, Archer, │                          │
│                    │   custom)        │                          │
│                    └──────────────────┘                          │
│                                                                 │
│  Tool Comparison:                                               │
│  ┌──────────────┬────────────┬────────────┬──────────────────┐  │
│  │ Tool         │ Cost       │ Platform   │ Notes            │  │
│  ├──────────────┼────────────┼────────────┼──────────────────┤  │
│  │ DISA SCC     │ Free (DoD) │ Windows    │ Official DoD     │  │
│  │ OpenSCAP     │ Free (OSS) │ Linux      │ RHEL integrated  │  │
│  │ Nessus       │ Commercial │ Cross-plat │ Broader vuln mgmt│  │
│  │ Rapid7       │ Commercial │ Cross-plat │ InsightVM + STIG │  │
│  └──────────────┴────────────┴────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

## Reference Links

- [DISA STIG Library](https://public.cyber.mil/stigs/)
- [SCAP Compliance Checker](https://public.cyber.mil/stigs/scap/)
- [OpenSCAP](https://www.open-scap.org/)
- [STIG Viewer](https://public.cyber.mil/stigs/srg-stig-tools/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [Ansible STIG Roles on Galaxy](https://galaxy.ansible.com/search?keywords=stig)

## See Also

- [security.md](security.md) -- general security architecture, threat modeling, and security controls
- [governance.md](governance.md) -- compliance frameworks, audit requirements, and organizational controls
- [tls-certificates.md](tls-certificates.md) -- TLS configuration and cipher suite management related to STIG requirements
- [iac-planning.md](iac-planning.md) -- infrastructure-as-code for embedding STIG settings into deployment templates
- [fedramp.md](../compliance/fedramp.md) -- FedRAMP control families and cloud control mapping
- [nist-800-171-cmmc.md](../compliance/nist-800-171-cmmc.md) -- NIST 800-171 and CMMC 2.0 cloud control mapping
