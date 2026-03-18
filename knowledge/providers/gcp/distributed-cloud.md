# Google Distributed Cloud

## Scope

Google Distributed Cloud Connected (on-prem with cloud connection), Google Distributed Cloud Edge (carrier/network edge), Google Distributed Cloud Hosted (air-gapped/sovereign), GKE Enterprise fleet management, Config Sync, Cloud Service Mesh on distributed infrastructure.

Google's family of products for running Google Cloud services outside of Google-owned datacenters. Three deployment models address different connectivity and sovereignty requirements: Google Distributed Cloud Connected (on-prem with cloud connection), Google Distributed Cloud Edge (carrier edge and network edge), and Google Distributed Cloud Hosted (fully air-gapped, sovereign). All models are built on GKE Enterprise and provide Kubernetes-native workload management with Google Cloud integration for observability, policy, and security.

## Checklist

- [ ] [Critical] Determine the deployment model: Connected (on-prem datacenter with persistent connection to Google Cloud), Edge (carrier or retail edge locations with Google-managed hardware), or Hosted (fully air-gapped, sovereign operations with no Google Cloud connectivity)
- [ ] [Critical] Select hardware platform: Connected supports bare metal servers from validated vendors (Dell, HPE, Lenovo, Supermicro) or vSphere environments; Edge uses Google-provided appliance hardware; Hosted uses Google-provided and managed rack-scale infrastructure
- [ ] [Critical] Plan GKE Enterprise cluster topology: admin cluster (manages lifecycle of user clusters) and one or more user clusters (run application workloads); size control plane nodes (minimum 3 for HA) and worker node pools for target workloads
- [ ] [Recommended] Design networking: choose between bundled load balancing (MetalLB-based, included) and manual load balancing (F5, Citrix); plan IP address allocation for node IPs, pod CIDRs, service CIDRs, and load balancer VIPs; configure BGP peering if advertising VIPs to the network
- [ ] [Recommended] Configure Config Sync for GitOps: set up GitOps-based configuration and policy enforcement using Config Sync (syncs K8s manifests from Git) and Policy Controller (OPA Gatekeeper-based admission control with predefined policy bundles); Config Sync replaces the legacy Anthos Config Management umbrella term
- [ ] [Recommended] Enable Cloud Logging and Cloud Monitoring agents: logging and monitoring agents forward cluster and workload telemetry to Google Cloud for centralized observability; for Hosted (air-gapped), configure local logging stack (Loki, Elasticsearch) instead
- [ ] [Recommended] Set up Cloud Service Mesh if needed: provides mTLS between services, traffic management, and observability; evaluate whether the operational overhead is justified by the security and observability benefits
- [ ] [Recommended] Configure private container registry: for Connected deployments, use Artifact Registry in Google Cloud with registry mirroring to local nodes; for Hosted (air-gapped), deploy Harbor or another OCI-compliant registry on-prem and establish an image promotion pipeline
- [ ] [Recommended] Enable Binary Authorization: enforce deploy-time attestation policies that require container images to be signed by trusted authorities before they can run on the cluster; critical for supply chain security in regulated environments
- [ ] [Recommended] Configure workload identity: map Kubernetes service accounts to Google Cloud IAM service accounts (Connected/Edge) or local identity providers (Hosted) for secure, keyless authentication to APIs and services
- [ ] [Recommended] Plan update and upgrade management: Connected and Edge clusters receive updates from Google Cloud with admin-initiated rolling upgrades; Hosted environments receive updates via physical media or secure transfer mechanisms for air-gapped upgrade; test upgrades in a staging cluster first
- [ ] [Optional] Evaluate supported workload types: VMs (via VM Runtime on GKE for migrating legacy workloads), containers, and bare-metal workloads; plan the migration path for existing VM-based applications
- [ ] [Recommended] Design multi-cluster strategy if deploying across multiple sites: use GKE Enterprise fleet management for consistent policy, config, and observability across clusters; configure Multi-Cluster Ingress or Multi-Cluster Services for cross-cluster traffic routing
- [ ] [Critical] Document compliance and sovereignty requirements: Hosted is designed for environments requiring data sovereignty, air-gapped operation, and operational sovereignty (no Google personnel access without explicit approval); map regulatory requirements to Hosted capabilities

