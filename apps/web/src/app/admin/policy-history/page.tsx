"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminConfigAudit,
  getAdminPromptRegistryVersions,
  getAdminRuntimePolicyVersions,
} from "@/lib/admin-api";

export default function PolicyHistoryPage() {
  const [selectedConfigKey, setSelectedConfigKey] = useState<string>("runtime_policy");

  const auditQuery = useQuery({
    queryKey: ["admin-config-audit", selectedConfigKey],
    queryFn: () => getAdminConfigAudit(selectedConfigKey),
  });

  const runtimeVersionsQuery = useQuery({
    queryKey: ["admin-runtime-policy-versions"],
    queryFn: getAdminRuntimePolicyVersions,
  });

  const promptVersionsQuery = useQuery({
    queryKey: ["admin-prompt-registry-versions"],
    queryFn: getAdminPromptRegistryVersions,
  });

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6 flex items-center justify-between gap-3">
          <h1 className="font-heading text-2xl font-bold text-foreground">Policy History</h1>
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

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Runtime Policy Versions
            </h2>
            <div className="space-y-2">
              {(runtimeVersionsQuery.data ?? []).map((item) => (
                <div key={item.id} className="rounded-md border border-border bg-background p-3 text-xs">
                  <div className="text-foreground">v{item.version_number}</div>
                  <div className="mt-1 text-muted-foreground">{item.change_note || "No change note"}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Prompt Registry Versions
            </h2>
            <div className="space-y-2">
              {(promptVersionsQuery.data ?? []).map((item) => (
                <div key={item.id} className="rounded-md border border-border bg-background p-3 text-xs">
                  <div className="text-foreground">v{item.version_number}</div>
                  <div className="mt-1 text-muted-foreground">{item.change_note || "No change note"}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Config Audit Timeline
            </h2>
            <div className="space-y-2">
              {(auditQuery.data ?? []).map((item) => (
                <div key={item.id} className="rounded-md border border-border bg-background p-3 text-xs">
                  <div className="text-foreground">{item.config_key}</div>
                  <div className="mt-1 text-muted-foreground">
                    {item.changed_keys_json?.join(", ") || "No changed keys"}
                  </div>
                  <div className="mt-2 text-[11px] text-muted-foreground">
                    {new Date(item.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}