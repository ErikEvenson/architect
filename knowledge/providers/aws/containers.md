# AWS Containers (ECS, EKS, ECR)

## Checklist

- [ ] Choose orchestrator: ECS (AWS-native, simpler, tighter AWS integration) vs EKS (Kubernetes-compatible, portable, broader ecosystem) based on team expertise and portability requirements
- [ ] Select ECS launch type: EC2 (full instance control, GPU support, larger task sizes, cost savings with reserved instances) vs Fargate (no instance management, per-vCPU/memory billing, faster scaling)
- [ ] Configure ECR repositories with image scanning (basic or enhanced via Inspector), lifecycle policies to expire untagged/old images, and cross-region replication for multi-region deployments
- [ ] Define ECS task definitions with appropriate CPU/memory combinations (Fargate has fixed ratios: 0.25-4 vCPU, 0.5-30 GB memory), IAM task roles (not instance roles), and log configuration
- [ ] Set up service discovery using AWS Cloud Map for service-to-service communication with DNS-based or API-based discovery; integrate with App Mesh for advanced traffic management
- [ ] Configure capacity providers: Fargate/Fargate Spot for ECS, managed node groups/Fargate profiles for EKS; use Fargate Spot for fault-tolerant workloads (up to 70% savings, 2-minute interruption notice)
- [ ] Evaluate Graviton (ARM-based) instances for ECS EC2 and EKS node groups -- typically 20-40% better price-performance than x86 equivalents for containerized workloads
- [ ] Implement container health checks at both the Docker HEALTHCHECK level and ALB/NLB target group level; configure deregistration delay to allow in-flight requests to complete
- [ ] Enable Container Insights (CloudWatch) for cluster, service, and task-level metrics including CPU, memory, network, and disk utilization; adds cost but essential for production observability
- [ ] Use EKS managed node groups for automatic node provisioning, AMI updates, and graceful draining; consider Karpenter for faster, more flexible node autoscaling than Cluster Autoscaler
- [ ] Configure EKS add-ons (CoreDNS, kube-proxy, VPC CNI, EBS CSI driver) as managed add-ons for automatic version compatibility and updates
- [ ] Evaluate Bottlerocket OS for container-optimized nodes: minimal attack surface, atomic updates, API-driven configuration, no SSH by default; supports both ECS and EKS
- [ ] Design task/pod placement with spread strategies across AZs for high availability; use binpack strategy for cost optimization on EC2 launch type

## Why This Matters

Containers provide consistent deployment units, efficient resource utilization, and faster startup compared to virtual machines. The choice between ECS and EKS affects operational complexity, team onboarding, ecosystem compatibility, and long-term portability. ECS is simpler to operate with deeper AWS integration (IAM task roles, CloudWatch native), while EKS provides Kubernetes API compatibility enabling multi-cloud portability and access to the massive Kubernetes ecosystem (Helm charts, operators, CNCF tools).

Fargate removes node management entirely but costs 20-30% more than well-utilized EC2 instances. For predictable steady-state workloads, EC2 with reserved instances or Savings Plans is more economical. For spiky or new workloads where utilization is uncertain, Fargate eliminates the waste of over-provisioned instances.

## Common Decisions (ADR Triggers)

- **ECS vs EKS** -- ECS is appropriate when the team lacks Kubernetes expertise, workloads are AWS-only, and simpler operations are preferred. EKS is appropriate when Kubernetes knowledge exists, multi-cloud portability matters, or specific Kubernetes ecosystem tools (Istio, Argo, Crossplane) are needed. EKS control plane costs $0.10/hour ($73/month) regardless of workload size.
- **Fargate vs EC2 launch type** -- Fargate for variable workloads, small teams without capacity planning expertise, and rapid scaling requirements. EC2 for GPU workloads, consistent high-utilization workloads, workloads needing host-level access (docker socket, kernel parameters), or cost optimization with reserved instances.
- **Fargate Spot vs regular Fargate** -- Fargate Spot provides up to 70% savings but tasks can be interrupted with 2 minutes notice. Suitable for batch processing, CI/CD runners, and stateless workers behind a queue. Not suitable for long-running tasks, user-facing services without sufficient redundancy, or in-memory state that cannot be reconstructed.
- **EKS managed node groups vs Karpenter** -- Managed node groups are simpler and AWS-managed but scale slower and use ASG-based scaling. Karpenter provisions right-sized nodes directly via the EC2 fleet API, supports diverse instance types in a single pool, and scales in seconds rather than minutes. Karpenter adds operational complexity but is superior for heterogeneous or rapidly scaling workloads.
- **App Mesh vs ALB-based routing** -- App Mesh (Envoy-based service mesh) provides fine-grained traffic control, retries, circuit breaking, and mutual TLS between services. ALB-based routing is simpler and sufficient for most request/response patterns. App Mesh adds sidecar resource overhead and operational complexity.
- **Single-container vs sidecar pattern** -- Sidecars (log routers, monitoring agents, proxies) enable separation of concerns but increase resource consumption and deployment complexity. ECS supports multiple containers per task definition; EKS supports sidecar containers natively as of Kubernetes 1.28.

