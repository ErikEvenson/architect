# OpenStack Deployment Tools

## Checklist

- [ ] **[Critical]** Hardware meets minimum requirements for chosen deployment tool (CPU, RAM, disk, NICs)
- [ ] **[Critical]** Base OS installed on all nodes (Ubuntu 22.04 LTS or CentOS Stream 9 depending on tool)
- [ ] **[Critical]** Network interfaces configured: at least 2 NICs per node (management + provider/tunnel), VLANs pre-configured on switches
- [ ] **[Critical]** DNS and NTP configured and verified on all nodes before deployment begins
- [ ] **[Critical]** SSH key-based authentication configured from deployment node to all target nodes (passwordless sudo)
- [ ] **[Critical]** Deployment tool prerequisites installed: Ansible (correct version), Python virtual environment, Docker (for Kolla-Ansible)
- [ ] **[Recommended]** Inventory file reviewed and validated: hostnames resolve, IP addresses correct, role assignments match hardware plan
- [ ] **[Recommended]** globals.yml or equivalent configuration reviewed: networking mode (linuxbridge vs OVS vs OVN), storage backend, enabled services
- [ ] **[Recommended]** Pre-deployment checks pass: connectivity tests between all nodes, disk devices available, no stale LVM/RAID configurations
- [ ] **[Recommended]** Backup and rollback plan documented before first deployment attempt
- [ ] **[Recommended]** Day-2 runbooks prepared: adding compute nodes, replacing failed controllers, upgrading OpenStack releases
- [ ] **[Optional]** CI/CD pipeline set up to test configuration changes against a staging environment before production
- [ ] **[Optional]** Deployment automated end-to-end with a wrapper script or pipeline that includes pre-checks, deployment, and post-deployment validation
- [ ] **[Optional]** Multi-region or multi-site deployment topology planned if applicable

## Why This Matters

Choosing the right deployment tool determines the operational complexity of the entire OpenStack lifecycle. A poor choice leads to painful upgrades, difficult troubleshooting, and inability to scale. Each tool makes different tradeoffs between simplicity and flexibility, and switching tools after deployment typically means rebuilding from scratch. The deployment tool also dictates how services are isolated (Docker containers, LXC containers, or bare processes), which affects debugging, resource overhead, and upgrade mechanics.

Production OpenStack deployments are multi-week efforts. A typical small cluster (3 controllers + 5 compute nodes) takes 2-4 hours for the actual deployment run, but days or weeks of planning, hardware preparation, and network configuration precede it. Getting the prerequisites wrong wastes that time.

## Common Decisions (ADR Triggers)

### ADR: Selection of OpenStack Deployment Tool
**Trigger:** Starting a new OpenStack deployment or migrating from a deprecated tool (e.g., TripleO).
**Considerations:**
- Team familiarity with Ansible, Juju, or other orchestration tools
- Whether bare-metal provisioning is needed (favors MAAS+Juju or Kayobe) or nodes arrive pre-installed (favors Kolla-Ansible or OSA)
- Container isolation preference: Docker (Kolla-Ansible) vs LXC (OSA) vs bare process (DevStack)
- Upgrade path maturity: Kolla-Ansible and OSA have well-tested rolling upgrade procedures
- Vendor support requirements: Red Hat customers may be locked into RHOSO; Canonical shops use MAAS+Juju

### ADR: Kolla-Ansible vs OpenStack-Ansible
**Trigger:** Narrowing down between the two most popular community tools.
**Considerations:**
- Kolla-Ansible uses Docker containers, making service isolation clean and rollback simpler (just re-pull the previous image). Deployment is faster and the configuration surface is smaller.
- OSA uses LXC containers and is more modular. It allows deeper customization via Ansible variable overrides at many levels. Used by Rackspace at massive scale.
- Kolla-Ansible is easier to learn; OSA is more powerful for complex environments.

