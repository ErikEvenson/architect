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

## Training Resources

### Official Training Platform

- **Linux Foundation Training** — official self-paced courses ($299-395 bundled with exam), instructor-led courses ($1,500-3,000), often bundled as course+exam packages
- **killer.sh** — 2 practice exam sessions included with every CKA/CKAD/CKS exam purchase, considered the closest simulation to the actual exam environment, sessions valid for 36 hours each

### Hands-On Labs

- **KodeKloud** — popular third-party platform ($15-25/mo), hands-on labs, practice tests, and guided exercises specifically for CKA/CKAD/CKS
- **Kubernetes the Hard Way** — free, self-guided tutorial by Kelsey Hightower for building a cluster from scratch — not required for certification but builds deep foundational understanding
- **killercoda.com** — free Kubernetes playground environments for browser-based practice
- **minikube/kind** — local cluster tools for hands-on practice on a workstation
- **Cloud provider free tiers** — EKS, AKS, and GKE managed Kubernetes for practicing with production-grade clusters

### Learning Paths by Role

- **Platform Engineer:** KCNA → CKA → CKS
- **Application Developer:** KCNA → CKAD
- **Security:** CKA → CKS
- **Vendor-Specific:** CKA + managed K8s cert (EKS/AKS/GKE specialty)

### Training Cost and Time Estimates

- ~60-80 hours of study for CKA/CKAD
- ~40-60 hours for CKS (after CKA)
- Exam fee: $395 (includes killer.sh practice sessions + 1 free retake)
- Linux Foundation course+exam bundles: $499-595
- KodeKloud subscription: $15-25/month

### Enterprise/Volume Options

- Linux Foundation corporate training programs for team-wide certification
- Kubernetes Forum and KubeCon workshops for in-person training
- Volume exam voucher purchases available through Linux Foundation

## Reference Links

- [CNCF Certification Programs](https://training.linuxfoundation.org/full-catalog/?_sft_topic_area=cloud-containers) -- Linux Foundation catalog of CKA, CKAD, CKS, KCNA, and KCSA exams
- [Kubernetes Documentation](https://kubernetes.io/docs/home/) -- official docs allowed as open-book reference during CKA/CKAD/CKS exams
- [CNCF Training Portal](https://training.linuxfoundation.org/training/plan-your-training/) -- self-paced and instructor-led courses aligned to CNCF certifications

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/kubernetes/compute.md` -- Kubernetes compute
- `providers/kubernetes/security.md` -- Kubernetes security
- `general/container-orchestration.md` -- container orchestration patterns
