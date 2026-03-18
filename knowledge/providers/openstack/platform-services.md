# OpenStack Platform Services (Heat, Magnum, Trove, Ironic, and Others)

## Scope

Covers OpenStack platform services beyond core IaaS: Heat orchestration, Magnum container orchestration, Trove database-as-a-service, Ironic bare metal provisioning, Sahara data processing (retired), Senlin clustering (retired), Zaqar messaging (retired), and integration with external tools (Terraform, Ansible).

## Checklist

- [ ] **[Critical]** Is Heat deployed for infrastructure orchestration? (HOT template format, `heat_template_version` pinned to a specific release for stability, nested stacks for modularity via `OS::Heat::ResourceGroup` and `type: nested_template.yaml`, environment files for parameter separation)
- [ ] **[Critical]** Is Terraform with the OpenStack provider considered as an alternative or complement to Heat? (Terraform provides multi-cloud consistency, state management, plan/apply workflow, drift detection -- Heat is native but OpenStack-only)
- [ ] **[Recommended]** Are Heat autoscaling policies configured? (`OS::Heat::AutoScalingGroup` with `OS::Heat::ScalingPolicy`, Ceilometer or Aodh alarms as triggers, cooldown periods set to prevent scaling thrash, `min_size`/`max_size`/`desired_capacity` defined)
- [ ] **[Recommended]** Is Heat stack lifecycle managed? (stack update for in-place changes, `OS::Heat::SoftwareConfig` and `OS::Heat::SoftwareDeployment` for post-boot configuration, `OS::Heat::WaitCondition` for orchestration sequencing, stack abandon for resource handoff without deletion)
- [ ] **[Recommended]** Is Magnum deployed for container orchestration? (Kubernetes cluster templates with `openstack coe cluster template create`, choice of `coe` type: kubernetes/swarm/mesos, `network-driver` flannel or calico, `volume-driver` cinder, master and node flavor selection)
- [ ] **[Recommended]** Are Magnum cluster templates hardened? (TLS enabled by default, `master-lb-enabled` for HA control plane, `floating-ip-enabled` only when needed, `docker-storage-driver` overlay2 recommended, node auto-scaling via Magnum auto-heal and cluster resize)
- [ ] **[Recommended]** Is Trove deployed for database-as-a-service? (supported datastores: MySQL, MariaDB, PostgreSQL; guest agent configuration for backup, replication, and clustering)
- [ ] **[Recommended]** Are Trove database instances properly configured? (flavor selection appropriate for database workload, Cinder volume for data persistence, automated backups to Swift with retention policy, replication for read replicas, configuration groups for tuning parameters)
- [ ] **[Recommended]** Is Ironic deployed for bare metal provisioning? (inspection via `ironic-inspector` for hardware discovery, cleaning policies between tenants via `automated_clean = True`, PXE/iPXE boot configuration, IPMI/iLO/iDRAC driver for out-of-band management)
- [ ] **[Recommended]** Are Ironic node resources mapped to Nova scheduling? (bare metal flavor with `resources:CUSTOM_BAREMETAL_*` resource class, `resource_class` set per Ironic node, Nova `ComputeFilter` and `BaremetalOvercommitFilter` in scheduler)
- [ ] **[Recommended]** Is Ansible OpenStack collection (`openstack.cloud`) used for operational automation? (module-per-resource approach, `os_server`, `os_network`, `os_security_group`, complements Heat/Terraform for day-2 operations and configuration management)
- [ ] **[Optional]** Is Sahara evaluated for data processing needs? (Retired since Wallaby -- use Kubernetes-based Spark on Magnum instead for Hadoop/Spark workloads)
- [ ] **[Optional]** Is Senlin evaluated for cluster management? (Retired since Yoga -- use Heat autoscaling with Aodh alarms or Kubernetes HPA via Magnum for auto-scaling needs)
- [ ] **[Optional]** Is Zaqar evaluated for messaging needs? (Retired since Xena -- use external messaging services such as RabbitMQ or Kafka for event-driven architectures)

## Why This Matters

