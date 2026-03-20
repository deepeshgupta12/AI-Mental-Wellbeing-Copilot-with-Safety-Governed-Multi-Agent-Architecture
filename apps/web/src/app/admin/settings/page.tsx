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

export default function EnterpriseSettingsPage() {
  const queryClient = useQueryClient();

  const [organizationId, setOrganizationId] = useState("");
  const [deploymentEditor, setDeploymentEditor] = useState("{}");
  const [organizationEditor, setOrganizationEditor] = useState("{}");
  const [deploymentChangeNote, setDeploymentChangeNote] = useState("");
  const [organizationChangeNote, setOrganizationChangeNote] = useState("");

  const deploymentSettingsQuery = useQuery({
    queryKey: ["admin-deployment-settings"],
    queryFn: getAdminDeploymentSettings,
  });

  const organizationSettingsQuery = useQuery({
    queryKey: ["admin-organization-settings", organizationId],
    queryFn: () => getAdminOrganizationSettings(organizationId),
    enabled: organizationId.trim().length > 0,
  });

  const resolvedSettingsQuery = useQuery({
    queryKey: ["admin-resolved-enterprise-settings", organizationId],
    queryFn: () => getAdminResolvedEnterpriseSettings(organizationId || null),
  });

  useEffect(() => {
    if (deploymentSettingsQuery.data) {
      setDeploymentEditor(JSON.stringify(deploymentSettingsQuery.data.payload_json, null, 2));
    }
  }, [deploymentSettingsQuery.data]);

  useEffect(() => {
    if (organizationSettingsQuery.data) {
      setOrganizationEditor(JSON.stringify(organizationSettingsQuery.data.payload_json, null, 2));
    } else if (!organizationId.trim()) {
      setOrganizationEditor("{}");
    }
  }, [organizationSettingsQuery.data, organizationId]);

  const deploymentMutation = useMutation({
    mutationFn: async () => {
      const parsed = JSON.parse(deploymentEditor) as Record<string, unknown>;
      return updateAdminDeploymentSettings(parsed, deploymentChangeNote || null);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-deployment-settings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-resolved-enterprise-settings"] });
      setDeploymentChangeNote("");
    },
  });

  const organizationMutation = useMutation({
    mutationFn: async () => {
      const parsed = JSON.parse(organizationEditor) as Record<string, unknown>;
      return updateAdminOrganizationSettings(
        organizationId,
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
              onChange={(e) => setDeploymentEditor(e.target.value)}
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
                onClick={() => deploymentMutation.mutate()}
                className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background"
              >
                {deploymentMutation.isPending ? "Saving..." : "Save Deployment Settings"}
              </button>
            </div>

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
              onChange={(e) => setOrganizationId(e.target.value)}
              placeholder="Organization ID"
              className="mb-3 w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
            />

            <textarea
              value={organizationEditor}
              onChange={(e) => setOrganizationEditor(e.target.value)}
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
                onClick={() => organizationMutation.mutate()}
                disabled={!organizationId.trim()}
                className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background disabled:opacity-60"
              >
                {organizationMutation.isPending ? "Saving..." : "Save Organization Overrides"}
              </button>
            </div>

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