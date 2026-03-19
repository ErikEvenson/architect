# Compliance Automation

## Scope

This file covers **automated compliance enforcement, scanning, and evidence collection** as a cross-cutting concern across cloud and hybrid environments. Includes policy-as-code frameworks, continuous compliance scanning, CIS benchmark automation, supply chain compliance, GRC platform integration, and automated remediation workflows. For specific regulatory frameworks, see files in `compliance/`. For governance and policy-as-code basics, see `general/governance.md`. For security controls, see `general/security.md`.

## Checklist

- [ ] **[Critical]** Is a policy-as-code framework selected and enforced? (OPA/Rego for Kubernetes and Terraform, HashiCorp Sentinel for Terraform Cloud/Enterprise, AWS Config Rules, Azure Policy, GCP Organization Policy; choose based on toolchain and multi-cloud requirements)
- [ ] **[Critical]** Is continuous compliance scanning enabled across all accounts, subscriptions, and projects? (AWS Security Hub with conformance packs, Microsoft Defender for Cloud regulatory compliance, GCP Security Command Center; must cover all environments including dev/sandbox)
- [ ] **[Critical]** Are CIS Benchmarks automated with scanning, drift detection, and remediation? (AWS Inspector CIS scans, Defender for Cloud CIS assessments, SCC Security Health Analytics; decide on auto-remediation vs alert-only based on environment criticality)
- [ ] **[Critical]** Are compliance policy checks integrated into CI/CD pipelines as pre-deploy gates? (OPA conftest for IaC validation, Checkov, tfsec, Bridgecrew; fail builds on Critical violations, warn on Recommended)
- [ ] **[Critical]** Are Kubernetes admission controllers enforcing compliance at deploy time? (OPA Gatekeeper, Kyverno; prevent non-compliant workloads from reaching the cluster rather than detecting them after deployment)
- [ ] **[Recommended]** Is evidence collection automated for audit readiness? (automated snapshots of configurations, scan results archived to immutable storage, audit log exports on schedule; manual evidence gathering does not scale and delays audits)
- [ ] **[Recommended]** Is a GRC platform integrated with cloud-native compliance tooling? (ServiceNow GRC, Archer, Drata, Vanta; decide whether cloud-native tools feed into GRC or GRC drives cloud controls; avoid dual maintenance of control mappings)
- [ ] **[Recommended]** Are SBOMs generated and tracked for all deployed software? (Syft, Trivy, Grype for generation; SPDX or CycloneDX format; integrate into CI/CD to block builds with known-vulnerable or unapproved components)
- [ ] **[Recommended]** Is POA&M tracking automated with remediation workflows? (findings from scanners automatically create POA&M entries, assign owners, track SLA compliance; integrate with ticketing systems for accountability)
- [ ] **[Recommended]** Are compliance dashboards providing real-time posture visibility? (executive summaries showing compliance percentage by framework, trend lines, aging findings; team-level dashboards showing remediation backlog and SLA adherence)
- [ ] **[Recommended]** Is infrastructure drift detection configured with defined response procedures? (AWS Config, Azure Policy compliance, Terraform Cloud drift detection; decide between auto-remediation and alert-and-investigate based on resource criticality)
- [ ] **[Optional]** Are preventive, detective, and corrective controls explicitly mapped for each compliance requirement? (preventive: SCPs, admission controllers, deny policies; detective: Config Rules, scanning, monitoring; corrective: auto-remediation Lambda/Functions, runbooks; mapping identifies gaps in defense-in-depth)
- [ ] **[Optional]** Is software supply chain provenance verified for all container images and artifacts? (Sigstore/cosign for image signing, SLSA framework for build provenance, in-toto attestations; blocks deployment of unsigned or untraceable artifacts)

## Why This Matters

Manual compliance processes are the single biggest source of audit friction, security drift, and wasted engineering time. Organizations that rely on spreadsheets and periodic manual reviews discover violations months after they occur, face expensive emergency remediation cycles, and cannot demonstrate continuous compliance to auditors or regulators.

