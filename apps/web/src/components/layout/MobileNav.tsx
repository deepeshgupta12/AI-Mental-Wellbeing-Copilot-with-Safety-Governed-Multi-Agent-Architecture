"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Home,
  ListChecks,
  MessageCircle,
  RefreshCcw,
  Settings,
} from "lucide-react";

const mobileNavItems = [
  { title: "Home", url: "/app", icon: Home },
  { title: "Check-in", url: "/app/checkin", icon: Activity },
  { title: "Chat", url: "/app/chat", icon: MessageCircle },
  { title: "Plans", url: "/app/plans", icon: ListChecks },
  { title: "Programs", url: "/app/programs", icon: RefreshCcw },
  { title: "Settings", url: "/app/settings", icon: Settings },
];

export function MobileNav() {
  const pathname = usePathname();

  const isActive = (url: string) =>
    url === "/app" ? pathname === "/app" : pathname.startsWith(url);

  return (
    <nav className="safe-area-bottom fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-background/95 backdrop-blur-sm md:hidden">
      <div className="grid h-16 grid-cols-6 items-center px-1">
        {mobileNavItems.map((item) => {
          const active = isActive(item.url);

          return (
            <Link
              key={item.url}
              href={item.url}
              className={`flex flex-col items-center gap-1 rounded-md px-1 py-1 transition-aether ${
                active ? "text-primary" : "text-muted-foreground"
              }`}
            >
              <item.icon className="h-5 w-5" strokeWidth={active ? 2 : 1.5} />
              <span className="text-[10px] font-medium">{item.title}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}