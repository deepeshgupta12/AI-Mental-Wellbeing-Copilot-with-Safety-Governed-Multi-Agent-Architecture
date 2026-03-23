"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Blocks,
  FileSearch,
  Flag,
  GitCompare,
  Globe2,
  History,
  LayoutDashboard,
  Network,
  Route,
  Settings2,
  ShieldAlert,
  SlidersHorizontal,
  SplitSquareVertical,
  Workflow,
} from "lucide-react";

const adminNav = [
  { title: "Overview", url: "/admin", icon: LayoutDashboard },
  { title: "Safety Queue", url: "/admin/safety-events", icon: ShieldAlert },
  { title: "Reviewer Dashboard", url: "/admin/reviewer-dashboard", icon: Activity },
  { title: "Decision Paths", url: "/admin/decision-paths", icon: SplitSquareVertical },
  { title: "Escalation Analytics", url: "/admin/escalations", icon: BarChart3 },
  { title: "Trace Viewer", url: "/admin/cases", icon: FileSearch },
  { title: "Flagged Sessions", url: "/admin/flagged", icon: Flag },
  { title: "Policy History", url: "/admin/policy-history", icon: History },
  { title: "Config Audit", url: "/admin/audit", icon: GitCompare },
  { title: "Routing & Policy", url: "/admin/policy", icon: Route },
  { title: "Care Programs", url: "/admin/care-plans", icon: Workflow },
  { title: "Language & Copy", url: "/admin/localization", icon: Globe2 },
  { title: "Enterprise Settings", url: "/admin/settings", icon: SlidersHorizontal },
  { title: "Enterprise Analytics", url: "/admin/enterprise-analytics", icon: Blocks },
  { title: "Integrations", url: "/admin/integrations", icon: Network },
  { title: "Analytics", url: "/admin/analytics", icon: BarChart3 },
];

export function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const isActive = (url: string) =>
    url === "/admin" ? pathname === "/admin" : pathname.startsWith(url);

  return (
    <div className="flex min-h-svh w-full bg-background">
      <aside className="hidden min-h-screen w-80 shrink-0 flex-col border-r border-border bg-sidebar md:flex">
        <div className="border-b border-border p-5">
          <Link href="/admin" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-foreground">
              <Settings2 className="h-4 w-4 text-background" />
            </div>
            <div>
              <span className="block font-heading text-base font-semibold leading-tight text-foreground">
                Aether Admin
              </span>
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Operations Console
              </span>
            </div>
          </Link>
        </div>

        <div className="border-b border-border px-4 py-3">
          <div className="rounded-xl border border-border bg-card px-3 py-3">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Designed for action
            </p>
            <p className="mt-1 text-sm text-foreground">
              Use these screens to spot risk, follow up on stalled support, and understand how
              people are using the platform.
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-0.5 p-3">
          {adminNav.map((item) => {
            const active = isActive(item.url);

            return (
              <Link
                key={item.url}
                href={item.url}
                className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition-aether ${
                  active
                    ? "bg-foreground/10 font-medium text-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <item.icon className="h-5 w-5" strokeWidth={1.5} />
                <span>{item.title}</span>
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-border p-4">
          <Link
            href="/"
            className="text-xs text-muted-foreground transition-aether hover:text-foreground"
          >
            ← Back to member experience
          </Link>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-border bg-background px-6">
          <div>
            <h2 className="font-heading font-semibold text-foreground">Operations Console</h2>
            <p className="text-xs text-muted-foreground">
              Safety, support programs, language preferences, and platform operations
            </p>
          </div>
          <div className="text-xs text-muted-foreground">Pack 9 UX Revamp</div>
        </header>
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}