# LocalStack (Local AWS Emulator)

## Scope

LocalStack as a local AWS cloud emulator for development and testing. Covers Community, Pro, and Enterprise editions, supported service fidelity, Docker-based deployment, AWS CLI/SDK/IaC integration, persistence, CI/CD patterns, testing strategies, and comparison with alternative local AWS simulation tools.

LocalStack provides a fully functional local AWS cloud stack that runs in a single Docker container. Developers use it to build and test AWS applications offline, run integration tests without incurring AWS costs or requiring credentials, and validate infrastructure-as-code templates before deploying to real AWS environments. The emulator exposes a single endpoint (default `http://localhost:4566`) that accepts AWS API calls for dozens of services, enabling rapid iteration without cloud round-trips or shared environment conflicts.

## Checklist

- [ ] [Critical] Select the appropriate edition: Community (free, open-source, ~60 services with varying fidelity), Pro ($35/month per developer, adds high-fidelity implementations of RDS, ECS, EKS, Cognito, Athena, ElastiCache, CloudFront, IAM enforcement, and persistence), or Enterprise (custom pricing, adds team management, CI analytics, Cloud Pods sharing, SSO, and priority support)
- [ ] [Critical] Identify which AWS services the project uses and verify their support level in LocalStack: high-fidelity services (S3, SQS, SNS, DynamoDB, Lambda, API Gateway, CloudFormation, IAM, CloudWatch Logs, Secrets Manager, SSM Parameter Store, Step Functions, EventBridge) work reliably in Community; partial-support services may lack specific API operations or advanced features
- [ ] [Critical] Configure AWS CLI and SDK clients to use the LocalStack endpoint: set `--endpoint-url http://localhost:4566` per command, use the `AWS_ENDPOINT_URL=http://localhost:4566` environment variable (AWS SDK v2+), or configure endpoint overrides in SDK configuration files; use any dummy credentials (`AWS_ACCESS_KEY_ID=test`, `AWS_SECRET_ACCESS_KEY=test`)
- [ ] [Recommended] Deploy LocalStack via Docker: use `docker run -p 4566:4566 localstack/localstack` for quick startup, or define a `docker-compose.yml` with the `localstack/localstack` image including volume mounts for persistence (`/var/lib/localstack`) and Docker socket mount (`/var/run/docker.sock`) for Lambda container execution
- [ ] [Recommended] Configure service selection and region: set the `DEFAULT_REGION` environment variable (defaults to `us-east-1`); the `SERVICES` environment variable is deprecated in recent versions as all supported services start automatically; set `LOCALSTACK_AUTH_TOKEN` for Pro/Enterprise features
- [ ] [Recommended] Configure Terraform to target LocalStack: use the `tflocal` wrapper (installed via `pip install terraform-local`) which automatically rewrites provider endpoints, or manually configure the AWS provider block with custom endpoint URLs for each service; use `s3_use_path_style = true` and `skip_credentials_validation = true` in the provider block
- [ ] [Recommended] Configure CDK to target LocalStack: use the `cdklocal` wrapper (installed via `npm install -g aws-cdk-local`) which redirects all CDK operations to the LocalStack endpoint; standard `cdk deploy` commands become `cdklocal deploy`
- [ ] [Recommended] Integrate LocalStack into CI/CD pipelines: add LocalStack as a service container in GitHub Actions (`services: localstack: image: localstack/localstack`), as a `service` in GitLab CI, or as a sidecar in other CI systems; run integration tests against LocalStack without needing real AWS credentials or IAM permissions in CI
- [ ] [Recommended] Enable persistence for data to survive container restarts: set `PERSISTENCE=1` environment variable; Community edition supports persistence for core services (S3, DynamoDB, SQS, SNS); Pro edition extends persistence to additional services (RDS, ElastiCache); mount `/var/lib/localstack` as a Docker volume
- [ ] [Optional] Use Cloud Pods (Pro/Enterprise) to capture and share LocalStack state snapshots: save the current state as a named pod (`localstack pod save <name>`), share it with team members or load it in CI to pre-seed test data and infrastructure; useful for reproducing bugs and standardizing test fixtures
- [ ] [Optional] Use LocalStack Desktop (GUI) for visual management of local AWS resources: browse S3 buckets, DynamoDB tables, Lambda functions, and other resources; inspect CloudWatch logs; available for macOS, Windows, and Linux
- [ ] [Optional] Configure multi-account simulation: LocalStack supports multiple AWS account IDs by setting different `AWS_ACCESS_KEY_ID` values; resources are isolated per account ID; useful for testing cross-account access patterns and IAM policies
- [ ] [Optional] Configure multi-region simulation: create resources in different regions by specifying the region in API calls; LocalStack maintains separate resource namespaces per region; useful for testing multi-region deployment strategies
- [ ] [Critical] Document known limitations and ensure the team understands boundaries: IAM policy enforcement is partial in Community (full enforcement requires Pro with `ENFORCE_IAM=1`); VPC networking is not simulated (all resources share the host network); eventual consistency is not simulated (all operations are immediately consistent); service quotas and rate limits are not enforced; some API operations return stubbed or incomplete responses

## Why This Matters

