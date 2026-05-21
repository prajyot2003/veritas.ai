"use client";

import { motion } from "framer-motion";
import { Shield } from "lucide-react";

interface TrustScoreCardProps {
  score: number;
}

export function TrustScoreCard({ score }: TrustScoreCardProps) {
  const clamped = Math.min(100, Math.max(0, score));
  const color =
    clamped >= 70 ? "hsl(160,84%,45%)" :
    clamped >= 50 ? "hsl(38,92%,55%)" :
    "hsl(350,89%,60%)";

  const label =
    clamped >= 70 ? "HIGH TRUST" :
    clamped >= 50 ? "MODERATE TRUST" : "LOW TRUST";

  return (
    <div className="flex flex-col items-center">
      <p className="text-xs text-muted uppercase tracking-wider mb-3">Trust Score</p>
      <div className="relative w-28 h-28">
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle cx="50" cy="50" r="42" fill="none" stroke="hsl(220,14%,18%)" strokeWidth="10" />
          {/* Score circle */}
          <motion.circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${2 * Math.PI * 42}`}
            initial={{ strokeDashoffset: 2 * Math.PI * 42 }}
            animate={{ strokeDashoffset: 2 * Math.PI * 42 * (1 - clamped / 100) }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            transform="rotate(-90 50 50)"
            style={{ filter: `drop-shadow(0 0 6px ${color})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Shield className="w-4 h-4 mb-0.5" style={{ color }} />
          <motion.p
            className="text-xl font-bold"
            style={{ color }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {clamped.toFixed(0)}
          </motion.p>
        </div>
      </div>
      <span className="mt-2 text-xs font-semibold" style={{ color }}>{label}</span>
    </div>
  );
}
