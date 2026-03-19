# Network Segmentation

## Scope

Covers network segmentation as an architecture pattern across cloud, on-premises, and hybrid environments — including macro-segmentation (VPC/VNet tiers, DMZ, trust zones), micro-segmentation (per-workload policies), Kubernetes network policies, service mesh as a segmentation layer, compliance-driven isolation, and east-west vs north-south traffic controls. For foundational network design decisions (CIDR planning, load balancing, connectivity), see `general/networking.md`. For zero trust principles that build on segmentation, see `patterns/zero-trust.md`.

## Overview

Network segmentation divides a network into isolated zones with controlled communication paths between them. The goal is to limit blast radius — when one workload is compromised, segmentation prevents the attacker from moving laterally to other workloads, tiers, or data stores. Segmentation operates at multiple granularity levels: macro-segmentation defines broad trust zones (DMZ, application tier, data tier); micro-segmentation enforces per-workload or per-service policies regardless of network location; and service mesh adds application-layer segmentation with identity-based authorization and mutual TLS.

## Checklist

- [ ] **[Critical]** What trust zones does the architecture define, and what traffic is permitted between them? (define macro-segmentation boundaries — DMZ for internet-facing services, application tier for business logic, data tier for databases and storage, management tier for admin access and monitoring; map allowed traffic flows between zones with explicit deny-all default; document every cross-zone flow with business justification and owning team)
- [ ] **[Critical]** Is default-deny enforced at every segmentation boundary? (security groups, NACLs, firewall rules, and Kubernetes network policies should all default to deny-all ingress and egress unless explicitly permitted; verify that new workloads deployed into a segment cannot communicate with anything until rules are created — implicit allow is the most common segmentation failure)
- [ ] **[Critical]** How is east-west traffic controlled between services within the same tier? (east-west traffic between services in the same subnet or security group is often unrestricted; micro-segmentation with per-service security groups, Kubernetes NetworkPolicy, or service mesh authorization policies prevents lateral movement within a tier; without east-west controls, compromising any service in a tier compromises all of them)
- [ ] **[Critical]** What cloud-native segmentation controls are used, and are they layered appropriately? (Security Groups and NSGs for instance-level filtering, NACLs and route tables for subnet-level enforcement, VPC Service Controls or Private Link for service-level isolation, firewall appliances or cloud-native firewalls for inspection — layered controls provide defense in depth so a misconfiguration in one layer does not expose the entire network)
- [ ] **[Critical]** How is segmentation enforced for compliance-scoped workloads? (PCI DSS requires CDE isolation with documented network diagrams and penetration testing of segmentation controls; HIPAA requires PHI to reside in access-controlled network zones with audit logging; FedRAMP requires defined authorization boundaries with continuous monitoring — compliance segmentation must be validated not just implemented, and auditors will test whether segmentation actually prevents cross-zone access)
- [ ] **[Recommended]** Is micro-segmentation implemented at the workload level in on-premises environments? (VMware NSX Distributed Firewall for vSphere workloads, Illumio or Guardicore/Akamai for agent-based segmentation across VMs and bare metal, VLAN-based segmentation with firewall zones for legacy infrastructure — agent-based solutions provide visibility into traffic flows before enforcing policy, which is essential for brownfield environments where undocumented dependencies are common)
- [ ] **[Recommended]** Are Kubernetes network policies enforced with a capable CNI plugin? (default Kubernetes NetworkPolicy requires a CNI that supports it — Calico, Cilium, or Antrea; the default kubenet CNI does not enforce policies at all; start with default-deny namespace policies and explicitly allow required pod-to-pod and pod-to-service communication; Cilium adds L7 visibility and DNS-aware policies; consider CiliumNetworkPolicy or CalicoNetworkPolicy for features beyond the native spec)
- [ ] **[Recommended]** Is service mesh used as a segmentation layer for service-to-service communication? (Istio AuthorizationPolicy or Linkerd Server/ServerAuthorization enforce identity-based access control with mTLS between services — segmentation based on cryptographic identity rather than IP address; service mesh segmentation complements but does not replace network-level controls; evaluate whether the operational overhead of a mesh is justified by the number of services and sensitivity of traffic)
- [ ] **[Recommended]** How is segmentation monitored for drift, misconfigurations, and violations? (VPC flow logs, NSX Distributed Firewall logs, Calico/Cilium flow logs, and service mesh telemetry detect unexpected cross-zone traffic; cloud security posture management tools — Prisma Cloud, Wiz, AWS Security Hub — alert on overly permissive security groups; establish a regular review cadence for segmentation rules and automate detection of rules that allow 0.0.0.0/0 or any-to-any traffic)
- [ ] **[Recommended]** How does segmentation work across hybrid and multi-cloud environments? (consistent segmentation policy across AWS VPCs, Azure VNets, GCP VPCs, and on-premises networks requires a unified policy layer — Illumio, Prisma Cloud, or Aviatrix for multi-cloud segmentation; transit gateways and hub-and-spoke topologies centralize inter-cloud inspection; avoid inconsistent segmentation postures where cloud environments are tightly segmented but on-premises is flat)
- [ ] **[Recommended]** How are north-south traffic controls coordinated with segmentation? (north-south traffic enters through internet-facing load balancers, WAF, and API gateways into the DMZ tier — ensure north-south entry points cannot bypass segmentation to reach internal tiers directly; use separate external and internal load balancers; place WAF and DDoS mitigation at the network edge before traffic reaches segmented zones)
- [ ] **[Optional]** Is PrivateLink, Private Link, or Private Service Connect used to access cloud services and SaaS without traversing the public internet? (AWS PrivateLink, Azure Private Link, and GCP Private Service Connect provide private connectivity to managed services — S3, RDS, Azure SQL, GCP Cloud Storage — and supported SaaS products; eliminates the need for NAT gateways and internet-facing routes for service access; reduces exposure to data exfiltration through DNS or internet paths)
- [ ] **[Optional]** Are segmentation controls tested through adversarial validation? (penetration testing should explicitly verify that segmentation prevents cross-zone access; tools like Infection Monkey or manual lateral movement testing validate that compromising a workload in one zone does not provide access to other zones; PCI DSS requires annual segmentation penetration testing — even non-PCI environments benefit from this validation)

