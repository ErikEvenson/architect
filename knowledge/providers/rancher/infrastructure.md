# Rancher Infrastructure

## Checklist

- [ ] Design Rancher server high-availability deployment: 3-node RKE2 cluster dedicated to Rancher management, separate from downstream workload clusters
- [ ] Choose downstream cluster distribution: RKE2 (FIPS-compliant, SELinux-compatible, production-grade) vs K3s (lightweight, edge/IoT, ARM support, single binary)
- [ ] Plan cluster provisioning model: custom clusters (bring your own nodes), node driver (Rancher provisions VMs via cloud API), or hosted clusters (import existing EKS/GKE/AKS)
- [ ] Evaluate Fleet for GitOps-based multi-cluster application deployment: GitRepo resources, cluster selectors, bundle lifecycle, and dependency management
- [ ] Design multi-cluster management topology: single Rancher instance managing clusters across regions/clouds, plan for network connectivity and latency requirements
- [ ] Assess Harvester HCI for bare-metal virtualization: VM lifecycle management, nested Kubernetes clusters (Harvester guest clusters), integration with Rancher for unified management
- [ ] Evaluate Longhorn for distributed block storage: replica count, data locality, backup targets (S3/NFS), disaster recovery volumes, and ReadWriteMany support (via NFS)
- [ ] Configure Rancher monitoring stack (based on Prometheus Operator): cluster monitoring, project monitoring, Grafana dashboards, and alert routing per project/namespace
- [ ] Plan Rancher logging stack (based on Fluent Bit/Fluentd): cluster-level and project-level log collection, output configuration (Elasticsearch, Splunk, Kafka, Syslog)
- [ ] Design authentication integration: external auth providers (Active Directory, LDAP, SAML, OIDC, GitHub, Azure AD), local auth for break-glass, and group-to-project mappings
- [ ] Plan Rancher backup and migration: rancher-backup operator for Rancher server state, etcd snapshots for downstream clusters, disaster recovery procedures
- [ ] Configure CIS hardening: RKE2 CIS 1.6/1.23 profile, Rancher CIS Benchmark scanning for downstream clusters, remediation tracking

## Why This Matters

Rancher provides a unified management plane for Kubernetes clusters across any infrastructure: public cloud, private data center, edge locations, and bare metal. Without Rancher (or equivalent tooling), organizations managing multiple Kubernetes clusters face fragmented visibility, inconsistent security policies, duplicated operational effort per cluster, and manual GitOps configuration. Rancher's value increases with the number of clusters: it centralizes authentication, RBAC, monitoring, logging, and policy enforcement. The choice between RKE2 and K3s determines the operational profile of downstream clusters: RKE2 is designed for security-sensitive, production environments (FIPS 140-2, SELinux, CIS hardened by default), while K3s targets edge and resource-constrained environments. Fleet extends Rancher's multi-cluster capabilities to application deployment, enabling consistent GitOps across hundreds of clusters. Harvester and Longhorn complete the SUSE/Rancher stack for organizations seeking a fully open-source infrastructure platform.

## Common Decisions (ADR Triggers)

- **RKE2 vs K3s for downstream clusters**: RKE2 is a full Kubernetes distribution with embedded etcd, containerd, and FIPS-validated cryptographic libraries. It is designed for production and government workloads. K3s is a lightweight distribution using SQLite (single-node) or external database (HA), with a smaller binary and lower resource requirements. Use RKE2 for production data center workloads; K3s for edge, IoT, development, and resource-constrained environments. Both are CNCF-certified Kubernetes distributions.
- **Rancher-provisioned vs imported clusters**: Rancher can provision clusters from scratch (creating VMs via node drivers, installing Kubernetes) or import existing clusters (EKS, GKE, AKS, or any conformant cluster). Provisioned clusters have deeper Rancher integration (node management, etcd snapshots, Kubernetes upgrades via UI). Imported clusters retain their existing lifecycle management. Provision for new clusters; import for existing managed Kubernetes (EKS/GKE/AKS) where the cloud provider manages the control plane.
- **Fleet vs ArgoCD for multi-cluster GitOps**: Fleet is built into Rancher and designed for multi-cluster deployment at scale (cluster selectors, automatic bundle deployment to matching clusters). ArgoCD has a richer single-cluster experience (UI, RBAC, ApplicationSets, health checks). Use Fleet when Rancher is the management plane and multi-cluster is the primary concern; ArgoCD when advanced per-cluster GitOps features are needed. They can coexist (Fleet for infrastructure, ArgoCD for applications).
- **Longhorn vs cloud-native storage vs Rook/Ceph**: Longhorn is simple to deploy (Helm chart), integrates with Rancher UI, and provides built-in backup/DR. But it has lower performance than direct cloud storage (EBS, GCE PD) and less scalability than Ceph. Use Longhorn for on-premises clusters needing distributed storage without Ceph complexity; cloud-native CSI for cloud clusters; Rook/Ceph for large-scale on-premises with dedicated storage nodes.
- **Harvester vs traditional virtualization (VMware, Proxmox)**: Harvester provides Kubernetes-native VM management, nested K8s clusters, and integration with Rancher. But it is younger than VMware with a smaller feature set (no vMotion equivalent, limited VM migration). Use Harvester for greenfield bare-metal deployments wanting an open-source HCI stack; VMware for existing enterprise environments with established operational practices.
- **Single Rancher instance vs multiple**: A single Rancher instance can manage clusters globally, simplifying authentication and policy. Multiple instances provide isolation and regional autonomy. Use a single instance for most organizations; multiple only when regulatory requirements mandate separate management planes (e.g., government vs commercial, different countries with data sovereignty).

