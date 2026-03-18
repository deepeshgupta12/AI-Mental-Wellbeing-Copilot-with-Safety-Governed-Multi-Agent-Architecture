import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { getAdminAuditTrail } from "@/lib/admin-api";

export default function AuditLogsPage() {
  const auditQuery = useQuery({
    queryKey: ["admin-audit-trail"],
    queryFn: getAdminAuditTrail,
  });

  const items = auditQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold text-foreground mb-6">
          Audit Logs
        </h1>

        <div className="space-y-3">
          {auditQuery.isLoading ? (
            <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
              Loading audit trail...
            </div>
          ) : items.length === 0 ? (
            <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
              No audit items found.
            </div>
          ) : (
            items.map((item, index) => (
              <div key={`${item.entity_id}-${item.event_type}-${index}`} className="rounded-lg border border-border bg-card shadow-card p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium text-foreground">{item.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{item.details}</p>
                    <p className="text-[11px] text-muted-foreground mt-2">
                      {item.event_type} · {item.entity_type} · {item.user_id ? `user ${item.user_id.slice(0, 8)}` : "system"}
                    </p>
                  </div>
                  <div className="text-[11px] text-muted-foreground whitespace-nowrap">
                    {new Date(item.occurred_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </motion.div>
    </div>
  );
}