import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, Clock, RotateCcw } from "lucide-react";
import { getCurrentUserId } from "@/lib/demo-session";
import { listActionPlans } from "@/lib/action-plans-api";

export default function PlansPage() {
  const userId = getCurrentUserId();

  const plansQuery = useQuery({
    queryKey: ["action-plans", userId],
    queryFn: () => listActionPlans(userId!),
    enabled: !!userId,
  });

  const plans = plansQuery.data ?? [];

  return (
    <div className="max-w-2xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2">Action Plans</h1>
        <p className="text-muted-foreground text-sm mb-8">Practical, flexible steps. No pressure — just direction.</p>

        {!userId ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            No active user session found. Please complete onboarding first.
          </div>
        ) : plansQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            Loading action plans...
          </div>
        ) : plans.length === 0 ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            No action plans yet. Create one through your flow APIs or conversation workflow.
          </div>
        ) : (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Clock className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
              <h2 className="font-heading font-semibold text-foreground text-sm">Saved plans</h2>
            </div>
            <div className="space-y-2">
              {plans.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 p-3 rounded-lg border border-border bg-card shadow-card"
                >
                  <button className="shrink-0">
                    {item.is_completed ? (
                      <CheckCircle2 className="w-5 h-5 text-safe" />
                    ) : (
                      <Circle className="w-5 h-5 text-border" />
                    )}
                  </button>
                  <div>
                    <span className="text-sm text-foreground">{item.title}</span>
                    {item.description && (
                      <p className="text-xs text-muted-foreground mt-0.5">{item.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground mb-3">
            Plans adapt based on your check-ins and conversations. Missed something? That's okay — re-entry is always gentle.
          </p>
          <Button variant="soft" size="sm">Adjust my plan</Button>
        </div>
      </motion.div>
    </div>
  );
}