"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Cog,
  FileSearch,
  Flag,
  LayoutDashboard,
  ScrollText,
  ShieldAlert,
} from "lucide-react";

const adminNav = [
  { title: "Overview", url: "/admin", icon: LayoutDashboard },
  { title: "Flagged Sessions", url: "/admin/flagged", icon: Flag },
  { title: "Case Reviews", url: "/admin/cases", icon: FileSearch },
  { title: "Safety Events", url: "/admin/safety-events", icon: ShieldAlert },
  { title: "Audit Logs", url: "/admin/audit", icon: ScrollText },
  { title: "Policy & Prompts", url: "/admin/policy", icon: Cog },
  { title: "Analytics", url: "/admin/analytics", icon: BarChart3 },
];

export function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const isActive = (url: string) =>
    url === "/admin" ? pathname === "/admin" : pathname.startsWith(url);

  return (
    <div className="flex min-h-svh w-full bg-background">
      <aside className="hidden min-h-screen w-60 shrink-0 flex-col border-r border-border bg-sidebar md:flex">
        <div className="border-b border-border p-5">
          <Link href="/admin" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-foreground">
              <span className="font-heading text-sm font-bold text-background">A</span>
            </div>
            <div>
              <span className="block font-heading text-base font-semibold leading-tight text-foreground">
                Aether
              </span>
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Operations
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
            Operations Console
          </h2>
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
              <span className="text-xs font-medium text-muted-foreground">R</span>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}