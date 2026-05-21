"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, XCircle, RefreshCw, ChevronRight } from "lucide-react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell, CartesianGrid
} from "recharts";
import { riskApi, documentsApi, anomalyApi } from "@/lib/api";

const DECISION_CONFIG: Record<string, { icon: any; color: string; label: string; bg: string }> = {
  approve: { icon: CheckCircle, color: "text-risk-low", label: "APPROVED", bg: "bg-risk-low/10 border-risk-low/30" },
  review:  { icon: AlertTriangle, color: "text-accent-amber", label: "REVIEW REQUIRED", bg: "bg-accent-amber/10 border-accent-amber/30" },
  reject:  { icon: XCircle, color: "text-risk-critical", label: "REJECTED", bg: "bg-risk-critical/10 border-risk-critical/30" },
};

const RADAR_DATA = [
  { subject: "KYC Integrity", A: 85 },
  { subject: "Collateral", A: 42 },
  { subject: "Financials", A: 70 },
  { subject: "Ownership", A: 55 },
  { subject: "History", A: 78 },
  { subject: "Compliance", A: 60 },
];

export default function RiskPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [underwriting, setUnderwriting] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uwLoading, setUwLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docs, alertData] = await Promise.all([
          documentsApi.list(),
          riskApi.getAlerts(),
        ]);
        setDocuments(docs.filter((d: any) => d.fraud_score !== null));
        setAlerts(alertData);
      } catch {
        const demoDocuments = [
          { id: "doc_001", filename: "land_record_tampered.pdf", fraud_score: 82.4, trust_score: 17.6, risk_level: "critical" },
          { id: "doc_002", filename: "kyc_rajesh_kumar.pdf", fraud_score: 41.2, trust_score: 58.8, risk_level: "high" },
          { id: "doc_003", filename: "financial_statement.pdf", fraud_score: 18.5, trust_score: 81.5, risk_level: "low" },
        ];
        setDocuments(demoDocuments);
        setAlerts([
          { id: "a1", type: "duplicate_collateral", severity: "critical", description: "Duplicate collateral mortgage on Plot No. 47" },
          { id: "a2", type: "metadata_tamper", severity: "high", description: "PDF metadata modification detected" },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const fetchUnderwriting = async (doc: any) => {
    setSelected(doc);
    setUnderwriting(null);
    setUwLoading(true);
    try {
      const uw = await riskApi.getUnderwriting(doc.id);
      setUnderwriting(uw);
    } catch {
      // Demo
      const score = doc.fraud_score;
      setUnderwriting({
        document_id: doc.id,
        decision: score > 70 ? "reject" : score > 40 ? "review" : "approve",
        confidence: 0.87,
        risk_score: score,
        explanation: score > 70
          ? "High underwriting risk detected due to ownership inconsistency and abnormal financial patterns. Document exhibits critical anomalies including metadata tampering and suspicious edit markers. Loan disbursement not recommended without complete re-verification."
          : score > 40
          ? "Moderate risk indicators require additional scrutiny. Financial data shows minor inconsistencies. Manual review of collateral ownership documentation is strongly recommended."
          : "Low risk profile. Document appears authentic with acceptable financial ratios. Proceed with standard underwriting protocol.",
        key_factors: score > 70
          ? ["Critical fraud indicators", "Ownership mismatch detected", "Metadata tampering found", "Suspicious edit markers"]
          : score > 40
          ? ["Moderate anomaly signals", "Date inconsistency noted", "Manual review required"]
          : ["Clean fraud indicators", "Valid KYC documentation", "Consistent financials"],
        recommendations: score > 70
          ? ["Escalate to fraud team", "Do not disburse", "File SAR with FIU-IND"]
          : score > 40
          ? ["Request additional KYC", "Verify with registry", "Cross-check IT returns"]
          : ["Proceed with standard processing", "Retain records 5 years"],
      });
    } finally {
      setUwLoading(false);
    }
  };

  const decisionCfg = underwriting ? DECISION_CONFIG[underwriting.decision] : null;

  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Risk Analysis</h1>
        <p className="text-muted text-sm mt-1">AI-powered underwriting intelligence · Explainable risk decisions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document selector */}
        <div className="space-y-3">
          <h3 className="text-xs text-muted uppercase tracking-wider font-semibold">Analyzed Documents</h3>
          {loading
            ? Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton h-16 rounded-xl" />)
            : documents.map((doc, i) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, x: -15 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  onClick={() => fetchUnderwriting(doc)}
                  className={`glass-card rounded-xl p-4 cursor-pointer transition-all ${
                    selected?.id === doc.id ? "border-primary/50 glow-primary" : "hover:border-border-light"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-foreground truncate">{doc.filename}</p>
                    <ChevronRight className="w-4 h-4 text-muted shrink-0 ml-2" />
                  </div>
                  <div className="flex items-center gap-2 mt-2 text-xs">
                    <span className="text-risk-critical font-semibold">Fraud: {doc.fraud_score?.toFixed(0)}</span>
                    <span className="text-muted">·</span>
                    <span className="text-risk-low font-semibold">Trust: {doc.trust_score?.toFixed(0)}</span>
                  </div>
                </motion.div>
              ))}

          {/* Radar chart */}
          <div className="glass-card rounded-xl p-4 mt-4">
            <h3 className="text-xs text-muted uppercase tracking-wider font-semibold mb-3">Risk Dimensions</h3>
            <ResponsiveContainer width="100%" height={160}>
              <RadarChart data={RADAR_DATA}>
                <PolarGrid stroke="hsl(220,12%,22%)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: "hsl(220,10%,50%)", fontSize: 9 }} />
                <Radar dataKey="A" stroke="hsl(213,94%,55%)" fill="hsl(213,94%,55%)" fillOpacity={0.2} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Underwriting panel */}
        <div className="lg:col-span-2">
          {!selected ? (
            <div className="glass-card rounded-xl h-full flex items-center justify-center p-12">
              <div className="text-center space-y-3">
                <BarChart3 className="w-12 h-12 text-muted mx-auto" />
                <p className="font-semibold text-foreground">Select a document</p>
                <p className="text-sm text-muted">Choose a document to view its underwriting decision</p>
              </div>
            </div>
          ) : (
            <motion.div
              key={selected.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {uwLoading ? (
                <div className="glass-card rounded-xl p-8 flex items-center justify-center gap-3">
                  <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  <p className="text-muted text-sm">Generating underwriting decision...</p>
                </div>
              ) : underwriting && decisionCfg && (
                <>
                  {/* Decision banner */}
                  <div className={`glass-card rounded-xl p-5 border ${decisionCfg.bg}`}>
                    <div className="flex items-center gap-3">
                      <decisionCfg.icon className={`w-8 h-8 ${decisionCfg.color}`} />
                      <div>
                        <p className={`text-xl font-bold ${decisionCfg.color}`}>{decisionCfg.label}</p>
                        <p className="text-sm text-muted">
                          Confidence: {(underwriting.confidence * 100).toFixed(0)}% ·
                          Risk Score: {underwriting.risk_score?.toFixed(1)}/100
                        </p>
                      </div>
                    </div>
                    <p className="text-sm text-foreground mt-4 leading-relaxed">{underwriting.explanation}</p>
                  </div>

                  {/* Key factors + Recommendations */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="glass-card rounded-xl p-4">
                      <h3 className="text-xs text-muted uppercase tracking-wider font-semibold mb-3">Key Risk Factors</h3>
                      <ul className="space-y-2">
                        {underwriting.key_factors?.map((f: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                            <AlertTriangle className="w-3 h-3 text-accent-amber shrink-0 mt-0.5" />
                            {f}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="glass-card rounded-xl p-4">
                      <h3 className="text-xs text-muted uppercase tracking-wider font-semibold mb-3">Recommendations</h3>
                      <ul className="space-y-2">
                        {underwriting.recommendations?.map((r: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                            <ChevronRight className="w-3 h-3 text-primary shrink-0 mt-0.5" />
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Alert list */}
                  {alerts.length > 0 && (
                    <div className="glass-card rounded-xl p-4">
                      <h3 className="text-xs text-muted uppercase tracking-wider font-semibold mb-3">Active Risk Alerts</h3>
                      <div className="space-y-2">
                        {alerts.slice(0, 4).map((a, i) => (
                          <div key={a.id} className="flex items-center gap-3 p-2 rounded-lg bg-surface-2">
                            <AlertTriangle className="w-4 h-4 text-risk-critical shrink-0" />
                            <p className="text-xs text-foreground">{a.description}</p>
                            <span className={`ml-auto badge-${a.severity} text-xs px-2 py-0.5 rounded-full shrink-0`}>
                              {a.severity?.toUpperCase()}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
