# GCP Containers

## Checklist

- [ ] Is the appropriate GKE mode selected? (Autopilot for hands-off node management and pod-level billing, Standard for full node configuration control, custom kernels, or privileged workloads)
- [ ] Are node pools configured with appropriate machine types, auto-scaling (min/max nodes), and surge upgrade settings (max-surge, max-unavailable) for rolling updates?
- [ ] Is Workload Identity enabled on the cluster and configured per namespace/service account to map Kubernetes service accounts to GCP IAM service accounts without key files?
- [ ] Is Binary Authorization enabled with attestation policies requiring container images to be signed by trusted authorities before deployment to production clusters?
- [ ] Is Artifact Registry used as the container image registry, with vulnerability scanning enabled and IAM-scoped access per repository?
- [ ] Is GKE Gateway Controller configured for advanced traffic management (traffic splitting, header-based routing, multi-cluster gateways) instead of legacy Ingress?
- [ ] Are Config Sync and Policy Controller deployed for GitOps-based cluster configuration and OPA Gatekeeper policy enforcement across fleet clusters?
- [ ] Is the GKE release channel configured appropriately? (Rapid for dev/test, Regular for staging, Stable for production) with maintenance windows and exclusions set?
- [ ] Are Pod Disruption Budgets, resource requests/limits, and priority classes configured to ensure workload availability during node upgrades and autoscaler scale-down?
- [ ] Is Cloud Run configured with appropriate concurrency (max 1000 requests/container), minimum instances (to eliminate cold starts), and CPU allocation mode (CPU always allocated vs request-only)?
- [ ] Is VPC-native (alias IP) networking enabled on the cluster with appropriately sized secondary ranges for pod and service CIDRs?
- [ ] Are GKE node auto-provisioning (NAP) and cluster autoscaler configured with resource limits (CPU, memory, GPU) to prevent runaway scaling costs?
- [ ] Is Anthos evaluated for multi-cloud or hybrid Kubernetes deployments, with Connect gateway and fleet management for centralized control?
- [ ] Are GKE Backup for workloads configured for stateful applications with appropriate backup schedules and retention policies?

## Why This Matters

GKE is the most mature managed Kubernetes offering across cloud providers, with Autopilot providing a unique pod-level abstraction that eliminates node management entirely. The choice between Autopilot and Standard has significant implications: Autopilot enforces security best practices (no privileged containers, no host network) and bills per pod resource request, while Standard gives full node access but requires managing node pools, OS patching, and capacity. Workload Identity is critical because the alternative (node-level service accounts or mounted key files) creates significant security risks. Cloud Run provides a simpler serverless container model for request-driven workloads where Kubernetes complexity is not needed, with per-request billing that can be dramatically cheaper for sporadic traffic.

## Common Decisions (ADR Triggers)

- **GKE mode** -- Autopilot (managed nodes, pod billing, security defaults) vs Standard (full control, node billing, custom configurations)
- **GKE vs Cloud Run** -- Kubernetes orchestration vs serverless containers, persistent workloads vs request-driven, team Kubernetes expertise
- **Multi-cluster strategy** -- single regional cluster vs multi-zonal vs multi-regional with Multi Cluster Ingress, fleet management
- **GitOps tooling** -- Config Sync (managed, Anthos) vs Argo CD vs Flux, policy enforcement via Policy Controller vs standalone Gatekeeper
- **Image management** -- Artifact Registry (regional, multi-region) vs self-hosted registry, vulnerability scanning policy (block critical CVEs)
- **Ingress model** -- GKE Gateway Controller vs classic GCE Ingress vs nginx Ingress Controller vs Istio ingress gateway
- **Anthos adoption** -- GKE on-prem vs Anthos on AWS/Azure vs GKE Attached Clusters, Connect gateway for fleet management
- **Cloud Run scaling** -- min instances (cost vs cold start latency) vs zero-to-N scaling, CPU always-allocated (background tasks) vs request-only (cost savings)

## Reference Architectures

- [Google Cloud Architecture Center: Containers](https://cloud.google.com/architecture#containers) -- reference architectures for GKE cluster design, multi-tenant patterns, and CI/CD pipelines
- [Google Cloud: GKE best practices](https://cloud.google.com/kubernetes-engine/docs/best-practices) -- comprehensive guidance on cluster setup, networking, security, and cost optimization
- [Google Cloud: Migrate to containers](https://cloud.google.com/architecture/migrating-containers-to-google-cloud) -- reference architecture for modernizing applications from VMs to GKE or Cloud Run
- [Google Cloud: Multi-cluster Kubernetes with GKE](https://cloud.google.com/kubernetes-engine/docs/concepts/multi-cluster-ingress) -- reference design for multi-region GKE with global load balancing and fleet management
- [Google Cloud: Cloud Run production best practices](https://cloud.google.com/run/docs/tips/general) -- reference patterns for concurrency tuning, cold start mitigation, and cost optimization for serverless containers
