"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  LayoutDashboard,
  Upload,
  FileSearch,
  CheckSquare,
  Network,
  BarChart3,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  User,
  Zap,
} from "lucide-react";
import { logout, getUser } from "@/lib/auth";
import clsx from "clsx";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard", badge: null },
  { href: "/upload", icon: Upload, label: "Upload Center", badge: null },
  { href: "/intelligence", icon: FileSearch, label: "Document Intelligence", badge: "3" },
  { href: "/compliance", icon: CheckSquare, label: "Compliance Center", badge: "2" },
  { href: "/graph", icon: Network, label: "Knowledge Graph", badge: null },
  { href: "/risk", icon: BarChart3, label: "Risk Analysis", badge: null },
  { href: "/settings", icon: Settings, label: "Settings", badge: null },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const user = getUser();

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 64 : 240 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="relative flex flex-col h-screen bg-surface border-r border-border shrink-0 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-border">
        <div
          className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: "linear-gradient(135deg, hsl(213,94%,45%) 0%, hsl(265,80%,55%) 100%)" }}
        >
          <Shield className="w-4 h-4 text-white" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              <p className="font-bold text-sm text-foreground tracking-tight">VERITAS AI</p>
              <div className="flex items-center gap-1 mt-0.5">
                <div className="pulse-dot w-1.5 h-1.5" />
                <p className="text-xs text-accent-emerald font-medium">Live</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ href, icon: Icon, label, badge }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link key={href} href={href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={clsx(
                  "sidebar-item relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all",
                  active && "active"
                )}
              >
                <Icon
                  className={clsx(
                    "shrink-0 w-4 h-4",
                    active ? "text-primary" : "text-muted"
                  )}
                />
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className={clsx(
                        "text-sm font-medium flex-1",
                        active ? "text-primary-light" : "text-foreground"
                      )}
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
                {badge && !collapsed && (
                  <span className="text-xs font-bold bg-risk-critical/20 text-risk-critical rounded-full px-1.5 py-0.5 min-w-[20px] text-center">
                    {badge}
                  </span>
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* User profile */}
      <div className="border-t border-border p-3">
        <div className="flex items-center gap-3 px-1 py-2">
          <div className="shrink-0 w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center">
            <User className="w-3.5 h-3.5 text-primary" />
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <p className="text-xs font-semibold text-foreground truncate">
                  {user?.name || "User"}
                </p>
                <p className="text-xs text-muted capitalize">{user?.role || "viewer"}</p>
              </motion.div>
            )}
          </AnimatePresence>
          {!collapsed && (
            <button
              onClick={logout}
              className="shrink-0 text-muted hover:text-risk-critical transition-colors"
              title="Logout"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-surface-2 border border-border flex items-center justify-center text-muted hover:text-foreground hover:border-primary transition-all z-10"
      >
        {collapsed ? (
          <ChevronRight className="w-3 h-3" />
        ) : (
          <ChevronLeft className="w-3 h-3" />
        )}
      </button>
    </motion.aside>
  );
}
