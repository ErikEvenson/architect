import { useEffect, useState, useCallback, useRef } from "react";
import { knowledgeApi } from "../api/client";
import type { ReindexStatus } from "../api/types";

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

const PHASE_LABELS: Record<string, string> = {
  idle: "Idle",
  parsing: "Parsing knowledge files",
  fetching_vendor_docs: "Fetching vendor docs",
  indexing_uploads: "Reading uploaded files",
  embedding: "Generating embeddings",
  done: "Done",
};

export function KnowledgePage() {
  const [tree, setTree] = useState<KnowledgeTree | null>(null);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [content, setContent] = useState<string>("");
  const [contentName, setContentName] = useState<string>("");

  // Reindex state (all driven by server)
  const [indexStatus, setIndexStatus] = useState<ReindexStatus | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [includeVendorDocs, setIncludeVendorDocs] = useState(true);
  const [includeUploads, setIncludeUploads] = useState(true);
  const [forceReindex, setForceReindex] = useState(false);
  const [timeoutMin, setTimeoutMin] = useState<string>("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Derived state
  const reindexing = indexStatus?.reindexing ?? false;
  const paused = indexStatus?.paused ?? false;
  const lastResult = indexStatus?.reindex_last_result ?? null;
  const reindexError = indexStatus?.reindex_last_error ?? null;
  const progress = indexStatus?.progress ?? null;
  const elapsed = indexStatus?.reindex_started_at
    ? Math.round(Date.now() / 1000 - indexStatus.reindex_started_at)
    : 0;

  const fetchStatus = useCallback(async () => {
    try {
      const status = await knowledgeApi.reindexStatus();
      setIndexStatus(status);
      return status;
    } catch {
      return null;
    }
  }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
  }, []);

  const startPolling = useCallback(() => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      const status = await fetchStatus();
      if (status && !status.reindexing) {
        stopPolling();
      }
    }, 2000);
  }, [fetchStatus, stopPolling]);

  useEffect(() => () => stopPolling(), [stopPolling]);

  useEffect(() => {
    fetch(`${API_BASE}/knowledge`)
      .then((r) => r.json())
      .then(setTree)
      .catch(() => {});
    fetchStatus().then((status) => {
      if (status?.reindexing) startPolling();
    });
  }, [fetchStatus, startPolling]);

  const handleAction = async (action: () => Promise<unknown>) => {
    setActionError(null);
    try {
      await action();
      await fetchStatus();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Action failed");
    }
  };

  const handleStart = () => handleAction(async () => {
    const timeoutSec = timeoutMin ? parseFloat(timeoutMin) * 60 : undefined;
    await knowledgeApi.reindex({
      include_vendor_docs: includeVendorDocs,
      include_uploads: includeUploads,
      force: forceReindex,
      timeout_seconds: timeoutSec,
    });
    startPolling();
  });

  const handleStop = () => handleAction(async () => {
    await knowledgeApi.stop();
  });

  const handlePause = () => handleAction(async () => {
    await knowledgeApi.pause();
  });

  const handleResume = () => handleAction(async () => {
    await knowledgeApi.resume();
  });

  const handleClear = () => handleAction(async () => {
    await knowledgeApi.clear();
  });

  const loadFile = async (path: string, name: string) => {
    setSelectedPath(path);
    setContentName(name);
    const res = await fetch(`${API_BASE}/knowledge/${path}`);
    const data = await res.json();
    setContent(data.content);
  };

  if (!tree) return <div className="text-gray-400">Loading...</div>;

  // Progress bar percentage
  const progressPct = progress && progress.total_chunks > 0
    ? Math.round((progress.chunks_processed / progress.total_chunks) * 100)
    : 0;

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
        {/* Reindex panel */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-200">RAG Index</h2>
            <div className="flex items-center gap-2">
              {reindexing && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  paused
                    ? "bg-yellow-900/40 text-yellow-400"
                    : "bg-blue-900/40 text-blue-400"
                }`}>
                  {paused ? "Paused" : "Indexing"}
                </span>
              )}
              {indexStatus && (
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    indexStatus.indexed
                      ? "bg-green-900/40 text-green-400"
                      : "bg-yellow-900/40 text-yellow-400"
                  }`}
                >
                  {indexStatus.indexed
                    ? `${indexStatus.total_embeddings} embeddings`
                    : "Not indexed"}
                </span>
              )}
            </div>
          </div>

          {indexStatus && indexStatus.indexed && !reindexing && (
            <div className="text-xs text-gray-400 mb-3 space-y-0.5">
              <p>{indexStatus.knowledge_file_count} knowledge files, {indexStatus.vendor_doc_count} vendor docs{indexStatus.upload_count > 0 && `, ${indexStatus.upload_count} uploads`}</p>
              {indexStatus.last_indexed_at && (
                <p>Last indexed: {new Date(indexStatus.last_indexed_at).toLocaleString()}</p>
              )}
            </div>
          )}

          {/* Progress display */}
          {reindexing && progress && (
            <div className="mb-3 p-3 bg-blue-900/20 border border-blue-800 rounded">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <div className={`h-2.5 w-2.5 rounded-full ${paused ? "bg-yellow-500" : "bg-blue-500 animate-pulse"}`} />
                  <span className="text-xs text-blue-300">
                    {PHASE_LABELS[progress.phase] || progress.phase}
                  </span>
                </div>
                <span className="text-xs text-gray-400">{elapsed}s</span>
              </div>

              {/* Progress bar */}
              {progress.phase === "embedding" && progress.total_chunks > 0 && (
                <div className="mb-1.5">
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full transition-all duration-500"
                      style={{ width: `${progressPct}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-1">
                    <span className="text-xs text-gray-400">
                      {progress.chunks_processed} / {progress.total_chunks} chunks
                    </span>
                    <span className="text-xs text-gray-400">
                      Batch {progress.current_batch} / {progress.total_batches}
                    </span>
                  </div>
                </div>
              )}

              {progress.phase === "fetching_vendor_docs" && progress.vendor_docs_total > 0 && (
                <div className="text-xs text-gray-400">
                  {progress.vendor_docs_fetched} / {progress.vendor_docs_total} vendor docs fetched
                </div>
              )}

              {progress.phase === "indexing_uploads" && progress.uploads_total > 0 && (
                <div className="text-xs text-gray-400">
                  {progress.uploads_processed} / {progress.uploads_total} uploads processed
                </div>
              )}

              {/* Live embedding count */}
              <div className="text-xs text-gray-400">
                {indexStatus?.total_embeddings ?? 0} embeddings in database
              </div>
            </div>
          )}

          {/* Controls: not running */}
          {!reindexing && (
            <>
              <div className="flex flex-col gap-2 mb-3">
                <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeVendorDocs}
                    onChange={(e) => setIncludeVendorDocs(e.target.checked)}
                    className="rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-0"
                  />
                  Include vendor docs
                </label>
                <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeUploads}
                    onChange={(e) => setIncludeUploads(e.target.checked)}
                    className="rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-0"
                  />
                  Include uploaded files
                </label>
                <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={forceReindex}
                    onChange={(e) => setForceReindex(e.target.checked)}
                    className="rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-0"
                  />
                  Force full rebuild
                </label>
                <label className="flex items-center gap-2 text-xs text-gray-300">
                  <span className="w-20">Timeout</span>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    placeholder="none"
                    value={timeoutMin}
                    onChange={(e) => setTimeoutMin(e.target.value)}
                    className="w-20 px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-gray-200 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
                  />
                  <span className="text-gray-500">minutes</span>
                </label>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleStart}
                  className="flex-1 px-3 py-2 text-sm font-medium rounded bg-blue-600 text-white hover:bg-blue-700"
                >
                  Rebuild Index
                </button>
                {indexStatus?.indexed && (
                  <button
                    onClick={handleClear}
                    className="px-3 py-2 text-sm font-medium rounded bg-red-900/40 text-red-400 hover:bg-red-900/60 border border-red-800"
                  >
                    Clear
                  </button>
                )}
              </div>
            </>
          )}

          {/* Controls: running */}
          {reindexing && (
            <div className="flex gap-2">
              {!paused ? (
                <button
                  onClick={handlePause}
                  className="flex-1 px-3 py-2 text-sm font-medium rounded bg-yellow-900/40 text-yellow-400 hover:bg-yellow-900/60 border border-yellow-800"
                >
                  Pause
                </button>
              ) : (
                <button
                  onClick={handleResume}
                  className="flex-1 px-3 py-2 text-sm font-medium rounded bg-blue-600 text-white hover:bg-blue-700"
                >
                  Resume
                </button>
              )}
              <button
                onClick={handleStop}
                className="flex-1 px-3 py-2 text-sm font-medium rounded bg-red-900/40 text-red-400 hover:bg-red-900/60 border border-red-800"
              >
                Stop
              </button>
            </div>
          )}

          {/* Last result */}
          {!reindexing && lastResult && (
            <div className="mt-3 p-2 bg-green-900/20 border border-green-800 rounded text-xs text-green-300">
              <p>
                {lastResult.status === "completed" ? "Completed" :
                 lastResult.status === "cancelled" ? "Cancelled" :
                 lastResult.status === "timed_out" ? "Timed out" :
                 lastResult.status}: {lastResult.checklist_items_indexed} items from {lastResult.files_processed} files
                {lastResult.vendor_docs_indexed > 0 && ` + ${lastResult.vendor_docs_indexed} vendor docs`}
                {lastResult.uploads_indexed > 0 && ` + ${lastResult.uploads_indexed} uploads`}
                {" "}in {lastResult.duration_seconds.toFixed(1)}s
              </p>
              {lastResult.errors.length > 0 && (
                <p className="text-yellow-400 mt-1">{lastResult.errors.length} error(s): {lastResult.errors[0]}</p>
              )}
            </div>
          )}

          {/* Errors */}
          {!reindexing && reindexError && (
            <div className="mt-3 p-2 bg-red-900/20 border border-red-800 rounded text-xs text-red-300">
              {reindexError}
            </div>
          )}
          {actionError && (
            <div className="mt-3 p-2 bg-red-900/20 border border-red-800 rounded text-xs text-red-300">
              {actionError}
            </div>
          )}
        </div>

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
