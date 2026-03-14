import { useEffect, useState } from "react";
import { artifactsApi, versionsApi } from "../../api/client";
import type { Artifact, Version } from "../../api/types";
import { DiagramViewer } from "./DiagramViewer";

interface ComparisonViewProps {
  projectId: string;
}

export function ComparisonView({ projectId }: ComparisonViewProps) {
  const [versions, setVersions] = useState<Version[]>([]);
  const [leftVersionId, setLeftVersionId] = useState<string>("");
  const [rightVersionId, setRightVersionId] = useState<string>("");
  const [leftArtifacts, setLeftArtifacts] = useState<Artifact[]>([]);
  const [rightArtifacts, setRightArtifacts] = useState<Artifact[]>([]);
  const [leftArtifactId, setLeftArtifactId] = useState<string>("");
  const [rightArtifactId, setRightArtifactId] = useState<string>("");

  useEffect(() => {
    versionsApi.list(projectId).then(setVersions).catch(() => {});
  }, [projectId]);

  useEffect(() => {
    if (leftVersionId) {
      artifactsApi.list(leftVersionId).then((arts) => {
        setLeftArtifacts(arts.filter((a) => a.render_status === "success"));
      }).catch(() => {});
    } else {
      setLeftArtifacts([]);
    }
  }, [leftVersionId]);

  useEffect(() => {
    if (rightVersionId) {
      artifactsApi.list(rightVersionId).then((arts) => {
        setRightArtifacts(arts.filter((a) => a.render_status === "success"));
      }).catch(() => {});
    } else {
      setRightArtifacts([]);
    }
  }, [rightVersionId]);

  const leftArtifact = leftArtifacts.find((a) => a.id === leftArtifactId);
  const rightArtifact = rightArtifacts.find((a) => a.id === rightArtifactId);

  const leftSvg = leftArtifact?.output_paths.find((p) => p.endsWith(".svg"));
  const rightSvg = rightArtifact?.output_paths.find((p) => p.endsWith(".svg"));

  const leftSvgUrl = leftSvg && leftVersionId
    ? artifactsApi.getOutputUrl(leftVersionId, leftArtifact!.id, leftSvg)
    : null;
  const rightSvgUrl = rightSvg && rightVersionId
    ? artifactsApi.getOutputUrl(rightVersionId, rightArtifact!.id, rightSvg)
    : null;

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-200 mb-4">Compare Versions</h2>

      <div className="grid grid-cols-2 gap-4">
        {/* Left side */}
        <div>
          <div className="flex gap-2 mb-3">
            <select
              value={leftVersionId}
              onChange={(e) => { setLeftVersionId(e.target.value); setLeftArtifactId(""); }}
              className="text-sm border border-gray-600 rounded px-2 py-1 flex-1"
            >
              <option value="">Select version...</option>
              {versions.map((v) => (
                <option key={v.id} value={v.id}>v{v.version_number}{v.label ? ` — ${v.label}` : ""}</option>
              ))}
            </select>
            <select
              value={leftArtifactId}
              onChange={(e) => setLeftArtifactId(e.target.value)}
              className="text-sm border border-gray-600 rounded px-2 py-1 flex-1"
              disabled={!leftVersionId}
            >
              <option value="">Select artifact...</option>
              {leftArtifacts.map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </div>
          {leftSvgUrl ? (
            <DiagramViewer svgUrl={leftSvgUrl} />
          ) : (
            <div className="bg-gray-700 rounded border border-gray-700 h-[500px] flex items-center justify-center text-gray-400">
              Select a version and artifact
            </div>
          )}
        </div>

        {/* Right side */}
        <div>
          <div className="flex gap-2 mb-3">
            <select
              value={rightVersionId}
              onChange={(e) => { setRightVersionId(e.target.value); setRightArtifactId(""); }}
              className="text-sm border border-gray-600 rounded px-2 py-1 flex-1"
            >
              <option value="">Select version...</option>
              {versions.map((v) => (
                <option key={v.id} value={v.id}>v{v.version_number}{v.label ? ` — ${v.label}` : ""}</option>
              ))}
            </select>
            <select
              value={rightArtifactId}
              onChange={(e) => setRightArtifactId(e.target.value)}
              className="text-sm border border-gray-600 rounded px-2 py-1 flex-1"
              disabled={!rightVersionId}
            >
              <option value="">Select artifact...</option>
              {rightArtifacts.map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </div>
          {rightSvgUrl ? (
            <DiagramViewer svgUrl={rightSvgUrl} />
          ) : (
            <div className="bg-gray-700 rounded border border-gray-700 h-[500px] flex items-center justify-center text-gray-400">
              Select a version and artifact
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
