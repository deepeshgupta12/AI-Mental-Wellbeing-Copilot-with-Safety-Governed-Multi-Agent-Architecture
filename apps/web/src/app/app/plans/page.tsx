"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Circle, Clock } from "lucide-react";

import { Button } from "@/components/ui/button";
import { listActionPlans } from "@/lib/action-plans-api";
import { getCurrentUserId } from "@/lib/demo-session";

export default function PlansPage() {
  const userId = getCurrentUserId();

  const plansQuery = useQuery({
    queryKey: ["action-plans", userId],
    queryFn: () => listActionPlans(userId!),
    enabled: !!userId,
  });

  const plans = plansQuery.data ?? [];

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 md:px-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-2 font-heading text-2xl font-bold text-foreground md:text-3xl">
          Action Plans
        </h1>
        <p className="mb-8 text-sm text-muted-foreground">
          Practical, flexible steps. No pressure — just direction.
        </p>

        {!userId ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            No active user session found. Please complete onboarding first.
          </div>
        ) : plansQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading action plans...
          </div>
        ) : plans.length === 0 ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            No action plans yet. Create one through your flow APIs or conversation workflow.
          </div>
        ) : (
          <div className="mb-6">
            <div className="mb-3 flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" strokeWidth={1.5} />
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Saved plans
              </h2>
            </div>
            <div className="space-y-2">
              {plans.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 rounded-lg border border-border bg-card p-3 shadow-card"
                >
                  <button className="shrink-0">
                    {item.is_completed ? (
                      <CheckCircle2 className="h-5 w-5 text-safe" />
                    ) : (
                      <Circle className="h-5 w-5 text-border" />
                    )}
                  </button>
                  <div>
                    <span className="text-sm text-foreground">{item.title}</span>
                    {item.description && (
                      <p className="mt-0.5 text-xs text-muted-foreground">{item.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-border pt-4">
          <p className="mb-3 text-xs text-muted-foreground">
            Plans adapt based on your check-ins and conversations. Missed something? That's okay — re-entry is always gentle.
          </p>
          <Button variant="soft" size="sm">
            Adjust my plan
          </Button>
        </div>
      </motion.div>
    </div>
  );
}