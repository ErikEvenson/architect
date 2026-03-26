# HashiCorp Consul

## Scope

HashiCorp Consul: server cluster sizing, ACL system, gossip and TLS encryption, health checks, DNS interface, service mesh (Connect with Envoy sidecars), Consul on Kubernetes, Consul Dataplane, KV store, WAN federation, and Consul Template.


## Checklist

- [ ] **[Critical]** Consul server cluster has 3 or 5 nodes (odd number required for Raft consensus); 3 nodes tolerates 1 failure, 5 tolerates 2; more than 5 is not recommended due to replication overhead
- [ ] **[Recommended]** Consul client agents run on every node that hosts services (as a DaemonSet in Kubernetes, or as a system service on VMs); services register with their local agent
- [ ] **[Critical]** ACL system is enabled and bootstrapped; default policy is `deny`; each service has a token with minimum required permissions for registration, discovery, and intention management
- [ ] **[Critical]** Gossip encryption is enabled with a shared symmetric key (`encrypt` config); all agents in the datacenter must use the same key; key rotation uses the `consul keyring` command
- [ ] **[Critical]** TLS is enabled for RPC and HTTP communication between agents; `verify_incoming` and `verify_outgoing` are both true; auto_encrypt simplifies client certificate distribution
- [ ] **[Recommended]** Health checks are defined for every service: HTTP (GET /health), TCP, gRPC, script, or TTL-based; check intervals and timeouts are tuned to avoid flapping (10s-30s interval, 5s timeout typical)
- [ ] **[Recommended]** DNS interface is configured and resolvers point to Consul for the `.consul` domain (e.g., `web.service.consul` resolves to healthy instances of the "web" service)
- [ ] **[Recommended]** Service mesh (Connect) is enabled with sidecar proxies (Envoy) for mTLS between services; intentions define which services can communicate (allow/deny per source-destination pair)
- [ ] **[Optional]** Prepared queries are configured for failover scenarios: query a service locally first, then failover to neighboring datacenters based on network coordinates (RTT-based)
- [ ] **[Optional]** WAN federation connects multiple datacenters; WAN gossip pool operates over port 8302; services in one DC can discover services in others via `service.dc2.consul` DNS queries
- [ ] **[Recommended]** Consul on Kubernetes uses the official Helm chart with connect-inject enabled; `connectInject.default: false` requires explicit annotation (`consul.hashicorp.com/connect-inject: "true"`) per pod
- [ ] **[Recommended]** Is Consul Dataplane used instead of traditional client agents for Kubernetes deployments (eliminates DaemonSet requirement)?
- [ ] **[Recommended]** KV store usage is limited to configuration data and coordination (leader election, distributed locks); it is not a general-purpose database; values are limited to 512 KB
- [ ] **[Optional]** Consul Template is deployed on application hosts to render configuration files from Consul KV and service catalog data, with automatic reload of dependent services on change

## Why This Matters

Consul provides the service discovery layer that enables dynamic infrastructure. Without reliable service discovery, applications hardcode IP addresses and ports, making scaling, failover, and deployment changes manual and error-prone. The service mesh (Connect) provides mutual TLS between services without application code changes, but misconfigured intentions can either block legitimate traffic (outage) or allow unauthorized communication (security gap). The ACL system prevents unauthorized service registration (a rogue service could intercept traffic by registering with a legitimate service name). Gossip encryption prevents network-level attackers from joining the cluster or reading service catalog data. In multi-datacenter deployments, WAN federation enables global service discovery and failover, but network partitions between datacenters can cause split-brain scenarios that must be understood and planned for.

## License

HashiCorp transitioned all products from MPL 2.0 to BSL 1.1 in August 2023. The BSL restricts competitive use of the software — you cannot use it to build a product that competes with HashiCorp's commercial offerings. For internal infrastructure use, the BSL is functionally equivalent to open source. IBM completed its acquisition of HashiCorp in late 2024, which may affect product direction, licensing terms, and commercial offerings over time. Community forks under MPL 2.0 exist for organizations requiring open-source licensing: OpenTofu (Terraform fork) and OpenBao (Vault fork). Evaluate license terms and IBM's product roadmap for your specific use case before adoption.

