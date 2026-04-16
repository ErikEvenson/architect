# Cloud Workload Hardening

## Scope

This file covers **security hardening standards, benchmarks, and hardened images for cloud-hosted workloads** across AWS, Azure, and GCP. It addresses CIS Benchmarks, cloud-native hardening services, pre-hardened marketplace images, golden image pipelines, and OS-level hardening for IaaS workloads (EC2, Azure VMs, Compute Engine). It does not cover STIG-specific workflows (see `general/stig-hardening.md`), general security architecture (see `general/security.md`), or container/Kubernetes hardening (see `providers/kubernetes/security.md`).

## Checklist

- [ ] **[Critical]** Which hardening standard is required for each workload? (CIS Benchmarks for commercial/enterprise — Level 1 for broad compatibility, Level 2 for defense-in-depth; DISA STIGs for DoD/federal — CAT I/II/III severity; vendor-specific guides from Red Hat, Canonical, Microsoft for OS-specific hardening; many organizations adopt CIS as the baseline and layer STIG requirements on top for regulated workloads)
- [ ] **[Critical]** Are pre-hardened marketplace images used for initial deployment, or is hardening applied post-deployment? (CIS publishes hardened images for AWS, Azure, and GCP — available for Windows Server 2022/2025, Amazon Linux 2023, RHEL 9, Ubuntu 22.04/24.04, SUSE; AWS also provides STIG-hardened AMIs with 160+ settings pre-applied; marketplace images carry per-hour cost but eliminate manual hardening effort; post-deployment hardening with Ansible/Chef/Puppet gives more control but delays time-to-compliant)
- [ ] **[Critical]** Is a golden image pipeline established for building and maintaining hardened images? (use Packer, EC2 Image Builder, Azure Image Builder, or GCP VM Image Import to bake CIS/STIG settings into base images; pipeline should layer: base OS image, hardening settings, monitoring agents, patching — then output versioned AMI/managed image/custom image; images must be rebuilt monthly minimum to incorporate OS patches; without a pipeline, hardened images become stale and drift from compliance within weeks)
- [ ] **[Critical]** Is instance metadata service hardened on all cloud VMs? (AWS: enforce IMDSv2 with hop limit of 1 to prevent SSRF-based credential theft — IMDSv1 is the most common EC2 attack vector; Azure: Instance Metadata Service requires Managed Identity with least-privilege role; GCP: use VM metadata server with service account scope restrictions; this is a frequently missed hardening step that leads to credential compromise)
- [ ] **[Critical]** Are cloud-native security posture management tools enabled? (AWS Security Hub with CIS AWS Foundations Benchmark and AWS Foundational Security Best Practices; Azure Defender for Cloud with regulatory compliance assessments; GCP Security Command Center with Security Health Analytics; these provide continuous compliance monitoring against CIS benchmarks at the account/subscription/project level, not just the OS level)
- [ ] **[Recommended]** Is automated compliance scanning configured to detect drift from the hardened baseline? (AWS Inspector for CVE and CIS scanning on EC2; Azure Policy guest configuration for in-VM compliance; GCP VM Manager OS policy compliance; OpenSCAP or commercial scanners like Nessus/Qualys for OS-level CIS/STIG benchmark scanning; schedule scans weekly minimum and alert on drift — hardened images lose compliance as configurations change during operations)
- [ ] **[Recommended]** Are CIS Benchmark profiles mapped to the organization's risk tolerance and operational requirements? (Level 1 profiles are designed to be applied broadly without breaking functionality — suitable for most workloads; Level 2 profiles add defense-in-depth controls that may impact performance or usability — require testing; some Level 1 items may still break specific applications, e.g., disabling unused filesystems can affect container workloads, password complexity rules can lock out service accounts)
- [ ] **[Recommended]** Is host-based intrusion detection or file integrity monitoring deployed on hardened instances? (AIDE or OSSEC for Linux file integrity monitoring; Sysmon for Windows event enrichment; AWS GuardDuty for runtime threat detection on EC2; Azure Defender for Servers for behavioral analytics; GCP Security Command Center Premium for VM threat detection; these detect post-deployment tampering that compliance scanning alone misses)
- [ ] **[Recommended]** Are hardening exceptions documented with compensating controls? (not every CIS or STIG recommendation is applicable to every workload — e.g., disabling IPv6 may break cloud-native services, enforcing FIPS mode may break vendor applications; each exception needs a documented business justification, compensating control, risk acceptance, and review date; store exception records alongside compliance scan results for audit evidence)
- [ ] **[Recommended]** Is the hardened image tested against the target application before production deployment? (hardening settings can break application functionality — TLS cipher restrictions may prevent legacy client connections, filesystem permission changes may break application writes, disabled services may remove required dependencies; test the application on a hardened image in a non-production environment and document any required exceptions before promoting to production)
- [ ] **[Optional]** Are cloud-provider-specific hardening features enabled beyond OS-level benchmarks? (AWS: EBS default encryption, S3 Block Public Access, VPC endpoint policies, Nitro Enclaves for sensitive processing; Azure: Confidential Computing, Trusted Launch with vTPM and Secure Boot, disk encryption with platform-managed or customer-managed keys; GCP: Shielded VMs with vTPM and Secure Boot, Confidential VMs, Organization Policy constraints; these complement OS hardening with infrastructure-level protections)
- [ ] **[Optional]** Is there a process for adopting new benchmark versions when CIS or DISA publishes updates? (CIS publishes benchmark updates 1-2 times per year per OS; new versions may add, remove, or modify recommendations; establish a review process: download new benchmark, diff against current baseline, test changes in non-production, update golden image pipeline, rescan fleet; without this process, the organization's hardening baseline becomes outdated while auditors reference the latest version)

## Why This Matters

Cloud workload hardening is the practice of reducing the attack surface of compute instances by applying security configuration baselines that disable unnecessary services, restrict permissions, enforce encryption, and configure audit logging. Default cloud VM images — even those from major providers — ship with configurations optimized for broad compatibility, not security. A default Amazon Linux 2023 AMI, Windows Server 2025 image, or Ubuntu image includes enabled services, open ports, and permissive settings that an attacker can exploit after gaining initial access.

The two dominant hardening standards — CIS Benchmarks and DISA STIGs — address this gap with hundreds of specific configuration checks per OS. CIS Benchmarks are the most widely adopted in commercial environments because they are well-documented, freely available (the benchmarks themselves, not the hardened images), organized into practical Level 1 and more restrictive Level 2 profiles, and supported by automated scanning tools. DISA STIGs are mandatory for DoD environments and increasingly adopted by federal civilian agencies and defense contractors; they are generally more restrictive than CIS Level 2 and include additional documentation requirements (POA&Ms, .ckl checklists).

The most common hardening failure is treating it as a one-time activity. Organizations harden an image, deploy it, and then watch compliance decay as patches are applied, configurations are changed for troubleshooting, software is installed, and drift accumulates. Within 30-60 days of deployment, a hardened instance can have dozens of new findings. Continuous compliance scanning and automated remediation (or regular image replacement from the golden image pipeline) are essential to maintaining the hardened state. The second most common failure is applying hardening without testing: CIS and STIG recommendations can break applications, disable management interfaces, or cause boot failures when applied blindly.

Pre-hardened marketplace images from CIS and third-party vendors (Nemu, SUSE, others) significantly reduce the effort to achieve initial compliance, but they are not a substitute for understanding the benchmark — organizations must still evaluate which controls apply, document exceptions, and maintain compliance over the instance lifecycle.

## Common Decisions (ADR Triggers)

- **CIS Level 1 vs Level 2 vs STIG baseline** — Level 1 is suitable for most commercial workloads with minimal application impact; Level 2 adds defense-in-depth but requires thorough testing; STIG is required for DoD/federal and is the most restrictive; some organizations apply CIS Level 1 broadly and STIG to specific high-sensitivity workloads; the choice drives testing effort, exception volume, and operational complexity
- **Pre-hardened marketplace image vs golden image pipeline** — marketplace images (CIS Hardened Images, AWS STIG AMIs, Nemu) are fastest to deploy and include monthly patching, but carry per-hour marketplace cost and limit customization; golden image pipelines (Packer, EC2 Image Builder, Azure Image Builder) give full control over hardening settings, agent installation, and application layers, but require engineering investment to build and maintain; most mature organizations use a pipeline that starts from a marketplace hardened image and layers application-specific configuration
- **In-place hardening remediation vs immutable image replacement** — in-place remediation (Ansible STIG roles, Chef InSpec, PowerShell DSC) applies hardening to running instances and can remediate drift, but risks configuration conflicts and requires change windows; immutable replacement tears down non-compliant instances and replaces them from the current golden image, ensuring consistency but requiring stateless application architecture and robust deployment automation
- **Cloud-native vs third-party compliance scanning** — cloud-native tools (AWS Security Hub + Inspector, Azure Defender for Cloud, GCP Security Command Center) integrate with provider IAM and are easiest to deploy, but may lag behind latest benchmark versions and have limited cross-cloud visibility; third-party tools (Qualys, Nessus/Tenable, Rapid7, Wiz, Prisma Cloud) provide cross-cloud coverage, deeper OS-level scanning, and broader vulnerability management, but add licensing cost and agent deployment overhead
- **Windows Server edition for hardened workloads** — Windows Server 2025 hardened images are now available from CIS (Level 1 and Level 2) and STIG providers (AWS STIG AMIs, Nemu) on AWS and Azure; Windows Server 2022 remains more widely available with mature benchmarks (CIS v2.0.0+, STIG V2R2+); organizations should evaluate whether new deployments should target 2025 for its longer support lifecycle or 2022 for benchmark maturity and broader ecosystem testing
- **IMDSv2 enforcement scope** — enforce IMDSv2 on all new instances via launch template or SCP (recommended), or allow IMDSv1 fallback for legacy applications that have not been updated; IMDSv1 is the most exploited EC2 attack vector via SSRF; the tradeoff is between security posture and application compatibility — applications using older AWS SDKs may need updates to support IMDSv2

## Reference Architectures

### CIS Benchmark Availability by OS and Cloud

```
+---------------------------+-----+-------+-----+--------+--------+
| Operating System          | CIS | AWS   | Azure| GCP   | STIG   |
|                           | Bench| Image | Image| Image | Avail  |
+---------------------------+-----+-------+-----+--------+--------+
| Amazon Linux 2023         | Yes | L1/L2 | N/A  | N/A   | Yes    |
| RHEL 9                    | Yes | L1/L2 | L1   | L1    | Yes    |
| Ubuntu 22.04 LTS          | Yes | L1/L2 | L1   | L1    | Yes    |
| Ubuntu 24.04 LTS          | Yes | L1/L2 | L1   | L1    | Yes    |
| SUSE Linux Enterprise 15  | Yes | L1/L2 | L1   | L1    | Yes    |
| Windows Server 2022       | Yes | L1/L2 | L1   | L1    | Yes    |
| Windows Server 2025       | Yes | L1/L2 | L1   | TBD   | Yes    |
| Debian 12                 | Yes | L1/L2 | L1   | L1    | No     |
+---------------------------+-----+-------+-----+--------+--------+

Notes:
- CIS Bench = CIS Benchmark document published (free PDF)
- AWS/Azure/GCP Image = CIS Hardened Image available in marketplace
- STIG Avail = DISA STIG published for this OS version
- L1/L2 = Level 1 and Level 2 hardened images available
- TBD = Check marketplace for current availability
```

### Golden Image Pipeline Architecture

```
+-----------+     +----------------+     +------------------+
| Base OS   |     | Hardening      |     | Application      |
| Image     |---->| Layer          |---->| Layer            |
| (CIS L1   |     | (Additional    |     | (Agents,         |
|  or vendor|     |  CIS/STIG      |     |  monitoring,     |
|  base)    |     |  settings,     |     |  certificates)   |
+-----------+     |  exceptions)   |     +--------+---------+
                  +----------------+              |
                                                  v
                  +------------------+   +--------+---------+
                  | Compliance Scan  |<--| Versioned        |
                  | (OpenSCAP,       |   | Golden Image     |
                  |  Inspector,      |   | (AMI / Managed   |
                  |  Nessus)         |   |  Image / Custom) |
                  +--------+---------+   +--------+---------+
                           |                      |
                    Pass?  |               +------v--------+
                    +------+------+        | Image         |
                    | Yes  | No   |        | Registry      |
                    +--+---+--+---+        | (with tags:   |
                       |      |            |  OS, CIS ver, |
                    Publish  Fix &         |  date, hash)  |
                    to       rebuild       +---------------+
                    registry

Pipeline Tools by Cloud:
  AWS:   EC2 Image Builder + Inspector + SSM   (see providers/aws/ec2-image-builder.md)
  Azure: Azure Image Builder + Defender for Cloud
  GCP:   Packer + Cloud Build + VM Manager
  Multi: Packer + Ansible + OpenSCAP (cloud-agnostic; see providers/hashicorp/packer.md)
```

### Cloud-Native Security Posture Tools

```
+------------------+-------------------+-------------------+
|      AWS         |      Azure        |      GCP          |
+------------------+-------------------+-------------------+
| Security Hub     | Defender for      | Security Command  |
|  - CIS AWS       |   Cloud           |   Center          |
|    Foundations    |  - CIS Azure      |  - Security       |
|  - AWS FSBP      |    Foundations     |    Health         |
|  - PCI DSS       |  - Azure Security |    Analytics      |
|                  |    Benchmark      |  - Compliance     |
+------------------+-------------------+-------------------+
| Inspector        | Defender for      | VM Manager        |
|  - EC2 CVE scan  |   Servers         |  - OS Policy      |
|  - CIS OS scan   |  - Guest config   |    Compliance     |
|  - Container     |  - Qualys         |  - Patch mgmt     |
|    scan          |    integrated     |                   |
+------------------+-------------------+-------------------+
| SSM Patch Mgr    | Update Management | OS Patch Mgmt     |
|  - Patch         |  - Patch          |  - Patch          |
|    baselines     |    schedules      |    deployments    |
|  - Compliance    |  - Compliance     |  - Compliance     |
|    reporting     |    reporting      |    reporting      |
+------------------+-------------------+-------------------+
| GuardDuty        | Defender Threat   | SCC Premium       |
|  - Runtime       |   Protection      |  - VM Threat      |
|    threat det.   |  - Behavioral     |    Detection      |
|  - EC2 findings  |    analytics      |  - Container      |
|                  |                   |    Threat Det.    |
+------------------+-------------------+-------------------+
```

## Reference Links

- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) -- free benchmark PDFs for all major operating systems
- [CIS Hardened Images](https://www.cisecurity.org/cis-hardened-images) -- pre-hardened images for AWS, Azure, GCP
- [CIS Windows Server 2025 Benchmark](https://www.cisecurity.org/benchmark/microsoft_windows_server)
- [AWS STIG Hardened AMIs](https://docs.aws.amazon.com/ec2/latest/windows-ami-reference/ami-windows-stig.html)
- [AWS EC2 Image Builder STIG Components](https://docs.aws.amazon.com/imagebuilder/latest/userguide/ib-stig.html)
- [AWS Security Hub](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html)
- [Azure Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/)
- [GCP Security Command Center](https://cloud.google.com/security-command-center/docs)
- [GCP Shielded VMs](https://cloud.google.com/shielded-vm)
- [OpenSCAP](https://www.open-scap.org/)
- [DISA STIG Library](https://public.cyber.mil/stigs/)
- [Packer by HashiCorp](https://www.packer.io/)

## See Also

- `general/stig-hardening.md` -- STIG-specific compliance workflows, SCAP scanning, VMware ESXi hardening, and POA&M management
- `general/security.md` -- general security architecture including IAM, secrets management, encryption, and network security
- `general/compute.md` -- compute platform selection, OS patching lifecycle, and golden image pipeline decisions
- `general/iac-planning.md` -- infrastructure-as-code for embedding hardening settings into deployment templates
- `providers/aws/ec2-asg.md` -- EC2 instance configuration, launch templates, and Auto Scaling
- `providers/azure/compute.md` -- Azure VM configuration, VMSS, and Trusted Launch
- `providers/gcp/compute.md` -- Compute Engine configuration and Shielded VMs
- `providers/hashicorp/packer.md` -- Packer for building hardened images across clouds
