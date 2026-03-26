# Ping Identity

## Scope

Ping Identity platform architecture: PingOne cloud identity platform (SSO, MFA, directory), PingFederate on-premises and hybrid federation server (SAML, OIDC, WS-Federation, WS-Trust), PingAccess web and API access management (policy enforcement, reverse proxy), PingDirectory LDAP directory and data store (high-performance, multi-master replication), PingOne Advanced Identity Cloud (formerly ForgeRock), DaVinci no-code identity orchestration, hybrid IdP deployment patterns (on-premises PingFederate with cloud PingOne), federation hub architectures for multi-partner B2B scenarios, PingOne Authorize for dynamic authorization (fine-grained, policy-based), PingOne Protect for fraud detection and risk scoring, and migration paths from legacy identity platforms.

## Checklist

- [ ] [Critical] Is the deployment model clearly defined as PingOne cloud-only, PingFederate on-premises only, or hybrid (PingFederate on-prem with PingOne cloud bridge), with documented rationale for the choice based on data residency, latency, and compliance requirements?
- [ ] [Critical] Are PingFederate server clusters deployed in an active-active or active-passive configuration with shared configuration across nodes, session state replication, and health monitoring, with a minimum of two nodes per datacenter for high availability?
- [ ] [Critical] Is the federation trust model designed with explicit partner connection configurations in PingFederate, including certificate lifecycle management (expiration monitoring, rotation procedures), and are metadata exchange processes documented for each partner?
- [ ] [Critical] Are authentication policies configured with adaptive MFA that evaluates device, network, and behavioral risk signals, with phishing-resistant factors (FIDO2, PingID with device biometrics) enforced for privileged and sensitive application access?
- [ ] [Critical] Is PingDirectory deployed with multi-master replication across sites for high availability, with replication topology designed to minimize convergence time, and are backend database sizes monitored to prevent disk exhaustion?
- [ ] [Critical] Are API access tokens issued by PingFederate or PingOne scoped to least-privilege with short expiration times (15 minutes or less for access tokens), and is token revocation supported and enforced for logout and session termination flows?
- [ ] [Recommended] Is PingAccess deployed as the policy enforcement point (PEP) for web applications and APIs, with agent-based or reverse-proxy deployment evaluated per application, and are access policies centrally managed with consistent enforcement?
- [ ] [Recommended] Is PingOne DaVinci used for identity orchestration flows (registration, progressive profiling, step-up authentication), replacing custom-coded authentication journeys with visual no-code workflows?
- [ ] [Recommended] Is a federation hub pattern implemented in PingFederate for organizations with many external partners, consolidating partner connections through a single hub rather than point-to-point federation relationships?
- [ ] [Recommended] Are PingFederate adapter chains and authentication selectors configured to support multiple authentication paths (employee vs partner vs customer) through a single federation endpoint, reducing application integration complexity?
- [ ] [Recommended] Is PingDirectory configured with entry-balancing or proxy distribution for environments exceeding 10 million entries, with connection pooling and search filter optimization to maintain sub-millisecond response times?
- [ ] [Recommended] Are PingFederate audit logs and PingOne event data forwarded to a SIEM, with detection rules for federation abuse (token replay, SAML assertion manipulation, unusual partner activity, certificate-based attacks)?
- [ ] [Recommended] Is a staging environment maintained for PingFederate configuration changes, with configuration archive exports used for version control and rollback capability, and are changes tested against partner connections before production deployment?
- [ ] [Optional] Is PingOne Authorize evaluated for fine-grained, attribute-based access control (ABAC) decisions at the API layer, replacing coarse role-based access control with dynamic policy evaluation?
- [ ] [Optional] Is PingOne Protect (fraud detection) integrated into authentication flows to provide risk scoring based on device intelligence, behavioral biometrics, and threat intelligence feeds?
- [ ] [Optional] Is migration from legacy identity platforms (CA SiteMinder, Oracle Access Manager, IBM ISAM) planned with a phased approach using PingFederate as a federation bridge during coexistence, maintaining existing sessions while routing new authentications through Ping?

## Why This Matters

