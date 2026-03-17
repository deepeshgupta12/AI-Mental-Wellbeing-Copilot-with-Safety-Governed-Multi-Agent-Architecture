import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { TrendingUp, TrendingDown, Minus, Sun, Moon, Zap, Battery } from "lucide-react";
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
  if (trend === "up") return <TrendingUp className="w-4 h-4 text-safe" />;
  if (trend === "recurring") return <TrendingDown className="w-4 h-4 text-urgent" />;
  return <Minus className="w-4 h-4 text-muted-foreground" />;
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
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2">Insights</h1>
        <p className="text-muted-foreground text-sm mb-8">Patterns and trends from your wellbeing data.</p>

        {!userId ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            No active user session found. Please complete onboarding first.
          </div>
        ) : trendQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            Loading trend summary...
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
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
                <div key={m.label} className="p-4 rounded-lg border border-border bg-card shadow-card text-center">
                  <m.icon className="w-4 h-4 text-muted-foreground mx-auto mb-2" strokeWidth={1.5} />
                  <p className="text-lg font-semibold text-foreground font-heading">{m.value}</p>
                  <p className="text-[10px] text-muted-foreground">{m.label}</p>
                  <p className="text-[10px] text-muted-foreground mt-1">{m.change}</p>
                </div>
              ))}
            </div>

            <div className="mb-6">
              <h2 className="font-heading font-semibold text-foreground text-sm mb-3">Observations</h2>
              <div className="space-y-3">
                {insights.map((insight) => (
                  <div key={insight.title} className="p-4 rounded-lg border border-border bg-card shadow-card">
                    <div className="flex items-start gap-3">
                      <TrendIcon trend={insight.trend} />
                      <div>
                        <h3 className="text-sm font-medium text-foreground">{insight.title}</h3>
                        <p className="text-sm text-muted-foreground leading-relaxed mt-1">{insight.desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 rounded-lg border border-border bg-card shadow-card">
              <h2 className="font-heading font-semibold text-foreground text-sm mb-4">Current continuity signals</h2>
              <div className="space-y-3 text-sm text-muted-foreground">
                <p>Latest check-in: {trend?.latest_check_in_at ? new Date(trend.latest_check_in_at).toLocaleString() : "Not available"}</p>
                <p>Latest journal entry: {trend?.latest_journal_entry_at ? new Date(trend.latest_journal_entry_at).toLocaleString() : "Not available"}</p>
                <p>Latest conversation: {trend?.latest_conversation_at ? new Date(trend.latest_conversation_at).toLocaleString() : "Not available"}</p>
              </div>
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
}