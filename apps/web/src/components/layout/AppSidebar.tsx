import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Home,
  Activity,
  MessageCircle,
  BookOpen,
  TrendingUp,
  ListChecks,
  Settings,
  ShieldAlert,
} from "lucide-react";

const navItems = [
  { title: "Home", url: "/app", icon: Home },
  { title: "Check-in", url: "/app/checkin", icon: Activity },
  { title: "Chat", url: "/app/chat", icon: MessageCircle },
  { title: "Journal", url: "/app/journal", icon: BookOpen },
  { title: "Insights", url: "/app/insights", icon: TrendingUp },
  { title: "Plans", url: "/app/plans", icon: ListChecks },
];

const bottomItems = [
  { title: "Safety Center", url: "/app/safety", icon: ShieldAlert, urgent: true },
  { title: "Settings", url: "/app/settings", icon: Settings },
];

export function AppSidebar() {
  const location = useLocation();
  const isActive = (url: string) =>
    url === "/app" ? location.pathname === "/app" : location.pathname.startsWith(url);

  return (
    <aside className="hidden md:flex flex-col w-60 border-r border-border bg-sidebar min-h-screen shrink-0">
      <div className="p-5 border-b border-border">
        <Link to="/app" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-md bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-heading font-bold text-sm">A</span>
          </div>
          <span className="font-heading font-semibold text-foreground text-lg">Aether</span>
        </Link>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const active = isActive(item.url);
          return (
            <Link
              key={item.url}
              to={item.url}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-aether relative ${
                active
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              {active && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-md bg-primary/10"
                  transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
                />
              )}
              <item.icon className="w-5 h-5 relative z-10" strokeWidth={1.5} />
              <span className="relative z-10">{item.title}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 space-y-1 border-t border-border">
        {bottomItems.map((item) => {
          const active = isActive(item.url);
          return (
            <Link
              key={item.url}
              to={item.url}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-aether ${
                active
                  ? "bg-primary/10 text-primary font-medium"
                  : item.urgent
                  ? "text-urgent hover:bg-urgent/10"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <item.icon className="w-5 h-5" strokeWidth={1.5} />
              <span>{item.title}</span>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
