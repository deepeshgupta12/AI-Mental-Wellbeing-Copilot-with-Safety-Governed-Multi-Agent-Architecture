"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { getAdminPolicyConfig } from "@/lib/admin-api";

export default function PolicyViewerPage() {
  const policyQuery = useQuery({
    queryKey: ["admin-policy-config"],
    queryFn: getAdminPolicyConfig,
  });

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Policy & Prompts
        </h1>

        {policyQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading policy configuration...
          </div>
        ) : !policyQuery.data ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Policy configuration is not available.
          </div>
        ) : (
          <div className="grid gap-6">
            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-3 font-heading text-sm font-semibold text-foreground">
                Runtime Policy
              </h2>
              <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-muted-foreground">
                {JSON.stringify(policyQuery.data.runtime_policy, null, 2)}
              </pre>
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-3 font-heading text-sm font-semibold text-foreground">
                Prompt Registry
              </h2>
              <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-muted-foreground">
                {JSON.stringify(policyQuery.data.prompt_registry, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}