## Reference Architectures

### Microservices on ECS Fargate
ALB -> ECS Fargate services (one per microservice) -> service discovery via Cloud Map for inter-service calls. ECR for images with lifecycle policies. CodePipeline for CI/CD with blue/green deployments via CodeDeploy. Container Insights for monitoring. Secrets from Secrets Manager injected as environment variables via task definition.

### Kubernetes Platform on EKS
EKS cluster with managed node groups across 3 AZs (mix of on-demand and Spot for non-critical workloads). AWS Load Balancer Controller for Ingress (ALB) and Service (NLB) resources. EBS CSI driver for stateful workloads. Fluent Bit DaemonSet shipping logs to CloudWatch. Prometheus/Grafana or CloudWatch Container Insights for metrics. External Secrets Operator syncing from Secrets Manager. ArgoCD for GitOps deployments.

### Batch Processing on ECS
SQS queue -> ECS service with target tracking auto-scaling based on queue depth (ApproximateNumberOfMessagesVisible). Fargate Spot capacity provider for cost savings. DLQ for failed messages. Step Functions for multi-stage batch orchestration with Map state for parallel processing.

## Version Notes

| Feature | EKS 1.27 | EKS 1.28 | EKS 1.29 | EKS 1.30 | EKS 1.31 |
|---|---|---|---|---|---|
| Kubernetes version | 1.27 | 1.28 | 1.29 | 1.30 | 1.31 |
| Standard support end | Nov 2024 | Jan 2025 | Mar 2025 | Jul 2025 | Oct 2025 |
| Extended support | +12 months | +12 months | +12 months | +12 months | +12 months |
| Karpenter version | 0.29-0.31 | 0.32-0.33 (v1beta1 API) | 0.34-0.36 (v1beta1) | 1.0 (v1 GA API) | 1.1 |
| Sidecar containers | Not available | GA (native init containers restartPolicy) | GA | GA | GA |
| Pod Identity | Not available | GA (EKS Pod Identity) | GA | GA | GA |
| EKS Auto Mode | Not available | Not available | Not available | Not available | GA |
| Access entries (API auth) | GA | GA | GA | GA | GA |
| VPC CNI prefix delegation | GA | GA | GA | GA | GA |
| Fargate updates | Standard | Standard | ARM64 support improved | ARM64 GA | ARM64 GA |
| CoreDNS add-on | Managed | Managed | Managed (improved scaling) | Managed | Managed (auto-scaling) |
| EKS Hybrid Nodes | Not available | Not available | Not available | Not available | GA |
| GuardDuty EKS Runtime | GA | GA | GA | GA | GA |

**Key changes across EKS versions:**
- **EKS version support policy:** Each EKS version receives 14 months of standard support followed by 12 months of extended support (at additional cost). Extended support allows running older Kubernetes versions while planning upgrades but incurs per-cluster-hour charges. Plan upgrades within standard support windows to avoid costs.
- **Karpenter versions:** Karpenter 0.32+ (EKS 1.28+) introduced the v1beta1 API with NodePool and EC2NodeClass resources, replacing the v1alpha5 Provisioner API. Karpenter 1.0 (EKS 1.30) graduated to v1 GA API. Migration from v1alpha5 to v1beta1/v1 requires updating CRDs and manifest definitions. Karpenter now supports consolidation, drift detection, and expiration policies natively.
- **EKS Pod Identity:** Introduced in EKS 1.28, Pod Identity simplifies IAM role association for pods compared to IRSA (IAM Roles for Service Accounts). Pod Identity uses an EKS-managed agent rather than webhook mutation, reducing configuration complexity. Both IRSA and Pod Identity are supported; Pod Identity is recommended for new workloads.
- **Sidecar containers:** EKS 1.28 added native sidecar container support via init containers with `restartPolicy: Always`. This enables proper lifecycle management for sidecars (logging, proxies) that should start before and terminate after the main container.
- **Fargate updates:** ARM64/Graviton support for Fargate has improved across versions, with full GA support in EKS 1.30+. Fargate Spot remains available for fault-tolerant workloads.
- **EKS Auto Mode:** GA in EKS 1.31, Auto Mode automates node provisioning, scaling, and updates using AWS-managed Karpenter, eliminating the need to configure managed node groups or self-managed Karpenter.

