# Pulumi

## Scope

Pulumi infrastructure as code: state backends (Pulumi Cloud, S3, GCS), secrets encryption, stack-per-environment design, component resources, CrossGuard policy packs, stack references, Pulumi ESC, Automation API, and multi-language support (TypeScript, Python, Go, C#, Java).


Infrastructure as Code using general-purpose programming languages with real-time state management. Pulumi supports TypeScript, Python, Go, C#, Java, and YAML to define, deploy, and manage cloud resources across AWS, Azure, GCP, Kubernetes, and 100+ providers.

---

## Checklist

- [ ] **[Critical]** Choose and configure a state backend before any deployment — Pulumi Cloud (default), S3, Azure Blob, GCS, or local file; production workloads must use a remote backend
- [ ] **[Critical]** Run `pulumi preview` before every `pulumi up` to review planned changes — never deploy blindly
- [ ] **[Critical]** Enable secrets encryption for all sensitive configuration (`pulumi config set --secret dbPassword hunter2`) — Pulumi encrypts secrets in state by default
- [ ] **[Critical]** Use separate stacks for each environment (dev, staging, prod) with `Pulumi.<stack>.yaml` configuration files
- [ ] **[Critical]** Protect stateful resources with `protect: true` option to prevent accidental deletion during `pulumi destroy`
- [ ] **[Recommended]** Write unit tests using your language's test framework to verify resource properties before deployment
- [ ] **[Recommended]** Use component resources to create reusable abstractions (similar to Terraform modules) with well-defined inputs and outputs
- [ ] **[Recommended]** Implement CrossGuard policy packs for organizational compliance (encryption, tagging, allowed regions)
- [ ] **[Recommended]** Use stack references for cross-stack dependencies instead of hardcoding values between projects
- [ ] **[Recommended]** Pin provider versions in your dependency file (`package.json`, `requirements.txt`, `go.mod`) for reproducible deployments
- [ ] **[Recommended]** Use Pulumi ESC for centralized environment, secret, and configuration management across stacks
- [ ] **[Optional]** Leverage the Automation API to embed Pulumi operations in custom CLIs, web services, or testing frameworks
- [ ] **[Optional]** Use `pulumi import` to bring existing cloud resources under Pulumi management
- [ ] **[Optional]** Explore `pulumi convert --from terraform` to migrate existing Terraform configurations

---

## Why This Matters

Pulumi enables infrastructure as software rather than infrastructure as configuration. By using real programming languages, teams get full IDE support (auto-completion, type checking, refactoring), existing test frameworks, package managers, and the ability to create abstractions using the same patterns they use for application code. Unlike CDK which only targets AWS (via CloudFormation), Pulumi natively supports every major cloud, Kubernetes, and dozens of SaaS providers with a single tool. State management is flexible — Pulumi Cloud provides a managed backend with RBAC, audit logs, and drift detection, but organizations can self-host state in S3 or other blob stores. Built-in secrets management encrypts sensitive values in state without requiring external tools. The Automation API is unique to Pulumi — it allows embedding infrastructure operations directly in applications, enabling use cases like self-service platforms, dynamic environment provisioning, and infrastructure testing harnesses that are difficult with CLI-only tools.

---

## Core Concepts

```
Project (pulumi.yaml — language, name, runtime)
  |-- Stack: dev   (Pulumi.dev.yaml — config values)
  |-- Stack: staging (Pulumi.staging.yaml)
  |-- Stack: prod  (Pulumi.prod.yaml)
  |
  State Backend (stores resource state)
  |-- Pulumi Cloud (app.pulumi.com)
  |-- Self-managed: s3://my-bucket/pulumi-state
  |-- Self-managed: azblob://container
  |-- Self-managed: gs://bucket
  |-- Local: file://~/.pulumi
```

## Languages and Basic Usage

### TypeScript

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
const environment = config.require("environment");

const bucket = new aws.s3.Bucket("data-bucket", {
  bucket: `myapp-${environment}-data`,
  versioning: { enabled: true },
  serverSideEncryptionConfiguration: {
    rule: {
      applyServerSideEncryptionByDefault: {
        sseAlgorithm: "aws:kms",
      },
    },
  },
  tags: { Environment: environment, ManagedBy: "pulumi" },
});

export const bucketArn = bucket.arn;
```

### Python

```python
import pulumi
import pulumi_aws as aws

config = pulumi.Config()
environment = config.require("environment")

bucket = aws.s3.Bucket("data-bucket",
    bucket=f"myapp-{environment}-data",
    versioning=aws.s3.BucketVersioningArgs(enabled=True),
    server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
        rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
            apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                sse_algorithm="aws:kms",
            ),
        ),
    ),
    tags={"Environment": environment, "ManagedBy": "pulumi"},
)

