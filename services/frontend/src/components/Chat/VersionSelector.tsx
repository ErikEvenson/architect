import { useEffect, useState } from "react";
import { clientsApi, projectsApi, versionsApi } from "../../api/client";
import { useChatStore } from "../../stores/chat";


interface VersionOption {
  versionId: string;
  label: string;
}

export function VersionSelector() {
  const { versionId, setVersionId } = useChatStore();
  const [options, setOptions] = useState<VersionOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOptions() {
      try {
        const clients = await clientsApi.list();
        const allOptions: VersionOption[] = [];

        for (const client of clients) {
          const projects = await projectsApi.list(client.id);
          for (const project of projects) {
            const versions = await versionsApi.list(project.id);
            for (const version of versions) {
              allOptions.push({
                versionId: version.id,
                label: `${client.name} / ${project.name} / ${version.version_number}${version.label ? ` (${version.label})` : ""}`,
              });
            }
          }
        }

        setOptions(allOptions);
      } catch {
        // silently fail - selector just won't have options
      } finally {
        setLoading(false);
      }
    }

    loadOptions();
  }, []);

  return (
    <select
      value={versionId || ""}
      onChange={(e) => setVersionId(e.target.value || null)}
      disabled={loading}
      className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500 disabled:opacity-50 max-w-xs"
    >
      <option value="">No project context</option>
      {options.map((opt) => (
        <option key={opt.versionId} value={opt.versionId}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}
