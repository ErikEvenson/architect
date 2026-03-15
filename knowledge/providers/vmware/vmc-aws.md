# VMware Cloud on AWS (VMC on AWS)

VMware-managed SDDC running on dedicated AWS bare-metal infrastructure. Provides full VMware stack (vSphere, vSAN, NSX, vCenter) on AWS with native AWS service integration.

## Checklist

- [ ] **[Critical]** SDDC size: single-host (dev/test only, no SLA) vs. multi-host (production, minimum 2 hosts)?
- [ ] **[Critical]** Host type selection: i3.metal (36 vCPU, 512GB RAM, 15.2TB NVMe), i3en.metal (larger storage), or i4i.metal (latest gen)?
- [ ] **[Critical]** Stretched cluster (multi-AZ) for HA, or single-AZ SDDC? Stretched clusters require minimum 6 hosts (3 per AZ + 2 witness).
- [ ] **[Critical]** Networking connectivity: linked VPC for AWS service access, Transit Connect for multi-VPC, Direct Connect for on-prem?
- [ ] **[Critical]** Migration strategy: HCX bulk migration, live vMotion, or replication-assisted vMotion from on-prem?
- [ ] **[Critical]** Pricing model: on-demand (per-host hourly) or 1yr/3yr subscription (significant discount)?
- [ ] **[Recommended]** vSAN storage policy: dedup+compression enabled, FTT level (failures to tolerate), RAID-1 vs. RAID-5/6?
- [ ] **[Recommended]** Elastic vSAN (disaggregated storage) for workloads needing more storage than compute?
- [ ] **[Recommended]** Elastic DRS configuration: auto-scale hosts based on utilization thresholds, min/max host count?
- [ ] **[Recommended]** NSX overlay network design: segments, firewall rules, NAT, VPN between SDDC and on-prem?
- [ ] **[Recommended]** AWS service integration plan: which AWS services (RDS, S3, Lambda, ELB) will VMware VMs consume via linked VPC?
- [ ] **[Recommended]** Add-ons needed: SRM for DR, Tanzu for Kubernetes, VMware Aria for operations?
- [ ] **[Optional]** Content library configuration for VM templates and ISOs across SDDCs?
- [ ] **[Optional]** Multi-SDDC or SDDC group topology for large deployments with shared networking?
- [ ] **[Optional]** Hybrid Linked Mode to manage on-prem vCenter and VMC vCenter from single pane?

## Why This Matters

VMC on AWS eliminates physical infrastructure management while preserving VMware operational familiarity. Misconfigurations are expensive: a single i3.metal host costs ~$8-9/hour on-demand. Choosing single-host dev SDDCs for production workloads means no vSAN redundancy and no SLA. Not using Direct Connect for high-throughput on-prem connectivity leads to unpredictable latency over public internet. Failing to right-size host count wastes significant budget since you pay per-host regardless of VM utilization.

## Common Decisions (ADR Triggers)

| Decision | When to Create ADR |
|----------|-------------------|
| Single-AZ vs. stretched cluster | Always — defines HA posture and cost (stretched doubles minimum hosts) |
| Host type selection | Always — determines compute/storage ratio and per-host cost |
| On-demand vs. subscription pricing | Always — 1yr saves ~30%, 3yr saves ~50%, but commits capacity |
| Linked VPC vs. Transit Connect | When VMs need AWS services — linked VPC is simpler, Transit Connect scales to multi-VPC |
| HCX migration approach | When migrating from on-prem — bulk vs. vMotion affects downtime windows |
| Elastic DRS enablement | When workloads have variable demand — auto-scaling hosts affects cost predictability |
| SRM vs. native AWS DR | When DR is required — SRM preserves VMware DR runbooks, AWS-native requires redesign |
| Elastic vSAN adoption | When storage/compute ratio is imbalanced — disaggregated storage adds flexibility but complexity |

## Reference Architectures

- **DC Extension**: on-prem vSphere + VMC SDDC connected via Direct Connect + HCX, stretched L2 networking for seamless migration
- **DR Landing Zone**: on-prem primary site, VMC as DR target using SRM, pilot-light or warm-standby hosts scaled up during failover
- **Migration Factory**: VMC as landing zone for large-scale DC migration, HCX bulk migration waves, post-migration optimization with Elastic DRS
- **Hybrid Application**: VMware VMs for stateful workloads + AWS-native services (RDS, S3, Lambda) via linked VPC for new microservices
- **Dev/Test in Cloud**: single-host SDDCs for non-production, multi-host production SDDC, separate SDDCs per environment

## Key Constraints

- VMware manages ESXi hosts — no custom ESXi images or direct host access
- Minimum 2 hosts for production SLA; single-host is dev/test only with no redundancy
- SDDC is in a dedicated AWS account managed by VMware; linked VPC connects to your account
- vCenter, NSX Manager, HCX Manager consume resources on management hosts
- Host scaling is not instant — adding hosts takes 15-20 minutes
- All VMware licensing (vSphere, vSAN, NSX, vCenter) included in per-host price
