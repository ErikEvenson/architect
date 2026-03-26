# Wiz

## Scope

This file covers **Wiz cloud security platform architecture and design** including Wiz CNAPP (Cloud-Native Application Protection Platform), agentless scanning architecture, Wiz Security Graph, CSPM (Cloud Security Posture Management), CWPP (Cloud Workload Protection Platform), DSPM (Data Security Posture Management), Kubernetes Security Posture Management (KSPM), Wiz Runtime Sensor, Wiz Code (IaC and code scanning), Wiz Defend (runtime detection and response), Wiz AI-SPM (AI Security Posture Management), and licensing models (per-workload, enterprise agreements). It does not cover general cloud security architecture; for that, see `general/security.md` and the cloud provider-specific security files.

## Checklist

- [ ] **[Critical]** Connect all cloud accounts and subscriptions to Wiz using read-only API connectors — Wiz's agentless scanning operates via cloud provider APIs (AWS AssumeRole, Azure service principal, GCP service account); incomplete account onboarding creates visibility gaps
- [ ] **[Critical]** Understand Wiz's agentless scanning mechanism — Wiz creates snapshots of VM disks and analyzes them externally; this avoids agent deployment but means scanning frequency is periodic (typically every 24 hours), not continuous
- [ ] **[Critical]** Use the Wiz Security Graph to identify toxic risk combinations rather than individual findings — Wiz's primary value is correlating vulnerabilities, misconfigurations, exposed secrets, identities, and network exposure into attack paths; reviewing findings in isolation misses the graph's power
- [ ] **[Critical]** Configure Wiz project scoping and RBAC to align with organizational team boundaries — Wiz projects control which teams see which cloud resources; misconfigured projects expose sensitive workloads to unauthorized teams or hide critical findings from responsible owners
- [ ] **[Critical]** Integrate Wiz with the ticketing system (Jira, ServiceNow) and configure automated issue routing based on resource ownership tags — without integration, Wiz findings remain in the Wiz console and are not actioned by the teams that own the resources
- [ ] **[Recommended]** Deploy the Wiz Runtime Sensor on high-value workloads for real-time threat detection — agentless scanning detects posture issues but cannot detect active exploitation; the Runtime Sensor provides container and VM-level runtime visibility
- [ ] **[Recommended]** Configure Wiz DSPM to discover and classify sensitive data in cloud storage (S3, Blob Storage, GCS, RDS, databases) — DSPM scanning identifies PII, PHI, financial data, and secrets in datastores and correlates exposure with security posture
- [ ] **[Recommended]** Enable Wiz Kubernetes Security Posture Management (KSPM) for all EKS, AKS, and GKE clusters — KSPM evaluates cluster configuration, RBAC, network policies, and image vulnerabilities; connect via Kubernetes connector, not just cloud account connector
- [ ] **[Recommended]** Establish Wiz policy baselines per workload type (production, dev, staging) and suppress known-accepted risks — untuned policies generate thousands of findings; prioritize critical issues and create exception workflows for accepted risks
- [ ] **[Recommended]** Use Wiz admission controller (OPA-based) to prevent deployment of workloads that violate security policies — shift-left by blocking non-compliant container images and Kubernetes manifests at the deployment pipeline, not just alerting post-deployment
- [ ] **[Recommended]** Configure Wiz Code scanning in CI/CD pipelines for IaC (Terraform, CloudFormation, Bicep) and container images — catch misconfigurations and vulnerabilities before they reach cloud environments
- [ ] **[Recommended]** Map Wiz findings to compliance frameworks (SOC 2, PCI DSS, HIPAA, CIS Benchmarks) using built-in compliance reports — Wiz auto-maps findings to controls; use these reports for audit evidence rather than manual mapping
- [ ] **[Optional]** Enable Wiz AI-SPM to discover and assess AI pipelines, training data, and model deployments in cloud environments — identifies shadow AI, exposed model endpoints, and training data with sensitive information
- [ ] **[Optional]** Evaluate Wiz Defend for cloud detection and response (CDR) — combines runtime sensor telemetry with cloud audit logs (CloudTrail, Activity Log, Audit Log) for threat detection and investigation
- [ ] **[Optional]** Configure Wiz ServiceNow CMDB integration to enrich CMDB records with security posture data — bidirectional sync ensures CMDB reflects actual cloud resource state and Wiz inherits asset ownership
- [ ] **[Optional]** Evaluate Wiz guardrails for automated remediation of critical misconfigurations — auto-remediation (e.g., closing public S3 buckets, removing overly permissive security groups) reduces response time but requires careful scoping to avoid breaking production

## Why This Matters

Wiz has become the fastest-growing cloud security platform by solving a fundamental problem: traditional security tools require agents on every workload, which creates deployment friction and coverage gaps in cloud environments where workloads are ephemeral. Wiz's agentless approach scans cloud environments via API access and disk snapshot analysis, achieving near-complete coverage without touching running workloads.

The Security Graph is Wiz's core differentiator. Individual findings (a CVE, a misconfiguration, an exposed secret) are noise at cloud scale. The Security Graph correlates these findings to identify attack paths: "This VM has a critical RCE vulnerability, is publicly exposed via a misconfigured security group, runs with an IAM role that has admin access to S3, and that S3 bucket contains PII." This toxic combination is an urgent priority. The same CVE on an internal VM with no privileges is low priority. Organizations that treat Wiz as a flat vulnerability list rather than an attack-path analyzer waste the platform's primary value.

