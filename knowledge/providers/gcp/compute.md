# GCP Compute Engine

## Checklist

- [ ] Are Managed Instance Groups (MIGs) used for production workloads requiring auto-scaling, auto-healing, and rolling updates?
- [ ] Are instances distributed across multiple zones using regional MIGs rather than zonal MIGs for high availability?
- [ ] Is the machine type selected from the appropriate family? (general-purpose N2/N2D/C3, compute-optimized C2/C3, memory-optimized M2/M3, Tau T2D/T2A for scale-out)
- [ ] Are custom machine types used when standard types overprovision CPU or memory, to avoid paying for unused resources?
- [ ] Are preemptible VMs or Spot VMs used for fault-tolerant batch workloads, with shutdown scripts handling graceful termination?
- [ ] Is OS Login enabled for SSH access management via IAM instead of managing SSH keys on individual instances?
- [ ] Are instance templates versioned and used by MIGs, with rolling update policies configured (max surge, max unavailable)?
- [ ] Is Shielded VM enabled with Secure Boot, vTPM, and integrity monitoring for tamper-resistant instances?
- [ ] Are persistent disks using the appropriate type? (pd-balanced for general, pd-ssd for high IOPS, pd-extreme for highest performance, Hyperdisk for configurable IOPS/throughput)
- [ ] Are disk snapshots scheduled with a snapshot schedule policy and cross-region replication for disaster recovery?
- [ ] Is sole-tenant node use evaluated for workloads with licensing, compliance, or isolation requirements?
- [ ] Are Ops Agent (unified monitoring and logging agent) installed on all instances for metrics and log collection?
- [ ] Is autoscaling configured with appropriate signals (CPU utilization, Cloud Monitoring metrics, load balancer utilization)?
- [ ] Are service accounts assigned per-instance with minimal IAM roles rather than using the default Compute Engine service account?

## Why This Matters

GCP Compute Engine has unique features like custom machine types, live migration (enabled by default), and a per-second billing model that require different design thinking. The default Compute Engine service account has Editor permissions on the project, making it a significant security risk if not replaced. Preemptible VMs are up to 91% cheaper but are terminated after 24 hours. Regional MIGs spread across zones provide automatic zone-failure resilience.

## Common Decisions (ADR Triggers)

- **Machine family selection** -- general-purpose (N2/C3) vs Tau (scale-out) vs Arm-based (T2A), generation migration
- **Purchase model** -- on-demand vs Committed Use Discounts (1 or 3 year, resource-based or spend-based) vs Spot VMs
- **MIG update strategy** -- proactive (instant) vs opportunistic (on scale-out only), canary updates
- **Disk type** -- pd-balanced vs pd-ssd vs Hyperdisk, local SSD for ephemeral high-IOPS workloads
- **Image management** -- custom images vs public images, image family for latest version, organization-level image policies
- **Access model** -- OS Login vs SSH key metadata, IAP TCP tunneling vs bastion host
- **Sole-tenant nodes** -- BYOL licensing vs shared tenancy, node affinity labels
