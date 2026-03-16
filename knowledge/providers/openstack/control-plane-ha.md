# OpenStack Control Plane High Availability

## Scope

Covers OpenStack control plane high availability: HAProxy + keepalived/Pacemaker load balancing, MariaDB Galera cluster configuration, RabbitMQ clustering with quorum queues, Memcached caching, failure scenarios and recovery procedures, and upgrade considerations for HA components.

## Version Notes

| Release | Date | Key HA Changes |
|---|---|---|
| 2024.1 Caracal (29) | Apr 2024 | RabbitMQ quorum queues improvements, Galera monitoring enhancements |
| 2024.2 Dalmatian (30) | Oct 2024 | Continued HA stability improvements |
| 2025.1 Epoxy (31) | Apr 2025 | Classic mirrored queues deprecated in RabbitMQ 3.13+ (quorum queues required); improved oslo.messaging reconnect logic for RabbitMQ failover |
| 2025.2 Flamingo (32) | Oct 2025 | RabbitMQ 4.x compatibility improvements; continued Galera stability improvements |

## Checklist

- [ ] **[Critical]** Three controller nodes deployed for quorum-based services (Galera, RabbitMQ) — never use two nodes without an arbiter
- [ ] **[Critical]** HAProxy configured with health checks for every backend service; VIP managed by keepalived (VRRP) on the management network
- [ ] **[Critical]** MariaDB Galera cluster verified: `wsrep_cluster_size=3`, `wsrep_ready=ON`, `wsrep_local_state_comment=Synced` on all nodes
- [ ] **[Critical]** RabbitMQ cluster formed with quorum queues enabled (RabbitMQ 3.8+); `rabbitmqctl cluster_status` shows all 3 nodes
- [ ] **[Critical]** Split-brain prevention configured: Galera uses odd node count, RabbitMQ uses `pause_minority` partition handling
- [ ] **[Critical]** SSL/TLS termination configured at HAProxy for all public API endpoints; internal endpoints may use TLS or plaintext depending on security requirements
- [ ] **[Recommended]** HAProxy stats page enabled on a non-public interface for monitoring backend health and connection counts
- [ ] **[Recommended]** Galera SST method set to `mariabackup` (non-blocking) rather than `rsync` (blocking) for faster node rejoin
- [ ] **[Recommended]** RabbitMQ memory and disk watermarks tuned: `vm_memory_high_watermark.relative = 0.6`, disk free limit at 2 GB minimum
- [ ] **[Recommended]** Monitoring deployed for all HA components: Galera wsrep metrics, RabbitMQ management API, HAProxy stats, API endpoint health checks
- [ ] **[Recommended]** Documented and tested procedure for full cluster restart (Galera bootstrap, RabbitMQ force_boot)
- [ ] **[Recommended]** Fencing/STONITH configured if using Pacemaker, to prevent split-brain scenarios from causing data corruption
- [ ] **[Optional]** Memcached deployed on all three controllers behind HAProxy; Keystone configured with multiple memcached servers for token caching redundancy
- [ ] **[Optional]** RabbitMQ shovel or federation configured for cross-site message routing in multi-region deployments
- [ ] **[Optional]** Pacemaker + Corosync evaluated as alternative to keepalived for environments requiring more sophisticated resource management

## Why This Matters

The OpenStack control plane is the brain of the cloud. When it fails, no new VMs can be created, no volumes attached, no networks configured, and existing workloads become unmanageable. A single-controller deployment means any hardware failure, kernel panic, or failed upgrade takes the entire cloud management layer offline.

HA for the control plane involves three distinct layers that must all work together: load balancing and VIP failover (HAProxy + keepalived), database replication (Galera), and message queue clustering (RabbitMQ). A failure in any one layer can cascade. For example, a Galera node falling out of sync can cause API requests to return stale data; a RabbitMQ partition can cause agents on compute nodes to lose communication with schedulers.

The most dangerous failure mode is split-brain, where nodes disagree about cluster membership and make conflicting decisions. Galera and RabbitMQ have built-in mechanisms to handle this, but they must be correctly configured. An improperly configured cluster can appear to work during normal operation and only fail catastrophically during a network partition — exactly when you need it most.

## Common Decisions (ADR Triggers)

