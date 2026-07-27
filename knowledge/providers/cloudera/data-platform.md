# Cloudera Data Platform

## Scope

The Cloudera platform (formerly Cloudera Data Platform, CDP) as it appears on real enterprise engagements: the form factors (Cloudera on cloud, Cloudera Base on premises, Cloudera Data Services on premises), the CDH/HDP legacy merge and what it means for an estate still running either, the Cloudera Runtime component set (Hive and the Hive Metastore, Impala, Spark, HBase, Kudu, Ozone, Solr, NiFi, Oozie, YARN/HDFS), SDX and the shared Data Lake as the security and governance substrate, Apache Ranger for authorization and Apache Atlas for metadata and lineage, Knox and IDBroker for identity and cloud-credential brokering, workload isolation across Data Hub clusters and Data Warehouse virtual warehouses, the CCU-based subscription model, and the realistic exit paths off a Cloudera estate.

This file exists because a large share of what enterprises call "the data lake" is a Cloudera cluster. Any cloud data engagement in a company with a Hadoop history will encounter one, and the migration question is usually "what do we do about Cloudera" rather than "which lakehouse do we like."

Note on naming: Cloudera renamed its product line, and both sets of names are in active use. "Cloudera Base on premises" is the former CDP Private Cloud Base; "Cloudera Data Services on premises" is the former CDP Private Cloud Data Services; "Cloudera on cloud" is the former CDP Public Cloud. Customer documentation, contracts, and internal runbooks will be inconsistent about this for years.

## Checklist

### Estate Assessment: What Are You Actually Looking At

