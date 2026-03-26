# Microsoft Azure Certifications and Training

## Scope

Microsoft Azure certification paths, training resources, and partner program requirements. Covers fundamentals (AZ-900), administrator (AZ-104), architect (AZ-305), security (AZ-500, SC-series), networking (AZ-700), hybrid (AZ-800/801 for Azure Stack HCI), and specialty certifications. Microsoft Partner Network certification requirements, Microsoft Learn training platform, Enterprise Skills Initiative (ESI). Relevance to Azure and NC2-on-Azure engagements.

## Checklist

- [Critical] Is AZ-305 (Azure Solutions Architect Expert) identified as the primary certification for architecture teams — requires passing AZ-104 as prerequisite, covers identity, governance, data, networking, and BCDR design?
- [Critical] Is AZ-104 (Azure Administrator Associate) required as the baseline for all engineers operating Azure infrastructure — covers subscriptions, VNets, VMs, storage, identity, monitoring?
- [Critical] For NC2 on Azure engagements, do engineers hold both Azure certifications (minimum AZ-104) and Nutanix NCP-MCI to cover the hybrid bare-metal + cloud stack?
- [Critical] Are Microsoft Cloud Partner Program certification requirements met — Solutions Partner designations require a minimum number of certified individuals across specific exams?
- [Recommended] Is AZ-500 (Azure Security Engineer Associate) required for teams designing security controls — covers identity, platform protection, data security, security operations?
- [Recommended] Is AZ-700 (Azure Network Engineer Associate) evaluated for teams designing complex hybrid networking — covers VNet, ExpressRoute, VPN, load balancing, Azure Firewall?
- [Recommended] Are AZ-800/AZ-801 (Windows Server Hybrid Administrator Associate) evaluated for teams working with Azure Stack HCI and hybrid Windows Server — directly relevant to Tier 0 architecture?
- [Recommended] Is Microsoft Learn (learn.microsoft.com) leveraged for free self-paced training modules, learning paths, and sandboxed labs aligned to each certification?
- [Recommended] Is Enterprise Skills Initiative (ESI) funding available through the Microsoft relationship — provides vouchers for certification exams and instructor-led training?
- [Recommended] Is certification renewal tracked — Microsoft certifications are valid for 1 year and require passing a free online renewal assessment on Microsoft Learn?
- [Optional] Are SC-series security certifications (SC-100, SC-200, SC-300, SC-400) evaluated for teams with Defender, Sentinel, Entra ID, or information protection responsibilities?
- [Optional] Is AZ-140 (Azure Virtual Desktop Specialty) evaluated for VDI migration engagements where AVD is a target option?
- [Optional] Is DP-300 (Azure Database Administrator Associate) required for teams managing SQL migrations to Azure SQL or Managed Instance?

## Why This Matters

Microsoft's 1-year certification validity is the most aggressive renewal cycle among major cloud vendors — certifications lapse quickly without active renewal planning. The free online renewal assessment is convenient but must be completed before expiry. For NC2 on Azure engagements, the intersection of Azure and Nutanix skills is the critical gap — engineers comfortable with Azure VNets, ExpressRoute, and subscriptions may have no Nutanix experience, and vice versa. ESI funding through Microsoft enterprise agreements can significantly reduce certification costs. The AZ-800/801 track is often overlooked but directly relevant when Azure Stack HCI is in scope for Tier 0 workloads. Partner designations (Solutions Partner for Infrastructure, Security, etc.) have hard certification requirements that affect Microsoft co-sell eligibility and incentive program access.

## Common Decisions (ADR Triggers)

- AZ-104 → AZ-305 vs AZ-104 → AZ-500 certification path based on role (architect vs security)
- AZ-700 priority for hybrid networking engagements (ExpressRoute, VPN Gateway)
- AZ-800/801 investment for Azure Stack HCI / hybrid Windows Server scope
- ESI funding utilization for team certification programs
- Dual Azure + Nutanix certification strategy for NC2 engagements
- 1-year renewal cadence planning (most aggressive among vendors)

## Training Resources

### Official Training Platform

**Microsoft Learn** (learn.microsoft.com) is completely free and includes self-paced modules, learning paths, sandboxed Azure environments, and exam readiness videos. All content is aligned to specific certification exams with hands-on exercises built in.

**Microsoft Official Courseware (MOC)** provides instructor-led training at $2,000-3,500 per 4-5 day course, delivered by Microsoft Certified Trainers (MCTs) at Microsoft Learning Partners.

**Applied Skills** are hands-on assessments (not exams) that validate specific scenario competency — free through Microsoft Learn. Useful for validating focused skills without full certification commitment.

### Hands-On Labs

- **Microsoft Learn Sandbox** — free, time-limited Azure environments embedded directly in learning modules (no Azure subscription required)
- **Azure Free Account** — $200 credit for 30 days plus 12 months of free-tier services for hands-on practice
- **Applied Skills Assessments** — scenario-based labs that test practical ability in specific areas (e.g., deploy a container app, configure secure access)

### Learning Paths by Role

- **Architect:** AZ-900 (Fundamentals) → AZ-104 (Administrator) → AZ-305 (Solutions Architect Expert)
- **Administrator:** AZ-900 (Fundamentals) → AZ-104 (Azure Administrator Associate)
- **Security:** AZ-900 (Fundamentals) → AZ-500 (Security Engineer) → SC-100 (Cybersecurity Architect Expert)
- **Network:** AZ-900 (Fundamentals) → AZ-104 (Administrator) → AZ-700 (Network Engineer Associate)
- **Hybrid:** AZ-900 (Fundamentals) → AZ-800 + AZ-801 (Windows Server Hybrid Administrator Associate)

### Training Cost and Time Estimates

| Certification | Study Hours | Exam Fee | Renewal |
|---|---|---|---|
| Fundamentals (AZ-900) | 20-40 hours | $165 | Does not expire |
| Associate certifications | 60-100 hours | $165 | Free annual renewal on Microsoft Learn |
| Expert certifications | 100-150 hours | $165 | Free annual renewal on Microsoft Learn |

Instructor-led training adds $2,000-3,500 per course. Microsoft Learn is entirely free including labs.

### Enterprise and Volume Options

- **Enterprise Skills Initiative (ESI)** — free exam vouchers and instructor-led training available to organizations with Microsoft Enterprise Agreements (EA); the most cost-effective path for large teams
- **Microsoft Learning Partner Network** — authorized training providers offering scheduled and private classes
- **Volume Exam Vouchers** — bulk exam voucher purchases available through Microsoft or authorized resellers
- **Microsoft Action Pack** — partner benefit includes training and certification resources

## Reference Links

- [Microsoft Learn training platform](https://learn.microsoft.com/en-us/training/) -- free self-paced modules, learning paths, and sandboxed labs for all Azure certifications
- [Microsoft Certifications overview](https://learn.microsoft.com/en-us/credentials/) -- certification paths, exam requirements, and renewal process
- [AZ-305 Azure Solutions Architect Expert](https://learn.microsoft.com/en-us/credentials/certifications/azure-solutions-architect/) -- exam objectives, prerequisites, and study resources
- [AZ-104 Azure Administrator Associate](https://learn.microsoft.com/en-us/credentials/certifications/azure-administrator/) -- exam objectives and study resources

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/azure/compute.md` -- Azure compute
- `providers/azure/networking.md` -- Azure networking
- `providers/azure/azure-local.md` -- Azure Local (Stack HCI)
- `providers/nutanix/certifications.md` -- Nutanix certifications (dual-cert strategy for NC2)