## Why This Matters

Google Distributed Cloud addresses three distinct market segments that public cloud alone cannot serve. Connected extends GKE and Google Cloud services to on-prem datacenters for organizations with hybrid cloud strategies -- this is a direct alternative to Azure Local or AWS Outposts but built on Kubernetes rather than VMs as the primary abstraction. Edge targets telco and network edge use cases where Google-managed hardware runs at carrier points of presence for 5G, MEC (Multi-access Edge Computing), and CDN workloads. Hosted addresses the most demanding sovereignty requirements -- defense, intelligence, and critical national infrastructure -- where no data or metadata can leave the customer's physical boundary.

The Kubernetes-native foundation is both a strength and a constraint. Teams already invested in Kubernetes find a natural extension of their operational model. Teams running primarily VM-based workloads face a steeper adoption curve, though VM Runtime on GKE provides a bridge. The decision to standardize on Distributed Cloud should account for organizational Kubernetes maturity.

Hosted is architecturally unique among the major cloud providers' on-prem offerings. Unlike AWS Outposts (which requires a Service Link) or Azure Local (which requires periodic Azure connectivity for billing), Hosted operates with zero connectivity to Google Cloud. Google delivers updates on physical media, and all management interfaces run locally. This comes at a significant cost premium and operational complexity, but it is the only offering from a hyperscaler that achieves true air-gapped operation.

## Common Decisions (ADR Triggers)

### Connected vs. Edge vs. Hosted
Connected is for standard hybrid cloud: datacenter workloads on customer hardware with Google Cloud management. Edge is for carrier and retail edge on Google-managed hardware. Hosted is for air-gapped sovereign operations. The choice is primarily driven by connectivity/sovereignty requirements and who manages the hardware. Document the regulatory environment, data classification, and connectivity constraints.

### Bare metal vs. vSphere (Connected only)
GKE on bare metal eliminates the hypervisor layer, reducing licensing costs and resource overhead. GKE on vSphere integrates with existing VMware infrastructure and operational tooling. If the organization has significant VMware investment and operational expertise, vSphere provides a smoother adoption. If starting fresh or optimizing for cost and performance, bare metal is preferred. Document the existing infrastructure landscape and migration constraints.

### Config Sync scope and Git repository structure
Config Sync can synchronize from a monorepo (all cluster configs in one repository) or multiple repos (per-team or per-cluster). Monorepo simplifies management but can create bottleneck on reviews. Multi-repo provides team autonomy but complicates cross-cutting policy application. Document the team structure and change management requirements.

### Policy Controller enforcement mode
Policy Controller can run in "audit" mode (logs violations but allows deployment) or "enforce" mode (blocks violating deployments). Start with audit to understand the violation landscape, then move to enforce once policies are tuned. Document the rollout strategy and exception handling process for legitimate policy violations.

### Service mesh adoption
Cloud Service Mesh provides mTLS, observability, and traffic management but adds operational complexity (sidecar injection, control plane management, latency overhead). Evaluate whether the security posture improvement and observability gains justify the complexity. For Hosted environments where defense-in-depth is critical, service mesh is typically mandated. For simpler Connected deployments, network policies may suffice. Document the security requirements driving the decision.

### Container registry strategy for air-gapped (Hosted)
Harbor is the most common choice for air-gapped OCI registries. Alternatives include JFrog Artifactory and cloud-prem GitLab. The registry must support vulnerability scanning (Trivy integration), RBAC, replication, and garbage collection. Document the image promotion workflow: how images move from development (potentially cloud-connected) environments to the air-gapped production registry.

### VM Runtime on GKE vs. native container migration
VM Runtime on GKE allows running existing VMs inside Kubernetes pods, providing a lift-and-shift path. Native containerization provides better resource efficiency and Kubernetes integration but requires application refactoring. Document the migration approach per application: which applications warrant containerization effort and which should run as VMs indefinitely.

