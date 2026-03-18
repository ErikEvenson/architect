# Compute

## Scope

Compute platform selection, sizing, scaling, placement, and lifecycle management for all workload types. This file covers **what** compute decisions need to be made and the trade-offs involved. For provider-specific **how**, see the provider compute files. Applies to all deployment models: public cloud IaaS/PaaS, on-premises virtualization, bare metal, and hybrid.

## Checklist

- [ ] **[Critical]** What compute platform does each workload require? (VMs for lift-and-shift or OS-level control; containers/Kubernetes for microservices density and portability; serverless/FaaS for event-driven and intermittent workloads; bare metal for license-bound, latency-sensitive, or GPU-direct workloads — most architectures use a mix, so classify each workload tier separately)
- [ ] **[Critical]** What instance or VM sizing methodology is used? (right-sizing from observed metrics vs. vendor reference architectures vs. developer estimates — developer estimates typically over-provision 3-5x; use cloud provider tools like AWS Compute Optimizer, Azure Advisor, or on-prem capacity data to establish baselines before selecting instance families)
- [ ] **[Critical]** How are compute resources distributed across failure domains for high availability? (across availability zones within a region, across racks in on-prem, or across regions for DR — minimum 2 AZs for HA, 3 preferred; consider anti-affinity rules to prevent co-location on the same hypervisor host; cross-region adds latency and data replication complexity)
- [ ] **[Critical]** How is OS patching and lifecycle management handled? (in-place patching with scheduled maintenance windows vs. immutable image replacement via golden AMI/template pipeline — in-place is simpler but creates configuration drift; immutable requires CI/CD pipeline for image builds but guarantees consistency; plan for end-of-life OS migration 12-18 months before vendor EOL)
- [ ] **[Critical]** Is the application stateless or stateful, and how does that affect compute design? (stateless enables simple horizontal scaling and immutable replacement; stateful requires external session stores like Redis/Memcached, sticky sessions at the load balancer, or persistent local storage — sticky sessions limit scaling flexibility and complicate rolling deployments)
- [ ] **[Recommended]** What autoscaling strategy is appropriate for each workload? (target tracking on CPU/memory for steady growth; step scaling for bursty traffic with defined thresholds; scheduled scaling for predictable patterns like business hours; Kubernetes HPA with custom metrics for container workloads; KEDA for event-driven scaling from queue depth — set scale-in cooldowns to prevent flapping, typically 5-10 minutes)
- [ ] **[Recommended]** What are the minimum, desired, and maximum instance counts, and how are they determined? (minimum must satisfy HA requirements across failure domains — e.g., 2 minimum across 2 AZs; maximum must account for downstream dependency limits such as database connection pools, license counts, and API rate limits; over-provisioning the maximum wastes spend, under-provisioning causes outages during traffic spikes)
- [ ] **[Recommended]** What instance family or class best fits the workload profile? (general-purpose for balanced CPU/memory; compute-optimized for CPU-bound batch, encoding, or scientific workloads; memory-optimized for in-memory databases, caches, and large JVM heaps; storage-optimized for data-intensive workloads with high IOPS requirements; burstable for dev/test and low-utilization workloads — burstable instances throttle when CPU credits are exhausted, causing unpredictable latency in production)
- [ ] **[Recommended]** Can spot, preemptible, or interruptible instances reduce cost for fault-tolerant workloads? (spot instances are 60-90% cheaper but can be reclaimed with 2-minute notice; suitable for batch processing, CI/CD runners, stateless workers, and data pipelines; not suitable for databases, single-instance workloads, or anything requiring graceful long-running shutdown; use diversified instance pools and capacity-optimized allocation to reduce interruption rates)
- [ ] **[Recommended]** Is reserved capacity or a savings plan needed for baseline workloads? (1-year or 3-year reservations offer 30-60% discount over on-demand; convertible reservations allow instance family changes at a smaller discount; savings plans provide flexibility across instance types and regions — commit only to the baseline that runs 24/7, use on-demand or spot for variable load above the baseline; on-prem equivalent is hardware procurement planning with 3-5 year refresh cycles)
- [ ] **[Recommended]** Are placement groups, affinity rules, or topology constraints required? (cluster placement for low-latency inter-node communication like HPC and distributed databases; spread placement to minimize correlated hardware failure for HA; partition placement for large distributed workloads like HDFS and Cassandra; on-prem DRS affinity/anti-affinity rules for similar purposes; over-constraining placement limits scheduling flexibility and can cause launch failures)
- [ ] **[Optional]** Are GPU, FPGA, or other accelerator workloads in scope? (GPU instance families for ML training/inference, video transcoding, and scientific simulation; GPU scheduling in Kubernetes requires device plugins and node selectors; consider GPU sharing via MIG or time-slicing for inference workloads that do not saturate a full GPU; GPU instances are 5-20x the cost of general-purpose — validate that the workload actually benefits from GPU acceleration before committing)
- [ ] **[Optional]** What container orchestration platform is used, and how are the worker nodes sized? (managed Kubernetes — EKS, AKS, GKE — vs. self-managed vs. lightweight alternatives like Nomad or ECS; node sizing must account for system overhead — kubelet, kube-proxy, OS — which consumes 10-15% of node resources; fewer large nodes reduce scheduling overhead and improve bin-packing, more small nodes improve fault isolation; node auto-scaling via Cluster Autoscaler or Karpenter adds nodes when pods are unschedulable)

