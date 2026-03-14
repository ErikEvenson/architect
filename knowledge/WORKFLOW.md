# Architecture Session Workflow

This document defines the systematic process for conducting architecture design sessions using the Architect tool and knowledge library.

## Prerequisites

- Architect API is running and accessible
- API base URL is set via `ARCHITECT_API_URL` environment variable (default: `http://localhost:30010/api/v1`)
- Knowledge files are available at `knowledge/`

## Workflow Steps

### Step 1: Read Project Context

Read the project from the API:
- `GET /clients` — find or create the client
- `GET /clients/{id}/projects` — find or create the project
- Note the `cloud_providers` array and `description`
- Create a version if one doesn't exist

### Step 2: Identify Architecture Pattern

Read the project description and infer the architecture pattern. Confirm with the user before proceeding.

Available patterns:
- `three-tier-web` — web application with presentation, application, and data tiers
- `microservices` — decomposed services with independent deployment
- `data-pipeline` — data ingestion, transformation, and storage
- `static-site` — pre-built assets served via CDN
- `hybrid-cloud` — spanning on-prem and cloud
- `event-driven` — event sourcing, CQRS, pub/sub
- `multi-cloud` — multiple public cloud providers
- `edge-computing` — edge/IoT with cloud aggregation
- `ai-ml-infrastructure` — GPU compute, training pipelines, model serving
- `saas-multi-tenant` — multi-tenant SaaS application
- `cdn-fronted-onprem` — on-prem with external CDN
- `disaster-recovery-implementations` — DR-focused design

### Step 3: Load Knowledge Files

Load files in this order:

#### Always load:
1. **General files** (`knowledge/general/*.md`) — all files. These ask WHAT decisions need to be made.
2. **Failure patterns** (`knowledge/failures/*.md`) — anti-patterns to avoid.

#### Load based on project:
3. **Provider files** (`knowledge/providers/{provider}/*.md`) — for each provider in the project's `cloud_providers`. These ask HOW to implement with that provider.
4. **Pattern file** (`knowledge/patterns/{pattern}.md`) — for the identified pattern.

#### Load if applicable:
5. **Compliance files** (`knowledge/compliance/{framework}.md`) — if compliance requirements are identified.
6. **Framework files** (`knowledge/frameworks/{provider}-well-architected.md`) — for the Well-Architected review pass at the end.

#### Load for on-prem projects:
7. **On-prem specific** — `general/load-balancing-onprem.md`, `general/networking-physical.md`, `general/cost-onprem.md` if any provider is on-prem (nutanix, vmware, openstack).
8. **Cross-cutting tools** — `providers/hashicorp/*` if Terraform/Vault/Consul are in scope, `providers/prometheus-grafana/*` for on-prem observability, `providers/ceph/*` for Ceph storage.

### Step 4: Systematic Questioning

Walk through the loaded knowledge files' checklist items. Process in this order:

1. **Critical items first** — items tagged `[Critical]` across all loaded files
2. **Recommended items** — items tagged `[Recommended]`
3. **Optional items** — items tagged `[Optional]`, ask only if time/budget allows

For each checklist item:
- Ask the user ONE question at a time
- Record the question via `POST /projects/{id}/questions`
- Record the answer via `PATCH /projects/{id}/questions/{id}`
- If the answer implies an architectural decision, create an ADR IMMEDIATELY via `POST /projects/{id}/adrs`
- Track which checklist items have been addressed

### Step 5: Gap Analysis

After walking through all checklist items:
- Review any unchecked items — ask if they should be addressed or deferred
- Ask: "What else am I missing?" for novel requirements not covered by checklists
- Check the failure patterns — verify no anti-patterns are present in the design
- Any gaps discovered should be noted for addition to knowledge files later

### Step 6: Generate Diagrams

Only after the architecture is fully specified, generate diagrams:

#### Engine Selection
- **Python `diagrams` library**: when cloud-provider icons are needed (AWS, Azure, GCP, Nutanix, VMware, OpenStack icons). ALWAYS prefer this for cloud architecture diagrams.
- **D2**: only for non-cloud-specific diagrams (sequence diagrams, generic flowcharts, process flows).

#### Detail Levels
Generate diagrams at appropriate detail levels:
- **Conceptual** (sort_order: 0) — high-level overview for stakeholders. Major components and data flows only.
- **Logical** (sort_order: 1) — service boundaries, network layout, AZs/regions for architects.
- **Detailed** (sort_order: 2) — specific resources, security groups, configurations for engineers.
- **Security-focused** (sort_order: 3) — if compliance is involved, a dedicated security controls diagram.

#### Process
1. Create artifact via `POST /versions/{id}/artifacts`
2. Trigger render via `POST /versions/{id}/artifacts/{id}/render`
3. Verify render status is "success"
4. If render fails, fix source code and re-render

### Step 7: Generate Documents

Create supporting documents:
- **Cost Estimate** — itemized cost breakdown based on the architecture decisions
- **Architecture Document** — if requested, summarizing all decisions (can use `POST /templates/render` for starting structure)

### Step 8: Well-Architected Review

Run the relevant Well-Architected Framework checklist as a final review pass:
- Load `knowledge/frameworks/{provider}-well-architected.md`
- Walk through each pillar's checklist items
- Track any findings as questions or ADRs
- This is a validation step, not a design step — it should confirm the design is sound

### Step 9: Retrospective

After the session:
- Note any knowledge gaps discovered during the session
- Create issues or PRs to add missing items to knowledge files
- This ensures the knowledge library improves with every project

## API Reference

All endpoints use the base URL from `ARCHITECT_API_URL` environment variable.

| Action | Method | Endpoint |
|--------|--------|----------|
| List clients | GET | `/clients` |
| Create client | POST | `/clients` |
| List projects | GET | `/clients/{id}/projects` |
| Create project | POST | `/clients/{id}/projects` |
| Create version | POST | `/projects/{id}/versions` |
| Create question | POST | `/projects/{id}/questions` |
| Answer question | PATCH | `/projects/{id}/questions/{id}` |
| Create ADR | POST | `/projects/{id}/adrs` |
| Create artifact | POST | `/versions/{id}/artifacts` |
| Trigger render | POST | `/versions/{id}/artifacts/{id}/render` |
| Export PDF | POST | `/versions/{id}/artifacts/{id}/export-pdf` |
| List templates | GET | `/templates` |
| Render template | POST | `/templates/render` |

## Rules

1. **Ask one question at a time** — never batch questions
2. **Create ADRs immediately** — every architectural decision gets an ADR, don't wait
3. **Use stack-specific icons** — always prefer Python `diagrams` library for cloud diagrams
4. **Do thorough analysis first** — don't generate diagrams until the architecture is fully specified
5. **Track everything** — every question and answer goes through the API
6. **Check failure patterns** — verify the design doesn't match known anti-patterns
7. **Feed back gaps** — any missing knowledge items get added to the library
