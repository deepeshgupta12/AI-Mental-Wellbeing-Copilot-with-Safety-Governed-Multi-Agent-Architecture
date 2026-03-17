import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { BackendStatusCard } from "@/components/system/BackendStatusCard";
import { getCurrentUserDisplayName, getCurrentUserId } from "@/lib/demo-session";
import { getMemorySummary, getTrendSummary } from "@/lib/memory-api";
import { listActionPlans } from "@/lib/action-plans-api";
import { getSafetyDashboardCounts } from "@/lib/safety-api";
import {
  Activity,
  MessageCircle,
  BookOpen,
  TrendingUp,
  ArrowRight,
  Sun,
  Moon,
  Zap,
  ShieldAlert,
} from "lucide-react";

const fadeIn = {
  hidden: { opacity: 0, y: 10 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.06, duration: 0.4 },
  }),
};

export default function DashboardPage() {
  const userId = getCurrentUserId();
  const storedName = getCurrentUserDisplayName();
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  const trendQuery = useQuery({
    queryKey: ["trend-summary", userId],
    queryFn: () => getTrendSummary(userId!),
    enabled: !!userId,
  });

  const memoryQuery = useQuery({
    queryKey: ["memory-summary", userId],
    queryFn: () => getMemorySummary(userId!),
    enabled: !!userId,
  });

  const plansQuery = useQuery({
    queryKey: ["action-plans", userId],
    queryFn: () => listActionPlans(userId!),
    enabled: !!userId,
  });

  const safetyCountsQuery = useQuery({
    queryKey: ["safety-dashboard-counts"],
    queryFn: getSafetyDashboardCounts,
    enabled: !!userId,
  });

  const displayName =
    memoryQuery.data?.display_name || storedName || "there";

  const latestMemory = memoryQuery.data?.recent_memories?.[0];
  const planItems = (plansQuery.data ?? []).slice(0, 3);

  return (
    <div className="max-w-6xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div
        initial="hidden"
        animate="visible"
        variants={{ visible: { transition: { staggerChildren: 0.06 } } }}
      >
        <motion.div variants={fadeIn} custom={0} className="mb-8">
          <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground">
            {greeting}, {displayName}.
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            {userId
              ? "Your latest wellbeing snapshot and continuity signals are below."
              : "Complete onboarding to start your live wellbeing dashboard."}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <motion.div
              variants={fadeIn}
              custom={1}
              className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8"
            >
              {[
                { label: "Check in", icon: Activity, to: "/app/checkin", color: "text-primary" },
                { label: "Talk", icon: MessageCircle, to: "/app/chat", color: "text-primary" },
                { label: "Journal", icon: BookOpen, to: "/app/journal", color: "text-primary" },
                { label: "Insights", icon: TrendingUp, to: "/app/insights", color: "text-primary" },
              ].map((action) => (
                <Link
                  key={action.label}
                  to={action.to}
                  className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border bg-card shadow-card hover:shadow-aether-md transition-aether"
                >
                  <action.icon className={`w-5 h-5 ${action.color}`} strokeWidth={1.5} />
                  <span className="text-xs font-medium text-foreground">{action.label}</span>
                </Link>
              ))}
            </motion.div>

            <motion.div
              variants={fadeIn}
              custom={2}
              className="p-6 rounded-lg border border-border bg-card shadow-card mb-6"
            >
              <h2 className="font-heading font-semibold text-foreground text-sm mb-4">
                Daily Snapshot
              </h2>

              {!userId ? (
                <p className="text-sm text-muted-foreground">
                  No live user session found yet. Complete onboarding first.
                </p>
              ) : trendQuery.isLoading ? (
                <p className="text-sm text-muted-foreground">Loading your latest trend summary...</p>
              ) : (
                <div className="grid grid-cols-3 gap-4">
                  {[
                    {
                      label: "Mood",
                      value:
                        trendQuery.data?.avg_mood_score != null
                          ? `${trendQuery.data.avg_mood_score}/10`
                          : "—",
                      icon: Sun,
                      trend: `${trendQuery.data?.total_check_ins ?? 0} total check-ins`,
                    },
                    {
                      label: "Sleep",
                      value:
                        trendQuery.data?.avg_sleep_hours != null
                          ? `${trendQuery.data.avg_sleep_hours}h`
                          : "—",
                      icon: Moon,
                      trend:
                        trendQuery.data?.latest_check_in_at
                          ? "Based on recent entries"
                          : "No recent check-ins",
                    },
                    {
                      label: "Stress",
                      value:
                        trendQuery.data?.avg_stress_score != null
                          ? `${trendQuery.data.avg_stress_score}/10`
                          : "—",
                      icon: Zap,
                      trend: `${trendQuery.data?.total_journal_entries ?? 0} journal entries`,
                    },
                  ].map((metric) => (
                    <div key={metric.label} className="text-center">
                      <metric.icon
                        className="w-4 h-4 text-muted-foreground mx-auto mb-2"
                        strokeWidth={1.5}
                      />
                      <p className="text-sm font-semibold text-foreground">{metric.value}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{metric.label}</p>
                      <p className="text-[10px] text-muted-foreground mt-1">{metric.trend}</p>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>

            <motion.div
              variants={fadeIn}
              custom={3}
              className="p-6 rounded-lg border border-border bg-card shadow-card mb-6"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="font-heading font-semibold text-foreground text-sm mb-1">
                    Continue Reflection
                  </h2>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {latestMemory
                      ? latestMemory.summary
                      : "Start a conversation or add a journal entry to build continuity over time."}
                  </p>
                </div>
                <Link to="/app/chat">
                  <Button variant="ghost" size="sm">
                    Continue <ArrowRight className="w-3 h-3 ml-1" />
                  </Button>
                </Link>
              </div>
            </motion.div>

            <motion.div
              variants={fadeIn}
              custom={4}
              className="p-6 rounded-lg border border-border bg-card shadow-card mb-6"
            >
              <h2 className="font-heading font-semibold text-foreground text-sm mb-4">
                Today's Focus
              </h2>

              {plansQuery.isLoading ? (
                <p className="text-sm text-muted-foreground">Loading your action plan...</p>
              ) : planItems.length === 0 ? (
                <>
                  <p className="text-xs text-muted-foreground mb-3">
                    No saved action plans yet. Create one from your reflections and check-ins.
                  </p>
                  <Link to="/app/plans" className="inline-block mt-1">
                    <Button variant="soft" size="sm">
                      Go to plans
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <p className="text-xs text-muted-foreground mb-3">
                    Your latest saved actions are shown below.
                  </p>
                  <div className="space-y-2.5">
                    {planItems.map((task) => (
                      <div key={task.id} className="flex items-center gap-3 text-sm">
                        <div className="w-4 h-4 rounded border border-border shrink-0" />
                        <span className="text-foreground">{task.title}</span>
                      </div>
                    ))}
                  </div>
                  <Link to="/app/plans" className="inline-block mt-4">
                    <Button variant="soft" size="sm">
                      View full plan
                    </Button>
                  </Link>
                </>
              )}
            </motion.div>

            <motion.div variants={fadeIn} custom={5} className="pt-4 border-t border-border">
              <Link
                to="/app/safety"
                className="flex items-center gap-2 text-sm text-urgent hover:text-urgent/80 transition-aether font-medium"
              >
                <ShieldAlert className="w-4 h-4" strokeWidth={1.5} />
                Safety & Resources
                {safetyCountsQuery.data && safetyCountsQuery.data.open_flags > 0 && (
                  <span className="text-[11px] text-muted-foreground font-normal">
                    · {safetyCountsQuery.data.open_flags} open safety items in admin queue
                  </span>
                )}
              </Link>
            </motion.div>
          </div>

          <div className="xl:col-span-1">
            <motion.div variants={fadeIn} custom={2} className="mb-6">
              <BackendStatusCard />
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}