## Why This Matters

Compute is the foundation of the application tier and typically the largest line item in cloud spend. Incorrect sizing leads to either wasted budget — studies consistently show 30-40% of cloud compute spend is on idle or underutilized resources — or performance degradation during peak load. Getting compute decisions wrong at the architecture phase is costly to fix later: migrating from VMs to containers, re-architecting from stateful to stateless, or changing instance families requires application changes, not just infrastructure changes.

High availability depends on compute placement decisions made at design time. Deploying all instances in a single availability zone or on a single hypervisor host creates a single point of failure that no amount of application-level resilience can compensate for. Similarly, autoscaling that is designed reactively — after the first outage — is always playing catch-up, because scaling policies need to account for instance launch time, application warm-up, and downstream dependency readiness.

OS lifecycle management is the most frequently deferred compute decision and the most dangerous to ignore. Unpatched operating systems are the primary attack vector in most breaches, yet many organizations treat patching as an operational task rather than an architectural decision. The choice between in-place patching and immutable image replacement has profound implications for CI/CD pipeline design, deployment velocity, and incident response capability.

## Common Decisions (ADR Triggers)

### ADR: Compute Platform Selection

**Context:** The architecture must support the application's performance, availability, and operational requirements while aligning with team skills and cost targets.

**Options:**

| Criterion | Virtual Machines | Containers (Kubernetes) | Serverless (FaaS) | Bare Metal |
|---|---|---|---|---|
| Workload fit | Monoliths, legacy apps, OS-dependent software | Microservices, 12-factor apps, polyglot stacks | Event-driven, intermittent, API backends | License-bound (Oracle per-core), HPC, GPU-direct |
| Density | 1 app per VM typical (lower density) | 10-50 containers per node (highest density) | Managed by provider (no capacity planning) | 1 workload per server (lowest density) |
| Scaling speed | Minutes (VM boot + app start) | Seconds (container start) | Milliseconds (cold start 100ms-10s depending on runtime) | N/A (manual provisioning) |
| Operational overhead | OS patching, antivirus, monitoring agents | Cluster management, networking (CNI), upgrades | Minimal (vendor-managed runtime) | Full hardware lifecycle: firmware, BIOS, RAID, OS |
| Cost model | Per-hour/second, reserved instances available | Node cost + cluster overhead (control plane, monitoring) | Per-invocation + duration, zero cost at idle | CapEx hardware + data center costs, or cloud bare metal premium |
| Portability | OVA/VMDK export, limited portability | High — container images run anywhere with K8s | Low — vendor-specific runtimes and triggers | N/A |

