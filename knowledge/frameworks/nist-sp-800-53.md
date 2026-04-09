# NIST SP 800-53 Security and Privacy Controls

## Scope

NIST Special Publication 800-53 (Revision 5) is the US federal control catalog for information systems and organizations. It defines ~1000 security and privacy controls organized into 20 control families, with three baselines (Low, Moderate, High) based on the system's FIPS 199 categorization. SP 800-53 is the underlying control catalog from which FedRAMP, NIST SP 800-171, NIST SP 800-172, the DoD Cloud Computing SRG, and many state and industry frameworks derive their controls. Covers the control family taxonomy, the baseline selection model, the control selection and tailoring process, the relationship between SP 800-53 and FedRAMP impact levels, the SP 800-53A assessment procedures, and the relationship to the broader NIST Risk Management Framework (RMF) defined in SP 800-37. Does not cover the privacy-only controls in detail (see SP 800-53 Appendix C for privacy control mapping).

## The 20 Control Families

| ID | Family | Focus |
|---|---|---|
| AC | Access Control | Account management, separation of duties, least privilege, session control, remote access |
| AT | Awareness and Training | Security awareness training, role-based training, training records |
| AU | Audit and Accountability | Audit events, content of audit records, audit storage, audit review and analysis, time stamps |
| CA | Assessment, Authorization, and Monitoring | Control assessments, system interconnections, plan of action and milestones, continuous monitoring |
| CM | Configuration Management | Baseline configurations, change control, configuration settings, software usage restrictions |
| CP | Contingency Planning | Contingency plan, training, testing, alternate sites, system backup and recovery |
| IA | Identification and Authentication | Identification, authenticators, authenticator management, cryptographic module authentication |
| IR | Incident Response | Incident response training, testing, handling, monitoring, reporting, response assistance |
| MA | Maintenance | Controlled maintenance, maintenance tools, nonlocal maintenance, maintenance personnel |
| MP | Media Protection | Media access, marking, storage, transport, sanitization, use |
| PE | Physical and Environmental Protection | Physical access authorizations, monitoring, visitor records, emergency power, water damage |
| PL | Planning | System security plan, rules of behavior, baseline tailoring, security architecture |
| PM | Program Management | Information security program plan, senior information security officer, resources, plan of action |
| PS | Personnel Security | Position risk designation, personnel screening, termination, transfer, sanctions |
| PT | PII Processing and Transparency | Authority to process PII, purpose specification, consent, individual access, data minimization |
| RA | Risk Assessment | Security categorization, risk assessment, vulnerability monitoring and scanning, criticality analysis |
| SA | System and Services Acquisition | Allocation of resources, system development life cycle, acquisition process, external system services |
| SC | System and Communications Protection | Boundary protection, transmission confidentiality, cryptographic protection, denial-of-service protection |
| SI | System and Information Integrity | Flaw remediation, malicious code protection, system monitoring, error handling, input validation |
| SR | Supply Chain Risk Management | Supply chain risk management policy, supply chain risk assessments, provenance, component authenticity |

## Baselines

SP 800-53 defines three baselines based on the FIPS 199 categorization of the system:

- **Low** — minimum baseline for systems where the loss of confidentiality, integrity, or availability would have a **limited** adverse effect. ~150 controls.
- **Moderate** — for systems where the loss would have a **serious** adverse effect. ~270 controls. The most common baseline for federal systems.
- **High** — for systems where the loss would have a **severe or catastrophic** adverse effect. ~370 controls. Reserved for systems handling national security information, critical infrastructure, or large-scale PII.

The baseline is chosen based on the highest categorization across confidentiality, integrity, and availability — a system that is Low for confidentiality but Moderate for integrity is a Moderate system overall.

## Relationship to FedRAMP

FedRAMP Impact Levels map directly onto SP 800-53 baselines:

- **FedRAMP Low** = SP 800-53 Low baseline + ~25 FedRAMP-specific controls and parameter values
- **FedRAMP Moderate** = SP 800-53 Moderate baseline + ~30 FedRAMP-specific controls and parameter values
- **FedRAMP High** = SP 800-53 High baseline + ~40 FedRAMP-specific controls and parameter values

The FedRAMP-specific controls fill gaps in the SP 800-53 baseline that are particularly relevant to cloud service providers (e.g., AC-2(7) Role-Based Schemes, CA-7 Continuous Monitoring with FedRAMP-specific frequencies, RA-5 Vulnerability Scanning with FedRAMP-specific timelines). Most are parameter values rather than entirely new controls — SP 800-53 leaves many parameters configurable by the implementing organization, and FedRAMP fixes those parameters to specific values.

For details on the cloud service provider audit experience under FedRAMP, see `compliance/fedramp.md`.

## Control Tailoring

SP 800-53 baselines are starting points, not final selections. The Risk Management Framework (RMF) defined in SP 800-37 specifies a **tailoring** process where the baseline is adjusted for the specific system:

