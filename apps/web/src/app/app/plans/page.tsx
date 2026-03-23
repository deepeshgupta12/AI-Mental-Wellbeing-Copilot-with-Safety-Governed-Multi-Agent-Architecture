"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  CheckCircle2,
  Circle,
  Compass,
  ListChecks,
  Plus,
  RefreshCcw,
  Sparkles,
  Wand2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { createActionPlan, listActionPlans } from "@/lib/action-plans-api";
import { getApiErrorMessage } from "@/lib/api-client";
import {
  createCarePlan,
  getCarePlanUserSummary,
  lifecycleCarePlan,
  listCarePlans,
  updateCarePlan,
} from "@/lib/care-plans-api";
import { getCurrentUserId } from "@/lib/demo-session";

function formatDateTime(value: string | null | undefined) {
  if (!value) return "Not scheduled yet";
  return new Date(value).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  });
}

function cadenceLabel(cadenceJson: Record<string, unknown> | null | undefined) {
  const everyNDays = cadenceJson?.every_n_days;
  if (typeof everyNDays !== "number") return "Flexible cadence";
  return everyNDays === 1 ? "Daily check-in" : `Every ${everyNDays} days`;
}

export default function PlansPage() {
  const userId = getCurrentUserId();
  const queryClient = useQueryClient();

  const [showAdjustPanel, setShowAdjustPanel] = useState(false);
  const [programTitle, setProgramTitle] = useState("");
  const [programDescription, setProgramDescription] = useState("");
  const [programLanguage, setProgramLanguage] = useState("en");
  const [cadenceDays, setCadenceDays] = useState("3");

  const actionPlansQuery = useQuery({
    queryKey: ["action-plans", userId],
    queryFn: () => listActionPlans(userId!),
    enabled: !!userId,
  });

  const carePlansQuery = useQuery({
    queryKey: ["care-plans", userId],
    queryFn: () => listCarePlans({ userId: userId! }),
    enabled: !!userId,
  });

  const careSummaryQuery = useQuery({
    queryKey: ["care-plan-summary", userId],
    queryFn: () => getCarePlanUserSummary(userId!),
    enabled: !!userId,
  });

  const quickPlanMutation = useMutation({
    mutationFn: async () =>
      createActionPlan({
        user_id: userId!,
        title: "Take one small next step",
        description:
          "Pick one helpful action you can realistically do today, even if it is very small.",
        timeframe: "today",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["action-plans", userId] });
    },
  });

  const refineProgramMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        title: programTitle.trim(),
        description: programDescription.trim() || null,
        preferred_language: programLanguage,
        cadence_json: {
          every_n_days: Math.max(Number(cadenceDays || "3"), 1),
        },
        metadata_json: {
          refined_from_plans_page: true,
        },
      };

      if (activeCarePlan) {
        return updateCarePlan(activeCarePlan.id, payload);
      }

      return createCarePlan({
        user_id: userId!,
        source_agent: "habit_care_plan",
        program_key: "steady_support_program",
        title: payload.title || "Steady Support Program",
        description: payload.description,
        preferred_language: payload.preferred_language,
        timezone: "Asia/Kolkata",
        cadence_json: payload.cadence_json,
        sequence_json: {
          steps: [
            { key: "stabilize", order: 1 },
            { key: "practice", order: 2 },
            { key: "review", order: 3 },
          ],
        },
        metadata_json: payload.metadata_json,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
      await queryClient.invalidateQueries({ queryKey: ["care-plan-summary", userId] });
      setShowAdjustPanel(false);
    },
  });

  const lifecycleMutation = useMutation({
    mutationFn: async ({
      carePlanId,
      action,
      notes,
      resetHistory,
    }: {
      carePlanId: string;
      action: "pause" | "resume" | "restart";
      notes: string;
      resetHistory?: boolean;
    }) =>
      lifecycleCarePlan(carePlanId, {
        action,
        notes,
        reset_history: resetHistory ?? true,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
      await queryClient.invalidateQueries({ queryKey: ["care-plan-summary", userId] });
    },
  });

  const actionPlans = actionPlansQuery.data ?? [];
  const carePlans = carePlansQuery.data ?? [];
  const summary = careSummaryQuery.data;

  const activeCarePlan = useMemo(() => {
    return carePlans.find((item) => item.status === "active") ?? carePlans[0] ?? null;
  }, [carePlans]);

  const latestQuickPlan = actionPlans[0] ?? null;
  const latestSupportProgram = carePlans[0] ?? null;
  const hasAnySupport = actionPlans.length > 0 || carePlans.length > 0;

  useEffect(() => {
    if (!activeCarePlan) {
      setProgramTitle("Steady Support Program");
      setProgramDescription(
        "A gentle recurring program for staying consistent with your next helpful steps.",
      );
      setProgramLanguage("en");
      setCadenceDays("3");
      return;
    }

    setProgramTitle(activeCarePlan.title || "Steady Support Program");
    setProgramDescription(activeCarePlan.description || "");
    setProgramLanguage(activeCarePlan.preferred_language || "en");

    const cadenceValue =
      typeof activeCarePlan.cadence_json?.every_n_days === "number"
        ? String(activeCarePlan.cadence_json.every_n_days)
        : "3";
    setCadenceDays(cadenceValue);
  }, [activeCarePlan]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
              <Compass className="h-3.5 w-3.5" />
              Your support roadmap
            </div>
            <h1 className="font-heading text-3xl font-bold text-foreground">
              Plans and support programs
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              Use Quick Plans for one-time next steps. Use Support Programs for ongoing
              routines that help you keep going with less friction.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button variant="soft" onClick={() => setShowAdjustPanel((current) => !current)} disabled={!userId}>
              <Wand2 className="h-4 w-4" />
              Adjust my plan
            </Button>
            <Button
              variant="hero"
              onClick={() => quickPlanMutation.mutate()}
              disabled={!userId || quickPlanMutation.isPending}
            >
              <Plus className="h-4 w-4" />
              Create quick plan
            </Button>
          </div>
        </div>

        {!userId ? (
          <div className="rounded-2xl border border-border bg-card p-5 text-sm text-muted-foreground shadow-card">
            No active user session found. Please complete onboarding first.
          </div>
        ) : (
          <>
            <div className="mb-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-border bg-card p-5 shadow-card">
                <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  <ListChecks className="h-4 w-4" />
                  Quick Plans
                </div>
                <div className="mt-3 text-3xl font-bold text-foreground">{actionPlans.length}</div>
                <p className="mt-2 text-sm text-muted-foreground">
                  One-time plans for a clear next action.
                </p>
              </div>

              <div className="rounded-2xl border border-border bg-card p-5 shadow-card">
                <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  <RefreshCcw className="h-4 w-4" />
                  Support Programs
                </div>
                <div className="mt-3 text-3xl font-bold text-foreground">
                  {summary?.active_care_plans ?? carePlans.filter((item) => item.status === "active").length}
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  Ongoing routines with progress and upcoming check-ins.
                </p>
              </div>

              <div className="rounded-2xl border border-border bg-card p-5 shadow-card">
                <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  <Sparkles className="h-4 w-4" />
                  Next check-in
                </div>
                <div className="mt-3 text-lg font-semibold text-foreground">
                  {formatDateTime(activeCarePlan?.next_check_in_at)}
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  Your next recurring support touchpoint.
                </p>
              </div>
            </div>

            <div className="mb-6 grid gap-4 lg:grid-cols-2">
              <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
                <p className="text-xs font-medium uppercase tracking-wide text-primary">
                  Quick Plans
                </p>
                <h2 className="mt-2 font-heading text-xl font-semibold text-foreground">
                  Best when you need one clear next step
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Good for today, this week, or any moment when you want direction without
                  committing to a full routine.
                </p>
              </div>

              <div className="rounded-3xl border border-primary/20 bg-primary/5 p-5 shadow-card">
                <p className="text-xs font-medium uppercase tracking-wide text-primary">
                  Support Programs
                </p>
                <h2 className="mt-2 font-heading text-xl font-semibold text-foreground">
                  Best when you want steady follow-through
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Better for gentle repetition, recurring check-ins, and progress you can
                  revisit over time.
                </p>
              </div>
            </div>

            {showAdjustPanel ? (
              <div className="mb-6 rounded-3xl border border-primary/20 bg-primary/5 p-5 shadow-card">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div className="max-w-2xl">
                    <h2 className="font-heading text-lg font-semibold text-foreground">
                      Refine your support setup
                    </h2>
                    <p className="mt-1 text-sm text-muted-foreground">
                      This now updates a real ongoing support experience. You can rename it,
                      change the rhythm, switch language, or pause and restart it gently.
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setShowAdjustPanel(false)}>
                    Close
                  </Button>
                </div>

                <div className="mt-5 grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
                  <div className="rounded-2xl border border-border bg-background p-4">
                    <h3 className="font-semibold text-foreground">
                      Ongoing support program
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Update the support flow you want to continue with.
                    </p>

                    <div className="mt-4 grid gap-4">
                      <label className="space-y-2">
                        <span className="text-sm font-medium text-foreground">Program title</span>
                        <input
                          value={programTitle}
                          onChange={(e) => setProgramTitle(e.target.value)}
                          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                          placeholder="Steady Support Program"
                        />
                      </label>

                      <label className="space-y-2">
                        <span className="text-sm font-medium text-foreground">What this is for</span>
                        <textarea
                          value={programDescription}
                          onChange={(e) => setProgramDescription(e.target.value)}
                          className="min-h-[96px] w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                          placeholder="Describe the kind of support you want this routine to provide."
                        />
                      </label>

                      <div className="grid gap-4 sm:grid-cols-2">
                        <label className="space-y-2">
                          <span className="text-sm font-medium text-foreground">Preferred language</span>
                          <select
                            value={programLanguage}
                            onChange={(e) => setProgramLanguage(e.target.value)}
                            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                          >
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="hinglish">Hinglish</option>
                          </select>
                        </label>

                        <label className="space-y-2">
                          <span className="text-sm font-medium text-foreground">Check-in every</span>
                          <select
                            value={cadenceDays}
                            onChange={(e) => setCadenceDays(e.target.value)}
                            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                          >
                            <option value="1">1 day</option>
                            <option value="2">2 days</option>
                            <option value="3">3 days</option>
                            <option value="7">7 days</option>
                          </select>
                        </label>
                      </div>

                      <div className="flex flex-wrap gap-3">
                        <Button
                          variant="hero"
                          onClick={() => refineProgramMutation.mutate()}
                          disabled={!programTitle.trim() || refineProgramMutation.isPending}
                        >
                          {activeCarePlan ? "Save support updates" : "Create support program"}
                        </Button>

                        <Button
                          variant="soft"
                          onClick={() => quickPlanMutation.mutate()}
                          disabled={quickPlanMutation.isPending}
                        >
                          Create quick plan instead
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-border bg-background p-4">
                    <h3 className="font-semibold text-foreground">Program controls</h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Use these when you need a lighter restart, a pause, or a gentler return.
                    </p>

                    {activeCarePlan ? (
                      <div className="mt-4 space-y-3">
                        <div className="rounded-xl border border-border px-4 py-3">
                          <p className="text-sm font-medium text-foreground">{activeCarePlan.title}</p>
                          <p className="mt-1 text-sm text-muted-foreground">
                            {cadenceLabel(activeCarePlan.cadence_json)} · Next check-in{" "}
                            {formatDateTime(activeCarePlan.next_check_in_at)}
                          </p>
                        </div>

                        {activeCarePlan.status === "paused" ? (
                          <Button
                            className="w-full"
                            variant="soft"
                            onClick={() =>
                              lifecycleMutation.mutate({
                                carePlanId: activeCarePlan.id,
                                action: "resume",
                                notes: "Resumed from plan refinement flow.",
                              })
                            }
                            disabled={lifecycleMutation.isPending}
                          >
                            Resume gently
                          </Button>
                        ) : (
                          <Button
                            className="w-full"
                            variant="soft"
                            onClick={() =>
                              lifecycleMutation.mutate({
                                carePlanId: activeCarePlan.id,
                                action: "pause",
                                notes: "Paused from plan refinement flow.",
                              })
                            }
                            disabled={lifecycleMutation.isPending || activeCarePlan.status === "completed"}
                          >
                            Pause for now
                          </Button>
                        )}

                        <Button
                          className="w-full"
                          variant="outline"
                          onClick={() =>
                            lifecycleMutation.mutate({
                              carePlanId: activeCarePlan.id,
                              action: "restart",
                              notes: "Restarted from plan refinement flow.",
                              resetHistory: true,
                            })
                          }
                          disabled={lifecycleMutation.isPending}
                        >
                          Restart from the beginning
                        </Button>
                      </div>
                    ) : (
                      <div className="mt-4 rounded-xl border border-dashed border-border px-4 py-5 text-sm text-muted-foreground">
                        No recurring support program yet. Save the form on the left to create one.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : null}

            {!hasAnySupport && !actionPlansQuery.isLoading && !carePlansQuery.isLoading ? (
              <div className="rounded-3xl border border-border bg-card p-8 shadow-card">
                <div className="mx-auto max-w-2xl text-center">
                  <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                    <Compass className="h-7 w-7" />
                  </div>
                  <h2 className="font-heading text-2xl font-semibold text-foreground">
                    Start with what feels manageable
                  </h2>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                    You do not need a perfect plan. Start with one quick next step or begin a
                    gentle support program that checks in with you over time.
                  </p>

                  <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
                    <Button
                      variant="hero"
                      onClick={() => quickPlanMutation.mutate()}
                      disabled={quickPlanMutation.isPending}
                    >
                      <Plus className="h-4 w-4" />
                      Create quick plan
                    </Button>
                    <Button variant="soft" asChild>
                      <Link href="/app/programs">
                        Start a support program
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
                <section className="rounded-3xl border border-border bg-card p-5 shadow-card">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                      <h2 className="font-heading text-xl font-semibold text-foreground">
                        Quick Plans
                      </h2>
                      <p className="mt-1 text-sm text-muted-foreground">
                        One-time actions you can return to whenever you need direction.
                      </p>
                    </div>
                    <Button
                      variant="soft"
                      size="sm"
                      onClick={() => quickPlanMutation.mutate()}
                      disabled={quickPlanMutation.isPending}
                    >
                      <Plus className="h-4 w-4" />
                      Add plan
                    </Button>
                  </div>

                  {actionPlansQuery.isLoading ? (
                    <div className="rounded-xl border border-border bg-background p-4 text-sm text-muted-foreground">
                      Loading quick plans...
                    </div>
                  ) : actionPlans.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-border bg-background p-5">
                      <p className="text-sm font-medium text-foreground">No quick plans yet</p>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Create one when you want a clear next action without setting up a full
                        support routine.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {actionPlans.map((item) => (
                        <div
                          key={item.id}
                          className="rounded-2xl border border-border bg-background p-4"
                        >
                          <div className="flex items-start gap-3">
                            <div className="pt-0.5">
                              {item.is_completed ? (
                                <CheckCircle2 className="h-5 w-5 text-safe" />
                              ) : (
                                <Circle className="h-5 w-5 text-muted-foreground" />
                              )}
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="flex flex-wrap items-center gap-2">
                                <p className="font-medium text-foreground">{item.title}</p>
                                <span
                                  className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                                    item.is_completed
                                      ? "bg-safe/15 text-safe"
                                      : "bg-muted text-muted-foreground"
                                  }`}
                                >
                                  {item.is_completed ? "Completed" : "In progress"}
                                </span>
                              </div>
                              {item.description ? (
                                <p className="mt-1 text-sm text-muted-foreground">
                                  {item.description}
                                </p>
                              ) : null}
                              {item.timeframe ? (
                                <p className="mt-2 text-xs text-muted-foreground">
                                  Best for: {item.timeframe}
                                </p>
                              ) : null}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                <section className="rounded-3xl border border-border bg-card p-5 shadow-card">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                      <h2 className="font-heading text-xl font-semibold text-foreground">
                        Support Programs
                      </h2>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Ongoing support with steps, adherence, and upcoming check-ins.
                      </p>
                    </div>
                    <Button asChild variant="soft" size="sm">
                      <Link href="/app/programs">Open all</Link>
                    </Button>
                  </div>

                  {carePlansQuery.isLoading ? (
                    <div className="rounded-xl border border-border bg-background p-4 text-sm text-muted-foreground">
                      Loading support programs...
                    </div>
                  ) : latestSupportProgram ? (
                    <div className="rounded-2xl border border-primary/20 bg-primary/5 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-xs font-medium uppercase tracking-wide text-primary">
                            Current program
                          </p>
                          <h3 className="mt-1 font-heading text-lg font-semibold text-foreground">
                            {latestSupportProgram.title}
                          </h3>
                          {latestSupportProgram.description ? (
                            <p className="mt-2 text-sm text-muted-foreground">
                              {latestSupportProgram.description}
                            </p>
                          ) : null}
                        </div>
                        <span className="rounded-full bg-background px-2.5 py-1 text-xs font-medium text-foreground">
                          {latestSupportProgram.status === "active"
                            ? "Active"
                            : latestSupportProgram.status === "completed"
                              ? "Completed"
                              : "Paused"}
                        </span>
                      </div>

                      <div className="mt-4 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-xl border border-border bg-background p-3">
                          <p className="text-xs text-muted-foreground">Next step</p>
                          <p className="mt-1 text-sm font-medium text-foreground">
                            {latestSupportProgram.current_step_key
                              ? latestSupportProgram.current_step_key.replaceAll("_", " ")
                              : "No current step"}
                          </p>
                        </div>
                        <div className="rounded-xl border border-border bg-background p-3">
                          <p className="text-xs text-muted-foreground">Upcoming check-in</p>
                          <p className="mt-1 text-sm font-medium text-foreground">
                            {formatDateTime(latestSupportProgram.next_check_in_at)}
                          </p>
                        </div>
                      </div>

                      <div className="mt-4">
                        <Button asChild variant="hero" className="w-full">
                          <Link href="/app/programs">
                            Continue program
                            <ArrowRight className="h-4 w-4" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-xl border border-dashed border-border bg-background p-5">
                      <p className="text-sm font-medium text-foreground">No active program yet</p>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Start a recurring support program when you want gentle follow-through,
                        progress tracking, and regular check-ins.
                      </p>
                      <Button asChild className="mt-4" variant="soft">
                        <Link href="/app/programs">Start a support program</Link>
                      </Button>
                    </div>
                  )}

                  {(latestQuickPlan || latestSupportProgram) && (
                    <div className="mt-5 rounded-2xl border border-border bg-background p-4">
                      <h3 className="font-semibold text-foreground">Recent support summary</h3>
                      <div className="mt-3 space-y-3">
                        {latestQuickPlan ? (
                          <div className="rounded-xl border border-border px-3 py-3">
                            <p className="text-xs text-muted-foreground">Most recent quick plan</p>
                            <p className="mt-1 text-sm font-medium text-foreground">
                              {latestQuickPlan.title}
                            </p>
                          </div>
                        ) : null}

                        {latestSupportProgram ? (
                          <div className="rounded-xl border border-border px-3 py-3">
                            <p className="text-xs text-muted-foreground">Most recent support program</p>
                            <p className="mt-1 text-sm font-medium text-foreground">
                              {latestSupportProgram.title}
                            </p>
                            <p className="mt-1 text-xs text-muted-foreground">
                              {cadenceLabel(latestSupportProgram.cadence_json)} · Next check-in{" "}
                              {formatDateTime(latestSupportProgram.next_check_in_at)}
                            </p>
                          </div>
                        ) : null}
                      </div>
                    </div>
                  )}
                </section>
              </div>
            )}

            {(quickPlanMutation.isError ||
              actionPlansQuery.isError ||
              carePlansQuery.isError ||
              refineProgramMutation.isError ||
              lifecycleMutation.isError) && (
              <div className="mt-6 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
                {getApiErrorMessage(
                  quickPlanMutation.error ||
                    actionPlansQuery.error ||
                    carePlansQuery.error ||
                    refineProgramMutation.error ||
                    lifecycleMutation.error,
                )}
              </div>
            )}
          </>
        )}
      </motion.div>
    </div>
  );
}