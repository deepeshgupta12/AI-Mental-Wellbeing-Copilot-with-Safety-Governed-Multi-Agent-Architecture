"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  FileSearch,
  Flag,
  GitCompare,
  LayoutDashboard,
  Route,
  Settings2,
  ShieldAlert,
  SplitSquareVertical,
  History,
} from "lucide-react";

const adminNav = [
  { title: "Overview", url: "/admin", icon: LayoutDashboard },
  { title: "Safety Queue", url: "/admin/safety-events", icon: ShieldAlert },
  { title: "Reviewer Dashboard", url: "/admin/reviewer-dashboard", icon: Activity },
  { title: "Decision Path Explorer", url: "/admin/decision-paths", icon: SplitSquareVertical },
  { title: "Escalation Analytics", url: "/admin/escalations", icon: BarChart3 },
  { title: "Trace Viewer", url: "/admin/cases", icon: FileSearch },
  { title: "Flagged Sessions", url: "/admin/flagged", icon: Flag },
  { title: "Policy History", url: "/admin/policy-history", icon: History },
  { title: "Config Audit", url: "/admin/audit", icon: GitCompare },
  { title: "Routing / Policy", url: "/admin/policy", icon: Route },
  { title: "Analytics", url: "/admin/analytics", icon: BarChart3 },
];

export function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const isActive = (url: string) =>
    url === "/admin" ? pathname === "/admin" : pathname.startsWith(url);

  return (
    <div className="flex min-h-svh w-full bg-background">
      <aside className="hidden min-h-screen w-72 shrink-0 flex-col border-r border-border bg-sidebar md:flex">
        <div className="border-b border-border p-5">
          <Link href="/admin" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-foreground">
              <Settings2 className="h-4 w-4 text-background" />
            </div>
            <div>
              <span className="block font-heading text-base font-semibold leading-tight text-foreground">
                Aether Admin
              </span>
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Intelligence Console
              </span>
            </div>
          </Link>
        </div>

        <nav className="flex-1 space-y-0.5 p-3">
          {adminNav.map((item) => {
            const active = isActive(item.url);
            return (
              <Link
                key={item.url}
                href={item.url}
                className={`flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-aether ${
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
            ← Back to user view
          </Link>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-border bg-background px-6">
          <h2 className="font-heading font-semibold text-foreground">
            Admin Intelligence & Safety Operations
          </h2>
          <div className="text-xs text-muted-foreground">V3-Pack6</div>
        </header>
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}