"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Brain,
  Heart,
  Lock,
  Shield,
  TrendingUp,
} from "lucide-react";

import { Button } from "@/components/ui/button";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1] as [number, number, number, number],
    },
  }),
};

const features = [
  {
    icon: Brain,
    title: "Intelligent Reflection",
    desc: "AI-guided conversations that help you understand your patterns, not just track them.",
  },
  {
    icon: TrendingUp,
    title: "Trend Awareness",
    desc: "See how your mood, stress, and energy shift over days and weeks — in context.",
  },
  {
    icon: Heart,
    title: "Coping Support",
    desc: "Evidence-informed techniques delivered when you need them, adapted to your style.",
  },
  {
    icon: Shield,
    title: "Safety-First Design",
    desc: "Built with safe escalation, clear boundaries, and human oversight at every layer.",
  },
];

const steps = [
  { num: "01", title: "Check in daily", desc: "A quick pulse on mood, stress, sleep, and energy." },
  { num: "02", title: "Reflect with support", desc: "Structured conversations that help you unpack and understand." },
  { num: "03", title: "See your patterns", desc: "Insights emerge over time — trends, triggers, what helps." },
  { num: "04", title: "Build your plan", desc: "Practical, flexible action steps that fit your life." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
              <span className="font-heading text-sm font-bold text-primary-foreground">A</span>
            </div>
            <span className="font-heading text-lg font-semibold text-foreground">Aether</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/auth">
              <Button variant="ghost" size="sm">Sign in</Button>
            </Link>
            <Link href="/auth?mode=signup">
              <Button variant="hero" size="sm">Get started</Button>
            </Link>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-6xl px-6 pb-24 pt-20 md:pb-36 md:pt-32">
          <motion.div
            className="max-w-2xl"
            initial="hidden"
            animate="visible"
            variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
          >
            <motion.div variants={fadeUp} custom={0}>
              <span className="mb-6 inline-flex items-center gap-1.5 rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
                <Lock className="h-3 w-3" />
                Private · Safe · Not therapy
              </span>
            </motion.div>
            <motion.h1
              variants={fadeUp}
              custom={1}
              className="font-heading text-4xl font-bold leading-[1.1] tracking-tight text-foreground md:text-6xl"
            >
              Your wellbeing deserves
              <br />
              calm intelligence.
            </motion.h1>
            <motion.p
              variants={fadeUp}
              custom={2}
              className="mt-6 max-w-lg text-lg leading-relaxed text-muted-foreground md:text-xl"
            >
              Aether is an AI mental wellbeing copilot for stress, burnout, overwhelm,
              and self-reflection — with real support boundaries and safety at every step.
            </motion.p>
            <motion.div variants={fadeUp} custom={3} className="mt-8 flex flex-wrap gap-3">
              <Link href="/auth?mode=signup">
                <Button variant="hero" size="lg">
                  Start your journey
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button variant="outline" size="lg">How it works</Button>
              </a>
            </motion.div>
          </motion.div>
        </div>
        <div className="pointer-events-none absolute right-0 top-0 h-full w-1/2 bg-gradient-to-l from-primary/[0.03] to-transparent" />
      </section>

      <section className="border-t border-border bg-card">
        <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
          <h2 className="mb-4 font-heading text-2xl font-bold text-foreground md:text-3xl">
            Support that understands you.
          </h2>
          <p className="mb-12 max-w-lg text-base text-muted-foreground md:text-lg">
            Not a chatbot. Not a meditation timer. A structured companion for your mental wellbeing.
          </p>
          <div className="grid gap-6 md:grid-cols-2">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                className="rounded-lg border border-border bg-background p-6 shadow-card"
              >
                <f.icon className="mb-4 h-6 w-6 text-primary" strokeWidth={1.5} />
                <h3 className="mb-2 font-heading text-lg font-semibold text-foreground">{f.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="border-t border-border">
        <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
          <h2 className="mb-12 font-heading text-2xl font-bold text-foreground md:text-3xl">
            How Aether works.
          </h2>
          <div className="grid gap-8 md:grid-cols-4">
            {steps.map((s, i) => (
              <motion.div
                key={s.num}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
              >
                <span className="font-mono text-xs text-muted-foreground">{s.num}</span>
                <h3 className="mt-2 mb-2 font-heading font-semibold text-foreground">{s.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-border bg-card">
        <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
          <div className="max-w-xl">
            <h2 className="mb-4 font-heading text-2xl font-bold text-foreground md:text-3xl">
              Built with clear boundaries.
            </h2>
            <div className="space-y-4 text-sm leading-relaxed text-muted-foreground">
              <p>
                Aether is <strong className="text-foreground">not</strong> a replacement
                for therapy, clinical diagnosis, or emergency services.
              </p>
              <p>
                It is a wellbeing companion designed for early support, self-reflection,
                habit building, and safe escalation when you need more.
              </p>
              <p>
                Your data is private. Your conversations are yours. Human oversight
                governs safety at every layer.
              </p>
            </div>
            <Link href="/auth?mode=signup" className="mt-8 inline-block">
              <Button variant="hero" size="lg">
                Begin with Aether
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 md:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-primary">
              <span className="font-heading text-[10px] font-bold text-primary-foreground">A</span>
            </div>
            <span className="text-sm text-muted-foreground">Aether · AI Mental Wellbeing Copilot</span>
          </div>
          <div className="flex items-center gap-6 text-xs text-muted-foreground">
            <span>Privacy</span>
            <span>Terms</span>
            <span>Safety</span>
            <Link href="/admin" className="transition-aether hover:text-foreground">
              Operations
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}