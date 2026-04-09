# AWS Data Perimeter Pattern

## Scope

The data perimeter pattern is a set of AWS-native controls that prevent compromised workloads in your account from talking to AWS resources outside your organization, and prevent untrusted external principals from talking to your resources. Covers the canonical condition keys (`aws:PrincipalOrgID`, `aws:ResourceOrgID`, `aws:SourceVpc`, `aws:SourceVpce`, `aws:VpcSourceIp`), where to apply them (VPC endpoint policies, S3 bucket policies, KMS key policies, IAM SCPs), the policy templates, the default-state trap (every VPC endpoint gets a do-nothing default policy), and the worked example of hardening a set of default-policy endpoints with one template applied uniformly.

## What problem does it solve

The threat model is "compromised workload with valid IAM credentials reaches an AWS resource outside the organization". The classic version of this is data exfiltration via S3: an attacker with credentials from a compromised EC2 instance copies data from your S3 bucket to an attacker-controlled S3 bucket in a different account. Both calls are valid AWS API calls. Both succeed because the IAM credentials grant `s3:GetObject` and `s3:PutObject` and there is no other layer that knows the destination bucket is "wrong".

The data perimeter pattern adds that other layer. It uses condition keys that AWS ships in every API request (or every resource access) to assert two things:

1. **The principal is in your org.** `aws:PrincipalOrgID` matches your AWS Organizations org ID. This blocks credentials from outside your org from being used against your resources.
2. **The resource is in your org.** `aws:ResourceOrgID` matches your org ID. This blocks principals in your org from being used against resources outside your org. This is the half that catches the exfiltration case.

Optionally, a third assertion narrows the source network:

3. **The traffic came from a known network.** `aws:SourceVpc`, `aws:SourceVpce`, or `aws:VpcSourceIp` constrain to specific VPCs, VPC endpoints, or source IP ranges.

The pattern is enforced at multiple layers — VPC endpoint policies, resource-based policies (S3 bucket policies, KMS key policies, etc.), and SCPs at the org level — so that no single layer is the only thing standing between a compromised workload and exfiltration.

## Where to apply it

The pattern uses the same condition key set in every layer; what changes is which layer is the enforcement point.

- **VPC endpoint policies** — the consumer-side enforcement point. Every interface and gateway endpoint can carry a policy that constrains which principals can use the endpoint and which resources can be accessed through it. This is where the data perimeter has the cleanest blast radius — a workload in a VPC with locked-down endpoints cannot reach out-of-org resources via those endpoints, full stop, regardless of what its IAM credentials say.
- **S3 bucket policies** — the resource-side enforcement point for S3. A bucket policy with a `Deny` for any principal not in the org makes the bucket unreachable from outside the org even if the principal somehow has the right IAM permissions. Applies to every other resource-based policy too: SQS queue policies, SNS topic policies, Secrets Manager resource policies, KMS key policies, etc.
- **KMS key policies** — the resource-side enforcement point for the encryption key, which is often the highest-value secondary control. A bucket can have a permissive policy but if the KMS key it uses denies decryption from outside the org, the data is effectively unreadable from outside the org. KMS key policies are an ideal data perimeter enforcement point because every read from an SSE-KMS-encrypted object goes through `kms:Decrypt`.
- **IAM SCPs (org-level)** — the org-wide enforcement point. An SCP at the root or at an OU can deny any API call where `aws:ResourceOrgID` is not the org's ID, blocking the principal-side half of the pattern across every account in the OU. This is the broadest stroke and the easiest one to deploy uniformly, but it is also the easiest to break — SCPs apply to root account too, so a too-aggressive SCP can lock you out of your own accounts. Test in a non-production OU first.

## Policy templates

### VPC endpoint policy (consumer side)

The starting point for every VPC endpoint that does not need cross-account access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalOrgID": "o-xxxxxxxxxx"
        },
        "StringEqualsIfExists": {
          "aws:ResourceOrgID": "o-xxxxxxxxxx"
        }
      }
    }
  ]
}
```

`StringEqualsIfExists` is used for `aws:ResourceOrgID` because not every action carries a resource org ID — the `IfExists` form makes the condition non-blocking when the key is not present, which is the safe default. Replace `o-xxxxxxxxxx` with your org ID.

### S3 bucket policy (resource side)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyOutsideOrg",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "*",
      "Resource": [
        "arn:aws:s3:::your-bucket",
        "arn:aws:s3:::your-bucket/*"
      ],
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:PrincipalOrgID": "o-xxxxxxxxxx"
        }
      }
    }
  ]
}
```

The `Deny` form is preferred over the `Allow + Condition` form on bucket policies because it composes correctly with other statements — a `Deny` always wins.

### KMS key policy (resource side)

```json
{
  "Sid": "DenyDecryptOutsideOrg",
  "Effect": "Deny",
  "Principal": "*",
  "Action": [
    "kms:Decrypt",
    "kms:GenerateDataKey*",
    "kms:ReEncrypt*"
  ],
  "Resource": "*",
  "Condition": {
    "StringNotEqualsIfExists": {
      "aws:PrincipalOrgID": "o-xxxxxxxxxx"
    }
  }
}
```

