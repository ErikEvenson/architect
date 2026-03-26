# AI and ML Managed Services

## Scope

Cross-provider strategy for consuming managed AI and ML services: build vs buy decisions for AI capabilities, foundation model selection (proprietary vs open-source), API-based AI vs self-hosted models, data residency and compliance for AI services, cost patterns (token-based, per-transaction, provisioned throughput), responsible AI and content safety, model evaluation and benchmarking, RAG architecture decisions. Does not cover GPU infrastructure or MLOps pipelines — see `patterns/ai-ml-infrastructure.md`. Does not cover provider-specific service details — see provider files.

## Checklist

- [ ] **[Critical]** Is the AI service consumption model decided — API-based managed service (Bedrock, Azure OpenAI, Vertex AI) vs self-hosted open-source models (on GPU instances or Kubernetes) vs hybrid? API services trade control for operational simplicity; self-hosted trades cost predictability for flexibility. Most organizations start with API-based services for speed to market and migrate latency-sensitive or high-volume workloads to self-hosted models as usage patterns become clear.
- [ ] **[Critical]** Is data privacy evaluated for each AI service — does customer data flow to a third-party model provider, is model training on customer data disabled, are inputs/outputs logged, and what data retention policies apply? Most managed services offer opt-out from model training, but this must be explicitly configured — default settings vary by provider and change over time.
- [ ] **[Critical]** Are data residency requirements mapped to AI service regional availability — foundation model APIs are not available in all regions, and some models are restricted by geography (e.g., Azure OpenAI requires separate regional deployments, some models are US/EU only)? Organizations in regulated industries must verify that data does not leave approved jurisdictions during inference, including any intermediate processing steps.
- [ ] **[Critical]** Is the cost model understood — token-based pricing (input/output tokens per request), per-transaction pricing (per API call), provisioned throughput (reserved capacity at fixed cost), GPU instance hours (self-hosted)? Production workloads can generate surprising costs without monitoring. A chatbot handling 10,000 conversations/day with a large context window can cost $5,000-50,000/month depending on model selection and prompt design.
- [ ] **[Critical]** Are responsible AI guardrails configured — content filtering, prompt injection detection, PII redaction, output validation, and bias monitoring? Most managed services provide built-in content safety that must be explicitly configured. Without guardrails, AI services can generate harmful, biased, or factually incorrect content that creates legal and reputational risk.
- [ ] **[Recommended]** Is provisioned throughput vs on-demand evaluated for production workloads — on-demand has no commitment but can be throttled during peak demand; provisioned throughput guarantees capacity but requires commitment and right-sizing? On-demand is appropriate for development and variable workloads; provisioned throughput is appropriate for steady-state production workloads where latency consistency matters.
- [ ] **[Recommended]** Is the RAG (Retrieval-Augmented Generation) architecture decided — vector database selection (pgvector, OpenSearch, Pinecone, dedicated vector DB), chunking strategy (fixed-size, semantic, document-aware), embedding model selection, and retrieval pipeline design? RAG adds domain-specific context to foundation models without fine-tuning, but retrieval quality directly determines output quality — poor chunking or embedding choices produce irrelevant context and degrade responses.
- [ ] **[Recommended]** Is model evaluation performed before production deployment — benchmarking against domain-specific test sets, comparing models on quality/latency/cost, evaluating hallucination rates, and establishing baseline metrics? The most capable model is not always the best choice — smaller models often match larger models on narrow tasks at a fraction of the cost and latency.
- [ ] **[Recommended]** Is a model selection framework documented — evaluating models on task fit (generation, classification, extraction, embedding), quality benchmarks, latency requirements, cost per request, context window size, and vendor lock-in risk? Different tasks within the same application may warrant different models — classification tasks rarely need the most expensive model.
- [ ] **[Recommended]** Is AI service monitoring implemented — tracking token usage, request latency (p50/p95/p99), content filter trigger rates, error rates, cost per day/week/month, and model version drift? Without monitoring, cost overruns and quality degradation go undetected until they become critical. Model provider version updates can silently change output quality.
- [ ] **[Recommended]** Is the domain adaptation strategy decided — prompt engineering (lowest effort, no training), RAG (adds context without model changes), fine-tuning (highest quality, requires training data and compute), or combination? Start with prompt engineering, add RAG when external knowledge is needed, and fine-tune only when the other approaches demonstrably fall short on quality benchmarks.
- [ ] **[Recommended]** Are AI service SLAs understood — most foundation model APIs offer 99.9% availability but with caveats on throughput guarantees, and latency is not typically covered by SLA? Applications that require guaranteed response times must implement fallback strategies (secondary model, cached responses, graceful degradation) to handle throttling and outages.
- [ ] **[Optional]** Is a multi-model routing strategy evaluated — using smaller/cheaper models for simple tasks and larger models for complex tasks, reducing average cost while maintaining quality? Routing logic can be based on input complexity scoring, task classification, or cascading (try the small model first, escalate to the large model if confidence is low).
- [ ] **[Optional]** Is prompt management and versioning implemented — tracking prompt templates, A/B testing prompts, and maintaining prompt libraries for consistency across applications? Prompts are code-equivalent artifacts in AI applications and should be version-controlled, tested, and deployed through CI/CD pipelines.
- [ ] **[Optional]** Is an AI gateway or proxy layer evaluated — centralizing API key management, rate limiting, cost allocation, logging, and model routing across multiple AI services? A gateway layer decouples application code from specific model providers, simplifying model migration and enabling centralized observability.
- [ ] **[Optional]** Are open-source model alternatives benchmarked against proprietary APIs — Llama, Mistral, Mixtral, Gemma for self-hosting vs Anthropic Claude, GPT-4, Gemini for managed API access? Open-source models eliminate per-token costs but require GPU infrastructure and operational expertise — the break-even point depends on request volume, model size, and infrastructure costs.
- [ ] **[Optional]** Is AI service disaster recovery and failover planned — what happens when the primary model provider is unavailable, and is a secondary provider or degraded-mode strategy defined? Multi-provider strategies increase resilience but add complexity in prompt compatibility, output normalization, and API abstraction.
- [ ] **[Optional]** Are AI output caching strategies evaluated — caching identical or semantically similar requests to reduce cost and latency for repetitive queries? Caching is effective for classification, extraction, and FAQ-style generation but inappropriate for creative or context-dependent generation tasks.

