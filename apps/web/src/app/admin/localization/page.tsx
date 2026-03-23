"use client";

import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Globe2, Languages, MessageSquareText, ShieldCheck } from "lucide-react";

import { getApiErrorMessage } from "@/lib/api-client";
import {
  getAdminLocalizationOverview,
  getLocalizationCatalog,
  getLocalizationRuntimeCopy,
} from "@/lib/localization-api";

function topEntry(input: Record<string, number> | undefined) {
  const entries = Object.entries(input ?? {});
  if (!entries.length) return null;
  return entries.sort((a, b) => b[1] - a[1])[0];
}

export default function AdminLocalizationPage() {
  const [organizationId, setOrganizationId] = useState("");
  const [previewLanguage, setPreviewLanguage] = useState("en");

  const overviewQuery = useQuery({
    queryKey: ["admin-localization-overview", organizationId],
    queryFn: () => getAdminLocalizationOverview(organizationId || null),
  });

  const catalogQuery = useQuery({
    queryKey: ["localization-catalog"],
    queryFn: getLocalizationCatalog,
  });

  const previewQuery = useQuery({
    queryKey: ["localization-runtime-copy", previewLanguage],
    queryFn: () => getLocalizationRuntimeCopy(previewLanguage),
  });

  const preferredLeader = useMemo(
    () => topEntry(overviewQuery.data?.language_preference_breakdown),
    [overviewQuery.data],
  );

  const carePlanLeader = useMemo(
    () => topEntry(overviewQuery.data?.care_plan_language_breakdown),
    [overviewQuery.data],
  );

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
              <Languages className="h-3.5 w-3.5" />
              Language operations
            </div>
            <h1 className="font-heading text-3xl font-bold text-foreground">Language & Copy</h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">
              Understand what language members prefer, where fallback language is being used, and
              how recurring support programs are being configured.
            </p>
          </div>

          <label className="space-y-2">
            <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Organization filter
            </span>
            <input
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              placeholder="Optional organization ID"
              className="w-full min-w-[260px] rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
            />
          </label>
        </div>

        <div className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Default language</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.default_language ?? "—"}
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Supported languages</p>
            <p className="mt-2 text-3xl font-bold text-foreground">
              {overviewQuery.data?.supported_language_codes?.length ?? "—"}
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Top preference language</p>
            <p className="mt-2 text-2xl font-bold text-foreground">
              {preferredLeader?.[0] ?? "—"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              {preferredLeader ? `${preferredLeader[1]} members` : "No preference data yet"}
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-4 shadow-card">
            <p className="text-xs text-muted-foreground">Top care-program language</p>
            <p className="mt-2 text-2xl font-bold text-foreground">
              {carePlanLeader?.[0] ?? "—"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              {carePlanLeader ? `${carePlanLeader[1]} programs` : "No program data yet"}
            </p>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
          <section className="rounded-3xl border border-border bg-card p-5 shadow-card">
            <div className="mb-4 flex items-center gap-2">
              <Globe2 className="h-4 w-4 text-muted-foreground" />
              <h2 className="font-heading text-xl font-semibold text-foreground">
                Language mix
              </h2>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-border bg-background p-4">
                <p className="text-sm font-semibold text-foreground">Member preference mix</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  What language members actively prefer for the product experience.
                </p>
                <div className="mt-4 space-y-2">
                  {Object.entries(overviewQuery.data?.language_preference_breakdown ?? {}).map(
                    ([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-xl border border-border px-3 py-2"
                      >
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm font-medium text-foreground">{value}</span>
                      </div>
                    ),
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-border bg-background p-4">
                <p className="text-sm font-semibold text-foreground">Content language mix</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  The language currently chosen for content delivery.
                </p>
                <div className="mt-4 space-y-2">
                  {Object.entries(overviewQuery.data?.content_language_breakdown ?? {}).map(
                    ([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-xl border border-border px-3 py-2"
                      >
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm font-medium text-foreground">{value}</span>
                      </div>
                    ),
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-border bg-background p-4">
                <p className="text-sm font-semibold text-foreground">Fallback language mix</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Backup language used when direct content is unavailable.
                </p>
                <div className="mt-4 space-y-2">
                  {Object.entries(overviewQuery.data?.fallback_language_breakdown ?? {}).map(
                    ([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-xl border border-border px-3 py-2"
                      >
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm font-medium text-foreground">{value}</span>
                      </div>
                    ),
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-border bg-background p-4">
                <p className="text-sm font-semibold text-foreground">Care-program language mix</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Which languages recurring support programs are currently configured with.
                </p>
                <div className="mt-4 space-y-2">
                  {Object.entries(overviewQuery.data?.care_plan_language_breakdown ?? {}).map(
                    ([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-xl border border-border px-3 py-2"
                      >
                        <span className="text-sm text-foreground">{key}</span>
                        <span className="text-sm font-medium text-foreground">{value}</span>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>
          </section>

          <section className="space-y-6">
            <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
              <div className="mb-4 flex items-center gap-2">
                <MessageSquareText className="h-4 w-4 text-muted-foreground" />
                <h2 className="font-heading text-xl font-semibold text-foreground">
                  Runtime copy preview
                </h2>
              </div>

              <label className="mb-4 block space-y-2">
                <span className="text-sm font-medium text-foreground">Preview language</span>
                <select
                  value={previewLanguage}
                  onChange={(e) => setPreviewLanguage(e.target.value)}
                  className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                >
                  {(catalogQuery.data?.supported_languages ?? []).map((item) => (
                    <option key={item.language_code} value={item.language_code}>
                      {item.display_name}
                    </option>
                  ))}
                </select>
              </label>

              <div className="space-y-3">
                {Object.entries(previewQuery.data?.copy ?? {}).map(([key, value]) => (
                  <div key={key} className="rounded-xl border border-border bg-background p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      {key}
                    </p>
                    <p className="mt-2 text-sm text-foreground">{String(value)}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
              <div className="mb-4 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-muted-foreground" />
                <h2 className="font-heading text-xl font-semibold text-foreground">
                  How to read this screen
                </h2>
              </div>

              <div className="space-y-3 text-sm text-muted-foreground">
                <p>
                  <span className="font-medium text-foreground">Preference mix</span> tells you what
                  members want.
                </p>
                <p>
                  <span className="font-medium text-foreground">Content mix</span> tells you what
                  they are currently receiving.
                </p>
                <p>
                  <span className="font-medium text-foreground">Fallback mix</span> helps identify
                  where language coverage may be incomplete.
                </p>
                <p>
                  <span className="font-medium text-foreground">Care-program language mix</span>
                  shows how recurring support is being delivered across languages.
                </p>
              </div>
            </div>
          </section>
        </div>

        {(overviewQuery.isError || catalogQuery.isError || previewQuery.isError) && (
          <div className="mt-6 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
            {getApiErrorMessage(
              overviewQuery.error || catalogQuery.error || previewQuery.error,
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}