# Container Orchestration

## Scope

This file covers **cloud-agnostic** container orchestration decisions — whether to containerize, which orchestration platform to use, and how to design the container platform (networking, storage, security, multi-tenancy). It addresses the **what** before provider-specific files cover the **how**. It does not cover provider-specific managed Kubernetes implementations (see provider container files), CI/CD pipeline design (see `general/deployment.md`), or application architecture patterns like microservices (see `patterns/microservices.md`).

## Checklist

- [ ] **[Critical]** Should workloads run in containers, VMs, serverless, or a mix? (Containers add operational complexity but improve density and portability; VMs provide stronger isolation for legacy or compliance-sensitive workloads; serverless eliminates infrastructure management but introduces vendor lock-in and cold-start latency)
- [ ] **[Critical]** Which container orchestration platform? (Kubernetes is the industry standard with the largest ecosystem but has steep operational overhead; ECS is simpler for AWS-only shops; Nomad is lightweight and supports mixed container/non-container workloads; Docker Swarm is deprecated for production use)
- [ ] **[Critical]** Managed Kubernetes vs self-managed? (Managed services like EKS, AKS, GKE reduce control plane burden but limit customization and may have version lag; self-managed gives full control but requires dedicated platform engineering capacity for upgrades, etcd backup, and HA)
- [ ] **[Critical]** How are container images built, stored, and scanned? (Private registries like Harbor, ECR, ACR, or Artifact Registry; images must be scanned for CVEs before deployment; consider image signing with Cosign/Notary for supply chain security; define a base image strategy to reduce sprawl)
- [ ] **[Critical]** What are the namespace and multi-tenancy boundaries? (Namespace-per-team, namespace-per-environment, or namespace-per-application; soft multi-tenancy with RBAC and network policies vs hard multi-tenancy with separate clusters; consider blast radius and noisy-neighbor risks)
- [ ] **[Critical]** What pod security standards are enforced? (Kubernetes Pod Security Standards — Privileged, Baseline, Restricted; enforce at namespace level via Pod Security Admission; decide whether any workloads genuinely need privileged access or host networking)
- [ ] **[Critical]** How is ingress traffic routed to services? (Ingress controller selection — NGINX, Traefik, HAProxy, cloud-native ALB controllers; consider whether a service mesh like Istio, Linkerd, or Consul Connect is warranted for mTLS, traffic shaping, and observability; service meshes add significant operational complexity)
- [ ] **[Recommended]** What container runtime is used? (containerd is the Kubernetes default and recommended for most deployments; CRI-O is an alternative optimized for Kubernetes-only use; Docker Engine as a runtime is deprecated in Kubernetes since v1.24; gVisor or Kata Containers add sandbox isolation for untrusted workloads)
- [ ] **[Recommended]** How are resource requests and limits defined? (CPU and memory requests drive scheduling; limits prevent noisy neighbors; ResourceQuotas enforce per-namespace caps; LimitRanges set defaults; over-provisioning wastes cost, under-provisioning causes OOM kills and throttling)
- [ ] **[Recommended]** What is the persistent storage strategy for stateful workloads? (CSI drivers for cloud or on-prem backends; StorageClass design — SSD vs HDD, replication, reclaim policy; StatefulSets vs Operators for databases; consider whether stateful workloads belong in the cluster or should use managed services)
- [ ] **[Recommended]** What container networking model and CNI plugin is used? (Calico for network policy enforcement and BGP peering; Cilium for eBPF-based networking and observability; Flannel for simplicity; cloud-native CNIs like VPC-CNI for AWS; consider IP address planning — overlay vs routable pod IPs)
- [ ] **[Recommended]** How is cluster capacity managed and scaled? (Cluster autoscaler or Karpenter for node scaling; Horizontal Pod Autoscaler for workload scaling; right-size node pools by workload class — general, compute-optimized, GPU; plan for surge capacity during deployments)
- [ ] **[Optional]** Is a GitOps workflow used for cluster configuration? (ArgoCD or Flux for declarative cluster state; separates application delivery from platform configuration; adds reconciliation loop complexity but improves auditability and drift detection)
- [ ] **[Optional]** How are multiple clusters managed? (Fleet management tools like Rancher, Tanzu Mission Control, or GKE Enterprise for multi-cluster governance; consider federation vs independent clusters; centralized policy enforcement across clusters)