## Why This Matters

AI managed services are the fastest-growing cloud spend category. Token-based pricing makes costs unpredictable without monitoring — a single application with poorly optimized prompts or unnecessary context can consume tens of thousands of dollars monthly. Organizations that skip model evaluation and deploy the most capable (and expensive) model for every use case overspend dramatically. Provisioned throughput commitments lock in capacity but waste money if utilization is low. The cost difference between models can be 10-100x for similar quality on narrow tasks, making model selection one of the highest-leverage cost decisions in modern cloud architectures.

Data privacy is the most common blocker for enterprise AI adoption. Many AI services process data through shared infrastructure, and model providers' data retention policies vary significantly. Regulated industries (healthcare, finance, government) require explicit confirmation that customer data is not used for model training and that data residency requirements are met. Responsible AI guardrails are not optional — without content filtering and output validation, AI services can generate harmful, biased, or factually incorrect content that creates legal and reputational risk. Organizations that defer responsible AI decisions to post-launch face costly retrofits and potential compliance violations.

## Common Decisions (ADR Triggers)

### ADR: AI Service Consumption Model

**Context:** The organization needs AI capabilities and must decide between consuming managed API services or hosting models on its own infrastructure.

**Options:**

| Criterion | API-Based Managed Service | Self-Hosted Open-Source Models | Hybrid |
|---|---|---|---|
| Operational complexity | Low — provider manages infrastructure, scaling, and model updates | High — requires GPU provisioning, model serving (vLLM, TGI), monitoring, and updates | Medium — manage self-hosted for some workloads, API for others |
| Cost model | Per-token or per-request — variable, scales with usage | GPU instance hours — fixed infrastructure cost regardless of usage | Mixed — optimize each workload for its cost profile |
| Data privacy | Data sent to provider — must verify retention and training opt-out policies | Data stays in your infrastructure — full control over data lifecycle | Sensitive data on self-hosted, non-sensitive on API |
| Model selection | Limited to provider catalog (typically 5-20 models) | Any open-source model (thousands available on Hugging Face) | Best of both — proprietary quality + open-source flexibility |
| Latency | Network round-trip + provider queue time (50-5000ms typical) | Network-local, no queue (10-500ms typical with dedicated GPU) | Route latency-sensitive requests to self-hosted |
| Scaling | Automatic but subject to provider rate limits and throttling | Manual capacity planning, limited by GPU availability | Scale API usage elastically, self-hosted for baseline |

