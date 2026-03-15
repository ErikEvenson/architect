# VMware / Broadcom Licensing (Post-2024)

## Checklist

- [ ] **[Critical]** Has the licensing model been confirmed as VCF (full stack) or VVF (vSphere only), and does the selected edition include all required components — particularly vSAN, NSX, and Aria — or will third-party alternatives be needed to fill gaps?
- [ ] **[Critical]** Is per-core licensing impact calculated for all target server hardware, using the formula: (number of CPUs × cores per CPU × per-core price), with the 16-core minimum per CPU applied even if the physical CPU has fewer cores?
- [ ] **[Critical]** Has the transition plan from perpetual licenses (if applicable) been documented, including support renewal deadlines, subscription start dates, and budget impact of moving from CapEx (perpetual) to OpEx (subscription)?
- [ ] **[Critical]** Has a Broadcom-authorized partner been identified for quoting, since VMware licensing is no longer available through all resellers and pricing is not publicly listed?
- [ ] **[Critical]** Are CPU core counts factored into hardware selection decisions — evaluating whether fewer high-core-count servers (higher license cost, fewer servers to manage) or more lower-core-count servers (lower license cost, more physical infrastructure) optimizes total cost of ownership?
- [ ] **[Recommended]** Has a VCF vs VVF feature comparison been performed against actual requirements, since VCF includes vSAN (eliminating external SAN/NAS licensing), NSX (eliminating physical east-west firewall licensing), and Aria (eliminating third-party monitoring/automation licensing)?
- [ ] **[Recommended]** Is the total cost of ownership (TCO) analysis comparing VMware subscription against alternatives (Nutanix, Proxmox, OpenStack, Azure Stack HCI) documented as an ADR, including migration costs, retraining, and ecosystem tool compatibility?
- [ ] **[Recommended]** Are support tier requirements defined — Production support (24/7, 4-hour response for Sev 1) vs Basic support (12×5, next business day) — and is the cost delta justified by workload criticality?
- [ ] **[Recommended]** Is license compliance monitoring in place to detect core count changes when hosts are added, CPUs are upgraded, or VMs are migrated to hosts with different core counts?
- [ ] **[Recommended]** Are VCF-included components (vSAN, NSX, Aria, Tanzu, HCX) being actively used, since the licensing cost includes them regardless — unused included components represent unrealized value?
- [ ] **[Optional]** Has Broadcom's partner program change impact been assessed — specifically whether your existing VMware partner is still authorized and whether alternative partners offer better pricing or support?
- [ ] **[Optional]** Is a license optimization review scheduled annually to right-size core counts, retire unused hosts, and evaluate whether workload consolidation can reduce the licensed core footprint?
- [ ] **[Optional]** Has VMware Explore (formerly VMworld) or Broadcom partner briefing intelligence been gathered on upcoming licensing changes, since Broadcom has made multiple adjustments since the initial 2024 restructure?

## Why This Matters

Broadcom's 2024 acquisition of VMware fundamentally changed the licensing model from per-socket perpetual licenses to per-core subscriptions, and consolidated dozens of individual products into two primary bundles: VCF and VVF. This has significant financial and architectural implications. An organization running 4 dual-socket servers with 32-core CPUs (256 total cores) under the old model paid for 8 socket licenses regardless of core count. Under the new model, they pay for 256 cores annually. For high-core-count CPUs (64+ cores per socket), the licensing cost increase can be 3-5x compared to the old per-socket model. This directly impacts hardware selection: a server with two 64-core AMD EPYC CPUs (128 cores) costs significantly more in VMware licensing than two 32-core CPUs (64 cores), even though the hardware price difference may be modest. The elimination of perpetual licenses means organizations can no longer capitalize VMware as a one-time purchase — it becomes a recurring operational expense that must be budgeted annually. VCF bundles vSAN, NSX, Aria, Tanzu, and HCX into a single subscription, which can be cost-effective if all components are used but represents overspend if the organization only needs basic vSphere compute. VVF provides a lower-cost option for organizations that use external storage (SAN/NAS) and do not need NSX or Aria, but it lacks the validated-design lifecycle management that SDDC Manager provides. Broadcom also reduced the number of authorized partners, so organizations may need to find new procurement channels. Pricing is not publicly available and varies significantly by partner, volume, and negotiation — budget planning requires actual quotes rather than list price calculations.

## Common Decisions (ADR Triggers)

