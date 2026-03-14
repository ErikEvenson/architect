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

## Key Patterns

- **Lambda Architecture**: batch + speed layers
- **Kappa Architecture**: streaming-only with replay capability
- **Change Data Capture (CDC)**: stream database changes
- **Dead Letter Queue**: isolate failed records for investigation
- **Backpressure**: consumer signals producer to slow down
