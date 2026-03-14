# Contributing to the Knowledge Library

This guide covers how to add new knowledge files, update existing ones, and maintain quality standards across the library.

## File Format

Every knowledge file must follow this structure:

```markdown
# Title

## Checklist

- [ ] Question or consideration? (context, options, or guidance in parentheses)
- [ ] Another question? (why it matters and what to look for)

## Why This Matters

One to three paragraphs explaining the real-world consequences of getting this wrong.
Include cost, security, reliability, or operational impact.

## Common Decisions (ADR Triggers)

- **Decision name** -- what the tradeoff is and why it deserves an ADR
- **Another decision** -- brief description of the options and implications
```

Pattern files (`patterns/`) may include additional sections:

```markdown
## Overview

Brief description of the pattern and when it applies.

## Common Mistakes

Bulleted list of anti-patterns and pitfalls.

## Key Patterns

Named sub-patterns with one-line descriptions.

## Reference Architectures

Links to official documentation and reference implementations.
```

## Adding a New Knowledge File

1. Determine which directory the file belongs in:
   - `general/` for cloud-agnostic topics
   - `providers/<provider>/` for provider-specific guidance
   - `patterns/` for architecture patterns
   - `compliance/` for regulatory frameworks
   - `failures/` for failure mode analysis

2. Name the file using **lowercase-kebab-case** with a `.md` extension:
   - `container-orchestration.md` (good)
   - `ContainerOrchestration.md` (bad)
   - `container_orchestration.md` (bad)

3. Write the file following the required format above.

4. Open a pull request with the new file.

## Adding Items to Existing Files

When you identify a gap in an existing checklist:

1. Add the new checklist item in a logical position relative to existing items (group related concerns together).
2. Include parenthetical context that explains why the item matters or what options exist.
3. If the new item represents a significant decision, add a corresponding entry to the **Common Decisions (ADR Triggers)** section.
4. Open a pull request describing what gap the new item addresses.

## Naming Conventions

- **Files**: `lowercase-kebab-case.md` (e.g., `secrets-manager.md`, `three-tier-web.md`)
- **Directories**: lowercase, single words where possible (e.g., `general`, `providers`, `aws`)
- **Titles**: Use the `# Title` heading as the human-readable name; it does not need to match the filename exactly but should be clearly related

## PR Process for Knowledge Contributions

1. Create a branch named `knowledge/<topic>` (e.g., `knowledge/add-serverless-pattern`).
2. Add or modify the knowledge file(s).
3. Run through the quality checklist below before opening the PR.
4. Open a PR with a description that includes:
   - What gap this addresses (link to an issue if one exists)
   - How the gap was discovered (architecture session, audit, incident review)
   - Any ADR triggers the new content introduces
5. Request review from someone with domain expertise in the topic.

## Quality Checklist for Contributions

Before submitting, verify your knowledge file meets these standards:

- [ ] File contains **8 to 15 checklist items** (fewer means the topic is too narrow or underexplored; more means it should be split into multiple files)
- [ ] Each checklist item is phrased as a **question**, not a statement (questions drive discussion; statements get skipped)
- [ ] Each checklist item includes **parenthetical context** explaining options, tradeoffs, or why it matters
- [ ] Checklist items are **ordered logically** (foundational decisions first, refinements later)
- [ ] The **Why This Matters** section explains real-world consequences, not just theory
- [ ] **ADR triggers are identified** for decisions that are costly to reverse, involve significant tradeoffs, or set long-term direction
- [ ] The file follows **lowercase-kebab-case** naming
- [ ] The file uses the **required section headings** (# Title, ## Checklist, ## Why This Matters, ## Common Decisions)
- [ ] No duplicate coverage with existing files (check `general/` before adding provider-specific items that are actually cloud-agnostic)
- [ ] Provider-specific files reference the corresponding `general/` topic where applicable

## Good vs Bad Checklist Items

### Good checklist items

These are actionable, specific, and include context:

```markdown
- [ ] What CIDR block size for the VPC? (Plan for growth; /16 gives 65K IPs,
      avoid overlaps with peered VPCs and on-premises ranges)
- [ ] Is automatic secret rotation configured? (reduces blast radius of
      compromised credentials; AWS Secrets Manager supports native rotation
      for RDS, Redshift, DocumentDB)
- [ ] How are cross-service transactions handled? (saga pattern, eventual
      consistency; avoid distributed two-phase commit in cloud environments)
```

Why these work:
- Each is a concrete question that demands a specific answer
- The parenthetical context provides enough information to make an informed decision
- They surface tradeoffs rather than prescribing a single answer

### Bad checklist items

These are vague, prescriptive, or missing context:

```markdown
- [ ] Use encryption
- [ ] Is security configured?
- [ ] Deploy to multiple availability zones
- [ ] Consider caching
```

Why these fail:
- "Use encryption" is a statement, not a question, and lacks specifics (encryption of what? at rest? in transit? which algorithm? who manages the keys?)
- "Is security configured?" is too broad to act on
- "Deploy to multiple availability zones" prescribes a solution without exploring whether it is needed or what the tradeoffs are
- "Consider caching" does not help the architect know what to decide

## Feeding Gaps Back from Architecture Sessions

When an architecture session reveals a question or concern not covered by the existing knowledge library:

1. Note the gap during the session (what question came up that should have been in a checklist).
2. After the session, determine whether it belongs in an existing file or warrants a new one.
3. Draft the checklist item(s) with proper context and ADR triggers.
4. Open a PR referencing the session or project where the gap was discovered (do not include client or project-specific data in the knowledge file -- keep it generic).
5. This feedback loop is how the knowledge library improves over time. Every session is an opportunity to make the next session better.
