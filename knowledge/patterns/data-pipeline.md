# Data Pipeline Architecture

## Scope

Covers batch, streaming, and hybrid data pipeline architectures including ingestion, transformation (ETL/ELT), orchestration, data quality validation, and storage tiering. Applicable when workloads involve moving data from sources to analytics platforms, data warehouses, or data lakes.

## Overview

Data pipelines ingest, transform, and store data for analytics, reporting, or downstream consumption. They can be batch, streaming, or hybrid.

## Checklist

- [ ] **[Critical]** Is the pipeline batch, streaming, or hybrid?
- [ ] **[Critical]** What is the data ingestion source? (APIs, databases, files, IoT devices, message queues)
- [ ] **[Critical]** What is the expected data volume? (GB/day, events/second)
- [ ] **[Critical]** What is the latency requirement? (real-time, near-real-time, daily batch)
- [ ] **[Recommended]** What transformation logic is needed? (ETL vs ELT)
- [ ] **[Critical]** What is the target data store? (data warehouse, data lake, operational database)
- [ ] **[Recommended]** Is schema evolution supported? (backward/forward compatible changes)
- [ ] **[Critical]** How is data quality validated? (schema validation, null checks, range checks)
- [ ] **[Critical]** Is exactly-once processing required or is at-least-once acceptable?
- [ ] **[Critical]** How are failed records handled? (dead letter queue, retry, manual review)
- [ ] **[Recommended]** Is data partitioning strategy defined? (by date, by tenant, by region)
- [ ] **[Recommended]** What is the data retention policy? (hot, warm, cold, archive tiers)
- [ ] **[Critical]** Is the pipeline idempotent? (safe to re-run without duplicates)
- [ ] **[Recommended]** How is pipeline orchestration managed? (Airflow, Step Functions, Dagster)
- [ ] **[Optional]** Are data lineage and audit trails maintained?

## Why This Matters

Data pipelines are the backbone of analytics, reporting, and downstream data consumption. Without dead letter queues, failed records are silently lost. Missing idempotency means re-runs create duplicates. Monolithic pipelines create single points of failure where one bad record blocks everything. No data validation leads to garbage-in, garbage-out that corrupts downstream analysis. Missing backpressure handling allows producers to overwhelm consumers. Without monitoring on pipeline lag, data freshness degrades silently until stakeholders notice stale dashboards.

## Common Decisions (ADR Triggers)

- **Batch vs streaming vs hybrid** — latency requirements, data volume, processing complexity
- **Ingestion platform** — Kafka vs Kinesis vs Pub/Sub vs Event Hubs, ordering and retention requirements
- **ETL vs ELT** — transform before loading vs transform in the warehouse, tool selection
- **Orchestration tool** — Airflow vs Step Functions vs Dagster vs Prefect, managed vs self-hosted
- **Data warehouse selection** — Redshift vs BigQuery vs Synapse vs Snowflake, pricing model and query patterns
- **Data quality framework** — Great Expectations vs Glue Data Quality vs Dataplex, validation scope and alerting
- **Schema evolution strategy** — backward/forward compatibility, schema registry, format selection (Avro, Parquet, JSON)
- **Data retention and tiering** — hot/warm/cold lifecycle, archive policy, cost optimization

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates based on AWS us-east-1 pricing as of early 2025. Actual costs vary by region, reserved instance commitments, and usage patterns. Prices change over time — always verify with the provider's pricing calculator.

### Small (10 GB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Kinesis Data Streams (1 shard) or S3 PUT | $15 |
| Compute | Lambda (10M invocations, 256 MB) or Glue (2 DPU, 1 hr/day) | $45 |
| Storage | S3 (300 GB cumulative, Standard) | $7 |
| Data Warehouse | Redshift Serverless (8 RPU base, light queries) | $90 |
| Orchestration | Step Functions (10K state transitions/day) | $8 |
| Monitoring | CloudWatch + SNS alerts | $15 |
| **Total** | | **~$180/mo** |

### Medium (1 TB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Kinesis Data Streams (10 shards) or MSK (3-broker kafka.m5.large) | $350 |
| Compute | EMR (4x m5.xlarge, 8 hr/day) or Glue (20 DPU, 4 hr/day) | $1,200 |
| Storage | S3 (30 TB cumulative, tiered: Standard + IA) | $500 |
| Data Warehouse | Redshift (2x ra3.xlplus reserved) or Athena ($5/TB scanned) | $650 |
| Orchestration | Airflow on MWAA (mw1.medium) | $370 |
| Data Quality | Glue Data Quality or Great Expectations (self-hosted) | $50 |
| Monitoring | CloudWatch + OpenSearch (1 node for pipeline logs) | $200 |
| **Total** | | **~$3,320/mo** |

