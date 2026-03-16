# Azure Stack Edge

Purpose-built edge appliances delivered as a service (hardware-as-a-service) for running compute, AI inference, and data transfer workloads at the edge. The product line includes Azure Stack Edge Pro (with GPU or FPGA acceleration) for standard edge deployments and Azure Stack Edge Mini R (ruggedized, portable) for harsh or field environments. Azure manages the device lifecycle; customers order through the Azure portal, receive the hardware, activate it, and pay a monthly fee.

## Checklist

- [ ] **[Critical]** Determine the appropriate SKU: Azure Stack Edge Pro 2 (latest generation, single or dual GPU), Azure Stack Edge Pro GPU (T4 GPUs), or Azure Stack Edge Mini R (ruggedized, single GPU, battery-capable). Note: Azure Stack Edge Pro FPGA was retired in February 2024 — all FPGA deployments must be migrated to GPU SKUs
- [ ] Order the device through the Azure portal: create an Azure Stack Edge resource, select SKU and shipping destination, provide site contact details; lead times vary by region (typically 2-6 weeks)
- [ ] Plan site requirements: rack space (Pro 2 is 1U, Mini R is portable), power (dual PSU recommended for Pro), network connectivity (1GbE management + 10/25GbE data ports), ambient temperature limits
- [ ] Activate the device using the activation key from the Azure portal; configure network settings, DNS, proxy, and time server via the local web UI during initial setup
- [ ] Configure edge compute: enable Kubernetes (Azure Arc-enabled) or IoT Edge runtime on the device for running containerized workloads at the edge
- [ ] Deploy AI inference workloads: use GPU acceleration with NVIDIA T4 for ONNX, TensorFlow, or PyTorch models; leverage Azure Machine Learning for model deployment pipelines
- [ ] Set up local storage shares: configure SMB or NFS shares backed by device storage; choose between edge local shares (data stays on device) and cloud-tiered shares (data automatically syncs to Azure Blob or Azure Files)
- [ ] Configure data transfer: for Data Box Gateway mode, map local shares to Azure storage accounts; set bandwidth schedules to control upload timing and throttle during business hours
- [ ] Plan certificate management: the device uses certificates for local web UI, Azure Resource Manager endpoint, Blob endpoint, and IoT Edge; use custom certificates from your CA or let the device auto-generate self-signed certificates (not recommended for production)
- [ ] Enable security features: BitLocker encryption at rest is enabled by default; configure data-at-rest encryption keys (device-managed or customer-managed via Azure Key Vault); set up tamper detection alerts
- [ ] Set up monitoring: use Azure Monitor integration for device health metrics, alerts on disk/CPU/memory/GPU utilization, and proactive support case creation; configure diagnostic log collection
- [ ] Plan update management: device updates (OS/firmware) are delivered through Azure and can be scheduled; Kubernetes and IoT Edge module updates are managed separately through their respective control planes
- [ ] Evaluate network function virtualization (NFV) scenarios: Azure Stack Edge can host virtualized network functions for SD-WAN or mobile packet core (Azure Private 5G Core) deployments
- [ ] Document the return/replacement process: devices are Microsoft-owned; at end of use, wipe data via local UI or Azure portal and arrange return shipping; replacement devices for hardware failure are shipped proactively

## Why This Matters

Edge locations — retail stores, factory floors, oil rigs, field hospitals, military forward operating bases — need local compute and AI inference without depending on reliable cloud connectivity. Azure Stack Edge provides this as a managed appliance: Microsoft owns the hardware, handles replacements, and pushes updates. This eliminates the operational burden of procuring, racking, and maintaining edge servers in potentially hundreds of locations.

The hardware-as-a-service model converts what would be a CapEx hardware purchase into a predictable monthly OpEx charge, which simplifies procurement in organizations where capital budgets are constrained. However, the monthly fees accumulate over multi-year deployments, so total cost of ownership should be compared against self-managed edge infrastructure for long-duration use cases.

AI inference at the edge is the primary differentiator. Rather than streaming raw video or sensor data to the cloud for processing (which consumes bandwidth and introduces latency), models run locally on GPU hardware with results sent to the cloud as structured data. This reduces bandwidth costs by orders of magnitude and enables real-time decision-making.

## Common Decisions (ADR Triggers)

### Azure Stack Edge Pro vs. Mini R
Pro devices are datacenter/closet-grade 1U appliances with higher compute and storage capacity, suitable for permanent installations. Mini R is ruggedized (IP65-rated), battery-capable, and portable, designed for field operations, disaster response, or deployments in harsh environments. Record the deployment environment and mobility requirements to justify the SKU selection.

