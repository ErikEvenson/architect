# OpenStack Heat Infrastructure as Code

## Scope

Covers OpenStack Heat orchestration service: HOT template format, template versioning, nested stacks, autoscaling with Aodh alarms, SoftwareConfig/SoftwareDeployment, environment files, resource registry, and comparison with Terraform and Ansible for OpenStack IaC.

## Version Notes

| Release | Date | Key Heat Changes |
|---|---|---|
| 2024.1 Caracal (29) | Apr 2024 | Continued convergence engine improvements |
| 2024.2 Dalmatian (30) | Oct 2024 | Template validation improvements |
| 2025.1 Epoxy (31) | Apr 2025 | Template engine stability improvements, improved error messages for stack update failures |
| 2025.2 Flamingo (32) | Oct 2025 | Continued stability improvements, no major new template features |

## Checklist

- [ ] **[Critical]** Pin `heat_template_version` to a specific date (e.g., `2021-04-16`) — using `latest` or omitting causes unpredictable behavior across OpenStack releases
- [ ] **[Critical]** Use `hidden: true` for all password, secret, and API key parameters — prevents them from appearing in stack details, API responses, and logs
- [ ] **[Critical]** Define security groups explicitly with least-privilege rules — never rely on the default security group which may allow all egress or even all traffic
- [ ] **[Critical]** Configure stack rollback behavior (`--rollback-on-failure`) for production deployments to avoid half-provisioned stacks that are difficult to clean up
- [ ] **[Critical]** Use wait conditions (`OS::Heat::WaitCondition`) when instances must complete cloud-init before dependent resources are created — without this, Heat marks the stack as CREATE_COMPLETE before the instance is actually ready
- [ ] **[Recommended]** Parameterize all environment-specific values (image IDs, flavor names, network IDs, key pair names) — hardcoded values break portability between OpenStack clouds
- [ ] **[Recommended]** Use nested stacks and `OS::Heat::ResourceGroup` for repeated patterns (e.g., N identical web servers) instead of duplicating resource blocks
- [ ] **[Recommended]** Define meaningful outputs (floating IPs, URLs, generated passwords) so consumers can discover stack endpoints without searching through resources
- [ ] **[Recommended]** Use environment files to separate parameters from templates — allows the same template to deploy to dev, staging, and production with different environment files
- [ ] **[Recommended]** Test templates with `openstack stack create --dry-run` (preview) before applying to catch reference errors and constraint violations
- [ ] **[Optional]** Use `OS::Heat::SoftwareConfig` and `OS::Heat::SoftwareDeployment` for multi-step provisioning instead of monolithic user-data scripts — enables structured deployments with individual success/failure tracking
- [ ] **[Optional]** Implement auto-scaling with `OS::Heat::AutoScalingGroup` + Aodh alarms for web tiers that need elastic capacity
- [ ] **[Optional]** Set up resource registry in environment files to create custom resource types that encapsulate complex patterns (e.g., `My::WebServer` maps to a nested template)
- [ ] **[Optional]** Use `depends_on` explicitly when Heat cannot infer the dependency order from `get_resource` / `get_attr` references
- [ ] **[Optional]** Tag all resources with stack name, environment, and owner using resource metadata or properties for cost tracking and operational visibility

## Why This Matters

Heat is OpenStack's native orchestration service. It reads declarative templates (HOT — Heat Orchestration Templates) and provisions compute, networking, storage, and application resources as a single unit called a stack. Without Heat, deploying a multi-tier application on OpenStack means running dozens of CLI commands or API calls in the correct order, tracking dependencies manually, and having no automated rollback or cleanup.

Heat's key advantage over external IaC tools is deep OpenStack integration: it uses the same API authentication (Keystone tokens), understands OpenStack resource lifecycles natively (no provider plugin needed), supports stack-update with in-place or replacement semantics, and can trigger auto-scaling based on Ceilometer/Aodh telemetry. It also supports `stack adopt` — importing existing resources into Heat management without recreation.

The primary limitation is that Heat is OpenStack-only. If your infrastructure spans multiple clouds or includes non-OpenStack resources, Terraform or Pulumi provides a single tool for everything. Heat is the right choice for OpenStack-only environments where simplicity and native integration matter more than multi-cloud portability.

## Common Decisions (ADR Triggers)

### ADR: Heat vs Terraform for OpenStack

**Heat (native orchestration)**
- No external state file — state is stored in the Heat API/database, accessible via `openstack stack show`
- No provider version compatibility issues — Heat's resource types are part of the OpenStack release
- Stack-update with rollback is built-in — failed updates revert automatically
- `stack adopt` lets you import existing resources without recreating them
- Auto-scaling is integrated via `OS::Heat::AutoScalingGroup` + Aodh alarms
- Limitation: OpenStack-only, smaller community, fewer learning resources, no module registry

