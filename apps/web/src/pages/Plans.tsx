import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, Clock } from "lucide-react";
import { getCurrentUserId } from "@/lib/demo-session";
import { listActionPlans } from "@/lib/action-plans-api";
import { getTrendSummary } from "@/lib/memory-api";

export default function PlansPage() {
  const userId = getCurrentUserId();

  const plansQuery = useQuery({
    queryKey: ["action-plans", userId],
    queryFn: () => listActionPlans(userId!),
    enabled: !!userId,
  });

  const trendQuery = useQuery({
    queryKey: ["trend-summary", userId],
    queryFn: () => getTrendSummary(userId!),
    enabled: !!userId,
  });

  const plans = plansQuery.data ?? [];

  const lightweightSuggestions = [
    trendQuery.data?.avg_stress_score != null && trendQuery.data.avg_stress_score >= 7
      ? "Choose one 5-minute unwind step for today."
      : null,
    trendQuery.data?.avg_sleep_hours != null && trendQuery.data.avg_sleep_hours < 7
      ? "Protect your next sleep window with one earlier wind-down cue."
      : null,
    "Keep the next step tiny enough that it feels easy to begin.",
  ].filter(Boolean) as string[];

  return (
    <div className="max-w-2xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2">
          Action Plans
        </h1>
        <p className="text-muted-foreground text-sm mb-8">
          Practical, flexible steps. No pressure — just direction.
        </p>

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

        <div className="mb-6 rounded-lg border border-border bg-card shadow-card p-5">
          <h2 className="font-heading font-semibold text-foreground text-sm mb-3">
            Follow-up Suggestions
          </h2>
          <div className="space-y-2">
            {lightweightSuggestions.map((item, index) => (
              <div key={index} className="rounded-md border border-border bg-background p-3">
                <p className="text-sm text-muted-foreground">{item}</p>
              </div>
            ))}
          </div>
        </div>

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