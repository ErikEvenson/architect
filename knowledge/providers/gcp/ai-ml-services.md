# GCP AI and ML Services

## Scope

GCP managed AI and ML services: Vertex AI (model garden with 150+ models, generative AI studio, Gemini API — Gemini 1.5 Pro/Flash/Ultra, custom model training, managed endpoints, pipelines, feature store, vector search, tuning — supervised and RLHF, grounding with Google Search and enterprise data), Google AI Studio (rapid prototyping with Gemini models), Document AI (form parsing, OCR, specialized processors for invoices/receipts/lending/procurement), Vision AI (image classification, object detection, OCR), Speech-to-Text and Text-to-Speech, Natural Language AI (entity analysis, sentiment, syntax, classification), Recommendations AI (retail recommendations), Translation AI, AlloyDB AI (pgvector integration for vector search with PostgreSQL), BigQuery ML (in-database ML — train and predict using SQL). Does not cover TPU/GPU instance types — see `patterns/ai-ml-infrastructure.md`.

## Checklist

- [ ] [Critical] Is the Vertex AI vs direct Gemini API decision made — Vertex AI for enterprise deployments (VPC-SC support, IAM integration, SLAs, data residency, model evaluation, MLOps pipeline integration) vs direct Gemini API (Google AI Studio) for rapid prototyping and simpler use cases without enterprise controls?
- [ ] [Critical] Is the Gemini model selection appropriate — Gemini 1.5 Pro (best quality, 1M+ token context window, multimodal), Gemini 1.5 Flash (fast, cost-effective, 1M context), Gemini Ultra (highest capability) — or are open-source models from Model Garden (Llama, Mistral, Falcon) more cost-effective for the use case?
- [ ] [Critical] Is data residency confirmed — Vertex AI endpoints can be deployed in specific regions, but not all models are available in all regions, and some processing may occur in different regions unless explicitly configured?
- [ ] [Critical] Are Vertex AI safety settings configured — configurable thresholds for harassment, hate speech, sexually explicit content, and dangerous content categories, with block thresholds from BLOCK_NONE to BLOCK_LOW_AND_ABOVE?
- [ ] [Recommended] Is Vertex AI Search evaluated for RAG — managed document indexing, chunking, embedding generation, and retrieval with grounding to enterprise data sources (Cloud Storage, BigQuery, third-party connectors)?
- [ ] [Recommended] Is grounding with Google Search evaluated — Vertex AI can ground Gemini responses with real-time Google Search results, reducing hallucination for factual queries, with source attribution in responses?
- [ ] [Recommended] Is Vertex AI Vector Search evaluated for custom vector similarity search — managed HNSW index, supports filtering, streaming updates, and integrates with Vertex AI Feature Store for feature serving alongside vector retrieval?
- [ ] [Recommended] Is Vertex AI Model Evaluation used before production — automated evaluation metrics (BLEU, ROUGE, coherence, fluency, safety), human evaluation workflows, and side-by-side model comparison?
- [ ] [Recommended] Is Vertex AI pricing understood — per-character or per-token pricing for Gemini models (input and output priced separately), Vertex AI Search per-query pricing, managed endpoint pricing (per-node-hour for custom models), and provisioned throughput for Gemini?
- [ ] [Recommended] Is Document AI evaluated for document processing — pre-trained processors (OCR, form parser, invoice parser, ID parser, lending/procurement processors), custom document extractors, and human-in-the-loop review workflows?
- [ ] [Recommended] Is AlloyDB AI evaluated for vector search workloads — PostgreSQL-compatible with built-in pgvector extension, optimized for vector similarity queries, integrates with Vertex AI embeddings, and provides a familiar SQL interface for RAG applications?
- [ ] [Optional] Is BigQuery ML evaluated for in-database ML — train and predict using SQL syntax, supports linear/logistic regression, XGBoost, DNN, time-series forecasting, and imported TensorFlow/ONNX models, useful for data teams already working in BigQuery?
- [ ] [Optional] Is Vertex AI tuning evaluated — supervised fine-tuning for Gemini models using labeled examples, adapter tuning (LoRA) for parameter-efficient tuning, and distillation for creating smaller task-specific models?
- [ ] [Optional] Are pre-trained AI APIs evaluated for specific tasks — Vision AI (label detection, face detection, OCR), Natural Language AI (entity analysis, sentiment, content classification), Speech-to-Text (streaming and batch transcription with speaker diarization)?
- [ ] [Optional] Is Recommendations AI evaluated for retail and media workloads — managed recommendation engine with real-time serving, A/B testing support, and integration with Google Analytics events?
- [ ] [Recommended] Is Vertex AI monitoring configured — tracking prediction count, latency, error rate, and feature drift via Cloud Monitoring, with model monitoring for training-serving skew detection?

