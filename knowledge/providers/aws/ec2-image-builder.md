# AWS EC2 Image Builder

## Scope

AWS-native golden image pipeline service for building, testing, and distributing AMIs and container images. Covers image and container recipes, components (AWSTOE), infrastructure and distribution configurations, image pipelines, lifecycle policies, cross-account/cross-region distribution, scheduling and parent-image-change triggers, Inspector integration, and IAM/network design for build instances. The cloud-agnostic alternative is `providers/hashicorp/packer.md`.

## Checklist

- [ ] **[Critical]** Is an Image Builder pipeline (or equivalent) producing the AMIs/container images used by EC2, ASG, ECS, and EKS, rather than instances launched from unmanaged base AMIs? (closes the **[Critical]** golden-image-pipeline gap from `general/cloud-workload-hardening.md`)
- [ ] **[Critical]** Is the build cadence at least monthly, with an additional trigger on parent image change (`pipelineExecutionStartCondition: EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE`) so OS patches and parent-image CVEs roll forward without manual intervention?
- [ ] **[Critical]** Does the recipe layer correctly: AWS-managed base AMI (or marketplace hardened image) → hardening components (CIS/STIG via AWS-managed or custom) → patching component (`update-linux` / `update-windows`) → agents (SSM, CloudWatch, Inspector, EDR) → application layer? Application images should reference an upstream hardened image rather than re-baking hardening every build.
- [ ] **[Critical]** Are test components run after image build (Inspector vulnerability scan, custom InSpec/Goss tests, smoke tests) with the pipeline configured to fail on critical findings, so a broken image never reaches distribution?
- [ ] **[Critical]** Is the build subnet private, with outbound via NAT or VPC endpoints (S3, SSM, SSM Messages, EC2 Messages, KMS, ImageBuilder, ECR, CloudWatch Logs)? Build instances need outbound for package repos and AWSTOE; they should never accept inbound traffic and should use SSM Session Manager (not SSH) if console access is needed for troubleshooting.
- [ ] **[Critical]** Is the Image Builder service-linked role (`AWSServiceRoleForImageBuilder`) created, and does the build instance profile have only the minimum policies (`EC2InstanceProfileForImageBuilder`, `EC2InstanceProfileForImageBuilderECRContainerBuilds` for container builds, `AmazonSSMManagedInstanceCore`)? Avoid attaching production application roles to build instances.
- [ ] **[Recommended]** Is distribution configured for cross-region copy to all regions where the image is consumed, with per-region KMS CMKs (Image Builder re-encrypts EBS snapshots with the destination-region key) and KMS grants to consumer accounts for the destination keys?
- [ ] **[Recommended]** For multi-account organizations, is cross-account AMI sharing handled via `launchPermissions` (account IDs, OUs, or `all` for public — never `all`) and `targetAccountIds` for full AMI copies into spoke accounts that need to deregister or modify the image?
- [ ] **[Recommended]** Is an image lifecycle policy attached (account/region or per-recipe scope) to deprecate images older than N months and delete images older than N+M months, with associated EBS snapshots cleaned up? Without lifecycle policy, snapshot storage cost grows linearly with build count.
- [ ] **[Recommended]** Is each AMI tagged with build metadata (recipe name, recipe version, parent image ID, build date, git SHA of custom components, CIS/STIG profile applied, Inspector scan ID) so consumers can filter and so deprecated AMIs can be located via tag-based queries?
- [ ] **[Recommended]** Are custom components versioned with semantic versioning (`1.2.3`) and stored in a git-tracked source-of-truth, with CI publishing new component versions before pipeline runs? Recipes pin component versions to avoid silent behavior change.
- [ ] **[Recommended]** Is Amazon Inspector enabled for Image Builder findings (vulnerability scan as part of the test stage), with results published to Security Hub and a build-stage gate that fails on critical CVEs?
- [ ] **[Recommended]** For container images, is the distribution configuration writing to ECR with image tag immutability enabled, scan-on-push enabled, and a lifecycle policy on the ECR repo to expire untagged images?
- [ ] **[Recommended]** Are pipeline executions, AWSTOE logs, and component output written to a dedicated S3 bucket (with object lock or lifecycle policy) for audit, debugging, and compliance evidence?
- [ ] **[Recommended]** Is a single central pipeline account used for builds with cross-account distribution to spoke accounts (preferred), rather than per-account pipelines that duplicate cost, drift independently, and complicate compliance reporting?
- [ ] **[Optional]** For workloads with strict latency or build-time SLAs, evaluate larger build instance types (`c5.4xlarge` and up) and instance store-backed builders to reduce build duration; default `t3.medium` builds can take 30+ minutes for hardened Windows images.
- [ ] **[Optional]** Where the same workload is delivered as both an AMI (for ASG) and a container image (for ECS/EKS), maintain parallel image and container recipes that share the same custom components so hardening logic does not diverge.
- [ ] **[Optional]** Evaluate AWS Marketplace hardened base images (CIS Hardened Images, STIG-hardened AMIs from Nemu/AWS) as the parent for the recipe rather than building hardening from scratch — faster to compliance, monthly vendor patching, but per-hour marketplace cost and limited customization.

