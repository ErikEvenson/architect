# Local Development Environments

## Scope

This file covers the decision framework for local development environments: when to use local emulators, local containers, cloud sandbox accounts, or ephemeral cloud environments. It addresses Docker Compose for local service dependencies, cloud service emulators, dev/prod parity, secrets management for local development, database seeding, hot reload workflows, port management, and network simulation. For local Kubernetes options (Docker Desktop, minikube, kind, K3s, Rancher Desktop), see [Container Orchestration](container-orchestration.md) and provider-specific files under [Kubernetes](../providers/kubernetes/docker-desktop.md) and [K3s](../providers/kubernetes/k3s.md). For CI/CD pipeline integration, see [CI/CD Pipeline Design](ci-cd.md). For deployment strategy decisions, see [Deployment](deployment.md).

## Checklist

- [ ] **[Critical]** Choose a local development strategy and document it — local emulators (LocalStack, Azurite, MinIO), cloud sandbox accounts per developer, shared dev environment, or ephemeral environments per feature branch — based on service complexity, cost tolerance, and fidelity requirements
- [ ] **[Critical]** Provide a Docker Compose file (or equivalent) that brings up all service dependencies (databases, caches, queues, object storage) with a single command — developers should never need to install PostgreSQL, Redis, or RabbitMQ directly on their machines
- [ ] **[Critical]** Manage local secrets separately from production — use `.env` files (gitignored), dotenv libraries, or Vault in dev mode; never hardcode credentials in source, Docker Compose files committed to the repo, or shared configuration
- [ ] **[Critical]** Establish a documented onboarding path that gets a new developer from `git clone` to a running local environment in under 30 minutes — track time-to-first-commit as a key metric for developer experience
- [ ] **[Recommended]** Select cloud service emulators based on fidelity needs — LocalStack (AWS: S3, SQS, SNS, DynamoDB, Lambda), Azurite (Azure Blob, Queue, Table Storage), Firebase Emulator Suite (Auth, Firestore, Functions, Hosting), GCP emulators (Pub/Sub, Datastore, Bigtable, Spanner) — and document which services have no viable emulator
- [ ] **[Recommended]** Implement hot reload for all services under active development — file watchers with automatic restart (nodemon, uvicorn --reload, air for Go, Spring DevTools), HMR for frontend frameworks — to keep the edit-save-test cycle under 2 seconds
- [ ] **[Recommended]** Minimize dev/prod parity gaps — use the same database engine and major version locally as production, same message broker, same cache engine; avoid SQLite-in-dev / PostgreSQL-in-prod substitutions that mask bugs
- [ ] **[Recommended]** Create a database seeding strategy — provide scripts or fixtures that populate local databases with realistic (but synthetic) test data, covering edge cases like empty states, large datasets, and multi-tenant scenarios
- [ ] **[Recommended]** Define a port management convention — assign fixed, documented ports per service (e.g., API on 8000, frontend on 3000, database on 5432) and provide a port map in the project README to prevent collisions when developers work on multiple projects
- [ ] **[Recommended]** Evaluate cost implications of each strategy — local emulators are free per developer, cloud sandbox accounts incur per-developer cloud spend (typically $50-200/month), shared dev environments reduce cost but create contention and data pollution
- [ ] **[Optional]** Support network simulation for resilience testing — offline mode testing (can the app degrade gracefully?), latency injection (toxiproxy, tc/netem), and bandwidth throttling to validate behavior under poor network conditions
- [ ] **[Optional]** Document services where local development is impractical — managed services with no emulator (e.g., AWS Aurora Serverless, Azure Cosmos DB multi-region, GCP BigQuery), GPU workloads, complex distributed systems requiring multi-node clusters — and provide a fallback strategy (cloud sandbox or shared dev environment)
- [ ] **[Optional]** Implement ephemeral preview environments for pull requests — spin up a full environment per PR using tools like Argo CD pull request generator, Vercel/Netlify preview deploys, or Namespace.so — to enable review without local setup

