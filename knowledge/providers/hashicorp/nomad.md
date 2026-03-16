# HashiCorp Nomad

## Checklist

- [ ] **[Recommended]** Determine job type for each workload: service (long-running), batch (short-lived, exit code matters), system (runs on every node matching constraints), sysbatch (batch on every node)
- [ ] **[Recommended]** Select appropriate task drivers: Docker (most common), exec (raw binary), Java, QEMU, containerd (community), Podman (community); plan driver plugin installation
- [ ] **[Recommended]** Design Consul integration for service discovery, health checking, and Consul Connect (service mesh with mTLS and intentions)
- [ ] **[Recommended]** Plan Vault integration for dynamic secrets injection (database credentials, PKI certificates, AWS STS tokens) into tasks via template stanza
- [ ] **[Optional]** Architect multi-region federation: configure servers in each region, set up WAN gossip, design job multi-region block with failover strategies
- [ ] **[Optional]** Configure autoscaling: Nomad Autoscaler with target plugins (Prometheus, Datadog, AWS ASG), scaling policies (target-value, threshold), and cooldown periods
- [ ] **[Recommended]** Plan CSI plugin deployment for persistent storage (EBS, EFS, Ceph, Portworx); configure volume registration and per-alloc volume claims
- [ ] **[Critical]** Design ACL policy structure: tokens, policies, capabilities (submit-job, read-job, alloc-lifecycle), namespace-scoped permissions, Sentinel policies (Enterprise)
- [ ] **[Recommended]** Configure resource management: CPU, memory (hard/soft limits), disk, network (port allocation: static, dynamic, mapped), device plugins (GPU)
- [ ] **[Recommended]** Evaluate spread and affinity scheduling constraints for rack-awareness, availability zone distribution, and hardware targeting
- [ ] **[Critical]** Plan upgrade strategy: server upgrades (one at a time, leader last), client upgrades (drain then upgrade), job version rollback procedures
- [ ] **[Recommended]** Design namespace isolation strategy for multi-team environments: resource quotas per namespace, ACL policies, Sentinel policies for governance

## Why This Matters

Nomad provides workload orchestration with significantly lower operational complexity than Kubernetes. Its single-binary architecture, first-class support for non-containerized workloads (raw binaries, JVMs, VMs), and deep HashiCorp ecosystem integration (Consul for service mesh, Vault for secrets) make it particularly suited for organizations that run heterogeneous workloads or lack dedicated platform engineering teams. The multi-region federation model is simpler than Kubernetes federation, making Nomad attractive for globally distributed deployments. However, Nomad's ecosystem is smaller than Kubernetes': fewer third-party integrations, less community tooling, and a smaller hiring pool. The architectural decision to use Nomad vs Kubernetes significantly impacts team structure, hiring, and long-term ecosystem access.

## License

HashiCorp transitioned all products from MPL 2.0 to BSL 1.1 in August 2023. The BSL restricts competitive use of the software — you cannot use it to build a product that competes with HashiCorp's commercial offerings. For internal infrastructure use, the BSL is functionally equivalent to open source. Community forks under MPL 2.0 exist: OpenTofu (Terraform fork) and OpenBao (Vault fork). Evaluate license terms for your specific use case before adoption.

## Common Decisions (ADR Triggers)

- **Nomad vs Kubernetes**: Nomad is simpler to operate (single binary, fewer moving parts), supports non-container workloads natively, and integrates tightly with Consul/Vault. Kubernetes has a vastly larger ecosystem, more third-party integrations, and a bigger talent pool. Choose Nomad when operational simplicity is paramount and workloads are heterogeneous; choose Kubernetes when ecosystem breadth and hiring are priorities.
- **Consul Connect vs standalone service mesh**: Consul Connect provides mTLS and service-to-service authorization (intentions) with minimal configuration. But it lacks Kubernetes-native features like traffic splitting and observability that Istio/Linkerd provide. If running Nomad, Consul Connect is the natural choice; mixing Istio with Nomad is unsupported.
- **Docker driver vs exec driver**: Docker provides image-based packaging, registry integration, and resource isolation. Exec runs raw binaries with chroot/cgroup isolation but no image layer caching. Use Docker for microservices with standard CI/CD; use exec for legacy binaries, performance-sensitive workloads, or environments without Docker.
- **Static ports vs dynamic ports**: Static ports simplify client configuration but limit scheduling flexibility (only one allocation per node for that port). Dynamic ports maximize bin-packing but require service discovery (Consul) for clients to find services. Default to dynamic ports with Consul service discovery.
- **Multi-region federation vs independent clusters**: Federation enables cross-region job deployment and failover from a single job spec. Independent clusters are simpler but require external tooling for cross-region orchestration. Use federation for active-active global services; independent clusters for isolated environments (dev/staging/prod).

## Reference Architectures

### Production Cluster Layout
```
[Region: us-east-1]                    [Region: eu-west-1]
+---------------------------+          +---------------------------+
| Nomad Servers (3 or 5)    |<--WAN-->| Nomad Servers (3 or 5)    |
| Consul Servers (3 or 5)   | Gossip  | Consul Servers (3 or 5)   |
| Vault Cluster (3)         |          | Vault Cluster (3)         |
+---------------------------+          +---------------------------+
         |                                       |
+---------------------------+          +---------------------------+
| Nomad Clients (N)         |          | Nomad Clients (N)         |
| - Docker driver           |          | - Docker driver           |
| - Consul agent            |          | - Consul agent            |
| - Vault agent (optional)  |          | - Vault agent (optional)  |
| - CSI plugin (node)       |          | - CSI plugin (node)       |
+---------------------------+          +---------------------------+
```
Servers form Raft consensus within each region. WAN gossip connects regions for federation. Consul provides service discovery and Connect mesh. Vault injects secrets via Nomad's template stanza. CSI node plugins run on clients for persistent volume attachment.

### Job with Consul Connect and Vault Secrets
```
job "api" {
  type = "service"

  group "api" {
    network {
      mode = "bridge"          # Required for Connect
      port "http" { to = 8080 }
    }

    service {
      name = "api"
      port = "http"
      connect {
        sidecar_service {
          proxy {
            upstreams {
              destination_name = "database"
              local_bind_port  = 5432
            }
          }
        }
      }
    }

    task "server" {
      driver = "docker"
      config {
        image = "api:v1.2.3"
      }

      vault { policies = ["api-policy"] }

      template {
        data = <<EOF
{{ with secret "database/creds/api-role" }}
DB_USER={{ .Data.username }}
DB_PASS={{ .Data.password }}
{{ end }}
EOF
        destination = "secrets/db.env"
        env         = true
      }
    }
  }
}
```
Bridge networking enables Consul Connect sidecar injection. Upstream blocks define service-to-service connectivity through the mesh. Vault template stanza fetches dynamic database credentials that rotate automatically. The Connect proxy handles mTLS and enforces Consul intentions (authorization policies).

### Autoscaling Pattern
```
[Nomad Autoscaler] --> [Prometheus (metrics source)]
        |
  [Scaling Policy]
  - target_value: avg CPU < 70%
  - min: 2, max: 20
  - cooldown: 60s
        |
  [Nomad API: scale job group]
        |
  [External Target Plugin (optional)]
  - AWS ASG for node scaling
  - Azure VMSS for node scaling
```
Nomad Autoscaler runs as a Nomad job. APM plugins query Prometheus, Datadog, or Nomad's own metrics for scaling signals. Task group count scales horizontally based on policies. For cluster-level scaling, target plugins adjust cloud provider auto-scaling groups to add/remove Nomad client nodes.
