"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { getAdminLocalizationOverview, getLocalizationCatalog } from "@/lib/localization-api";

export default function AdminLocalizationPage() {
  const catalogQuery = useQuery({
    queryKey: ["localization-catalog"],
    queryFn: getLocalizationCatalog,
  });

  const overviewQuery = useQuery({
    queryKey: ["admin-localization-overview"],
    queryFn: () => getAdminLocalizationOverview(null),
  });

  const catalog = catalogQuery.data;
  const overview = overviewQuery.data;

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-6">
          <h1 className="font-heading text-2xl font-bold text-foreground">Localization</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Review supported languages, user language adoption, and care-plan language usage.
          </p>
        </div>

        {!catalog || !overview ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading localization overview...
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Default Language</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {catalog.default_language}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Supported Languages</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {catalog.supported_languages.length}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Safety Copy Keys</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {catalog.safety_copy_keys.length}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <div className="text-xs text-muted-foreground">Localized Sections</div>
                <div className="mt-2 font-heading text-2xl font-bold text-foreground">
                  {catalog.localized_ui_sections.length}
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Supported Languages</h2>
                <div className="space-y-2">
                  {catalog.supported_languages.map((item) => (
                    <div key={item.language_code} className="rounded-md border border-border bg-background px-3 py-2">
                      <div className="text-sm text-foreground">
                        {item.display_name} · {item.native_name}
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">{item.language_code}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">User Language Breakdown</h2>
                <div className="space-y-2">
                  {Object.entries(overview.user_language_breakdown).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                      <span className="text-sm text-foreground">{key}</span>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">Care Plan Language Breakdown</h2>
                <div className="space-y-2">
                  {Object.entries(overview.care_plan_language_breakdown).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2">
                      <span className="text-sm text-foreground">{key}</span>
                      <span className="text-sm text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}