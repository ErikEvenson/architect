import { useCallback, useEffect, useRef, useState } from "react";
import type { Upload } from "../../api/types";
import { uploadsApi } from "../../api/client";

interface UploadPanelProps {
  versionId: string;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function UploadPanel({ versionId }: UploadPanelProps) {
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadUploads = useCallback(async () => {
    try {
      const data = await uploadsApi.list(versionId);
      setUploads(data);
    } catch {
      // ignore load errors
    }
  }, [versionId]);

  useEffect(() => {
    loadUploads();
  }, [loadUploads]);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setError(null);

    try {
      for (const file of Array.from(files)) {
        await uploadsApi.upload(versionId, file);
      }
      await loadUploads();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (upload: Upload) => {
    try {
      await uploadsApi.delete(versionId, upload.id);
      setUploads((prev) => prev.filter((u) => u.id !== upload.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleUpload(e.dataTransfer.files);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-300">Uploads</h3>
        <span className="text-xs text-gray-500">{uploads.length} file{uploads.length !== 1 ? "s" : ""}</span>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition ${
          dragOver
            ? "border-blue-500 bg-blue-900/20"
            : "border-gray-700 hover:border-gray-500"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => handleUpload(e.target.files)}
        />
        {uploading ? (
          <p className="text-sm text-blue-400">Uploading...</p>
        ) : (
          <p className="text-sm text-gray-400">
            Drop files here or click to upload
          </p>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-400">{error}</p>
      )}

      {/* File list */}
      {uploads.length > 0 && (
        <div className="space-y-1">
          {uploads.map((upload) => (
            <div
              key={upload.id}
              className="flex items-center justify-between p-2 rounded bg-gray-800 border border-gray-700"
            >
              <div className="flex-1 min-w-0 mr-2">
                <p className="text-sm text-gray-200 truncate">{upload.original_filename}</p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(upload.file_size)} &middot; {new Date(upload.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <a
                  href={uploadsApi.downloadUrl(versionId, upload.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-400 hover:text-blue-300"
                >
                  Download
                </a>
                <button
                  onClick={() => handleDelete(upload)}
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