## Common Decisions (ADR Triggers)

- **Consul vs alternatives for service discovery**: Consul provides DNS and HTTP APIs for discovery, health checking, KV, and service mesh in one tool. Alternatives include Kubernetes-native service discovery (sufficient if everything is in one cluster), AWS Cloud Map, or etcd/ZooKeeper for simpler KV + discovery. Consul's advantage is multi-platform (VMs + Kubernetes + serverless) and multi-datacenter federation. Its disadvantage is operational complexity.
- **Service mesh: Consul Connect vs Istio vs Linkerd**: Consul Connect uses Envoy sidecars and integrates with Consul's service catalog and intentions. Istio is Kubernetes-native and more feature-rich (traffic splitting, fault injection, observability) but more complex. Linkerd is simpler and lighter but less flexible. Choose Consul Connect when Consul is already deployed for discovery or when the mesh must span VMs and Kubernetes.
- **Sidecar proxy: Envoy vs built-in proxy**: Consul ships a basic built-in proxy for development but production deployments must use Envoy. Envoy provides L7 routing, observability (metrics, tracing), circuit breaking, and retry policies. The built-in proxy supports only basic TCP proxying.
- **DNS vs HTTP API for discovery**: DNS is universal (any application can resolve `web.service.consul`) but limited in metadata and load balancing (DNS round-robin only, TTL caching issues). The HTTP API (`/v1/health/service/web`) returns full metadata, tags, weights, and health status but requires application integration. Use DNS for simple cases; HTTP API when you need tag-based filtering, weighted routing, or rich metadata.
- **KV store vs dedicated config management**: Consul KV is convenient for service configuration, feature flags, and coordination. But it lacks schema validation, access audit trails (beyond ACLs), and rich query capabilities. For complex configuration management, consider dedicated tools (Vault for secrets, a config service for application settings) and use Consul KV only for infrastructure coordination.
- **Deployment model on Kubernetes: Helm vs manual**: The official Helm chart manages server StatefulSets, client DaemonSets, connect-inject webhook, mesh-gateway, and ACL initialization. Manual deployment gives more control but requires maintaining all these components. Use Helm unless there is a specific requirement it cannot meet.
- **Multi-datacenter topology: WAN federation vs cluster peering**: Traditional WAN federation joins all Consul server nodes across datacenters into a WAN gossip pool. Cluster peering (Consul 1.14+) connects specific clusters with a peering token, supports partial connectivity, and works across admin partitions. Cluster peering is simpler for connecting independent Consul deployments; WAN federation is better for tightly coupled datacenters under single management.

## Reference Architectures

### Multi-Datacenter Service Discovery

```
Datacenter: us-east-1                    Datacenter: eu-west-1
+----------------------------+           +----------------------------+
| Consul Server Cluster (3)  |<-- WAN -->| Consul Server Cluster (3)  |
| Raft consensus (leader +2) | Federation| Raft consensus (leader +2) |
+---+---+---+----------------+ Port 8302 +---+---+---+----------------+
    |   |   |                                 |   |   |
    v   v   v                                 v   v   v
+--------+ +--------+ +--------+         +--------+ +--------+
|Client  | |Client  | |Client  |         |Client  | |Client  |
|Agent   | |Agent   | |Agent   |         |Agent   | |Agent   |
|node-01 | |node-02 | |node-03 |         |node-04 | |node-05 |
+---+----+ +---+----+ +---+----+         +---+----+ +---+----+
    |          |          |                   |          |
  web-01    api-01     db-01              web-02      api-02

DNS resolution:
  web.service.consul           -> web-01 (local DC only)
  web.service.us-east-1.consul -> web-01 (explicit DC)
  web.service.eu-west-1.consul -> web-02 (cross-DC query)

Prepared Query (failover):
  Name: "web"
  Service: "web"
  Failover:
    NearestN: 2  (failover to 2 nearest DCs by RTT)
  Result: web-01 (healthy, local), web-02 (failover, remote)
```

