# Bank Regulatory Reporting — Data Architecture Consequences

## Scope

US banks file a set of periodic regulatory reports that, taken together, impose harder data-architecture requirements than most of their customer-facing systems do. Covers the **Call Report** (FFIEC 031 / 041 / 051), **HMDA** Loan/Application Register submission, **CRA** reporting, **BSA/AML** obligations (SAR and CTR filing to FinCEN), and **CECL / ACL** allowance estimation — plus the cross-cutting requirements those filings force: reconciliation to the general ledger, record retention, lineage sufficient to answer "where did this number come from," restatement and amendment handling, and the **BCBS 239** risk-data-aggregation principles.

This page exists because regulatory reporting is the most common **legitimate** reason a bank builds a data lake or warehouse. Plenty of bank data platforms are built on a vague analytics ambition and struggle to justify themselves. CECL is different: its measurement model requires loan-level historical data with point-in-time reconstruction, and no core banking system provides that natively. That is a real architectural forcing function, and recognising it separates a defensible platform business case from a speculative one.

**Precision note.** Applicability differs sharply by institution size and charter, and several items below are in active flux as of mid-2026. Where a claim could not be confirmed against a primary source in preparing this page, it is marked **[unverified]** inline rather than stated confidently. Treat those as prompts to check, not as facts.

**Does not cover** the examination framework itself (see `compliance/ffiec.md` — read that first for who examines whom and the $10B CFPB threshold), financial-reporting ITGCs (see `compliance/sox.md`), or customer-information safeguards (see `compliance/glba.md`).

## The Call Report

The **Consolidated Reports of Condition and Income** — universally called the Call Report — is the quarterly financial and condition report filed by insured depository institutions. Per the FDIC:

> "Every national bank, state member bank, insured state nonmember bank, and savings association ('institution') is required to file Consolidated Reports of Condition and Income (a 'Call Report') as of the close of business on the last day of each calendar quarter, i.e., the report date."

Note who is **not** in that list: credit unions do not file the FFIEC Call Report. They file a separate NCUA report — commonly referred to as the 5300 Call Report, though the form designation is **[unverified]** here. Do not assume the FFIEC forms or their instructions apply to a credit union engagement.

### Which institutions file which form

Verified against the agencies' most recent Paperwork Reduction Act notice for this collection ([published 11 December 2025](https://www.federalregister.gov/documents/2025/12/11/2025-22481/proposed-agency-information-collection-activities-comment-request)), which states the form titles verbatim:

| Form | Full title | Filed by |
|---|---|---|
| **FFIEC 031** | Consolidated Reports of Condition and Income for a Bank with **Domestic and Foreign Offices** | Institutions with any foreign office |
| **FFIEC 041** | Consolidated Reports of Condition and Income for a Bank with **Domestic Offices Only** | Domestic-only institutions not eligible for the 051 |
| **FFIEC 051** | Consolidated Reports of Condition and Income for a Bank with **Domestic Offices Only and Total Assets Less Than $5 Billion** | Eligible smaller domestic-only institutions (streamlined) |

The **$5 billion** figure on the FFIEC 051 is current as of the December 2025 notice. It was lower historically, so any older reference material asserting a $1 billion threshold is stale. **Frequency of response for all three forms is quarterly.** The relative burden the agencies estimate is itself informative about form complexity — roughly 86 hours per quarter for the 031, 56 for the 041, and 35 for the 051.

The **filing deadline** (commonly cited as 30 calendar days after the report date, with a longer allowance for institutions with foreign offices) is **[unverified]** — it lives in the Call Report general instructions on the FFIEC's own site, which blocks automated access. Confirm before relying on a specific number of days.

