import { useEffect, useState } from "react";
import { Outlet, Link } from "react-router-dom";
import { NavigationTree } from "./Sidebar/NavigationTree";
import { useUIStore } from "../stores/ui";
import { clientsApi, projectsApi, versionsApi } from "../api/client";
import type { Client, Project, Version } from "../api/types";

export function Layout() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const [clients, setClients] = useState<Client[]>([]);
  const [projectsByClient, setProjectsByClient] = useState<Record<string, Project[]>>({});
  const [versionsByProject, setVersionsByProject] = useState<Record<string, Version[]>>({});

  useEffect(() => {
    clientsApi.list().then(async (clientList) => {
      setClients(clientList);
      const projectMap: Record<string, Project[]> = {};
      const versionMap: Record<string, Version[]> = {};
      for (const c of clientList) {
        const projects = await projectsApi.list(c.id);
        projectMap[c.id] = projects;
        for (const p of projects) {
          versionMap[p.id] = await versionsApi.list(p.id);
        }
      }
      setProjectsByClient(projectMap);
      setVersionsByProject(versionMap);
    }).catch(() => {});
  }, []);

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={toggleSidebar} className="text-gray-500 hover:text-gray-700 p-1">
            ☰
          </button>
          <Link to="/" className="text-lg font-semibold text-gray-900">Architect</Link>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        {!sidebarCollapsed && (
          <aside className="w-64 bg-gray-50 border-r border-gray-200 overflow-y-auto shrink-0">
            <div className="p-3 border-b border-gray-200">
              <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Projects</h2>
            </div>
            <NavigationTree
              clients={clients}
              projectsByClient={projectsByClient}
              versionsByProject={versionsByProject}
            />
          </aside>
        )}

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
