# Data Platform Selection

## Scope

Covers the selection of an enterprise analytical data platform — the system that holds
governed, cross-domain data and serves BI, reporting, regulatory extracts, and analytics or
ML workloads. Compares eight candidate answers: Microsoft Fabric; classic Azure analytics
(ADLS Gen2 with Synapse and/or Data Factory, Power BI, Purview); Databricks; Snowflake;
AWS-native (S3, Glue, Lake Formation, Athena, Redshift); GCP-native (BigQuery, Dataplex);
a self-managed open-source stack (object storage, Apache Iceberg, a catalogue, Trino or
Spark); and the analytics offering shipped by the organisation's own system-of-record
application vendor.

This file is about **choosing and defending a choice**. It does not cover implementation
of the chosen platform — see `patterns/lakehouse-medallion.md` for layered lake design,
`general/data-ingestion.md` for landing data, `general/data-modelling.md` for the modelling
layer, `general/open-table-formats.md` for Delta/Iceberg/Hudi mechanics,
`general/query-engines.md` for engine characteristics, and
`patterns/data-warehouse-migration.md` for moving off a legacy warehouse. For the operating
pattern once the platform is running, see `patterns/data-pipeline.md`.

**Statements dated in this file were verified against vendor documentation on 2026-07-26.**
This category moves fast. Re-verify anything load-bearing before you put it in front of an
executive or an examiner, and treat any undated capability claim in *any* comparison —
including this one — as suspect.

## Overview

Most published platform comparisons are feature grids. Feature grids do not decide anything,
because at the top of this market every candidate can ingest, store, transform, and serve
data competently. The decision is made by five things a grid does not show:

1. **What the organisation already owns and already runs.** Identity, BI tooling, enterprise
   agreements, and — very often — capacity that is already paid for and not being used.
2. **How many people are available to operate it, and at what skill level.** This is the
   single most common cause of a failed platform, and it is an operations failure, not an
   architecture failure.
3. **What can be *shown* to a reviewer**, as distinct from what is technically logged.
4. **What it costs to leave**, in data, in rework, and in elapsed time.
5. **How much of the organisation now depends on one supplier.**

The remaining sections give a weighted framework across these dimensions, a per-candidate
"do not choose this when" list, and three worked scenario profiles that produce three
different winners from the same capability scores.

## Checklist

### Estate and commercial position

- [ ] **[Critical]** Has anyone checked what analytical capacity the organisation **already
      owns**? A Power BI Premium per-capacity (P) SKU supports Microsoft Fabric workloads —
      lakehouses, warehouses, notebooks, pipelines — once a tenant admin enables Fabric on
      that capacity. Fabric items are disabled on a P capacity by default, which is why many
      organisations do not know they are already licensed for the platform they are about to
      buy (verified against Microsoft licensing documentation, 2026-07-26).
- [ ] **[Critical]** Is the identity provider already in place, and does every candidate
      federate to it cleanly for **both** human and non-human principals (SCIM group sync,
      service principals, workload identity)?
- [ ] **[Critical]** What BI tool is already deployed and licensed, and how many report authors
      and viewers are on it? BI licensing frequently dominates platform licensing, and the
      per-viewer rules change at capacity thresholds.
- [ ] **[Recommended]** Is there an existing enterprise agreement or committed cloud spend that
      a candidate can draw down against? A platform billed through an existing cloud commitment
      has materially lower procurement friction than one requiring a new master agreement.
- [ ] **[Recommended]** Does the organisation already run the storage layer a candidate would
      use (object storage with established lifecycle, immutability, and key policy)? Reusing a
      hardened storage account or bucket is faster and more defensible than standing up a new one.
- [ ] **[Critical]** Has the **disposal cost** of the incumbent platform been enumerated as a line
      item — contract termination charges, decommissioning effort, migration effort, and any
      accelerated depreciation or impairment — separately from the sunk cost already spent on it?
      These are different numbers with different relevance, and conflating them derails the decision
      in both directions. See the disposal-cost section below.
- [ ] **[Recommended]** For each asset in the incumbent estate, is it recorded whether it would be
      **retired or repurposed**? Assets that continue serving other workloads are not written off at
      all, and they are routinely counted as though they were.
- [ ] **[Optional]** Are there existing third-party tools (catalogue, quality, orchestration,
      reverse ETL) whose contracts constrain or subsidise the choice?

### Operability versus available staff

- [ ] **[Critical]** How many engineers will operate this platform in steady state, named, at
      what seniority, and what else are they responsible for? Write the number down. Most
      failed platforms were architecturally sound and understaffed.
- [ ] **[Critical]** Does the candidate require the team to operate a **distributed query engine
      and a catalogue service** (self-managed open source) or does the vendor operate them? This
      single distinction accounts for most of the operational-effort difference between candidates.
- [ ] **[Critical]** Who performs upgrades, and what is the blast radius of a failed one? Managed
      platforms move the runtime under you on their schedule; self-managed stacks move it on
      yours, which is a different risk, not a smaller one.
- [ ] **[Recommended]** Is there a named on-call rotation for the data platform, or does it
      inherit the application on-call? Data platforms fail quietly — a pipeline that stops is
      often noticed by a business user days later.
- [ ] **[Recommended]** What is the operational failure mode under overload for each candidate?
      Capacity-based platforms throttle and queue; warehouse credit models spend money instead.
      Know which failure your organisation tolerates better.
- [ ] **[Optional]** Can the platform be operated through infrastructure-as-code end to end, or
      are there portal-only configuration surfaces that will drift?

### Security, isolation, and key custody

- [ ] **[Critical]** Can every candidate's data path be made private — no public endpoint, on both
      the inbound (user and API) and outbound (platform to data) directions? Check **serverless**
      compute separately: serverless is where private connectivity maturity varies most.
- [ ] **[Critical]** What is the actual key-custody model — platform-managed, customer-managed key
      in the cloud provider's KMS (CMK/BYOK), or a key held in hardware the organisation controls
      (HYOK, generally via an external key store)? Be precise about which *data* each key covers;
      partial CMK coverage is the norm, not the exception.
- [ ] **[Critical]** If the customer-held key is revoked, what happens, and how fast? Verify this
      is a documented behaviour and not an inference. On at least one platform the documented
      result is that all data operations cease within minutes — which is the point of the control,
      and also an availability risk that needs an owner.
- [ ] **[Recommended]** Is fine-grained access control (row filters, column masks) enforced by the
      platform for *every* engine that can reach the data, or can a principal with direct storage
      permissions bypass it? Catalogue-level policy that a storage-level grant defeats is not a control.
- [ ] **[Recommended]** Are the network controls available on the licensing tier being purchased?
      Private connectivity, customer-managed keys, and compliance profiles are commonly gated to
      higher editions or add-ons on every commercial platform in this comparison.
- [ ] **[Optional]** Is there a documented list of features that stop working once private
      networking is enforced? There usually is, and it is usually not in the marketing material.

### Residency, evidence, and retention

- [ ] **[Critical]** Where does data actually rest, per workload, and what metadata or identity
      material is stored outside that region? Compute residency and *identity* residency are
      different questions and vendors answer them in different documents.
- [ ] **[Critical]** What lineage can be produced **automatically**, at what granularity (table
      versus column), for which compute paths, and how long is it retained? Lineage that only
      exists for one execution engine is a partial answer to an examiner's question.
- [ ] **[Critical]** What audit evidence can be exported, over what retention window, without
      building anything? Distinguish "the event is logged" from "the report can be produced".
- [ ] **[Critical]** Is there a **retention and legal-hold** mechanism, and does it survive the
      table format's own file maintenance? Compaction and snapshot expiry rewrite and delete
      files by design; write-once storage policies block exactly those operations. These two
      requirements are in direct tension and the resolution has to be designed, not assumed.
- [ ] **[Recommended]** Can a specific dataset be placed under hold without freezing the whole
      storage container, and can the hold be evidenced to a third party?
- [ ] **[Recommended]** What is the data-deletion story for erasure requests, and how does it
      interact with time-travel and snapshot retention windows?
- [ ] **[Optional]** Has the platform's immutability implementation been assessed by an independent
      records-management assessor against the relevant records rules? Some have; the assessment
      letter is a useful artefact to hold.

### Openness, concentration, and exit

- [ ] **[Critical]** Can the data be read by an engine the vendor does not control, **in place,
      without copying**? Test the specific case: a managed table read by an external engine
      through an open catalogue interface. "Supports Iceberg" covers several very different
      arrangements.
- [ ] **[Critical]** What is the concentration position after this decision — how many of
      identity, productivity, BI, data platform, and cloud infrastructure sit with one supplier?
      Record the answer before choosing, because it will be asked afterwards.
- [ ] **[Recommended]** What does exit actually cost: unload time, egress charges, rebuilt
      transformation logic, rebuilt semantic model, rebuilt access policy, and retraining. Openness
      of the *storage format* addresses only the first item on that list.
- [ ] **[Recommended]** Is there a documented, exercised path to run the same workload on a second
      platform for a defined subset of data? An untested exit plan is a paragraph, not a control.
- [ ] **[Optional]** If the vendor is acquired, changes licensing, or exits a region, which of these
      dependencies becomes urgent?

### Running the selection

- [ ] **[Critical]** Are the decision dimensions **weighted before** the candidates are scored?
      Weighting after scoring is how a pre-selected answer gets a paper trail.
- [ ] **[Recommended]** Has a "do not choose this when" statement been written for the *preferred*
      option? If the preferred option has no downside, the comparison is not finished.