## Reference Architectures

### Enterprise Multi-Cluster Deployment
```
[Rancher Management Cluster (3-node RKE2 HA)]
  - Rancher Server
  - Fleet Controller
  - Rancher Monitoring (self-monitoring)
  - rancher-backup operator
  - Auth: Azure AD (SAML) + local admin (break-glass)
        |
  +-----+------+------+------+
  |            |            |            |
[RKE2 Cluster] [RKE2 Cluster] [K3s Cluster] [Imported EKS]
(Production)   (Staging)      (Edge Sites)  (AWS Workloads)
  - 3 CP + N workers  - 3 CP + N workers  - Single node per site  - Managed CP
  - Longhorn storage   - Longhorn storage  - Local PV              - EBS CSI
  - CIS hardened       - CIS hardened      - Minimal monitoring    - Full monitoring
  - Full monitoring    - Full monitoring
        |
  [Fleet GitRepo Resources]
  - infra-bundle: monitoring, logging, policies (all clusters)
  - app-bundle: applications (cluster selector: env=production)
  - edge-bundle: edge agents (cluster selector: type=edge)
```
Dedicated Rancher management cluster isolated from workloads. Fleet deploys infrastructure bundles (monitoring, logging, security policies) to all clusters and application bundles selectively based on cluster labels. Authentication centralized through Rancher with Azure AD, granting appropriate project/namespace access based on group membership.

### Harvester HCI + Rancher Stack
```
[Bare Metal Servers (3+ nodes)]
        |
  [Harvester HCI Cluster]
  - VM management (KubeVirt)
  - VLAN networking
  - Longhorn storage (built-in)
  - Image management (cloud images, ISOs)
        |
  +-----+------+
  |            |
[Rancher VM]  [Guest K8s Clusters]
(Management)  (RKE2 on Harvester VMs)
  |                 |
  +--------+--------+
           |
     [Rancher Server]
     - Manages Harvester cluster (VM lifecycle)
     - Manages guest K8s clusters (workload lifecycle)
     - Unified UI for VMs + containers
```
Harvester provides the bare-metal virtualization layer. Rancher server runs as a VM on Harvester (or separately). Rancher manages both the Harvester cluster (for VM operations) and guest Kubernetes clusters running on Harvester VMs. This creates a fully open-source infrastructure stack from bare metal to container orchestration.

### Edge Deployment at Scale (K3s + Fleet)
```
[Central Rancher + Fleet]
        |
  [Fleet GitRepo: edge-apps]
  - Cluster selector: location-type=edge
  - Helm chart with per-cluster values
        |
  +-----+------+------+------+------+
  |          |          |          |          |
[K3s]     [K3s]     [K3s]     [K3s]     [K3s]    ... (100s of sites)
(Site A)  (Site B)  (Site C)  (Site D)  (Site E)
  - Single node or 3-node HA
  - ARM64 or x86
  - Embedded SQLite or external DB
  - Agent phones home to Rancher
  - Fleet applies desired state
  - Local PV for storage
  - Minimal resource footprint (~512MB RAM)

[Fleet Bundle Customization]
  fleet.yaml:
    targetCustomizations:
      - name: high-traffic-sites
        clusterSelector:
          matchLabels:
            tier: high-traffic
        helm:
          values:
            replicas: 3
            resources.requests.memory: 512Mi
      - name: low-traffic-sites
        clusterSelector:
          matchLabels:
            tier: low-traffic
        helm:
          values:
            replicas: 1
            resources.requests.memory: 128Mi
```
K3s provides lightweight Kubernetes at each edge site with minimal resource requirements. Fleet manages application deployment from central Rancher, using cluster selectors and target customizations to adapt configurations per site characteristics. Each K3s agent registers with Rancher via an outbound connection (no inbound firewall rules needed at edge sites). Fleet handles intermittent connectivity gracefully, reconciling state when sites reconnect.
