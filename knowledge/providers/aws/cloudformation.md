# AWS CloudFormation

Infrastructure as Code using declarative JSON/YAML templates to provision and manage AWS resources with automatic dependency resolution, rollback, and drift detection.

---

## Checklist

- [ ] **[Critical]** Define all resources in CloudFormation templates — never create production resources manually in the console
- [ ] **[Critical]** Use parameters with `AllowedValues`, `AllowedPattern`, and `ConstraintDescription` to validate inputs at deploy time
- [ ] **[Critical]** Enable termination protection on production stacks (`aws cloudformation update-termination-protection --enable-termination-protection --stack-name prod-stack`)
- [ ] **[Critical]** Set stack policies to prevent accidental updates or replacements of stateful resources (RDS, DynamoDB, S3)
- [ ] **[Critical]** Use change sets to preview every modification before executing (`aws cloudformation create-change-set` then `execute-change-set`)
- [ ] **[Recommended]** Lint templates with `cfn-lint` in CI before deployment (`cfn-lint template.yaml`)
- [ ] **[Recommended]** Use nested stacks or cross-stack references (`Fn::ImportValue`) to decompose large templates into reusable components
- [ ] **[Recommended]** Validate templates with CloudFormation Guard (`cfn-guard validate -d template.yaml -r rules.guard`) for policy-as-code enforcement
- [ ] **[Recommended]** Tag all resources using a `Tags` property or `AWS::CloudFormation::Init` and propagate stack-level tags
- [ ] **[Recommended]** Configure rollback triggers with CloudWatch alarms to auto-rollback failed deployments
- [ ] **[Recommended]** Run drift detection periodically to identify manual changes (`aws cloudformation detect-stack-drift --stack-name my-stack`)
- [ ] **[Optional]** Use StackSets for multi-account, multi-region deployments with AWS Organizations integration
- [ ] **[Optional]** Adopt SAM (`sam deploy --guided`) for serverless workloads to simplify Lambda, API Gateway, and DynamoDB definitions
- [ ] **[Optional]** Implement custom resources (Lambda-backed) for provisioning resources not yet supported by CloudFormation
- [ ] **[Recommended]** Enable Git Sync to automatically trigger stack updates from commits to a linked Git repository (GitHub, Bitbucket, or AWS CodeConnections), eliminating manual `update-stack` calls in CI/CD pipelines
- [ ] **[Recommended]** Deploy CloudFormation Hooks to proactively validate resource configurations before creation or update (e.g., enforce encryption, block public access) -- Hooks run as pre-create/pre-update/pre-delete handlers and can FAIL the operation if policy is violated

---

## Why This Matters

CloudFormation is AWS's native IaC service, meaning it has zero-delay support for new AWS services, deep integration with IAM, AWS Organizations, and Service Catalog, and requires no external state management. Templates serve as the single source of truth for infrastructure — every resource, its configuration, and its dependencies are captured in version-controlled files. When a stack update fails, CloudFormation automatically rolls back to the last known good state, reducing the blast radius of misconfiguration. Change sets provide a critical safety net by showing exactly what will be created, modified, or destroyed before any action is taken. For organizations standardized on AWS, CloudFormation avoids the operational overhead of managing Terraform state backends, provider version pinning, and third-party licensing considerations.

---

## Template Anatomy

A CloudFormation template has seven top-level sections:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: "Production VPC with public and private subnets"

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

Mappings:
  RegionAMI:
    us-east-1:
      HVM64: ami-0abcdef1234567890
    eu-west-1:
      HVM64: ami-0fedcba0987654321

Conditions:
  IsProd: !Equals [!Ref Environment, prod]

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: "10.0.0.0/16"
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub "${Environment}-vpc"

Outputs:
  VpcId:
    Description: "VPC ID"
    Value: !Ref VPC
    Export:
      Name: !Sub "${Environment}-vpc-id"
```

Only the `Resources` section is required. `Parameters` accept user input at deploy time. `Mappings` provide static lookup tables. `Conditions` control whether resources are created. `Outputs` expose values for cross-stack references or display.

## Intrinsic Functions

| Function | Purpose | Example |
|---|---|---|
| `Ref` | Return parameter value or resource physical ID | `!Ref MyBucket` |
| `Fn::GetAtt` | Get resource attribute | `!GetAtt MyBucket.Arn` |
| `Fn::Sub` | String interpolation | `!Sub "arn:aws:s3:::${BucketName}/*"` |
| `Fn::Join` | Concatenate with delimiter | `!Join ["-", [!Ref Env, "app", "sg"]]` |
| `Fn::Select` | Pick item from list | `!Select [0, !GetAZs ""]` |
| `Fn::If` | Conditional value | `!If [IsProd, "m5.xlarge", "t3.micro"]` |
| `Fn::ImportValue` | Cross-stack reference | `!ImportValue prod-vpc-id` |
| `Fn::Split` | Split string into list | `!Split [",", !Ref SubnetList]` |

## Nested Stacks and Cross-Stack References

Nested stacks decompose large templates. The parent passes parameters down; the child exposes outputs:

```yaml
# Parent template
NetworkStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: https://s3.amazonaws.com/templates/network.yaml
    Parameters:
      Environment: !Ref Environment