- [ ] **[Recommended]** Is the sensitivity of the result tested — which single weight change flips
      the winner? A decision that survives no weight change is fragile and should be labelled so.
- [ ] **[Optional]** Is there a documented review trigger (date, or a named capability reaching GA)
      at which the decision is revisited rather than assumed permanent?

## Why This Matters

**Understaffing, not architecture, is what kills data platforms.** A self-managed stack of object
storage, Apache Iceberg, a catalogue service, and Trino or Spark is a genuinely excellent
architecture and it is the wrong choice for most mid-size organisations, because it requires a
team that can own a distributed query engine, a metadata service, a table-maintenance schedule,
and an upgrade cadence — indefinitely, including when the person who built it leaves. The same
logic, more mildly, separates the fully-managed SaaS platforms from the assemble-it-yourself
cloud-native toolkits. State the staffing constraint plainly in the decision record; it is the
dimension most likely to be understated in the business case and most likely to be the actual
cause of failure two years later.

**Organisations routinely buy what they already own.** Analytical capacity arrives bundled with BI
licensing, and the bundling is not obvious. An organisation on a Power BI Premium per-capacity SKU
already has a Fabric-capable capacity; the non-BI Fabric workloads are simply switched off until an
administrator enables them. Checking the existing entitlement before running a procurement is a
one-hour task that occasionally removes the procurement entirely — and, just as often, reveals that
the free path forgoes controls (see the F-SKU note under Fabric below) that the regulated use case
actually requires. Either outcome is worth an hour.

**Evidence is a product requirement, not a compliance afterthought.** The question an examiner or
auditor asks is not "is access logged" but "show me every principal that read this column in the last
year, and show me the lineage from the regulatory report back to the system of record". Platforms
differ enormously here, and the differences are concrete and checkable: automatic column-level lineage
versus none, a 365-day access-history retention versus 90 days, a first-class write-once retention
mode versus no immutability at all. These are the properties most likely to be discovered late, when
they are expensive.

**Retention obligations and lakehouse mechanics genuinely conflict.** Table formats keep tables fast by
rewriting files — compaction merges small files, snapshot expiry deletes old ones. Write-once storage
policies exist to prevent exactly that. An organisation with records-retention obligations that
adopts a lakehouse without resolving this ends up with either a table that cannot be maintained or a
retention control that does not hold. The resolution is usually architectural — an immutable landing
zone under a separate policy from the maintained analytical tables — and it needs to be decided at
selection time, because it constrains which platform can hold the records.

**Concentration is a risk in its own right, and it cuts against the incumbent.** Consolidating identity,
productivity, BI, and the data platform onto one supplier is genuinely efficient and genuinely
integrates better. It also means one supplier's outage, pricing decision, licensing change, or
regional exit reaches every layer at once, and third-party-risk frameworks in regulated sectors treat
that as a distinct exposure requiring its own assessment and mitigation. The option that scores best
on integration is, by construction, the option that scores worst here. That is not a reason to reject
it — it is a reason to make the trade consciously and write down the compensating controls, because
the question will be asked.

## Candidate Options

Each candidate below lists what it is, capability notes (marked **[verified]** where checked against
vendor documentation on 2026-07-26, **[assessment]** where it is judgement), and an explicit "do not
choose this when".

### 1. Microsoft Fabric

A single SaaS analytics platform: OneLake as the tenant-wide storage layer in Delta-Parquet, with
warehouse, lakehouse, data engineering, real-time, data science, and Power BI workloads sharing one
capacity and one governance surface. Purchased as F SKUs (capacity units), or run on an existing
Power BI Premium P capacity.

- **[verified]** Capacity SKUs run F2 (2 CU) through F8192. Microsoft's migration guidance maps
  P1→F64, P2→F128, P3→F256, P4→F512, P5→F1024 ("each P SKU v-core corresponds to 8 CUs") while
  warning: "Don't interpret it as functional or licensing equivalence."
- **[verified]** **Power BI Premium P SKUs support Fabric.** On a P capacity, Fabric items are
  disabled until a Fabric administrator enables them via the "Users can create Fabric items" tenant
  setting; once enabled, non-Power-BI Fabric items (lakehouses, warehouses, notebooks, pipelines) run
  on that existing capacity, consuming the same CUs, with no additional charge documented. This is
  the single most commonly missed commercial fact in this comparison — an organisation can be
  licensed for the platform it is about to procure.
- **[verified]** **But the P-capacity path forfeits precisely the controls a regulated buyer needs.**
  Microsoft publishes an explicit F-versus-P parity table. Available on F SKUs and **not** on
  P SKUs: Azure Resource Manager APIs and Terraform, **managed private endpoints**,
  **workspace-level private links**, **customer-managed keys for workspaces**, trusted workspace
  access, on-demand resizing, pause and resume, and Spark autoscale billing. (Power BI autoscale
  runs the other way — P only.) **[assessment]** The "we already own it" path and the
  "we can evidence it to an examiner" path are therefore not the same path. Treat the free
  P-capacity route as a pilot mechanism, not as the production licensing answer.
- **[verified]** P SKUs are being retired, but **there is no single global retirement date**: "Each
  P SKU subscription retires at the end of its current agreement term," Microsoft no longer sells new
  P SKUs, and "migration isn't automatic" — an F SKU is purchased in Azure and each workspace is
  reassigned manually. After a subscription expires the documented ladder is days 1–30 grace at no
  charge, days 31–90 "access is throttled, interactive operations are delayed", and from day 91
  "all operations are rejected. Data is retained but inaccessible." Fabric is not available in
  sovereign clouds, so P SKUs remain supported there. Pro and PPU are unaffected.
- **[verified]** There is a hard per-user cost cliff at F64. Below F64, every user viewing Power BI
  content needs a Pro or PPU licence; at F64 or above, a Free licence plus a viewer role suffices.
  Premium Per User does **not** provision a Fabric capacity and cannot run non-Power-BI Fabric items;
  neither does a Pro licence alone.
- **[verified]** The 60-day trial capacity is "either an F4 capacity (4 capacity units) or an F64
  capacity" with 1 TB of OneLake storage — not always F64, as is widely assumed. Trial capacities do
  not support Copilot, trusted workspace access, or AI experiences, and **Private Link is disabled**
  on trial.
- **[verified]** The operational failure mode is throttling, and it is well documented. Consumption is
  smoothed — interactive operations over 5 to 64 minutes, background operations over 24 hours — and
  bursting lets a job temporarily exceed the SKU. Overage then escalates: up to 10 minutes of future
  capacity is consumed without penalty; 10–60 minutes delays interactive jobs by 20 seconds at
  submission; 60 minutes to 24 hours **rejects** interactive jobs; beyond 24 hours all requests are
  rejected. In-flight work is allowed to finish. Recovery is by burndown, by scaling up, or by
  pause-and-resume (which bills the accumulated future usage immediately). **[assessment]** This is a
  materially different failure mode from a credit-based warehouse: the platform stops rather than
  spending, which most organisations prefer, provided someone owns the capacity-sizing decision.
- **[verified]** OneLake "stores tables in Delta Parquet or Iceberg format", and shortcuts read
  external stores in place — ADLS Gen2, Azure Blob, Amazon S3 and S3-compatible (read-only), Google
  Cloud Storage (read-only), Dataverse, OneDrive/SharePoint, and on-premises sources via the
  data gateway. Snowflake and Databricks Unity Catalog are **not** shortcut targets; those integrate
  through mirroring instead.
- **[verified, with a caveat]** OneLake exposes an Iceberg REST catalog endpoint, documented as
  **read-only** ("operations that handle metadata write operations aren't yet supported"), Iceberg
  **V2 only**, single-level namespaces, same-region shortcuts only, with 5-second-to-2-minute
  conversion latency and **private links not supported**. The GA-versus-preview status of the
  underlying Delta/Iceberg metadata virtualisation **is genuinely contradictory in Microsoft's own
  documentation** as read on 2026-07-26 — the archive records it generally available in February 2026
  while the live what's-new page still lists it under preview features. Do not assert a status either
  way without checking on the day.
- **[verified]** Customer-managed keys exist at **workspace** level, on F SKUs only, using Azure Key
  Vault or Managed HSM. The exclusions are the important part and they are enumerated in the docs:
  CMK does **not** cover data in Spark clusters — "data stored in temp discs as part of shuffle or
  data spills or RDD caches in a spark application… includes all the Spark Jobs from Notebooks,
  Lakehouses, Spark Job Definitions" — nor Spark history-server job logs, attached libraries, pipeline
  and copy-job metadata, ML model and experiment metadata, lakehouse column names, or warehouse
  backend cache. **[assessment]** An exclusion covering most of the data-engineering compute path
  means "all Fabric data at rest is under customer key control" is not a supportable statement. There
  is **no hold-your-own-key or external-key-store option** anywhere in the Fabric security
  documentation — a verified absence, not an oversight in this write-up.
- **[verified]** The public endpoint can be eliminated: tenant-level private links plus the "Block
  Public Internet Access" setting. The cost is a long, documented casualty list — on-premises data
  gateways fail to register, the Fabric Capacity Metrics app is unsupported, Copilot is unsupported,
  Publish to Web and PDF/PowerPoint export stop working, warehouse copy operations and T-SQL queries
  against an Eventhouse are blocked, cross-tenant shortcuts are unsupported, Spark starter pools are
  disabled (3–5 minute session starts), and trial capacities are excluded entirely. Note also that
  **tenant-level private link is not a superset of workspace-level**: a workspace that blocks public
  access "can only be accessed through a workspace-level private link", which is an F-SKU feature.
