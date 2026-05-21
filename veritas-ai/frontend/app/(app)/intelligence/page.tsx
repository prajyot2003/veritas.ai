"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FileText, AlertTriangle, CheckCircle, Eye, RefreshCw, ChevronRight } from "lucide-react";
import { documentsApi, anomalyApi } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

const RISK_BADGE = {
  low: "badge-low",
  medium: "badge-medium",
  high: "badge-high",
  critical: "badge-critical",
};

export default function IntelligencePage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docs, anomalies] = await Promise.all([
          documentsApi.list(),
          anomalyApi.listResults(),
        ]);
        setDocuments(docs);
        setResults(anomalies);
      } catch {
        // Demo data
        const demo = [
          {
            id: "doc_001",
            filename: "land_record_tampered.pdf",
            fraud_score: 82.4,
            trust_score: 17.6,
            risk_level: "critical",
            status: "flagged",
            created_at: new Date().toISOString(),
            anomaly_flags: ["metadata_modification_detected", "suspicious_edit_marker", "ownership_complexity"],
          },
          {
            id: "doc_002",
            filename: "kyc_rajesh_kumar.pdf",
            fraud_score: 41.2,
            trust_score: 58.8,
            risk_level: "high",
            status: "analyzed",
            created_at: new Date(Date.now() - 3600000).toISOString(),
            anomaly_flags: ["date_inconsistency", "ml_anomaly_detected"],
          },
          {
            id: "doc_003",
            filename: "financial_statement_q3.pdf",
            fraud_score: 18.5,
            trust_score: 81.5,
            risk_level: "low",
            status: "analyzed",
            created_at: new Date(Date.now() - 86400000).toISOString(),
            anomaly_flags: [],
          },
        ];
        setDocuments(demo);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="p-6 h-screen flex flex-col gap-6 max-w-[1400px]">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Document Intelligence</h1>
        <p className="text-muted text-sm mt-1">OCR extraction, anomaly detection, and forgery analysis</p>
      </div>

      <div className="flex gap-6 flex-1 overflow-hidden">
        {/* Document list */}
        <div className="w-80 shrink-0 space-y-2 overflow-y-auto pr-2">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)
            : documents.map((doc, i) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                  onClick={() => setSelected(doc)}
                  className={`glass-card rounded-xl p-4 cursor-pointer transition-all ${
                    selected?.id === doc.id ? "border-primary/50 glow-primary" : "hover:border-border-light"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-muted shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-foreground truncate">{doc.filename}</p>
                      <p className="text-xs text-muted mt-0.5">
                        {formatDistanceToNow(new Date(doc.created_at), { addSuffix: true })}
                      </p>
                      {doc.fraud_score !== null && doc.fraud_score !== undefined && (
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-xs">Fraud: <strong className="text-risk-critical">{doc.fraud_score?.toFixed(0)}</strong></span>
                          {doc.risk_level && (
                            <span className={`text-xs ${RISK_BADGE[doc.risk_level as keyof typeof RISK_BADGE] || "badge-medium"} px-1.5 py-0.5 rounded-full`}>
                              {doc.risk_level.toUpperCase()}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted shrink-0" />
                  </div>
                </motion.div>
              ))}
        </div>

        {/* Detail panel */}
        <div className="flex-1 glass-card rounded-xl p-6 overflow-y-auto">
          {!selected ? (
            <div className="h-full flex flex-col items-center justify-center text-center gap-4">
              <Eye className="w-12 h-12 text-muted" />
              <div>
                <p className="font-semibold text-foreground">Select a document</p>
                <p className="text-muted text-sm">Click a document on the left to view its analysis</p>
              </div>
            </div>
          ) : (
            <motion.div
              key={selected.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Header */}
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-foreground">{selected.filename}</h2>
                  <p className="text-sm text-muted">{selected.id}</p>
                </div>
                <span className={`${RISK_BADGE[selected.risk_level as keyof typeof RISK_BADGE] || "badge-medium"} px-3 py-1 rounded-full text-sm font-bold`}>
                  {(selected.risk_level || "UNKNOWN").toUpperCase()} RISK
                </span>
              </div>

              {/* Score row */}
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: "Fraud Score", value: `${selected.fraud_score?.toFixed(0) ?? "—"}/100`, color: "text-risk-critical" },
                  { label: "Trust Score", value: `${selected.trust_score?.toFixed(0) ?? "—"}/100`, color: "text-risk-low" },
                  { label: "Anomaly Flags", value: selected.anomaly_flags?.length ?? 0, color: "text-accent-amber" },
                ].map((m) => (
                  <div key={m.label} className="bg-surface-2 rounded-xl p-4 text-center">
                    <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
                    <p className="text-xs text-muted mt-1">{m.label}</p>
                  </div>
                ))}
              </div>

              {/* Anomaly flags */}
              {selected.anomaly_flags?.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">Anomaly Flags</h3>
                  <div className="space-y-2">
                    {selected.anomaly_flags.map((flag: string, i: number) => (
                      <motion.div
                        key={flag}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.06 }}
                        className="flex items-center gap-3 p-3 rounded-lg bg-risk-critical/5 border border-risk-critical/20"
                      >
                        <AlertTriangle className="w-4 h-4 text-risk-critical shrink-0" />
                        <span className="text-sm text-foreground font-mono">
                          {flag.replace(/_/g, " ")}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {/* AI explanation placeholder */}
              {selected.fraud_score !== undefined && (
                <div className="bg-surface-2 rounded-xl p-4 border border-border">
                  <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-2">AI Reasoning</h3>
                  <p className="text-sm text-foreground leading-relaxed">
                    {selected.fraud_score > 70
                      ? `⚠️ HIGH RISK — Fraud Score: ${selected.fraud_score?.toFixed(0)}/100. Document exhibits ${selected.anomaly_flags?.length || 0} critical anomaly indicators. Immediate investigation recommended. Do not approve pending manual review.`
                      : selected.fraud_score > 40
                      ? `🔍 MODERATE RISK — Fraud Score: ${selected.fraud_score?.toFixed(0)}/100. Suspicious patterns detected requiring additional verification before proceeding.`
                      : `✅ LOW RISK — Fraud Score: ${selected.fraud_score?.toFixed(0)}/100. Document appears authentic. Proceed with standard verification.`}
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