## Why This Matters

Image Builder is the AWS-native execution of the **[Critical]** golden-image-pipeline checklist item that appears in `general/cloud-workload-hardening.md` and `providers/aws/ec2-asg.md`. Without it (or an equivalent like Packer), AMIs are either built by hand, copied from old snapshots, or pulled fresh from public AMIs at launch — all of which produce drift, miss patches, lack hardening, and leave no audit trail of what is in production.

Image Builder's specific value over alternatives is integration: the build instance can use SSM Session Manager and IAM instance profiles instead of SSH keys; Inspector findings flow directly into the pipeline as a gate; cross-region distribution re-encrypts with per-region KMS keys without separate Lambda glue; lifecycle policies remove snapshots automatically (a cost trap that catches teams running Packer without a separate cleanup job); and AWS-managed components for common hardening (`amazon-cloudwatch-agent-linux`, `update-linux`, `stig-build-linux-high`) eliminate boilerplate that every Packer shop ends up writing.

The most common failure modes:

1. **Re-baking hardening in every application image.** Recipes that combine OS hardening, patching, agents, and application install in a single recipe rebuild slowly and make it impossible to know when hardening last changed. The fix is layered recipes: a hardened-base recipe builds the parent image, application recipes reference the parent and only add the application layer.
2. **Pipelines that never run.** A pipeline created once with no schedule and no parent-image trigger produces an AMI that is fresh on day one and stale on day 60. The schedule + `EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE` combination is non-default and frequently missed.
3. **No lifecycle policy.** Each build creates a new AMI with EBS snapshots. At one build per week per region per account, snapshot cost climbs into the thousands per month within a year. Lifecycle policies (introduced in late 2023) are the AWS-native cleanup; without them, teams write their own cleanup Lambda or simply pay for the storage.
4. **Build instance attached to a production role.** Image Builder uses an EC2 instance profile during build; if that profile has broad production permissions, a malicious or buggy build component can act on production resources. Build instance profiles should have only what AWSTOE needs.
5. **Inspector findings ignored.** Image Builder integrates with Inspector for vulnerability scans, but the integration is opt-in and the build-stage gate (fail on critical findings) is opt-in. Without both, scans become reports nobody reads.

## Common Decisions (ADR Triggers)

