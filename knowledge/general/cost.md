# Cost

## Scope

This file covers **what** cost strategy decisions need to be made (budgeting, right-sizing, reserved capacity, tagging). Provider-specific pricing models and cost tools vary; consult individual provider documentation for implementation details.

## Checklist

- [ ] What is the monthly budget target?
- [ ] Have instance types been right-sized for the workload? (not over-provisioned)
- [ ] Are reserved instances or savings plans appropriate? (1-year or 3-year commits)
- [ ] Is auto-scaling configured to scale down during low traffic?
- [ ] Are there resources that can use spot/preemptible instances?
- [ ] Is data transfer cost accounted for? (cross-AZ, cross-region, internet egress)
- [ ] Is storage tiering configured? (hot, warm, cold, archive)
- [ ] Are unused resources identified and cleaned up? (unattached volumes, old snapshots)
- [ ] Is cost allocation tagging in place? (by project, environment, team)
- [ ] Are budget alerts configured?
- [ ] Is there a cost anomaly detection mechanism?
- [ ] Has a cost estimate been produced for the proposed architecture?
- [ ] Are there cost optimization opportunities? (NAT gateway vs VPC endpoints, reserved capacity)

## Why This Matters

Cloud costs can spiral unexpectedly. Without budget controls, a misconfigured auto-scaling policy or data transfer pattern can generate massive bills. Right-sizing and reserved capacity can reduce costs 30-70%.

## Common Decisions (ADR Triggers)

- **Reserved vs on-demand** — commitment level for known workloads
- **Spot/preemptible usage** — which workloads can tolerate interruption
- **Data transfer optimization** — VPC endpoints vs NAT gateway
- **Storage tiering** — lifecycle policies for aging data
- **Budget controls** — hard limits vs alerts
