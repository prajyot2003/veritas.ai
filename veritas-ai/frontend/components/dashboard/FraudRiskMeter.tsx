"use client";

import { motion } from "framer-motion";

interface FraudRiskMeterProps {
  score: number;
}

export function FraudRiskMeter({ score }: FraudRiskMeterProps) {
  const clamped = Math.min(100, Math.max(0, score));
  const angle = (clamped / 100) * 180 - 90;

  const color =
    clamped > 70 ? "hsl(350,89%,60%)" :
    clamped > 50 ? "hsl(25,95%,55%)" :
    clamped > 30 ? "hsl(38,92%,55%)" :
    "hsl(160,84%,45%)";

  const label =
    clamped > 70 ? "CRITICAL" :
    clamped > 50 ? "HIGH" :
    clamped > 30 ? "MEDIUM" : "LOW";

  // SVG arc helper
  const polarToCartesian = (cx: number, cy: number, r: number, angle: number) => {
    const rad = ((angle - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  };

  const arc = (cx: number, cy: number, r: number, start: number, end: number) => {
    const s = polarToCartesian(cx, cy, r, start);
    const e = polarToCartesian(cx, cy, r, end);
    const large = end - start > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
  };

  return (
    <div className="flex flex-col items-center">
      <p className="text-xs text-muted uppercase tracking-wider mb-2">Avg Fraud Score</p>
      <div className="relative">
        <svg width="160" height="90" viewBox="0 0 160 90">
          {/* Background arc */}
          <path
            d={arc(80, 80, 60, 180, 360)}
            fill="none"
            stroke="hsl(220,14%,18%)"
            strokeWidth="12"
            strokeLinecap="round"
          />
          {/* Risk zones */}
          <path d={arc(80, 80, 60, 180, 234)} fill="none" stroke="hsl(160,84%,35%)" strokeWidth="12" strokeLinecap="round" opacity={0.4} />
          <path d={arc(80, 80, 60, 234, 288)} fill="none" stroke="hsl(38,92%,45%)" strokeWidth="12" strokeLinecap="round" opacity={0.4} />
          <path d={arc(80, 80, 60, 288, 324)} fill="none" stroke="hsl(25,95%,45%)" strokeWidth="12" strokeLinecap="round" opacity={0.4} />
          <path d={arc(80, 80, 60, 324, 360)} fill="none" stroke="hsl(350,89%,50%)" strokeWidth="12" strokeLinecap="round" opacity={0.4} />
          {/* Score arc */}
          <motion.path
            d={arc(80, 80, 60, 180, 180 + (clamped / 100) * 180)}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            style={{ filter: `drop-shadow(0 0 6px ${color})` }}
          />
          {/* Needle */}
          <motion.line
            x1="80" y1="80"
            x2="80" y2="30"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            initial={{ rotate: -90 }}
            animate={{ rotate: angle }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            style={{ transformOrigin: "80px 80px", filter: `drop-shadow(0 0 4px ${color})` }}
          />
          <circle cx="80" cy="80" r="4" fill={color} style={{ filter: `drop-shadow(0 0 4px ${color})` }} />
        </svg>
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
          <motion.p
            className="text-2xl font-bold"
            style={{ color }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {clamped.toFixed(0)}
          </motion.p>
        </div>
      </div>
      <span className={`mt-1 text-xs font-bold px-2 py-0.5 rounded-full badge-${label.toLowerCase()}`}>
        {label}
      </span>
    </div>
  );
}