**Decision drivers:** Data sensitivity and regulatory requirements, request volume and cost projections, latency requirements, model customization needs, team GPU/ML infrastructure expertise, and vendor lock-in tolerance.

### ADR: Foundation Model Selection

**Context:** The application requires a foundation model for one or more AI tasks and must choose among available proprietary and open-source options.

**Options:**
- **Proprietary API models (Anthropic Claude, GPT-4, Gemini):** Highest general quality, frequent updates, no infrastructure management. Highest per-token cost, vendor lock-in, data leaves your infrastructure.
- **Large open-source models (Llama 70B+, Mixtral 8x22B):** Near-proprietary quality on many tasks, full data control, no per-token cost. Requires significant GPU infrastructure (4-8+ GPUs), operational expertise, and slower update cycles.
- **Small open-source models (Llama 8B, Mistral 7B, Gemma 7B):** Good quality for narrow tasks, runs on single GPU, lowest infrastructure cost. Lower quality on complex reasoning, requires task-specific evaluation, may need fine-tuning.
- **Task-specific models (embedding models, classification models, code models):** Optimized for specific task types, often smaller and faster. Limited to their trained task, requires separate model for each capability.

**Decision drivers:** Task complexity (complex reasoning favors larger models), latency budget, cost per request at projected volume, data residency requirements, and whether the task is well-defined (narrow tasks can use smaller models) or open-ended (favors larger models).

### ADR: Domain Adaptation Strategy

**Context:** The foundation model needs domain-specific knowledge or behavior that it does not exhibit out of the box.

**Options:**
- **Prompt engineering:** Add instructions, examples, and constraints to the prompt. Zero training cost, immediate iteration, works with any model. Limited by context window size, increases per-request token cost, prompt injection risk.
- **RAG (Retrieval-Augmented Generation):** Retrieve relevant documents and inject them into the prompt context. Keeps knowledge up-to-date without retraining, works with any model, auditable sources. Requires vector database infrastructure, retrieval quality directly affects output quality, adds latency.
- **Fine-tuning:** Train the model on domain-specific examples. Highest quality for well-defined tasks, reduces prompt size, can encode domain behavior. Requires labeled training data (hundreds to thousands of examples), compute cost for training, and retraining when the base model updates.
- **Combination (prompt engineering + RAG + fine-tuning):** Layer approaches — fine-tune for behavior, RAG for knowledge, prompts for task instructions. Highest quality ceiling but highest complexity and cost.

**Decision drivers:** Availability and volume of training data, how frequently domain knowledge changes, acceptable latency, budget for ongoing training compute, and whether the adaptation is behavioral (fine-tuning) or knowledge-based (RAG).

### ADR: Provisioned Throughput vs On-Demand

**Context:** The production workload has steady-state AI request volume and requires consistent latency and availability.

**Options:**
- **On-demand:** Pay per token/request with no commitment. Zero waste at low volume, automatic access to latest models. Subject to throttling during peak demand, higher per-token cost, no latency guarantees.
- **Provisioned throughput:** Reserve model capacity at a fixed hourly/monthly rate. Guaranteed throughput and consistent latency, lower effective per-token cost at high utilization. Wasted spend if utilization is below commitment, requires capacity planning, commitment period (1 month to 1 year).
- **Mixed (on-demand + provisioned baseline):** Provision for steady-state, burst to on-demand for peaks. Optimizes cost and availability. More complex capacity planning, requires monitoring and adjustment.

**Decision drivers:** Request volume predictability, latency consistency requirements, budget for committed spend, and willingness to manage capacity planning.