- **[verified]** **Retention and legal hold: there is none.** Neither the OneLake overview nor the
  OneLake disaster-recovery documentation mentions immutability, WORM, retention locks, or legal
  hold, and the Microsoft Purview retention-policy supported-locations list contains no mention of
  Fabric, OneLake, Power BI, lakehouses, or warehouses — I grepped the full page independently and
  found zero matches. What exists instead is a fixed, non-configurable **7-day OneLake soft delete**,
  workspace retention (7–90 days, 30 days fixed for My Workspace), and item recovery, which is
  **disabled by default**, covers an allowlist of item types, does not restore share permissions, and
  permanently loses warehouse snapshots. **[assessment]** For an organisation with records-retention
  obligations over analytical data, this is a gap, not a configuration exercise.
- **[verified]** Lineage is workspace-scoped and shallow: the lineage view shows relationships within
  a workspace plus external data sources "one-step upstream", and "downstream items in different
  workspaces aren't shown". **No column-level lineage is documented.** Audit is stronger — roughly
  795 documented operation types — but note the default Microsoft Purview audit retention is **180
  days** (changed from 90 for records generated on or after 2023-10-17), that Fabric records sit in
  the 180-day bucket even under the Audit Premium default policy, and that the Fabric-native activity
  events API only serves **the last 28 days**. Also note that operation names were standardised in
  July 2025, which breaks log parsers keyed to the old names.
- **[verified]** Microsoft Purview Unified Catalog is **not** included with Fabric. Fabric is an
  explicitly-listed pay-as-you-go Purview data source, metered on "number of unique assets
  governed/day" for curation and on data-governance processing units for health management;
  Information Protection and DLP over Fabric are metered the same way. Only the in-product OneLake
  catalog Govern tab is free. **[assessment]** Governance cost belongs in the Fabric business case
  and is routinely omitted from it.
- **[verified]** Multi-Geo is supported for Fabric workloads, not only Power BI — compute and storage
  including OneLake sit in the multi-geo region while tenant metadata stays in the home region — but
  "workspaces with non-Power BI Fabric items can't be moved between regions", so the placement is
  effectively permanent. Copilot processing may cross geographies by design: the Azure OpenAI
  deployments backing it are documented in US datacentres and the EU data boundary, with tenants in
  the UK, Australia, Canada, Brazil, India, Japan, Korea, and elsewhere routed cross-geo. The three
  Copilot cross-region tenant switches all default to disabled.
- **[assessment]** Fabric's real advantage is not any individual workload — it is that one capacity,
  one identity model, one storage layer and one portal collapse the integration work that classic
  Azure analytics leaves to the customer. For a small team this is worth more than any feature, and
  it is why Fabric wins profile C below.

**Choose it when:** the estate is Microsoft-centric, Power BI is already the BI standard, the team is
small, and the analytical workload is BI-led with moderate engineering depth. It is the fastest path
to first value in that estate by a wide margin, and often the cheapest incremental one.

**Do not choose it when:** you have records-retention or legal-hold obligations over the analytical
store and no separate immutable landing zone — this is the disqualifier, and it is verified rather
than assumed. Also avoid it when key custody must cover the Spark compute path; when the workload is
heavily ML- or streaming-led and needs engine flexibility; when a multi-year production track record
in your regulated sector is a selection criterion (see the maturity note below); or when your
third-party-risk posture cannot absorb adding the data platform to a supplier that already holds
identity, productivity, and BI. It is also the wrong answer if the organisation's data gravity is on
another cloud — shortcutting across clouds works, but paying egress forever to keep a platform you
chose for integration reasons is a poor trade.

**On maturity, precisely.** I could not confirm Fabric's platform general-availability date against
any reachable official Microsoft page this session: there is no Fabric entry on Microsoft's product
lifecycle site, the announcement blog is Cloudflare-blocked to automated retrieval, and neither the
what's-new page nor its archive states it. Rather than repeat a remembered date, use the better
signal — the **documented GA dates of the capabilities a regulated buyer depends on**: OneLake Table
APIs and the Iceberg REST catalog in February 2026, OneLake security and data access roles in May
2026, Fabric Item Recovery in June 2026, and no documented GA date at all for tenant or
workspace private links, Block Public Internet Access, managed private endpoints, workspace CMK,
Multi-Geo, or surge protection. **[assessment]** The governance and isolation surface is months old,
not years, and parts of it have no published status. That is the maturity argument, and it is
stronger and more checkable than any launch date.

### 2. Classic Azure analytics (ADLS Gen2 + Synapse and/or Data Factory + Power BI + Purview)

The component-assembled Azure stack that predates Fabric: Data Lake Storage Gen2 for storage, Synapse
Analytics (dedicated SQL pools, serverless SQL, Spark pools) and/or Data Factory for processing and
orchestration, Power BI for delivery, Purview for cataloguing and governance.

- **[verified]** Azure Synapse Analytics follows the Modern Lifecycle Policy and Microsoft's product
  lifecycle page lists it as **"In Support" with no retirement date** (page last updated 2024-01-24;
  checked 2026-07-26). Anyone telling you Synapse is "end of life" is over-stating the public record.
- **[verified]** The investment direction is nonetheless unambiguous: the Synapse "what's new" URL
  now redirects to the Microsoft Fabric what's-new page, the Synapse product overview carries a
  document date of 2024-07-10, and Fabric shipped AI-assisted Synapse-to-Fabric migration tooling
  (in preview) in its July 2026 release notes. **[assessment]** A supported product that has stopped
  accruing documentation and has vendor-supplied migration tooling pointed away from it is a
  maintenance-mode product in everything but the formal notice. Plan accordingly; do not claim a
  retirement date that does not exist.
- **[verified]** This stack's decisive advantage is **retention**. Azure Blob immutable storage
  provides WORM through time-based retention policies and legal holds; a locked time-based policy
  cannot be deleted or shortened (only extended, at most five times at container level), with a
  maximum interval of 146,000 days. Microsoft commissioned an independent records-management
  assessment (Cohasset Associates) finding it meets the relevant storage requirements of CFTC Rule
  1.31(c)-(d), FINRA Rule 4511, and SEC Rule 17a-4(f).
- **[verified]** Important limit for lake designs: **version-level WORM is not supported on storage
  accounts with hierarchical namespace enabled** — that is, on ADLS Gen2. Container-level WORM *is*
  supported there. **[assessment]** Container-level WORM applies to every blob in the container and
  blocks modification and deletion, which is incompatible with an analytical table that compacts and
  expires snapshots. The workable design is an immutable landing container holding the retained
  records, with the maintained analytical tables in a separate, mutable container derived from it.
- **[verified]** Microsoft Purview today spans data security, data governance (Data Map and Unified
  Catalog), and data compliance (including Audit, eDiscovery, Data Lifecycle Management, Records
  Management) under one portal. **[assessment]** The governance portion has been substantially
  re-architected relative to the older standalone Purview account model; verify the current SKU,
  metering model, and automatic-lineage coverage for your specific sources before relying on it in a
  business case — this is the part of the Microsoft stack where public documentation and product
  reality have drifted most.

**Choose it when:** retention and legal hold over analytical data are hard requirements; when the
organisation already operates ADLS Gen2 with hardened key, network, and immutability policy; when
fine-grained control of each component's network and key configuration matters more than integration
convenience; or as the storage substrate *underneath* another platform rather than as a platform in
itself.

**Do not choose it when:** the team is small. This is the highest-integration-burden option in the
comparison that is not self-managed open source — five products, five control planes, five identity
and network configurations, and no single throat to choke for a cross-product failure. Also do not
choose it as a *new-build* platform without a specific reason that Fabric cannot meet, because you
will be building on the component the vendor is steering away from, and the talent market is moving
with the vendor.

### 3. Databricks

The lakehouse platform: Delta Lake (and now Iceberg) tables on the customer's own object storage,
Unity Catalog as the governance plane, with classic and serverless compute. Available on AWS, Azure,
and GCP; on Azure it is an Azure resource, sold and billed through Azure, documented by Microsoft.

- **[verified]** External Iceberg clients — the documentation names Apache Spark, Apache Flink, and
  Trino — can read Unity Catalog tables through an Iceberg REST catalog endpoint
  (`/api/2.1/unity-catalog/iceberg-rest`). Managed Iceberg tables are readable **and writable**;
  foreign Iceberg tables and UniForm-enabled Delta tables (managed and external) are read-only
  through that endpoint. **[assessment]** This is the strongest open-access position of the
  commercial platforms compared here: an external engine reads the production table, in place, no copy.
- **[verified]** Customer-managed keys on Azure Databricks require the **Premium** tier and cover
  three distinct scopes — managed disks in the compute plane, managed services in the control plane
  (notebook source and results, secrets, SQL queries and query history, Git credentials), and the
  DBFS root workspace storage account. Keys come from Azure Key Vault or Key Vault Managed HSM.
- **[verified]** Serverless network isolation is configured through account-level **network
  connectivity configurations** (NCCs) that manage private endpoints from the serverless plane to
  customer resources; where no private endpoint is configured, serverless reaches storage over
  service endpoints identifiable by the `AzureDatabricksServerless` service tag, and reaches other
  resources via NAT IPs. Control-plane-to-serverless traffic is stated to traverse the cloud backbone
  rather than the public internet. Microsoft's documentation carries a **2026-06-09 deadline** for
  migrating storage accounts that allowlist Databricks serverless subnet IDs onto a network security
  perimeter — a live migration item, not a theoretical one.
