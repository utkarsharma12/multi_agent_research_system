"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { uploadDocument } from "@/services/api";
import { useResearchStore } from "@/store/researchStore";
import { Upload, FileText, CheckCircle2, AlertCircle, X, Loader2 } from "lucide-react";

interface UploadZoneProps {
  onClose?: () => void;
}

interface UploadStatus {
  file: File;
  status: "uploading" | "done" | "error";
  error?: string;
}

const UploadZone: React.FC<UploadZoneProps> = ({ onClose }) => {
  const { addDocument } = useResearchStore();
  const [uploads, setUploads] = useState<UploadStatus[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const newUploads: UploadStatus[] = acceptedFiles.map((f) => ({
        file: f,
        status: "uploading",
      }));
      setUploads((prev) => [...prev, ...newUploads]);

      for (const file of acceptedFiles) {
        try {
          const doc = await uploadDocument(file);
          addDocument(doc);
          setUploads((prev) =>
            prev.map((u) =>
              u.file === file ? { ...u, status: "done" } : u
            )
          );
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : "Upload failed";
          setUploads((prev) =>
            prev.map((u) =>
              u.file === file ? { ...u, status: "error", error: msg } : u
            )
          );
        }
      }
    },
    [addDocument]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const formatBytes = (b: number) => {
    if (b < 1024) return `${b} B`;
    if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
    return `${(b / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="glass-bright rounded-2xl p-6 fade-in-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="font-bold text-slate-200 text-lg">Upload Documents</h3>
          <p className="text-sm text-slate-500 mt-0.5">
            PDF files will be indexed for RAG search
          </p>
        </div>
        {onClose && (
          <button onClick={onClose} className="btn-ghost p-2 rounded-lg">
            <X size={16} />
          </button>
        )}
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? "border-indigo-500 bg-indigo-500/10 scale-[1.01]"
            : "border-slate-700 hover:border-indigo-500/50 hover:bg-indigo-500/5"
        }`}
      >
        <input {...getInputProps()} />
        <div
          className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
          style={{
            background: isDragActive
              ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
              : "rgba(99,102,241,0.1)",
            border: "1px solid rgba(99,102,241,0.3)",
          }}
        >
          <Upload
            size={24}
            className={isDragActive ? "text-white" : "text-indigo-400"}
          />
        </div>
        {isDragActive ? (
          <p className="text-indigo-400 font-semibold">Drop PDFs here…</p>
        ) : (
          <>
            <p className="text-slate-300 font-semibold">
              Drag & drop PDFs here
            </p>
            <p className="text-slate-600 text-sm mt-1">
              or click to browse · Max 50MB per file
            </p>
          </>
        )}
      </div>

      {/* Upload list */}
      {uploads.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploads.map((u, i) => (
            <div
              key={i}
              className={`flex items-center gap-3 p-3 rounded-xl border transition-colors ${
                u.status === "done"
                  ? "bg-green-500/5 border-green-500/20"
                  : u.status === "error"
                  ? "bg-red-500/5 border-red-500/20"
                  : "bg-indigo-500/5 border-indigo-500/20"
              }`}
            >
              <FileText size={16} className="text-slate-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-300 truncate">{u.file.name}</p>
                <p className="text-xs text-slate-600">
                  {formatBytes(u.file.size)}
                  {u.error && (
                    <span className="text-red-400 ml-2">{u.error}</span>
                  )}
                </p>
              </div>
              {u.status === "uploading" && (
                <Loader2 size={14} className="animate-spin text-indigo-400" />
              )}
              {u.status === "done" && (
                <CheckCircle2 size={14} className="text-green-400" />
              )}
              {u.status === "error" && (
                <AlertCircle size={14} className="text-red-400" />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UploadZone;
