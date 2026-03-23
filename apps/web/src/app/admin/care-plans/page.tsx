"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { getAdminCarePlanEvents, getAdminCarePlanOverview, getAdminCarePlans } from "@/lib/care-plans-api";

export default function AdminCarePlansPage() {
  const [organizationId, setOrganizationId] = useState("");

  const overviewQuery = useQuery({
    queryKey: ["admin-care-plan-overview", organizationId],
    queryFn: () => getAdminCarePlanOverview(organizationId || null),
  });

  const plansQuery = useQuery({
    queryKey: ["admin-care-plans", organizationId],
    queryFn: () => getAdminCarePlans(organizationId || null),
  });

  const eventsQuery = useQuery({
    queryKey: ["admin-care-plan-events"],
    queryFn: () => getAdminCarePlanEvents(),
  });

  const overview = overviewQuery.data;
  const plans = plansQuery.data ?? [];
  const events = eventsQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">Care Plans</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Monitor recurring programs, adherence, sequence progression, language usage, and recent care-plan events.
          </p>
        </div>

        <div className="mb-6 rounded-lg border border-border bg-card p-4 shadow-card">
          <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Organization filter
          </label>
          <input
            value={organizationId}
            onChange={(e) => setOrganizationId(e.target.value)}
            placeholder="Filter by organization ID"
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
          />
        </div>

        {!overview ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading care-plan overview...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-6">
              {[
                { label: "Total", value: overview.total_care_plans },
                { label: "Active", value: overview.active_care_plans },
                { label: "Completed", value: overview.completed_care_plans },
                { label: "Paused", value: overview.paused_care_plans },
                { label: "Overdue", value: overview.overdue_check_ins },
                { label: "Avg Adherence", value: overview.avg_adherence_score ?? "—" },
              ].map((item) => (
                <div key={item.label} className="rounded-lg border border-border bg-card p-4 shadow-card">
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="mt-2 font-heading text-2xl font-bold text-foreground">{item.value}</div>
                </div>
              ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Status Breakdown</h2>
                <div className="space-y-2">
                  {Object.entries(overview.status_breakdown).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                      <span className="text-sm text-foreground">{key}</span>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Program Breakdown</h2>
                <div className="space-y-2">
                  {Object.entries(overview.program_breakdown).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                      <span className="text-sm text-foreground">{key}</span>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Language Breakdown</h2>
                <div className="space-y-2">
                  {Object.entries(overview.language_breakdown).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                      <span className="text-sm text-foreground">{key}</span>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Care Plans</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left">
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Title</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Program</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Status</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Step</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Language</th>
                    </tr>
                  </thead>
                  <tbody>
                    {plans.map((item) => (
                      <tr key={item.id} className="border-b border-border last:border-0">
                        <td className="px-3 py-3 text-foreground">{item.title}</td>
                        <td className="px-3 py-3 text-muted-foreground">{item.program_key}</td>
                        <td className="px-3 py-3 text-muted-foreground">{item.status}</td>
                        <td className="px-3 py-3 text-muted-foreground">{item.current_step_key ?? "—"}</td>
                        <td className="px-3 py-3 text-muted-foreground">{item.preferred_language}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Recent Care Plan Events</h2>
              <div className="space-y-3">
                {events.slice(0, 12).map((item) => (
                  <div key={item.id} className="rounded-md border border-border bg-background p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-medium text-foreground">{item.event_type}</div>
                      <div className="text-xs text-muted-foreground">{item.event_status ?? "—"}</div>
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      step: {item.step_key ?? "—"} · adherence: {item.adherence_score ?? "—"}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}