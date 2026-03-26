# AWS Outposts

## Scope

AWS-managed on-premises infrastructure extending AWS services to customer datacenters. Covers Outposts Rack and Server form factors, Service Link networking, Local Gateway, supported services, S3 on Outposts, capacity management, and hybrid EKS patterns.

AWS-managed infrastructure deployed on-premises that extends AWS services, APIs, and tooling to customer datacenters or co-location facilities. Available as Outposts Rack (full 42U rack, 5-96kW power range, now in second-generation with improved performance and power efficiency) or Outposts Server (1U/2U individual servers for smaller locations). Outposts Rack delivers a broad set of AWS services locally; Outposts Server supports EC2 and ECS in a smaller form factor. All Outposts require a persistent Service Link connection back to a parent AWS Region.

## Checklist

- [ ] **[Critical]** Determine form factor: Outposts Rack (42U, minimum ~5kW, second-generation racks available with improved power efficiency and performance) vs. Outposts Server (1U/2U, for retail stores, branch offices, or space-constrained locations needing only EC2/ECS)
- [ ] **[Critical]** Select the parent AWS Region: the Outpost is logically an extension of this region; all control plane operations, IAM, and service APIs route through it; choose the nearest region for lowest latency on the Service Link
- [ ] **[Critical]** Choose a capacity configuration: Outposts Rack offers predefined configurations based on EC2 instance families (general purpose, compute-optimized, memory-optimized, GPU, storage-optimized); Outposts Server configurations are fixed per server SKU
- [ ] **[Critical]** Plan site requirements: power (three-phase for rack), cooling (rear-door or in-row), floor loading (rack weighs ~1500 lbs), physical security, and network connectivity; AWS provides a site survey before installation
- [ ] **[Critical]** Design Service Link networking: dedicated network path from Outpost to the parent region; requires minimum 500 Mbps bandwidth with sub-200ms RTT; redundant paths recommended; can use AWS Direct Connect, VPN, or internet (Direct Connect strongly recommended for production)
- [ ] **[Recommended]** Configure the Local Gateway (LGW): provides connectivity between Outpost subnets and the on-premises network; supports VLANs, CoIP (Customer-Owned IP) addresses, and BGP peering with on-premises routers for local traffic routing
- [ ] **[Critical]** Plan VPC and subnet design: Outpost subnets are created within a VPC in the parent region; instances on the Outpost get IPs from these subnets; security groups, NACLs, and route tables apply as they do in-region
- [ ] **[Critical]** Evaluate supported services for your workloads: EC2, EBS (gp2, io1), ECS, EKS, S3 on Outposts (local object storage), RDS (MySQL, PostgreSQL), ElastiCache (Redis, Memcached), EMR, ALB, and more; not all instance types or service features are available — check the latest service availability matrix
- [ ] **[Recommended]** Configure S3 on Outposts if local object storage is needed: S3 on Outposts uses local storage (not replicated to region S3); set up access points and bucket policies; plan capacity as S3 on Outposts does not auto-scale — it uses the provisioned storage on the rack
- [ ] **[Optional]** Plan for shared Outposts (multi-account): Outpost capacity can be shared across AWS accounts using AWS RAM (Resource Access Manager); decide on account isolation boundaries and capacity allocation
- [ ] **[Recommended]** Set up monitoring: CloudWatch metrics for Outpost-local instances and services flow to the parent region; configure CloudWatch alarms for capacity utilization (EC2, EBS, S3); use AWS Config and CloudTrail for compliance and audit
- [ ] **[Recommended]** Understand capacity management: use self-service capacity management to view utilization metrics and request capacity changes through the AWS console without opening support cases; plan for peak utilization and headroom; AWS does not auto-scale Outpost hardware but capacity can be added to existing racks through self-service requests
- [ ] **[Recommended]** Evaluate third-party block storage integration: Outposts supports qualified third-party block storage (e.g., Pure Storage, NetApp) for workloads requiring storage capabilities beyond native EBS, providing local high-performance storage with familiar enterprise storage management
- [ ] **[Critical]** Plan for Service Link disruption: during connectivity loss, running instances continue operating but new instance launches, EBS snapshots, and control plane operations are unavailable; design applications to tolerate control plane unavailability
- [ ] **[Recommended]** Document pricing model: Outposts Rack uses a 3-year commitment (all upfront, partial upfront, or no upfront) with monthly charges based on the selected configuration; Outposts Server follows a similar commitment model; there are no additional charges for data transfer between the Outpost and its parent region

## Why This Matters

Outposts solves the "same APIs, local execution" problem. Teams that have standardized on AWS services and tooling (CloudFormation, CDK, Terraform AWS provider, IAM, CloudWatch) can deploy the same infrastructure-as-code to an Outpost without retooling. This is fundamentally different from running self-managed Kubernetes or VMs on-prem and bridging to AWS — it eliminates the operational gap between on-prem and cloud environments.

The fixed-capacity model is a significant constraint. Unlike the cloud, you cannot burst beyond your provisioned Outpost. Capacity planning becomes critical and mirrors traditional datacenter planning disciplines. Self-service capacity management now allows customers to view utilization and request capacity additions through the AWS console, simplifying what was previously a support-driven process. Third-party block storage support (from partners like Pure Storage and NetApp) extends Outposts' storage capabilities beyond native EBS for workloads requiring enterprise storage features.

The Service Link dependency is the most important architectural consideration. Outposts is not designed for disconnected operation. If the link to the parent region goes down, the existing workloads continue running (data plane persists), but you cannot launch new instances, create snapshots, or perform any control plane operation. Applications must be designed to handle this gracefully.

