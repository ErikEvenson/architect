# HashiCorp Boundary

## Scope

HashiCorp Boundary: deployment models (self-managed vs HCP), target types (SSH, RDP, TCP, HTTP, Kubernetes), Vault credential injection, multi-hop worker topology, session recording, auth method integration (OIDC, LDAP), scope hierarchy, and host catalog strategies.


## Checklist

- [ ] **[Recommended]** Determine deployment model: self-managed Boundary (controllers + workers) vs HCP Boundary (managed control plane, self-hosted workers)
- [ ] **[Recommended]** Design target types for each access pattern: TCP (generic), SSH (session injection, key signing), RDP, HTTP, Kubernetes API server
- [ ] **[Critical]** Plan credential injection strategy: Vault credential libraries (dynamic database creds, SSH certificates, AD passwords) vs static credential stores
- [ ] **[Recommended]** Configure worker types: PKI workers (trusted by controller via certificate) vs KMS workers (join via shared KMS), ingress workers vs egress workers
- [ ] **[Recommended]** Design multi-hop worker topology for accessing private networks without VPN (ingress worker in DMZ -> egress worker in private subnet)
- [ ] **[Recommended]** Plan session recording configuration: storage buckets (S3/MinIO), retention policies, and playback access controls
- [ ] **[Critical]** Architect auth method integration: OIDC (Okta, Entra ID, Auth0), LDAP, password (dev only); map IdP groups to Boundary roles
- [ ] **[Recommended]** Define scope hierarchy: global -> org -> project; plan org/project structure aligned to team boundaries and access policies
- [ ] **[Recommended]** Configure managed groups to auto-assign roles based on IdP group membership (eliminates manual role assignment)
- [ ] **[Recommended]** Design host catalog strategy: static (manually registered hosts), dynamic (AWS, Azure, GCP plugin-based discovery), or Consul-based
- [ ] **[Optional]** Plan alias configuration for user-friendly target addressing (e.g., `boundary connect ssh -target-name prod-db` instead of target IDs)
- [ ] **[Optional]** Evaluate Boundary Desktop client vs CLI for end-user experience; plan distribution and auto-update strategy

## Why This Matters

Boundary implements identity-based access to infrastructure, replacing network-based controls (VPNs, bastion hosts, shared SSH keys) with a model where access is granted based on user identity and role, credentials are injected just-in-time and never exposed to users, and all sessions are recorded and auditable. This directly addresses the security risks of traditional access patterns: shared credentials, permanent network access, lack of session visibility, and credential sprawl. The multi-hop worker architecture eliminates VPN dependencies for accessing private networks, while Vault integration ensures credentials are dynamic, short-lived, and automatically rotated. Session recording provides a complete audit trail for compliance (SOC2, PCI-DSS, HIPAA) without requiring dedicated jump hosts with recording agents.

## License

HashiCorp transitioned all products from MPL 2.0 to BSL 1.1 in August 2023. The BSL restricts competitive use of the software — you cannot use it to build a product that competes with HashiCorp's commercial offerings. For internal infrastructure use, the BSL is functionally equivalent to open source. IBM completed its acquisition of HashiCorp in late 2024, which may affect product direction, licensing terms, and commercial offerings over time. Community forks under MPL 2.0 exist for organizations requiring open-source licensing: OpenTofu (Terraform fork) and OpenBao (Vault fork). Evaluate license terms and IBM's product roadmap for your specific use case before adoption.

## Common Decisions (ADR Triggers)

- **Boundary vs bastion hosts / jump boxes**: Bastion hosts provide a familiar model but require SSH key management, OS patching, and logging configuration. Boundary eliminates the bastion host entirely: users authenticate with their IdP, Boundary injects credentials and proxies the session. Choose Boundary when eliminating shared credentials and VPN dependencies is a priority.
- **Self-managed vs HCP Boundary**: HCP Boundary eliminates controller infrastructure management (database, TLS, high availability) but requires self-hosted workers for private network access. Self-managed gives full control but requires operating the controller cluster (PostgreSQL backend, load balancer, TLS certificates). Use HCP for reduced operational burden; self-managed for air-gapped or sovereignty requirements.
- **Vault credential injection vs static credentials**: Vault credential libraries generate dynamic, short-lived credentials per session (database creds, SSH certificates, AD passwords). Static credential stores hold fixed credentials that Boundary injects without exposing to users. Always prefer Vault dynamic credentials; use static credentials only for systems that cannot integrate with Vault.
- **Boundary vs Teleport vs StrongDM**: Boundary is open-source with deep Vault/Consul integration and a clear separation of control plane (controllers) and data plane (workers). Teleport provides an integrated solution with built-in certificate authority and session recording. StrongDM is SaaS-only with broad protocol support. Choose Boundary when already invested in HashiCorp ecosystem; Teleport for all-in-one; StrongDM for SaaS simplicity.
- **PKI workers vs KMS workers**: PKI workers use certificate-based authentication and support multi-hop topologies. KMS workers use shared encryption keys and are simpler to set up but do not support multi-hop. Use PKI workers for production and multi-hop; KMS workers for development environments.
- **Session recording: enabled by default vs opt-in**: Recording all sessions provides complete audit coverage but increases storage costs and may raise privacy concerns. Opt-in recording reduces costs but creates audit gaps. Enable by default for production targets; disable for development targets.