- **[verified]** The compliance security profile is required to process data regulated under C5,
  K-FSI, PCI-DSS, UK Cyber Essentials Plus, CCCS Medium (Protected B), TISAX, and ISMAP, and
  **becomes required for HIPAA, HITRUST, and IRAP on 2026-09-01**. It is billed as an Enhanced
  Security and Compliance add-on, and it restricts the workspace to a documented subset of preview
  features.
- **[verified]** A real residency caveat, stated in that same document: Databricks identities and
  their attributes are stored **in the United States** as well as in each workspace region, and
  customer-defined free-text fields (workspace, compute, job, tag, credential, storage account names,
  Git repository IDs and URLs) "might be stored, processed, or accessed outside the compliance
  boundary". This is the kind of specific that belongs in a residency assessment and is almost never
  in a comparison.
- **[verified]** Product naming has moved: Delta Sharing is now presented as **OpenSharing**, Delta
  Live Tables as **Lakeflow pipelines**, asset bundles as **Declarative Automation Bundles**, and
  there is a managed Postgres OLTP service (**Lakebase**). **[assessment]** If a document you are
  reading still uses the old names throughout, it predates mid-2026 and its capability claims should
  be re-checked.
- **[assessment]** There is no first-class legal-hold or WORM feature for Delta or Unity Catalog
  managed tables, and there is a structural reason: `OPTIMIZE` and `VACUUM` exist to rewrite and
  delete files, which is precisely what object-lock immutability prevents. Retention has to be
  designed around the tables, not applied to them. I did not find vendor documentation resolving this
  either way — see the open-questions list.

**Choose it when:** the workload mix includes serious ML or streaming alongside BI; when openness and
a credible exit are weighted heavily; when the team has real data-engineering depth; or when you want
a platform that is a distinct supplier from your identity and productivity vendor while still billing
through your existing cloud commitment.

**Do not choose it when:** the workload is straightforward SQL reporting on modest data and the team
is small — you will pay in operational complexity and cost for flexibility you do not use. Also avoid
it when the organisation cannot absorb the residency caveats above, when the analytical workload is
almost entirely inside one SaaS application's data model (see option 8), or when the buying
organisation genuinely cannot manage a two-vendor split of compute and cloud infrastructure.

### 4. Snowflake

A fully-managed multi-cloud data platform with a strict separation of storage, compute (virtual
warehouses), and a cloud-services layer. Runs on AWS, Azure, and GCP; the account is pinned to one
cloud and region.

- **[verified]** Editions gate the controls that regulated buyers need. **Business Critical** (or VPS)
  is required for customer-managed encryption keys via Tri-Secret Secure; for private connectivity via
  AWS PrivateLink, Azure Private Link, or Google Cloud Private Service Connect; for PHI under
  HIPAA/HITRUST; for PCI DSS; for public-sector requirements such as FedRAMP and ITAR; and for failover
  and failback between accounts. Extended Time Travel up to 90 days requires Enterprise or above —
  Standard is capped at 1 day.
- **[verified]** Tri-Secret Secure composes a Snowflake-maintained key with a customer-managed key
  from AWS KMS, Azure Key Vault, or Google Cloud KMS. If the customer key becomes unavailable,
  "after 10 minutes, if the key remains unavailable, all data operations in your Snowflake account
  will cease completely." **[assessment]** That is the control working as intended and an availability
  dependency that needs a named owner and a tested runbook.
- **[verified]** ACCOUNT_USAGE views — including QUERY_HISTORY and ACCESS_HISTORY — retain **1 year
  (365 days)** of history. ACCESS_HISTORY requires Enterprise Edition or higher. **[assessment]** A
  year of column-level access history available in SQL, with no build required, is one of the
  strongest audit-evidence positions in this comparison.
- **[verified]** On Iceberg: Snowflake-managed Iceberg tables get "full Snowflake platform support
  with read and write access"; externally-managed (external catalog) tables get "limited Snowflake
  platform support" and Snowflake "does not assume any life-cycle management" for them. External
  engines can read via an Iceberg REST Catalog API through the Horizon Catalog, and the documentation
  states **only Snowflake-managed Iceberg tables are supported** for that access.
- **[verified]** Documented limits on Iceberg tables include no Fail-safe, no hybrid or
  temporary/transient tables, no Snowflake encryption, and constraints on streams for
  externally-managed tables. The documentation's treatment of replication for Iceberg tables and
  external volumes is not internally consistent as read on 2026-07-26 — verify against your specific
  configuration rather than trusting either reading.
- **[assessment]** There is no WORM or legal-hold primitive. Time Travel (≤90 days) and Fail-safe are
  recovery mechanisms, not retention controls, and Fail-safe is not customer-configurable. Long
  retention means exporting to immutable object storage.

**Choose it when:** operability is the binding constraint. Snowflake asks less of an operations team
than anything else here that is not a SaaS application's built-in analytics, the SQL talent market is
the deepest of any candidate, and it has the longest continuous production record among the
independent platforms. Also choose it when multi-cloud portability or supplier independence from the
cloud and identity vendor is a stated objective.

**Do not choose it when:** cost per unit of work at scale is a primary constraint — it is the most
expensive candidate here for heavy, steady transformation workloads. Also avoid it when the workload
is ML-first rather than SQL-first; when the controls you need sit in Business Critical but the budget
was built on Enterprise (a very common and expensive surprise); or when the data must remain in
storage the organisation controls, since native table storage is Snowflake's, not yours — Iceberg
tables on an external volume change this, at the cost of some platform features.

### 5. AWS-native (S3 + Glue + Lake Formation + Athena and/or Redshift)

Object storage as the substrate, Glue Data Catalog for metadata, Lake Formation for governance,
Athena for ad-hoc SQL, Redshift for warehousing, plus S3 Tables for managed Iceberg.

- **[assessment]** The strongest storage-layer controls in the comparison. S3 Object Lock provides
  governance and compliance retention modes plus legal holds; KMS integration is mature; VPC endpoint
  policies and a data-perimeter design (see `patterns/aws-data-perimeter.md`) allow a genuinely closed
  network posture.
- **[assessment]** The weakness is coherence, not capability. This is an assembled platform: the
  catalogue, the governance layer, the query engines, the warehouse, and the cataloguing/lineage
  product are separate services with separate models, and the lineage and business-catalogue layer has
  been re-branded and re-homed more than once in recent years. A small team assembling it spends its
  first two quarters on integration.
- See the open-questions list for the specific AWS claims I could not pin down this session.

**Choose it when:** the estate is already AWS-centric, the data gravity is in S3, and there is a
platform team that can assemble and own the pieces. Also choose it when storage-level retention and
legal hold over the analytical data are hard requirements and you want them enforced by the object
store itself.

**Do not choose it when:** the organisation is not already on AWS — none of these components is
compelling enough to justify a cloud migration — or when the team is small. It is also a poor choice
when the requirement is "one governed platform for the whole business", because the governance surface
spans several services and the story you can tell a reviewer is correspondingly harder to assemble.

### 6. GCP-native (BigQuery + Dataplex)

BigQuery as a serverless warehouse over its own columnar storage, with BigLake for tables over object
storage, managed Iceberg tables, and Dataplex Universal Catalog for cataloguing, quality, and lineage.

- **[assessment]** BigQuery is technically excellent and operationally the least demanding warehouse
  of the three hyperscaler-native options — genuinely serverless, with a mature editions/slots model.
  Automatic lineage in the Google catalogue is a real capability rather than a promise.
- **[assessment]** It is the weakest *fit* for most enterprises in this comparison, and the reason is
  estate, not product: outside organisations already on Google Cloud, adopting BigQuery means
  introducing a third cloud relationship — identity federation, network connectivity, procurement,
  and a security review — to gain a warehouse advantage that Snowflake or Databricks can largely
  match without the estate change. It scores well on capability and poorly on fit, and fit is
  weighted higher here for good reason.
- See the open-questions list for the GCP claims I could not pin down this session.

**Choose it when:** the organisation is already on Google Cloud; when the analytical workload is
bursty and unpredictable enough that true serverless economics matter; or when a specific Google
capability (geospatial, ML integration, a data-sharing relationship with a counterparty already on
BigQuery) is the actual driver.

**Do not choose it when:** the organisation is not on Google Cloud and has no other reason to be. The
platform is not the problem; the third cloud relationship is. Also avoid it where the retention and
legal-hold requirement is central, since that is the dimension where it is furthest from the
storage-native options.

### 7. Self-managed open source (object storage + Iceberg + a catalogue + Trino/Spark)

Bring your own everything: object storage, Apache Iceberg as the table format, a catalogue
implementing the Iceberg REST specification, Trino and/or Spark for compute, plus separately-chosen
projects for access control, lineage, cataloguing, orchestration, and quality.

- **[assessment]** The best answer on openness and on concentration risk, unambiguously. No vendor
  controls the format, the catalogue, or the engine; every component is substitutable; there is no
  exit cost because there is no lock.
- **[assessment]** It is also the option that fails most often, and it fails on operations. The
  cluster, the catalogue, the table-maintenance schedule, the policy engine, the lineage collector,
  and the orchestrator are each a service to run, monitor, patch, and upgrade — and the enterprise
  capabilities that arrive built-in elsewhere (fine-grained access control, column masking, automatic
  lineage, business cataloguing, audit reporting) arrive here as additional projects to integrate and
  operate. The talent market for this combination is the thinnest of any candidate, and the people who
  can do it well are expensive and mobile.
