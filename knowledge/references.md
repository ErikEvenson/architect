# Reference Architectures Index

Master index of vendor-published reference architecture resources organized by provider.

## AWS

### Portals

- [AWS Architecture Center](https://aws.amazon.com/architecture/) -- central hub for all AWS reference architectures, solution guides, and diagrams
- [AWS Well-Architected Labs](https://www.wellarchitectedlabs.com/) -- hands-on labs organized by the six Well-Architected Framework pillars
- [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/) -- opinionated patterns and guides for common cloud scenarios
- [AWS Solutions Library](https://aws.amazon.com/solutions/) -- deployable reference implementations for common workloads

### By Domain

- **Networking** -- [Networking & Content Delivery architectures](https://aws.amazon.com/architecture/networking-content-delivery/), [VPC scenarios](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-example-web-database-servers.html), [Multi-account network design](https://docs.aws.amazon.com/prescriptive-guidance/latest/robust-network-design-control-tower/)
- **IAM & Security** -- [Security Reference Architecture (SRA)](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/), [Security, Identity, & Compliance architectures](https://aws.amazon.com/architecture/security-identity-compliance/)
- **Databases** -- [Database architectures](https://aws.amazon.com/architecture/databases/), [Aurora Global Database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html), [Database migration patterns](https://docs.aws.amazon.com/dms/latest/userguide/)
- **Compute** -- [Compute architectures](https://aws.amazon.com/architecture/), [Spot best practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html), [EC2 Image Builder](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html)
- **Caching** -- [ElastiCache best practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/best-practices.html), [Caching strategies](https://docs.aws.amazon.com/prescriptive-guidance/latest/)
- **Edge & CDN** -- [CloudFront origin failover](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/high_availability_origin_failover.html), [WAF Security Automations](https://aws.amazon.com/solutions/implementations/security-automations-for-aws-waf/), [DDoS mitigation](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/)
- **Observability** -- [Observability Best Practices](https://aws-observability.github.io/observability-best-practices/), [Centralized Logging with OpenSearch](https://aws.amazon.com/solutions/implementations/centralized-logging-with-opensearch/), [Management & Governance architectures](https://aws.amazon.com/architecture/management-governance/)
- **Secrets** -- [Secrets Manager rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html), [EKS Secrets Store CSI Driver](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html)

## Azure

### Portals

- [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/) -- central hub for Azure reference architectures, best practices, and design patterns
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/) -- design principles and service guides across reliability, security, cost, performance, and operations
- [Azure Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/) -- enterprise landing zone architecture and governance patterns
- [Microsoft Cybersecurity Reference Architectures (MCRA)](https://learn.microsoft.com/en-us/security/adoption/mcra) -- comprehensive reference for Microsoft security services

### By Domain

- **Networking** -- [Hub-spoke topology](https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke), [Networking architectures](https://learn.microsoft.com/en-us/azure/architecture/networking/), [Landing Zone network design](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/network-topology-and-connectivity)
- **Compute** -- [VM architectures](https://learn.microsoft.com/en-us/azure/architecture/browse/?azure_categories=compute), [VMSS autoscaling](https://learn.microsoft.com/en-us/azure/architecture/best-practices/auto-scaling), [Well-Architected VM guide](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/virtual-machines)
- **Data** -- [Data architecture guide](https://learn.microsoft.com/en-us/azure/architecture/data-guide/), [Azure SQL HA](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla), [Cosmos DB multi-region](https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/globally-distributed-mission-critical-applications-using-cosmos-db)
- **Security** -- [Security architectures](https://learn.microsoft.com/en-us/azure/security/fundamentals/overview), [Landing Zone security](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/security), [Identity architectures](https://learn.microsoft.com/en-us/entra/fundamentals/)

## GCP

### Portals

- [Google Cloud Architecture Center](https://cloud.google.com/architecture) -- central hub for GCP reference architectures, best practices, and design guides
- [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework) -- design principles covering system design, reliability, security, cost, and performance
- [Google Cloud Enterprise Foundations Blueprint](https://cloud.google.com/architecture/security-foundations) -- enterprise-grade organization structure, IAM, and security baseline

### By Domain

- **Networking** -- [Networking architectures](https://cloud.google.com/architecture#networking), [Hub-and-spoke design](https://cloud.google.com/architecture/networking), [Hybrid/multi-cloud topologies](https://cloud.google.com/architecture/hybrid-and-multi-cloud-network-topologies), [Cloud Armor best practices](https://cloud.google.com/armor/docs/best-practices)
- **Compute** -- [Compute architectures](https://cloud.google.com/architecture#compute), [Compute Engine best practices](https://cloud.google.com/compute/docs/instances), [Scalable web apps on Compute Engine](https://cloud.google.com/architecture/scalable-and-resilient-apps)
- **Data** -- [Database architectures](https://cloud.google.com/architecture#databases), [Spanner reference architectures](https://cloud.google.com/spanner/docs), [Cloud SQL HA](https://cloud.google.com/sql/docs/mysql/high-availability), [Bigtable schema design](https://cloud.google.com/bigtable/docs/schema-design)
- **Security** -- [Security architectures](https://cloud.google.com/architecture#security), [VPC Service Controls best practices](https://cloud.google.com/vpc-service-controls/docs), [Security Command Center](https://cloud.google.com/security-command-center/docs/concepts-security-command-center-overview)

## Nutanix

### Portals

- [Nutanix Validated Designs](https://portal.nutanix.com/page/documents/solutions) -- vendor-validated architectures for enterprise applications
- [Nutanix Reference Architecture Library](https://portal.nutanix.com/page/documents/solutions) -- tested architectures for databases, EUC, DevOps, and hybrid cloud
- [The Nutanix Bible](https://www.nutanixbible.com/) -- comprehensive architecture guide for the Nutanix Cloud Platform

### Key Resources

- [AHV best practice guide](https://portal.nutanix.com/page/documents/solutions/details?targetId=BP-2071-AHV:BP-2071-AHV) -- hypervisor configuration, networking, and storage best practices
- [DR and Business Continuity designs](https://portal.nutanix.com/page/documents/solutions) -- Leap-based disaster recovery and metro availability validated designs

## VMware

> **Note:** VMware documentation URLs may redirect following the Broadcom acquisition (2023). Verify links before citing.

### Portals

- [VMware Validated Solutions](https://core.vmware.com/vmware-validated-solutions) -- tested and validated SDDC architectures for private cloud and edge
- [VMware Cloud Foundation Architecture Guide](https://core.vmware.com/resource/vmware-cloud-foundation-architecture-guide) -- full-stack SDDC reference architecture

### Key Resources

- [vSAN Design Guide](https://core.vmware.com/resource/vmware-vsan-design-guide) -- hyper-converged storage sizing, fault domains, and stretched clusters
- [NSX Reference Design Guide](https://communities.vmware.com/t5/VMware-NSX/ct-p/3200) -- microsegmentation, distributed firewall, and multi-site networking
- [Tanzu Reference Architecture](https://docs.vmware.com/en/VMware-Tanzu/services/tanzu-reference-architecture/GUID-reference-designs-index.html) -- Kubernetes on vSphere validated designs

## OpenStack

### Portals

- [OpenStack Architecture Design Guide](https://docs.openstack.org/arch-design/) -- official architecture guide for compute, storage, networking, and multi-site design
- [OpenStack Deployment Guides](https://docs.openstack.org/project-deploy-guide/) -- deployment architectures for Kolla-Ansible, TripleO, and other tools

### Key Resources

- [High Availability Guide](https://docs.openstack.org/ha-guide/) -- HA control plane, database clustering, and message queue resilience
- [Ceph integration reference](https://docs.openstack.org/cinder/latest/configuration/block-storage/drivers/ceph-rbd-volume-driver.html) -- Ceph as unified storage backend for Cinder, Glance, and Manila
- [Red Hat OpenStack Platform documentation](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/) -- enterprise deployment architectures with director-based lifecycle management