- **Apply scoping considerations** — some controls do not apply (e.g., PE controls do not apply to a SaaS workload running in a public cloud where the customer has no physical access to the underlying infrastructure)
- **Compensating controls** — when a baseline control cannot be implemented as stated, document a compensating control that achieves the same security objective
- **Parameter assignment** — for controls with configurable parameters, assign specific values appropriate to the system's risk
- **Supplemental controls** — add controls beyond the baseline when the risk assessment indicates additional protection is needed

The tailored control set is documented in the System Security Plan (SSP) along with the implementation status of each control.

## Implementation Notes for Cloud Workloads

### Inherited controls

When deploying on a cloud provider (AWS, Azure, GCP), many SP 800-53 controls are **inherited** from the provider's own authorization. The customer's SSP can reference the provider's controls for the underlying infrastructure (PE family, much of MA, much of SC at the network layer) and only needs to document the customer-implemented controls (AC, AU, CM, IA, IR, RA, SI in particular).

The inheritance model is documented in the cloud provider's Customer Responsibility Matrix (CRM) — AWS publishes one for each service, Azure publishes one per service category, GCP publishes one per service. The CRM is the load-bearing artifact for the SSP because it tells the customer which controls they must implement themselves and which they inherit.

### Common control implementations in cloud

- **AC-2 Account Management** → IAM Identity Center, Entra ID, Cloud Identity with automated lifecycle
- **AC-6 Least Privilege** → role-based IAM with PIM (Azure) or session-based access (AWS Identity Center)
- **AU-2 Auditable Events** → CloudTrail / Activity Log / Audit Logs with all management events
- **AU-9 Protection of Audit Information** → log destination in a separate account with object lock / immutable storage
- **CM-2 Baseline Configuration** → IaC (CloudFormation, Bicep, Terraform) as the baseline
- **CM-7 Least Functionality** → AMI hardening, container image scanning, port closure
- **IA-2 Identification and Authentication (Organizational Users)** → MFA enforced via identity provider
- **IR-4 Incident Handling** → defined incident response process with playbooks and automation
- **RA-5 Vulnerability Monitoring and Scanning** → Inspector / Defender for Cloud / Security Command Center with continuous scanning
- **SC-7 Boundary Protection** → VPC / VNet / VPC with security groups, network firewall, web application firewall
- **SC-8 Transmission Confidentiality and Integrity** → TLS 1.2+ for all transmissions, mTLS for service-to-service
- **SC-13 Cryptographic Protection** → KMS / Key Vault / Cloud KMS with FIPS 140-2 validated modules
- **SC-28 Protection of Information at Rest** → SSE with customer-managed keys
- **SI-2 Flaw Remediation** → automated patch management with documented timelines
- **SI-4 System Monitoring** → cloud-native monitoring + SIEM integration

### Control documentation

Each control implementation must be documented in the SSP with:

- **Implementation description** — how the control is implemented in this system, in plain language
- **Status** — implemented, partially implemented, not implemented, alternative implementation
- **Responsible role** — who owns the control
- **Test procedure** — how the control is verified (manual or automated)
- **Last assessment date** — when the control was last verified to be operating

The SSP is the source of truth for the control implementation and is the artifact that an assessor reviews during authorization.

## Common Decisions

- **Baseline selection** — driven by FIPS 199 categorization, not by preference. Most cloud workloads with non-public data are Moderate; systems handling national security information are High; public-facing marketing sites might be Low.
- **Tailoring vs full baseline implementation** — tailoring is allowed and expected. The baseline is a starting point. Document every deviation with justification.
- **Inherited vs customer-implemented controls** — read the cloud provider's CRM and document inheritance in the SSP. Do not re-implement controls that are inherited (it inflates the SSP and creates audit confusion).
- **SSP format** — most authorizations require the OSCAL format (the NIST-defined machine-readable format for security plans) or an OSCAL-derivable format. Word documents are still accepted in some authorizations but are being phased out.
- **Continuous monitoring scope** — the CA-7 control requires continuous monitoring with a specific frequency for each control. The frequency should match the control's risk; high-impact controls (e.g., AU-2 audit log generation) need near-real-time monitoring, low-impact controls (e.g., AT-2 awareness training) can be monitored quarterly.

## Reference Links

- [NIST SP 800-53 Revision 5](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search)
- [NIST SP 800-53A — Assessment Procedures](https://csrc.nist.gov/publications/detail/sp/800-53a/rev-5/final)
- [NIST SP 800-37 — Risk Management Framework](https://csrc.nist.gov/publications/detail/sp/800-37/rev-2/final)
- [NIST OSCAL — Open Security Controls Assessment Language](https://pages.nist.gov/OSCAL/)
- [FedRAMP control selections](https://www.fedramp.gov/baselines/)

## See Also

- `compliance/fedramp.md` — FedRAMP authorization process and the cloud service provider perspective
- `compliance/nist-800-171-cmmc.md` — NIST SP 800-171 (CUI protection) which is a derived subset of SP 800-53
- `frameworks/nist-csf-2.0.md` — NIST Cybersecurity Framework as a higher-level reference (when added)
- `general/security.md` — general security architecture
- `general/governance.md` — broader governance context