- See the open-questions list for the open-source project-status claims I could not pin down this session.

**Choose it when:** there is a real platform engineering team with distributed-systems depth and a
mandate to keep it; when supplier independence is a first-order requirement rather than a preference;
when data volumes are large enough that commercial per-unit pricing is genuinely prohibitive; or when
an existing on-premises or sovereign object store must be the substrate.

**Do not choose it when:** you cannot name the four or more engineers who will operate it in three
years' time. That is the whole test. Also avoid it when audit evidence and lineage are central
requirements on a short timeline, because those are the components you will be assembling last and
they are the ones the reviewer asks about first.

### 8. The system-of-record vendor's own analytics offering

The analytics product shipped by the vendor of the dominant source application — the ERP, CRM, HCM,
ITSM, or core platform. Routinely omitted from comparisons, and routinely the fastest path to first
value, because the semantic model, the security model, and the data definitions already exist and are
already correct.

- **[assessment]** The advantage is real and underrated. Reproducing a major application vendor's
  semantic model in a general-purpose platform is months of work that produces, at best, a slightly
  worse copy of something the vendor maintains for you. If the question is "we need governed reporting
  on our core system by the end of the quarter", this is very often the honest answer.
- **[assessment]** The disadvantages are equally real and are structural rather than fixable: it can
  only ever serve data from that application, so it cannot be the enterprise platform; the data is
  usually in the vendor's store under the vendor's key and network model, with weaker isolation and
  key-custody options than any dedicated platform here; and it deepens dependency on a supplier whose
  primary product is already business-critical.
- **[assessment]** The zero-copy sharing arrangements several application vendors now offer with the
  major data platforms materially change this calculus where they apply — read in place, no pipeline
  to build, no copy to govern. The specific arrangements, their availability, and whether they read in
  place or copy vary by vendor and change frequently; verify the current position for your specific
  application before relying on it. See the open-questions list.

**Choose it when:** one application genuinely is the business, the reporting need is about that
application's own processes, the timeline is short, and there is no data-engineering team. Also choose
it as a deliberate **first move** alongside a longer platform build — it delivers value in the first
quarter while the platform is stood up.

**Do not choose it when:** the analytical questions cross systems. The moment a report needs the ERP
joined to the CRM joined to an operational database, this option is disqualified and no amount of
connector marketing changes that. Also avoid it when data must be retained beyond the application's
own retention model, when key custody or network isolation requirements exceed what the application
vendor offers, or when it would be the fourth or fifth analytics silo rather than the first.

**[assessment] The most useful framing:** this option rarely wins a *platform* decision on points —
it scores near the bottom of every weighted profile below because it cannot host anything else and
locks the data. But it very often wins the *first ninety days*. The frequently-correct answer is
"both, sequenced": ship the application vendor's analytics now, build the platform behind it, and
retire the former only if and when the latter genuinely surpasses it.

## Decision Framework

### Dimensions and default weights

Fourteen dimensions. Two of them — **estate fit** and **incremental cost** — are organisation-specific
and must be scored by the reader for their own situation; the other twelve are scored once below.
Weights are 1 (marginal) to 5 (decisive). The defaults reflect a mid-size regulated organisation; the
worked profiles show how much the answer moves when they change.

| # | Dimension | What it measures | Default weight |
|---|-----------|------------------|----------------|
| 1 | **Estate fit** *(org-specific)* | Identity, BI already deployed, enterprise agreements, capacity already owned | 5 |
| 2 | **Operability vs available staff** | Whether the named team can run it in steady state | 5 |
| 3 | **Incremental cost to production** *(org-specific)* | New spend required given what is already owned | 3 |
| 4 | **Time to first value** | Elapsed time to a governed report a business user trusts | 3 |
| 5 | **Talent availability** | Depth of the hiring market for the required skills | 3 |
| 6 | **Workload breadth** | BI, ETL, ML, streaming, real-time on one platform | 3 |
| 7 | **Openness and exit cost** | Can other engines read the data in place; what leaving costs | 3 |
| 8 | **Vendor concentration risk** | Dependency added to a supplier already holding other layers | 3 |
| 9 | **Network isolation** | Private connectivity maturity, public-endpoint elimination, serverless included | 4 |
| 10 | **Key custody** | CMK/BYOK/HYOK support and its real coverage limits | 3 |
| 11 | **Data residency** | Where data — and identity metadata — actually rests | 3 |
| 12 | **Lineage and audit evidence** | What can be *shown*, automatically, and for how long | 5 |
| 13 | **Retention and legal hold** | WORM, holds, and their compatibility with table maintenance | 5 |
| 14 | **Maturity in regulated industries** | Years in regulated production, not recency of launch | 5 |

Note the deliberate weighting: cost sits at 3 and features do not appear at all. If cost is the
dimension deciding your platform choice, either the requirements are not yet real or the candidates
are not actually comparable.

### Capability scores

**These scores are my assessment, not vendor claims.** They are informed by the verified capability
facts above, but the compression of a capability into 0–5 is a judgement and reasonable architects
will disagree. Use them as a starting point and change the ones you disagree with — the framework is
the deliverable, not the numbers. Higher is better throughout, including for concentration risk
(5 = least concentrated).

| Dimension | Fabric | Azure classic | Databricks | Snowflake | AWS | GCP | OSS | SoR vendor |
|-----------|:------:|:-------------:|:----------:|:---------:|:---:|:---:|:---:|:----------:|
| Operability vs staff | 4 | 2 | 3 | 5 | 2 | 4 | 1 | 5 |
| Time to first value | 5 | 2 | 3 | 4 | 2 | 4 | 1 | 5 |
| Talent availability | 3 | 3 | 4 | 5 | 4 | 3 | 2 | 3 |
| Workload breadth | 4 | 4 | 5 | 3 | 4 | 4 | 4 | 1 |
| Openness / exit cost | 4 | 3 | 5 | 3 | 4 | 3 | 5 | 1 |
| Concentration risk | 1 | 2 | 4 | 4 | 2 | 2 | 5 | 1 |
| Network isolation | 3 | 5 | 4 | 4 | 5 | 4 | 5 | 2 |
| Key custody | 2 | 5 | 4 | 4 | 5 | 4 | 5 | 1 |
| Data residency | 3 | 5 | 3 | 4 | 5 | 4 | 5 | 2 |
| Lineage / audit evidence | 3 | 3 | 5 | 4 | 3 | 4 | 2 | 3 |
| Retention / legal hold | 1 | 5 | 2 | 2 | 4 | 2 | 4 | 2 |
| Regulated maturity | 2 | 4 | 4 | 5 | 5 | 4 | 3 | 4 |

Estate fit and incremental cost are supplied per profile below.

### Worked profile A — regulated, Microsoft-centric estate, small data team

Existing Microsoft identity and productivity estate with Power BI already the BI standard and
Premium capacity already owned; three to five data engineers; examiner-facing reporting obligations
including records retention.

*Weights:* estate 5, cost 3, operability 5, time-to-value 3, talent 3, breadth 3, openness 3,
concentration 3, network 4, keys 3, residency 3, lineage 5, retention 5, maturity 5.
*Estate fit:* Fabric 5, Azure classic 5, Databricks 4, Snowflake 3, AWS 2, GCP 1, OSS 2, SoR 4.
*Incremental cost:* Fabric 5, Azure classic 3, Databricks 3, Snowflake 2, AWS 3, GCP 3, OSS 4, SoR 4.

| Rank | Candidate | Score (max 265) | |
|:----:|-----------|:---------------:|---|
| 1 | Databricks | 199 | 75.1% |
| 2 | Snowflake | 198 | 74.7% |
| 3 | Azure classic | 196 | 74.0% |
| 4 | AWS-native | 187 | 70.6% |
| 5 | Self-managed OSS | 173 | 65.3% |
| 6 | GCP-native | 172 | 64.9% |
| 7 | **Fabric** | **168** | **63.4%** |
| 8 | SoR vendor | 152 | 57.4% |

**Read this correctly.** The top three are separated by three points out of 265 — that is a tie inside
the model's resolution, and claiming Databricks "wins" by one point would be false precision. The
honest finding is that **three options are viable and the incumbent-vendor answer is not among them**,
and the reason is specific and checkable rather than aesthetic: Fabric is dragged down by three
heavily-weighted dimensions where it scores 1 or 2 — a verified absence of any retention or legal-hold
primitive over OneLake, a governance and isolation surface whose documented GA dates fall in 2026
rather than years earlier, and maximum vendor concentration in an estate that already runs on the same
supplier's identity, productivity, and BI. Note also that the fourth low score, key custody at 2, is
driven by a documented exclusion rather than an opinion: workspace CMK does not cover the Spark
compute path.

**What would change it.** Fabric moves into contention the moment the retention obligation is
architecturally separated — records retained in an immutable ADLS Gen2 container under a locked
container-level time-based policy, with OneLake shortcutting to it and holding only derived analytical
tables. That is a legitimate design, it costs one storage account, and it converts the weakest score
in the table into a non-issue. **[assessment]** For a Microsoft-centric regulated organisation, that
hybrid is very often the right answer, and it is the answer neither a Fabric datasheet nor a
Databricks datasheet will propose.

### Worked profile B — multi-cloud product engineering, ML-heavy, lightly regulated

AWS-primary estate with a second cloud in use, third-party identity, mixed BI tooling; a real platform
team; machine learning and streaming are first-class workloads; no records-retention obligation.

