# Salt (SaltStack)

## Scope

This document covers Salt (SaltStack) configuration management and remote execution architecture, including the master/minion model, state files and state trees, pillar data for secrets and node-specific configuration, Salt Cloud for cloud infrastructure provisioning, the event-driven infrastructure system (reactor, beacons, orchestration), VMware acquisition (now Aria Automation Config / VCF Automation Config), high-speed execution for large-scale environments, Salt SSH for agentless operation, proxy minions for network devices, and migration considerations.

## Checklist

- [ ] **[Critical]** Is the Salt Master infrastructure sized for the managed minion count, with multi-master configuration (hot-hot or failover) for environments exceeding 1,000 minions or requiring high availability?
- [ ] **[Critical]** Is the minion key management process documented, including key acceptance workflow (manual, auto-accept with restrictions, or pre-seeded keys), key rotation policy, and rejected/orphaned key cleanup?
- [ ] **[Critical]** Is pillar data properly secured, with sensitive values (passwords, API keys, certificates) stored in encrypted pillar (GPG-encrypted pillar) or external pillar modules (HashiCorp Vault, AWS Secrets Manager)?
- [ ] **[Critical]** Is the state tree organized with a clear top file (top.sls) structure, environment separation (base, dev, staging, prod), and modular state files following Salt best practices for reusability?
- [ ] **[Recommended]** Is the Salt event bus and reactor system evaluated for event-driven automation (auto-remediation, auto-scaling, security response) leveraging Salt's real-time ZeroMQ transport?
- [ ] **[Recommended]** Is Salt Cloud configured for cloud infrastructure provisioning (AWS, Azure, GCP, VMware, Proxmox) with profiles and providers defined, or is Terraform preferred for infrastructure provisioning with Salt for configuration?
- [ ] **[Recommended]** Are Salt formulas (reusable state collections) sourced from the Salt community formulas repository, evaluated for quality, and pinned to specific versions via GitFS or file_roots?
- [ ] **[Recommended]** Is the Salt job management and return system configured with an appropriate returner (PostgreSQL, Elasticsearch, MySQL) for job history, compliance reporting, and audit trails?
- [ ] **[Recommended]** Are grains (system properties) and custom grains used appropriately for targeting and pillar data selection, with grain-based targeting documented for consistent environment classification?
- [ ] **[Optional]** Is Salt SSH evaluated for managing hosts where minion installation is not possible (DMZ servers, legacy systems, network appliances), understanding the performance tradeoff vs ZeroMQ transport?
- [ ] **[Optional]** Is VMware Aria Automation Config (formerly vRealize Automation SaltStack Config) evaluated for organizations with existing VMware/VCF investments, providing enterprise UI, RBAC, and compliance features on top of open-source Salt?
- [ ] **[Optional]** Are proxy minions configured for managing network devices (switches, routers, firewalls) and IoT/edge devices that cannot run a native Salt minion?

## Why This Matters

Salt is the fastest configuration management and remote execution platform at scale, built on an asynchronous ZeroMQ message bus that enables real-time command execution across thousands of nodes in seconds. This speed advantage makes Salt particularly suited for large environments (10,000+ nodes) where Ansible's SSH-based approach becomes a bottleneck and Puppet/Chef's periodic convergence model is too slow for operational tasks. Salt's dual nature as both a configuration management tool (states) and a remote execution framework (ad-hoc commands) provides unique flexibility.

VMware acquired SaltStack in 2020 and integrated it as vRealize Automation SaltStack Config (now Aria Automation Config / VCF Automation Config), providing an enterprise management layer with RBAC, compliance dashboards, and VMware ecosystem integration. The open-source Salt project continues under the Salt Project community, but the enterprise product roadmap is now tied to VMware/Broadcom's VCF strategy. Organizations must evaluate whether to use open-source Salt (community support, no enterprise UI) or VCF Automation Config (enterprise features, VMware licensing dependency). Salt's event-driven reactor system is a differentiating capability -- beacons monitor system conditions and trigger automated remediation in real-time, enabling truly reactive infrastructure management that other tools require additional orchestration layers to achieve.

## Common Decisions (ADR Triggers)

- **Open-source Salt vs VCF Automation Config** -- community-supported Salt vs VMware enterprise product, licensing implications and feature differences
- **Salt vs Ansible for remote execution** -- Salt's ZeroMQ speed vs Ansible's agentless simplicity, environment scale and real-time requirements
- **Salt Cloud vs Terraform** -- Salt Cloud for tightly integrated provisioning+configuration vs Terraform for infrastructure with Salt for configuration only
- **Master topology** -- single master vs multi-master (hot-hot) vs Salt syndic (hierarchical) for geographically distributed environments
- **Event-driven automation** -- reactor system for auto-remediation vs scheduled state runs, risk tolerance for automated changes
- **Pillar encryption** -- GPG-encrypted pillar vs Vault external pillar module vs cloud-native secrets, key management complexity
- **State management workflow** -- GitFS (direct git integration) vs file_roots with CI/CD deployment, environment branching strategy
- **Migration strategy** -- continue Salt investment vs migrate to Ansible (most common migration target), phased approach by workload type

## See Also

- `providers/ansible/configuration.md` -- Ansible configuration management architecture
- `general/iac-planning.md` -- infrastructure-as-code planning patterns
- `providers/vmware/platform-services.md` -- VMware platform services including Aria/VCF suite

## Reference Links

- [Salt Documentation](https://docs.saltproject.io/en/latest/) -- master/minion architecture, state files, pillar data, and execution modules
- [Salt Cloud](https://docs.saltproject.io/en/latest/topics/cloud/) -- cloud infrastructure provisioning across AWS, Azure, GCP, and other providers
- [Salt Reactor and Event System](https://docs.saltproject.io/en/latest/topics/reactor/) -- event-driven automation, beacons, and orchestration runners