### Large (10 TB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | MSK (6-broker kafka.m5.4xlarge) | $4,500 |
| Compute | EMR (20x r5.2xlarge, 12 hr/day) or Spark on EKS | $8,000 |
| Storage | S3 (300 TB cumulative, tiered: Standard + IA + Glacier) | $3,500 |
| Data Warehouse | Redshift (4x ra3.4xlarge reserved) | $5,500 |
| Data Lake Query | Athena (heavy ad-hoc, 50 TB scanned/mo) | $250 |
| Orchestration | Airflow on MWAA (mw1.xlarge) or self-hosted on EKS | $800 |
| Data Quality | Glue Data Quality + custom validation jobs | $300 |
| Monitoring | CloudWatch + OpenSearch (3-node cluster) + Grafana | $600 |
| Data Transfer | Cross-AZ and cross-region replication | $500 |
| **Total** | | **~$23,950/mo** |

### Azure Estimates

> **Disclaimer:** Azure prices are approximate, based on East US region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the Azure Pricing Calculator.

#### Small (10 GB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Event Hubs (1 TU, Basic) or ADLS PUT | $15 |
| Compute | Azure Data Factory (10 pipeline runs/day, light activities) | $40 |
| Storage | ADLS Gen2 (300 GB cumulative, Hot tier) | $7 |
| Data Warehouse | Synapse Serverless (light queries, 500 GB scanned/mo) | $3 |
| Orchestration | Data Factory orchestration (included) | $0 |
| Monitoring | Azure Monitor + alerts | $15 |
| **Total** | | **~$80/mo** |

#### Medium (1 TB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Event Hubs (10 TUs, Standard) | $400 |
| Compute | Synapse Spark Pool (4x Medium nodes, 8 hr/day) or Data Factory Data Flows | $1,100 |
| Storage | ADLS Gen2 (30 TB cumulative, tiered: Hot + Cool) | $450 |
| Data Warehouse | Synapse Dedicated Pool (DW200c reserved) | $700 |
| Orchestration | Data Factory (orchestration + monitoring) | $100 |
| Data Quality | Data Factory data flows for validation | $50 |
| Monitoring | Azure Monitor + Log Analytics | $180 |
| **Total** | | **~$2,980/mo** |

#### Large (10 TB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Event Hubs (Dedicated 1 CU) | $4,200 |
| Compute | Synapse Spark Pool (20x Large nodes, 12 hr/day) or HDInsight | $7,500 |
| Storage | ADLS Gen2 (300 TB cumulative, tiered: Hot + Cool + Archive) | $3,200 |
| Data Warehouse | Synapse Dedicated Pool (DW1000c reserved) | $5,800 |
| Data Lake Query | Synapse Serverless (ad-hoc, 50 TB scanned/mo) | $250 |
| Orchestration | Data Factory (complex pipelines + monitoring) | $400 |
| Data Quality | Data Factory data flows + custom validation | $300 |
| Monitoring | Azure Monitor + Log Analytics + Grafana | $550 |
| Data Transfer | Cross-region replication | $450 |
| **Total** | | **~$22,650/mo** |

### GCP Estimates

> **Disclaimer:** GCP prices are approximate, based on us-central1 region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the GCP Pricing Calculator.

#### Small (10 GB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Pub/Sub (10 GB/day) or GCS upload | $5 |
| Compute | Dataflow (1 worker, 1 hr/day) or Cloud Functions | $35 |
| Storage | GCS (300 GB cumulative, Standard) | $6 |
| Data Warehouse | BigQuery (on-demand, 500 GB scanned/mo) | $3 |
| Orchestration | Cloud Composer (small, or Cloud Workflows) | $0 |
| Monitoring | Cloud Monitoring basic | $10 |
| **Total** | | **~$59/mo** |

#### Medium (1 TB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Pub/Sub (1 TB/day) | $300 |
| Compute | Dataflow (4x n2-standard-4 workers, 8 hr/day) | $1,000 |
| Storage | GCS (30 TB cumulative, tiered: Standard + Nearline) | $400 |
| Data Warehouse | BigQuery (flat-rate 100 slots reserved) | $500 |
| Orchestration | Cloud Composer (medium environment) | $350 |
| Data Quality | Dataplex data quality tasks | $50 |
| Monitoring | Cloud Monitoring + Cloud Logging | $150 |
| **Total** | | **~$2,750/mo** |

