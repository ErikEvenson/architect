# Nutanix Platform Services

## Scope

Higher-level Nutanix platform services layered on top of core infrastructure: object storage (Objects), file services (Files), Kubernetes management, automation/self-service, database-as-a-service, hybrid cloud (NC2), and governance via categories and playbooks.

## Checklist

- [ ] [Recommended] Is Nutanix Objects deployed for S3-compatible object storage use cases (backup targets, log aggregation, data lake landing zone), with WORM (Write Once Read Many) policies enabled for immutable backup copies?
- [ ] [Recommended] Are Nutanix Objects buckets configured with lifecycle policies to tier cold data or expire old objects, and are access policies using IAM-style bucket and user policies rather than open access?
- [ ] [Recommended] Is Nutanix Files deployed for SMB and NFS file share requirements, with the file server VM sized appropriately (minimum 3 FSVMs for HA, 12 vCPUs and 32 GB RAM per FSVM for production)?
- [ ] [Recommended] Are Nutanix Files quotas configured at the share and user level to prevent storage sprawl, with File Analytics enabled for audit trails, usage reporting, and anomalous access detection?
- [ ] [Recommended] Is Nutanix Kubernetes Management (formerly NKE/Karbon) evaluated for containerized workloads, with node OS image updates, etcd backup policies, and Nutanix CSI driver configured for persistent volume provisioning?
- [ ] [Recommended] Are Nutanix Kubernetes Management clusters configured with separate node pools for system components (etcd, control plane) and worker nodes, with auto-scaling enabled for worker pools based on resource demand?
- [ ] [Recommended] Is NCM Self-Service (formerly Calm) deployed for infrastructure-as-code and application lifecycle management, with blueprints version-controlled in Git and marketplace items published for self-service provisioning?
- [ ] [Recommended] Are NCM Self-Service blueprints using Nutanix-native provider actions (VM create, snapshot, scale) combined with script tasks (shell, PowerShell, Python) for end-to-end application deployment automation?
- [ ] [Recommended] Is Nutanix Database Service (NDB, formerly Era) configured for database-as-a-service, with software profiles (OS + DB engine), compute profiles, network profiles, and time machine (continuous data protection) policies for provisioned databases?
- [ ] [Recommended] Are NDB clones used for development and testing environments to provide space-efficient, writable copies of production databases that refresh on schedule without consuming proportional storage?
- [ ] [Recommended] Are Prism Central categories (key:value pairs) applied consistently across VMs, with a defined taxonomy (Environment:Production, AppType:WebServer, Team:Engineering) enforced through NCM Self-Service (formerly Calm) or API automation?
- [ ] [Optional] Is Nutanix Clusters (NC2) on public cloud (AWS/Azure) evaluated for hybrid cloud use cases -- cloud bursting, DR to cloud, or lift-and-shift migration with consistent management through Prism Central?
- [ ] [Optional] Are Prism Central custom reports and playbooks configured for automated remediation (e.g., power off idle VMs, alert on snapshot sprawl, auto-tag untagged VMs)?

## Why This Matters

Nutanix platform services transform a hyperconverged cluster from basic compute and storage into a full private cloud platform. Objects provides S3-compatible storage without deploying a separate MinIO or Ceph cluster, and its WORM capability is critical for ransomware-resilient backup targets (required by most cyber insurance policies). Files replaces traditional Windows file servers or NetApp filers with a scale-out, Nutanix-integrated file service that inherits the cluster's data protection and DR capabilities. Nutanix Kubernetes Management (formerly NKE/Karbon) provides managed Kubernetes without the operational overhead of kubeadm or Rancher, but locks Kubernetes lifecycle management to Nutanix's release cadence. NCM Self-Service (formerly Calm) provides application automation comparable to Terraform + Ansible but integrated into Prism Central's RBAC and governance model. Nutanix Database Service (NDB, formerly Era) turns database provisioning from a weeks-long process into minutes, with continuous data protection that enables point-in-time recovery and space-efficient clones. Category taxonomy is the foundation for Flow policies, NCM Self-Service automation, and Prism Central reporting -- poor taxonomy undermines all three capabilities.

## Common Decisions (ADR Triggers)

