# AWS Snow Family

> **SERVICE STATUS NOTICE**
>
> - **Snowcone: DISCONTINUED** as of November 12, 2024. No longer available for new orders.
> - **Snowball Edge: UNAVAILABLE to new customers** as of November 7, 2025. Existing customers with active jobs can continue use.
> - **Snowmobile: RETIRED** as of April 2024. Service fully decommissioned.
>
> AWS recommends **AWS DataSync** and **AWS Data Transfer Terminal** as alternatives for data transfer workloads. Evaluate these services before considering Snow Family devices.

Ruggedized, portable devices for edge computing and offline data transfer. The family includes Snowcone (smallest, most portable), Snowball Edge Storage Optimized (high-capacity data transfer), and Snowball Edge Compute Optimized (edge compute with optional GPU). Snow devices operate fully disconnected, are tamper-resistant, and integrate with AWS services for data import/export and edge workload execution. Designed for environments where network transfer is impractical (bandwidth-limited, disconnected, or physically remote).

## Checklist

- [ ] [Critical] Determine the use case category: bulk data migration to AWS (import/export to S3), edge compute in disconnected environments, or hybrid (compute + data collection for later upload)
- [ ] [Critical] Select the appropriate device: Snowcone (8TB HDD or 14TB SSD, 2 vCPUs, 4GB RAM — ultraportable at 4.5 lbs), Snowball Edge Storage Optimized (210TB usable, 40 vCPUs, 80GB RAM — for large data transfers), or Snowball Edge Compute Optimized (28TB NVMe SSD, 104 vCPUs, 416GB RAM, optional NVIDIA V100 GPU — for heavy edge compute and ML inference)
- [ ] [Recommended] Order devices through the AWS Console or AWS CLI: specify the job type (import to S3, export from S3, or local compute/storage), select the device type, configure shipping address, and assign an IAM role for S3 access
- [ ] [Recommended] Plan logistics and chain of custody: devices are shipped by AWS with E Ink shipping labels; track shipment via the console; physical tamper-evident seals and TPM-based chain of custody verification ensure device integrity
- [ ] [Recommended] Unlock and configure the device on-site: use OpsHub (desktop GUI application) or the Snowball Edge CLI to unlock the device with the manifest file and unlock code from the console; connect to the local network
- [ ] [Recommended] Configure data transfer for migration jobs: use the S3-compatible endpoint on the device to copy data via AWS CLI (`aws s3 cp`), S3 SDK, or third-party transfer tools; NFS mount is available on Storage Optimized for file-based ingestion
- [ ] [Optional] Deploy edge compute workloads: launch EC2-compatible instances (AMIs pre-loaded during ordering or transferred via OpsHub) on Snowball Edge devices; deploy IoT Greengrass on Snowcone for lightweight edge processing and Lambda execution
- [ ] [Optional] Set up clustering for Snowball Edge: cluster 5-10 Snowball Edge devices together for increased storage capacity and compute power; clustered devices provide a single S3-compatible endpoint and support EC2 instances across the cluster with local networking
- [ ] [Optional] Install AWS DataSync agent on Snowcone for automated, efficient data transfer to S3 when network connectivity is available; DataSync handles incremental transfers, compression, and integrity verification
- [ ] [Critical] Configure encryption: all data on Snow devices is encrypted with 256-bit keys managed through AWS KMS; select the KMS key during job creation; data is encrypted before being written to device storage
- [ ] [Recommended] Plan for power and environmental conditions: Snowcone operates on USB-C power or optional battery; Snowball Edge requires standard AC power (110V/220V); all devices operate in 0-45C ambient temperature ranges; Snowcone is rated for harsher conditions with optional ruggedized cases
- [ ] [Recommended] Document the return and data lifecycle: after use, ship the device back to AWS; for import jobs, AWS transfers data to the designated S3 bucket; AWS then performs a NIST 800-88-compliant media wipe; data on the device is cryptographically erased

## Why This Matters

Network-based data transfer has physical limits. Transferring 100TB over a 1Gbps link takes roughly 10 days of continuous transfer, assuming no overhead. Over typical enterprise WAN connections with contention, it takes much longer. Snow devices bypass the network entirely — 210TB of data can be shipped overnight. For petabyte-scale migrations, Snow is often the only practical approach.

Beyond data transfer, Snow devices extend AWS compute to locations where no other AWS presence exists: ships at sea, mining sites, disaster zones, forward military positions. The ability to run EC2 instances and containers on a tamper-resistant, encrypted device means sensitive workloads can execute in austere environments without compromising security.

The operational model is fundamentally different from Outposts. Snow devices are transient — ordered for a job, used, and returned (or kept on a renewable long-term lease). There is no persistent Service Link to AWS. Applications must be designed for fully disconnected operation with eventual data sync. This makes Snow suitable for batch-oriented and intermittently-connected workloads rather than always-on services.

## Common Decisions (ADR Triggers)

### Snowcone vs. Snowball Edge [Recommended]
Snowcone is the choice for portability-first scenarios: carried in a backpack, deployed on a vehicle, or used in locations with limited power. Its compute capacity is modest (2 vCPUs). Snowball Edge provides dramatically more capacity and compute but requires AC power and is larger (50 lbs for Compute Optimized). If the workload requires significant processing power or more than 14TB of storage, Snowball Edge is necessary. Document the portability requirements, storage volume, and compute needs.

