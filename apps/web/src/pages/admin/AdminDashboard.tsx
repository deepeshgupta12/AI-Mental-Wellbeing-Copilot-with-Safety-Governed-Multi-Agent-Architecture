import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { getSafetyDashboardCounts, getSafetyQueue } from "@/lib/safety-api";
import {
  Flag,
  ShieldAlert,
  Clock,
  Users,
} from "lucide-react";

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
        <h1 className="font-heading text-2xl font-bold text-foreground mb-6">Operations Overview</h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
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
            <div key={s.label} className="p-4 rounded-lg border border-border bg-card shadow-card">
              <div className="flex items-center gap-2 mb-2">
                <s.icon className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                <span className="text-xs text-muted-foreground">{s.label}</span>
              </div>
              <p className="text-2xl font-heading font-bold text-foreground">{s.value}</p>
              <p className="text-[11px] text-muted-foreground mt-1">{s.change}</p>
            </div>
          ))}
        </div>

        <div className="rounded-lg border border-border bg-card shadow-card overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="font-heading font-semibold text-foreground text-sm">Recent Safety Queue</h2>
            <Button variant="ghost" size="sm" className="text-xs">Live data</Button>
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
                      className="border-b border-border last:border-0 hover:bg-muted/30 transition-aether cursor-pointer"
                    >
                      <td className="px-4 py-3 font-mono text-xs text-foreground">{f.id.slice(0, 8)}</td>
                      <td className="px-4 py-3 font-mono text-xs text-foreground">{f.user_id.slice(0, 8)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${riskColors[f.severity] ?? "text-muted-foreground bg-muted"}`}>
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