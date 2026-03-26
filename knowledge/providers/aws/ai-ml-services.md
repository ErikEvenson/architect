# AWS AI and ML Services

## Scope

AWS managed AI and ML services. Covers Amazon Bedrock (foundation model API — Anthropic Claude, Amazon Titan, Meta Llama, Mistral, Cohere, Stability AI; knowledge bases for RAG, agents, guardrails, model evaluation, fine-tuning), Amazon SageMaker (training, hosting, pipelines, feature store, Canvas no-code ML, JumpStart model hub, HyperPod for distributed training), Amazon Q (enterprise AI assistant — Q Business for enterprise search, Q Developer for code assistance), Amazon Comprehend (NLP — entity extraction, sentiment, PII detection), Amazon Rekognition (image/video analysis), Amazon Textract (document extraction — forms, tables, queries), Amazon Transcribe and Polly (speech-to-text, text-to-speech), Amazon Kendra (enterprise search), Amazon Personalize (recommendations), AWS Trainium and Inferentia (custom AI accelerators). Does not cover GPU instance types — see `patterns/ai-ml-infrastructure.md`.

## Checklist

- [ ] **[Critical]** Decide Bedrock vs SageMaker — Bedrock for consuming foundation models via API (serverless, no infrastructure management, pay-per-token), SageMaker for custom model training, fine-tuning, and hosting with full control over infrastructure and model artifacts
- [ ] **[Critical]** Configure Bedrock guardrails for production deployments — content filtering (hate, violence, sexual, misconduct), denied topics, word filters, PII redaction (with configurable entity types), and contextual grounding checks to reduce hallucination
- [ ] **[Critical]** Confirm Bedrock pricing model is understood — on-demand (per input/output token, no commitment, may be throttled), provisioned throughput (reserved model units, guaranteed capacity, 1-month or 6-month commitment), and batch inference (50% discount, async processing)
- [ ] **[Critical]** Confirm data privacy posture — Bedrock does not use customer inputs/outputs for model training by default, data is encrypted in transit and at rest, and inputs/outputs are not stored by AWS unless explicitly configured via CloudWatch logging
- [ ] **[Recommended]** Evaluate Bedrock Knowledge Bases for RAG — managed vector store (OpenSearch Serverless), automatic chunking and embedding, S3 data source sync, and retrieval API; simplifies RAG architecture but has limitations on chunking customization and embedding model selection
- [ ] **[Recommended]** Evaluate Bedrock Agents for tool-use workflows — agents can invoke Lambda functions, query knowledge bases, and chain multi-step reasoning with automatic prompt orchestration
- [ ] **[Recommended]** Use Bedrock model evaluation before production deployment — automated evaluation (accuracy, robustness, toxicity) and human evaluation workflows for comparing models against domain-specific test sets
- [ ] **[Recommended]** Evaluate Amazon Q Business for enterprise search and Q&A — connects to 40+ enterprise data sources (S3, SharePoint, Confluence, Salesforce, databases), with access control respecting source system permissions
- [ ] **[Recommended]** Evaluate SageMaker JumpStart for open-source model deployment — pre-built containers for Llama, Falcon, Mistral, Stable Diffusion with one-click deployment to SageMaker endpoints
- [ ] **[Recommended]** Configure SageMaker inference endpoint auto-scaling — scale to zero for dev/test, target-tracking scaling on InvocationsPerInstance for production, and async inference with SQS queue for batch workloads
- [ ] **[Recommended]** Evaluate Textract and Comprehend for document processing pipelines — Textract for structured extraction (forms, tables, queries on documents), Comprehend for NLP (entity recognition, sentiment, PII detection, custom classification)
- [ ] **[Recommended]** Configure CloudWatch monitoring for Bedrock — tracking InputTokenCount, OutputTokenCount, InvocationLatency, InvocationCount, and ThrottleCount metrics per model
- [ ] **[Optional]** Evaluate AWS Trainium (Trn1) and Inferentia (Inf2) instances for cost-optimized training and inference — up to 50% cost savings vs GPU instances for supported model architectures, requires Neuron SDK compilation
- [ ] **[Optional]** Evaluate Amazon Kendra for enterprise search — ML-powered search with natural language queries, document ranking, and FAQ extraction; higher cost than OpenSearch but better out-of-box relevance for enterprise documents
- [ ] **[Optional]** Evaluate Amazon Personalize for recommendation workloads — managed recommendation engine with real-time personalization, no ML expertise required, but requires structured interaction data
- [ ] **[Optional]** Evaluate SageMaker Canvas for no-code ML — business analysts can build models without code using AutoML, useful for forecasting, classification, and regression on tabular data