### ADR: Keepalived vs Pacemaker for VIP Management
**Trigger:** Choosing how to manage the virtual IP address (VIP) that clients use to reach API endpoints.
**Considerations:**
- **Keepalived** uses VRRP to manage a floating VIP. Simple to configure, lightweight, and sufficient for most deployments. The VIP moves to another node if the primary fails. Most deployment tools (Kolla-Ansible, OSA) default to keepalived.
- **Pacemaker + Corosync** is a full cluster resource manager. It can manage VIPs, services, and complex dependencies. Supports fencing (STONITH) to forcibly power off a misbehaving node. More complex to set up but provides stronger guarantees against split-brain.
- For most OpenStack deployments, keepalived is sufficient. Pacemaker is warranted when you need fencing (e.g., shared storage that could be corrupted by split-brain writes) or complex resource ordering.

### ADR: Classic Mirrored Queues vs Quorum Queues in RabbitMQ
**Trigger:** Configuring RabbitMQ clustering for OpenStack message queues.
**Considerations:**
- **Classic mirrored queues** (`ha-mode=all`): The legacy approach. Mirrors every queue to all nodes. Works but has known issues with synchronization during network partitions and node rejoins. Deprecated in RabbitMQ 3.13+.
- **Quorum queues**: Based on Raft consensus. Provide stronger consistency guarantees, better performance during node failures, and automatic leader election. Recommended for RabbitMQ 3.8+ and required going forward.
- OpenStack services support quorum queues via the `rabbit_quorum_queue` configuration option in oslo.messaging. Not all deployment tools enable this by default — verify and enable it.

### ADR: Galera SST Method
**Trigger:** A Galera node needs to rejoin the cluster after an extended outage.
**Considerations:**
- **IST (Incremental State Transfer):** Used when the rejoining node is only slightly behind. Transfers only the missing write sets via the gcache. Fast and non-disruptive. Happens automatically when possible.
- **SST (State Snapshot Transfer):** Used when the node is too far behind for IST (gcache has been overwritten). Transfers the entire database.
  - `rsync`: Blocks the donor node during transfer. Simple but causes a period where the donor cannot serve writes, temporarily reducing the cluster to a single writable node.
  - `mariabackup`: Non-blocking on the donor. Takes a hot backup while the donor continues serving. Recommended for production.
- Configure gcache.size large enough to cover expected maintenance windows (e.g., 1-2 GB) to maximize IST opportunities.

### ADR: SSL/TLS Strategy for Internal APIs
**Trigger:** Deciding whether to encrypt traffic between OpenStack services on the internal network.
**Considerations:**
- **TLS at HAProxy only (public endpoints):** Simplest. Internal traffic between services is plaintext on a trusted management network. Acceptable if the management network is isolated and physically secured.
- **Full TLS (internal + public):** Encrypts all inter-service communication. Required for compliance-sensitive environments (PCI-DSS, HIPAA). Adds CPU overhead for TLS handshakes and certificate management complexity.
- Certificate management: Use a private CA (e.g., Vault, FreeIPA, or simple OpenSSL CA) for internal certificates. Automate renewal.

### ADR: Monitoring Stack for HA Components
**Trigger:** Need visibility into control plane health.
**Considerations:**
- HAProxy exposes a stats page (CSV or HTML) and can be scraped by Prometheus via `haproxy_exporter`.
- Galera exposes wsrep metrics via `SHOW STATUS LIKE 'wsrep%'` — scrape with `mysqld_exporter`.
- RabbitMQ has a management plugin with HTTP API — scrape with `rabbitmq_exporter` or use the built-in Prometheus plugin (RabbitMQ 3.8+).
- OpenStack API health: periodically call each service's version endpoint (e.g., `GET /v3` for Keystone) and alert on failures.

## Reference Architectures

### HAProxy + Keepalived

HAProxy runs on all three controller nodes. Keepalived manages a VIP that floats between them. Clients connect to the VIP; HAProxy distributes requests to the healthy backends.

**HAProxy configuration pattern (per service):**
```
frontend keystone_public
    bind <VIP>:5000 ssl crt /etc/haproxy/certs/cloud.pem
    default_backend keystone_public_backend

backend keystone_public_backend
    balance roundrobin
    option httpchk GET /v3
    http-check expect status 200
    server ctrl01 10.0.0.11:5000 check inter 5s fall 3 rise 2
    server ctrl02 10.0.0.12:5000 check inter 5s fall 3 rise 2
    server ctrl03 10.0.0.13:5000 check inter 5s fall 3 rise 2
```

**Keepalived configuration pattern:**
```
vrrp_instance VI_1 {
    state MASTER          # MASTER on one node, BACKUP on others
    interface ens3         # Management network interface
    virtual_router_id 51
    priority 100           # Highest priority becomes MASTER
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass secretpassword
    }
    virtual_ipaddress {
        10.0.0.10/24       # The VIP
    }
}
```

