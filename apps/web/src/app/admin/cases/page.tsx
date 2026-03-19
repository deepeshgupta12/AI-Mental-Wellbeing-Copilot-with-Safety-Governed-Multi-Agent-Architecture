"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminAgentTraceExecutionDetail,
  getAdminAgentTraceExecutions,
} from "@/lib/admin-api";

export default function CaseReviewPage() {
  const [selectedTraceName, setSelectedTraceName] = useState<string | null>(null);

  const executionsQuery = useQuery({
    queryKey: ["admin-agent-trace-executions"],
    queryFn: getAdminAgentTraceExecutions,
  });

  const defaultTraceName = useMemo(() => {
    return selectedTraceName ?? executionsQuery.data?.[0]?.trace_name ?? null;
  }, [selectedTraceName, executionsQuery.data]);

  const detailQuery = useQuery({
    queryKey: ["admin-agent-trace-execution-detail", defaultTraceName],
    queryFn: () => getAdminAgentTraceExecutionDetail(defaultTraceName as string),
    enabled: Boolean(defaultTraceName),
  });

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Agent Trace Viewer
        </h1>

        <div className="grid gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Grouped Runtime Executions
            </h2>
            <div className="space-y-3">
              {(executionsQuery.data ?? []).map((item) => {
                const active = item.trace_name === defaultTraceName;
                return (
                  <button
                    key={item.trace_name}
                    type="button"
                    onClick={() => setSelectedTraceName(item.trace_name)}
                    className={`w-full rounded-md border p-3 text-left transition-aether ${
                      active
                        ? "border-foreground/30 bg-foreground/5"
                        : "border-border bg-background hover:bg-muted/40"
                    }`}
                  >
                    <div className="font-mono text-xs text-foreground">{item.trace_name}</div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      {item.agents.join(" → ")}
                    </div>
                    <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                      <span>{item.event_count} events</span>
                      <span>{new Date(item.latest_at).toLocaleString()}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Execution Detail
            </h2>

            {!detailQuery.data ? (
              <div className="text-sm text-muted-foreground">Select a trace execution to inspect.</div>
            ) : (
              <div className="space-y-3">
                {detailQuery.data.events.map((event) => (
                  <div key={event.id} className="rounded-md border border-border bg-background p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-foreground">{event.agent_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {event.handoff_from_agent && event.handoff_to_agent
                            ? `${event.handoff_from_agent} → ${event.handoff_to_agent}`
                            : "No explicit handoff"}
                        </div>
                      </div>
                      <div className="text-right text-xs text-muted-foreground">
                        <div>{event.status}</div>
                        <div>{new Date(event.created_at).toLocaleString()}</div>
                      </div>
                    </div>

                    <div className="mt-3 grid gap-3 lg:grid-cols-2">
                      <div>
                        <div className="mb-1 text-[11px] font-medium uppercase text-muted-foreground">
                          Input
                        </div>
                        <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border p-2 text-[11px] text-muted-foreground">
                          {JSON.stringify(event.input_payload_json ?? {}, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <div className="mb-1 text-[11px] font-medium uppercase text-muted-foreground">
                          Output
                        </div>
                        <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border p-2 text-[11px] text-muted-foreground">
                          {JSON.stringify(event.output_payload_json ?? {}, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}