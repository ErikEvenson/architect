import { useEffect, useState } from "react";

interface KnowledgeFile {
  path: string;
  name: string;
  category: string;
}

interface KnowledgeTree {
  general: KnowledgeFile[];
  providers: Record<string, KnowledgeFile[]>;
  patterns: KnowledgeFile[];
}

const API_BASE = "/api/v1";

export function KnowledgePage() {
  const [tree, setTree] = useState<KnowledgeTree | null>(null);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [content, setContent] = useState<string>("");
  const [contentName, setContentName] = useState<string>("");

  useEffect(() => {
    fetch(`${API_BASE}/knowledge`)
      .then((r) => r.json())
      .then(setTree)
      .catch(() => {});
  }, []);

  const loadFile = async (path: string, name: string) => {
    setSelectedPath(path);
    setContentName(name);
    const res = await fetch(`${API_BASE}/knowledge/${path}`);
    const data = await res.json();
    setContent(data.content);
  };

  if (!tree) return <div className="text-gray-400">Loading...</div>;

  return (
    <div className="flex gap-6">
      {/* Sidebar: file tree */}
      <div className="w-64 shrink-0">
        <h1 className="text-xl font-bold text-gray-100 mb-4">Knowledge Library</h1>

        {/* General */}
        <div className="mb-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">General</h3>
          {tree.general.map((f) => (
            <button
              key={f.path}
              onClick={() => loadFile(f.path, f.name)}
              className={`block w-full text-left px-3 py-1.5 text-sm rounded ${
                selectedPath === f.path ? "bg-blue-900/30 text-blue-400 font-medium" : "text-gray-300 hover:bg-gray-700"
              }`}
            >
              {f.name}
            </button>
          ))}
        </div>

        {/* Providers */}
        {Object.entries(tree.providers).map(([provider, files]) => (
          <div key={provider} className="mb-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
              {provider.toUpperCase()}
            </h3>
            {files.map((f) => (
              <button
                key={f.path}
                onClick={() => loadFile(f.path, f.name)}
                className={`block w-full text-left px-3 py-1.5 text-sm rounded ${
                  selectedPath === f.path ? "bg-blue-900/30 text-blue-400 font-medium" : "text-gray-300 hover:bg-gray-700"
                }`}
              >
                {f.name}
              </button>
            ))}
          </div>
        ))}

        {/* Patterns */}
        <div className="mb-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Patterns</h3>
          {tree.patterns.map((f) => (
            <button
              key={f.path}
              onClick={() => loadFile(f.path, f.name)}
              className={`block w-full text-left px-3 py-1.5 text-sm rounded ${
                selectedPath === f.path ? "bg-blue-900/30 text-blue-400 font-medium" : "text-gray-300 hover:bg-gray-700"
              }`}
            >
              {f.name}
            </button>
          ))}
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1 min-w-0">
        {selectedPath ? (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-bold text-gray-100 mb-4">{contentName}</h2>
            <div
              className="prose prose-invert prose-sm max-w-none
                [&_h1]:text-lg [&_h1]:font-bold [&_h1]:text-gray-100 [&_h1]:mt-6 [&_h1]:mb-3
                [&_h2]:text-base [&_h2]:font-semibold [&_h2]:text-gray-200 [&_h2]:mt-5 [&_h2]:mb-2
                [&_h3]:text-sm [&_h3]:font-semibold [&_h3]:text-gray-300 [&_h3]:mt-4 [&_h3]:mb-1
                [&_p]:text-gray-300 [&_p]:mb-2
                [&_li]:text-gray-300
                [&_ul]:mb-3 [&_ol]:mb-3
                [&_code]:bg-gray-700 [&_code]:px-1 [&_code]:rounded [&_code]:text-gray-200
                [&_pre]:bg-gray-900 [&_pre]:p-3 [&_pre]:rounded [&_pre]:overflow-x-auto
                [&_table]:w-full [&_table]:mb-3
                [&_th]:bg-gray-700 [&_th]:px-3 [&_th]:py-1.5 [&_th]:text-left [&_th]:text-gray-200 [&_th]:text-sm
                [&_td]:border-t [&_td]:border-gray-700 [&_td]:px-3 [&_td]:py-1.5 [&_td]:text-gray-300 [&_td]:text-sm
                [&_strong]:text-gray-100
                [&_blockquote]:border-l-4 [&_blockquote]:border-blue-500 [&_blockquote]:pl-4 [&_blockquote]:text-gray-400
              "
              dangerouslySetInnerHTML={{
                __html: renderMarkdown(content),
              }}
            />
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            Select a knowledge file to view.
          </div>
        )}
      </div>
    </div>
  );
}

function renderMarkdown(md: string): string {
  // Simple markdown to HTML conversion for display
  let html = md
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Checklist items
    .replace(/^- \[ \] (.+)$/gm, '<li>☐ $1</li>')
    .replace(/^- \[x\] (.+)$/gm, '<li>☑ $1</li>')
    // Regular list items
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // Table rows
    .replace(/^\|(.+)\|$/gm, (match) => {
      const cells = match.split('|').filter(Boolean).map((c) => c.trim());
      if (cells.every((c) => /^-+$/.test(c))) return '';
      const tag = cells.some((c) => /^-+$/.test(c)) ? 'td' : 'td';
      return '<tr>' + cells.map((c) => `<${tag}>${c}</${tag}>`).join('') + '</tr>';
    })
    // Code blocks
    .replace(/```[\w]*\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // Paragraphs (lines not already tagged)
    .replace(/^(?!<[hluotp]|<tr|$)(.+)$/gm, '<p>$1</p>');

  // Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>[\s\S]*?<\/li>(\n|$))+/g, (match) => `<ul>${match}</ul>`);
  // Wrap consecutive <tr> in <table>
  html = html.replace(/(<tr>[\s\S]*?<\/tr>(\n|$))+/g, (match) => `<table>${match}</table>`);

  return html;
}
