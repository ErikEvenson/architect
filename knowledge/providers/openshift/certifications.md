# Red Hat OpenShift Certifications and Training

## Scope

Red Hat certification paths relevant to OpenShift container platform engagements. Covers RHCSA (EX200), RHCE (EX294), EX280 (Red Hat Certified Specialist in OpenShift Administration), EX288 (Red Hat Certified Specialist in OpenShift Application Development), DO280/DO288 courses. Exam format (performance-based), Red Hat Learning Subscription, partner certification requirements.

## Checklist

- [Critical] Is EX280 (OpenShift Administration) identified as the primary certification for platform teams — covers installation, configuration, management, troubleshooting, networking, storage, security, and updates of OpenShift clusters?
- [Critical] Is the Red Hat exam format understood — all Red Hat exams are performance-based (live systems, no multiple choice), making them among the most rigorous in the industry?
- [Critical] Is RHCSA (EX200) understood as a prerequisite foundation — OpenShift administration requires solid Linux system administration skills?
- [Recommended] Is EX288 (OpenShift Application Development) required for development teams — covers building, deploying, and managing applications using OpenShift, including S2I, templates, and Operators?
- [Recommended] Is RHCE (EX294) evaluated for teams managing OpenShift at scale — covers Ansible automation which is core to OpenShift lifecycle management?
- [Recommended] Is Red Hat Learning Subscription (RHLS) evaluated for team training — provides access to all Red Hat courses, labs, and exam prep ($7,000/year per seat but comprehensive)?
- [Recommended] Is certification validity tracked — Red Hat certifications are valid for 3 years (tied to the major RHEL version), among the longest validity periods?
- [Recommended] Are DO280 (OpenShift Administration I) and DO380 (OpenShift Administration II) courses used for structured preparation before attempting EX280?
- [Optional] Is Red Hat Certified Architect (RHCA) targeted for senior engineers — requires RHCE plus 5 specialist certifications including EX280?
- [Optional] Are Red Hat partner program certification requirements assessed — Red Hat partner tiers require minimum RHCSA and specialist-certified headcount?
- [Optional] Is EX380 (OpenShift Administration II) evaluated for advanced cluster management, including multi-cluster, GitOps, and advanced networking?

## Why This Matters

Red Hat certifications are entirely performance-based — candidates must complete tasks on live systems within time limits, with no multiple choice questions. This makes them among the most respected certifications in the infrastructure space because passing demonstrates real-world competency. EX280 (OpenShift Administration) is the gold standard for container platform engineers. The Red Hat Learning Subscription is expensive but provides the most comprehensive lab-based training environment. For teams running OpenShift, EX280 is effectively a hard requirement — the platform's operational model (Operators, machine configs, cluster updates) requires specific knowledge that general Kubernetes experience does not fully cover. The 3-year validity is the most generous among major vendors.

## Common Decisions (ADR Triggers)

- RHCSA followed by EX280 vs CKA followed by EX280 certification path (Linux foundation vs Kubernetes foundation first)
- EX280 vs CKA priority for teams running OpenShift (EX280 is OpenShift-specific, CKA is vendor-neutral)
- Red Hat Learning Subscription investment vs individual course purchases
- EX288 priority for development teams vs EX280 only for platform team
- RHCA certification track for senior engineers vs broad team EX280 coverage

## Training Resources

### Official Training Platform

- **Red Hat Learning Subscription (RHLS)** — $7,000/year per seat, access to ALL Red Hat courses, hands-on labs, and exam prep, most comprehensive but expensive option
- **Individual Courses** — DO280 (OpenShift Administration I, ~$3,000-4,000), DO380 (OpenShift Administration II), DO288 (OpenShift Development), each includes lab access

### Hands-On Labs

- Red Hat Interactive Labs (free, limited)
- RHLS lab environments (subscription)
- Red Hat Developer Sandbox (free OpenShift cluster, 30 days)

### Learning Paths by Role

- **Platform Admin:** RHCSA (EX200) → DO280 → EX280 → DO380 → EX380
- **Developer:** DO180 (Containers) → DO288 → EX288
- **Senior Architect:** RHCE (EX294) → EX280 → 5 specialist certs → RHCA

### Training Cost and Time Estimates

- ~80-120 hours per specialist exam
- Exam fee $400-500
- RHLS $7,000/yr
- Individual courses $3,000-4,000 each
- **Enterprise:** Red Hat partner program training requirements, volume RHLS agreements, Red Hat Training units

## Reference Links

- [Red Hat certification portal](https://www.redhat.com/en/services/certifications) -- RHCSA, RHCE, and OpenShift certification paths and exam registration
- [Red Hat Certified Specialist in OpenShift Administration (EX280)](https://www.redhat.com/en/services/training/ex280-red-hat-certified-specialist-in-openshift-administration-exam) -- OpenShift administration exam objectives and preparation
- [Red Hat training and certification](https://www.redhat.com/en/services/training-and-certification) -- instructor-led and self-paced OpenShift training courses

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/openshift/infrastructure.md` -- OpenShift infrastructure
- `providers/openshift/security.md` -- OpenShift security
- `providers/kubernetes/certifications.md` -- CNCF Kubernetes certifications
- `general/container-orchestration.md` -- container orchestration patterns
