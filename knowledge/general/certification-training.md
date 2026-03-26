# Certification and Training Strategy

## Scope

This file covers **cross-vendor certification planning and training strategy** for architecture engagements: identifying certification requirements, skill gap analysis, training budget allocation, certification specifications in RFPs and managed services contracts, renewal cycle management, and mapping certifications to architecture roles. Does not cover individual exam preparation tactics or vendor-specific certification details -- those are addressed in provider-specific knowledge files (e.g., `nutanix/`, `vmware/`, `aws/`, `azure/`, `gcp/`).

## Checklist

### Engagement Requirements

- [ ] **[Critical]** Are certification requirements identified for the engagement scope -- which vendor certs are required vs recommended for the team delivering the work?
- [ ] **[Critical]** Is a skill gap analysis completed mapping current team certifications against engagement requirements?
- [ ] **[Critical]** Are certification requirements specified in managed services contracts -- minimum cert levels for engineers with customer-facing access?
- [ ] **[Critical]** Are subcontractor and third-party certifications verified before granting access to customer environments? (Vendor partner agreements often mandate this.)

### Training and Preparation

- [ ] **[Recommended]** Is a training budget allocated for certification preparation (exam fees, training courses, lab environments)?
- [ ] **[Recommended]** Is vendor-provided free training evaluated before purchasing third-party courses? (Most vendors offer free digital training -- AWS Skill Builder, Microsoft Learn, Google Cloud Skills Boost, Nutanix University.)
- [ ] **[Recommended]** Are hands-on lab environments available for certification preparation (vendor sandboxes, trial accounts, lab subscriptions)?
- [ ] **[Recommended]** Is training time allocation accounted for in project schedules? (Certification preparation requires 40-80 hours per exam depending on difficulty level; this must not compete with delivery milestones.)
- [ ] **[Optional]** Is a certification incentive program in place (exam fee reimbursement, bonuses for achieving certs)?

### Certification Management

- [ ] **[Recommended]** Are certification renewal timelines tracked -- most vendor certs expire every 2-3 years and require continuing education or re-examination?
- [ ] **[Recommended]** Is a certification matrix maintained mapping required certs to architecture roles (designer, operator, specialist, administrator)?
- [ ] **[Recommended]** Are partner program certification thresholds documented -- many vendor partner tiers require minimum numbers of certified staff?
- [ ] **[Optional]** Are cross-certification equivalencies documented for multi-cloud teams? (e.g., CKA covers Kubernetes fundamentals applicable across all cloud providers)

### Multi-Vendor Engagements

- [ ] **[Recommended]** Is certification prioritization defined for multi-vendor or hybrid engagements -- which vendor certs take precedence based on workload distribution and contract requirements?
- [ ] **[Optional]** Is a vendor-neutral certification baseline established for the team (e.g., CompTIA, ITIL, TOGAF, CKA) to complement vendor-specific certifications?

## Why This Matters

Certifications validate hands-on competency and are increasingly used by customers as a proxy for team capability during vendor selection. Partner program tiers -- which directly affect deal registration, discount levels, and access to vendor engineering support -- require minimum certified headcount. A lapse in renewals can drop an organization from a higher partner tier, reducing margins on every deal in the pipeline. Managed services contracts frequently specify minimum certification levels for engineers with access to production environments; failing to meet these requirements is a contractual breach, not just an operational gap.

Certification gaps discovered mid-engagement cause staffing delays that cascade into missed milestones. An architect who identifies a VMware-to-Nutanix migration but whose team holds no Nutanix certifications faces a 2-4 month lead time for training and examination before qualified engineers are available. Addressing certification planning during the engagement scoping phase -- not after contract signature -- prevents these delays and ensures the delivery team is qualified for the architecture they are building.

## Common Decisions (ADR Triggers)

- **Vendor-specific vs vendor-neutral certifications** -- whether to invest in platform-specific certs (e.g., AWS Solutions Architect, Nutanix NCP) vs vendor-neutral alternatives (e.g., CKA for Kubernetes, TOGAF for architecture); driven by customer requirements, partner program needs, and team versatility goals
- **Certification investment strategy** -- broad team coverage (every engineer holds foundational certs) vs deep specialization (a few engineers hold expert/professional-level certs); depends on team size, engagement complexity, and partner tier requirements
- **Training delivery model** -- self-paced digital learning vs instructor-led training vs intensive bootcamp format; trade-offs between cost, schedule impact, and certification pass rates
- **Certification requirements in contracts** -- whether managed services contracts specify certifications as hard requirements (must have before access is granted) vs preferred qualifications (best-effort staffing); contractual language has compliance and liability implications
- **Multi-vendor certification prioritization** -- for hybrid and multi-cloud engagements, which vendor certifications to pursue first based on workload volume, contract terms, and partner program tier targets

## Training Planning Framework

### Training Budget Template

- **Exam fees:** $150-500 per certification depending on vendor
- **Training courses:** $0 (free self-paced) to $5,000 (instructor-led per course) to $7,000/yr (all-access subscriptions)
- **Lab environments:** $0 (free tiers/trials) to $29-50/mo (subscription labs)
- **Time cost:** 40-200 hours per certification (opportunity cost of engineer time)
- **Rule of thumb:** budget $1,500-3,000 per certification including training and exam

### Time-to-Competency Estimates

| Vendor | Entry Cert | Study Hours | Experienced Cert | Study Hours |
|--------|-----------|-------------|-----------------|-------------|
| AWS | Cloud Practitioner | 40-60 hrs | SA Professional | 150-200 hrs |
| Azure | AZ-900 | 20-40 hrs | AZ-305 | 100-150 hrs |
| GCP | Cloud Digital Leader | 30-50 hrs | PCA | 80-120 hrs |
| Kubernetes | KCNA | 30-50 hrs | CKA | 60-80 hrs |
| Nutanix | NCA | 30-50 hrs | NCP-MCI | 60-100 hrs |
| HashiCorp | Terraform Associate | 40-60 hrs | Vault Professional | 80-120 hrs |

### Training ROI Metrics

- **Partner tier maintenance** — certification counts directly affect tier status and deal economics
- **Reduced time-to-delivery** — certified teams ramp faster on engagements
- **Risk reduction** — certified engineers make fewer critical configuration mistakes
- **Staff retention** — certification programs are a top-cited reason for staying at an employer

## See Also

- `general/managed-services-scoping.md` -- Contract structure, SLA definition, and operational staffing
- `general/governance.md` -- Organizational governance, Cloud Center of Excellence, and enablement programs
