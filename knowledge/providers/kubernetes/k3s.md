# K3s Lightweight Kubernetes

## Scope

K3s lightweight Kubernetes: installation topologies (single-node, HA embedded etcd, external database), secrets encryption, bundled components (Traefik, CoreDNS, local-path-provisioner), CIS hardening, private registries, automated upgrades, and CNI replacement.


## Checklist

- [ ] **[Critical]** Select installation topology: single-node (curl script), HA embedded etcd (3+ server nodes), or external database (MySQL/PostgreSQL/etcd) based on availability requirements
- [ ] **[Critical]** Configure --secrets-encryption flag on server to enable encryption at rest for Secrets stored in the datastore
- [ ] **[Critical]** Secure the join token (stored at /var/lib/rancher/k3s/server/node-token) and distribute securely to agent nodes; rotate if compromised
- [ ] **[Critical]** Set up backup strategy: file copy for SQLite (single-node), etcdctl snapshot for embedded etcd, or database-native backup for external DB
- [ ] **[Recommended]** Evaluate default bundled components (Traefik, CoreDNS, local-path-provisioner, ServiceLB/Klipper, metrics-server) and disable unneeded ones with --disable flags (e.g., --disable traefik to use a different ingress controller)
- [ ] **[Recommended]** Enable CIS benchmark hardening with --protect-kernel-defaults and validate node kernel parameters comply with kubelet expectations
- [ ] **[Recommended]** Configure private registry mirrors in /etc/rancher/k3s/registries.yaml for air-gapped environments, rate-limit avoidance, or private image hosting
- [ ] **[Recommended]** Deploy system-upgrade-controller for automated K3s version upgrades via Plan CRDs with concurrency controls and cordon/drain behavior
- [ ] **[Recommended]** Configure audit logging (--kube-apiserver-arg=audit-log-path=/var/log/k3s-audit.log) for security event tracking and compliance
- [ ] **[Recommended]** Plan TLS certificate rotation strategy; K3s auto-rotates certificates but verify rotation works before expiry (default 12 months)
- [ ] **[Optional]** Replace default Flannel CNI with Calico, Cilium, or other CNI by installing K3s with --flannel-backend=none and deploying the alternative CNI
- [ ] **[Optional]** Configure resource reservations (--kubelet-arg=system-reserved=cpu=250m,memory=256Mi) to protect K3s server processes from workload pressure
- [ ] **[Optional]** Set up air-gapped installation with pre-downloaded images tarball (k3s-airgap-images-amd64.tar.gz) placed in /var/lib/rancher/k3s/agent/images/

## Why This Matters

K3s is a CNCF-certified Kubernetes distribution that packages the control plane into a single binary under 100MB, using roughly 512MB RAM and 0.5 CPU for the server process. This makes it practical for environments where full upstream Kubernetes is too resource-intensive: edge deployments, IoT gateways, CI/CD runners, development machines, and proof-of-concept clusters. K3s achieves this by replacing etcd with SQLite (single-node) or embedded etcd (HA), bundling essential components (ingress, DNS, storage, load balancer), and using containerd directly instead of Docker.

Despite its lightweight footprint, K3s runs the same Kubernetes API and passes CNCF conformance tests. Workloads, Helm charts, and kubectl commands work identically to upstream Kubernetes. This means POC workloads built on K3s can migrate to EKS, GKE, or upstream Kubernetes without application changes -- only infrastructure-layer configuration (ingress, storage classes, cloud integrations) needs adjustment.

## Common Decisions (ADR Triggers)

