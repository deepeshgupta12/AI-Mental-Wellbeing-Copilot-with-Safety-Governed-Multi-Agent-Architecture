"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminExternalIntegrationConnections,
  getAdminExternalIntegrationsOverview,
  getAdminExternalIntegrationSignals,
  getAdminExternalIntegrationSyncJobs,
} from "@/lib/external-integrations-api";

export default function AdminExternalIntegrationsPage() {
  const [organizationId, setOrganizationId] = useState("");

  const overviewQuery = useQuery({
    queryKey: ["admin-external-integrations-overview", organizationId],
    queryFn: () => getAdminExternalIntegrationsOverview(organizationId || null),
  });

  const connectionsQuery = useQuery({
    queryKey: ["admin-external-integrations-connections", organizationId],
    queryFn: () => getAdminExternalIntegrationConnections(organizationId || null),
  });

  const syncJobsQuery = useQuery({
    queryKey: ["admin-external-integrations-sync-jobs", organizationId],
    queryFn: () => getAdminExternalIntegrationSyncJobs(organizationId || null),
  });

  const signalsQuery = useQuery({
    queryKey: ["admin-external-integrations-signals", organizationId],
    queryFn: () => getAdminExternalIntegrationSignals(organizationId || null),
  });

  const overview = overviewQuery.data;
  const connections = connectionsQuery.data ?? [];
  const syncJobs = syncJobsQuery.data ?? [];
  const signals = signalsQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">
            External Integrations: Calendar, Reminders, Wearable, Sleep
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Org-scoped visibility into consented external connections, sync jobs, normalized
            wellbeing signals, and enterprise-safe boundary posture.
          </p>
        </div>

        <div className="mb-6 rounded-lg border border-border bg-card p-4 shadow-card">
          <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Organization filter
          </label>
          <input
            value={organizationId}
            onChange={(e) => setOrganizationId(e.target.value)}
            placeholder="Filter by organization ID"
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
          />
        </div>

        {!overview ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading external integration overview...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-7">
              {[
                { label: "Connections", value: overview.total_connections },
                { label: "Active", value: overview.active_connections },
                { label: "Consented", value: overview.consented_connections },
                { label: "Sync Jobs", value: overview.total_sync_jobs },
                { label: "Queued Jobs", value: overview.queued_sync_jobs },
                { label: "Failed Jobs", value: overview.failed_sync_jobs },
                { label: "Signals", value: overview.total_signals },
              ].map((item) => (
                <div key={item.label} className="rounded-lg border border-border bg-card p-4 shadow-card">
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Boundary Policy
                </h2>
                <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
                  {JSON.stringify(overview.boundary_policy, null, 2)}
                </pre>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Provider Catalog
                </h2>
                <div className="space-y-3">
                  {overview.catalog.map((item) => (
                    <div key={item.provider_key} className="rounded-md border border-border bg-background p-3">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <div className="text-sm font-medium text-foreground">{item.display_name}</div>
                          <div className="mt-1 text-xs text-muted-foreground">
                            {item.integration_key} · {item.category} · {item.adapter_type}
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {item.enabled ? "Enabled" : "Disabled"}
                        </div>
                      </div>
                      <div className="mt-2 text-xs text-muted-foreground">{item.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Connection Breakdown by Provider
                </h2>
                <div className="space-y-2">
                  {Object.entries(overview.connection_breakdown_by_provider).length === 0 ? (
                    <div className="text-sm text-muted-foreground">No provider activity yet.</div>
                  ) : (
                    Object.entries(overview.connection_breakdown_by_provider).map(([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2"
                      >
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm text-muted-foreground">{value}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Signal Breakdown by Type
                </h2>
                <div className="space-y-2">
                  {Object.entries(overview.signal_breakdown_by_type).length === 0 ? (
                    <div className="text-sm text-muted-foreground">No normalized signals yet.</div>
                  ) : (
                    Object.entries(overview.signal_breakdown_by_type).map(([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2"
                      >
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm text-muted-foreground">{value}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Connections
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left">
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Provider</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Category</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Consent</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Sync</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Updated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {connections.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-3 py-4 text-muted-foreground">
                          No connections available.
                        </td>
                      </tr>
                    ) : (
                      connections.map((item) => (
                        <tr key={item.id} className="border-b border-border last:border-0">
                          <td className="px-3 py-3 text-foreground">{item.provider_key}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.category}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.consent_status}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.last_sync_status ?? "—"}</td>
                          <td className="px-3 py-3 text-xs text-muted-foreground">
                            {new Date(item.updated_at).toLocaleString()}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Recent Sync Jobs
                </h2>
                <div className="space-y-3">
                  {syncJobs.length === 0 ? (
                    <div className="text-sm text-muted-foreground">No sync jobs recorded.</div>
                  ) : (
                    syncJobs.slice(0, 10).map((job) => (
                      <div key={job.id} className="rounded-md border border-border bg-background p-3">
                        <div className="flex items-center justify-between gap-3">
                          <div className="text-sm font-medium text-foreground">{job.provider_key}</div>
                          <div className="text-xs text-muted-foreground">{job.status}</div>
                        </div>
                        <div className="mt-1 text-xs text-muted-foreground">
                          {job.job_type} · {job.signal_count} signals
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Recent Signals
                </h2>
                <div className="space-y-3">
                  {signals.length === 0 ? (
                    <div className="text-sm text-muted-foreground">No normalized signals yet.</div>
                  ) : (
                    signals.slice(0, 10).map((signal) => (
                      <div key={signal.id} className="rounded-md border border-border bg-background p-3">
                        <div className="flex items-center justify-between gap-3">
                          <div className="text-sm font-medium text-foreground">{signal.signal_type}</div>
                          <div className="text-xs text-muted-foreground">{signal.provider_key}</div>
                        </div>
                        <div className="mt-1 text-xs text-muted-foreground">
                          {signal.text_value ?? "—"} {signal.numeric_value ?? ""}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}