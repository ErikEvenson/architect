# Ansible

Agentless automation tool for configuration management, application deployment, and infrastructure provisioning. Ansible uses SSH (or WinRM for Windows) to execute tasks defined in YAML playbooks, requiring no agent installation on managed hosts.

---

## Checklist

- [ ] **[Critical]** Use Ansible Vault to encrypt all sensitive data (passwords, API keys, certificates) in playbooks and variable files — never commit plaintext secrets
- [ ] **[Critical]** Ensure all tasks are idempotent — use purpose-built modules (e.g., `ansible.builtin.copy`, `ansible.builtin.service`) instead of `command`/`shell` wherever possible
- [ ] **[Critical]** Use roles to organize tasks into reusable, testable units with well-defined interfaces (`defaults/main.yml` for overridable variables, `vars/main.yml` for internal variables)
- [ ] **[Critical]** Maintain an inventory that reflects the actual environment — use dynamic inventory plugins for cloud environments (AWS EC2, Azure, GCP) to auto-discover hosts
- [ ] **[Critical]** Pin collection versions in `requirements.yml` for reproducible automation (`ansible-galaxy collection install -r requirements.yml`)
- [ ] **[Recommended]** Test roles with Molecule before deploying to production (lint, converge, verify, idempotence checks)
- [ ] **[Recommended]** Use `ansible-lint` in CI to enforce playbook best practices and coding standards
- [ ] **[Recommended]** Structure variables by precedence: `group_vars/` for environment-level, `host_vars/` for host-specific, role `defaults/` for overridable defaults
- [ ] **[Recommended]** Use handlers for service restarts after configuration changes — handlers run once at the end of a play even if notified multiple times
- [ ] **[Recommended]** Tag tasks to enable selective execution (`ansible-playbook site.yml --tags "config,deploy"`)
- [ ] **[Recommended]** Use `--check` (dry-run) and `--diff` modes to preview changes before applying
- [ ] **[Optional]** Deploy AWX or Ansible Automation Platform for web-based UI, RBAC, scheduling, and credential management
- [ ] **[Optional]** Use callback plugins or ARA for playbook run reporting and history
- [ ] **[Optional]** Implement custom modules in Python for organization-specific automation that existing modules do not cover

---

## Why This Matters

Ansible's agentless architecture is its defining advantage — there is nothing to install, patch, or maintain on managed hosts. SSH and Python (present on virtually every Linux system) are the only requirements. This makes Ansible uniquely practical for brownfield environments, network devices, legacy systems, and air-gapped infrastructure where installing agents is impractical or prohibited. Playbooks are YAML, which is readable by developers and operations staff alike, lowering the barrier to collaboration. Ansible's module library is extraordinarily broad: from cloud provisioning (AWS, Azure, GCP, VMware, OpenStack) to OS configuration, application deployment, networking devices (Cisco IOS, Juniper, Arista), and container orchestration. Unlike Terraform which focuses on infrastructure lifecycle, Ansible excels at the configuration and deployment layers — what happens inside the OS after the VM is provisioned. The two are complementary, not competing. For organizations already using SSH, Ansible integrates into existing access control and audit infrastructure with no additional attack surface.

---

## Core Concepts

### Inventory

Static inventory:

```ini
# inventory/production.ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com ansible_port=2222

[production:children]
webservers
databases

[production:vars]
ansible_user=deploy
ntp_server=time.example.com
```

Dynamic inventory (AWS EC2):

```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2
keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: instance_type
    prefix: type
filters:
  tag:ManagedBy: ansible
compose:
  ansible_host: private_ip_address
```

```bash
# Verify dynamic inventory
ansible-inventory -i inventory/aws_ec2.yml --graph
```

### Playbooks

```yaml
# site.yml
---
- name: Configure web servers
  hosts: webservers
  become: true
  vars:
    http_port: 8080
    max_clients: 200

  pre_tasks:
    - name: Update apt cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600

  roles:
    - common
    - nginx
    - app_deploy

  post_tasks:
    - name: Verify application health
      ansible.builtin.uri:
        url: "http://localhost:{{ http_port }}/health"
        status_code: 200
      register: health_check
      retries: 5
      delay: 10
      until: health_check.status == 200
```