```

Cross-stack references use `Export` in outputs and `Fn::ImportValue` in consuming stacks. Exports must be unique per account per region. A stack cannot be deleted while another stack imports its values.

## StackSets

StackSets deploy a single template across multiple AWS accounts and regions:

```bash
aws cloudformation create-stack-set \
  --stack-set-name security-baseline \
  --template-body file://security.yaml \
  --permission-model SERVICE_MANAGED \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false
```

Operation preferences control parallelism: `MaxConcurrentPercentage`, `FailureToleranceCount`, and `RegionConcurrencyType` (SEQUENTIAL or PARALLEL). Service-managed StackSets with AWS Organizations auto-deploy to new accounts as they join an OU.

## Change Sets and Drift Detection

Always preview before applying:

```bash
# Create change set
aws cloudformation create-change-set \
  --stack-name prod-app \
  --change-set-name release-v2 \
  --template-body file://app.yaml \
  --parameters ParameterKey=ImageTag,ParameterValue=v2.0.1

# Review changes
aws cloudformation describe-change-set \
  --stack-name prod-app \
  --change-set-name release-v2

# Execute after review
aws cloudformation execute-change-set \
  --stack-name prod-app \
  --change-set-name release-v2
```

Drift detection identifies resources modified outside CloudFormation:

```bash
aws cloudformation detect-stack-drift --stack-name prod-app
aws cloudformation describe-stack-resource-drifts --stack-name prod-app \
  --stack-resource-drift-status-filters MODIFIED DELETED
```

## CloudFormation Guard

Policy-as-code to validate templates before deployment:

```
# rules.guard
AWS::EC2::SecurityGroup {
  Properties.SecurityGroupIngress[*] {
    CidrIp != "0.0.0.0/0" OR
    FromPort == 443
    <<Security groups must not allow unrestricted ingress except HTTPS>>
  }
}

AWS::S3::Bucket {
  Properties.BucketEncryption EXISTS
  <<All S3 buckets must have encryption configured>>
}
```

```bash
cfn-guard validate -d template.yaml -r rules.guard
```

## Custom Resources

For resources CloudFormation does not natively support, use Lambda-backed custom resources:

```yaml
CustomDNS:
  Type: Custom::ExternalDNS
  Properties:
    ServiceToken: !GetAtt CustomResourceFunction.Arn
    DomainName: "app.example.com"
    RecordValue: !GetAtt ALB.DNSName
```

The Lambda function receives `Create`, `Update`, or `Delete` events and must send a response to a pre-signed S3 URL. Always implement idempotency and handle all three request types.

## Stack Policies

Protect critical resources from accidental updates:

```json
{
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "Update:Replace",
      "Principal": "*",
      "Resource": "LogicalResourceId/ProductionDatabase"
    },
    {
      "Effect": "Allow",
      "Action": "Update:*",
      "Principal": "*",
      "Resource": "*"
    }
  ]
}
```

## SAM (Serverless Application Model)

SAM extends CloudFormation with shorthand for serverless resources:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31

Resources:
  OrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: nodejs20.x
      Events:
        Api:
          Type: Api
          Properties:
            Path: /orders
            Method: post
```

```bash
sam build
sam local invoke OrderFunction --event event.json  # Local testing
sam deploy --guided                                  # Interactive deploy
```

## Git Sync

Git Sync connects a CloudFormation stack to a Git repository, automatically deploying template changes when commits are pushed:

```bash
# Stack file in Git repo must be at a specified path
# Configuration is done via AWS Console or CLI
aws cloudformation create-stack \
  --stack-name my-app \
  --template-body file://template.yaml \
  # Git Sync is configured as a stack property linking to a Git repo
```

Git Sync eliminates the need for separate CI/CD pipelines for simple stack deployments. The stack monitors a specified branch and file path, triggering updates when the template file changes. For production workloads requiring approval gates, testing, and multi-environment promotion, a full CI/CD pipeline is still recommended.

## CloudFormation Hooks

Hooks provide proactive, deploy-time policy enforcement:

