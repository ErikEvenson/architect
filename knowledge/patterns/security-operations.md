# Security Operations

## Scope

Covers security operations center (SOC) design, SIEM architecture, incident response planning, threat detection and hunting, SOAR integration, threat intelligence, and forensic readiness. Applicable to any organization establishing or maturing security operations capabilities — whether building an in-house SOC, operating a hybrid model with an MSSP, or deploying cloud-native security monitoring across multi-cloud environments.

## Overview

Security operations is the continuous practice of detecting, analyzing, and responding to cybersecurity threats against an organization's infrastructure, applications, and data. A mature security operations program combines people (SOC analysts organized in tiers), processes (incident response playbooks aligned to frameworks like NIST 800-61), and technology (SIEM for log aggregation and correlation, SOAR for automated response, EDR/XDR for endpoint visibility, and threat intelligence feeds for context enrichment). The goal is to minimize mean time to detect (MTTD) and mean time to respond (MTTR) while maintaining forensic readiness and compliance with regulatory incident reporting requirements.

## Checklist

- [ ] **[Critical]** What is the SIEM architecture and how are logs aggregated from all critical sources? (select a SIEM platform — Splunk Enterprise Security, Microsoft Sentinel, Google Chronicle, Elastic Security, IBM QRadar, or CrowdStrike Falcon LogScale; define log collection architecture using agents, syslog forwarders, API collectors, and cloud-native integrations; ensure all security-relevant log sources are onboarded before declaring operational capability)
- [ ] **[Critical]** Which log sources are prioritized for onboarding, and is there a log source coverage matrix? (prioritize based on MITRE ATT&CK data source mapping: identity provider logs, endpoint detection logs, DNS query logs, firewall/proxy logs, cloud control plane audit logs, email gateway logs, VPN/remote access logs; track coverage gaps against ATT&CK techniques to identify blind spots)
- [ ] **[Critical]** How is log retention sized and tiered to meet both operational and compliance requirements? (hot storage for 30-90 days of full-fidelity searchable data, warm storage for 6-12 months of indexed but slower-access data, cold/archive storage for 1-7 years depending on regulatory mandates — PCI DSS requires 12 months, HIPAA requires 6 years; calculate daily ingest volume per source and apply compression ratios to size storage; budget for 20-30% annual log volume growth)
- [ ] **[Critical]** Is the SOC organized using a tiered analyst model with clearly defined escalation paths? (L1 analysts handle alert triage, initial classification, and false positive filtering; L2 analysts perform deep investigation, correlation across data sources, and containment actions; L3 analysts and threat hunters conduct proactive hypothesis-driven hunting, malware analysis, and forensic examination; define escalation criteria, handoff procedures, and SLAs for each tier)
- [ ] **[Critical]** Are incident response playbooks documented and aligned to the NIST 800-61 framework? (cover all four phases: Preparation, Detection and Analysis, Containment/Eradication/Recovery, and Post-Incident Activity; create specific playbooks for common incident types — ransomware, business email compromise, data exfiltration, insider threat, DDoS, supply chain compromise, cloud account takeover; include decision trees, communication templates, and escalation criteria in each playbook)
- [ ] **[Critical]** How are detection rules mapped to the MITRE ATT&CK framework, and what is the technique coverage percentage? (map every correlation rule and detection to specific ATT&CK techniques and sub-techniques; track coverage across the ATT&CK matrix to identify detection gaps; prioritize detection engineering for techniques most relevant to the organization's threat profile — use ATT&CK Navigator to visualize coverage and gaps)
- [ ] **[Critical]** What is the alert fatigue management strategy, and what is the current false positive rate? (target less than 30% false positive rate for alerts escalated to analysts; implement alert tuning cycles — review top-volume alerts weekly and suppress or enrich noisy detections; use risk-based alerting that scores events by asset criticality, user risk, and behavioral anomaly rather than triggering on individual IOCs; track mean alerts per analyst per shift and ensure it remains below 50 actionable alerts)
- [ ] **[Recommended]** Is a SOAR platform integrated to automate repetitive response actions? (select a SOAR platform — Palo Alto XSOAR, Splunk SOAR, Microsoft Sentinel with Logic Apps, Tines, Swimlane; automate common response actions: IOC enrichment from threat intel feeds, user account disablement, endpoint isolation, firewall block rule creation, ticket creation in ITSM; start with 5-10 high-volume playbooks before expanding automation scope)
- [ ] **[Recommended]** How are threat intelligence feeds ingested, scored, and operationalized? (subscribe to commercial feeds — Recorded Future, Mandiant Advantage, CrowdStrike Falcon Intelligence — and open-source feeds — MISP, AlienVault OTX, Abuse.ch; integrate feeds into SIEM for IOC matching against logs; implement a threat intelligence platform (TIP) to deduplicate, score confidence, and age out stale indicators; ensure intel feeds are relevant to the organization's industry vertical and threat landscape)
- [ ] **[Recommended]** Is there a purple teaming program to validate detection coverage? (conduct regular exercises where red team operators execute ATT&CK techniques against production or staging environments while blue team analysts attempt to detect and respond; document detection gaps discovered during exercises and feed them back into detection engineering sprints; use frameworks like Atomic Red Team or MITRE Caldera for repeatable adversary emulation)
- [ ] **[Recommended]** What is the forensic readiness posture, and can evidence be collected without disrupting operations? (ensure forensic imaging capability for endpoints — disk images and memory captures using tools like Velociraptor, GRR Rapid Response, or CrowdStrike Falcon RTR; configure cloud environments for forensic snapshot capability — EBS snapshots, Azure disk snapshots, GCP persistent disk snapshots; maintain chain-of-custody procedures and evidence handling documentation; pre-stage forensic tools on golden images or deploy via EDR)
- [ ] **[Recommended]** How is the SOC monitoring cloud-native services and cloud control plane activity? (ingest cloud audit logs — AWS CloudTrail, Azure Activity Log, GCP Cloud Audit Logs — into SIEM; build detections for cloud-specific threats: IAM privilege escalation, S3/blob public exposure, security group modifications, impossible travel for cloud console logins, service account key creation; use cloud security posture management (CSPM) tools to complement SIEM detections)
- [ ] **[Recommended]** What are the incident communication procedures during an active incident? (define communication channels — dedicated war room in Slack/Teams, bridge call procedures, out-of-band communication for compromised environments; establish notification matrices for different severity levels; document regulatory notification timelines — GDPR 72-hour breach notification, SEC 4-business-day material incident disclosure, sector-specific requirements; prepare holding statements and customer communication templates)
- [ ] **[Recommended]** Is there a detection-as-code practice for managing correlation rules in version control? (store detection rules in Git repositories using standardized formats — Sigma rules for vendor-agnostic detection logic, YARA rules for malware detection, Snort/Suricata rules for network detection; implement CI/CD pipelines that validate, test, and deploy detection rules to the SIEM; track detection rule performance metrics — true positive rate, time to detection, coverage percentage)
- [ ] **[Optional]** Is there a deception technology layer deployed for early breach detection? (deploy honeypots, honeytokens, and decoy credentials across the environment — Thinkst Canary for network honeypots, decoy Active Directory accounts, fake API keys in code repositories, canary files on file shares; deception-based alerts have near-zero false positive rates and indicate active adversary presence; integrate deception alerts with SOAR for immediate containment)
- [ ] **[Optional]** What metrics and KPIs are tracked to measure SOC effectiveness? (track MTTD, MTTR, alert-to-incident ratio, false positive rate, detection coverage percentage against ATT&CK, analyst utilization rate, playbook automation percentage, and mean time to containment; report metrics monthly to security leadership; benchmark against industry peers using frameworks like MITRE ATT&CK Evaluations and SANS SOC survey data)
- [ ] **[Optional]** Is there a formal threat hunting program beyond reactive alert-driven investigation? (establish hypothesis-driven hunts based on threat intelligence, ATT&CK techniques with low detection coverage, and industry-specific threat actor TTPs; allocate dedicated analyst time — at least 20% of L3 capacity — for proactive hunting; document hunt hypotheses, methodologies, and findings; convert successful hunts into automated detections)

## Why This Matters

Organizations without mature security operations face an average breach dwell time exceeding 200 days — meaning attackers operate undetected in the environment for over six months before discovery. During that time, they establish persistence, move laterally, escalate privileges, and exfiltrate data at will. The cost differential between breaches detected internally versus those discovered by external parties (law enforcement, customers, or the media) is dramatic: internally detected breaches are contained faster, affect fewer records, and cost significantly less to remediate.

A well-designed SOC with properly tuned SIEM, documented playbooks, and trained analysts reduces dwell time to hours or days rather than months. Alert fatigue is the primary operational risk — when analysts are overwhelmed by thousands of low-fidelity alerts, they begin ignoring or auto-closing them, and real attacks slip through. Organizations that invest in detection engineering, alert tuning, and SOAR automation see measurable improvements in analyst effectiveness and incident response times.

Forensic readiness is frequently overlooked until a breach occurs. Without pre-positioned forensic tooling, proper log retention, and chain-of-custody procedures, organizations cannot determine the scope of a breach, satisfy regulatory investigation requirements, or provide evidence for law enforcement. The cost of retrofitting forensic capability during an active incident — including hiring external IR firms at premium rates — vastly exceeds the cost of building readiness into the architecture from the start.

MITRE ATT&CK has become the de facto standard for measuring detection coverage and communicating about adversary behavior. Organizations that map their detection rules to ATT&CK techniques can quantify their security posture, identify gaps, and prioritize detection engineering investments based on the techniques most commonly used by threat actors targeting their industry.

## Common Decisions (ADR Triggers)

### ADR: SIEM Platform Selection

**Context:** The organization must select a SIEM platform for centralized log aggregation, correlation, and threat detection across on-premises and cloud environments.

**Options:**

| Platform | Deployment Model | Strengths | Considerations |
|---|---|---|---|
| Splunk Enterprise Security | On-prem, cloud (Splunk Cloud), hybrid | Most mature search language (SPL), largest ecosystem of apps and integrations, strong for complex correlation | Expensive at high ingest volumes (ingest-based licensing), requires significant tuning expertise, hardware-intensive for on-prem |
| Microsoft Sentinel | Cloud-native (Azure) | Native integration with Microsoft 365 and Azure, built-in SOAR via Logic Apps, KQL query language, free ingestion for Microsoft data sources | Best value for Microsoft-heavy environments, weaker for non-Microsoft log sources, Azure dependency |
| Google Chronicle (SecOps) | Cloud-native (GCP) | Fixed-price storage model (not ingest-based), petabyte-scale search, YARA-L detection language, integrated SOAR | Smaller ecosystem than Splunk, relatively newer platform, best for organizations comfortable with Google Cloud |
| Elastic Security | Self-managed or Elastic Cloud | Open-source core, flexible deployment, strong for custom data sources, no per-GB licensing for self-managed | Requires significant operational investment for self-managed, cluster management complexity, security features require paid license |
| CrowdStrike Falcon LogScale (Humio) | Cloud-native or self-managed | Streaming architecture for real-time search, compression-efficient storage, fast query performance | Primarily log management rather than full SIEM, detection content library smaller than Splunk/Sentinel |

**Decision drivers:** Daily log ingest volume and growth projections, existing technology stack (Microsoft vs multi-vendor), budget model preference (ingest-based vs fixed-price vs self-managed), team expertise with query languages (SPL, KQL, EQL), cloud strategy, and compliance requirements for data residency.

### ADR: SOC Operating Model

**Context:** The organization must decide how to staff and operate its security operations center — fully in-house, fully outsourced to an MSSP/MDR, or a hybrid model.

**Options:**

- **In-house SOC:** Full control over detection engineering, incident response, and threat hunting. Requires significant investment in hiring, training, and retaining skilled analysts (24x7 coverage requires minimum 8-12 FTEs). Best for large organizations with complex environments and regulatory requirements that demand direct control.
- **MSSP/MDR (fully outsourced):** Managed security service provider handles monitoring, alert triage, and initial response. Lower cost for 24x7 coverage, faster time to operational capability. Less customization, potential alert fatigue from generic rule sets, shared analyst attention across multiple clients. Best for small-to-mid-size organizations without dedicated security staff.
- **Hybrid SOC:** MSSP provides 24x7 L1 monitoring and alert triage, in-house team handles L2/L3 investigation, threat hunting, and detection engineering. Balances cost and control. Requires clear escalation procedures and SLAs between MSSP and internal team. Most common model for mid-size organizations.

**Decision drivers:** Organization size and security team maturity, budget for 24x7 staffing, regulatory requirements for incident handling (some frameworks require internal IR capability), complexity of the technology environment, and tolerance for outsourced access to security telemetry.

### ADR: Log Retention and Storage Tiering Strategy

**Context:** Log data must be retained for operational investigation, threat hunting, and compliance mandates, but storage costs grow linearly with retention duration and ingest volume.

**Options:**

- **Single-tier hot storage:** All logs searchable at full speed for the entire retention period. Simplest to operate but most expensive. Only viable for small-to-moderate ingest volumes (under 100 GB/day).
- **Two-tier (hot + cold):** Hot storage for 30-90 days of full-fidelity indexed data, cold storage in object storage (S3, Azure Blob, GCS) for long-term compliance retention. Cold data requires rehydration for searching. Good balance of cost and accessibility.
- **Three-tier (hot + warm + cold):** Hot for 7-30 days of real-time search, warm for 30-365 days of slower but still searchable data, cold archive for multi-year retention. Optimizes cost for high-volume environments. Adds operational complexity for managing tier transitions.

**Decision drivers:** Daily ingest volume, compliance retention mandates (PCI DSS 12 months, HIPAA 6 years, SOX 7 years), threat hunting requirements (hunters need access to historical data for retrospective IOC searches), budget constraints, and query performance requirements for different use cases.

### ADR: SOAR Platform Selection and Automation Scope

**Context:** Repetitive incident response tasks consume analyst time and delay response. A SOAR platform can automate enrichment, containment, and notification workflows, but scope must be carefully defined to avoid automating high-risk actions without human oversight.

**Options:**

- **Palo Alto XSOAR (formerly Demisto):** Largest integration marketplace (700+ integrations), mature playbook visual editor, strong case management. Enterprise pricing, complex deployment.
- **Splunk SOAR (formerly Phantom):** Tight integration with Splunk SIEM, visual playbook editor, community playbook sharing. Best paired with Splunk ES. Separate licensing from Splunk SIEM.
- **Microsoft Sentinel + Logic Apps:** Native SOAR capability within Sentinel using Azure Logic Apps for workflow automation. No additional licensing for Sentinel customers. Limited to Azure ecosystem for native integrations.
- **Tines:** No-code automation platform, cloud-native, flexible API integration model, not SIEM-dependent. Strong for organizations that want SOAR without SIEM vendor lock-in.

**Decision drivers:** Existing SIEM platform (native SOAR integration reduces complexity), number of integrations needed, team capability for playbook development, budget for additional platform licensing, and whether SOAR must support non-security automation use cases.

### ADR: Threat Intelligence Strategy

**Context:** Detection effectiveness depends on contextual threat intelligence — indicators of compromise, adversary TTPs, and industry-specific threat reporting. The organization must decide which intelligence sources to consume and how to operationalize them.

**Options:**

- **Commercial feeds only (Recorded Future, Mandiant, CrowdStrike):** High-confidence indicators, curated industry reporting, finished intelligence products. Expensive but low operational overhead. Best for organizations without dedicated threat intelligence analysts.
- **Open-source feeds only (MISP, OTX, Abuse.ch, VirusTotal community):** Free but requires significant curation effort to filter noise, score confidence, and age out stale indicators. High false positive risk without tuning. Best as a supplement rather than sole source.
- **Hybrid with TIP (MISP, ThreatConnect, Anomali):** Aggregate commercial and open-source feeds into a threat intelligence platform that deduplicates, scores, and distributes indicators to SIEM and security tools. Highest operational maturity but requires dedicated TI analyst capacity.

**Decision drivers:** Security team size and TI expertise, budget for commercial feeds, industry vertical (financial services and defense have specialized threat actors requiring tailored intelligence), volume tolerance for IOC matching in SIEM, and whether the organization needs finished intelligence reports for executive communication.

## Reference Links

- [NIST SP 800-61 Rev. 2: Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [MITRE ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
- [Sigma Rules — Generic Signature Format for SIEM Systems](https://github.com/SigmaHQ/sigma)
- [Atomic Red Team — Adversary Emulation Library](https://github.com/redcanaryco/atomic-red-team)
- [MITRE Caldera — Adversary Emulation Platform](https://caldera.mitre.org/)
- [Splunk Enterprise Security](https://www.splunk.com/en_us/products/enterprise-security.html)
- [Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/overview)
- [Google Chronicle Security Operations](https://chronicle.security/)
- [Elastic Security](https://www.elastic.co/security)
- [Palo Alto XSOAR](https://www.paloaltonetworks.com/cortex/cortex-xsoar)
- [Velociraptor — Digital Forensics and Incident Response](https://docs.velociraptor.app/)
- [Thinkst Canary — Deception Technology](https://canary.tools/)
- [SANS Incident Handler's Handbook](https://www.sans.org/white-papers/33901/)

## See Also

- `general/security.md` — Foundational security controls including IAM, encryption, and audit logging that security operations monitors
- `general/observability.md` — Observability architecture for application and infrastructure telemetry that feeds into SIEM
- `patterns/zero-trust.md` — Zero trust architecture whose microsegmentation and identity verification generate security telemetry for SOC monitoring
- `compliance/soc2.md` — SOC 2 compliance requirements for security monitoring, incident response, and audit logging
- `compliance/pci-dss.md` — PCI DSS requirements for security monitoring, log retention, and incident response procedures
- `general/ransomware-resilience.md` — Ransomware-specific detection, containment, and recovery patterns that security operations must address
- `general/tier0-security-enclaves.md` — Tier 0 asset protection that requires heightened SOC monitoring and dedicated detection rules
- `general/itsm-integration.md` — ITSM integration for incident ticket creation and escalation workflows from SOC
