"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getApiErrorMessage } from "@/lib/api-client";
import {
  getExternalIntegrationCatalog,
  getMyExternalIntegrationStatus,
  getMyExternalSignals,
  ingestMyExternalIntegrationPayload,
  queueMyExternalIntegrationSync,
  upsertMyExternalIntegrationConnection,
} from "@/lib/external-integrations-api";

const DEFAULT_INGEST_PAYLOADS: Record<string, Record<string, unknown>> = {
  google_calendar: {
    events: [
      {
        id: "demo-cal-1",
        title: "Therapy Session",
        start_at: "2026-03-22T09:00:00+00:00",
        end_at: "2026-03-22T10:00:00+00:00",
        status: "confirmed",
      },
    ],
  },
  apple_reminders: {
    reminders: [
      {
        id: "demo-rem-1",
        title: "Breathing Exercise",
        due_at: "2026-03-22T18:00:00+00:00",
        completed: false,
      },
    ],
  },
  fitbit_wearable: {
    samples: [
      {
        id: "demo-fit-1",
        metric_type: "steps",
        value: 6200,
        unit: "count",
        captured_at: "2026-03-22T08:00:00+00:00",
      },
    ],
  },
  oura_sleep: {
    sessions: [
      {
        id: "demo-sleep-1",
        start_at: "2026-03-21T22:30:00+00:00",
        end_at: "2026-03-22T05:45:00+00:00",
        duration_minutes: 435,
        sleep_score: 81,
      },
    ],
  },
};

