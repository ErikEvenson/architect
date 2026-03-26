# Chef

## Scope

This document covers Chef configuration management architecture, including the Chef Server/Client/Workstation model, cookbooks and recipes, Chef Infra for infrastructure automation, Chef InSpec for compliance-as-code, Chef Habitat for application packaging, the Progress Software acquisition and product roadmap, Chef Automate for visibility and compliance dashboards, Policyfiles vs environments/roles for workflow management, and migration strategies to alternative configuration management tools.

## Checklist

- [ ] **[Critical]** Is the Chef Server (or Chef SaaS/Automate) infrastructure deployed with appropriate high availability (standalone for small environments, HA backend for production) and backup/restore procedures documented?
- [ ] **[Critical]** Is the cookbook development workflow defined with version pinning, environment promotion (dev/staging/production), and CI/CD pipeline integration (Test Kitchen, ChefSpec, Cookstyle linting)?
- [ ] **[Critical]** Is the node bootstrapping process documented, including chef-client installation method, validation key management (or token-based registration), run-list assignment, and initial convergence verification?
- [ ] **[Critical]** Is sensitive data (passwords, API keys, certificates) managed through Chef Vault, encrypted data bags, or external secrets management integration (HashiCorp Vault, AWS Secrets Manager) rather than plaintext attributes?
- [ ] **[Recommended]** Are Policyfiles evaluated as the preferred workflow over legacy environments and roles, providing deterministic cookbook resolution, single artifact promotion, and simplified dependency management?
- [ ] **[Recommended]** Is Chef InSpec used for compliance validation with profiles mapped to regulatory frameworks (CIS benchmarks, STIG, PCI-DSS), running as part of the chef-client convergence or independently via scheduled scans?
- [ ] **[Recommended]** Is Chef Automate deployed for centralized visibility, compliance dashboards, client run history, and node status reporting across the managed fleet?
- [ ] **[Recommended]** Are community cookbooks sourced from Chef Supermarket evaluated for quality, actively maintained, and pinned to specific versions in metadata or Policyfiles?
- [ ] **[Recommended]** Is the chef-client run interval configured appropriately (default 30 minutes) with splay to prevent thundering herd on Chef Server, and are failed runs monitored and alerted?
- [ ] **[Optional]** Is Chef Habitat evaluated for application-centric automation, providing build/deploy/manage lifecycle independent of infrastructure, particularly for containerized or cloud-native workloads?
- [ ] **[Optional]** Is a migration path from Chef to an alternative tool (Ansible, Puppet, or cloud-native configuration) documented, considering the Progress acquisition impact on licensing and product direction?
- [ ] **[Optional]** Are custom resources (formerly LWRPs) developed with proper unit testing and documentation when existing Supermarket cookbooks do not meet requirements?

## Why This Matters

Chef is a mature configuration management platform with particular strength in compliance automation through Chef InSpec. The Ruby-based DSL for cookbooks provides significant flexibility but carries a steep learning curve and higher development overhead compared to Ansible's YAML-based playbooks. Chef's "infrastructure as code" approach with Test Kitchen, ChefSpec, and InSpec provides a robust testing pipeline that appeals to organizations with strong software development practices.

Progress Software acquired Chef in 2020, which has raised questions about long-term product investment and community momentum. While Chef Infra, InSpec, and Habitat continue to receive updates, the open-source community has contracted significantly compared to its peak. Organizations with existing Chef investments must evaluate whether to continue investing in the platform or begin migration planning. Chef InSpec remains a standout capability -- many organizations retain InSpec for compliance scanning even after migrating infrastructure automation to Ansible or Terraform. The client-server architecture, Ruby expertise requirement, and cookbook development complexity make Chef one of the more operationally demanding configuration management tools to maintain.

## Common Decisions (ADR Triggers)

- **Chef Server vs Chef SaaS** -- self-managed infrastructure vs Progress-hosted SaaS, data sovereignty and control considerations
- **Policyfiles vs environments/roles** -- modern deterministic workflow vs legacy flexible-but-complex model, migration effort for existing cookbooks
- **Chef InSpec retention** -- keep InSpec for compliance even if migrating Chef Infra, InSpec standalone vs integrated with chef-client
- **Cookbook sourcing** -- Supermarket community cookbooks vs wrapper cookbooks vs fully custom, maintenance burden tradeoffs
- **Migration strategy** -- continue Chef investment vs migrate to Ansible/Puppet, phased approach for large estates, InSpec portability
- **Chef Habitat adoption** -- application-centric packaging vs container-native (Docker/OCI) vs traditional deployment, operational complexity
- **Secrets management** -- encrypted data bags vs Chef Vault vs external secrets manager (Vault, cloud-native), rotation automation
- **Testing pipeline** -- Test Kitchen + ChefSpec + Cookstyle (full pipeline) vs minimal testing, CI/CD integration requirements

## See Also

- `providers/ansible/configuration.md` -- Ansible configuration management architecture
- `general/iac-planning.md` -- infrastructure-as-code planning patterns

## Reference Links

- [Chef Infra Documentation](https://docs.chef.io/chef_overview/) -- server/client architecture, cookbooks, recipes, and resource types
- [Chef InSpec Documentation](https://docs.chef.io/inspec/) -- compliance-as-code framework for auditing and testing infrastructure
- [Chef Supermarket](https://supermarket.chef.io/) -- community cookbook repository for reusable infrastructure automation
