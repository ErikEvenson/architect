# AI/ML Infrastructure

## Overview

AI/ML infrastructure encompasses the compute, storage, pipelines, and operational tooling needed to train, serve, and maintain machine learning models in production. This includes GPU/TPU instance selection, managed ML platforms (SageMaker, Vertex AI, Azure ML), MLOps practices (experiment tracking, model registry, CI/CD for ML), and cost management for expensive GPU workloads. The gap between a working notebook and a production ML system is substantial.

## Checklist

- [ ] What GPU/accelerator instance types are needed? (NVIDIA A100, H100, L4 for inference, T4 for cost-effective inference, Google TPUs, AWS Trainium/Inferentia)
- [ ] Is a managed ML platform used? (SageMaker, Vertex AI, Azure ML — vs self-managed Kubernetes with GPU operators)
- [ ] What is the training pipeline architecture? (data ingestion, preprocessing, distributed training, hyperparameter tuning, model evaluation)
- [ ] How is model serving implemented? (real-time endpoints, batch transform, streaming inference — latency vs throughput requirements)
- [ ] Is there a feature store? (Feast, SageMaker Feature Store, Vertex Feature Store — online/offline feature consistency)
- [ ] How is experiment tracking managed? (MLflow, Weights & Biases, Neptune — hyperparameters, metrics, artifacts, reproducibility)
- [ ] Is there a model registry with versioning? (MLflow Registry, SageMaker Model Registry — approval workflows, staging/production promotion)
- [ ] How are A/B tests and canary deployments handled for models? (traffic splitting, shadow mode, champion/challenger testing)
- [ ] What is the data labeling pipeline? (SageMaker Ground Truth, Label Studio, Scale AI — quality control, annotation guidelines)
- [ ] Is distributed training required? (data parallelism, model parallelism, pipeline parallelism — Horovod, DeepSpeed, PyTorch FSDP)
- [ ] What model optimization techniques are applied? (quantization INT8/FP16, knowledge distillation, pruning, ONNX conversion for portability)
- [ ] How are inference costs managed? (spot/preemptible instances for training, right-sized inference endpoints, auto-scaling to zero, model compilation)
- [ ] How is model drift and data drift detected? (monitoring input distributions, prediction distributions, ground truth feedback loops)
- [ ] What is the GPU cost management strategy? (reserved instances, spot training with checkpointing, inference auto-scaling, multi-tenancy)

## Why This Matters

GPU compute is 5-50x more expensive than CPU compute, making infrastructure decisions directly impact ML project viability. A single H100 instance costs $30+/hour; distributed training jobs can cost thousands per run. Without proper MLOps, teams waste GPU hours on irreproducible experiments, deploy stale models, and cannot roll back when model quality degrades. Feature stores prevent training-serving skew, the most common source of ML production bugs. Model serving architecture (real-time vs batch) dramatically affects cost and latency. Organizations that treat ML infrastructure as an afterthought end up with "notebook-to-production" gaps that delay deployments by months.

## Common Decisions (ADR Triggers)

- **Managed platform vs self-managed** — SageMaker/Vertex AI convenience and cost vs Kubernetes + KubeFlow flexibility and portability
- **GPU instance selection** — training instances (A100, H100) vs inference instances (T4, L4, Inferentia), spot vs on-demand for training
- **Serving architecture** — real-time endpoints vs batch prediction vs streaming, auto-scaling configuration, scale-to-zero capability
- **Feature store adoption** — build vs buy, online/offline store split, feature freshness requirements
- **Experiment tracking tool** — MLflow (open source, self-hosted) vs W&B (managed, better UX) vs platform-native
- **Distributed training framework** — PyTorch FSDP vs DeepSpeed vs Horovod, multi-node vs multi-GPU strategy
- **Model optimization pipeline** — quantization level (FP16, INT8, INT4), distillation strategy, inference runtime (TensorRT, ONNX Runtime, vLLM)
- **ML CI/CD pipeline** — automated retraining triggers, model validation gates, staged rollout, rollback criteria
- **Cost guardrails** — training job budgets, idle GPU detection, spot instance interruption handling, inference endpoint auto-scaling policies