### Roles

```
roles/nginx/
  |-- defaults/main.yml    # overridable default variables
  |-- vars/main.yml         # internal variables (higher precedence)
  |-- tasks/main.yml        # task definitions
  |-- handlers/main.yml     # handler definitions
  |-- templates/nginx.conf.j2  # Jinja2 templates
  |-- files/ssl/            # static files to copy
  |-- meta/main.yml         # role metadata and dependencies
  |-- molecule/             # test scenarios
```

```yaml
# roles/nginx/tasks/main.yml
---
- name: Install nginx
  ansible.builtin.apt:
    name: nginx
    state: present

- name: Deploy nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: nginx -t -c %s
  notify: Restart nginx

- name: Ensure nginx is running and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
```

```yaml
# roles/nginx/handlers/main.yml
---
- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

## Ansible Vault

```bash
# Encrypt a file
ansible-vault encrypt group_vars/production/secrets.yml

# Encrypt a string (inline in YAML)
ansible-vault encrypt_string 'SuperSecretPassword' --name 'db_password'

# Edit encrypted file
ansible-vault edit group_vars/production/secrets.yml

# Run playbook with vault password
ansible-playbook site.yml --ask-vault-pass
ansible-playbook site.yml --vault-password-file ~/.vault_pass

# Multiple vault IDs for different secrets
ansible-vault encrypt --vault-id prod@prompt secrets_prod.yml
ansible-vault encrypt --vault-id dev@prompt secrets_dev.yml
ansible-playbook site.yml --vault-id prod@prompt --vault-id dev@prompt
```

```yaml
# group_vars/production/secrets.yml (encrypted)
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  61626364656667686970...
api_key: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  71828394051627384950...
```

## Collections

```yaml
# requirements.yml
---
collections:
  - name: amazon.aws
    version: ">=7.0.0,<8.0.0"
  - name: azure.azcollection
    version: "2.3.0"
  - name: community.vmware
    version: "4.0.0"
  - name: ansible.posix
    version: "1.5.0"

roles:
  - name: geerlingguy.docker
    version: "6.1.0"
```

```bash
# Install collections and roles
ansible-galaxy collection install -r requirements.yml
ansible-galaxy role install -r requirements.yml

# Install from private automation hub
ansible-galaxy collection install myorg.internal_collection \
  --server https://automationhub.example.com/
