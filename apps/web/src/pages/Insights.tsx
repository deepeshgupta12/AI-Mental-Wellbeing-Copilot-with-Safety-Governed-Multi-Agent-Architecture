import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, Sun, Moon, Zap, Battery, Calendar } from "lucide-react";

const weeklyData = [
  { day: "Mon", mood: 6, stress: 4, sleep: 7, energy: 5 },
  { day: "Tue", mood: 5, stress: 6, sleep: 5, energy: 4 },
  { day: "Wed", mood: 7, stress: 3, sleep: 7, energy: 6 },
  { day: "Thu", mood: 4, stress: 7, sleep: 4, energy: 3 },
  { day: "Fri", mood: 6, stress: 5, sleep: 6, energy: 5 },
  { day: "Sat", mood: 8, stress: 2, sleep: 8, energy: 7 },
  { day: "Sun", mood: 7, stress: 3, sleep: 7, energy: 6 },
];

const insights = [
  {
    title: "Stress peaks mid-week",
    desc: "Thursday consistently shows elevated stress. This often correlates with work deadlines.",
    trend: "recurring",
  },
  {
    title: "Sleep drives everything",
    desc: "Days with 7+ hours of sleep show 40% better mood and energy scores.",
    trend: "up",
  },
  {
    title: "Weekend recovery pattern",
    desc: "You consistently recover on weekends. Consider whether small weekday resets could help.",
    trend: "stable",
  },
];

const copingEffectiveness = [
  { name: "Breathing exercises", effectiveness: 72 },
  { name: "Walking", effectiveness: 85 },
  { name: "Journaling", effectiveness: 68 },
  { name: "Social connection", effectiveness: 55 },
];

const TrendIcon = ({ trend }: { trend: string }) => {
  if (trend === "up") return <TrendingUp className="w-4 h-4 text-safe" />;
  if (trend === "recurring") return <TrendingDown className="w-4 h-4 text-urgent" />;
  return <Minus className="w-4 h-4 text-muted-foreground" />;
};

export default function InsightsPage() {
  const maxVal = 10;

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2">Insights</h1>
        <p className="text-muted-foreground text-sm mb-8">Patterns and trends from your wellbeing data.</p>

        {/* Weekly chart */}
        <div className="p-6 rounded-lg border border-border bg-card shadow-card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading font-semibold text-foreground text-sm">This Week</h2>
            <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
              <Calendar className="w-3 h-3" />
              Mar 11–17, 2026
            </div>
          </div>

          {/* Simple bar chart */}
          <div className="flex items-end gap-2 h-32 mb-3">
            {weeklyData.map((d) => (
              <div key={d.day} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full flex flex-col items-center gap-0.5">
                  <div
                    className="w-full max-w-[20px] bg-primary/20 rounded-t"
                    style={{ height: `${(d.mood / maxVal) * 100}%`, minHeight: 4 }}
                  />
                </div>
                <span className="text-[10px] text-muted-foreground">{d.day}</span>
              </div>
            ))}
          </div>

          <div className="flex gap-4 text-[11px] text-muted-foreground">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-primary/20" />
              Mood
            </div>
          </div>
        </div>

        {/* Metric summary cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[
            { label: "Avg Mood", value: "6.1", icon: Sun, change: "+0.3" },
            { label: "Avg Stress", value: "4.3", icon: Zap, change: "-0.5" },
            { label: "Avg Sleep", value: "6.3h", icon: Moon, change: "+0.2" },
            { label: "Avg Energy", value: "5.1", icon: Battery, change: "+0.1" },
          ].map((m) => (
            <div key={m.label} className="p-4 rounded-lg border border-border bg-card shadow-card text-center">
              <m.icon className="w-4 h-4 text-muted-foreground mx-auto mb-2" strokeWidth={1.5} />
              <p className="text-lg font-semibold text-foreground font-heading">{m.value}</p>
              <p className="text-[10px] text-muted-foreground">{m.label}</p>
              <p className="text-[10px] text-safe mt-1">{m.change}</p>
            </div>
          ))}
        </div>

        {/* AI Insights */}
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

        {/* Coping effectiveness */}
        <div className="p-6 rounded-lg border border-border bg-card shadow-card">
          <h2 className="font-heading font-semibold text-foreground text-sm mb-4">What's helping</h2>
          <div className="space-y-3">
            {copingEffectiveness.map((c) => (
              <div key={c.name}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-foreground">{c.name}</span>
                  <span className="text-muted-foreground tabular-nums">{c.effectiveness}%</span>
                </div>
                <div className="h-1.5 bg-border rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-safe rounded-full"
                    initial={{ width: 0 }}
                    whileInView={{ width: `${c.effectiveness}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
