# Data Pipeline Architecture

## Overview

Data pipelines ingest, transform, and store data for analytics, reporting, or downstream consumption. They can be batch, streaming, or hybrid.

## Checklist

- [ ] Is the pipeline batch, streaming, or hybrid?
- [ ] What is the data ingestion source? (APIs, databases, files, IoT devices, message queues)
- [ ] What is the expected data volume? (GB/day, events/second)
- [ ] What is the latency requirement? (real-time, near-real-time, daily batch)
- [ ] What transformation logic is needed? (ETL vs ELT)
- [ ] What is the target data store? (data warehouse, data lake, operational database)
- [ ] Is schema evolution supported? (backward/forward compatible changes)
- [ ] How is data quality validated? (schema validation, null checks, range checks)
- [ ] Is exactly-once processing required or is at-least-once acceptable?
- [ ] How are failed records handled? (dead letter queue, retry, manual review)
- [ ] Is data partitioning strategy defined? (by date, by tenant, by region)
- [ ] What is the data retention policy? (hot, warm, cold, archive tiers)
- [ ] Is the pipeline idempotent? (safe to re-run without duplicates)
- [ ] How is pipeline orchestration managed? (Airflow, Step Functions, Dagster)
- [ ] Are data lineage and audit trails maintained?

## Common Mistakes

- No dead letter queue (failed records silently lost)
- No idempotency (re-runs create duplicates)
- Monolithic pipeline (one failure blocks everything)
- No data validation (garbage in, garbage out)
- Missing backpressure handling (producer overwhelms consumer)
- No monitoring on pipeline lag (data freshness degrades silently)

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
- Use **Kinesis Data Firehose** for simple ingestion to S3 (no shard management, pay per GB).
- Consider **columnar formats** (Parquet, ORC) — 3-5x compression reduces storage and query costs.

## Key Patterns

- **Lambda Architecture**: batch + speed layers
- **Kappa Architecture**: streaming-only with replay capability
- **Change Data Capture (CDC)**: stream database changes
- **Dead Letter Queue**: isolate failed records for investigation
- **Backpressure**: consumer signals producer to slow down
