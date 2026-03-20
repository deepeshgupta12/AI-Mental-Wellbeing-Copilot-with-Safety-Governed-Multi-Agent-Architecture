"use client";

import { motion } from "framer-motion";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import {
  createAdminSafetyEventReview,
  getAdminAuditTimeline,
  getAdminEscalationAnalytics,
  getAdminReviewerDashboard,
  getAdminSafetyEventDetail,
  getAdminSafetyEvents,
} from "@/lib/admin-api";

export default function SafetyEventsPage() {
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const eventsQuery = useQuery({
    queryKey: ["admin-safety-events"],
    queryFn: () => getAdminSafetyEvents(),
  });

  const reviewerDashboardQuery = useQuery({
    queryKey: ["admin-reviewer-dashboard"],
    queryFn: getAdminReviewerDashboard,
  });

  const escalationAnalyticsQuery = useQuery({
    queryKey: ["admin-escalation-analytics"],
    queryFn: getAdminEscalationAnalytics,
  });

  const auditTimelineQuery = useQuery({
    queryKey: ["admin-audit-timeline"],
    queryFn: getAdminAuditTimeline,
  });

  const detailQuery = useQuery({
    queryKey: ["admin-safety-event-detail", selectedEventId],
    queryFn: () => getAdminSafetyEventDetail(selectedEventId!),
    enabled: !!selectedEventId,
  });

  const reviewMutation = useMutation({
    mutationFn: () =>
      createAdminSafetyEventReview(selectedEventId!, {
        reviewer_id: "admin-ui-reviewer",
        review_status: "resolved",
        reviewer_note: "Resolved from reviewer dashboard.",
        human_summary: "Human reviewer confirmed follow-up action.",
        decision_rationale: "Event reviewed and escalated as needed.",
        resolution_type: "human_escalation",
        escalation_required: true,
        escalation_status: "escalated",
        review_payload_json: { source: "admin_ui" },
      }),
    onSuccess: async () => {
      await Promise.all([
        eventsQuery.refetch(),
        reviewerDashboardQuery.refetch(),
        escalationAnalyticsQuery.refetch(),
        auditTimelineQuery.refetch(),
        detailQuery.refetch(),
      ]);
    },
  });

  const events = eventsQuery.data ?? [];
  const dashboard = reviewerDashboardQuery.data;
  const analytics = escalationAnalyticsQuery.data;
  const auditItems = auditTimelineQuery.data ?? [];
  const selectedEvent = detailQuery.data?.event;
  const selectedReviews = detailQuery.data?.reviews ?? [];

  const queuedCount = useMemo(
    () => events.filter((item) => item.queue_status === "queued").length,
    [events],
  );

  const selectedDecisionPath =
    (selectedEvent?.evidence_json?.decision_path_label as string | undefined) ?? "—";

  const selectedHumanSummary =
    (selectedEvent?.evidence_json?.human_summary as string | undefined) ?? "No human summary available.";

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Safety Event Queue
        </h1>

        <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-5">
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Queued</div>
            <div className="mt-2 font-heading text-2xl font-bold text-foreground">
              {dashboard?.queued_events ?? queuedCount}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">In Review</div>
            <div className="mt-2 font-heading text-2xl font-bold text-foreground">
              {dashboard?.in_review_events ?? "—"}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Resolved</div>
            <div className="mt-2 font-heading text-2xl font-bold text-foreground">
              {dashboard?.resolved_events ?? "—"}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">High Risk</div>
            <div className="mt-2 font-heading text-2xl font-bold text-foreground">
              {analytics?.high_risk_events ?? "—"}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-4 shadow-card">
            <div className="text-xs text-muted-foreground">Critical</div>
            <div className="mt-2 font-heading text-2xl font-bold text-foreground">
              {analytics?.critical_events ?? "—"}
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.1fr_1.2fr]">
          <div className="overflow-hidden rounded-lg border border-border bg-card shadow-card">
            <div className="border-b border-border px-4 py-3">
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Review queue
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left">
                    <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Event</th>
                    <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Risk</th>
                    <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Queue</th>
                    <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Detected</th>
                  </tr>
                </thead>
                <tbody>
                  {events.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-4 text-muted-foreground">
                        No safety events found.
                      </td>
                    </tr>
                  ) : (
                    events.map((item) => (
                      <tr
                        key={item.id}
                        onClick={() => setSelectedEventId(item.id)}
                        className={`cursor-pointer border-b border-border last:border-0 hover:bg-muted/30 ${
                          selectedEventId === item.id ? "bg-muted/40" : ""
                        }`}
                      >
                        <td className="px-4 py-3">
                          <div className="text-foreground">{item.title}</div>
                          <div className="mt-1 text-xs text-muted-foreground">
                            {item.summary || item.event_type}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-foreground">{item.risk_level}</td>
                        <td className="px-4 py-3 text-muted-foreground">{item.queue_status}</td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {new Date(item.detected_at).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Safety review detail
              </h2>

              {!selectedEvent ? (
                <div className="text-sm text-muted-foreground">
                  Select a safety event from the queue to inspect evidence, decision path, human summary, and reviews.
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-foreground">{selectedEvent.title}</div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      {selectedEvent.summary || "No summary available"}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="rounded-md border border-border bg-background p-3">
                      <div className="text-muted-foreground">Risk level</div>
                      <div className="mt-1 text-foreground">{selectedEvent.risk_level}</div>
                    </div>
                    <div className="rounded-md border border-border bg-background p-3">
                      <div className="text-muted-foreground">Queue status</div>
                      <div className="mt-1 text-foreground">{selectedEvent.queue_status}</div>
                    </div>
                    <div className="rounded-md border border-border bg-background p-3">
                      <div className="text-muted-foreground">Escalation</div>
                      <div className="mt-1 text-foreground">{selectedEvent.escalation_status}</div>
                    </div>
                    <div className="rounded-md border border-border bg-background p-3">
                      <div className="text-muted-foreground">Human review</div>
                      <div className="mt-1 text-foreground">
                        {selectedEvent.requires_human_review ? "Required" : "Not required"}
                      </div>
                    </div>
                  </div>

                  <div className="rounded-md border border-border bg-background p-3">
                    <div className="mb-1 text-[11px] uppercase text-muted-foreground">
                      Decision path
                    </div>
                    <div className="text-sm text-foreground">{selectedDecisionPath}</div>
                  </div>

                  <div className="rounded-md border border-border bg-background p-3">
                    <div className="mb-1 text-[11px] uppercase text-muted-foreground">
                      Human summary
                    </div>
                    <div className="text-sm text-foreground">{selectedHumanSummary}</div>
                  </div>

                  <div>
                    <div className="mb-2 text-xs font-medium text-muted-foreground">Reviews</div>
                    <div className="space-y-2">
                      {selectedReviews.length === 0 ? (
                        <div className="rounded-md border border-border bg-background p-3 text-sm text-muted-foreground">
                          No reviews yet.
                        </div>
                      ) : (
                        selectedReviews.map((review) => (
                          <div key={review.id} className="rounded-md border border-border bg-background p-3">
                            <div className="flex items-center justify-between gap-3">
                              <div className="text-sm font-medium text-foreground">
                                {review.review_status}
                              </div>
                              <div className="text-[11px] text-muted-foreground">
                                {review.reviewer_id || "unknown reviewer"}
                              </div>
                            </div>
                            <div className="mt-2 text-xs text-muted-foreground">
                              {review.reviewer_note || review.human_summary || "No note"}
                            </div>
                            {review.decision_rationale ? (
                              <div className="mt-2 text-[11px] text-muted-foreground">
                                Rationale: {review.decision_rationale}
                              </div>
                            ) : null}
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 text-xs font-medium text-muted-foreground">
                      Evidence payload
                    </div>
                    <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-[11px] text-muted-foreground">
                      {JSON.stringify(selectedEvent.evidence_json ?? {}, null, 2)}
                    </pre>
                  </div>

                  <button
                    onClick={() => reviewMutation.mutate()}
                    disabled={reviewMutation.isPending}
                    className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-aether hover:opacity-90 disabled:opacity-60"
                  >
                    {reviewMutation.isPending ? "Updating..." : "Mark reviewed & escalated"}
                  </button>
                </div>
              )}
            </div>

            <div className="rounded-lg border border-border bg-card p-4 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Audit timeline
              </h2>
              <div className="space-y-2">
                {auditItems.length === 0 ? (
                  <div className="text-sm text-muted-foreground">No audit items available.</div>
                ) : (
                  auditItems.slice(0, 10).map((item) => (
                    <div key={item.id} className="rounded-md border border-border bg-background p-3">
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-sm text-foreground">{item.title}</div>
                        <div className="text-[11px] text-muted-foreground">
                          {item.is_immutable ? "immutable" : "mutable"}
                        </div>
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        {item.event_type} · {new Date(item.occurred_at).toLocaleString()}
                      </div>
                      {item.details ? (
                        <div className="mt-2 text-[11px] text-muted-foreground">{item.details}</div>
                      ) : null}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}