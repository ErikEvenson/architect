# OpenShift Infrastructure

## Checklist

- [ ] Choose between OCP (Red Hat OpenShift Container Platform) and OKD (community upstream)
- [ ] Select deployment model: IPI (Installer-Provisioned Infrastructure) vs UPI (User-Provisioned Infrastructure)
- [ ] Determine target platform (bare metal, vSphere, AWS, Azure, GCP, RHV/OpenStack, IBM Power/Z)
- [ ] Size control plane nodes (minimum 3 for HA; 8 vCPU / 16 GB RAM recommended for production)
- [ ] Plan worker node capacity based on workload projections and resource overhead
- [ ] Decide whether to use dedicated infrastructure nodes for routers, registry, and monitoring
- [ ] Configure RHCOS (Red Hat CoreOS) as the immutable node OS managed via Ignition configs
- [ ] Set up Machine API with MachineSets per availability zone or failure domain
- [ ] Define MachineHealthChecks to auto-remediate unhealthy nodes
- [ ] Configure cluster autoscaler with min/max node boundaries and scale-down policies
- [ ] Select upgrade channel (stable, fast, candidate, eus) aligned with change management policy
- [ ] Plan OpenShift lifecycle: minor version support windows, EUS (Extended Update Support) eligibility
- [ ] Establish day-2 operations procedures: certificate rotation, etcd defragmentation, node draining
- [ ] Define cluster topology: single cluster, hub-spoke with RHACM, or fleet management model

## Why This Matters

OpenShift is an opinionated Kubernetes distribution that bundles operators, security defaults, and lifecycle tooling. Choosing the wrong deployment model or sizing can lock teams into expensive rework. IPI automates infrastructure provisioning (Terraform-like) but limits customization; UPI gives full control but requires maintaining Ignition configs, load balancers, and DNS manually. RHCOS is not optional for control plane nodes -- it is tightly coupled to the Machine Config Operator (MCO) for in-place OS updates. Cluster sizing errors compound: undersized control planes lead to etcd latency and API server timeouts under load; missing infrastructure nodes cause router and monitoring pods to compete with application workloads.

The Machine API (`machine.openshift.io/v1beta1`) provides declarative node lifecycle management. MachineSets define desired replica counts per zone, and the cluster autoscaler adjusts them based on pending pod pressure. Without MachineHealthChecks, failed nodes remain in the cluster, consuming capacity and triggering alert fatigue.

Upgrade channels control the pace of updates. The `stable` channel lags behind `fast` by weeks to allow community soak time. EUS channels (available on even-numbered minor releases like 4.14, 4.16) allow skipping intermediate minor versions, reducing upgrade frequency for regulated environments.

## Common Decisions (ADR Triggers)

- **IPI vs UPI deployment**: IPI is faster to stand up but may conflict with enterprise network/firewall requirements (e.g., proxy, air-gapped). UPI is required for disconnected/air-gapped installs and non-standard network topologies.
- **Dedicated infrastructure nodes**: Running router, registry, and monitoring on infra-labeled nodes avoids Red Hat subscription costs for those workloads and isolates platform services from tenant applications.
- **Single large cluster vs multiple smaller clusters**: Blast radius, tenancy model, compliance boundaries, and team autonomy all factor in. RHACM can manage fleet topology but adds operational complexity.
- **Upgrade cadence**: Staying on a single EUS release reduces upgrade overhead but delays access to new features and security fixes. Fast channel suits dev/test; stable suits production.
- **Bare metal vs virtualized vs cloud**: Bare metal with IPI requires a provisioning network and IPMI/BMC access. vSphere IPI requires specific privilege sets. Cloud IPI is simplest but may conflict with enterprise landing zone patterns.

## Version Notes

| Feature | OCP 4.12 | OCP 4.14 (EUS) | OCP 4.16 (EUS) |
|---|---|---|---|
| RHCOS base | RHEL 8.6 | RHEL 9.2 | RHEL 9.4 |
| Kubernetes version | 1.25 | 1.27 | 1.29 |
| CRI-O version | 1.25 | 1.27 | 1.29 |
| Machine API | GA | GA (improved health checks) | GA (Machine API v2 preview) |
| Cluster Autoscaler | GA | GA | GA (improved scale-down) |
| EUS channel | Not available | Available | Available |
| Update path (EUS-to-EUS) | N/A | 4.12 -> 4.14 (direct) | 4.14 -> 4.16 (direct) |
| Platform Monitoring Stack | Prometheus + Thanos | Prometheus + Thanos | Prometheus + Thanos (improved retention) |
| OLM v1 | Not available | Not available | Tech Preview |
| Agent-based installer | Tech Preview | GA | GA |
| Single Node OpenShift (SNO) | GA | GA | GA |

**Key changes across versions:**
- **RHCOS rebasing to RHEL 9:** OCP 4.14 rebased RHCOS from RHEL 8 to RHEL 9, bringing kernel 5.14+, updated systemd, and new default crypto policies. This is a significant change for customers relying on RHEL 8-specific kernel modules or configurations.
- **Machine API improvements:** OCP 4.14 improved MachineHealthCheck responsiveness and added better reporting. OCP 4.16 introduced early previews of Machine API v2 with a clearer separation between infrastructure and machine lifecycle.
- **EUS upgrade paths:** Even-numbered minor releases (4.14, 4.16) are eligible for Extended Update Support (18 months). EUS-to-EUS upgrades allow skipping odd-numbered releases (e.g., 4.14 directly to 4.16), reducing upgrade frequency for regulated environments. EUS requires a separate subscription.
- **Agent-based installer:** Reached GA in 4.14, enabling disconnected and bare-metal installations without a bootstrap node by embedding the installation payload into an ISO.
- **OLM v1:** Tech Preview in 4.16 introduces a new operator lifecycle model with better dependency resolution, simpler packaging, and support for non-operator content.

## Reference Architectures

- **Red Hat Reference Architecture -- OpenShift on AWS**: 3 control plane (m5.2xlarge), 3+ worker (m5.4xlarge), 3 infra nodes, cross-AZ spread, EBS gp3 for etcd, ALB for ingress, Route 53 for DNS.
- **Red Hat Reference Architecture -- OpenShift on vSphere**: 3 control plane VMs (8 vCPU / 32 GB / 120 GB disk), DRS anti-affinity rules, vSphere CSI driver for dynamic PV provisioning, NSX-T or standard vSwitch networking.
- **Red Hat Reference Architecture -- OpenShift on Bare Metal**: 3 control plane + 2 worker minimum, provisioning network for PXE/IPMI, MetalLB for ingress VIPs, local storage operator or ODF for persistent storage.
- **Disconnected/Air-Gapped**: Mirror registry (oc-mirror or Quay), ICSP/IDMS for image content source policies, update graph served locally, catalog sources for operator mirroring.
- **Edge -- Single Node OpenShift (SNO)**: All-in-one topology for edge/remote sites, minimum 8 vCPU / 32 GB RAM, managed centrally via RHACM and zero-touch provisioning (ZTP).
