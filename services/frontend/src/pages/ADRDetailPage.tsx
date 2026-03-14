import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { adrsApi } from "../api/client";
import type { ADR } from "../api/types";
import { StatusBadge } from "../components/Common/StatusBadge";

const STATUS_OPTIONS = ["proposed", "accepted", "deprecated", "superseded"] as const;

export function ADRDetailPage() {
  const { versionId, adrId } = useParams<{ clientId: string; projectId: string; versionId: string; adrId: string }>();
  const [adr, setAdr] = useState<ADR | null>(null);

  useEffect(() => {
    if (!versionId || !adrId) return;
    adrsApi.get(versionId, adrId).then(setAdr).catch(() => {});
  }, [versionId, adrId]);

  const updateStatus = async (status: string) => {
    if (!versionId || !adrId) return;
    const updated = await adrsApi.update(versionId, adrId, { status: status as ADR["status"] });
    setAdr(updated);
  };

  if (!adr) return <div className="text-gray-400">Loading...</div>;

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-100">
          ADR-{String(adr.adr_number).padStart(3, "0")}: {adr.title}
        </h1>
        <div className="flex items-center gap-3 mt-2">
          <StatusBadge status={adr.status} />
          <select
            value={adr.status}
            onChange={(e) => updateStatus(e.target.value)}
            className="text-sm border border-gray-600 rounded bg-gray-700 text-gray-100 px-2 py-1"
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-6">
        <section className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Context</h2>
          <p className="text-gray-200 whitespace-pre-wrap">{adr.context}</p>
        </section>

        <section className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Decision</h2>
          <p className="text-gray-200 whitespace-pre-wrap">{adr.decision}</p>
        </section>

        <section className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Consequences</h2>
          <p className="text-gray-200 whitespace-pre-wrap">{adr.consequences}</p>
        </section>

        {adr.superseded_by && (
          <div className="text-sm text-gray-400">
            Superseded by ADR {adr.superseded_by}
          </div>
        )}
      </div>
    </div>
  );
}
