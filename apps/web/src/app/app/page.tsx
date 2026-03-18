"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  ArrowRight,
  BookOpen,
  MessageCircle,
  Moon,
  ShieldAlert,
  Sun,
  TrendingUp,
  Zap,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { BackendStatusCard } from "@/components/system/BackendStatusCard";
import { listActionPlans } from "@/lib/action-plans-api";
import { getCurrentUserDisplayName, getCurrentUserId } from "@/lib/demo-session";
import { getMemorySummary, getTrendSummary } from "@/lib/memory-api";
import { getSafetyDashboardCounts } from "@/lib/safety-api";

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

  const displayName = memoryQuery.data?.display_name || storedName || "there";
  const latestMemory = memoryQuery.data?.recent_memories?.[0];
  const planItems = (plansQuery.data ?? []).slice(0, 3);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-12">
      <motion.div
        initial="hidden"
        animate="visible"
        variants={{ visible: { transition: { staggerChildren: 0.06 } } }}
      >
        <motion.div variants={fadeIn} custom={0} className="mb-8">
          <h1 className="font-heading text-2xl font-bold text-foreground md:text-3xl">
            {greeting}, {displayName}.
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {userId
              ? "Your latest wellbeing snapshot and continuity signals are below."
              : "Complete onboarding to start your live wellbeing dashboard."}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <motion.div
              variants={fadeIn}
              custom={1}
              className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-4"
            >
              {[
                { label: "Check in", icon: Activity, to: "/app/checkin" },
                { label: "Talk", icon: MessageCircle, to: "/app/chat" },
                { label: "Journal", icon: BookOpen, to: "/app/journal" },
                { label: "Insights", icon: TrendingUp, to: "/app/insights" },
              ].map((action) => (
                <Link
                  key={action.label}
                  href={action.to}
                  className="flex flex-col items-center gap-2 rounded-lg border border-border bg-card p-4 shadow-card transition-aether hover:shadow-aether-md"
                >
                  <action.icon className="h-5 w-5 text-primary" strokeWidth={1.5} />
                  <span className="text-xs font-medium text-foreground">{action.label}</span>
                </Link>
              ))}
            </motion.div>

            <motion.div
              variants={fadeIn}
              custom={2}
              className="mb-6 rounded-lg border border-border bg-card p-6 shadow-card"
            >
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Daily Snapshot
              </h2>

              {!userId ? (
                <p className="text-sm text-muted-foreground">
                  No live user session found yet. Complete onboarding first.
                </p>
              ) : trendQuery.isLoading ? (
                <p className="text-sm text-muted-foreground">
                  Loading your latest trend summary...
                </p>
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
                      trend: trendQuery.data?.latest_check_in_at
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
                        className="mx-auto mb-2 h-4 w-4 text-muted-foreground"
                        strokeWidth={1.5}
                      />
                      <p className="text-sm font-semibold text-foreground">{metric.value}</p>
                      <p className="mt-0.5 text-[10px] text-muted-foreground">
                        {metric.label}
                      </p>
                      <p className="mt-1 text-[10px] text-muted-foreground">
                        {metric.trend}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>

            <motion.div
              variants={fadeIn}
              custom={3}
              className="mb-6 rounded-lg border border-border bg-card p-6 shadow-card"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="mb-1 font-heading text-sm font-semibold text-foreground">
                    Continue Reflection
                  </h2>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {latestMemory
                      ? latestMemory.summary
                      : "Start a conversation or add a journal entry to build continuity over time."}
                  </p>
                </div>
                <Link href="/app/chat">
                  <Button variant="ghost" size="sm">
                    Continue <ArrowRight className="ml-1 h-3 w-3" />
                  </Button>
                </Link>
              </div>
            </motion.div>

            <motion.div
              variants={fadeIn}
              custom={4}
              className="mb-6 rounded-lg border border-border bg-card p-6 shadow-card"
            >
              <h2 className="mb-4 font-heading text-sm font-semibold text-foreground">
                Today's Focus
              </h2>

              {plansQuery.isLoading ? (
                <p className="text-sm text-muted-foreground">Loading your action plan...</p>
              ) : planItems.length === 0 ? (
                <>
                  <p className="mb-3 text-xs text-muted-foreground">
                    No saved action plans yet. Create one from your reflections and check-ins.
                  </p>
                  <Link href="/app/plans" className="mt-1 inline-block">
                    <Button variant="soft" size="sm">
                      Go to plans
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <p className="mb-3 text-xs text-muted-foreground">
                    Your latest saved actions are shown below.
                  </p>
                  <div className="space-y-2.5">
                    {planItems.map((task) => (
                      <div key={task.id} className="flex items-center gap-3 text-sm">
                        <div className="h-4 w-4 shrink-0 rounded border border-border" />
                        <span className="text-foreground">{task.title}</span>
                      </div>
                    ))}
                  </div>
                  <Link href="/app/plans" className="mt-4 inline-block">
                    <Button variant="soft" size="sm">
                      View full plan
                    </Button>
                  </Link>
                </>
              )}
            </motion.div>

            <motion.div variants={fadeIn} custom={5} className="border-t border-border pt-4">
              <Link
                href="/app/safety"
                className="flex items-center gap-2 text-sm font-medium text-urgent transition-aether hover:text-urgent/80"
              >
                <ShieldAlert className="h-4 w-4" strokeWidth={1.5} />
                Safety & Resources
                {safetyCountsQuery.data && safetyCountsQuery.data.open_flags > 0 && (
                  <span className="text-[11px] font-normal text-muted-foreground">
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