*Weights:* estate 3, cost 4, operability 3, time-to-value 3, talent 4, breadth 5, openness 5,
concentration 4, network 2, keys 2, residency 2, lineage 3, retention 1, maturity 2.
*Estate fit:* Fabric 1, Azure classic 2, Databricks 5, Snowflake 5, AWS 5, GCP 3, OSS 4, SoR 2.
*Incremental cost:* Fabric 2, Azure classic 2, Databricks 3, Snowflake 2, AWS 4, GCP 4, OSS 5, SoR 3.

| Rank | Candidate | Score (max 215) | |
|:----:|-----------|:---------------:|---|
| 1 | **Databricks** | **174** | **80.9%** |
| 2 | Snowflake | 164 | 76.3% |
| 3 | AWS-native | 160 | 74.4% |
| 4 | Self-managed OSS | 157 | 73.0% |
| 5 | GCP-native | 150 | 69.8% |
| 6 | Azure classic | 133 | 61.9% |
| 7 | Fabric | 124 | 57.7% |
| 8 | SoR vendor | 103 | 47.9% |

A clear result rather than a tie: workload breadth and openness at weight 5, with retention at 1 and
maturity at 2, rewards exactly the platform that carries no format lock and hosts ML natively.

### Worked profile C — Microsoft-centric mid-size, BI-led, not heavily regulated

Same Microsoft estate as profile A, but the analytics is reporting and self-service BI, the regulatory
surface is ordinary commercial compliance, and there is no records-retention obligation over
analytical data.

*Weights:* estate 5, cost 5, operability 5, time-to-value 5, talent 3, breadth 3, openness 2,
concentration 2, network 2, keys 2, residency 2, lineage 2, retention 1, maturity 2.
*Estate fit and incremental cost:* as profile A.

| Rank | Candidate | Score (max 205) | |
|:----:|-----------|:---------------:|---|
| 1 | **Fabric** | **153** | **74.6%** |
| =2 | Databricks | 152 | 74.1% |
| =2 | Snowflake | 152 | 74.1% |
| 4 | Azure classic | 140 | 68.3% |
| 5 | GCP-native | 133 | 64.9% |
| 6 | SoR vendor | 132 | 64.4% |
| 7 | AWS-native | 131 | 63.9% |
| 8 | Self-managed OSS | 122 | 59.5% |

Same capability scores, different weights, different winner — and a legitimate one. When estate fit,
incremental cost, operability, and time to first value are all decisive and the evidence dimensions
are not, the platform that is already partly paid for and already integrated with the identity and BI
estate is genuinely the right answer.

Be equally honest about the margin: 153 against 152 and 152 is a three-way dead heat, not a victory.
The finding worth carrying is not "Fabric wins C" but that **Fabric moves from seventh place to joint
first purely on a change of weights** — the same capability scores, re-weighted for an organisation
with no records obligation and a lighter evidence burden. Across the four tables the top slot is taken
by **three different platforms** (Databricks in A and B, Fabric in C, Databricks and Snowflake tied in
C-prime), which is the point: this framework is a way to expose which dimension is doing the deciding,
not a league table. If your own weighting produces a winner by a single point, you have learned that
the decision is not being made by the model — go and find the qualitative tie-break.

### Sensitivity — profile C after an obligation lands

The same organisation acquires a records-retention obligation and a third-party-risk requirement to
assess concentration. Only the weights change: retention 1 → 5, concentration 2 → 4, network 2 → 4,
keys 2 → 4, lineage 2 → 4, maturity 2 → 4.

| Rank | Candidate | Score (max 275) | |
|:----:|-----------|:---------------:|---|
| =1 | **Databricks** | **202** | **73.5%** |
| =1 | **Snowflake** | **202** | **73.5%** |
| 3 | Azure classic | 198 | 72.0% |
| 4 | AWS-native | 187 | 68.0% |
| 5 | Fabric | 179 | 65.1% |
| 6 | Self-managed OSS | 178 | 64.7% |
| 7 | GCP-native | 177 | 64.4% |
| 8 | SoR vendor | 162 | 58.9% |

Fabric falls from first to fifth without a single capability score changing. **[assessment]** This is
the most useful output of the whole exercise: it identifies precisely which future change invalidates
the decision, which turns an architecture choice into a monitorable one. Record the flip condition in
the ADR and it becomes a review trigger instead of a surprise.

## Sunk Cost Versus Disposal Cost

This distinction is botched in almost every platform conversation, and the resulting argument consumes
more time than the technical comparison does. It is worth getting right because both sides are usually
correct about different things and neither realises it.

**Sunk cost is genuinely irrelevant to a comparison of future paths.** Money already spent on the
incumbent platform cannot be recovered by continuing to use it. The licence fees paid, the
implementation effort expended, and the training delivered are gone regardless of which option is
chosen next, so they carry no weight in choosing between options. That is the correct and complete
statement of the principle.

**Disposal cost is not sunk, and it belongs in the comparison as a line item.** What it will cost to
*stop* using the incumbent is a future cash and accounting event, it differs between the options, and
it is therefore exactly the kind of figure a comparison should include. Treating it as sunk — or waving
it away with the phrase "sunk cost fallacy" — is a straightforward analytical error, and it is also
dismissive of whoever authorised the original spend, who is frequently a finance stakeholder whose
support the change requires. Winning the philosophical point and losing that stakeholder is not a win.

**The failure mode runs both ways.** An advocate for the new platform invokes the sunk-cost fallacy to
dispose of the existing investment rhetorically; this is right about past spend and wrong about what
happens next. A sceptic points at the write-off as a reason not to proceed; this conflates a real
future cost with an argument against change, since a one-off disposal cost can be entirely worth
paying. Both objections dissolve on contact with an actual number.

**So produce the number rather than arguing the principle.** Enumerate what would genuinely be
disposed of:

- **Assets that continue serving other workloads are not written off at all.** A database platform that
  keeps running operational and transactional workloads after the analytical workload moves off it is
  repurposed, not retired, and contributes nothing to the disposal figure. This category is larger than
  people expect and is the most common source of inflated write-off claims.
- **Contract termination charges, decommissioning effort, migration effort, and any accelerated
  depreciation or impairment are real future events.** These are the legitimate contents of the line
  item. Migration effort in particular is usually the largest component and the least well estimated.
- **Where the asset does not yet exist, there is nothing to write off.** A partially built or merely
  planned system has no disposal cost beyond the effort already expended — which is sunk — and possibly
  some contracted commitments. This objection frequently quantifies to zero, and saying so with a
  worked figure is far more persuasive than debating whether the objection is a fallacy.
- **For a listed company an impairment is a disclosed event.** The number therefore has consequences
  beyond the project — timing, materiality, and disclosure — which is a legitimate reason for finance
  to care about it and a reason to involve them early rather than present it as a technicality.

**[assessment]** The practical value of doing this is that the enumerated figure is usually far smaller
than the objection implies, because most of what gets counted falls into the first or third category
above. That converts a philosophical disagreement into a figure a finance stakeholder can verify and
challenge on its merits — a much stronger position than conceding the framing, and a much better use
of the meeting than a debate about fallacies.

## Vendor Concentration Risk

This dimension deserves its own treatment because it is the one most often omitted, and because it
is the one that most often argues against the answer everyone already assumed.

**The trade is real in both directions.** Consolidating identity, productivity, BI, and the data
platform onto a single supplier produces genuine benefits that are not marketing: one identity model
instead of four federation integrations; one commercial relationship and one negotiating position;
one support escalation path; one set of security reviews; and integration that actually works because
one organisation built both ends. For a small team these are not conveniences, they are the
difference between a platform that gets operated and one that does not. Anyone presenting
concentration as purely a risk is arguing badly.

**And the exposure is equally real.** Third-party risk frameworks in regulated sectors treat
concentration as a distinct category — not a sum of the individual dependencies but a property of the
portfolio. The specific exposures are:

- **Correlated failure.** An identity-provider outage at a single supplier takes down authentication,
  productivity, BI, *and* the data platform simultaneously. These are not independent failure domains
  once they share a control plane, and continuity plans written per-system will assume independence
  they no longer have.
- **Commercial asymmetry.** Renewal leverage falls as the share of estate held by one supplier rises.
  A licensing model change — of exactly the kind seen when the Power BI Premium per-capacity SKUs were
  put on a retirement path — reaches every layer at once, and the substitution cost is the sum of all
  layers rather than one of them.
- **Regulatory attention.** Supervisory interest in concentration among financial-sector technology
  suppliers has been rising for years, and the direction of travel in oversight regimes is toward
  treating critical third parties as a systemic matter rather than a firm-by-firm one. The practical
  effect is that "we consolidated for integration benefits" is an answer that will be probed, and
  needs to have been documented at the time rather than reconstructed afterwards.
- **Exit realism.** With four layers on one supplier, the exit plan for any one of them has
  dependencies on the other three. Exit plans written per-system tend to assume the others stay put,
  which is exactly the assumption that fails in the scenario the plan exists for.

**How to use this rather than be used by it.** Concentration is a lever with two legitimate settings,
and the decision record should state explicitly which one was chosen:

1. **Consciously accept and document it.** Choose the integrated answer, name the concentration in
   the risk register, and record the compensating controls: an independent copy of critical data in a
   format and location the primary supplier does not control; an identity break-glass path that does
   not depend on the primary IdP; a tested restore into a second platform for a defined critical
   dataset; and a contractual position on notice periods and regional exit. This is a defensible
   posture and it is far stronger than an undocumented assumption of the same risk.
