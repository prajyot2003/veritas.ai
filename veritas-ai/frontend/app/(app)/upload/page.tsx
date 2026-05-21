"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, File, X, CheckCircle, Loader2, AlertCircle, Eye, Play } from "lucide-react";
import { documentsApi, anomalyApi } from "@/lib/api";
import toast from "react-hot-toast";

interface UploadedFile {
  file: File;
  id?: string;
  status: "pending" | "uploading" | "uploaded" | "analyzing" | "done" | "error";
  preview?: string;
  result?: any;
  error?: string;
}

const ACCEPTED_TYPES = {
  "application/pdf": [".pdf"],
  "image/png": [".png"],
  "image/jpeg": [".jpg", ".jpeg"],
  "image/tiff": [".tiff"],
};

const STATUS_CONFIG = {
  pending: { label: "Ready", color: "text-muted", icon: null },
  uploading: { label: "Uploading...", color: "text-primary", icon: Loader2 },
  uploaded: { label: "Uploaded", color: "text-accent-cyan", icon: CheckCircle },
  analyzing: { label: "Analyzing...", color: "text-accent-amber", icon: Loader2 },
  done: { label: "Complete", color: "text-risk-low", icon: CheckCircle },
  error: { label: "Error", color: "text-risk-critical", icon: AlertCircle },
};

export default function UploadPage() {
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback((accepted: File[]) => {
    const newFiles = accepted.map((f) => ({
      file: f,
      status: "pending" as const,
      preview: f.type.startsWith("image/") ? URL.createObjectURL(f) : undefined,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: 50 * 1024 * 1024,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => {
      const copy = [...prev];
      if (copy[index].preview) URL.revokeObjectURL(copy[index].preview!);
      copy.splice(index, 1);
      return copy;
    });
  };

  const uploadAndAnalyze = async (index: number) => {
    const entry = files[index];
    setFiles((prev) => {
      const c = [...prev]; c[index] = { ...c[index], status: "uploading" }; return c;
    });

    try {
      // Upload
      const uploaded = await documentsApi.upload([entry.file]);
      const docId = uploaded[0]?.id;

      setFiles((prev) => {
        const c = [...prev]; c[index] = { ...c[index], status: "analyzing", id: docId }; return c;
      });

      // Trigger analysis
      await anomalyApi.analyze(docId);

      // Poll for results
      let result = null;
      for (let attempt = 0; attempt < 20; attempt++) {
        await new Promise((r) => setTimeout(r, 2000));
        try {
          result = await anomalyApi.getResult(docId);
          break;
        } catch (e: any) {
          if (e.response?.status !== 202) break;
        }
      }

      setFiles((prev) => {
        const c = [...prev]; c[index] = { ...c[index], status: "done", result }; return c;
      });
      toast.success(`Analysis complete: Fraud Score ${result?.fraud_score?.toFixed(0) ?? "N/A"}`);
    } catch (err: any) {
      setFiles((prev) => {
        const c = [...prev]; c[index] = { ...c[index], status: "error", error: err.message }; return c;
      });
      toast.error("Analysis failed");
    }
  };

  const uploadAll = async () => {
    const pending = files.map((f, i) => ({ f, i })).filter(({ f }) => f.status === "pending");
    for (const { i } of pending) {
      await uploadAndAnalyze(i);
    }
  };

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Upload Center</h1>
        <p className="text-muted text-sm mt-1">Upload documents for AI-powered fraud analysis</p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50 hover:bg-surface-2"
        }`}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={{ y: isDragActive ? -8 : 0 }}
          transition={{ duration: 0.3 }}
          className="flex flex-col items-center gap-3"
        >
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all ${
            isDragActive ? "bg-primary/20" : "bg-surface-2"
          }`}>
            <Upload className={`w-6 h-6 ${isDragActive ? "text-primary" : "text-muted"}`} />
          </div>
          <div>
            <p className="font-semibold text-foreground">
              {isDragActive ? "Drop files here" : "Drag & drop files here"}
            </p>
            <p className="text-sm text-muted mt-1">
              PDF, PNG, JPG, TIFF · Max 50MB per file
            </p>
          </div>
          <span className="px-4 py-2 rounded-lg bg-surface-2 border border-border text-sm text-muted hover:text-foreground transition-colors">
            Browse Files
          </span>
        </motion.div>
      </div>

      {/* File list */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-foreground">{files.length} file(s) selected</p>
              <button
                onClick={uploadAll}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all"
                style={{ background: "linear-gradient(135deg, hsl(213,94%,50%), hsl(213,94%,40%))", boxShadow: "0 4px 20px hsl(213,94%,55%,0.3)" }}
              >
                <Play className="w-4 h-4" />
                Analyze All
              </button>
            </div>

            <div className="space-y-3">
              {files.map((entry, i) => {
                const cfg = STATUS_CONFIG[entry.status];
                const Icon = cfg.icon;
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: i * 0.05 }}
                    className="glass-card rounded-xl p-4 flex items-center gap-4"
                  >
                    {/* Preview / icon */}
                    <div className="shrink-0 w-12 h-12 rounded-lg overflow-hidden bg-surface-2 flex items-center justify-center">
                      {entry.preview ? (
                        <img src={entry.preview} alt="preview" className="w-full h-full object-cover" />
                      ) : (
                        <File className="w-5 h-5 text-muted" />
                      )}
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-foreground truncate">{entry.file.name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-muted">
                          {(entry.file.size / 1024).toFixed(0)} KB · {entry.file.type || "unknown"}
                        </span>
                        <span className={`text-xs font-semibold flex items-center gap-1 ${cfg.color}`}>
                          {Icon && <Icon className={`w-3 h-3 ${entry.status === "uploading" || entry.status === "analyzing" ? "animate-spin" : ""}`} />}
                          {cfg.label}
                        </span>
                      </div>

                      {/* Result preview */}
                      {entry.result && (
                        <div className="flex items-center gap-3 mt-2">
                          <span className="text-xs">
                            Fraud: <strong className="text-risk-critical">{entry.result.fraud_score?.toFixed(0)}</strong>
                          </span>
                          <span className="text-xs">
                            Trust: <strong className="text-risk-low">{entry.result.trust_score?.toFixed(0)}</strong>
                          </span>
                          <span className={`text-xs badge-${entry.result.risk_level} px-1.5 py-0.5 rounded-full`}>
                            {entry.result.risk_level?.toUpperCase()}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 shrink-0">
                      {entry.status === "pending" && (
                        <button
                          onClick={() => uploadAndAnalyze(i)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-primary/20 text-primary hover:bg-primary/30 transition-colors"
                        >
                          Analyze
                        </button>
                      )}
                      <button
                        onClick={() => removeFile(i)}
                        className="w-7 h-7 rounded-lg flex items-center justify-center text-muted hover:text-risk-critical hover:bg-risk-critical/10 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
