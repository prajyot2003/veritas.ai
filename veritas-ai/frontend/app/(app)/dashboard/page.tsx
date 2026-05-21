"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle, Shield, TrendingUp, FileText,
  CheckCircle, XCircle, Clock, Zap, Activity
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Cell
} from "recharts";
import { riskApi } from "@/lib/api";
import { FraudRiskMeter } from "@/components/dashboard/FraudRiskMeter";
import { TrustScoreCard } from "@/components/dashboard/TrustScoreCard";
import { AlertFeed } from "@/components/dashboard/AlertFeed";

const RISK_COLORS: Record<string, string> = {
  low: "hsl(160, 84%, 45%)",
  medium: "hsl(38, 92%, 55%)",
  high: "hsl(25, 95%, 55%)",
  critical: "hsl(350, 89%, 60%)",
};

function StatCard({ title, value, subtitle, icon: Icon, color, delta }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-xl p-5 relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-5"
        style={{ background: color, filter: "blur(20px)", transform: "translate(30%, -30%)" }} />
      <div className="flex items-start justify-between mb-3">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center"
          style={{ background: `${color}20`, border: `1px solid ${color}30` }}>
          <Icon className="w-4 h-4" style={{ color }} />
        </div>
        {delta !== undefined && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
            delta >= 0 ? "bg-risk-low/15 text-risk-low" : "bg-risk-critical/15 text-risk-critical"
          }`}>
            {delta >= 0 ? "+" : ""}{delta}%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="text-sm font-medium text-foreground mt-0.5">{title}</p>
      {subtitle && <p className="text-xs text-muted mt-1">{subtitle}</p>}
    </motion.div>
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div className="custom-tooltip">
        <p className="font-semibold mb-1">{label}</p>
        {payload.map((p: any, i: number) => (
          <p key={i} style={{ color: p.color }}>{p.name}: {p.value}</p>
        ))}
      </div>
    );
  }
  return null;
};

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await riskApi.getDashboard();
        setMetrics(data);
      } catch {
        // Use demo data
        setMetrics({
          total_documents: 47,
          flagged_documents: 12,
          average_fraud_score: 38.4,
          average_trust_score: 61.6,
          compliance_rate: 60.0,
          active_maps: 5,
          critical_alerts: 3,
          risk_distribution: { low: 18, medium: 12, high: 11, critical: 6 },
          recent_alerts: [
            { id: "a1", title: "Duplicate Collateral Detected", severity: "critical", description: "Plot No. 47 mortgaged to 2 banks", created_at: new Date().toISOString() },
            { id: "a2", title: "Metadata Tampering", severity: "high", description: "PDF modified after creation", created_at: new Date().toISOString() },
            { id: "a3", title: "Suspicious Ownership Transfer", severity: "high", description: "3 transfers within 30 days", created_at: new Date().toISOString() },
          ],
          trend_data: Array.from({ length: 7 }, (_, i) => ({
            day: `Day ${i + 1}`,
            fraud_score: Math.round(20 + Math.random() * 60),
            trust_score: Math.round(40 + Math.random() * 50),
            documents: Math.round(1 + Math.random() * 12),
          })),
        });
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="skeleton h-24 rounded-xl" />
        ))}
      </div>
    );
  }

  const riskDistData = Object.entries(metrics.risk_distribution).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
    color: RISK_COLORS[k],
  }));

  return (
    <div className="p-6 space-y-6 max-w-[1600px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Risk Intelligence Dashboard</h1>
          <p className="text-muted text-sm mt-1">Real-time fraud monitoring & compliance overview</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-2 border border-border text-xs text-muted">
          <div className="pulse-dot w-2 h-2" />
          Live · Updated just now
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Documents" value={metrics.total_documents} subtitle="Across all cases"
          icon={FileText} color="hsl(213,94%,55%)" delta={12} />
        <StatCard title="Flagged Documents" value={metrics.flagged_documents} subtitle="Requiring review"
          icon={AlertTriangle} color="hsl(350,89%,60%)" delta={-4} />
        <StatCard title="Compliance Rate" value={`${metrics.compliance_rate}%`} subtitle="MAPs resolved"
          icon={CheckCircle} color="hsl(160,84%,45%)" delta={5} />
        <StatCard title="Critical Alerts" value={metrics.critical_alerts} subtitle="Need immediate action"
          icon={Zap} color="hsl(38,92%,55%)" delta={null} />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Fraud + Trust Meters */}
        <div className="glass-card rounded-xl p-5 flex flex-col gap-4">
          <h3 className="text-sm font-semibold text-muted uppercase tracking-wider">Risk Gauges</h3>
          <FraudRiskMeter score={metrics.average_fraud_score} />
          <TrustScoreCard score={metrics.average_trust_score} />
        </div>

        {/* Trend chart */}
        <div className="lg:col-span-2 glass-card rounded-xl p-5">
          <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-4">7-Day Risk Trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={metrics.trend_data}>
              <defs>
                <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(350,89%,60%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(350,89%,60%)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="trustGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(160,84%,45%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(160,84%,45%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,12%,18%)" />
              <XAxis dataKey="day" tick={{ fill: "hsl(220,10%,50%)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "hsl(220,10%,50%)", fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 100]} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="fraud_score" name="Fraud Score" stroke="hsl(350,89%,60%)" fill="url(#fraudGrad)" strokeWidth={2} />
              <Area type="monotone" dataKey="trust_score" name="Trust Score" stroke="hsl(160,84%,45%)" fill="url(#trustGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk distribution */}
        <div className="glass-card rounded-xl p-5">
          <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={riskDistData} barSize={28}>
              <XAxis dataKey="name" tick={{ fill: "hsl(220,10%,50%)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "hsl(220,10%,50%)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {riskDistData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Alert feed */}
        <div className="lg:col-span-2">
          <AlertFeed alerts={metrics.recent_alerts} />
        </div>
      </div>
    </div>
  );
}
