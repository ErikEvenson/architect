# Entity Resolution and Record Linkage

## Scope

The mechanics of deciding whether two records describe the same real-world entity, and of turning
those pairwise decisions into entity clusters that downstream systems can key on. Covers **blocking
and candidate generation**; **similarity scoring** (edit distance, phonetic, token-based, frequency
weighting) and the normalisation that has to precede it; the **Fellegi-Sunter** decision model and
where deterministic rules belong instead; **clustering and transitive-closure hazards** — the failure
mode that produces a single "customer" containing three unrelated people; **measuring match quality**,
why a labelled sample is unavoidable, and the cost asymmetry between a false merge and a false split;
**human-in-the-loop review and active learning**; **identifiers that are reused, shared, absent or
outright false**; **un-merge as a first-class requirement**; and the **temporal** problem of
distinguishing an entity that legitimately changed from a genuine duplicate.

The surrounding decisions — implementation style, survivorship rules, stewardship operating model,
reference data, and vendor selection — live in `general/master-data-management.md`, which this file
pairs with and does not repeat. For the conformed dimensions and slowly-changing-dimension history
that consume the resulting identifiers, see `general/data-modelling.md`.

**Statements marked [verified] were read from the cited page on 2026-07-27.** Statements marked
**[assessment]** are reasoning, not sourced claim. The algorithmic material rests on the record
linkage literature descending from Fellegi and Sunter (1969); where this file draws on it, the
citation is given. The section
[What Is Verified and What Is Judgement](#what-is-verified-and-what-is-judgement) separates the two
explicitly.

## Overview

Every entity-resolution system, whether it is a managed service, a commercial hub, an open-source
library or five hundred lines of SQL, is the same five stages:

1. **Normalise** — bring the comparable fields into a comparable form.
2. **Block** — generate candidate pairs, because comparing every record with every other record is
   not affordable.
3. **Score** — compute a similarity or a match probability per candidate pair.
4. **Decide** — turn the score into match / review / non-match.
5. **Cluster** — turn accepted pairs into entities with stable identifiers.

Each stage has a distinct and non-substitutable failure mode, which is why "the matching is bad" is
never a diagnosis. A true match whose records disagree on the blocking key is never compared, and no
amount of model tuning recovers it. A perfectly scored pair set can still produce nonsense entities if
the clustering step is naive. Measuring the stages separately is the difference between fixing the
problem and tuning the wrong parameter. **[assessment]**

## Checklist

### Framing and ground truth

- [ ] **[Critical]** Is the **entity type and the definition of "the same"** written down before any
      matching is configured? "The same person" and "the same customer" are different targets and
      produce different systems: two policyholders who are the same human are one person and,
      depending on the business, one customer or two. `general/master-data-management.md` covers who
      decides this; nothing in this file can be tuned until they have.
- [ ] **[Critical]** Is a **labelled sample** planned, budgeted and produced? Precision can be
      estimated by reviewing what the system matched. **Recall cannot be estimated at all without
      ground truth**, because the matches the system missed are, by construction, not in its output.
      **[verified]** Splink states this directly: producing edge metrics "will require a 'ground
      truth' to compare your linkage results against (which can be achieved by Clerical Labelling)".
      A programme with no labelling plan has no recall number and will present a precision number as
      though it were one.
- [ ] **[Critical]** Has the **cost asymmetry between a false merge and a false split** been stated
      and used to set thresholds? They are not symmetric errors and treating them as such is the
      single most consequential modelling mistake in the discipline. See
      [Measuring match quality](#measuring-match-quality). **[assessment]**
- [ ] **[Recommended]** Has every candidate comparison field been **profiled** first — population
      rate, distinct-value count, and the frequency of its top values? This one exercise predicts most
      of what will go wrong: the placeholder date of birth, the shared switchboard number, the branch
      address on ten thousand customers. Doing it after the first bad merge is doing it late.
      **[assessment]**
- [ ] **[Recommended]** Is there a **stated target** expressed as precision and recall at a threshold,
      rather than as a "match rate"? A match rate is a function of the population, the attribute
      availability and the threshold; it is not comparable between estates and it is not a quality
      measure. Two systems with identical quality will report wildly different match rates on
      different data.
- [ ] **[Optional]** Is the resolution **reproducible** — same inputs, same code, same clusters? Where
      any stage samples, shuffles, or depends on processing order, that has to be pinned or the run is
      not evidence of anything.

### Blocking and candidate generation

- [ ] **[Critical]** Is blocking understood as a **recall decision**, not a performance optimisation?
      **[verified]** Splink puts the arithmetic plainly: pairwise comparisons grow as
      *n*(*n*−1)/2, so "a dataset of 1 million input records would generate around 500 billion
      pairwise record comparisons". Blocking is not optional at that scale — and **[verified]** the
      Splink cluster-evaluation guide is explicit that "Blocking rules, necessary to make computations
      tractable, can prevent record comparisons between some true matches ever being made". Every true
      match excluded by the blocking key is permanently lost, and no downstream scoring, model
      retraining or threshold change recovers it.
- [ ] **[Critical]** Are **multiple complementary blocking passes** used and unioned, rather than one
      key? A single key concentrates the recall loss on whichever field it uses. Blocking on
      (surname, year of birth) OR (postcode, first initial) OR (email domain, surname) recovers pairs
      that any one of them misses, at a candidate-set cost that is far smaller than the recall gain.
      **[verified]** Splink's recommended practice is to start strict and loosen incrementally,
      observing the effect on both runtime and result quality — the documentation walks through
      loosening `first_name AND surname AND dob` to a first-initial-plus-surname-plus-year-of-birth
      rule that tolerates typos and partial date errors.
- [ ] **[Critical]** Is **blocking recall measured separately from model recall** against the labelled
      sample? These are different failures with different fixes: pairs never generated versus pairs
      generated and scored too low. Reporting one recall number conflates them and sends effort to the
      classifier when the loss is upstream of it. **[assessment]**
- [ ] **[Critical]** Is **block-size skew** controlled? Pair count within a block is quadratic in the
      block's own size, so one pathological value dominates the entire job: blocking on surname in an
      English-speaking population puts every Smith in one block; blocking on postcode with a
      placeholder value puts every unmapped record in one block. The controls are to exclude
      high-frequency values from the blocking key (not the field), to cap block size, and to route
      the excluded records through a different pass. **[assessment]**
- [ ] **[Recommended]** Has the appropriate **blocking family** been chosen for the data rather than
      defaulting to exact-key blocking? The main ones, per the blocking-and-filtering survey
      literature: **standard blocking** (exact match on a derived key); **sorted neighbourhood** (sort
      on a key, compare within a sliding window — tolerant of near-misses in the key itself);
      **q-gram / canopy indexing** (overlapping blocks from character n-grams, higher recall, larger
      candidate sets); and **locality-sensitive hashing / MinHash** (probabilistic, scales well, gives
      a tunable recall guarantee).
- [ ] **[Recommended]** Is the candidate-set size **measured and reported** as a first-class number?
      **[verified]** Zingg quotes typical comparison volumes of "0.05-1% of the possible problem space"
      after its learned blocking, which is a reasonable order-of-magnitude sanity check: a blocking
      design that reduces the space by two or three orders of magnitude is normal, one that reduces it
      by six is probably discarding true matches.
- [ ] **[Recommended]** For record **linkage** between two sources (as opposed to deduplication within
      one), is the blocking asymmetry exploited? Cross-source linkage only needs pairs spanning the
      sources, which is *n*₁ × *n*₂ rather than the full quadratic, and blocking rules can be written
      accordingly.
- [ ] **[Optional]** Where a learned blocking model is used, is it retrained when the source
      population changes? Learned blocking encodes the distribution it was trained on, and a new
      source with different key quality silently degrades it.

### Normalisation and similarity scoring

- [ ] **[Critical]** Is **normalisation done before comparison**, and is its scope explicit? Case,
      whitespace, punctuation, diacritics, company suffixes (Ltd/Limited/Inc/GmbH), street-type
      abbreviations, and phone-number formatting account for a large share of achievable improvement
      and cost nothing at scoring time. **[verified]** Note that tools frequently normalise less than
      assumed — AWS Entity Resolution's ML-based matching normalises only **Name, Phone and Email**.
      Verify rather than assume, and normalise upstream where the tool does not.
- [ ] **[Critical]** Are **person names and postal addresses treated as their own disciplines** rather
      than as strings? Address parsing (unit and sub-premise handling, thoroughfare types, locality
      versus post town, country-specific ordering) and name handling (given/family ordering,
      patronymics, mononyms, particles, honorifics, married and maiden names, nickname sets,
      transliteration variants) each have decades of prior art and mature libraries such as
      `libpostal`. Hand-rolling either is the most reliable way to build a matcher that works on the
      developer's own name and fails on a quarter of the population. **[assessment]**
- [ ] **[Critical]** Is **frequency weighting** applied, so that agreement on a rare value counts for
      more than agreement on a common one? This is the central Fellegi-Sunter insight and it is worth
      more than any similarity-function choice. **[verified]** Splink's term-frequency adjustment
      documents exactly this: the basic model "doesn't account for skew in the distributions of
      linking variables", and where two records both hold a common value the *u* probability (the
      chance of agreeing by coincidence) is under-estimated — its worked example is a 10:1 gender skew
      in a prison population, and the surname case where "the average match probability for record
      pairs that share a surname is 0.2 but the average for the specific surname Smith is 0.1". A
      matcher that treats "both are called Smith" as equal evidence to "both are called Krzyzanowski"
      is systematically over-merging in exactly the populations where it matters.
- [ ] **[Recommended]** Is the **similarity function matched to the field**, rather than one function
      applied to everything?

  | Family | Examples | Good for | Fails on |
  |---|---|---|---|
  | Edit distance | Levenshtein, Damerau-Levenshtein | Typos, transpositions, OCR errors | Abbreviations, word reordering, initials |
  | Jaro-Winkler | Jaro-Winkler | Personal names — it boosts agreement in the leading characters, which is where names are stable | Strings whose discriminating content is at the **end** (account numbers, house numbers, sequential IDs), where the leading-prefix boost actively misleads |
  | Phonetic | Soundex, NYSIIS, Metaphone / Double Metaphone, Daitch-Mokotoff | Names captured by ear or across spelling variants; usually as a blocking key rather than a score | Non-English name populations, when the wrong variant is chosen |
  | Token-based | Jaccard, TF-IDF cosine, Monge-Elkan | Multi-word fields — business names, addresses — where word order varies | Short strings; anything without frequency weighting, where "Ltd" and "Street" dominate |
  | Numeric / date | Absolute difference, date-component swap | Dates of birth, amounts | Placeholder values, which look numerically plausible |

- [ ] **[Recommended]** If a **phonetic algorithm** is used, has the right one been chosen for the
      population? **[verified]** Soundex indexes "names by sound as pronounced in English", and the
      variants exist because it does not generalise: Daitch-Mokotoff Soundex "was developed in 1985 …
      because of problems they encountered while trying to apply the Russell Soundex to Jews with
      Germanic or Slavic surnames"; NYSIIS (1970) improved vowel handling; Metaphone (1990) was "a
      response to deficiencies in the Soundex algorithm". **[assessment]** The practical consequence
      is a fairness one: using English-tuned Soundex as a blocking key on a multi-ethnic population
      loses recall *unevenly across groups*, so the system works measurably better for some customers
      than others while reporting a single aggregate recall number that hides it. Measure match
      quality by name-origin cohort where the population is diverse.
- [ ] **[Recommended]** Are **comparison levels** used rather than a single continuous score per
      field? Exact match / normalised match / high similarity / low similarity / one side null are
      genuinely different pieces of evidence and deserve separate weights. Collapsing them to one
      number discards information and makes the model harder to explain to a steward.
- [ ] **[Recommended]** Is **null handled as its own level**, not as disagreement? A missing date of
      birth is not evidence against a match; treating it as disagreement penalises exactly the sparse
      records that most need matching.
- [ ] **[Optional]** Where the platform supplies native similarity functions, are they used before a
      library is introduced? **[verified]** Snowflake ships `JAROWINKLER_SIMILARITY` (0-100,
      case-insensitive, default scaling factor 0.1) and `EDITDISTANCE` as built-ins, which with
      blocking keys is enough to build candidate scoring in SQL.

### The decision model

- [ ] **[Critical]** Is the decision structured as **match / possible match / non-match** with two
      thresholds, rather than one cut-off? This is the Fellegi-Sunter structure and its middle band is
      the clerical-review queue — the deliberate, sized, staffed acknowledgement that some pairs are
      genuinely ambiguous. A single threshold does not remove those pairs; it assigns them silently to
      whichever side it falls on.
- [ ] **[Critical]** Is it clear **which model is in use and why**? Deterministic rules (explainable,
      auditable, cheap, brittle); Fellegi-Sunter probabilistic linkage (principled, handles
      uncertainty, parameters estimable without labels via expectation-maximisation, and the standard
      in official statistics); supervised machine learning (highest ceiling, needs labels, hardest to
      explain); or a waterfall of deterministic rules first and probabilistic on the residual (what
      most working systems converge on). **[verified]** Splink implements Fellegi-Sunter with
      EM-estimated parameters — λ (the prior probability any two records match), *m* (probability of
      an observation given a match) and *u* (probability of that observation given a non-match) — with
      the match weight as log₂(*m*/*u*).
- [ ] **[Critical]** Where the match decision has a **regulatory or customer-facing consequence**, can
      a specific decision be explained in terms a complaint handler or examiner will accept? "The
      model scored 0.94" is not an explanation. Per-field match weights are; a black-box embedding
      similarity is not. This constrains model choice, and it is cheaper to know that at design time.
      **[assessment]**
- [ ] **[Recommended]** Are the model's parameters **estimated on this estate's data** rather than
      inherited from a default or a different population? *u* probabilities in particular are
      properties of the population's value distributions and do not transfer between datasets.
- [ ] **[Optional]** Where a learned model is used, is there a fallback deterministic path for the
      cases the model has never seen — new sources, new geographies, newly onboarded populations?

### Clustering and transitive closure

> This is the section most commonly missing from an entity-resolution design, and the one most
> commonly responsible for its worst production incidents.

- [ ] **[Critical]** Is it understood that **pairwise decisions are not entities**, and that the
      pairwise-to-cluster step is a separate design decision with its own failure mode?
      **[verified]** The default in most implementations, Splink included, is **connected components**:
      records are grouped "based on whether there is a sufficiently strong match between record pairs
      and by applying transitive association", so if R1 matches R2 and R2 matches R3, all three land in
      one cluster.
- [ ] **[Critical]** Has the **transitive-closure hazard** been confronted explicitly? Under connected
      components, **A matches B and B matches C puts A and C in the same entity even where A and C
      were compared and rejected.** The pairwise model's own verdict on the A-C pair is discarded. The
      consequence is not proportional to the error: a *single* false-positive edge between two
      otherwise-correct clusters of 50 records produces one 100-record "customer", and the badness of
      the outcome scales with the size of what it joined, not with the number of mistakes.
      **[assessment]**
- [ ] **[Critical]** Have **hub records** been identified and excluded, since they are the usual
      mechanism? A record carrying a placeholder or shared value — `test@test.com`, `0000000000`,
      `01/01/1900`, the branch's own postal address, a company switchboard number — matches many
      unrelated records and becomes an articulation point joining clusters that have nothing to do
      with each other. The control is to exclude the *high-frequency values*, not the field: profile
      the value-frequency distribution of every comparison field and blocking key, and exclude the top
      values from matching while retaining the field for the records where its value is discriminating.
      **[assessment]**
- [ ] **[Critical]** Is the **clustering threshold set independently of, and higher than, the pairwise
      match threshold**? This is the cheapest and most effective control available. **[verified]**
      Splink separates the two: the model produces a match probability per pair, and clustering takes a
      `match_probability_threshold` that excludes weaker edges, with the documentation noting that "the
      choice of threshold can have a significant impact on the final linked data produced (i.e.
      clusters)". Accepting a pair for review at 0.80 and admitting it to a cluster at 0.98 are
      different decisions and should use different numbers.
- [ ] **[Critical]** Where false merges are costly, has a **clustering algorithm other than connected
      components** been considered? Connected components is transitive by construction and therefore
      cannot represent "A and C were rejected". The alternatives penalise or forbid that: **correlation
      clustering** optimises agreement with both positive and negative pairwise evidence; **Markov
      clustering** and other flow-based methods resist merging across sparse bridges; **hierarchical /
      agglomerative** clustering with a stopping rule gives explicit control over cluster cohesion;
      **star clustering** bounds cluster diameter. All cost more compute than connected components and
      all are cheaper than a privacy incident. **[assessment]**
- [ ] **[Critical]** Are **cluster-level constraints** enforced after clustering, whatever the
      algorithm? The high-value ones are: a **maximum cluster size** (with anything above it routed to
      review rather than published); a **source-cardinality rule** (a cluster containing four records
      from a source that guarantees one row per person is prima facie wrong); and **explicit no-merge
      assertions** — a steward's "these are not the same" must be persisted and honoured by the
      clustering step, not applied once as an un-merge and forgotten. **[assessment]**
- [ ] **[Recommended]** Are **graph metrics used to find the clusters most likely to be wrong**,
      rather than only aggregate quality numbers? **[verified]** Splink documents node degree, cluster
      size, **cluster density**, cluster centralisation, and an **"is bridge"** edge metric for exactly
      this purpose, noting that graph metrics "can also help us home in on problematic clusters, such
      as those containing inaccurate links (false positives)". A bridge edge — one whose removal splits
      the cluster — is the highest-yield review candidate in the whole system, because it is the
      structural signature of the transitive-closure failure. **[verified]** Splink also cautions that
      these metrics "are rarely definitive, especially when taken in isolation" and must be read
      against the dataset's own distribution: "a cluster of size 80 might be suspiciously large for one
      dataset but not for another".
- [ ] **[Recommended]** Is the **cluster-size distribution monitored across runs**, with a new right
      tail treated as an incident rather than a curiosity? The appearance of a small number of very
      large clusters after a rule change is the signature of a new hub record or a loosened blocking
      key, and it is visible in a histogram days before it is visible in a complaint. **[assessment]**
- [ ] **[Optional]** Is there a defined behaviour for clusters that **exceed review capacity**? A
      500-record cluster cannot be adjudicated pair by pair, and the realistic options are to suppress
      it, split it by a stricter threshold and re-review, or publish its members unmerged. Deciding
      under time pressure is worse than deciding now.

### Measuring match quality

- [ ] **[Critical]** Are **precision and recall reported at a stated threshold**, on both **pairs** and
      **clusters**? They are different measures: a model can have excellent pairwise precision and
      still produce bad clusters through transitive closure, which pairwise metrics cannot see.
      **[verified]** Splink frames the edge-level trade-off in exactly these terms — whether the
      priority is "to ensure that you capture all possible matches (i.e. high recall)" or "to minimise
      the number of incorrectly predicted matches (i.e. high precision)" — and provides separate
      cluster-evaluation guidance because the questions differ.
- [ ] **[Critical]** Is the **labelled sample stratified rather than uniformly random**? Uniform
      sampling of pairs is useless for recall: a one-million-record dataset has roughly 500 billion
      pairs and perhaps a few hundred thousand true matches, so a uniform sample is essentially all
      non-matches and estimates recall with no precision at all. Stratify across the score
      distribution (over-sampling the uncertain band), and sample *within blocks* and *outside all
      blocks* separately in order to estimate blocking recall at all. **[assessment]** — standard
      practice in the record-linkage literature, but the sampling design is the part most often got
      wrong in industry implementations.
- [ ] **[Critical]** Has the team stated that **a false merge is usually far worse than a false
      split**, and set thresholds accordingly? The asymmetry has four independent causes and none of
      them is aesthetic. **[assessment]**
  - **Detectability.** A false split is visible to everybody: the customer gets two statements, the
    agent sees two records, someone complains. A false merge is invisible by construction — the two
    people simply appear as one, and nothing in the system indicates that anything happened.
  - **Who discovers it.** Because it is invisible internally, a false merge is typically discovered
    externally — one customer seeing another customer's data, address, balance or correspondence. That
    makes it a privacy incident with a notification obligation before it is a data-quality defect.
  - **Reversibility.** A false split is repaired by merging, which is a supported everyday operation.
    A false merge is repaired by un-merging, which is only possible if the system was built for it,
    and after survivorship has chosen winners the losing values may no longer exist to restore.
  - **Propagation.** Downstream systems have already keyed to the merged identifier, so the repair is
    not local to the hub.
- [ ] **[Critical]** Is the automatic-merge threshold set for **precision**, with the uncertain band
      routed to review, rather than at the F1 optimum? Optimising F1 asserts that a false positive and
      a false negative cost the same. In this domain they demonstrably do not, so an F1-optimal
      threshold is an unstated and wrong cost model presented as a neutral metric. **[assessment]**
- [ ] **[Recommended]** Is **inter-annotator agreement measured** before labels are treated as truth?
      Genuinely ambiguous pairs are ambiguous to humans too. If two experienced reviewers disagree on
      15% of the review band, no model will exceed that ceiling and the measured "model error" in that
      band is partly label noise. **[assessment]**
- [ ] **[Recommended]** Are quality metrics **segmented** — by source pair, by name-origin cohort, by
      record completeness, by geography — rather than reported only in aggregate? Aggregate recall
      hides the population where the system fails, and that population is rarely random.
      **[assessment]**
- [ ] **[Recommended]** Is **no industry match-rate benchmark quoted** in the business case? Match
      rates depend entirely on the population, the attribute availability and the threshold, and are
      not transferable between estates. Widely circulated duplicate-rate and data-quality-cost figures
      generally cannot be traced to a primary source; measure the estate's own overlap on a sample
      instead. **[assessment]** — this file quotes no such figure for that reason.
- [ ] **[Optional]** Is quality **re-measured on a schedule**, not just at go-live? Source data changes,
      populations change, and a model tuned on last year's distribution degrades without any code
      changing.

### Human-in-the-loop and active learning

- [ ] **[Critical]** Are the **three distinct human tasks separated** — labelling pairs to train and
      evaluate, adjudicating production exceptions, and authoring match and survivorship rules? They
      need different skills, different tooling and usually different people, and conflating them
      produces a queue where nobody is doing any of the three well. **[assessment]**
- [ ] **[Critical]** Do reviewers see **the source records and their provenance**, not the composed
      result? Adjudicating requires knowing what each system actually said and when. A review screen
      showing only the merged record asks for a decision without the evidence for it.
- [ ] **[Recommended]** Is **active learning** used to choose what gets labelled — the pairs the model
      is least certain about, rather than a random sample? **[verified]** Zingg's workflow is built on
      this: an "interactive training data builder using active learning" driving label, train, match
      and link phases. **[verified]** `dedupe` uses the same active-learning shape. It typically
      reaches a usable model on a few hundred labelled pairs rather than tens of thousands.
- [ ] **[Recommended]** Are **steward decisions captured as durable labels** and fed back into the
      training and evaluation set? Production adjudication is the cheapest high-quality ground truth
      an organisation will ever generate, and most programmes consume it once and discard it.
- [ ] **[Recommended]** Is **review throughput** measured — queue depth, age of the oldest item,
      decisions per reviewer-day, and reversal rate? Reversal rate is the leading indicator that the
      rules are wrong rather than that the data is hard.
- [ ] **[Optional]** Is there a second-reviewer path for high-impact merges (large clusters, high-value
      accounts, politically exposed persons)? Cheap, and the alternative is that the most consequential
      decisions get the same treatment as the routine ones.

### Identifiers that are reused, absent, or lie

- [ ] **[Critical]** Has every identifier proposed as a deterministic key been **profiled for reuse and
      sharing** before it is trusted? The recurring cases are all mundane and all destructive:
      **recycled** customer and account numbers reissued after closure; **reassigned** phone numbers
      redistributed by carriers; **shared** email addresses and phone numbers within a household or a
      small business; **role** addresses (`info@`, `admin@`, `noreply@`); and **placeholder** values
      entered to satisfy a mandatory field. A deterministic rule on any of these is a bulk-merge
      instrument. **[assessment]**
- [ ] **[Critical]** Are **high-frequency values excluded rather than whole fields**? A phone number
      shared by 4,000 records is worthless as evidence; the same field is excellent evidence for the
      records holding a unique value. Dropping the field discards the good cases along with the bad;
      dropping the top values by frequency keeps them. **[verified]** Splink's term-frequency
      adjustment does this statistically rather than by exclusion, which is the more principled form of
      the same idea.
- [ ] **[Critical]** Are structurally **validatable identifiers actually validated** before use — LEI,
      IBAN, VAT number, and any other identifier with a check digit or defined format? An invalid
      value in a strong-identifier field is not a weak match, it is a data-entry event, and matching on
      it merges everything that shares the same typo. **[assessment]**
- [ ] **[Recommended]** Is it understood that an identifier's **uniqueness guarantee holds within its
      issuing system, not across systems**? Two sources can each guarantee unique customer numbers and
      collide with each other trivially. Composite keys (source system plus identifier) are the
      minimum; assuming the identifier alone is global is the classic post-merger defect.
- [ ] **[Recommended]** Is **placeholder detection** a standing rule set rather than a one-off cleanup?
      New placeholders appear whenever a new mandatory field is introduced, and they appear in
      production before anyone documents them. Detect them by frequency, not by a maintained list.
      **[assessment]**
- [ ] **[Optional]** Where an identifier is **self-asserted** rather than verified, is that recorded as
      a property of the value? A verified national identifier and a customer-typed one deserve
      different weights, and the distinction is usually available at capture and thrown away
      immediately afterwards.

### Un-merge and reversibility

- [ ] **[Critical]** Is **un-merge treated as a first-class requirement designed in from the start**?
      If merges cannot be reversed, every false positive is permanent — and since false positives are
      certain at any usable threshold, an irreversible system has accepted permanent corruption as its
      operating condition. This is a design property, not a feature to look for late in a selection.
      **[assessment]**
- [ ] **[Critical]** Are the **pre-merge records and per-attribute provenance retained**, so there is
      something to restore to? **[verified]** Reltio's crosswalks exist partly for this: attribute
      values accumulate with the integrity of their originating crosswalk maintained, including for
      "the need to return the attribute and its values to the original entity if an unmerge is
      requested". A design that overwrites source records with a composed golden record has destroyed
      the information un-merge requires.
- [ ] **[Critical]** Is **bulk un-merge** supported, not just single-record un-merge? The usual trigger
      is not one bad pair; it is a rule change that affects thousands of clusters at once.
      **[verified]** Reltio documents an automatic-unmerge task and a batch unmerge operation, and
      states the task should be run after match rules, or survivorship rules used in match rules, are
      added, deleted or edited. A tool that only offers a per-record un-merge button cannot recover
      from a bad deployment.
- [ ] **[Critical]** Is the **published master identifier stable and independent of which source record
      won**? **[verified]** Reltio selects a "winning entity" ID by comparing creation and update
      timestamps when none is specified — a reasonable rule, and precisely why the identifier published
      downstream must not be the surviving source key. Otherwise every re-run that changes a merge
      outcome changes downstream keys. **[assessment]**
- [ ] **[Critical]** Is there a **defined downstream contract for a split**? When an identifier
      consumers hold divides into two, somebody must decide which side keeps the original identifier
      (or whether both get new ones), how consumers are notified, and what happens to transactions
      already keyed to it. This is the genuinely hard part of un-merge and it is a downstream contract
      question, not an MDM-tool question. **[assessment]**
- [ ] **[Recommended]** Are **no-merge assertions persisted** so an un-merged pair is not re-merged on
      the next run? Without this, un-merge is a treadmill and the steward correctly concludes the
      system ignores them.
- [ ] **[Recommended]** Has un-merge been **tested before go-live** by deliberately injecting a false
      merge and recovering from it end to end, including downstream? Un-merge is the disaster-recovery
      procedure of an entity-resolution system, and an untested one should be assumed not to work.
      **[assessment]**
- [ ] **[Optional]** Is there an audit record of every merge and un-merge — what was joined, on which
      evidence, under which rule version, by whom or by which job?

### Temporal aspects

- [ ] **[Critical]** Can the system distinguish **an entity that legitimately changed** from **two
      entities that are genuinely distinct**? A person who married, changed surname and moved is one
      entity with two states; two people who share an address are two entities. Matching against
      *current-state attributes only* cannot tell these apart. The fix is structural: retain prior
      values — previous surnames, previous addresses, previous phone numbers — as additional comparison
      fields rather than overwriting them, so the match can be made against the state that existed when
      the other record was captured. **[assessment]**
- [ ] **[Critical]** Is the interaction with **slowly changing dimension history** designed rather than
      discovered? When two dimension rows are found to be one entity, every historical fact keyed to
      the retired surrogate key must remain correct. This is exactly what `general/data-modelling.md`'s
      durable "supernatural" key exists for — a stable identifier tying all versions of one entity
      together independently of any source key — and a mastering programme that does not populate it is
      building a merge that will orphan history.
- [ ] **[Critical]** Do **corporate entities get a relationship model rather than a version chain**?
      Companies merge, demerge, rename, redomicile and are acquired; the entity's history is a graph
      with legitimate splits and joins, not a linear sequence of versions. Legal Entity Identifier
      relationship data models this explicitly, and a schema that only supports "this record supersedes
      that one" cannot represent a demerger at all.
- [ ] **[Recommended]** Is the **cluster assignment itself effective-dated**, where point-in-time
      reconstruction is an obligation? "Who did we believe this was on 31 March" requires the *identity
      decision* to be versioned, not just the attributes — and that is a different and stronger
      requirement than a Type 2 dimension on the golden record. Very few implementations build it, and
      it is exactly what a regulator asks for during a reconciliation. **[assessment]**
- [ ] **[Recommended]** Is the difference between **full re-resolution and incremental resolution**
      understood and decided? Re-running the whole population from scratch produces different clusters
      from incrementally adding records to existing ones, because incremental resolution is
      order-dependent. Decide which is authoritative, how often the full run happens, and whether
      cluster identifiers are permitted to change between runs — and if they are, that is a downstream
      contract. **[assessment]**
- [ ] **[Optional]** Are entity **death events** modelled (deceased persons, dissolved companies,
      closed accounts)? They stop further matching, and they affect what may lawfully be retained and
      published.

### Running it in production

- [ ] **[Critical]** Are **match rule changes treated as releases** — with a diff, an impact count
      (clusters created, clusters split, records moved), a review, and a rollback path — rather than as
      configuration edits? A rule change is a data change affecting every consumer, and the impact
      count should be produced *before* the change is applied, not observed afterwards. **[assessment]**
- [ ] **[Critical]** Is the resolution **run reproducible and versioned**, with the rule set, model
      parameters, thresholds and input snapshot recorded alongside the output? Without it, "why is this
      customer merged" is unanswerable a month later.
- [ ] **[Recommended]** Is the choice between **batch and real-time resolution** driven by the
      consumer? Batch is simpler, reproducible and adequate for analytics; real-time resolution at the
      point of capture prevents duplicates being created at all, and costs a service with an
      availability commitment. Both is common: real-time for capture, batch for reconciliation.
- [ ] **[Recommended]** Are **cost and runtime monitored per stage**? Blocking dominates cost, scoring
      dominates runtime, and clustering dominates memory. Knowing which one moved when a job doubles in
      duration takes minutes to instrument and hours to reconstruct later. **[assessment]**
- [ ] **[Optional]** Where a managed service is used, is the **per-record pricing** modelled against
      run frequency? **[verified]** AWS Entity Resolution charges $0.25 per 1,000 records processed for
      rule-based or ML matching, and $0.10 per 1,000 for provider matching. Per-record pricing on a
      full re-resolution run is a recurring cost proportional to how often you re-run, which is a
      different shape from a licence.

## Why This Matters

Entity resolution fails in ways that do not look like failures. A pipeline that drops records raises
an alert; a matcher that merges two customers produces one clean, complete, confident record and
nothing anywhere indicates a problem. The output of a broken entity-resolution system is
indistinguishable, on inspection, from the output of a working one — which is why the discipline is
built around measurement against labelled data rather than around monitoring, and why programmes that
skip the labelling step have no way of knowing what they built.

The blocking stage is where the largest silent loss happens. It is presented as a performance
optimisation and it is nothing of the sort: it is a decision about which pairs will *never* be
considered. The arithmetic forces it — a million records is around 500 billion pairs — but the
consequence is that recall is capped by the blocking design before the model sees anything, and no
amount of subsequent tuning lifts the cap. Teams routinely spend weeks improving a classifier whose
ceiling was set in the first ten lines of the job, and the measurement that would have shown this —
blocking recall computed separately from model recall — takes an afternoon.

Transitive closure is the failure that produces the worst outcomes and gets the least design
attention. Almost every implementation clusters by connected components because it is the obvious
thing to do and it is what the default library function does. It is also transitive by construction,
which means a single false-positive edge silently overrides the model's own explicit rejection of
every other pair it transitively joins. One record with `test@test.com` in the email field, or a bank
branch's own address on the customers opened there, becomes a bridge between clusters that have
nothing to do with each other — and the result is one "customer" containing dozens of unrelated
people, complete with a plausible golden record composed by survivorship from all of them. This is not
a rare pathological case; it is the normal consequence of putting real data through a default
configuration, and the controls — a higher clustering threshold than pairwise threshold, high-frequency
value exclusion, maximum cluster size, and bridge-edge review — are all cheap and all frequently
absent.

The cost asymmetry between false merges and false splits is the most consequential thing an
architecture review can insist on, because it changes a number that everything else depends on. A
false split annoys someone, is visible, and is fixed by a routine merge. A false merge is invisible
internally, discovered externally by one customer seeing another's data, hard to reverse, and already
propagated to every downstream system that keyed to the merged identifier. Any threshold chosen by
optimising F1 has implicitly asserted that these two cost the same. They do not, and the assertion is
usually made without anyone noticing that it was made.

Un-merge is the requirement that gets deferred and cannot be retrofitted. It depends on architectural
choices made much earlier: retaining pre-merge records, keeping per-attribute provenance, and
publishing a master identifier that does not change when a merge outcome changes. A system that
composes a golden record and discards the inputs has not made un-merge difficult, it has made it
impossible — and since false positives are certain at any threshold that is useful, that system has
accepted permanent, unrecoverable corruption as a design condition. Rule changes make this acute
rather than theoretical: the ordinary trigger for mass un-merge is not one bad pair, it is a
threshold adjustment that reclassifies thousands of clusters at once.

Finally, the temporal dimension is where entity resolution meets the warehouse and where the two
disciplines most often fail to meet. A merge decided today has to be correct about facts recorded
years ago, which requires a durable identifier that survives the merge and requires history to be
keyed to it rather than to whichever source key happened to win. And the reconstruction question —
"who did we believe this was on the reporting date" — requires the *identity decision itself* to be
versioned, which almost nobody builds and which is exactly what gets asked for the first time a
regulator reconciles two reports that grouped the same counterparty differently.

## What Is Verified and What Is Judgement

**Verified against the cited page on 2026-07-27** (each has a URL in Reference Links): the *n*(*n*−1)/2
pair-growth arithmetic and the 1 million records → ~500 billion comparisons figure; that blocking
rules necessary for tractability can prevent true matches from ever being compared; the
strict-then-incrementally-loosen blocking practice and its worked example; the Fellegi-Sunter λ/*m*/*u*
parameterisation, EM estimation, and match weight as log₂(*m*/*u*); the term-frequency skew problem,
the 10:1 gender example and the Smith surname example; connected components as the default clustering
method with transitive association; that the clustering threshold is a separate parameter whose choice
significantly affects the resulting clusters; the Splink graph metrics (node degree, cluster size,
cluster density, cluster centralisation, "is bridge") and their stated use in finding clusters
containing false positives, together with the caution that they are rarely definitive in isolation;
that edge metrics require clerically labelled ground truth; the high-recall-versus-high-precision
framing; Soundex's English-language design and the stated motivations for Daitch-Mokotoff, NYSIIS and
Metaphone; Snowflake's `JAROWINKLER_SIMILARITY` range and default scaling factor and the existence of
`EDITDISTANCE`; AWS Entity Resolution's ML normalisation being limited to Name, Phone and Email, its
lack of hashed-data support for ML matching, and its published per-1,000-record pricing; Zingg's
active-learning training-data builder and its stated 0.05-1% comparison-space figure; `dedupe`'s
active-learning approach; and Reltio's crosswalk provenance, unmerge-restoration rationale, automatic
and batch unmerge, the requirement to re-run after rule changes, and the winning-entity-ID selection
rule.

**Assessment, not sourced claim:** the five-stage framing and the argument that each stage has a
non-substitutable failure mode; the recommendation to measure blocking recall separately from model
recall; block-size skew control by excluding high-frequency values rather than fields; the hub-record
mechanism and its identification by value-frequency profiling; the recommendation to set the
clustering threshold above the pairwise threshold as a standing control; the suggestion of correlation
clustering, Markov clustering, agglomerative clustering and star clustering as false-merge-resistant
alternatives (the algorithms are standard; the recommendation for *this* purpose is judgement);
cluster-level constraints including maximum size and source-cardinality rules; the four-cause argument
for false-merge/false-split asymmetry and the consequent rejection of F1-optimal thresholding; the
fairness argument about English-tuned phonetic algorithms on multi-ethnic populations and the
recommendation to segment quality metrics by cohort; the stratified-sampling guidance; the
inter-annotator-agreement recommendation; treating rule changes as releases with a pre-computed impact
count; the effective-dated cluster assignment recommendation; the full-versus-incremental
re-resolution warning; and every characterisation in Why This Matters.

**Explicitly not verified this session:**

- **Any duplicate rate, match rate, or cost-of-poor-data-quality figure.** None is quoted. These
  circulate widely without traceable primary sources, and where a primary source exists the figure is
  a property of one specific population and threshold and does not transfer. Measure on the estate's
  own data.
- **The Fellegi and Sunter (1969) paper itself.** The publisher's page returns HTTP 403 to automated
  clients and the article is paywalled; the model as described here was verified from Splink's topic
  guide and the US Census Bureau's record-linkage overview, both of which are open.
- **The ACM Computing Surveys version of the blocking survey**, which returns HTTP 403 to automated
  clients. The arXiv preprint of the same work is open and was verified.
- **Relative accuracy claims between named products.** No comparative benchmark is asserted here, and
  vendor-published accuracy comparisons in this category are not independently reproducible.

## Common Decisions (ADR Triggers)

- **Blocking strategy** — standard blocking on exact derived keys (simplest, sharpest recall cliff)
  vs sorted neighbourhood (tolerant of near-misses in the key itself) vs q-gram or canopy indexing
  (higher recall, larger candidate sets) vs LSH/MinHash (scales best, tunable recall guarantee). Decided
  by key quality, data volume and how much recall loss is acceptable — which requires measuring it
- **Number of blocking passes** — one key (cheap, concentrates recall loss on one field) vs a union of
  complementary passes (materially better recall for a modest candidate-set increase). The union is
  almost always right and is skipped because the first pass "works"
- **Matching model** — deterministic rules (explainable, auditable, brittle) vs Fellegi-Sunter
  probabilistic (principled, parameters estimable without labels, the standard in official statistics)
  vs supervised ML (highest ceiling, needs labels, weakest explainability) vs a deterministic-first
  waterfall with probabilistic on the residual. Forced toward the explainable end by any regulatory or
  customer-facing consequence
- **One threshold vs two** — a single cut-off (no review queue, ambiguous pairs assigned silently) vs
  auto-merge / review / auto-reject bands (the classical structure; makes the ambiguous population
  explicit and turns it into a staffing decision)
- **Where the threshold sits** — precision-optimised at the auto-merge boundary with a wide review band
  (correct where false merges are costly, expensive in review capacity) vs F1-optimised (implicitly
  asserts symmetric error costs, which is wrong in this domain) vs recall-optimised (defensible only
  where a human confirms every merge)
- **Clustering algorithm** — connected components (default, fast, transitive by construction, cannot
  represent a rejected pair) vs correlation or flow-based clustering (respects negative evidence, more
  compute) vs agglomerative with a stopping rule (explicit cohesion control). The choice is a direct
  function of how costly a false merge is
- **Clustering threshold relative to the match threshold** — same value (simplest, and the transitive
  hazard runs at full strength) vs a higher clustering threshold (cheapest available control on false
  merges, at some recall cost)
- **Un-merge design** — full reversibility with pre-merge records, per-attribute provenance and bulk
  un-merge (the only defensible option where merges have customer-visible consequences) vs
  forward-only merging (cheaper to build, accepts every false positive as permanent). This decision
  must be made before the first merge, not at the first incident
- **Master identifier stability** — a synthetic identifier independent of merge outcomes (downstream
  keys survive re-runs; needs its own generation and persistence) vs the surviving source key (free,
  and changes whenever a merge outcome changes, propagating to every consumer)
- **Batch vs real-time resolution** — batch (simple, reproducible, adequate for analytics, duplicates
  are created and then found) vs real-time at capture (prevents duplicate creation, requires a service
  with an availability commitment) vs both, which is the common end state
- **Full re-resolution vs incremental** — full re-run (order-independent, reproducible, expensive, may
  move cluster identifiers) vs incremental (cheap, order-dependent, drifts from what a full run would
  produce). Decide which is authoritative and whether cluster identifiers may change
- **Build vs managed service vs commercial hub** — a library such as Splink, Zingg or dedupe (full
  control, no licence cost, check the licence, and you own the operational surface) vs a managed
  matching service (fastest to a result, per-record pricing, thin stewardship) vs a commercial MDM
  platform (complete operating surface, licence and implementation cost). See
  `general/master-data-management.md` — the matching is the cheap part to build; the stewardship
  application is not

## Reference Architectures

- **Batch resolution over a lakehouse (the common analytical default).** Sources land unchanged;
  normalisation and blocking run as transformations; scoring produces a pair table with per-field match
  weights retained; clustering produces a crosswalk table (source key → master identifier, with
  evidence and provenance) that is the durable output. Conformed dimensions join through the crosswalk
  at build time per `general/data-modelling.md`. Every intermediate table is materialised, which is
  what makes the pipeline debuggable and the decisions auditable.
- **Real-time resolution at capture, batch reconciliation behind it.** A synchronous service resolves
  each incoming record against the existing population at the point of creation, so duplicates are
  largely prevented rather than found later; a periodic batch job re-resolves the full population to
  catch what the incremental path missed and to correct order-dependence. The two paths must share one
  rule set, and the batch run's disagreements with the online path are a monitored metric rather than a
  surprise.
- **Managed matching service.** Inputs registered in the platform's catalog, a rule-based and/or ML
  workflow producing match identifiers and confidence levels, outputs written back for downstream
  consumption. Fastest path to a working matcher and per-record pricing that scales with re-run
  frequency; supplies little or no stewardship, workflow or un-merge, so those must exist elsewhere.
- **Library in the warehouse.** A Fellegi-Sunter implementation executing against the analytical engine
  itself (Splink over DuckDB, Spark, Athena or a warehouse backend), so no data movement is required and
  the model parameters are estimated on the actual population. Strong where explainability matters —
  per-field match weights are directly inspectable — and it leaves the steward application to be built
  or bought separately.
- **Deterministic-first waterfall.** Exact matching on validated strong identifiers first, removing
  those pairs from consideration; probabilistic matching on the residual; human review on the
  uncertain band. Produces the best explainability-to-recall ratio in most estates and makes the
  probabilistic layer's job smaller and better characterised. **[assessment]**

## Reference Links

All links checked on 2026-07-27; codes and effective URLs are as returned that day.

- [Record linkage (Wikipedia)](https://en.wikipedia.org/wiki/Record_linkage)
  — vendor-neutral overview of the field, its history, and deterministic versus probabilistic linkage
- [Winkler, *Overview of Record Linkage and Current Research Directions* (US Census Bureau, 2006)](https://www.census.gov/content/dam/Census/library/working-papers/2006/adrm/rrs2006-02.pdf)
  — open primary-source treatment of the Fellegi-Sunter model, parameter estimation, string
  comparators and blocking, from the statistical agency that developed much of the practice
- [Fellegi and Sunter, *A Theory for Record Linkage*, JASA 64(328), 1969](https://www.tandfonline.com/doi/abs/10.1080/01621459.1969.10501049)
  — the foundational paper. *Note: the publisher returns HTTP 403 to automated clients and the article
  is paywalled; the model as used here was verified from the two open sources above and below.*
- [Splink: The Fellegi-Sunter model](https://moj-analytical-services.github.io/splink/topic_guides/theory/fellegi_sunter.html)
  — λ, *m* and *u* parameters, match weight as log₂(*m*/*u*), and EM estimation
- [Splink documentation](https://moj-analytical-services.github.io/splink/index.html)
  — the UK Ministry of Justice's open-source probabilistic linkage library
- [Linacre et al., *Splink: Free software for probabilistic record linkage at scale*, IJPDS](https://ijpds.org/article/view/1794)
  — the published account of Splink's design and its FastLink/EM lineage
- [Splink: What are blocking rules?](https://moj-analytical-services.github.io/splink/topic_guides/blocking/blocking_rules.html)
  — the *n*(*n*−1)/2 growth and the 1 million records → ~500 billion comparisons figure
- [Splink: Blocking rule performance](https://moj-analytical-services.github.io/splink/topic_guides/blocking/performance.html)
  — strict-versus-lenient rules and the incremental-loosening practice, with worked examples
- [Splink: Term-frequency adjustments](https://moj-analytical-services.github.io/splink/topic_guides/comparisons/term-frequency.html)
  — why value skew breaks *u* probabilities, with the gender-skew and Smith-surname examples
- [Splink: Linked data as graphs](https://moj-analytical-services.github.io/splink/topic_guides/theory/linked_data_as_graphs.html)
  — nodes, edges and clusters, and how the threshold changes the resulting clusters
- [Splink: Clustering API](https://moj-analytical-services.github.io/splink/api_docs/clustering.html)
  — connected components, transitive association, and the `match_probability_threshold` parameter
- [Splink: Edge evaluation overview](https://moj-analytical-services.github.io/splink/topic_guides/evaluation/edge_overview.html)
  — the precision-versus-recall framing and the requirement for clerically labelled ground truth
- [Splink: Edge metrics](https://moj-analytical-services.github.io/splink/topic_guides/evaluation/edge_metrics.html)
  — the metric definitions built up from confusion-matrix primitives
- [Splink: Cluster evaluation](https://moj-analytical-services.github.io/splink/topic_guides/evaluation/clusters/overview.html)
  — what a high-quality cluster is, and that blocking can prevent true matches from being compared
- [Splink: Graph metrics](https://moj-analytical-services.github.io/splink/topic_guides/evaluation/clusters/graph_metrics.html)
  — node degree, cluster size, density, centralisation and the "is bridge" edge metric, with the
  caution that they are rarely definitive in isolation
- [Splink: Model evaluation](https://moj-analytical-services.github.io/splink/topic_guides/evaluation/model.html)
  — inspecting match weights and *m*/*u* parameters, and EM training stability
- [Papadakis et al., *A Survey of Blocking and Filtering Techniques for Entity Resolution* (arXiv 1905.06167)](https://arxiv.org/abs/1905.06167)
  — the reference survey of blocking families. *The ACM Computing Surveys version at
  `dl.acm.org/doi/10.1145/3377455` returns HTTP 403 to automated clients; the arXiv preprint is open.*
- [Christophides et al., *End-to-End Entity Resolution for Big Data: A Survey* (arXiv 1905.06397)](https://arxiv.org/abs/1905.06397)
  — the full pipeline including clustering, incremental resolution and evaluation
- [Christen, *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection* (Springer, 2012)](https://link.springer.com/book/10.1007/978-3-642-31164-2)
  — the standard textbook treatment of the whole pipeline
- [Levenshtein distance (Wikipedia)](https://en.wikipedia.org/wiki/Levenshtein_distance)
  — edit distance definition and variants
- [Jaro-Winkler distance (Wikipedia)](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance)
  — including the prefix-scaling behaviour that makes it good for names and poor for trailing-digit
  identifiers
- [Soundex (Wikipedia)](https://en.wikipedia.org/wiki/Soundex)
  — the English-language design, and the Daitch-Mokotoff, NYSIIS and Metaphone variants that exist
  because of its limitations
- [Metaphone (Wikipedia)](https://en.wikipedia.org/wiki/Metaphone)
  — the 1990 response to Soundex's deficiencies, and Double Metaphone
- [NYSIIS (Wikipedia)](https://en.wikipedia.org/wiki/New_York_State_Identification_and_Intelligence_System)
  — the 1970 phonetic algorithm with improved vowel handling
- [Locality-sensitive hashing (Wikipedia)](https://en.wikipedia.org/wiki/Locality-sensitive_hashing)
  — the probabilistic blocking family, including MinHash
- [Connected component (Wikipedia)](https://en.wikipedia.org/wiki/Connected_component_(graph_theory))
  — the graph-theoretic definition underlying the default clustering behaviour
- [libpostal](https://github.com/openvenues/libpostal)
  — statistical international address parsing and normalisation; the reason not to hand-roll address
  matching
- [Legal Entity Identifier (Wikipedia)](https://en.wikipedia.org/wiki/Legal_Entity_Identifier)
  — the global legal-entity identifier and its relationship data, for corporate-hierarchy resolution
- [Zingg (GitHub)](https://github.com/zinggAI/zingg)
  — Spark-based ML entity resolution with an active-learning training-data builder; AGPL v3.0; states
  typical comparison volumes of 0.05-1% of the problem space
- [dedupe (GitHub)](https://github.com/dedupeio/dedupe)
  — Python deduplication and record linkage using active learning. *Note: `docs.dedupe.io` sits behind
  a bot challenge returning HTTP 429 to automated clients; the repository is the reliable reference.*
- [What is AWS Entity Resolution?](https://docs.aws.amazon.com/entityresolution/latest/userguide/what-is-service.html)
  — rule-based, ML-based and provider-led matching as a managed service
- [AWS Entity Resolution: rule-based matching workflow](https://docs.aws.amazon.com/entityresolution/latest/userguide/creating-matching-workflow-rule-based.html)
  — the configurable hierarchical waterfall structure
- [AWS Entity Resolution: ML-based matching workflow](https://docs.aws.amazon.com/entityresolution/latest/userguide/create-matching-workflow-ml.html)
  — match IDs and confidence levels; no hashed-data support; Name/Phone/Email normalisation only
- [AWS Entity Resolution: matching workflows](https://docs.aws.amazon.com/entityresolution/latest/userguide/create-matching-workflow.html)
  — the workflow types and their inputs
- [AWS Entity Resolution glossary](https://docs.aws.amazon.com/entityresolution/latest/userguide/glossary.html)
  — the service's own vocabulary for match IDs, match groups and confidence
- [AWS Entity Resolution pricing](https://aws.amazon.com/entity-resolution/pricing/)
  — $0.25 per 1,000 records for rule-based or ML matching; $0.10 per 1,000 for provider matching
- [Snowflake: `JAROWINKLER_SIMILARITY`](https://docs.snowflake.com/en/sql-reference/functions/jarowinkler_similarity)
  — 0-100 similarity, case-insensitive, default scaling factor 0.1
- [Snowflake: `EDITDISTANCE`](https://docs.snowflake.com/en/sql-reference/functions/editdistance)
  — Levenshtein distance as a built-in function
- [Reltio: Crosswalks](https://docs.reltio.com/en/objectives/model-data/data-modeling-at-a-glance/data-modeling-operation/define-crosswalks-for-data-sources/crosswalks)
  — per-source, per-attribute provenance as a first-class construct
- [Reltio: Merge matched data](https://docs.reltio.com/en/objectives/resolve-potential-matches/potential-matching-at-a-glance/potential-matching-reference/merge-matched-data)
  — winning-entity-ID selection and what survives a merge
- [Reltio: Automatically unmerge entity records](https://docs.reltio.com/en/objectives/resolve-potential-matches/potential-matching-at-a-glance/potential-matching-operation/unmerge-entity-records/automatically-unmerge-entity-records)
  — automatic and batch unmerge, and the requirement to re-run after match or survivorship rule changes
- [Semarchy xDM: Match and merge](https://www.semarchy.com/doc/semarchy-xdm/xdm/latest/Design/matching/matching.html)
  — fuzzy and ID matching and how matched records reach consolidation

## See Also

- `general/master-data-management.md` — the decisions that surround this pipeline: implementation
  style, survivorship rules, stewardship operating model, reference data, and vendor selection
- `general/data-modelling.md` — conformed dimensions, slowly changing dimensions, and the durable
  "supernatural" key that a resolved entity's identifier becomes
- `general/data-governance.md` — stewardship roles, exception queues and SLAs, plus the lineage and
  audit evidence a resolution pipeline has to produce
- `general/data-classification.md` — the sensitivity and lawful-basis constraints that determine
  whether two records may be combined at all
- `general/data-ingestion.md` — how source records arrive, and why the capture method constrains what
  can be compared and when
- `patterns/data-pipeline.md` — the pipeline architecture, orchestration and quality gating this runs
  inside
- `patterns/lakehouse-medallion.md` — the layering that a batch resolution pipeline naturally occupies
- `patterns/data-warehouse-migration.md` — where existing merge decisions surface during a migration,
  and why they should not simply be carried across unexamined
- `patterns/core-banking-data-integration.md` — the customer information file as a worked example of a
  party master with duplicate records and many-to-many role semantics
- `patterns/regulated-financial-data-platform.md` — the control environment in which identity decisions
  become regulatory evidence
