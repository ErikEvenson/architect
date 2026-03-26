# Azure AI and ML Services

## Scope

Azure managed AI and ML services: Azure OpenAI Service (GPT-4o, GPT-4, GPT-4 Turbo, o1/o3-mini reasoning models, DALL-E 3, Whisper, text-embedding-ada-002/text-embedding-3; provisioned throughput units (PTU), content filtering, fine-tuning, Assistants API), Azure AI Services (formerly Cognitive Services — Vision, Speech, Language, Document Intelligence, Custom Vision, Translator), Azure AI Search (vector search, hybrid search, semantic ranking, integrated vectorization, skillsets for document cracking), Azure Machine Learning (training compute, managed endpoints, pipelines, prompt flow, responsible AI dashboard), Azure AI Studio (unified AI development portal, playground, deployments, evaluations), Azure AI Document Intelligence (form extraction, layout analysis, custom models, prebuilt models for invoices/receipts/IDs), Copilot Studio (low-code AI agents and chatbots). Does not cover GPU VM sizes — see `patterns/ai-ml-infrastructure.md`.

## Checklist

- [ ] **[Critical]** Is the Azure OpenAI Service deployment model decided — Standard (pay-per-token, shared capacity, may be throttled), Provisioned (PTU — reserved capacity, predictable latency, monthly commitment), or Global Standard (cross-region load balancing, highest availability)?
- [ ] **[Critical]** Is Azure OpenAI regional availability verified — not all models are available in all regions, GPT-4o and GPT-4 Turbo have different region availability, and PTU capacity must be reserved per region?
- [ ] **[Critical]** Is content filtering configured appropriately — Azure OpenAI has mandatory content filtering enabled by default (hate, sexual, violence, self-harm categories with configurable severity thresholds), and additional filters for jailbreak detection and protected material?
- [ ] **[Critical]** Is data privacy confirmed — Azure OpenAI does not use customer data for model training, prompts and completions are not stored beyond 30 days (abuse monitoring), and customers can apply for modified abuse monitoring with zero data retention?
- [ ] **[Critical]** Are Azure OpenAI quotas and rate limits understood — tokens-per-minute (TPM) and requests-per-minute (RPM) limits per deployment, with separate quotas per model per region per subscription?
- [ ] **[Recommended]** Is Azure AI Search evaluated for RAG — supports vector search (HNSW and exhaustive KNN), hybrid search (vector + keyword), semantic ranking, integrated vectorization (automatic chunking and embedding via skillsets), and direct integration with Azure OpenAI for end-to-end RAG?
- [ ] **[Recommended]** Is Azure AI Search pricing tier selected — Free (limited), Basic ($73/mo, 15 indexes), Standard S1 ($250/mo, 50 indexes, semantic ranking), Standard S2/S3 for large-scale? Vector search storage can be significant — plan for index size.
- [ ] **[Recommended]** Is PTU capacity planning performed — PTUs are measured per model, 1 PTU processes approximately 6 TPM for GPT-4 and 85 TPM for GPT-4o, minimum commitment varies by model, and overprovisioning wastes spend while underprovisioning causes 429 throttling?
- [ ] **[Recommended]** Is Azure AI Document Intelligence evaluated for document processing — prebuilt models (invoices, receipts, identity documents, tax forms), layout analysis (tables, paragraphs, selection marks), and custom models for organization-specific document types?
- [ ] **[Recommended]** Is the Azure AI Studio evaluated as the unified development environment — model catalog, playground for prompt testing, evaluation pipelines, deployment management, and prompt flow for orchestrating multi-step AI workflows?
- [ ] **[Recommended]** Is Azure Machine Learning evaluated for custom model training — managed compute clusters (CPU and GPU), automated ML, responsible AI dashboard (fairness, explainability, error analysis), and managed online endpoints for model serving?
- [ ] **[Recommended]** Are managed identity and private endpoints configured for Azure OpenAI — API key authentication is default but managed identity with RBAC (Cognitive Services OpenAI User role) is recommended for production, and private endpoints keep traffic on the Microsoft backbone?
- [ ] **[Optional]** Is Copilot Studio evaluated for low-code AI agents — builds chatbots and AI assistants with connectors to enterprise data sources, suitable for internal helpdesk and FAQ scenarios without custom development?
- [ ] **[Optional]** Is Azure OpenAI fine-tuning evaluated — supported for GPT-4o-mini and GPT-3.5 Turbo, requires minimum training data (10 examples, 50+ recommended), billed for training compute hours plus hosted fine-tuned model inference?
- [ ] **[Optional]** Are Azure AI Services (formerly Cognitive Services) evaluated for specific tasks — Custom Vision (image classification with minimal training data), Speech Service (real-time transcription, pronunciation assessment), Language Service (entity extraction, summarization, custom NER)?
- [ ] **[Recommended]** Is Azure OpenAI monitoring configured — tracking TokenTransaction, ProcessedPromptTokens, GeneratedTokens, ProvisionedManagedUtilizationV2 metrics via Azure Monitor, plus content filtering metrics?

## Why This Matters

Azure OpenAI Service is the primary enterprise entry point for generative AI due to Microsoft's enterprise relationships, Entra ID integration, and data residency guarantees. The PTU vs Standard deployment decision is the most consequential cost choice — Standard pricing is simple (pay-per-token) but subject to throttling under load, while PTU guarantees latency and throughput but requires capacity planning and minimum monthly commitment. A production chatbot processing 500K tokens/hour on GPT-4o costs approximately $750/month on Standard or requires 6+ PTUs (~$6,000/month) for guaranteed performance. Overprovisioning PTUs is the most common cost mistake.

Azure AI Search has become the default RAG backend in the Azure ecosystem due to integrated vectorization — it can automatically chunk documents, generate embeddings via Azure OpenAI, and serve hybrid search queries without a separate vector database. However, index storage for vector embeddings is substantially larger than keyword-only indexes (3-10x), making tier selection critical. Content filtering on Azure OpenAI is mandatory and cannot be fully disabled — organizations that need unfiltered model access for specific use cases (security research, medical content) must apply for modified content filtering through Microsoft.

## Common Decisions (ADR Triggers)

- **Standard vs PTU vs Global Standard deployment** -- for Azure OpenAI production workloads
- **Azure AI Search vs dedicated vector database** -- Qdrant, Weaviate, or pgvector for RAG
- **Azure OpenAI vs Azure ML managed endpoints** -- managed API vs custom model hosting
- **Azure AI Document Intelligence vs Azure OpenAI** -- structured extraction vs LLM understanding for document processing
- **Content filtering configuration** -- default filters vs modified filtering (requires Microsoft approval)
- **Single-region vs multi-region Azure OpenAI deployment** -- for availability and latency
- **Copilot Studio vs custom development** -- for conversational AI scenarios

---

## See Also

- `general/ai-ml-services.md` -- cross-provider AI service strategy
- `patterns/ai-ml-infrastructure.md` -- GPU/MLOps infrastructure patterns
- `providers/azure/data.md` -- Azure data services
- `providers/azure/security.md` -- Azure security controls
- `providers/azure/identity.md` -- Entra ID integration for AI services
- `providers/azure/observability.md` -- Azure Monitor for AI service metrics
