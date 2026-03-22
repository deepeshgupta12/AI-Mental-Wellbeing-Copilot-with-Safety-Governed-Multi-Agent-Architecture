"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminEnterpriseAnalyticsOverview,
  getAdminEnterpriseOrganizationDetail,
  getAdminEnterpriseOrganizations,
  getAdminReviewerProductivityOverview,
} from "@/lib/admin-api";

const WINDOW_OPTIONS = [7, 14, 30, 60, 90] as const;

function StatCard({ label, value, helper }: { label: string; value: string | number; helper?: string }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 shadow-card">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-2 font-heading text-2xl font-bold text-foreground">{value}</div>
      {helper ? <div className="mt-1 text-xs text-muted-foreground">{helper}</div> : null}
    </div>
  );
}

function BreakdownTable({ title, values }: { title: string; values: Record<string, number> }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 shadow-card">
      <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">{title}</h2>
      <div className="space-y-2">
        {Object.entries(values).length === 0 ? (
          <div className="text-sm text-muted-foreground">No data available.</div>
        ) : (
          Object.entries(values).map(([key, value]) => (
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
  );
}

export default function EnterpriseAnalyticsPage() {
  const [selectedOrganizationId, setSelectedOrganizationId] = useState<string | null>(null);
  const [windowDays, setWindowDays] = useState<number>(30);

  const organizationsQuery = useQuery({
    queryKey: ["admin-enterprise-organizations"],
    queryFn: getAdminEnterpriseOrganizations,
  });

  const defaultOrganizationId = organizationsQuery.data?.[0]?.id ?? null;
  const activeOrganizationId = selectedOrganizationId ?? defaultOrganizationId;

  const overviewQuery = useQuery({
    queryKey: ["admin-enterprise-analytics-overview", activeOrganizationId, windowDays],
    queryFn: () => getAdminEnterpriseAnalyticsOverview(activeOrganizationId, windowDays),
    enabled: Boolean(activeOrganizationId),
  });

  const detailQuery = useQuery({
    queryKey: ["admin-enterprise-organization-detail", activeOrganizationId, windowDays],
    queryFn: () => getAdminEnterpriseOrganizationDetail(activeOrganizationId as string, windowDays),
    enabled: Boolean(activeOrganizationId),
  });

  const reviewerQuery = useQuery({
    queryKey: ["admin-reviewer-productivity-overview", activeOrganizationId, windowDays],
    queryFn: () => getAdminReviewerProductivityOverview(activeOrganizationId as string, windowDays),
    enabled: Boolean(activeOrganizationId),
  });

  const organizations = organizationsQuery.data ?? [];
  const overview = overviewQuery.data;
  const detail = detailQuery.data;
  const reviewerOverview = reviewerQuery.data;

  const activityTotals = useMemo(() => {
    const items = detail?.activity_trends ?? [];
    return items.reduce(
      (acc, item) => {
        acc.safety += item.safety_events;
        acc.interventions += item.interventions;
        acc.followUps += item.follow_up_events;
        return acc;
      },
      { safety: 0, interventions: 0, followUps: 0 },
    );
  }, [detail?.activity_trends]);

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="font-heading text-2xl font-bold text-foreground">Enterprise Analytics</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
              Org-aware Pack 4 dashboards covering operational KPIs, safety/intervention rollups,
              reviewer productivity, member segmentation, and activity windows.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Organization
              </label>
              <select
                value={activeOrganizationId ?? ""}
                onChange={(e) => setSelectedOrganizationId(e.target.value || null)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.name} ({org.slug})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Trend Window
              </label>
              <select
                value={windowDays}
                onChange={(e) => setWindowDays(Number(e.target.value))}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                {WINDOW_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    Last {option} days
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {!overview || !detail ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading enterprise analytics...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-6">
              <StatCard label="Organizations" value={overview.total_organizations} />
              <StatCard label="Active Orgs" value={overview.active_organizations} />
              <StatCard label="Members" value={detail.operational_kpis.member_count} />
              <StatCard label="Active Sessions" value={detail.operational_kpis.active_session_count} />
              <StatCard
                label="Review Completion"
                value={`${detail.operational_kpis.review_completion_rate_pct}%`}
              />
              <StatCard
                label="Avg Queue Age"
                value={`${detail.operational_kpis.avg_queue_age_hours}h`}
                helper={`Window: ${windowDays}d`}
              />
            </div>

            <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Organization Selector</h2>
                <div className="space-y-3">
                  {organizations.map((org) => {
                    const active = org.id === activeOrganizationId;
                    return (
                      <button
                        key={org.id}
                        type="button"
                        onClick={() => setSelectedOrganizationId(org.id)}
                        className={`w-full rounded-md border p-3 text-left transition-aether ${
                          active
                            ? "border-foreground/30 bg-foreground/5"
                            : "border-border bg-background hover:bg-muted/40"
                        }`}
                      >
                        <div className="text-sm font-medium text-foreground">{org.name}</div>
                        <div className="mt-1 text-xs text-muted-foreground">{org.slug}</div>
                        <div className="mt-2 text-[11px] text-muted-foreground">
                          {org.membership_count} memberships · {org.active_session_count} active sessions
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-6">
                <div className="grid gap-4 md:grid-cols-3">
                  <StatCard
                    label="Safety Events"
                    value={detail.operational_kpis.safety_event_count_window}
                    helper={`${detail.safety_rollup.high_risk_events} high risk`}
                  />
                  <StatCard
                    label="Interventions"
                    value={detail.operational_kpis.intervention_count_window}
                    helper={
                      detail.intervention_rollup.avg_effectiveness_rating != null
                        ? `Avg rating ${detail.intervention_rollup.avg_effectiveness_rating}`
                        : "No ratings yet"
                    }
                  />
                  <StatCard
                    label="Follow-up Events"
                    value={detail.operational_kpis.follow_up_event_count_window}
                    helper={`${detail.operational_kpis.follow_up_plan_count_window} plans`}
                  />
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <BreakdownTable
                    title="Membership Breakdown"
                    values={detail.membership_breakdown_by_role}
                  />
                  <BreakdownTable
                    title="Safety Queue Breakdown"
                    values={detail.safety_rollup.queue_status_breakdown}
                  />
                  <BreakdownTable
                    title="Safety Risk Breakdown"
                    values={detail.safety_rollup.risk_level_breakdown}
                  />
                  <BreakdownTable
                    title="Intervention Outcomes"
                    values={detail.intervention_rollup.outcome_status_breakdown}
                  />
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Reviewer Productivity
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Reviewer</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Reviews</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Resolved</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Completion</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Lag</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(reviewerOverview?.reviewers ?? detail.reviewer_productivity).length === 0 ? (
                        <tr>
                          <td colSpan={5} className="px-3 py-4 text-muted-foreground">
                            No reviewer activity for this organization and window.
                          </td>
                        </tr>
                      ) : (
                        (reviewerOverview?.reviewers ?? detail.reviewer_productivity).map((item) => (
                          <tr key={item.reviewer_id} className="border-b border-border last:border-0">
                            <td className="px-3 py-3 text-foreground">{item.reviewer_id}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.review_count}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.resolved_count}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.completion_rate_pct}%</td>
                            <td className="px-3 py-3 text-muted-foreground">
                              {item.avg_review_lag_hours != null ? `${item.avg_review_lag_hours}h` : "—"}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Recent Members
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Name</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Email</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Role</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.member_summaries.length === 0 ? (
                        <tr>
                          <td colSpan={4} className="px-3 py-4 text-muted-foreground">
                            No members found.
                          </td>
                        </tr>
                      ) : (
                        detail.member_summaries.map((item) => (
                          <tr key={item.membership_id} className="border-b border-border last:border-0">
                            <td className="px-3 py-3 text-foreground">
                              {item.display_name || item.user_id}
                            </td>
                            <td className="px-3 py-3 text-muted-foreground">{item.email || "—"}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.role_name || "—"}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.status}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Activity Window Summary
                </h2>
                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-md border border-border bg-background p-3">
                    <div className="text-xs text-muted-foreground">Safety</div>
                    <div className="mt-2 text-lg font-semibold text-foreground">{activityTotals.safety}</div>
                  </div>
                  <div className="rounded-md border border-border bg-background p-3">
                    <div className="text-xs text-muted-foreground">Interventions</div>
                    <div className="mt-2 text-lg font-semibold text-foreground">
                      {activityTotals.interventions}
                    </div>
                  </div>
                  <div className="rounded-md border border-border bg-background p-3">
                    <div className="text-xs text-muted-foreground">Follow-ups</div>
                    <div className="mt-2 text-lg font-semibold text-foreground">{activityTotals.followUps}</div>
                  </div>
                </div>
                <div className="mt-4 overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Date</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Safety</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Interventions</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Follow-ups</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.activity_trends.slice(-10).map((item) => (
                        <tr key={item.date} className="border-b border-border last:border-0">
                          <td className="px-3 py-3 text-foreground">{item.date}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.safety_events}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.interventions}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.follow_up_events}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Artifact Drill-down
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Scope</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Kind</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Provider</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Bytes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.recent_artifacts.length === 0 ? (
                        <tr>
                          <td colSpan={4} className="px-3 py-4 text-muted-foreground">
                            No recent artifacts linked to this organization’s member activity.
                          </td>
                        </tr>
                      ) : (
                        detail.recent_artifacts.map((item) => (
                          <tr key={item.id} className="border-b border-border last:border-0">
                            <td className="px-3 py-3 text-foreground">{item.scope_type}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.artifact_kind}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.storage_provider}</td>
                            <td className="px-3 py-3 text-muted-foreground">{item.byte_size}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
