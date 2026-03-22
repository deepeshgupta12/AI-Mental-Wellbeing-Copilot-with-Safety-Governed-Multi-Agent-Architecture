"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getAdminDeploymentSettings,
  getAdminOrganizationSettings,
  getAdminResolvedEnterpriseSettings,
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
      setOrganizationChangeNote("");
      setOrganizationValidationError(null);
    },
  });

  const effectiveSettingsPreview = useMemo(() => {
    return JSON.stringify(resolvedSettingsQuery.data?.effective_settings ?? {}, null, 2);
  }, [resolvedSettingsQuery.data]);

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">
            Enterprise Settings & Environment Governance
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Manage deployment-level governance, organization overrides, escalation behavior,
            and model-provider policy settings from one operational surface.
          </p>
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
                Apply tenant-specific escalation and provider overrides on top of deployment defaults.
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
                    parseEditorObject(
                      organizationEditor,
                      "Organization override settings",
                    );
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

        <div className="mt-6 rounded-lg border border-border bg-card p-4 shadow-card">
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
      </motion.div>
    </div>
  );
}