**Decision drivers:** Application architecture (monolith vs. microservices), team Kubernetes expertise, cold start tolerance, cost at scale, and compliance requirements (some regulations require dedicated hardware).

### ADR: Autoscaling Strategy

**Context:** The application experiences variable load and must scale automatically to maintain performance SLAs without over-provisioning.

**Options:**
- **Target tracking:** Maintains a metric (CPU, request count) at a target value. Simplest to configure, works well for gradual load changes. Reacts slowly to spikes.
- **Step scaling:** Defines thresholds with corresponding scale-out increments (e.g., CPU > 70% add 2, > 85% add 4). Better for bursty traffic with known patterns. More complex to tune.
- **Scheduled scaling:** Pre-scales at known times (business hours, batch windows, campaign launches). Predictable and cost-efficient when patterns are stable. Does not handle unexpected traffic.
- **Predictive scaling:** Uses ML to forecast load and pre-provision capacity. Combines scheduled and reactive approaches. Available in AWS ASG and some Kubernetes solutions. Requires historical data to be accurate.
- **Event-driven (KEDA):** Scales from zero based on external metrics (SQS queue depth, Kafka lag, cron schedules). Ideal for async processing workloads. Requires metric adapter configuration.

**Decision drivers:** Traffic pattern predictability, acceptable response time during scale-out (including instance boot + application warm-up), cost tolerance for pre-provisioned headroom, and complexity budget.

### ADR: OS Patching Strategy

**Context:** The organization must keep operating systems patched for security compliance while minimizing application downtime.

**Options:**
- **In-place patching with maintenance windows:** Patch running instances during scheduled windows. Simple, requires reboot scheduling. Creates drift over time as instances accumulate unique patch histories. Tools: AWS SSM Patch Manager, WSUS, Ansible.
- **Immutable image replacement:** Build new golden images (AMI, VM template) via CI/CD pipeline, replace instances via rolling deployment. No drift, fully reproducible. Requires image pipeline investment and longer deployment time. Tools: Packer, EC2 Image Builder, Azure Image Builder.
- **Container base image updates:** Rebuild container images with updated base images, redeploy via Kubernetes rolling update. Fastest patch cycle, but only patches the container OS — host node OS requires separate patching via node rotation (EKS managed node group updates, GKE auto-upgrade).

**Recommendation:** Use immutable image replacement for production workloads and container base image updates for Kubernetes. Reserve in-place patching for legacy workloads that cannot be rebuilt from automation. Regardless of strategy, scan images with vulnerability scanners (Trivy, Qualys, Nessus) before deployment.

### ADR: Spot/Preemptible Instance Strategy

**Context:** The organization wants to reduce compute costs for workloads that can tolerate interruption.

**Options:**
- **No spot usage:** All on-demand or reserved. Highest cost, zero interruption risk. Appropriate for databases, stateful services, and SLA-bound workloads.
- **Spot for batch/CI only:** Use spot instances for batch processing, CI/CD runners, and data pipelines. Moderate savings with contained blast radius. Most common starting point.
- **Spot for stateless production:** Run stateless web/API tiers on spot with on-demand fallback. Highest savings (60-90%), requires robust health checks, graceful shutdown handlers, and diversified instance pools. Risk: simultaneous reclamation during capacity crunches.
- **Mixed fleet (spot + on-demand baseline):** Run the minimum required capacity on on-demand/reserved, burst with spot. Balanced cost and reliability. Requires capacity-aware load balancing.

**Decision drivers:** Workload fault tolerance, acceptable interruption frequency, instance type availability in the target region/AZ, and team readiness to handle spot interruption signals.

## See Also

- `providers/aws/ec2-asg.md` — AWS EC2 instances and Auto Scaling Groups
- `providers/azure/compute.md` — Azure VMs and Scale Sets
- `providers/gcp/compute.md` — GCP Compute Engine and instance groups
- `general/containers.md` — Container orchestration and Kubernetes design decisions
- `general/cost-optimization.md` — Cloud cost management strategies including compute right-sizing
