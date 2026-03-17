# Ceph Storage

Ceph is a distributed, software-defined storage platform providing block (RBD), object (RGW/S3), and file (CephFS) storage from a single cluster. Used as the storage backend for OpenStack (Cinder, Glance, Manila), OpenShift Data Foundation (ODF/Rook), Proxmox, and standalone deployments.

## Checklist

- [ ] **[Critical]** Is the cluster sized correctly? (minimum 3 nodes for production, 3 monitors for quorum, OSD count determines capacity and IOPS — plan for at least 3 replicas or EC profile overhead)
- [ ] **[Critical]** Is the CRUSH map designed to match the failure domain topology? (host-level failure domain minimum, rack-level for larger clusters — controls data placement across failure domains)
- [ ] **[Critical]** Is the storage backend BlueStore? (default since Luminous, direct block device management — do not use legacy FileStore for new deployments)
- [ ] **[Critical]** Are pools configured with appropriate replication or erasure coding? (3x replication for hot data and RBD, erasure coding like 4+2 for cold/archive data — EC saves space but has write amplification and no partial reads)
- [ ] **[Recommended]** Is the OSD journal/WAL/DB on fast media? (NVMe for WAL/DB when using HDD OSDs — BlueStore WAL/DB placement significantly impacts write latency)
- [ ] **[Recommended]** Are PG (Placement Group) counts set correctly per pool? (too few PGs causes uneven data distribution, too many wastes memory — use `ceph osd pool autoscale-mode on` in Nautilus+ or calculate manually: target ~100 PGs per OSD)
- [ ] **[Critical]** Is the cluster network separated from the public network? (dedicated backend network for OSD replication traffic — prevents replication from competing with client I/O, typically 10GbE minimum, 25GbE recommended)
- [ ] **[Recommended]** Are MDS (Metadata Server) instances deployed for CephFS? (active-standby minimum, active-active for high metadata workloads — MDS count scales with metadata operations, not data throughput)
- [ ] **[Recommended]** Is RGW (RADOS Gateway) deployed for S3/Swift API access? (multiple RGW instances behind a load balancer, multi-site for geo-replication — configured per realm/zonegroup/zone)
- [ ] **[Critical]** Is monitoring configured? (Ceph Dashboard, Prometheus module for metrics, Grafana dashboards — monitor OSD latency, PG states, cluster health, capacity, scrub status)
- [ ] **[Critical]** Is the monitoring stack deployment model decided? (cephadm deploys its own Prometheus, Grafana, Alertmanager, and Node Exporter by default — Rook does not, it exposes ServiceMonitors for an existing Prometheus Operator. If a centralized Prometheus/Grafana stack already exists, decide whether to disable Ceph's built-in stack and scrape Ceph exporters from the central instance, or run both and accept dashboard fragmentation)
- [ ] **[Recommended]** If using cephadm with an external Prometheus, is the Prometheus module enabled and the exporter endpoint exposed? (`ceph mgr module enable prometheus` — scrape at `http://<mgr-host>:9283/metrics`, add as a target in the central Prometheus)
- [ ] **[Recommended]** Are Ceph Grafana dashboards imported into the centralized Grafana? (Ceph provides pre-built dashboards — import from the ceph-mixins project or from the cephadm-deployed Grafana to avoid maintaining separate Grafana instances)
- [ ] **[Recommended]** Is the upgrade path planned? (Ceph requires sequential major version upgrades — cannot skip versions, rolling upgrades with `ceph orch upgrade` in cephadm-managed clusters)
- [ ] **[Critical]** Is encryption at rest configured? (dm-crypt for OSD encryption in BlueStore — keys managed by Ceph or external KMS like Vault, required for compliance workloads)
- [ ] **[Recommended]** Are scrub and deep-scrub schedules configured? (scrub verifies metadata consistency, deep-scrub verifies data checksums — schedule during low-I/O windows, do not disable)
- [ ] **[Optional]** Is RBD mirroring configured for disaster recovery? (journal-based or snapshot-based mirroring between clusters — RPO depends on mirroring mode, journal-based is near-synchronous)

## Why This Matters

Ceph is the de facto standard for open-source distributed storage. It underpins OpenStack clouds, OpenShift container storage (ODF), and many enterprise storage platforms. Design decisions at deployment time — CRUSH map, pool replication strategy, network topology — are extremely difficult to change later. A poorly designed CRUSH map leads to uneven data distribution and hotspots. Undersized PG counts cause data imbalance that worsens as the cluster grows. Missing network separation causes replication traffic to starve client I/O during recovery events.

Ceph recovery after an OSD failure is I/O intensive — the cluster rebalances data across remaining OSDs. If the cluster is near capacity (>80%), recovery may not complete before the next failure, risking data loss. Capacity planning must account for failure recovery headroom, not just raw storage needs.

## Common Decisions (ADR Triggers)

- **Deployment tool** — cephadm (official, container-based, Octopus+) vs Rook (Kubernetes operator, used by ODF) vs manual (legacy) — cephadm for standalone, Rook for K8s-integrated
- **Monitoring stack: built-in vs centralized** — cephadm deploys Prometheus, Grafana, Alertmanager, and Node Exporter as containers by default (skip with `--skip-monitoring-stack` at bootstrap). When a centralized observability stack already exists (common in enterprise environments), running Ceph's built-in stack creates duplicate infrastructure and dashboard fragmentation. Options: (1) disable Ceph's monitoring containers and scrape `ceph-exporter` from the central Prometheus, importing Ceph dashboards into the central Grafana; (2) keep Ceph's stack isolated for storage team autonomy; (3) federate Ceph's Prometheus into the central instance. Rook deployments expose `ServiceMonitor` CRDs for Prometheus Operator — no built-in stack to manage. See also: [Prometheus/Grafana observability](../prometheus-grafana/observability.md)
- **Replication vs erasure coding** — 3x replication (simple, fast reads, 3x raw cost) vs EC 4+2 (1.5x raw cost, higher write latency, no partial overwrites for RBD) — use replication for RBD/hot data, EC for RGW/cold data
- **All-flash vs hybrid** — NVMe/SSD-only (high IOPS, predictable latency) vs HDD with NVMe WAL/DB (high capacity, lower cost, variable latency) — depends on workload IOPS requirements
- **CephFS vs RGW vs RBD** — block (RBD for VMs/containers), object (RGW for S3-compatible), file (CephFS for shared POSIX) — often all three from one cluster
- **Single cluster vs multi-site** — single cluster with rack-level failure domains vs multi-site with RGW multi-site or RBD mirroring — latency between sites determines sync vs async replication
- **Dedicated OSD nodes vs converged** — dedicated storage nodes (better performance isolation) vs converged with compute (lower cost, HCI model like Nutanix/Proxmox) — depends on scale and performance requirements

## Version Notes

| Feature | Luminous (12) | Mimic (13) | Nautilus (14) | Octopus (15) | Pacific (16) | Quincy (17) | Reef (18) | Squid (19) |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| BlueStore default | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| cephadm orchestrator | — | — | — | GA | GA | GA | GA | GA |
| PG autoscaling | — | — | GA | GA | GA | GA | GA | GA |
| Dashboard | Basic | Improved | Full | Full | Full | Full | Full | Full |
| RBD snapshot-based mirroring | — | — | GA | GA | GA | GA | GA | GA |
| Stretch clusters | — | — | — | — | GA | GA | GA | GA |
| msgr2 (v2 protocol) | — | — | GA | GA | GA | GA | GA | GA |
| RGW multi-site sync | GA | GA | GA | GA | Improved | Improved | Improved | Improved |
| CephFS multi-active MDS | Preview | Preview | GA | GA | GA | GA | GA | GA |
| Quincy LTS | — | — | — | — | — | LTS | — | — |
| Prometheus module | Preview | GA | GA | GA | GA | GA | GA | GA |

## Monitoring Configuration

### Cephadm Built-in Grafana

Cephadm deploys Grafana automatically. To deploy manually or reconfigure:

```bash
ceph orch apply grafana
```

Service spec (`grafana.yaml`):

```yaml
service_type: grafana
placement:
  count: 1
spec:
  port: 4200
  protocol: https
  initial_admin_password: <password>
  anonymous_access: False
```

TLS is managed by cephadm's certificate manager by default. For custom certificates:

```bash
ceph orch certmgr cert set --cert-name grafana_ssl_cert --hostname <host> -i certificate.pem
ceph orch certmgr key set --key-name grafana_ssl_key --hostname <host> -i key.pem
ceph orch reconfig grafana
```

Enable TLS and authentication across all monitoring components:

```bash
ceph config set mgr mgr/cephadm/secure_monitoring_stack true
```

Dashboard integration is automatic. If Grafana is in a different DNS zone from users:

```bash
ceph dashboard set-grafana-api-url <backend-grafana-url>
ceph dashboard set-grafana-frontend-api-url <browser-accessible-url>
ceph dashboard set-grafana-api-ssl-verify False  # for self-signed certs
```

### External Prometheus/Grafana Integration

To scrape Ceph from a centralized Prometheus instead of using the built-in stack:

1. Enable the Prometheus module: `ceph mgr module enable prometheus`
2. Configure the external Prometheus to scrape ceph-exporter using cephadm's service discovery:

```yaml
- job_name: 'ceph-exporter'
  http_sd_configs:
  - url: https://<mgr-ip>:8765/sd/prometheus/sd-config?service=ceph-exporter
    basic_auth:
      username: '<username>'
      password: '<password>'
    tls_config:
      ca_file: '/path/to/ca.crt'
```

3. Import Ceph Grafana dashboards from the [ceph-mixin dashboards](https://github.com/ceph/ceph/tree/main/monitoring/ceph-mixin/dashboards_out) into the centralized Grafana.
4. Configure "Dashboard1" as the Prometheus data source name in Grafana (required by Ceph dashboard JSON).

## Reference Architectures

- [Ceph Documentation — Architecture](https://docs.ceph.com/en/latest/architecture/) — official architecture overview covering RADOS, CRUSH, and client protocols
- [Ceph Hardware Recommendations](https://docs.ceph.com/en/latest/start/hardware-recommendations/) — official sizing guidance for OSD, MON, MDS, and RGW nodes
- [Red Hat Ceph Storage Architecture Guide](https://docs.redhat.com/en/documentation/red_hat_ceph_storage/) — enterprise deployment patterns and best practices
- [Rook Ceph Operator](https://rook.io/docs/rook/latest/) — Kubernetes-native Ceph deployment via Rook (used by ODF)
- [Ceph Monitoring Services (cephadm)](https://docs.ceph.com/en/latest/cephadm/services/monitoring/) — deploying and configuring Prometheus, Grafana, and Alertmanager via cephadm
- [Ceph Dashboard — Grafana](https://docs.ceph.com/en/latest/mgr/dashboard/) — configuring Grafana integration with the Ceph Dashboard UI
