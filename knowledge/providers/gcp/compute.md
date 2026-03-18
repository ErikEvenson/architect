# GCP Compute Engine

## Scope

Compute Engine instances (machine families, Spot VMs, sole-tenant nodes), Managed Instance Groups, persistent disks (PD, Hyperdisk), instance templates, OS Login, Shielded VM, autoscaling.

## Checklist

- [ ] [Recommended] Are Managed Instance Groups (MIGs) used for production workloads requiring auto-scaling, auto-healing, and rolling updates?
- [ ] [Recommended] Are instances distributed across multiple zones using regional MIGs rather than zonal MIGs for high availability?
- [ ] [Critical] Is the machine type selected from the appropriate family? (general-purpose N2/N2D/N4/C3/C3D, compute-optimized C2/C3/C4/C4A, memory-optimized M2/M3, Tau T2D/T2A for scale-out)
- [ ] [Recommended] Are custom machine types used when standard types overprovision CPU or memory, to avoid paying for unused resources?
- [ ] [Recommended] Are Spot VMs used for fault-tolerant batch workloads, with shutdown scripts handling graceful termination? (Spot VMs are the recommended replacement for preemptible VMs; preemptible VMs are legacy and have a 24-hour maximum runtime limit whereas Spot VMs do not)
- [ ] [Recommended] Is OS Login enabled for SSH access management via IAM instead of managing SSH keys on individual instances?
- [ ] [Recommended] Are instance templates versioned and used by MIGs, with rolling update policies configured (max surge, max unavailable)?
- [ ] [Recommended] Is Shielded VM enabled with Secure Boot, vTPM, and integrity monitoring for tamper-resistant instances?
- [ ] [Recommended] Are persistent disks using the appropriate type? (pd-balanced for general, pd-ssd for high IOPS, pd-extreme for highest performance, Hyperdisk for configurable IOPS/throughput)
- [ ] [Optional] Are disk snapshots scheduled with a snapshot schedule policy and cross-region replication for disaster recovery?
- [ ] [Optional] Is sole-tenant node use evaluated for workloads with licensing, compliance, or isolation requirements?
- [ ] [Recommended] Are Ops Agent (unified monitoring and logging agent) installed on all instances for metrics and log collection?
- [ ] [Recommended] Is autoscaling configured with appropriate signals (CPU utilization, Cloud Monitoring metrics, load balancer utilization)?
- [ ] [Critical] Are service accounts assigned per-instance with minimal IAM roles rather than using the default Compute Engine service account?

## Why This Matters

GCP Compute Engine has unique features like custom machine types, live migration (enabled by default), and a per-second billing model that require different design thinking. The default Compute Engine service account has Editor permissions on the project, making it a significant security risk if not replaced. Spot VMs provide up to 91% savings for fault-tolerant workloads and are the recommended replacement for legacy preemptible VMs (preemptible VMs have a 24-hour maximum runtime limit and are no longer the preferred option). Regional MIGs spread across zones provide automatic zone-failure resilience.

The latest machine families offer significant price-performance improvements: C4 (Intel Emerald Rapids) and C4A (Arm-based Axion) provide the best compute-optimized performance; N4 (general-purpose, Intel Emerald Rapids) offers better price-performance than N2 for most workloads. Evaluate newer families before defaulting to N2/C2.

## Common Decisions (ADR Triggers)

- **Machine family selection** -- general-purpose (N2/N4/C3) vs compute-optimized (C4/C4A) vs Tau (scale-out) vs Arm-based (T2A/C4A), generation migration for price-performance gains
- **Purchase model** -- on-demand vs Committed Use Discounts (1 or 3 year, resource-based or spend-based) vs Spot VMs (replaces preemptible)
- **MIG update strategy** -- proactive (instant) vs opportunistic (on scale-out only), canary updates
- **Disk type** -- pd-balanced vs pd-ssd vs Hyperdisk, local SSD for ephemeral high-IOPS workloads
- **Image management** -- custom images vs public images, image family for latest version, organization-level image policies
- **Access model** -- OS Login vs SSH key metadata, IAP TCP tunneling vs bastion host
- **Sole-tenant nodes** -- BYOL licensing vs shared tenancy, node affinity labels

## Reference Architectures

- [Google Cloud Architecture Center: Compute](https://cloud.google.com/architecture#compute) -- reference architectures for Compute Engine, MIGs, and autoscaling patterns
- [Google Cloud Architecture Framework: System design - Compute](https://cloud.google.com/architecture/framework/system-design/compute) -- best practices for machine type selection, scaling, and availability
- [Google Cloud: Building scalable and resilient web applications on Compute Engine](https://cloud.google.com/architecture/scalable-and-resilient-apps) -- reference design for auto-scaling multi-tier applications
- [Google Cloud: Best practices for Compute Engine](https://cloud.google.com/compute/docs/instances) -- official best practices for instance management, images, and disk configuration
- [Google Cloud: Migrating VMs to Compute Engine](https://cloud.google.com/architecture/migration-to-gcp-getting-started) -- reference architecture for VM migration and modernization patterns

## See Also

- `general/compute.md` -- general compute architecture patterns
- `providers/gcp/containers.md` -- GKE and Cloud Run container compute
- `providers/gcp/serverless.md` -- GCP serverless compute options
- `providers/gcp/networking.md` -- VPC, load balancing, and network configuration
