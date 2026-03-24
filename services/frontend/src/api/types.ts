export interface Client {
  id: string;
  name: string;
  slug: string;
  logo_path: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
  logo_path?: string | null;
  metadata?: Record<string, unknown>;
}

export interface ClientUpdate {
  name?: string;
  logo_path?: string | null;
  metadata?: Record<string, unknown>;
}

export interface Project {
  id: string;
  client_id: string;
  name: string;
  slug: string;
  description: string | null;
  cloud_providers: string[];
  status: "draft" | "active" | "archived";
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
  cloud_providers?: string[];
  status?: "draft" | "active" | "archived";
}

export interface ProjectUpdate {
  name?: string;
  description?: string | null;
  cloud_providers?: string[];
  status?: "draft" | "active" | "archived";
}

export interface Version {
  id: string;
  project_id: string;
  version_number: string;
  label: string | null;
  status: "draft" | "review" | "approved" | "superseded";
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface VersionCreate {
  version_number: string;
  label?: string | null;
  status?: "draft" | "review" | "approved" | "superseded";
  notes?: string | null;
}

export interface VersionUpdate {
  label?: string | null;
  status?: "draft" | "review" | "approved" | "superseded";
  notes?: string | null;
}

export interface Artifact {
  id: string;
  version_id: string;
  name: string;
  artifact_type: "diagram" | "document" | "pdf_report";
  detail_level: "conceptual" | "logical" | "detailed" | "deployment";
  engine: "diagrams_py" | "d2" | "markdown" | "weasyprint";
  source_code: string | null;
  output_paths: string[];
  render_status: "pending" | "rendering" | "success" | "error";
  render_error: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface ArtifactCreate {
  name: string;
  artifact_type: Artifact["artifact_type"];
  engine: Artifact["engine"];
  detail_level?: Artifact["detail_level"];
  source_code?: string | null;
  sort_order?: number;
}

export interface ArtifactUpdate {
  name?: string;
  detail_level?: Artifact["detail_level"];
  source_code?: string | null;
  sort_order?: number;
}

export interface ADR {
  id: string;
  version_id: string;
  adr_number: number;
  title: string;
  status: "proposed" | "accepted" | "deprecated" | "superseded";
  context: string;
  decision: string;
  consequences: string;
  superseded_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface ADRCreate {
  title: string;
  status?: "proposed" | "accepted" | "deprecated" | "superseded";
  context: string;
  decision: string;
  consequences: string;
}

export interface ADRUpdate {
  title?: string;
  status?: "proposed" | "accepted" | "deprecated" | "superseded";
  context?: string;
  decision?: string;
  consequences?: string;
}

export interface Question {
  id: string;
  version_id: string;
  question_text: string;
  answer_text: string | null;
  status: "open" | "answered" | "deferred";
  category: "requirements" | "security" | "scaling" | "compliance" | "cost" | "operations";
  created_at: string;
  updated_at: string;
}

export interface QuestionCreate {
  question_text: string;
  category?: Question["category"];
}

export interface QuestionUpdate {
  question_text?: string;
  answer_text?: string | null;
  status?: Question["status"];
  category?: Question["category"];
}

export interface Upload {
  id: string;
  version_id: string;
  original_filename: string;
  content_type: string;
  file_size: number;
  created_at: string;
  updated_at: string;
}

export interface ReindexProgress {
  phase: string;
  chunks_processed: number;
  total_chunks: number;
  current_batch: number;
  total_batches: number;
  vendor_docs_fetched: number;
  vendor_docs_total: number;
  uploads_processed: number;
  uploads_total: number;
}

export interface ReindexStatus {
  indexed: boolean;
  total_embeddings: number;
  knowledge_file_count: number;
  vendor_doc_count: number;
  upload_count: number;
  last_indexed_at: string | null;
  reindexing: boolean;
  paused: boolean;
  reindex_started_at: number | null;
  reindex_timeout: number | null;
  reindex_last_result: ReindexResponse | null;
  reindex_last_error: string | null;
  progress: ReindexProgress | null;
}

export interface ReindexResponse {
  status: string;
  files_processed: number;
  checklist_items_indexed: number;
  vendor_docs_indexed: number;
  uploads_indexed: number;
  duration_seconds: number;
  errors: string[];
}
