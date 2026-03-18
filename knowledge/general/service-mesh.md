# Service Mesh

## Scope

This file covers service mesh adoption decisions, platform selection, traffic management, security (mTLS), observability integration, and performance considerations for Kubernetes-based and multi-cluster environments. It is cloud-agnostic. For Kubernetes networking fundamentals, see `general/networking.md`. For observability integration details, see `general/observability.md`. For deployment strategies (canary, blue-green) at the application level, see `general/deployment.md`.

## Checklist

- [ ] **[Critical]** Is a service mesh justified for this workload? (Service meshes add operational complexity; they are warranted when you need consistent mTLS, fine-grained traffic control, or cross-service observability across many services -- typically 10+ microservices. For fewer services, application-level libraries or simple Kubernetes NetworkPolicies may suffice)
- [ ] **[Critical]** Which service mesh platform is selected, and does it align with the team's operational capacity? (Istio: most features, highest complexity, largest community; Linkerd: lightweight, minimal configuration, Rust-based proxy; Consul Connect: strong multi-datacenter support, integrates with non-Kubernetes workloads; Cilium service mesh: eBPF-based, no sidecars, requires Linux 5.10+ kernel)
- [ ] **[Critical]** Is mTLS enforced for all service-to-service communication within the mesh? (Strict mode encrypts and authenticates all traffic; permissive mode allows plaintext during migration. Strict mode should be the target state. Verify no services break when plaintext is disallowed)
- [ ] **[Critical]** How are mesh certificates managed and rotated? (Istio uses an internal CA (istiod) by default with 24-hour leaf cert lifetime; Linkerd uses trust anchors with a 1-year default root cert that must be manually rotated; both can integrate with external CAs like cert-manager, Vault, or AWS Private CA for production-grade PKI)
- [ ] **[Recommended]** Is the sidecar proxy resource overhead budgeted per pod? (Envoy sidecar typically consumes 50-100 MB memory and 0.1-0.5 vCPU per pod at baseline; at 200 pods, this adds 10-20 GB memory and 20-100 vCPU cluster-wide. Multiply by actual pod count to verify node capacity)
- [ ] **[Recommended]** Are traffic management policies defined for critical services? (Retries: set max retries and per-try timeout to prevent retry storms; circuit breakers: configure outlier detection thresholds; timeouts: set request-level timeouts shorter than client-side timeouts; rate limiting: global vs. local rate limiting at the mesh gateway)
- [ ] **[Recommended]** Is a canary or progressive delivery strategy implemented through the mesh? (Traffic splitting via VirtualService weighted routing in Istio, TrafficSplit in Linkerd/SMI, or integration with Flagger/Argo Rollouts for automated canary analysis and rollback)
- [ ] **[Recommended]** Is the mesh integrated with the observability stack? (Sidecar proxies emit L7 metrics -- request rate, error rate, latency per service pair -- automatically. Configure Prometheus scraping of proxy metrics, enable distributed tracing propagation via headers such as x-request-id and b3, and export access logs for debugging)
- [ ] **[Recommended]** Is sidecar injection configured correctly? (Namespace-level auto-injection vs. pod-level annotations; ensure init containers, Jobs, and CronJobs handle sidecar lifecycle correctly -- sidecars that do not terminate can cause Jobs to hang indefinitely)
- [ ] **[Recommended]** Is Gateway API adopted instead of legacy Ingress for north-south traffic? (Gateway API is the successor to Ingress with support for traffic splitting, header-based routing, and cross-namespace references; Istio, Linkerd, and Cilium all support it. Legacy Ingress remains functional but will not receive new features)
- [ ] **[Optional]** Is a sidecar-less architecture evaluated? (Istio ambient mesh uses per-node ztunnel for L4 mTLS and optional waypoint proxies for L7 policy, reducing per-pod overhead; Cilium service mesh uses eBPF for L4/L7 without sidecars. Both are newer with smaller production footprints as of 2025)
- [ ] **[Optional]** Is multi-cluster mesh connectivity required? (Istio supports multi-primary and primary-remote topologies; Linkerd uses multi-cluster gateway with service mirroring; Consul Connect uses mesh gateways for cross-datacenter federation. All require network connectivity between clusters and shared trust roots)
- [ ] **[Optional]** Are non-Kubernetes workloads (VMs, bare metal) included in the mesh? (Istio supports VM workloads via WorkloadEntry with a sidecar agent; Consul Connect natively supports non-Kubernetes workloads. Linkerd is Kubernetes-only)
- [ ] **[Optional]** Is the mesh control plane deployed in high availability? (Istio: run multiple istiod replicas across zones with leader election; Linkerd: run multiple control plane replicas. Single-replica control plane is a single point of failure for policy updates and certificate rotation, though the data plane continues operating if the control plane is briefly unavailable)

