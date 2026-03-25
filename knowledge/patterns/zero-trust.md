# Zero Trust Architecture

## Scope

Covers zero trust architecture principles, identity-aware access proxies, microsegmentation, device posture assessment, continuous authentication, workload identity, and implementation maturity models. Applicable to any environment transitioning from perimeter-based security to identity-and-context-based access controls — cloud-native, on-premises, or hybrid.

## Overview

Zero trust is a security model that eliminates implicit trust based on network location. Every access request — whether from a user, device, or workload — is authenticated, authorized, and continuously validated regardless of where it originates. The core principles are: never trust, always verify; assume breach; enforce least privilege; and inspect and log all traffic. Zero trust is not a single product but an architectural pattern that spans identity, network, device, application, and data layers.

## Checklist

- [ ] **[Critical]** What are the trust boundaries in the current architecture, and which implicit trust assumptions must be eliminated? (map existing network perimeters, VPN tunnels, and "trusted" subnets to identify where access is granted based on network location rather than identity verification)
- [ ] **[Critical]** How is user identity verified before granting access to each resource? (select an identity-aware proxy — Cloudflare Access, Zscaler Private Access, Google BeyondCorp Enterprise, Azure AD Application Proxy — or cloud-native ZTNA service; enforce MFA at the proxy layer, not just at initial VPN login)
- [ ] **[Critical]** Is microsegmentation implemented to restrict lateral movement? (network-level with NSX Distributed Firewall, Illumio, or Guardicore/Akamai; application-level with Kubernetes NetworkPolicy or Calico/Cilium; service mesh mTLS with Istio, Linkerd, or Consul Connect — choose based on environment type and operational maturity)
- [ ] **[Critical]** How are workload identities established and verified for service-to-service communication? (SPIFFE/SPIRE for platform-agnostic workload identity, cloud-native workload identity federation for AWS/Azure/GCP, Kubernetes service account token projection — avoid shared secrets or long-lived service account keys)
- [ ] **[Critical]** Is device posture assessed before granting access? (verify OS patch level, disk encryption status, endpoint protection agent presence, and managed device enrollment; integrate with MDM platforms — Intune, Jamf, CrowdStrike Falcon — and enforce posture checks continuously, not just at session start)
- [ ] **[Recommended]** What is the ZTNA vs VPN migration strategy? (ZTNA provides per-application access with identity verification, while VPN grants broad network access; ZTNA reduces attack surface but requires application-by-application onboarding; plan for a phased transition with VPN as fallback during migration)
- [ ] **[Recommended]** How is continuous authentication and authorization enforced throughout a session? (re-evaluate risk signals — user behavior anomalies, device posture changes, impossible travel, IP reputation shifts — and step up authentication or terminate sessions when risk increases; avoid treat-authentication-as-one-time-event patterns)
- [ ] **[Recommended]** Which cloud-native zero trust services are used for cloud-hosted applications? (AWS Verified Access for VPC-based workloads, Azure Conditional Access with Private Link for Azure resources, GCP BeyondCorp Enterprise for Google Cloud and hybrid workloads — evaluate integration depth with existing identity providers)
- [ ] **[Recommended]** What is the policy engine and where are access policies defined? (centralized policy engine — OPA/Rego, Cedar, Azure AD Conditional Access, Google Access Context Manager — that evaluates identity, device posture, location, time, and risk score for every access decision; avoid scattering policy logic across individual applications)
- [ ] **[Recommended]** How is east-west traffic between services inspected and authorized? (service mesh authorization policies, API gateway token validation for internal APIs, or microsegmentation firewall rules — define explicit allow-lists for every service-to-service communication path; default-deny all unspecified east-west traffic)
- [ ] **[Recommended]** What is the implementation maturity model and phased rollout plan? (crawl: inventory assets, deploy identity provider, enable MFA everywhere; walk: deploy identity-aware proxy for critical applications, implement device posture checks, begin microsegmentation; run: continuous authentication, full microsegmentation, workload identity for all service-to-service traffic, automated policy enforcement)
- [ ] **[Optional]** How are legacy applications that cannot support modern authentication integrated into the zero trust model? (deploy an identity-aware reverse proxy or application gateway in front of legacy applications, translate modern tokens to legacy auth protocols, and isolate legacy systems in tightly segmented network zones with enhanced monitoring)
- [ ] **[Optional]** Is data-centric zero trust implemented beyond network and identity layers? (classify data sensitivity levels, enforce access controls at the data layer — column-level database encryption, DRM for documents, tokenization for sensitive fields — so data remains protected even if an authorized session is compromised)

