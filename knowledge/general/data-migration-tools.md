# Data Migration Tooling and Strategies

## Scope

This file covers **data migration tooling and execution** including rclone, pg_dump/pg_restore, AWS DMS, bandwidth planning, and data validation. It does not cover migration strategy selection or cutover planning; for those, see `general/database-migration.md` and `general/workload-migration.md`.

## Checklist

- [ ] **[Critical]** Inventory all data stores (databases, object storage, file systems, caches) with sizes and growth rates
- [ ] **[Critical]** Calculate total transfer time: data size / available bandwidth, accounting for overhead and parallel stream limits
- [ ] **[Critical]** Validate data integrity post-transfer using checksums (md5sum, sha256sum) and row count comparisons
- [ ] **[Critical]** Test restore procedures before production migration — a backup you cannot restore is not a backup
- [ ] **[Critical]** Encrypt all data in transit (TLS 1.2+, VPN tunnels) and at rest (encrypted dump files, encrypted volumes)
- [ ] **[Recommended]** Configure rclone with bandwidth limiting (`--bwlimit`) to avoid saturating production network links
- [ ] **[Recommended]** Use parallel restore with pg_dump custom format (`-Fc`) and pg_restore `--jobs` for large PostgreSQL databases
- [ ] **[Recommended]** Set up incremental sync (rclone sync, aws s3 sync) after initial full copy to minimize cutover window
- [ ] **[Recommended]** Test cross-version database migration (e.g., PostgreSQL 12 to 15) in staging before production
- [ ] **[Recommended]** Document and migrate database roles, permissions, and globals separately (pg_dumpall --globals-only)
- [ ] **[Recommended]** Configure multipart upload thresholds for large files (aws s3 cp --multipart-threshold, rclone --s3-upload-cutoff)
- [ ] **[Optional]** Evaluate AWS Snowball or similar physical transfer for datasets exceeding 10TB over slow links
- [ ] **[Optional]** Set up AWS DMS for continuous replication (CDC) if zero-downtime migration is required
- [ ] **[Optional]** Build automated validation scripts that compare source and target row counts, schema structure, and sample data
- [ ] **[Optional]** Create a dedicated migration network (separate VLAN or VPN) to isolate transfer traffic from production

## Why This Matters

Data migration is the highest-risk phase of any cloud migration. Data loss or corruption during transfer can be catastrophic and often undetectable until production traffic reveals inconsistencies. Choosing the wrong tool or strategy can turn a 2-hour migration into a 2-day outage. The difference between `rclone copy` (additive) and `rclone sync` (destructive — deletes files at destination not present at source) has caused production data loss. Similarly, a pg_dump without `--no-owner` or `--no-acl` flags will fail on restore if roles do not exist in the target. Every decision in this space has consequences that are expensive to reverse.

Transfer time is frequently underestimated. 1TB over a 100Mbps link takes approximately 22 hours at theoretical maximum — real-world throughput with protocol overhead, encryption, and shared bandwidth is typically 50-70% of line speed. Planning for this avoids blown maintenance windows and rushed cutover decisions.

## Common Decisions (ADR Triggers)

### ADR: Object Storage Migration Tool Selection
**Context:** Need to migrate files between S3-compatible storage backends (AWS S3, Ceph RGW, Swift s3api, MinIO).
**Options:**
- **rclone** — Multi-cloud, supports 40+ backends, checksumming, bandwidth limiting, filtering. Good for heterogeneous environments. Config file (`~/.config/rclone/rclone.conf`) stores multiple backend credentials.
- **aws s3 sync** — AWS-native, incremental sync by default (compares size and timestamp), tight IAM integration. Only works with S3 or S3-compatible endpoints.
- **s3cmd** — Lightweight, good for scripting (`s3cmd put`, `s3cmd sync`), supports S3-compatible endpoints via `--host` and `--host-bucket` flags.

**Decision criteria:** If migrating between two different cloud providers or to/from on-prem, rclone is the better choice. If staying within AWS or S3-compatible ecosystems, aws s3 sync is simpler. If writing shell scripts that need granular control, s3cmd offers the most scriptable interface.

### ADR: Database Migration Approach (Dump/Restore vs Replication)
**Context:** Need to migrate a production PostgreSQL or MySQL database with minimal downtime.
**Options:**
- **pg_dump/pg_restore (or mysqldump/mydumper)** — Snapshot-based. Requires downtime proportional to database size. pg_dump custom format (`-Fc`) enables parallel restore (`pg_restore -j 8`). mysqldump is single-threaded; mydumper enables parallel dump and restore.
- **AWS DMS with CDC** — Continuous replication. Initial full load followed by change data capture. Supports heterogeneous migration (e.g., Oracle to PostgreSQL via Schema Conversion Tool). Requires ongoing replication instance cost.
- **Logical replication (native)** — PostgreSQL logical replication or MySQL binlog replication. Near-zero downtime but requires same or compatible engine versions. More complex to set up but no third-party tooling.

**Decision criteria:** For databases under 50GB with an acceptable maintenance window (1-2 hours), dump/restore is simplest. For databases over 50GB or zero-downtime requirements, DMS or native logical replication is necessary. For heterogeneous migrations (different database engines), DMS with Schema Conversion Tool is the primary option.

### ADR: Large Dataset Transfer Method
**Context:** Migrating datasets exceeding 10TB where network transfer time is prohibitive.
**Options:**
- **Parallel network transfer** — rclone with `--transfers 32 --checkers 16`, multiple parallel streams, compression (`--gzip`).
- **Physical transfer (AWS Snowball, Azure Data Box)** — Ship physical devices. 50TB or 80TB Snowball Edge capacity. 1-2 week round trip.
- **Chunked migration** — Migrate in phases: cold data first (historical, archival), then warm data, then hot data with final sync at cutover.

