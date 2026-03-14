# Azure Containers

## Checklist

- [ ] Is AKS deployed with system and user node pools separated, with system pools reserved for critical add-ons (CoreDNS, konnectivity) and user pools for application workloads?
- [ ] Is the AKS networking model selected -- Azure CNI (pods get VNet IPs, required for Windows nodes and advanced networking) vs Azure CNI Overlay (pod CIDR separate from VNet) vs kubenet (simpler, limited scale)?
- [ ] Is the cluster autoscaler enabled on user node pools with appropriate min/max node counts, and is the Horizontal Pod Autoscaler (HPA) configured for application-level scaling?
- [ ] Is AKS workload identity configured to federate Kubernetes service accounts with Microsoft Entra ID managed identities, replacing pod-managed identity (deprecated)?
- [ ] Is Azure Container Registry (ACR) deployed with geo-replication for multi-region AKS clusters, integrated via managed identity (not admin credentials or image pull secrets)?
- [ ] Is Azure Policy for AKS (Gatekeeper) enforcing cluster-level governance -- no privileged containers, required resource limits, allowed image registries, no latest tags?
- [ ] Is GitOps with Flux v2 configured as an AKS extension for declarative cluster configuration and application deployment from Git repositories?
- [ ] Are AKS backup and disaster recovery strategies defined -- Azure Backup for AKS (Velero-based), cross-region cluster deployment, and persistent volume snapshot policies?
- [ ] Is Azure Container Apps evaluated for microservices that do not require full Kubernetes control -- serverless scaling to zero, built-in Dapr for service invocation, pub/sub, and state management?
- [ ] Is Azure Container Instances (ACI) used only for appropriate workloads -- burst scaling from AKS (virtual nodes), CI/CD build agents, or short-lived batch tasks?
- [ ] Are AKS node pool VM SKUs selected based on workload profile -- general purpose (D-series), memory-optimized (E-series), compute-optimized (F-series), or GPU (NC/ND-series)?
- [ ] Is Azure Monitor Container Insights enabled with Prometheus metrics collection and Grafana dashboards for cluster and workload observability?
- [ ] Are AKS maintenance windows configured to control when node image upgrades and Kubernetes version upgrades are applied to minimize disruption?
- [ ] Is ingress configured with appropriate controller -- NGINX Ingress Controller, Application Gateway Ingress Controller (AGIC), or Azure-managed Istio service mesh for mTLS and traffic management?

## Why This Matters

Azure offers three container hosting options at different abstraction levels: AKS (full Kubernetes), Azure Container Apps (serverless containers with Dapr), and Azure Container Instances (single container groups). AKS networking decisions are particularly impactful -- Azure CNI consumes VNet IP addresses for every pod, requiring careful subnet sizing (a 100-node cluster with 30 pods each needs 3,000+ IPs). Container Apps eliminates cluster management entirely and scales to zero, making it ideal for event-driven microservices, but offers less control than AKS. Workload identity federation is the recommended authentication pattern, replacing the deprecated AAD pod-managed identity. ACR geo-replication ensures fast image pulls in multi-region deployments.

## Common Decisions (ADR Triggers)

- **AKS vs Azure Container Apps** -- full Kubernetes control with node management vs serverless containers with built-in Dapr, KEDA scaling, and zero infrastructure management
- **Azure CNI vs CNI Overlay vs kubenet** -- native VNet integration (IP-intensive) vs overlay networking (separate pod CIDR) vs simple routing (limited to 400 nodes)
- **Ingress controller** -- community NGINX (flexible, widely adopted) vs Application Gateway Ingress Controller (Azure-native L7, WAF integration) vs Istio-based (service mesh, mTLS)
- **AKS managed vs self-managed add-ons** -- Azure-managed Flux, Istio, monitoring vs Helm-installed community equivalents (ArgoCD, Linkerd, Prometheus stack)
- **Container Apps vs ACI** -- serverless microservices with Dapr and scaling rules vs simple container execution for burst workloads and batch jobs
- **Node pool strategy** -- single pool (simple) vs multiple pools per workload type with taints and tolerations vs spot node pools for cost-tolerant batch workloads
- **ACR tier** -- Basic (dev/test, 10 GB) vs Standard (production, 100 GB) vs Premium (geo-replication, private link, content trust, 500 GB)

## Reference Architectures

- [Azure Architecture Center: AKS baseline architecture](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks/baseline-aks) -- production-ready AKS cluster with networking, identity, observability, and governance best practices
- [Azure Architecture Center: Microservices on AKS](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices) -- reference design for deploying microservices with service mesh, API gateway, and observability
- [Azure Architecture Center: Azure Container Apps overview](https://learn.microsoft.com/en-us/azure/architecture/guide/container-apps/container-apps-overview) -- decision guide for when to use Container Apps vs AKS vs ACI
- [Azure Landing Zone: AKS enterprise-scale](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/app-platform/aks/landing-zone-accelerator) -- Cloud Adoption Framework accelerator for enterprise AKS deployment with governance and networking
- [Azure Architecture Center: AKS multi-region cluster](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks-multi-region/aks-multi-cluster) -- reference architecture for high availability AKS across multiple Azure regions with global load balancing
