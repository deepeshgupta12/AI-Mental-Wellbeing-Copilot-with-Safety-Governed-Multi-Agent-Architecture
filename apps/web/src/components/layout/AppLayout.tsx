import { Outlet, Link } from "react-router-dom";
import { AppSidebar } from "./AppSidebar";
import { MobileNav } from "./MobileNav";
import { ShieldAlert } from "lucide-react";

export function AppLayout() {
  return (
    <div className="flex min-h-svh w-full bg-background">
      <AppSidebar />
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <header className="md:hidden flex items-center justify-between h-14 px-4 border-b border-border bg-background/95 backdrop-blur-sm sticky top-0 z-40">
          <Link to="/app" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-heading font-bold text-xs">A</span>
            </div>
            <span className="font-heading font-semibold text-foreground">Aether</span>
          </Link>
          <Link to="/app/safety" className="p-2 text-urgent hover:bg-urgent/10 rounded-md transition-aether">
            <ShieldAlert className="w-5 h-5" strokeWidth={1.5} />
          </Link>
        </header>

        <main className="flex-1 pb-20 md:pb-0">
          <Outlet />
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
