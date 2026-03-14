import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { projectsApi, versionsApi } from "../api/client";
import type { Project, Version } from "../api/types";
import { StatusBadge } from "../components/Common/StatusBadge";
import { EmptyState } from "../components/Common/EmptyState";
import { ConfirmDialog } from "../components/Common/ConfirmDialog";

export function ProjectDetailPage() {
  const { clientId, projectId } = useParams<{ clientId: string; projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [versionNumber, setVersionNumber] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (!clientId || !projectId) return;
    projectsApi.get(clientId, projectId).then(setProject).catch(() => {});
    versionsApi.list(projectId).then(setVersions).catch(() => {});
  }, [clientId, projectId]);

  const handleCreateVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !versionNumber.trim()) return;
    const version = await versionsApi.create(projectId, { version_number: versionNumber.trim() });
    setVersions((prev) => [...prev, version]);
    setVersionNumber("");
    setShowForm(false);
  };

  const handleDelete = async () => {
    if (!clientId || !projectId) return;
    await projectsApi.delete(clientId, projectId);
    navigate(`/clients/${clientId}`);
  };

  if (!project) return <div className="text-gray-400">Loading...</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">{project.name}</h1>
          <div className="flex items-center gap-2 mt-1">
            <StatusBadge status={project.status} />
            {project.cloud_providers.map((p) => (
              <span key={p} className="text-xs bg-gray-700 px-2 py-0.5 rounded">{p}</span>
            ))}
          </div>
          {project.description && <p className="text-sm text-gray-400 mt-2">{project.description}</p>}
        </div>
        <div className="flex gap-2">
          <Link
            to={`/clients/${clientId}/projects/${projectId}/compare`}
            className="px-3 py-1.5 text-sm border border-gray-600 rounded hover:bg-gray-700"
          >
            Compare
          </Link>
          <button onClick={() => setConfirmDelete(true)} className="px-3 py-1.5 text-red-400 hover:text-red-300 text-sm">
            Delete
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-200">Versions</h2>
        <button
          onClick={() => setShowForm(true)}
          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
        >
          New Version
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreateVersion} className="mb-4 bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex gap-3">
            <input
              type="text"
              value={versionNumber}
              onChange={(e) => setVersionNumber(e.target.value)}
              placeholder="Version number (e.g. 1.0.0)"
              className="flex-1 px-3 py-2 border border-gray-600 rounded bg-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
              autoFocus
            />
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Create</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-400">Cancel</button>
          </div>
        </form>
      )}

      {versions.length === 0 ? (
        <EmptyState message="No versions yet." />
      ) : (
        <div className="space-y-3">
          {versions.map((version) => (
            <Link
              key={version.id}
              to={`/clients/${clientId}/projects/${projectId}/versions/${version.id}`}
              className="block bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 transition"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-100">
                  v{version.version_number}
                  {version.label && <span className="text-gray-400 font-normal ml-2">— {version.label}</span>}
                </h3>
                <StatusBadge status={version.status} />
              </div>
              {version.notes && <p className="text-sm text-gray-400 mt-1">{version.notes}</p>}
            </Link>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={confirmDelete}
        title="Delete Project"
        message={`Delete "${project.name}" and all its versions? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setConfirmDelete(false)}
      />
    </div>
  );
}