- **Image Builder vs Packer vs HCP Packer** — Image Builder is the AWS-native choice and the right default for AWS-only shops because of Inspector integration, lifecycle policies, cross-region KMS handling, and zero licensing cost; Packer (open source / BSL) is the right choice when the same image must be produced for multiple clouds or for on-prem hypervisors; HCP Packer adds a registry layer with channel promotion and ancestry tracking that Image Builder approximates with image lifecycle and tags but does not match for cross-cloud lineage. See `providers/hashicorp/packer.md` for the alternative.
- **AWS-managed components vs custom components** — AWS-managed components for `update-linux`, `update-windows`, `amazon-cloudwatch-agent-*`, and STIG/CIS hardening are maintained by AWS with documented end-of-support windows and remove a maintenance burden; custom components are required for organization-specific hardening exceptions, internal agent installation, application-layer setup, and any test logic. Use AWS-managed components wherever they exist and custom components for the gaps.
- **Single central pipeline account vs per-account pipelines** — central pipeline account with cross-account distribution gives one source of truth, one set of IAM controls, one Inspector configuration, and one lifecycle policy to manage; per-account pipelines duplicate everything and let images drift; the only reason to run per-account is when accounts are owned by independent teams that need to customize images without coordination, in which case a shared base layer with per-account application recipes is the better compromise.
- **Marketplace hardened base image vs build-from-scratch** — marketplace CIS/STIG images (CIS Hardened Images, Nemu, AWS STIG AMIs) are the fastest path to compliance and include monthly vendor patching, but they carry per-hour marketplace cost across every running instance and limit which hardening exceptions you can document; build-from-scratch via the AWS-managed STIG/CIS components is free but requires the team to maintain the hardening pipeline and keep up with benchmark version changes; most mature organizations build from scratch using the AWS-managed components and reserve marketplace images for narrow regulatory cases.
- **AMI pipeline vs container pipeline for the same workload** — when a workload is being modernized from EC2 to ECS/EKS, both pipelines may be needed during the transition; design the application-layer custom components to work in both contexts (avoid hardcoded paths assuming a full OS) so the container recipe and image recipe share the same component library and the hardening story stays parallel.
- **Build cadence** — monthly is the floor for security; weekly is appropriate for environments under active CVE pressure; daily builds are usually overkill except for base images consumed by many downstream pipelines, where the parent-image-change trigger plus a weekly schedule is a better pattern than a daily cron.
- **Image lifecycle retention window** — retain three to six versions of any AMI currently referenced by a launch template or ASG (rollback capacity); deprecate older versions immediately; delete six to twelve months after deprecation; never delete an AMI still referenced by a running launch template version (the lifecycle policy can be configured to skip referenced AMIs).
- **Distribution scope** — distribute to every region where the workload runs, plus disaster-recovery regions; re-encrypt with per-region KMS CMKs at distribution time rather than relying on the source-region key; for cross-account, use `targetAccountIds` to copy the AMI fully into spoke accounts that need to manage it independently, and `launchPermissions` for accounts that only need to launch.

## Reference Architectures

### Layered Pipeline (Hardened Base + Application)

```
+----------------------+           +-----------------------+
| AWS-managed base AMI |           | AWS-managed components|
| (Amazon Linux 2023,  |           | - update-linux        |
|  Windows Server 2025)|           | - stig-build-linux-*  |
+----------+-----------+           | - cloudwatch-agent    |
           |                       +-----------+-----------+
           |                                   |
           v                                   v
  +-----------------------------------------+
  | Hardened-Base Image Recipe              |
  | + custom components: EDR agent, certs   |
  +--------------------+--------------------+
                       |
                       v
            +------------------------+
            | Hardened-Base Pipeline |   schedule: weekly
            +-----------+------------+   trigger: parent change
                        |
                        v
            +------------------------+
            | AMI: hardened-base v.N |   tags: profile=stig,
            +-----------+------------+         scan_id=...
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
+--------------+ +--------------+ +--------------+
| App-A Recipe | | App-B Recipe | | App-C Recipe |
| parent: HB-N | | parent: HB-N | | parent: HB-N |
| + app layer  | | + app layer  | | + app layer  |
+------+-------+ +------+-------+ +------+-------+
       |                |                |
       v                v                v
[App-A AMI]      [App-B AMI]      [App-C AMI]
       |                |                |
       v                v                v
[Dev/Stg/Prod]   [Dev/Stg/Prod]   [Dev/Stg/Prod]
```

When the hardened-base pipeline produces a new AMI (parent image change), application pipelines configured with `EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE` automatically rebuild on their next scheduled run. Hardening changes propagate without per-application intervention.

### Central Pipeline Account with Cross-Account Distribution

