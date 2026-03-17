import { Link, useLocation } from "react-router-dom";
import { Home, Activity, MessageCircle, BookOpen, TrendingUp } from "lucide-react";

const mobileNavItems = [
  { title: "Home", url: "/app", icon: Home },
  { title: "Check-in", url: "/app/checkin", icon: Activity },
  { title: "Chat", url: "/app/chat", icon: MessageCircle },
  { title: "Journal", url: "/app/journal", icon: BookOpen },
  { title: "Insights", url: "/app/insights", icon: TrendingUp },
];

export function MobileNav() {
  const location = useLocation();
  const isActive = (url: string) =>
    url === "/app" ? location.pathname === "/app" : location.pathname.startsWith(url);

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-sm border-t border-border safe-area-bottom">
      <div className="flex items-center justify-around h-16 px-2">
        {mobileNavItems.map((item) => {
          const active = isActive(item.url);
          return (
            <Link
              key={item.url}
              to={item.url}
              className={`flex flex-col items-center gap-1 py-1 px-3 rounded-md transition-aether ${
                active ? "text-primary" : "text-muted-foreground"
              }`}
            >
              <item.icon className="w-5 h-5" strokeWidth={active ? 2 : 1.5} />
              <span className="text-[10px] font-medium">{item.title}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
