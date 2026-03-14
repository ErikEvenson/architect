import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { versionsApi, artifactsApi } from "../api/client";
import type { Version, Artifact } from "../api/types";
import { StatusBadge } from "../components/Common/StatusBadge";
import { EmptyState } from "../components/Common/EmptyState";

export function VersionDetailPage() {
  const { projectId, versionId } = useParams<{ projectId: string; versionId: string }>();
  const [version, setVersion] = useState<Version | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  useEffect(() => {
    if (!projectId || !versionId) return;
    versionsApi.get(projectId, versionId).then(setVersion).catch(() => {});
    artifactsApi.list(versionId).then(setArtifacts).catch(() => {});
  }, [projectId, versionId]);

  if (!version) return <div className="text-gray-500">Loading...</div>;

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
        {version.notes && <p className="text-sm text-gray-600 mt-2">{version.notes}</p>}
      </div>

      <h2 className="text-lg font-semibold text-gray-800 mb-4">Artifacts</h2>

      {artifacts.length === 0 ? (
        <EmptyState message="No artifacts yet. Create one in the artifact management view." />
      ) : (
        <div className="space-y-3">
          {artifacts.map((artifact) => (
            <div key={artifact.id} className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">{artifact.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{artifact.engine}</span>
                  <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{artifact.detail_level}</span>
                  <StatusBadge status={artifact.render_status} />
                </div>
              </div>
              {artifact.render_error && (
                <p className="text-sm text-red-600 mt-1">{artifact.render_error}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
