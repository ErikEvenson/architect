# AWS EC2 and Auto Scaling Groups

## Checklist

- [ ] Are launch templates (not launch configurations) used for all ASG definitions, supporting versioning and mixed instance policies?
- [ ] Is the ASG spread across at least 2 AZs (3 recommended) with capacity rebalancing enabled?
- [ ] Are mixed instance policies configured with multiple instance types and purchase options (On-Demand base + Spot) for cost savings?
- [ ] Are Spot Instances used for fault-tolerant workloads with Spot placement scores checked and interruption handling implemented?
- [ ] **[Critical]** Is the instance type selected using the correct family for the workload? (compute-optimized C series, memory-optimized R series, general-purpose M series, Graviton4 R8g/M8g/C8g for best price-performance)
- [ ] Are AMIs hardened, patched, and built via a pipeline (EC2 Image Builder or Packer) with golden AMI versioning?
- [ ] Is instance metadata service v2 (IMDSv2) enforced to prevent SSRF-based credential theft?
- [ ] Are EBS volumes encrypted with customer-managed KMS keys, and are gp3 volumes used instead of gp2 for cost and performance?
- [ ] Are placement groups used where needed? (cluster for low-latency, spread for HA, partition for large distributed workloads)
- [ ] Are target tracking scaling policies configured for CPU, request count, or custom CloudWatch metrics with appropriate cooldowns?
- [ ] Is lifecycle hook configured for graceful drain on scale-in, allowing in-flight requests to complete?
- [ ] Are instance health checks using ELB health checks (not just EC2 status checks) for accurate replacement of unhealthy instances?
- [ ] Is SSM Session Manager used for shell access instead of SSH bastion hosts, eliminating port 22 exposure?
- [ ] **[Recommended]** Are Nitro-based instances used for enhanced networking, EBS optimization, and security (encryption, Nitro Enclaves)?
- [ ] **[Recommended]** Are EC2 Capacity Blocks for ML evaluated for GPU instance reservations (P5, P4d, Trn1) when predictable capacity is needed for ML training and inference workloads? Capacity Blocks reserve GPU instances for a defined duration (days to weeks) at a discounted rate.

## Why This Matters

EC2 and ASG configuration directly affects availability, performance, and cost. Launch configurations are legacy and cannot be versioned. Single-AZ ASGs fail completely during AZ outages. IMDSv1 is a known attack vector. Oversized instances waste money; undersized instances degrade performance. Ungoverned AMIs accumulate vulnerabilities.

## Common Decisions (ADR Triggers)

- **Instance family and generation** -- Graviton4 (R8g/M8g/C8g, best price-performance) vs Graviton3 vs x86 (Intel/AMD), latest generation vs compatibility needs
- **Purchase model** -- On-Demand vs Reserved Instances vs Savings Plans vs Spot, commitment term
- **AMI management** -- EC2 Image Builder vs Packer, base AMI source, patching cadence, AMI lifecycle policy
- **Scaling strategy** -- target tracking vs step scaling vs predictive scaling, scale-out speed vs cost
- **EBS volume type** -- gp3 (baseline IOPS/throughput) vs io2 (provisioned IOPS) vs instance store for ephemeral data
- **Access model** -- SSM Session Manager vs SSH bastion, OS-level access controls
- **Spot strategy** -- capacity-optimized vs lowest-price allocation, diversified instance pools
- **ML/GPU capacity** -- On-Demand GPU instances vs Capacity Blocks for ML (reserved GPU capacity for defined duration) vs Spot GPU instances (high interruption risk for training)

## Reference Architectures

- [AWS Architecture Center: Compute](https://aws.amazon.com/architecture/) -- reference architectures for EC2, Auto Scaling, and Spot integration patterns
- [AWS Well-Architected Labs: Cost Optimization - EC2 Right Sizing](https://www.wellarchitectedlabs.com/cost/) -- hands-on labs for right-sizing EC2 instances and optimizing Auto Scaling
- [AWS Prescriptive Guidance: EC2 Auto Scaling for predictable and dynamic workloads](https://docs.aws.amazon.com/autoscaling/ec2/userguide/) -- scaling strategies and mixed instance policies
- [AWS Spot Instances best practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html) -- reference patterns for Spot diversification, capacity-optimized allocation, and interruption handling
- [AWS EC2 Image Builder pipeline architecture](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html) -- reference architecture for automated AMI build and distribution pipelines
