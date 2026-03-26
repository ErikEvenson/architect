# Splunk

## Scope

This file covers **Splunk** platform architecture for observability and security including Splunk Enterprise and Splunk Cloud deployment models, indexer and search head clustering, forwarder deployment (Universal Forwarder, Heavy Forwarder), index management (retention, volume, data model acceleration), Search Processing Language (SPL) for data analysis, Splunk SOAR (Security Orchestration, Automation and Response), Splunk Observability Cloud (formerly SignalFx) for infrastructure and APM, and licensing models (ingest-based per GB/day vs workload-based SVCs). For general observability patterns, see `general/observability.md`.

## Checklist

- [ ] **[Critical]** Is the Splunk deployment architecture defined -- Splunk Cloud (SaaS, Splunk-managed) vs Splunk Enterprise (self-managed) with appropriate sizing for indexers (storage IOPS, CPU for search), search heads (CPU, memory), and cluster replication factor (RF) and search factor (SF)?
- [ ] **[Critical]** Is the licensing model understood and data ingestion controlled -- ingest-based licensing charges per GB/day ($1,800-$4,500+ per GB/day annually), and uncontrolled log volume from verbose applications or debug logging can cause license violations that block searching?
- [ ] **[Critical]** Are forwarders deployed with appropriate types -- Universal Forwarder (UF) for lightweight log collection from endpoints (syslog, file monitoring), Heavy Forwarder (HF) for data transformation, filtering, and routing before indexing -- with deployment server managing forwarder configurations at scale?
- [ ] **[Critical]** Are indexes defined with appropriate retention policies, data model definitions, and access controls -- separating security data (long retention, restricted access) from operational data (shorter retention, broader access), with index sizing aligned to license entitlement?
- [ ] **[Recommended]** Is search head clustering configured for high availability and load distribution, with knowledge object replication, captain election, and search affinity configured to prevent search performance degradation during cluster operations?
- [ ] **[Recommended]** Are data inputs validated to avoid common pitfalls -- duplicate data from multiple forwarders monitoring the same source, timestamp extraction issues causing events to land in wrong time buckets, and character encoding problems corrupting non-ASCII data?
- [ ] **[Recommended]** Is Splunk SOAR integrated for security operations with playbooks automated for common incident types (phishing triage, endpoint isolation, threat intelligence enrichment), with SOAR actions audited and rate-limited to prevent automated runaway responses?
- [ ] **[Recommended]** Are saved searches, reports, and alerts designed with efficiency -- using tstats for accelerated data models instead of raw search, limiting time ranges, using indexed fields for filtering, and scheduling searches to spread load across off-peak windows?
- [ ] **[Recommended]** Is the migration path evaluated if transitioning between deployment models (Enterprise to Cloud, ingest-based to workload-based licensing) -- including data migration, app compatibility, custom configuration portability, and network architecture changes for forwarder connectivity?
- [ ] **[Optional]** Is Splunk Observability Cloud (formerly SignalFx) evaluated for infrastructure and APM use cases separately from log management -- it provides streaming analytics and real-time metrics that complement Splunk's log-centric strengths?
- [ ] **[Optional]** Are summary indexes and data model acceleration configured for frequently accessed reports to reduce search time and indexer load, with storage overhead monitored and managed?
- [ ] **[Optional]** Is Splunk integrated with ticketing systems (ServiceNow, Jira) for automated incident creation from notable events, with bidirectional sync for status updates and resolution tracking?
- [ ] **[Recommended]** Is a data onboarding process defined -- including source type creation, field extraction (regex vs delimited vs JSON auto-extraction), CIM compliance for security use cases, and data quality validation before production use?

## Why This Matters

Splunk is the most widely deployed log analytics platform in enterprises, particularly dominant in security operations centers (SOCs) where it serves as the SIEM. Its power -- the ability to search, correlate, and alert on any machine data -- makes it invaluable for security investigation and operational troubleshooting, but its ingest-based pricing model creates a direct tension between visibility and cost. Organizations commonly discover that their Splunk license represents one of their largest software expenses, with costs growing proportionally to infrastructure scale. A single misconfigured application generating verbose debug logs can consume tens of GB/day and blow through license entitlements. Architecture designs must treat Splunk data ingestion as a metered resource with governance controls.

