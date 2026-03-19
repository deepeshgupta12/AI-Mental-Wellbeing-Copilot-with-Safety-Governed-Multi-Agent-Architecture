"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { getAdminAnalyticsOverview } from "@/lib/admin-api";

export default function AnalyticsPage() {
  const analyticsQuery = useQuery({
    queryKey: ["admin-analytics-overview"],
    queryFn: getAdminAnalyticsOverview,
  });

  const data = analyticsQuery.data;

  const sections: Array<[string, Record<string, number>]> = data
    ? [
        ["Runtime Status", data.runtime_status_breakdown],
        ["Specialist Agents", data.specialist_agent_breakdown],
        ["Support Strategies", data.support_strategy_breakdown],
        ["Follow-up Status", data.follow_up_status_breakdown],
      ]
    : [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Analytics Warehouse Views
        </h1>

        {!data ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading analytics overview...
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-2">
            {sections.map(([title, values]) => (
              <div key={title} className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  {title}
                </h2>
                <div className="space-y-2">
                  {Object.entries(values).length === 0 ? (
                    <div className="text-sm text-muted-foreground">No data available.</div>
                  ) : (
                    Object.entries(values).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm text-muted-foreground">{value}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ))}

            <div className="rounded-lg border border-border bg-card p-4 shadow-card lg:col-span-2">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Intervention Outcome Overview
              </h2>
              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
                {JSON.stringify(data.intervention_overview, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}