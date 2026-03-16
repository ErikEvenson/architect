# OpenShift Security

## Checklist

- [ ] **[Critical]** Review and restrict Security Context Constraints (SCCs): avoid granting `anyuid` or `privileged` SCCs to application workloads
- [ ] **[Critical]** Configure OAuth identity provider: LDAP, Active Directory, OIDC (Keycloak, Azure AD, Okta), GitHub, or HTPasswd for break-glass access
- [ ] **[Critical]** Define RBAC strategy: ClusterRoles for platform operations, namespaced Roles for application teams, Groups synced from identity provider
- [ ] **[Critical]** Enable pod security admission (PSA) labels per namespace: `restricted`, `baseline`, or `privileged` (enforces Kubernetes pod security standards)
- [ ] **[Recommended]** Configure image signature verification and image policy (ImagePolicy admission, Sigstore/cosign integration)
- [ ] **[Recommended]** Deploy Quay registry with Clair vulnerability scanning; define policies to block images with critical CVEs
- [ ] **[Critical]** Implement network policies for namespace-to-namespace isolation (default-deny ingress and egress)
- [ ] **[Recommended]** Install Compliance Operator and run CIS OpenShift Benchmark, NIST 800-53, and PCI-DSS scans; remediate findings
- [ ] **[Critical]** Configure audit logging: API server audit policy, forwarding audit logs to SIEM (Splunk, Elastic, QRadar)
- [ ] **[Critical]** Manage secrets: evaluate Sealed Secrets, External Secrets Operator (ESO) with HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault
- [ ] **[Critical]** Enable FIPS mode at install time if required (cannot be enabled post-install; affects crypto libraries cluster-wide)
- [ ] **[Critical]** Configure certificate rotation: API server certs, ingress certs, service-serving certs (auto-rotated by service-ca operator)
- [ ] **[Recommended]** Implement image pull policies: restrict registries via `ImageContentSourcePolicy` or `ImageDigestMirrorSet`, enforce `Always` pull policy for mutable tags
- [ ] **[Critical]** Set up cluster-admin break-glass procedures: HTPasswd identity provider with emergency admin user, audit trail for privileged operations

## Why This Matters

OpenShift is more secure by default than upstream Kubernetes. Pods run as non-root by default (the `restricted` SCC), SELinux is enforced on RHCOS nodes, and the OAuth server provides integrated authentication. However, these defaults are frequently weakened during development ("just grant anyuid") and never tightened for production.

Security Context Constraints (SCCs) are OpenShift's mechanism for controlling what a pod can do at the OS level -- user IDs, capabilities, SELinux contexts, host networking, and volume types. SCCs predate and are more granular than Kubernetes Pod Security Standards (PSS). The priority order matters: when a pod matches multiple SCCs, the most restrictive one that satisfies the pod's requirements is chosen. Granting `privileged` or `anyuid` SCCs to service accounts is a common antipattern that effectively disables container isolation.

The Compliance Operator automates security scanning using OpenSCAP profiles. It creates `ComplianceScan` and `ComplianceSuite` CRDs, produces `ComplianceCheckResult` objects for each rule, and can auto-remediate findings by creating `MachineConfig` objects or applying `ComplianceRemediation` CRDs. This is critical for regulated industries (finance, healthcare, government) that require demonstrable compliance posture.

Secret management is a persistent challenge. Kubernetes Secrets are base64-encoded (not encrypted) by default. OpenShift encrypts etcd at rest, but secrets in Git repositories remain a risk. External Secrets Operator bridges the gap by syncing secrets from external vaults into Kubernetes Secret objects, keeping sensitive data out of Git entirely.

## Common Decisions (ADR Triggers)