pulumi.export("bucket_arn", bucket.arn)
```

## CLI Commands

```bash
# Create a new project
pulumi new aws-typescript

# Set configuration
pulumi config set environment prod
pulumi config set --secret dbPassword 's3cret!'

# Preview changes (like terraform plan)
pulumi preview

# Deploy changes
pulumi up

# Deploy with auto-approval (CI/CD)
pulumi up --yes

# Show current stack outputs
pulumi stack output

# Destroy all resources
pulumi destroy

# Import existing resource
pulumi import aws:s3/bucket:Bucket my-bucket my-existing-bucket-name

# Switch stacks
pulumi stack select prod

# View stack state
pulumi stack
```

## State Backend Configuration

```bash
# Pulumi Cloud (default)
pulumi login

# Self-managed S3
pulumi login s3://my-pulumi-state-bucket

# Self-managed Azure Blob
pulumi login azblob://pulumi-state-container

# Self-managed GCS
pulumi login gs://my-pulumi-state-bucket

# Local filesystem
pulumi login --local
```

## Component Resources (Reusable Abstractions)

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

interface VpcArgs {
  cidrBlock: string;
  azCount: number;
  enableNatGateway: boolean;
  tags: Record<string, string>;
}

class Vpc extends pulumi.ComponentResource {
  public readonly vpcId: pulumi.Output<string>;
  public readonly publicSubnetIds: pulumi.Output<string>[];
  public readonly privateSubnetIds: pulumi.Output<string>[];

  constructor(name: string, args: VpcArgs, opts?: pulumi.ComponentResourceOptions) {
    super("myorg:network:Vpc", name, {}, opts);

    const vpc = new aws.ec2.Vpc(`${name}-vpc`, {
      cidrBlock: args.cidrBlock,
      enableDnsSupport: true,
      enableDnsHostnames: true,
      tags: { ...args.tags, Name: `${name}-vpc` },
    }, { parent: this });

    this.vpcId = vpc.id;

    // Create subnets, route tables, NAT gateways...
    // (implementation details)

    this.registerOutputs({
      vpcId: this.vpcId,
    });
  }
}

// Usage
const vpc = new Vpc("prod", {
  cidrBlock: "10.0.0.0/16",
  azCount: 3,
  enableNatGateway: true,
  tags: { Environment: "prod" },
});
```

## Stack References (Cross-Stack Dependencies)

```typescript
// In network stack: export values
export const vpcId = vpc.id;
export const privateSubnetIds = privateSubnets.map(s => s.id);

// In application stack: reference network stack
const networkStack = new pulumi.StackReference("myorg/network/prod");
const vpcId = networkStack.getOutput("vpcId");
const subnetIds = networkStack.getOutput("privateSubnetIds");

const service = new aws.ecs.Service("app", {
  networkConfiguration: {
    subnets: subnetIds,
  },
});
```

## Secrets Management

```bash
# Set a secret (encrypted in state)
pulumi config set --secret dbPassword 'my-secret-password'

# Use AWS KMS for encryption
pulumi stack init prod --secrets-provider="awskms://alias/pulumi-secrets"

# Use Azure Key Vault
pulumi stack init prod --secrets-provider="azurekeyvault://mykeyvault.vault.azure.net/keys/pulumi-key"
```

```typescript
// Access secrets in code
const config = new pulumi.Config();
const dbPassword = config.requireSecret("dbPassword");  // Output<string>, never logged

// Create secret outputs
const connectionString = pulumi.secret(
  pulumi.interpolate`postgresql://admin:${dbPassword}@${db.endpoint}/mydb`
);
```

## CrossGuard (Policy-as-Code)

```typescript
// policy-pack/index.ts
import { PolicyPack, validateResourceOfType } from "@pulumi/policy";
import * as aws from "@pulumi/aws";