## Why This Matters

Container orchestration is the most consequential platform decision in modern infrastructure. Choosing the wrong abstraction level — over-investing in Kubernetes for a small team running a handful of services, or under-investing in orchestration for a growing microservices fleet — creates years of technical debt. Teams that adopt Kubernetes without dedicated platform engineering capacity frequently end up with insecure, unreliable clusters that are harder to operate than the VMs they replaced.

The decisions in this file cascade through every other architectural concern. Namespace design affects security boundaries, network policy scope, and RBAC complexity. Storage strategy determines whether stateful workloads can run reliably or will suffer data loss during node failures. Ingress and service mesh choices affect latency, observability, and the ability to do canary deployments. Getting these foundational decisions wrong is expensive to reverse because workloads, CI/CD pipelines, and operational runbooks all build on top of them.

A common failure pattern is treating container orchestration as purely an infrastructure concern. In practice, it requires close collaboration between platform teams and application developers on image build standards, resource sizing, health check design, and graceful shutdown behavior. Organizations that skip this alignment end up with clusters full of misconfigured workloads — containers without resource limits consuming entire nodes, missing readiness probes causing traffic to hit unready pods, and images pulled from public registries without vulnerability scanning.

## Common Decisions (ADR Triggers)

- **Containers vs VMs vs serverless** — which workload types go where and why
- **Orchestration platform selection** — Kubernetes vs ECS vs Nomad vs managed service
- **Managed vs self-managed Kubernetes** — operational model and control plane ownership
- **Container runtime** — containerd vs CRI-O vs sandboxed runtimes for sensitive workloads
- **Image registry and supply chain security** — private registry, scanning policy, image signing
- **Cluster topology** — single cluster vs multi-cluster, cluster-per-environment vs shared clusters
- **Namespace and tenancy model** — how teams, environments, and applications map to namespaces
- **Ingress controller and service mesh** — whether to adopt a service mesh and which one
- **CNI plugin selection** — overlay vs routable networking, network policy engine
- **Persistent storage strategy** — in-cluster stateful workloads vs external managed services
- **GitOps adoption** — ArgoCD vs Flux vs imperative deployment pipelines

## Reference Links

- [Kubernetes](https://kubernetes.io/docs/)
- [containerd](https://containerd.io/)
- [CRI-O](https://cri-o.io/)
- [Calico](https://www.tigera.io/project-calico/)
- [Cilium](https://cilium.io/)
- [Karpenter](https://karpenter.sh/)
- [Harbor](https://goharbor.io/)

## See Also

- `providers/kubernetes/compute.md` — Kubernetes workload scheduling, pod design, and node management
- `providers/kubernetes/networking.md` — Kubernetes-specific CNI, ingress, and service mesh configuration
- `providers/kubernetes/storage.md` — CSI drivers, PersistentVolumes, and StorageClasses
- `providers/kubernetes/security.md` — RBAC, Pod Security Standards, and network policies in Kubernetes
- `providers/kubernetes/operations.md` — Kubernetes cluster lifecycle, upgrades, and troubleshooting
- `providers/aws/containers.md` — ECS and EKS implementation details
- `providers/azure/containers.md` — AKS implementation details
- `providers/gcp/containers.md` — GKE implementation details
- `providers/openshift/infrastructure.md` — OpenShift as an opinionated Kubernetes distribution
- `providers/hashicorp/nomad.md` — Nomad as an alternative orchestrator
- `providers/harbor/registry.md` — Harbor container registry deployment
- `providers/rancher/infrastructure.md` — Rancher multi-cluster management
- `general/deployment.md` — CI/CD pipelines and deployment strategies
- `general/security.md` — General security considerations including container security context
- `patterns/microservices.md` — Microservices architecture patterns that drive container orchestration needs
- `general/service-mesh.md` — Service mesh adoption, mTLS, traffic management, and observability integration
