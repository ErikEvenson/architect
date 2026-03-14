import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { versionsApi, artifactsApi } from "../api/client";
import type { Version, Artifact, ArtifactCreate } from "../api/types";
import { StatusBadge } from "../components/Common/StatusBadge";
import { ConfirmDialog } from "../components/Common/ConfirmDialog";
import { ArtifactList } from "../components/Artifact/ArtifactList";
import { CreateArtifactForm } from "../components/Artifact/CreateArtifactForm";
import { CodeEditor } from "../components/Artifact/CodeEditor";
import { DiagramViewer } from "../components/Artifact/DiagramViewer";

export function VersionDetailPage() {
  const { projectId, versionId } = useParams<{ projectId: string; versionId: string }>();
  const [version, setVersion] = useState<Version | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selected, setSelected] = useState<Artifact | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [sourceCode, setSourceCode] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<Artifact | null>(null);
  const [rendering, setRendering] = useState(false);

  const loadArtifacts = useCallback(async () => {
    if (!versionId) return;
    const list = await artifactsApi.list(versionId);
    setArtifacts(list);
  }, [versionId]);

  useEffect(() => {
    if (!projectId || !versionId) return;
    versionsApi.get(projectId, versionId).then(setVersion).catch(() => {});
    loadArtifacts();
  }, [projectId, versionId, loadArtifacts]);

  const handleSelect = (artifact: Artifact) => {
    setSelected(artifact);
    setSourceCode(artifact.source_code ?? "");
  };

  const handleCreate = async (data: ArtifactCreate) => {
    if (!versionId) return;
    const artifact = await artifactsApi.create(versionId, data);
    setArtifacts((prev) => [...prev, artifact]);
    setSelected(artifact);
    setSourceCode(artifact.source_code ?? "");
    setShowCreateForm(false);
  };

  const handleSaveSource = async () => {
    if (!versionId || !selected) return;
    const updated = await artifactsApi.update(versionId, selected.id, { source_code: sourceCode });
    setSelected(updated);
    setArtifacts((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
  };

  const handleRender = async () => {
    if (!versionId || !selected) return;
    setRendering(true);
    try {
      await artifactsApi.update(versionId, selected.id, { source_code: sourceCode });
      const updated = await artifactsApi.triggerRender(versionId, selected.id);
      setSelected(updated);
      setArtifacts((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
    } catch {
      const refreshed = await artifactsApi.get(versionId, selected.id);
      setSelected(refreshed);
      setArtifacts((prev) => prev.map((a) => (a.id === refreshed.id ? refreshed : a)));
    } finally {
      setRendering(false);
    }
  };

  const handleDelete = async () => {
    if (!versionId || !deleteTarget) return;
    await artifactsApi.delete(versionId, deleteTarget.id);
    setArtifacts((prev) => prev.filter((a) => a.id !== deleteTarget.id));
    if (selected?.id === deleteTarget.id) setSelected(null);
    setDeleteTarget(null);
  };

  if (!version) return <div className="text-gray-500">Loading...</div>;

  const svgFile = selected?.output_paths.find((p) => p.endsWith(".svg"));
  const svgUrl = svgFile && versionId
    ? artifactsApi.getOutputUrl(versionId, selected!.id, svgFile)
    : null;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          v{version.version_number}
          {version.label && <span className="text-gray-500 font-normal ml-2">— {version.label}</span>}
        </h1>
        <div className="flex items-center gap-2 mt-1">
          <StatusBadge status={version.status} />
        </div>
      </div>

      <div className="flex gap-6">
        {/* Left panel: artifact list */}
        <div className="w-72 shrink-0">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-800">Artifacts</h2>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
            >
              + New
            </button>
          </div>

          {showCreateForm && (
            <div className="mb-3">
              <CreateArtifactForm onSubmit={handleCreate} onCancel={() => setShowCreateForm(false)} />
            </div>
          )}

          <ArtifactList
            artifacts={artifacts}
            selectedId={selected?.id ?? null}
            onSelect={handleSelect}
            onDelete={setDeleteTarget}
          />
        </div>

        {/* Right panel: editor + viewer */}
        <div className="flex-1 min-w-0">
          {selected ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">{selected.name}</h3>
                <div className="flex items-center gap-2">
                  <StatusBadge status={selected.render_status} />
                  <button
                    onClick={handleSaveSource}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50"
                  >
                    Save
                  </button>
                  <button
                    onClick={handleRender}
                    disabled={rendering || !sourceCode.trim()}
                    className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                  >
                    {rendering ? "Rendering..." : "Render"}
                  </button>
                </div>
              </div>

              {/* Source editor */}
              <div>
                <h4 className="text-sm font-medium text-gray-600 mb-1">Source Code</h4>
                <CodeEditor
                  value={sourceCode}
                  onChange={setSourceCode}
                  language={selected.engine === "d2" ? "d2" : "python"}
                />
              </div>

              {/* Render error */}
              {selected.render_status === "error" && selected.render_error && (
                <div className="bg-red-50 border border-red-200 rounded p-3">
                  <h4 className="text-sm font-medium text-red-800 mb-1">Render Error</h4>
                  <pre className="text-xs text-red-700 whitespace-pre-wrap">{selected.render_error}</pre>
                </div>
              )}

              {/* Diagram viewer */}
              {selected.render_status === "success" && svgUrl && (
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-1">Output</h4>
                  <DiagramViewer svgUrl={svgUrl} />
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              Select an artifact or create a new one.
            </div>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Artifact"
        message={`Delete "${deleteTarget?.name}"? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