new PolicyPack("aws-security", {
  policies: [
    {
      name: "s3-no-public-read",
      description: "S3 buckets must not have public read ACLs",
      enforcementLevel: "mandatory",  // "advisory" | "mandatory" | "remediate"
      validateResource: validateResourceOfType(aws.s3.Bucket, (bucket, args, reportViolation) => {
        if (bucket.acl === "public-read" || bucket.acl === "public-read-write") {
          reportViolation("S3 bucket must not have public read access");
        }
      }),
    },
    {
      name: "required-tags",
      description: "All resources must have required tags",
      enforcementLevel: "mandatory",
      validateResource: (args, reportViolation) => {
        if (args.props.tags) {
          const requiredTags = ["Environment", "CostCenter", "ManagedBy"];
          for (const tag of requiredTags) {
            if (!(tag in args.props.tags)) {
              reportViolation(`Missing required tag: ${tag}`);
            }
          }
        }
      },
    },
  ],
});
```

```bash
# Run with policy enforcement
pulumi up --policy-pack ./policy-pack

# Publish to Pulumi Cloud for organization-wide enforcement
pulumi policy publish ./policy-pack
```

## Automation API

Embed Pulumi in applications — no CLI required:

```typescript
import { LocalWorkspace } from "@pulumi/pulumi/automation";

async function deployInfra(environment: string) {
  const stack = await LocalWorkspace.createOrSelectStack({
    stackName: environment,
    projectName: "myapp",
    program: async () => {
      // Pulumi program inline
      const bucket = new aws.s3.Bucket("app-bucket");
      return { bucketName: bucket.id };
    },
  });

  await stack.setConfig("aws:region", { value: "us-east-1" });

  const previewResult = await stack.preview();
  console.log("Changes:", previewResult.changeSummary);

  const upResult = await stack.up({ onOutput: console.log });
  console.log("Outputs:", upResult.outputs);

  return upResult.outputs;
}
```

Use cases: self-service infrastructure portals, dynamic test environment provisioning, infrastructure testing harnesses, custom CLI tools.

## Testing

```typescript
// Unit test (TypeScript with Mocha)
import * as pulumi from "@pulumi/pulumi";

// Mock Pulumi runtime
pulumi.runtime.setMocks({
  newResource: (args) => ({ id: `${args.name}-id`, state: args.inputs }),
  call: (args) => args.inputs,
});

describe("S3 Bucket", () => {
  let infra: typeof import("./index");

  before(async () => {
    infra = await import("./index");
  });

  it("should have versioning enabled", (done) => {
    pulumi.all([infra.bucket.versioning]).apply(([versioning]) => {
      assert.strictEqual(versioning?.enabled, true);
      done();
    });
  });

  it("should have encryption configured", (done) => {
    pulumi.all([infra.bucket.serverSideEncryptionConfiguration]).apply(([enc]) => {
      assert.ok(enc);
      done();
    });
  });
});
```

## Pulumi ESC (Environments, Secrets, Configuration)

```yaml
# Pulumi.yaml ESC environment reference
environment:
  - aws-prod  # pulls config from Pulumi ESC environment

# ESC environment definition (in Pulumi Cloud)
# aws-prod:
#   values:
#     aws:region: us-east-1
#     dbPassword:
#       fn::secret: "prod-password"
#     pulumiConfig:
#       environment: prod
```

```bash
# Open environment in shell
pulumi env open aws-prod