- **SQLite vs embedded etcd vs external database** -- SQLite is the default for single-node and requires no additional configuration, but cannot support HA (only one server node can write). Embedded etcd enables HA with 3+ server nodes using the Raft consensus protocol without external dependencies, but adds ~500MB memory per node. External databases (MySQL, PostgreSQL, external etcd) allow separating state from compute and leveraging managed database services (RDS), but add an infrastructure dependency and network latency. Choose SQLite for development/POC, embedded etcd for production HA without external dependencies, external DB when managed database services are available and preferred.
- **K3s vs upstream K8s (kubeadm)** -- K3s uses containerd (not Docker), bundles Flannel as the default CNI, and includes Traefik ingress, CoreDNS, and local-path storage provisioner out of the box. Upstream kubeadm requires installing each component separately, consuming more resources (2-3GB RAM vs 512MB) but providing more flexibility in component selection. K3s is appropriate when operational simplicity and low resource usage matter more than component-level customization.
- **Default Traefik vs alternative ingress** -- K3s bundles Traefik 2.x as the default ingress controller. Disable it (--disable traefik) when the team standardizes on NGINX Ingress Controller, or when advanced features like Istio gateway are needed. Keeping Traefik simplifies initial setup and reduces components to manage.
- **ServiceLB (Klipper) vs external load balancer** -- K3s includes Klipper LoadBalancer which creates host-port DaemonSets to expose LoadBalancer-type services. This works for single-node and bare-metal but does not provide true load balancing across nodes. For production multi-node, consider MetalLB or a cloud load balancer and disable Klipper with --disable servicelb.
- **Single-node POC vs HA production** -- A single K3s server is the fastest path to a working cluster (one curl command) and is sufficient for development and POC. For production, embedded etcd with 3 server nodes provides control plane HA with automatic leader election. The migration path from single-node SQLite to HA etcd requires a fresh cluster (no in-place migration), so plan the topology upfront if production use is anticipated.

## Reference Architectures

### Single-Node Development/POC
```
[Single K3s Server]
  ├── containerd (container runtime)
  ├── SQLite (datastore)
  ├── Flannel (CNI)
  ├── CoreDNS
  ├── Traefik (ingress)
  ├── local-path-provisioner (storage)
  ├── ServiceLB/Klipper (LoadBalancer)
  └── metrics-server

Install: curl -sfL https://get.k3s.io | sh -
Kubeconfig: /etc/rancher/k3s/k3s.yaml
Backup: cp /var/lib/rancher/k3s/server/db/state.db /backup/
```
Everything runs on a single node. Suitable for local development, CI/CD test clusters, and architecture POCs. Resource usage: ~512MB RAM + 0.5 CPU for K3s itself, remainder available for workloads.

### HA Production with Embedded etcd
```
[K3s Server 1] ── etcd ──┐
[K3s Server 2] ── etcd ──┼── Raft consensus (3-node minimum)
[K3s Server 3] ── etcd ──┘
       │
       ├── [Load Balancer / VIP] ← kubectl, agent registration
       │
[K3s Agent 1] ── workloads
[K3s Agent 2] ── workloads
[K3s Agent N] ── workloads
```
Three server nodes with embedded etcd for control plane HA. Agent nodes join via the load balancer endpoint. Servers also run workloads unless tainted. Backup via `k3s etcd-snapshot save` on any server node. Auto-upgrades managed by system-upgrade-controller with Plan CRDs specifying version and concurrency.

### Air-Gapped Edge Deployment
```
[Build Machine]
  ├── Download k3s binary
  ├── Download k3s-airgap-images tarball
  └── Package with application images

[Edge Node]
  ├── /usr/local/bin/k3s (binary)
  ├── /var/lib/rancher/k3s/agent/images/ (airgap images)
  └── /etc/rancher/k3s/registries.yaml (private registry mirror)

Install: INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh
```
For environments without internet access. Pre-download the K3s binary and images tarball, transfer to the target node, and install offline. Configure registries.yaml to point to a local registry mirror for application images. Common in manufacturing, retail edge, and secure government environments.

## See Also

- `general/container-orchestration.md` -- container orchestration platform selection
- `providers/kubernetes/security.md` -- Kubernetes security controls and RBAC
- `providers/kubernetes/operations.md` -- Kubernetes operations and upgrade strategies
- `providers/rancher/infrastructure.md` -- Rancher management for K3s clusters