## Common Mistakes

- **Flat networks with security-group-only segmentation:** Relying solely on security groups without subnet separation, NACLs, or micro-segmentation creates a single layer of defense where one misconfigured rule exposes the entire network.
- **Overly permissive security group rules:** Rules that allow 0.0.0.0/0 inbound or allow all traffic between groups accumulate over time as teams add "temporary" exceptions that become permanent; quarterly rule reviews with automated compliance checks prevent this drift.
- **Security group sprawl:** Creating per-instance security groups without naming conventions, tagging, or lifecycle management leads to hundreds of orphaned groups that obscure the actual segmentation posture and make audits impossible.
- **Ignoring east-west traffic:** Investing heavily in north-south perimeter controls (WAF, DDoS, ingress firewalls) while leaving east-west traffic between services completely unrestricted — attackers who breach the perimeter move laterally through uncontrolled east-west paths.
- **Segmentation that exists on paper but is not enforced:** Drawing trust zone diagrams without validating that firewall rules, security groups, and network policies actually prevent cross-zone traffic; segmentation must be tested, not just documented.
- **Inconsistent segmentation across environments:** Production is segmented but development and staging share a flat network — attackers target the weakest environment and pivot to production through shared connectivity, CI/CD pipelines, or credential reuse.

## Why This Matters

Network segmentation is the primary architectural control that limits blast radius during a security breach. Without segmentation, an attacker who compromises any single workload — through a vulnerable dependency, stolen credential, or misconfigured service — can reach every other system on the network. The majority of significant breaches involve lateral movement through insufficiently segmented networks, where the initial foothold in a low-value system provides a path to high-value targets such as databases, key management systems, and administrative interfaces.

