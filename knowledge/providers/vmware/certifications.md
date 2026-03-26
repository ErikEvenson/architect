# VMware / Broadcom Certifications and Training

## Scope

VMware certification paths under Broadcom ownership, training availability, and relevance during migration engagements. Covers VCP-DCV (Data Center Virtualization), VCAP-DCV (Design and Deploy), VCF certifications, NSX certifications. Post-Broadcom changes to the certification program, exam availability, training platform transition, and certification relevance for teams migrating away from VMware.

## Checklist

- [Critical] Is VCP-DCV (vSphere) identified as the baseline VMware certification — required for understanding source environments during migration engagements?
- [Critical] Has the Broadcom certification program transition been assessed — VMware certifications transitioned to Broadcom's certification platform, and some exams have been updated or retired?
- [Critical] For migration-away engagements, are source-platform VMware certifications still valued for understanding the environment being migrated (vSphere, vSAN, NSX configuration)?
- [Recommended] Is VCP-DCV 2024 (or current version) exam scope understood — covers vSphere 8.x, vCenter, vSAN, ESXi configuration, storage, networking, and security?
- [Recommended] Is VCAP-DCV certification targeted for senior architects — covers advanced design (VCAP-DCV Design) and advanced deployment (VCAP-DCV Deploy)?
- [Recommended] Is VCF certification evaluated for teams working with VMware Cloud Foundation environments — covers SDDC Manager, vSAN, NSX integration?
- [Recommended] Is VMware NSX certification (VCP-NV) required for teams managing NSX environments — critical for understanding microsegmentation policies during migration?
- [Recommended] Are Broadcom Learning (formerly VMware Learning) training resources evaluated — on-demand courses, Hands-on Labs (HOL), and instructor-led training?
- [Recommended] Is certification renewal tracked — VCP certifications are valid for 2 years; VCAP and above valid for 3 years?
- [Optional] Are VMware Hands-on Labs (HOL) used for free lab-based practice — available at labs.hol.vmware.com?
- [Optional] Is the ROI of new VMware certifications evaluated for teams migrating away from VMware — certifications in the target platform (Nutanix, Azure) may be higher priority?

## Why This Matters

Post-Broadcom acquisition, the VMware certification landscape is in flux. Training platforms and exam content are being consolidated. For migration engagements, VMware source-platform knowledge remains critical — understanding vSphere, vSAN, and NSX configuration is essential for accurate workload assessment and migration planning. However, investing heavily in new VMware certifications for teams migrating away from VMware may not be the best use of training budget. The decision is whether to maintain VMware cert currency for migration competency or redirect training investment to the target platform.

## Common Decisions (ADR Triggers)

- VMware cert maintenance vs redirect to target platform certs during migration
- VCP-DCV vs VCF certification for teams working with VCF environments
- Broadcom Learning vs third-party training providers
- NSX certification priority for environments with microsegmentation policies

## Training Resources

### Official Training Platform

- **Broadcom Learning (formerly VMware Learning)** — on-demand courses and learning paths, transitioned from VMware's mylearn portal to Broadcom's platform
- **Post-Broadcom Changes:** training platform consolidation is ongoing; some courses temporarily unavailable during migration; verify current offerings before planning

### Hands-On Labs

- **VMware Hands-on Labs (HOL)** — free browser-based lab environments at labs.hol.vmware.com, pre-built scenarios for vSphere, NSX, VCF, Horizon, and more — among the best free lab resources in the industry
- HOL availability may change under Broadcom ownership; verify access before relying on specific labs

### Learning Paths by Role

- **Infrastructure Architect:** VCP-DCV → VCAP-DCV Design → VCAP-DCV Deploy → VCDX
- **Network Engineer:** VCP-NV (NSX) → VCAP-NV
- **Cloud Admin:** VCP-DCV → VCF Certification
- **Migration Specialist:** VCP-DCV + target platform cert (NCP-MCI, AZ-104, CKA)

### Training Cost and Time Estimates

- ~80-120 hours of study per VCP certification
- Exam fees: $250 (VCP), $400+ (VCAP)
- VMware Hands-on Labs: free
- Instructor-Led Training (ILT): 3-5 day courses, $3,000-5,000 per course, delivered by VMware Authorized Training Centers (VATCs)
- Note: significant reduction in available VATCs post-Broadcom acquisition

### Enterprise/Volume Options

- Broadcom partner program certification requirements dictate minimum certified headcount per tier
- Volume training agreements available through authorized training partners
- Partner enablement resources transitioning under Broadcom's partner program structure

## Reference Links

- [Broadcom VMware Certification Portal](https://www.broadcom.com/support/education/vmware/certification) -- current VMware certification paths, exam registration, and recertification under Broadcom
- [Broadcom Learning (VMware Training)](https://www.broadcom.com/support/education/vmware) -- on-demand courses, Hands-on Labs, and instructor-led training
- [VMware Hands-on Labs](https://labs.hol.vmware.com/) -- free browser-based lab environments for VMware product practice

## See Also

- general/certification-training.md
- providers/vmware/infrastructure.md
- providers/vmware/licensing.md
- patterns/hypervisor-migration.md