**Active development worth tracking:** the agencies published a [Request for Information: Streamlining the Call Report](https://www.federalregister.gov/documents/2025/12/01/2025-21621/request-for-information-streamlining-the-call-report) on 1 December 2025. If you are scoping a multi-year regulatory reporting platform, the schedule set is a moving target; design for schedule change rather than hard-coding the current line items.

### What the Call Report does to a data architecture

- **It is quarterly, it is granular, and it is signed.** The report aggregates the entire balance sheet and income statement into a fixed taxonomy of schedules and line items. Every line has to trace to something.
- **The taxonomy is not your chart of accounts.** The mapping from GL accounts to Call Report line items is a maintained artifact with its own change history, and it is a frequent source of error. Treat the mapping as versioned code with review, not as a spreadsheet on someone's desktop.
- **Quarter-end is a hard boundary.** "As of the close of business on the last day of each calendar quarter" means your platform needs a defensible as-of snapshot, not a continuously-mutating current state. This is the same requirement CECL imposes for a different reason, and it is worth solving once.

## HMDA — Home Mortgage Disclosure Act

HMDA is implemented by **Regulation C, 12 CFR part 1003**, administered by the **CFPB**.

### Who reports

Under [12 CFR 1003.2(g)](https://www.ecfr.gov/current/title-12/chapter-X/part-1003/section-1003.2), a depository financial institution is covered only if it meets several criteria (asset size, office location in an MSA, federal insurance or regulation, and origination of a covered loan) **and** meets at least one of these loan-volume tests:

- "In each of the two preceding calendar years, originated **at least 25 closed-end mortgage loans**"; **or**
- "In each of the two preceding calendar years, originated **at least 200 open-end lines of credit**"

Both thresholds are as they appear in the current eCFR text. The closed-end threshold has a litigated history — a 2020 rule raised it and a subsequent court decision restored the lower figure — so material published between roughly 2020 and 2023 may cite a different number. The current text says 25.

The same two volume tests apply to nondepository institutions, with different accompanying criteria.

### Submission mechanics

[12 CFR 1003.5](https://www.ecfr.gov/current/title-12/chapter-X/part-1003/section-1003.5) sets two distinct obligations:

- **Annual.** "By **March 1** following the calendar year for which data are collected and recorded... a financial institution shall submit its annual loan/application register in electronic format to the appropriate Federal agency." An authorized representative **with knowledge of the data** must **certify to its accuracy and completeness**. The institution retains a copy **for at least three years**.
- **Quarterly.** "Within **60 calendar days** after the end of each calendar quarter **except the fourth quarter**," an institution that reported **at least 60,000 covered loans and applications, combined, excluding purchased covered loans** for the preceding calendar year must submit a quarterly LAR.

The submission must carry the institution's name, the period covered, a contact person, its appropriate Federal agency, the **total number of entries**, its Federal TIN, and its **Legal Entity Identifier (LEI)**.

### Architectural consequence

The certification is the part architects under-weight. Someone signs a personal attestation that a record-level dataset is accurate and complete. That is only reasonable if the pipeline producing the LAR is reproducible, has a record count that reconciles to the origination system, and can show what changed between a draft and the filed version. A LAR assembled by manual extract-and-massage is a certification someone is signing on faith.

The **60,000-loan quarterly threshold** is a genuine architecture trigger: it converts an annual batch process into a quarterly one with a 60-day clock, which for most institutions is the point where the manual approach stops working.

## CRA — Community Reinvestment Act

**Read this section as a status report, not as settled law.** CRA is mid-rulemaking and the answer as of mid-2026 is genuinely unsettled.

- The agencies' modernized CRA final rule, titled "Community Reinvestment Act," was **published in the Federal Register on 1 February 2024** ([FR doc 2023-25797](https://www.federalregister.gov/documents/2024/02/01/2023-25797/community-reinvestment-act)). Note the publication date: this rule is widely referred to as "the 2023 CRA rule" because the agencies adopted and announced it in October 2023, but its Federal Register publication is February 2024. Both descriptions circulate and they refer to the same rule.
- On **18 July 2025**, the OCC, Federal Reserve Board, and FDIC **proposed to rescind** it. In the agencies' own words, they propose "rescinding the final rule titled 'Community Reinvestment Act' published in the Federal Register on February 1, 2024, and replacing it with the agencies' CRA regulations in effect on **March 29, 2024**, with certain conforming and technical amendments" ([FR doc 2025-13559](https://www.federalregister.gov/documents/2025/07/18/2025-13559/community-reinvestment-act-regulations)). Comments closed 18 August 2025.
- **Whether a final rescission rule has been issued could not be confirmed in preparing this page — [unverified].** A Federal Register search for a corresponding final rule returned nothing. Confirm the current state of 12 CFR parts 25 / 228 / 345 before building anything CRA-specific.

There was also litigation against the 2024-published rule; the details and current posture are **[unverified]** here.

**Design implication:** do not hard-code CRA assessment-area logic or performance-test definitions. Whichever way the rescission lands, the definitions in force have changed at least once recently and the data model should treat them as configuration. CRA data collection obligations (small business and small farm loan registers, and their filing deadline, commonly cited as 1 March) are **[unverified]** in this page's research.

Note separately that the CFPB's small business lending data rule under **ECOA / Regulation B** (1071) is a distinct, overlapping small-business data collection with its own active rulemaking — a [final rule published 1 May 2026](https://www.federalregister.gov/documents/2026/05/01/2026-08494/small-business-lending-under-the-equal-credit-opportunity-act-regulation-b) appears in the Federal Register, but its content and compliance dates are **[unverified]** here. If small-business lending data is in scope for your engagement, research 1071 specifically; do not treat it as a CRA subset.

## BSA / AML — SAR and CTR Obligations

These are among the few areas on this page where the numbers are stable, long-settled, and precisely stated in rule. Filing is to **FinCEN**, via the [BSA E-Filing System](https://bsaefiling.fincen.gov/).

### Currency Transaction Reports

[31 CFR 1010.311](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-C/section-1010.311): each financial institution other than a casino must file a report of each deposit, withdrawal, exchange of currency, or other payment or transfer "which involves a **transaction in currency of more than $10,000**."

**More than $10,000 — not "$10,000 or more."** A transaction of exactly $10,000.00 does not meet the threshold on its face. Rule engines get this wrong in both directions, and aggregation rules (multiple transactions by or on behalf of the same person in one business day) add further nuance not detailed here.

### Suspicious Activity Reports

Two rule sets operate together and they are stated differently, which is the source of most confusion:

**FinCEN's rule for banks**, [31 CFR 1020.320](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1020/subpart-C/section-1020.320), requires reporting where a transaction "is conducted or attempted by, at, or through the bank, it **involves or aggregates at least $5,000** in funds or other assets, and the bank knows, suspects, or has reason to suspect" one of the enumerated conditions (illicit source, structuring, no apparent lawful purpose, facilitating criminal activity).

**The banking agencies' parallel rules** state tiered triggers. For national banks, [12 CFR 21.11](https://www.ecfr.gov/current/title-12/chapter-I/part-21/subpart-B/section-21.11) requires a SAR for:

1. **Insider abuse involving any amount** — where the bank has a substantial basis for identifying a director, officer, employee, agent, or other institution-affiliated party as having committed or aided a criminal act, **regardless of the amount involved**;
2. **Violations aggregating $5,000 or more where a suspect can be identified**;
3. **Violations aggregating $25,000 or more regardless of potential suspects**.

The other banking agencies maintain substantively parallel provisions for the institutions they supervise (**[unverified]** — the precise citations for the FRB, FDIC, and NCUA analogues were not confirmed here).

**Timing** (31 CFR 1020.320(b)(3)): "no later than **30 calendar days** after the date of initial detection... of facts that may constitute a basis for filing a SAR. If no suspect was identified on the date of the detection... a bank may delay filing a SAR for an **additional 30 calendar days** to identify a suspect. In no case shall reporting be delayed **more than 60 calendar days** after the date of initial detection." Violations requiring immediate attention — the rule names ongoing money laundering schemes — additionally require **immediate telephone notification** to law enforcement.

**Retention** (31 CFR 1020.320(d)): the bank keeps a copy of the SAR and "the original or business record equivalent of **any supporting documentation** for a period of **five years from the date of filing**." Supporting documentation is **deemed to have been filed with the SAR**, and must be made available to FinCEN, law enforcement, and examining authorities.

### Architectural consequence — the one that bites

That retention clause is a data-architecture requirement disguised as a recordkeeping rule. "Supporting documentation" means the evidence the analyst actually looked at: transaction records, account history, alert detail, KYC documents, the analyst's own notes. If your alerting platform retains rolling 13 months of transaction detail and your SAR is filed in month 12, you have five years of obligation against a system that will drop the evidence in one.

Design consequences:

- **Snapshot the evidence at filing time** into an immutable, separately-retained store keyed to the SAR. Do not rely on the source system still holding it.
- **The 30-day clock runs from "initial detection,"** which is a defined moment your platform should record explicitly, not reconstruct later from ticket timestamps.
- **Confidentiality is statutory.** SAR existence and content are subject to strict disclosure prohibitions. Access control on the SAR store is a legal control, not a hygiene one, and SAR data must not leak into general analytics environments, BI extracts, or model training sets.

The general BSA retention rule, [31 CFR 1010.430(d)](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-D/section-1010.430), requires **all** records retained under chapter X to be kept **five years** and, importantly, "filed or stored in such a way as to be **accessible within a reasonable period of time**." Deep-archive tiers with multi-hour or multi-day restore times are a live compliance question, not just a cost optimization. Address it in the storage-tiering ADR. See `general/storage.md` and `general/legal-hold.md`.

FinCEN's AML/CFT program rulemaking has been active recently; the status of any final AML program rule is **[unverified]** here and deliberately not asserted.

## CECL — The Reason Banks Build Data Platforms

**CECL** (Current Expected Credit Losses) comes from FASB **ASU 2016-13**, "Financial Instruments—Credit Losses (Topic 326): Measurement of Credit Losses on Financial Instruments," codified as **FASB ASC Topic 326**. The banking agencies — OCC, Federal Reserve, FDIC, **and NCUA** — jointly issued the [Interagency Policy Statement on Allowances for Credit Losses (Revised April 2023)](https://www.federalregister.gov/documents/2023/04/27/2023-08876/interagency-policy-statement-on-allowances-for-credit-losses-revised-april-2023) at 88 FR 25479, superseding their original statement at 85 FR 32991 (1 June 2020). Because NCUA is a party, this applies to credit unions as well as banks.

**Terminology moved.** The incurred-loss-era term was **ALLL** (allowance for loan and lease losses). Under Topic 326 the term is **ACL** — allowance for credit losses. Encountering ALLL in a bank's data dictionary is a reliable sign the model or the documentation predates CECL adoption.

**Effective dates are [unverified] here.** ASU 2016-13 adoption was phased by filer category over several years, and the agencies adopted regulatory-capital transition relief in separate rulemakings (Federal Register titles including "Regulatory Capital Rule: Revised Transition of the Current Expected Credit Losses Methodology for Allowances," published 30 September 2020, and NCUA's "Transition to the Current Expected Credit Loss Methodology," published 1 July 2021 — titles observed, **contents not read**). The commonly cited three-year capital phase-in and the CARES Act delay option are **not asserted here**. If an adoption date or transition length is load-bearing for your work, confirm it against FASB and the relevant capital rule directly.

### What the measurement model actually requires

From the interagency policy statement, quoting its own language:

- An ACL is "a valuation account that is deducted from, or added to, the amortized cost basis of financial assets to present the **net amount expected to be collected over the contractual term** of the assets."
- In estimating that amount, "management should consider the effects of **past events, current conditions, and reasonable and supportable forecasts** on the collectibility of the institution's financial assets."
- "FASB ASC Topic 326 requires management to use relevant **forward-looking information** and expectations drawn from reasonable and supportable forecasts when estimating expected credit losses."
- Topic 326 "requires an institution to measure estimated expected credit losses **over the contractual term** of its financial assets, **considering expected prepayments**." Renewals, extensions, and modifications are excluded from the contractual term unless they are part of the original or modified contract and are **not unconditionally cancellable** by the institution.
- "**Historical loss information** generally provides a basis for an institution's assessment of expected credit losses," drawn from internal information, external information, or both — and adjusted where current asset-specific characteristics differ (underwriting standards, portfolio mix, and similar).

The policy statement names several acceptable loss-rate approaches, including the **weighted-average remaining maturity (WARM)** method, **vintage analysis**, and the **snapshot / open pool** method.

### Why this forces loan-level data with point-in-time reconstruction

This is the core claim of the page, so it is worth stating precisely rather than as a slogan.

The incurred-loss model that CECL replaced was, in data terms, cheap. It asked what losses had already been incurred as of the balance sheet date. A pool-level reserve rate applied to current balances could support it, and current balances are exactly what a core banking system holds.

CECL asks a structurally different question: **what will be lost over the remaining contractual term of every asset currently held**, given past events, current conditions, and a forecast. Answering it requires:

1. **Loan-level granularity, not pool-level.** Contractual term, remaining maturity, prepayment behaviour, and risk characteristics vary per loan. Vintage analysis and WARM both operate on cohorts defined by loan attributes, which means you need the attributes on each loan, not a pool average.
2. **Historical loss experience over a full period, at the same granularity.** You cannot calibrate an expected-loss model on a snapshot. You need the performance history — origination characteristics, subsequent status transitions, charge-offs, recoveries — for loans that have already run their course.
3. **Point-in-time reconstruction.** This is the requirement that breaks conventional core-banking data. To build a vintage curve you must answer "what did this loan's risk grade, balance, delinquency status, and collateral value look like **as of the end of Q3 four years ago**." A core system holds *current* state. It overwrites. Risk grades get updated in place; balances change; borrower attributes are corrected. Without a deliberate history-preserving design, the past is simply gone.
4. **Reproducibility of a prior estimate.** The allowance is a signed number in a filed report and is examined. When an examiner or auditor asks how last quarter's ACL was derived, you must be able to re-run it — same input data, same model version, same assumptions — and obtain the same answer.

Those four requirements together describe a **slowly-changing-dimension, append-only, as-of-queryable historical store** — that is, a data warehouse or lakehouse. That is why CECL is the most common legitimate driver for a bank to build one. The business case does not rest on analytics aspiration; it rests on a measurement standard the institution cannot satisfy from its transactional systems.

Two cautions against over-reading this:

- **A smaller institution may reasonably satisfy CECL with far less.** The interagency statement's inclusion of WARM is significant: WARM is deliberately tractable and is workable for a community institution with a simpler portfolio. "CECL therefore requires a lakehouse" is wrong at the low end. Scale the platform to the portfolio's complexity.
- **CECL alone rarely justifies the whole platform.** It justifies the historical loan-level store and the reproducibility machinery. Extending that into a general enterprise data platform is a separate decision needing separate justification. See `general/data.md` and `patterns/data-pipeline.md`.

## Cross-Cutting Requirements

### Reconciliation to the general ledger

Every filed financial report must tie to the institution's books. Reported figures are certified, examined, and cross-checked against the GL and against prior periods.

**The specific instruction language mandating reconciliation is [unverified] here** — the Call Report general instructions are hosted on the FFIEC's site, which blocks automated retrieval. What is verified is the surrounding structure: the report is filed as of a fixed quarter-end date, and HMDA's Regulation C explicitly requires an authorized representative with knowledge of the data to certify to its accuracy and completeness. Treat GL reconciliation as a hard design requirement on that basis, and confirm the precise instruction text if you need to quote it.

Architecturally this means:

- **The reconciliation is a first-class pipeline output, not a manual month-end check.** Produce a control total per reported line item and a documented variance against the GL, automatically, every cycle.
- **Tolerances must be explicit and approved.** An unexplained variance is a finding whether or not it is material.
- **Reconciliation must survive replay.** If you re-run a period, the reconciliation must re-run with it and produce the same result.

### Lineage — answering "where did this number come from"

This is the question that arrives from an examiner, an internal auditor, an external auditor, and the CFO, and it is asked about a specific cell in a specific filed report, often for a period that closed some quarters ago.

Answering it requires, at minimum:

- **Column- and row-level lineage** from the reported line item back through every transformation to the source-system record. Table-level lineage is not sufficient; the question is about a number, not a dataset.
- **Version pinning of transformation logic.** The mapping in force at the time of filing, not the mapping in force today. This is a compelling reason to hold reporting transformations in version control with tagged releases rather than in a BI tool's ad-hoc layer.
- **Input data immutability for the filed period.** If the inputs have since changed, you can no longer reproduce the filing.
- **Preservation of the filed artifact itself.** Keep exactly what was submitted, not a regenerated approximation.

See `general/data.md` and `general/governance.md`.

### Record retention

Verified retention periods:

| Item | Period | Source |
|---|---|---|
| BSA records generally (chapter X) | **5 years**, stored so as to be **accessible within a reasonable period of time** | [31 CFR 1010.430(d)](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-D/section-1010.430) |
| SAR copy + **supporting documentation** | **5 years from the date of filing** | [31 CFR 1020.320(d)](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1020/subpart-C/section-1020.320) |
| HMDA annual LAR copy | **at least 3 years** | [12 CFR 1003.5(a)(1)(i)](https://www.ecfr.gov/current/title-12/chapter-X/part-1003/section-1003.5) |

Retention periods for **Call Report workpapers and CRA records were not confirmed and are [unverified]** here. Do not assume a single institution-wide retention period satisfies everything; the periods differ by regime, and the longest applicable one governs any given record. Note also that SOX-driven retention for a public bank holding company runs on its own clock (see `compliance/sox.md`), and litigation holds override all of it (see `general/legal-hold.md`).

### Restatements and amendments

Filed reports get corrected. The Call Report amendment mechanism (amended filings through the agencies' Central Data Repository) and any stated expectation to amend are **[unverified]** here — confirm against the current instructions.

What is not in doubt is the architectural requirement, which holds regardless of the mechanism:

- **Never overwrite a filed period.** Model the filing as an immutable versioned artifact — original, amendment 1, amendment 2 — each independently reproducible.
- **Restatement must be a first-class pipeline operation**, not a manual patch. The corrected figures must be derivable from corrected inputs by the same logic.
- **Keep the reason.** A restatement is accompanied by an explanation, and the explanation is examined alongside the number.
- **Downstream propagation is your problem.** A restated Call Report figure may feed capital ratios, deposit-insurance assessments, and public disclosures. Know what consumes each figure before you have to restate one.

## BCBS 239 — Be Precise About Who It Binds

**[Principles for effective risk data aggregation and risk reporting](https://www.bis.org/publ/bcbs239.pdf)**, Basel Committee on Banking Supervision, published **9 January 2013**. It comprises **14 Principles**. Principles 1–11 are addressed to banks; Principles 12–14 are addressed to supervisors — Principle 12 says supervisors "should periodically review and evaluate a bank's compliance with the **eleven Principles above**," which is the document's own confirmation of that split.

| # | Principle |
|---|---|
| 1 | Governance |
| 2 | Data architecture and IT infrastructure |
| 3 | Accuracy and Integrity |
| 4 | Completeness |
| 5 | Timeliness |
| 6 | Adaptability |
| 7 | Accuracy |
| 8 | Comprehensiveness |
| 9 | Clarity and usefulness |
| 10 | Frequency |
| 11 | Distribution |
| 12 | Review *(supervisors)* |
| 13 | Remedial actions and supervisory measures *(supervisors)* |
| 14 | Home/host cooperation *(supervisors)* |

### Applicability — the part people get wrong

Quoting the document directly:

- Paragraph 14: "Banks identified as **G-SIBs** by the FSB in November 2011 or November 2012 **must meet these Principles by January 2016**; G-SIBs designated in subsequent annual updates will need to meet the Principles **within three years of their designation**."
- Paragraph 15: "It is **strongly suggested** that national supervisors **also apply these Principles to banks identified as D-SIBs** by their national supervisors three years after their designation as D-SIBs."

And separately, supervisors "may nevertheless choose to apply the Principles to a wider range of banks, in a way that is **proportionate to the size, nature and complexity** of these banks' operations."

So, precisely:

- **G-SIBs:** binding, on a defined timeline.
- **D-SIBs:** strongly suggested to national supervisors — an expectation transmitted through the supervisor, not a direct obligation from Basel.
- **Everyone else:** at national supervisory discretion, and explicitly proportionate.
- **A US community bank is not a BCBS 239 institution.** Citing BCBS 239 as a requirement at a $2B community bank is wrong, and it is a costly kind of wrong — the Principles imply an investment in data architecture, lineage, and reporting infrastructure that is unjustifiable at that scale. Equally, treating a G-SIB's risk-data-aggregation obligations as optional is wrong in the other direction.

Note also that BCBS 239 is a Basel Committee standard, not US law. Its force in any jurisdiction comes from how the national supervisor has adopted it. **The specific mechanism by which US supervisors give effect to BCBS 239 was not confirmed here — [unverified].**

### What it asks for, for those in scope

Principle 2 (Data architecture and IT infrastructure) is the one aimed squarely at architects: a bank should design, build, and maintain data architecture and IT infrastructure that fully supports its risk-data-aggregation capabilities **both in normal times and during times of stress or crisis**. The stress clause matters — an aggregation capability that works at month-end but cannot produce a firm-wide exposure view on demand during a crisis does not satisfy it. In practice this pushes toward automated aggregation over manual consolidation, a single authoritative source per risk data element, and the ability to produce ad-hoc aggregations quickly.

## Architect Checklist

- [ ] **[Critical]** **Establish the institution's charter, size, and reporting profile first** — which Call Report form, whether HMDA-covered, whether BCBS 239 applies, whether above the $10B CFPB threshold (see `compliance/ffiec.md`). Every downstream decision depends on it, and advice calibrated for the wrong tier is actively harmful.
- [ ] **[Critical]** **Design for point-in-time reconstruction from the start.** Append-only history with as-of query capability for loan-level data is close to impossible to retrofit, because the history you failed to capture no longer exists. This is the single highest-leverage decision on this page.
- [ ] **[Critical]** **Make regulatory reporting transformations version-controlled, reviewed code** with tagged releases per filing period — not BI-layer logic or spreadsheets. Lineage and restatement both depend on it.
- [ ] **[Critical]** **Build GL reconciliation as an automatic pipeline output** with per-line-item control totals, explicit approved tolerances, and documented variances every cycle.
- [ ] **[Critical]** **Snapshot SAR supporting documentation at filing time** into an immutable store retained five years, keyed to the SAR. Do not depend on the source system's retention.
- [ ] **[Critical]** **Enforce SAR confidentiality as an access-control boundary.** SAR data must not flow into general analytics, BI extracts, or model training. Treat it as its own security domain.
- [ ] **[Critical]** **Model filed reports as immutable versioned artifacts** — original plus amendments, each independently reproducible from pinned inputs and pinned logic.
- [ ] **[Critical]** **Verify retention tiering against the "accessible within a reasonable period of time" requirement** in 31 CFR 1010.430(d) before moving BSA records to deep archive.
- [ ] **[Recommended]** **Treat the GL-to-Call-Report line item mapping as a reviewed, versioned artifact** with change history. It is a top source of reporting error and it changes when the schedules change.
- [ ] **[Recommended]** **Implement column-level lineage** from reported figure back to source record. Table-level lineage does not answer the question that actually gets asked.
- [ ] **[Recommended]** **Instrument the HMDA LAR pipeline for certification** — reproducible run, record count reconciled to the origination system, and a diff between draft and filed versions.
- [ ] **[Recommended]** **Record "initial detection" as an explicit, stored event** in the AML platform. The 30-day SAR clock runs from it and reconstructing it later from ticket metadata is not defensible.
- [ ] **[Recommended]** **Keep CRA and 1071 assessment logic in configuration, not code paths.** The rules have changed recently and a rescission is pending.
- [ ] **[Recommended]** **Right-size the CECL platform to portfolio complexity.** WARM is an accepted method and is workable for a simpler portfolio; do not sell a lakehouse where a well-governed loan-level history and a documented WARM calculation would satisfy the standard.
- [ ] **[Optional]** **For BCBS 239 institutions, test aggregation under stress conditions**, not just at month-end. Principle 2 explicitly contemplates crisis-time capability.
- [ ] **[Optional]** **Track the Call Report streamlining RFI** if scoping a multi-year reporting platform; design the schedule set as data rather than as structure.

## Why This Matters

Regulatory reporting failures do not usually present as outages. They present as an examiner asking a question the institution cannot answer, and the consequences follow the supervisory path described in `compliance/ffiec.md` — findings, MRAs, and in serious cases enforcement.

Specific to reporting:

- **Reporting errors are examined and corrected in public.** A restated Call Report is visible.
- **Wrong numbers propagate.** Call Report figures feed capital ratios and deposit-insurance assessments; an error is rarely contained to the report that carried it.
- **Certification is personal.** HMDA requires an authorized representative to certify accuracy and completeness. Someone's name is on it, and "the pipeline produced it" is not a defence anyone will find comforting.
- **BSA/AML failures carry the heaviest penalties in this space.** AML enforcement actions against institutions have historically produced very large monetary penalties, and unlike most items here the obligations are rule-based rather than guidance-based.
- **The evidence problem is usually the real problem.** In practice, institutions rarely fail because the number was wrong. They fail because they cannot demonstrate how the number was produced, three quarters after the fact, with the people who produced it no longer in the role. That is an architecture problem and it is solvable in advance.

## Common Decisions (ADR Triggers)

- **Point-in-time history: capture-everything versus capture-what-CECL-needs** — capturing everything is simpler to reason about and expensive; scoping to the risk-relevant attributes is cheaper and risks a gap you discover four years later when you need the history and it does not exist. Bias toward over-capture on loan-level attributes specifically; the asymmetry is severe.
- **Warehouse versus lakehouse versus in-core reporting** — for a smaller institution with a simple portfolio, a well-governed loan-level historical store plus a documented calculation may be sufficient. Do not default to a platform build.
- **Build versus buy for regulatory reporting** — vendor reporting products handle schedule changes for you and constrain your data model. Assess against how much your institution's product set deviates from vanilla.
- **Where the golden source of each risk data element lives** — BCBS 239 Principle 2 effectively asks this question directly, and it is worth answering explicitly even below BCBS 239 scope.
- **Retention tiering under the accessibility constraint** — cold and archive tiers against the 31 CFR 1010.430(d) "accessible within a reasonable period of time" requirement. Get the tier-restore SLA agreed and documented rather than assumed.
- **SAR data isolation** — separate store and separate access domain versus row-level security within the main platform. Separation is more defensible and more operationally annoying; decide deliberately.
- **Restatement handling** — full pipeline replay versus targeted correction. Replay is more defensible and more expensive; targeted correction is faster and harder to evidence.
- **Model risk management for CECL** — the CECL estimate is a model output and falls under model risk management expectations. Decide early who owns validation, and how model versions are pinned to filed periods.

## Reference Links

All links verified reachable in preparing this page. Note that the FFIEC's own site (`ffiec.gov`, which hosts the Call Report forms and instructions) blocks automated access, which is why several Call Report specifics above are marked unverified.

**Call Report**

- [Proposed Agency Information Collection Activities; Comment Request (11 Dec 2025)](https://www.federalregister.gov/documents/2025/12/11/2025-22481/proposed-agency-information-collection-activities-comment-request) — states the FFIEC 031 / 041 / 051 form titles and the $5 billion FFIEC 051 threshold verbatim
- [FDIC — Bank Financial Reports](https://www.fdic.gov/bank-financial-reports) — who must file, forms and instructions by quarter
- [Request for Information: Streamlining the Call Report (1 Dec 2025)](https://www.federalregister.gov/documents/2025/12/01/2025-21621/request-for-information-streamlining-the-call-report)

**HMDA**

- [12 CFR part 1003 — Regulation C](https://www.ecfr.gov/current/title-12/chapter-X/part-1003)
- [12 CFR 1003.2 — definitions, including the 25 closed-end / 200 open-end coverage tests](https://www.ecfr.gov/current/title-12/chapter-X/part-1003/section-1003.2)
- [12 CFR 1003.5 — disclosure and reporting, annual and quarterly submission](https://www.ecfr.gov/current/title-12/chapter-X/part-1003/section-1003.5)

**CRA**

- [Community Reinvestment Act final rule, published 1 Feb 2024](https://www.federalregister.gov/documents/2024/02/01/2023-25797/community-reinvestment-act)
- [Community Reinvestment Act Regulations — proposed rescission, 18 Jul 2025](https://www.federalregister.gov/documents/2025/07/18/2025-13559/community-reinvestment-act-regulations)
- [Small Business Lending Under the Equal Credit Opportunity Act (Regulation B), 1 May 2026](https://www.federalregister.gov/documents/2026/05/01/2026-08494/small-business-lending-under-the-equal-credit-opportunity-act-regulation-b) — the separate 1071 collection

**BSA / AML**

- [31 CFR 1010.311 — CTR, transactions in currency of more than $10,000](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-C/section-1010.311)
- [31 CFR 1020.320 — SAR by banks: thresholds, 30/60-day timing, five-year retention](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1020/subpart-C/section-1020.320)
- [31 CFR 1010.430 — record retention, five years, accessible within a reasonable period](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-D/section-1010.430)
- [12 CFR 21.11 — OCC SAR rule with the any-amount / $5,000 / $25,000 tiers](https://www.ecfr.gov/current/title-12/chapter-I/part-21/subpart-B/section-21.11)
- [FinCEN BSA E-Filing System](https://bsaefiling.fincen.gov/)

**CECL / ACL**

- [Interagency Policy Statement on Allowances for Credit Losses (Revised April 2023), 88 FR 25479](https://www.federalregister.gov/documents/2023/04/27/2023-08876/interagency-policy-statement-on-allowances-for-credit-losses-revised-april-2023)

**BCBS 239**

- [Principles for effective risk data aggregation and risk reporting (overview)](https://www.bis.org/publ/bcbs239.htm)
- [Principles for effective risk data aggregation and risk reporting (full text, PDF)](https://www.bis.org/publ/bcbs239.pdf)

## See Also

- `compliance/ffiec.md` — the examination framework: who examines whom, the IT Handbook, the $10B CFPB threshold, incident notification
- `compliance/sox.md` — ITGCs and 7-year retention for a public bank holding company; the reporting pipeline is in SOX scope too
- `compliance/glba.md` — customer information safeguards over the same data estate
- `compliance/pci-dss.md` — card data, a different authority over an adjacent dataset
- `general/data.md` — data platform architecture and lineage
- `general/data-analytics.md` — warehouse and lakehouse selection
- `general/data-classification.md` — classifying SAR, HMDA, and customer data
- `general/storage.md` — retention tiering against the accessibility constraint
- `general/legal-hold.md` — holds that override retention schedules
- `general/governance.md` — data governance and ownership of risk data elements
- `patterns/data-pipeline.md` — pipeline patterns for reproducible, replayable reporting
- `failures/data.md` — data failure patterns
- `failures/compliance.md` — compliance failure patterns
