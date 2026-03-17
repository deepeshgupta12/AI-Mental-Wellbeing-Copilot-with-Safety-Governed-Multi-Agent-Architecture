import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ArrowRight, Flame, Brain, Moon, Heart, Cloud, Zap, ListChecks, Feather } from "lucide-react";
import { createUser } from "@/lib/users-api";
import { setCurrentUserSession } from "@/lib/demo-session";
import { getApiErrorMessage } from "@/lib/api-client";

const steps = [
  {
    id: "intent",
    title: "What brings you to Aether?",
    subtitle: "Choose what resonates most. You can change this anytime.",
    options: [
      { id: "burnout", label: "Burnout Recovery", icon: Flame, desc: "Rest, reset, and rebuild energy." },
      { id: "clarity", label: "Emotional Clarity", icon: Brain, desc: "Understand what you feel and why." },
      { id: "habits", label: "Habit Support", icon: ListChecks, desc: "Build sustainable wellbeing routines." },
      { id: "prevention", label: "Crisis Prevention", icon: Heart, desc: "Early awareness and safe support." },
    ],
  },
  {
    id: "style",
    title: "How should we communicate?",
    subtitle: "This shapes the tone of your conversations.",
    options: [
      { id: "direct", label: "Direct & Structured", icon: Zap, desc: "Clear, efficient, action-oriented." },
      { id: "reflective", label: "Soft & Reflective", icon: Cloud, desc: "Gentle, exploratory, open-ended." },
      { id: "minimal", label: "Minimalist", icon: Feather, desc: "Less is more. Brief and calm." },
    ],
  },
  {
    id: "focus",
    title: "What areas matter most?",
    subtitle: "Select all that apply.",
    multiSelect: true,
    options: [
      { id: "stress", label: "Stress", icon: Zap },
      { id: "anxiety", label: "Anxiety", icon: Cloud },
      { id: "sleep", label: "Sleep", icon: Moon },
      { id: "burnout", label: "Burnout", icon: Flame },
      { id: "loneliness", label: "Loneliness", icon: Heart },
      { id: "motivation", label: "Motivation", icon: Brain },
    ],
  },
  {
    id: "boundaries",
    title: "What Aether is — and isn't.",
    subtitle: "",
    isBoundary: true,
  },
] as const;

function buildEmailFromSelections(selections: Record<string, string | string[]>) {
  const style = typeof selections.style === "string" ? selections.style : "reflective";
  const intent = typeof selections.intent === "string" ? selections.intent : "wellbeing";
  const suffix = `${Date.now()}`;
  return `${intent}-${style}-${suffix}@aether.local`;
}

function buildDisplayName(selections: Record<string, string | string[]>) {
  const intent = typeof selections.intent === "string" ? selections.intent : "Aether";
  return `${intent.charAt(0).toUpperCase()}${intent.slice(1)} User`;
}

