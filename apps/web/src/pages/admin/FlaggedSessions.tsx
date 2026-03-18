import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getAdminFlaggedSessions } from "@/lib/admin-api";

export default function FlaggedSessionsPage() {
  const flaggedQuery = useQuery({
    queryKey: ["admin-flagged-sessions"],
    queryFn: getAdminFlaggedSessions,
  });

  const items = flaggedQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold text-foreground mb-6">
          Flagged Sessions
        </h1>

        <div className="rounded-lg border border-border bg-card shadow-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left">
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Flag</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">User</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Severity</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Status</th>
                  <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Created</th>
                </tr>
              </thead>
              <tbody>
                {flaggedQuery.isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-muted-foreground">
                      Loading flagged sessions...
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-muted-foreground">
                      No flagged sessions found.
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr key={item.id} className="border-b border-border last:border-0 hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <Link to="/admin/cases" className="text-foreground hover:underline">
                          {item.flag_type}
                        </Link>
                        {item.summary && (
                          <p className="text-xs text-muted-foreground mt-1">{item.summary}</p>
                        )}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-foreground">
                        {item.user_id.slice(0, 8)}
                      </td>
                      <td className="px-4 py-3 text-foreground">{item.severity}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {item.is_resolved ? "Resolved" : item.needs_review ? "Pending Review" : "Reviewed"}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {new Date(item.created_at).toLocaleString()}
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