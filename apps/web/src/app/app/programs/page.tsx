"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { advanceCarePlan, createCarePlanEvent, getCarePlanUserSummary, listCarePlans } from "@/lib/care-plans-api";
import { getCurrentUserId } from "@/lib/demo-session";

export default function ProgramsPage() {
  const queryClient = useQueryClient();
  const userId = getCurrentUserId();

  const summaryQuery = useQuery({
    queryKey: ["care-plan-summary", userId],
    queryFn: () => getCarePlanUserSummary(userId!),
    enabled: !!userId,
  });

  const carePlansQuery = useQuery({
    queryKey: ["care-plans", userId],
    queryFn: () => listCarePlans({ userId }),
    enabled: !!userId,
  });

  const checkInMutation = useMutation({
    mutationFn: async (carePlanId: string) =>
      createCarePlanEvent(carePlanId, {
        user_id: userId,
        event_type: "check_in",
        event_status: "completed",
        adherence_score: 1,
        notes: "Marked from user programs screen.",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
      await queryClient.invalidateQueries({ queryKey: ["care-plan-summary", userId] });
    },
  });

  const advanceMutation = useMutation({
    mutationFn: async (carePlanId: string) =>
      advanceCarePlan(carePlanId, {
        notes: "Advanced from user programs screen.",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
      await queryClient.invalidateQueries({ queryKey: ["care-plan-summary", userId] });
    },
  });

  const plans = carePlansQuery.data ?? [];
  const summary = summaryQuery.data;

  const activePlans = useMemo(() => plans.filter((item) => item.status === "active"), [plans]);

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">Care Programs</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Track long-term care plans, recurring programs, adherence, and step-by-step progress.
          </p>
        </div>

        {!summary ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading care program summary...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
              {[
                { label: "Total Plans", value: summary.total_care_plans },
                { label: "Active", value: summary.active_care_plans },
                { label: "Completed", value: summary.completed_care_plans },
                { label: "Due Today", value: summary.due_today_count },
                { label: "Avg Adherence", value: summary.avg_adherence_score ?? "—" },
              ].map((item) => (
                <div key={item.label} className="rounded-lg border border-border bg-card p-4 shadow-card">
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Active Care Plans
              </h2>

              {activePlans.length === 0 ? (
                <div className="text-sm text-muted-foreground">No active care plans yet.</div>
              ) : (
                <div className="space-y-4">
                  {activePlans.map((plan) => {
                    const progress = Number((plan.progress_json?.completion_pct as number | undefined) ?? 0);
                    const adherence = (plan.adherence_json?.avg_score as number | undefined) ?? null;

                    return (
                      <div key={plan.id} className="rounded-md border border-border bg-background p-4">
                        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                          <div>
                            <div className="text-sm font-medium text-foreground">{plan.title}</div>
                            <div className="mt-1 text-xs text-muted-foreground">
                              {plan.program_key} · step: {plan.current_step_key || "—"} · language: {plan.preferred_language}
                            </div>
                            <div className="mt-2 text-sm text-muted-foreground">
                              {plan.description || "No description available."}
                            </div>
                          </div>

                          <div className="flex flex-wrap gap-2">
                            <button
                              type="button"
                              onClick={() => checkInMutation.mutate(plan.id)}
                              className="rounded-md border border-border bg-card px-3 py-2 text-sm text-foreground"
                            >
                              Mark check-in
                            </button>
                            <button
                              type="button"
                              onClick={() => advanceMutation.mutate(plan.id)}
                              className="rounded-md bg-foreground px-3 py-2 text-sm font-medium text-background"
                            >
                              Advance step
                            </button>
                          </div>
                        </div>

                        <div className="mt-4 grid gap-3 md:grid-cols-3">
                          <div className="rounded-md border border-border bg-card px-3 py-2">
                            <div className="text-xs text-muted-foreground">Progress</div>
                            <div className="mt-1 text-sm font-medium text-foreground">{progress}%</div>
                          </div>
                          <div className="rounded-md border border-border bg-card px-3 py-2">
                            <div className="text-xs text-muted-foreground">Adherence</div>
                            <div className="mt-1 text-sm font-medium text-foreground">
                              {adherence ?? "—"}
                            </div>
                          </div>
                          <div className="rounded-md border border-border bg-card px-3 py-2">
                            <div className="text-xs text-muted-foreground">Next check-in</div>
                            <div className="mt-1 text-sm font-medium text-foreground">
                              {plan.next_check_in_at
                                ? new Date(plan.next_check_in_at).toLocaleString()
                                : "—"}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}