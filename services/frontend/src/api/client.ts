import type {
  Client, ClientCreate, ClientUpdate,
  Project, ProjectCreate, ProjectUpdate,
  Version, VersionCreate, VersionUpdate,
  Artifact, ArtifactCreate, ArtifactUpdate,
  ADR, ADRCreate, ADRUpdate,
  Question, QuestionCreate, QuestionUpdate,
} from "./types";

const API_BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (res.status === 204) return undefined as T;
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || res.statusText);
  }
  return res.json();
}

// Clients
export const clientsApi = {
  list: () => request<Client[]>("/clients"),
  get: (id: string) => request<Client>(`/clients/${id}`),
  create: (data: ClientCreate) =>
    request<Client>("/clients", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: ClientUpdate) =>
    request<Client>(`/clients/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/clients/${id}`, { method: "DELETE" }),
};

// Projects
export const projectsApi = {
  list: (clientId: string) => request<Project[]>(`/clients/${clientId}/projects`),
  get: (clientId: string, id: string) => request<Project>(`/clients/${clientId}/projects/${id}`),
  create: (clientId: string, data: ProjectCreate) =>
    request<Project>(`/clients/${clientId}/projects`, { method: "POST", body: JSON.stringify(data) }),
  update: (clientId: string, id: string, data: ProjectUpdate) =>
    request<Project>(`/clients/${clientId}/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (clientId: string, id: string) =>
    request<void>(`/clients/${clientId}/projects/${id}`, { method: "DELETE" }),
};

// Versions
export const versionsApi = {
  list: (projectId: string) => request<Version[]>(`/projects/${projectId}/versions`),
  get: (projectId: string, id: string) => request<Version>(`/projects/${projectId}/versions/${id}`),
  create: (projectId: string, data: VersionCreate) =>
    request<Version>(`/projects/${projectId}/versions`, { method: "POST", body: JSON.stringify(data) }),
  update: (projectId: string, id: string, data: VersionUpdate) =>
    request<Version>(`/projects/${projectId}/versions/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// Artifacts
export const artifactsApi = {
  list: (versionId: string) => request<Artifact[]>(`/versions/${versionId}/artifacts`),
  get: (versionId: string, id: string) => request<Artifact>(`/versions/${versionId}/artifacts/${id}`),
  create: (versionId: string, data: ArtifactCreate) =>
    request<Artifact>(`/versions/${versionId}/artifacts`, { method: "POST", body: JSON.stringify(data) }),
  update: (versionId: string, id: string, data: ArtifactUpdate) =>
    request<Artifact>(`/versions/${versionId}/artifacts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (versionId: string, id: string) =>
    request<void>(`/versions/${versionId}/artifacts/${id}`, { method: "DELETE" }),
  triggerRender: (versionId: string, id: string) =>
    request<Artifact>(`/versions/${versionId}/artifacts/${id}/render`, { method: "POST" }),
  getOutputUrl: (versionId: string, id: string, filename: string) =>
    `${API_BASE}/versions/${versionId}/artifacts/${id}/outputs/${filename}`,
  clone: (versionId: string, targetVersionId: string) =>
    request<Artifact[]>(`/versions/${versionId}/artifacts/clone`, {
      method: "POST",
      body: JSON.stringify({ target_version_id: targetVersionId }),
    }),
  exportPdfUrl: (versionId: string, id: string) =>
    `${API_BASE}/versions/${versionId}/artifacts/${id}/export-pdf`,
};

// ADRs
export const adrsApi = {
  list: (projectId: string) => request<ADR[]>(`/projects/${projectId}/adrs`),
  get: (projectId: string, id: string) => request<ADR>(`/projects/${projectId}/adrs/${id}`),
  create: (projectId: string, data: ADRCreate) =>
    request<ADR>(`/projects/${projectId}/adrs`, { method: "POST", body: JSON.stringify(data) }),
  update: (projectId: string, id: string, data: ADRUpdate) =>
    request<ADR>(`/projects/${projectId}/adrs/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  supersede: (projectId: string, id: string, data: ADRCreate) =>
    request<ADR>(`/projects/${projectId}/adrs/${id}/supersede`, { method: "POST", body: JSON.stringify(data) }),
};

// Questions
export const questionsApi = {
  list: (projectId: string, params?: { status?: string; category?: string }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set("status", params.status);
    if (params?.category) query.set("category", params.category);
    const qs = query.toString();
    return request<Question[]>(`/projects/${projectId}/questions${qs ? `?${qs}` : ""}`);
  },
  get: (projectId: string, id: string) => request<Question>(`/projects/${projectId}/questions/${id}`),
  create: (projectId: string, data: QuestionCreate) =>
    request<Question>(`/projects/${projectId}/questions`, { method: "POST", body: JSON.stringify(data) }),
  update: (projectId: string, id: string, data: QuestionUpdate) =>
    request<Question>(`/projects/${projectId}/questions/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};
