"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminIntegrationArtifactDrilldown,
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

  const artifactsQuery = useQuery({
    queryKey: ["admin-integration-artifact-drilldown", organizationId],
    queryFn: () =>
      getAdminIntegrationArtifactDrilldown({
        organizationId: organizationId || null,
        limit: 20,
      }),
  });

  const overview = overviewQuery.data;
  const feed = feedQuery.data;
  const artifactDrilldown = artifactsQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">Integrations</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Pack 5 integration readiness, typed registry surfaces, adapter/config placeholders,
            sync posture, runtime export health, and artifact drill-downs without changing the
            storage/auth model.
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

        {!overview || !feed || !artifactDrilldown ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading integration readiness surfaces...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-6">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Auth Mode</div>
                <div className="mt-2 font-heading text-lg font-semibold text-foreground">
                  {overview.auth_mode ?? "—"}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Storage Provider</div>
                <div className="mt-2 font-heading text-lg font-semibold text-foreground">
                  {overview.storage_provider}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Secrets Backend</div>
                <div className="mt-2 font-heading text-lg font-semibold text-foreground">
                  {overview.secret_backend}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Scheduler</div>
                <div className="mt-2 font-heading text-lg font-semibold text-foreground">
                  {overview.scheduler_backend}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Temporal</div>
                <div className="mt-2 font-heading text-lg font-semibold text-foreground">
                  {overview.temporal_enabled ? "Enabled" : "Disabled"}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Artifacts</div>
                <div className="mt-2 font-heading text-lg font-semibold text-foreground">
                  {feed.counts.stored_artifacts}
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Integration Registry
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Name</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Category</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Adapter</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Health</th>
                      </tr>
                    </thead>
                    <tbody>
                      {overview.integration_registry.map((item) => (
                        <tr key={item.integration_key} className="border-b border-border last:border-0">
                          <td className="px-3 py-3 text-foreground">
                            <div>{item.display_name}</div>
                            <div className="mt-1 text-xs text-muted-foreground">{item.integration_key}</div>
                          </td>
                          <td className="px-3 py-3 text-muted-foreground">{item.category}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.adapter_type}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.health.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Runtime Feed Counts
                </h2>
                <div className="space-y-3">
                  {Object.entries(feed.counts).map(([key, value]) => (
                    <div
                      key={key}
                      className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2"
                    >
                      <span className="text-sm text-foreground">{key}</span>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
                <h3 className="mt-6 mb-3 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Artifact Counts by Scope
                </h3>
                <div className="space-y-2">
                  {Object.entries(feed.artifact_counts_by_scope).map(([key, value]) => (
                    <div
                      key={key}
                      className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2"
                    >
                      <span className="text-sm text-foreground">{key}</span>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Endpoint Catalog
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Name</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Method</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Category</th>
                        <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Path</th>
                      </tr>
                    </thead>
                    <tbody>
                      {feed.endpoints.map((item) => (
                        <tr key={item.name} className="border-b border-border last:border-0">
                          <td className="px-3 py-3 text-foreground">{item.name}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.method}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.category}</td>
                          <td className="px-3 py-3 text-xs text-muted-foreground">{item.path}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Config Placeholders & Audit Hooks
                </h2>
                <div className="space-y-4">
                  {overview.integration_registry.map((item) => (
                    <div key={item.integration_key} className="rounded-md border border-border bg-background p-3">
                      <div className="text-sm font-medium text-foreground">{item.display_name}</div>
                      <div className="mt-1 text-xs text-muted-foreground">{item.description}</div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.config_placeholders.map((field) => (
                          <span
                            key={`${item.integration_key}-${field.key}`}
                            className="rounded-full border border-border px-2 py-1 text-[11px] text-muted-foreground"
                          >
                            {field.key}
                            {field.secret ? " · secret" : ""}
                            {field.required ? " · required" : ""}
                          </span>
                        ))}
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.audit_hooks.map((hook) => (
                          <span
                            key={`${item.integration_key}-${hook.event_type}`}
                            className="rounded-full border border-border px-2 py-1 text-[11px] text-muted-foreground"
                          >
                            {hook.event_type}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Artifact Drill-down
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left">
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Scope</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Kind</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Provider</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">URI</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Bytes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {artifactDrilldown.artifacts.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-3 py-4 text-muted-foreground">
                          No artifacts available.
                        </td>
                      </tr>
                    ) : (
                      artifactDrilldown.artifacts.map((item) => (
                        <tr key={item.id} className="border-b border-border last:border-0">
                          <td className="px-3 py-3 text-foreground">{item.scope_type}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.artifact_kind}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.storage_provider}</td>
                          <td className="px-3 py-3 text-xs text-muted-foreground">{item.storage_uri}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.byte_size}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