```
                 +--------------------+
                 | Pipeline Account   |
                 |  (build runs here) |
                 |                    |
                 |  Image Builder     |
                 |  Pipeline + Recipe |
                 |  Inspector         |
                 |  Lifecycle Policy  |
                 |  KMS CMK (us-east-1)|
                 +----------+---------+
                            |
            distribution config:
            - copy to us-west-2, eu-west-1
            - re-encrypt with destination-region KMS CMKs
            - share with: org/o-xxxx, accts: [spoke-A, spoke-B]
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
+---------------+   +---------------+   +---------------+
| Spoke Acct A  |   | Spoke Acct B  |   | Spoke Acct C  |
| (us-east-1,   |   | (us-west-2)   |   | (eu-west-1)   |
|  us-west-2)   |   |               |   |               |
| AMI: shared   |   | AMI: shared   |   | AMI: shared   |
| (launch only) |   | (launch only) |   | (launch only) |
| ASG launches  |   | ASG launches  |   | ASG launches  |
| from AMI      |   | from AMI      |   | from AMI      |
+---------------+   +---------------+   +---------------+
```

Spoke accounts receive `launchPermissions` only — they cannot deregister or modify the AMI. Use `targetAccountIds` (full copy) instead when a spoke account needs independent lifecycle management. Per-region KMS CMKs avoid cross-region KMS API calls at instance launch.

### Pipeline with Inspector Gate

```
[Image Pipeline Execution]
        |
        v
+------------------+
| Build Stage      |   build components run on build instance
| - update-linux   |
| - stig-hardening |
| - install agents |
+--------+---------+
        |
        v
+------------------+
| Validate Stage   |   build components' validate phase
| - config checks  |
+--------+---------+
        |
        v
[EBS snapshot of build instance]
        |
        v
+------------------+
| Test Stage       |   test components on a fresh instance
| - Inspector scan |   from the snapshot
| - Goss/InSpec    |
| - smoke tests    |
+--------+---------+
        |
   Inspector findings -> Security Hub
        |
   Critical CVE present?
        |
   +----+----+
   | Yes     | No
   v         v
[FAIL]   [Distribution Stage]
              |
              v
         [Cross-region copy + cross-account share]
              |
              v
         [AMI tagged + lifecycle policy applies]
```

Test stage runs on a *new* instance launched from the snapshot, not the build instance — this catches anything baked into the running build instance that is not actually present in the snapshot (services started by hand, files in `/tmp`).

## Reference Architectures and Documentation

- [What is EC2 Image Builder](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html) -- service overview and resource model
- [Image Builder distribution settings](https://docs.aws.amazon.com/imagebuilder/latest/userguide/manage-distribution-settings.html) -- cross-region, cross-account, and ECR distribution patterns
- [Cross-account AMI distribution](https://docs.aws.amazon.com/imagebuilder/latest/userguide/cross-account-dist.html) -- full reference for `launchPermissions` vs `targetAccountIds`
- [Image lifecycle policies](https://docs.aws.amazon.com/imagebuilder/latest/userguide/image-lifecycle.html) -- retain, deprecate, disable, delete actions and policy scopes
- [Components and AWSTOE](https://docs.aws.amazon.com/imagebuilder/latest/userguide/manage-components.html) -- component model, build vs test phases, AWS-managed vs custom
- [Cron expressions for pipeline scheduling](https://docs.aws.amazon.com/imagebuilder/latest/userguide/cron-expressions.html) -- six-field cron syntax and rate expressions
- [Image Builder integration with Amazon Inspector](https://docs.aws.amazon.com/imagebuilder/latest/userguide/security-vulnerability-scans.html) -- vulnerability scan as a build-stage gate
- [AWS-managed components reference](https://docs.aws.amazon.com/imagebuilder/latest/userguide/toe-component-summary.html) -- catalog of update, hardening, and agent components

---

## See Also

- `providers/aws/ec2-asg.md` -- launch templates and ASGs that consume Image Builder AMIs
- `providers/aws/containers.md` -- ECS/EKS consumption of container images produced by Image Builder
- `providers/aws/iam.md` -- service-linked role and instance profile design for build instances
- `providers/aws/kms.md` -- per-region CMKs for cross-region distribution re-encryption
- `providers/aws/multi-account.md` -- central pipeline account and cross-account distribution patterns
- `providers/aws/devops.md` -- CI/CD integration for component publishing and pipeline triggers
- `providers/hashicorp/packer.md` -- multi-cloud / on-prem alternative
- `general/cloud-workload-hardening.md` -- the [Critical] golden-image-pipeline requirement this file satisfies for AWS
- `general/compute.md` -- immutable image replacement vs in-place patching strategies
- `compliance/pci-dss.md` -- hardened-image controls and Image Builder's role in evidence capture