## Why This Matters

The local development environment is the first thing every developer touches and the last thing most teams invest in. A broken or slow local setup compounds across the entire engineering organization: if it takes a day to onboard a new developer, that is a day of lost productivity multiplied by every hire, every laptop replacement, and every time someone switches projects. Teams that treat local development as an afterthought end up with tribal knowledge ("ask Sarah how to set up the database") and works-on-my-machine bugs that waste hours in debugging.

The choice between local emulators and cloud sandbox accounts is fundamentally a tradeoff between cost and fidelity. Local emulators like LocalStack provide free, fast iteration with instant feedback loops, but they diverge from real cloud services in subtle ways — IAM policy evaluation, rate limiting, eventual consistency behavior, and service-specific edge cases. Cloud sandbox accounts provide perfect fidelity but introduce costs ($50-200/month per developer), network latency in the development loop, and dependency on internet connectivity. Most teams benefit from a hybrid approach: local emulators for fast inner-loop development, cloud sandboxes for integration testing and validating cloud-specific behavior.

Dev/prod parity failures are a leading cause of production incidents. When developers use SQLite locally but PostgreSQL in production, they miss transaction isolation bugs, JSON operator differences, and migration edge cases. When they skip the message queue locally and use synchronous calls instead, they miss race conditions and ordering guarantees. The Twelve-Factor App methodology identified dev/prod parity as a critical factor over a decade ago, yet teams continue to make this mistake because maintaining parity requires deliberate investment in local tooling.

## Common Decisions (ADR Triggers)

### ADR: Local Development Strategy

**Context:** The team needs to decide how developers run and test cloud-dependent services on their local machines.

**Options:**

| Criterion | Local Emulators | Cloud Sandbox (per dev) | Shared Dev Environment | Ephemeral Environments |
|---|---|---|---|---|
| Fidelity | Medium — emulators approximate but diverge on edge cases | High — real cloud services | High — real cloud services | High — real cloud services |
| Cost | Free | $50-200/month per developer | $50-200/month shared | Per-environment cost, often higher |
| Speed (inner loop) | Fast — no network round-trip | Slower — network latency on every call | Slower — network latency | Slowest — environment spin-up time |
| Offline capable | Yes | No | No | No |
| Data isolation | Perfect — each dev has own instance | Good — separate accounts | Poor — shared data, contention | Good — isolated per branch |
| Setup complexity | Medium — Docker Compose + emulator config | Low — just credentials | Low — just credentials | High — requires CI/CD integration |
| Best Fit | Inner-loop development, unit/integration tests | Cloud-specific feature validation | Small teams, early-stage projects | PR review, pre-merge validation |

**Recommendation:** Use local emulators as the default for inner-loop development (code-test-debug cycles). Provide cloud sandbox accounts for developers who need to validate cloud-specific behavior or work with services that have no emulator. Reserve shared dev environments for early-stage teams where per-developer sandbox costs are not justified. Add ephemeral environments for PR-based review once the team has CI/CD maturity to support it.

### ADR: Cloud Service Emulator Selection

**Context:** The team needs to select which cloud service emulators to use for local development and understand their coverage limitations.

**Options:**
- **LocalStack (AWS):** Emulates S3, SQS, SNS, DynamoDB, Lambda, API Gateway, CloudFormation, IAM, and 60+ other services. Community edition covers core services; Pro edition adds more complete IAM enforcement, advanced Lambda runtimes, and services like RDS and ECS. Well-maintained, large community. Coverage gaps: Aurora Serverless, Bedrock, some advanced IAM policy conditions.
- **Azurite (Azure):** Official Microsoft emulator for Azure Blob Storage, Queue Storage, and Table Storage. High fidelity for storage operations. Does not cover Cosmos DB, Service Bus, Event Hubs, Functions, or other Azure services. Azure Functions Core Tools provides a separate local runtime.
- **Firebase Emulator Suite (GCP/Firebase):** Covers Authentication, Firestore, Realtime Database, Cloud Functions, Hosting, Pub/Sub, and Storage. Tightly integrated with Firebase CLI. Does not cover non-Firebase GCP services.
- **GCP individual emulators:** Google provides standalone emulators for Pub/Sub, Datastore, Bigtable, and Spanner. No emulator for BigQuery, Cloud SQL, GKE, or Cloud Run. Coverage is narrower than LocalStack's AWS coverage.
- **MinIO (S3-compatible):** High-fidelity S3-compatible object storage. Production-grade, not just an emulator. Useful when you need S3 API compatibility across any cloud or on-prem.

