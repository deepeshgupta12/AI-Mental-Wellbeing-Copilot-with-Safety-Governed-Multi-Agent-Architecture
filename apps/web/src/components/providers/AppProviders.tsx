"use client";

import { PropsWithChildren } from "react";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { AppQueryProvider } from "@/providers/query-provider";

export function AppProviders({ children }: PropsWithChildren) {
  return (
    <AppQueryProvider>
      <TooltipProvider>
        {children}
        <Toaster />
        <Sonner />
      </TooltipProvider>
    </AppQueryProvider>
  );
}