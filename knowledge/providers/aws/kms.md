# AWS KMS

## Scope

AWS Key Management Service (KMS) is the centralized cryptographic key management service used by every encryption-at-rest control in AWS. Covers customer-managed CMKs vs AWS-managed CMKs vs AWS-owned keys, automatic key rotation semantics, key policies vs IAM policies, grants, multi-region keys, key naming as audit signal, the rotation-disabled finding pattern, key alias hygiene, and integration with KMS-encrypted services (S3, EBS, RDS, Secrets Manager, CloudWatch Logs, SNS, SQS, EFS, FSx, DynamoDB). Does not cover CloudHSM (separate service for FIPS 140-2 Level 3 hardware key custody).

## Checklist

- [ ] **[Critical]** Automatic key rotation must be enabled on every customer-managed CMK that protects production data. Rotation is **disabled by default** when a customer-managed CMK is created — this is the most common KMS finding in any audit. Enabling rotation is a one-call fix (`aws kms enable-key-rotation --key-id <id>`) and should be the first thing done after creating any customer-managed CMK that is not throwaway.
- [ ] **[Critical]** Every customer-managed CMK must have a meaningful alias and a meaningful key policy `Description`. Plain-language names that describe what the key protects (e.g., `alias/prod-customer-pii`, `alias/staging-rds-postgres`) are how rotation findings become quotable: "rotation is disabled on the CMK named `prod-customer-pii`" lands very differently than "rotation is disabled on `key-id 1234abcd...`". The audit finding intensity is a function of the name.
- [ ] **[Critical]** Key policies must follow least privilege. The default key policy AWS creates with the console wizard grants the entire account broad access via `"Principal": {"AWS": "arn:aws:iam::<account>:root"}, "Action": "kms:*"`. This is the AWS-recommended default for break-glass purposes but should be tightened on any production CMK so that only the specific principals that need to use the key can use it.
- [ ] **[Critical]** Confirm which AWS-managed services are using each CMK and document it. KMS usage is invisible to the key owner unless explicitly monitored — CloudTrail data events (`kms:Decrypt`, `kms:GenerateDataKey`, `kms:Encrypt`) are the only way to see who is actually using a CMK in production. A CMK that nobody can explain the use of is either dead weight or a hidden dependency; both are findings.
- [ ] **[Critical]** Read-access to `kms:GetKeyRotationStatus` must be granted to the security or audit role. Without this permission, an external reviewer cannot verify that rotation is enabled — the answer to "is rotation on" requires the API call, not just the key policy. Audit roles should have `kms:Describe*`, `kms:Get*`, `kms:List*` at minimum on all CMKs in scope.
- [ ] **[Recommended]** Use customer-managed CMKs (not AWS-managed CMKs) when any of the following applies: cross-account access is required, the key policy needs to be customized, key usage needs to appear in CloudTrail, key rotation cadence needs to be controlled, the workload is subject to regulations that require demonstrable customer control of the key. AWS-managed CMKs (the `aws/<service>` keys) are sufficient for non-regulated, single-account workloads only.
- [ ] **[Recommended]** Tag every customer-managed CMK with `Owner`, `Environment`, `Purpose`, and `DataClassification`. Tag-based access control via `aws:ResourceTag` is the simplest way to scale key access policies across many CMKs without writing per-key policies.
- [ ] **[Recommended]** For workloads that span regions, evaluate multi-region keys (MRKs). MRKs share the same key ID across regions and let an encrypted blob created in region A be decrypted in region B without re-encrypting. Use them for cross-region replication, multi-region failover, and disaster recovery patterns. Do NOT use them when the workload is genuinely region-isolated — single-region keys are simpler and have a smaller blast radius.
- [ ] **[Recommended]** For workloads that need attestation of who decrypted what and when, enable CloudTrail data events for KMS at the key level (`Read` and `Write` events). Default CloudTrail captures management events only — `Decrypt` and `GenerateDataKey` are data events and are off by default. Without them, KMS usage is invisible.
- [ ] **[Recommended]** Use `kms:ViaService` condition keys in key policies to restrict which AWS services can use a CMK on the principal's behalf. A CMK intended only for S3 should have `"Condition": {"StringEquals": {"kms:ViaService": "s3.<region>.amazonaws.com"}}` so that a compromised principal cannot abuse the same key against EBS or DynamoDB.
- [ ] **[Optional]** Disable (do not delete) CMKs that are no longer in use. KMS key deletion has a mandatory 7–30 day waiting period and is irreversible — if anything still references the key, decryption fails. The safe pattern is: disable, monitor for `KMSDisabledException` errors for at least one full business cycle (typically 30 days), then schedule deletion.
- [ ] **[Optional]** For workloads requiring imported key material (BYOK), document the import process, expiration, and reimport schedule. Imported key material can have an explicit expiration; rotation is manual and requires reimporting. This is the right answer for some compliance regimes and the wrong answer for most.

## Why This Matters

KMS is the foundation for every "is this encrypted at rest" control in AWS. A misconfigured KMS posture undermines every other control that depends on it: S3 SSE-KMS, EBS encryption, RDS encryption, Secrets Manager, CloudWatch Logs encryption, SNS/SQS encryption, and so on. Three failure modes drive most of the high-value findings:

