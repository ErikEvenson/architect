# Azure Key Vault

## Scope

Azure Key Vault is the centralized secret, key, and certificate management service used by every encryption-at-rest control in Azure. Covers vaults vs Managed HSM pools, the access policy vs Azure RBAC permission models (and the migration between them), soft-delete and purge protection, key rotation (auto and manual), key types (RSA / EC / symmetric / managed HSM keys), the integration with Storage SSE / SQL TDE / Disk Encryption Sets / Service Bus / App Service / AKS, certificate lifecycle management, and the audit characteristics of orphaned vaults and over-permissive access policies. Does not cover Azure Information Protection (separate service for document classification).

## Checklist

- [ ] **[Critical]** Soft-delete must be enabled on every Key Vault. Soft-delete is enabled by default for vaults created after February 2025 and cannot be disabled, but vaults created earlier may still have it off — check explicitly. Without soft-delete, an accidental or malicious vault deletion is unrecoverable, taking every key, secret, and certificate stored there with it.
- [ ] **[Critical]** Purge protection must be enabled on any Key Vault that protects production data. Purge protection prevents the soft-delete grace period from being bypassed even by an account owner — once enabled it cannot be disabled until the retention period elapses. Without it, an attacker who compromises a privileged account can force-delete the vault before recovery is possible.
- [ ] **[Critical]** Use **Azure RBAC** as the permission model, not the legacy access policy model. Access policies are flat per-vault grants with no inheritance and no fine-grained scope; RBAC integrates with the broader Azure permission model, supports management group / subscription / resource group inheritance, and is auditable through Azure Activity Log + Monitor in the same way as every other Azure resource. Migrating an existing vault from access policies to RBAC requires explicit role assignment for every principal that previously had access — plan the migration deliberately.
- [ ] **[Critical]** Automatic key rotation must be enabled on every customer-managed key (CMK) used for production data. Rotation is **disabled by default** when a key is created via the portal — this is the same finding pattern as AWS KMS (see `providers/aws/kms.md`). Enable rotation policies via `az keyvault key rotation-policy update` or via Bicep/ARM at provisioning time.
- [ ] **[Critical]** Restrict network access to the vault. By default a vault accepts traffic from any public IP. Lock it down with private endpoints (preferred), service endpoints, or firewall rules that limit to specific source IPs / virtual networks. The "public access enabled" finding is one of the most common in any Azure baseline review.
- [ ] **[Critical]** For the Storage / SQL / Disk Encryption use case, use a customer-managed key (CMK) stored in Key Vault rather than the default Microsoft-managed key. Microsoft-managed keys are sufficient for non-regulated workloads only — they provide no audit trail, no key policy customization, and no demonstrable customer control of the key.
- [ ] **[Recommended]** Tag every vault with `Environment`, `Owner`, `DataClassification`, and `Purpose`. Tag-based access control via ABAC (preview) or via group-based RBAC policies is the simplest way to scale access management across many vaults.
- [ ] **[Recommended]** For workloads that require attestation of who decrypted what and when, enable **diagnostic settings** on the vault and forward to Log Analytics or a SIEM. Default Azure Monitor captures management plane operations (creates, updates, deletes); the data plane events (`KeyGet`, `Decrypt`, `Sign`) require explicit diagnostic settings. Without them, key usage is invisible.
- [ ] **[Recommended]** For workloads that need cross-region availability of the same key material, evaluate Managed HSM (which supports multi-region replication) or design the application to handle multi-vault key references with the same key material imported into vaults in each region. Standard Key Vault is regional and a region outage takes the keys with it.
- [ ] **[Recommended]** For high-assurance workloads (FIPS 140-2 Level 3 hardware key custody, BYOK with HSM-protected key material, single-tenant HSM pools), use **Managed HSM** instead of standard Key Vault. Managed HSM is more expensive (~$3/hour vs ~$0.03/10k operations for standard Key Vault) but provides the higher assurance level required by some regulated regimes.
- [ ] **[Recommended]** Use **Key Vault references** in App Service, Functions, AKS (via the Secrets Store CSI driver), and Container Apps so that secrets never appear as environment variables in the deployment manifest. The reference is resolved at runtime by the platform's managed identity, leaving the secret in Key Vault as the system of record.
- [ ] **[Optional]** For workloads that need to import third-party CA certificates with automatic renewal (DigiCert, GlobalSign, Sectigo), use the **certificate lifecycle integration** rather than manually rotating certificates. Key Vault can request and renew certificates from supported providers automatically.
- [ ] **[Optional]** Vaults that have not been accessed in the last 90 days are candidates for review and potential decommissioning — they are either unused (delete after the 30-day audit window) or are protecting data that is itself unused.

## Why This Matters

Key Vault is the foundation for every "is this encrypted at rest" control in Azure. A misconfigured Key Vault posture undermines every other control that depends on it: Storage SSE with CMK, SQL TDE, Disk Encryption Sets, Service Bus / Event Hubs / Cosmos DB encryption, Application Gateway TLS termination, Front Door certificates, AKS secret references, and so on. Three failure modes drive most of the high-value findings:

1. **Soft-delete or purge protection disabled.** A vault that can be permanently destroyed in a single API call is a single-call data-loss risk. Both controls are reversible (can be enabled at any time on existing vaults), and both should be enabled by default on every production vault. Vaults created before the soft-delete-by-default change need to be checked individually.
2. **Access policies still in use.** The legacy access policy model has no inheritance, no role-based abstraction, and no native integration with PIM (Privileged Identity Management). Vaults that are still on access policies are harder to audit, harder to reason about for least-privilege, and inconsistent with the rest of the Azure permission model. Migrating to RBAC is one-time work and pays back every time the vault permissions need to change.
3. **Public network access.** A vault that is reachable from the public internet is a credential exfiltration target. The fix is private endpoints or firewall rules — both are well-supported and have minimal operational overhead. Yet the default state is "open" and a substantial fraction of vaults in any unaudited Azure account are still reachable from arbitrary internet IPs.