export default function AppIntegrationsPage() {
  const queryClient = useQueryClient();
  const [providerKey, setProviderKey] = useState("google_calendar");
  const [integrationKey, setIntegrationKey] = useState("calendar");
  const [consentStatus, setConsentStatus] = useState("active");
  const [configJson, setConfigJson] = useState('{"account_label":"Primary"}');
  const [ingestConnectionId, setIngestConnectionId] = useState("");
  const [ingestPayloadJson, setIngestPayloadJson] = useState(
    JSON.stringify(DEFAULT_INGEST_PAYLOADS.google_calendar, null, 2),
  );

  const statusQuery = useQuery({
    queryKey: ["my-external-integration-status"],
    queryFn: getMyExternalIntegrationStatus,
  });

  const catalogQuery = useQuery({
    queryKey: ["external-integration-catalog"],
    queryFn: getExternalIntegrationCatalog,
  });

  const signalsQuery = useQuery({
    queryKey: ["my-external-signals"],
    queryFn: () => getMyExternalSignals(),
  });

  const upsertMutation = useMutation({
    mutationFn: async () =>
      upsertMyExternalIntegrationConnection({
        integration_key: integrationKey,
        provider_key: providerKey,
        consent_status: consentStatus,
        config_json: JSON.parse(configJson) as Record<string, unknown>,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["my-external-integration-status"] });
    },
  });

  const syncMutation = useMutation({
    mutationFn: async () =>
      queueMyExternalIntegrationSync(ingestConnectionId, {
        job_type: "manual_sync",
        sync_window_days: 7,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["my-external-integration-status"] });
    },
  });

  const ingestMutation = useMutation({
    mutationFn: async () =>
      ingestMyExternalIntegrationPayload(ingestConnectionId, {
        source_label: "ui_demo_ingest",
        payload_json: JSON.parse(ingestPayloadJson) as Record<string, unknown>,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["my-external-integration-status"] });
      await queryClient.invalidateQueries({ queryKey: ["my-external-signals"] });
    },
  });

  const catalog = catalogQuery.data ?? [];
  const status = statusQuery.data;
  const signals = signalsQuery.data ?? [];

  const selectableProviders = useMemo(
    () =>
      catalog.map((item) => ({
        providerKey: item.provider_key,
        integrationKey: item.integration_key,
        label: `${item.display_name} (${item.category})`,
      })),
    [catalog],
  );

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">
            External Integrations
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Manage consent, create external connections, queue sync jobs, and ingest normalized
            calendar, reminders, wearable, and sleep signals.
          </p>
        </div>

        {!status ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading external integration status...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {[
                { label: "Connections", value: status.connections.length },
                { label: "Sync Jobs", value: status.recent_sync_jobs.length },
                { label: "Signals", value: status.recent_signals.length },
                { label: "Catalog Providers", value: status.catalog.length },
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
                  Create / Update Connection
                </h2>

                <div className="space-y-3">
                  <select
                    value={providerKey}
                    onChange={(e) => {
                      const selected = selectableProviders.find(
                        (item) => item.providerKey === e.target.value,
                      );
                      setProviderKey(e.target.value);
                      setIntegrationKey(selected?.integrationKey ?? "calendar");
                      setIngestPayloadJson(
                        JSON.stringify(DEFAULT_INGEST_PAYLOADS[e.target.value] ?? {}, null, 2),
                      );
                    }}
                    className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                  >
                    {selectableProviders.map((item) => (
                      <option key={item.providerKey} value={item.providerKey}>
                        {item.label}
                      </option>
                    ))}
                  </select>

                  <select
                    value={consentStatus}
                    onChange={(e) => setConsentStatus(e.target.value)}
                    className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                  >
                    <option value="active">active</option>
                    <option value="pending">pending</option>
                    <option value="revoked">revoked</option>
                  </select>

                  <textarea
                    value={configJson}
                    onChange={(e) => setConfigJson(e.target.value)}
                    className="min-h-[120px] w-full rounded-md border border-border bg-background p-3 font-mono text-xs text-foreground"
                  />

                  <button
                    type="button"
                    onClick={() => upsertMutation.mutate()}
                    className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background"
                  >
                    {upsertMutation.isPending ? "Saving..." : "Save Connection"}
                  </button>

                  {upsertMutation.isError ? (
                    <div className="text-sm text-destructive">
                      {getApiErrorMessage(upsertMutation.error)}
                    </div>
                  ) : null}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Manual Sync / Ingest
                </h2>

                <div className="space-y-3">
                  <input
                    value={ingestConnectionId}
                    onChange={(e) => setIngestConnectionId(e.target.value)}
                    placeholder="Connection ID"
                    className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                  />

                  <textarea
                    value={ingestPayloadJson}
                    onChange={(e) => setIngestPayloadJson(e.target.value)}
                    className="min-h-[180px] w-full rounded-md border border-border bg-background p-3 font-mono text-xs text-foreground"
                  />

                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => syncMutation.mutate()}
                      className="rounded-md border border-border bg-background px-4 py-2 text-sm font-medium text-foreground"
                    >
                      {syncMutation.isPending ? "Queueing..." : "Queue Sync Job"}
                    </button>

                    <button
                      type="button"
                      onClick={() => ingestMutation.mutate()}
                      className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background"
                    >
                      {ingestMutation.isPending ? "Ingesting..." : "Ingest Payload"}
                    </button>
                  </div>

                  {syncMutation.isError ? (
                    <div className="text-sm text-destructive">
                      {getApiErrorMessage(syncMutation.error)}
                    </div>
                  ) : null}

                  {ingestMutation.isError ? (
                    <div className="text-sm text-destructive">
                      {getApiErrorMessage(ingestMutation.error)}
                    </div>
                  ) : null}
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                My Connections
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left">
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">ID</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Provider</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Consent</th>
                      <th className="px-3 py-2 text-xs font-medium text-muted-foreground">Sync</th>
                    </tr>
                  </thead>
                  <tbody>
                    {status.connections.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-3 py-4 text-muted-foreground">
                          No external connections created yet.
                        </td>
                      </tr>
                    ) : (
                      status.connections.map((item) => (
                        <tr key={item.id} className="border-b border-border last:border-0">
                          <td className="px-3 py-3 text-xs text-muted-foreground">{item.id}</td>
                          <td className="px-3 py-3 text-foreground">{item.provider_key}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.consent_status}</td>
                          <td className="px-3 py-3 text-muted-foreground">{item.last_sync_status ?? "—"}</td>
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
                  Signal Breakdown
                </h2>
                <div className="space-y-2">
                  {Object.entries(status.signal_breakdown_by_type).length === 0 ? (
                    <div className="text-sm text-muted-foreground">No normalized signals yet.</div>
                  ) : (
                    Object.entries(status.signal_breakdown_by_type).map(([key, value]) => (
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
                  Recent Signals
                </h2>
                <div className="space-y-3">
                  {signals.length === 0 ? (
                    <div className="text-sm text-muted-foreground">No signals available.</div>
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