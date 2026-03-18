"use client";

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
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Audit Logs
        </h1>

        <div className="space-y-3">
          {auditQuery.isLoading ? (
            <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
              Loading audit trail...
            </div>
          ) : items.length === 0 ? (
            <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
              No audit items found.
            </div>
          ) : (
            items.map((item, index) => (
              <div
                key={`${item.entity_id}-${item.event_type}-${index}`}
                className="rounded-lg border border-border bg-card p-4 shadow-card"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium text-foreground">{item.title}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{item.details}</p>
                    <p className="mt-2 text-[11px] text-muted-foreground">
                      {item.event_type} · {item.entity_type} ·{" "}
                      {item.user_id ? `user ${item.user_id.slice(0, 8)}` : "system"}
                    </p>
                  </div>
                  <div className="whitespace-nowrap text-[11px] text-muted-foreground">
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