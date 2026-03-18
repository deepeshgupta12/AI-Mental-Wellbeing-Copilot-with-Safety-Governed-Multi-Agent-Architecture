"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { ShieldAlert } from "lucide-react";

import { AppSidebar } from "./AppSidebar";
import { MobileNav } from "./MobileNav";

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-svh w-full bg-background">
      <AppSidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-border bg-background/95 px-4 backdrop-blur-sm md:hidden">
          <Link href="/app" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
              <span className="font-heading text-xs font-bold text-primary-foreground">
                A
              </span>
            </div>
            <span className="font-heading font-semibold text-foreground">Aether</span>
          </Link>
          <Link
            href="/app/safety"
            className="rounded-md p-2 text-urgent transition-aether hover:bg-urgent/10"
          >
            <ShieldAlert className="h-5 w-5" strokeWidth={1.5} />
          </Link>
        </header>

        <main className="flex-1 pb-20 md:pb-0">{children}</main>
        <MobileNav />
      </div>
    </div>
  );
}