# NIST SP 800-207 Zero Trust Architecture

## Scope

NIST Special Publication 800-207 (August 2020) is the US federal reference document for Zero Trust Architecture. It defines Zero Trust as a cybersecurity paradigm that moves defenses from static, network-based perimeters to focus on users, assets, and resources, treating no entity as implicitly trustworthy regardless of network location. SP 800-207 is the framework reference; `patterns/zero-trust.md` is the architectural pattern. The two are complementary — SP 800-207 defines what Zero Trust *means* and the NIST-defined components and tenets, while the pattern file describes the *architectural shapes* organizations adopt to implement it. Covers the seven tenets, the logical Zero Trust Architecture components (Policy Engine, Policy Administrator, Policy Enforcement Point), the deployment variations (enhanced identity governance, micro-segmentation, software-defined perimeter), the trust algorithm models, and the relationship to identity-aware proxies, software-defined perimeters, and the cloud-native zero trust patterns.

## The Seven Tenets

SP 800-207 defines seven tenets that distinguish a Zero Trust Architecture from a traditional perimeter-based architecture:

1. **All data sources and computing services are considered resources.** Anything that can be accessed (databases, APIs, files, IoT devices, cloud workloads) is a resource subject to access policy. There are no "internal" resources that are exempt from policy enforcement.

2. **All communication is secured regardless of network location.** Traffic on the "internal" network is not implicitly trusted. TLS, mTLS, or other authenticated and encrypted channels are required between every component, not just between components that cross the perimeter.

3. **Access to individual enterprise resources is granted on a per-session basis.** Each access decision is made independently. A successful authentication does not grant a long-lived session that bypasses subsequent policy checks. Trust is not transitive — being authenticated to resource A does not automatically grant access to resource B.

4. **Access to resources is determined by dynamic policy.** Policy includes the requesting user/service, the requested resource, the device posture, environmental signals (location, time, threat intelligence), and historical behavior. Static IP-based or role-based-only policies are insufficient.

5. **The enterprise monitors and measures the integrity and security posture of all owned and associated assets.** Device posture, software inventory, vulnerability state, and patch level are continuously monitored and feed into the policy decision. A device that is out of compliance loses access until it is remediated.

6. **All resource authentication and authorization are dynamic and strictly enforced before access is allowed.** Authentication and authorization happen at every access, not just at session start. Re-authentication is triggered by policy events (long session, privilege change, anomalous behavior).

7. **The enterprise collects as much information as possible about the current state of assets, network infrastructure, and communications and uses it to improve its security posture.** Telemetry from every layer feeds into the trust algorithm. The architecture is designed to collect and use this telemetry, not just to log it.

## Logical Components

SP 800-207 defines a three-component logical model for the policy decision and enforcement layer:

### Policy Engine (PE)

The component that makes the actual access decision. It takes inputs from the user/device identity, the requested resource, the environmental signals, the policy database, and threat intelligence, and produces an access decision (allow, deny, conditional). The Policy Engine implements the **trust algorithm** (see below).

### Policy Administrator (PA)

The component that establishes or shuts down the communication path between the subject and the resource based on the Policy Engine's decision. It generates session-specific authentication tokens or credentials, configures the path (e.g., creating an mTLS tunnel, opening a firewall port), and tears down the path when the session ends or when policy revokes access.

### Policy Enforcement Point (PEP)

The component that actually enables, monitors, and terminates the connection between the subject and the resource. The PEP sits inline with the traffic and is the place where the access decision is operationally enforced. PEPs can be:

- **Identity-aware proxies** (Cloudflare Access, Google BeyondCorp Enterprise, AWS Verified Access, Microsoft Entra Application Proxy)
- **Service mesh sidecars** (Istio, Linkerd, Consul Connect) for service-to-service communication
- **API gateways** with auth integration
- **Network-layer enforcement** (NSGs, firewalls, software-defined perimeters)

The PE/PA/PEP split is logical, not physical — many implementations combine multiple components in a single product.

## The Trust Algorithm

The Trust Algorithm is the function that the Policy Engine uses to compute the access decision. SP 800-207 describes two general approaches:

- **Criteria-based** — the algorithm enforces a set of conditions (qualifications) that must all be satisfied for access. This is the more deterministic, easier-to-reason-about approach. Example: "user must be authenticated, device must be compliant, location must be in expected geo, request must be within business hours".
- **Score-based** — the algorithm computes a confidence score from the inputs and grants access if the score exceeds a threshold. The threshold can be different per resource. This is the more flexible approach but is harder to audit because the policy decision is the output of a model rather than a clear set of rules.

Most production implementations use criteria-based for the primary decision with score-based as a layered signal (e.g., "user must pass MFA AND be on a compliant device, but if the risk score from the identity provider is high, also require step-up authentication").

