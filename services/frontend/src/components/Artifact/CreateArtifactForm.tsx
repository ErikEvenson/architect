import { useState } from "react";
import type { ArtifactCreate, Artifact } from "../../api/types";

interface CreateArtifactFormProps {
  onSubmit: (data: ArtifactCreate) => void;
  onCancel: () => void;
}

export function CreateArtifactForm({ onSubmit, onCancel }: CreateArtifactFormProps) {
  const [name, setName] = useState("");
  const [artifactType, setArtifactType] = useState<Artifact["artifact_type"]>("diagram");
  const [engine, setEngine] = useState<Artifact["engine"]>("diagrams_py");
  const [detailLevel, setDetailLevel] = useState<Artifact["detail_level"]>("conceptual");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    onSubmit({ name: name.trim(), artifact_type: artifactType, engine, detail_level: detailLevel });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-3">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Artifact name"
        className="w-full px-3 py-2 border border-gray-600 rounded bg-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
        autoFocus
      />
      <div className="flex gap-3">
        <select
          value={artifactType}
          onChange={(e) => setArtifactType(e.target.value as Artifact["artifact_type"])}
          className="text-sm border border-gray-600 rounded bg-gray-700 text-gray-100 px-2 py-1.5"
        >
          <option value="diagram">Diagram</option>
          <option value="document">Document</option>
          <option value="pdf_report">PDF Report</option>
        </select>
        <select
          value={engine}
          onChange={(e) => setEngine(e.target.value as Artifact["engine"])}
          className="text-sm border border-gray-600 rounded bg-gray-700 text-gray-100 px-2 py-1.5"
        >
          <option value="diagrams_py">Python Diagrams</option>
          <option value="d2">D2</option>
          <option value="markdown">Markdown</option>
          <option value="weasyprint">WeasyPrint (PDF)</option>
        </select>
        <select
          value={detailLevel}
          onChange={(e) => setDetailLevel(e.target.value as Artifact["detail_level"])}
          className="text-sm border border-gray-600 rounded bg-gray-700 text-gray-100 px-2 py-1.5"
        >
          <option value="conceptual">Conceptual</option>
          <option value="logical">Logical</option>
          <option value="detailed">Detailed</option>
          <option value="deployment">Deployment</option>
        </select>
      </div>
      <div className="flex gap-3">
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Create</button>
        <button type="button" onClick={onCancel} className="px-4 py-2 text-gray-400">Cancel</button>
      </div>
    </form>
  );
}
