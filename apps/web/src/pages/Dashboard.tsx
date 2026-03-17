import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Activity,
  MessageCircle,
  BookOpen,
  TrendingUp,
  ArrowRight,
  Sun,
  Moon,
  Zap,
  Brain,
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
  const userName = "Alex";
  const streakDays = 4;
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial="hidden" animate="visible" variants={{ visible: { transition: { staggerChildren: 0.06 } } }}>
        {/* Greeting */}
        <motion.div variants={fadeIn} custom={0} className="mb-8">
          <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground">
            {greeting}, {userName}.
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            You've maintained your reflection streak for {streakDays} days. How is your energy now?
          </p>
        </motion.div>

        {/* Quick actions */}
        <motion.div variants={fadeIn} custom={1} className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
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

        {/* Daily Snapshot */}
        <motion.div variants={fadeIn} custom={2} className="p-6 rounded-lg border border-border bg-card shadow-card mb-6">
          <h2 className="font-heading font-semibold text-foreground text-sm mb-4">Daily Snapshot</h2>
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: "Mood", value: "Okay", icon: Sun, trend: "+1 from yesterday" },
              { label: "Sleep", value: "6.5h", icon: Moon, trend: "Below your average" },
              { label: "Stress", value: "Moderate", icon: Zap, trend: "Stable this week" },
            ].map((metric) => (
              <div key={metric.label} className="text-center">
                <metric.icon className="w-4 h-4 text-muted-foreground mx-auto mb-2" strokeWidth={1.5} />
                <p className="text-sm font-semibold text-foreground">{metric.value}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">{metric.label}</p>
                <p className="text-[10px] text-muted-foreground mt-1">{metric.trend}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Continue Reflection */}
        <motion.div variants={fadeIn} custom={3} className="p-6 rounded-lg border border-border bg-card shadow-card mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="font-heading font-semibold text-foreground text-sm mb-1">Continue Reflection</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                We were discussing your boundaries at work and how they relate to your stress patterns...
              </p>
            </div>
            <Link to="/app/chat">
              <Button variant="ghost" size="sm">
                Continue <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Today's Plan */}
        <motion.div variants={fadeIn} custom={4} className="p-6 rounded-lg border border-border bg-card shadow-card mb-6">
          <h2 className="font-heading font-semibold text-foreground text-sm mb-4">Today's Focus</h2>
          <p className="text-xs text-muted-foreground mb-3">Based on your high stress and low sleep, today's plan is focused on Micro-Rest.</p>
          <div className="space-y-2.5">
            {[
              { text: "5-minute breathing exercise", done: false },
              { text: "15-minute walk or stretch break", done: false },
              { text: "Evening wind-down journaling", done: false },
            ].map((task, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <div className="w-4 h-4 rounded border border-border shrink-0" />
                <span className="text-foreground">{task.text}</span>
              </div>
            ))}
          </div>
          <Link to="/app/plans" className="inline-block mt-4">
            <Button variant="soft" size="sm">View full plan</Button>
          </Link>
        </motion.div>

        {/* Safety anchor */}
        <motion.div variants={fadeIn} custom={5} className="pt-4 border-t border-border">
          <Link
            to="/app/safety"
            className="flex items-center gap-2 text-sm text-urgent hover:text-urgent/80 transition-aether font-medium"
          >
            <ShieldAlert className="w-4 h-4" strokeWidth={1.5} />
            Safety & Resources
          </Link>
        </motion.div>
      </motion.div>
    </div>
  );
}
