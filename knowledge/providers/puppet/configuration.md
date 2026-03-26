# Puppet

## Scope

This document covers Puppet configuration management architecture, including the server/agent model, manifest and module structure, Hiera data hierarchy, Puppet Forge module ecosystem, Puppet Enterprise vs open-source Puppet, orchestration (Puppet Bolt, Plans, Tasks), reporting and compliance enforcement, PuppetDB for infrastructure data, node classification (ENC, console-based, manifests), r10k/Code Manager for code deployment, and migration strategies from Puppet to Ansible, Terraform, or other configuration management tools.

## Checklist

- [ ] **[Critical]** Is the Puppet Server infrastructure sized appropriately for the managed node count, with compile masters (compilers) for environments exceeding 1,000 nodes and appropriate JVM heap tuning?
- [ ] **[Critical]** Is the Hiera data hierarchy designed with appropriate layers (common, environment, role, node-specific) and sensitive data handled via hiera-eyaml encryption or external secrets integration (Vault, AWS Secrets Manager)?
- [ ] **[Critical]** Is the Puppet code deployment workflow defined using r10k or Code Manager with a control repository, environment branches (production, staging, development), and CI/CD pipeline for module testing?
- [ ] **[Critical]** Is the node classification strategy defined -- External Node Classifier (ENC), Puppet Enterprise console groups, or role/profile pattern in manifests -- with clear documentation of how nodes receive their catalog?
- [ ] **[Recommended]** Is the role and profile pattern implemented to separate business logic (roles) from component configuration (profiles), providing a clean abstraction layer between Hiera data and Puppet Forge modules?
- [ ] **[Recommended]** Are Puppet Forge modules evaluated for quality (Supported, Approved, or Partner badges) and pinned to specific versions in the Puppetfile to prevent unexpected changes during deployments?
- [ ] **[Recommended]** Is PuppetDB deployed and sized for infrastructure data collection, exported resources, and reporting, with PostgreSQL backend properly configured for the environment scale?
- [ ] **[Recommended]** Is Puppet Enterprise (PE) evaluated for its console UI, RBAC, orchestration, compliance reporting, and support vs open-source Puppet with community tooling for environments requiring enterprise features?
- [ ] **[Recommended]** Are enforcement modes configured appropriately -- noop (audit) mode for initial rollout and change validation, enforce mode for production compliance -- with clear promotion process between modes?
- [ ] **[Optional]** Is Puppet Bolt used for agentless ad-hoc task execution and orchestration Plans, reducing dependency on the agent for one-time or infrequent operations?
- [ ] **[Optional]** Is a migration path from Puppet to an alternative tool (Ansible, Terraform, or cloud-native configuration) documented if the organization is evaluating tool consolidation?
- [ ] **[Optional]** Are custom facts (Facter) and custom resource types developed only when existing Forge modules do not meet requirements, with proper unit testing (rspec-puppet) and documentation?

## Why This Matters

Puppet pioneered the declarative, model-driven approach to configuration management and remains widely deployed in large enterprise environments, particularly those with thousands of servers requiring continuous compliance enforcement. Its strength lies in drift detection and remediation -- Puppet continuously enforces the desired state every 30 minutes by default, automatically correcting configuration drift. This makes it well-suited for compliance-heavy environments (PCI-DSS, HIPAA, SOX) where configuration consistency is a regulatory requirement.

However, Puppet's learning curve is steeper than alternatives like Ansible due to its domain-specific language (Puppet DSL), agent requirement, client-server architecture, and certificate management. The r10k/Code Manager workflow adds deployment complexity. Organizations are increasingly evaluating whether to maintain Puppet or migrate to Ansible (agentless, simpler syntax) or cloud-native tools (AWS Systems Manager, Azure Automation). Perforce acquired Puppet in 2022, and the product roadmap and licensing model should be evaluated for long-term viability. Migration from Puppet is a significant effort due to the fundamentally different paradigm (declarative DSL vs imperative/procedural playbooks).

## Common Decisions (ADR Triggers)

- **Puppet Enterprise vs open-source** -- PE console, RBAC, orchestration, and support vs community tooling and custom dashboards
- **Agent-based enforcement vs agentless** -- Puppet agent for continuous drift remediation vs Bolt for ad-hoc tasks, or hybrid approach
- **Hiera backend** -- file-based (YAML/JSON) vs external backends (Vault for secrets, database lookups), encryption strategy for sensitive data
- **Code deployment** -- r10k with control repository vs Code Manager (PE), branch-per-environment vs single branch with feature flags
- **Module sourcing** -- Puppet Forge modules vs custom-written modules, version pinning and update cadence
- **Migration strategy** -- continue investing in Puppet vs migrate to Ansible/Terraform, phased approach (new workloads on new tool, existing Puppet maintained)
- **Compliance workflow** -- noop-first rollout with manual promotion vs automated enforce mode, change window coordination
- **Node classification** -- role/profile pattern in code vs ENC vs PE console groups, flexibility vs auditability tradeoffs

## See Also

- `providers/ansible/configuration.md` -- Ansible configuration management architecture
- `general/iac-planning.md` -- infrastructure-as-code planning patterns
