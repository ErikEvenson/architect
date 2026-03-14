import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { adrsApi } from "../api/client";
import type { ADR, ADRCreate } from "../api/types";
import { StatusBadge } from "../components/Common/StatusBadge";
import { EmptyState } from "../components/Common/EmptyState";

export function ADRListPage() {
  const { clientId, projectId } = useParams<{ clientId: string; projectId: string }>();
  const [adrs, setAdrs] = useState<ADR[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<ADRCreate>({ title: "", context: "", decision: "", consequences: "" });

  useEffect(() => {
    if (!projectId) return;
    adrsApi.list(projectId).then(setAdrs).catch(() => {});
  }, [projectId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !form.title.trim()) return;
    const adr = await adrsApi.create(projectId, form);
    setAdrs((prev) => [...prev, adr]);
    setForm({ title: "", context: "", decision: "", consequences: "" });
    setShowForm(false);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Architectural Decision Records</h1>
        <button
          onClick={() => setShowForm(true)}
          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
        >
          New ADR
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 bg-white p-4 rounded-lg border border-gray-200 space-y-3">
          <input
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Title"
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
          />
          <textarea
            value={form.context}
            onChange={(e) => setForm({ ...form, context: e.target.value })}
            placeholder="Context — What is the issue?"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            value={form.decision}
            onChange={(e) => setForm({ ...form, decision: e.target.value })}
            placeholder="Decision — What was decided?"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            value={form.consequences}
            onChange={(e) => setForm({ ...form, consequences: e.target.value })}
            placeholder="Consequences — What are the implications?"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="flex gap-3">
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Create</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600">Cancel</button>
          </div>
        </form>
      )}

      {adrs.length === 0 ? (
        <EmptyState message="No ADRs yet." />
      ) : (
        <div className="space-y-3">
          {adrs.map((adr) => (
            <Link
              key={adr.id}
              to={`/clients/${clientId}/projects/${projectId}/adrs/${adr.id}`}
              className="block bg-white p-4 rounded-lg border border-gray-200 hover:border-blue-300 transition"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">
                  ADR-{String(adr.adr_number).padStart(3, "0")}: {adr.title}
                </h3>
                <StatusBadge status={adr.status} />
              </div>
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">{adr.context}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
