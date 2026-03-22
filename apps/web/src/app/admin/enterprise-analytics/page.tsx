"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import {
  getAdminEnterpriseAnalyticsOverview,
  getAdminEnterpriseOrganizationDetail,
} from "@/lib/admin-api";

export default function EnterpriseAnalyticsPage() {
  const [selectedOrganizationId, setSelectedOrganizationId] = useState<string | null>(null);

  const overviewQuery = useQuery({
    queryKey: ["admin-enterprise-analytics-overview"],
    queryFn: getAdminEnterpriseAnalyticsOverview,
  });

  const selectedOrgId = selectedOrganizationId ?? overviewQuery.data?.organizations?.[0]?.id ?? null;

  const detailQuery = useQuery({
    queryKey: ["admin-enterprise-organization-detail", selectedOrgId],
    queryFn: () => getAdminEnterpriseOrganizationDetail(selectedOrgId as string),
    enabled: Boolean(selectedOrgId),
  });

  const data = overviewQuery.data;
  const detail = detailQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Enterprise Analytics
        </h1>

        {!data ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading enterprise analytics...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-6">
              {[
                { label: "Organizations", value: data.total_organizations },
                { label: "Active Orgs", value: data.active_organizations },
                { label: "Memberships", value: data.total_memberships },
                { label: "Auth Sessions", value: data.total_auth_sessions },
                { label: "Artifacts", value: data.stored_artifact_count },
                { label: "Immutable Audit Logs", value: data.immutable_audit_log_count },
              ].map((item) => (
                <div key={item.label} className="rounded-lg border border-border bg-card p-4 shadow-card">
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                  <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Organizations
                </h2>
                <div className="space-y-3">
                  {data.organizations.map((org) => {
                    const active = org.id === selectedOrgId;
                    return (
                      <button
                        key={org.id}
                        type="button"
                        onClick={() => setSelectedOrganizationId(org.id)}
                        className={`w-full rounded-md border p-3 text-left transition-aether ${
                          active
                            ? "border-foreground/30 bg-foreground/5"
                            : "border-border bg-background hover:bg-muted/40"
                        }`}
                      >
                        <div className="text-sm font-medium text-foreground">{org.name}</div>
                        <div className="mt-1 text-xs text-muted-foreground">{org.slug}</div>
                        <div className="mt-2 text-[11px] text-muted-foreground">
                          {org.membership_count} memberships · {org.active_session_count} sessions
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                  Organization Detail
                </h2>

                {!detail ? (
                  <div className="text-sm text-muted-foreground">
                    Select an organization to inspect Pack 4 enterprise analytics and Pack 5 runtime posture.
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-3">
                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="text-xs text-muted-foreground">Organization</div>
                        <div className="mt-2 text-sm font-medium text-foreground">
                          {detail.organization.name}
                        </div>
                        <div className="mt-1 text-xs text-muted-foreground">
                          {detail.organization.slug}
                        </div>
                      </div>
                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="text-xs text-muted-foreground">Memberships</div>
                        <div className="mt-2 text-sm font-medium text-foreground">
                          {detail.organization.membership_count}
                        </div>
                      </div>
                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="text-xs text-muted-foreground">Active Sessions</div>
                        <div className="mt-2 text-sm font-medium text-foreground">
                          {detail.organization.active_session_count}
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-6 lg:grid-cols-2">
                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="mb-2 text-xs font-medium uppercase text-muted-foreground">
                          Membership Breakdown
                        </div>
                        <pre className="overflow-x-auto whitespace-pre-wrap text-[11px] text-muted-foreground">
                          {JSON.stringify(detail.membership_breakdown_by_role, null, 2)}
                        </pre>
                      </div>

                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="mb-2 text-xs font-medium uppercase text-muted-foreground">
                          Recent Auth Sessions
                        </div>
                        <pre className="overflow-x-auto whitespace-pre-wrap text-[11px] text-muted-foreground">
                          {JSON.stringify(detail.recent_auth_sessions, null, 2)}
                        </pre>
                      </div>
                    </div>

                    <div className="grid gap-6 lg:grid-cols-2">
                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="mb-2 text-xs font-medium uppercase text-muted-foreground">
                          Effective Settings
                        </div>
                        <pre className="overflow-x-auto whitespace-pre-wrap text-[11px] text-muted-foreground">
                          {JSON.stringify(detail.effective_settings, null, 2)}
                        </pre>
                      </div>

                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="mb-2 text-xs font-medium uppercase text-muted-foreground">
                          Infrastructure Summary
                        </div>
                        <pre className="overflow-x-auto whitespace-pre-wrap text-[11px] text-muted-foreground">
                          {JSON.stringify(detail.infrastructure_summary, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}