"use client";

import { motion } from "framer-motion";
import { AlertTriangle, XCircle, AlertCircle, Info } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

const SEVERITY_CONFIG: Record<string, { icon: any; color: string; bg: string }> = {
  critical: { icon: XCircle, color: "hsl(350,89%,60%)", bg: "hsl(350,89%,60%,0.1)" },
  high: { icon: AlertTriangle, color: "hsl(25,95%,55%)", bg: "hsl(25,95%,55%,0.1)" },
  medium: { icon: AlertCircle, color: "hsl(38,92%,55%)", bg: "hsl(38,92%,55%,0.1)" },
  low: { icon: Info, color: "hsl(160,84%,45%)", bg: "hsl(160,84%,45%,0.1)" },
};

interface Alert {
  id: string;
  title: string;
  description: string;
  severity: string;
  created_at: string;
}

export function AlertFeed({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="glass-card rounded-xl p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-muted uppercase tracking-wider">Recent Alerts</h3>
        <div className="flex items-center gap-1.5">
          <div className="pulse-dot" />
          <span className="text-xs text-accent-emerald">Live</span>
        </div>
      </div>

      <div className="space-y-2 overflow-y-auto max-h-64">
        {alerts.length === 0 && (
          <p className="text-center text-muted text-sm py-8">No alerts at this time</p>
        )}
        {alerts.map((alert, i) => {
          const cfg = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.medium;
          const Icon = cfg.icon;
          return (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="flex items-start gap-3 p-3 rounded-lg transition-colors hover:bg-surface-2 cursor-default"
              style={{ background: cfg.bg, border: `1px solid ${cfg.color}20` }}
            >
              <Icon className="w-4 h-4 mt-0.5 shrink-0" style={{ color: cfg.color }} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-foreground truncate">{alert.title}</p>
                <p className="text-xs text-muted truncate mt-0.5">{alert.description}</p>
              </div>
              <div className="shrink-0 text-right">
                <span className={`text-xs font-bold badge-${alert.severity} px-1.5 py-0.5 rounded-full`}>
                  {alert.severity.toUpperCase()}
                </span>
                <p className="text-xs text-muted mt-1">
                  {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
