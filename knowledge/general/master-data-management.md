# Master Data Management

## Scope

Covers master data management as an architecture and operating-model problem: the four
implementation styles (**registry, consolidation, coexistence, centralised/transaction hub**) and
what each commits you to operationally; **match, merge and survivorship** rules and why survivorship
is a business decision routinely mistaken for a technical one; **the golden record concept and its
limits**, including the case where a single golden record is the wrong model; deterministic versus
probabilistic matching and where each belongs; **stewardship workflow** — exception queues,
adjudication, SLAs, and what downstream consumers see while a conflict is unresolved; **reference
data management** as the tractable sibling problem; and the vendor landscape at a factual level.

The matching *algorithms* — blocking, similarity scoring, clustering, precision and recall, un-merge
— live in `patterns/entity-resolution.md` and are deliberately not repeated here. This file is about
the decisions that surround them. For the conformed dimensions and slowly-changing-dimension history
that mastered entities feed, see `general/data-modelling.md`. For stewardship and ownership as a
general governance discipline, see `general/data-governance.md`, which this file cross-links rather
than restates.

**This file exists mainly to settle one argument.** "We are building a data platform" is the label
that gets attached to post-merger customer-master integration, CRM or ERP consolidation, "customer
360", and regulatory aggregation across systems — and in every one of those, the work that has to
happen is entity resolution, survivorship rules, and a conformed dimension layer. That is modelling
and stewardship work. It is not platform work. The section
[This Is Not a Platform Problem](#this-is-not-a-platform-problem) is the reason to read this file.

**Statements marked [verified] were read from the cited page on 2026-07-27.** Statements marked
**[assessment]** are judgement, not vendor claim. The section
[What Is Verified and What Is Judgement](#what-is-verified-and-what-is-judgement) separates them
explicitly, and lists what this session could *not* verify.

## This Is Not a Platform Problem

A data platform gives you somewhere to put the records, compute to compare them with, a catalog to
describe them in, and lineage to trace them through. It supplies no answer to any of the questions
that actually block the work:

- Are these two records the same customer?
- When they disagree about the address, which one is right?
- Who decides that, and on what authority?
- What does a downstream consumer see while nobody has decided?
- If we merge them and we were wrong, how do we undo it?

None of those are storage, compute, or catalog questions. They are modelling questions (what is an
entity, at what grain, with what identity) and stewardship questions (who adjudicates, under what
rule, with what SLA). A lake or lakehouse is a perfectly reasonable *place* to do this work and does
not do one bit of it. **[assessment]**

The failure mode is specific and repeatable. An acquisition closes. Two customer masters, two charts
of accounts, two product taxonomies now exist. Someone proposes a data platform as the venue for
reconciling them — which is not wrong — and the programme gets *scoped, funded and staffed* as a
platform build: ingestion, storage, catalog, BI. Eighteen months later the platform works, every
pipeline is green, and the organisation still cannot say how many customers it has, because nobody
was funded to make the survivorship decisions and nobody was appointed to adjudicate the exceptions.
The platform is then judged to have failed. It did not fail; it was asked to answer a question it
structurally cannot answer. **[assessment]**

The diagnostic is a single question at scoping time: **does the acceptance criterion contain the
phrase "one row per customer", or anything that reduces to it?** If it does, an entity-resolution and
stewardship workstream must exist, with its own budget line, its own business owner, and its own
success measure — regardless of what the programme is called. If it does not exist, the platform
budget will silently absorb it, and the absorption is invisible until the first reconciliation.

## Checklist

### Is this actually a master-data problem?

- [ ] **[Critical]** Is the programme being funded as a platform build when the work is entity
      resolution, survivorship, and a conformed dimension layer? This is the most consequential item
      in this file. Symptoms: two customer masters after an acquisition; two charts of accounts; two
      product taxonomies; a "single view" or "customer 360" whose acceptance criterion is one row per
      customer; a regulatory aggregation that must reconcile the same counterparty across systems.
      The platform is the venue, not the solution, and the difference is a budget line and a named
      business owner. **[assessment]**
- [ ] **[Critical]** Has someone stated, in one sentence per domain, **what "the same" means**?
      "The same customer" is not self-evident: two policies held by one person may be one customer to
      finance and two to servicing; two SKUs differing only in packaging may be one product to
      merchandising and two to logistics; two accounts at one address may be one household or two
      unrelated tenants. Matching cannot be tuned against an unstated target, and the argument about
      the target will happen either at design time or at user acceptance.
- [ ] **[Critical]** Is there a **named business owner per mastered domain** who can decide, and is
      expected to decide, which source wins for which attribute? Survivorship is a business decision
      about which system the organisation trusts for what. Delegating it to whoever configures the
      tool means the organisation's data-trust policy is being set by its most junior available
      implementer. See `general/data-governance.md` for the owner-versus-steward split, which applies
      here unchanged.
- [ ] **[Critical]** Is the consumption **operational** or **analytical**? Operational consumption —
      a running system reads the master synchronously and behaves differently based on the answer —
      forces availability, latency and change-control commitments equal to the systems it serves.
      Analytical consumption — a report counts distinct entities — does not. This single distinction
      constrains the implementation style more than any other input, and it is frequently left
      unstated until the style has already been chosen. **[assessment]**
- [ ] **[Critical]** Is there an **explainability requirement** on the match decision? If a merge can
      affect a credit decision, a claim, a regulatory return, or a customer-facing entitlement, then
      "the model scored it 0.94" is not an adequate answer to a complaint or an examiner. That
      requirement pushes the automatic-merge band toward deterministic rules and pushes everything
      else to human review, and it must be established before matching is designed, not after.
- [ ] **[Recommended]** Has the problem been **measured before the tool is chosen** — record counts
      per source, estimated overlap between sources, and a profile of every candidate match key
      (population rate, distinct-value count, and the frequency of the top values)? A source whose
      customer-number column is 40% populated and whose email column is 12% shared across records is
      a different problem from one where both are clean, and the tool decision should follow the
      measurement rather than precede it. **[assessment]**
- [ ] **[Recommended]** Is scope **one domain at a time**, sequenced by where the pain is? Multidomain
      first releases are attractive on a slide and produce a programme where nothing is finished for
      a year. Party/customer is usually the hardest and product is usually the most immediately
      valuable; picking the hardest one first because it is the most visible is a common and
      expensive instinct. **[assessment]**
- [ ] **[Recommended]** Does a **crosswalk already exist** that nobody mentioned? Most estates have
      one — in a spreadsheet, in an integration layer's lookup table, or hard-coded in a report. Find
      it before building a new one: it encodes years of decisions, it is probably partly wrong, and
      both facts are useful.
- [ ] **[Optional]** Is the *absence* of an MDM programme a defensible position for this estate? One
      source system, one authoring point, and no acquisitions is not an MDM problem, and buying a hub
      for it produces synchronisation work with no compensating benefit. **[assessment]**

### Implementation style

- [ ] **[Critical]** Has the implementation style been chosen **explicitly** from the four
      industry-standard ones, with what each commits you to operationally understood rather than
      inferred from the demo?

  | Style | Where master data is authored | What the hub holds | What it commits you to | Typical fit |
  |---|---|---|---|---|
  | **Registry** | Sources only | Keys, match links, and the rules to assemble a view on read | Read-time assembly latency and availability; no write-back, so source data quality never improves; the assembled view exists only at query time | Many sources, low appetite for changing them, analytical consumption, or a constraint that the data must not be copied |
  | **Consolidation** | Sources only | A physical merged golden record, built downstream | The hub is a copy and therefore lags; it is authoritative for reporting and explicitly not for operations; source divergence continues | Reporting and analytics; the usual first step after a merger |
  | **Coexistence** | Sources **and** the hub | The golden record, maintained centrally and published back to subscribing systems | Bidirectional synchronisation, conflict resolution in both directions, and every subscriber being able to accept an update it did not originate — which is usually the part nobody costs | Distributed authoring where the organisation genuinely intends the sources to improve |
  | **Centralised / transaction hub** | The hub | The system of record; sources subscribe | The hub becomes production-critical: availability, latency, change control and support equal to the operational systems it feeds | Greenfield, or a mandate strong enough to change how people author data |

- [ ] **[Critical]** If coexistence or a transaction hub is proposed, has the **operational SLA** been
      written down and accepted by whoever will be paged? A transaction hub is a system of record: its
      outage is an outage of every subscribing system, and its change-freeze calendar becomes
      everyone's change-freeze calendar. This is the commitment most often accepted implicitly and
      most often regretted. **[assessment]**
- [ ] **[Critical]** Is **write-back designed against the source's own validation**, where the style
      includes it? Publishing a corrected address into a source that silently rejects it, or that
      accepts it and overwrites it on the next batch from a third system, is the characteristic
      coexistence failure — and it looks like success from the hub, because the hub sent the message.
      Round-trip verification (read the value back from the source after publishing) is the control.
      **[assessment]**
- [ ] **[Critical]** Is the **migration path between styles** understood as a sequence of projects
      rather than a configuration change? Registry → consolidation → coexistence → transaction hub is
      the usual maturity ordering, and each step adds a category of work (physical storage, then
      publish-back, then authoring and workflow) rather than a setting. Vendors will say the platform
      supports all four, which is true and does not make the transition cheap. **[assessment]**
- [ ] **[Recommended]** Is a **different style per domain** allowed rather than one style imposed
      estate-wide? Mastering product centrally while leaving customer in registry style is a coherent
      and common answer. **[verified]** SAP documents consolidation and central governance as
      separable in its own product — consolidation "can be used with or without central governance",
      with the activation-by-change-request behaviour a choice — which is the same idea expressed as
      product configuration.
- [ ] **[Recommended]** For registry style, has the **read-time assembly cost** been measured against
      the consumer's latency budget, including the failure behaviour when one source is unavailable?
      A registry assembles from sources at query time; a source outage is therefore a partial answer,
      and "partial answer" needs a defined semantic before it happens rather than after.
- [ ] **[Optional]** Where the constraint on copying data is legal or contractual rather than
      technical, has that been stated as the driver? It is a legitimate and decisive reason to choose
      registry style, and it is worth recording as such so the choice is not revisited annually.

### Matching: deterministic versus probabilistic

- [ ] **[Critical]** Is matching **deterministic where a trustworthy shared identifier exists** and
      probabilistic only where it does not? Deterministic rules are explainable, auditable, cheap, and
      reproducible; probabilistic matching recovers the matches deterministic rules miss and costs
      explainability. Most working systems are a waterfall of both. **[verified]** AWS Entity
      Resolution offers exactly this split — "rule-based matching, machine learning-based matching (ML
      matching), and data service provider-led matching" — with rule-based documented as "a
      hierarchical set of waterfall matching rules".
- [ ] **[Critical]** Has the **trustworthiness of each candidate deterministic key been tested rather
      than assumed**? A national identifier, account number or email address is a deterministic key
      only if it is unique in practice, not merely unique by declaration. Reused, shared, and
      placeholder values are the normal case, and each of them turns a deterministic rule into a
      bulk-merge instrument. `patterns/entity-resolution.md` covers the profiling that establishes
      this.
- [ ] **[Recommended]** Is there a **defined uncertain band** between automatic merge and automatic
      non-match, sized against the review capacity that actually exists? A two-threshold design
      (auto-merge, review, auto-reject) is the classical record-linkage structure and it is the point
      at which a technical parameter becomes a staffing decision. Setting one threshold instead of two
      does not remove the uncertain pairs; it just assigns them silently.
- [ ] **[Optional]** Where a data service provider or third-party identity graph is used to supply
      matches, is it understood which of your data leaves and what the provider's own precision
      characteristics are? **[verified]** AWS documents provider-led matching as a distinct workflow
      type with its own pricing and a subscription prerequisite.

### Survivorship

- [ ] **[Critical]** Is survivorship defined **per attribute**, not per record? The best source for a
      postal address is rarely the best source for a date of birth, and "the winning record wins
      everything" throws away known-good values for no reason. **[verified]** Semarchy defines a
      survivorship rule as applying "to either a single attribute or a set of attributes within a
      specific entity"; Reltio computes an operational value per attribute rather than per record.
      Both are attribute-grain by construction, and a design that ignores that is using the tool
      against its own model.
- [ ] **[Critical]** Has **recency versus authority** been decided explicitly, per attribute?
      Most tools default to recency, and recency is frequently the wrong answer: a CRM record touched
      by a marketing synchronisation is more recent and less authoritative than an
      identity-verified record captured at onboarding. **[verified]** Informatica models this as
      trust scores from 0 to 100 assigned by source, with recency as the *tiebreak* rather than the
      rule — "if two columns are trust-enabled, then the cell with the highest trust score wins; if
      the trust scores are equal, then the cell with the most recent `LAST_UPDATE_DATE` wins".
      **[assessment]** That ordering — authority first, recency as tiebreak — is the right default,
      and adopting the reverse because it is easier to configure is the single most common
      survivorship error.
- [ ] **[Critical]** Is the survivorship rule set **owned by the business and recorded outside the
      tool's configuration**, in a form a non-implementer can review? A rule that exists only as a
      tool configuration is not reviewable by the person accountable for it, does not survive a tool
      migration, and cannot be produced as evidence. A table of attribute, ranked sources, and the
      reason for the ranking is the artefact; the tool configuration is its implementation.
      **[assessment]**
- [ ] **[Critical]** Is it explicit that a survivorship-composed golden record **may exist in no
      source system**? Name from CRM, address from billing, date of birth from onboarding is a
      synthesis, not a record anyone ever created. That is usually fine and occasionally matters a
      great deal — when the record is shown to the customer, used as evidence, or relied on as
      "what the system held". Decide which of those apply before, not after.
- [ ] **[Recommended]** Are the tool's built-in consolidation strategies treated as **defaults to be
      overridden**, not as decisions? **[verified]** Semarchy ships Any Value, Largest Value, Longest
      Value, Most Frequent Value, Shortest Value, Smallest Value, and Custom Ranking, and creates
      every entity with a default rule using Custom Ranking with no ranking expression — that is, a
      rule that must be adjusted. **[assessment]** "Most frequent value" deserves particular
      suspicion: across five systems that all synchronise from the same upstream, it counts copies,
      not evidence, and hands the decision to whichever source has been replicated most.
- [ ] **[Recommended]** Is a **steward override modelled as its own layer** that outranks automatic
      consolidation and survives the next load? **[verified]** Semarchy separates the consolidation
      rule (how to pick among source values) from the override rule (how user-authored values
      override the consolidated value) for exactly this reason. Without the separation, a steward's
      correction is silently reverted by the next batch and the steward stops correcting things.
- [ ] **[Recommended]** Is **per-attribute provenance retained on the golden record** — which source
      contributed each surviving value, and when? **[verified]** Reltio's crosswalks associate
      attribute values with the source that supplied them, and the documentation is explicit that this
      is partly so values can be returned to the original entity if an unmerge is requested. This is
      the same discipline as the record-source column in `general/data-modelling.md`, and it is what
      makes both dispute resolution and reversal possible.
- [ ] **[Optional]** Is there a rule for what happens when the **winning source stops sending** an
      attribute? Silence is not a value. Deciding between "retain the last known value", "fall through
      to the next-ranked source", and "null it" is a per-attribute decision with visible downstream
      consequences, and defaulting to whichever the tool happens to do is how stale values persist
      for years.

### The golden record and its limits

- [ ] **[Critical]** Is a **single** golden record actually the right model, or do different consumers
      legitimately need **different views of the same entity**? This is the most under-examined
      assumption in the discipline. Consider one retail bank customer: billing needs the legal person
      and the registered address; marketing needs the household; servicing needs whoever actually
      calls; regulatory aggregation needs the legal-entity hierarchy as it stood on the reporting
      date. Those are four different groupings of the same underlying records, all correct, and only
      one of them is "the customer". Forcing them into one flattened record does not resolve the
      disagreement — it relocates it into a permanent argument about whose definition the golden
      record encodes. **[assessment]**
- [ ] **[Critical]** Where multiple views are legitimate, is the architecture **stable entity identity
      plus multiple projections**, rather than one record? The durable artefact is the *cluster* — the
      set of source records asserted to be one entity, with a stable identifier and per-source
      provenance. Golden *views* are then projected from it per consumer, each with its own
      survivorship rules and its own grain. This costs one extra concept and removes an argument that
      otherwise never ends. **[assessment]** — this is reasoning, not a vendor pattern, though it is
      the shape that per-attribute provenance models such as Reltio's crosswalks make possible.
- [ ] **[Critical]** In business-to-business domains, is the entity a **hierarchy** rather than a
      record — legal entity, operating site, contact — and is the level at which questions are asked
      preserved? Flattening a corporate structure into one "customer" destroys the exact granularity
      that credit exposure, contract compliance and regulatory aggregation are computed at.
      **[assessment]**
- [ ] **[Critical]** Have the **legal constraints on combining attributes** been checked before
      merging, rather than after? Where consent, lawful basis, or jurisdictional restriction differs
      between two source records, the merged record can be the violation — a single record combining
      data the organisation was permitted to hold only separately. This is a genuine reason for a
      registry-style architecture and a genuine reason for per-consumer projections. See
      `general/data-classification.md` and `general/data-governance.md`. **[assessment]**
- [ ] **[Recommended]** Do downstream consumers receive a **stable master identifier** that is
      independent of which source record won the merge? **[verified]** Reltio's merge selects a
      "winning entity" ID by comparing creation and update timestamps when no winner is specified —
      which is a perfectly reasonable rule and precisely why the *published* key must not be the
      surviving source key. If it is, every re-run that changes a merge outcome changes downstream
      keys, and the change propagates to everything that stored them. **[assessment]**
- [ ] **[Recommended]** Is the golden record **versioned with history**? Without it, "why did this
      value change" is unanswerable, and every slowly-changing dimension built downstream sits on a
      base that mutates without record — see `general/data-modelling.md` on bi-temporal history and
      point-in-time reconstruction, which cannot be satisfied by a golden record that only holds
      current state.
- [ ] **[Optional]** Is there a documented answer to "**which record do we show the customer**"? It is
      not necessarily the golden record, and the case where it is not — a synthesised record the
      customer never provided — is worth deciding deliberately.

### Stewardship workflow

- [ ] **[Critical]** Does a **steward exist before the tool is bought**? A matching tool with no
      steward is worse than no tool at all, because it manufactures confident wrong merges at scale
      and publishes them with the authority of the platform. Manual duplication is visible and
      annoying; automated false merges are invisible and authoritative. **[assessment]**
- [ ] **[Critical]** Is there an **exception queue with a named owner and a response SLA**, rather
      than a steward role with no work management? `general/data-governance.md` makes this point for
      governance generally; it binds hardest here, because matching generates a continuous,
      predictable stream of genuinely ambiguous pairs that no amount of tuning removes.
- [ ] **[Critical]** Is it decided **what downstream consumers see while a conflict is unresolved**?
      Three defensible answers exist: suppress the entity from published output; publish it with an
      explicit unresolved flag that consumers must handle; publish the last resolved state and hold
      the conflict internally. Each has different consumer obligations. Silence — publishing as though
      nothing is in dispute — is the fourth option, it is the default when nobody chooses, and it is
      the one that destroys trust when the discrepancy surfaces downstream. **[assessment]**
- [ ] **[Critical]** Is the **exception rate forecast and staffed** before go-live? The review-band
      thresholds determine queue volume directly: a threshold set for high precision on automatic
      merges necessarily pushes more pairs to humans. That is a resourcing decision expressed as a
      number in a configuration file, and it is routinely made by someone with no visibility of the
      staffing consequence. **[assessment]**
- [ ] **[Recommended]** Do stewards see the **source records and their provenance**, not just the
      merged result? Adjudicating a merge requires seeing what each source actually said and when.
      **[verified]** Reltio surfaces the source of every attribute with its crosswalk ID for this
      purpose. A steward UI that shows only the composed record is asking for a decision without the
      evidence.
- [ ] **[Recommended]** Are steward decisions **captured as labelled data** and fed back into rule or
      model improvement, rather than consumed once and discarded? This is the cheapest source of
      ground truth an organisation will ever have, and most programmes throw it away. See
      `patterns/entity-resolution.md` on active learning.
- [ ] **[Recommended]** Are **negative decisions persisted**? "These two are not the same" must be
      stored and honoured by subsequent runs, or the steward re-adjudicates the same pair every cycle
      and correctly concludes the system does not listen. **[assessment]**
- [ ] **[Optional]** Is steward throughput measured (queue depth, age of oldest item, decisions per
      day, reversal rate)? Reversal rate in particular is the leading indicator that the rules are
      wrong rather than that the data is hard.

### Reference data management

- [ ] **[Critical]** Is **reference data separated from master data**, and is it being solved first?
      Country and currency codes, units of measure, product taxonomies, status and reason codes, and
      the chart of accounts are small, slow-changing, enumerable, and require no probabilistic
      matching at all. The mappings can be written down completely and reviewed by a human in an
      afternoon. **[assessment]** This is very often the highest ratio of delivered value to effort in
      the entire programme, and it is routinely deferred behind a customer-matching workstream that
      will not deliver for a year.
- [ ] **[Critical]** Is there **one authoritative, versioned, effective-dated mapping per code set**?
      Codes are retired and reused: ISO 3166-1 has reassigned alpha-2 codes as countries have
      dissolved and formed, and internal status codes get recycled far more casually than that. A
      mapping table without effective dates silently rewrites history the moment a code changes
      meaning, and the rewrite is undetectable afterwards.
- [ ] **[Critical]** Is the **chart-of-accounts mapping** recognised as jointly a finance artefact and
      a data artefact, and owned by finance? It is the same mapping the consolidation and planning
      systems depend on — see `general/enterprise-performance-management.md`. Two independently
      maintained account mappings in one organisation is a reconciliation obligation nobody signed up
      for. **[assessment]**
- [ ] **[Recommended]** Are **external standards adopted where they exist** rather than local schemes
      invented? ISO 3166 for countries, ISO 4217 for currencies, UNSPSC or GS1 GPC for product
      classification, LEI for legal entities. The value is not the taxonomy itself — it is that
      counterparties, regulators and acquired companies already use it, so the mapping to the next
      system you integrate is already done.
- [ ] **[Recommended]** Is reference data **distributed as data** — an API or table consumers read at
      run time — rather than embedded as enumerations compiled into each application? Embedded
      enumerations are how a retired code stays live in three systems for five years.
- [ ] **[Optional]** Is there a change process for reference data with a lead time, given that a code
      addition can break a downstream constraint or a report filter on the day it lands?

### Tooling and the operating model

- [ ] **[Critical]** Is it understood that **MDM is an operating-model commitment, not a tool
      purchase**? A tool supplies a matching engine, a survivorship configuration surface, a steward
      interface, and an audit trail. It supplies none of the decisions those need: which sources are
      authoritative, what "the same" means, who adjudicates, what the SLA is, and what consumers see
      while a case is open. A programme that buys the tool and defers the decisions has bought a
      mechanism for making the wrong decisions faster. **[assessment]**
- [ ] **[Critical]** Is the **ongoing run cost** modelled — steward capacity, rule maintenance, source
      onboarding, and the periodic re-tuning that follows every source change — rather than only the
      implementation cost? MDM is a standing operational function. Funding it as a project produces a
      hub that is accurate on the day it goes live and decays from then on. **[assessment]**
- [ ] **[Critical]** Has the tool's **un-merge capability been verified rather than assumed**,
      including bulk un-merge after a rule change? See `patterns/entity-resolution.md` — this is a
      first-class requirement, not a feature checkbox, and the difference between per-record un-merge
      and bulk un-merge is the difference between fixing one mistake and recovering from a bad rule
      deployment. **[verified]** Reltio documents both an automatic-unmerge task and a batch unmerge
      operation, and states that the task must be run after match rules or survivorship rules used in
      match rules are added, edited or deleted.
- [ ] **[Recommended]** Has **build-on-the-platform** been evaluated honestly against buy, rather than
      dismissed or assumed? The build option is genuinely viable for analytical mastering — matching
      libraries and native string-similarity functions are mature — and genuinely weak for the parts
      nobody remembers to scope: the steward interface, the audit trail, workflow, un-merge, and
      publish-back. The realistic decision rule is that the *matching* is the easy part to build and
      the *stewardship application* is not. **[assessment]**
- [ ] **[Recommended]** Is the **exit path** known — can the crosswalk (source key to master
      identifier, with provenance) be exported in full? That table is the accumulated value of the
      programme. If it can only be read through the vendor's application, the switching cost is the
      whole programme rather than the licence.
- [ ] **[Optional]** Where an open-source library is chosen, has the **licence** been checked against
      how the output will be distributed? **[verified]** Zingg is AGPL v3.0, which is a materially
      different obligation from a permissive licence and is easy to miss in a proof of concept.

## Why This Matters

The characteristic MDM failure is not a bad match algorithm. It is a programme that treats a
modelling and stewardship problem as an engineering problem, and therefore staffs it with engineers,
measures it with pipeline metrics, and discovers at the end that no decisions were made. Every
symptom of that failure looks technical — duplicate rates, match quality, tool limitations — and none
of the fixes are.

The post-merger case is the clearest instance and the most expensive. Two organisations combine; the
customer masters, product taxonomies and charts of accounts must be reconciled; and because the
obvious venue for that reconciliation is a shared data platform, the *problem* gets renamed after the
*venue*. The platform is then delivered on time and to specification, and the organisation still
cannot produce a combined customer count, because producing one requires somebody with authority to
say that the acquired company's CRM outranks the acquirer's billing system for postal addresses and
the reverse for legal names. Nobody was appointed to say that. The programme is judged a failure of
the platform.

The second failure is buying the tool first. MDM tools are good: they implement matching, per-source
trust, per-attribute survivorship, steward workflow, and audit. What they cannot do is supply the
inputs those mechanisms consume. Deployed without a steward and without a business owner, a matching
engine does exactly what it is built to do — it merges records confidently, at scale, according to
whatever defaults were left in place — and every one of those merges arrives downstream carrying the
platform's authority. The pre-tool state is visible duplication that annoys people into fixing it.
The post-tool state is invisible over-merging that nobody detects until a customer sees another
customer's data. That is not an improvement, and it is the normal outcome of deploying the mechanism
without the operating model.

Survivorship is where the "technical decision" mistake is most concentrated. Which source wins for
which attribute is a statement about which parts of the organisation the organisation trusts, and it
has consequences for billing accuracy, regulatory reporting, and customer experience. It is
nonetheless routinely settled during configuration by whoever is closest to the keyboard, usually as
"most recent wins" because that is the path of least resistance in most tools. Recency is a proxy for
authority, and it is a bad one: automated synchronisation touches records constantly and knows
nothing, while the highest-authority capture event — identity verification at onboarding, a signed
contract, a regulatory filing — is by construction old. Systems that default to recency
systematically prefer the least authoritative source they have.

The golden-record assumption deserves more scepticism than it gets. "One version of the truth" is a
good slogan for eliminating accidental disagreement and a bad model for entities whose consumers have
genuinely different, equally legitimate needs. Billing's legal person, marketing's household,
servicing's caller and regulation's legal-entity hierarchy are not four attempts at one answer; they
are four correct answers to four different questions. Forcing them into one record does not settle
the argument, it institutionalises it — and the organisation then spends years relitigating the
definition of "customer" in change requests. Keeping the *identity* single and the *views* plural
costs one extra concept and ends the argument.

Reference data is the counterweight and the most reliably under-exploited opportunity in the
discipline. Country codes, currencies, units, product classifications and the chart of accounts are
finite, slow, enumerable, and require no statistics. The mappings can be completed, reviewed and
signed off. They deliver visible cross-system consistency in weeks. And they are consistently
deferred behind a customer-matching workstream that will not produce anything for a year, on the
grounds that they are less interesting — which they are, and which is not a reason.

## Vendors

Software vendors only, with capability claims marked for confidence. Naming in this market changes
frequently — IBM's product has been renamed twice in recent years and Microsoft's has been removed
from the product it shipped in — so re-check before quoting any of this.

### Informatica

Multidomain MDM (on-premises and the cloud edition) is the long-standing enterprise incumbent.
**[verified]** Informatica's model is **trust scores**: "a measure of the relative trustworthiness
associated with field values based on their source system, change history, and other business
rules", scored 0 to 100, with a documented tiebreak that "if two columns are trust-enabled, then the
cell with the highest trust score wins; if the trust scores are equal, then the cell with the most
recent `LAST_UPDATE_DATE` wins". **[verified]** Survivorship is documented as "the process of
creating a master record or the most trusted version of a record from multiple matching source
records", and the resulting record is presented to stewards as the "best version of the truth", which
a steward can override. **[assessment]** The trust-score model is the clearest commercial expression
of authority-over-recency, and it is worth understanding even if the tool is not chosen, because it
is the shape any hand-built survivorship layer converges on.

### IBM

**[verified]** IBM's current product is **IBM Master Data Management**, described on IBM's product
page as "an AI-infused, cloud-native platform that unifies and governs data across domains" that
"uses machine learning for entity resolution and relationship discovery", with SaaS, on-premises and
hybrid deployment. **[verified]** It is the successor to **IBM Match 360**, which is in turn the
successor line to **InfoSphere MDM**: IBM's Cloud Pak for Data documentation carries a procedure
titled "Adding master data from IBM InfoSphere MDM to IBM Master Data Management", which both
confirms the naming and confirms that InfoSphere-era estates are expected to migrate rather than
remain. **[assessment]** For an estate running InfoSphere MDM, that migration path is the fact that
matters most in a selection: the incumbent option is not "stay where you are".

### SAP

**[verified]** SAP Master Data Governance covers both **consolidation** and **central governance**,
and SAP documents them as separable: consolidation and mass processing "can be used with or without
central governance", with activation by change request and the use of central-governance validations
each presented as a choice. **[verified]** The consolidation process includes an explicit **best
record calculation** step with data controllers assigned to it, and the documented domains include
Business Partner (with customer and vendor), Business Partner Relationships, Material Master, and
custom objects. **[assessment]** The natural fit is an SAP-centric estate where the master data
objects are already SAP objects; the consolidation-plus-central-governance combination is a good
structural match for the post-merger case specifically, because it lets an organisation consolidate
first and impose central authoring later without changing products.

### Reltio

**[verified]** Cloud-native multidomain MDM whose distinguishing structure is the **crosswalk** — a
unique identifier linking an entity to its originating source, with attribute values associated to
the crosswalk that supplied them, so the source of every attribute is visible with its crosswalk ID.
**[verified]** That structure is explicitly what makes reversal possible: values accumulate within an
attribute with the integrity of their originating crosswalk maintained, including for "the need to
return the attribute and its values to the original entity if an unmerge is requested".
**[verified]** Reltio also documents **automatic unmerge** and a **batch unmerge** operation, and
states that the automatic-unmerge task should be run after match rules are added, deleted or edited,
or survivorship rules used in match rules are changed. **[assessment]** Per-attribute provenance as a
first-class construct, rather than an audit log bolted on, is the property to look for in any tool
evaluated for this class of problem — it is the precondition for both dispute resolution and
un-merge.

### Semarchy

**[verified]** Semarchy xDM models survivorship as two composable parts: a **consolidation rule**
defining how duplicate values are combined into the golden record, and an **override rule** defining
how user-authored values override the consolidated result. **[verified]** Consolidation strategies
shipped are Any Value, Largest Value, Longest Value, Most Frequent Value, Shortest Value, Smallest
Value, and Custom Ranking (a SemQL ranking expression); every entity is created with a master-ID
survivorship rule and a default rule using Custom Ranking with no ranking expression, which the
documentation says should be adjusted. **[verified]** There are also **ID survivorship rules** that
determine which master record's ID anchors the golden record. **[assessment]** The
consolidation/override split is the cleanest published expression of the steward-override problem,
and it is the model to copy if you are building rather than buying.

### Stibo Systems

**[verified]** STEP's matching and linking is built on **match codes** and **matching algorithms**,
with incoming source records matched against existing golden records and merged using survivorship
rules where a match is found. **[assessment]** Stibo's centre of gravity is product and multidomain
mastering in retail, manufacturing and distribution rather than party mastering, which matters mostly
for which reference customers and accelerators exist rather than for the architecture.

### Microsoft

**[verified]** SQL Server **Master Data Services is removed in SQL Server 2025 (17.x)**; Microsoft
continues to support it in SQL Server 2022 (16.x) and earlier. **[assessment]** This is the single
most actionable vendor fact in this section for existing estates: MDS is widely deployed as a
low-profile reference-data and hierarchy tool, often by finance rather than IT, and it commonly does
not appear on application inventories. Any SQL Server upgrade plan that reaches SQL Server 2025
should be checked for an MDS dependency explicitly, because the discovery point is otherwise the
upgrade itself.

### Build on the platform

A credible option for analytical mastering, and the components are mature:

- **[verified]** **AWS Entity Resolution** is a managed matching service offering rule-based, ML-based
  and provider-led matching, reading inputs from AWS Glue (up to 20 data inputs per workflow) and
  assigning a Match ID and a confidence level to matched sets. Rule-based matching is documented as a
  configurable hierarchical waterfall; ML-based matching does not support hashed data and normalises
  only Name, Phone and Email. **[verified]** Pricing is per record processed: **$0.25 per 1,000
  records** for rule-based or ML-powered matching and **$0.10 per 1,000 records** for data service
  provider matching (which requires a subscription); AWS states pricing does not vary by Region.
- **[verified]** **Snowflake** ships `JAROWINKLER_SIMILARITY` (returns 0-100, case-insensitive,
  default scaling factor 0.1) and `EDITDISTANCE` as built-in string functions, which with blocking
  keys is enough to build candidate scoring in SQL.
- **[verified]** **Splink** (UK Ministry of Justice, open source) implements the Fellegi-Sunter model
  with expectation-maximisation parameter estimation across several SQL backends. See
  `patterns/entity-resolution.md`.
- **[verified]** **Zingg** is an ML-based entity-resolution tool running on Spark with an interactive
  active-learning training-data builder; it is licensed **AGPL v3.0**, and its README states typical
  comparison volumes of "0.05-1% of the possible problem space" after its learned blocking.
- **[verified]** **dedupe** is a Python library for deduplication and record linkage using active
  learning (its hosted documentation sits behind a bot challenge; the source repository is the
  reliable reference).

**[assessment]** The honest boundary is that all of the above solve *matching*. None of them supplies
a steward application, an exception queue with SLAs, an audit trail a regulator would accept,
publish-back to source systems, or bulk un-merge. Building those is where a build-instead-of-buy
decision usually turns out to have been a decision to build an MDM product. For analytical mastering
consumed by a warehouse, build is often right. For operational mastering with stewards and
publish-back, it usually is not.

## What Is Verified and What Is Judgement

**Verified against the cited page on 2026-07-27** (each has a URL in Reference Links): Informatica
trust scores, the trust-then-recency tiebreak, the survivorship definition and best-version-of-the-
truth steward override; IBM's current product name and positioning and the documented InfoSphere MDM
→ IBM Master Data Management path; SAP MDG consolidation being usable with or without central
governance, the best-record-calculation step, and the listed domains; Reltio crosswalks and
per-attribute source provenance, the winning-entity-ID selection rule, automatic and batch unmerge,
and the requirement to re-run unmerge after rule changes; Semarchy's consolidation/override rule
split, the enumerated consolidation strategies, the default-rule behaviour, and ID survivorship
rules; Stibo STEP match codes, matching algorithms and merge-into-golden-record behaviour; Microsoft
MDS being removed in SQL Server 2025 and supported in 2022 and earlier; AWS Entity Resolution's three
matching techniques, the waterfall rule structure, the 20-input limit, ML normalisation scope, and
the published per-1,000-record pricing; Snowflake's `JAROWINKLER_SIMILARITY` and `EDITDISTANCE`;
Zingg's AGPL v3.0 licence and its stated comparison-space reduction.

**Assessment, not vendor claim:** the whole "this is not a platform problem" framing and the
diagnostic question derived from it; the claim that the platform budget silently absorbs the
integration problem; the argument that a single golden record is the wrong model where consumers
legitimately differ, and the identity-plus-projections alternative; the authority-over-recency
default; the "a tool with no steward is worse than no tool" claim; the ranking of reference data as
the highest value-to-effort work in most programmes; the build-versus-buy boundary drawn at the
steward application rather than at the matching engine; the maturity ordering of the four
implementation styles and the assertion that each transition is a project; and every "common failure"
characterisation in Why This Matters.

**Explicitly not verified this session:**

- **Any market-share, adoption, duplicate-rate, match-rate, or cost-of-poor-data-quality figure.**
  None is quoted in this file. Match rates and data-quality cost statistics circulate widely without
  attributable primary sources, and where they do have one, they are functions of a specific
  population, attribute availability and threshold, and are not transferable between estates. If a
  number is needed for a business case, measure it on the estate's own data.
- **`help.sap.com`**, which serves a roughly 1 KB JavaScript shell to automated clients rather than
  content. The SAP claims above were verified from `learning.sap.com`, which renders; the SAP Help
  Portal link is given as the canonical entry point only.
- **Pricing and licence tiering for every commercial vendor named here** except the AWS figures
  above. Assume the stewardship, workflow and audit capabilities a regulated buyer needs sit in a
  higher tier until proven otherwise — that is the pattern across the adjacent categories in
  `patterns/data-platform-selection.md`.
- **Profisee, Ataccama, Tamr, Senzing and the rest of the market.** Not evaluated; no capability claim
  is made about any of them.

## Common Decisions (ADR Triggers)

- **Whether this is an MDM workstream at all** — a funded entity-resolution and stewardship
  workstream with its own business owner vs folding it into a platform programme's backlog, which is
  the default and which reliably under-resources it. Trigger: any acceptance criterion that reduces
  to "one row per customer"
- **Implementation style** — registry (no copy, read-time assembly, sources unchanged) vs
  consolidation (physical golden record downstream, authoritative for reporting only) vs coexistence
  (bidirectional, sources improve, synchronisation and conflict handling in both directions) vs
  transaction hub (hub is the system of record, with the operational commitments that implies).
  Decided primarily by whether consumption is operational or analytical, and by whether the
  organisation can change how people author data
- **Style per domain vs one style estate-wide** — a single style is simpler to operate and forces the
  hardest domain's requirements onto the easiest; per-domain styles fit better and produce more
  moving parts
- **Deterministic vs probabilistic vs waterfall matching** — deterministic where a trustworthy shared
  identifier exists (explainable, auditable, cheap); probabilistic where it does not (recovers matches
  deterministic rules miss, costs explainability); waterfall of both, which is what most working
  systems converge on. Forced toward deterministic by any explainability obligation
- **Survivorship basis** — source authority ranking (correct, requires a business decision per
  attribute) vs recency (easy, defaults in most tools, systematically prefers the least authoritative
  source) vs field-level trust scores with decay (Informatica's model; most expressive, most to
  configure and maintain)
- **Single golden record vs stable identity with per-consumer views** — one record (simple, forces one
  definition to win, institutionalises the argument) vs cluster identity plus projections (one extra
  concept, ends the definitional argument, requires per-attribute provenance to be retained)
- **What consumers see during an unresolved conflict** — suppress the entity, publish with an
  unresolved flag, or publish last-resolved-state. All defensible; the fourth option, publishing
  silently as though nothing is disputed, is what happens when nobody decides
- **Buy an MDM platform vs build on the data platform** — buy for operational mastering with
  stewards, workflow, publish-back and audit; build for analytical mastering where the consumer is a
  warehouse and the steward application is not required. The matching is the part that is cheap to
  build; the stewardship application is not
- **Managed matching service vs library vs commercial hub** — AWS Entity Resolution or equivalent
  (fastest to a result, per-record pricing, limited stewardship) vs Splink/Zingg/dedupe (full control,
  no licence cost, and you own the operational surface — check the licence) vs a commercial MDM hub
  (complete operating surface, licence and implementation cost, and an exit cost concentrated in the
  crosswalk)
- **Reference data first vs master data first** — reference data first delivers visible cross-system
  consistency in weeks with no statistics involved; master data first goes after the bigger prize and
  typically shows nothing for a year. The sequencing choice is usually made by which is more
  interesting rather than by which is more valuable
- **Where the crosswalk lives** — inside the MDM tool (natural, and concentrates the exit cost) vs
  materialised into the data platform as a governed table (portable, and needs a synchronisation
  story). This decides what switching costs later

## Reference Architectures

- **Registry over a lakehouse (analytical, no copy).** Sources land in the platform unchanged; a
  resolution job produces a crosswalk table (source key → master identifier, with match evidence and
  provenance) and nothing else; conformed dimensions join through the crosswalk at build time. No
  golden record is materialised and no source is modified. Cheapest to stand up, keeps every source
  authoritative for itself, and delivers nothing to operational systems.
- **Consolidation hub feeding the conformed dimension (the common analytical default).** Resolution
  produces the crosswalk; survivorship produces a physical golden record per entity; the golden record
  becomes the conformed dimension's source, with a durable master identifier carried as the dimension's
  supernatural key per `general/data-modelling.md`. Steward decisions are captured in the platform and
  fed back as labels. Authoritative for reporting, explicitly not for operations.
- **Coexistence with publish-back.** As above, plus a publish path to subscribing source systems and a
  round-trip verification step that reads the value back to confirm the source accepted it. Adds
  conflict resolution in both directions and a per-source contract describing what each system will
  accept. The step that is routinely under-costed is not the publish — it is every source system's
  ability to receive an update it did not originate.
- **Transaction hub as system of record.** Authoring moves into the hub; sources subscribe. Requires
  operational availability, latency and change control equal to the systems it feeds, plus a
  user-facing authoring application and its own support model. Justified by a mandate, rarely by an
  architecture argument alone.
- **Reference-data-first.** A governed, versioned, effective-dated code and mapping service (country,
  currency, unit, product classification, chart of accounts) published as data and consumed at run
  time, delivered ahead of any entity matching. Low effort, visible cross-system consistency, and it
  builds the governance muscle — owner, change process, effective dating — that the harder domains
  will need.
- **Post-merger sequence.** Reference data and chart of accounts first (weeks); registry-style
  customer and product crosswalks second, to establish overlap and size the real problem; consolidation
  for reporting third; and only then a decision about coexistence or a transaction hub, taken with
  measured data rather than with the assumptions available on day one. **[assessment]**

## Reference Links

All links checked on 2026-07-27; codes and effective URLs are as returned that day.

- [Master data management (Wikipedia)](https://en.wikipedia.org/wiki/Master_data_management)
  — vendor-neutral overview of the discipline and its vocabulary
- [DAMA-DMBOK (DAMA International)](https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/)
  — the data-management body of knowledge; master and reference data management are knowledge areas
  within it
- [Reltio: What are MDM implementation styles?](https://www.reltio.com/glossary/master-data-management/what-are-mdm-implementation-styles/)
  — enumerates the registry, consolidation, coexistence and centralised styles and the factors that
  select between them
- [Stibo Systems: 4 common MDM implementation styles](https://www.stibosystems.com/blog/4-common-master-data-management-implementation-styles)
  — a second independent enumeration of the same four styles
- [Profisee: MDM implementation styles explained](https://profisee.com/blog/master-data-management-implementation-styles/)
  — a third, useful mainly for confirming the taxonomy is industry-standard rather than one vendor's
- [Informatica: Trust Levels](https://docs.informatica.com/master-data-management/multidomain-mdm/10-3/data-steward-guide/introduction/key-concepts/trust-levels.html)
  — trust scores 0-100 by source, and the trust-then-`LAST_UPDATE_DATE` tiebreak
- [Informatica: Survivorship (glossary)](https://docs.informatica.com/master-data-management/multidomain-mdm/10-3/data-steward-guide/glossary/glossary-of-terms/survivorship.html)
  — survivorship as creating the most trusted version from multiple matching source records
- [Informatica: Best version of the truth and trust scores](https://docs.informatica.com/master-data-management/multidomain-mdm/10-3/data-director-user-guide/data-director-with-business-entities/resolving-duplicate-records/resolving-duplicate-records-overview/best-version-of-the-truth-and-trust-scores.html)
  — the steward's merge-preview override of the computed best version
- [Informatica Master Data Management (product page)](https://www.informatica.com/products/master-data-management.html)
  — current product positioning
- [IBM Master Data Management (product page)](https://www.ibm.com/products/master-data-management)
  — the current product name, multidomain scope, and deployment options
- [IBM: Adding master data from IBM InfoSphere MDM to IBM Master Data Management](https://dataplatform.cloud.ibm.com/docs/content/wsj/mdm/publish-mdm.html)
  — the documented migration path from the InfoSphere-era product
- [IBM Match 360 (IBM Software Hub documentation)](https://www.ibm.com/docs/en/software-hub/5.2.x?topic=services-match-360)
  — the product documentation entry point. *Note: `ibm.com/docs` serves a JavaScript shell to
  automated clients; contents were not verified from this URL.*
- [SAP Master Data Governance (SAP Help Portal)](https://help.sap.com/docs/SAP_MASTER_DATA_GOVERNANCE)
  — the canonical documentation entry point. *Note: returns a roughly 1 KB JavaScript shell to
  automated clients; contents were not verified from this URL.*
- [SAP Learning: Common features of consolidation and mass processing](https://learning.sap.com/courses/sap-master-data-governance-on-sap-s-4hana/introducing-common-features-of-consolidation-and-mass-processing)
  — consolidation usable with or without central governance, the best-record-calculation step, and
  the supported domains
- [Reltio: Survivorship rules](https://docs.reltio.com/en/objectives/resolve-potential-matches/potential-matching-at-a-glance/potential-matching-navigation/design-survivorship-rules/survivorship-rules)
  — per-attribute operational value and the separation of survivorship from merge
- [Reltio: Crosswalks](https://docs.reltio.com/en/objectives/model-data/data-modeling-at-a-glance/data-modeling-operation/define-crosswalks-for-data-sources/crosswalks)
  — crosswalks as source-linked identifiers carrying per-attribute provenance
- [Reltio: Merge matched data](https://docs.reltio.com/en/objectives/resolve-potential-matches/potential-matching-at-a-glance/potential-matching-reference/merge-matched-data)
  — winning-entity-ID selection and what is preserved through a merge
- [Reltio: Automatically unmerge entity records](https://docs.reltio.com/en/objectives/resolve-potential-matches/potential-matching-at-a-glance/potential-matching-operation/unmerge-entity-records/automatically-unmerge-entity-records)
  — automatic unmerge, batch unmerge, and the requirement to re-run after rule changes
- [Semarchy xDM: Create a survivorship rule](https://www.semarchy.com/doc/semarchy-xdm/xdm/latest/Design/matching/create-a-survivorship-rule.html)
  — consolidation rule plus override rule, the enumerated strategies, and the adjustable default
- [Semarchy xDM: Match and merge](https://www.semarchy.com/doc/semarchy-xdm/xdm/latest/Design/matching/matching.html)
  — matching, ID matching, and how matched records reach survivorship
- [Semarchy xDM: Data certification](https://www.semarchy.com/doc/semarchy-xdm/xdm/latest/Integrate/data-certification.html)
  — the certification pipeline from source records to golden records
- [Semarchy: Set survivorship rules (SaaS documentation)](https://docs.semarchy.com/saas/guides/design/certification/match-merge/survivorship-rules)
  — the same model in the current SaaS documentation set
- [Stibo STEP: Match and merge](https://doc.stibosystems.com/doc/version/latest/web/content/mtchlnkmrg/match_action/match_and_merge/matchandmerge.html)
  — match codes, matching algorithms, and merging source records into golden records
- [Microsoft: Discontinued features of Master Data Services](https://learn.microsoft.com/en-us/sql/master-data-services/discontinued-master-data-services-features?view=sql-server-ver17)
  — MDS removed in SQL Server 2025; supported in SQL Server 2022 and earlier
- [Microsoft: Master Data Services overview](https://learn.microsoft.com/en-us/sql/master-data-services/master-data-services-overview-mds?view=sql-server-ver16)
  — what MDS does, for estates that still run it
- [What is AWS Entity Resolution?](https://docs.aws.amazon.com/entityresolution/latest/userguide/what-is-service.html)
  — rule-based, ML-based and provider-led matching; Glue inputs; the 20-input limit
- [AWS Entity Resolution: rule-based matching workflow](https://docs.aws.amazon.com/entityresolution/latest/userguide/creating-matching-workflow-rule-based.html)
  — the configurable hierarchical waterfall rule structure
- [AWS Entity Resolution: ML-based matching workflow](https://docs.aws.amazon.com/entityresolution/latest/userguide/create-matching-workflow-ml.html)
  — match IDs and confidence levels; no hashed-data support; Name/Phone/Email normalisation only
- [AWS Entity Resolution pricing](https://aws.amazon.com/entity-resolution/pricing/)
  — $0.25 per 1,000 records for rule-based or ML matching; $0.10 per 1,000 for provider matching
- [Snowflake: `JAROWINKLER_SIMILARITY`](https://docs.snowflake.com/en/sql-reference/functions/jarowinkler_similarity)
  — 0-100 similarity, case-insensitive, default scaling factor 0.1
- [Snowflake: `EDITDISTANCE`](https://docs.snowflake.com/en/sql-reference/functions/editdistance)
  — Levenshtein distance as a built-in function
- [Zingg (GitHub)](https://github.com/zinggAI/zingg)
  — Spark-based ML entity resolution, active-learning label workflow, AGPL v3.0
- [dedupe (GitHub)](https://github.com/dedupeio/dedupe)
  — Python deduplication and record linkage with active learning. *Note: `docs.dedupe.io` sits behind
  a bot challenge and returns HTTP 429 to automated clients; the repository is the reliable
  reference.*
- [ISO 3166-1 (Wikipedia)](https://en.wikipedia.org/wiki/ISO_3166-1)
  — country codes, including the reassignment history that makes effective dating necessary
- [UNSPSC](https://www.unspsc.org/)
  — the United Nations Standard Products and Services Code, one of the external product taxonomies
  worth adopting rather than reinventing

## See Also

- `patterns/entity-resolution.md` — the matching mechanics this file depends on: blocking, similarity
  scoring, clustering and transitive-closure hazards, precision and recall, un-merge, and temporal
  handling
- `general/data-modelling.md` — conformed dimensions, the bus matrix, slowly changing dimensions, and
  the durable "supernatural" key that a mastered entity's identifier becomes
- `general/data-governance.md` — ownership versus stewardship, exception queues, certification, and
  the catalog and lineage this depends on
- `general/data-ingestion.md` — how source records arrive, and why the capture method constrains what
  can be matched and when
- `general/data-classification.md` — sensitivity and lawful-basis constraints that bear directly on
  whether two records may be merged
- `general/enterprise-performance-management.md` — the chart of accounts and the consolidation mapping
  as a shared reference-data artefact
- `patterns/data-warehouse-migration.md` — where legacy conformance decisions surface during a
  migration, and where they must not simply be carried across
- `patterns/migration-coexistence.md` — the general coexistence problem of which MDM coexistence style
  is a data-layer instance
- `patterns/data-platform-selection.md` — platform selection, and the tier-gating pattern that applies
  to MDM licensing too
- `patterns/core-banking-data-integration.md` — the customer information file as a worked example of
  a party master with duplicate records and many-to-many role semantics
