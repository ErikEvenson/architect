import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { clientsApi, projectsApi } from "../api/client";
import type { Client, Project } from "../api/types";
import { StatusBadge } from "../components/Common/StatusBadge";
import { EmptyState } from "../components/Common/EmptyState";
import { ConfirmDialog } from "../components/Common/ConfirmDialog";

export function ClientDetailPage() {
  const { clientId } = useParams<{ clientId: string }>();
  const navigate = useNavigate();
  const [client, setClient] = useState<Client | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (!clientId) return;
    clientsApi.get(clientId).then(setClient).catch(() => {});
    projectsApi.list(clientId).then(setProjects).catch(() => {});
  }, [clientId]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientId || !projectName.trim()) return;
    const project = await projectsApi.create(clientId, { name: projectName.trim() });
    setProjects((prev) => [...prev, project]);
    setProjectName("");
    setShowForm(false);
  };

  const handleDelete = async () => {
    if (!clientId) return;
    await clientsApi.delete(clientId);
    navigate("/");
  };

  if (!client) return <div className="text-gray-500">Loading...</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{client.name}</h1>
          <p className="text-sm text-gray-500">{client.slug}</p>
        </div>
        <button onClick={() => setConfirmDelete(true)} className="px-3 py-1.5 text-red-600 hover:text-red-800 text-sm">
          Delete Client
        </button>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Projects</h2>
        <button
          onClick={() => setShowForm(true)}
          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
        >
          New Project
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreateProject} className="mb-4 bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex gap-3">
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Project name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Create</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600">Cancel</button>
          </div>
        </form>
      )}

      {projects.length === 0 ? (
        <EmptyState message="No projects yet." />
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/clients/${clientId}/projects/${project.id}`}
              className="block bg-white p-4 rounded-lg border border-gray-200 hover:border-blue-300 transition"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{project.name}</h3>
                <StatusBadge status={project.status} />
              </div>
              {project.description && <p className="text-sm text-gray-600 mt-1">{project.description}</p>}
              {project.cloud_providers.length > 0 && (
                <div className="flex gap-1 mt-2">
                  {project.cloud_providers.map((p) => (
                    <span key={p} className="text-xs bg-gray-100 px-2 py-0.5 rounded">{p}</span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={confirmDelete}
        title="Delete Client"
        message={`Delete "${client.name}" and all its projects? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setConfirmDelete(false)}
      />
    </div>
  );
}
