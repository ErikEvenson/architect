# OpenStack Security (Keystone, Barbican, RBAC, Compliance)

## Scope

Covers OpenStack security services and practices: Keystone identity management (authentication, federation, MFA, application credentials, domains), Barbican secret management (HSM, Vault integration), RBAC and oslo.policy, security groups, TLS configuration, token management, audit logging, and compliance considerations.

## Checklist

- [ ] **[Critical]** Is Keystone configured with an appropriate identity backend? (SQL for small/dev, LDAP for enterprise directory integration with `[ldap]` section in `keystone.conf`, federated SAML2/OIDC via `[federation]` for SSO with corporate IdP like Okta, Microsoft Entra ID, Keycloak)
- [ ] **[Critical]** Are TLS certificates configured for all API endpoints? (HAProxy or Apache/nginx termination with valid CA-signed certificates, internal endpoints using internal CA, `[ssl]` settings in service configs, verify `openstack endpoint list` shows https URLs)
- [ ] **[Critical]** Is service-to-service authentication configured securely? (each OpenStack service has a dedicated service user in Keystone, credentials in service config files with restricted file permissions `0640`, consider `[keystone_authtoken]` `service_token_roles_check = True`)
- [ ] **[Critical]** Are Keystone token settings hardened? (Fernet tokens as default -- rotate keys regularly with `keystone-manage fernet_rotate`, token expiration set appropriately -- default 1 hour, `[token] expiration` in `keystone.conf`)
- [ ] **[Recommended]** Are Keystone domains used to isolate organizational units? (default domain for service accounts, separate domains per business unit or customer, domain-scoped admin roles for delegated administration)
- [ ] **[Recommended]** Is multi-factor authentication enabled for privileged users? (Keystone MFA rules via `[auth] methods = password,totp`, TOTP credentials per user, or enforced through federated IdP MFA policies)
- [ ] **[Recommended]** Are application credentials used instead of user passwords for automation? (`openstack application credential create` with restricted roles and expiration, secret stored in vault, not embedded in scripts or CI/CD pipelines)
- [ ] **[Recommended]** Are security groups configured as default-deny ingress with explicit allow rules, and is the difference from Firewall-as-a-Service (FWaaS v2) understood? (security groups are per-port/instance, FWaaS applies to router interfaces for network-wide policy)
- [ ] **[Recommended]** Is Barbican deployed for secret management? (symmetric keys, certificates, private keys, passphrases -- used by Cinder for volume encryption keys, Octavia for TLS certificates, Magnum for cluster credentials, configured with appropriate backend: simple crypto, PKCS11 HSM, Vault)
- [ ] **[Recommended]** Is Barbican's secret store backend production-ready? (simple crypto plugin stores keys encrypted by a master key in the DB -- acceptable for dev; PKCS11 with HSM like Thales Luna or Entrust nShield for production; HashiCorp Vault plugin for existing Vault infrastructure)
- [ ] **[Recommended]** Is Oslo.policy customized from defaults where needed? (`policy.yaml` overrides for each service, review default `admin_or_owner` rules, consider `project_member` and `project_reader` personas from secure RBAC initiative, test with `oslopolicy-checker`)
- [ ] **[Recommended]** Are project quotas enforced to prevent resource abuse? (compute: instances, cores, ram; storage: volumes, snapshots, gigabytes; network: floating IPs, routers, networks, security group rules -- review defaults with `openstack quota show`)
- [ ] **[Recommended]** Is the Keystone credential encryption key managed and rotated? (`keystone-manage credential_rotate` and `credential_migrate` for re-encrypting credentials, key stored outside of database)
- [ ] **[Optional]** Is audit logging enabled? (Keystone CADF audit middleware via `[audit]` section, `audit_map_file` for notification-based auditing, Panko for event storage, or direct forwarding to SIEM via oslo.messaging notifications)

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

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) | 2025.1 Epoxy (31) | 2025.2 Flamingo (32) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fernet tokens | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default | Default |
| JWS tokens | Not available | Not available | Not available | Not available | Tech Preview | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Application credentials | Not available | Not available | Introduced | GA | GA | GA (access rules) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Federated identity (SAML2/OIDC) | GA (improved) | GA | GA | GA (K2K improvements) | GA | GA | GA | GA | GA (improved mapping) | GA | GA | GA | GA | GA | GA | GA | GA |
| MFA (multi-factor auth) | Not available | Not available | Not available | Introduced (TOTP) | GA (MFA rules) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| OAuth 1.0a | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| OAuth 2.0 | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA (device authorization grant) | GA |
| Secure RBAC (system/domain/project scope) | Not available | Not available | Not available | Not available | Introduced (spec) | Tech Preview (Keystone) | Tech Preview (expanding) | Tech Preview (more services) | GA (Keystone, Nova) | GA (expanding) | GA (most services) | GA (default in some) | GA | GA (default) | GA (default) | GA (default) | GA (default) |
| oslo.policy JSON format | Default | Default | Deprecated notice | Deprecated | Deprecated | Deprecated (YAML recommended) | Deprecated | Deprecated | Deprecated (removal warnings) | YAML default | YAML default | YAML enforced (JSON removed) | YAML only | YAML only | YAML only | YAML only | YAML only |
| Keystone domains | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Keystone trust delegation | GA | GA | GA | GA | GA (improved expiry) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Barbican secret store | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Barbican PKCS11 (HSM) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Barbican Vault plugin | Not available | Not available | Tech Preview | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Service token (send_service_token) | Not available | Not available | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA (enforced in some services) | GA | GA | GA | GA | GA |
| Credential encryption rotation | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |

