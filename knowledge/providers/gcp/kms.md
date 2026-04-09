# Google Cloud KMS

## Scope

Google Cloud Key Management Service (Cloud KMS) is the centralized cryptographic key management service used by every encryption-at-rest control in GCP. Covers software vs HSM-protected keys, customer-managed encryption keys (CMEK), customer-supplied encryption keys (CSEK), automatic vs manual key rotation, key ring scoping (project-level vs folder vs org), the integration with Cloud Storage / BigQuery / Persistent Disk / Cloud SQL / Secret Manager / Compute Engine / GKE, IAM-driven access control, key destruction with delayed actual deletion, and the audit characteristics of orphaned keys and over-permissive IAM bindings on key rings. Does not cover external key managers (EKM) in detail except where they intersect with the standard Cloud KMS workflow.

## Checklist

- [ ] **[Critical]** **Automatic key rotation** must be enabled on every customer-managed key (CMEK) used for production data. Rotation is **disabled by default** when a key is created via the console or API — this is the same finding pattern as AWS KMS and Azure Key Vault. Enable rotation with `gcloud kms keys update <key> --rotation-period=90d --next-rotation-time=...` (Cloud KMS supports any rotation period from 1 day to several years).
- [ ] **[Critical]** Use **customer-managed encryption keys (CMEK)** rather than the default Google-managed encryption keys (GMEK) for any workload subject to regulatory requirements, customer audit, or any need for demonstrable customer control of the key. GMEK is sufficient for non-regulated workloads only — it provides no audit trail of key operations, no customer control of rotation, and no way to demonstrate "we hold the key" to an auditor.
- [ ] **[Critical]** **HSM-protected keys** (`protectionLevel: HSM`) for any workload requiring FIPS 140-2 Level 3 hardware key custody, regulated workloads, or workloads where the risk model includes a malicious insider at Google. HSM keys are slightly more expensive (~$1/key/month vs $0.06/key/month for software) and have lower throughput, but provide hardware-backed key isolation.
- [ ] **[Critical]** Restrict IAM access to **key rings** at the project or key ring level, not at the individual key level. The standard pattern is `roles/cloudkms.cryptoKeyEncrypterDecrypter` granted to the workload's service account on the key ring; finer-grained per-key bindings are an option but add management complexity.
- [ ] **[Critical]** **Never grant `roles/cloudkms.admin` to workload service accounts.** The admin role can create, update, destroy, and rotate keys — far more than any workload should be able to do. Workloads need only encrypt/decrypt or wrap/unwrap permissions, not admin.
- [ ] **[Critical]** **Audit access to key rings** via Cloud Audit Logs. Cloud KMS automatically generates Admin Activity logs (key creation, deletion, IAM binding changes) — these are always on. **Data Access Audit Logs** (encrypt, decrypt, sign operations) must be **explicitly enabled** in the project's audit configuration; without them, the answer to "who used this key" is "we don't know".
- [ ] **[Critical]** Use **separate key rings per blast radius**, not a single key ring per project. The right granularity is "one key ring protects one set of related resources that should be revocable together". A workload that handles customer PII should have a separate key ring from a workload that handles internal logs.
- [ ] **[Recommended]** For multi-region workloads, use **multi-region keys** (key location like `us`, `eu`, or `global`) rather than single-region keys with manual cross-region copy. Multi-region keys are replicated automatically by Google and survive a single-region outage.
- [ ] **[Recommended]** Tag every key ring and key with labels: `environment`, `owner`, `data-classification`, `purpose`. Labels are how cost attribution works in GCP and how key inventory becomes manageable at scale.
- [ ] **[Recommended]** For workloads that need to revoke access to encrypted data without re-encrypting it, use the **destroy schedule** mechanism: `gcloud kms keys versions destroy` schedules destruction with a configurable delay (default 24 hours, can be set up to 30 days). Within the delay window, the destruction can be undone. After the delay, the key version is permanently destroyed and the data encrypted with it is irrecoverable.
- [ ] **[Recommended]** Use **Cloud KMS with Cloud Storage** for any bucket holding sensitive data — set the bucket's default CMEK key, and every object written to the bucket inherits the encryption. The customer manages the key, Google manages the encryption operation, and the audit trail is in Cloud Audit Logs.
- [ ] **[Recommended]** Use **Cloud KMS with BigQuery** for any dataset holding sensitive data — set the dataset's default CMEK key, and BigQuery uses it for at-rest encryption. Note that BigQuery query processing requires the key to be available; revoking access to the key effectively disables the dataset.
- [ ] **[Optional]** For workloads requiring **customer-supplied encryption keys** (CSEK) — where the customer holds the key material and never gives it to Google — use Cloud Storage CSEK or Compute Engine CSEK. CSEK has significant operational overhead (the customer must provide the key on every read and write) and is appropriate only for the highest-assurance workloads.
- [ ] **[Optional]** For workloads with **external key custody** requirements (the key is held in a customer-controlled HSM or external KMS, not in Google's infrastructure), use **Cloud External Key Manager (EKM)** with a partner like Thales, Fortanix, Equinix, or Futurex. EKM is the strongest assurance level but adds latency to every key operation.

## Why This Matters

Cloud KMS is the foundation for every "is this encrypted at rest" control in GCP. A misconfigured KMS posture undermines every other control that depends on it: Cloud Storage CMEK, BigQuery CMEK, Persistent Disk CMEK, Cloud SQL CMEK, Secret Manager (which uses Cloud KMS internally), Compute Engine CMEK, GKE CMEK, and many more. Three failure modes drive most of the high-value findings:

1. **Rotation disabled on customer-managed keys.** This is the highest-leverage / lowest-effort finding in any GCP security baseline review. Enabling rotation on a single CMEK key is a 60-second action. Finding a production project where most or all of the customer-managed keys have rotation disabled is the same single-data-point pattern as in AWS and Azure. The fix is trivial. The current state is almost always a finding.

2. **Data Access Audit Logs disabled for KMS.** Admin Activity logs are always on, but Data Access logs (the records of who decrypted what) are off by default. Enabling them generates volume and cost — but disabling them eliminates the most important audit signal Cloud KMS produces. The right answer is "enable Data Access logs for KMS in any project that has CMEK keys" and accept the cost.

3. **Over-broad IAM on key rings.** The path of least resistance for granting key access is to bind `roles/cloudkms.admin` (which grants everything) or `roles/owner` at the project level (which inherits to KMS). Either of these gives the workload far more access than it needs. The right pattern is to grant `roles/cloudkms.cryptoKeyEncrypterDecrypter` (or `cryptoKeyDecrypter` if the workload only reads) at the key ring level, scoped to the specific service account.

A secondary failure mode that compounds the first three: the audit signal of a finding is proportional to how plainly the key name describes what it protects, the same as in AWS KMS and Azure Key Vault. Descriptive names land harder when something is wrong.

## Common Decisions (ADR Triggers)

- **CMEK vs GMEK** — CMEK when any of: regulatory requirement, audit requirement to see key operations, controlled rotation cadence, requirement to demonstrably revoke access by destroying the key. GMEK for everything else. The decision is per-data-classification, not per-workload.
- **Software vs HSM key** — HSM for FIPS 140-2 Level 3 requirements, regulated financial / healthcare / defense workloads, or any workload where the threat model includes "Google insider with access to KMS infrastructure". Software for everything else. HSM is moderately more expensive and has lower throughput.
- **Single-region vs multi-region key location** — multi-region (`us`, `eu`) for any workload that has cross-region data access patterns. Single-region for workloads that are genuinely region-pinned for data residency or latency reasons. Pick the location at key creation; it cannot be changed.
- **Key rotation cadence** — 90 days is the right default for most regulated workloads. 365 days is acceptable for non-regulated workloads. Manual rotation is appropriate when the consuming service does not handle key version updates gracefully and requires coordinated rotation.
- **Key ring granularity** — one key ring per blast radius, not one per project. A project that runs three workloads with different data classifications should have three key rings, not one shared one.
- **Customer-supplied (CSEK) vs customer-managed (CMEK) vs Google-managed (GMEK)** — CSEK only for the rare workloads where the customer must provably never give the key to Google (extreme compliance regimes). CMEK for the standard "we control the key in Cloud KMS" pattern. GMEK for non-regulated workloads.

## Reference Architectures

### Production CMEK with rotation and audit

- Cloud KMS key ring `kms-prod-customer-pii` in the workload project, in the appropriate region (or `us`/`eu` for multi-region)
- Customer-managed key `customer-pii-cmek`, software protection level (or HSM if required)
- Automatic rotation every 90 days
- Labels: `environment=prod`, `owner=team-payments`, `data-classification=restricted`, `purpose=customer-pii-encryption`
- IAM bindings:
  - `roles/cloudkms.cryptoKeyEncrypterDecrypter` to the workload service account on the key ring
  - `roles/cloudkms.admin` to a single named admin service account (used by IaC, not by humans)
  - `roles/cloudkms.viewer` to the security team's group for audit
- Data Access Audit Logs enabled in the project audit configuration for Cloud KMS
- Documented in an ADR: what data the key protects, what the blast radius is, who owns rotation, recovery procedure if rotation fails

### Cloud Storage with CMEK

- Cloud Storage bucket configured with `defaultKmsKeyName` pointing to the production CMEK
- Every object written inherits the bucket's default encryption
- The bucket's service account has `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key ring
- Object listing and metadata are not encrypted (only the object contents); plan accordingly for sensitive metadata

### BigQuery with CMEK

- BigQuery dataset configured with `defaultEncryptionConfiguration.kmsKeyName` pointing to the production CMEK
- Every table inherits the dataset default
- The BigQuery service agent in the project has `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key ring (this is granted automatically when the dataset is configured but should be verified)
- Note: revoking the CMEK access disables query operations on the dataset until the access is restored

---

## Reference Links

- [Cloud KMS documentation](https://cloud.google.com/kms/docs)
- [Cloud KMS key rotation](https://cloud.google.com/kms/docs/key-rotation)
- [Cloud KMS HSM-protected keys](https://cloud.google.com/kms/docs/hsm)
- [Cloud KMS audit logging](https://cloud.google.com/kms/docs/audit-logging)
- [Cloud External Key Manager (EKM)](https://cloud.google.com/kms/docs/ekm)

## See Also

- `providers/gcp/security.md` — broader GCP security service set
- `providers/gcp/iam.md` — IAM fundamentals (foundation for KMS access control)
- `providers/gcp/storage.md` — Cloud Storage CMEK integration
- `providers/gcp/data.md` — BigQuery CMEK integration
- `providers/aws/kms.md` — equivalent service in AWS
- `providers/azure/key-vault.md` — equivalent service in Azure
- `compliance/pci-dss.md` — Req 3 (data at rest) and Req 4 (data in transit) cite KMS controls
