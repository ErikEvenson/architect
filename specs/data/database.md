# Database Schema

## Overview

PostgreSQL 16 database `architect` with eleven tables supporting the core data model:
Client → Project → Version → Artifact/InventoryItem, plus ADR and Question per version,
CoverageItem per version, and a standalone knowledge_embeddings table for vector search over the knowledge library.

All tables use UUID primary keys and UTC timestamps.

## Tables

### clients

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(255) | NOT NULL, UNIQUE |
| logo_path | VARCHAR(500) | NULL |
| metadata | JSONB | NOT NULL, default '{}' |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_clients_slug` UNIQUE on `slug`
- `ix_clients_name` on `name`

**Notes:**
- `slug` is auto-generated server-side from `name` (lowercase, hyphens, no special chars)
- `metadata` stores arbitrary key-value pairs (e.g., industry, contact info)

### projects

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| client_id | UUID | NOT NULL, FK → clients(id) ON DELETE CASCADE |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| cloud_providers | JSONB | NOT NULL, default '[]' |
| status | VARCHAR(20) | NOT NULL, default 'draft', CHECK IN ('draft', 'active', 'archived') |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_projects_client_slug` UNIQUE on `(client_id, slug)`
- `ix_projects_client_id` on `client_id`
- `ix_projects_status` on `status`

**Notes:**
- `slug` is unique per client (not globally)
- `cloud_providers` is a JSON array of strings (e.g., `["aws", "azure", "nutanix"]`)
- `status` transitions: draft → active → archived

### versions

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| project_id | UUID | NOT NULL, FK → projects(id) ON DELETE CASCADE |
| version_number | VARCHAR(20) | NOT NULL |
| label | VARCHAR(255) | NULL |
| status | VARCHAR(20) | NOT NULL, default 'draft', CHECK IN ('draft', 'review', 'approved', 'superseded') |
| notes | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_versions_project_version` UNIQUE on `(project_id, version_number)`
- `ix_versions_project_id` on `project_id`
- `ix_versions_status` on `status`

**Notes:**
- `version_number` is semver format (e.g., "1.0.0")
- Unique per project

### artifacts

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| version_id | UUID | NOT NULL, FK → versions(id) ON DELETE CASCADE |
| name | VARCHAR(255) | NOT NULL |
| artifact_type | VARCHAR(20) | NOT NULL, CHECK IN ('diagram', 'document', 'pdf_report') |
| detail_level | VARCHAR(20) | NOT NULL, default 'conceptual', CHECK IN ('conceptual', 'logical', 'detailed', 'deployment') |
| engine | VARCHAR(20) | NOT NULL, CHECK IN ('diagrams_py', 'd2', 'markdown', 'weasyprint') |
| source_code | TEXT | NULL |
| output_paths | JSONB | NOT NULL, default '[]' |
| render_status | VARCHAR(20) | NOT NULL, default 'pending', CHECK IN ('pending', 'rendering', 'success', 'error') |
| render_error | TEXT | NULL |
| sort_order | INTEGER | NOT NULL, default 0 |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_artifacts_version_id` on `version_id`
- `ix_artifacts_version_type` on `(version_id, artifact_type)`
- `ix_artifacts_version_sort` on `(version_id, sort_order)`

**Notes:**
- `output_paths` is a JSON array of relative file paths (e.g., `["diagram.svg", "diagram.png"]`)
- `render_error` stores error message when `render_status` is 'error'

### adrs

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| version_id | UUID | NOT NULL, FK → versions(id) ON DELETE CASCADE |
| adr_number | INTEGER | NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| status | VARCHAR(20) | NOT NULL, default 'proposed', CHECK IN ('proposed', 'accepted', 'deprecated', 'superseded') |
| context | TEXT | NOT NULL |
| decision | TEXT | NOT NULL |
| consequences | TEXT | NOT NULL |
| superseded_by | UUID | NULL, FK → adrs(id) ON DELETE SET NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_adrs_version_number` UNIQUE on `(version_id, adr_number)`
- `ix_adrs_version_id` on `version_id`
- `ix_adrs_status` on `status`

**Notes:**
- `adr_number` is sequential per version (auto-assigned as max+1 within version)
- When superseding, set old ADR status to 'superseded' and `superseded_by` to new ADR id

### questions

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| version_id | UUID | NOT NULL, FK → versions(id) ON DELETE CASCADE |
| question_text | TEXT | NOT NULL |
| answer_text | TEXT | NULL |
| status | VARCHAR(20) | NOT NULL, default 'open', CHECK IN ('open', 'answered', 'deferred', 'not_applicable') |
| category | VARCHAR(20) | NOT NULL, default 'requirements', CHECK IN ('requirements', 'networking', 'security', 'storage', 'compute', 'identity', 'monitoring', 'dr', 'compliance', 'migration', 'cost', 'operations') |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_questions_version_id` on `version_id`
- `ix_questions_version_status` on `(version_id, status)`
- `ix_questions_category` on `category`