Wiz's agentless scanning has a fundamental trade-off: it operates on snapshots, not live systems. Scanning happens on a periodic schedule (typically 24 hours). This means Wiz detects posture issues and vulnerabilities reliably but cannot detect active exploitation, runtime behavior, or real-time threats. The Wiz Runtime Sensor fills this gap for organizations that need detection and response capabilities alongside posture management.

Licensing is per-workload (VMs, containers, serverless functions) and can scale quickly in large cloud environments. Accurate workload counting before contract signing prevents budget surprises. Workloads that auto-scale (ASGs, Kubernetes pods) should be counted at their typical scale, not peak, but the contract must accommodate growth.

## Common Decisions (ADR Triggers)

### ADR: Wiz CNAPP vs. Cloud-Provider-Native Security Tools

**Context:** AWS (Security Hub, GuardDuty, Inspector), Azure (Defender for Cloud), and GCP (Security Command Center) offer native security posture management.

**Options:**

| Criterion | Wiz CNAPP | Cloud-Native Tools | Both |
|---|---|---|---|
| Multi-cloud | Single pane for AWS/Azure/GCP/OCI | Per-cloud console | Wiz as overlay |
| Agentless | Yes (API + snapshot) | Varies (Inspector needs agent) | Wiz agentless + native agents |
| Attack path analysis | Security Graph | Limited or manual | Wiz for graph, native for realtime |
| Cost | Per-workload subscription | Included/low-cost | Higher total cost |
| Compliance reporting | Multi-cloud unified | Per-cloud only | Wiz for unified reporting |

### ADR: Agentless-Only vs. Agent + Agentless (Wiz Runtime Sensor)

**Context:** Wiz's agentless scanning provides posture visibility but the Runtime Sensor adds real-time threat detection.

**Decision factors:** Whether the organization needs runtime detection and response (CDR) in addition to posture management, workload types (containers benefit most from runtime sensors), performance impact tolerance, existing EDR coverage on cloud workloads (CrowdStrike, Defender), and whether Wiz Defend is intended to replace or complement the existing CDR tool.

### ADR: Wiz vs. Alternative CNAPP (Prisma Cloud, Orca, Lacework)

**Context:** Multiple CNAPP vendors compete in the cloud security posture space.

**Decision factors:** Agentless-first vs. agent-first architecture, Security Graph depth, multi-cloud parity, DSPM and AI-SPM capabilities, runtime detection maturity, CI/CD integration depth, existing vendor relationships, and pricing model (per-workload vs. per-asset vs. consumption-based).

### ADR: Wiz Integration Architecture

**Context:** Wiz findings must be routed to the teams that own the affected resources for remediation.

**Decision factors:** Ticketing system (Jira, ServiceNow, Azure DevOps), resource ownership tagging strategy, automated vs. manual issue creation, bidirectional status sync (closing Wiz issues when tickets are resolved), and whether to use Wiz guardrails for automated remediation of critical findings.

## AI and GenAI Capabilities

**Wiz AskAI** -- Natural-language interface for querying the Wiz Security Graph. Analysts can ask questions like "Show me all publicly exposed databases with PII" or "What is the blast radius if this EC2 instance is compromised?" AskAI translates natural language into graph queries and returns visual attack path results.

**Wiz AI-SPM (AI Security Posture Management)** -- Discovers AI services, pipelines, models, and training data across cloud environments. Identifies shadow AI deployments, exposed model endpoints, overprivileged AI service roles, and training datasets containing sensitive information. Covers AWS SageMaker, Azure OpenAI, GCP Vertex AI, and self-hosted model deployments.

**Wiz Threat Intelligence** -- ML-powered threat context enrichment that correlates vulnerability findings with exploit availability, active exploitation in the wild, and threat actor campaigns. Prioritizes findings based on real-world threat landscape rather than theoretical CVSS scores.

## See Also

- `general/security.md` -- Security architecture, hardening, compliance frameworks
- `general/cloud-workload-hardening.md` -- Cloud workload hardening best practices
- `providers/aws/security.md` -- AWS-specific security services (complementary to Wiz)
- `providers/azure/security.md` -- Azure-specific security services (complementary to Wiz)
- `providers/gcp/security.md` -- GCP-specific security services (complementary to Wiz)
- `providers/qualys/vulnerability-management.md` -- Vulnerability management (complementary for on-premises assets)
- `providers/crowdstrike/endpoint-security.md` -- EDR/XDR (complementary for endpoint/runtime detection)

## Reference Links

- [Wiz Documentation](https://docs.wiz.io/) -- platform configuration, connector setup, policy management, and API reference
- [Wiz Security Graph Query Language](https://docs.wiz.io/wiz-docs/docs/graph-query-language) -- writing custom graph queries for security analysis and reporting
- [Wiz Kubernetes Connector Setup](https://docs.wiz.io/wiz-docs/docs/kubernetes-connector) -- EKS, AKS, GKE, and self-managed cluster integration
- [Wiz Runtime Sensor Deployment](https://docs.wiz.io/wiz-docs/docs/wiz-sensor) -- agent deployment for containers and VMs for runtime threat detection
- [Wiz Blog: Toxic Combinations and Attack Paths](https://www.wiz.io/blog) -- architectural deep-dives on Security Graph analysis methodology