- **Object storage** -- Nutanix Objects (integrated, S3-compatible, WORM) vs standalone MinIO (open source, multi-platform) vs cloud S3/Blob (offsite, pay-per-use)
- **File services** -- Nutanix Files (integrated, DR-capable, analytics) vs Windows File Server VMs (familiar, AD-native) vs NetApp ONTAP Select (enterprise features, additional licensing)
- **Kubernetes platform** -- Nutanix Kubernetes Management (formerly NKE/Karbon, Nutanix-managed, simple) vs Rancher (multi-cluster, multi-provider) vs OpenShift (enterprise Kubernetes, Red Hat ecosystem) vs upstream kubeadm (maximum flexibility)
- **Automation platform** -- NCM Self-Service (formerly Calm, Prism-integrated, blueprint marketplace) vs Terraform + Ansible (open source, multi-cloud) vs vRealize Automation (VMware ecosystem)
- **Database management** -- Nutanix Database Service (NDB, formerly Era, DBaaS, clone-based dev/test, continuous protection) vs manual DBA provisioning vs cloud-managed databases (RDS, Azure SQL)
- **Hybrid cloud strategy** -- NC2 on AWS/Azure (consistent Nutanix management) vs native cloud VMs (cloud-native tools) vs VMware Cloud on AWS (VMware ecosystem continuity)
- **Category governance** -- Enforced via NCM Self-Service blueprints (tags applied at provisioning) vs Prism Central playbooks (auto-tag based on rules) vs manual tagging (error-prone, inconsistent)

## Version Notes

| Feature | Previous Versions | Current / Latest |
|---|---|---|
| Nutanix Kubernetes Management (formerly NKE/Karbon) | Karbon 2.x (K8s 1.22-1.25) | NKM 3.x (K8s 1.26-1.30, renamed from NKE/Karbon) |
| Nutanix Objects | Objects 3.x (S3 basic) | Objects 4.x (improved IAM, versioning, WORM 2.0) |
| NC2 on AWS | GA (limited regions) | GA (expanded regions, improved networking) |
| NC2 on Azure | Not available | GA (Azure integration, ExpressRoute support) |
| NCM Self-Service (formerly Calm) | Calm 3.x (blueprints, marketplace) | NCM Self-Service 4.x (improved runbooks, Terraform integration) |
| Nutanix Database Service (NDB, formerly Era) | Era 2.x (PostgreSQL, MySQL, SQL Server, Oracle) | NDB 2.5+ (improved cloning, multi-cluster, SAP HANA) |
| Prism Central | PC 2022.x | PC 7.5 (improved UI, playbooks, reporting) |
| Nutanix Files | Files 4.x | Files 4.3+ (improved analytics, ransomware detection) |
| AHV | AHV 20220304.x | AHV 11.0 (improved live migration, GPU support enhancements) |
| Nutanix Data Lens | Not available | GA (SaaS-based analytics, replaces on-prem File Analytics) |
| Nutanix Unified Storage | Individual products | Unified Storage 4.x (Files + Objects + Block unified licensing) |

**Key changes across versions:**
- **Nutanix Kubernetes Management (formerly NKE/Karbon):** Rebranded from NKE (Nutanix Kubernetes Engine) to Nutanix Kubernetes Management. Supports Kubernetes 1.26-1.30, adds improved node pool management, and provides better integration with Prism Central categories for network policies. The Nutanix CSI driver supports volume snapshots and expansion.
- **Objects 4.x:** Significant improvements to IAM policies with more granular bucket and object-level permissions. WORM 2.0 adds legal hold and governance mode in addition to compliance mode. Object versioning is now GA. Performance improvements for small-object workloads.
- **NC2 availability:** Nutanix Cloud Clusters (NC2) expanded from AWS-only to include Azure. NC2 on Azure provides native integration with Azure networking (VNet, ExpressRoute) and allows extending Nutanix clusters to Azure for DR, cloud bursting, and migration. Both platforms are managed through Prism Central.
- **NCM Self-Service and NDB updates:** NCM Self-Service (formerly Calm) 4.x added native Terraform provider integration, allowing blueprints to orchestrate Terraform plans. NDB (formerly Era) 2.5+ added support for SAP HANA databases, improved multi-cluster database management, and faster clone refresh operations.
- **Unified Storage licensing:** Nutanix consolidated Files, Objects, and Block (Volume Groups) into a single Unified Storage license, simplifying procurement for customers using multiple storage services.
- **AHV 11.0:** Improved live migration performance with reduced vCPU stun times, GPU support enhancements for vGPU profiles, and improved VM placement algorithms.
- **Prism Central 7.5:** Updated UI with improved dashboards, enhanced playbook capabilities, and better multi-cluster reporting.
- **AOS 7.5 (December 2025):** VM Startup Policies for controlled boot sequencing, enhanced CVM security with improved integrity validation.
