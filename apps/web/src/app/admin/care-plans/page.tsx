"use client";

import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  Filter,
  PauseCircle,
  Workflow,
} from "lucide-react";

import { getApiErrorMessage } from "@/lib/api-client";
import {
  getAdminCarePlanEvents,
  getAdminCarePlanOverview,
  getAdminCarePlans,
} from "@/lib/care-plans-api";

function formatDateTime(value: string | null | undefined) {
  if (!value) return "Not scheduled";
  return new Date(value).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatStepLabel(value: string | null | undefined) {
  if (!value) return "No current step";
  return value.replaceAll("_", " ");
}

export default function AdminCarePlansPage() {
  const [organizationId, setOrganizationId] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [languageFilter, setLanguageFilter] = useState("all");
  const [programFilter, setProgramFilter] = useState("all");
  const [attentionFilter, setAttentionFilter] = useState("all");

  const overviewQuery = useQuery({
    queryKey: ["admin-care-plan-overview", organizationId],
    queryFn: () => getAdminCarePlanOverview(organizationId || null),
  });

  const carePlansQuery = useQuery({
    queryKey: ["admin-care-plans", organizationId],
    queryFn: () => getAdminCarePlans({ organizationId: organizationId || null, limit: 300 }),
  });

  const eventsQuery = useQuery({
    queryKey: ["admin-care-plan-events", organizationId],
    queryFn: () => getAdminCarePlanEvents({ limit: 20 }),
  });

  const allPlans = carePlansQuery.data ?? [];

  const languageOptions = useMemo(
    () => Array.from(new Set(allPlans.map((item) => item.preferred_language))).sort(),
    [allPlans],
  );

  const programOptions = useMemo(
    () => Array.from(new Set(allPlans.map((item) => item.program_key))).sort(),
    [allPlans],
  );

  const now = Date.now();

  const filteredPlans = useMemo(() => {
    return allPlans.filter((item) => {
      const avgScore =
        typeof item.adherence_json?.avg_score === "number" ? item.adherence_json.avg_score : null;
      const overdue =
        item.status === "active" &&
        !!item.next_check_in_at &&
        new Date(item.next_check_in_at).getTime() < now;
      const atRisk = item.status === "active" && (overdue || (avgScore !== null && avgScore < 0.6));

      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      if (languageFilter !== "all" && item.preferred_language !== languageFilter) return false;
      if (programFilter !== "all" && item.program_key !== programFilter) return false;

      if (attentionFilter === "overdue" && !overdue) return false;
      if (attentionFilter === "at_risk" && !atRisk) return false;
      if (attentionFilter === "on_track" && (overdue || atRisk || item.status !== "active")) {
        return false;
      }

      return true;
    });
  }, [allPlans, statusFilter, languageFilter, programFilter, attentionFilter, now]);

  const overduePlans = useMemo(() => {
    return filteredPlans.filter(
      (item) =>
        item.status === "active" &&
        !!item.next_check_in_at &&
        new Date(item.next_check_in_at).getTime() < now,
    );
  }, [filteredPlans, now]);

  const atRiskPlans = useMemo(() => {
    return filteredPlans.filter((item) => {
      const avgScore =
        typeof item.adherence_json?.avg_score === "number" ? item.adherence_json.avg_score : null;
      const overdue =
        item.status === "active" &&
        !!item.next_check_in_at &&
        new Date(item.next_check_in_at).getTime() < now;
      return item.status === "active" && (overdue || (avgScore !== null && avgScore < 0.6));
    });
  }, [filteredPlans, now]);

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
              <Workflow className="h-3.5 w-3.5" />
              Support program operations
            </div>
            <h1 className="font-heading text-3xl font-bold text-foreground">Care Programs</h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">
              Track ongoing support programs, spot stalled momentum, and review recent support
              activity without digging through raw tables first.
            </p>
          </div>

          <label className="space-y-2">
            <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Organization filter
            </span>
            <input
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              placeholder="Optional organization ID"
              className="w-full min-w-[260px] rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
            />
          </label>
        </div>

        <div className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Total programs</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.total_care_plans ?? "—"}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Active</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.active_care_plans ?? "—"}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Paused</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.paused_care_plans ?? "—"}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Overdue</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.overdue_check_ins ?? "—"}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">At risk</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.at_risk_care_plans ?? "—"}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Needs attention</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.needs_attention_count ?? "—"}
            </p>
          </div>
        </div>

        <div className="mb-6 rounded-3xl border border-border bg-card p-5 shadow-card">
          <div className="mb-4 flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <h2 className="font-heading text-xl font-semibold text-foreground">Operational filters</h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <label className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Status
              </span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                <option value="all">All programs</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Language
              </span>
              <select
                value={languageFilter}
                onChange={(e) => setLanguageFilter(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                <option value="all">All languages</option>
                {languageOptions.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Program type
              </span>
              <select
                value={programFilter}
                onChange={(e) => setProgramFilter(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                <option value="all">All program keys</option>
                {programOptions.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Attention state
              </span>
              <select
                value={attentionFilter}
                onChange={(e) => setAttentionFilter(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                <option value="all">All attention states</option>
                <option value="overdue">Overdue</option>
                <option value="at_risk">At risk</option>
                <option value="on_track">On track</option>
              </select>
            </label>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <section className="space-y-6">
            <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
              <div className="mb-4 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                <h2 className="font-heading text-xl font-semibold text-foreground">
                  Overdue now
                </h2>
              </div>

              {carePlansQuery.isLoading ? (
                <div className="rounded-xl border border-border bg-background p-4 text-sm text-muted-foreground">
                  Loading programs...
                </div>
              ) : overduePlans.length === 0 ? (
                <div className="rounded-xl border border-dashed border-border bg-background p-5">
                  <p className="text-sm font-medium text-foreground">No overdue programs in this view</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    This usually means timing is healthy for the currently filtered set.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {overduePlans.slice(0, 6).map((plan) => (
                    <div key={plan.id} className="rounded-2xl border border-border bg-background p-4">
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="font-semibold text-foreground">{plan.title}</p>
                            <span className="rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-medium text-primary">
                              Active
                            </span>
                          </div>
                          <div className="mt-3 grid gap-3 sm:grid-cols-3">
                            <div>
                              <p className="text-xs text-muted-foreground">Current step</p>
                              <p className="mt-1 text-sm text-foreground">
                                {formatStepLabel(plan.current_step_key)}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Next check-in</p>
                              <p className="mt-1 text-sm text-foreground">
                                {formatDateTime(plan.next_check_in_at)}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Average adherence</p>
                              <p className="mt-1 text-sm text-foreground">
                                {typeof plan.adherence_json?.avg_score === "number"
                                  ? `${Math.round(plan.adherence_json.avg_score * 100)}%`
                                  : "No signal yet"}
                              </p>
                            </div>
                          </div>
                        </div>

                        <span className="inline-flex items-center gap-1 rounded-full bg-urgent/10 px-2.5 py-1 text-[11px] font-medium text-urgent">
                          <CalendarClock className="h-3.5 w-3.5" />
                          Needs re-entry
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
              <div className="mb-4 flex items-center gap-2">
                <Workflow className="h-4 w-4 text-muted-foreground" />
                <h2 className="font-heading text-xl font-semibold text-foreground">
                  At-risk programs
                </h2>
              </div>

              {carePlansQuery.isLoading ? (
                <div className="rounded-xl border border-border bg-background p-4 text-sm text-muted-foreground">
                  Loading programs...
                </div>
              ) : atRiskPlans.length === 0 ? (
                <div className="rounded-xl border border-dashed border-border bg-background p-5">
                  <p className="text-sm font-medium text-foreground">No at-risk programs in this view</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Adherence looks stable for the currently filtered set.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {atRiskPlans.slice(0, 6).map((plan) => (
                    <div key={plan.id} className="rounded-2xl border border-border bg-background p-4">
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="font-semibold text-foreground">{plan.title}</p>
                            <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-[11px] font-medium text-amber-600">
                              At risk
                            </span>
                          </div>
                          <div className="mt-3 grid gap-3 sm:grid-cols-3">
                            <div>
                              <p className="text-xs text-muted-foreground">Program key</p>
                              <p className="mt-1 text-sm text-foreground">{plan.program_key}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Language</p>
                              <p className="mt-1 text-sm text-foreground">{plan.preferred_language}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Average adherence</p>
                              <p className="mt-1 text-sm text-foreground">
                                {typeof plan.adherence_json?.avg_score === "number"
                                  ? `${Math.round(plan.adherence_json.avg_score * 100)}%`
                                  : "No signal yet"}
                              </p>
                            </div>
                          </div>
                        </div>

                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2.5 py-1 text-[11px] font-medium text-amber-600">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          Review timing or framing
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          <section className="space-y-6">
            <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
              <div className="mb-4 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                <h2 className="font-heading text-xl font-semibold text-foreground">
                  How to read this screen
                </h2>
              </div>

              <div className="space-y-3 text-sm text-muted-foreground">
                <p>
                  <span className="font-medium text-foreground">Overdue</span> means a live program
                  has passed its next expected check-in time.
                </p>
                <p>
                  <span className="font-medium text-foreground">At risk</span> means adherence looks
                  weak or the program is drifting toward missed follow-through.
                </p>
                <p>
                  <span className="font-medium text-foreground">Paused</span> means the routine was
                  intentionally stopped and may need a softer re-entry path later.
                </p>
              </div>
            </div>

            <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
              <h2 className="font-heading text-xl font-semibold text-foreground">
                Recent activity
              </h2>

              {eventsQuery.isLoading ? (
                <div className="mt-4 rounded-xl border border-border bg-background p-4 text-sm text-muted-foreground">
                  Loading recent events...
                </div>
              ) : (
                <div className="mt-4 space-y-3">
                  {(eventsQuery.data ?? []).slice(0, 10).map((event) => (
                    <div
                      key={event.id}
                      className="rounded-xl border border-border bg-background px-4 py-3"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium text-foreground">{event.event_type}</p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            Step: {formatStepLabel(event.step_key)}
                          </p>
                          {event.notes ? (
                            <p className="mt-1 text-sm text-muted-foreground">{event.notes}</p>
                          ) : null}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {formatDateTime(event.created_at)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
              <h2 className="font-heading text-xl font-semibold text-foreground">
                Current filtered view
              </h2>
              <div className="mt-4 space-y-2">
                {filteredPlans.slice(0, 8).map((plan) => (
                  <div
                    key={plan.id}
                    className="flex items-center justify-between rounded-xl border border-border bg-background px-4 py-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-foreground">{plan.title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {plan.program_key} · {plan.preferred_language}
                      </p>
                    </div>

                    {plan.status === "active" ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-medium text-primary">
                        <CalendarClock className="h-3.5 w-3.5" />
                        Active
                      </span>
                    ) : plan.status === "paused" ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1 text-[11px] font-medium text-muted-foreground">
                        <PauseCircle className="h-3.5 w-3.5" />
                        Paused
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-safe/15 px-2.5 py-1 text-[11px] font-medium text-safe">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Completed
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>

        {(overviewQuery.isError || carePlansQuery.isError || eventsQuery.isError) && (
          <div className="mt-6 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
            {getApiErrorMessage(
              overviewQuery.error || carePlansQuery.error || eventsQuery.error,
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}