```yaml
# Hook configuration (registered as a CloudFormation extension)
# Example: Block S3 buckets without encryption
TypeName: MyOrg::S3::EncryptionCheck
Handlers:
  preCreate:
    targetNames:
      - AWS::S3::Bucket
    permissions: []
  preUpdate:
    targetNames:
      - AWS::S3::Bucket
    permissions: []
```

Hooks run before resource creation, update, or deletion and can:
- **PASS** the operation (allow it to proceed)
- **FAIL** the operation (block it with an error message)
- **WARN** (log a warning but allow the operation)

Unlike Guard (which validates templates offline), Hooks run within the CloudFormation service during stack operations, catching policy violations that may not be visible in the template alone (e.g., cross-resource dependencies).

## CloudFormation vs Terraform

| Aspect | CloudFormation | Terraform |
|---|---|---|
| Scope | AWS only | Multi-cloud, multi-provider |
| Language | YAML/JSON (declarative) | HCL (declarative) |
| State | Managed by AWS (no state file) | Self-managed (S3, Terraform Cloud) |
| New AWS features | Day-0 support | Days to weeks delay |
| Rollback | Automatic on failure | Manual (`terraform apply` previous state) |
| Modularity | Nested stacks, cross-stack refs | Modules, workspaces |
| Policy-as-code | CloudFormation Guard | Sentinel, OPA |
| Ecosystem | AWS-specific | Broad community modules |
| Cost | Free (pay for resources) | Free OSS; Terraform Cloud paid tiers |

---

## Common Decisions (ADR Triggers)

- **CloudFormation vs Terraform vs CDK**: If the organization is AWS-only and prefers declarative YAML, CloudFormation is the simplest choice. Multi-cloud or teams wanting richer programming constructs should evaluate Terraform or CDK respectively. Record the decision and rationale.
- **Nested stacks vs cross-stack references vs single large template**: Templates over ~500 resources become unwieldy. Nested stacks provide encapsulation; cross-stack references enable loose coupling. Document the decomposition strategy.
- **StackSets vs per-account pipelines**: StackSets centralize multi-account deployments but limit customization per account. Per-account pipelines offer flexibility at higher operational cost.
- **Custom resources vs waiting for native support**: Custom resources add Lambda maintenance burden. Decide when the operational need justifies building one versus waiting for AWS to add native support.
- **SAM vs raw CloudFormation for serverless**: SAM reduces boilerplate but adds a transform layer. Teams mixing serverless and traditional resources must decide on one or both approaches.
- **State protection strategy**: Define which resources get stack policies, which stacks get termination protection, and how drift is monitored and remediated.
- **Git Sync vs CI/CD pipeline deployments**: Git Sync provides automatic stack updates on commit for simpler workflows; CI/CD pipelines (CodePipeline, GitHub Actions) offer more control with approval gates, testing stages, and multi-environment promotion. Document when each approach is appropriate.
- **CloudFormation Hooks vs Guard vs Config Rules**: Hooks enforce policy at deploy-time (blocking non-compliant creates/updates), Guard validates templates pre-deployment (shift-left), and Config Rules detect non-compliance post-deployment (detective). A comprehensive strategy may use all three layers.

---

## Reference Architectures

### Multi-Account Landing Zone (StackSets + Organizations)

```
Management Account
  |-- StackSet: SecurityBaseline
  |     |-- GuardDuty, Config Rules, CloudTrail
  |     |-- Deployed to all accounts in all regions
  |-- StackSet: NetworkBaseline
  |     |-- VPC, Transit Gateway attachment, VPC Flow Logs
  |     |-- Deployed to workload accounts
  |
  |-- Prod OU
  |     |-- Account: prod-app-1  (auto-deployed stacks)
  |     |-- Account: prod-app-2
  |-- Dev OU
        |-- Account: dev-sandbox  (auto-deployed stacks)
```

### CI/CD Pipeline for CloudFormation

```
Source (Git)
  --> cfn-lint (syntax + best practices)
  --> cfn-guard (policy validation)
  --> Create Change Set (staging)
  --> Manual Approval
  --> Execute Change Set (staging)
  --> Integration Tests
  --> Create Change Set (production)
  --> Manual Approval
  --> Execute Change Set (production)
  --> Drift Detection (scheduled)
```

### Serverless Application (SAM)

```
SAM Template
  |-- AWS::Serverless::Function (Lambda)
  |     |-- Event: API Gateway trigger
  |     |-- Event: SQS queue trigger
  |     |-- Policies: DynamoDBCrudPolicy
  |-- AWS::Serverless::SimpleTable (DynamoDB)
  |-- AWS::Serverless::Api (API Gateway + custom domain)
  |
  sam local start-api  -->  Local development
  sam deploy --guided  -->  Production deployment
```
