"use client";

import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CalendarClock,
  CheckCircle2,
  PauseCircle,
  PlayCircle,
  RefreshCcw,
  RotateCcw,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { getApiErrorMessage } from "@/lib/api-client";
import {
  advanceCarePlan,
  createCarePlan,
  createCarePlanEvent,
  listCarePlans,
  updateCarePlan,
} from "@/lib/care-plans-api";
import { getCurrentUserId } from "@/lib/demo-session";

function formatStepLabel(value: string | null | undefined) {
  if (!value) return "No current step";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return "Not scheduled yet";
  return new Date(value).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  });
}

function progressPercent(value: unknown) {
  if (!value || typeof value !== "object") return 0;
  const raw = (value as { completion_pct?: number }).completion_pct;
  return typeof raw === "number" ? raw : 0;
}

function adherenceScore(value: unknown) {
  if (!value || typeof value !== "object") return null;
  const raw = (value as { avg_score?: number | null }).avg_score;
  return typeof raw === "number" ? raw : null;
}

export default function ProgramsPage() {
  const userId = getCurrentUserId();
  const queryClient = useQueryClient();

  const carePlansQuery = useQuery({
    queryKey: ["care-plans", userId],
    queryFn: () => listCarePlans({ userId: userId! }),
    enabled: !!userId,
  });

  const createProgramMutation = useMutation({
    mutationFn: async () =>
      createCarePlan({
        user_id: userId!,
        source_agent: "habit_care_plan",
        program_key: "steady_support_program",
        title: "Steady Support Program",
        description:
          "A gentle recurring program for staying consistent with your next helpful steps.",
        preferred_language: "en",
        timezone: "Asia/Kolkata",
        cadence_json: { every_n_days: 3 },
        sequence_json: {
          steps: [
            { key: "stabilize", order: 1 },
            { key: "practice", order: 2 },
            { key: "review", order: 3 },
          ],
        },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
    },
  });

  const markCheckInMutation = useMutation({
    mutationFn: async (carePlanId: string) =>
      createCarePlanEvent(carePlanId, {
        user_id: userId!,
        event_type: "check_in",
        event_status: "completed",
        adherence_score: 1,
        notes: "Marked complete from the program screen.",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
    },
  });

  const advanceMutation = useMutation({
    mutationFn: async (carePlanId: string) =>
      advanceCarePlan(carePlanId, {
        notes: "Moved to the next step from the member experience.",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
    },
  });

  const statusMutation = useMutation({
    mutationFn: async ({ carePlanId, status }: { carePlanId: string; status: string }) =>
      updateCarePlan(carePlanId, { status }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["care-plans", userId] });
    },
  });

  const carePlans = carePlansQuery.data ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
              <RefreshCcw className="h-3.5 w-3.5" />
              Recurring support
            </div>
            <h1 className="font-heading text-3xl font-bold text-foreground">Support Programs</h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              These are ongoing routines that help you stay supported over time. You can track
              progress, check in, pause, resume, and continue from the next step.
            </p>
          </div>

          <Button
            variant="hero"
            onClick={() => createProgramMutation.mutate()}
            disabled={!userId || createProgramMutation.isPending}
          >
            Start a support program
          </Button>
        </div>

        {!userId ? (
          <div className="rounded-2xl border border-border bg-card p-5 text-sm text-muted-foreground shadow-card">
            No active user session found. Please complete onboarding first.
          </div>
        ) : carePlansQuery.isLoading ? (
          <div className="rounded-2xl border border-border bg-card p-5 text-sm text-muted-foreground shadow-card">
            Loading support programs...
          </div>
        ) : carePlans.length === 0 ? (
          <div className="rounded-3xl border border-border bg-card p-8 shadow-card">
            <div className="mx-auto max-w-2xl text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <Sparkles className="h-7 w-7" />
              </div>
              <h2 className="font-heading text-2xl font-semibold text-foreground">
                No support program yet
              </h2>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                Start one when you want gentle follow-through, recurring check-ins, and a clearer
                sense of momentum.
              </p>
              <Button
                className="mt-6"
                variant="hero"
                onClick={() => createProgramMutation.mutate()}
                disabled={createProgramMutation.isPending}
              >
                Start a support program
              </Button>
            </div>
          </div>
        ) : (
          <div className="grid gap-5">
            {carePlans.map((plan) => {
              const progress = progressPercent(plan.progress_json);
              const adherence = adherenceScore(plan.adherence_json);
              const isPaused = plan.status === "paused";
              const isCompleted = plan.status === "completed";

              return (
                <section
                  key={plan.id}
                  className="rounded-3xl border border-border bg-card p-5 shadow-card"
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="max-w-3xl">
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="font-heading text-xl font-semibold text-foreground">
                          {plan.title}
                        </h2>
                        <span
                          className={`rounded-full px-2.5 py-1 text-[11px] font-medium ${
                            plan.status === "active"
                              ? "bg-primary/10 text-primary"
                              : plan.status === "completed"
                                ? "bg-safe/15 text-safe"
                                : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {plan.status === "active"
                            ? "Active"
                            : plan.status === "completed"
                              ? "Completed"
                              : "Paused"}
                        </span>
                      </div>

                      {plan.description ? (
                        <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>
                      ) : null}

                      <div className="mt-4 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-xl border border-border bg-background p-4">
                          <p className="text-xs text-muted-foreground">Current step</p>
                          <p className="mt-1 text-sm font-medium text-foreground">
                            {formatStepLabel(plan.current_step_key)}
                          </p>
                        </div>
                        <div className="rounded-xl border border-border bg-background p-4">
                          <p className="text-xs text-muted-foreground">Upcoming check-in</p>
                          <p className="mt-1 text-sm font-medium text-foreground">
                            {formatDateTime(plan.next_check_in_at)}
                          </p>
                        </div>
                        <div className="rounded-xl border border-border bg-background p-4">
                          <p className="text-xs text-muted-foreground">Average adherence</p>
                          <p className="mt-1 text-sm font-medium text-foreground">
                            {adherence !== null ? `${Math.round(adherence * 100)}%` : "No check-ins yet"}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="min-w-[260px] rounded-2xl border border-border bg-background p-4">
                      <p className="text-xs text-muted-foreground">Progress</p>
                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary"
                          style={{ width: `${Math.min(progress, 100)}%` }}
                        />
                      </div>
                      <p className="mt-2 text-sm font-medium text-foreground">
                        {progress.toFixed(0)}% complete
                      </p>

                      <div className="mt-4 flex flex-col gap-2">
                        <Button
                          variant="hero"
                          onClick={() => markCheckInMutation.mutate(plan.id)}
                          disabled={
                            markCheckInMutation.isPending || isPaused || isCompleted || !userId
                          }
                        >
                          <CheckCircle2 className="h-4 w-4" />
                          Mark today’s check-in
                        </Button>

                        <Button
                          variant="soft"
                          onClick={() => advanceMutation.mutate(plan.id)}
                          disabled={advanceMutation.isPending || isPaused || isCompleted}
                        >
                          <CalendarClock className="h-4 w-4" />
                          Move to next step
                        </Button>

                        {isPaused ? (
                          <Button
                            variant="outline"
                            onClick={() =>
                              statusMutation.mutate({ carePlanId: plan.id, status: "active" })
                            }
                            disabled={statusMutation.isPending}
                          >
                            <PlayCircle className="h-4 w-4" />
                            Resume program
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            onClick={() =>
                              statusMutation.mutate({ carePlanId: plan.id, status: "paused" })
                            }
                            disabled={statusMutation.isPending || isCompleted}
                          >
                            <PauseCircle className="h-4 w-4" />
                            Pause program
                          </Button>
                        )}

                        <Button
                          variant="ghost"
                          onClick={() =>
                            statusMutation.mutate({ carePlanId: plan.id, status: "active" })
                          }
                          disabled={statusMutation.isPending}
                        >
                          <RotateCcw className="h-4 w-4" />
                          Re-activate gently
                        </Button>
                      </div>
                    </div>
                  </div>
                </section>
              );
            })}
          </div>
        )}

        {(carePlansQuery.isError ||
          createProgramMutation.isError ||
          markCheckInMutation.isError ||
          advanceMutation.isError ||
          statusMutation.isError) && (
          <div className="mt-6 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
            {getApiErrorMessage(
              carePlansQuery.error ||
                createProgramMutation.error ||
                markCheckInMutation.error ||
                advanceMutation.error ||
                statusMutation.error,
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}