## Why This Matters

AWS has the broadest AI service portfolio among hyperscalers. The Bedrock vs SageMaker decision is the most consequential — Bedrock is the right choice for 80% of generative AI use cases (chatbots, document processing, code generation) because it eliminates infrastructure management, but SageMaker is required when custom training, fine-tuning with proprietary data, or hosting open-source models with specific hardware requirements is needed. Choosing SageMaker when Bedrock would suffice adds significant operational overhead.

Bedrock pricing can be surprising at scale — a customer-facing chatbot using Claude 3.5 Sonnet with 8K context averaging 1,000 requests/hour generates roughly $3,000-8,000/month in token costs alone. Provisioned throughput eliminates throttling risk and can reduce per-token cost for sustained workloads, but requires accurate capacity planning — overprovisioning wastes committed spend. Guardrails are not optional for production; without content filtering and PII redaction, regulated industries cannot deploy Bedrock.

## Common Decisions (ADR Triggers)

- **Bedrock vs SageMaker** -- API consumption vs custom training/hosting. Bedrock is appropriate when consuming foundation models without custom training, workloads are inference-only, and serverless operation is preferred. SageMaker is appropriate when custom model training or fine-tuning is required, open-source models need specific hosting configurations, or full control over model artifacts and infrastructure is needed.
- **Bedrock model selection** -- Claude (strongest reasoning), Titan (AWS-native, cheapest embeddings), Llama (open-source, fine-tunable), Mistral (cost-effective for simpler tasks). Model choice affects cost, latency, quality, and vendor lock-in.
- **On-demand vs provisioned throughput** -- On-demand for development, experimentation, and low-volume production. Provisioned throughput for sustained production workloads needing guaranteed capacity and predictable latency. Batch inference for offline processing where 50% cost savings outweigh async latency.
- **Bedrock Knowledge Bases vs custom RAG pipeline** -- Knowledge Bases for managed simplicity (automatic chunking, embedding, vector store). Custom RAG for control over chunking strategies, embedding model selection, hybrid search, metadata filtering, and reranking. Custom pipelines add complexity but enable domain-specific optimization.
- **Textract + Comprehend vs Bedrock for document processing** -- Textract for structured extraction (forms with known fields, tables, specific queries). Bedrock for unstructured understanding (summarization, classification, free-form Q&A over documents). Many production pipelines combine both — Textract extracts structured data, Bedrock handles reasoning over extracted content.
- **SageMaker real-time vs async vs batch inference** -- Real-time endpoints for low-latency interactive workloads (sub-second response). Async inference with SQS queue for workloads tolerating minutes of latency (document processing, image generation). Batch transform for offline processing of large datasets.

## Reference Links

- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/) -- foundation model access, knowledge bases, agents, and guardrails
- [Amazon SageMaker Developer Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/) -- custom model training, hosting, pipelines, and MLOps
- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) -- on-demand, provisioned throughput, and batch inference pricing

## See Also

- `general/ai-ml-services.md` -- cross-provider AI service strategy
- `patterns/ai-ml-infrastructure.md` -- GPU/MLOps infrastructure patterns
- `providers/aws/lambda-serverless.md` -- Lambda for Bedrock agent actions
- `providers/aws/s3.md` -- S3 as data source for Knowledge Bases and training data
- `providers/aws/observability.md` -- CloudWatch monitoring for AI services
