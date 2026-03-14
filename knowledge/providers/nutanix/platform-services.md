# Nutanix Platform Services

## Checklist

- [ ] Is Nutanix Objects deployed for S3-compatible object storage use cases (backup targets, log aggregation, data lake landing zone), with WORM (Write Once Read Many) policies enabled for immutable backup copies?
- [ ] Are Nutanix Objects buckets configured with lifecycle policies to tier cold data or expire old objects, and are access policies using IAM-style bucket and user policies rather than open access?
- [ ] Is Nutanix Files deployed for SMB and NFS file share requirements, with the file server VM sized appropriately (minimum 3 FSVMs for HA, 12 vCPUs and 32 GB RAM per FSVM for production)?
- [ ] Are Nutanix Files quotas configured at the share and user level to prevent storage sprawl, with File Analytics enabled for audit trails, usage reporting, and anomalous access detection?
- [ ] Is Nutanix Karbon (NKE -- Nutanix Kubernetes Engine) evaluated for containerized workloads, with node OS image updates, etcd backup policies, and Nutanix CSI driver configured for persistent volume provisioning?
- [ ] Are NKE clusters configured with separate node pools for system components (etcd, control plane) and worker nodes, with auto-scaling enabled for worker pools based on resource demand?
- [ ] Is Nutanix Calm deployed for infrastructure-as-code and application lifecycle management, with blueprints version-controlled in Git and marketplace items published for self-service provisioning?
- [ ] Are Calm blueprints using Nutanix-native provider actions (VM create, snapshot, scale) combined with script tasks (shell, PowerShell, Python) for end-to-end application deployment automation?
- [ ] Is Nutanix Era configured for database-as-a-service, with software profiles (OS + DB engine), compute profiles, network profiles, and time machine (continuous data protection) policies for provisioned databases?
- [ ] Are Era clones used for development and testing environments to provide space-efficient, writable copies of production databases that refresh on schedule without consuming proportional storage?
- [ ] Are Prism Central categories (key:value pairs) applied consistently across VMs, with a defined taxonomy (Environment:Production, AppType:WebServer, Team:Engineering) enforced through Calm or API automation?
- [ ] Is Nutanix Clusters (NC2) on public cloud (AWS/Azure) evaluated for hybrid cloud use cases -- cloud bursting, DR to cloud, or lift-and-shift migration with consistent management through Prism Central?
- [ ] Are Prism Central custom reports and playbooks configured for automated remediation (e.g., power off idle VMs, alert on snapshot sprawl, auto-tag untagged VMs)?

## Why This Matters

Nutanix platform services transform a hyperconverged cluster from basic compute and storage into a full private cloud platform. Objects provides S3-compatible storage without deploying a separate MinIO or Ceph cluster, and its WORM capability is critical for ransomware-resilient backup targets (required by most cyber insurance policies). Files replaces traditional Windows file servers or NetApp filers with a scale-out, Nutanix-integrated file service that inherits the cluster's data protection and DR capabilities. Karbon/NKE provides managed Kubernetes without the operational overhead of kubeadm or Rancher, but locks Kubernetes lifecycle management to Nutanix's release cadence. Calm provides application automation comparable to Terraform + Ansible but integrated into Prism Central's RBAC and governance model. Era turns database provisioning from a weeks-long process into minutes, with continuous data protection that enables point-in-time recovery and space-efficient clones. Category taxonomy is the foundation for Flow policies, Calm automation, and Prism Central reporting -- poor taxonomy undermines all three capabilities.

## Common Decisions (ADR Triggers)

- **Object storage** -- Nutanix Objects (integrated, S3-compatible, WORM) vs standalone MinIO (open source, multi-platform) vs cloud S3/Blob (offsite, pay-per-use)
- **File services** -- Nutanix Files (integrated, DR-capable, analytics) vs Windows File Server VMs (familiar, AD-native) vs NetApp ONTAP Select (enterprise features, additional licensing)
- **Kubernetes platform** -- NKE/Karbon (Nutanix-managed, simple) vs Rancher (multi-cluster, multi-provider) vs OpenShift (enterprise Kubernetes, Red Hat ecosystem) vs upstream kubeadm (maximum flexibility)
- **Automation platform** -- Nutanix Calm (Prism-integrated, blueprint marketplace) vs Terraform + Ansible (open source, multi-cloud) vs vRealize Automation (VMware ecosystem)
- **Database management** -- Nutanix Era (DBaaS, clone-based dev/test, continuous protection) vs manual DBA provisioning vs cloud-managed databases (RDS, Azure SQL)
- **Hybrid cloud strategy** -- NC2 on AWS/Azure (consistent Nutanix management) vs native cloud VMs (cloud-native tools) vs VMware Cloud on AWS (VMware ecosystem continuity)
- **Category governance** -- Enforced via Calm blueprints (tags applied at provisioning) vs Prism Central playbooks (auto-tag based on rules) vs manual tagging (error-prone, inconsistent)
