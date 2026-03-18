# OpenStack Infrastructure

## Scope

Covers the foundational OpenStack infrastructure components: Nova (compute), Neutron (networking), Cinder (block storage), Swift (object storage), Keystone (identity), Horizon (dashboard), and control plane HA. This file provides an overview checklist; see dedicated files for deep-dive coverage of each service.

## Checklist

- [ ] **[Critical]** Is Nova configured with appropriate compute drivers (libvirt/KVM recommended for production), CPU pinning, NUMA topology awareness, and huge pages for performance-sensitive workloads?
- [ ] **[Critical]** Is Neutron configured with the appropriate network plugin? (ML2/OVN recommended for all new deployments; ML2/OVS deprecated since 2023.1 Antelope -- migrate to OVN; Contrail/Tungsten for SDN features)
- [ ] **[Critical]** Is Cinder configured with appropriate storage backends (Ceph RBD recommended for scale, LVM for simple deployments) with volume type and QoS policies defined?
- [ ] **[Critical]** Is Keystone configured with federation (SAML, OIDC) or LDAP backend for enterprise identity integration instead of local SQL users?
- [ ] **[Critical]** Is the control plane highly available with HAProxy/keepalived or pacemaker, MariaDB Galera cluster, and RabbitMQ clustering with quorum queues?
- [ ] **[Critical]** Is tenant isolation verified at the network level (no cross-tenant traffic without explicit router or shared network), and are admin-only provider networks properly restricted?
- [ ] **[Recommended]** Are Nova availability zones and host aggregates defined to separate workload types (compute-optimized, memory-optimized, GPU) and provide failure domain isolation?
- [ ] **[Recommended]** Are Neutron security groups configured per tenant with default-deny ingress rules, and is port security enabled to prevent MAC/IP spoofing?
- [ ] **[Recommended]** Is network segmentation implemented with provider networks (VLAN) for external connectivity and self-service networks (VXLAN/Geneve) for tenant isolation?
- [ ] **[Recommended]** Are Cinder volume backups configured to a separate storage target (Swift, Ceph, NFS) with scheduled backup policies?
- [ ] **[Recommended]** Are Keystone projects (tenants) provisioned with appropriate quotas for compute (cores, RAM, instances), storage (volumes, snapshots, gigabytes), and network (floating IPs, routers, networks)?
- [ ] **[Recommended]** Is Horizon deployed and secured with TLS, session timeout, and RBAC aligned with Keystone roles?
- [ ] **[Recommended]** Are OpenStack services monitored with appropriate health checks, and is Ceilometer/Gnocchi or Prometheus configured for metering and capacity planning?
- [ ] **[Optional]** Is Swift or Ceph RGW deployed for object storage with appropriate replication policies (3 replicas or erasure coding) and container ACLs?
- [ ] **[Optional]** Is Heat used for infrastructure-as-code orchestration, or is Terraform with the OpenStack provider preferred for consistency with multi-cloud deployments?

## Why This Matters

OpenStack provides cloud-like infrastructure on premises but requires significant operational expertise. Unlike managed cloud services, every component (compute, network, storage, identity) must be explicitly configured and maintained. Neutron plugin selection affects network performance, scale limits, and available features. Cinder backend choice determines storage performance and data protection capabilities. Missing HA configuration for the control plane creates a single point of failure for the entire cloud. Tenant isolation relies on correct Neutron and Keystone configuration.

## Common Decisions (ADR Triggers)

- **Neutron plugin** -- ML2/OVN (recommended default since 2023.1, distributed L3/DHCP) vs ML2/OVS (deprecated since 2023.1, migrate to OVN) vs commercial SDN (Contrail, NSX)
- **Storage backend** -- Ceph (unified block/object/file, scale-out) vs commercial SAN (Dell, Pure, NetApp) for Cinder
- **Deployment tool** -- Kolla-Ansible (containers) vs TripleO (deprecated -- replaced by RHOSO) vs Canonical MAAS + Juju vs RHOSO (Red Hat OpenStack Services on OpenShift)
- **Identity backend** -- Keystone SQL (simple) vs LDAP (enterprise) vs federated SAML/OIDC (multi-org)
- **Orchestration tool** -- Heat (native) vs Terraform (multi-cloud consistency) vs Ansible (procedural)
- **Networking model** -- provider networks (VLAN, operator-managed) vs self-service networks (VXLAN, tenant-managed), DVR vs centralized routing
- **Upgrade strategy** -- rolling upgrade (service-by-service) vs blue-green control plane, skip-level upgrade feasibility
- **Object storage** -- Swift (native, proven) vs Ceph RGW (unified with block storage), replication vs erasure coding

## Version Notes

| Release | Date | Key Infrastructure Changes |
|---|---|---|
| 2024.1 Caracal (29) | Apr 2024 | Secure RBAC default across all services, improved Ironic multi-tenant bare metal, OVN DPDK support |
| 2024.2 Dalmatian (30) | Oct 2024 | Ironic runbooks, OVN interconnection improvements, continued ML2/OVS deprecation |
| 2025.1 Epoxy (31) | Apr 2025 | TripleO officially retired (replaced by RHOSO); ML2/OVS deprecated with removal timeline published; Nova libvirt 10.x+ required; Cinder NVMe-oF improvements for multi-path HA; Keystone OAuth 2.0 device authorization grant |
| 2025.2 Flamingo (32) | Oct 2025 | ML2/OVS removal planned for next cycle; OVN 24.09+ required; Nova vGPU live migration improvements; Ironic secure boot enhancements; Barbican KMIP backend improvements |

## Reference Architectures

- [OpenStack Architecture Design Guide](https://docs.openstack.org/arch-design/) -- official architecture guide covering compute, storage, networking, and multi-site design
- [OpenStack Deployment Guides](https://docs.openstack.org/project-deploy-guide/) -- step-by-step deployment architectures for Kolla-Ansible, TripleO, and other deployment tools
- [OpenStack Reference Architecture: Ceph integration](https://docs.openstack.org/cinder/latest/configuration/block-storage/drivers/ceph-rbd-volume-driver.html) -- reference design for Ceph as unified storage backend for Cinder, Glance, and Manila
- [OpenStack High Availability Guide](https://docs.openstack.org/ha-guide/) -- reference architecture for HA control plane, database clustering, and message queue resilience
- [Red Hat OpenStack Platform Reference Architecture](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/) -- enterprise-supported deployment architectures with director-based installation and lifecycle management

## See Also

- `general/compute.md` -- general compute architecture patterns
- `general/hardware-sizing.md` -- hardware sizing for OpenStack hosts
- `providers/openstack/deployment-tools.md` -- deployment tool selection
- `providers/openstack/control-plane-ha.md` -- control plane HA architecture