### Storage Optimized vs. Compute Optimized (Snowball Edge) [Critical]
Storage Optimized maximizes data capacity (210TB) for migration-heavy workloads. Compute Optimized maximizes CPU/RAM (104 vCPUs, 416GB) and optionally includes a GPU for ML inference, video processing, or other compute-intensive edge tasks. If the primary use case is data transfer with minimal processing, Storage Optimized is more cost-effective. If edge compute is the primary purpose and data transfer is secondary, Compute Optimized is appropriate. Document the workload profile.

### Single device vs. cluster [Recommended]
A single Snowball Edge supports up to 210TB storage and a finite number of EC2 instances. Clustering 5-10 devices provides a unified storage pool and distributed compute. Clustering adds operational complexity (device networking, cluster management) but enables workloads that exceed single-device capacity. Document the storage and compute requirements and whether they can be met by a single device.

### OpsHub vs. CLI management [Optional]
OpsHub provides a graphical interface for unlocking devices, transferring files, managing EC2 instances, and monitoring device status. The CLI provides scriptable automation for the same tasks. OpsHub is simpler for operators with limited CLI experience; CLI is better for automated and repeatable workflows (scripted data ingestion pipelines, automated instance deployment). Document the operator skill profile and automation requirements.

### Data transfer method: S3 API vs. NFS vs. DataSync [Recommended]
The S3-compatible endpoint provides the most versatile access (any S3-compatible tool works). NFS mount on Storage Optimized is simpler for file-based workflows (mount and copy). DataSync on Snowcone provides intelligent, incremental transfer with verification. Choose based on the data source system capabilities and whether the transfer is one-time (S3 API or NFS) or ongoing (DataSync). Document the data source integration method.

### Short-term job vs. long-term lease [Optional]
Standard Snow jobs last up to a year (with extensions). For permanent or semi-permanent edge compute, Snow devices can be leased long-term (1-3 years) at reduced daily rates. Document the expected deployment duration and whether the use case is a one-time migration or ongoing edge presence. Compare long-term Snow lease costs against alternatives (Outposts Server, local hardware).

## Reference Architectures

### Petabyte-scale data migration to S3
Multiple Snowball Edge Storage Optimized devices ordered in parallel. On-prem data pipeline server mounts NFS shares on each device and runs parallel copy jobs using a migration tool (e.g., `cp`, `rsync`, or AWS-provided transfer tools). Devices are filled to capacity, shipped to AWS, and data is imported into target S3 buckets. AWS wipes devices and ships new ones for the next batch. A migration coordinator script tracks which files are on which device and verifies completeness after import using S3 inventory. For 1PB+ migrations, 10-15 devices cycling in parallel completes the transfer in weeks rather than months.

### Disconnected edge compute — field operations
Snowball Edge Compute Optimized (with GPU) deployed to a remote field site. Before deployment, EC2 AMIs containing the application stack are loaded onto the device. On-site, the device runs ML inference models for geospatial analysis, image classification, or sensor data processing. Data is collected from local instruments via the device's network interfaces. Processed results are stored on the device's S3-compatible storage. When the device is returned or connectivity becomes available, data is synced to AWS S3. IoT Greengrass manages the application lifecycle on the device.

### Maritime/vessel deployment
Snowcone devices deployed on ships or offshore platforms. Small form factor and USB-C power compatibility suit the constrained environment. IoT Greengrass runs data collection and preprocessing Lambda functions that aggregate sensor telemetry from vessel systems. When the vessel reaches port or has satellite connectivity, DataSync agent on the Snowcone incrementally transfers collected data to S3. Multiple voyages' worth of data accumulates on the device (up to 14TB SSD); critical data is prioritized for satellite upload via bandwidth-aware DataSync configuration.

### Disaster response / humanitarian operations
Snowcone devices carried by response teams to disaster zones. Battery-powered operation (optional external battery) enables deployment without infrastructure. Devices host communication coordination applications, mapping tools, and data collection forms as EC2 instances. Field data (photos, assessments, GPS coordinates) is written to the device. When connectivity is restored, data syncs to S3 for centralized analysis. Tamper resistance and encryption protect sensitive personal data collected in the field.

### Content distribution and edge rendering
Snowball Edge Compute Optimized deployed at content production locations (film sets, live event venues). GPU-accelerated instances run video transcoding and rendering workloads on raw footage. Rendered content is stored on the device's local S3 storage. Completed assets are transferred to S3 when the device returns to a connected location. This avoids shipping raw footage on unencrypted drives and provides compute for time-sensitive rendering without dependence on cloud connectivity.

### Snowball Edge cluster for remote research stations
A cluster of 5 Snowball Edge devices deployed to an Arctic or Antarctic research station. The cluster provides a combined 1PB+ storage pool and hundreds of vCPUs. Research instruments write data to the cluster's unified S3 endpoint. Compute instances run data analysis and simulation workloads. The cluster operates fully disconnected for months at a time. When seasonal resupply occurs, devices are cycled out — filled devices are shipped to AWS for S3 import, and fresh devices are deployed. This provides both storage capacity and compute power in locations with zero internet connectivity.
