# AWS Certifications and Training

## Scope

AWS certification paths, training resources, and partner program requirements. Covers Cloud Practitioner, Solutions Architect (Associate/Professional), SysOps Administrator, DevOps Engineer, and Specialty certifications (Security, Networking, Database, SAP, Machine Learning). Training platforms (AWS Skill Builder, AWS Training), partner program certification requirements (AWS Partner Network tiers).

## Checklist

- [Critical] Is AWS Solutions Architect - Associate (SAA-C03) identified as the baseline certification for architecture teams — covers VPC, EC2, S3, RDS, IAM, and core service design?
- [Critical] Is AWS Solutions Architect - Professional (SAP-C02) targeted for senior architects leading AWS design decisions — covers multi-account, hybrid, migration, cost optimization at scale?
- [Critical] Are AWS Partner Network (APN) certification requirements met — Select tier requires 2 foundational + 2 technical certs, Advanced requires 6 technical, Premier requires 20+ technical?
- [Recommended] Is AWS Cloud Practitioner (CLF-C02) used as the entry point for non-technical stakeholders and team members new to AWS?
- [Recommended] Is AWS Security Specialty (SCS-C02) required for teams designing or operating security-sensitive workloads — covers IAM, encryption, logging, incident response?
- [Recommended] Is AWS Networking Specialty (ANS-C01) evaluated for teams designing complex hybrid networking — covers VPC, Direct Connect, Transit Gateway, Route 53?
- [Recommended] Is AWS Database Specialty (DBS-C01) evaluated for teams managing database migrations or multi-engine database architectures?
- [Recommended] Is AWS Skill Builder (skillbuilder.aws) leveraged for free digital training, including exam readiness courses and practice exams?
- [Recommended] Is certification renewal tracked — all AWS certifications are valid for 3 years and require re-examination to renew?
- [Recommended] Is AWS SysOps Administrator - Associate required for operations teams managing day-to-day AWS infrastructure?
- [Optional] Is AWS DevOps Engineer - Professional targeted for teams implementing CI/CD and IaC on AWS?
- [Optional] Are AWS Specialty certifications (SAP, ML, Data Analytics) evaluated based on specific workload requirements?
- [Optional] Is AWS Jam or AWS GameDay used for team-based hands-on challenge exercises?

## Why This Matters

AWS certifications are the most widely recognized cloud credentials. APN partner tier status directly impacts deal registration benefits, co-selling opportunities, and access to AWS funding programs (Migration Acceleration Program, ISV Accelerate). Each APN tier has hard certification count requirements — losing certified staff can cause tier demotion. The 3-year validity period is more generous than other vendors but still requires renewal planning. AWS Skill Builder provides extensive free training but the sheer volume of services (200+) makes structured certification paths essential for team development.

## Common Decisions (ADR Triggers)

- Associate vs Professional certification targets based on team seniority
- Specialty certification selection based on engagement workload types
- AWS Skill Builder free tier vs subscription ($29/mo for enhanced labs)
- Certification count planning against APN tier requirements
- AWS Training and Certification vs third-party providers (A Cloud Guru, Stephane Maarek)

## Training Resources

### Official Training Platform

AWS Skill Builder (skillbuilder.aws) is the primary training platform. Free tier includes 800+ digital courses and exam readiness content. Subscription tier ($29/mo) adds enhanced labs, practice exams, and jam challenges. Team subscription is available at $449/user/year with usage reporting and admin controls.

AWS Classroom Training provides instructor-led virtual and in-person courses, typically $2,000-3,000 per 3-4 day course, delivered by AWS or authorized training partners (e.g., A Cloud Guru, Pluralsight).

### Hands-On Labs

- **AWS Free Tier** — 12 months of free-tier usage for hands-on practice with core services (EC2, S3, RDS, Lambda)
- **Skill Builder Sandbox Labs** — guided and open-ended labs included with subscription tier
- **AWS GameDay** — team-based competitive challenges simulating real-world operational scenarios
- **AWS Jam** — guided challenge events focused on specific service areas (security, serverless, containers)

### Learning Paths by Role

- **Architect:** Cloud Practitioner (CLF-C02) → Solutions Architect Associate (SAA-C03) → Solutions Architect Professional (SAP-C02)
- **Administrator:** Cloud Practitioner (CLF-C02) → SysOps Administrator Associate (SOA-C02)
- **Developer:** Cloud Practitioner (CLF-C02) → Developer Associate (DVA-C02) → DevOps Professional (DOP-C02)
- **Security:** Cloud Practitioner (CLF-C02) → Solutions Architect Associate (SAA-C03) → Security Specialty (SCS-C02)

### Training Cost and Time Estimates

| Level | Study Hours | Exam Fee |
|---|---|---|
| Cloud Practitioner | 40-60 hours | $100 |
| Associate certifications | 80-120 hours | $150 |
| Professional certifications | 150-200 hours | $300 |
| Specialty certifications | 150-200 hours | $300 |

Classroom training adds $2,000-3,000 per course. Skill Builder subscription adds $29/mo or $449/user/year for teams.

### Enterprise and Volume Options

- **AWS Training Subscriptions** — volume pricing for organizations, includes usage dashboards and team management
- **AWS Partner Training** — APN partners have specific training requirements per tier (Select, Advanced, Premier) with access to partner-exclusive training content
- **AWS re/Start** — free 12-week workforce training program for organizations building cloud teams

## Reference Links

- [AWS Certification](https://aws.amazon.com/certification/) -- certification paths, exam guides, and registration
- [AWS Skill Builder](https://aws.amazon.com/training/digital/) -- free and subscription-based digital training, labs, and exam prep

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/aws/vpc.md` -- AWS VPC networking
- `providers/aws/iam.md` -- AWS IAM
- `providers/aws/multi-account.md` -- AWS multi-account strategy