## Why This Matters

Traditional perimeter-based security assumes that everything inside the corporate network is trustworthy. This assumption fails catastrophically when an attacker breaches the perimeter through phishing, credential theft, a compromised VPN endpoint, or a supply chain attack — once inside, they move laterally through "trusted" networks with minimal resistance. The majority of high-profile breaches in recent years involved lateral movement through flat networks after an initial foothold, often remaining undetected for months.

Zero trust directly addresses this by treating every access request as potentially hostile, regardless of network location. Microsegmentation limits blast radius by preventing an attacker who compromises one workload from reaching others. Identity-aware proxies eliminate the VPN model where a single compromised credential grants broad network access. Continuous authentication detects anomalous behavior mid-session rather than relying on a single login event. Device posture assessment ensures that unpatched or unmanaged devices — common vectors for malware — cannot access sensitive resources.

The cost of implementing zero trust is significant, involving identity infrastructure, proxy deployments, microsegmentation tooling, and policy engineering. However, the cost of not implementing it is higher — the average breach dwell time exceeds 200 days in perimeter-based environments, while organizations with mature zero trust architectures detect and contain breaches significantly faster. Regulatory frameworks including NIST 800-207, executive orders on federal cybersecurity, and PCI DSS 4.0 increasingly mandate zero trust principles, making adoption a compliance requirement as well as a security imperative.

## Common Decisions (ADR Triggers)

### ADR: ZTNA vs VPN Strategy

**Context:** The organization must decide whether to replace VPN-based remote access with zero trust network access, maintain both in parallel, or adopt a phased migration.

**Options:**

| Approach | Access Model | Advantages | Disadvantages |
|---|---|---|---|
| VPN only | Broad network access after authentication | Well-understood, existing infrastructure, supports all protocols | Flat network access post-auth, single point of compromise, poor mobile experience, VPN concentrator scaling |
| ZTNA only | Per-application access with identity + device verification | Minimal attack surface, granular audit, no network-level access | Requires application-by-application onboarding, may not support UDP/non-HTTP protocols, vendor lock-in risk |
| Hybrid (ZTNA + VPN fallback) | ZTNA for modern apps, VPN for legacy/unsupported | Incremental migration, maintains access to legacy systems | Two systems to maintain, users may default to VPN, increased operational complexity |

**Decision drivers:** Application portfolio maturity (how many support OIDC/SAML), protocol requirements (SSH, RDP, database protocols), legacy system dependencies, user population size and device diversity, and timeline for full migration.

### ADR: Microsegmentation Approach

**Context:** East-west traffic must be controlled to prevent lateral movement, but the implementation approach varies by environment type and operational capacity.

**Options:**
- **Network-level microsegmentation (NSX DFW, Illumio, Guardicore/Akamai):** Applies firewall rules at the hypervisor or host level, independent of application changes. Works for VMs, bare metal, and containers. Requires traffic flow mapping before policy enforcement. Best for on-premises and hybrid environments with existing VM workloads.
- **Kubernetes NetworkPolicy (Calico, Cilium):** Namespace and pod-level network policies enforced by the CNI plugin. Native to Kubernetes environments. Does not cover VM-to-VM or non-Kubernetes workloads. Sufficient for container-only environments.
- **Service mesh mTLS (Istio, Linkerd, Consul Connect):** Encrypts and authenticates all service-to-service traffic with mutual TLS. Provides L7 authorization policies (method, path, headers). Adds sidecar proxy overhead (10-15% CPU and memory). Best for microservices architectures where L7 policy granularity is needed.

**Decision drivers:** Workload types (VMs vs containers vs mixed), environment (cloud vs on-premises vs hybrid), desired policy granularity (L3/L4 vs L7), team operational maturity with service mesh, and whether encryption of east-west traffic is a compliance requirement.

### ADR: Identity-Aware Proxy Selection

**Context:** An identity-aware proxy or ZTNA platform must be selected to enforce per-request authentication and authorization for user-facing applications.