## Why This Matters

GCP's Gemini models offer the largest context windows in the industry (1M+ tokens for Gemini 1.5 Pro), enabling use cases that are impractical on other platforms — such as processing entire codebases, lengthy legal documents, or video content in a single request. However, the Vertex AI vs direct Gemini API distinction is important: Vertex AI provides enterprise controls (VPC Service Controls, customer-managed encryption keys, IAM, audit logging) that the direct Gemini API does not. Organizations that prototype in Google AI Studio must re-architect for Vertex AI when moving to production if enterprise security controls are required.

GCP's AI portfolio is deeply integrated with its data stack — BigQuery ML enables data analysts to build models without leaving SQL, AlloyDB AI adds vector search to PostgreSQL workloads, and Vertex AI Feature Store shares features between training and serving. This integration is GCP's differentiator for organizations already invested in BigQuery and Cloud Storage for their data platform. Document AI processors are pre-trained on Google's document understanding capabilities and often outperform general-purpose LLMs for structured extraction tasks (invoices, forms, IDs) at a fraction of the cost.

## Common Decisions (ADR Triggers)

- **Vertex AI vs direct Gemini API** -- enterprise controls vs simplicity
- **Gemini Pro vs Flash vs open-source models from Model Garden** -- quality vs cost vs control
- **Vertex AI Search vs AlloyDB AI (pgvector) vs custom vector database for RAG** -- managed retrieval vs SQL-native vectors vs self-managed
- **Grounding with Google Search vs enterprise-only grounding** -- real-time factual accuracy vs data privacy
- **Document AI pre-trained processors vs Gemini for document understanding** -- structured extraction vs flexible LLM
- **BigQuery ML vs Vertex AI training for tabular ML workloads** -- SQL-native vs full MLOps
- **Supervised fine-tuning vs adapter tuning vs distillation** -- model customization approach

## Reference Links

- [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs) -- model garden, managed endpoints, pipelines, feature store, and vector search
- [Gemini API documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/overview) -- Gemini model family, prompting, tuning, and grounding
- [Google AI Studio](https://ai.google.dev/) -- rapid prototyping with Gemini models
- [Document AI documentation](https://cloud.google.com/document-ai/docs) -- form parsing, OCR, and specialized processors
- [AlloyDB AI documentation](https://cloud.google.com/alloydb/docs/ai) -- pgvector integration and Vertex AI embeddings for vector search
- [BigQuery ML documentation](https://cloud.google.com/bigquery/docs/bqml-introduction) -- in-database ML training and prediction using SQL

## See Also

- `general/ai-ml-services.md` -- cross-provider AI service strategy
- `patterns/ai-ml-infrastructure.md` -- GPU/MLOps infrastructure patterns
- `providers/gcp/data.md` -- BigQuery and GCP data services
- `providers/gcp/security.md` -- VPC Service Controls and IAM
- `providers/gcp/database.md` -- AlloyDB and Cloud SQL
- `providers/gcp/observability.md` -- Cloud Monitoring for AI services
