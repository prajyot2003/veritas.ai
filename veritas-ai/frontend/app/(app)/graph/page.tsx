"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { Network, RefreshCw, ZoomIn, ZoomOut, Filter } from "lucide-react";
import { graphApi } from "@/lib/api";

// Node colors by type
const NODE_COLORS: Record<string, string> = {
  borrower: "#3b82f6",
  entity: "#a855f7",
  collateral: "#f59e0b",
  transaction: "#10b981",
};

const RISK_COLORS = ["#10b981", "#f59e0b", "#f97316", "#ef4444"];

function getRiskColor(score?: number): string {
  if (!score) return "#64748b";
  if (score > 75) return RISK_COLORS[3];
  if (score > 50) return RISK_COLORS[2];
  if (score > 25) return RISK_COLORS[1];
  return RISK_COLORS[0];
}

// Simple canvas-based force graph renderer
function ForceGraph({ data }: { data: any }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [tooltip, setTooltip] = useState<{ node: any; x: number; y: number } | null>(null);

  const nodesRef = useRef<any[]>([]);
  const edgesRef = useRef<any[]>([]);
  const animFrameRef = useRef<number>();

  useEffect(() => {
    if (!data?.nodes?.length) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;
    const W = canvas.width;
    const H = canvas.height;

    // Initialize nodes with random positions
    const nodes = data.nodes.map((n: any, i: number) => ({
      ...n,
      x: W / 2 + (Math.random() - 0.5) * W * 0.6,
      y: H / 2 + (Math.random() - 0.5) * H * 0.6,
      vx: 0,
      vy: 0,
      r: 12,
    }));
    nodesRef.current = nodes;
    edgesRef.current = data.edges;

    // Force simulation
    const simulate = () => {
      const ns = nodesRef.current;
      const es = edgesRef.current;

      // Repulsion
      for (let i = 0; i < ns.length; i++) {
        for (let j = i + 1; j < ns.length; j++) {
          const dx = ns[j].x - ns[i].x;
          const dy = ns[j].y - ns[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 2000 / (dist * dist);
          ns[i].vx -= (dx / dist) * force;
          ns[i].vy -= (dy / dist) * force;
          ns[j].vx += (dx / dist) * force;
          ns[j].vy += (dy / dist) * force;
        }
      }

      // Attraction (edges)
      const nodeMap = Object.fromEntries(ns.map((n: any) => [n.id, n]));
      for (const e of es) {
        const src = nodeMap[e.source];
        const tgt = nodeMap[e.target];
        if (!src || !tgt) continue;
        const dx = tgt.x - src.x;
        const dy = tgt.y - src.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = (dist - 120) * 0.02;
        src.vx += (dx / dist) * force;
        src.vy += (dy / dist) * force;
        tgt.vx -= (dx / dist) * force;
        tgt.vy -= (dy / dist) * force;
      }

      // Center gravity
      for (const n of ns) {
        n.vx += (W / 2 - n.x) * 0.002;
        n.vy += (H / 2 - n.y) * 0.002;
        // Damping
        n.vx *= 0.85;
        n.vy *= 0.85;
        n.x += n.vx;
        n.y += n.vy;
        // Bounds
        n.x = Math.max(20, Math.min(W - 20, n.x));
        n.y = Math.max(20, Math.min(H - 20, n.y));
      }

      // Draw
      ctx.clearRect(0, 0, W, H);

      // Grid
      ctx.strokeStyle = "rgba(255,255,255,0.03)";
      ctx.lineWidth = 1;
      for (let x = 0; x < W; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
      }
      for (let y = 0; y < H; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      }

      // Edges
      const nodeMapDraw = Object.fromEntries(ns.map((n: any) => [n.id, n]));
      for (const e of es) {
        const src = nodeMapDraw[e.source];
        const tgt = nodeMapDraw[e.target];
        if (!src || !tgt) continue;
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);
        ctx.strokeStyle = `rgba(100, 116, 139, ${Math.min(0.6, e.weight)})`;
        ctx.lineWidth = e.weight * 1.5;
        ctx.stroke();

        // Edge label
        const mx = (src.x + tgt.x) / 2;
        const my = (src.y + tgt.y) / 2;
        ctx.fillStyle = "rgba(148,163,184,0.7)";
        ctx.font = "9px Inter, sans-serif";
        ctx.fillText(e.relationship, mx, my);
      }

      // Nodes
      for (const n of ns) {
        const color = NODE_COLORS[n.type] || "#64748b";
        const riskColor = getRiskColor(n.risk_score);

        // Outer glow ring (risk)
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r + 4, 0, Math.PI * 2);
        ctx.fillStyle = riskColor + "30";
        ctx.fill();

        // Node circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = color + "cc";
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.fillStyle = "#e2e8f0";
        ctx.font = "bold 10px Inter, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(n.label.split(" ")[0], n.x, n.y + n.r + 14);
      }

      animFrameRef.current = requestAnimationFrame(simulate);
    };

    animFrameRef.current = requestAnimationFrame(simulate);
    return () => { if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current); };
  }, [data]);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        width={900}
        height={560}
        className="w-full h-full rounded-xl"
        style={{ background: "hsl(220, 20%, 7%)" }}
      />
      {/* Legend */}
      <div className="absolute bottom-4 left-4 glass rounded-xl p-3 space-y-1">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ background: color }} />
            <span className="text-xs text-muted capitalize">{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function GraphPage() {
  const [graphData, setGraphData] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string | null>(null);

  const fetchGraph = async () => {
    setLoading(true);
    try {
      const [g, a] = await Promise.all([
        graphApi.getData(filter || undefined),
        graphApi.getAnalytics(),
      ]);
      setGraphData(g);
      setAnalytics(a);
    } catch {
      // Demo fallback
      setGraphData({
        nodes: [
          { id: "b001", label: "Rajesh Kumar", type: "borrower", risk_score: 72 },
          { id: "b003", label: "Suresh Patel", type: "borrower", risk_score: 85 },
          { id: "e001", label: "RK Holdings", type: "entity", risk_score: 68 },
          { id: "e003", label: "SP Real Estate", type: "entity", risk_score: 81 },
          { id: "c001", label: "Plot No. 47", type: "collateral", risk_score: 65 },
          { id: "c003", label: "Surat Commercial", type: "collateral", risk_score: 78 },
          { id: "t002", label: "TXN-2023-002", type: "transaction", risk_score: 82 },
        ],
        edges: [
          { source: "b001", target: "e001", relationship: "DIRECTOR_OF", weight: 1 },
          { source: "b003", target: "e003", relationship: "DIRECTOR_OF", weight: 1 },
          { source: "e001", target: "c001", relationship: "MORTGAGED_BY", weight: 0.8 },
          { source: "e003", target: "c003", relationship: "MORTGAGED_BY", weight: 0.9 },
          { source: "b001", target: "c001", relationship: "OWNS", weight: 0.9 },
          { source: "b001", target: "b003", relationship: "ASSOCIATED_WITH", weight: 0.6 },
          { source: "b003", target: "t002", relationship: "INITIATED", weight: 1 },
        ],
      });
      setAnalytics({
        total_nodes: 7,
        total_edges: 7,
        high_risk_entities: 4,
        duplicate_collateral_detected: 1,
        circular_relationships: 1,
        graph_density: 0.238,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchGraph(); }, [filter]);

  return (
    <div className="p-6 space-y-5 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Knowledge Graph</h1>
          <p className="text-muted text-sm mt-1">Borrower relationships · Ownership structure · Transaction network</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            {["all", "borrower", "entity", "collateral", "transaction"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f === "all" ? null : f)}
                className={`px-2 py-1 rounded-lg text-xs font-medium transition-all ${
                  (filter === null && f === "all") || filter === f
                    ? "bg-primary/20 text-primary border border-primary/30"
                    : "text-muted hover:text-foreground"
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
          <button onClick={fetchGraph} className="p-2 rounded-lg hover:bg-surface-2 text-muted hover:text-foreground transition-colors">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Analytics strip */}
      {analytics && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {[
            { label: "Total Nodes", value: analytics.total_nodes },
            { label: "Relationships", value: analytics.total_edges },
            { label: "High-Risk Entities", value: analytics.high_risk_entities, color: "text-risk-critical" },
            { label: "Duplicate Collateral", value: analytics.duplicate_collateral_detected, color: "text-accent-amber" },
            { label: "Circular Links", value: analytics.circular_relationships, color: "text-accent-violet" },
          ].map((s) => (
            <div key={s.label} className="glass-card rounded-xl p-3 text-center">
              <p className={`text-xl font-bold ${s.color || "text-foreground"}`}>{s.value}</p>
              <p className="text-xs text-muted mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Graph canvas */}
      <div className="glass-card rounded-xl overflow-hidden" style={{ height: 560 }}>
        {loading ? (
          <div className="w-full h-full flex items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <Network className="w-10 h-10 text-muted animate-pulse" />
              <p className="text-muted text-sm">Building knowledge graph...</p>
            </div>
          </div>
        ) : (
          <ForceGraph data={graphData} />
        )}
      </div>
    </div>
  );
}