## Common Decisions (ADR Triggers)

### Outposts Rack vs. Outposts Server
Rack provides a broad service portfolio (EC2, EBS, S3, RDS, EKS, ECS, ElastiCache, ALB, EMR) and higher total capacity. Server provides only EC2 and ECS in a small form factor. Choose Server for space-constrained locations with simple compute needs (edge processing, local API serving). Choose Rack when you need storage services (S3, EBS), managed databases, or significant compute capacity. Document the service requirements driving the choice.

### Service Link connectivity: Direct Connect vs. VPN vs. internet
Direct Connect provides the most reliable, lowest-latency Service Link with consistent bandwidth. VPN over internet is acceptable for non-production or smaller deployments. Internet-only is technically supported but not recommended for production. Document the connectivity option, redundancy design, and bandwidth allocation for the Service Link.

### VPC architecture: single VPC extension vs. multi-VPC
An Outpost can host subnets from multiple VPCs. A single VPC keeps routing simple. Multiple VPCs provide stronger isolation between workloads or tenants. Document the VPC topology and how it maps to application isolation requirements.

### Local Gateway (LGW) routing: CoIP vs. VPC routing
Customer-Owned IP (CoIP) pools allow instances on the Outpost to use IP addresses from the on-premises network, making them directly routable on-prem. Alternatively, instances use VPC IPs and the LGW NATs or routes traffic between VPC and on-prem networks. CoIP simplifies on-prem integration but consumes on-prem IP space. Document the IP addressing strategy and on-prem routing integration approach.

### S3 on Outposts vs. EBS for local storage
S3 on Outposts provides object storage semantics locally but has fixed capacity and no replication to regional S3. EBS provides block storage for EC2 instances. For applications needing S3 APIs locally (data lakes, media processing), S3 on Outposts is appropriate. For traditional database and application storage, EBS is the right choice. Document the storage architecture and data lifecycle (local only vs. eventual sync to region).

### Shared Outpost vs. dedicated per-account
Sharing an Outpost across accounts via AWS RAM maximizes utilization but requires governance around capacity consumption. Dedicated Outposts per account provide isolation but may waste capacity. Document the multi-tenancy model and capacity reservation strategy.

### Commitment term and payment structure
3-year terms are required. All-upfront provides the lowest effective monthly cost. No-upfront preserves cash flow but has a higher total cost. Document the financial model and alignment with budgeting cycles.

## Reference Architectures

### Low-latency application tier on-premises
Outposts Rack deployed in a customer datacenter adjacent to on-premises databases and legacy systems. EC2 instances on the Outpost run application tiers (APIs, web servers) that require sub-5ms latency to on-prem databases. The Local Gateway provides direct L2/L3 connectivity to the datacenter network. Frontend traffic from users hits the application on the Outpost; the application queries on-prem databases directly. Analytics and logging data flows to the parent AWS region via the Service Link for CloudWatch, S3 archival, and Athena queries.

### Hybrid EKS with on-prem and cloud nodes
EKS cluster spanning the parent region and the Outpost. Control plane runs in the region. Worker nodes run on EC2 instances on the Outpost. Pods needing low-latency access to on-prem data sources are scheduled onto Outpost nodes using node selectors or taints/tolerations. Pods without locality requirements run in-region. ALB on Outpost handles on-prem ingress; ALB in-region handles internet-facing ingress. Container images are pulled from ECR in the parent region via the Service Link.

### S3 on Outposts for local data processing
Outposts Rack with S3 on Outposts for local object storage. On-premises applications write data (images, sensor data, logs) to S3 on Outposts using standard S3 APIs and access points. EC2 instances on the Outpost run processing workloads (ETL, ML inference) against the local S3 data. Processed results are uploaded to regional S3 for long-term storage, analytics (Athena, Redshift Spectrum), and archival (S3 Glacier). DataSync or custom copy jobs handle the Outpost-to-region data movement since S3 on Outposts does not automatically replicate to regional S3.

### Managed database on-premises with RDS on Outpost
RDS for MySQL or PostgreSQL running on the Outpost. Provides a fully managed database experience (automated backups, patching, monitoring) on-premises. Application servers on the Outpost connect to RDS locally with sub-millisecond network latency. Automated backups are stored in the parent region's S3. Read replicas can be created in the parent region for disaster recovery or analytics offloading. This pattern suits applications requiring managed database operations on-prem due to data residency or latency constraints.

### Multi-site retail with Outposts Servers
Outposts Server (1U) deployed in each retail store. EC2 instances run point-of-sale processing, local inventory APIs, and edge inference models. ECS containers handle microservice workloads. Traffic between the store and the parent AWS region flows over VPN or Direct Connect. During WAN outages, existing workloads continue running (transactions are queued locally). A central hub-and-spoke architecture in the parent region aggregates data from all store Outposts for analytics, inventory planning, and ML model training.

---

## Reference Links

- [AWS Outposts User Guide](https://docs.aws.amazon.com/outposts/latest/userguide/) -- rack and server setup, networking, supported services, and capacity management
- [AWS Outposts Pricing](https://aws.amazon.com/outposts/pricing/) -- rack and server configurations, commitment terms, and payment options

## See Also

- `patterns/hybrid-cloud.md` -- Hybrid cloud architecture patterns including on-premises extensions
- `providers/aws/snow-family.md` -- Portable edge compute and offline data transfer as an alternative
- `providers/aws/vpc.md` -- VPC subnet design for Outpost-hosted resources
- `providers/aws/ec2-asg.md` -- EC2 instance types available on Outposts