#### Large (10 TB/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Ingestion | Pub/Sub (10 TB/day) + Dataflow streaming ingest | $3,800 |
| Compute | Dataflow (20x n2-highmem-8 workers, 12 hr/day) or Dataproc | $7,000 |
| Storage | GCS (300 TB cumulative, tiered: Standard + Nearline + Coldline) | $3,000 |
| Data Warehouse | BigQuery (flat-rate 500 slots reserved) | $4,800 |
| Data Lake Query | BigQuery (ad-hoc on-demand, 50 TB scanned/mo) | $250 |
| Orchestration | Cloud Composer (large environment) or self-hosted Airflow on GKE | $700 |
| Data Quality | Dataplex data quality + custom validation | $250 |
| Monitoring | Cloud Monitoring + Cloud Logging + Grafana | $500 |
| Data Transfer | Cross-region replication | $400 |
| **Total** | | **~$20,700/mo** |

### Provider Comparison

> **Disclaimer:** All prices are approximate monthly estimates as of early 2025. Actual costs vary significantly based on region, commitment discounts, negotiated contracts, and usage patterns. Always verify with each provider's pricing calculator.

| Scale | AWS | Azure | GCP |
|-------|-----|-------|-----|
| Small (10 GB/day) | ~$180/mo | ~$80/mo | ~$59/mo |
| Medium (1 TB/day) | ~$3,320/mo | ~$2,980/mo | ~$2,750/mo |
| Large (10 TB/day) | ~$23,950/mo | ~$22,650/mo | ~$20,700/mo |

**Notes:**
- GCP BigQuery's separation of storage and compute, plus on-demand pricing ($5/TB scanned), makes it very cost-effective for variable query workloads.
- Azure Synapse Serverless is excellent for small/medium pipelines with infrequent queries, keeping costs very low at small scale.
- GCP Pub/Sub is generally cheaper than Kinesis or Event Hubs for message-based ingestion at moderate volumes.
- All three providers' costs are dominated by compute (ETL) and storage accumulation at scale.

### Biggest Cost Drivers

1. **Compute (ETL/ELT)** — Spark/EMR cluster hours dominate at medium and large scale. Typically 35-45% of total cost.
2. **Streaming ingestion** — Kafka (MSK) broker costs are significant. Kinesis charges per shard-hour and per GB.
3. **Storage accumulation** — data lakes grow indefinitely without lifecycle policies. S3 costs compound monthly.
4. **Data warehouse** — Redshift provisioned clusters run 24/7. Serverless is cheaper for intermittent queries.

### Optimization Tips

- Use **S3 lifecycle policies** aggressively — move data to IA after 30 days, Glacier after 90 days.
- Use **Spot Instances** for EMR task nodes (60-80% savings for batch workloads).
- Choose **Athena** over always-on Redshift for ad-hoc or infrequent queries ($5/TB scanned).
- Use **Glue** for simple ETL jobs instead of provisioning full EMR clusters.
- Partition data by date/region in S3 — reduces Athena scan costs and improves query speed.
- Use **Amazon Data Firehose** for simple ingestion to S3 (no shard management, pay per GB).
- Consider **columnar formats** (Parquet, ORC) — 3-5x compression reduces storage and query costs.

## Key Patterns

- **Lambda Architecture**: batch + speed layers
- **Kappa Architecture**: streaming-only with replay capability
- **Change Data Capture (CDC)**: stream database changes
- **Dead Letter Queue**: isolate failed records for investigation
- **Backpressure**: consumer signals producer to slow down

## Reference Links

- [Apache Kafka](https://kafka.apache.org/) -- Distributed event streaming platform for high-throughput data ingestion and pub/sub messaging
- [Apache Spark](https://spark.apache.org/) -- Unified analytics engine for large-scale batch and streaming data processing
- [Apache Airflow](https://airflow.apache.org/) -- Workflow orchestration platform for authoring, scheduling, and monitoring data pipelines
- [dbt](https://www.getdbt.com/) -- Data transformation tool for analytics engineering using SQL-based ELT workflows
- [Apache Flink](https://flink.apache.org/) -- Stream processing framework for stateful computations over data streams
- [Debezium](https://debezium.io/) -- Change data capture platform for streaming database changes into event logs

## See Also

- `patterns/event-driven.md` — Event-driven architecture patterns including streaming and messaging
- `general/data.md` — Data architecture, storage patterns, and data management
- `patterns/ai-ml-infrastructure.md` — ML training pipelines that consume data pipeline output
- `general/observability.md` — Monitoring pipeline health, lag, and data freshness