### inventory_items

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| version_id | UUID | NOT NULL, FK → versions(id) ON DELETE CASCADE |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| data_type | VARCHAR(50) | NOT NULL, default 'custom' |
| data | TEXT | NOT NULL |
| sort_order | INTEGER | NOT NULL, default 0 |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_inventory_items_version_id` on `version_id`
- `ix_inventory_items_version_type` on `(version_id, data_type)`

**Notes:**
- `data` stores raw source inventory content in original form (CSV, JSON, plain text, etc.)
- `data_type` categorizes the inventory (e.g., 'vm_inventory', 'network_topology', 'server_list', 'custom')
- Scoped to a version; cloned when cloning version artifacts

### uploads

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| version_id | UUID | NOT NULL, FK → versions(id) ON DELETE CASCADE |
| original_filename | VARCHAR(500) | NOT NULL |
| stored_filename | VARCHAR(500) | NOT NULL |
| content_type | VARCHAR(255) | NOT NULL, default 'application/octet-stream' |
| file_size | BIGINT | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_uploads_version_id` on `version_id`

**Notes:**
- Binary files stored on PVC at `{output_dir}/{client}/{project}/{version}/uploads/{upload_id}/{stored_filename}`
- `original_filename` preserves the user's filename; `stored_filename` may be sanitized
- `file_size` in bytes
- Scoped to a version; files on disk deleted via CASCADE trigger or application logic

### knowledge_embeddings

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| source_file | VARCHAR(500) | NOT NULL |
| source_type | VARCHAR(20) | NOT NULL, default 'knowledge_file', CHECK IN ('knowledge_file', 'vendor_doc') |
| section | VARCHAR(255) | NOT NULL |
| checklist_item | TEXT | NULL |
| priority | VARCHAR(20) | NULL, CHECK IN ('critical', 'recommended', 'optional') |
| content | TEXT | NOT NULL |
| content_hash | VARCHAR(64) | NOT NULL |
| embedding | VECTOR(384) | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_knowledge_embeddings_source_file` on `source_file`
- `ix_knowledge_embeddings_source_type` on `source_type`
- `ix_knowledge_embeddings_priority` on `priority`
- `ix_knowledge_embeddings_content_hash` on `content_hash`
- `ix_knowledge_embeddings_vector` HNSW on `embedding` using vector_cosine_ops

**Notes:**
- Requires `pgvector` extension (`CREATE EXTENSION vector;`)
- `content_hash` is SHA-256 of `content`, used to skip re-embedding unchanged items during reindex
- `source_file` is the relative path for knowledge files (e.g., `general/api-design.md`) or a URL for vendor docs
- `source_type` distinguishes knowledge library files from fetched vendor documentation
- `checklist_item` is the extracted checklist item text (null for non-checklist sections like "Why This Matters")
- `priority` is extracted from checklist item tags: `[Critical]`, `[Recommended]`, `[Optional]`
- `embedding` is a 384-dimensional vector from the `all-MiniLM-L6-v2` sentence-transformers model
- HNSW index provides approximate nearest neighbor search with cosine distance

### coverage_items

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| version_id | UUID | NOT NULL, FK → versions(id) ON DELETE CASCADE |
| knowledge_file | VARCHAR(255) | NOT NULL |
| item_text | TEXT | NOT NULL |
| priority | VARCHAR(20) | NOT NULL, CHECK IN ('Critical', 'Recommended', 'Optional') |
| status | VARCHAR(20) | NOT NULL, default 'pending', CHECK IN ('pending', 'addressed', 'deferred', 'na') |
| question_id | UUID | NULL, FK → questions(id) ON DELETE SET NULL |
| reason | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**Indexes:**
- `ix_coverage_items_version_id` on `version_id`
- `ix_coverage_items_version_file` on `(version_id, knowledge_file)`
- `ix_coverage_items_version_priority` on `(version_id, priority)`

**Notes:**
- Tracks whether knowledge library checklist items have been addressed in the architecture design
- Links to the specific knowledge file and checklist item text
- `question_id` optionally links to a question that addresses this coverage item
- `reason` captures why an item was deferred or marked not applicable

## Cascade Behavior

| Parent | Child | ON DELETE |
|---|---|---|
| clients | projects | CASCADE |
| projects | versions | CASCADE |
| versions | adrs | CASCADE |
| versions | questions | CASCADE |
| versions | coverage_items | CASCADE |
| versions | artifacts | CASCADE |
| versions | inventory_items | CASCADE |
| versions | uploads | CASCADE |
| adrs | adrs (superseded_by) | SET NULL |
| questions | coverage_items (question_id) | SET NULL |

## Updated At Trigger

All tables use a trigger to auto-update `updated_at` on row modification:

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
