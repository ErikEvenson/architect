# Kubernetes / CNCF Certifications and Training

## Scope

Cloud Native Computing Foundation (CNCF) Kubernetes certifications and training. Covers CKA (Certified Kubernetes Administrator), CKAD (Certified Kubernetes Application Developer), CKS (Certified Kubernetes Security Specialist), KCNA (Kubernetes and Cloud Native Associate), KCSA (Kubernetes and Cloud Native Security Associate). Exam format (performance-based labs), training resources, and relevance to container orchestration engagements.

## Checklist

- [ ] [Critical] Is CKA (Certified Kubernetes Administrator) identified as the baseline certification for platform/infrastructure teams — covers cluster architecture, workloads, services, storage, networking, security, and troubleshooting in a hands-on lab environment?
- [ ] [Critical] Is the CKA exam format understood — performance-based (live Kubernetes cluster), 2 hours, open-book (kubernetes.io docs only), passing score 66%, proctored online?
- [ ] [Recommended] Is CKAD (Certified Kubernetes Application Developer) required for development teams deploying to Kubernetes — covers application design, deployment, observability, services, and networking from the developer perspective?
- [ ] [Recommended] Is CKS (Certified Kubernetes Security Specialist) required for teams responsible for cluster security — covers cluster setup, system hardening, supply chain security, runtime security, and network policies? Prerequisite: active CKA.
- [ ] [Recommended] Is certification validity tracked — CKA, CKAD, and CKS are valid for 2 years (changed from 3 years in 2023)?
- [ ] [Recommended] Are killer.sh practice exams used for preparation — included with exam purchase (2 sessions), considered the closest simulation to the actual exam environment?
- [ ] [Recommended] Is KCNA (Kubernetes and Cloud Native Associate) used as the entry point for team members new to Kubernetes and cloud-native concepts — multiple choice format, lower barrier than CKA?
- [ ] [Optional] Is KCSA (Kubernetes and Cloud Native Security Associate) evaluated as a stepping stone before CKS — covers security fundamentals without the hands-on lab format?
- [ ] [Optional] Are Kubernetes the Hard Way exercises used for deep understanding of cluster bootstrapping — not required for certification but builds foundational knowledge?
- [ ] [Recommended] Are vendor-specific Kubernetes certifications (EKS, AKS, GKE) evaluated in addition to CNCF certs for managed Kubernetes engagements?
- [ ] [Optional] Is Linux Foundation Training (training.linuxfoundation.org) evaluated for instructor-led and self-paced courses aligned to CNCF certifications?

## Why This Matters

CNCF certifications are vendor-neutral and performance-based — candidates must solve real problems on live Kubernetes clusters, making them among the most respected infrastructure certifications. The hands-on format means passing CKA demonstrates practical competency, not just theoretical knowledge. CKA is increasingly a hard requirement in job descriptions and RFP evaluation criteria for container platform engagements. The 2-year validity (reduced from 3 years in 2023) means more frequent renewal. For teams working with managed Kubernetes (EKS, AKS, GKE), CKA provides the foundational knowledge but vendor-specific certifications may be additionally required to cover managed service features.

## Common Decisions (ADR Triggers)

- CKA vs CKAD first certification based on role (platform team vs application team)
- CKS investment timeline — prerequisite is active CKA, so plan sequencing
- CNCF vendor-neutral certs vs vendor-specific managed K8s certs (or both)
- KCNA as team-wide baseline vs CKA directly for experienced engineers
- Training approach — Kubernetes the Hard Way + killer.sh vs structured courses

## Reference Links

- [CNCF Certification Programs](https://training.linuxfoundation.org/full-catalog/?_sft_topic_area=cloud-containers) -- Linux Foundation catalog of CKA, CKAD, CKS, KCNA, and KCSA exams
- [Kubernetes Documentation](https://kubernetes.io/docs/home/) -- official docs allowed as open-book reference during CKA/CKAD/CKS exams
- [CNCF Training Portal](https://training.linuxfoundation.org/training/plan-your-training/) -- self-paced and instructor-led courses aligned to CNCF certifications

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/kubernetes/compute.md` -- Kubernetes compute
- `providers/kubernetes/security.md` -- Kubernetes security
- `general/container-orchestration.md` -- container orchestration patterns
