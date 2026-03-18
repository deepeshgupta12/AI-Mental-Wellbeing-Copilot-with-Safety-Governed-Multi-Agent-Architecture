import { Outlet, Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Flag,
  MessageCircleMore,
  FileSearch,
  ScrollText,
  Cog,
} from "lucide-react";

const adminNav = [
  { title: "Overview", url: "/admin", icon: LayoutDashboard },
  { title: "Flagged Sessions", url: "/admin/flagged", icon: Flag },
  { title: "Session Logs", url: "/admin/sessions", icon: MessageCircleMore },
  { title: "Case Reviews", url: "/admin/cases", icon: FileSearch },
  { title: "Audit Logs", url: "/admin/audit", icon: ScrollText },
  { title: "Policy & Prompts", url: "/admin/policy", icon: Cog },
];

export function AdminLayout() {
  const location = useLocation();
  const isActive = (url: string) =>
    url === "/admin" ? location.pathname === "/admin" : location.pathname.startsWith(url);

  return (
    <div className="flex min-h-svh w-full bg-background">
      <aside className="hidden md:flex flex-col w-60 border-r border-border bg-sidebar min-h-screen shrink-0">
        <div className="p-5 border-b border-border">
          <Link to="/admin" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md bg-foreground flex items-center justify-center">
              <span className="text-background font-heading font-bold text-sm">A</span>
            </div>
            <div>
              <span className="font-heading font-semibold text-foreground text-base block leading-tight">
                Aether
              </span>
              <span className="text-[10px] text-muted-foreground font-medium tracking-wider uppercase">
                Operations
              </span>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-3 space-y-0.5">
          {adminNav.map((item) => {
            const active = isActive(item.url);
            return (
              <Link
                key={item.url}
                to={item.url}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-aether ${
                  active
                    ? "bg-foreground/10 text-foreground font-medium"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <item.icon className="w-5 h-5" strokeWidth={1.5} />
                <span>{item.title}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <Link
            to="/"
            className="text-xs text-muted-foreground hover:text-foreground transition-aether"
          >
            ← Back to user view
          </Link>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 flex items-center justify-between px-6 border-b border-border bg-background">
          <h2 className="font-heading font-semibold text-foreground">Operations Console</h2>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
              <span className="text-xs font-medium text-muted-foreground">R</span>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}