## Reference Architectures

### Zero Trust Access to Private Infrastructure
```
[User (Browser/CLI/Desktop)]
        |
  [OIDC Authentication (Okta/Entra ID)]
        |
  [Boundary Controller (HCP or self-managed)]
  - AuthN/AuthZ decisions
  - Session management
  - Credential brokering
        |
  [Ingress Worker (DMZ / Public Subnet)]
        |  (multi-hop)
  [Egress Worker (Private Subnet)]
        |
  +-----+------+------+
  |            |            |
[SSH Target]  [RDP Target]  [K8s API Server]
  |            |            |
[Vault: SSH   [Vault: AD   [Vault: K8s
 cert signing] password     service account
              rotation]     token]
```
Users authenticate via OIDC. Boundary authorizes based on role bindings. Ingress worker in DMZ accepts user connections. Multi-hop relays through egress worker in private subnet, eliminating VPN requirement. Vault generates just-in-time credentials for each session. Sessions are optionally recorded to S3.

### Self-Managed HA Deployment
```
[Load Balancer (API: 9200, Cluster: 9201)]
        |
+-------+-------+
|               |
[Controller 1]  [Controller 2]  [Controller 3]
        |               |               |
        +-------+-------+
                |
        [PostgreSQL (HA)]
        - Session state
        - Configuration
        - Auth data
                |
+-------+-------+-------+
|               |               |
[PKI Worker 1]  [PKI Worker 2]  [PKI Worker 3]
(AZ-a)          (AZ-b)          (AZ-c)
        |               |               |
  [Private Targets in each AZ]
```
Three controllers behind a load balancer for HA. PostgreSQL stores all state (use managed PostgreSQL like RDS/Cloud SQL for reduced operational burden). Workers deployed across availability zones, registered via PKI certificates. Controllers handle API and auth; workers handle session proxying (data plane never touches controllers).

### Scope and Permission Model
```
[Global Scope]
  |
  +-- [Org: Engineering]
  |     |
  |     +-- [Project: Platform]
  |     |     - Host Catalog: AWS dynamic (production VPCs)
  |     |     - Targets: SSH to EC2, K8s API
  |     |     - Credential Libraries: Vault SSH cert signer
  |     |     - Roles: platform-admin (full), platform-readonly (list+read)
  |     |
  |     +-- [Project: Application]
  |           - Host Catalog: Consul-based (service discovery)
  |           - Targets: TCP to application ports
  |           - Credential Libraries: Vault database dynamic creds
  |           - Roles: app-developer (connect), app-admin (full)
  |
  +-- [Org: Data]
        |
        +-- [Project: Analytics]
              - Host Catalog: Static (data warehouse hosts)
              - Targets: SSH, PostgreSQL
              - Credential Libraries: Vault PostgreSQL dynamic creds
              - Roles: data-analyst (connect to PostgreSQL only)
```
Global scope contains org-level auth methods (OIDC). Orgs map to business units. Projects contain targets, host catalogs, and credential libraries. Managed groups auto-assign roles based on IdP group membership (e.g., `engineering-platform` IdP group gets `platform-admin` role in the Platform project).

## Reference Links

- [Boundary Documentation](https://developer.hashicorp.com/boundary/docs) -- architecture, deployment models, targets, credential injection, and session recording
- [Boundary Tutorials](https://developer.hashicorp.com/boundary/tutorials) -- hands-on guides for HCP Boundary, self-managed deployment, and Vault integration
- [Boundary Reference Architecture](https://developer.hashicorp.com/boundary/docs/install-boundary/reference/reference-architecture) -- production deployment patterns for self-managed Boundary

## See Also

- `general/security.md` -- general security architecture patterns
- `providers/hashicorp/vault.md` -- Vault credential libraries for Boundary
- `providers/hashicorp/consul.md` -- Consul service discovery for dynamic host catalogs
