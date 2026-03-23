"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getAdminDeploymentSettings,
  getAdminInfrastructureSummary,
  getAdminOrganizationSettings,
  getAdminResolvedEnterpriseSettings,
  getAdminStoredArtifacts,
  updateAdminDeploymentSettings,
  updateAdminOrganizationSettings,
} from "@/lib/admin-api";
import { getApiErrorMessage } from "@/lib/api-client";

function defaultOrganizationOverridePayload() {
  return {
    governance: {
      escalation_policy_overrides: {},
      model_provider_policy_overrides: {},
      feature_flags: {},
      storage_policy_overrides: {},
      queue_hardening_overrides: {},
      file_handling_overrides: {},
    },
  };
}

function safeStringify(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function parseEditorObject(value: string, label: string): Record<string, unknown> {
  const trimmed = value.trim();

  if (!trimmed) {
    throw new Error(`${label} JSON cannot be empty.`);
  }

  const parsed = JSON.parse(trimmed) as unknown;

  if (parsed === null || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error(`${label} JSON must be an object.`);
  }

  return parsed as Record<string, unknown>;
}

export default function EnterpriseSettingsPage() {
  const queryClient = useQueryClient();

  const [organizationId, setOrganizationId] = useState("");
  const [deploymentEditor, setDeploymentEditor] = useState("{}");
  const [organizationEditor, setOrganizationEditor] = useState(
    safeStringify(defaultOrganizationOverridePayload()),
  );
  const [deploymentChangeNote, setDeploymentChangeNote] = useState("");
  const [organizationChangeNote, setOrganizationChangeNote] = useState("");
  const [deploymentValidationError, setDeploymentValidationError] = useState<string | null>(null);
  const [organizationValidationError, setOrganizationValidationError] = useState<string | null>(
    null,
  );

  const deploymentSettingsQuery = useQuery({
    queryKey: ["admin-deployment-settings"],
    queryFn: getAdminDeploymentSettings,
  });

  const organizationSettingsQuery = useQuery({
    queryKey: ["admin-organization-settings", organizationId],
    queryFn: () => getAdminOrganizationSettings(organizationId),
    enabled: organizationId.trim().length > 0,
    retry: false,
  });

  const resolvedSettingsQuery = useQuery({
    queryKey: ["admin-resolved-enterprise-settings", organizationId],
    queryFn: () => getAdminResolvedEnterpriseSettings(organizationId || null),
  });

  const infrastructureSummaryQuery = useQuery({
    queryKey: ["admin-infrastructure-summary", organizationId],
    queryFn: () => getAdminInfrastructureSummary(organizationId || null),
  });

  const storedArtifactsQuery = useQuery({
    queryKey: ["admin-stored-artifacts", organizationId],
    queryFn: () =>
      getAdminStoredArtifacts({
        limit: 20,
      }),
  });

  useEffect(() => {
    if (deploymentSettingsQuery.data) {
      setDeploymentEditor(JSON.stringify(deploymentSettingsQuery.data.payload_json, null, 2));
      setDeploymentValidationError(null);
    }
  }, [deploymentSettingsQuery.data]);

  useEffect(() => {
    if (organizationSettingsQuery.data) {
      const nextPayload =
        organizationSettingsQuery.data.payload_json ?? defaultOrganizationOverridePayload();
      setOrganizationEditor(JSON.stringify(nextPayload, null, 2));
      setOrganizationValidationError(null);
      return;
    }

    if (!organizationId.trim()) {
      setOrganizationEditor(JSON.stringify(defaultOrganizationOverridePayload(), null, 2));
      setOrganizationValidationError(null);
    }
  }, [organizationSettingsQuery.data, organizationId]);

  const deploymentMutation = useMutation({
    mutationFn: async () => {
      const parsed = parseEditorObject(deploymentEditor, "Deployment settings");
      return updateAdminDeploymentSettings(parsed, deploymentChangeNote || null);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-deployment-settings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-resolved-enterprise-settings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-infrastructure-summary"] });
      setDeploymentChangeNote("");
      setDeploymentValidationError(null);
    },
  });

  const organizationMutation = useMutation({
    mutationFn: async () => {
      const parsed = parseEditorObject(organizationEditor, "Organization override settings");
      return updateAdminOrganizationSettings(
        organizationId.trim(),
        parsed,
        organizationChangeNote || null,
      );
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-organization-settings", organizationId],
      });
      await queryClient.invalidateQueries({ queryKey: ["admin-resolved-enterprise-settings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-infrastructure-summary"] });
      setOrganizationChangeNote("");
      setOrganizationValidationError(null);
    },
  });

  const effectiveSettingsPreview = useMemo(() => {
    return JSON.stringify(resolvedSettingsQuery.data?.effective_settings ?? {}, null, 2);
  }, [resolvedSettingsQuery.data]);

  const infra = infrastructureSummaryQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">
            Enterprise Settings & Environment Governance
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Manage deployment-level governance, organization overrides, escalation behavior,
            model-provider policy settings, storage, secrets posture, and queue hardening from one
            operational surface.
          </p>
        </div>

        <div className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Storage Provider</div>
            <div className="mt-2 font-heading text-lg font-semibold text-foreground">
              {infra?.storage.provider ?? "—"}
            </div>
            <div className="mt-1 text-xs text-muted-foreground">
              {infra?.storage.write_mode ?? "Loading..."}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Secrets Backend</div>
            <div className="mt-2 font-heading text-lg font-semibold text-foreground">
              {infra?.secrets.backend ?? "—"}
            </div>
            <div className="mt-1 text-xs text-muted-foreground">
              {infra ? `${infra.secrets.configured_keys.length} configured keys` : "Loading..."}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Queue Max Attempts</div>
            <div className="mt-2 font-heading text-lg font-semibold text-foreground">
              {infra?.queue.max_attempts ?? "—"}
            </div>
            <div className="mt-1 text-xs text-muted-foreground">
              {infra?.queue.dead_letter_enabled ? "DLQ enabled" : "DLQ disabled"}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Attachment Limit</div>
            <div className="mt-2 font-heading text-lg font-semibold text-foreground">
              {infra?.file_handling.max_attachment_bytes ?? "—"}
            </div>
            <div className="mt-1 text-xs text-muted-foreground">bytes</div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Cloud Profile</div>
            <div className="mt-2 font-heading text-lg font-semibold text-foreground">
              {infra?.cloud.deployment_profile ?? "—"}
            </div>
            <div className="mt-1 text-xs text-muted-foreground">
              {infra?.cloud.config_source ?? "Loading..."}
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="mb-3">
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Deployment Settings
              </h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Global environment configuration for the current deployment.
              </p>
            </div>

            <textarea
              value={deploymentEditor}
              onChange={(e) => {
                setDeploymentEditor(e.target.value);
                setDeploymentValidationError(null);
              }}
              className="min-h-[420px] w-full rounded-md border border-border bg-background p-3 font-mono text-xs text-foreground"
            />

            <div className="mt-3 flex flex-col gap-3">
              <input
                value={deploymentChangeNote}
                onChange={(e) => setDeploymentChangeNote(e.target.value)}
                placeholder="Change note"
                className="rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              />
              <button
                type="button"
                onClick={() => {
                  try {
                    parseEditorObject(deploymentEditor, "Deployment settings");
                    setDeploymentValidationError(null);
                    deploymentMutation.mutate();
                  } catch (error) {
                    setDeploymentValidationError(
                      error instanceof Error ? error.message : "Invalid deployment settings JSON.",
                    );
                  }
                }}
                className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background"
              >
                {deploymentMutation.isPending ? "Saving..." : "Save Deployment Settings"}
              </button>
            </div>

            {deploymentValidationError ? (
              <div className="mt-3 text-sm text-destructive">{deploymentValidationError}</div>
            ) : null}

            {deploymentMutation.isError ? (
              <div className="mt-3 text-sm text-destructive">
                {getApiErrorMessage(deploymentMutation.error)}
              </div>
            ) : null}
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="mb-3">
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Organization Override Settings
              </h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Apply tenant-specific overrides on top of deployment defaults.
              </p>
            </div>

            <input
              value={organizationId}
              onChange={(e) => {
                setOrganizationId(e.target.value);
                setOrganizationValidationError(null);
              }}
              placeholder="Organization ID"
              className="mb-3 w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
            />

            <textarea
              value={organizationEditor}
              onChange={(e) => {
                setOrganizationEditor(e.target.value);
                setOrganizationValidationError(null);
              }}
              className="min-h-[420px] w-full rounded-md border border-border bg-background p-3 font-mono text-xs text-foreground"
            />

            <div className="mt-3 flex flex-col gap-3">
              <input
                value={organizationChangeNote}
                onChange={(e) => setOrganizationChangeNote(e.target.value)}
                placeholder="Change note"
                className="rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              />
              <button
                type="button"
                onClick={() => {
                  if (!organizationId.trim()) {
                    setOrganizationValidationError("Organization ID is required.");
                    return;
                  }

                  try {
                    parseEditorObject(organizationEditor, "Organization override settings");
                    setOrganizationValidationError(null);
                    organizationMutation.mutate();
                  } catch (error) {
                    setOrganizationValidationError(
                      error instanceof Error
                        ? error.message
                        : "Invalid organization override JSON.",
                    );
                  }
                }}
                disabled={!organizationId.trim()}
                className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background disabled:opacity-60"
              >
                {organizationMutation.isPending ? "Saving..." : "Save Organization Overrides"}
              </button>
            </div>

            {organizationSettingsQuery.isError ? (
              <div className="mt-3 text-sm text-destructive">
                {getApiErrorMessage(organizationSettingsQuery.error)}
              </div>
            ) : null}

            {organizationValidationError ? (
              <div className="mt-3 text-sm text-destructive">{organizationValidationError}</div>
            ) : null}

            {organizationMutation.isError ? (
              <div className="mt-3 text-sm text-destructive">
                {getApiErrorMessage(organizationMutation.error)}
              </div>
            ) : null}
          </div>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="mb-3">
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Infrastructure Runtime Summary
              </h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Safe, redacted deployment posture for storage, secrets, queue, and cloud config.
              </p>
            </div>

            <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
              {safeStringify(infra ?? {})}
            </pre>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="mb-3">
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Effective Resolved Settings
              </h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Final governance state after deployment defaults and organization overrides are merged.
              </p>
            </div>

            <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
              {effectiveSettingsPreview}
            </pre>
          </div>
        </div>

        <div className="mt-6 rounded-lg border border-border bg-card p-4 shadow-card">
          <div className="mb-3">
            <h2 className="font-heading text-sm font-semibold text-foreground">
              Recent Stored Artifacts
            </h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Latest persisted audit, safety, and attachment manifests from Pack 3 storage hardening.
            </p>
          </div>

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
                {(storedArtifactsQuery.data ?? []).length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-4 text-muted-foreground">
                      No stored artifacts yet.
                    </td>
                  </tr>
                ) : (
                  (storedArtifactsQuery.data ?? []).map((item) => (
                    <tr key={item.id} className="border-b border-border last:border-0">
                      <td className="px-3 py-3 text-foreground">
                        <div>{item.scope_type}</div>
                        <div className="mt-1 text-xs text-muted-foreground">{item.scope_id}</div>
                      </td>
                      <td className="px-3 py-3 text-foreground">{item.artifact_kind}</td>
                      <td className="px-3 py-3 text-foreground">{item.storage_provider}</td>
                      <td className="px-3 py-3 text-xs text-muted-foreground">{item.storage_uri}</td>
                      <td className="px-3 py-3 text-muted-foreground">{item.byte_size}</td>
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