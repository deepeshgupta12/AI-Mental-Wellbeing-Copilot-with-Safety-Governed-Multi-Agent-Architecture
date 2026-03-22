"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminIntegrationOverview,
  getAdminIntegrationRuntimeFeed,
} from "@/lib/admin-api";

export default function AdminIntegrationsPage() {
  const [organizationId, setOrganizationId] = useState("");

  const overviewQuery = useQuery({
    queryKey: ["admin-integration-overview", organizationId],
    queryFn: () => getAdminIntegrationOverview(organizationId || null),
  });

  const feedQuery = useQuery({
    queryKey: ["admin-integration-runtime-feed", organizationId],
    queryFn: () => getAdminIntegrationRuntimeFeed(organizationId || null),
  });

  const overview = overviewQuery.data;
  const feed = feedQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">Integrations</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Pack 5 integration readiness, runtime export posture, model routing policy, and safe operational endpoints.
          </p>
        </div>

        <div className="mb-6 rounded-lg border border-border bg-card p-4 shadow-card">
          <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Organization ID (optional)
          </label>
          <input
            value={organizationId}
            onChange={(e) => setOrganizationId(e.target.value)}
            placeholder="Filter by organization ID"
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Integration Overview
            </h2>
            {!overview ? (
              <div className="text-sm text-muted-foreground">Loading integration overview...</div>
            ) : (
              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
                {JSON.stringify(overview, null, 2)}
              </pre>
            )}
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Runtime Feed
            </h2>
            {!feed ? (
              <div className="text-sm text-muted-foreground">Loading runtime feed...</div>
            ) : (
              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
                {JSON.stringify(feed, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}