Ping Identity is frequently selected for enterprises requiring hybrid identity architectures where on-premises federation must coexist with cloud identity services. PingFederate's strength in complex federation scenarios (hundreds of SAML/OIDC partners, WS-Trust token translation, SOAP-based legacy integration) makes it the platform of choice for large financial institutions, healthcare organizations, and government agencies that cannot move entirely to cloud identity.

The hybrid deployment model (PingFederate on-prem + PingOne cloud) introduces architectural complexity that must be carefully planned. Configuration drift between environments, certificate management across trust boundaries, and session management across on-prem and cloud components are common sources of outages. PingFederate clusters require shared configuration state, and a misconfigured node can issue invalid assertions to all connected applications.

PingDirectory's multi-master LDAP replication provides the performance needed for high-throughput environments (millions of authentications per day), but replication conflicts, schema consistency, and backup/restore procedures must be explicitly designed. Unlike cloud-only identity providers, Ping deployments carry infrastructure responsibility -- patching, scaling, certificate rotation, and disaster recovery are customer-managed for on-premises components.

## Common Decisions (ADR Triggers)

- **Deployment model** -- PingOne cloud-only (simplest operations) vs PingFederate on-premises (maximum control, data residency) vs hybrid with PingOne bridge (flexibility with complexity)
- **Federation architecture** -- Direct partner connections (simple, limited scale) vs federation hub in PingFederate (centralized management, scales to hundreds of partners) vs PingOne as the cloud federation endpoint
- **Access management** -- PingAccess reverse proxy (centralized enforcement, no app changes) vs PingAccess agent per app (distributed, requires deployment) vs application-native token validation (no PingAccess needed)
- **Directory strategy** -- PingDirectory as primary LDAP store (high performance, Ping-native) vs Active Directory as primary with PingDirectory as proxy/cache vs PingOne Directory (cloud-only, limited scale)
- **Authentication orchestration** -- PingFederate adapter chains (code-level flexibility) vs PingOne DaVinci flows (no-code, visual) vs PingOne Advanced Identity Cloud journeys (ForgeRock-based trees)
- **Token architecture** -- Reference tokens with PingAccess validation (centralized revocation) vs self-contained JWTs (stateless, harder to revoke) vs hybrid with short-lived JWTs and refresh tokens
- **Migration strategy** -- Big-bang cutover (risky, fast) vs phased with PingFederate as federation bridge (safe, extended coexistence) vs parallel running with DNS-based traffic shifting
- **Multi-datacenter HA** -- Active-active PingFederate clusters with global load balancing vs active-passive with DNS failover vs PingOne cloud as the resilient layer with on-prem as fallback

## See Also

- `general/identity.md` -- cross-platform identity and access management patterns
- `general/tier0-security-enclaves.md` -- Tier 0 security enclave design and hardening
- `providers/microsoft/active-directory.md` -- AD integration with PingFederate (AD adapter)
- `patterns/zero-trust.md` -- zero trust architecture patterns
- `providers/f5/load-balancer.md` -- load balancing for PingFederate and PingAccess clusters

## Reference Links

- [PingFederate Documentation](https://docs.pingidentity.com/pingfederate/latest/overview.html) -- PingFederate server administration, federation configuration, and adapter reference
- [PingOne Platform Documentation](https://docs.pingidentity.com/pingone/main/p1_landing_page.html) -- PingOne cloud platform setup, SSO, MFA, and directory services
- [PingAccess Documentation](https://docs.pingidentity.com/pingaccess/latest/overview.html) -- PingAccess deployment, policy configuration, and agent setup
- [PingDirectory Documentation](https://docs.pingidentity.com/pingdirectory/latest/overview.html) -- PingDirectory LDAP server, replication, and performance tuning
- [PingOne DaVinci](https://docs.pingidentity.com/davinci/latest/overview.html) -- no-code identity orchestration flows and connector catalog
- [Ping Identity Architecture Resources](https://www.pingidentity.com/en/resources.html) -- reference architectures, deployment guides, and best practices
- [PingFederate Cluster Administration](https://docs.pingidentity.com/pingfederate/latest/administrators_reference_guide/pf_c_clusterManagement.html) -- cluster configuration, node management, and session replication