# Run command with environment
pulumi env run aws-prod -- aws s3 ls
```

## Pulumi vs Terraform

| Aspect | Pulumi | Terraform |
|---|---|---|
| Language | TypeScript, Python, Go, C#, Java, YAML | HCL |
| State | Pulumi Cloud, S3, Azure Blob, GCS, local | Terraform Cloud, S3, Azure Blob, GCS, local |
| Secrets | Built-in encryption (passphrase, KMS) | Marked sensitive, stored in state plaintext by default |
| Providers | 100+ (many generated from Terraform providers) | 3000+ (largest ecosystem) |
| Policy-as-code | CrossGuard (TypeScript, Python, OPA) | Sentinel (paid), OPA |
| Testing | Native language test frameworks | `terraform test`, Terratest |
| Automation | Automation API (embed in apps) | CLI-only (or API via Terraform Cloud) |
| Module ecosystem | Smaller, growing | Very large (Terraform Registry) |
| Learning curve | Low for developers, higher for ops | Moderate; HCL is purpose-built |
| Pricing | Free OSS; Pulumi Cloud paid tiers | Free OSS; Terraform Cloud paid tiers |
| Migration | `pulumi convert --from terraform` | N/A (native) |

---

## Common Decisions (ADR Triggers)

- **Pulumi vs Terraform**: Pulumi excels when teams prefer real programming languages, need the Automation API, or value built-in secrets management. Terraform has a larger provider ecosystem and more community modules. Record the team's language skills, multi-cloud requirements, and state management preferences.
- **State backend selection**: Pulumi Cloud offers managed state, RBAC, audit logs, drift detection, and CI/CD integration. Self-managed backends (S3, Azure Blob) offer more control and no SaaS dependency. Document compliance, cost, and operational requirements.
- **Secrets provider**: Default passphrase encryption is simple but requires distributing the passphrase. KMS-based encryption integrates with cloud IAM. Evaluate based on secret rotation requirements and key management policies.
- **Mono-repo vs multi-repo project structure**: A single repo simplifies cross-stack references but can slow CI. Multiple repos provide team autonomy at the cost of coordination. Document the organization structure and deployment coupling.
- **CrossGuard enforcement level**: Advisory policies warn; mandatory policies block deployment. Decide which policies are hard blockers versus informational, and who can override.
- **Automation API adoption**: Embedding Pulumi in applications (self-service portals, ephemeral environments) adds significant capability but also complexity. Document use cases and maintenance ownership.

---

## Reference Architectures

### Multi-Cloud Deployment

```
Pulumi Project: multi-cloud-app
  |-- Stack: aws-prod
  |     |-- Provider: @pulumi/aws
  |     |-- EKS Cluster, RDS, S3, CloudFront
  |
  |-- Stack: azure-prod
  |     |-- Provider: @pulumi/azure-native
  |     |-- AKS Cluster, Azure SQL, Blob Storage, Front Door
  |
  |-- Stack: shared-dns
  |     |-- Provider: @pulumi/cloudflare
  |     |-- DNS records pointing to both clouds
  |     |-- Stack references to aws-prod and azure-prod outputs
  |
  Policy Pack: company-security
  |-- Applied to all stacks via Pulumi Cloud
  |-- Enforces encryption, tagging, allowed regions
```

### Self-Service Platform (Automation API)

```
Web Application (Express/FastAPI)
  |-- POST /environments
  |     |-- Automation API: LocalWorkspace.createOrSelectStack()
  |     |-- Inline program defines VPC, EKS, RDS
  |     |-- stack.up() provisions infrastructure
  |     |-- Returns endpoints and credentials
  |
  |-- DELETE /environments/:id
  |     |-- Automation API: stack.destroy()
  |     |-- Cleans up all resources
  |
  |-- GET /environments/:id/status
        |-- stack.preview() shows current state
        |-- Returns resource list and outputs
```

### GitOps CI/CD Pipeline

```
Git Push
  --> CI (GitHub Actions / GitLab CI)
  |     |-- pulumi preview (on PR — comment plan on PR)
  |     |-- Policy pack validation (CrossGuard)
  |     |-- Unit tests (language-native test framework)
  |
  --> Merge to main
  |     |-- pulumi up --yes --stack staging
  |     |-- Integration tests against staging
  |     |-- Manual approval gate
  |     |-- pulumi up --yes --stack prod
  |
  --> Pulumi Cloud
        |-- State storage and locking
        |-- Deployment history and audit log
        |-- Drift detection (scheduled)
```

## See Also

- `general/iac-planning.md` -- infrastructure as code planning patterns
- `providers/hashicorp/terraform.md` -- Terraform as alternative IaC tool
- `providers/hashicorp/vault.md` -- Vault for secret management in Pulumi stacks

## Reference Links

- [Pulumi Documentation](https://www.pulumi.com/docs/) -- concepts, state management, secrets encryption, and multi-language SDK reference
- [Pulumi Registry](https://www.pulumi.com/registry/) -- provider catalog for AWS, Azure, GCP, Kubernetes, and 150+ cloud services
- [Pulumi ESC (Environments, Secrets, Configuration)](https://www.pulumi.com/docs/esc/) -- centralized environment and secrets management across stacks