### ADR: Bare-Metal Provisioning Strategy
**Trigger:** Need to manage hardware lifecycle (new server racking, OS installation, firmware updates).
**Considerations:**
- MAAS handles PXE boot, IPMI control, OS installation, and hardware testing. Pairs with Juju for service deployment.
- Kayobe wraps Kolla-Ansible and adds Bifrost (Ironic-based) for bare-metal provisioning, providing a single tool for the full lifecycle.
- Manual OS installation with Kickstart/Preseed is simpler for small environments but does not scale.

### ADR: Handling TripleO / RHOSP Deprecation
**Trigger:** Running Red Hat OpenStack Platform (RHOSP) 16.x or 17.x with TripleO.
**Considerations:**
- TripleO is deprecated. Red Hat's replacement is RHOSO (Red Hat OpenStack Services on OpenShift), which runs control plane services as Kubernetes operators on OpenShift.
- Migration from TripleO to RHOSO is a significant undertaking; evaluate whether migrating to a community tool (Kolla-Ansible) is preferable.

## Reference Architectures

### Kolla-Ansible Production Deployment

Kolla-Ansible is the most widely adopted community deployment tool. It packages each OpenStack service into a Docker container and uses Ansible playbooks to deploy, configure, and upgrade them.

**Prerequisites:**
- Deployment node: 4 vCPU, 8 GB RAM, running the Ansible orchestration
- Target nodes: base OS (Ubuntu 22.04 or CentOS Stream 9), Docker CE or Docker Engine installed
- Ansible version must match Kolla-Ansible release (check release notes)
- Python 3.8+ with a virtual environment for kolla-ansible and its dependencies

**Key configuration files:**
- `/etc/kolla/globals.yml` — primary configuration: base distro, network interfaces, VIP address, enabled services, storage backend, TLS settings
- `/etc/kolla/passwords.yml` — auto-generated via `kolla-genpwd`, contains all service passwords
- Inventory file (multinode) — maps hosts to roles: control, network, compute, storage, monitoring

**Typical inventory structure:**
```ini
[control]
ctrl01 ansible_host=10.0.0.11
ctrl02 ansible_host=10.0.0.12
ctrl03 ansible_host=10.0.0.13

[network]
ctrl01
ctrl02
ctrl03

[compute]
comp01 ansible_host=10.0.0.21
comp02 ansible_host=10.0.0.22

[storage]
stor01 ansible_host=10.0.0.31
stor02 ansible_host=10.0.0.32
stor03 ansible_host=10.0.0.33

[monitoring]
ctrl01
```

**Networking prerequisites:**
- NIC 1 (e.g., `ens3`): management network — API traffic, inter-service communication, database/MQ replication
- NIC 2 (e.g., `ens4`): provider/tunnel network — VM traffic (VXLAN/Geneve tunnels or VLAN provider networks)
- VLANs must be pre-configured on physical switches; Kolla-Ansible does not configure switch ports
- A floating IP range on the provider network for external VM access

**Deployment sequence:**
```
kolla-ansible -i multinode bootstrap-servers    # Install Docker, configure hosts
kolla-ansible -i multinode prechecks            # Validate configuration
kolla-ansible -i multinode deploy               # Deploy all services (2-4 hours)
kolla-ansible -i multinode post-deploy          # Generate admin-openrc.sh, clouds.yaml
```

**Upgrade procedure:**
```
# Pull new container images for the target release
kolla-ansible -i multinode pull

# Run the upgrade (rolling, one node at a time for HA services)
kolla-ansible -i multinode upgrade
```

### OpenStack-Ansible (OSA) Production Deployment

OSA deploys each service into an LXC container on the target host. It provides extensive customization through a layered variable override system.

**Architecture:**
- Each service runs in its own LXC container (e.g., `ctrl01_keystone_container-abc123`)
- Host-level networking uses Linux bridges to connect containers
- Ansible roles are modular: each OpenStack service has its own role with its own variables