## Why This Matters

Service meshes solve real problems -- consistent encryption, traffic control, and observability across a microservices architecture -- but they are one of the most frequently over-adopted technologies in cloud-native environments. Teams deploy a service mesh for a 5-service application and spend more time debugging proxy configuration, troubleshooting sidecar injection failures, and managing control plane upgrades than they would have spent adding TLS and retry logic to the applications directly. The decision to adopt a mesh should be driven by concrete requirements (regulatory mTLS mandate, complex traffic routing needs, 10+ services needing uniform observability) rather than by architectural aspiration.

Once adopted, the most common failure mode is neglecting the operational burden. Sidecar proxies consume real resources -- a 500-pod cluster with Envoy sidecars requires 25-50 GB of additional memory and significant CPU. Mesh upgrades require careful coordination because the control plane and data plane (sidecars) must be version-compatible, and in-place sidecar upgrades require pod restarts. Certificate rotation failures in Linkerd's trust anchor have caused production outages when the root certificate expired after 1 year without rotation. Teams must treat the mesh as infrastructure that requires dedicated operational investment.

Traffic management features (canary deployments, circuit breaking, retries) are powerful but dangerous when misconfigured. Retry policies without proper budgets cause retry storms that amplify failures instead of mitigating them. Circuit breakers with overly aggressive thresholds prematurely cut off healthy backends. Traffic splitting percentages that do not account for session affinity cause inconsistent user experiences. Each traffic policy should be tested under realistic load before production deployment, and every retry or circuit breaker configuration should include explicit reasoning about failure scenarios.

## Common Decisions (ADR Triggers)

- **Adopt vs. defer service mesh** -- service mesh adds uniform mTLS and observability but introduces sidecar overhead, upgrade complexity, and operational burden; application-level libraries (gRPC TLS, OpenTelemetry SDK) are simpler but inconsistent across languages and teams
- **Platform selection: Istio vs. Linkerd vs. Cilium vs. Consul Connect** -- Istio has the broadest feature set but highest complexity and resource cost; Linkerd is simpler and lighter but lacks some advanced traffic features; Cilium eliminates sidecar overhead via eBPF but requires recent kernels and has a smaller service mesh track record; Consul Connect excels at multi-runtime (VM + K8s) but adds HashiCorp dependency
- **Sidecar vs. sidecar-less (ambient mesh / eBPF)** -- sidecars provide full L7 control per workload but consume resources per pod; sidecar-less reduces overhead and eliminates injection complexity but offers less mature L7 features and tighter kernel/CNI coupling
- **Certificate authority: mesh-internal CA vs. external CA integration** -- internal CA (istiod, Linkerd identity) is simple to set up but creates an isolated PKI; external CA (Vault, cert-manager, cloud provider CA) integrates with enterprise PKI but adds integration complexity and external dependency
- **Gateway API vs. Ingress for north-south traffic** -- Gateway API provides richer routing, cross-namespace support, and is the Kubernetes standard going forward; legacy Ingress is simpler and widely supported but frozen in functionality
- **Multi-cluster mesh topology** -- flat network with shared control plane is simplest but requires cross-cluster network connectivity; federated control planes with service mirroring work across network boundaries but add latency and configuration complexity
- **Progressive delivery integration** -- mesh-native traffic splitting (VirtualService weights) vs. dedicated progressive delivery controller (Flagger, Argo Rollouts) that automates canary analysis and rollback; dedicated controllers add another component but reduce manual error

## Reference Links

- [Istio](https://istio.io/)
- [Linkerd](https://linkerd.io/)
- [Cilium](https://cilium.io/)
- [Consul Connect](https://developer.hashicorp.com/consul/docs/connect)
- [Gateway API](https://gateway-api.sigs.k8s.io/)
- [Envoy Proxy](https://www.envoyproxy.io/)

## See Also

- `general/networking.md` -- Kubernetes networking, CNI selection, NetworkPolicy
- `general/deployment.md` -- Deployment strategies, CI/CD pipeline design
- `general/observability.md` -- Metrics, tracing, and logging strategy
- `general/security.md` -- Zero-trust networking, encryption in transit
- `general/tls-certificates.md` -- Certificate management and rotation
- `providers/kubernetes/networking.md` -- Kubernetes-specific networking and CNI
- `providers/hashicorp/consul.md` -- Consul Connect details