**Options:**
- **Cloudflare Access:** CDN-integrated, supports browser-based and non-HTTP applications via Cloudflare Tunnel, device posture via WARP client. Strong for internet-facing applications. Per-seat pricing.
- **Zscaler Private Access (ZPA):** Full ZTNA platform with application connector model, inline inspection, and extensive protocol support. Enterprise-focused with broad integration ecosystem. Complex pricing model.
- **Google BeyondCorp Enterprise:** Integrated with Google Workspace and GCP, Chrome Enterprise for device posture, Access Context Manager for policy. Best for Google-centric environments.
- **Azure AD Application Proxy / Entra Private Access:** Integrated with Microsoft Entra ID, supports legacy on-premises web applications, Conditional Access policies. Best for Microsoft-centric environments.
- **AWS Verified Access:** Integrated with AWS IAM Identity Center and third-party IdPs, verifies identity and device posture for applications in VPCs. Best for AWS-hosted workloads.

**Decision drivers:** Existing identity provider (Okta, Entra ID, Google Workspace), primary cloud platform, protocol requirements beyond HTTP/HTTPS, device posture integration needs, and whether the proxy must cover on-premises applications in addition to cloud workloads.

### ADR: Workload Identity Strategy

**Context:** Service-to-service communication requires identity verification to prevent spoofing and enforce authorization, replacing network-location-based trust with cryptographic identity.

**Options:**
- **SPIFFE/SPIRE:** Platform-agnostic workload identity framework. Issues SVID (SPIFFE Verifiable Identity Documents) as X.509 certificates or JWT tokens. Works across Kubernetes, VMs, and bare metal. Requires deploying and operating the SPIRE server and agents. Best for multi-platform and multi-cloud environments.
- **Cloud workload identity federation (AWS IAM Roles for Service Accounts, Azure Workload Identity, GCP Workload Identity Federation):** Cloud-native binding between Kubernetes service accounts and cloud IAM roles. Zero additional infrastructure. Locked to a single cloud provider. Sufficient for single-cloud Kubernetes environments.
- **Service mesh identity (Istio Citadel, Linkerd identity):** Automatic mTLS certificate issuance and rotation for mesh workloads. Identity tied to Kubernetes service account. Only covers workloads within the mesh. Simplest to adopt if service mesh is already deployed.

**Decision drivers:** Multi-cloud vs single-cloud, workload platforms (Kubernetes, VMs, serverless), whether non-mesh workloads need cryptographic identity, compliance requirements for workload authentication, and whether the identity must be portable across environments.

### ADR: Policy Engine Selection

**Context:** Zero trust access decisions require a centralized policy engine that evaluates multiple signals (identity, device, location, risk) for every request.

**Options:**
- **OPA (Open Policy Agent) with Rego:** General-purpose policy engine, works with any platform, declarative policy language. Steep learning curve for Rego. Best for organizations standardizing policy across heterogeneous infrastructure.
- **Cloud-native conditional access (Azure Conditional Access, AWS Verified Access policies, GCP Access Context Manager):** Integrated with the cloud provider's identity and access platform. Easiest to adopt within a single cloud. Limited policy portability.
- **Cedar (AWS):** Purpose-built authorization policy language, used in AWS Verified Access and Amazon Verified Permissions. Strong for application-level authorization. AWS-centric.

**Decision drivers:** Multi-cloud vs single-cloud policy needs, team familiarity with policy-as-code, whether policies must cover infrastructure access and application access, and integration requirements with existing identity providers.

## Reference Links

- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [CISA Zero Trust Maturity Model](https://www.cisa.gov/zero-trust-maturity-model)
- [SPIFFE (Secure Production Identity Framework for Everyone)](https://spiffe.io/)
- [SPIRE (SPIFFE Runtime Environment)](https://spiffe.io/docs/latest/spire-about/)
- [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/policies/access/)
- [Zscaler Private Access](https://www.zscaler.com/products/zscaler-private-access)
- [Google BeyondCorp Enterprise](https://cloud.google.com/beyondcorp-enterprise)
- [AWS Verified Access](https://docs.aws.amazon.com/verified-access/)
- [Illumio Core](https://www.illumio.com/products/illumio-core)
- [Open Policy Agent (OPA)](https://www.openpolicyagent.org/)

## See Also

- `general/security.md` — Foundational security controls including IAM, encryption, and audit logging that underpin zero trust implementations
- `general/networking.md` — Network segmentation and firewall design that microsegmentation extends
- `general/service-mesh.md` — Service mesh mTLS and authorization policies for east-west traffic control
- `general/identity.md` — Identity provider selection, federation, and MFA that zero trust relies on
- `patterns/microservices.md` — Microservices communication patterns where service mesh zero trust is most applicable
- `patterns/hybrid-cloud.md` — Hybrid cloud architectures where zero trust bridges on-premises and cloud trust boundaries