Platform services transform OpenStack from raw IaaS into a platform that offers managed databases, container orchestration, and bare metal provisioning as self-service capabilities. Without Heat or Terraform, infrastructure deployments are manual and non-repeatable. Magnum provides a supported path to Kubernetes on OpenStack, but cluster template configuration significantly affects security and performance -- misconfigured templates can expose the Docker socket or use insecure registries. Trove eliminates the operational burden of database management for tenants but requires careful flavor and volume sizing to prevent performance problems. Ironic enables bare metal workloads (HPC, ML training, licensed software requiring physical CPU counts) but introduces physical provisioning complexity including PXE networking, IPMI access, and hardware cleaning between tenants. Choosing between Heat and Terraform affects team skill requirements and multi-cloud portability.

## Common Decisions (ADR Triggers)

- **Orchestration tool** -- Heat (native, HOT templates, tightly integrated with Ceilometer for autoscaling) vs Terraform (multi-cloud, state file management, plan/apply workflow) vs Ansible (procedural, good for day-2) vs Pulumi (programming language SDKs) -- team skills and multi-cloud strategy
- **Container platform** -- Magnum-managed Kubernetes (OpenStack-integrated, Cinder CSI, Octavia ingress) vs self-managed Kubernetes on VMs (more control, more work) vs bare metal Kubernetes via Ironic (highest performance) -- operational ownership and integration depth
- **Database service** -- Trove managed databases (tenant self-service, automated backups, replication) vs databases in VMs (full control, tenant-managed) vs external managed database service -- operational delegation vs control
- **Bare metal strategy** -- Ironic for tenant-facing bare metal (multi-tenant, Nova-integrated scheduling) vs Ironic for infrastructure provisioning only (control plane deployment) vs no bare metal (all workloads virtualized) -- workload requirements and hardware management
- **Autoscaling approach** -- Heat autoscaling with Aodh alarms (native, simple) vs Kubernetes HPA via Magnum (container-native) -- Senlin is retired; workload type and scaling complexity drive this
- **Configuration management** -- `OS::Heat::SoftwareConfig` (Heat-native, cloud-init based) vs Ansible post-provision (flexible, idempotent) vs Packer pre-baked images (immutable infrastructure) -- deployment speed vs flexibility trade-off
- **Data processing** -- Kubernetes-based data processing (Spark on K8s via Magnum, recommended) vs tenant-managed clusters on VMs (more control) -- Sahara is retired

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) | 2025.1 Epoxy (31) | 2025.2 Flamingo (32) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Heat convergence engine | Tech Preview | GA | GA (default) | GA (default) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Heat template version | 2017-09-01 | 2018-03-02 | 2018-08-31 | 2018-08-31 | 2018-08-31 | 2018-08-31 | 2018-08-31 | 2021-04-16 | 2021-04-16 | 2021-04-16 | 2021-04-16 | 2021-04-16 | 2021-04-16 | 2021-04-16 | 2021-04-16 | 2021-04-16 | 2021-04-16 |
| Heat external resource types | Not available | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Magnum K8s version | K8s 1.7-1.8 | K8s 1.9-1.11 | K8s 1.11-1.12 | K8s 1.13-1.14 | K8s 1.15-1.16 | K8s 1.17-1.18 | K8s 1.18-1.19 | K8s 1.20-1.21 | K8s 1.21-1.23 | K8s 1.23-1.24 | K8s 1.24-1.25 | K8s 1.25-1.27 | K8s 1.27-1.28 | K8s 1.28-1.29 | K8s 1.29-1.30 | K8s 1.30-1.31 | K8s 1.31-1.32 |
| Magnum cluster driver | Fedora Atomic | Fedora Atomic | Fedora CoreOS (migration) | Fedora CoreOS | Fedora CoreOS | Fedora CoreOS (default) | Fedora CoreOS | Fedora CoreOS | Fedora CoreOS / Ubuntu | Fedora CoreOS / Ubuntu | Ubuntu (default) | Ubuntu (default) | Ubuntu (default) | Ubuntu (default) | Ubuntu (default) | Ubuntu (default) | Ubuntu (default) |
| Magnum auto-healing | Not available | Not available | Not available | Tech Preview | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Magnum cluster upgrades | Not available | Not available | Not available | Not available | Tech Preview | Tech Preview | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Trove instance management | GA | GA | GA | GA | GA | GA (major redesign) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Trove supported datastores | MySQL, MariaDB, PostgreSQL, MongoDB, Redis, Cassandra | Same | Same | Same | Same | MySQL, MariaDB, PostgreSQL (simplified) | Same | Same | Same | Same | Same | Same | Same | Same | Same | Same | Same |
| Ironic standalone (without Nova) | Tech Preview | GA | GA | GA (improved) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Ironic BIOS configuration | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Ironic deploy steps | Not available | Not available | Introduced | GA (fast-track) | GA (deploy templates) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Ironic firmware updates | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Tech Preview | GA | GA | GA (improved) | GA | GA | GA | GA | GA |
| Ironic sharding | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Introduced | GA | GA | GA | GA | GA |
| Senlin clustering | GA | GA | GA | GA | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Retired | Retired |
| Sahara data processing | GA | GA | GA | GA | Maintenance mode | Maintenance mode | Maintenance mode | Retired | Retired | Retired | Retired | Retired | Retired | Retired | Retired | Retired | Retired |
| Zaqar messaging | GA | GA | GA | GA | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Retired | Retired | Retired | Retired | Retired | Retired | Retired | Retired | Retired |

