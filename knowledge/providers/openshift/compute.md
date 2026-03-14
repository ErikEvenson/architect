# OpenShift Compute

## Checklist

- [ ] Define worker node instance types or VM sizes per workload class (general, memory-optimized, compute-optimized, GPU)
- [ ] Create MachineSets per availability zone with appropriate labels and taints
- [ ] Configure MachineConfigPools (master, worker, custom) for OS-level configuration (kernel args, sysctls, chrony)
- [ ] Apply node labels for workload placement (e.g., `node-role.kubernetes.io/infra`, app-tier labels)
- [ ] Define taints and tolerations for dedicated node pools (GPU, high-memory, compliance-sensitive)
- [ ] Set pod resource requests and limits for all workloads; enforce via LimitRanges and ResourceQuotas per namespace
- [ ] Configure Horizontal Pod Autoscaler (HPA) with CPU/memory or custom metrics from Prometheus
- [ ] Evaluate Vertical Pod Autoscaler (VPA) for workloads with unpredictable resource patterns
- [ ] Set cluster autoscaler boundaries (min/max replicas per MachineSet, scale-down delay, expendable pods)
- [ ] Plan node overcommit ratios: set `ClusterResourceOverride` admission webhook for CPU/memory overcommit
- [ ] Provision infrastructure nodes and move router, registry, monitoring, and logging pods to them
- [ ] Install NVIDIA GPU Operator and Node Feature Discovery (NFD) operator for ML/AI workloads
- [ ] Configure pod topology spread constraints for HA across zones and failure domains
- [ ] Define pod disruption budgets (PDBs) for critical workloads to protect during node drains and upgrades

## Why This Matters

Compute is the largest ongoing cost in an OpenShift cluster. Worker node sizing directly impacts application density, performance, and upgrade velocity (larger nodes mean fewer nodes to drain during rolling updates, but higher blast radius per node failure). MachineSets are the declarative primitive for node pools -- each MachineSet maps to a specific instance type, zone, and label/taint combination.

MachineConfigPools (MCPs) control how the Machine Config Operator (MCO) applies OS-level changes. The default `worker` and `master` pools cover most cases, but custom MCPs (e.g., `infra`, `gpu-workers`) allow rolling out kernel parameters or container runtime changes to subsets of nodes without affecting the entire fleet. MCP updates trigger node cordoning, draining, and rebooting -- a poorly planned MCP change can cascade into a cluster-wide outage.

Resource requests and limits are the foundation of scheduling. Without requests, the scheduler cannot bin-pack effectively; without limits, a single pod can consume an entire node. The `ClusterResourceOverride` admission controller can automatically apply overcommit ratios (e.g., set limits to 2x requests) to improve density while accepting controlled risk.

Infrastructure nodes are a cost optimization lever: workloads running on nodes labeled `node-role.kubernetes.io/infra` do not count toward OpenShift subscription entitlements. Moving the default router (HAProxy), internal registry, Prometheus monitoring stack, and logging stack to infra nodes can materially reduce licensing costs.

## Common Decisions (ADR Triggers)

- **Node sizing strategy**: Fewer large nodes (e.g., 32 vCPU / 128 GB) vs many small nodes (e.g., 8 vCPU / 32 GB). Larger nodes improve density and reduce overhead but increase blast radius. Smaller nodes give finer scaling granularity.
- **Overcommit policy**: Conservative (1:1 requests-to-limits) vs aggressive (4:1 CPU overcommit, 2:1 memory). Overcommit improves cost efficiency but risks noisy-neighbor performance issues and OOMKills.
- **Autoscaling approach**: Cluster autoscaler (add/remove nodes) vs HPA (add/remove pods) vs VPA (resize pods). Most production workloads use HPA + cluster autoscaler. VPA is useful for batch jobs and workloads with unpredictable memory profiles.
- **Infrastructure node strategy**: Dedicated infra MachineSets vs co-located on worker nodes. Dedicated infra nodes are recommended for production to isolate platform services and reduce subscription costs.
- **GPU workload isolation**: Dedicated GPU node pool with taints (e.g., `nvidia.com/gpu=present:NoSchedule`) vs shared GPU time-slicing. The NVIDIA GPU Operator manages driver installation, device plugins, and MIG (Multi-Instance GPU) partitioning.
- **Custom MachineConfigPool creation**: When to create separate MCPs for specialized node groups (e.g., real-time kernel for telco, FIPS-enabled nodes for compliance).

## Reference Architectures

- **General-purpose production cluster**: 3 control plane (8 vCPU / 32 GB), 3 infra (8 vCPU / 32 GB), 6+ worker (16 vCPU / 64 GB), cluster autoscaler with min=6 max=20 workers.
- **ML/AI platform on OpenShift**: GPU worker pool (NVIDIA A100/H100), NFD operator for GPU feature detection, NVIDIA GPU Operator for driver lifecycle, Kubeflow or Open Data Hub for ML pipelines, VPA for training jobs.
- **Multi-tenant SaaS**: Multiple worker pools with taints per tenant tier (dedicated, shared), ResourceQuotas per namespace, LimitRanges for default requests/limits, HPA per application, topology spread constraints across zones.
- **Telco / NFV workload**: Real-time kernel via custom MCP and `performance-addon-operator` (now PAO merged into NTO -- Node Tuning Operator), CPU pinning, NUMA-aware scheduling, hugepages configuration, DPDK support.
- **Cost-optimized dev/test**: Aggressive overcommit (4:1 CPU), no infra nodes, smaller instance types, scale-to-zero with KEDA operator, single-zone deployment.