- **SCC strategy**: Grant minimum SCCs per workload vs blanket `anyuid` for convenience. Create custom SCCs for specific workload requirements (e.g., allow `NET_BIND_SERVICE` capability without full `anyuid`). Use `oc adm policy who-can use scc/privileged` to audit access.
- **Identity provider selection**: OIDC (Keycloak, Azure AD) is recommended for SSO integration and MFA. LDAP sync with Group objects enables automatic RBAC assignment. HTPasswd should only be used for break-glass admin access.
- **Image security policy**: Block unsigned images vs allow with warnings. Quay Clair scanning vs Trivy operator vs ACS (Red Hat Advanced Cluster Security / StackRox). ACS provides runtime threat detection beyond build-time scanning.
- **Secrets management approach**: Sealed Secrets (encrypts secrets for Git storage) vs External Secrets Operator (syncs from external vault) vs CSI Secrets Store Driver (mounts secrets as volumes). ESO with Vault is the most common enterprise pattern.
- **Compliance framework**: CIS Benchmark (general best practices) vs NIST 800-53 (US government) vs PCI-DSS (payment card data) vs custom profiles. The Compliance Operator supports tailored profiles for organization-specific rules.
- **FIPS mode**: Required for US federal workloads (FedRAMP, FISMA). Must be enabled at install time. FIPS mode restricts cryptographic algorithms cluster-wide, which can break applications using non-FIPS-compliant crypto libraries.
- **Red Hat ACS (StackRox) deployment**: ACS provides runtime security, network segmentation analysis, vulnerability management, and compliance dashboards beyond what the Compliance Operator offers. Evaluate whether the additional cost and complexity is justified.

## Version Notes

| Feature | OCP 4.12 | OCP 4.14 | OCP 4.16 |
|---|---|---|---|
| Pod Security Admission (PSA) | Enabled (warn/audit) | Enforced (restricted by default) | Enforced (restricted by default) |
| SCCs | Supported | Supported | Supported (PSA coexists) |
| Compliance Operator | 0.1.x (CIS, NIST) | 1.3.x (CIS, NIST, PCI-DSS) | 1.5.x (CIS 1.5, NIST, PCI-DSS, STIG) |
| ACS / StackRox | 3.x (separate install) | 4.x (integrated RHACS operator) | 4.4+ (deeper OCP integration) |
| Sigstore / cosign integration | Tech Preview | GA | GA |
| External Secrets Operator (ESO) | Community supported | OLM-distributed | GA (Red Hat supported) |
| FIPS mode | Supported (install-time) | Supported (install-time) | Supported (install-time) |
| Kyverno support | Community | Community | Tech Preview |

**Key changes across versions:**
- **Pod Security Admission enforcement timeline:** OCP 4.12 enabled PSA in `warn` and `audit` modes by default, allowing teams to identify non-compliant pods without breaking workloads. OCP 4.14 began enforcing the `restricted` Pod Security Standard by default on new namespaces. Existing namespaces retained their labels. OCP 4.16 continues enforcement; namespaces must explicitly opt into `baseline` or `privileged` if needed.
- **SCCs and PSA coexistence:** SCCs remain the primary pod security mechanism in OpenShift. PSA operates alongside SCCs -- both must be satisfied. SCCs provide finer-grained control (SELinux contexts, supplemental groups, volume types) that PSA does not cover.
- **Compliance Operator versions:** Newer versions added additional profiles (STIG for DoD environments), improved auto-remediation reliability, and added support for tailored profiles with inheritance. Version 1.5.x in OCP 4.16 includes updated CIS Benchmark 1.5 rules.
- **ACS/StackRox integration:** In OCP 4.12, ACS was deployed separately. Starting with OCP 4.14, the RHACS operator is available in OperatorHub with tighter integration into the OCP console for vulnerability dashboards and policy management. OCP 4.16 adds deeper integration with the OCP audit subsystem.

## Reference Architectures

- **Enterprise multi-tenant security**: Azure AD OIDC with group sync, namespace-scoped Roles per team, default-deny NetworkPolicy, `restricted` SCC enforced, Quay with Clair scanning, ESO with HashiCorp Vault, Compliance Operator with CIS benchmark.
- **US Federal / FedRAMP**: FIPS mode enabled at install, NIST 800-53 compliance scans, ACS for runtime threat detection, audit logs forwarded to Splunk, etcd encryption enabled, signed images only, air-gapped deployment with mirror registry.
- **Financial services (PCI-DSS)**: Cardholder data namespaces with `restricted` SCC and strict NetworkPolicy, Compliance Operator with PCI-DSS profile, audit logging to QRadar SIEM, secrets in Vault with automatic rotation, image scanning gates in CI/CD pipeline.
- **Healthcare (HIPAA)**: Encryption at rest (ODF dm-crypt or cloud KMS), encryption in transit (service mesh mTLS), audit logging for all PHI access, RBAC with principle of least privilege, namespace isolation for PHI workloads, break-glass procedures documented.
- **Zero-trust platform**: Service mesh with strict mTLS (PeerAuthentication STRICT mode), SPIFFE/SPIRE for workload identity, OPA Gatekeeper or Kyverno for policy enforcement, network observability for anomaly detection, short-lived certificates with cert-manager.