### GPU vs. FPGA SKU
FPGA SKUs were retired in February 2024. New deployments must use GPU SKUs. If migrating from FPGA, document the model conversion plan (FPGA models to ONNX/GPU-compatible formats) and timeline.

### Kubernetes (Arc-enabled) vs. IoT Edge runtime
Both run containers on the device. Kubernetes (Arc-enabled) provides standard K8s APIs, Helm chart deployment, and GitOps via Flux. IoT Edge provides module-based deployment managed through IoT Hub, with built-in message routing and device twin capabilities. Choose Kubernetes for cloud-native teams and workloads that may migrate between edge and cloud. Choose IoT Edge for IoT-centric scenarios with device management, message brokering, and integration with IoT Hub analytics.

### Edge local shares vs. cloud-tiered shares
Edge local shares keep data on the device only — suitable for scratch space, temporary processing data, or air-gapped scenarios. Cloud-tiered shares automatically upload data to Azure Storage — suitable for data collection, backup, and analytics pipelines. Document the data residency and data flow requirements for each share.

### Self-signed vs. CA-issued certificates
Self-signed certificates work for initial testing but cause trust warnings and complicate automation. CA-issued certificates (from internal PKI or public CA) are required for production to enable trusted connections from client machines and automated systems. Document the certificate lifecycle and renewal process.

### Single device vs. multi-device deployment at scale
For deployments spanning many sites (retail chains, cell towers), use Azure Resource Manager templates and Azure CLI/PowerShell for repeatable provisioning. Consider Azure Lighthouse for multi-tenant management if an MSP manages the devices. Record the scale-out strategy and per-site configuration management approach.

### Bandwidth scheduling for data transfer
Cloud-tiered shares can saturate WAN links. Bandwidth schedules throttle or pause uploads during business hours. Document the bandwidth allocation, schedule windows, and priority of data transfer relative to other site traffic.

## Reference Architectures

### Retail edge — AI-powered inventory and checkout
Azure Stack Edge Pro 2 (single GPU) deployed in a store backroom. Computer vision models (ONNX format, deployed via Azure ML) process camera feeds to detect shelf stock levels and checkout anomalies. Edge local shares store video buffer temporarily; structured inference results (item counts, alerts) are sent to Azure IoT Hub for aggregation. Cloud-tiered shares upload daily summary data to Azure Blob Storage for retraining pipelines. IoT Edge runtime manages camera ingestion modules and inference modules. Azure Monitor tracks device health; store IT staff interact only with the Azure portal.

### Manufacturing — defect detection on production lines
Azure Stack Edge Pro 2 (dual GPU) at the factory edge. High-resolution camera feeds from production lines are processed by defect detection models running on the GPUs. Inference latency must be sub-100ms to enable real-time rejection. Results are published to a local MQTT broker (running as an IoT Edge module) and consumed by the PLC/SCADA system. Cloud-tiered shares upload defect images and metadata to Azure Blob for model retraining in Azure ML. OPC UA adapter modules connect to industrial equipment for telemetry collection.

### Field operations — disconnected/semi-connected
Azure Stack Edge Mini R carried in a transit case to field locations (disaster response, military, geological survey). Device operates on battery or generator power. Kubernetes workloads run data processing pipelines entirely offline. Data is stored on edge local shares. When connectivity is available (satellite link, temporary cellular), cloud-tiered shares sync collected data to Azure. Azure Arc-enabled Kubernetes allows remote workload updates when connected. Tamper-resistant enclosure and BitLocker encryption protect data in transit and at rest.

### Telco edge — Azure Private 5G Core
Azure Stack Edge Pro deployed at cell tower sites or central offices. Azure Private 5G Core (packet core) runs as a network function on the device, providing private LTE/5G connectivity for enterprise campuses. Kubernetes hosts the packet core and additional edge applications (video analytics, AR/VR). The device connects back to Azure for management and monitoring. Multiple devices across sites are managed as a fleet through Azure portal and ARM templates.

### Data transfer and migration — Data Box Gateway mode
Azure Stack Edge configured primarily as a data gateway. NFS/SMB shares are mounted by on-premises servers and applications. Data written to shares is automatically transferred to Azure Blob or Azure Files. Bandwidth schedules control transfer windows. This architecture replaces physical Data Box shipments for ongoing data ingestion from sites with adequate network connectivity. Useful for media production (dailies upload), scientific data collection, and backup-to-cloud workflows.