**Key changes across releases:**
- **Application credentials (Rocky+):** Introduced in Rocky and GA in Stein, application credentials allow automation to authenticate without exposing user passwords. Access rules (Ussuri+) further restrict application credentials to specific API endpoints and methods, following least-privilege principles.
- **Federated identity improvements:** Federation via SAML2 and OIDC has been GA since before Pike with continuous improvements. Keystone-to-Keystone (K2K) federation improved in Stein. Mapping rules became more flexible across releases, supporting complex group-to-role mappings from enterprise IdPs like Microsoft Entra ID (formerly Azure AD), Okta, and Keycloak.
- **MFA support (Stein+):** Multi-factor authentication was introduced in Stein with TOTP support. MFA rules (Train+) allow per-user MFA enforcement. For stronger MFA, federated identity with MFA enforced at the IdP level is recommended.
- **OAuth 2.0 (Xena+):** OAuth 2.0 client credentials grant was introduced in Xena, providing a modern authentication mechanism for service-to-service communication and external application integration. Device authorization grant was added in Epoxy (2025.1). This complements the older OAuth 1.0a support.
- **Secure RBAC:** The secure RBAC initiative introduced system-scope, domain-scope, and project-scope personas (admin, member, reader) starting in Ussuri as a tech preview. This graduated to GA across services through Xena-Yoga and became the default in 2024.1. It replaces the legacy coarse-grained admin-or-owner policy model.
- **oslo.policy JSON deprecation:** The legacy JSON policy file format was deprecated starting in Stein, with YAML becoming the recommended format. JSON support was fully removed in 2023.1 (Antelope). All custom policy overrides must use `policy.yaml` format.
- **Barbican evolution:** Barbican has been stable across all releases. The HashiCorp Vault plugin (GA in Stein) enables organizations with existing Vault infrastructure to use it as the secret backend. Barbican remains required for Cinder volume encryption, Octavia TLS certificates, and Magnum cluster secrets. KMIP backend improvements in Flamingo (2025.2).
- **Service tokens (Stein+):** Service token sending was introduced in Stein to prevent token expiration issues during long-running operations. Services send both the user token and a service token, ensuring operations complete even if the user token expires mid-request. This became enforced in some services starting in 2023.1.
- **Epoxy (2025.1) security changes:** OAuth 2.0 device authorization grant for CLI and headless authentication flows. Continued secure RBAC improvements across all services.
- **Flamingo (2025.2) security changes:** Barbican KMIP backend improvements for interoperability with enterprise key management systems. Continued hardening of default security policies.

## See Also

- `general/security.md` -- general security architecture patterns
- `general/identity.md` -- identity and access management patterns
- `providers/openstack/networking.md` -- security groups and network controls
- `providers/hashicorp/vault.md` -- Vault as Barbican backend alternative