function buildGoals(selections: Record<string, string | string[]>) {
  const intent = typeof selections.intent === "string" ? selections.intent : "wellbeing";
  const goalsMap: Record<string, string> = {
    burnout: "Recover energy and reduce burnout.",
    clarity: "Gain emotional clarity and reflect better.",
    habits: "Build more stable wellbeing routines.",
    prevention: "Stay safer and respond earlier to distress signals.",
  };
  return goalsMap[intent] ?? "Improve overall wellbeing and self-awareness.";
}

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [selections, setSelections] = useState<Record<string, string | string[]>>({});
  const step = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  const createUserMutation = useMutation({
    mutationFn: createUser,
    onSuccess: (user) => {
      setCurrentUserSession({
        userId: user.id,
        email: user.email,
        displayName: user.profile?.display_name ?? "Aether User",
      });
      navigate("/app");
    },
  });

  const handleSelect = (optionId: string) => {
    if ("multiSelect" in step && step.multiSelect) {
      const current = (selections[step.id] as string[]) || [];
      const updated = current.includes(optionId)
        ? current.filter((id) => id !== optionId)
        : [...current, optionId];
      setSelections({ ...selections, [step.id]: updated });
    } else {
      setSelections({ ...selections, [step.id]: optionId });
    }
  };

  const canProceed =
    "isBoundary" in step && step.isBoundary
      ? true
      : !!(
          selections[step.id] &&
          (Array.isArray(selections[step.id])
            ? (selections[step.id] as string[]).length > 0
            : true)
        );

  const handleNext = async () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
      return;
    }

    const payload = {
      email: buildEmailFromSelections(selections),
      display_name: buildDisplayName(selections),
      timezone: "Asia/Kolkata",
      support_style:
        typeof selections.style === "string" ? selections.style : "reflective",
      wellbeing_goals: buildGoals(selections),
      focus_areas: Array.isArray(selections.focus)
        ? selections.focus.join(",")
        : "",
    };

    createUserMutation.mutate(payload);
  };

  return (
    <div className="min-h-svh bg-background flex flex-col">
      <div className="h-0.5 bg-border">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg">
          <AnimatePresence mode="wait">
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.35 }}
            >
              <h1
                className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2"
                style={{ textWrap: "balance" } as React.CSSProperties}
              >
                {step.title}
              </h1>

              {step.subtitle && (
                <p className="text-muted-foreground text-sm mb-8">{step.subtitle}</p>
              )}

              {"isBoundary" in step && step.isBoundary ? (
                <div className="space-y-5 mb-8">
                  <div className="p-5 rounded-lg border border-border bg-card shadow-card">
                    <p className="text-sm text-foreground leading-relaxed mb-3">
                      <strong>Aether is</strong> a wellbeing companion for self-reflection, coping guidance, habit support, and trend awareness.
                    </p>
                    <p className="text-sm text-foreground leading-relaxed mb-3">
                      <strong>Aether is not</strong> a therapist, a clinical diagnostic tool, or an emergency response system.
                    </p>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      If you are in crisis, Aether will guide you to appropriate resources. Human oversight governs safety at every layer of this system.
                    </p>
                  </div>
                </div>
              ) : (
                <div
                  className={`grid gap-3 mb-8 ${
                    step.options && step.options.length > 3 ? "grid-cols-2" : "grid-cols-1"
                  }`}
                >
                  {step.options?.map((opt) => {
                    const isSelected =
                      "multiSelect" in step && step.multiSelect
                        ? ((selections[step.id] as string[]) || []).includes(opt.id)
                        : selections[step.id] === opt.id;

                    return (
                      <button
                        key={opt.id}
                        onClick={() => handleSelect(opt.id)}
                        className={`text-left p-4 rounded-lg border transition-aether ${
                          isSelected
                            ? "border-primary bg-primary/5 shadow-card"
                            : "border-border bg-card hover:border-primary/30"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <opt.icon
                            className={`w-5 h-5 shrink-0 ${
                              isSelected ? "text-primary" : "text-muted-foreground"
                            }`}
                            strokeWidth={1.5}
                          />
                          <div>
                            <span className="text-sm font-medium text-foreground">
                              {opt.label}
                            </span>
                            {"desc" in opt && opt.desc && (
                              <p className="text-xs text-muted-foreground mt-0.5">
                                {opt.desc}
                              </p>
                            )}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}

              {createUserMutation.isError && (
                <div className="mb-4 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
                  {getApiErrorMessage(createUserMutation.error)}
                </div>
              )}

              <Button
                onClick={handleNext}
                variant="hero"
                size="lg"
                disabled={!canProceed || createUserMutation.isPending}
                className="w-full"
              >
                {createUserMutation.isPending
                  ? "Creating your space..."
                  : "isBoundary" in step && step.isBoundary
                    ? "I understand"
                    : currentStep === steps.length - 1
                      ? "Begin"
                      : "Continue"}
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}