### Kubernetes Service Mesh with Connect

```
Kubernetes Cluster
  |
  +-- Namespace: consul
  |     |-- consul-server (StatefulSet, 3 replicas)
  |     |    Persistent volumes for Raft data
  |     |    Anti-affinity: one per node/AZ
  |     |
  |     |-- consul-connect-injector (Deployment)
  |     |    Mutating webhook: watches pod annotations
  |     |    Injects: envoy sidecar + consul-dataplane
  |     |
  |     |-- consul-mesh-gateway (Deployment)
  |          Routes cross-DC service mesh traffic
  |          Exposes single port for inter-cluster communication
  |
  +-- Namespace: production
       |
       |-- Pod: frontend
       |    Annotation: consul.hashicorp.com/connect-inject: "true"
       |    Container: frontend-app (port 8080)
       |    Sidecar: envoy (inbound: mTLS listener -> 8080)
       |                     (outbound: localhost:9090 -> api-sidecar)
       |    Upstream: consul.hashicorp.com/connect-service-upstreams:
       |              "api:9090"
       |
       |-- Pod: api
       |    Annotation: consul.hashicorp.com/connect-inject: "true"
       |    Container: api-app (port 3000)
       |    Sidecar: envoy (inbound: mTLS listener -> 3000)
       |                     (outbound: localhost:5432 -> db-sidecar)
       |    Upstream: "database:5432"
       |
       |-- Pod: database
            Annotation: consul.hashicorp.com/connect-inject: "true"
            Container: postgres (port 5432)
            Sidecar: envoy (inbound: mTLS listener -> 5432)

Intentions (service-level firewall):
  frontend -> api:       ALLOW
  api -> database:       ALLOW
  frontend -> database:  DENY  (must go through api)
  * -> *:                DENY  (default deny)
```

### Consul Template for Dynamic Configuration

```
Application Host
  |
  +-- Consul Agent (client mode)
  |     Registered services: nginx, app
  |     Health checks: HTTP /health every 10s
  |
  +-- Consul Template (daemon)
  |     Watches: service catalog + KV store
  |     Renders: configuration files on change
  |     Reloads: dependent services after render
  |
  |     Template: nginx-upstreams.ctmpl
  |     ----------------------------------------
  |     upstream api_backends {
  |       {{range service "api"}}
  |       server {{.Address}}:{{.Port}} weight=1;
  |       {{end}}
  |     }
  |     ----------------------------------------
  |     Output: /etc/nginx/conf.d/upstreams.conf
  |     Command: "nginx -s reload"
  |
  |     Template: app-config.ctmpl
  |     ----------------------------------------
  |     {{with secret "secret/data/app/config"}}
  |     DB_HOST={{key "config/app/db_host"}}
  |     DB_PORT={{key "config/app/db_port"}}
  |     API_KEY={{.Data.data.api_key}}
  |     FEATURE_FLAGS={{key "config/app/features"}}
  |     {{end}}
  |     ----------------------------------------
  |     Output: /etc/app/config.env
  |     Command: "systemctl restart app"

Consul KV:
  config/app/db_host    = "db-primary.internal"
  config/app/db_port    = "5432"
  config/app/features   = "dark_mode=true,beta_api=false"
  config/app/log_level  = "info"
```

## Reference Links

- [Consul Documentation](https://developer.hashicorp.com/consul/docs) -- architecture, ACL system, service mesh (Connect), KV store, and multi-datacenter federation
- [Consul on Kubernetes](https://developer.hashicorp.com/consul/docs/k8s) -- Helm chart configuration, connect-inject, Consul Dataplane, and mesh gateway setup
- [Consul Tutorials](https://developer.hashicorp.com/consul/tutorials) -- hands-on guides for service discovery, service mesh, and cluster operations

## See Also

- `general/service-mesh.md` -- service mesh architecture patterns
- `providers/hashicorp/vault.md` -- Vault integration for Consul Connect certificates
- `providers/hashicorp/nomad.md` -- Nomad integration with Consul for service discovery
- `providers/kubernetes/networking.md` -- Kubernetes service mesh alternatives