**Key tuning parameters:**
- `inter 5s`: Health check interval. Lower values detect failures faster but add load.
- `fall 3`: Number of consecutive failed checks before marking backend down (15 seconds total with 5s interval).
- `rise 2`: Number of consecutive passed checks before marking backend up.
- `balance roundrobin`: Simple and effective for stateless API services. Use `source` for sticky sessions if needed.
- Connection limits: Set `maxconn` per backend to prevent overwhelming a service during failover (all traffic shifting to 2 backends).

### MariaDB Galera Cluster

Galera provides synchronous multi-master replication. All three controllers can accept writes. Writes are replicated to all nodes before the transaction commits (virtually synchronous — the write set is certified on all nodes).

**How Galera replication works:**
1. A write transaction executes locally on the originating node.
2. At commit time, the write set (changed rows) is broadcast to all nodes.
3. Each node certifies the write set against its own pending transactions (optimistic concurrency control).
4. If certification passes on all nodes, the transaction commits on all nodes. If it fails (conflict), the originating node rolls back.

**Cluster initialization (bootstrap):**
```bash
# On the first node only:
galera_new_cluster
# This starts MariaDB with wsrep_cluster_address=gcomm:// (empty = new cluster)

# On remaining nodes:
systemctl start mariadb
# These join the existing cluster via wsrep_cluster_address=gcomm://ctrl01,ctrl02,ctrl03
```

**Critical Galera settings:**
```ini
[galera]
wsrep_on=ON
wsrep_cluster_name="openstack_galera"
wsrep_cluster_address="gcomm://10.0.0.11,10.0.0.12,10.0.0.13"
wsrep_node_address="10.0.0.11"
wsrep_provider=/usr/lib/galera/libgalera_smm.so
wsrep_sst_method=mariabackup
wsrep_sst_auth=backup_user:backup_password

# Performance tuning
wsrep_slave_threads=4                 # Parallel replication threads (set to number of CPU cores / 4)
gcache.size=1G                        # Write-ahead cache for IST (larger = longer IST window)
max_connections=1000                  # Shared across all OpenStack services

# Safety
wsrep_auto_evict_dead_nodes=YES
wsrep_provider_options="gcache.size=1G; gcs.fc_limit=256; gcs.fc_factor=0.8"
```

**Monitoring queries:**
```sql
SHOW STATUS LIKE 'wsrep_cluster_size';     -- Should be 3
SHOW STATUS LIKE 'wsrep_ready';            -- Should be ON
SHOW STATUS LIKE 'wsrep_local_state_comment';  -- Should be "Synced"
SHOW STATUS LIKE 'wsrep_flow_control_paused';  -- Should be near 0 (>0.1 indicates replication lag)
SHOW STATUS LIKE 'wsrep_local_recv_queue_avg'; -- Should be near 0 (>1 indicates slow apply)
```

**Full cluster restart procedure (all nodes down):**
1. On each node, check `/var/lib/mysql/grastate.dat` for `seqno` — the node with the highest sequence number has the most recent data.
2. On that node, edit `grastate.dat` and set `safe_to_bootstrap: 1`.
3. Run `galera_new_cluster` on that node to start a new cluster with the most recent data.
4. Start MariaDB on the remaining nodes; they will join and perform IST or SST as needed.

**WARNING:** Never run `galera_new_cluster` on a node that does not have the highest `seqno`. This will cause data loss by rolling back transactions that the other nodes had committed.

### RabbitMQ Clustering

RabbitMQ runs on all three controllers. Nodes form a cluster and share queue metadata. Message data replication depends on the queue type.

**Cluster formation:**
```bash
# On ctrl02 and ctrl03:
rabbitmqctl stop_app
rabbitmqctl join_cluster rabbit@ctrl01
rabbitmqctl start_app

# Verify:
rabbitmqctl cluster_status
```

**Quorum queues (recommended):**
Quorum queues use Raft consensus for replication. Messages are replicated to a majority of nodes before being acknowledged to the producer. This provides strong consistency and automatic leader election.

Enable in OpenStack services (`/etc/nova/nova.conf`, `/etc/neutron/neutron.conf`, etc.):
```ini
[oslo_messaging_rabbit]
rabbit_quorum_queue = true
rabbit_quorum_queue_durable = true
```

**Partition handling:**
```ini
# In rabbitmq.conf:
cluster_partition_handling = pause_minority
```
With `pause_minority`, if a node loses contact with the majority of the cluster, it pauses itself (stops accepting connections) rather than continuing to operate independently. This prevents split-brain at the cost of temporary unavailability for the minority partition. When connectivity is restored, the paused node automatically resumes.

