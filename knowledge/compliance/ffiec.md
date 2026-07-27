# FFIEC — US Bank IT Examination Framework

## Scope

The Federal Financial Institutions Examination Council (FFIEC) is the interagency body that prescribes uniform principles, standards, and report forms for the federal examination of US financial institutions. For an architect, FFIEC matters because it is the layer where **cloud architecture decisions meet the bank examiner** — the FFIEC IT Examination Handbook is what examiners carry into the room, and the interagency statements the FFIEC member agencies issue are what determine whether a design survives contact with supervision. Covers who actually examines whom (the thing practitioners most often state incorrectly), the IT Examination Handbook booklet structure, the 2020 interagency cloud statement, the 2023 interagency third-party risk management guidance, the computer-security incident notification rules, what examiners actually ask for in an IT exam, and what all of it changes about a design.

This page deliberately separates **what is required by rule**, **what is supervisory guidance**, and **what is common practice**. Conflating those three is the most damaging error a bank-compliance page can make, and it is the error that leads architects to over-build for a community bank or under-build for a large one. Applicability by institution size is called out wherever it differs.

**Does not cover** the customer-information safeguards program itself (see `compliance/glba.md` — the Interagency Guidelines Establishing Information Security Standards are the GLBA 501(b) implementation and are the substantive security rule behind most IT exam findings), financial-reporting ITGCs (see `compliance/sox.md`), card data (see `compliance/pci-dss.md`), or regulatory reporting data architecture (see `compliance/bank-regulatory-reporting.md`).

## What the FFIEC Is — and Is Not

The FFIEC is established by statute at [12 U.S.C. 3303](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section3303&num=0&edition=prelim). Its members are:

1. the Comptroller of the Currency
2. the Chairman of the Board of Directors of the FDIC
3. a Governor of the Federal Reserve Board designated by the Chairman
4. the Director of the Consumer Financial Protection Bureau
5. the Chairman of the NCUA Board
6. the Chairman of the **State Liaison Committee**

**The FFIEC is not a regulator.** It issues no rules, brings no enforcement, and examines no institution. It produces uniform examination guidance and report forms that its member agencies then adopt individually. This distinction has a direct practical consequence: when someone says "FFIEC requires X," the accurate statement is almost always either "the FFIEC IT Handbook sets an examiner expectation of X" (guidance) or "12 CFR part *nn* requires X" (rule). Architects should insist on knowing which, because guidance is risk-based and scalable to the institution while a rule is not.

## Who Actually Examines Whom

Federal supervisory assignment for insured depository institutions is set by the definition of **"appropriate Federal banking agency"** at [12 U.S.C. 1813(q)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section1813&num=0&edition=prelim). Verbatim from the statute:

| Agency | Institutions (12 U.S.C. 1813(q)) |
|---|---|
| **OCC** | National banking associations; Federal branches and agencies of foreign banks; **Federal savings associations** |
| **FDIC** | **State nonmember** insured banks; foreign banks having an insured branch; **State savings associations** |
| **Federal Reserve Board** | **State member banks**; branches/agencies of foreign banks (for provisions of the Federal Reserve Act applied via the International Banking Act); foreign banks not operating an insured branch; agencies and commercial lending companies other than Federal agencies; **bank holding companies** and their non-depository subsidiaries; **savings and loan holding companies** and their non-depository subsidiaries |

Two points the statute makes explicitly that practitioners routinely miss:

- **"Under the rule set forth in this subsection, more than one agency may be an appropriate Federal banking agency with respect to any given institution."** A single design can therefore face two federal examiners with different examination calendars and different findings.
- **State-chartered institutions are examined by their state banking department as well.** 12 U.S.C. 1813(r) defines the "State bank supervisor" as the state officer or agency with primary regulatory authority over state banks or state savings associations. A state-chartered savings bank is examined by its **state regulator and its federal counterpart** — commonly on an alternating-year or joint basis depending on the state and the agency. Architects designing for state charters should expect two sets of examination requests, not one, and should not assume the state examiner's expectations are a subset of the federal ones.

Beyond the banking agencies:

- **NCUA** supervises federally insured credit unions. It is an FFIEC member and it participates in most interagency IT statements, **but not all of them** — notably it was not a party to the 2023 third-party risk management guidance (below).
- **CFPB** has **exclusive authority** to examine for compliance with Federal consumer financial law at insured depository institutions and insured credit unions with **total assets of more than $10,000,000,000**, and their affiliates ([12 U.S.C. 5515](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section5515&num=0&edition=prelim)). At institutions with **$10,000,000,000 or less** in total assets, the prudential regulator retains consumer-compliance examination authority and the CFPB's role is narrower ([12 U.S.C. 5516](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section5516&num=0&edition=prelim)). The $10B line is the single most consequential size threshold in US bank supervision and it is a **statutory** threshold, not a supervisory convention. Crossing it adds an examiner, not just a reporting obligation.

### Your cloud provider is examinable — Bank Service Company Act

This is the provision that most changes how an architect should think about a bank's cloud and SaaS estate. Under [12 U.S.C. 1867(c)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section1867&num=0&edition=prelim), when a depository institution has services performed for it by contract or otherwise:

> "(1) such performance shall be subject to regulation and examination by such agency **to the same extent as if such services were being performed by the depository institution itself on its own premises**, and (2) the depository institution shall notify each such agency of the existence of the service relationship **within thirty days** after the making of such service contract or the performance of the service, whichever occurs first."

Two design consequences follow directly, and they are **rule**, not guidance:

- The examination perimeter does not stop at the bank's network edge. A managed service provider, core processor, or cloud service in scope of the Bank Service Company Act can be examined directly. The agencies run a formal technology service provider examination program on that authority.
- **There is a 30-day agency notification obligation for new service relationships.** Architects who stand up a new SaaS or cloud service supporting a covered banking function are creating a filing obligation for someone. Build the trigger into the intake/onboarding workflow rather than discovering it at exam time.

## FFIEC IT Examination Handbook

The IT Examination Handbook (the "IT Handbook", published at `ithandbook.ffiec.gov`) is a set of booklets giving examiners procedures and expectations for information technology examinations. It is **examiner guidance, not regulation**. Its expectations are explicitly risk-based and scaled to institution size and complexity — the OCC's transmittal bulletins carry a standing "Note for Community Banks" saying so.

The FFIEC's own site is aggressively bot-protected, so the links below point at the **member-agency transmittal bulletins**, which are stable, citable, and state the rescissions precisely.

