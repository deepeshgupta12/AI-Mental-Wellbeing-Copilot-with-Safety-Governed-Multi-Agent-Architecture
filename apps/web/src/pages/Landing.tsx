import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Shield, Brain, TrendingUp, Heart, ArrowRight, Lock, MessageCircle } from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: [0.4, 0, 0.2, 1] as [number, number, number, number] },
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
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-6xl mx-auto flex items-center justify-between h-16 px-6">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-heading font-bold text-sm">A</span>
            </div>
            <span className="font-heading font-semibold text-foreground text-lg">Aether</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link to="/auth">
              <Button variant="ghost" size="sm">Sign in</Button>
            </Link>
            <Link to="/auth?mode=signup">
              <Button variant="hero" size="sm">Get started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="max-w-6xl mx-auto px-6 pt-20 pb-24 md:pt-32 md:pb-36">
          <motion.div
            className="max-w-2xl"
            initial="hidden"
            animate="visible"
            variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
          >
            <motion.div variants={fadeUp} custom={0}>
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground bg-muted rounded-full px-3 py-1 mb-6">
                <Lock className="w-3 h-3" />
                Private · Safe · Not therapy
              </span>
            </motion.div>
            <motion.h1
              variants={fadeUp}
              custom={1}
              className="font-heading text-4xl md:text-6xl font-bold text-foreground leading-[1.1] tracking-tight"
              style={{ textWrap: "balance" } as React.CSSProperties}
            >
              Your wellbeing deserves
              <br />
              calm intelligence.
            </motion.h1>
            <motion.p
              variants={fadeUp}
              custom={2}
              className="mt-6 text-lg md:text-xl text-muted-foreground leading-relaxed max-w-lg"
              style={{ textWrap: "balance" } as React.CSSProperties}
            >
              Aether is an AI mental wellbeing copilot for stress, burnout, overwhelm, and self-reflection — with real support boundaries and safety at every step.
            </motion.p>
            <motion.div variants={fadeUp} custom={3} className="flex flex-wrap gap-3 mt-8">
              <Link to="/auth?mode=signup">
                <Button variant="hero" size="lg">
                  Start your journey
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
              <Link to="#how-it-works">
                <Button variant="outline" size="lg">How it works</Button>
              </Link>
            </motion.div>
          </motion.div>
        </div>
        {/* Ambient gradient */}
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/[0.03] to-transparent pointer-events-none" />
      </section>

      {/* Features */}
      <section className="border-t border-border bg-card">
        <div className="max-w-6xl mx-auto px-6 py-20 md:py-28">
          <h2 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-4">
            Support that understands you.
          </h2>
          <p className="text-muted-foreground text-base md:text-lg mb-12 max-w-lg">
            Not a chatbot. Not a meditation timer. A structured companion for your mental wellbeing.
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                className="p-6 rounded-lg border border-border bg-background shadow-card"
              >
                <f.icon className="w-6 h-6 text-primary mb-4" strokeWidth={1.5} />
                <h3 className="font-heading font-semibold text-foreground text-lg mb-2">{f.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-t border-border">
        <div className="max-w-6xl mx-auto px-6 py-20 md:py-28">
          <h2 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-12">
            How Aether works.
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            {steps.map((s, i) => (
              <motion.div
                key={s.num}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
              >
                <span className="text-xs font-mono text-muted-foreground">{s.num}</span>
                <h3 className="font-heading font-semibold text-foreground mt-2 mb-2">{s.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust & Boundaries */}
      <section className="border-t border-border bg-card">
        <div className="max-w-6xl mx-auto px-6 py-20 md:py-28">
          <div className="max-w-xl">
            <h2 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-4">
              Built with clear boundaries.
            </h2>
            <div className="space-y-4 text-muted-foreground text-sm leading-relaxed">
              <p>Aether is <strong className="text-foreground">not</strong> a replacement for therapy, clinical diagnosis, or emergency services.</p>
              <p>It is a wellbeing companion designed for early support, self-reflection, habit building, and safe escalation when you need more.</p>
              <p>Your data is private. Your conversations are yours. Human oversight governs safety at every layer.</p>
            </div>
            <Link to="/auth?mode=signup" className="inline-block mt-8">
              <Button variant="hero" size="lg">
                Begin with Aether
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="max-w-6xl mx-auto px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-heading font-bold text-[10px]">A</span>
            </div>
            <span className="text-sm text-muted-foreground">Aether · AI Mental Wellbeing Copilot</span>
          </div>
          <div className="flex items-center gap-6 text-xs text-muted-foreground">
            <span>Privacy</span>
            <span>Terms</span>
            <span>Safety</span>
            <Link to="/admin" className="hover:text-foreground transition-aether">Operations</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
