"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminEscalationAnalytics,
  getAdminOpsOverview,
  getAdminReviewerDashboard,
} from "@/lib/admin-api";

export default function AdminDashboard() {
  const opsQuery = useQuery({
    queryKey: ["admin-ops-overview"],
    queryFn: getAdminOpsOverview,
  });

  const reviewerDashboardQuery = useQuery({
    queryKey: ["admin-reviewer-dashboard"],
    queryFn: getAdminReviewerDashboard,
  });

  const escalationAnalyticsQuery = useQuery({
    queryKey: ["admin-escalation-analytics"],
    queryFn: getAdminEscalationAnalytics,
  });

  const data = opsQuery.data;
  const reviewer = reviewerDashboardQuery.data;
  const escalation = escalationAnalyticsQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Operations Overview
        </h1>

        {!data ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading operational overview...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {[
                { label: "Unresolved Flags", value: data.unresolved_flags },
                { label: "Trace Events", value: data.total_traces },
                { label: "Intervention Logs", value: data.total_intervention_logs },
                { label: "Follow-up Plans", value: data.total_follow_up_plans },
                { label: "Follow-up Events", value: data.total_follow_up_events },
                { label: "Active Configs", value: data.active_config_versions },
                { label: "Total Flags", value: data.total_flags },
                {
                  label: "Avg Intervention Rating",
                  value: data.intervention_overview.avg_effectiveness_rating ?? "—",
                },
              ].map((item) => (
                <div key={item.label} className="rounded-lg border border-border bg-card p-4 shadow-card">
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Safety Queue</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {reviewer?.queued_events ?? "—"}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Safety In Review</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {reviewer?.in_review_events ?? "—"}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">High Risk Events</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {escalation?.high_risk_events ?? "—"}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Critical Events</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {escalation?.critical_events ?? "—"}
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Latest Runtime Executions
                </h2>
                <div className="space-y-3">
                  {data.latest_runtime_executions.length === 0 ? (
                    <div className="text-sm text-muted-foreground">
                      No runtime executions available.
                    </div>
                  ) : (
                    data.latest_runtime_executions.slice(0, 8).map((item) => (
                      <div key={item.trace_name} className="rounded-md border border-border bg-background p-3">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <div className="font-mono text-xs text-foreground">
                              {item.trace_name}
                            </div>
                            <div className="mt-1 text-xs text-muted-foreground">
                              {item.agents.join(" → ")}
                            </div>
                          </div>
                          <div className="text-right text-xs text-muted-foreground">
                            <div>{item.event_count} events</div>
                            <div>{new Date(item.latest_at).toLocaleString()}</div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Safety Review Snapshot
                </h2>
                <div className="space-y-3">
                  {!reviewer ? (
                    <div className="text-sm text-muted-foreground">
                      Loading reviewer queue snapshot...
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                        <span className="text-sm text-foreground">Queued events</span>
                        <span className="text-sm text-muted-foreground">
                          {reviewer.queued_events}
                        </span>
                      </div>
                      <div className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                        <span className="text-sm text-foreground">In review</span>
                        <span className="text-sm text-muted-foreground">
                          {reviewer.in_review_events}
                        </span>
                      </div>
                      <div className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                        <span className="text-sm text-foreground">Resolved</span>
                        <span className="text-sm text-muted-foreground">
                          {reviewer.resolved_events}
                        </span>
                      </div>
                      <div className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                        <span className="text-sm text-foreground">Escalated events</span>
                        <span className="text-sm text-muted-foreground">
                          {escalation?.escalated_events ?? "—"}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Intervention Outcome Snapshot
                </h2>
                <div className="space-y-3">
                  {Object.entries(data.intervention_overview.outcome_status_breakdown).length === 0 ? (
                    <div className="text-sm text-muted-foreground">
                      No intervention outcomes available.
                    </div>
                  ) : (
                    Object.entries(data.intervention_overview.outcome_status_breakdown).map(
                      ([key, value]) => (
                        <div
                          key={key}
                          className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2"
                        >
                          <span className="text-sm text-foreground">{key}</span>
                          <span className="text-sm text-muted-foreground">{value}</span>
                        </div>
                      ),
                    )
                  )}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Escalation Breakdown
                </h2>
                <div className="space-y-3">
                  {!escalation || Object.keys(escalation.event_type_breakdown).length === 0 ? (
                    <div className="text-sm text-muted-foreground">
                      No escalation analytics available.
                    </div>
                  ) : (
                    Object.entries(escalation.event_type_breakdown).map(([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2"
                      >
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm text-muted-foreground">{value}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}