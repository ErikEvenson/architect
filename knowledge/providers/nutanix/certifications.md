# Nutanix Certifications and Training

## Scope

Nutanix certification paths, training resources, and partner program requirements. Covers NCP-MCI (Multicloud Infrastructure), NCP-DB (Database), NCP-DS (Data Services/Objects/Files), NCP-MCA (Multicloud Automation), NCM (Certified Master), and NPX (Platform Expert). Prerequisites, exam structure, renewal cadence, relevance to NC2 on Azure engagements.

## Checklist

- [Critical] Is NCP-MCI 6.5 (or current version) identified as the baseline certification for all engineers working on Nutanix infrastructure — covering AHV, Prism, storage, networking, and data protection?
- [Critical] For NC2 on Azure engagements, do engineers hold both NCP-MCI and Azure certifications (minimum AZ-104 or AZ-305) to cover the hybrid stack?
- [Recommended] Is the NCP-MCI v6.5 exam scope understood — 75 questions, 120 minutes, passing score ~3000/6000, covers AOS, AHV, Prism Central, Flow, Leap, LCM?
- [Recommended] Is NCP-DB certification required for teams managing Nutanix Database Service (NDB/Era) — covers database provisioning, patching, cloning, and time machine?
- [Recommended] Is certification renewal tracked — NCP certifications are valid for 2 years and require passing the current version exam to renew?
- [Recommended] Is Nutanix University (nu.nutanix.com) leveraged for free self-paced training courses aligned to each NCP track?
- [Recommended] Are Nutanix Test Drive and lab environments used for hands-on certification preparation?
- [Optional] Is NCM (Nutanix Certified Master) targeted for senior architects requiring deep platform expertise — requires passing NCP-MCI plus the NCM exam?
- [Optional] Is NPX (Nutanix Platform Expert) identified for principal-level engineers — the highest Nutanix certification, invitation-based?
- [Recommended] Are Nutanix partner program (ATP/AMP) certification requirements met — Authorized Technology Partner and Authorized Managed Services Partner tiers require minimum certified headcount?
- [Optional] Is NCP-MCA certification evaluated for teams implementing NCM Self-Service (formerly Calm) automation and IaC on Nutanix?

## Why This Matters

Nutanix partner tiers directly impact deal registration, pricing, and support access. ATP status requires minimum NCP-certified engineers. For NC2 on Azure, the intersection of Nutanix and Azure skills is rare — certification planning must address both stacks. NCP-MCI is the minimum for anyone touching Nutanix infrastructure; without it, common mistakes include misconfigured RF settings, improper Prism Central sizing, and missed LCM update procedures.

## Common Decisions (ADR Triggers)

- NCP-MCI vs NCP-DB vs NCP-DS prioritization based on engagement scope
- NCM/NPX investment for senior staff vs broad NCP coverage
- Nutanix University self-paced vs instructor-led training
- Dual-certification strategy for NC2 on Azure (Nutanix + Azure certs)

## See Also

- general/certification-training.md
- providers/nutanix/infrastructure.md
- providers/nutanix/nc2-azure.md
- providers/azure/certifications.md