The cost of non-automation compounds over time. Each new compliance framework (SOC 2, FedRAMP, HIPAA, PCI DSS) adds another layer of manual evidence collection, another set of controls to verify, and another audit cycle to support. Without automation, compliance teams become bottlenecks and engineering teams treat compliance as a checkbox exercise rather than a continuous practice.

Infrastructure drift is the silent compliance killer. A resource deployed in compliance can drift out of compliance within hours through manual console changes, ad-hoc scripts, or misconfigured automation. Without continuous scanning and drift detection, point-in-time audits create a false sense of security. Automated compliance ensures that the state observed during an audit is the state that exists every day.

## Common Decisions (ADR Triggers)

- **Policy-as-code framework selection** -- OPA/Rego (portable, multi-cloud, Kubernetes-native) vs HashiCorp Sentinel (Terraform-native, simpler for Terraform-only shops) vs cloud-native policies (deepest integration but vendor lock-in); affects team skills, policy portability, and enforcement scope
- **Preventive vs detective control balance** -- preventive controls (deny policies, admission controllers) block violations before they occur but can slow development; detective controls (scanning, Config Rules) allow violations and alert after the fact; corrective controls (auto-remediation) fix violations automatically but risk unintended changes in production
- **Auto-remediation scope** -- which resources and which violations are safe to auto-remediate vs which require human review; auto-closing a public S3 bucket is safe, auto-modifying a production database security group may cause outages
- **SBOM format and toolchain** -- SPDX vs CycloneDX format, generation point (build time vs registry scan), storage and query infrastructure, integration with vulnerability databases
- **GRC platform integration model** -- cloud-native tools as source of truth feeding GRC for reporting vs GRC platform as control authority driving cloud configuration; affects data flow, latency of compliance posture updates, and cost
- **Compliance-as-code pipeline strategy** -- fail builds on any violation vs tiered enforcement (block Critical, warn Recommended, log Optional); affects developer velocity and compliance rigor tradeoff
- **Evidence retention and immutability** -- how long to retain compliance evidence, which storage tier, immutability controls (Object Lock, WORM); must align with regulatory retention requirements
- **Drift response model** -- auto-remediate all drift vs auto-remediate non-production and alert for production vs alert-only with SLA for manual remediation; affects operational risk and change management process

## Reference Links

- [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) -- policy-as-code engine for Kubernetes, Terraform, CI/CD, and microservices authorization
- [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/) -- Kubernetes admission controller built on OPA for enforcing policies on cluster resources
- [Kyverno](https://kyverno.io/) -- Kubernetes-native policy engine using YAML-based policies without requiring Rego
- [HashiCorp Sentinel](https://www.hashicorp.com/sentinel) -- policy-as-code framework for HashiCorp Enterprise products
- [AWS Security Hub](https://aws.amazon.com/security-hub/) -- centralized security and compliance findings aggregation with automated checks against standards
- [Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/) -- cloud security posture management with regulatory compliance assessments
- [GCP Security Command Center](https://cloud.google.com/security-command-center) -- security and risk management platform with compliance monitoring
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) -- consensus-based security configuration guidelines for cloud providers, operating systems, and applications
- [Checkov](https://www.checkov.io/) -- static analysis tool for infrastructure-as-code scanning against compliance policies
- [Syft](https://github.com/anchore/syft) -- SBOM generation tool supporting SPDX and CycloneDX formats
- [Trivy](https://trivy.dev/) -- comprehensive security scanner for containers, IaC, SBOMs, and cloud configurations
- [SPDX Specification](https://spdx.dev/) -- ISO/IEC standard for software bill of materials
- [CycloneDX Specification](https://cyclonedx.org/) -- OWASP standard for SBOM, SaaSBOM, and VEX
- [SLSA Framework](https://slsa.dev/) -- supply chain integrity framework for software build provenance

## See Also

- `general/governance.md` -- Cloud governance, tagging, policy-as-code basics, and guardrails vs gates
- `general/security.md` -- Security controls, encryption, and threat detection
- `general/ci-cd.md` -- CI/CD pipeline design and deployment strategies
- `general/container-orchestration.md` -- Kubernetes security and admission control
- `compliance/fedramp.md` -- FedRAMP continuous monitoring and POA&M requirements
- `compliance/soc2.md` -- SOC 2 control mapping and evidence requirements