## ECR Authentication for Non-EKS Kubernetes

EKS clusters authenticate to ECR natively via IAM instance profiles and IRSA/Pod Identity -- no additional configuration is needed for pulling images from ECR in the same account. However, K3s, kubeadm, and other self-managed Kubernetes distributions running on EC2, on-premises, or in other clouds have no built-in ECR integration. These clusters require explicit credential management because ECR tokens expire every 12 hours.

### Solution 1: ECR Credential Helper on Nodes

Install the [amazon-ecr-credential-helper](https://github.com/awslabs/amazon-ecr-credential-helper) on each node. Configure containerd or Docker to use it as a credential store. The helper automatically refreshes ECR tokens using the node's IAM role or configured AWS credentials.

- **Pros:** No Kubernetes-level configuration, works transparently for all pods on the node.
- **Cons:** Requires installation on every node, relies on node-level IAM permissions, tighter coupling between node configuration and workload requirements.
- **K3s-specific:** Configure in `/etc/rancher/k3s/registries.yaml` with the ECR endpoint as a mirror.

### Solution 2: CronJob with imagePullSecret Rotation

Deploy a Kubernetes CronJob that runs every 6-10 hours (ECR tokens expire at 12 hours) to:
1. Run `aws ecr get-login-password --region <region>`
2. Create or update a `docker-registry` Secret with the new token
3. Patch the Secret in each namespace that needs ECR access

```
CronJob (every 8h)
  → aws ecr get-login-password
  → kubectl create secret docker-registry ecr-creds --docker-server=<account>.dkr.ecr.<region>.amazonaws.com --docker-username=AWS --docker-password=<token> --dry-run=client -o yaml | kubectl apply -f -
```

- **Pros:** Pure Kubernetes solution, no node-level changes, works with any distribution.
- **Cons:** Credentials expire if the CronJob fails, must replicate Secrets across namespaces, requires RBAC for the CronJob ServiceAccount to manage Secrets.

### Solution 3: Open-Source Controllers

Purpose-built controllers that automate ECR token refresh as Kubernetes-native operators:
- **ecr-token-refresh:** Lightweight controller that watches namespaces and keeps imagePullSecrets updated.
- **aws-ecr-credential:** Operator-pattern controller with CRD-based configuration.

These controllers run as Deployments, watch for new namespaces, and automatically create/refresh ECR Secrets. They handle the CronJob approach's complexity (multi-namespace, failure recovery) with less manual configuration.

### Cross-Account ECR Access

When pulling images from a different AWS account's ECR:
1. In the **source account** (ECR owner): Add a repository policy allowing the target account's IAM role to perform `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`, and `ecr:GetAuthorizationToken`.
2. In the **target account** (K8s cluster): Configure IAM role assumption for the source account, either via node instance profile or a dedicated IAM role used by the credential refresh mechanism.
3. Use the full ECR URI including the source account ID: `<source-account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>`.

### imagePullSecrets: ServiceAccount vs Per-Pod

- **Per-pod:** Add `imagePullSecrets` to each pod spec. Explicit but requires updating every Deployment/StatefulSet manifest.
- **ServiceAccount-level:** Attach `imagePullSecrets` to a ServiceAccount and assign that ServiceAccount to pods. Any pod using the ServiceAccount automatically inherits the pull credentials. This is the recommended approach -- create an `ecr-pull` ServiceAccount in each namespace with the ECR Secret attached, and reference it in workload manifests. Reduces duplication and centralizes credential management.

### Multi-Region Active-Active
Global Accelerator -> ALBs in each region -> ECS/EKS services. ECR cross-region replication for images. DynamoDB global tables or Aurora Global Database for state. Route 53 health checks for DNS-level failover. CI/CD pipeline deploys to all regions with canary validation per region.