**Decision criteria:** Calculate break-even: if network transfer time exceeds 1 week and Snowball round-trip is faster, use physical transfer. For 10-50TB over 1Gbps, parallel network transfer with rclone typically completes in 1-5 days and is operationally simpler.

## Reference Architectures

### rclone Multi-Cloud Sync Architecture

```
Source (AWS S3)                    Target (Ceph RGW / Swift)
+------------------+               +------------------+
| S3 Bucket        | -- rclone --> | Ceph RGW Bucket  |
| us-east-1        |   sync       | on-prem cluster  |
+------------------+               +------------------+
        |                                   |
   rclone config:                    rclone config:
   [aws]                            [ceph]
   type = s3                        type = s3
   provider = AWS                   provider = Ceph
   access_key_id = ...              access_key_id = ...
   secret_access_key = ...          secret_access_key = ...
   region = us-east-1               endpoint = https://rgw.example.com

Command:
  rclone sync aws:source-bucket ceph:target-bucket \
    --transfers 16 \
    --checkers 8 \
    --bwlimit 500M \
    --checksum \
    --log-file /var/log/rclone-migration.log \
    --log-level INFO \
    --progress
```

Key rclone flags:
- `sync` vs `copy`: sync deletes files at destination not present at source; copy is additive only
- `--checksum`: compare by hash instead of size+modtime (slower but more reliable)
- `--filter-from filters.txt`: include/exclude patterns for selective migration
- `--dry-run`: preview what would be transferred without making changes
- `--retries 3 --retries-sleep 10s`: automatic retry on transient failures

### PostgreSQL Migration Architecture

```
Source (AWS RDS PostgreSQL 12)         Target (OpenStack VM PostgreSQL 15)
+---------------------------+          +---------------------------+
| RDS pg 12                 |          | Nova VM pg 15             |
| - application database    |          | - empty database created  |
| - roles & permissions     |          | - roles pre-created       |
+---------------------------+          +---------------------------+
        |                                        |
   pg_dumpall --globals-only > globals.sql       |
   pg_dump -Fc -j 4 dbname > dbname.dump         |
        |                                        |
        +--- scp / rclone (encrypted) ---------->+
                                                 |
                                        psql -f globals.sql
                                        pg_restore -Fc -j 8 \
                                          --no-owner \
                                          --no-acl \
                                          -d dbname dbname.dump
                                                 |
                                        ANALYZE (update statistics)
                                        Validate: row counts, checksums
```

Cross-version considerations:
- pg_dump from newer client can dump older server (use target version's pg_dump binary)
- Extension compatibility: check that all extensions (PostGIS, pgcrypto, etc.) are available on target version
- Configuration parameters: some pg settings change between major versions (review postgresql.conf)
- Sequence values: verify sequences migrated correctly (they are included in pg_dump but worth validating)

### AWS DMS Continuous Replication Architecture

```
Source DB                  AWS DMS                      Target DB
+-----------+      +----------------------+      +-------------+
| Oracle    | ---> | Replication Instance | ---> | PostgreSQL  |
| (on-prem) |      | - Schema Conversion  |      | (OpenStack) |
+-----------+      |   Tool (SCT)         |      +-------------+
                   | - Full Load task     |
                   | - CDC task           |
                   +----------------------+

Task Types:
1. Full Load Only: one-time snapshot migration
2. CDC Only: ongoing replication of changes (requires full load done separately)
3. Full Load + CDC: initial snapshot then continuous replication

CDC Requirements:
- Source: supplemental logging enabled (Oracle), binlog enabled (MySQL), logical replication (PostgreSQL)
- Network: persistent connectivity between DMS instance and both source/target
- Monitoring: CloudWatch metrics for replication lag, table statistics
```

### Data Validation Pipeline

```
Source DB/Storage              Validation Layer              Target DB/Storage
+---------------+        +------------------------+        +---------------+
| Production    | -----> | Row Count Comparison   | <----- | Migrated      |
| Data          |        | Schema Diff            |        | Data          |
+---------------+        | Checksum Validation    |        +---------------+
                         | Sample Query Compare   |
                         +------------------------+
                                    |
                              Pass / Fail
                              Report

Validation Script Outline:
1. Row counts: SELECT COUNT(*) FROM each table on source and target
2. Checksum: SELECT md5(string_agg(col::text, '')) FROM table ORDER BY pk
3. Schema diff: pg_dump --schema-only on both, diff the output
4. Sample queries: run 10 representative queries, compare results
5. Object storage: rclone check source:bucket target:bucket --one-way
```

### Bandwidth Planning Reference

| Data Size | 100 Mbps | 1 Gbps | 10 Gbps |
|-----------|----------|--------|---------|
| 100 GB    | 2.5 hrs  | 15 min | 1.5 min |
| 1 TB      | 24 hrs   | 2.5 hrs| 15 min  |
| 10 TB     | 10 days  | 24 hrs | 2.5 hrs |
| 100 TB    | 100 days | 10 days| 24 hrs  |

*Assumes 80% effective throughput. Multiply by 1.3-1.5 for real-world estimates with encryption, protocol overhead, and retransmissions.*

## See Also

- [database-migration.md](database-migration.md) -- migration strategy selection, cutover planning, and rollback procedures
- [workload-migration.md](workload-migration.md) -- overall workload migration planning and sequencing
- [cloud-service-mapping.md](cloud-service-mapping.md) -- service equivalents across cloud providers relevant to migration targets