**Memory and disk watermarks:**
```ini
# In rabbitmq.conf:
vm_memory_high_watermark.relative = 0.6
disk_free_limit.absolute = 2GB
```
When memory usage exceeds the watermark, RabbitMQ blocks all publishers (producers) to prevent out-of-memory crashes. This causes OpenStack services to queue up messages locally, which manifests as API slowness. Monitor memory usage and increase RAM or tune watermarks before hitting this threshold.

**Monitoring:**
- `rabbitmqctl cluster_status` — cluster membership and running nodes
- `rabbitmqctl list_queues name messages consumers` — queue depth and consumer count
- Management plugin (port 15672): web UI and HTTP API for detailed metrics
- Prometheus plugin (RabbitMQ 3.8+): native `/metrics` endpoint

**Full cluster restart procedure (all nodes down):**
1. Start the node that was stopped last (it has the most recent data): `rabbitmq-server -detached`
2. If unsure which was last, force-boot one node: `rabbitmqctl force_boot && rabbitmq-server -detached`
3. Start remaining nodes normally; they will rejoin and sync.
4. `force_boot` tells a node to start without waiting for its peers. Only use this during a full cluster restart, never during normal operation.

### Memcached

Memcached provides distributed caching for Keystone tokens and other short-lived data. It has no built-in replication — if a memcached instance dies, cached data is lost, and services fall back to the database.

**Configuration in OpenStack services (e.g., Keystone):**
```ini
[cache]
enabled = true
backend = dogpile.cache.pymemcache
memcache_servers = 10.0.0.11:11211,10.0.0.12:11211,10.0.0.13:11211
```

Listing multiple servers makes OpenStack clients distribute keys across them using consistent hashing. If one server is lost, only its portion of the cache is invalidated — the remaining servers continue to serve their cached data.

**Sizing:** 512 MB to 2 GB per instance is typical. Keystone token caching is the largest consumer. Monitor hit rates: below 80% suggests the cache is too small or TTLs are too short.

### Common Failure Scenarios and Recovery

**Scenario: Single controller failure (hardware crash)**
- HAProxy detects the failed backend via health checks (within 15 seconds at default settings) and stops routing traffic to it.
- Galera continues operating with 2 of 3 nodes. All writes still succeed (majority quorum maintained).
- RabbitMQ continues with 2 of 3 nodes. Quorum queues elect new leaders for queues that were led by the failed node.
- Memcached loses its cache shard; affected tokens are re-fetched from the database.
- **Impact:** Minimal. API services remain available. Repair or replace the failed node and rejoin it to all clusters.

**Scenario: Network partition (ctrl03 loses connectivity to ctrl01 and ctrl02)**
- Galera: ctrl03 detects it is in a non-primary partition (minority) and refuses writes. ctrl01 and ctrl02 continue normally as the majority partition. When connectivity is restored, ctrl03 performs IST to catch up (or SST if the gcache has been overwritten).
- RabbitMQ (with `pause_minority`): ctrl03 pauses itself. ctrl01 and ctrl02 continue serving. When connectivity is restored, ctrl03 unpauses and rejoins.
- **Impact:** Services on ctrl03 are unavailable during the partition, but the majority partition continues operating. Recovery is automatic.

**Scenario: Full cluster restart (data center power loss)**
1. Identify the Galera node with the highest `seqno` and bootstrap it first.
2. Force-boot one RabbitMQ node, then start the others.
3. Start keepalived and HAProxy on all nodes.
4. Verify: all Galera nodes synced, all RabbitMQ nodes joined, all API endpoints responding.
5. **Estimated recovery time:** 10-30 minutes for an experienced operator.

### Upgrade Considerations

**Rolling upgrade pattern (one controller at a time):**
1. Disable the controller being upgraded in HAProxy (drain connections).
2. Stop OpenStack services on that controller.
3. Upgrade packages or container images.
4. Run database migrations (only on the first controller — migrations are idempotent but should only run once).
5. Start services on the upgraded controller.
6. Re-enable in HAProxy and verify health checks pass.
7. Repeat for the next controller.

**Galera during upgrades:**
- MariaDB minor version upgrades are safe with rolling restarts.
- Major version upgrades (e.g., 10.6 to 10.11) require more care: upgrade all nodes to the same version, then run `mysql_upgrade` on each.
- During an upgrade, the cluster temporarily operates with 2 nodes. Avoid upgrading more than one node at a time.

**RabbitMQ during upgrades:**
- Minor version upgrades support rolling restarts.
- Feature flag compatibility between versions must be verified — RabbitMQ will refuse to cluster nodes with incompatible feature flags.
- After upgrading all nodes, enable any new feature flags: `rabbitmqctl enable_feature_flag all`.