**Key configuration:**
- `/etc/openstack_deploy/openstack_user_config.yml` — defines hosts, networks, and service placement
- `/etc/openstack_deploy/user_variables.yml` — global overrides
- `/etc/openstack_deploy/user_secrets.yml` — auto-generated secrets

**Strengths:** Very flexible, battle-tested at Rackspace scale (thousands of nodes), excellent documentation for customization.

**Weaknesses:** More complex initial setup, longer deployment times, LXC debugging can be less intuitive than Docker.

### MAAS + Juju (Canonical)

This stack separates bare-metal provisioning (MAAS) from service orchestration (Juju).

**MAAS (Metal as a Service):**
- Discovers servers via IPMI/BMC
- PXE boots and installs Ubuntu on bare metal
- Manages hardware inventory, commissioning tests, and network configuration
- Provides a machine pool that Juju draws from

**Juju:**
- Models applications as "charms" — each OpenStack service has a charm
- Charms handle installation, configuration, relations (service discovery), and scaling
- `juju deploy openstack-base` deploys a full OpenStack bundle

**Best for:** Large deployments (50+ nodes) where hardware lifecycle management is important.

### Kayobe (Bare Metal to Kolla-Ansible)

Kayobe wraps Kolla-Ansible and adds bare-metal provisioning via Bifrost (an Ironic-based tool for provisioning the deployment infrastructure itself).

**Lifecycle coverage:**
1. Bifrost provisions the base OS on bare-metal servers via PXE/IPMI
2. Kayobe configures the hosts (networking, storage, users)
3. Kolla-Ansible deploys OpenStack services in Docker containers
4. Kayobe manages ongoing operations (upgrades, node additions)

**Best for:** Environments that want a single tool from bare metal to running cloud, without the complexity of MAAS+Juju.

### DevStack (Development/Testing Only)

Single-node, all-in-one OpenStack for developers and CI. Installs services directly as system processes from git repositories. Not containerized, not isolated, not upgradeable. Useful for learning OpenStack internals, running Tempest tests, and developing new features.

**Never use DevStack for production.** It has no upgrade path, no HA, and no isolation between services.

### Comparison Matrix

| Aspect | Kolla-Ansible | OSA | MAAS+Juju | TripleO/RHOSO | Kayobe | DevStack |
|---|---|---|---|---|---|---|
| Isolation | Docker | LXC | Bare/LXC | K8s (RHOSO) | Docker | None |
| Bare-metal provisioning | No | No | Yes (MAAS) | Yes (Ironic) | Yes (Bifrost) | No |
| Ease of deployment | Medium | Medium-High | High | High | Medium | Low |
| Upgrade support | Good | Good | Good | Varies | Good | None |
| Production readiness | Yes | Yes | Yes | Yes (RHOSO) | Yes | No |
| Community activity | High | Medium | Medium | Declining (TripleO) | Medium | High |
| Minimum nodes | 1 (AIO) | 1 (AIO) | 4+ (MAAS+3) | 4+ | 1 (AIO) | 1 |

### Day-2 Operations

**Adding a compute node:**
1. Prepare the new host (OS, networking, SSH keys, NTP)
2. Add the host to the inventory under `[compute]`
3. Run `kolla-ansible -i multinode bootstrap-servers --limit new-compute`
4. Run `kolla-ansible -i multinode deploy --limit new-compute`
5. Verify with `openstack compute service list`

**Replacing a failed controller (in a 3-node HA cluster):**
1. Remove the failed node from HAProxy and Galera/RabbitMQ clusters
2. Rebuild or repair the host
3. Re-add to inventory and run deployment targeting that host
4. Verify cluster membership for Galera, RabbitMQ, and all API services

**Upgrading OpenStack releases:**
1. Read release notes for the target version — check for deprecations and required configuration changes
2. Test the upgrade on a staging environment
3. Back up databases and configuration
4. Pull new images/packages, then run the upgrade playbook
5. Verify all services are running and API endpoints respond
