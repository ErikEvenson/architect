# AWS CDK (Cloud Development Kit)

## Scope

AWS-specific infrastructure-as-code using general-purpose programming languages that synthesize to CloudFormation. Covers construct levels, CDK Pipelines, Aspects, testing, and asset handling.

Define AWS infrastructure using general-purpose programming languages (TypeScript, Python, Java, Go, C#). CDK synthesizes CloudFormation templates from code, combining the expressiveness of programming with the reliability of declarative infrastructure.

---

## Checklist

- [ ] **[Critical]** Use L2 constructs (opinionated defaults) over L1 constructs (raw CloudFormation) — L2 constructs encode AWS best practices and reduce boilerplate
- [ ] **[Critical]** Run `cdk diff` before every `cdk deploy` to review planned changes — treat it like a change set review
- [ ] **[Critical]** Never hardcode account IDs or regions — use `Stack.of(this).account` and `Stack.of(this).region` or environment-aware stacks
- [ ] **[Critical]** Set `removalPolicy: RemovalPolicy.RETAIN` on stateful resources (databases, S3 buckets) to prevent accidental deletion during stack destroy
- [ ] **[Critical]** Bootstrap every target account/region with `cdk bootstrap` before first deployment — this creates the CDK staging bucket and IAM roles
- [ ] **[Recommended]** Write unit tests with `assertions` module to verify synthesized CloudFormation matches expectations
- [ ] **[Recommended]** Use CDK Pipelines for self-mutating CI/CD — the pipeline updates itself when you change pipeline code
- [ ] **[Recommended]** Apply Aspects for cross-cutting concerns (tagging, compliance checks, encryption enforcement) rather than modifying each construct individually
- [ ] **[Recommended]** Organize stacks by lifecycle — resources that change together belong in the same stack; resources with different change rates go in separate stacks
- [ ] **[Recommended]** Pin CDK library versions in `package.json` / `requirements.txt` and update deliberately, not automatically
- [ ] **[Optional]** Use CDK context (`cdk.json`) and feature flags to control behavior across CDK versions
- [ ] **[Optional]** Leverage escape hatches (`addPropertyOverride`, `node.defaultChild`) when L2 constructs do not expose a needed property
- [ ] **[Optional]** Explore CDK for Terraform (cdktf) if the team prefers CDK constructs but needs multi-cloud Terraform providers
- [ ] **[Optional]** Use `cdk migrate` to import existing CloudFormation stacks or deployed resources into CDK management

---

## Why This Matters

CDK bridges the gap between software engineering and infrastructure provisioning. By using real programming languages, teams get loops, conditionals, type checking, IDE auto-completion, refactoring tools, and the ability to create abstractions (classes, functions, packages) that are impossible in declarative YAML/HCL. The three-tier construct model (L1/L2/L3) lets teams choose their level of abstraction: L1 for full control, L2 for opinionated best-practice defaults, and L3 for complete architectural patterns. CDK Pipelines eliminate the "who deploys the deployment pipeline" problem with self-mutating pipelines. Aspects provide a visitor pattern for policy enforcement across the entire construct tree. Since CDK synthesizes standard CloudFormation, organizations get CloudFormation's rollback, drift detection, and StackSets capabilities for free. For teams already strong in TypeScript or Python, CDK has a lower effective learning curve than HCL or YAML-heavy approaches.

---

## Core Concepts: Constructs, Stacks, and Apps

```
App (top-level)
  |-- Stack A (maps to a CloudFormation stack)
  |     |-- L3 Construct: ApplicationLoadBalancedFargateService
  |     |     |-- L2: ApplicationLoadBalancer
  |     |     |-- L2: FargateService
  |     |     |     |-- L1: CfnService (raw CloudFormation)
  |     |     |-- L2: TargetGroup
  |     |
  |     |-- L2 Construct: Table (DynamoDB with defaults)
  |
  |-- Stack B
        |-- L2 Construct: Function (Lambda)
        |-- L2 Construct: Bucket (S3)
```

- **L1 (CfnXxx)**: 1:1 mapping to CloudFormation resources. Generated automatically, always up-to-date. Use when L2 does not exist.
- **L2 (e.g., `Bucket`, `Function`, `Table`)**: Opinionated constructs with sensible defaults (encryption enabled, versioning, least-privilege IAM). The recommended level for most use.
- **L3 (Patterns, e.g., `ApplicationLoadBalancedFargateService`)**: Complete architectural patterns combining multiple L2 constructs.

## CDK in TypeScript (Primary Example)

```typescript
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class ApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const table = new dynamodb.Table(this, 'Orders', {
      partitionKey: { name: 'orderId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,  // protect data
      pointInTimeRecovery: true,                  // L2 default: off; enable explicitly
    });

    const fn = new lambda.Function(this, 'OrderHandler', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/order-handler'),
      environment: {
        TABLE_NAME: table.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
    });

    // L2 grant methods generate least-privilege IAM policies
    table.grantReadWriteData(fn);
  }
}
```

## CLI Commands

```bash
# Initialize a new CDK project
cdk init app --language typescript

# Synthesize CloudFormation template (to cdk.out/)
cdk synth

# Show diff between deployed stack and local code
cdk diff

# Deploy all stacks
cdk deploy --all

# Deploy a specific stack with approval for IAM changes
cdk deploy ApiStack --require-approval broadening

# Destroy a stack
cdk destroy ApiStack

# List all stacks in the app
cdk ls

# Bootstrap target account/region
cdk bootstrap aws://123456789012/us-east-1
```

## CDK Pipelines

Self-mutating CI/CD pipeline that deploys itself and application stacks:

```typescript
import { CodePipeline, CodePipelineSource, ShellStep } from 'aws-cdk-lib/pipelines';

const pipeline = new CodePipeline(this, 'Pipeline', {
  pipelineName: 'MyAppPipeline',
  synth: new ShellStep('Synth', {
    input: CodePipelineSource.gitHub('myorg/myrepo', 'main'),
    commands: ['npm ci', 'npx cdk synth'],
  }),
});

// Add stages (environments)
pipeline.addStage(new StagingStage(this, 'Staging', {
  env: { account: '111111111111', region: 'us-east-1' },
}));

pipeline.addStage(new ProductionStage(this, 'Production', {
  env: { account: '222222222222', region: 'us-east-1' },
}), {
  pre: [new ManualApprovalStep('PromoteToProd')],
});
```

The pipeline updates itself: when you modify pipeline code and push, the pipeline re-synthesizes and updates its own definition before deploying application changes.

## Aspects (Cross-Cutting Concerns)

Aspects walk the construct tree and apply checks or modifications:

```typescript
import { IAspect, Annotations } from 'aws-cdk-lib';
import { CfnBucket } from 'aws-cdk-lib/aws-s3';

class BucketEncryptionChecker implements IAspect {
  visit(node: IConstruct): void {
    if (node instanceof CfnBucket) {
      if (!node.bucketEncryption) {
        Annotations.of(node).addError('S3 buckets must have encryption enabled');
      }
    }
  }
}

class MandatoryTagger implements IAspect {
  visit(node: IConstruct): void {
    if (cdk.TagManager.isTaggable(node)) {
      cdk.Tags.of(node).add('CostCenter', '12345');
      cdk.Tags.of(node).add('ManagedBy', 'cdk');
    }
  }
}

// Apply to entire app
cdk.Aspects.of(app).add(new BucketEncryptionChecker());
cdk.Aspects.of(app).add(new MandatoryTagger());
```

## Asset Handling

CDK automatically bundles and uploads local files:

```typescript
// Lambda code from local directory — bundled as zip, uploaded to S3
const fn = new lambda.Function(this, 'Fn', {
  code: lambda.Code.fromAsset('lambda/my-function'),
  // ...
});

// Docker image built and pushed to ECR
const service = new ecs.FargateService(this, 'Service', {
  taskDefinition: taskDef,
  // taskDef references ContainerImage.fromAsset('./docker/app')
});

// NodejsFunction bundles with esbuild automatically
const fn = new lambda_nodejs.NodejsFunction(this, 'Handler', {
  entry: 'src/handlers/order.ts',
  bundling: { minify: true, sourceMap: true },
});
```

## Testing

```typescript
import { Template, Match } from 'aws-cdk-lib/assertions';

describe('ApiStack', () => {
  const app = new cdk.App();
  const stack = new ApiStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  test('DynamoDB table has point-in-time recovery', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      PointInTimeRecoverySpecification: {
        PointInTimeRecoveryEnabled: true,
      },
    });
  });

  test('Lambda has correct environment variables', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      Environment: {
        Variables: {
          TABLE_NAME: Match.anyValue(),
        },
      },
    });
  });

  test('creates exactly one DynamoDB table', () => {
    template.resourceCountIs('AWS::DynamoDB::Table', 1);
  });

  // Snapshot test — detect unintended changes
  test('matches snapshot', () => {
    expect(template.toJSON()).toMatchSnapshot();
  });
});
```

## Escape Hatches

When L2 constructs do not expose a property:

```typescript
const bucket = new s3.Bucket(this, 'Bucket');

// Access the underlying L1 construct
const cfnBucket = bucket.node.defaultChild as s3.CfnBucket;
cfnBucket.addPropertyOverride('IntelligentTieringConfigurations', [{
  Id: 'archive-after-90-days',
  Status: 'Enabled',
  Tierings: [{ AccessTier: 'ARCHIVE_ACCESS', Days: 90 }],
}]);
```

## CDK vs CloudFormation vs Terraform

| Aspect | CDK | CloudFormation | Terraform |
|---|---|---|---|
| Language | TypeScript, Python, Java, Go, C# | YAML/JSON | HCL |
| Abstraction | L1/L2/L3 constructs | Resources only | Resources + modules |
| Logic | Full programming language | Limited (Fn::If, Conditions) | Expressions, for_each |
| Testing | Standard test frameworks | cfn-guard rules | `terraform test`, Sentinel |
| State | CloudFormation-managed | CloudFormation-managed | Self-managed |
| Multi-cloud | No (cdktf for Terraform providers) | No | Yes |
| Learning curve | Low for developers, high for ops | Moderate | Moderate |
| Ecosystem | Constructs Hub, Solutions Constructs | Limited community templates | Large module registry |

---

## Common Decisions (ADR Triggers)

- **CDK vs CloudFormation vs Terraform**: CDK suits teams with strong programming backgrounds. CloudFormation suits declarative-first teams. Terraform suits multi-cloud. Record team skills, cloud strategy, and maintenance considerations.
- **Programming language choice**: TypeScript has the best CDK tooling and most examples. Python is popular for data/ML teams. Java/C# fit enterprise shops. The language choice affects hiring, code review practices, and available constructs.
- **L2 vs L3 construct usage**: L3 patterns (like `ApplicationLoadBalancedFargateService`) trade flexibility for speed. Decide when teams should use patterns versus composing L2 constructs for more control.
- **Mono-stack vs multi-stack architecture**: A single stack is simpler but has CloudFormation resource limits (500). Multiple stacks require cross-stack references and coordinated deployments. Document the decomposition strategy.
- **CDK Pipelines vs external CI/CD**: CDK Pipelines are self-mutating and tightly integrated. External pipelines (GitHub Actions, GitLab CI) offer more flexibility and existing team familiarity. Choose based on operational model.
- **Construct library development**: Decide whether to build an internal construct library (npm package / PyPI) for organizational patterns. This requires versioning, testing, and documentation investment.

---

## Reference Architectures

### Microservices on ECS Fargate (CDK Pipelines)

```
App
  |-- PipelineStack
  |     |-- CodePipeline (self-mutating)
  |     |-- Source: GitHub
  |     |-- Synth: npm ci && cdk synth
  |     |-- Stage: Staging
  |     |     |-- NetworkStack (VPC, subnets, NAT)
  |     |     |-- ServiceStack (ALB + Fargate services)
  |     |     |-- DataStack (RDS, ElastiCache)
  |     |-- Manual Approval
  |     |-- Stage: Production
  |           |-- (same stacks, different parameters)
```

---

## Reference Links

- [AWS CDK Developer Guide](https://docs.aws.amazon.com/cdk/v2/guide/) -- getting started, constructs, stacks, pipelines, and best practices
- [AWS CDK API Reference](https://docs.aws.amazon.com/cdk/api/v2/) -- construct library reference for all supported languages

## See Also

- `general/iac-planning.md` -- IaC strategy selection and planning across providers
- `providers/aws/cloudformation.md` -- Declarative CloudFormation templates that CDK synthesizes to
- `providers/aws/containers.md` -- ECS/EKS resources commonly provisioned via CDK constructs

### Serverless API with Shared Constructs

```
Internal Construct Library (@myorg/cdk-constructs)
  |-- SecureApi (API Gateway + WAF + logging)
  |-- ManagedTable (DynamoDB + backups + alarms)
  |-- MonitoredFunction (Lambda + X-Ray + CloudWatch dashboard)

Application Stack
  |-- SecureApi
  |     |-- Route: POST /orders --> OrderHandler (MonitoredFunction)
  |     |-- Route: GET /orders/{id} --> GetOrderHandler
  |-- ManagedTable (Orders)
  |-- Aspects: BucketEncryptionChecker, MandatoryTagger, CostAllocator
```

### Multi-Account Deployment

```
Management Account
  |-- cdk bootstrap aws://MGMT_ACCT/us-east-1 --trust CICD_ACCT
  |
CI/CD Account
  |-- PipelineStack (CodePipeline)
  |     |-- cdk bootstrap aws://DEV_ACCT/us-east-1 --trust CICD_ACCT
  |     |-- cdk bootstrap aws://PROD_ACCT/us-east-1 --trust CICD_ACCT
  |     |
  |     |-- Stage: Dev   (env: { account: DEV_ACCT, region: 'us-east-1' })
  |     |-- Stage: Prod  (env: { account: PROD_ACCT, region: 'us-east-1' })
  |           |-- pre: ManualApprovalStep
```
