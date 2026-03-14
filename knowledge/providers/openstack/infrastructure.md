# OpenStack Infrastructure

## Checklist

- [ ] Is Nova configured with appropriate compute drivers (libvirt/KVM recommended for production), CPU pinning, NUMA topology awareness, and huge pages for performance-sensitive workloads?
- [ ] Are Nova availability zones and host aggregates defined to separate workload types (compute-optimized, memory-optimized, GPU) and provide failure domain isolation?
- [ ] Is Neutron configured with the appropriate network plugin? (ML2/OVS for general use, ML2/OVN for scale and performance, Contrail/Tungsten for SDN features)
- [ ] Are Neutron security groups configured per tenant with default-deny ingress rules, and is port security enabled to prevent MAC/IP spoofing?
- [ ] Is network segmentation implemented with provider networks (VLAN) for external connectivity and self-service networks (VXLAN/Geneve) for tenant isolation?
- [ ] Is Cinder configured with appropriate storage backends (Ceph RBD recommended for scale, LVM for simple deployments) with volume type and QoS policies defined?
- [ ] Are Cinder volume backups configured to a separate storage target (Swift, Ceph, NFS) with scheduled backup policies?
- [ ] Is Swift or Ceph RGW deployed for object storage with appropriate replication policies (3 replicas or erasure coding) and container ACLs?
- [ ] Is Keystone configured with federation (SAML, OIDC) or LDAP backend for enterprise identity integration instead of local SQL users?
- [ ] Are Keystone projects (tenants) provisioned with appropriate quotas for compute (cores, RAM, instances), storage (volumes, snapshots, gigabytes), and network (floating IPs, routers, networks)?
- [ ] Is Heat used for infrastructure-as-code orchestration, or is Terraform with the OpenStack provider preferred for consistency with multi-cloud deployments?
- [ ] Is Horizon deployed and secured with TLS, session timeout, and RBAC aligned with Keystone roles?
- [ ] Is tenant isolation verified at the network level (no cross-tenant traffic without explicit router or shared network), and are admin-only provider networks properly restricted?
- [ ] Is the control plane highly available with HAProxy/keepalived or pacemaker, MariaDB Galera cluster, and RabbitMQ clustering with quorum queues?
- [ ] Are OpenStack services monitored with appropriate health checks, and is Ceilometer/Gnocchi or Prometheus configured for metering and capacity planning?

## Why This Matters

OpenStack provides cloud-like infrastructure on premises but requires significant operational expertise. Unlike managed cloud services, every component (compute, network, storage, identity) must be explicitly configured and maintained. Neutron plugin selection affects network performance, scale limits, and available features. Cinder backend choice determines storage performance and data protection capabilities. Missing HA configuration for the control plane creates a single point of failure for the entire cloud. Tenant isolation relies on correct Neutron and Keystone configuration.

## Common Decisions (ADR Triggers)

- **Neutron plugin** -- ML2/OVS (mature, widely deployed) vs ML2/OVN (modern, better scale) vs commercial SDN (Contrail, NSX)
- **Storage backend** -- Ceph (unified block/object/file, scale-out) vs commercial SAN (Dell, Pure, NetApp) for Cinder
- **Deployment tool** -- Kolla-Ansible (containers) vs TripleO (OpenStack-on-OpenStack) vs Canonical MAAS + Juju vs Red Hat OpenStack Platform
- **Identity backend** -- Keystone SQL (simple) vs LDAP (enterprise) vs federated SAML/OIDC (multi-org)
- **Orchestration tool** -- Heat (native) vs Terraform (multi-cloud consistency) vs Ansible (procedural)
- **Networking model** -- provider networks (VLAN, operator-managed) vs self-service networks (VXLAN, tenant-managed), DVR vs centralized routing
- **Upgrade strategy** -- rolling upgrade (service-by-service) vs blue-green control plane, skip-level upgrade feasibility
- **Object storage** -- Swift (native, proven) vs Ceph RGW (unified with block storage), replication vs erasure coding