### ADR: Vector Database Selection for RAG

**Context:** The RAG architecture requires a vector database to store and retrieve document embeddings.

**Options:**

| Criterion | pgvector (PostgreSQL) | Managed Vector Service (OpenSearch Serverless, Azure AI Search, Vertex Vector Search) | Dedicated Vector DB (Pinecone, Qdrant, Weaviate) |
|---|---|---|---|
| Operational overhead | Low — extension on existing PostgreSQL | Medium — managed service but separate infrastructure | Medium — additional service to manage (SaaS or self-hosted) |
| Scale limit | Millions of vectors (adequate for most enterprise RAG) | Billions of vectors with auto-scaling | Billions of vectors, purpose-built for scale |
| Query performance | Good for < 10M vectors, degrades at scale without tuning | High — optimized for vector search at scale | Highest — purpose-built indexing and retrieval |
| Cost | Minimal — uses existing database | Per-query + storage, can be expensive at scale | Per-vector + query, varies widely by provider |
| Integration complexity | Low — SQL interface, familiar tooling | Medium — provider-specific SDK and query syntax | Medium — dedicated client libraries and APIs |
| Hybrid search | Limited (text + vector requires additional setup) | Built-in (keyword + vector + metadata filtering) | Built-in (most support hybrid search natively) |

**Decision drivers:** Vector count (millions vs billions), existing infrastructure (already running PostgreSQL?), query latency requirements, hybrid search needs (combining keyword and vector search), and team familiarity with the technology.

### ADR: Single-Provider vs Multi-Provider AI Strategy

**Context:** The organization must decide whether to standardize on one AI provider or use multiple providers for different capabilities.

**Options:**
- **Single provider:** Standardize on one platform (e.g., all on Bedrock, all on Azure OpenAI). Simplified operations, consolidated billing, consistent API patterns. Vendor lock-in, limited model selection, single point of failure for all AI capabilities.
- **Multi-provider with abstraction layer:** Use multiple providers behind an AI gateway or abstraction layer. Access to best-of-breed models, provider failover, competitive pricing leverage. Higher operational complexity, prompt compatibility challenges across models, abstraction layer maintenance.
- **Multi-provider without abstraction:** Use each provider's native SDK directly. Lowest initial setup, full access to provider-specific features. Tightly coupled application code, difficult to switch providers, no centralized monitoring or cost tracking.

**Decision drivers:** Model quality requirements (some models are only available on specific platforms), risk tolerance for vendor lock-in, operational complexity budget, and whether the organization has a broader cloud provider standardization strategy.

### ADR: AI Gateway / Proxy Layer

**Context:** The organization uses AI services across multiple applications and needs centralized management of API access, cost tracking, and observability.

**Options:**
- **No gateway (direct API calls):** Each application manages its own API keys, rate limiting, and error handling. Simplest initial setup, no additional infrastructure. Decentralized cost tracking, duplicated retry/fallback logic, no centralized observability.
- **Open-source gateway (LiteLLM, Portkey, custom):** Deploy a proxy layer that normalizes API calls across providers. Centralized key management, unified logging, model routing. Requires infrastructure to host and operate, community support varies, may lag behind provider API changes.
- **Commercial AI gateway:** Use a managed gateway service with built-in analytics, cost management, and compliance features. Richest feature set, vendor support. Additional cost, potential latency overhead, dependency on gateway provider availability.

**Decision drivers:** Number of AI-consuming applications, number of AI providers in use, cost visibility requirements, compliance and audit logging needs, and team capacity to operate additional infrastructure.

## See Also

- `patterns/ai-ml-infrastructure.md` — GPU/MLOps infrastructure patterns
- `providers/aws/ai-ml-services.md` — AWS Bedrock, SageMaker, AI services
- `providers/azure/ai-ml-services.md` — Azure OpenAI, AI Services, AI Search
- `providers/gcp/ai-ml-services.md` — GCP Vertex AI, Gemini, Document AI
- `general/data-classification.md` — Data classification for AI service data flows
- `general/cost.md` — Cost management patterns
- `general/security.md` — Security controls for AI services