**Terraform (multi-cloud IaC)**
- Single tool for OpenStack + AWS + GCP + Azure + DNS + monitoring + everything else
- State management requires backend configuration (S3, Swift, Consul, Terraform Cloud)
- OpenStack provider requires version pinning and may lag behind OpenStack releases
- `terraform plan` gives a detailed preview (Heat's `--dry-run` is less comprehensive)
- Rich module ecosystem, large community, extensive documentation
- Limitation: external state file is a single point of failure if not properly managed

**Decision trigger:** Use Heat when the environment is purely OpenStack and the team prefers native tooling. Use Terraform when managing resources across multiple clouds or when the team already uses Terraform elsewhere. They can coexist — Heat for OpenStack-specific patterns (auto-scaling, software deployments) and Terraform for cross-cloud orchestration.

### ADR: Monolithic vs Nested Stack Architecture

**Monolithic template**: All resources in a single HOT file. Simple for small deployments (< 20 resources). Easy to read and debug. Becomes unwieldy as complexity grows — long files, parameter explosion, hard to reuse components.

**Nested stacks**: Break the architecture into layers — network.yaml, security.yaml, compute.yaml, database.yaml. Parent template orchestrates child templates via `type: network.yaml` or `OS::Heat::ResourceGroup`. Each layer is testable independently. Parameters flow from parent to children, outputs flow back up.

```yaml
# Parent template
resources:
  network:
    type: network.yaml
    properties:
      cidr: { get_param: network_cidr }

  web_servers:
    type: OS::Heat::ResourceGroup
    properties:
      count: { get_param: web_server_count }
      resource_def:
        type: web-server.yaml
        properties:
          network: { get_attr: [network, network_id] }
          subnet: { get_attr: [network, subnet_id] }
```

**Decision trigger:** More than 15-20 resources, multiple environments reusing the same patterns, or multiple teams contributing to the infrastructure definition.

### ADR: Cloud-Init vs SoftwareConfig for Instance Provisioning

**Cloud-init (user_data)**: Single script or cloud-config YAML baked into `OS::Nova::Server`. Simple, no additional Heat resources needed. Limitation: no structured success/failure reporting back to Heat (unless you add `WaitCondition` manually). Debugging requires SSH into the instance and reading `/var/log/cloud-init-output.log`.

**SoftwareConfig + SoftwareDeployment**: Multi-step provisioning with individual success/failure tracking per step. Each `SoftwareConfig` defines a script, `SoftwareDeployment` applies it to a server. Heat tracks deployment status. Supports input/output values between steps. Uses `os-collect-config` and `os-apply-config` agents on the instance. More complex setup but better observability.

```yaml
resources:
  install_config:
    type: OS::Heat::SoftwareConfig
    properties:
      group: script
      config: |
        #!/bin/bash
        apt-get update && apt-get install -y nginx

  install_deployment:
    type: OS::Heat::SoftwareDeployment
    properties:
      config: { get_resource: install_config }
      server: { get_resource: my_server }
      signal_transport: HEAT_SIGNAL
```

**Decision trigger:** Use cloud-init for simple, single-step provisioning. Use SoftwareConfig when you need multi-step provisioning, input/output passing between steps, or structured deployment status reporting.

### ADR: Auto-Scaling Strategy

Heat provides auto-scaling through three resources working together:

- **`OS::Heat::AutoScalingGroup`**: Manages a group of identical resources (servers) that can scale up/down. Defines `min_size`, `max_size`, and the `resource` template.
- **`OS::Heat::ScalingPolicy`**: Defines the scaling action (change_in_capacity: +1, -1 or exact_capacity or percent_change). Has a `cooldown` period (seconds) to prevent flapping.
- **`OS::Aodh::GnocchiAggregationByResourcesAlarm`** (or legacy `OS::Ceilometer::Alarm`): Triggers the scaling policy when a metric threshold is crossed (e.g., average CPU > 80% for 5 minutes).

```yaml
resources:
  scaling_group:
    type: OS::Heat::AutoScalingGroup
    properties:
      min_size: 2
      max_size: 10
      resource:
        type: web-server.yaml
        properties:
          network: { get_param: network_id }

  scale_up_policy:
    type: OS::Heat::ScalingPolicy
    properties:
      adjustment_type: change_in_capacity
      auto_scaling_group_id: { get_resource: scaling_group }
      cooldown: 300
      scaling_adjustment: 1

  cpu_alarm_high:
    type: OS::Aodh::GnocchiAggregationByResourcesAlarm
    properties:
      metric: cpu_util
      aggregation_method: mean
      granularity: 300
      evaluation_periods: 3
      threshold: 80.0
      comparison_operator: gt
      resource_type: instance
      alarm_actions:
        - { get_attr: [scale_up_policy, signal_url] }
```

**Decision trigger:** Web tiers or worker pools with variable load. Requires Ceilometer/Gnocchi and Aodh services to be deployed in the OpenStack environment — check availability first.

## Reference Architectures

### Single-Server Deployment

```yaml
heat_template_version: 2021-04-16
description: Single server with floating IP

parameters:
  image:
    type: string
    default: Ubuntu-22.04
  flavor:
    type: string
    default: m1.medium
  key_name:
    type: string
  public_net:
    type: string
    default: external
  private_net_cidr:
    type: string
    default: 192.168.1.0/24

resources:
  network:
    type: OS::Neutron::Net
  subnet:
    type: OS::Neutron::Subnet
    properties:
      network: { get_resource: network }
      cidr: { get_param: private_net_cidr }
      dns_nameservers: [8.8.8.8, 8.8.4.4]
  router:
    type: OS::Neutron::Router
    properties:
      external_gateway_info:
        network: { get_param: public_net }
  router_interface:
    type: OS::Neutron::RouterInterface
    properties:
      router: { get_resource: router }
      subnet: { get_resource: subnet }
  security_group:
    type: OS::Neutron::SecurityGroup
    properties:
      rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
        - protocol: tcp
          port_range_min: 80
          port_range_max: 80
        - protocol: tcp
          port_range_min: 443
          port_range_max: 443
  port:
    type: OS::Neutron::Port
    properties:
      network: { get_resource: network }
      security_groups: [{ get_resource: security_group }]
      fixed_ips:
        - subnet: { get_resource: subnet }
  server:
    type: OS::Nova::Server
    properties:
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      networks:
        - port: { get_resource: port }
      user_data_format: RAW
      user_data: |
        #!/bin/bash
        apt-get update && apt-get install -y nginx
        systemctl enable --now nginx
  floating_ip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network: { get_param: public_net }
  floating_ip_assoc:
    type: OS::Neutron::FloatingIPAssociation
    properties:
      floatingip_id: { get_resource: floating_ip }
      port_id: { get_resource: port }

outputs:
  server_public_ip:
    description: Public IP address of the server
    value: { get_attr: [floating_ip, floating_ip_address] }
  server_url:
    description: URL of the web server
    value:
      str_replace:
        template: http://HOST
        params:
          HOST: { get_attr: [floating_ip, floating_ip_address] }
```

### Multi-Tier Application with Nested Stacks

```
[Parent Stack: app-stack.yaml]
  |
  +-- [Network Layer: network.yaml]
  |     OS::Neutron::Net (app-net)
  |     OS::Neutron::Subnet (app-subnet: 10.0.1.0/24)
  |     OS::Neutron::Subnet (db-subnet: 10.0.2.0/24)
  |     OS::Neutron::Router (gateway to external)
  |     Outputs: app_net_id, app_subnet_id, db_subnet_id
  |
  +-- [Web Tier: web-tier.yaml]
  |     OS::Heat::ResourceGroup (count: 3)
  |       -> web-server.yaml
  |            OS::Nova::Server (Ubuntu, m1.medium)
  |            OS::Neutron::Port (app-subnet)
  |            OS::Neutron::FloatingIP
  |            user_data: install nginx, configure reverse proxy
  |     OS::Neutron::SecurityGroup (80, 443, 22)
  |     Outputs: server_ips, floating_ips
  |
  +-- [App Tier: app-tier.yaml]
  |     OS::Heat::ResourceGroup (count: 2)
  |       -> app-server.yaml
  |            OS::Nova::Server (Ubuntu, m1.large)
  |            OS::Neutron::Port (app-subnet, no floating IP)
  |            user_data: install app runtime, deploy application
  |     OS::Neutron::SecurityGroup (8080 from web-sg only)
  |     Outputs: server_ips
  |
  +-- [Database Tier: db-tier.yaml]
        OS::Trove::Instance (MySQL 8.0, m1.large)
          OR
        OS::Nova::Server + OS::Cinder::Volume (100GB)
        OS::Cinder::VolumeAttachment
        OS::Neutron::SecurityGroup (3306 from app-sg only)
        Outputs: db_host, db_port

Environment file (env-prod.yaml):
  parameters:
    web_count: 3
    app_count: 2
    web_flavor: m1.medium
    app_flavor: m1.large
    db_flavor: m1.xlarge
    db_volume_size: 100
    image: Ubuntu-22.04
    key_name: prod-keypair

Deploy: openstack stack create -t app-stack.yaml -e env-prod.yaml prod-app
```

### Auto-Scaling Web Tier

```
[Load Balancer (Octavia)]
       |
[AutoScalingGroup: 2-10 web servers]
       |
  [ScalingPolicy: +1]  <-- [Aodh Alarm: CPU > 80% for 5min]
  [ScalingPolicy: -1]  <-- [Aodh Alarm: CPU < 20% for 10min]
       |
[Ceilometer/Gnocchi: CPU metrics collection]

Key configuration:
  - AutoScalingGroup.min_size: 2 (always have redundancy)
  - AutoScalingGroup.max_size: 10 (cost control)
  - Scale-up cooldown: 300s (wait for new instance to warm up)
  - Scale-down cooldown: 600s (avoid flapping)
  - Alarm evaluation_periods: 3 (sustained load, not spikes)
  - Load balancer health check: HTTP /health, interval 10s, 3 failures

Stack update behavior:
  - Changing the resource template triggers rolling update
  - rolling_updates policy: max_batch_size: 1, pause_time: 60
  - Ensures zero-downtime deployments for template changes
```
