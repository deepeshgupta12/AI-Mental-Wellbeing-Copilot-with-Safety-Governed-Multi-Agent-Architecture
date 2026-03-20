"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { getAdminEscalationAnalytics } from "@/lib/admin-api";

export default function EscalationAnalyticsPage() {
  const analyticsQuery = useQuery({
    queryKey: ["admin-escalation-analytics"],
    queryFn: getAdminEscalationAnalytics,
  });

  const data = analyticsQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Escalation Analytics
        </h1>

        {!data ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading escalation analytics...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {[
                { label: "Total Events", value: data.total_events },
                { label: "Escalated", value: data.escalated_events },
                { label: "High Risk", value: data.high_risk_events },
                { label: "Critical", value: data.critical_events },
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
                Event Type Breakdown
              </h2>
              <div className="space-y-2">
                {Object.entries(data.event_type_breakdown).length === 0 ? (
                  <div className="text-sm text-muted-foreground">No escalation analytics available.</div>
                ) : (
                  Object.entries(data.event_type_breakdown).map(([key, value]) => (
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
        )}
      </motion.div>
    </div>
  );
}