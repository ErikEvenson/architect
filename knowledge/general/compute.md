# Compute

## Scope

This file covers **what** compute decisions need to be made. For provider-specific **how**, see the provider compute files.

## Checklist

- [ ] **[Critical]** What compute platform is required? (VMs, containers, serverless, bare metal)
- [ ] **[Critical]** How many instances/replicas are needed for the expected load?
- [ ] **[Critical]** What instance sizing is appropriate? (CPU, memory, storage)
- [ ] **[Recommended]** Is horizontal scaling needed? What triggers scaling? (CPU, memory, request count, queue depth)
- [ ] **[Recommended]** What are the minimum and maximum instance counts?
- [ ] **[Critical]** How are instances distributed across availability zones?
- [ ] **[Recommended]** What OS and runtime versions are required?
- [ ] **[Critical]** How is OS patching handled? (automated, scheduled, immutable image replacement)
- [ ] **[Optional]** Are there GPU or specialized hardware requirements?
- [ ] **[Critical]** Is the application stateless or stateful?
- [ ] **[Recommended]** If stateful, how is state managed across instances? (external session store, sticky sessions)

## Why This Matters

Compute is the foundation of the application tier. Incorrect sizing leads to either wasted spend or performance issues. Missing HA configuration means single points of failure. Ignoring patching creates security vulnerabilities.

## Common Decisions (ADR Triggers)

- **Compute platform choice** — VMs vs containers vs serverless
- **Instance type selection** — burstable vs general purpose vs compute-optimized
- **Scaling strategy** — target tracking vs step scaling vs scheduled
- **Patching strategy** — in-place vs immutable image replacement
- **Session management** — external store vs sticky sessions vs stateless

## See Also

- `providers/aws/ec2-asg.md` — AWS EC2 instances and Auto Scaling Groups
- `providers/azure/compute.md` — Azure VMs and Scale Sets
- `providers/gcp/compute.md` — GCP Compute Engine and instance groups