| Booklet | Status | Agency transmittal |
|---|---|---|
| **Architecture, Infrastructure, and Operations (AIO)** | Issued **June 30, 2021**. **Rescinds and replaces the "Operations" booklet**, which had been issued **July 2004**. | [OCC Bulletin 2021-30](https://www.occ.gov/news-issuances/bulletins/2021/bulletin-2021-30.html) |
| **Business Continuity Management (BCM)** | Issued **November 14, 2019**. Replaces the "Business Continuity Planning" booklet issued **February 2015** and rescinds OCC Bulletin 2015-9 (the outsourced-technology-services resilience appendix). | [OCC Bulletin 2019-57](https://www.occ.gov/news-issuances/bulletins/2019/bulletin-2019-57.html) |
| **Development, Acquisition, and Maintenance (DA&M)** | Issued **2024** (OCC transmittal dated September 5, 2024). Replaces the "Development and Acquisition" booklet issued **April 2004**. | [OCC Bulletin 2024-26](https://www.occ.gov/news-issuances/bulletins/2024/bulletin-2024-26.html) |
| **Information Security** | Current booklet in the handbook. Carries the technical security examination procedures; substantively anchored to the Interagency Guidelines Establishing Information Security Standards (below). *Revision date not verified for this page — check the handbook index before citing a date.* | — |
| **Outsourcing Technology Services** | Long-standing booklet, **materially older than the cloud era**. *Current status and revision date not verified for this page — confirm against the handbook index.* Read it alongside the 2023 third-party guidance and the 2020 cloud statement, which are where current supervisory expectation demonstrably lives. | — |

### Why AIO replacing Operations matters architecturally

The 2004 "Operations" booklet was written for a bank that ran its own data center. The AIO booklet, per the OCC transmittal, "explains how architecture, infrastructure, and operations are separate, but related, functions," addresses governance across all three, and covers "the risks of technology systems and operations that reside in, **or are connected to**, the institution."

That last clause is the whole shift. AIO is the booklet that gives examiners an explicit hook into architecture as a discipline — enterprise architecture artifacts, target-state design, IT strategic alignment — not just operational run-state. In practice this means an examiner may now reasonably ask to see **architecture documentation and an architecture governance process**, and "we have runbooks and change tickets" is no longer a complete answer. If you are the architect on a bank engagement, the AIO booklet is the one to read first; it is the booklet your deliverables will be judged against.

### The rule underneath the guidance

The IT Handbook is guidance. The **rule** behind most IT examination findings is the **Interagency Guidelines Establishing Information Security Standards**, adopted under section 39 of the Federal Deposit Insurance Act and section 501(b) of GLBA, codified at:

- [12 CFR part 30, appendix B](https://www.ecfr.gov/current/title-12/chapter-I/part-30/appendix-Appendix%20B%20to%20Part%2030) (OCC)
- 12 CFR part 208, appendix D-2 (Board)
- [12 CFR part 364, appendix B](https://www.ecfr.gov/current/title-12/part-364/appendix-Appendix%20B%20to%20Part%20364) (FDIC)

When you need to know whether something is *actually mandatory*, this is the text to read — not the handbook. See `compliance/glba.md` for the safeguards program itself.

## Interagency Statement on Risk Management for Cloud Computing Services (2020)

Issued **April 30, 2020** by the FFIEC members and distributed by each agency — for example [FDIC FIL-52-2020](https://www.fdic.gov/news/financial-institution-letters/2020/fil20052.html), "FFIEC Joint Statement on Risk Management for Cloud Computing Services." Notably, the FDIC's transmittal states it applies to **all** FDIC-supervised institutions, explicitly including those **under $1 billion in total assets** — this is not a large-bank-only statement.

**Status: supervisory guidance, not a rule.** It creates no new legal requirement. It does establish the examiner's frame of reference, and its central assertion is the one architects need to internalize:

> "Inherent in the use of cloud computing services are shared responsibilities between the provider and the client."

What it changes about a design:

- **The shared-responsibility model becomes an examinable artifact, not a slide.** The statement identifies responsibilities the institution retains when contracting with cloud providers. An examiner can reasonably ask which specific controls the institution owns versus inherits, and expect a documented answer per service — not per provider. "AWS is FedRAMP authorized" is not responsive; "we own key management, IAM configuration, network policy, logging retention, and patching of these layers" is.
- **Your own configuration is where the retained risk concentrates.** The FDIC transmittal describes the statement as providing "examples of risk management practices for a financial institution's safe and sound use of cloud computing services and safeguards to protect its customers' sensitive information" — that is, practices the *institution* performs. Budget assurance effort accordingly: continuous configuration assessment against a defined baseline beats an annual provider-attestation review. (The underlying joint statement is a PDF on the FFIEC's site, which blocks automated retrieval; the characterisation here is drawn from the agency transmittal, not from the statement text.) See `general/compliance-automation.md` and `general/cloud-workload-hardening.md`.
- **Provider attestation reports are an input, not the control.** Expect to review SOC reports for complementary user entity controls and to evidence that you implemented them — the same CUEC discipline described in `compliance/sox.md`.

## Interagency Guidance on Third-Party Relationships: Risk Management (2023)

Published at **88 FR 37920** on **June 9, 2023**, [final as of June 6, 2023](https://www.federalregister.gov/documents/2023/06/09/2023-12340/interagency-guidance-on-third-party-relationships-risk-management), issued jointly by the **Federal Reserve Board, FDIC, and OCC**.

**NCUA is not a party to this guidance.** Credit unions follow NCUA's own vendor/third-party expectations. Do not cite this guidance as binding on a credit union engagement.

It **replaced each agency's separate prior TPRM guidance** — the Federal Register text names precisely what it supersedes:

| Superseded | Agency |
|---|---|
| SR Letter 13-19 / CA Letter 13-21, "Guidance on Managing Outsourcing Risk" (Dec 5, 2013, updated Feb 26, 2021) | Board |
| FIL-44-2008, "Guidance for Managing Third-Party Risk" (June 6, 2008) | FDIC |
| OCC Bulletin 2013-29, "Third-Party Relationships: Risk Management Guidance" | OCC |
| OCC Bulletin 2020-10, the FAQs supplementing Bulletin 2013-29 | OCC |

OCC Bulletin 2002-16 on **foreign-based** third-party service providers was **not** rescinded and continues to supplement the guidance — relevant whenever a design places data or support personnel offshore.

**Status: guidance.** The Federal Register notice is styled "Final interagency guidance," is published as a Notice rather than a Rule, and states it creates no new information collections. It is nonetheless the document examiners work from, and it is explicitly **tailored** — "sound third-party risk management takes into account the level of risk, complexity, and size of the banking organization and the nature of the third-party relationship."

### The five life-cycle stages and three governance elements

The guidance is organized as a risk management life cycle:

1. **Planning**
2. **Due Diligence and Third-Party Selection**
3. **Contract Negotiation**
4. **Ongoing Monitoring**
5. **Termination**

Supported by governance: **Oversight and Accountability**, **Independent Reviews**, **Documentation and Reporting**.

The Contract Negotiation section is the one that shapes architecture, because it enumerates what the contract has to address — and several of those items are only satisfiable by a design decision made early. The guidance's own subsections include: *Nature and Scope of Arrangement; Performance Measures or Benchmarks; Responsibilities for Providing, Receiving, and Retaining Information; **The Right To Audit and Require Remediation**; Responsibility for Compliance With Applicable Laws and Regulations; Costs and Compensation; **Ownership and License**; **Confidentiality and Integrity**; **Operational Resilience and Business Continuity**; Indemnification and Limits on Liability; Insurance; Dispute Resolution; Customer Complaints; **Subcontracting**; **Foreign-Based Third Parties**; **Default and Termination**.*

Two of those are chronically under-designed:

- **Subcontracting.** The fourth-party chain is in scope. A SaaS vendor running on a hyperscaler that in turn depends on a specialized sub-processor is three parties deep, and the bank still owns the risk. Inventory it before an examiner asks.
- **Default and Termination.** Termination provisions are only meaningful if the data is actually extractable. See the exit/portability discussion below.

Note also that the guidance **clarifies not all third-party relationships carry the same risk or criticality** — the "critical activities" concept drives depth of due diligence and contract rigor. Tiering vendors is not a corner-cut; it is what the guidance asks for. For community banks specifically, the agencies issued a separate, more accessible companion on fintech due diligence: [SR 21-15 / CA 21-11](https://www.federalreserve.gov/supervisionreg/srletters/SR2115.htm) (August 25, 2021).

## Incident Notification — This Part Is a Rule

Unlike almost everything else on this page, the notification timelines below are **binding regulation**.

### Banking organizations: 36 hours

The Computer-Security Incident Notification rule was published at **86 FR 66424** on **November 23, 2021** by the OCC, Board, and FDIC, with an **effective date of April 1, 2022 and a compliance date of May 1, 2022** ([Federal Register](https://www.federalregister.gov/documents/2021/11/23/2021-25510/computer-security-incident-notification-requirements-for-banking-organizations-and-their-bank)). It is codified at **12 CFR part 53** (OCC), **12 CFR part 225** (Board, Regulation Y), and **12 CFR part 304** (FDIC).

The operative text, at [12 CFR 53.3](https://www.ecfr.gov/current/title-12/chapter-I/part-53/section-53.3):

> "The OCC must receive this notification from the banking organization as soon as possible and **no later than 36 hours after the banking organization determines that a notification incident has occurred**."

The 36-hour clock starts on **determination**, not on occurrence or detection. That is a meaningful distinction and it puts weight on having a defined, documented determination step in the incident process — an undefined determination point is how institutions end up arguing with an examiner about when the clock started.

A **"notification incident"** is defined at [12 CFR 53.2](https://www.ecfr.gov/current/title-12/chapter-I/part-53/section-53.2) as a computer-security incident that has materially disrupted or degraded, or is reasonably likely to materially disrupt or degrade, the banking organization's:

1. ability to carry out banking operations, activities, or processes, or deliver banking products and services **to a material portion of its customer base**, in the ordinary course of business;
2. business line(s) whose failure would result in a **material loss of revenue, profit, or franchise value**; or
3. operations whose failure or discontinuance would **pose a threat to the financial stability of the United States**.

Prong 3 is a systemic-risk prong that in practice reaches only the largest institutions; prongs 1 and 2 are what a community or regional bank will actually trigger on. Note also that a "computer-security incident" under 53.2 requires **actual harm** to confidentiality, integrity, or availability — an attempted-but-blocked intrusion is not one.

### Bank service providers: 4-hour disruption trigger

The same rule places an obligation on the **provider side**. A bank service provider must notify each affected banking organization customer as soon as possible when it determines it has experienced a computer-security incident that has caused, or is reasonably likely to cause, a **material service disruption or degradation for four or more hours**.

"Bank service provider" means a bank service company or other person performing **covered services** — services subject to the Bank Service Company Act (12 U.S.C. 1861–1867). If you are architecting a platform that serves banks, this obligation is yours, and it needs to be wired into your own incident process and your customer-notification tooling.

### Credit unions: 72 hours

NCUA's rule is different and is often misquoted as 36 hours. Under [12 CFR 748.1(c)](https://www.ecfr.gov/current/title-12/chapter-VII/subchapter-A/part-748/section-748.1), a federally insured credit union must notify NCUA "as soon as possible but **no later than 72 hours after** a federally insured credit union **reasonably believes** that it has experienced a **reportable cyber incident**" — or within 72 hours of being notified by a third party, whichever is sooner. Different clock, different trigger standard ("reasonably believes" rather than "determines"), different term of art.

### Design consequence

Incident notification is a **detection-and-decision** problem before it is a reporting problem. If mean time to determination exceeds a day, the 36-hour window is already consumed by internal triage. Practical implications: severity classification criteria that map to the 53.2 prongs directly, a named determination authority available out of hours, and telemetry sufficient to establish blast radius quickly. See `general/observability.md` and `patterns/security-operations.md`.

## What Examiners Actually Ask For

Distilled from the AIO/BCM booklets, the 2020 cloud statement, the 2023 third-party guidance, and the Interagency Guidelines. Presented as the *request*, with the architecture decision that determines whether you can answer it.

| Examiner request | Architecture decision that determines the answer |
|---|---|
| **Key custody** — who can decrypt this data, and can the provider? | Provider-managed vs customer-managed vs external/HYOK key material; whether key administration is separable from data-plane admin; whether key deletion is a real control. Decide at design time; it is close to unchangeable later. |
| **Data location** — where does this data physically reside, including backups, replicas, logs, and support access? | Region and replication topology; whether managed services silently egress (telemetry, model endpoints, support tooling); DR region selection. Note this is a *residency* question about data **and** about the personnel who can see it. |
| **Vendor concentration risk** — what breaks if this one provider fails? | Single-cloud simplicity versus concentration exposure. Do the inventory at the *service* level, not the *vendor* level — a bank on one cloud plus four SaaS products that are themselves on that same cloud has more concentration than its vendor list suggests. See `patterns/multi-cloud.md`. |
| **Exit and portability plan** — can you actually leave, and have you proven it? | Proprietary managed services versus portable ones; whether data is extractable in a usable format at realistic volumes; whether the exit has ever been tested. An untested exit plan is a document, not a control. |
| **Right to audit** — what audit rights do you hold contractually, and how are they exercised? | Hyperscalers rarely grant bespoke on-site audit; the practical answer is pooled audit programs, attestation reports, and contractual regulator-access clauses. Negotiate the substitute **before** signing, because it is unwinnable afterward. |
| **Incident notification** — will the provider tell you in time to meet your 36 hours? | Contractual provider notification SLA, and whether it is short enough to leave you usable time. A 72-hour provider SLA is structurally incompatible with a 36-hour obligation. |
| **Evidence of access reviews** — show recertification for privileged and application access. | Whether entitlements are modelled reviewably or scattered across bespoke roles. Widely reported as among the most frequent IT exam findings (practitioner observation, not a published agency statistic), and it is an identity-architecture problem rather than a paperwork problem. See `general/identity.md`. |
| **Change and configuration control over cloud resources** | IaC with reviewed, evidenced pipelines versus console changes. See `general/change-management.md`. |
| **Resilience evidence** — RTO/RPO for critical services, and proof they were met in a test. | BCM booklet expectations. Untested recovery is the finding. See `general/disaster-recovery.md`. |
| **Third-party inventory including subcontractors** | Whether the CMDB models fourth parties at all. See `general/supply-chain-security.md`. |

## Cloud Service Mapping

| Examination theme | AWS | Azure | GCP |
|---|---|---|---|
| Key custody / customer-managed keys | KMS, CloudHSM, External Key Store | Key Vault, Managed HSM | Cloud KMS, Cloud HSM, Cloud External Key Manager |
| Data location control | Region selection, S3 Block Public Access, SCP region conditions | Azure Policy allowed-locations, data residency options | Organization Policy resource-location constraint |
| Configuration baseline / drift | Config, Security Hub, Control Tower guardrails | Azure Policy, Defender for Cloud, Landing Zones | Security Command Center, Organization Policy, Assured Workloads |
| Privileged access + recertification | IAM Identity Center, Access Analyzer | Entra ID PIM, Access Reviews | IAM Recommender, privileged access management |
| Audit logging / immutability | CloudTrail + S3 Object Lock | Activity Log + immutable Blob storage | Cloud Audit Logs + bucket retention lock |
| Incident detection | GuardDuty, Detective, Security Hub | Defender for Cloud, Sentinel | Security Command Center |
| Resilience testing | Fault Injection Service, cross-Region backup | Chaos Studio, Azure Backup/Site Recovery | Backup and DR Service |
| Provider attestations for TPRM file | AWS Artifact | Service Trust Portal | Compliance Reports Manager |

Availability and naming change; verify against current provider documentation before relying on a specific service in a deliverable.

## Architect Checklist

- [ ] **[Critical]** **Establish which agencies actually examine this institution** before writing any compliance-driven design. Charter type determines the federal agency (12 U.S.C. 1813(q)); a state charter adds the state banking department; crossing **$10B in total assets** adds CFPB examination authority. Getting this wrong invalidates everything downstream.
- [ ] **[Critical]** **Identify every relationship that is a "covered service" under the Bank Service Company Act** and confirm the 30-day agency notification obligation is being met for new ones. Wire the trigger into vendor onboarding rather than relying on memory.
- [ ] **[Critical]** **Document the shared-responsibility split per cloud service, not per provider**, and map each retained responsibility to a named control owner. This is the artifact the 2020 cloud statement effectively asks for.
- [ ] **[Critical]** **Confirm the provider's incident notification SLA is shorter than your regulatory clock** — 36 hours for banks (12 CFR 53.3 and parallels), 72 hours for federally insured credit unions (12 CFR 748.1(c)). A provider SLA measured in business days is a defect, and it is a contract-negotiation item you cannot fix later.
- [ ] **[Critical]** **Define the incident "determination" step explicitly** — who declares, on what criteria, with what out-of-hours coverage. The 36-hour clock runs from determination; an undefined determination point is an examination finding waiting to happen.
- [ ] **[Critical]** **Decide key custody deliberately and document the rationale.** Customer-managed keys are not universally required, but the decision must be reasoned and evidenced, and it is effectively irreversible once data volume accumulates.
- [ ] **[Critical]** **Produce a data-location answer that covers backups, replicas, logs, and support/administrative access** — not just the primary region. Support-personnel location is a data-location question and is regularly missed.
- [ ] **[Critical]** **Maintain access recertification evidence for privileged and application access.** Among the most frequently reported IT exam findings, and one determined by identity architecture rather than by process documentation.
- [ ] **[Recommended]** **Tier third parties by criticality** per the 2023 interagency guidance rather than treating all vendors identically. The guidance explicitly contemplates tailoring; uniform treatment wastes effort on low-risk vendors and under-serves critical ones.
- [ ] **[Recommended]** **Inventory concentration at the service layer, including fourth parties.** Count what actually runs where, not what the vendor list says.
- [ ] **[Recommended]** **Test the exit plan at least once for each critical provider relationship.** Extraction rate at production data volume is the number that matters; a plan that assumes an unmeasured throughput has not been tested.
- [ ] **[Recommended]** **Negotiate the right-to-audit substitute before signing** — attestation reports, pooled audit participation, and explicit regulator-access clauses. Hyperscalers will not grant bespoke on-site audit; the time to establish the alternative is pre-signature.
- [ ] **[Recommended]** **Produce architecture documentation and an architecture governance record**, not just operational runbooks. The AIO booklet gives examiners an explicit hook into architecture as a function.
- [ ] **[Recommended]** **Evidence recovery objectives with an actual test result** rather than a stated RTO/RPO. Untested recovery is the BCM booklet's standing finding.
- [ ] **[Optional]** **Map controls once to a common framework** (NIST CSF 2.0 or ISO 27001) and cross-walk to the Interagency Guidelines, PCI-DSS, and SOX ITGCs rather than maintaining parallel control sets. See `frameworks/nist-csf-2.0.md`.
- [ ] **[Optional]** **For institutions approaching $10B in total assets**, begin consumer-compliance and data-governance preparation ahead of the threshold. The examiner arrives with the threshold, not after a grace period.

## Why This Matters

There is no FFIEC fine schedule, because the FFIEC does not enforce. Consequences arrive through the member agencies and they are supervisory rather than financial in the first instance — which understates their severity to anyone reading from a GDPR or PCI frame.

- **Examination ratings.** IT examinations feed the institution's supervisory ratings. Poor ratings constrain the business directly: they can impede merger and acquisition approvals, new activity applications, branch expansion, and charter changes. For a bank pursuing an acquisition, an IT examination finding is not a compliance cost — it is a deal risk.
- **Matters Requiring Attention (MRAs) and Matters Requiring Immediate Attention (MRIAs).** These are supervisory directives to remediate. They carry board-level visibility, defined timelines, and follow-up examination. An unresolved MRA escalates.
- **Formal enforcement.** The agencies can issue consent orders, cease-and-desist orders, civil money penalties, and removal actions. Consent orders are typically public.
- **The asymmetry that matters for architects.** A design that is defensible but undocumented fails examination the same way a bad design does. The evidence artifact is part of the deliverable, not an afterthought — this is the single most reliable predictor of whether a bank engagement goes smoothly.

## Common Decisions (ADR Triggers)

- **Single-cloud versus multi-cloud for concentration risk** — multi-cloud genuinely reduces concentration but multiplies the control surface, the evidence burden, and the operational cost. For a community bank the honest answer is usually single-cloud with a tested exit plan and documented concentration acceptance; for a large institution with critical operations, the calculus shifts. Do not import a G-SIB's answer into a $5B bank.
- **Customer-managed keys versus provider-managed keys** — CMK buys a cleaner examination narrative and a real revocation control at the cost of operational risk (a key management failure is a data-loss event). Decide explicitly, document the reasoning, and do not treat CMK as automatically correct.
- **Managed services versus portable services** — proprietary managed services reduce operational burden and increase exit cost. Frame this against the termination expectations in the 2023 guidance rather than on TCO alone.
- **Where the incident determination authority sits** — centralizing determination gives a defensible, consistent 36-hour clock; distributing it gives speed. Whichever you choose, name it in the runbook.
- **Depth of third-party due diligence by tier** — questionnaire, attestation review, or full assessment. Document the tiering criteria; the criteria are as examinable as the assessments.
- **Evidence collection: automated versus manual** — automated control evidence scales and survives auditor turnover; manual collection is cheaper to start and reliably degrades. See `general/compliance-automation.md`.
- **State-charter dual examination handling** — whether to maintain one evidence set satisfying both examiners or two. One set is the right default; confirm the state's specific expectations early rather than assuming federal sufficiency.

## Reference Links

All links verified reachable as of July 2026. Note the FFIEC's own site (`ithandbook.ffiec.gov`) blocks automated access, so the handbook is referenced here through member-agency transmittals.

**Statute**

- [12 U.S.C. 3303 — Financial Institutions Examination Council](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section3303&num=0&edition=prelim) — establishment and membership
- [12 U.S.C. 1813 — Definitions](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section1813&num=0&edition=prelim) — subsection (q) "appropriate Federal banking agency", subsection (r) "State bank supervisor"
- [12 U.S.C. 1867 — Bank Service Company Act, regulation and examination of services](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section1867&num=0&edition=prelim)
- [12 U.S.C. 5515 — CFPB supervision of very large banks, savings associations, and credit unions](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section5515&num=0&edition=prelim)
- [12 U.S.C. 5516 — CFPB, other banks, savings associations, and credit unions](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section5516&num=0&edition=prelim)

**Rules**

- [12 CFR part 53 — Computer-Security Incident Notification (OCC)](https://www.ecfr.gov/current/title-12/chapter-I/part-53) · [§ 53.2 definitions](https://www.ecfr.gov/current/title-12/chapter-I/part-53/section-53.2) · [§ 53.3 notification](https://www.ecfr.gov/current/title-12/chapter-I/part-53/section-53.3)
- [86 FR 66424 — Computer-Security Incident Notification Requirements final rule](https://www.federalregister.gov/documents/2021/11/23/2021-25510/computer-security-incident-notification-requirements-for-banking-organizations-and-their-bank)
- [12 CFR 748.1 — NCUA security program and cyber incident report (72 hours)](https://www.ecfr.gov/current/title-12/chapter-VII/subchapter-A/part-748/section-748.1)
- [12 CFR part 30, appendix B — Interagency Guidelines Establishing Information Security Standards (OCC)](https://www.ecfr.gov/current/title-12/chapter-I/part-30/appendix-Appendix%20B%20to%20Part%2030)
- [12 CFR part 364, appendix B — Interagency Guidelines Establishing Information Security Standards (FDIC)](https://www.ecfr.gov/current/title-12/part-364/appendix-Appendix%20B%20to%20Part%20364)

**Supervisory guidance**

- [88 FR 37920 — Interagency Guidance on Third-Party Relationships: Risk Management (2023)](https://www.federalregister.gov/documents/2023/06/09/2023-12340/interagency-guidance-on-third-party-relationships-risk-management)
- [OCC Bulletin 2023-17 — transmittal of the 2023 third-party guidance, with rescissions](https://www.occ.gov/news-issuances/bulletins/2023/bulletin-2023-17.html)
- [FDIC FIL-52-2020 — FFIEC Joint Statement on Risk Management for Cloud Computing Services](https://www.fdic.gov/news/financial-institution-letters/2020/fil20052.html)
- [OCC Bulletin 2021-30 — FFIEC IT Handbook: new Architecture, Infrastructure, and Operations booklet](https://www.occ.gov/news-issuances/bulletins/2021/bulletin-2021-30.html)
- [OCC Bulletin 2019-57 — FFIEC IT Handbook: revised Business Continuity Management booklet](https://www.occ.gov/news-issuances/bulletins/2019/bulletin-2019-57.html)
- [OCC Bulletin 2024-26 — FFIEC IT Handbook: new Development, Acquisition, and Maintenance booklet](https://www.occ.gov/news-issuances/bulletins/2024/bulletin-2024-26.html)
- [SR 21-15 / CA 21-11 — community bank due diligence on financial technology companies](https://www.federalreserve.gov/supervisionreg/srletters/SR2115.htm)

## See Also

- `compliance/bank-regulatory-reporting.md` — Call Report, HMDA, CRA, BSA/AML, CECL, and the data architecture they force
- `compliance/glba.md` — the customer-information safeguards program; the Interagency Guidelines are its banking-agency implementation
- `compliance/sox.md` — ITGCs for public bank holding companies; CUEC discipline for provider attestations
- `compliance/pci-dss.md` — card data, which sits inside the same estate but under a different authority
- `compliance/dora.md` — the EU analogue; useful contrast, since DORA makes binding rules of much of what FFIEC leaves to guidance
- `compliance/soc2.md` — the attestation reports that carry most of the third-party assurance weight
- `frameworks/nist-csf-2.0.md` — the usual common control framework underneath a bank's mapping
- `general/compliance-automation.md` — automated control evidence
- `general/identity.md` — access recertification, a recurring IT exam finding
- `general/disaster-recovery.md` — resilience evidence for the BCM booklet
- `general/change-management.md` — change control over cloud resources
- `general/supply-chain-security.md` — fourth-party and subcontractor risk
- `patterns/multi-cloud.md` — concentration risk versus operational cost
- `patterns/security-operations.md` — detection and determination capability behind the 36-hour clock
- `failures/compliance.md` — compliance failure patterns
- `failures/dependencies.md` — third-party and concentration failure patterns