Segmentation is also a hard requirement for compliance in regulated industries. PCI DSS mandates network segmentation to reduce the scope of the Cardholder Data Environment (CDE) — without validated segmentation, the entire network is in scope for PCI assessment, multiplying audit cost and remediation effort. HIPAA requires that Protected Health Information (PHI) be stored and processed in access-controlled network segments with monitoring. FedRAMP defines authorization boundaries that must be enforced through network controls. Failing segmentation validation during a compliance audit can halt certification and block revenue.

Retrofitting segmentation into a flat network is one of the most disruptive infrastructure changes an organization can undertake. It requires mapping all traffic flows (many of which are undocumented), defining policy for every communication path, testing that segmentation does not break applications, and coordinating cutover across all teams. Organizations that design segmentation from the start avoid this costly retrofit and benefit from contained blast radius, cleaner compliance posture, and simpler troubleshooting throughout the infrastructure lifecycle.

## Common Decisions (ADR Triggers)

### ADR: Segmentation Granularity

**Context:** The architecture must decide how finely to segment the network — from broad tier-based zones to per-workload micro-segmentation.

**Options:**

| Approach | Granularity | Blast Radius | Operational Complexity | Best Fit |
|---|---|---|---|---|
| Macro-segmentation (VPC/VNet tiers, VLANs) | Subnet/tier level | Contained to tier — all workloads in a tier can communicate | Low — well-understood, maps to compliance frameworks | Traditional applications, smaller environments, compliance baseline |
| Micro-segmentation (per-workload policy) | Individual workload | Contained to single workload | Medium to high — requires traffic flow discovery and policy engineering | Regulated environments, multi-tenant platforms, high-security workloads |
| Service mesh segmentation (mTLS + AuthZ) | Per-service at L7 | Contained to single service with identity-based verification | High — requires mesh deployment, sidecar overhead, policy management | Microservices architectures with 10+ services, environments requiring L7 policy |
| Combined (macro + micro + mesh) | All layers | Minimal — defense in depth at every level | Highest — multiple policy layers to maintain consistently | High-security regulated environments, financial services, government |

**Decision drivers:** Number of workloads and services, compliance requirements, team operational maturity with segmentation tooling, whether the environment is greenfield or brownfield, and risk tolerance for lateral movement.

### ADR: Micro-Segmentation Platform

**Context:** East-west traffic between workloads must be controlled to prevent lateral movement, requiring a micro-segmentation platform that fits the workload types in the environment.

**Options:**
- **VMware NSX Distributed Firewall:** Hypervisor-level enforcement for vSphere workloads, no agent required on VMs, integrates with vCenter for workload context. Locked to VMware environments. Best for organizations with existing NSX investment.
- **Illumio Core:** Agent-based, works across VMs, bare metal, and containers on any platform. Provides traffic flow visualization (Illumination) before policy enforcement. Platform-agnostic but requires agent deployment and management.
- **Guardicore/Akamai Microsegmentation:** Agent-based with process-level visibility, supports VMs and containers, includes deception capabilities. Acquired by Akamai. Strong in hybrid environments.
- **Cloud-native security groups and NACLs:** No additional tooling — use per-instance security groups with references between groups. Limited visibility into traffic flows, no application-level context, rules are IP/port only. Sufficient for simple environments with few workloads.
- **Calico/Cilium (Kubernetes):** CNI-level enforcement for container workloads. Calico supports both Kubernetes and non-Kubernetes hosts via calico-node. Cilium provides eBPF-based enforcement with L7 visibility. Container-focused.

**Decision drivers:** Workload types (VMs, containers, bare metal, mixed), existing virtualization platform, cloud vs on-premises, need for traffic flow visualization before enforcement, operational capacity for agent management, and budget.

### ADR: Kubernetes Network Policy Strategy

