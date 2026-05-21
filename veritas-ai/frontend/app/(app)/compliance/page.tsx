"use client";

import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle, Clock, XCircle, AlertTriangle, Upload,
  FileCheck, Loader2, ChevronRight, RefreshCw
} from "lucide-react";
import { complianceApi } from "@/lib/api";
import toast from "react-hot-toast";

const STATUS_CONFIG: Record<string, { icon: any; color: string; label: string }> = {
  compliant:    { icon: CheckCircle, color: "text-risk-low",      label: "Compliant" },
  non_compliant:{ icon: XCircle,     color: "text-risk-critical",  label: "Non-Compliant" },
  pending:      { icon: Clock,        color: "text-muted",          label: "Pending" },
  under_review: { icon: AlertTriangle,color: "text-accent-amber",   label: "Under Review" },
};

const PRIORITY_BADGE: Record<string, string> = {
  low: "badge-low", medium: "badge-medium", high: "badge-high", critical: "badge-critical",
};

export default function CompliancePage() {
  const [maps, setMaps] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [selected, setSelected] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchData = async () => {
    try {
      const [mapsData, summaryData] = await Promise.all([
        complianceApi.getMaps(),
        complianceApi.getSummary(),
      ]);
      setMaps(mapsData);
      setSummary(summaryData);
    } catch {
      const demo = [
        {
          id: "map_001",
          title: "Update KYC Retention Policy",
          description: "Ensure KYC documents retained for 5+ years per RBI directive.",
          regulation_ref: "RBI/2023-24/10",
          status: "pending",
          priority: "high",
          evidence_uploaded: false,
          due_date: new Date(Date.now() + 30 * 86400000).toISOString(),
        },
        {
          id: "map_002",
          title: "Verify Collateral Ownership",
          description: "Cross-verify collateral with government land registry.",
          regulation_ref: "RBI RPCD Circular",
          status: "under_review",
          priority: "critical",
          evidence_uploaded: true,
          due_date: new Date(Date.now() + 7 * 86400000).toISOString(),
        },
        {
          id: "map_003",
          title: "Upload Q3 Compliance Evidence",
          description: "Submit SEBI LODR quarterly compliance documentation.",
          regulation_ref: "SEBI LODR Reg. 27",
          status: "compliant",
          priority: "medium",
          evidence_uploaded: true,
          due_date: new Date(Date.now() - 5 * 86400000).toISOString(),
        },
        {
          id: "map_004",
          title: "Beneficial Ownership Audit",
          description: "Identify beneficial owners holding >25% per PMLA 2002.",
          regulation_ref: "PMLA 2002 Sec. 12A",
          status: "non_compliant",
          priority: "critical",
          evidence_uploaded: false,
          due_date: new Date(Date.now() + 7 * 86400000).toISOString(),
        },
      ];
      setMaps(demo);
      setSummary({ total: demo.length, compliant: 1, non_compliant: 1, pending: 1, under_review: 1, compliance_rate: 25, critical_pending: 2 });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleValidate = async (file?: File) => {
    if (!selected) return;
    setValidating(true);
    setValidationResult(null);
    try {
      const result = await complianceApi.validate(selected.id, file);
      setValidationResult(result);
      if (result.is_valid) {
        toast.success("Compliance evidence validated!");
        fetchData();
      } else {
        toast.error("Validation failed — see suggestions");
      }
    } catch {
      toast.error("Validation request failed");
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="p-6 max-w-[1400px] space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Compliance Center</h1>
          <p className="text-muted text-sm mt-1">Measurable Action Points · Regulatory Intelligence · AI Validation</p>
        </div>
        <button onClick={fetchData} className="p-2 rounded-lg hover:bg-surface-2 text-muted hover:text-foreground transition-colors">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {[
            { label: "Total MAPs", value: summary.total, color: "text-foreground" },
            { label: "Compliant", value: summary.compliant, color: "text-risk-low" },
            { label: "Non-Compliant", value: summary.non_compliant, color: "text-risk-critical" },
            { label: "Pending", value: summary.pending, color: "text-muted" },
            { label: "Rate", value: `${summary.compliance_rate}%`, color: "text-primary" },
          ].map((s) => (
            <div key={s.label} className="glass-card rounded-xl p-4 text-center">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-muted mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-6">
        {/* MAPs list */}
        <div className="w-96 shrink-0 space-y-2 overflow-y-auto">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)
            : maps.map((map, i) => {
                const cfg = STATUS_CONFIG[map.status] || STATUS_CONFIG.pending;
                const Icon = cfg.icon;
                return (
                  <motion.div
                    key={map.id}
                    initial={{ opacity: 0, x: -15 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    onClick={() => { setSelected(map); setValidationResult(null); }}
                    className={`glass-card rounded-xl p-4 cursor-pointer transition-all ${
                      selected?.id === map.id ? "border-primary/50 glow-primary" : "hover:border-border-light"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${cfg.color}`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-foreground">{map.title}</p>
                        <p className="text-xs text-muted mt-0.5 truncate">{map.regulation_ref}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`text-xs ${PRIORITY_BADGE[map.priority] || "badge-medium"} px-1.5 py-0.5 rounded-full`}>
                            {map.priority.toUpperCase()}
                          </span>
                          <span className={`text-xs ${cfg.color} font-medium`}>{cfg.label}</span>
                          {map.evidence_uploaded && <FileCheck className="w-3 h-3 text-risk-low" />}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
        </div>

        {/* MAP detail */}
        <div className="flex-1 glass-card rounded-xl p-6 overflow-y-auto">
          {!selected ? (
            <div className="h-full flex flex-col items-center justify-center gap-4 text-center">
              <FileCheck className="w-12 h-12 text-muted" />
              <div>
                <p className="font-semibold text-foreground">Select a Compliance Action</p>
                <p className="text-muted text-sm">Choose a MAP from the list to view details and validate evidence</p>
              </div>
            </div>
          ) : (
            <motion.div
              key={selected.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-foreground">{selected.title}</h2>
                  <p className="text-sm text-muted mt-1">{selected.regulation_ref}</p>
                </div>
                <span className={`${PRIORITY_BADGE[selected.priority]} px-3 py-1 rounded-full text-sm font-bold`}>
                  {selected.priority.toUpperCase()}
                </span>
              </div>

              <p className="text-sm text-foreground leading-relaxed bg-surface-2 rounded-xl p-4">
                {selected.description}
              </p>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-surface-2 rounded-xl p-3">
                  <p className="text-xs text-muted">Status</p>
                  <p className={`font-semibold mt-1 ${STATUS_CONFIG[selected.status]?.color || "text-foreground"}`}>
                    {STATUS_CONFIG[selected.status]?.label}
                  </p>
                </div>
                <div className="bg-surface-2 rounded-xl p-3">
                  <p className="text-xs text-muted">Evidence</p>
                  <p className={`font-semibold mt-1 ${selected.evidence_uploaded ? "text-risk-low" : "text-risk-critical"}`}>
                    {selected.evidence_uploaded ? "Uploaded ✓" : "Not uploaded"}
                  </p>
                </div>
              </div>

              {/* Upload evidence */}
              <div>
                <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">Upload Compliance Evidence</h3>
                <input ref={fileRef} type="file" className="hidden" onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleValidate(f);
                }} />
                <div className="flex gap-3">
                  <button
                    onClick={() => fileRef.current?.click()}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold bg-surface-2 border border-border text-foreground hover:border-primary transition-all"
                  >
                    <Upload className="w-4 h-4" />
                    Upload File
                  </button>
                  <button
                    onClick={() => handleValidate()}
                    disabled={validating}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all disabled:opacity-60"
                    style={{ background: "linear-gradient(135deg, hsl(213,94%,50%), hsl(213,94%,40%))" }}
                  >
                    {validating ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                    {validating ? "Validating..." : "AI Validate"}
                  </button>
                </div>
              </div>

              {/* Validation result */}
              {validationResult && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`rounded-xl p-4 border ${
                    validationResult.is_valid
                      ? "bg-risk-low/10 border-risk-low/30"
                      : "bg-risk-critical/10 border-risk-critical/30"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {validationResult.is_valid
                      ? <CheckCircle className="w-4 h-4 text-risk-low" />
                      : <XCircle className="w-4 h-4 text-risk-critical" />}
                    <p className={`font-semibold text-sm ${validationResult.is_valid ? "text-risk-low" : "text-risk-critical"}`}>
                      {validationResult.is_valid ? "Compliance Validated" : "Validation Failed"}
                      {" "}· Confidence: {(validationResult.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                  <p className="text-sm text-foreground">{validationResult.reasoning}</p>
                  {validationResult.suggestions?.length > 0 && (
                    <ul className="mt-3 space-y-1">
                      {validationResult.suggestions.map((s: string, i: number) => (
                        <li key={i} className="text-xs text-muted flex items-center gap-2">
                          <ChevronRight className="w-3 h-3 shrink-0" /> {s}
                        </li>
                      ))}
                    </ul>
                  )}
                </motion.div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
