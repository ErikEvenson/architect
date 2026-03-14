import { useState } from "react";
import type { Artifact } from "../../api/types";
import { StatusBadge } from "../Common/StatusBadge";
import { EmptyState } from "../Common/EmptyState";

const DETAIL_LEVELS = ["all", "conceptual", "logical", "detailed", "deployment"] as const;

interface ArtifactListProps {
  artifacts: Artifact[];
  selectedId: string | null;
  onSelect: (artifact: Artifact) => void;
  onDelete: (artifact: Artifact) => void;
}

export function ArtifactList({ artifacts, selectedId, onSelect, onDelete }: ArtifactListProps) {
  const [filterLevel, setFilterLevel] = useState<string>("all");

  const filtered = filterLevel === "all"
    ? artifacts
    : artifacts.filter((a) => a.detail_level === filterLevel);

  return (
    <div>
      {/* Detail level tabs */}
      <div className="flex gap-1 mb-3 border-b border-gray-700">
        {DETAIL_LEVELS.map((level) => (
          <button
            key={level}
            onClick={() => setFilterLevel(level)}
            className={`px-3 py-1.5 text-sm capitalize ${
              filterLevel === level
                ? "border-b-2 border-blue-600 text-blue-600 font-medium"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            {level}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState message="No artifacts at this detail level." />
      ) : (
        <div className="space-y-2">
          {filtered.map((artifact) => (
            <div
              key={artifact.id}
              onClick={() => onSelect(artifact)}
              className={`p-3 rounded-lg border cursor-pointer transition ${
                selectedId === artifact.id
                  ? "border-blue-400 bg-blue-900/30"
                  : "border-gray-700 bg-gray-800 hover:border-gray-600"
              }`}
            >
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-100 text-sm">{artifact.name}</h4>
                <div className="flex items-center gap-1">
                  <span className="text-xs bg-gray-700 px-1.5 py-0.5 rounded">{artifact.engine}</span>
                  <StatusBadge status={artifact.render_status} />
                </div>
              </div>
              <div className="flex items-center justify-between mt-1">
                <span className="text-xs text-gray-400">{artifact.detail_level}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); onDelete(artifact); }}
                  className="text-xs text-red-500 hover:text-red-400"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
