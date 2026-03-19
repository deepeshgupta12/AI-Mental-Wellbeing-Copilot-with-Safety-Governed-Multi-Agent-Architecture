"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { getAdminConfigAudit, getAdminConfigDiff } from "@/lib/admin-api";

export default function AuditLogsPage() {
  const [selectedConfigKey, setSelectedConfigKey] = useState<string>("runtime_policy");
  const auditQuery = useQuery({
    queryKey: ["admin-config-audit", selectedConfigKey],
    queryFn: () => getAdminConfigAudit(selectedConfigKey),
  });

  const pair = useMemo(() => {
    const items = auditQuery.data ?? [];
    if (items.length < 1) return null;
    const first = items[0];
    if (!first.from_version_id) return null;
    return {
      fromVersionId: first.from_version_id,
      toVersionId: first.to_version_id,
    };
  }, [auditQuery.data]);

  const diffQuery = useQuery({
    queryKey: ["admin-config-diff", selectedConfigKey, pair?.fromVersionId, pair?.toVersionId],
    queryFn: () =>
      getAdminConfigDiff(
        selectedConfigKey,
        pair!.fromVersionId,
        pair!.toVersionId,
      ),
    enabled: Boolean(pair),
  });

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6 flex items-center justify-between gap-3">
          <h1 className="font-heading text-2xl font-bold text-foreground">
            Config Audit & Diffs
          </h1>
          <select
            value={selectedConfigKey}
            onChange={(e) => setSelectedConfigKey(e.target.value)}
            className="rounded-md border border-border bg-card px-3 py-2 text-sm text-foreground"
          >
            <option value="runtime_policy">runtime_policy</option>
            <option value="prompt_registry">prompt_registry</option>
            <option value="routing_rules">routing_rules</option>
          </select>
        </div>

        <div className="grid gap-6 lg:grid-cols-[420px_minmax(0,1fr)]">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Audit Timeline
            </h2>
            <div className="space-y-3">
              {(auditQuery.data ?? []).map((item) => (
                <div key={item.id} className="rounded-md border border-border bg-background p-3">
                  <div className="text-sm font-medium text-foreground">{item.config_key}</div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {item.changed_keys_json?.join(", ") || "No changed keys"}
                  </div>
                  <div className="mt-2 text-[11px] text-muted-foreground">
                    {new Date(item.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Latest Diff
            </h2>
            {!diffQuery.data ? (
              <div className="text-sm text-muted-foreground">
                No comparable version pair available yet.
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-sm text-muted-foreground">
                  Changed keys: {diffQuery.data.changed_keys.join(", ") || "None"}
                </div>
                <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
                  {JSON.stringify(diffQuery.data.diff_json, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}