- **VCF vs VVF** — VCF for environments needing vSAN (hyper-converged, no external SAN), NSX (microsegmentation, load balancing), and Aria (monitoring, automation) vs VVF for environments with existing SAN/NAS investment, physical firewalls, and third-party monitoring that only need vSphere compute and vCenter management
- **VMware vs alternative hypervisors** — VMware for ecosystem maturity, enterprise support, existing team skills, and application vendor support certifications vs Nutanix (comparable HCI with different licensing), Proxmox (open-source, dramatically lower cost, limited enterprise support), OpenStack (open-source, significant operational overhead), or Azure Stack HCI (Microsoft ecosystem integration); migration costs and retraining often exceed 2-3 years of licensing savings
- **High-core vs low-core CPU selection** — fewer servers with high-core CPUs for maximum consolidation ratio and reduced physical infrastructure vs more servers with lower-core CPUs to minimize per-core licensing cost; the breakeven depends on per-core license price, server hardware cost, rack space cost, power/cooling cost, and management overhead per server
- **Production vs Basic support** — Production support (24/7, 4-hour Sev 1 response) for business-critical workloads where downtime has significant financial impact vs Basic support (12×5, next business day) for development, test, or non-critical workloads; many organizations mix tiers across environments
- **Annual vs multi-year subscription** — annual subscription for flexibility to change platforms or reduce footprint vs multi-year commitment (typically 3 years) for discounted per-core pricing; multi-year locks in spend but may include price protection against future increases
- **Use VCF-included components vs existing third-party tools** — adopt vSAN/NSX/Aria since they are included in VCF licensing (reduces third-party tool spend, simplifies stack) vs retain existing SAN/firewall/monitoring investments to avoid migration risk, retraining, and operational disruption; often a phased transition over 2-3 renewal cycles

## Reference Architectures

### VMware Edition Comparison (Post-2024)

```
┌──────────────────────┬──────────────────────┬──────────────────────┐
│                      │        VVF           │        VCF           │
│      Component       │  vSphere Foundation  │  Cloud Foundation    │
├──────────────────────┼──────────────────────┼──────────────────────┤
│ ESXi Hypervisor      │         ✓            │         ✓            │
│ vCenter Server       │         ✓            │         ✓            │
│ vSphere Lifecycle Mgr│         ✓            │         ✓            │
│ vSAN                 │         ✗            │         ✓            │
│ NSX Networking       │         ✗            │         ✓            │
│ NSX Firewall (DFW)   │         ✗            │         ✓            │
│ SDDC Manager         │         ✗            │         ✓            │
│ Aria Operations      │         ✗            │         ✓            │
│ Aria Automation      │         ✗            │         ✓            │
│ Aria Operations Logs │         ✗            │         ✓            │
│ Tanzu (Kubernetes)   │         ✗            │         ✓            │
│ HCX (Migration)      │         ✗            │         ✓            │
├──────────────────────┼──────────────────────┼──────────────────────┤
│ Pricing Model        │  Per core/year       │  Per core/year       │
│ Minimum Cores/CPU    │       16             │       16             │
│ Lifecycle Management │  Manual / vLCM       │  SDDC Manager        │
│ Validated Design     │  No (flexible)       │  Yes (enforced)      │
└──────────────────────┴──────────────────────┴──────────────────────┘
```

### Per-Core Licensing Cost Impact — Hardware Selection

```
Scenario A: High-Core Consolidation
  2 servers × 2 CPUs × 64 cores = 256 licensed cores
  Hardware: ~$30K × 2 = $60K
  VMware:   256 cores × $price/core/year
  Servers to manage: 2
  Rack units: 2-4U

Scenario B: Lower-Core, More Servers
  4 servers × 2 CPUs × 32 cores = 256 licensed cores  (same!)
  Hardware: ~$20K × 4 = $80K
  VMware:   256 cores × $price/core/year  (same license cost)
  Servers to manage: 4
  Rack units: 4-8U

Scenario C: Optimized Core Count
  3 servers × 2 CPUs × 24 cores = 144 licensed cores
  Hardware: ~$22K × 3 = $66K
  VMware:   144 cores × $price/core/year  (44% less than A/B)
  Servers to manage: 3
  Rack units: 3-6U
  Trade-off: fewer total cores = lower VM density

Key Insight: Total core count drives license cost, not server count.
             Right-size CPU core count to actual workload needs.
             16-core minimum per CPU means a 12-core CPU still pays
             for 16 cores.
```

### Cost Optimization Decision Tree

```
                    ┌─────────────────────┐
                    │ Do you need vSAN?    │
                    │ (HCI, no external    │
                    │  SAN/NAS)            │
                    └────────┬────────────┘
                        ┌────┴────┐
                       Yes        No
                        │         │
                        ▼         ▼
               ┌────────────┐  ┌────────────────┐
               │ VCF is the  │  │ Do you need     │
               │ only option │  │ NSX or Aria?    │
               │ for vSAN    │  └───────┬────────┘
               └─────────────┘     ┌────┴────┐
                                  Yes        No
                                   │         │
                                   ▼         ▼
                          ┌──────────┐  ┌──────────────┐
                          │ VCF      │  │ VVF          │
                          │ (bundled │  │ (vSphere     │
                          │  is      │  │  only,       │
                          │  cheaper │  │  lowest      │
                          │  than    │  │  VMware      │
                          │  buying  │  │  cost)       │
                          │  parts)  │  │              │
                          └──────────┘  └──────┬───────┘
                                               │
                                               ▼
                                      ┌────────────────┐
                                      │ Is VMware cost  │
                                      │ acceptable vs   │
                                      │ alternatives?   │
                                      └───────┬────────┘
                                          ┌───┴───┐
                                         Yes      No
                                          │       │
                                          ▼       ▼
                                     ┌────────┐ ┌──────────┐
                                     │ VVF    │ │ Evaluate │
                                     │        │ │ Nutanix, │
                                     │        │ │ Proxmox, │
                                     │        │ │ Azure    │
                                     │        │ │ Stack HCI│
                                     └────────┘ └──────────┘
```
