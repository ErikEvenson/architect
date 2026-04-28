# Morpheus Cloud Management

## Scope

Morpheus Data as a hybrid cloud management platform (CMP): unified provisioning, orchestration, cost management, governance, and operations across VMware, Nutanix, AWS, Azure, GCP, OpenStack, Kubernetes, Hyper-V, and bare metal. Covers appliance architecture, cloud integrations, self-service catalogs, policy engine, networking/IPAM integration, backup integration, and multi-tenant governance.

## Checklist

- [ ] [Critical] Which cloud integrations are in scope and how are they connected? (VMware vCenter, Nutanix Prism Central, AWS accounts, Azure subscriptions, GCP projects, OpenStack — each integration has different feature depth and API credential requirements)
- [ ] [Critical] Is the Morpheus appliance deployed in HA configuration? (single-node for lab/POC vs 3-node HA with external Percona/MySQL cluster, Elasticsearch cluster, and RabbitMQ cluster for production — single-node is a complete outage risk for all managed infrastructure)
- [ ] [Critical] How is multi-tenancy structured? (single master tenant vs sub-tenants per business unit or customer — tenant isolation controls blast radius but adds administrative overhead; groups within tenants provide lighter-weight resource boundaries)
- [ ] [Critical] What RBAC model is applied? (built-in roles vs custom roles, Active Directory/LDAP/SAML/OIDC identity source integration — overly permissive roles defeat the purpose of a governance layer)
- [ ] [Critical] What policies are enforced through the policy engine? (naming conventions, tagging requirements, instance sizing limits, approval workflows, lease expiration, budget caps — policies should match organizational governance requirements without creating friction that drives shadow IT)
- [ ] [Recommended] How is IPAM integrated for automated IP assignment? (Morpheus built-in IPAM vs Infoblox vs BlueCat vs SolarWinds — built-in works for simple environments, enterprise IPAM integration prevents address conflicts across hybrid networks)
- [ ] [Recommended] Are instance types and layouts defined for standardized provisioning? (pre-built blueprints with approved OS images, sizing options, and automation scripts vs freeform provisioning — standardized layouts enforce consistency but need ongoing maintenance as requirements change)
- [ ] [Recommended] What task automation engine is used within workflows? (Ansible playbooks, Puppet modules, Chef recipes, shell/Python/PowerShell scripts, Terraform plans, ARM templates — choose based on existing team skills and IaC investments rather than starting fresh)
- [ ] [Recommended] How are self-service catalog items structured for end users? (catalog items per application stack vs per VM type vs per environment — catalog design determines user experience and governs what can be provisioned without admin intervention)
- [ ] [Recommended] Is Morpheus managing Kubernetes clusters? (provision and manage full lifecycle vs integrate with existing clusters for workload deployment — Morpheus can provision clusters on multiple platforms but may overlap with dedicated Kubernetes management tools like Rancher or OpenShift)
- [ ] [Recommended] How is backup integration configured? (Veeam, Commvault, Rubrik integration vs native snapshot-based protection — Morpheus orchestrates backup jobs through integrations but does not replace the backup platform itself)
- [ ] [Recommended] Are lifecycle management policies configured? (lease expiration with user self-service extension, automatic reclamation of expired instances, shutdown schedules for non-production — prevents cloud sprawl but requires organizational buy-in on enforcement)
- [ ] [Optional] Are distributed worker nodes deployed for remote site or cloud management? (direct appliance connectivity vs worker nodes in remote networks — workers reduce latency and firewall complexity for geographically distributed infrastructure)
- [ ] [Optional] Is the Morpheus migration tool used for VM migrations between clouds? (built-in migration assessment and execution vs dedicated migration tools like RVTools + HCX or Nutanix Move — Morpheus migration is convenient for CMP-managed sources but may lack depth of specialized tools)
- [ ] [Optional] Is drift detection and compliance scanning enabled? (Morpheus compliance checks vs external tools like Chef InSpec or HashiCorp Sentinel — built-in checks cover common baselines, external tools provide deeper audit capabilities)

## Why This Matters

A cloud management platform sits at the control plane of the entire infrastructure estate. Morpheus provides a single API and UI across disparate clouds, which accelerates provisioning and enables consistent governance — but a poorly configured CMP creates a false sense of control. If RBAC is too loose, users can provision unconstrained resources across any integrated cloud. If policies are not enforced, the CMP becomes a pass-through portal with no governance value. If the appliance is not deployed in HA, a single server failure disables provisioning, monitoring, and policy enforcement for all managed infrastructure simultaneously. The choice of which integrations to enable, how deeply to configure them, and what policies to enforce determines whether Morpheus functions as a governance layer or just another console.

## Common Decisions (ADR Triggers)

- **Appliance architecture** -- single-node (simple, lab/POC) vs 3-node HA (production, requires external Percona, Elasticsearch, RabbitMQ) vs distributed workers for remote sites
- **Tenant model** -- single tenant with groups (simpler, shared policies) vs multi-tenant (stronger isolation, per-tenant admins, more complex)
- **Provisioning approach** -- Morpheus-native instance types/layouts vs Terraform/ARM template integration (leverage existing IaC) vs hybrid with Morpheus orchestrating Terraform runs
- **IPAM strategy** -- Morpheus built-in IPAM (zero integration effort) vs Infoblox/BlueCat (enterprise source of truth, prevents conflicts across hybrid networks)
- **Automation engine** -- Morpheus tasks and workflows (self-contained) vs Ansible Tower/AWX integration (existing automation investment) vs mixed with per-workflow tool selection
- **Kubernetes management** -- Morpheus-provisioned clusters (unified lifecycle) vs external cluster integration (Rancher, OpenShift, EKS/AKS/GKE with Morpheus as consumer)
- **Cost governance** -- Morpheus budgets and approvals (built-in, per-tenant/group) vs external FinOps tools (CloudHealth, Apptio) with Morpheus as provisioning layer only
- **Backup integration** -- Morpheus-orchestrated backup jobs via Veeam/Commvault/Rubrik vs backup managed entirely outside CMP
- **Agent vs agentless management** -- Morpheus agent on managed VMs (richer monitoring, remote execution) vs agentless (less intrusion, relies on cloud APIs and SSH/WinRM)
- **Load balancer integration** -- Morpheus-managed F5/NSX/AVI profiles vs external LB management with Morpheus handling only VM provisioning

## Reference Links

- [Morpheus Documentation](https://docs.morpheusdata.com/)
- [Morpheus Supported Integrations](https://morpheusdata.com/integrations/)

## See Also

- `general/compute.md` -- general compute architecture patterns
- `general/governance.md` -- governance policies and organizational controls
- `general/cost.md` -- cost management principles
- `general/enterprise-backup.md` -- enterprise backup strategy
- `providers/vmware/infrastructure.md` -- VMware vCenter integration target
- `providers/nutanix/infrastructure.md` -- Nutanix Prism Central integration target
- `providers/hashicorp/terraform.md` -- Terraform integration for IaC-driven provisioning
- `providers/kubernetes/compute.md` -- Kubernetes cluster management considerations
- `patterns/hybrid-cloud.md` -- hybrid cloud architecture patterns
- `patterns/hpe-hybrid-cloud.md` -- HPE-anchored hybrid pattern positioning Morpheus as the cross-environment orchestrator (HPE acquired Morpheus)
- `patterns/multi-cloud.md` -- multi-cloud architecture patterns
