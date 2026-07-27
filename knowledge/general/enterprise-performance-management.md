# Enterprise Performance Management (EPM)

## Scope

Covers the enterprise performance management category — the finance-owned systems that hold
**driver-based planning and budgeting, rolling forecasts, financial consolidation and close,
allocations, what-if and scenario modelling, and target setting**. Covers the multidimensional
(OLAP) modelling style these tools use, why the model belongs to finance rather than to a data
team, how EPM and an analytics data platform differ, where they genuinely overlap, and the
integration pattern that makes them work together instead of against each other.

The category is also sold as *corporate performance management* (CPM), *extended planning and
analysis* (xP&A), and — for the planning half only — *financial planning and analysis* (FP&A)
software. Treat those as marketing partitions of the same architecture problem.

**This file exists mainly to settle one argument.** "We already have an EPM tool, why do we need
a data platform?" and "the data platform will replace the EPM tool" are both common, both wrong,
and both derail platform decisions. The section
[EPM Versus an Analytics Platform](#epm-versus-an-analytics-platform) is the answer to both, and
it is the reason to read this file rather than a vendor comparison.

This file does **not** cover analytical platform selection — see
`patterns/data-platform-selection.md`, which this file pairs with. For the dimensional modelling
vocabulary that EPM cubes share with warehouse stars, see `general/data-modelling.md`; that file
is the reference for grain, conformed dimensions, slowly changing dimensions and fact-table
design, and this one deliberately does not repeat it. For the platform that supplies EPM its
actuals, see `general/data-analytics.md` and `general/data-ingestion.md`. For the control
environment a consolidation system sits inside, see `compliance/sox.md`.

**Statements marked [verified] in this file were read from the cited vendor page on 2026-07-26.**
Statements marked **[assessment]** are judgement. This market renames products frequently — the
same engine has been sold under three names in a decade at more than one vendor — so treat any
undated capability claim in *any* comparison, including this one, as needing a re-check.

## Overview

An EPM tool is not a reporting tool that finance happens to own. It is a different machine, and
the difference is visible in one sentence: **an analytics platform's fundamental unit is an
immutable fact appended to a table; an EPM tool's fundamental unit is a mutable cell that a named
person is accountable for.** Every structural difference between the two categories follows from
that.

If a cell is mutable and a human owns it, you need cell-level ownership, locking, approval state,
validation on submit, and an audit trail of who changed what — transaction-processing machinery,
not analytics machinery. If changing one cell must instantly propagate through the whole
dependency graph so the person who typed it sees the consequence, you need a calculation engine
that holds the graph in memory and recalculates on write. That is why every serious EPM vendor
ships a proprietary in-memory multidimensional engine and none of them ships "just SQL": Oracle
has Essbase, Anaplan has Hyperblock (in two variants), IBM has TM1, Workday has Elastic Hypercube.
Columnar analytical engines are optimised for exactly the opposite profile — large scans, bulk
loads, no per-cell ownership.

The practical consequence for an architect is that **running both is the normal end state, not a
transitional one**, and the integration between them is the design problem worth spending time on.
The rest of this file is about doing that well and about being able to say precisely why, in a
room where the finance organisation owns the EPM tool, the budget, and the veto.

## Checklist

### Scoping the workload

- [ ] **[Critical]** Which of the EPM workloads is actually in scope — **planning and budgeting**,
      **rolling forecast**, **statutory consolidation and close**, **allocations and
      profitability**, **scenario and what-if modelling**, **target setting** — and which are
      merely aspirational? These have different owners, different cadences, and different
      regulatory exposure. A consolidation requirement changes the candidate list far more than a
      budgeting requirement does; a scoping document that says "EPM" without naming the workloads
      is not a scope.
- [ ] **[Critical]** Is this a **write-back workload with human-entered data**, or is it reporting
      on numbers that already exist elsewhere? This single question separates EPM from analytics
      and it decides the architecture. If nobody types a number that did not previously exist,
      you may not need an EPM tool at all.
- [ ] **[Critical]** How many people will enter data, in what window, and with what approval
      structure? Budget submission is a concurrency problem with a deadline — dozens or hundreds
      of people editing overlapping intersections in the same fortnight, each responsible for
      their own slice. Sizing a planning tool on data volume rather than on concurrent accountable
      editors is the standard way to get the sizing wrong.
- [ ] **[Critical]** Is there a **statutory close** with intercompany elimination, currency
      translation, ownership percentages and non-controlling interest — or only a management
      rollup? Management rollup is arithmetic. Statutory consolidation is accounting-standard
      territory, auditable, and in scope for internal control over financial reporting. Tools
      that do the former well often do not do the latter at all.
- [ ] **[Recommended]** Does the plan need to be **driver-based**, and if so, do the drivers exist
      as data anywhere? Driver-based planning needs headcount, volumes, units, rates and prices at
      a usable grain. If those live only in operational systems that nobody has ever landed, the
      driver-based ambition is a data-platform project wearing an EPM project's clothes.
- [ ] **[Recommended]** What forecast cadence is genuinely required — annual budget, quarterly
      reforecast, monthly rolling, or continuous? Cadence drives the automation requirement far
      more than model complexity does, because a monthly cycle survives manual steps and a
      continuous one does not.
- [ ] **[Optional]** Are there non-finance planning domains in scope (workforce, supply, sales
      capacity, project portfolio)? Several vendors sell "connected planning" across these; the
      integration benefit is real, and so is the risk of buying a suite for one module's sake.

### Model ownership and governance

- [ ] **[Critical]** Who owns the model — named, in finance — and who owns the platform it runs
      on? These are different roles and both must exist. An EPM model with no finance owner
      degrades into a reporting cube; an EPM model with no platform owner degrades into an
      unpatched, unversioned single point of failure.
- [ ] **[Critical]** Is it understood that the model encodes **business logic and accountability**,
      not just data structure? The approval hierarchy, the ownership of each line, the allocation
      bases, the transfer-pricing rules and the FX rate policy are all *policy* expressed as
      configuration. This is why an EPM model does not migrate cleanly into a general-purpose
      platform — see the ownership section below.
- [ ] **[Critical]** Are the model's calculation assets — calculation scripts, business rules,
      allocation definitions, mapping tables — held in **version control with a test harness**?
      They are code. They are almost never treated as code. This is the highest-value, lowest-cost
      governance intervention available in an EPM estate and the one most consistently absent.
- [ ] **[Critical]** Who governs the **dimensions and hierarchies** — chart of accounts, legal
      entity, management hierarchy, cost centre — and is that the same governance that the data
      platform's conformed dimensions use? Two independently maintained hierarchies for the same
      real-world structure guarantee that finance and analytics disagree at the next
      reorganisation. See `general/data-governance.md`.
- [ ] **[Recommended]** Are **alternate hierarchies** required — statutory rollup, management
      rollup, planning rollup over the same base members? EPM engines handle this natively with
      shared members; a single conformed star dimension does not, and the star-schema equivalent
      (bridge or closure tables, per `general/data-modelling.md`) is materially more work.
- [ ] **[Recommended]** Is there a documented **model change process** with a test environment and
      a promotion path? A change to an allocation rule in the middle of a close is a production
      change to a financial reporting system. See `general/change-management.md`.
- [ ] **[Optional]** Is there a named successor for every person who is currently the only one who
      understands part of the model? Key-person concentration is the defining operational risk of
      this category and it is rarely on the risk register.

### Multidimensional design

- [ ] **[Critical]** Has the **leaf-level intersection** of the cube been declared explicitly —
      the equivalent of declaring fact-table grain? Every storage, calculation and performance
      property follows from it, and like grain it is expensive to change later. See
      `general/data-modelling.md` for why this decision outlives every platform choice around it.
- [ ] **[Critical]** For engines that expose it, has the **sparse versus dense** split been
      designed rather than defaulted? In Oracle Essbase block storage, block size follows the
      dense dimensions and block count follows the populated sparse combinations, so the split
      determines storage footprint and calculation time by orders of magnitude. **[verified]**
      Oracle documents that "Essbase creates a data block for each unique combination of sparse
      standard dimension members (providing that at least one data value exists for the sparse
      dimension member combination)" and that "Each data block is a multidimensional array that
      contains a fixed, ordered location for each possible combination of dense dimension
      members."
- [ ] **[Critical]** Is the **calculation order** understood and documented, including which
      members are stored versus dynamically calculated and what the solve order is for members
      that could be computed more than one way? Order-dependent imperative calculation is the
      normal state of these models and the normal cause of numbers that are wrong only in certain
      cells.
- [ ] **[Critical]** Are **scenario and version** first-class dimensions, with a defined lifecycle
      for each (draft, submitted, approved, locked, archived)? Planning without versioning is not
      auditable, and "which forecast was that?" is a question asked after the fact, when it is too
      late to reconstruct.
- [ ] **[Recommended]** Are **semi-additive measures** — balances, headcount, inventory levels —
      identified and given correct time aggregation? This is the same defect class as in
      dimensional modelling, and it is more common in cubes because a cube will happily sum a
      balance across twelve months and present the result without complaint.
- [ ] **[Recommended]** Have the **aggregation operators per child member** been reviewed
      (addition, subtraction, ignore, never)? These are how a cube expresses a chart of accounts
      where expenses reduce a subtotal, and a wrong operator produces a plausible-looking number
      that is wrong by exactly twice the line.
- [ ] **[Recommended]** Is dimension **cardinality growth** projected? Cubes degrade
      non-linearly as sparse dimensions grow — a product dimension going from hundreds to hundreds
      of thousands of members is a redesign, not a data load.
- [ ] **[Optional]** Is there a defined position on **where aggregation happens** — stored,
      dynamically calculated at query time, or pre-aggregated on load? Every engine offers a mix
      and the mix is a tuning decision with a maintenance cost attached.

### Integration with the data platform

- [ ] **[Critical]** Is the data platform the **source of actuals** for EPM, rather than EPM
      extracting independently from each source system? Independent extraction produces a second
      mapping of the general ledger, and two mappings produce two versions of revenue. This is
      the single most valuable integration decision in the file.
- [ ] **[Critical]** Does the **plan, budget and forecast flow back into the platform** for
      variance reporting and downstream consumption? EPM output is an input to analytics. If it
      does not flow back, every plan-versus-actual report gets rebuilt inside the EPM tool, badly,
      and the platform's variance reporting is permanently stale.
- [ ] **[Critical]** For each of **actuals, plan, and the plan-versus-actual comparison**, which
      system is the book of record? Write it down once. Two systems computing variance from two
      mappings is the most common way finance and analytics arrive at a meeting with different
      numbers on the same slide.
- [ ] **[Critical]** Where does the **GL-account-to-EPM-account mapping** live, and is it a single
      versioned artefact consumed by both sides? If EPM's mapping lives in the EPM tool and the
      platform's lives in the transformation layer, they diverge at the next chart-of-accounts
      change and nobody notices until the reconciliation fails.
- [ ] **[Recommended]** Is the **aggregation from transaction grain to cube grain** performed in
      the platform, where it is testable and reconcilable, rather than inside the EPM tool's data
      load rules, where it usually is not?
- [ ] **[Recommended]** Is the integration **cadence** matched to the business process — actuals
      after close rather than continuously, plan versions after approval rather than mid-edit? A
      streaming pipeline into a planning cube solves a problem nobody has and creates several.
- [ ] **[Recommended]** Has the **security model mismatch** been addressed? EPM security is
      cell-level by entity, scenario and version, and by approval role; platform security is
      table, row and column. Synchronising a plan into a lake without re-applying classification
      exposes a draft budget to everyone with warehouse access. See
      `general/data-classification.md`.
- [ ] **[Optional]** Is master-data alignment handled by a dedicated tool or process rather than by
      hand? Several EPM suites ship one specifically for this (Oracle sells Enterprise Data
      Management as a Cloud EPM module); the alternative is a spreadsheet of hierarchy changes
      emailed monthly.

### Close, controls, and evidence

- [ ] **[Critical]** Is the **close orchestrated** — tasks with owners, dependencies, relative-day
      scheduling, approval and sign-off — or is it run from a shared spreadsheet and a recurring
      meeting? **[verified]** Oracle's Task Manager documents templates that "define a repeatable
      set of tasks required for a business process", and schedules that map relative dates such as
      "Day 1 and 2 of the business process to calendar dates". This capability is a large part of
      what separates a consolidation product from a reporting cube.
- [ ] **[Critical]** Is the EPM system in **internal-control-over-financial-reporting scope**, and
      have its IT general controls been designed accordingly — access, change management, and
      evidence of both? A consolidation engine that produces the statutory result is a financial
      reporting system. See `compliance/sox.md`.
- [ ] **[Critical]** Can the system evidence **who changed which number, when, and with what
      approval**, for a period that has since closed? This is the question an auditor asks, and
      "the data is in the cube" is not an answer to it.
- [ ] **[Recommended]** Are **top-side journals and adjustments** captured inside the tool rather
      than applied by hand to the output? **[verified]** Oracle documents that adjustments are
      entered through journals both before and after the consolidation process runs. Adjustments
      made outside the system are invisible to reconciliation and to the auditor.
- [ ] **[Recommended]** Is **period locking** enforced, and is there a defined and evidenced
      re-open process? A period that can be silently re-opened is a period whose reported result
      cannot be reproduced.
- [ ] **[Optional]** Is there a retention position for closed-period plan and consolidation data,
      consistent with the organisation's records obligations? See `general/legal-hold.md`.

### Implementation and operations

- [ ] **[Critical]** Is the implementation estimate built on **number of rules and owners**, not
      number of rows? The effort driver in an EPM programme is logic archaeology — enumerating and
      re-certifying business rules that currently exist only as scripts and one person's memory.
      Row counts are close to irrelevant and estimates built on them are close to always wrong.
- [ ] **[Critical]** Is there a **parallel-run period with full tie-out** to the incumbent before
      cutover? The acceptance criterion for an EPM cutover is "the numbers match", which is binary
      and unforgiving in a way that analytics cutovers are not.
- [ ] **[Critical]** Which decisions are **irreversible after go-live** on the chosen tool, and
      have they been made deliberately? Examples that are verified rather than folklore: Essbase
      dense/sparse configuration, and Anaplan's engine choice — **[verified]** "Workspaces are
      either a Classic workspace or a Polaris workspace, and one workspace cannot have both
      Classic and Polaris models", and "You cannot convert a Classic Workspace into a Polaris
      workspace or a Polaris workspace into a Classic workspace."
- [ ] **[Recommended]** Is there a named administrator who can perform the vendor's documented
      **routine optimisation** work? **[verified]** Oracle publishes a BSO cube optimisation
      procedure involving an explicit dense restructure, a Block Analysis report identifying
      zero-only blocks and repeated values, replacement of zero blocks with `#missing`, and
      changing consolidation operators to `Never` for non-numeric data types. A product that
      publishes that procedure needs somebody who knows it.
- [ ] **[Recommended]** Is deployment automated through the vendor's API or automation tool rather
      than performed by hand in the interface? Reproducible deployment is what makes the test
      environment meaningful.
- [ ] **[Recommended]** Has the **Excel dependency** been designed for rather than fought? Every
      major vendor ships an Excel add-in as a first-class client. A proposal that promises to
      "get finance off Excel" is promising something the vendors themselves do not promise.
- [ ] **[Optional]** Is there a defined position on what happens to the spreadsheets that will
      continue to exist around the tool — where they are stored, who reviews them, and which ones
      are load-bearing?

## Why This Matters

**Getting the EPM-versus-analytics distinction wrong costs credibility with the one function that
can stop the programme.** Finance usually owns the EPM tool, its budget, and a veto over anything
that touches the close. An architect who implies the finance team's tool is a legacy artefact
awaiting rationalisation has lost the room, and has also said something false. The inverse error
is just as damaging and more expensive: agreeing that the EPM tool can serve as the enterprise
analytics platform commits the organisation to answering cross-domain questions from a cube that
only ever contained a summarised chart-of-accounts view of one function's data. Both errors are
avoided by the same five minutes of precision about what each system is for.

**Planning models fail at the point where nobody can explain them.** The business logic in an EPM
model is real code — order-dependent, imperative, mutating shared state — and it is almost
universally maintained without the practices applied to any other code in the organisation: no
version control, no automated tests, no review, no reproducible deployment. The result is a system
that produces the numbers the board sees, whose logic exists in one or two people's heads, and
which nobody is willing to change during the six weeks either side of year end. When those people
leave, the organisation does not lose documentation; it loses the ability to modify its own
financial plan. This is the failure mode to name early, because finance already privately agrees
with it.

**The integration, not the tool, is where the two versions of the truth come from.** When the EPM
tool extracts the general ledger on its own schedule with its own account mapping, and the data
platform extracts the same ledger with a different mapping, the organisation now has two revenue
figures that differ for defensible reasons nobody can reconstruct under time pressure. Every
subsequent meeting spends its first fifteen minutes on which number is right. Deciding once that
the platform is the source of actuals, holding the mapping as a single versioned artefact, and
flowing the approved plan back into the platform for variance reporting eliminates an entire
recurring category of organisational friction for a modest amount of pipeline work.

**Consolidation is a control, not a calculation.** A statutory consolidation applies currency
translation at policy-defined rates, eliminates intercompany balances, applies ownership
percentages and non-controlling interest, and carries top-side journals — and it does so under
audit, inside the internal control environment, with evidence of who approved what. Proposals to
"just do the consolidation in SQL" fail not because the arithmetic is hard but because the
arithmetic was never the requirement. Anyone who has sat through a close knows this; anyone who
has not should assume it before proposing a replacement.

**The incumbent in every one of these decisions is a spreadsheet.** Not a competitor product — a
spreadsheet, or several hundred of them, maintained by the people who understand the business
best. Its advantages are genuine: zero procurement, unlimited flexibility, and the model author is
the domain expert. Its costs are also genuine and researched. Panko's review of the research
literature concludes that "spreadsheet errors are both common and non-trivial" and that "only one
technique, cell-by-cell code inspection, has been demonstrated to be effective" at reducing them.
Any EPM proposal is competing against this, and a proposal that does not acknowledge what the
spreadsheets are good at will not be believed about anything else.

## EPM Versus an Analytics Platform

This is the section that answers the two objections in the Scope. Read it before the vendor
comparison, not after.

### What each actually does

| | **EPM** | **Analytics platform** |
|---|---|---|
| Direction of data flow | Write-first — humans enter numbers that did not previously exist | Read-first — numbers already exist and are being landed, joined and served |
| Whose numbers | The organisation's **intent**: plan, budget, forecast, target, allocation, statutory result | The organisation's **record**: what happened |
| Unit of work | A mutable cell with a named accountable owner | An immutable fact appended to a table |
| Recalculation | On write, across the dependency graph, so the person typing sees the consequence | On schedule or at query time |
| Model owner | Finance | Data engineering, with domain input |
| Model encodes | Business policy and accountability — allocation bases, FX policy, approval hierarchy | Data structure — grain, conformance, history |
| Concurrency shape | Many humans editing overlapping intersections in a compressed window | Bulk loads plus read concurrency |
| Period semantics | Open and closed periods; scenario and version as first-class dimensions | Effective dating and slowly changing dimensions |
| Typical engine | Proprietary in-memory multidimensional | Columnar, distributed, SQL-first |
| Governing artefact | Approval hierarchy, close checklist, accounting standard | Data contract, SLA, lineage |

**[assessment] The table is not a feature comparison; it is a statement that these are different
machines because the workload has the opposite read/write profile.** That is why the pairing is
legitimate rather than transitional, and why "consolidate onto one platform" is not available as a
rationalisation saving in the way it is for, say, two overlapping BI tools.

### Where they genuinely overlap

Be honest about this. The overlap is real, it is what starts the argument, and pretending it does
not exist is why architects lose the argument.

1. **Reporting on actuals.** Both systems can produce a profit-and-loss statement by cost centre
   for a closed period. Both can demo it. This is the single largest genuine overlap and it is
   where most of the duplicated effort in real estates actually sits.
2. **Variance analysis.** Plan-versus-actual requires plan and actual in one place. Either system
   can hold both. The question is never "can it" but "which one is the book of record for each
   half", and that question is answerable.
3. **The source of actuals.** Both want to consume the general ledger. If they consume it
   independently, they will map it independently, and the organisation gets two definitions of
   revenue with no reconciliation path.
4. **Ad-hoc analysis of the plan.** Once a plan exists, people want to slice it. BI tools slice
   better than planning grids, so the plan usually ends up in the BI tool anyway — which is an
   argument for designing that flow rather than discovering it.
5. **Write-back, increasingly.** Analytics platforms have begun acquiring documented write paths.
   **[verified]** Microsoft documents translytical task flows, in which "Translytical task flows
   can enable data write-back so that end users can update, add, or delete data in Fabric
   databases from within Power BI reports", implemented by connecting report buttons to Fabric
   user data functions. **[assessment]** Be precise about what this narrows and what it does not.
   It narrows the gap in *data capture* — a user can now type a value into a report and have it
   persist. It does not supply an approval-unit hierarchy, a locked period, a currency-translation
   engine, an elimination rule set, or a close checklist. Treat it as making annotation and
   lightweight status capture native to the BI layer, not as making the BI layer a planning tool.
6. **One vendor has genuinely merged the categories.** SAP sells planning capability inside its
   analytics product rather than as a separate application, which makes the category boundary a
   product boundary at that vendor and not at the others. See the vendor section for what could
   and could not be verified about it this session.

### Where they do not overlap

Three things a general-purpose data platform does not do, and is not close to doing:

**1. Planning write-back with accountability.** The value is not the ability to store a
user-entered number; it is the machinery around it. **[verified]** Oracle documents that a
planning application "supports bottom-up, distributed, or free-form budgeting", that "high-level
users start the approval units containing loaded data, and then delegate data entry into the
lowest-level members to their direct reports, who distribute to their direct reports, and so on",
that until a budget is distributed "users can't access it", and that administrators define
"Approval unit hierarchies", "Owners and reviewers of the approval unit hierarchies" and
"Validation rules for evaluating submitted data" — after which, on submission, "If the data passes
the validations, the budget is promoted to the next owner, and the original user can't edit the
data unless ownership is granted again." **[assessment]** That paragraph is a workflow engine, a
delegation model, an authorisation model and a validation framework, expressed as part of the data
model. No analytics platform ships it, and building it is not a pipeline task.

**2. Allocation logic.** Systematically pushing shared and indirect cost onto products, regions,
customers or services, with traceable cost flows, re-run every period, reconciling to the ledger
to the penny. **[verified]** Oracle sells this as a distinct Cloud EPM module — Profitability and
Cost Management — whose stated purpose includes "Systematically allocate shared costs to analyze
profitability by product, region, or customer segment" and "Trace cost flows … to understand key
profitability drivers." **[assessment]** Allocation is expressible in SQL. It is not *maintainable*
in SQL by the people who own the allocation policy, and the traceability requirement — being able
to show which source cost pool contributed how much to a given product's fully-loaded margin — is
substantial machinery in its own right.

**3. Close orchestration and statutory consolidation.** **[verified]** Oracle documents
consolidation as "the process of gathering data from descendant entities and aggregating the data
to parent entities", that "The translation process is run as required to convert data from the
child entity currency to the parent entity currency" and is skipped when currencies match, that
"the system translates data based on the exchange rate" for differing currencies, and that
adjustments are entered "through journals" both before and after consolidation. Around that sits
the orchestration layer already quoted — tasks, templates, relative-day schedules, assignees and
approvers. **[assessment]** None of this is a query. It is a controlled business process with an
accounting standard behind it and an auditor at the end of it.

### Answering the two objections precisely

> **"We already have an EPM tool — why do we need a data platform?"**

Because the EPM tool holds only what finance loaded into it, at the grain finance loaded it at, on
the dimensions finance owns. Ask for three specific things and let the answers decide it:

- **Join finance data to non-finance data at transaction grain.** The cube holds a summarised
  chart-of-accounts view. It does not hold order lines, sensor readings, service tickets or
  clickstream, and it cannot be made to without destroying the properties that make it a planning
  tool.
- **Serve non-finance consumers.** Supply chain, operations, product and data science questions
  never enter a finance cube, and the security model is built around finance's entity and scenario
  structure rather than around those consumers.
- **Retain source-fidelity history for audit, regulatory extract or model training.** The cube
  keeps the mapped, aggregated view; the platform keeps the record.

**[assessment] If the honest answer to all three is "we don't need those", then the EPM tool
genuinely is enough, and saying so is what earns the credibility to be believed when the answer is
the opposite.** An architect who has never once concluded "you don't need the platform" is not
being trusted on the cases where they conclude the reverse.

> **"The data platform will replace the EPM tool."**

Ask what replaces four specific things, in order:

- the approval hierarchy and the delegation model that go with it;
- the locked period and the evidence that it was locked;
- the consolidation rule set — translation, elimination, ownership, non-controlling interest;
- the auditor's assurance that the consolidated statement was produced by controlled software
  under change management.

Then ask who on the data team will own currency-translation policy at quarter end, and who they
escalate to at 11pm on close day. **[assessment]** The proposal usually ends there, and it should,
because the replacement being proposed is not a technology substitution — it is a controls change
to a financial reporting system, and it belongs to the control owner rather than to the platform
team. See `compliance/sox.md`.

### The one case where consolidating onto the platform is right

**[assessment]** Be equally honest about the exception. Where an organisation has no statutory
consolidation, a single annual budget, and one or two people who produce it, the "EPM tool" is a
spreadsheet and the right answer is often a governed table, a semantic model, and a light
write-back path on the data platform — not an EPM purchase. The two tests that separate this case
from the others are whether there is a genuine **close** with elimination and translation, and
whether there are **multiple accountable planners** who need delegation and approval. If both
answers are no, buying an EPM suite is over-engineering, and proposing one damages credibility in
exactly the same way as dismissing one does elsewhere.

## Why Finance Owns the Model

**[assessment]** The model belongs to finance for reasons that are structural rather than
political, and understanding them is what prevents an architect from proposing a migration that
cannot work.

**The dimensions are finance's governed artefacts.** The chart of accounts, the legal-entity
hierarchy, the management hierarchy and the cost-centre tree are maintained by finance, change on
finance's calendar — reorganisations, acquisitions, disposals, statutory changes — and must
reconcile to the ledger. They are not modelling choices available to a data team.

**The calculations encode policy, not logic.** Allocation bases, transfer-pricing rules,
capitalisation treatment, and FX rate policy (closing rate, average rate, or historical rate, per
account category) are decisions with accounting consequences. They are configured in the tool
because the people who own the decision are the people who configure it.

**The structure encodes accountability.** The approval-unit hierarchy quoted above is not
metadata; it is the org chart expressed as a data-entry authorisation model, and it determines who
can change which numbers and when they lose the right to. Nothing in a data platform's security
model corresponds to it.

**The architectural consequence.** A migration of an EPM model into a general-purpose platform is
a **re-implementation of finance policy, not a data migration**. It requires finance to re-derive,
re-certify and re-approve logic that currently exists as calculation scripts plus institutional
memory. That is why:

- estimates built on data volume are wrong, sometimes by an order of magnitude;
- the critical path runs through finance's availability, which is worst in the quarters when the
  programme most wants their time;
- the acceptance test is a full parallel run with tie-out rather than a sampled data-quality check;
- and the correct question at the start is "how many rules are there and who owns each one",
  which almost nobody can answer on day one.

## Multidimensional Modelling

`general/data-modelling.md` is the reference for grain, conformed dimensions, slowly changing
dimensions, fact-table types and star-versus-snowflake. This section covers only what is
*different* about a cube, and cross-references rather than restates.

**Same vocabulary, different physics.** A star schema and a cube both have dimensions,
hierarchies, members and measures. The difference is where the aggregate lives. In dimensional
modelling on a columnar engine, aggregates are computed from atomic facts at query time (or
materialised as a derived, tested artefact). In a cube, **a parent member is a first-class member
in its own right** — it can be stored, dynamically calculated, or *written to*. A parent in an EPM
cube is frequently not the sum of its children: it can be a target set top-down, an adjustment, or
the destination of a top-side journal. There is no clean star-schema equivalent of that, and it is
the modelling difference that matters most.

**Sparse and dense — the concept with no dimensional-modelling equivalent.** **[verified]** In
Essbase block storage, "Essbase creates a data block for each unique combination of sparse
standard dimension members (providing that at least one data value exists for the sparse dimension
member combination)", and "Each data block is a multidimensional array that contains a fixed,
ordered location for each possible combination of dense dimension members." Oracle notes that "By
carefully selecting dense and sparse standard dimensions, you can ensure that data blocks do not
contain many empty cells, minimizing disk storage requirements and improving performance."
**[assessment]** Two things follow. First, block size follows the dense dimensions and block count
follows the populated sparse combinations, so this is a storage-footprint and calculation-time
decision made at design time. Second, sparsity is the axis on which the whole category is
differentiated — **[verified]** Anaplan documents "Two different calculation engines based on
Hyperblock technology … the Classic Engine and the Anaplan Polaris™ Calculation Engine", where
"The Classic Engine is the general-purpose multidimensional planning engine for dense data sets
where the majority of cells are populated" and "Polaris is designed as a natively sparse
calculation engine, so is well-suited to sparse data sets", enabling "greater potential size,
dimensionality, and granularity". When reading any EPM vendor comparison, the sparsity question is
usually the one the benchmark is quietly answering.

**Hierarchies and consolidation operators.** Members roll up parent/child with a per-child
operator — add, subtract, ignore, never — which is how a chart of accounts expresses that expense
lines reduce a subtotal. Shared members let a base member appear in more than one rollup, which is
how statutory, management and planning hierarchies coexist over one set of leaves.
`general/data-modelling.md` treats ragged and variable-depth hierarchies as a
bridge-or-closure-table problem;
a cube handles them natively, and that native handling is a real reason finance models do not
port cleanly to a star schema.

**Calculation scripts and their maintainability.** **[verified]** Oracle documents that Essbase
calculation scripts "are created by your Essbase administrator for your specific system", that
script types "can be Essbase or MDX", that they can prompt for "variable information, called
runtime prompts", and that the solve order of a member point-of-view can be changed before a
calculation is run. **[assessment]** So
the business logic of a finance model is imperative, order-dependent code that mutates shared
state in place, authored by an administrator, typically without a type system, without unit tests,
and — in most estates — without version control. The mitigation is not "rewrite it in SQL", which
solves nothing and loses the write path. The mitigation is to treat the calculation and rule
assets as source code: put them in version control, build a regression harness that runs a known
input set and compares outputs, and deploy through the vendor's automation API so the test
environment is meaningful. This is the highest-leverage recommendation in this file and it costs
almost nothing.

**Aggregation versus consolidation — not the same word.** Aggregation is arithmetic rollup along a
hierarchy. **Consolidation** additionally applies currency translation, ownership percentages,
intercompany elimination, and non-controlling interest, and admits journal adjustments before and
after. **[verified]** Oracle's documented sequence is: enter or load data into base-level entities,
calculate and adjust, then run consolidation for a selected scenario, year, period and entity;
translation runs only where child and parent currencies differ; adjustments are made through
journals both before consolidation and against contribution data afterwards. **[assessment]** A
tool that aggregates is a reporting tool. A tool that consolidates is a financial reporting
system, with the control obligations that implies.

**Hybrid storage.** **[verified]** Oracle documents hybrid block-storage cubes, which "support
some Aggregate Storage Option (ASO) capabilities in addition to BSO capabilities" so that parents
of sparse and dense dimensions can be dynamic, with stated benefits of "smaller database and
application size, better cube refresh performance, faster import and export of data, improved
performance of business rules, and faster daily maintenance". Oracle also documents that Cloud EPM
generally uses hybrid cubes — "Financial Consolidation and Close, Custom Planning, Planning
Modules, and FreeForm applications that you create in EPM Enterprise use Hybrid BSO cubes" — and
that "Enterprise Data Management does not use Essbase." **[assessment]** The practical reading is
that the historic BSO-versus-ASO design fork is much less prominent in the SaaS products than in
the on-premises estate an organisation may be migrating from, which matters when comparing effort
estimates written by people whose experience is on either side of that line.

## The Integration Pattern

**[assessment]** State this plainly in any architecture document, because it dissolves most of the
false conflict on its own:

> **The data platform is normally the right source of actuals for the EPM tool, and the EPM tool's
> output — plan, budget, forecast, allocated cost — is normally a source back into the data
> platform for variance and downstream reporting.** Two arrows, both load-bearing.

**Platform → EPM (actuals in).** The platform already holds a mapped, reconciled and lineage-traced
version of the ledger; it already carries the access evidence an auditor will ask for; and it is
the only place that also holds the **non-GL drivers** — headcount, volumes, units, rates — that a
driver-based plan needs and that the ledger alone cannot supply. The anti-pattern is EPM
extracting from each source system directly on its own schedule with its own mapping, which
guarantees a monthly reconciliation meeting and a permanent second definition of revenue.

**EPM → platform (plan out).** Variance reporting belongs where the actuals and the wide dimensional
context already are. Plan data also feeds downstream operational planning (supply, workforce,
capacity) and, increasingly, features for forecasting models. If the plan never leaves the EPM
tool, every plan-versus-actual view gets rebuilt inside it, and the platform's version is
permanently one cycle behind.

Both directions are first-class, documented vendor capabilities rather than integration
improvisation:

- **[verified]** Oracle ships a Data Integration component within Cloud EPM whose documented
  scope includes creating a data export file integration — exporting data out of the EPM
  application to a file for loading into an ERP application or an external system — alongside the
  inbound loads.
- **[verified]** Anaplan documents CloudWorks: "With CloudWorks™, Integration administrators can
  import and export model data, to and from the cloud", with permissions described as "Read for
  import, Write for export, related to files in your Amazon (AWS) S3 buckets, Google BigQuery
  tables, and Azure Blob containers" — that is, the major cloud data platforms named explicitly as
  both sources and targets.

**Design points that decide whether this works:**

- **Book of record, declared once.** For actuals, for plan, and for the variance comparison, name
  the system. Ambiguity here is what produces two numbers on one slide.
- **The mapping is the coupling.** GL account to EPM account is a shared artefact. Version it,
  hold it once, and have both sides consume it. Divergence appears at the next chart-of-accounts
  change and is discovered during close.
- **Grain change belongs in the platform.** The platform holds transactions; the cube holds a
  summarised intersection. Do the aggregation where it is testable and reconcilable, not in the
  EPM tool's load rules.
- **Cadence follows the business process.** Actuals after close; plan versions after approval.
  Neither is a streaming use case.
- **Dimension alignment needs an owner, and usually a tool.** Hierarchy changes must land in both
  systems in the same period or the comparison breaks. Several suites sell a master-data module
  for exactly this. See `general/data-governance.md`.
- **Re-apply security on the way out.** EPM's cell-level, scenario-aware model has no equivalent
  on the platform side; an unclassified plan extract is a draft budget in a shared warehouse. See
  `general/data-classification.md`.
- **Reconciliation is a product feature, not a project task.** Build the tie-out report that
  proves the cube's actuals equal the platform's actuals for every period, and run it every cycle.
  It is the cheapest possible insurance against the argument this whole pattern exists to prevent.

## Vendors

Software vendors only, with capability claims marked for confidence. Product naming in this market
changes frequently; re-check before quoting.

### Oracle — Essbase and Oracle Fusion Cloud EPM

Two distinct things sold under one heading, and conflating them is a common error.

**Essbase** is the multidimensional engine itself, with a long on-premises history (Hyperion
lineage) and a current customer-deployed release. **[verified]** The Essbase 21c documentation set
covers "Essbase Stack Deployment on Oracle Cloud Infrastructure" and "Essbase Independent
Deployment", alongside migration paths for "Essbase 11g on-premises Applications and Users" — that
is, 21c is deployed and operated by the customer rather than consumed as SaaS. Storage models are
block storage (BSO), aggregate storage (ASO), and hybrid, per the modelling section above.

**Oracle Fusion Cloud EPM** is the SaaS suite. **[verified]** Oracle's product page names the
constituent business processes as **Connected Planning, Financial Consolidation and Close,
Profitability and Cost Management, Account Reconciliation, Tax Reporting, and Enterprise Data
Management**. **[verified]** Oracle documents that Cloud EPM runs on Essbase — with hybrid BSO
cubes used by Financial Consolidation and Close, Custom Planning, Planning Modules and FreeForm in
EPM Enterprise — and that Enterprise Data Management is the exception that "does not use Essbase".
**[verified]** Oracle also ships **Smart View for Office**, documented as working "with data
sources for both on-premises providers and for Oracle Cloud EPM services", letting users "view,
import, manipulate, distribute, and share data from various data sources using Microsoft Excel,
Word, Outlook, and PowerPoint".

### Anaplan

Connected planning across finance and non-finance domains, on a proprietary in-memory engine.
**[verified]** Anaplan documents "Two different calculation engines based on Hyperblock technology
… the Classic Engine and the Anaplan Polaris™ Calculation Engine", with Classic as "the
general-purpose multidimensional planning engine for dense data sets where the majority of cells
are populated" and Polaris "designed as a natively sparse calculation engine". **[verified]**
Polaris "uses the same modeling interface, formula syntax, and functions as the Classic Engine,
with minor differences", but the engine choice is fixed at workspace level: "Workspaces are either
a Classic workspace or a Polaris workspace, and one workspace cannot have both Classic and Polaris
models", and neither type can be converted into the other. **[assessment]** That last point is
architecturally significant and easy to miss in a selection: it is a permanent decision made at
provisioning time, before anyone has built the model that would inform it.

### OneStream

Positions itself as a single unified application spanning the finance processes that competitors
split across modules. **[verified]** OneStream describes "a modern, uniquely unified platform and
data model" that "unifies your financial and operational data and processes in a single source of
truth", covering financial close and consolidation, planning and analysis, reporting and account
reconciliation, and states the platform "is built to be infinitely extensible", with a Solution
Exchange from which customers "can download more than 100 solutions from OneStream, our partners
and community". "Extensible dimensionality" is OneStream's own term for its dimensional approach.
**[assessment]** The unified-application claim is the differentiator to test in a proof of
concept — specifically, whether a single application genuinely serves both the close and the
planning cycle without a second model, since that is the claim the architecture rests on.

### Workday Adaptive Planning

**[verified]** Workday's product navigation lists Financial Planning, Close & Consolidation,
Workforce Planning and Operational Planning under Adaptive Planning, and the technology page
states it is "Powered by Elastic Hypercube Technology" and "automatically adds memory and
computing power any time you need it—without sacrificing performance". **[verified]** Workday also
documents pulling "data directly into Microsoft Excel and PowerPoint, as well as Google Sheets,
Google Slides, and Google Docs".

### SAP — BPC, Analytics Cloud, and group reporting

SAP's answer spans three products: **Business Planning and Consolidation (BPC)**, the older
product with on-premises NetWeaver and Microsoft-platform variants; **SAP Analytics Cloud**, which
carries planning capability inside the analytics product; and **S/4HANA Finance for group
reporting**, which executes consolidation inside the ERP.

**[assessment] This is the one vendor where the EPM-versus-analytics boundary is genuinely a
product boundary rather than a category boundary**, because planning lives inside the analytics
tool. That makes SAP the interesting counter-example to this file's central distinction, and it
does not invalidate it: the underlying workloads still differ in exactly the ways described above;
SAP has simply chosen to ship both engines behind one user experience.

**Explicitly not verified this session — do not quote SAP specifics from this file.**
`www.sap.com` returns HTTP 403 to automated retrieval, `community.sap.com` is behind an
interstitial challenge, and `help.sap.com` serves a roughly 1 KB JavaScript shell to a
non-browser client rather than page content. Maintenance timelines for BPC in particular are
version-specific and platform-specific, are widely misquoted by third parties, and change; check
the SAP Product Availability Matrix and the relevant SAP Note directly rather than any secondary
summary, including this one.

### Pigment

A newer entrant in the planning half of the category. **[verified]** Pigment's documentation
describes its model primitives as **Metrics** ("A critical Block type used in Pigment for inputs,
calculations, and outputs or reporting. Metrics are structured by Dimension Lists"), **Dimension
Lists** ("Groups of related Items … They are fundamental to Pigment as they define the structure
and content of a model"), **Scenarios** ("Allow for rapid 'on-the-fly' simulations") and
**Versions** ("Essential for repeatable, auditable planning that is deeply integrated into your
model"). **[assessment]** The vocabulary is the same multidimensional vocabulary under different
names, which is the point worth carrying: newer tools are not a different modelling paradigm, they
are a different implementation and a different authoring experience over the same one.

### IBM Planning Analytics

Included because the TM1 engine is one of the major multidimensional engines and appears
frequently in incumbent estates. **[verified]** IBM describes Planning Analytics as "powered by
the IBM® TM1® engine" and markets an Excel add-in with the framing "Keep Excel. Add TM1 power."

### Others in the market

Board, Jedox, Vena, Prophix, Wolters Kluwer CCH Tagetik, and Workiva (weighted toward reporting
and disclosure) are active participants in this category. They are named here for completeness of
the landscape; no capability claim is made about any of them in this file, and none was verified.

### The real incumbent: Excel plus a cube plus tribal knowledge

**[assessment]** A large share of organisations run their planning and much of their close on
spreadsheets, with a cube — if one exists at all — used mainly as a reporting back end, and with
the exception handling, mappings and adjustments held in the heads of one or two people. **This,
not another vendor, is what any EPM proposal actually competes with**, and treating it as an
embarrassment to be swept away is the fastest route to losing the room.

Two things are worth knowing about it.

**First, the Excel front end is not a legacy workaround — it is the vendors' own design.**
**[verified]** Oracle ships Smart View for Office and documents Excel, Word, Outlook and
PowerPoint as first-class clients; IBM markets its add-in as "Keep Excel. Add TM1 power."; Workday
documents pushing data into Excel, PowerPoint and the Google equivalents. **[assessment]** Any
proposal promising to "get finance off Excel" is promising something no vendor in the category
promises. The realistic goal is to move the *model and the numbers* behind a governed engine while
leaving Excel as the interface, which is exactly what the add-ins exist to do.

**Second, the costs of the spreadsheet-only variant are researched rather than anecdotal.** Panko's
review of fifteen years of studies concludes that "spreadsheet errors are both common and
non-trivial", and that "To date, only one technique, cell-by-cell code inspection, has been
demonstrated to be effective" — with other, easier-to-adopt approaches appealing but unproven.
**[assessment]** The architecturally decisive risk, though, is not the error rate: it is
**key-person concentration**. The model, the mappings, and every exception live in a small number
of heads with no artefact to hand over. When those people leave, the organisation does not lose
documentation — it loses the ability to modify its own financial plan. Name that risk; it is the
one finance already agrees with privately, and it converts an IT proposal into a continuity
argument the CFO owns.

## Implementation Risk, Stated Factually

The Essbase and wider Hyperion family carries a strong practitioner reputation for cost and effort
overrun relative to vendor projections. That reputation materially shapes how any successor
proposal is received by anyone who has lived through one, so it is worth being precise about what
can and cannot be supported.

**What I could not source.** I did not find, this session, a controlled study, published audit
report, or other primary source quantifying Essbase-specific or Hyperion-specific cost or effort
overrun against vendor projections. Searches across public audit reporting and the general web
returned vendor marketing and consultancy material rather than measurement. **Do not repeat a
figure for this — including one you think you remember.** The reputation is practitioner-reported,
it is widespread, and it is not, as far as this session could establish, publicly measured.

**What is documented, and is enough to reason with.** The *mechanisms* that drive effort in this
product family are in Oracle's own documentation, and an architect can point at them without
asserting anything unsupported:

- **[verified]** Storage design is a design-time decision with order-of-magnitude consequences:
  block size follows the dense dimensions, block count follows populated sparse combinations, and
  Oracle explicitly instructs that careful selection is what keeps blocks from containing many
  empty cells.
- **[verified]** Routine optimisation is a published, specialist procedure. Oracle's BSO
  optimisation guidance covers running an explicit dense restructure — "An explicit restructure
  removes #missing blocks to reduce the BSO database size" — running a Block Analysis report that
  reports the "Percentage of blocks with only Zero", the top repeated numerical values and the top
  dense member combinations with repeated values, replacing zero blocks with `#missing`, using
  `@round` or `@truncate` to eliminate near-zero values, and setting the consolidation operator to
  `Never` for SmartList, Date, Text and Percentage data types because "Using the Addition
  consolidation operator increases the cube size without adding any value."
- **[verified]** Business logic is administrator-authored imperative script with configurable solve
  order and runtime prompts, rather than declarative model configuration.

**[assessment] The honest formulation** is therefore: this is a product family whose vendor
documents a multi-step manual optimisation procedure as normal operations, whose storage design is
irreversible in practice, and whose business logic is code maintained outside normal engineering
practice. Those properties are sufficient to explain a pattern of underestimation without needing
a number, and they are checkable by anyone who doubts you.

**[assessment] What to do with it.** Three things, all of which apply to any EPM programme and not
only to Oracle's:

1. **Estimate by rules and owners, not by rows.** The effort is logic archaeology. Count the
   calculation scripts, the allocation rules, the mapping tables and the people who own each, and
   accept that the count itself takes weeks to establish.
2. **Budget a full parallel run with tie-out.** The acceptance criterion is "the numbers match",
   which is binary. Analytics programmes can go live with known data-quality caveats; a
   consolidation cutover cannot.
3. **Do not let the incumbent's reputation do the arguing.** Someone in the room has lived through
   a bad implementation and will supply the scepticism unprompted; the credible move is to name
   the mechanisms above and show how the proposal addresses each, rather than to assert that the
   new tool is different.

## What Is Verified and What Is Judgement

**Verified against vendor documentation on 2026-07-26** (each has a URL in Reference Links):

- **Oracle** — Essbase block-storage mechanics (one data block per populated sparse member
  combination; each block a fixed-order array over the dense members; the instruction to select
  dense and sparse dimensions carefully); hybrid BSO cubes supporting some ASO capabilities and
  their stated benefits; which Cloud EPM application types use hybrid cubes and that Enterprise
  Data Management does not use Essbase; the Cloud EPM module list on Oracle's product page,
  including the Profitability and Cost Management allocation language; the consolidation process
  sequence including conditional currency translation and journal adjustments before and after;
  Task Manager tasks, templates and relative-day schedules; the budget process including approval
  unit hierarchies, owners and reviewers, validation rules, promotion to the next owner and loss
  of edit rights; the BSO optimisation procedure (explicit restructure, Block Analysis report,
  zero-block replacement, `@round`/`@truncate`, `Never` operator); calculation scripts being
  administrator-authored, Essbase or MDX, with runtime prompts and a changeable member-POV solve
  order; Smart View
  supporting Excel, Word, Outlook and PowerPoint against both on-premises and Cloud EPM sources;
  Essbase 21c deployment options (OCI stack and independent deployment) with documented 11g
  migration; Data Integration's data-export-file capability.
- **Anaplan** — two engines on Hyperblock (Classic and Polaris); Classic as the dense
  general-purpose engine and Polaris as natively sparse; shared modelling interface, syntax and
  functions with minor differences; workspace-level engine choice with no conversion in either
  direction; CloudWorks importing and exporting model data with read/write against S3 buckets,
  BigQuery tables and Azure Blob containers.
- **OneStream** — the unified platform and data model claim, the process areas covered, "infinitely
  extensible", and the Solution Exchange's stated 100-plus solutions.
- **Workday** — Adaptive Planning product areas (Financial Planning, Close & Consolidation,
  Workforce Planning, Operational Planning); Elastic Hypercube Technology and the stated automatic
  memory and compute scaling; export into Excel, PowerPoint and the Google office suite.
- **Pigment** — Metrics, Dimension Lists, Scenarios and Versions as the documented model
  primitives, with the quoted descriptions.
- **IBM** — Planning Analytics being powered by the TM1 engine, and the marketed Excel add-in.
- **Microsoft** — translytical task flows enabling end users to "update, add, or delete data in
  Fabric databases from within Power BI reports" via Fabric user data functions, together with the
  documented limitations.
- **Panko (2008)** — the abstract's conclusions that spreadsheet errors are "both common and
  non-trivial" and that only cell-by-cell code inspection has been demonstrated effective. Note
  that the widely-circulated per-cell and per-spreadsheet error percentages attributed to this
  literature are **not** in the abstract and were not verified here; do not quote them.

**Assessment, not vendor claim:** the immutable-fact-versus-mutable-cell framing and everything
derived from it; the overlap and non-overlap lists; the two scripted objection responses; the
"one case where consolidating onto the platform is right"; the claim that EPM migration is finance
policy re-implementation rather than data migration; the estimate-by-rules-and-owners guidance;
the key-person-concentration risk framing; the characterisation of calculation scripts as code
without engineering practice; and the reading that hybrid storage reduces the prominence of the
BSO/ASO fork in the SaaS products.

**Explicitly not verified this session:**

- **All SAP specifics.** `www.sap.com` returns 403 to automated retrieval, `community.sap.com` is
  behind an interstitial challenge, and `help.sap.com` serves a roughly 1 KB JavaScript shell
  rather than content. The SAP section states product *positioning* only; no SAP capability claim,
  version, or maintenance date in this file is verified, and none should be quoted from it.
- **Essbase and Hyperion cost or effort overrun figures.** No primary source found — see the
  implementation-risk section. The reputation is real and is reported by practitioners; the
  measurement is not public as far as this session could establish.
- **Board, Jedox, Vena, Prophix, CCH Tagetik and Workiva.** Named as market participants only. No
  capability claim is made and none was checked.
- **Pricing, licensing metrics, and per-tier feature gating for every vendor here.** These change
  constantly and none were verified. Assume the controls a regulated buyer needs sit behind a
  higher tier until proven otherwise — that is the pattern in every adjacent category, per
  `patterns/data-platform-selection.md`.

## Common Decisions (ADR Triggers)

- **Buy an EPM tool vs extend the data platform** — decided by whether there is a genuine close
  (elimination, translation, ownership) and whether there are multiple accountable planners
  requiring delegation and approval. Record both tests and their answers; this is the decision the
  rest depend on.
- **Which system is the book of record for actuals, for plan, and for the variance comparison** —
  three separate declarations, made once. Ambiguity here is the root cause of the two-numbers
  problem and it is worth an ADR on its own.
- **Unified EPM suite vs best-of-breed planning plus separate consolidation** — a single
  application across close and planning against two specialised tools with an integration between
  them. Trade integration coherence against fit to each workload, and test the unified claim in a
  proof of concept rather than accepting it from a datasheet.
- **Statutory consolidation inside the ERP vs in a dedicated EPM tool** — proximity to the ledger
  and one fewer system against a consolidation engine built for multi-GAAP, multi-currency and
  complex ownership. Decided by group structure complexity, not by preference.
- **Calculation engine selection where it is fixed at provisioning** — Anaplan's Classic-versus-
  Polaris workspace choice is verified as non-convertible in either direction, which makes it an
  irreversible decision taken before the model that would inform it exists. Record the sparsity
  assumption it rests on.
- **Sparse/dense configuration and storage model** — a design-time decision with order-of-magnitude
  consequences for storage and calculation time, and expensive to reverse. Record the cardinality
  assumptions so the decision can be revisited when they change.
- **Alternate hierarchies: native cube shared members vs star-schema bridge tables** — determines
  whether the statutory, management and planning rollups can coexist cheaply. This is frequently
  the technical reason an EPM model does not port to the warehouse.
- **Where the GL-to-EPM account mapping lives, and who owns it** — one versioned artefact consumed
  by both systems, or two mappings that diverge at the next chart-of-accounts change.
- **Where transaction-to-cube aggregation happens** — in the platform, where it is testable and
  reconcilable, or in the EPM tool's load rules, where it usually is not.
- **Applying software engineering practice to calculation assets** — version control, a regression
  harness, and API-based deployment for calc scripts, business rules and mappings. Worth an ADR
  because it is a change to how finance works, not only to how the system is managed, and because
  it needs a named owner to survive.
- **Excel as a supported client vs a migration target** — every major vendor ships an Excel add-in;
  a decision to eliminate spreadsheets is a decision the vendor does not support. Record the
  intended end state for spreadsheets explicitly rather than leaving it as an unstated aspiration.
- **Analytics-platform write-back as a substitute for lightweight planning** — where the
  requirement is data capture and annotation rather than delegated, approved, period-locked
  planning, a documented platform write-back path may be sufficient and much cheaper. Record which
  requirement it is; the two are routinely conflated in both directions.
- **Cutover approach: parallel run with tie-out vs phased migration by entity or process** — the
  acceptance criterion for consolidation is that the numbers match exactly, which constrains the
  options more than it does for an analytics migration.
- **Retention and archive for closed-period plan and consolidation data** — how long, in what
  system, and evidenced how. See `general/legal-hold.md`.

## Reference Architectures

- **Platform-as-source-of-actuals (the default).** Source systems → data platform (landing,
  conformed, marts per `patterns/lakehouse-medallion.md`) → mapped, aggregated actuals load into
  the EPM cube after close → planning and consolidation run in EPM → approved plan, budget,
  forecast and allocated cost export back to the platform → variance and management reporting
  served from the platform alongside the actuals. One mapping artefact, versioned, consumed by
  both directions. A tie-out report reconciles cube actuals to platform actuals every cycle.
- **Consolidation-in-ERP with planning alongside.** Statutory consolidation executed inside the
  ERP close, with a separate planning tool integrated to the same platform for actuals and
  exporting plan back. Reduces the systems count for the close at the cost of consolidation
  flexibility for complex ownership structures; the planning integration pattern is unchanged.
- **Unified EPM application.** One application spanning close, planning, reconciliation and
  reporting on a single model, integrated to the data platform in both directions as above.
  Fewest interfaces on the finance side; the claim to validate is that one model genuinely serves
  both the close and the planning cycle.
- **Lightweight write-back on the platform (no EPM tool).** For organisations with no statutory
  close and a single accountable planner: a governed table on the platform for plan values, a
  documented write path from the BI layer, versioning by scenario column, and reporting from the
  same semantic model as actuals. Explicitly not suitable once delegation, approval, period
  locking or elimination enter the requirements — at which point this becomes a migration, so
  record the trigger condition when adopting it.
- **Transitional coexistence during EPM migration.** Legacy cube and successor tool both loaded
  from the platform with the same mapping for the duration of the parallel run, with an automated
  cell-level comparison as the cutover gate. Related pattern mechanics in
  `patterns/migration-coexistence.md` and `patterns/migration-cutover.md`.

## Reference Links

All links checked on 2026-07-26; codes and effective URLs are as returned that day.

- [Oracle Essbase 21c — Get Started](https://docs.oracle.com/en/database/other-databases/essbase/21/index.html)
  — deployment options: OCI stack deployment, independent deployment, and 11g on-premises migration
- [Oracle Essbase — Data Storage (block storage)](https://docs.oracle.com/en/database/other-databases/essbase/21/essdm/data-storage.html)
  — one data block per populated sparse member combination; blocks as fixed-order arrays over dense members
- [Oracle Essbase — Calculation Command List](https://docs.oracle.com/en/database/other-databases/essbase/21/esscq/calculation-command-list.html)
  — the calculation command surface behind calc-script maintainability
- [About Essbase in Oracle Cloud EPM](https://docs.oracle.com/en/cloud/saas/enterprise-performance-management-common/cgsad/1_about_one_epm_hybrid_essbase.html)
  — hybrid BSO cubes, their stated benefits, which application types use them, and the EDM exception
- [Oracle Cloud EPM — Optimize BSO Cubes](https://docs.oracle.com/en/cloud/saas/enterprise-performance-management-common/tsepm/op_procs_bso_defrg_plan_type.html)
  — explicit restructure, Block Analysis report, zero-block replacement, `Never` consolidation operator
- [About Calculating Data in Essbase (Smart View)](https://docs.oracle.com/en/cloud/saas/enterprise-performance-management-common/wsvfg/calcscr_about_calc_in_essbase_102xb8f0b255.html)
  — calc scripts authored by the administrator, Essbase or MDX, runtime prompts, solve order
- [Oracle Enterprise Performance Management (product page)](https://www.oracle.com/erp/performance-management/)
  — the Cloud EPM module list and the Profitability and Cost Management allocation language.
  *Note: returns HTTP 403 to some automated clients; readable via a browser user agent.*
- [Oracle Financial Consolidation and Close — Consolidation Process](https://docs.oracle.com/en/cloud/saas/financial-consolidation-cloud/agfcc/consol_process.html)
  — aggregation to parents, conditional currency translation, journal adjustments before and after
- [Oracle Financial Consolidation and Close — Task Manager Terms](https://docs.oracle.com/en/cloud/saas/financial-consolidation-cloud/agfcc/cm_close_mgr_terms.html)
  — tasks, templates, and schedules mapping relative business days to calendar dates
- [Oracle Planning — Budget Process](https://docs.oracle.com/en/cloud/saas/planning-budgeting-cloud/pfusa/budget_process.html)
  — approval unit hierarchies, owners and reviewers, validation rules, promotion and loss of edit rights
- [Oracle Cloud EPM — Creating a Data Export File Integration](https://docs.oracle.com/en/cloud/saas/epm-cloud/diepm/integrations_creating_a_data_export.html)
  — exporting EPM data out to a file for an ERP or external system
- [Oracle Smart View for Office documentation](https://docs.oracle.com/en/applications/enterprise-performance-management/smart-view/index.html)
  — Excel, Word, Outlook and PowerPoint as first-class EPM clients, on-premises and cloud
- [Anaplan — Calculation engines](https://help.anaplan.com/anaplan-calculation-engines-06c06ade-2807-4f3d-9a6e-d69ae0e257e5)
  — Classic vs Polaris, density design intent, and the non-convertible workspace constraint
- [Anaplan — Polaris calculation engine](https://help.anaplan.com/polaris-calculation-engine-8b466778-42b2-4e35-b318-e5e4128b63b7)
  — both engines built on Hyperblock; Polaris as a natively sparse engine
- [Anaplan — CloudWorks](https://help.anaplan.com/cloudworks-96f951fe-52fc-45a3-b6cb-16b7fe38e1aa)
  — bidirectional model-data integration with S3, BigQuery and Azure Blob
- [OneStream platform overview](https://www.onestream.com/platform/)
  — unified platform and data model, process coverage, extensibility, and the Solution Exchange
- [Workday Adaptive Planning — technology](https://www.workday.com/en-us/products/adaptive-planning/technology.html)
  — Elastic Hypercube Technology and the Office/Google export surface
- [Workday Adaptive Planning — overview](https://www.workday.com/en-us/products/adaptive-planning/overview.html)
  — product areas: Financial Planning, Close & Consolidation, Workforce Planning, Operational Planning
- [Pigment — Modeling and Formulas](https://kb.pigment.com/docs/models-formulas)
  — Metrics, Dimension Lists, Scenarios and Versions as the model primitives
- [Pigment — Multi-Dimensional modeling](https://kb.pigment.com/docs/multi-dimensional-modeling)
  — dimensional aggregation, allocation and mapping in Pigment's formula syntax
- [IBM Planning Analytics](https://www.ibm.com/products/planning-analytics)
  — the TM1 engine and the Excel add-in positioning
- [Understand translytical task flows (Power BI / Fabric)](https://learn.microsoft.com/en-us/power-bi/create-reports/translytical-task-flow-overview)
  — documented analytics-platform write-back via Fabric user data functions, and its limitations
- [Panko, *Spreadsheet Errors: What We Know. What We Think We Can Do* (arXiv, 2008)](https://arxiv.org/abs/0802.3457)
  — the research position on spreadsheet error prevalence and which mitigations are demonstrated

**Checked and deliberately not cited as evidence:** `https://www.sap.com/...` returned HTTP 403 to
automated retrieval; `https://help.sap.com/docs/SAP_ANALYTICS_CLOUD` returned HTTP 200 with a
roughly 1 KB JavaScript shell rather than page content; `https://community.sap.com/...` returned
HTTP 403 behind an interstitial challenge. A 403 here indicates bot filtering, not link rot — but
none of these could be read this session, so no SAP claim in this file rests on them.

## See Also

- `patterns/data-platform-selection.md` — the analytical platform decision this file pairs with;
  read both before answering "do we need one, the other, or both"
- `general/data-analytics.md` — warehouse vs lake vs lakehouse, ETL/ELT, semantic layers, and the
  governance tooling around the platform that supplies EPM its actuals
- `general/data-modelling.md` — grain, conformed dimensions, SCD types, semi-additive measures and
  ragged hierarchies; the reference for the dimensional vocabulary a cube shares and reinterprets
- `general/data-ingestion.md` — how actuals physically arrive, and why the capture method
  constrains the history available to a plan-versus-actual comparison
- `general/data-governance.md` — hierarchy and master-data governance, which is where EPM and
  platform dimensions must be reconciled
- `general/data-classification.md` — classification for plan and forecast data leaving the EPM
  security model for the platform's
- `patterns/data-pipeline.md` — the pipelines that move actuals in and plan out, and their
  orchestration
- `patterns/lakehouse-medallion.md` — the layered design that produces the conformed actuals EPM
  should consume
- `patterns/data-warehouse-migration.md` — the adjacent migration pattern, and a useful contrast:
  an EPM migration is logic re-certification, not schema conversion
- `patterns/migration-coexistence.md` and `patterns/migration-cutover.md` — parallel-run and
  cutover mechanics for the tie-out gate an EPM cutover requires
- `compliance/sox.md` — IT general controls for financial reporting systems, which a consolidation
  engine is
- `compliance/bank-regulatory-reporting.md` — the regulated-reporting variant of the close and
  submission problem
- `general/change-management.md` — the change process a model edit during close has to pass through
- `general/legal-hold.md` — retention and hold over closed-period financial data
- `general/governance.md` — the governance operating model that decides who owns a hierarchy
- `providers/oracle/database.md` — Oracle platform detail adjacent to the Essbase estate
- `providers/azure/fabric.md` — the platform behind the documented write-back path referenced above
- `providers/dbt/transformation.md` — where the GL mapping and the transaction-to-cube aggregation
  should live if the platform owns them
- `failures/data.md` — data platform failure modes, several of which are how the two-versions-of-
  the-truth problem manifests