- [ ] **[Critical]** Has the estate been identified as CDH, HDP, or Cloudera Runtime 7.x, and is its support status established? CDH 5.x and the Hortonworks stacks are long past end of support (Cloudera's lifecycle page lists CDH 5.8 and earlier at August 2019, HDP 2.6.x at December 2020, HDP 3.1.x at December 2021, and Cloudera Enterprise 6.3 at March 2022). A cluster in that state is running unpatched software with no vendor path for a CVE, which is frequently the actual business driver behind the migration.
- [ ] **[Critical]** Is the current Runtime version's support horizon known and is the LTS/non-LTS distinction understood? Cloudera designates specific releases as Long Term Support -- 7.1.9 is listed through October 2028 and 7.3.2 through March 2032 -- while intermediate releases have much shorter windows. Planning a three-year migration on a non-LTS release means an unplanned in-place upgrade in the middle of it.
- [ ] **[Critical]** Has a full component inventory been taken, not just "we run Hive and Spark"? A mature cluster typically also carries Oozie workflows, Sqoop jobs, HBase tables, Kudu tables, Solr collections, NiFi flows, Phoenix, and a long tail of MapReduce and Pig jobs nobody claims. Cloudera Runtime bundles roughly fifty open-source projects; the migration effort is set by the tail, not by the headline engines.
- [ ] **[Critical]** Is the Hive Metastore treated as the estate's most important single asset? Nearly every engine in the stack -- Hive, Impala, Spark, Trino, and most external tools -- resolves table locations, schemas, partitions, and statistics through the Hive Metastore, backed by a relational database. It is simultaneously the thing everything depends on and the thing nobody has a backup or migration plan for. Establish where its backing RDBMS lives, how large it is, and how many partitions it holds before anything else.
- [ ] **[Recommended]** Is Kerberos in play, and is the KDC topology documented? Secured Cloudera clusters are Kerberized end to end, with cross-realm trust to Active Directory. Kerberos is the most common cause of "the migration tool cannot connect" and of long-tail integration failures for anything reaching into the cluster from outside.
- [ ] **[Recommended]** Has HDFS been profiled for the small-file problem? NameNode heap consumption scales with the number of files and blocks, not with data volume. A cluster with hundreds of millions of small files has a NameNode that is already the operational constraint, and it will not survive being re-created naively on object storage either -- the file count has to be addressed as part of the migration, not after it.
- [ ] **[Optional]** Is data actually growing, or is the cluster mostly cold? Many Cloudera estates have a small hot working set and a very large cold archive that nobody queries. Splitting those two before migrating is often the largest single cost reduction available.

### Platform Architecture and Form Factor

- [ ] **[Critical]** Is the target form factor decided explicitly -- Cloudera on cloud, Cloudera Base on premises, Cloudera Data Services on premises, or exit from Cloudera entirely? These are genuinely different products with different operational models, and "upgrade to CDP" is often chosen by default when the real question is whether Cloudera should remain in the architecture at all.
- [ ] **[Critical]** In Cloudera on cloud, is the Environment/Data Lake/Data Hub model understood? An Environment is a logical subset of the cloud account including a specific virtual network. Registering an Environment automatically deploys a Data Lake, which Cloudera describes as "a service for creating a protective ring of security and governance around your data" and which runs the shared Hive Metastore, Ranger, Atlas, and Knox. Workload clusters (Data Hubs) and data services attach to that Data Lake and inherit its security and governance.
- [ ] **[Critical]** Is the Data Lake sized appropriately at creation? The Data Lake is the single point of failure for security and governance across every attached workload, and it is deployed at a chosen scale (light duty by default in some flows). Under-sizing it produces Ranger and Hive Metastore contention that presents as unrelated workload slowness across every cluster in the Environment.
- [ ] **[Critical]** Is data kept in cloud object storage rather than in cluster-local HDFS in cloud deployments? The entire value of the cloud form factor is that compute clusters are ephemeral and disposable while data persists in S3 or ADLS. A cloud deployment that recreates long-lived HDFS on attached disks has bought the operational cost of Hadoop without the elasticity benefit.
- [ ] **[Recommended]** For Cloudera Data Services on premises, is the Kubernetes substrate decision made deliberately? Data Services on premises runs on top of Cloudera Base on premises and is delivered on Kubernetes -- either an existing Red Hat OpenShift estate or Cloudera's embedded container platform. Choosing the embedded option to avoid an OpenShift dependency trades that dependency for a Cloudera-managed Kubernetes that your platform team does not otherwise operate.
- [ ] **[Recommended]** Is Apache Ozone evaluated where HDFS scale is the binding constraint on premises? Ozone is Cloudera's answer to the HDFS small-file and NameNode-scale problem: it is designed to store over 100 billion objects in a single cluster, supports DataNode storage density up to 400 TB against roughly 100 TB for HDFS DataNodes, and exposes both an S3-compatible API and a Hadoop-compatible filesystem interface. That last property is what makes it a viable in-place replacement for HDFS under existing Hive and Spark jobs.
- [ ] **[Optional]** Is Replication Manager in scope for on-premises-to-cloud data movement or DR between Cloudera environments? It handles HDFS, Hive, and HBase replication between Cloudera clusters and is usually simpler than hand-built DistCp pipelines for the same job.

### Components and Workload Placement

- [ ] **[Critical]** Is each SQL workload placed on the right engine rather than defaulting to whichever the team knows? Impala is a low-latency MPP engine for interactive BI; Hive on Tez is the batch ETL engine and tolerates long-running, high-volume transformations; Spark SQL is the right home for anything mixing SQL with procedural code or ML. Running interactive dashboards on Hive and nightly ETL on Impala is a common and expensive inversion.
- [ ] **[Critical]** Are Hive ACID (transactional) tables identified early? Hive ACID tables are ORC-backed, require compaction to stay performant, and are the single most common blocker when moving Hive data to another engine or table format -- most external readers cannot interpret the delta directories correctly. Inventory them before promising a migration date.
- [ ] **[Critical]** Is HBase versus Kudu versus a relational store settled on access pattern rather than habit? HBase is for high-volume random read/write on very wide sparse rows with no analytic scan requirement; Kudu is for workloads that need both fast random updates and fast columnar scans, which HBase and HDFS each do badly. Kudu is the harder of the two to migrate away from because there is no direct managed equivalent in the major clouds -- workloads generally split into an operational store plus a lakehouse table.
- [ ] **[Recommended]** Are Oozie workflows inventoried as a distinct migration workstream? Oozie XML workflow and coordinator definitions encode scheduling, dependencies, retries, and often business logic. There is no automated Oozie-to-Airflow converter that produces production-quality output; this is manual rewrite work and it is routinely underestimated.
- [ ] **[Recommended]** Is Cloudera Data Warehouse evaluated for the BI tier where the estate is staying on Cloudera? CDW provides independent, self-service virtual warehouses that autoscale up and down and give each consumer group isolated compute against shared data and shared metadata -- which is the cleanest available answer to noisy-neighbour contention inside a single cluster.
- [ ] **[Optional]** Is Apache Iceberg support in current Runtime versions considered for tables that will eventually leave Cloudera? Writing new tables in an open, engine-portable table format rather than Hive-managed ORC materially reduces later migration cost, whether or not the estate ever leaves. Confirm the supported Iceberg version and the engine-by-engine feature coverage in the Runtime release notes for the specific version deployed.

### SDX: Security, Governance, and Metadata

- [ ] **[Critical]** Is Apache Ranger the single authorization point, with no direct filesystem or object-storage bypass path? Ranger enforces resource-based and tag-based policies per service (Hive, Impala, HBase, Kafka, HDFS, Ozone, Solr) and produces the audit trail. If users can reach the underlying storage directly with their own cloud credentials, Ranger policies are advisory rather than enforced, and the audit record is incomplete.
- [ ] **[Critical]** Is Apache Atlas actually populated and maintained, not just installed? Atlas holds the technical metadata, classifications, and lineage. Tag-based Ranger policies consume Atlas classifications, so an unmaintained Atlas silently degrades the authorization model from "policies follow the data" to "policies follow the path."
- [ ] **[Critical]** Is IDBroker configured with correct group-to-cloud-role mappings in cloud deployments? IDBroker is a REST API built as part of Apache Knox's authentication services; it exchanges a Cloudera credential or token for cloud vendor access tokens based on mappings between Cloudera users and groups and native cloud roles (on AWS, IAM roles). When a Hadoop connector such as `s3a` reads data, it obtains short-lived credentials through IDBroker. Over-broad mappings here are the fastest route to a data-perimeter failure, because they hand real cloud credentials to workload processes.
- [ ] **[Critical]** Is authorization for cloud object storage fine-grained or role-coarse, and is that a conscious choice? IDBroker mapping alone grants access at the granularity of the cloud IAM role. Cloudera's Ranger Authorization Service (RAZ) exists to push fine-grained, Ranger-managed authorization down to object-storage paths. Confirm RAZ availability, prerequisites, and limitations against current documentation for the specific cloud provider before designing around it -- support and constraints have varied by provider and release.
- [ ] **[Recommended]** Is Knox the only external entry point to cluster UIs and APIs? Knox is the perimeter gateway; leaving service web UIs directly reachable on cluster nodes defeats it and is a recurring audit finding.
- [ ] **[Recommended]** Is HDFS/Ozone encryption at rest configured with Ranger KMS, and is the key custody model documented? Transparent encryption zones plus a KMS is the standard pattern; the operational risk is key material custody and the recovery story, not the encryption itself.
- [ ] **[Recommended]** Are Ranger policies exported and version-controlled? They are the security posture of the estate, they drift constantly, and they are the artifact most often lost in a migration -- because nobody realises that a Ranger policy set is not represented anywhere in the target's IAM model.
- [ ] **[Optional]** For estates upgrading from CDH, has the Sentry-to-Ranger and Navigator-to-Atlas conversion been scoped as a separate workstream? The CDH lineage used Sentry for authorization and Navigator for governance; the Hortonworks lineage used Ranger and Atlas; the merged platform standardized on Ranger and Atlas. Conversion tooling exists in the upgrade path, but the resulting policy set needs review rather than acceptance, because the two models are not semantically identical.

### Workload Isolation and Capacity

- [ ] **[Critical]** Is there real workload isolation between competing tenants, or one shared YARN queue and one Impala pool? On a monolithic cluster, isolation comes from the YARN capacity scheduler queues and Impala admission control, and both need deliberate configuration with per-queue memory and concurrency limits. Without them, a single analyst query can starve the nightly ETL, and the platform team learns about it from the business.
- [ ] **[Critical]** In cloud and Data Services deployments, is the cluster-per-workload model used rather than one large shared cluster? Separate Data Hub clusters or separate CDW virtual warehouses against the same Data Lake give physical compute isolation with shared data and shared governance. This is the single largest operational improvement the cloud form factor offers over classic Hadoop, and it is routinely not taken up because the migration was done as a lift.
- [ ] **[Recommended]** Is autoscaling configured with sensible floors and ceilings, and is auto-suspend enabled on interactive warehouses? An always-on virtual warehouse sized for peak is the cloud equivalent of a permanently over-provisioned cluster and produces the same bill without the same excuse.
- [ ] **[Recommended]** Is JVM and heap configuration reviewed for the services that actually matter -- NameNode, Hive Metastore, HBase RegionServers, Impala coordinators? Cloudera clusters accumulate years of ad-hoc heap tuning; the settings that were right at 200 nodes are frequently wrong now.
- [ ] **[Optional]** Are Impala metadata operations (catalog and `INVALIDATE METADATA`) understood as a scaling limit? On estates with very large numbers of tables and partitions, Impala catalog propagation becomes the bottleneck long before query execution does.

### Commercial Model

- [ ] **[Critical]** Is the licensing unit understood before capacity is planned? Cloudera prices per Cloudera Compute Unit (CCU), which the vendor defines as a combination of core and memory. Cloud data services are billed hourly per CCU at published rates -- as read from Cloudera's pricing page on 26 July 2026, Data Hub $0.04/CCU, Data Warehouse $0.07/CCU, Data Engineering $0.07/CCU (core) or $0.20/CCU (all-purpose), Operational Database $0.08/CCU, Machine Learning $0.20/CCU, DataFlow deployments $0.30/CCU. On-premises offerings are annual subscriptions quoted by sales rather than list-priced. Verify current rates directly; they change.
- [ ] **[Critical]** Is the CCU subscription cost separated from the infrastructure cost in every business case? In cloud deployments you pay Cloudera per CCU-hour *and* the cloud provider for the underlying instances and storage. A business case built on cloud instance pricing alone understates the true cost, in the same way that a Databricks estimate that omits DBUs does.
- [ ] **[Recommended]** Is there any free or community edition assumption in the plan? There is no free production edition; the old free CDH express path no longer exists. Proof-of-concept work needs a commercial arrangement or a trial.
- [ ] **[Recommended]** Are the add-on line items accounted for -- Observability, Data Visualization per user, GPU units for AI workloads? These are separately priced and are routinely discovered after the budget is approved.
- [ ] **[Optional]** Is the renewal date the actual constraint on the migration timeline? On most Cloudera exit programmes, the subscription renewal is the deadline that matters, and the licence saving is the funding source. Sequence the migration so decommissioning lands before renewal, not after -- see the decommissioning discipline in `patterns/data-warehouse-migration.md`.

### Exit Paths

- [ ] **[Critical]** Is the exit target chosen per workload class rather than as a single platform decision? A Cloudera estate is not one workload. In practice, SQL analytics goes to a cloud warehouse or lakehouse, Spark ETL goes to Databricks, EMR, Dataproc, or a serverless Spark service, HBase goes to a managed NoSQL store, Kudu workloads split into an operational store plus lakehouse tables, Solr goes to a managed search service, and NiFi either lifts to a managed NiFi offering or is rewritten. Forcing all of these onto one target is what makes Cloudera exits fail.
- [ ] **[Critical]** Is the Hive Metastore migration explicitly planned, including partition-level metadata and statistics? Table definitions, storage locations, partition lists, and statistics all live there. A migration that recreates DDL by hand loses partition metadata and statistics, and the target's optimizer then behaves nothing like the source's.
- [ ] **[Critical]** Is Ranger policy translation planned into the target's authorization model? Ranger policies do not map one-to-one onto cloud IAM, Unity Catalog grants, or warehouse RBAC. This is analysis work with a real risk of over-granting during translation, and it should be reviewed by whoever owns the access model, not by the migration engineers.
- [ ] **[Recommended]** Are jobs profiled for actual runtime and cost before they are ported? A large fraction of jobs on a mature Cloudera cluster produce output nobody consumes. Porting them faithfully is the most expensive way to discover that.
- [ ] **[Recommended]** Is the difference between HDFS semantics and object-storage semantics accounted for in job rewrites? Rename is not atomic and directory listing is not free on object storage; jobs that relied on HDFS rename-based commit protocols or that list large directories per task will behave differently and sometimes incorrectly.
- [ ] **[Optional]** Is a hybrid end state acceptable -- Cloudera retained for a specific regulated or latency-bound workload while everything else moves? This is a legitimate outcome and is often cheaper than forcing a complete exit, but it needs an explicit owner and a support plan, or it becomes an orphaned cluster.

## Why This Matters

A great many enterprise "data lakes" are Cloudera clusters, and the platform is old enough that most of them are now a liability rather than an asset. The typical estate is on an unsupported or nearly unsupported release, has accumulated a decade of jobs whose owners have left, is Kerberized in a way nobody fully understands, and has a Hive Metastore that every downstream tool depends on and nobody backs up. The cost of that estate is not just the subscription -- it is a specialist platform team, a hardware refresh cycle, and an inability to adopt anything new without a compatibility argument.

The Cloudera-Hortonworks merger left a specific structural legacy that still matters. The two stacks brought overlapping and incompatible components -- Sentry and Navigator from one lineage, Ranger and Atlas from the other, Impala from one and Hive on Tez from the other -- and the merged platform standardized on a single set. This means an in-place CDH-to-current upgrade is not a version bump; it is a security-model migration with a governance-model migration attached, and it is routinely scoped as if it were routine patching.

The Hive Metastore is the piece that determines how hard the exit is. It is the metadata substrate the entire ecosystem resolves against, and its contents -- schemas, partition lists, storage locations, statistics -- represent years of accumulated state that cannot be reconstructed from the data files alone. Teams that treat metastore migration as an afterthought discover that their target platform's optimizer has no statistics, that partition discovery on a table with a hundred thousand partitions takes hours, and that a meaningful fraction of table definitions point at paths that no longer exist.

Authorization is the second determinant. Ranger's policy model -- per-service, resource-based and tag-based, with Atlas classifications feeding the tag policies -- has no equivalent in cloud IAM. Translating it is genuine analysis, and the failure mode is silent: the migration succeeds, everything works, and access is broader than it was before because the translation defaulted to permissive to avoid breaking jobs. Nobody notices until an audit.

Finally, the cloud form factor's real benefit is workload isolation, and it is the benefit most often left on the table. Classic Hadoop forces every tenant onto one cluster with one scheduler; the whole point of the Environment plus Data Lake plus per-workload compute model is that compute becomes disposable while security, governance, and metadata stay shared. A migration executed as a lift -- one big long-lived cluster in a cloud account -- pays the cloud's cost structure while keeping Hadoop's operational model, which is the worst of both.

## Common Decisions (ADR Triggers)

- **Modernize on Cloudera vs exit the platform** -- upgrade to current Cloudera Runtime and adopt the Data Lake plus per-workload compute model (preserves existing skills, jobs, Ranger policies, and metastore; keeps the CCU subscription) vs migrate workloads to cloud-native services and decommission (removes the subscription and the platform team, but requires rewriting Oozie, Ranger, and HBase/Kudu workloads)
- **Form factor** -- Cloudera on cloud (elastic, cloud-provider-native storage, Cloudera-managed control plane in your cloud account) vs Cloudera Base on premises (classic cluster, full control, hardware refresh cycle) vs Cloudera Data Services on premises (cloud-like separation of compute and storage without leaving the datacentre, at the cost of running Kubernetes)
- **Kubernetes substrate for Data Services on premises** -- existing Red Hat OpenShift (reuses an operated platform, adds an OpenShift licence and dependency) vs Cloudera's embedded container platform (no OpenShift dependency, but a Kubernetes your team does not otherwise run)
- **HDFS vs Ozone vs cloud object storage** -- keep HDFS where the cluster is small and stable vs adopt Ozone where NameNode scale or small-file count is the binding constraint on premises vs move to S3/ADLS in cloud deployments, accepting the object-storage semantics change in job commit protocols
- **Authorization granularity for cloud storage** -- IDBroker group-to-IAM-role mapping alone (simple, coarse, the role is the access boundary) vs adding RAZ for fine-grained Ranger-managed path authorization (consistent with the on-premises model, additional components and provider-specific constraints)
- **SQL engine placement** -- Impala for interactive BI vs Hive on Tez for batch ETL vs Spark SQL for mixed procedural and analytic work; this decision is per workload, not per platform
- **Shared cluster vs cluster-per-workload** -- one large cluster with YARN queues and Impala admission control (higher utilization, real contention risk, cheaper licence footprint) vs separate Data Hubs or virtual warehouses per tenant (true isolation, independent scaling and cost attribution, more surfaces to operate)
- **Table format for new tables** -- Hive-managed ORC/Parquet (native, simplest inside Cloudera) vs an open engine-portable table format (materially lower future migration cost, engine feature coverage varies by Runtime version)
- **Exit target per workload class** -- SQL analytics to a cloud warehouse or lakehouse, Spark to a managed Spark service, HBase to a managed NoSQL store, Kudu split into an operational store plus lakehouse tables, Oozie to a modern orchestrator; forcing a single target across all classes is the common failure mode
- **Sequencing against the subscription renewal** -- decommission before renewal so the licence saving funds the programme vs accept one more renewal cycle to de-risk the cutover; this is a commercial decision that should be made explicitly, not discovered

## Reference Architectures

### Cloudera on cloud, per-workload isolation

- One Environment per major boundary (production, non-production, and any region or sovereignty boundary), each mapped to a specific virtual network in the cloud account
- Data Lake deployed at a scale matched to the number of attached workloads, running the shared Hive Metastore, Ranger, Atlas, and Knox; sized above light duty for anything with several concurrent workload clusters
- Data persisted in S3 or ADLS, never in long-lived cluster HDFS; workload clusters are disposable
- Data Hub clusters created per workload class -- one for streaming ingestion, one for batch ETL, one for data science -- each attached to the same Data Lake and therefore sharing policy and lineage
- Cloudera Data Warehouse virtual warehouses per consumer group for BI, with auto-suspend so idle groups cost nothing
- IDBroker mappings scoped per group to narrowly-permissioned cloud roles; Ranger policies exported to version control on a schedule

### On-premises modernization without leaving the datacentre

- Cloudera Base on premises as the storage and core-service layer, with Ozone adopted where HDFS NameNode scale or small-file count is the constraint
- Cloudera Data Services on premises layered on top, running on Kubernetes, providing Data Warehouse, Data Engineering (Spark with Airflow orchestration), and AI workloads as separately-scaled services
- Shared metadata and policy through the same Hive Metastore, Ranger, and Atlas that the base cluster uses -- so the compute separation does not fragment governance
- Replication Manager configured for DR replication of HDFS, Hive, and HBase to a second site

### Staged exit to a cloud lakehouse

- Phase 0: inventory. Component census, Hive Metastore statistics (table count, partition count, backing RDBMS size), Ranger policy export, Oozie workflow census, and a job-level usage profile to identify what is genuinely consumed
- Phase 1: land the data. Bulk copy from HDFS to cloud object storage, converting Hive-managed tables into an open table format at the same time; keep the Cloudera cluster authoritative and read-only-replicating
- Phase 2: metadata. Migrate Hive Metastore contents into the target catalog, including partitions and statistics; translate Ranger policies into the target's grant model and have the access owner review the result rather than the migration team
- Phase 3: workloads, by class. Spark jobs first (highest portability), then Hive/Impala SQL, then Oozie orchestration rewritten into the target orchestrator, then HBase/Kudu/Solr as separate projects
- Phase 4: dual-run and reconciliation. Both platforms produce the same outputs; reconcile row counts, checksums, and business metrics until parity holds across a full reporting cycle -- see `patterns/data-warehouse-migration.md`
- Phase 5: decommission, timed so the cluster is retired and the subscription is not renewed

## Reference Links

- [Cloudera Documentation](https://docs.cloudera.com/) -- entry point for all current product documentation
- [Cloudera Support Lifecycle Policy](https://www.cloudera.com/services-and-support/support-lifecycle-policy.html) -- end-of-support dates for CDH, HDP, and each Cloudera Runtime release, including LTS designations
- [Cloudera Platform Pricing](https://www.cloudera.com/products/pricing.html) -- the CCU definition and published hourly rates for cloud data services
- [Cloudera on cloud overview](https://docs.cloudera.com/cdp-public-cloud/cloud/overview/topics/cdp-public-cloud.html) -- the platform overview and SDX positioning
- [Cloudera on cloud core concepts](https://docs.cloudera.com/management-console/cloud/overview/topics/mc-core-concepts.html) -- Environment, Data Lake, and the services the Data Lake runs
- [Cloudera Base on premises documentation](https://docs.cloudera.com/cdp-private-cloud-base/7.3.2/index.html) -- the on-premises cluster product (formerly CDP Private Cloud Base)
- [Cloudera Data Services on premises overview](https://docs.cloudera.com/cdp-private-cloud-data-services/1.5.4/overview/topics/cdppvc-data-services-overview.html) -- how Data Services layers on Base, and the included services
- [Cloudera platform release summaries](https://docs.cloudera.com/cdp-private-cloud/latest/release-summaries/index.html) -- release contents and version mapping
- [Cloudera Runtime documentation](https://docs.cloudera.com/runtime/7.3.1/index.html) -- the open-source component distribution; check the release notes here for exact component versions and Iceberg coverage
- [Cloudera Data Warehouse](https://docs.cloudera.com/data-warehouse/cloud/index.html) -- virtual warehouses, autoscaling, and the Hive/Impala/Trino query engines
- [Cloudera Data Engineering](https://docs.cloudera.com/data-engineering/cloud/index.html) -- managed Spark with Airflow orchestration
- [Cloudera Machine Learning / AI](https://docs.cloudera.com/machine-learning/cloud/index.html) -- the data science and ML service
- [Cloudera Replication Manager](https://docs.cloudera.com/replication-manager/cloud/index.html) -- HDFS, Hive, and HBase replication between Cloudera clusters
- [Cloudera upgrade and migration documentation](https://docs.cloudera.com/cdp-private-cloud-upgrade/latest/index.html) -- CDH and HDP upgrade paths, including Sentry-to-Ranger and Navigator-to-Atlas conversion
- [Identity federation in Cloudera on cloud](https://docs.cloudera.com/cdp-public-cloud/cloud/security-overview/topics/security_how_identity_federation_works_in_cdp.html) -- IDBroker and user/group to cloud IAM role mapping
- [Apache Ozone in Cloudera](https://docs.cloudera.com/cdp-private-cloud-base/7.3.1/ozone-overview/topics/ozone-introduction.html) -- scale targets, DataNode density, volumes/buckets/keys
- [Apache Ozone](https://ozone.apache.org/) -- upstream project: S3 protocol support and Hadoop filesystem interfaces
- [Apache Ranger](https://ranger.apache.org/) -- the authorization and audit framework used across the stack
- [Apache Atlas](https://atlas.apache.org/) -- metadata, classification, and lineage; the source of tag-based Ranger policies
- [Apache Knox](https://knox.apache.org/) -- perimeter gateway and the basis of IDBroker
- [Apache Hive](https://hive.apache.org/) -- Hive engine and the Hive Metastore
- [Hive Metastore administration](https://cwiki.apache.org/confluence/display/Hive/AdminManual+Metastore+Administration) -- metastore configuration and the backing relational database
- [Apache Impala](https://impala.apache.org/) -- the MPP interactive SQL engine
- [Apache Kudu](https://kudu.apache.org/) -- columnar storage supporting fast random updates and fast scans

---

## See Also

- `patterns/data-warehouse-migration.md` -- the migration pattern this platform is most often the source of, including dual-run reconciliation and decommissioning discipline
- `providers/teradata/data-warehouse.md` -- the other dominant legacy source in the same engagements; frequently coexists with a Cloudera estate
- `providers/databricks/data-platform.md` -- the most common Spark-workload exit target; Unity Catalog is the destination for Hive Metastore contents
- `providers/aws/redshift.md` -- common SQL-analytics exit target on AWS
- `providers/snowflake/data-platform.md` -- common SQL-analytics exit target where multi-cloud is a requirement
- `general/data-analytics.md` -- warehouse vs lake vs lakehouse framing and the governance-platform decision
- `general/data-migration-tools.md` -- bulk data movement tooling for the storage-layer phase of a Cloudera exit
- `patterns/data-pipeline.md` -- target-side pipeline architecture for rewritten Oozie and Spark workloads
- `providers/openshift/infrastructure.md` -- OpenShift as the substrate for Cloudera Data Services on premises
- `general/security.md` -- authorization and audit patterns that Ranger policy translation has to land in
- `general/cost-onprem.md` -- total cost framing for an on-premises cluster including hardware refresh and platform staffing
