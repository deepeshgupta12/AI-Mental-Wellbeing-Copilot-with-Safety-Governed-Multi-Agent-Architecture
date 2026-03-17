import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Flag,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Users,
  TrendingUp,
  Activity,
} from "lucide-react";

const stats = [
  { label: "Active Users", value: "1,247", icon: Users, change: "+12%" },
  { label: "Flagged Sessions", value: "23", icon: Flag, change: "−3 from yesterday" },
  { label: "Safety Events", value: "4", icon: ShieldAlert, change: "2 pending review" },
  { label: "Avg Response Time", value: "14m", icon: Clock, change: "Within SLA" },
];

const recentFlags = [
  { id: "USR-4821", risk: "High", trigger: "self-harm language", time: "12m ago", status: "Pending Review", reviewer: "—" },
  { id: "USR-3102", risk: "Medium", trigger: "sleep disruption escalation", time: "1h ago", status: "Intervention Sent", reviewer: "Dr. Chen" },
  { id: "USR-7744", risk: "Low", trigger: "repeated distress keywords", time: "3h ago", status: "Resolved", reviewer: "M. Torres" },
  { id: "USR-1199", risk: "High", trigger: "crisis disclosure", time: "4h ago", status: "Escalated", reviewer: "Dr. Chen" },
];

const riskColors: Record<string, string> = {
  High: "text-urgent bg-urgent/10",
  Medium: "text-foreground bg-muted",
  Low: "text-muted-foreground bg-muted",
};

const statusColors: Record<string, string> = {
  "Pending Review": "text-urgent",
  "Intervention Sent": "text-primary",
  "Resolved": "text-safe",
  "Escalated": "text-urgent",
};

export default function AdminDashboard() {
  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold text-foreground mb-6">Operations Overview</h1>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((s) => (
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

        {/* Flagged sessions table */}
        <div className="rounded-lg border border-border bg-card shadow-card overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="font-heading font-semibold text-foreground text-sm">Recent Flagged Sessions</h2>
            <Button variant="ghost" size="sm" className="text-xs">View all</Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left">
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">User ID</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Risk</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Trigger</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Time</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Reviewer</th>
                </tr>
              </thead>
              <tbody>
                {recentFlags.map((f) => (
                  <tr key={f.id} className="border-b border-border last:border-0 hover:bg-muted/30 transition-aether cursor-pointer">
                    <td className="px-4 py-3 font-mono text-xs text-foreground">{f.id}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${riskColors[f.risk]}`}>
                        {f.risk}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-foreground">{f.trigger}</td>
                    <td className="px-4 py-3 text-muted-foreground">{f.time}</td>
                    <td className={`px-4 py-3 font-medium ${statusColors[f.status]}`}>{f.status}</td>
                    <td className="px-4 py-3 text-muted-foreground">{f.reviewer}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
