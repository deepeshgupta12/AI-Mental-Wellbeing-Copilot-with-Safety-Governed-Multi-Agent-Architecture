"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Activity,
  BookOpen,
  Home,
  ListChecks,
  MessageCircle,
  RefreshCcw,
  Settings,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";

const navItems = [
  { title: "Home", url: "/app", icon: Home },
  { title: "Check-in", url: "/app/checkin", icon: Activity },
  { title: "Chat", url: "/app/chat", icon: MessageCircle },
  { title: "Journal", url: "/app/journal", icon: BookOpen },
  { title: "Insights", url: "/app/insights", icon: TrendingUp },
  { title: "Quick Plans", url: "/app/plans", icon: ListChecks },
  { title: "Support Programs", url: "/app/programs", icon: RefreshCcw },
];

const bottomItems = [
  { title: "Safety Center", url: "/app/safety", icon: ShieldAlert, urgent: true },
  { title: "Settings", url: "/app/settings", icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();

  const isActive = (url: string) =>
    url === "/app" ? pathname === "/app" : pathname.startsWith(url);

  return (
    <aside className="hidden min-h-screen w-72 shrink-0 flex-col border-r border-border bg-sidebar md:flex">
      <div className="border-b border-border px-5 py-5">
        <Link href="/app" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary">
            <span className="font-heading text-sm font-bold text-primary-foreground">A</span>
          </div>
          <div>
            <span className="block font-heading text-lg font-semibold text-foreground">Aether</span>
            <span className="block text-[11px] text-muted-foreground">
              Gentle support, one step at a time
            </span>
          </div>
        </Link>
      </div>

      <div className="border-b border-border px-4 py-3">
        <div className="rounded-xl border border-border bg-card px-3 py-3">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Your support space
          </p>
          <p className="mt-1 text-sm text-foreground">
            Quick Plans are one-time next steps. Support Programs are ongoing routines with
            check-ins.
          </p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const active = isActive(item.url);

          return (
            <Link
              key={item.url}
              href={item.url}
              className={`relative flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition-aether ${
                active
                  ? "bg-primary/10 font-medium text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              {active ? (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-xl bg-primary/10"
                  transition={{ type: "spring", bounce: 0.15, duration: 0.45 }}
                />
              ) : null}
              <item.icon className="relative z-10 h-5 w-5" strokeWidth={1.5} />
              <span className="relative z-10">{item.title}</span>
            </Link>
          );
        })}
      </nav>

      <div className="space-y-1 border-t border-border p-3">
        {bottomItems.map((item) => {
          const active = isActive(item.url);

          return (
            <Link
              key={item.url}
              href={item.url}
              className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition-aether ${
                active
                  ? "bg-primary/10 font-medium text-primary"
                  : item.urgent
                    ? "text-urgent hover:bg-urgent/10"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <item.icon className="h-5 w-5" strokeWidth={1.5} />
              <span>{item.title}</span>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}