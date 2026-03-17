import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowRight, Sun, Moon, Zap, Battery } from "lucide-react";

const sliderLabels: Record<string, { icon: React.ElementType; low: string; high: string }> = {
  mood: { icon: Sun, low: "Low", high: "High" },
  stress: { icon: Zap, low: "Calm", high: "Intense" },
  sleep: { icon: Moon, low: "Poor", high: "Great" },
  energy: { icon: Battery, low: "Depleted", high: "Charged" },
};

export default function CheckInPage() {
  const navigate = useNavigate();
  const [values, setValues] = useState<Record<string, number>>({
    mood: 5,
    stress: 3,
    sleep: 5,
    energy: 4,
  });
  const [context, setContext] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (key: string, val: number) => {
    setValues({ ...values, [key]: val });
  };

  const handleSubmit = () => setSubmitted(true);

  if (submitted) {
    return (
      <div className="max-w-lg mx-auto px-4 md:px-8 py-12 md:py-20">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <h1 className="font-heading text-2xl font-bold text-foreground mb-2">Check-in complete.</h1>
          <p className="text-muted-foreground text-sm mb-6">Here's your daily focus based on today's pulse.</p>

          <div className="p-6 rounded-lg border border-border bg-card shadow-card mb-6">
            <h2 className="font-heading font-semibold text-foreground text-sm mb-2">Daily Focus: Micro-Rest</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Your stress is elevated and energy is lower than usual. Today, prioritize short recovery moments rather than pushing through.
            </p>
          </div>

          <div className="flex gap-3">
            <Button variant="hero" onClick={() => navigate("/app/chat")}>
              Reflect with Aether <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
            <Button variant="outline" onClick={() => navigate("/app")}>
              Back to home
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2">Daily Check-in</h1>
        <p className="text-muted-foreground text-sm mb-8">A quick pulse. No pressure, just awareness.</p>

        <div className="space-y-6 mb-8">
          {Object.entries(sliderLabels).map(([key, meta]) => (
            <div key={key}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <meta.icon className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
                  <span className="text-sm font-medium text-foreground capitalize">{key}</span>
                </div>
                <span className="text-xs text-muted-foreground tabular-nums">{values[key]}/10</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] text-muted-foreground w-12">{meta.low}</span>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={values[key]}
                  onChange={(e) => handleChange(key, parseInt(e.target.value))}
                  className="flex-1 h-1.5 bg-border rounded-full appearance-none cursor-pointer accent-primary"
                />
                <span className="text-[10px] text-muted-foreground w-12 text-right">{meta.high}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-8">
          <label className="text-sm font-medium text-foreground mb-2 block">
            Anything on your mind? <span className="text-muted-foreground font-normal">(optional)</span>
          </label>
          <Textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="A word, a sentence, or nothing at all."
            className="min-h-[80px] resize-none"
          />
        </div>

        <Button onClick={handleSubmit} variant="hero" size="lg" className="w-full">
          Complete check-in <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      </motion.div>
    </div>
  );
}