**Key changes across releases:**
- **Heat convergence engine:** The convergence engine, which enables parallel resource creation and more efficient stack updates, was tech preview in Pike, GA in Queens, and became the default in Rocky. It replaces the legacy stack-based engine with a graph-based approach that improves update performance and reliability.
- **Magnum Kubernetes version support:** Magnum tracks upstream Kubernetes releases with a delay of 1-2 minor versions. The cluster base OS migrated from Fedora Atomic to Fedora CoreOS (Rocky-Ussuri) and then to Ubuntu as the default (Zed+). Each release supports 2-3 Kubernetes minor versions. Cluster in-place upgrades became GA in Victoria. Epoxy (2025.1) supports K8s 1.30-1.31, Flamingo (2025.2) supports K8s 1.31-1.32.
- **Trove redesign (Ussuri):** Trove underwent a major architectural redesign in Ussuri, simplifying the guest agent and reducing the number of supported datastores to MySQL, MariaDB, and PostgreSQL (dropping MongoDB, Redis, Cassandra support). The redesign improved reliability and reduced operational complexity.
- **Ironic standalone improvements:** Ironic standalone mode (without Nova integration) has been GA since Queens, enabling use cases like infrastructure provisioning and edge computing. Fast-track deployment (Stein) dramatically reduced provisioning time by skipping cleaning for trusted workloads. Deploy templates (Train) enabled reusable provisioning configurations. Sharding (2023.1) enabled scaling Ironic conductors across large deployments.
- **Senlin status:** Senlin (clustering service for auto-scaling with rich policies) entered maintenance mode in Train due to declining community activity. It is effectively retired as of Yoga and fully retired in Epoxy (2025.1). Organizations needing auto-scaling should use Heat autoscaling with Aodh alarms or Kubernetes HPA via Magnum.
- **Sahara and Zaqar retirement:** Sahara (data processing) entered maintenance mode in Train and was retired in Wallaby. Zaqar (messaging service) entered maintenance mode in Train and was retired in Xena. For data processing, Kubernetes-based Spark on Magnum is the recommended alternative. For messaging, external services (RabbitMQ, Kafka) are recommended.
- **Epoxy (2025.1) platform services changes:** Magnum supports K8s 1.30-1.31. Senlin fully retired. Continued Ironic runbook improvements.
- **Flamingo (2025.2) platform services changes:** Magnum supports K8s 1.31-1.32. Continued Ironic secure boot enhancements. Heat template engine stability improvements.

## See Also

- `providers/openstack/infrastructure.md` -- core OpenStack infrastructure
- `providers/openstack/heat.md` -- Heat orchestration deep dive
- `providers/openstack/compute.md` -- Nova compute and Ironic bare metal
- `providers/kubernetes/compute.md` -- Kubernetes workloads via Magnum
