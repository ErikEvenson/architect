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

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates based on AWS us-east-1 pricing as of early 2025. GPU pricing is particularly volatile — spot prices fluctuate significantly, and new instance types change the cost landscape. Always verify with the provider's pricing calculator.

### GPU Instance Costs (On-Demand, per Hour)

| Instance | GPU | vCPUs | Memory | On-Demand/hr | Spot/hr (typical) | Use Case |
|----------|-----|-------|--------|-------------|-------------------|----------|
| p3.2xlarge | 1x V100 (16 GB) | 8 | 61 GB | $3.06 | $0.92 | Legacy training, medium inference |
| p4d.24xlarge | 8x A100 (40 GB) | 96 | 1.1 TB | $32.77 | $13.10 | Large model training |
| p5.48xlarge | 8x H100 (80 GB) | 192 | 2 TB | $98.32 | $39.33 | Frontier model training, large-scale fine-tuning |
| g5.xlarge | 1x A10G (24 GB) | 4 | 16 GB | $1.01 | $0.30 | Cost-effective inference, light training |
| g5.2xlarge | 1x A10G (24 GB) | 8 | 32 GB | $1.21 | $0.36 | Inference with more CPU/memory |
| g6.xlarge | 1x L4 (24 GB) | 4 | 16 GB | $0.80 | $0.24 | Efficient inference |
| inf2.xlarge | 1x Inferentia2 | 4 | 16 GB | $0.76 | $0.23 | AWS-optimized inference |
| trn1.32xlarge | 16x Trainium | 128 | 512 GB | $21.50 | $6.45 | AWS-optimized training |

### Training Cost Examples

| Workload | Instance | Duration | On-Demand Cost | With Spot (70% savings) |
|----------|----------|----------|---------------|------------------------|
| Fine-tune 7B parameter model | 1x p4d.24xlarge | 8 hours | $262 | $105 |
| Fine-tune 7B model (full) | 4x p4d.24xlarge | 24 hours | $3,146 | $1,258 |
| Train custom CV model | 1x g5.2xlarge | 48 hours | $58 | $17 |
| Hyperparameter sweep (50 trials) | 50x g5.xlarge | 2 hours each | $101 | $30 |
| Pre-train 70B model | 64x p5.48xlarge | 14 days | $8.4M | $3.4M |

### Inference Cost Examples (Monthly)

| Workload | Instance | Requests/day | Monthly Cost |
|----------|----------|-------------|-------------|
| Small model serving (< 1B params) | 1x g6.xlarge | 10K | $580 |
| Medium model serving (7B params) | 1x g5.2xlarge | 50K | $870 |
| LLM serving (70B params) | 2x g5.12xlarge (or p4d) | 100K | $7,200 |
| Batch inference (daily) | g5.xlarge spot (4 hrs/day) | N/A | $36 |
| Real-time + batch hybrid | 1x g5.xlarge (always-on) + spot batch | 10K real-time | $760 |

### Managed ML Platform Costs

| Service | Component | Monthly Cost |
|---------|-----------|-------------|
| SageMaker | Notebook (ml.t3.medium, 8 hr/day) | $30 |
| SageMaker | Training job (ml.p3.2xlarge, 20 hr/mo) | $61 |
| SageMaker | Real-time endpoint (ml.g5.xlarge, 24/7) | $730 |
| SageMaker | Processing job (ml.m5.xlarge, 10 hr/mo) | $2 |
| SageMaker | Feature Store (online: 100 GB, offline: 1 TB S3) | $80 |
| SageMaker | Model Registry | Free |
| Vertex AI (GCP) | Training (n1-standard-8 + 1x T4, 20 hr/mo) | $35 |
| Vertex AI (GCP) | Prediction endpoint (g2-standard-4, 24/7) | $620 |
| W&B (Weights & Biases) | Team plan (5 users) | $250 |
| MLflow | Self-hosted on EC2 (t3.large + EBS) | $80 |

### Biggest Cost Drivers

1. **GPU instance hours** — a single H100 node costs $98/hr. Training large models is the dominant cost. A p5.48xlarge running for a month costs $71K.
2. **Idle inference endpoints** — endpoints running 24/7 at low utilization. A g5.xlarge endpoint at 5% utilization wastes $690/mo.
3. **Experiment waste** — irreproducible experiments, untracked hyperparameter sweeps, and forgotten running instances.
4. **Data storage and movement** — large training datasets (TB+) cost significantly in S3, and data transfer to GPU instances adds overhead.

### Optimization Tips

- Use **Spot Instances for training** (60-70% savings). Implement checkpointing every 15-30 minutes to handle interruptions.
- Use **SageMaker Managed Spot Training** — automatic checkpoint/resume handling.
- **Scale inference to zero** when possible — SageMaker Serverless Inference or custom auto-scaling with scale-down to 0.
- Use **Inferentia/Trainium** (AWS) for 40-50% savings on inference/training if models compile successfully with Neuron SDK.
- Apply **model quantization** (FP16, INT8) — halves memory and often doubles throughput with minimal quality loss.
- Use **batch inference** instead of real-time endpoints for non-latency-sensitive predictions — spot instances for batch are 5-10x cheaper.
- Set **GPU budget alerts** and auto-terminate idle notebooks/training jobs.
- Use **smaller models** when accuracy is acceptable — a well-tuned 7B model can replace a 70B model for many tasks at 1/10th the inference cost.
- Consider **model distillation** — train a smaller model to mimic a larger one for production serving.
- Use **SageMaker Savings Plans** (1yr/3yr) for steady-state inference endpoints — up to 64% savings.

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
