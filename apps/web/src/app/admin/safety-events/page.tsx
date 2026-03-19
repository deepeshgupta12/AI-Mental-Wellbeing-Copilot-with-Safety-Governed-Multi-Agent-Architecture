"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminInterventionLogs,
  getAdminInterventionOverview,
} from "@/lib/admin-api";

export default function SessionLogsPage() {
  const logsQuery = useQuery({
    queryKey: ["admin-intervention-logs"],
    queryFn: getAdminInterventionLogs,
  });

  const overviewQuery = useQuery({
    queryKey: ["admin-intervention-overview"],
    queryFn: getAdminInterventionOverview,
  });

  const items = logsQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Intervention Outcome Logs
        </h1>

        {overviewQuery.data ? (
          <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <div className="text-xs text-muted-foreground">Total Logs</div>
              <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                {overviewQuery.data.total_logs}
              </div>
            </div>
            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <div className="text-xs text-muted-foreground">Avg Rating</div>
              <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                {overviewQuery.data.avg_effectiveness_rating ?? "—"}
              </div>
            </div>
            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <div className="text-xs text-muted-foreground">Types</div>
              <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                {Object.keys(overviewQuery.data.intervention_type_breakdown).length}
              </div>
            </div>
            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <div className="text-xs text-muted-foreground">Outcome States</div>
              <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                {Object.keys(overviewQuery.data.outcome_status_breakdown).length}
              </div>
            </div>
          </div>
        ) : null}

        <div className="overflow-hidden rounded-lg border border-border bg-card shadow-card">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left">
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Intervention</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Outcome</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Rating</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">User</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Created</th>
                </tr>
              </thead>
              <tbody>
                {items.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-muted-foreground">
                      No intervention logs found.
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr key={item.id} className="border-b border-border last:border-0 hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <div className="text-foreground">{item.intervention_type}</div>
                        <div className="mt-1 text-xs text-muted-foreground">
                          {item.recommendation_text || "No recommendation text"}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{item.outcome_status || "—"}</td>
                      <td className="px-4 py-3 text-foreground">{item.effectiveness_rating ?? "—"}</td>
                      <td className="px-4 py-3 font-mono text-xs text-foreground">{item.user_id.slice(0, 8)}</td>
                      <td className="px-4 py-3 text-muted-foreground">{new Date(item.created_at).toLocaleString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </motion.div>
    </div>
  );
}