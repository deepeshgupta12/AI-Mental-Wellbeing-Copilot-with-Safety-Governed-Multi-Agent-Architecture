"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getAdminPolicyConfig,
  getAdminPromptRegistryVersions,
  getAdminRoutingRules,
  getAdminRuntimePolicyVersions,
  updateAdminPromptRegistry,
  updateAdminRoutingRules,
  updateAdminRuntimePolicy,
} from "@/lib/admin-api";
import { getApiErrorMessage } from "@/lib/api-client";

type EditableTarget = "runtime_policy" | "prompt_registry" | "routing_rules";

export default function PolicyViewerPage() {
  const queryClient = useQueryClient();
  const [target, setTarget] = useState<EditableTarget>("runtime_policy");
  const [editorValue, setEditorValue] = useState("");
  const [changeNote, setChangeNote] = useState("");

  const policyConfigQuery = useQuery({
    queryKey: ["admin-policy-config"],
    queryFn: getAdminPolicyConfig,
  });

  const routingRulesQuery = useQuery({
    queryKey: ["admin-routing-rules"],
    queryFn: getAdminRoutingRules,
  });

  const runtimeVersionsQuery = useQuery({
    queryKey: ["admin-runtime-policy-versions"],
    queryFn: getAdminRuntimePolicyVersions,
  });

  const promptVersionsQuery = useQuery({
    queryKey: ["admin-prompt-registry-versions"],
    queryFn: getAdminPromptRegistryVersions,
  });

  const currentPayload = useMemo(() => {
    if (!policyConfigQuery.data) return {};
    if (target === "runtime_policy") return policyConfigQuery.data.runtime_policy;
    if (target === "prompt_registry") return policyConfigQuery.data.prompt_registry;
    return routingRulesQuery.data?.live_payload ?? {};
  }, [policyConfigQuery.data, routingRulesQuery.data, target]);

  useEffect(() => {
    setEditorValue(JSON.stringify(currentPayload, null, 2));
  }, [currentPayload]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      const parsed = JSON.parse(editorValue) as Record<string, unknown>;
      if (target === "runtime_policy") {
        return updateAdminRuntimePolicy(parsed, changeNote || null);
      }
      if (target === "prompt_registry") {
        return updateAdminPromptRegistry(parsed, changeNote || null);
      }
      return updateAdminRoutingRules(parsed, changeNote || null);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-policy-config"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-routing-rules"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-runtime-policy-versions"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-prompt-registry-versions"] });
      setChangeNote("");
    },
  });

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6 flex items-center justify-between gap-3">
          <h1 className="font-heading text-2xl font-bold text-foreground">
            Routing / Policy / Prompt Registry
          </h1>
          <select
            value={target}
            onChange={(e) => setTarget(e.target.value as EditableTarget)}
            className="rounded-md border border-border bg-card px-3 py-2 text-sm text-foreground"
          >
            <option value="runtime_policy">runtime_policy</option>
            <option value="prompt_registry">prompt_registry</option>
            <option value="routing_rules">routing_rules</option>
          </select>
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="mb-3 text-sm font-medium text-foreground">Live Config Editor</div>
            <textarea
              value={editorValue}
              onChange={(e) => setEditorValue(e.target.value)}
              className="min-h-[520px] w-full rounded-md border border-border bg-background p-3 font-mono text-xs text-foreground"
            />
            <div className="mt-3 flex flex-col gap-3 md:flex-row">
              <input
                value={changeNote}
                onChange={(e) => setChangeNote(e.target.value)}
                placeholder="Change note"
                className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
              />
              <button
                type="button"
                onClick={() => saveMutation.mutate()}
                className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background"
              >
                {saveMutation.isPending ? "Saving..." : "Save new version"}
              </button>
            </div>
            {saveMutation.isError ? (
              <div className="mt-3 text-sm text-destructive">
                {getApiErrorMessage(saveMutation.error)}
              </div>
            ) : null}
          </div>

          <div className="space-y-6">
            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <div className="mb-3 text-sm font-medium text-foreground">Runtime Policy Versions</div>
              <div className="space-y-2">
                {(runtimeVersionsQuery.data ?? []).map((item) => (
                  <div key={item.id} className="rounded-md border border-border bg-background p-2 text-xs">
                    <div className="text-foreground">v{item.version_number}</div>
                    <div className="text-muted-foreground">{item.change_note || "No change note"}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <div className="mb-3 text-sm font-medium text-foreground">Prompt Registry Versions</div>
              <div className="space-y-2">
                {(promptVersionsQuery.data ?? []).map((item) => (
                  <div key={item.id} className="rounded-md border border-border bg-background p-2 text-xs">
                    <div className="text-foreground">v{item.version_number}</div>
                    <div className="text-muted-foreground">{item.change_note || "No change note"}</div>
                  </div>
                ))}
              </div>
            </div>

            {routingRulesQuery.data ? (
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="mb-3 text-sm font-medium text-foreground">Routing Rules Active Version</div>
                <div className="text-xs text-muted-foreground">
                  v{routingRulesQuery.data.active_version.version_number}
                </div>
                <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-2 text-[11px] text-muted-foreground">
                  {JSON.stringify(routingRulesQuery.data.live_payload, null, 2)}
                </pre>
              </div>
            ) : null}
          </div>
        </div>
      </motion.div>
    </div>
  );
}