1. **Rotation disabled on customer-managed CMKs.** This is the highest-leverage / lowest-effort finding in any AWS security baseline review. Enabling rotation on a single customer-managed CMK is a 60-second action. Finding a production account where most or all of the customer-managed CMKs have rotation disabled is the kind of single-data-point pattern that gets executive attention, especially when the key names hint at what they protect. The fix is trivial. The current state is almost always a finding.
2. **Default key policies that grant the whole account.** The console wizard creates CMKs with key policies that effectively delegate permission management to IAM. This is correct as a break-glass mechanism but is too broad as a steady state. Tightening the key policy to enumerate the specific principals (or a small set of roles) that can use the key is the difference between "encrypted with KMS" and "encrypted with KMS, controlled by KMS".
3. **CMKs nobody can explain.** A CMK that exists in the account but has no documented owner, no tag, no alias, and no traffic in CloudTrail is either dead weight (delete) or a hidden dependency (find before deleting). Both are findings. The fact that you cannot tell which is the problem.

A secondary failure mode that compounds the first three: the audit signal of a finding is proportional to how plainly the key name describes what the key protects. "Rotation is disabled on `prod-customer-pii`" is a higher-intensity finding than "rotation is disabled on a key with no alias". This is not a defect of the audit — it is the same fact, surfaced two different ways. The lesson is to **name keys descriptively from day one**, both because it helps everyone find them and because it makes any future finding land harder when something is wrong.

## Common Decisions (ADR Triggers)

- **Customer-managed CMK vs AWS-managed CMK** — customer-managed when any of: cross-account access, custom key policy, CloudTrail visibility, controlled rotation cadence, regulatory requirement for customer control. AWS-managed (the `aws/<service>` keys) for everything else. The trade-off is operational overhead — customer-managed CMKs cost $1/month per key, plus per-API charges, and require explicit lifecycle management.
- **Single-region key vs multi-region key (MRK)** — MRK only when there is a real cross-region dependency (replicated data, multi-region failover). Single-region keys for everything else. MRKs increase blast radius and are harder to revoke.
- **Key per workload vs key per data classification vs key per service** — most environments default to "key per service per environment" (e.g., one CMK for S3 in prod, one for EBS in prod), which is too coarse for many regulated workloads. Higher-sensitivity workloads should get their own CMK so that revocation can be surgical. The rule of thumb: one CMK protects one blast radius; if you cannot describe the blast radius in one sentence, the granularity is wrong.
- **Rotation cadence** — automatic (annual, AWS-managed) is the right default. Manual rotation (creating a new CMK and re-encrypting) is appropriate when a regulatory regime requires a specific cadence shorter than annual, or when a key has been potentially exposed and needs immediate retirement. Manual rotation requires re-encryption of all data protected by the old key — plan for it.
- **CloudTrail data events for KMS** — enable on every customer-managed CMK that protects regulated or business-critical data. Cost is real (data events are charged per event) but the visibility is the only way to answer "who used this key" after the fact. For lower-sensitivity workloads, leave data events off and accept the visibility gap.

## Reference Architectures

### Production data CMK (the right shape)

- Customer-managed CMK with descriptive alias (`alias/prod-app-customer-pii`)
- Tags: `Owner=team-payments`, `Environment=prod`, `Purpose=customer-pii-encryption`, `DataClassification=restricted`
- Key policy that names specific roles (the application role, the backup role, the audit role) with specific actions, plus a separate statement allowing the security team's IAM role full administration
- Automatic rotation enabled
- CloudTrail data events enabled at the key level
- `kms:ViaService` condition restricting use to the specific AWS services that legitimately consume the key
- Documented in an ADR: what data it protects, what the blast radius is, who owns the rotation runbook, what the manual rotation procedure is if needed

### Cross-region replicated CMK (multi-region key)

- Multi-region primary in us-east-1, replica in us-west-2
- Same alias in both regions for application portability
- Automatic rotation enabled (rotation propagates from primary to replicas)
- Replica is read-only — administrative operations happen on the primary
- Used for S3 cross-region replication, RDS Aurora global database, DynamoDB global tables

### "Encrypted with KMS, but..." anti-pattern

- AWS-managed CMK (`aws/s3`) used for sensitive data because the bucket was created via console wizard
- No key policy customization possible
- No CloudTrail visibility into key usage
- No way to demonstrate customer control to an auditor
- **Fix:** create a customer-managed CMK with the right alias, re-encrypt the data via S3 batch operations or lifecycle, update bucket default encryption to the new CMK, document in an ADR

---

## Reference Links

- [AWS KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/) — service overview, key policies, rotation, multi-region keys
- [Rotating AWS KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html) — automatic rotation semantics and how to enable it
- [Key policies in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html) — key policies vs IAM policies, default key policy, condition keys
- [Multi-Region keys in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html) — when to use, replication semantics, limitations
- [Logging AWS KMS API calls with AWS CloudTrail](https://docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html) — management events vs data events for KMS

## See Also

- `providers/aws/security.md` — broader AWS security service set (GuardDuty, Security Hub, Config, Firewall Manager)
- `providers/aws/iam.md` — IAM policies that interact with KMS key policies
- `providers/aws/secrets-manager.md` — Secrets Manager uses KMS for envelope encryption
- `providers/aws/s3.md` — SSE-KMS configuration for S3 buckets
- `providers/aws/rds-aurora.md` — RDS encryption-at-rest using KMS
- `patterns/aws-data-perimeter.md` — KMS key policies as one of the resource-side enforcement points for data perimeter
- `compliance/pci-dss.md` — Req 3 (data at rest) and Req 4 (data in transit) cite KMS controls
