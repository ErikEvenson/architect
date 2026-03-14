import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { clientsApi } from "../api/client";
import type { Client } from "../api/types";
import { EmptyState } from "../components/Common/EmptyState";

export function DashboardPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");

  useEffect(() => {
    clientsApi.list().then(setClients).catch(() => {});
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    const client = await clientsApi.create({ name: name.trim() });
    setClients((prev) => [...prev, client]);
    setName("");
    setShowForm(false);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-100">Dashboard</h1>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          New Client
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex gap-3">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Client name"
              className="flex-1 px-3 py-2 border border-gray-600 rounded bg-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
              autoFocus
            />
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Create
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-400 hover:text-gray-200">
              Cancel
            </button>
          </div>
        </form>
      )}

      {clients.length === 0 ? (
        <EmptyState message="No clients yet. Create one to get started." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {clients.map((client) => (
            <Link
              key={client.id}
              to={`/clients/${client.id}`}
              className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 hover:shadow-sm transition"
            >
              <h3 className="font-semibold text-gray-100">{client.name}</h3>
              <p className="text-sm text-gray-400 mt-1">{client.slug}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