## Deployment Variations

SP 800-207 describes three primary deployment variations, each appropriate for different organizational contexts:

### Enhanced Identity Governance

The primary policy decision is based on identity (user, device, application). The network is largely orthogonal — traffic from any network is permitted to reach the resource, but the resource enforces identity-based access. This is the BeyondCorp model and the AWS Verified Access model. Appropriate when the organization can identity every user and device that should access the resource.

### Micro-segmentation

The network is divided into very small segments, each with its own access policy. Communication between segments requires explicit policy permission. This is the service mesh approach and the cloud-native NSG approach. Appropriate when the workload has well-defined service-to-service communication patterns.

### Software-Defined Perimeter (SDP)

A software-defined overlay network creates encrypted tunnels between authenticated clients and the resources they are authorized to access. The resources are not visible to unauthenticated clients (network-level invisibility). Appropriate when the organization needs to expose resources to external users without exposing them to the internet at large.

Most real implementations combine elements of all three variations — identity governance for human access to applications, micro-segmentation for service-to-service traffic, and SDP for vendor or contractor access.

## Common Implementation Patterns

### Replacing the VPN with an identity-aware proxy

- Internal applications are placed behind an identity-aware proxy (Cloudflare Access, Google IAP, AWS Verified Access)
- The proxy authenticates the user via the corporate identity provider (Okta, Entra ID, Google Workspace) and checks device posture (Jamf, Intune, CrowdStrike)
- The proxy enforces per-application access policy
- VPN is removed or restricted to legacy use cases that cannot work behind a proxy
- Result: same applications, same users, no VPN, dynamic access decisions per request

### Service-to-service mTLS via service mesh

- Workloads are deployed in a Kubernetes cluster with a service mesh (Istio, Linkerd, Consul Connect)
- Every service-to-service call is authenticated via SPIFFE identity (the service's cryptographic identity, not its IP)
- The service mesh enforces mTLS for every connection
- Authorization policies are written in terms of service identity, not network location
- Result: traffic on the cluster network is fully encrypted and authenticated, network policy enforcement is by service identity, network location is no longer a trust signal

### Cloud-native zero trust with the data perimeter pattern

- AWS / Azure / GCP workloads use the cloud provider's data perimeter equivalent (see `patterns/aws-data-perimeter.md`)
- Resource-based policies enforce that only workloads in the org can access resources in the org
- Identity-based policies enforce that workloads can only access the specific resources they need
- VPC endpoint / Private Link policies enforce that workloads can only reach the specific cloud services they need
- Result: a compromised workload's blast radius is limited to its actual permission scope, not "everything in the cloud account"

## Common Decisions

- **Identity-aware proxy vs VPN** — proxy is the right answer for internal application access by remote users. VPN is acceptable for legacy applications that cannot be moved behind a proxy and for full network access scenarios that genuinely require it (rare).
- **Service mesh vs network policy** — service mesh for mTLS and identity-based authorization. Network policy (Kubernetes NetworkPolicy, NSG, security groups) for coarser per-namespace or per-subnet rules. Both are typically deployed together.
- **Score-based vs criteria-based trust algorithm** — criteria-based for the primary decision, score-based as a layered signal. Pure score-based is hard to audit and hard to debug when it gets a decision wrong.
- **Phased rollout** — Zero Trust is rarely deployed all at once. Common phasing: (1) MFA everywhere, (2) device posture for sensitive resources, (3) identity-aware proxy for internal apps, (4) micro-segmentation for the most critical workloads, (5) full Zero Trust across the organization.
- **Pilot scope** — start with a workload that has clear identity boundaries, a small user population, and stakeholders who can articulate access requirements. Avoid starting with the workload that has the most political resistance or the most ambiguous access patterns.

## Reference Links

- [NIST SP 800-207 Zero Trust Architecture (PDF)](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf)
- [NIST National Cybersecurity Center of Excellence: Implementing a Zero Trust Architecture](https://www.nccoe.nist.gov/projects/implementing-zero-trust-architecture)
- [CISA Zero Trust Maturity Model](https://www.cisa.gov/zero-trust-maturity-model)
- [DoD Zero Trust Reference Architecture](https://dodcio.defense.gov/Library/)

## See Also

- `patterns/zero-trust.md` — Zero Trust as an architectural pattern (the implementation companion to this framework reference)
- `frameworks/nist-csf-2.0.md` — CSF 2.0 references Zero Trust as an implementation approach for several Subcategories
- `frameworks/nist-sp-800-53.md` — SP 800-53 controls that support Zero Trust implementation
- `providers/azure/rbac-and-managed-identities.md` — Azure-side identity foundation for Zero Trust
- `providers/aws/iam.md` — AWS IAM and the foundation for Zero Trust on AWS
- `general/identity.md` — general identity architecture