The distributed architecture (indexers, search heads, forwarders) requires careful planning. Under-provisioned indexer clusters create search bottlenecks during incident investigations when fast results are critical. Forwarder deployment strategy directly impacts data quality -- Universal Forwarders cannot parse or transform data, so complex log formats may require Heavy Forwarders or intermediate processing. The shift from Splunk Enterprise to Splunk Cloud changes the operational model significantly: Splunk manages the infrastructure but customers lose direct access to the operating system, limiting custom app deployment and integration patterns.

## Common Decisions (ADR Triggers)

- **Splunk Enterprise vs Splunk Cloud** -- Enterprise provides full infrastructure control, custom app deployment, and direct OS access for advanced integrations, but requires dedicated infrastructure and operations teams (sizing: ~1 FTE per 500 GB/day). Cloud eliminates infrastructure management, provides automatic upgrades, and includes premium features, but restricts custom app deployment (Splunk app vetting required), limits private connectivity options, and costs 20-40% more than self-managed. Choose Cloud for organizations without Splunk infrastructure expertise; Enterprise when customization, data sovereignty, or existing infrastructure investment justifies self-management.
- **Ingest-based vs workload-based (SVC) licensing** -- Ingest-based charges per GB/day of indexed data, incentivizing data reduction but creating tension with visibility goals. Workload-based (Splunk Virtual Compute units) decouples cost from data volume, enabling unlimited ingestion with cost based on search compute used. Workload-based is more predictable for growing environments but requires understanding search patterns. Evaluate workload-based when daily ingestion exceeds 100 GB and is growing unpredictably.
- **Splunk as SIEM vs dedicated SIEM** -- Splunk with Enterprise Security (ES) provides a powerful SIEM with flexible correlation rules, notable events framework, and investigation workbench, but ES adds significant licensing cost (~$30K-$100K+/yr). Dedicated SIEMs (Microsoft Sentinel, Google Chronicle) offer cloud-native security analytics with different pricing models. Use Splunk ES when Splunk is already deployed for operational data and the team has SPL expertise; dedicated cloud SIEM when starting fresh or when log volume makes ingest-based pricing prohibitive.
- **Universal Forwarder vs Heavy Forwarder vs syslog** -- UF is lightweight (50-100 MB), deployed to every endpoint, with minimal processing overhead but no data transformation. HF provides full Splunk processing (field extraction, filtering, routing) but consumes significant resources (4+ GB RAM). Syslog ingestion (via HF or Splunk Connect for Syslog) handles network devices and legacy systems that cannot run agents. Use UF as default; HF for data transformation requirements; syslog for network infrastructure.
- **Splunk Observability Cloud vs Splunk Enterprise for metrics** -- Observability Cloud provides real-time streaming analytics, infrastructure monitoring, and APM purpose-built for cloud-native environments. Splunk Enterprise can ingest metrics but is optimized for log search, not real-time metric visualization. Use Observability Cloud for infrastructure metrics and APM; Splunk Enterprise for log analytics and security. The two platforms integrate via federation but are separate products with separate pricing.

## See Also

- `general/observability.md` -- general observability architecture and monitoring strategy
- `general/security.md` -- security architecture including SIEM placement and log requirements

## Reference Links

- [Splunk Enterprise Documentation](https://docs.splunk.com/Documentation/Splunk) -- indexer clustering, search heads, forwarder deployment, and SPL reference
- [Splunk Observability Cloud](https://docs.splunk.com/observability/en/) -- infrastructure monitoring, APM, RUM, and synthetic monitoring
- [Splunk SOAR Documentation](https://docs.splunk.com/Documentation/SOAR) -- security orchestration, playbooks, and automated response workflows