### Fleet management scope
GKE Enterprise fleets can span Connected, Edge, and cloud-based GKE clusters. Decide whether to manage all clusters in a single fleet (maximum consistency) or use separate fleets per environment/region (more isolation). Document the fleet boundary and the consistency vs. isolation tradeoff.

## Reference Architectures

### Hybrid cloud platform -- Connected
GKE on bare metal deployed in two on-prem datacenters, each with an admin cluster and multiple user clusters. Config Sync enforces consistent security policies and namespace configurations across all clusters from a central Git repository. Cloud Logging and Cloud Monitoring aggregate observability data in Google Cloud. Artifact Registry in Google Cloud serves container images with local registry mirrors on each cluster for pull performance and resilience. CI/CD pipelines in Cloud Build produce images, sign them with Binary Authorization attestations, and push to Artifact Registry. Multi-Cluster Ingress distributes traffic across datacenters for HA. Workload identity maps Kubernetes service accounts to Google Cloud IAM for secure access to BigQuery, Pub/Sub, and Cloud Storage from on-prem workloads.

### Telco 5G edge -- Edge
Google Distributed Cloud Edge appliances deployed at cell tower aggregation sites and central offices. Each site runs a small GKE cluster hosting network functions (User Plane Function, Session Management Function) as containerized workloads. Google manages the hardware and infrastructure lifecycle. Operators manage the workloads through GKE Enterprise fleet management. Cloud Monitoring collects network function performance metrics. Traffic engineering policies route user plane traffic locally for low-latency Mobile Edge Computing (MEC) applications (AR/VR, autonomous vehicles, industrial IoT). Additional edge application clusters host third-party MEC applications alongside the network functions.

### Defense / sovereign operations -- Hosted
Google Distributed Cloud Hosted deployed in a government-classified facility. Fully air-gapped: no network connectivity to Google Cloud or the internet. All management interfaces (GKE control plane, logging, monitoring, registry) run locally on the Hosted infrastructure. Harbor serves as the container registry with offline vulnerability scanning via Trivy. Updates are delivered on encrypted physical media, validated against cryptographic signatures, and applied during scheduled maintenance windows. Binary Authorization enforces that only attested images from the approved supply chain run on the clusters. Policy Controller enforces CIS Kubernetes benchmarks and organization-specific security policies. Workload identity integrates with the facility's on-prem identity provider (e.g., LDAP, CAC/PKI). Multiple user clusters provide workload isolation by classification level.

### Retail edge -- Connected
Small GKE on bare metal clusters (3 nodes each) deployed in regional distribution centers and flagship stores. Each cluster runs inventory management, point-of-sale APIs, and local ML inference (demand forecasting, visual search). Config Sync delivers application configurations from a central GitOps repository. Cloud Logging captures application logs for centralized analysis. During WAN outages, applications continue operating locally with data queued for sync. Fleet-wide policy ensures consistent security baselines (Pod Security Standards, network policies, image provenance) across hundreds of store clusters. A central GKE cluster in Google Cloud runs the platform management tools, CI/CD pipelines, and aggregated analytics.

### Multi-cluster platform with VM migration
Organizations migrating from VMware to Kubernetes deploy GKE on bare metal with VM Runtime on GKE. Legacy VMs are migrated using Migrate to Containers (generates container artifacts from VM images) or run directly as VM workloads inside GKE. New applications are developed as containers. Both VM and container workloads share the same cluster infrastructure, networking (Cloud Service Mesh provides unified mTLS and observability), and policy framework. Over time, VM workloads are incrementally containerized. This architecture provides a single operational model during the migration period rather than maintaining parallel VM and container platforms.

## See Also

- `providers/gcp/containers.md` -- GKE and GKE Enterprise fleet management
- `providers/gcp/networking.md` -- GCP networking for hybrid connectivity
- `providers/gcp/security.md` -- security controls for distributed deployments
