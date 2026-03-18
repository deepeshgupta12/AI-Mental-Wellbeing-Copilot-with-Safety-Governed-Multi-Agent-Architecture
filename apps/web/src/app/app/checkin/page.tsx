"use client";

import { motion } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowRight, Battery, Moon, Sun, Zap } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { getApiErrorMessage } from "@/lib/api-client";
import { createCheckIn } from "@/lib/check-ins-api";
import { getCurrentUserId } from "@/lib/demo-session";

const sliderLabels: Record<
  string,
  { icon: React.ElementType; low: string; high: string }
> = {
  mood: { icon: Sun, low: "Low", high: "High" },
  stress: { icon: Zap, low: "Calm", high: "Intense" },
  sleep: { icon: Moon, low: "Poor", high: "Great" },
  energy: { icon: Battery, low: "Depleted", high: "Charged" },
};

export default function CheckInPage() {
  const router = useRouter();
  const userId = getCurrentUserId();

  const [values, setValues] = useState<Record<string, number>>({
    mood: 5,
    stress: 3,
    sleep: 5,
    energy: 4,
  });
  const [context, setContext] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const createCheckInMutation = useMutation({
    mutationFn: createCheckIn,
    onSuccess: () => setSubmitted(true),
  });

  const handleChange = (key: string, val: number) => {
    setValues({ ...values, [key]: val });
  };

  const handleSubmit = () => {
    if (!userId) return;

    createCheckInMutation.mutate({
      user_id: userId,
      mood_score: values.mood,
      stress_score: values.stress,
      energy_score: values.energy,
      sleep_hours: values.sleep,
      notes: context || null,
    });
  };

  if (submitted) {
    return (
      <div className="mx-auto max-w-lg px-4 py-12 md:px-8 md:py-20">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="mb-2 font-heading text-2xl font-bold text-foreground">
            Check-in complete.
          </h1>
          <p className="mb-6 text-sm text-muted-foreground">
            Your latest pulse has been saved successfully.
          </p>

          <div className="mb-6 rounded-lg border border-border bg-card p-6 shadow-card">
            <h2 className="mb-2 font-heading text-sm font-semibold text-foreground">
              Saved Snapshot
            </h2>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Mood {values.mood}/10 · Stress {values.stress}/10 · Sleep {values.sleep}h · Energy {values.energy}/10
            </p>
          </div>

          <div className="flex gap-3">
            <Button variant="hero" onClick={() => router.push("/app/chat")}>
              Reflect with Aether <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
            <Button variant="outline" onClick={() => router.push("/app")}>
              Back to home
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-8 md:px-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-2 font-heading text-2xl font-bold text-foreground md:text-3xl">
          Daily Check-in
        </h1>
        <p className="mb-8 text-sm text-muted-foreground">
          A quick pulse. No pressure, just awareness.
        </p>

        {!userId && (
          <div className="mb-6 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
            No active user session found. Please complete onboarding first.
          </div>
        )}

        <div className="mb-8 space-y-6">
          {Object.entries(sliderLabels).map(([key, meta]) => (
            <div key={key}>
              <div className="mb-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <meta.icon className="h-4 w-4 text-muted-foreground" strokeWidth={1.5} />
                  <span className="text-sm font-medium capitalize text-foreground">{key}</span>
                </div>
                <span className="tabular-nums text-xs text-muted-foreground">
                  {values[key]}/10
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-12 text-[10px] text-muted-foreground">{meta.low}</span>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={values[key]}
                  onChange={(e) => handleChange(key, parseInt(e.target.value))}
                  className="h-1.5 flex-1 cursor-pointer appearance-none rounded-full bg-border accent-primary"
                />
                <span className="w-12 text-right text-[10px] text-muted-foreground">
                  {meta.high}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-8">
          <label className="mb-2 block text-sm font-medium text-foreground">
            Anything on your mind?{" "}
            <span className="font-normal text-muted-foreground">(optional)</span>
          </label>
          <Textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="A word, a sentence, or nothing at all."
            className="min-h-[80px] resize-none"
          />
        </div>

        {createCheckInMutation.isError && (
          <div className="mb-4 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
            {getApiErrorMessage(createCheckInMutation.error)}
          </div>
        )}

        <Button
          onClick={handleSubmit}
          variant="hero"
          size="lg"
          className="w-full"
          disabled={!userId || createCheckInMutation.isPending}
        >
          {createCheckInMutation.isPending ? "Saving check-in..." : "Complete check-in"}
          <ArrowRight className="ml-1 h-4 w-4" />
        </Button>
      </motion.div>
    </div>
  );
}