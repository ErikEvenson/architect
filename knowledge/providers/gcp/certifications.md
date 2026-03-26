# Google Cloud Certifications and Training

## Scope

GCP certification paths, training resources, and partner program requirements. Covers Cloud Digital Leader, Associate Cloud Engineer, Professional Cloud Architect, Professional Cloud Security Engineer, Professional Cloud Network Engineer, Professional Cloud DevOps Engineer, Professional Cloud Database Engineer, Professional Data Engineer, Professional Machine Learning Engineer. Google Cloud Skills Boost training platform, partner certification requirements.

## Checklist

- [ ] [Critical] Is Professional Cloud Architect identified as the primary certification for architecture teams — covers solution design, security, compliance, network, deployment, and migration on GCP?
- [ ] [Critical] Is Associate Cloud Engineer required as the baseline for operations teams — covers deploying applications, monitoring, managing enterprise solutions on GCP?
- [ ] [Recommended] Is Professional Cloud Security Engineer required for teams designing GCP security controls — covers IAM, VPC Service Controls, Security Command Center, encryption, and data protection?
- [ ] [Recommended] Is Professional Cloud Network Engineer evaluated for teams designing complex networking — covers VPC, Cloud Interconnect, Cloud VPN, load balancing, Cloud DNS?
- [ ] [Recommended] Is Cloud Digital Leader used as the entry point for non-technical stakeholders — covers cloud concepts, GCP products, and business value?
- [ ] [Recommended] Is Google Cloud Skills Boost (cloudskillsboost.google) leveraged for hands-on labs, quests, and learning paths — many labs are free, full access requires subscription ($29/mo)?
- [ ] [Recommended] Is certification validity tracked — all GCP certifications are valid for 2 years and require re-examination to renew?
- [ ] [Recommended] Are Google Cloud Partner Advantage program certification requirements met — specializations require minimum certified individuals in the relevant certification track?
- [ ] [Optional] Is Professional Data Engineer or Professional Machine Learning Engineer evaluated for data-intensive or ML workloads?
- [ ] [Optional] Is Professional Cloud DevOps Engineer targeted for teams implementing CI/CD and SRE practices on GCP?
- [ ] [Optional] Is Professional Cloud Database Engineer evaluated for teams managing Cloud SQL, Spanner, Bigtable, or Firestore?
- [ ] [Optional] Are Google Cloud Labs and Qwiklabs challenges used for hands-on team practice?

## Why This Matters

GCP certifications are widely respected and carry weight in the industry, particularly the Professional Cloud Architect which has been recognized as one of the highest-paying IT certifications globally. Google's partner program (Cloud Partner Advantage) requires specialization credentials that map directly to certification counts — losing certified staff can impact partner tier and access to co-sell programs, customer credits, and technical support escalation. The 2-year validity is standard but Google does not offer free renewal assessments like Microsoft — re-examination is required.

## Common Decisions (ADR Triggers)

- Associate Cloud Engineer vs Professional Cloud Architect first certification based on role
- Professional specialty certification selection based on engagement workload (security, networking, data, ML)
- Google Cloud Skills Boost free labs vs subscription for full access
- Certification count planning against Partner Advantage specialization requirements
- GCP certification priority vs other cloud vendors for multi-cloud teams

## Training Resources

### Official Training Platform

**Google Cloud Skills Boost** (cloudskillsboost.google) is the primary training platform. Free tier includes limited labs per month and select learning paths. Subscription tier ($29/mo or $299/yr) provides unlimited hands-on labs, learning paths, and skill badges.

**Google Cloud Training** offers instructor-led courses at $800-2,400 per 1-3 day course, delivered by Google or authorized training partners. Courses are shorter and more focused than AWS or Azure equivalents.

### Hands-On Labs

- **Cloud Skills Boost Labs** — guided Qwiklabs with real GCP project environments, available on free tier (limited) or subscription (unlimited)
- **Google Cloud Free Trial** — $300 credit for 90 days for hands-on practice with any GCP service
- **Sandbox Projects** — temporary GCP projects provisioned within Cloud Skills Boost for lab exercises
- **Skill Badges** — completion-based credentials earned by finishing lab quests, demonstrating practical competency

### Learning Paths by Role

- **Architect:** Cloud Digital Leader → Associate Cloud Engineer → Professional Cloud Architect
- **Administrator:** Cloud Digital Leader → Associate Cloud Engineer
- **Security:** Associate Cloud Engineer → Professional Cloud Security Engineer
- **Data:** Associate Cloud Engineer → Professional Data Engineer
- **DevOps:** Associate Cloud Engineer → Professional Cloud DevOps Engineer
- **ML/AI:** Associate Cloud Engineer → Professional Machine Learning Engineer

### Training Cost and Time Estimates

| Level | Study Hours | Exam Fee |
|---|---|---|
| Cloud Digital Leader | 30-50 hours | $99 |
| Associate Cloud Engineer | 60-80 hours | $200 |
| Professional certifications | 80-120 hours | $200 |

Instructor-led training adds $800-2,400 per course. Cloud Skills Boost subscription adds $29/mo or $299/yr. All certifications are valid for 2 years with full re-examination required for renewal.

### Enterprise and Volume Options

- **Google Cloud Partner Advantage** — training requirements vary by partner specialization; certified individuals count toward specialization thresholds
- **Partner Training Programs** — Google Cloud consulting and service partners have access to partner-exclusive training and certification vouchers
- **Google Cloud Skills Boost for Teams** — enterprise subscription with team management, usage tracking, and custom learning paths
- **Google Cloud Authorized Training Partners** — deliver official Google Cloud curriculum with certified instructors

## Reference Links

- [Google Cloud Certifications](https://cloud.google.com/learn/certification) -- certification paths, exam guides, and registration
- [Google Cloud Skills Boost](https://www.cloudskillsboost.google/) -- hands-on labs, learning paths, and quests for exam preparation
- [Professional Cloud Architect certification](https://cloud.google.com/learn/certification/cloud-architect) -- exam objectives, study guide, and sample questions
- [Google Cloud Partner Advantage](https://cloud.google.com/partners) -- partner program tiers, specialization requirements, and benefits

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/gcp/compute.md` -- GCP compute
- `providers/gcp/networking.md` -- GCP networking
- `providers/gcp/security.md` -- GCP security
