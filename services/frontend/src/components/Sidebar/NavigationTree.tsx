import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { Client, Project, Version } from "../../api/types";

interface TreeProps {
  clients: Client[];
  projectsByClient: Record<string, Project[]>;
  versionsByProject: Record<string, Version[]>;
}

export function NavigationTree({ clients, projectsByClient, versionsByProject }: TreeProps) {
  const params = useParams();
  const [expandedClients, setExpandedClients] = useState<Set<string>>(new Set());
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(new Set());

  const toggleClient = (id: string) => {
    setExpandedClients((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleProject = (id: string) => {
    setExpandedProjects((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <nav className="text-sm text-gray-300">
      {clients.map((client) => (
        <div key={client.id}>
          <button
            onClick={() => toggleClient(client.id)}
            className={`w-full text-left px-3 py-1.5 hover:bg-gray-700 flex items-center gap-1 ${
              params.clientId === client.id ? "font-semibold text-blue-400" : ""
            }`}
          >
            <span className="text-xs">{expandedClients.has(client.id) ? "▼" : "▶"}</span>
            <Link to={`/clients/${client.id}`} className="flex-1 truncate" onClick={(e) => e.stopPropagation()}>
              {client.name}
            </Link>
          </button>

          {expandedClients.has(client.id) && (
            <div className="ml-4">
              {(projectsByClient[client.id] ?? []).map((project) => (
                <div key={project.id}>
                  <button
                    onClick={() => toggleProject(project.id)}
                    className={`w-full text-left px-3 py-1 hover:bg-gray-700 flex items-center gap-1 ${
                      params.projectId === project.id ? "font-semibold text-blue-400" : ""
                    }`}
                  >
                    <span className="text-xs">{expandedProjects.has(project.id) ? "▼" : "▶"}</span>
                    <Link
                      to={`/clients/${client.id}/projects/${project.id}`}
                      className="flex-1 truncate"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {project.name}
                    </Link>
                  </button>

                  {expandedProjects.has(project.id) && (
                    <div className="ml-4">
                      {(versionsByProject[project.id] ?? []).map((version) => (
                        <Link
                          key={version.id}
                          to={`/clients/${client.id}/projects/${project.id}/versions/${version.id}`}
                          className={`block px-3 py-1 hover:bg-gray-700 truncate ${
                            params.versionId === version.id ? "font-semibold text-blue-400" : ""
                          }`}
                        >
                          v{version.version_number}
                          {version.label ? ` — ${version.label}` : ""}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </nav>
  );
}