**Decision drivers:** Target cloud provider, services used by the application, required fidelity level, team willingness to maintain emulator configuration, and whether the free tier of an emulator covers needed services.

### ADR: Dev/Prod Parity Strategy

**Context:** The team must decide how much investment to make in keeping local development environments aligned with production.

**Options:**
- **Full parity:** Same database engine and version, same message broker, same cache, same service mesh — all running in local containers. Highest fidelity, highest resource consumption (16+ GB RAM common), longest startup time.
- **Selective parity:** Match critical data-path services (database, cache) exactly; substitute or skip non-critical services (logging, monitoring, tracing). Practical balance for most teams. Requires documenting which services are stubbed and what risks that introduces.
- **Minimal parity:** Use in-memory or lightweight substitutes (SQLite for PostgreSQL, in-process queues for Kafka). Fastest startup, lowest resource usage. High risk of parity bugs reaching production. Only appropriate for simple applications with no cloud-specific behavior.

**Recommendation:** Use selective parity as the default. Always match the database engine and version (PostgreSQL, MySQL, MongoDB) — never substitute with SQLite or H2. Match the message broker and cache engine. Stub out observability, service mesh, and CDN layers locally. Document every parity gap and its risk.

### ADR: Local Secrets Management

**Context:** Developers need credentials (database passwords, API keys, service tokens) to run the application locally without compromising production secrets.

**Options:**
- **Dotenv files (.env, gitignored):** Simple, well-supported across frameworks. Each developer maintains a local `.env` file populated from a `.env.example` template. Risk: developers copy production secrets into `.env` files. Mitigation: generate local-only credentials in the Docker Compose setup.
- **Vault dev mode:** Run HashiCorp Vault in dev mode (`vault server -dev`) as part of the local stack. Application reads secrets from Vault, same as production. Higher setup complexity but validates Vault integration locally.
- **Local secrets files with sops/age:** Encrypt secrets in the repo using sops with age keys. Developers decrypt locally. Supports secret rotation via re-encryption. More complex than dotenv, better for teams that need to share non-production secrets securely.
- **Docker Compose-generated credentials:** Docker Compose generates random passwords for local databases and services at startup. No secrets to manage — everything is ephemeral. Limits: does not work for external API keys or third-party service credentials.

**Recommendation:** Use dotenv files with a committed `.env.example` template for most projects. Generate local database and cache credentials in Docker Compose so developers never need to set passwords manually. For teams using Vault in production, run Vault in dev mode locally to validate integration. Never store production credentials in any local secrets mechanism.

## See Also

- [Container Orchestration](container-orchestration.md) — local Kubernetes options (Docker Desktop, minikube, kind, K3s) and orchestration decisions
- [CI/CD Pipeline Design](ci-cd.md) — pipeline integration with local development workflows and ephemeral environments
- [Testing Strategy](testing-strategy.md) — test data management, test pyramid, and environment requirements for each test tier
- [Deployment](deployment.md) — deployment strategies and how local environments feed into staging and production
- [Security](security.md) — secrets management principles and credential handling
- [Dev DNS Patterns](dns-dev-patterns.md) — local DNS resolution and service discovery for development
- [TLS Certificates](tls-certificates.md) — local TLS setup with mkcert and self-signed certificates
