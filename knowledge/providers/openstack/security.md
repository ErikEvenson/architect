# OpenStack Security (Keystone, Barbican, RBAC, Compliance)

## Checklist

- [ ] Is Keystone configured with an appropriate identity backend? (SQL for small/dev, LDAP for enterprise directory integration with `[ldap]` section in `keystone.conf`, federated SAML2/OIDC via `[federation]` for SSO with corporate IdP like Okta, Azure AD, Keycloak)
- [ ] Are Keystone domains used to isolate organizational units? (default domain for service accounts, separate domains per business unit or customer, domain-scoped admin roles for delegated administration)
- [ ] Is multi-factor authentication enabled for privileged users? (Keystone MFA rules via `[auth] methods = password,totp`, TOTP credentials per user, or enforced through federated IdP MFA policies)
- [ ] Are application credentials used instead of user passwords for automation? (`openstack application credential create` with restricted roles and expiration, secret stored in vault, not embedded in scripts or CI/CD pipelines)
- [ ] Is service-to-service authentication configured securely? (each OpenStack service has a dedicated service user in Keystone, credentials in service config files with restricted file permissions `0640`, consider `[keystone_authtoken]` `service_token_roles_check = True`)
- [ ] Are security groups configured as default-deny ingress with explicit allow rules, and is the difference from Firewall-as-a-Service (FWaaS v2) understood? (security groups are per-port/instance, FWaaS applies to router interfaces for network-wide policy)
- [ ] Is Barbican deployed for secret management? (symmetric keys, certificates, private keys, passphrases -- used by Cinder for volume encryption keys, Octavia for TLS certificates, Magnum for cluster credentials, configured with appropriate backend: simple crypto, PKCS11 HSM, Vault)
- [ ] Is Barbican's secret store backend production-ready? (simple crypto plugin stores keys encrypted by a master key in the DB -- acceptable for dev; PKCS11 with HSM like Thales Luna or Entrust nShield for production; HashiCorp Vault plugin for existing Vault infrastructure)
- [ ] Are TLS certificates configured for all API endpoints? (HAProxy or Apache/nginx termination with valid CA-signed certificates, internal endpoints using internal CA, `[ssl]` settings in service configs, verify `openstack endpoint list` shows https URLs)
- [ ] Is Oslo.policy customized from defaults where needed? (`policy.yaml` overrides for each service, review default `admin_or_owner` rules, consider `project_member` and `project_reader` personas from secure RBAC initiative, test with `oslopolicy-checker`)
- [ ] Are project quotas enforced to prevent resource abuse? (compute: instances, cores, ram; storage: volumes, snapshots, gigabytes; network: floating IPs, routers, networks, security group rules -- review defaults with `openstack quota show`)
- [ ] Is audit logging enabled? (Keystone CADF audit middleware via `[audit]` section, `audit_map_file` for notification-based auditing, Panko for event storage, or direct forwarding to SIEM via oslo.messaging notifications)
- [ ] Are Keystone token settings hardened? (Fernet tokens as default -- rotate keys regularly with `keystone-manage fernet_rotate`, token expiration set appropriately -- default 1 hour, `[token] expiration` in `keystone.conf`)
- [ ] Is the Keystone credential encryption key managed and rotated? (`keystone-manage credential_rotate` and `credential_migrate` for re-encrypting credentials, key stored outside of database)

## Why This Matters

Security in OpenStack is not a single service -- it is a cross-cutting concern that spans identity, network isolation, secret management, encryption, and policy enforcement. Keystone is the trust anchor for the entire platform: a compromised Keystone allows access to all services. Default Oslo.policy rules are often overly permissive (e.g., any authenticated user can list all projects in some configurations). Barbican is required for volume encryption, TLS certificate management in Octavia, and Magnum cluster secrets -- without it, these features either do not work or fall back to insecure local key storage. Security groups are stateful and per-port, which means they consume conntrack resources on hypervisors -- high-connection-rate workloads may need stateless security groups or FWaaS. Fernet token key rotation is critical: if keys are not rotated, a stolen key allows indefinite token forging; if rotated too aggressively, valid tokens are prematurely invalidated.

## Common Decisions (ADR Triggers)

- **Identity backend** -- Keystone SQL (self-contained, simple) vs LDAP (read-only user directory, groups mapped to roles) vs federated SAML/OIDC (SSO, MFA via IdP, no local passwords) -- enterprise integration requirements drive this
- **RBAC model** -- legacy admin/member/reader (coarse) vs secure RBAC with system/domain/project scope (granular, newer releases) vs custom policy overrides (flexible but maintenance burden) -- compliance and delegation needs
- **Secret management** -- Barbican with simple crypto (dev/small) vs Barbican with HSM (compliance-mandated hardware key protection) vs HashiCorp Vault integration (existing Vault infrastructure) -- compliance posture and existing tooling
- **Network security model** -- security groups only (per-port, stateful) vs FWaaS v2 (network-wide, router-level) vs external firewall integration (Palo Alto, Fortinet) -- granularity and compliance requirements
- **TLS strategy** -- public CA for external endpoints + internal CA for inter-service (common) vs public CA everywhere (simpler but more certificates) vs mutual TLS between services (strongest but operationally complex)
- **Token format and lifetime** -- Fernet tokens (default, stateless, requires key sync across Keystone nodes) vs JWS tokens (asymmetric, no key distribution needed) -- operational simplicity vs key management
- **Audit and compliance** -- Keystone CADF notifications to Panko (native) vs forwarding to external SIEM (Splunk, ELK) vs CloudKitty for usage/billing auditing -- depends on compliance framework (SOC2, ISO 27001, FedRAMP)
- **Tenant isolation** -- project-level isolation (standard) vs domain-level isolation with domain admins (delegated management) vs separate OpenStack deployments per customer (strongest isolation, highest cost)