2. **Deliberately diversify at the platform layer.** Keep identity, productivity, and BI with the
   incumbent — where integration value is highest and substitution cost is lowest — and place the data
   platform with a different supplier. This is why profile A produces Databricks and Snowflake ahead
   of the incumbent even in a thoroughly Microsoft estate: the data platform is the layer where a
   second supplier costs the least integration and buys the most independence, particularly when it
   still bills through the existing cloud commitment.

**The trap to avoid.** Do not treat concentration as an unanswerable objection that blocks the
efficient choice, and do not treat it as a box to tick. It is a weighted dimension like the others —
weight 3 by default, higher in a regulated sector with critical-third-party obligations, lower in an
organisation whose supplier portfolio is already diversified. What is not defensible is leaving it out
of the comparison entirely, which is what almost every vendor-produced comparison does.

## What Is Verified and What Is Judgement

Because this file exists to support a decision that will later be defended, the confidence of every
capability claim is stated. **Sentences marked [verified] in the candidate sections were read from the
cited vendor page on 2026-07-26.** Sentences marked **[assessment]** are judgement. Anything in
neither category, and anything on the "could not be pinned down" list below, must be re-checked before
it is quoted to anyone.

**Verified against vendor documentation on 2026-07-26** (each has a URL in Reference Links; all 34
cited URLs returned HTTP 200 with no redirect drift and substantive page bodies when checked):

- **Microsoft Fabric** — capacity SKU range and the P→F mapping with Microsoft's own
  "don't interpret as functional or licensing equivalence" warning; P-SKU support for Fabric items and
  the tenant switch that enables them; the F-versus-P parity table naming ARM/Terraform, managed
  private endpoints, workspace-level private links, workspace CMK, trusted workspace access,
  on-demand resizing, pause/resume and Spark autoscale billing as F-only (independently re-read and
  confirmed); P-SKU retirement at end of agreement term with no global date, plus the 30/90-day
  post-expiry throttle-then-reject ladder; the F64 per-user viewing threshold; PPU and Pro not
  provisioning a capacity; trial capacity being F4 *or* F64 with Private Link disabled; the smoothing
  windows and the full throttling escalation; OneLake Delta-Parquet-and-Iceberg storage and the
  shortcut source list; the Iceberg REST catalog being read-only, V2-only, same-region, private-links-
  unsupported; workspace CMK being F-SKU-only with the enumerated exclusions including the Spark
  compute path, and the absence of any HYOK/external-key-store option; tenant private link plus Block
  Public Internet Access, the unsupported-feature casualty list, and tenant-level not being a superset
  of workspace-level; workspace-scoped one-hop lineage with no column-level lineage documented; the
  180-day default Purview audit retention and the 28-day Fabric activity API window; Purview Unified
  Catalog being separately metered rather than bundled; Multi-Geo covering Fabric workloads but
  workspaces with non-Power-BI items not being movable between regions.
- **Fabric retention — a verified absence.** Neither the OneLake overview, the soft-delete page, nor
  the retention-and-recovery page documents WORM, immutability, retention locks, or legal hold; and I
  independently grepped the full Microsoft Purview retention supported-locations page and found **zero
  occurrences** of Fabric, OneLake, Power BI, lakehouse, or warehouse. What exists is a fixed 7-day
  OneLake soft delete, workspace retention, and item recovery that is disabled by default. This is the
  single most decision-relevant finding in the file and it is verified, not inferred.
- **Classic Azure** — Azure Synapse Analytics listed as "In Support" under the Modern Lifecycle Policy
  with **no retirement date**, and the Synapse what's-new URL now resolving to the Fabric what's-new
  page (confirmed via `url_effective`). Azure Blob immutable storage: time-based retention versus legal
  hold, locked-policy irreversibility, the 146,000-day maximum, the Cohasset assessment against CFTC
  1.31(c)-(d) / FINRA 4511 / SEC 17a-4(f), and the non-support of version-level WORM on
  hierarchical-namespace (ADLS Gen2) accounts. Microsoft Purview's current solution areas.
- **Databricks** — the Unity Catalog Iceberg REST endpoint and its per-table-type read/write matrix;
  CMK scopes and the Premium tier requirement; serverless network connectivity configurations and the
  2026-06-09 storage-allowlist migration deadline; the compliance security profile's standard list,
  the 2026-09-01 HIPAA/HITRUST/IRAP requirement date, and the documented US identity-storage and
  free-text-field residency caveats; current product naming.
- **Snowflake** — per-edition gating of Tri-Secret Secure, private connectivity,
  HIPAA/PCI/FedRAMP/ITAR and failover; the 10-minute key-unavailability behaviour; Time Travel limits
  by edition; 365-day ACCOUNT_USAGE retention and the Enterprise requirement for ACCESS_HISTORY;
  managed versus externally-managed Iceberg semantics and the managed-only restriction on
  external-engine access.

**Assessment, not vendor claim:** every score in the capability table and every weight in the profiles;
the characterisation of classic Azure analytics as maintenance-mode-in-practice; the claim that
container-level WORM is incompatible with maintained analytical tables; the absence of a first-class
legal-hold primitive on Databricks and Snowflake; the operational-burden rankings; the talent-market
rankings; and the entire "do not choose this when" set. These are the parts of this document a
reasonable architect may disagree with, and disagreement should change the numbers rather than be
suppressed.

**Explicitly NOT verified this session — the AWS-native, GCP-native, self-managed open-source, and
system-of-record candidate sections carry no [verified] markers at all.** Those four sections are
written entirely as assessment: architectural reasoning and market judgement, not documented
capability claims. They are deliberately kept at that altitude rather than dressed up with specifics
I did not check. Treat their *relative scores* as usable and any implied specific as unverified.

**Could not be pinned down this session — do not assert these without checking:**

- Microsoft Fabric: the platform general-availability date (no lifecycle-site entry exists, and the
  announcement blog is inaccessible to automated retrieval — the file deliberately argues maturity
  from documented sub-feature GA dates instead); F-SKU list pricing; and the GA-versus-preview status
  of Delta/Iceberg metadata virtualisation, which **Microsoft's own documentation reports
  inconsistently** — the archive records GA in February 2026 while the live what's-new page still
  lists it under preview. Also unstated anywhere reachable: published GA status for tenant and
  workspace private links, Block Public Internet Access, managed private endpoints, workspace CMK,
  Multi-Geo, and surge protection.
- AWS: whether AWS documents any interaction between S3 Object Lock and Iceberg/Delta compaction or
  snapshot expiry (I found no such documentation, which is not the same as confirming none exists);
  which analytics services support KMS External Key Store-backed keys; the current product name and
  lineage coverage of the AWS business-catalogue layer after its recent re-homing; S3 Tables' current
  limitations and REST-catalog exposure.
- GCP: GA-versus-preview status of BigQuery managed Iceberg tables and external-engine read access;
  the Data Catalog to Dataplex Universal Catalog transition date; Cloud EKM coverage for BigQuery.
- Open source: the current Apache Iceberg specification version and v3 engine support; Apache Polaris
  incubation status; the current maintenance posture of Hive Metastore.
- System-of-record vendors: which zero-copy sharing arrangements are generally available today and
  whether each reads in place or copies; and, for the largest ERP vendor, whether restrictions on
  third-party extraction of its data are technical or contractual. Public documentation on the latter
  is thin and I could not verify contract terms — treat any confident claim in either direction with
  suspicion and ask the vendor in writing.

## Common Decisions (ADR Triggers)

- **Integrated single-vendor platform vs deliberately diversified platform layer** — the concentration
  decision. Record which of the two legitimate postures was chosen and the compensating controls.
- **Fabric vs classic Azure analytics for a new Microsoft-estate build** — integration and speed
  against component-level control and a formally-supported-but-static component set; also the
  retention question, which usually decides it.
- **Run Fabric on existing Power BI Premium capacity vs purchase F SKUs** — no incremental spend
  against access to ARM/Terraform management and managed private endpoints; the free path is a bridge,
  not a destination, given the announced P-SKU retirement.
- **Capacity size relative to the F64 per-user viewing threshold** — below F64 every Power BI viewer
  needs a per-user licence; this can invert the total cost comparison for a wide-readership deployment.
- **Warehouse-first (Snowflake) vs lakehouse-first (Databricks) vs storage-first (cloud-native)** —
  operability and SQL-talent depth against workload breadth and format openness against maximal
  control of storage-layer policy.
- **Managed table format vs externally-managed Iceberg** — full platform features on a managed table
  against direct external-engine access and customer-held storage; on every platform compared here the
  externally-managed path forfeits specific platform capabilities that must be enumerated first.
- **Retention architecture: immutable landing zone vs retention on analytical tables** — table
  compaction and snapshot expiry are incompatible with container-level write-once policy; separating
  retained records from maintained tables is usually the resolution and it constrains platform choice.
- **Edition and tier selection at contract time** — private connectivity, customer-managed keys, and
  compliance profiles are gated behind higher editions or paid add-ons on every commercial platform
  here; budgeting on the lower tier and discovering the gating during security review is a common and
  avoidable failure.
- **Key custody model** — platform-managed vs cloud-KMS customer-managed vs external key store, with
  an explicit owner and runbook for the availability dependency that customer-held keys create.
- **System-of-record vendor analytics as first move vs as the platform** — sequencing it in front of a
  platform build is frequently right; selecting it *as* the platform is right only when the analytical
  scope genuinely never leaves one application.