**Context:** Kubernetes clusters require network policies to restrict pod-to-pod communication, but the policy model and CNI plugin must be chosen deliberately.

**Options:**
- **Native Kubernetes NetworkPolicy with Calico:** Standard API, portable across clusters, supports ingress and egress rules by namespace, pod label, and CIDR. Calico extends with GlobalNetworkPolicy for cluster-wide rules. Well-documented and widely adopted.
- **CiliumNetworkPolicy with Cilium:** eBPF-based enforcement, adds L7 policy (HTTP method/path filtering), DNS-aware egress policies, and transparent encryption. Higher performance than iptables-based enforcement. Requires Cilium as CNI.
- **Default-deny with progressive allow-listing:** Start with deny-all ingress and egress in every namespace, then add policies as services are deployed. Most secure but requires discipline to maintain and can break deployments that forget to include policy manifests.
- **Namespace-level isolation only:** Restrict cross-namespace traffic but allow free communication within a namespace. Simpler to manage, provides meaningful isolation between teams or environments sharing a cluster. Insufficient for high-security workloads.

**Decision drivers:** CNI plugin already in use, need for L7 policy granularity, team familiarity with network policy authoring, whether policies are managed via GitOps, and compliance requirements for container-level segmentation.

### ADR: Compliance-Driven Segmentation Scope

**Context:** Compliance frameworks require specific segmentation controls, and the scope of segmentation directly affects the scope of audit and assessment.

**Options:**
- **Minimal segmentation (entire network in scope):** No segmentation boundary around regulated data — all systems are in scope for compliance assessment. Simplest to implement, most expensive to audit, highest risk.
- **Dedicated VPC/VNet for regulated workloads:** Separate VPC/VNet for CDE (PCI), PHI (HIPAA), or authorization boundary (FedRAMP) with controlled connectivity to non-regulated environments. Reduces assessment scope significantly. Requires maintaining separate infrastructure.
- **Micro-segmented zone within shared infrastructure:** Regulated workloads share infrastructure but are isolated through security groups, network policies, and encryption. Reduces infrastructure duplication. Requires rigorous segmentation validation to satisfy auditors.

**Decision drivers:** Volume of regulated data, number of systems that process it, whether the organization operates dedicated compliance infrastructure or shared platforms, cost of audit scope expansion, and auditor/QSA expectations for segmentation evidence.

## Reference Links

- [PCI DSS Network Segmentation Guidance](https://www.pcisecuritystandards.org/)
- [NIST SP 800-125B: Secure Virtual Network Configuration for VM Protection](https://csrc.nist.gov/pubs/sp/800/125/b/final)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Calico Network Policy](https://docs.tigera.io/calico/latest/network-policy/)
- [Cilium Network Policy](https://docs.cilium.io/en/stable/security/policy/)
- [Istio Authorization Policy](https://istio.io/latest/docs/reference/config/security/authorization-policy/)
- [VMware NSX Distributed Firewall](https://docs.vmware.com/en/VMware-NSX/index.html)
- [Illumio Core](https://www.illumio.com/products/illumio-core)
- [AWS VPC Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Azure Network Security Groups](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)

## See Also

- `general/networking.md` — Network topology, CIDR planning, load balancing, and foundational network architecture decisions
- `general/security.md` — Security controls including IAM, encryption, audit logging, and firewall design that segmentation enforces
- `patterns/zero-trust.md` — Zero trust architecture that extends segmentation with identity-based access, device posture, and continuous verification
- `general/service-mesh.md` — Service mesh mTLS and authorization policies as an application-layer segmentation mechanism
- `compliance/pci-dss.md` — PCI DSS requirements for CDE network segmentation and annual segmentation penetration testing
- `compliance/hipaa.md` — HIPAA requirements for PHI network isolation and access controls
- `patterns/hybrid-cloud.md` — Hybrid cloud architectures where segmentation must span on-premises and cloud environments consistently
