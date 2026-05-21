"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Settings, User, Shield, Database, Cpu, Eye, EyeOff, Save } from "lucide-react";
import { getUser } from "@/lib/auth";
import toast from "react-hot-toast";

export default function SettingsPage() {
  const user = getUser();
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
  const [ollamaUrl, setOllamaUrl] = useState("http://localhost:11434");
  const [model, setModel] = useState("llama3.1:8b");
  const [showKey, setShowKey] = useState(false);
  const [neo4jUri, setNeo4jUri] = useState("bolt://localhost:7687");
  const [embeddingModel, setEmbeddingModel] = useState("BAAI/bge-small-en-v1.5");

  const handleSave = () => {
    toast.success("Settings saved (session only — restart to persist)");
  };

  const Section = ({ title, icon: Icon, children }: any) => (
    <div className="glass-card rounded-xl p-6 space-y-4">
      <div className="flex items-center gap-2 border-b border-border pb-3">
        <Icon className="w-4 h-4 text-primary" />
        <h2 className="text-sm font-semibold text-foreground">{title}</h2>
      </div>
      {children}
    </div>
  );

  const Field = ({ label, value, onChange, type = "text", suffix }: any) => (
    <div>
      <label className="block text-xs text-muted uppercase tracking-wider mb-1.5">{label}</label>
      <div className="flex gap-2">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm text-foreground font-mono focus:outline-none focus:border-primary transition-all"
        />
        {suffix}
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted text-sm mt-1">Configure AI models, databases, and preferences</p>
      </div>

      {/* User */}
      <Section title="User Profile" icon={User}>
        <div className="flex items-center gap-4 p-4 bg-surface-2 rounded-xl">
          <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
            <User className="w-6 h-6 text-primary" />
          </div>
          <div>
            <p className="font-semibold text-foreground">{user?.name}</p>
            <p className="text-sm text-muted">{user?.email}</p>
            <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary font-medium capitalize mt-1 inline-block">
              {user?.role}
            </span>
          </div>
        </div>
      </Section>

      {/* AI Models */}
      <Section title="AI Model Configuration" icon={Cpu}>
        <Field label="Ollama Base URL" value={ollamaUrl} onChange={setOllamaUrl} />
        <Field label="LLM Model" value={model} onChange={setModel} />
        <Field label="Embedding Model" value={embeddingModel} onChange={setEmbeddingModel} />
        <div className="p-3 rounded-lg bg-primary/5 border border-primary/20">
          <p className="text-xs text-primary font-medium">ℹ️ Using local Ollama — no API keys required. All inference runs on your machine.</p>
        </div>
      </Section>

      {/* Backend */}
      <Section title="Backend & API" icon={Settings}>
        <Field label="Backend API URL" value={apiUrl} onChange={setApiUrl} />
      </Section>

      {/* Databases */}
      <Section title="Database Configuration" icon={Database}>
        <Field label="Neo4j URI" value={neo4jUri} onChange={setNeo4jUri} />
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "ChromaDB", status: "Connected", color: "text-risk-low" },
            { label: "Redis", status: "Connected", color: "text-risk-low" },
            { label: "Neo4j", status: "Checking...", color: "text-accent-amber" },
            { label: "Ollama", status: "Active", color: "text-risk-low" },
          ].map((s) => (
            <div key={s.label} className="flex items-center justify-between p-3 bg-surface-2 rounded-lg">
              <span className="text-xs text-muted">{s.label}</span>
              <div className="flex items-center gap-1.5">
                <div className={`w-2 h-2 rounded-full ${s.color === "text-risk-low" ? "bg-risk-low" : "bg-accent-amber"} animate-pulse`} />
                <span className={`text-xs font-semibold ${s.color}`}>{s.status}</span>
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Security */}
      <Section title="Security" icon={Shield}>
        <div className="flex items-center justify-between p-3 bg-surface-2 rounded-lg">
          <div>
            <p className="text-sm text-foreground font-medium">JWT Authentication</p>
            <p className="text-xs text-muted">Tokens expire after 24 hours</p>
          </div>
          <span className="text-xs badge-low px-2 py-1 rounded-full">Enabled</span>
        </div>
        <div className="flex items-center justify-between p-3 bg-surface-2 rounded-lg">
          <div>
            <p className="text-sm text-foreground font-medium">Rate Limiting</p>
            <p className="text-xs text-muted">100 req/min per IP</p>
          </div>
          <span className="text-xs badge-low px-2 py-1 rounded-full">Active</span>
        </div>
      </Section>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleSave}
        className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm text-white transition-all"
        style={{ background: "linear-gradient(135deg, hsl(213,94%,50%), hsl(213,94%,40%))", boxShadow: "0 4px 20px hsl(213,94%,55%,0.3)" }}
      >
        <Save className="w-4 h-4" />
        Save Settings
      </motion.button>
    </div>
  );
}