- **Self-managed open source vs managed platform** — decided by named operators in steady state, not
  by architecture quality or by unit economics.
- **Treatment of the incumbent platform's disposal cost** — an enumerated line item covering
  termination charges, decommissioning, migration effort, and any impairment, held separately from the
  sunk cost already spent and from assets that will be repurposed rather than retired. Worth an ADR
  because the figure is contested, because it is a disclosed event for a listed company, and because
  recording the method prevents the argument being re-run every time the decision is reviewed.
- **Decision review trigger** — the specific weight change or capability GA that would flip the
  outcome, recorded as a monitorable condition rather than left implicit.

## Reference Architectures

- [Microsoft Fabric licensing and capacity concepts](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
  — tenants, capacities, workspace types, SKU table, and the per-user licensing rules that drive cost
- [Azure Synapse Analytics product lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/azure-synapse-analytics)
  — the authoritative support-status record; check this rather than repeating hallway claims
- [Databricks lakehouse platform overview (Azure)](https://learn.microsoft.com/en-us/azure/databricks/introduction/)
  — current platform composition and product naming
- [Snowflake edition feature comparison](https://docs.snowflake.com/en/user-guide/intro-editions)
  — which controls are gated to which edition; read before building a budget
- `patterns/lakehouse-medallion.md` — layered lake design once a platform is chosen
- `patterns/aws-data-perimeter.md` — closed-network posture for an AWS-native platform
- `frameworks/azure-well-architected.md` and `frameworks/aws-well-architected.md` — the workload
  review each vendor expects a platform design to pass

## Reference Links

All links checked and returning HTTP 200 on 2026-07-26.

- [Understand Microsoft Fabric licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
  — F/P SKU table, P-SKU support for Fabric items, P-SKU retirement statement, F64 threshold, PPU limits
- [Microsoft Fabric features by SKU and capacity](https://learn.microsoft.com/en-us/fabric/enterprise/fabric-features)
  — the F-versus-P parity table: ARM/Terraform, managed private endpoints, workspace-level private
  links, workspace CMK, trusted workspace access, pause/resume are F-only
- [Power BI Premium licence migration FAQ](https://learn.microsoft.com/en-us/power-bi/support/premium-migration-faq)
  — P-SKU retirement at end of agreement term, P→F mapping, and the 30/90-day post-expiry throttle ladder
- [Enable Microsoft Fabric for your organization](https://learn.microsoft.com/en-us/fabric/admin/fabric-switch)
  — the tenant setting that enables Fabric items on an existing capacity
- [Microsoft Fabric throttling and smoothing](https://learn.microsoft.com/en-us/fabric/enterprise/throttling)
  — smoothing windows, bursting, and the overage escalation to interactive delay then rejection
- [Fabric trial capacity](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial)
  — F4-or-F64 trial sizing, 1 TB OneLake storage, and excluded features
- [OneLake overview](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)
  — Delta Parquet and Iceberg storage, shortcuts, and supported external sources
- [Use Iceberg tables with OneLake](https://learn.microsoft.com/en-us/fabric/onelake/onelake-iceberg-tables)
  — read-only Iceberg REST catalog, V2 only, same-region shortcuts, private links unsupported
- [Customer-managed keys for Fabric workspaces](https://learn.microsoft.com/en-us/fabric/security/workspace-customer-managed-keys)
  — F-SKU-only workspace CMK and the enumerated exclusions including the Spark compute path
- [Fabric private links overview](https://learn.microsoft.com/en-us/fabric/security/security-private-links-overview)
  — tenant-level private link, Block Public Internet Access, and the unsupported-feature casualty list
- [Fabric workspace-level private links](https://learn.microsoft.com/en-us/fabric/security/security-workspace-level-private-links-overview)
  — workspace-level private link scope and why tenant-level is not a superset
- [Fabric advanced networking admin settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-advanced-networking)
  — the tenant switches governing public access and private link enforcement
- [Fabric lineage view](https://learn.microsoft.com/en-us/fabric/governance/lineage)
  — workspace-scoped lineage, one-step-upstream external sources, no cross-workspace downstream view
- [OneLake soft delete](https://learn.microsoft.com/en-us/fabric/onelake/soft-delete)
  — the fixed 7-day non-configurable soft-delete window
- [Fabric workspace retention and item recovery](https://learn.microsoft.com/en-us/fabric/admin/retention-recovery)
  — workspace retention windows and item recovery, which is disabled by default
- [Fabric Multi-Geo support](https://learn.microsoft.com/en-us/fabric/admin/service-admin-premium-multi-geo)
  — multi-geo capacity placement, home-region metadata, and the no-region-move constraint
- [Microsoft Purview audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies)
  — the 180-day default retention for records generated on or after 2023-10-17
- [Microsoft Purview retention policies and labels](https://learn.microsoft.com/en-us/purview/retention)
  — supported locations; contains no Fabric, OneLake, Power BI, lakehouse, or warehouse entry
- [Microsoft Purview billing models](https://learn.microsoft.com/en-us/purview/purview-billing-models)
  — pay-as-you-go metering for governing Fabric assets; Unified Catalog is not bundled with Fabric
- [What's new in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/whats-new)
  — release record; the Azure Synapse what's-new URL now redirects here
- [What is Azure Synapse Analytics?](https://learn.microsoft.com/en-us/azure/synapse-analytics/overview-what-is)
  — product overview, document date 2024-07-10
- [Azure Synapse Analytics lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/azure-synapse-analytics)
  — Modern Lifecycle Policy, listed "In Support", no retirement date
- [Immutable storage for Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)
  — time-based retention, legal holds, locked policies, container- vs version-level WORM, HNS limitation
- [Microsoft Purview overview](https://learn.microsoft.com/en-us/purview/purview)
  — current solution areas including Data Map and Unified Catalog
- [Azure Databricks data security and encryption](https://learn.microsoft.com/en-us/azure/databricks/security/keys/)
  — CMK scopes and Premium tier requirement
- [Azure Databricks serverless compute plane networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/)
  — network connectivity configurations, private endpoints, service tag, 2026-06-09 migration deadline
- [Azure Databricks compliance security profile](https://learn.microsoft.com/en-us/azure/databricks/security/privacy/security-profile)
  — covered standards, 2026-09-01 HIPAA/HITRUST/IRAP requirement, identity residency caveat
- [What is Azure Databricks?](https://learn.microsoft.com/en-us/azure/databricks/introduction/)
  — current platform composition and product naming
- [Read Databricks tables from Apache Iceberg clients](https://docs.databricks.com/aws/en/external-access/iceberg)
  — Unity Catalog Iceberg REST endpoint and per-table-type read/write matrix
- [Snowflake editions](https://docs.snowflake.com/en/user-guide/intro-editions)
  — per-edition gating of Tri-Secret Secure, private connectivity, HIPAA/PCI/FedRAMP/ITAR, failover
- [Snowflake managing encryption keys](https://docs.snowflake.com/en/user-guide/security-encryption-manage)
  — Tri-Secret Secure composition, supported KMS, 10-minute key-unavailability behaviour
- [Snowflake Time Travel](https://docs.snowflake.com/en/user-guide/data-time-travel)
  — retention limits by edition, Fail-safe semantics
- [Snowflake ACCOUNT_USAGE schema](https://docs.snowflake.com/en/sql-reference/account-usage)
  — 365-day retention, ACCESS_HISTORY edition requirement
- [Snowflake Apache Iceberg tables](https://docs.snowflake.com/en/user-guide/tables-iceberg)
  — managed vs externally-managed semantics, external-engine access, unsupported features

## See Also

- `general/data-analytics.md` — analytics platform patterns and the warehouse vs lakehouse framing
- `general/open-table-formats.md` — Delta, Iceberg, and Hudi mechanics underlying the openness dimension
- `general/query-engines.md` — engine characteristics behind the workload-breadth dimension
- `general/data-modelling.md` — the modelling layer, which outlives any platform choice
- `general/data-ingestion.md` — landing data into whichever platform is selected
- `general/semantic-layer.md` — the metric layer above the platform, and where row/column security is actually enforced
- `general/business-intelligence.md` — the consumption tier, BI vendor landscape, and the Power BI licensing model that frequently drives the platform decision
- `patterns/lakehouse-medallion.md` — layered lake design on the chosen platform
- `patterns/data-warehouse-migration.md` — moving off a legacy warehouse onto the selection
- `patterns/data-pipeline.md` — the operating pattern once the platform is running
- `patterns/regulated-financial-data-platform.md` — the regulated-sector variant of this decision
- `patterns/core-banking-data-integration.md` — system-of-record integration in that sector
- `providers/azure/fabric.md` — Fabric platform detail
- `providers/databricks/data-platform.md` — Databricks platform detail
- `providers/snowflake/data-platform.md` — Snowflake platform detail
- `providers/gcp/bigquery.md` — BigQuery detail
- `providers/azure/data.md` and `providers/azure/storage.md` — Azure data services and ADLS Gen2
- `general/data-classification.md` — classification, which should precede platform selection
- `general/legal-hold.md` — legal hold mechanics behind the retention dimension
- `general/governance.md` — the governance operating model the platform must support
- `general/identity.md` — identity federation, the first estate-fit test
- `compliance/ffiec.md` — supervisory expectations relevant to the concentration dimension
- `compliance/sox.md` and `compliance/glba.md` — control and privacy obligations shaping evidence needs
- `failures/data.md` — data platform failure modes
- `failures/dependencies.md` — dependency and concentration failure modes
