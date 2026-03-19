"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminFlaggedSessionDetail,
  getAdminFlaggedSessions,
} from "@/lib/admin-api";

export default function FlaggedSessionsPage() {
  const [selectedFlagId, setSelectedFlagId] = useState<string | null>(null);

  const flagsQuery = useQuery({
    queryKey: ["admin-flagged-sessions"],
    queryFn: getAdminFlaggedSessions,
  });

  const activeFlagId = useMemo(
    () => selectedFlagId ?? flagsQuery.data?.[0]?.id ?? null,
    [selectedFlagId, flagsQuery.data],
  );

  const detailQuery = useQuery({
    queryKey: ["admin-flagged-session-detail", activeFlagId],
    queryFn: () => getAdminFlaggedSessionDetail(activeFlagId as string),
    enabled: Boolean(activeFlagId),
  });

  const items = flagsQuery.data ?? [];

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Flagged Sessions
        </h1>

        <div className="grid gap-6 lg:grid-cols-[340px_minmax(0,1fr)]">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Safety Review Queue
            </h2>
            <div className="space-y-3">
              {items.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedFlagId(item.id)}
                  className={`w-full rounded-md border p-3 text-left transition-aether ${
                    item.id === activeFlagId
                      ? "border-foreground/30 bg-foreground/5"
                      : "border-border bg-background hover:bg-muted/30"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-sm font-medium text-foreground">{item.flag_type}</div>
                    <div className="text-[11px] text-muted-foreground">{item.severity}</div>
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {item.summary || "No summary available."}
                  </div>
                  <div className="mt-2 text-[11px] text-muted-foreground">
                    {new Date(item.created_at).toLocaleString()}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
              Review Detail
            </h2>

            {!detailQuery.data ? (
              <div className="text-sm text-muted-foreground">Select a flagged session to inspect.</div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-md border border-border bg-background p-4">
                  <div className="text-sm font-medium text-foreground">{detailQuery.data.flag.flag_type}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{detailQuery.data.flag.summary}</div>
                  <div className="mt-3 grid gap-2 text-xs text-muted-foreground md:grid-cols-2">
                    <div>User: {detailQuery.data.flag.user_id}</div>
                    <div>Severity: {detailQuery.data.flag.severity}</div>
                    <div>Needs review: {String(detailQuery.data.flag.needs_review)}</div>
                    <div>Resolved: {String(detailQuery.data.flag.is_resolved)}</div>
                    <div>Reviewed at: {detailQuery.data.flag.reviewed_at ?? "—"}</div>
                    <div>Resolved at: {detailQuery.data.flag.resolved_at ?? "—"}</div>
                  </div>
                  <div className="mt-3 rounded-md border border-border p-3 text-sm text-foreground">
                    <div className="mb-1 text-[11px] uppercase text-muted-foreground">
                      Reviewer Note
                    </div>
                    {detailQuery.data.flag.reviewer_note || "No reviewer note recorded yet."}
                  </div>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-md border border-border bg-background p-4">
                    <div className="mb-3 text-sm font-medium text-foreground">Related Traces</div>
                    <div className="space-y-2">
                      {detailQuery.data.related_traces.length === 0 ? (
                        <div className="text-sm text-muted-foreground">No related traces available.</div>
                      ) : (
                        detailQuery.data.related_traces.slice(0, 8).map((trace, index) => (
                          <div key={index} className="rounded-md border border-border p-2 text-xs">
                            <div className="font-mono text-foreground">{String(trace.trace_name)}</div>
                            <div className="text-muted-foreground">{String(trace.agent_name)}</div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  <div className="rounded-md border border-border bg-background p-4">
                    <div className="mb-3 text-sm font-medium text-foreground">Related Sessions</div>
                    <div className="space-y-2">
                      {detailQuery.data.related_sessions.length === 0 ? (
                        <div className="text-sm text-muted-foreground">No related sessions available.</div>
                      ) : (
                        detailQuery.data.related_sessions.slice(0, 8).map((session, index) => (
                          <div key={index} className="rounded-md border border-border p-2 text-xs">
                            <div className="text-foreground">{String(session.title ?? "Untitled session")}</div>
                            <div className="text-muted-foreground">{String(session.status)}</div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}