This statement is added to the existing key policy, not used as the entire key policy.

### SCP (org-level)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyResourceOutsideOrg",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:ResourceOrgID": "o-xxxxxxxxxx"
        }
      }
    }
  ]
}
```

Apply to a non-production OU first. The SCP affects every principal in the OU, including the root user of every member account, so it must be tested.

## The default-state trap

Every VPC endpoint, when created, gets a default policy that looks like this:

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

This is technically a policy in the API and counts as "having a policy attached". It is not a useful policy. It permits everything to everything. The default-state trap is that an audit that asks "do all your endpoints have policies" will return "yes" for an account where every endpoint has the default — and that account has zero data perimeter enforcement on any of its endpoints.

The audit question is "do all your endpoints have policies that **constrain** something" — and the answer to that is almost always "no" for any account that has not explicitly hardened its endpoint policies.

## Common mistakes

- **Forgetting the `aws:ResourceOrgID` half.** A policy that asserts `aws:PrincipalOrgID` only blocks external principals from using your resources. It does not block your principals from talking to external resources, which is the exfiltration direction. Both halves are required for full coverage.
- **Applying inconsistently across endpoints.** Hardening one S3 endpoint but leaving the other ten endpoints in the same VPC at default policy creates the false impression of coverage. The pattern only works if it is applied uniformly. Inventory all endpoints, not just the ones you remember.
- **Not auditing the existing endpoint policies.** Many accounts have endpoint policies that were customized once for a specific reason (e.g., "allow this specific cross-account access for the migration") and never returned to the standard pattern. The cleanup step is reading every endpoint policy, identifying the ones that diverge from the standard, and either re-justifying or normalizing them.
- **Using `StringNotEquals` instead of `StringNotEqualsIfExists`.** `StringNotEquals` evaluates to `true` when the key is missing, which means the `Deny` triggers for legitimate AWS-internal calls that do not carry the key. `StringNotEqualsIfExists` evaluates to `false` when the key is missing, which is the safe default.
- **Not testing SCP changes.** SCPs apply to every principal in the affected OU, including roles used by AWS services on your behalf. A too-aggressive SCP can break legitimate AWS-internal calls and is hard to debug. Always test in a non-production OU before promoting.
- **Treating the data perimeter as a one-time project.** New endpoints, new buckets, new keys, and new accounts all need to be brought into the pattern. Without enforcement (Config rules, Firewall Manager, an SCP that requires a specific Sid in every endpoint policy), drift is inevitable.

## Worked example: hardening a set of default-policy endpoints

**Starting state.** A network account has 14 VPC endpoints across 3 VPCs. All 14 have the default `Allow * * *` policy. The account is in a 12-account org (`o-abc123def4`).

**Step 1 — inventory.** Run `aws ec2 describe-vpc-endpoints` and capture the policy of each. Confirm that all 14 are at default. Save the originals to a file (in case rollback is needed).

**Step 2 — design the standard.** The org has no cross-account VPC endpoint use cases, so the standard is "principal in org" and "resource in org" with `IfExists`. Build the policy template once.

**Step 3 — apply uniformly.** Loop over all 14 endpoints and apply the same policy. Use `aws ec2 modify-vpc-endpoint --vpc-endpoint-id <id> --policy-document file://standard-policy.json`.

**Step 4 — verify.** For each endpoint, fetch the policy back and confirm it matches the standard. Run a known-good cross-org call (e.g., listing a public S3 bucket from a different org's account) — it should be denied. Run a known-good in-org call — it should succeed.

**Step 5 — codify.** Move the standard policy into the IaC tool that owns the endpoints (Terraform, CloudFormation, CDK). Add a Config rule or a Firewall Manager policy that flags any endpoint with a default policy or a policy that does not match the standard. Document the standard in an ADR.

The whole sequence is a few hours of work and converts an account that had zero endpoint-level data perimeter enforcement into one with uniform coverage. The harder part is sustaining it as new endpoints are added — that is what the Config rule or Firewall Manager policy is for.

---

## Reference Links

- [AWS Data Perimeter Workshop](https://catalog.workshops.aws/data-perimeter/) — AWS-published workshop with complete policy templates and exercises
- [aws:PrincipalOrgID condition key](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-principalorgid)
- [aws:ResourceOrgID condition key](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-resourceorgid)
- [VPC endpoint policies for AWS services](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-access.html)

## See Also

- `providers/aws/networking.md` — VPC endpoint configuration that sits underneath this pattern
- `providers/aws/security-groups.md` — endpoint SG hygiene as a complementary layer
- `providers/aws/kms.md` — KMS key policies as a resource-side enforcement point
- `providers/aws/s3.md` — S3 bucket policies as a resource-side enforcement point
- `providers/aws/multi-account.md` — SCPs as the org-level enforcement point
- `providers/aws/iam.md` — identity-based policies that complement the resource-side controls
