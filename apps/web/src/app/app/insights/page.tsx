"use client";

import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Battery, Minus, Moon, Sun, TrendingDown, TrendingUp, Zap } from "lucide-react";

import { getCurrentUserId } from "@/lib/demo-session";
import { getTrendSummary } from "@/lib/memory-api";

const insights = [
  {
    title: "Stress and energy often move together",
    desc: "Higher stress can show up alongside lower energy and reduced emotional bandwidth.",
    trend: "recurring",
  },
  {
    title: "Sleep is a powerful stabilizer",
    desc: "Consistent sleep quality often improves mood and decision-making resilience.",
    trend: "up",
  },
  {
    title: "Small repeats matter",
    desc: "Even low-intensity habits can become meaningful when repeated consistently.",
    trend: "stable",
  },
];

const TrendIcon = ({ trend }: { trend: string }) => {
  if (trend === "up") return <TrendingUp className="h-4 w-4 text-safe" />;
  if (trend === "recurring") return <TrendingDown className="h-4 w-4 text-urgent" />;
  return <Minus className="h-4 w-4 text-muted-foreground" />;
};

export default function InsightsPage() {
  const userId = getCurrentUserId();

  const trendQuery = useQuery({
    queryKey: ["trend-summary", userId],
    queryFn: () => getTrendSummary(userId!),
    enabled: !!userId,
  });

  const trend = trendQuery.data;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 md:px-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-2 font-heading text-2xl font-bold text-foreground md:text-3xl">
          Insights
        </h1>
        <p className="mb-8 text-sm text-muted-foreground">
          Patterns and trends from your wellbeing data.
        </p>

        {!userId ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            No active user session found. Please complete onboarding first.
          </div>
        ) : trendQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading trend summary...
          </div>
        ) : (
          <>
            <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
              {[
                {
                  label: "Avg Mood",
                  value: trend?.avg_mood_score != null ? `${trend.avg_mood_score}` : "—",
                  icon: Sun,
                  change: `${trend?.total_check_ins ?? 0} check-ins`,
                },
                {
                  label: "Avg Stress",
                  value: trend?.avg_stress_score != null ? `${trend.avg_stress_score}` : "—",
                  icon: Zap,
                  change: `${trend?.total_journal_entries ?? 0} journal entries`,
                },
                {
                  label: "Avg Sleep",
                  value: trend?.avg_sleep_hours != null ? `${trend.avg_sleep_hours}h` : "—",
                  icon: Moon,
                  change: trend?.latest_check_in_at ? "Recently updated" : "No recent check-in",
                },
                {
                  label: "Conversations",
                  value: `${trend?.total_conversation_sessions ?? 0}`,
                  icon: Battery,
                  change: `${trend?.total_conversation_messages ?? 0} total messages`,
                },
              ].map((m) => (
                <div
                  key={m.label}
                  className="rounded-lg border border-border bg-card p-4 text-center shadow-card"
                >
                  <m.icon className="mx-auto mb-2 h-4 w-4 text-muted-foreground" strokeWidth={1.5} />
                  <p className="font-heading text-lg font-semibold text-foreground">{m.value}</p>
                  <p className="text-[10px] text-muted-foreground">{m.label}</p>
                  <p className="mt-1 text-[10px] text-muted-foreground">{m.change}</p>
                </div>
              ))}
            </div>

            <div className="mb-6">
              <h2 className="mb-3 font-heading text-sm font-semibold text-foreground">
                Observations
              </h2>
              <div className="space-y-3">
                {insights.map((insight) => (
                  <div
                    key={insight.title}
                    className="rounded-lg border border-border bg-card p-4 shadow-card"
                  >
                    <div className="flex items-start gap-3">
                      <TrendIcon trend={insight.trend} />
                      <div>
                        <h3 className="text-sm font-medium text-foreground">{insight.title}</h3>
                        <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                          {insight.desc}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-6 shadow-card">
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Current continuity signals
              </h2>
              <div className="space-y-3 text-sm text-muted-foreground">
                <p>
                  Latest check-in:{" "}
                  {trend?.latest_check_in_at
                    ? new Date(trend.latest_check_in_at).toLocaleString()
                    : "Not available"}
                </p>
                <p>
                  Latest journal entry:{" "}
                  {trend?.latest_journal_entry_at
                    ? new Date(trend.latest_journal_entry_at).toLocaleString()
                    : "Not available"}
                </p>
                <p>
                  Latest conversation:{" "}
                  {trend?.latest_conversation_at
                    ? new Date(trend.latest_conversation_at).toLocaleString()
                    : "Not available"}
                </p>
              </div>
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
}