Cloud development without a local emulator creates a slow and expensive feedback loop. Every code change requires deployment to a shared or personal AWS environment, incurring API latency, potential cost, and contention with other developers. LocalStack eliminates this by providing a local AWS-compatible environment that starts in seconds and costs nothing per API call.

Integration testing is where LocalStack delivers the most value. Unit tests with mocked AWS calls verify code logic but miss integration errors — wrong IAM permissions, incorrect CloudFormation resource properties, misconfigured event source mappings, or S3 key naming issues. Tests against LocalStack exercise real AWS API calls against a real (emulated) service, catching these errors before code reaches a real AWS environment. This is substantially more reliable than mock-based testing while remaining fast and free.

For infrastructure-as-code workflows, LocalStack enables a tight validation loop. Terraform plans and CDK synths catch syntax and type errors, but only an actual deployment reveals runtime issues — circular dependencies, unsupported resource combinations, or incorrect property values. Deploying to LocalStack validates the full resource creation flow in seconds rather than the minutes-to-hours required for real AWS deployments.

The cost argument becomes significant at scale. A team of 20 developers each running integration tests 10 times per day against real AWS can accumulate meaningful Lambda invocation, DynamoDB read/write, and S3 operation costs. LocalStack reduces these costs to zero for development and CI, reserving real AWS spend for staging and production validation only.

## Common Decisions (ADR Triggers)

### Community vs. Pro edition [Critical]
Community edition provides high-fidelity emulation of core services (S3, SQS, SNS, DynamoDB, Lambda, API Gateway, CloudFormation, Step Functions, EventBridge) and is sufficient for many projects. Pro is necessary when the project uses services only available in Pro (RDS with real Postgres/MySQL engines, ECS with container orchestration, EKS, Cognito, Athena, Redshift, ElastiCache, CloudFront) or when IAM policy enforcement is required for security testing. Document which services the project uses, whether they are available in Community, and whether the per-developer cost of Pro is justified by the testing fidelity gained.

### LocalStack vs. moto (Python mock library) [Recommended]
moto is a Python library that mocks AWS service calls in-process using decorators or context managers. It requires no Docker container and runs faster for pure unit tests. However, moto only works in Python, cannot test infrastructure-as-code, and does not exercise real HTTP API calls. LocalStack provides a language-agnostic HTTP endpoint that works with any AWS SDK, CLI, Terraform, or CDK. Choose moto for fast Python unit tests that verify SDK call parameters; choose LocalStack for integration tests that validate end-to-end workflows across multiple services and languages.

### LocalStack vs. AWS SAM Local [Recommended]
AWS SAM Local (`sam local invoke`, `sam local start-api`) provides local Lambda and API Gateway emulation specifically for SAM-defined serverless applications. It is tightly integrated with the SAM framework but only covers Lambda and API Gateway. LocalStack emulates dozens of services and works with any deployment framework (SAM, CDK, Terraform, CloudFormation, Serverless Framework). Choose SAM Local for SAM-only projects that only need Lambda/API Gateway testing; choose LocalStack for projects that use multiple AWS services or non-SAM IaC tools.

### Persistence strategy for local development [Recommended]
By default, LocalStack state is ephemeral — restarting the container destroys all resources. Enabling `PERSISTENCE=1` preserves state across restarts, which is convenient for developers who want to keep their local environment intact between work sessions. However, ephemeral mode ensures tests always start from a clean state. Document whether the team uses persistent mode for development and ephemeral mode for CI testing, or whether initialization scripts (`awslocal` commands or Terraform apply) recreate the environment on every start.

### CI/CD integration approach [Recommended]
Options include: running LocalStack as a CI service container (GitHub Actions services, GitLab CI services), starting LocalStack in a `before_script` step, or using LocalStack's CI Docker Compose configuration. Service containers are simplest but may have port mapping and health check timing issues. Script-based startup provides more control over configuration and readiness checks. Document the CI platform, the LocalStack startup method, health check strategy (`curl http://localhost:4566/_localstack/health`), and how test fixtures are initialized.

### Test isolation strategy [Optional]
When multiple test suites run against the same LocalStack instance, resource name collisions can cause flaky tests. Options include: unique resource name prefixes per test run (e.g., `test-{uuid}-my-bucket`), resetting LocalStack between test suites (`curl -X POST http://localhost:4566/_localstack/state/reset`), or running separate LocalStack containers per test suite. Document the chosen approach and the tradeoff between test isolation and execution speed.

---

## See Also

- `providers/aws/containers.md` -- ECS/EKS services that LocalStack Pro emulates locally
- `providers/aws/lambda-serverless.md` -- Lambda development workflow that benefits from LocalStack testing
- `providers/aws/cloudformation.md` -- CloudFormation template validation against LocalStack
- `providers/aws/cdk.md` -- CDK integration with LocalStack via cdklocal wrapper
- `providers/aws/dynamodb.md` -- DynamoDB local testing with high-fidelity LocalStack emulation
- `providers/aws/s3.md` -- S3 operations testing against LocalStack
- `providers/hashicorp/terraform.md` -- Terraform provider configuration for LocalStack endpoints
- `general/testing-strategy.md` -- Testing strategy patterns including integration testing with emulators
- `general/ci-cd.md` -- CI/CD pipeline design including local service emulation
