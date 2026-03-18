import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { getAdminSessionLogs } from "@/lib/admin-api";

export default function SessionLogsPage() {
  const logsQuery = useQuery({
    queryKey: ["admin-session-logs"],
    queryFn: getAdminSessionLogs,
  });

  const items = logsQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold text-foreground mb-6">
          Session Logs
        </h1>

        <div className="rounded-lg border border-border bg-card shadow-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left">
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Session</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">User</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Messages</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Latest Message</th>
                </tr>
              </thead>
              <tbody>
                {logsQuery.isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-muted-foreground">
                      Loading session logs...
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-muted-foreground">
                      No session logs found.
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr key={item.session_id} className="border-b border-border last:border-0 hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <p className="text-foreground">{item.title || "Untitled session"}</p>
                        <p className="text-xs text-muted-foreground mt-1 font-mono">
                          {item.session_id.slice(0, 8)}
                        </p>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-foreground">
                        {item.user_id.slice(0, 8)}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{item.status}</td>
                      <td className="px-4 py-3 text-foreground">{item.message_count}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {item.latest_message_at
                          ? new Date(item.latest_message_at).toLocaleString()
                          : "No messages yet"}
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