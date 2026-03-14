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
  project_id: string;
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
  project_id: string;
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