A secondary failure mode that compounds the first three: the audit signal of a finding is proportional to how plainly the vault and key names describe what they protect. "Rotation is disabled on the key `prod-customer-pii-cmk`" lands very differently than "rotation is disabled on a key with no documented purpose". As with AWS KMS, descriptive naming makes future findings land harder when something is wrong, both because it helps everyone find them and because it makes the consequence of the misconfiguration concrete.

## Common Decisions (ADR Triggers)

- **Standard Key Vault vs Managed HSM** — standard Key Vault for the vast majority of workloads (multi-tenant pool, FIPS 140-2 Level 2 by default, optional Premium tier for FIPS 140-2 Level 3 software-protected keys). Managed HSM only when the workload requires single-tenant HSM custody, FIPS 140-2 Level 3 hardware-protected keys, or specific regulatory requirements (often GovRAMP / DOD / banking). Managed HSM costs ~$3/hour and is overkill for most workloads.
- **Access policies vs Azure RBAC** — Azure RBAC is the right answer for any new vault and for any vault that can be migrated. Access policies are appropriate only for legacy vaults where the migration cost is not yet justified, or where a tool or platform specifically requires the access policy model and has not yet been updated.
- **Customer-managed key (CMK) vs Microsoft-managed key (MMK)** — CMK when any of: regulatory requirement for customer control, audit requirement to see key operations, requirement to control rotation cadence, requirement to revoke access by deleting the key. MMK is acceptable for non-regulated workloads where the operational simplicity of "Microsoft handles it" is the right trade-off. The decision should be made per data classification, not per workload.
- **Vault per workload vs vault per environment vs vault per data classification** — most environments default to "vault per environment" (one vault for prod, one for dev), which is too coarse for many regulated workloads. Higher-sensitivity workloads should get their own vault so that revocation can be surgical and so that the access scope is narrow. Rule of thumb: one vault protects one blast radius.
- **Public access vs private endpoint vs service endpoint** — private endpoint is the right default. Service endpoint is acceptable for vaults accessed only from within a single VNet. Public access with firewall rules is acceptable as a temporary state during migration but should never be the steady state for a production vault.
- **Key rotation cadence** — automatic (annual default, configurable down to ~28 days minimum) is the right default. Manual rotation is appropriate when a regulatory regime mandates a specific cadence, when a key has been potentially exposed and needs immediate retirement, or when the consuming service does not handle key version updates gracefully and requires coordination.

## Reference Architectures

### Production data CMK (the right shape)

- Standard Key Vault, RBAC permission model, soft-delete + purge protection enabled
- Private endpoint in the workload VNet; public access disabled
- Customer-managed key with descriptive name (`kv-prod-app-customer-pii-cmk`)
- Tags: `Environment=prod`, `Owner=team-payments`, `DataClassification=restricted`, `Purpose=customer-pii-encryption`
- Automatic rotation policy (annual)
- Diagnostic settings forwarding data plane operations to a Log Analytics workspace in the security tooling subscription
- RBAC role assignments scoped to specific user-assigned managed identities (no broad grants); reviewed quarterly
- Documented in an ADR: what data it protects, what the blast radius is, who owns the rotation runbook, what the recovery procedure is

### App Service / Functions secret reference pattern

- App Service uses a system-assigned or user-assigned managed identity
- Application settings reference secrets via `@Microsoft.KeyVault(SecretUri=https://kv-prod.vault.azure.net/secrets/db-connection)`
- Key Vault RBAC grants the managed identity `Key Vault Secrets User` role on the specific secret (or on the vault if the vault is single-purpose)
- App Service caches the resolved value with periodic refresh; rotation in Key Vault propagates within ~24 hours by default
- No secret material in the deployment manifest, in source control, or in the App Service configuration directly

### AKS Secrets Store CSI driver

- AKS cluster has the Secrets Store CSI driver and Azure Key Vault provider installed
- Workloads use a `SecretProviderClass` that references the vault and the secrets to project
- Pod uses workload identity (federated credential) to authenticate to Key Vault
- Secrets are mounted as files in the pod, never injected as environment variables
- Rotation is handled by the CSI driver's auto-rotation feature with a configurable poll interval

---

## Reference Links

- [Azure Key Vault documentation](https://learn.microsoft.com/azure/key-vault/) — overview, vaults, Managed HSM, security
- [Azure Key Vault soft-delete and purge protection](https://learn.microsoft.com/azure/key-vault/general/soft-delete-overview) — semantics and recovery
- [Azure RBAC for Key Vault](https://learn.microsoft.com/azure/key-vault/general/rbac-guide) — RBAC vs access policy migration guide
- [Configure key auto-rotation](https://learn.microsoft.com/azure/key-vault/keys/how-to-configure-key-rotation)
- [Azure Key Vault private endpoints](https://learn.microsoft.com/azure/key-vault/general/private-link-service)
- [Azure Managed HSM overview](https://learn.microsoft.com/azure/key-vault/managed-hsm/overview)

## See Also

- `providers/azure/identity.md` — Entra ID, managed identities, the principals that need RBAC role assignments on Key Vault
- `providers/azure/security.md` — broader Azure security service set
- `providers/azure/storage.md` — Storage SSE with CMK references Key Vault
- `providers/azure/database.md` — SQL TDE with CMK references Key Vault
- `providers/aws/kms.md` — equivalent service in AWS, similar findings patterns
- `compliance/pci-dss.md` — Req 3 (data at rest) and Req 4 (data in transit) cite key management controls