```

Key collections:
- `amazon.aws` — EC2, S3, RDS, EKS, IAM, CloudFormation
- `azure.azcollection` — VMs, AKS, Storage, networking
- `google.cloud` — GCE, GKE, Cloud SQL, networking
- `community.vmware` — vSphere VMs, networking, storage
- `openstack.cloud` — Nova, Neutron, Cinder, Keystone
- `ansible.netcommon` — base networking (cli_command, cli_config)
- `cisco.ios`, `junipernetworks.junos`, `arista.eos` — vendor-specific networking

## Jinja2 Templating

```jinja2
{# templates/nginx.conf.j2 #}
worker_processes {{ ansible_processor_vcpus }};

events {
    worker_connections {{ max_clients | default(1024) }};
}

http {
    {% for server in virtual_hosts %}
    server {
        listen {{ http_port }};
        server_name {{ server.name }};

        {% if server.ssl is defined and server.ssl %}
        listen 443 ssl;
        ssl_certificate /etc/ssl/{{ server.name }}.crt;
        ssl_certificate_key /etc/ssl/{{ server.name }}.key;
        {% endif %}

        location / {
            proxy_pass http://{{ server.upstream }};
        }
    }
    {% endfor %}
}
```

## Idempotency

Modules are idempotent by default — running a playbook twice produces no changes on the second run. The `command` and `shell` modules are exceptions; guard them with `creates` or `removes`:

```yaml
# BAD — runs every time
- name: Initialize database
  ansible.builtin.command: /opt/app/init-db.sh

# GOOD — only runs if the file does not exist
- name: Initialize database
  ansible.builtin.command: /opt/app/init-db.sh
  args:
    creates: /opt/app/.db_initialized

# GOOD — use a purpose-built module instead
- name: Ensure database exists
  community.postgresql.postgresql_db:
    name: myapp
    state: present
```

## Molecule (Testing Framework)

```yaml
# roles/nginx/molecule/default/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: ubuntu:22.04
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible  # or testinfra
```

```yaml
# roles/nginx/molecule/default/verify.yml
---
- name: Verify nginx installation
  hosts: all
  gather_facts: false
  tasks:
    - name: Check nginx is installed
      ansible.builtin.package_facts:
        manager: auto

    - name: Assert nginx package is present
      ansible.builtin.assert:
        that: "'nginx' in ansible_facts.packages"

    - name: Check nginx is listening on port 80
      ansible.builtin.wait_for:
        port: 80
        timeout: 5
```

```bash
# Run full test sequence
molecule test

# Run individual phases
molecule create      # create test instance
molecule converge    # run the role
molecule verify      # run verification tests
molecule idempotence # run again, expect no changes
molecule destroy     # tear down
```

## AWX / Ansible Automation Platform

AWX (upstream open-source) and Ansible Automation Platform (Red Hat commercial) provide:

- **Web UI**: Visual playbook management, job history, real-time output
- **RBAC**: Role-based access control per project, inventory, credential, and job template
- **Credential management**: Store SSH keys, cloud credentials, vault passwords securely
- **Scheduling**: Cron-like scheduling of playbook runs
- **Workflow templates**: Chain multiple job templates with conditional logic (on success/failure/always)
- **API**: REST API for integration with ticketing systems, ChatOps, self-service portals
- **Execution environments**: Container images with specific Ansible versions and collections

## Dynamic Inventory

```bash
# AWS EC2
ansible-inventory -i inventory/aws_ec2.yml --list

# Azure
# inventory/azure_rm.yml
plugin: azure.azcollection.azure_rm
auth_source: auto
include_vm_resource_groups:
  - myapp-prod-rg
keyed_groups:
  - key: tags.Role
    prefix: role

# GCP
# inventory/gcp_compute.yml
plugin: google.cloud.gcp_compute
projects:
  - my-gcp-project
zones:
  - us-central1-a
filters:
  - labels.managed_by = ansible
```

## Connection Plugins

```yaml
# SSH (default for Linux)
[linux_servers]
web1.example.com

# WinRM (Windows)
[windows_servers]
win1.example.com
[windows_servers:vars]
ansible_connection=winrm
ansible_winrm_transport=ntlm
ansible_port=5986
ansible_winrm_server_cert_validation=ignore

# Local (run on Ansible controller)
- name: Run locally
  ansible.builtin.command: echo "local task"
  delegate_to: localhost
  connection: local

# Network devices (network_cli)
[routers]
router1.example.com
[routers:vars]
ansible_connection=ansible.netcommon.network_cli
ansible_network_os=cisco.ios.ios
```

## Ansible for Networking

```yaml
- name: Configure Cisco IOS router
  hosts: routers
  gather_facts: false
  tasks:
    - name: Configure interface
      cisco.ios.ios_l3_interfaces:
        config:
          - name: GigabitEthernet0/1
            ipv4:
              - address: 192.168.1.1/24
        state: merged

    - name: Configure OSPF
      cisco.ios.ios_ospfv2:
        config:
          processes:
            - process_id: 1
              router_id: 1.1.1.1
              areas:
                - area_id: "0"
                  ranges:
                    - address: 192.168.0.0
                      netmask: 255.255.0.0

    - name: Save configuration
      cisco.ios.ios_config:
        save_when: modified
```

## Ansible vs Terraform

| Aspect | Ansible | Terraform |
|---|---|---|
| Primary use | Configuration management, app deployment | Infrastructure provisioning |
| Approach | Procedural (ordered task list) | Declarative (desired state) |
| State | Stateless (no state file) | Stateful (state file tracks resources) |
| Agent | Agentless (SSH/WinRM) | Agentless (API calls) |
| Strengths | OS config, app deploy, networking, runbooks | Cloud resource lifecycle management |
| Idempotency | Module-dependent (most are idempotent) | Built-in (plan/apply model) |
| Scope | Very broad (cloud, OS, network, apps) | Infrastructure-focused |
| Complementary? | Yes — configure what Terraform provisions | Yes — provision what Ansible configures |

Typical combined workflow: Terraform creates VMs, VPCs, load balancers. Ansible configures the OS, deploys applications, manages users, and handles ongoing configuration drift on those VMs.

---

## Common Decisions (ADR Triggers)

- **Ansible vs Terraform vs both**: Ansible excels at OS-level configuration and application deployment. Terraform excels at cloud infrastructure lifecycle. Most organizations benefit from both. Document the boundary: what Terraform manages vs what Ansible manages.
- **Static vs dynamic inventory**: Static inventories are simple but drift from reality. Dynamic inventory plugins auto-discover hosts but require cloud API access and proper tagging. Choose based on environment volatility.
- **AWX/AAP vs CLI-only**: AWX adds RBAC, scheduling, audit trails, and self-service. CLI-only is simpler and sufficient for small teams. Evaluate based on team size, compliance requirements, and self-service needs.
- **Role sourcing strategy**: Decide between writing roles from scratch, using Ansible Galaxy community roles, or maintaining a private automation hub. Community roles save time but may not meet security/compliance standards.
- **Vault strategy**: Single vault password for simplicity or multiple vault IDs per environment for security isolation. Consider who needs access to which secrets and how passwords are distributed.
- **Testing approach**: Molecule provides comprehensive role testing but adds CI time. Decide which roles require full Molecule testing (critical infrastructure roles) versus lighter-weight linting only.

---

## Reference Architectures

### Full-Stack Application Deployment

```
Playbook: site.yml
  |-- Play 1: Common (all hosts)
  |     |-- Role: common (NTP, SSH hardening, users, packages)
  |     |-- Role: monitoring_agent (Prometheus node_exporter)
  |
  |-- Play 2: Web Tier (webservers)
  |     |-- Role: nginx (reverse proxy, TLS termination)
  |     |-- Role: app_deploy (git clone, pip install, systemd service)
  |     |-- Handler: Restart nginx, Restart app
  |
  |-- Play 3: Database Tier (databases)
  |     |-- Role: postgresql (install, pg_hba.conf, replication)
  |     |-- Role: backup (pg_dump cron, S3 upload)
  |
  |-- Serial deployment: web tier uses serial: 1 for rolling updates
  |-- Vault: database passwords, TLS keys encrypted
```

### Network Automation

```
Inventory (dynamic + static)
  |-- Routers (Cisco IOS) — ansible_network_os: cisco.ios.ios
  |-- Switches (Arista EOS) — ansible_network_os: arista.eos.eos
  |-- Firewalls (Juniper) — ansible_network_os: junipernetworks.junos.junos
  |
Playbooks:
  |-- network_baseline.yml
  |     |-- NTP, syslog, SNMP, AAA configuration
  |     |-- Banner, password policies
  |
  |-- network_changes.yml
  |     |-- VLAN provisioning
  |     |-- ACL updates
  |     |-- OSPF/BGP neighbor configuration
  |     |-- Pre-change: backup running config
  |     |-- Post-change: verify connectivity, save config
  |
AWX Workflow:
  Backup --> Apply Changes --> Verify --> (on failure) Rollback
```

### Hybrid Cloud Configuration (Terraform + Ansible)

```
Phase 1: Terraform provisions infrastructure
  |-- VPC, subnets, security groups
  |-- EC2 instances, RDS, ALB
  |-- Outputs: instance IPs, RDS endpoint
  |-- Generates Ansible dynamic inventory tags

Phase 2: Ansible configures instances
  |-- Dynamic inventory discovers tagged EC2 instances
  |-- Role: base_os (hardening, patching, monitoring agent)
  |-- Role: app_server (runtime, application code, environment variables)
  |-- Role: log_shipping (Fluentd/Filebeat to central logging)
  |-- Variables: RDS endpoint from Terraform output or SSM Parameter Store

Phase 3: Ansible handles day-2 operations
  |-- Scheduled: compliance checks, patch reporting
  |-- On-demand: application deployments, config updates
  |-- Runbooks: incident response, failover procedures
```
