"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Clock, Flag, ShieldAlert, Users } from "lucide-react";

import { Button } from "@/components/ui/button";
import { getSafetyDashboardCounts, getSafetyQueue } from "@/lib/safety-api";

const riskColors: Record<string, string> = {
  high: "text-urgent bg-urgent/10",
  medium: "text-foreground bg-muted",
  low: "text-muted-foreground bg-muted",
};

export default function AdminDashboard() {
  const countsQuery = useQuery({
    queryKey: ["safety-dashboard-counts"],
    queryFn: getSafetyDashboardCounts,
  });

  const queueQuery = useQuery({
    queryKey: ["safety-queue"],
    queryFn: getSafetyQueue,
  });

  const queue = queueQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Operations Overview
        </h1>

        <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          {[
            {
              label: "Open Flags",
              value: countsQuery.data?.open_flags ?? "—",
              icon: Flag,
              change: "Active safety review load",
            },
            {
              label: "Review Needed",
              value: countsQuery.data?.review_needed_flags ?? "—",
              icon: ShieldAlert,
              change: "Awaiting reviewer action",
            },
            {
              label: "Resolved Flags",
              value: countsQuery.data?.resolved_flags ?? "—",
              icon: Clock,
              change: "Completed review outcomes",
            },
            {
              label: "Total Flags",
              value: countsQuery.data?.total_flags ?? "—",
              icon: Users,
              change: "All recorded safety items",
            },
          ].map((s) => (
            <div key={s.label} className="rounded-lg border border-border bg-card p-4 shadow-card">
              <div className="mb-2 flex items-center gap-2">
                <s.icon className="h-4 w-4 text-muted-foreground" strokeWidth={1.5} />
                <span className="text-xs text-muted-foreground">{s.label}</span>
              </div>
              <p className="font-heading text-2xl font-bold text-foreground">{s.value}</p>
              <p className="mt-1 text-[11px] text-muted-foreground">{s.change}</p>
            </div>
          ))}
        </div>

        <div className="overflow-hidden rounded-lg border border-border bg-card shadow-card">
          <div className="flex items-center justify-between border-b border-border p-4">
            <h2 className="font-heading text-sm font-semibold text-foreground">
              Recent Safety Queue
            </h2>
            <Button variant="ghost" size="sm" className="text-xs">
              Live data
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left">
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Flag ID</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">User ID</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Risk</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Trigger</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
                </tr>
              </thead>
              <tbody>
                {queueQuery.isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-sm text-muted-foreground">
                      Loading safety queue...
                    </td>
                  </tr>
                ) : queue.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-sm text-muted-foreground">
                      No active safety flags in queue.
                    </td>
                  </tr>
                ) : (
                  queue.slice(0, 10).map((f) => (
                    <tr
                      key={f.id}
                      className="cursor-pointer border-b border-border transition-aether last:border-0 hover:bg-muted/30"
                    >
                      <td className="px-4 py-3 font-mono text-xs text-foreground">{f.id.slice(0, 8)}</td>
                      <td className="px-4 py-3 font-mono text-xs text-foreground">{f.user_id.slice(0, 8)}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                            riskColors[f.severity] ?? "text-muted-foreground bg-muted"
                          }`}
                        >
                          {f.severity}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-foreground">{f.flag_type}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {f.is_resolved ? "Resolved" : f.needs_review ? "Pending Review" : "Reviewed"}
                      </td>
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