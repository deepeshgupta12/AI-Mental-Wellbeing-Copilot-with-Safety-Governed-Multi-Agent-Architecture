"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { getAdminReviewerDashboard } from "@/lib/admin-api";

export default function ReviewerDashboardPage() {
  const dashboardQuery = useQuery({
    queryKey: ["admin-reviewer-dashboard"],
    queryFn: getAdminReviewerDashboard,
  });

  const data = dashboardQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Reviewer Dashboard
        </h1>

        {!data ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading reviewer dashboard...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {[
                { label: "Total Events", value: data.total_events },
                { label: "Queued", value: data.queued_events },
                { label: "In Review", value: data.in_review_events },
                { label: "Resolved", value: data.resolved_events },
              ].map((item) => (
                <div key={item.label} className="rounded-lg border border-border bg-card p-4 shadow-card">
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Severity Breakdown
                </h2>
                <div className="space-y-2">
                  {Object.entries(data.severity_breakdown).length === 0 ? (
                    <div className="text-sm text-muted-foreground">No data available.</div>
                  ) : (
                    Object.entries(data.severity_breakdown).map(([key, value]) => (
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
                  Escalation Status Breakdown
                </h2>
                <div className="space-y-2">
                  {Object.entries(data.escalation_status_breakdown).length === 0 ? (
                    <div className="text-sm text-muted-foreground">No data available.</div>
                  ) : (
                    Object.entries(data.escalation_status_breakdown).map(([key, value]) => (
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
                Recent Reviews
              </h2>
              <div className="space-y-3">
                {data.recent_reviews.length === 0 ? (
                  <div className="text-sm text-muted-foreground">No recent reviews available.</div>
                ) : (
                  data.recent_reviews.map((review) => (
                    <div key={review.id} className="rounded-md border border-border bg-background p-3">
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-sm font-medium text-foreground">{review.review_status}</div>
                        <div className="text-[11px] text-muted-foreground">
                          {review.reviewer_id || "unknown reviewer"}
                        </div>
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        {review.human_summary || review.reviewer_note || "No summary available"}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}