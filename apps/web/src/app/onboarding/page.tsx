// apps/web/src/app/onboarding/page.tsx
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  ArrowRight,
  Brain,
  Cloud,
  Feather,
  Flame,
  Heart,
  ListChecks,
  Moon,
  Zap,
  type LucideIcon,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { getApiErrorMessage } from "@/lib/api-client";
import { setCurrentUserSession } from "@/lib/demo-session";
import { createUser } from "@/lib/users-api";

type SelectionValue = string | string[];

type StepOption = {
  id: string;
  label: string;
  icon: LucideIcon;
  desc?: string;
};

type ChoiceStep = {
  id: "intent" | "style" | "focus";
  title: string;
  subtitle: string;
  options: readonly StepOption[];
  multiSelect?: boolean;
  isBoundary?: false;
};

type BoundaryStep = {
  id: "boundaries";
  title: string;
  subtitle: string;
  isBoundary: true;
};

type OnboardingStep = ChoiceStep | BoundaryStep;

const steps: readonly OnboardingStep[] = [
  {
    id: "intent",
    title: "What brings you to Aether?",
    subtitle: "Choose what resonates most. You can change this anytime.",
    options: [
      {
        id: "burnout",
        label: "Burnout Recovery",
        icon: Flame,
        desc: "Rest, reset, and rebuild energy.",
      },
      {
        id: "clarity",
        label: "Emotional Clarity",
        icon: Brain,
        desc: "Understand what you feel and why.",
      },
      {
        id: "habits",
        label: "Habit Support",
        icon: ListChecks,
        desc: "Build sustainable wellbeing routines.",
      },
      {
        id: "prevention",
        label: "Crisis Prevention",
        icon: Heart,
        desc: "Early awareness and safe support.",
      },
    ],
  },
  {
    id: "style",
    title: "How should we communicate?",
    subtitle: "This shapes the tone of your conversations.",
    options: [
      {
        id: "direct",
        label: "Direct & Structured",
        icon: Zap,
        desc: "Clear, efficient, action-oriented.",
      },
      {
        id: "reflective",
        label: "Soft & Reflective",
        icon: Cloud,
        desc: "Gentle, exploratory, open-ended.",
      },
      {
        id: "minimal",
        label: "Minimalist",
        icon: Feather,
        desc: "Less is more. Brief and calm.",
      },
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

function isBoundaryStep(step: OnboardingStep): step is BoundaryStep {
  return step.id === "boundaries";
}

function buildEmailFromSelections(selections: Record<string, SelectionValue>) {
  const style = typeof selections.style === "string" ? selections.style : "reflective";
  const intent = typeof selections.intent === "string" ? selections.intent : "wellbeing";
  return `${intent}-${style}-${Date.now()}@example.com`;
}

function buildDisplayName(selections: Record<string, SelectionValue>) {
  const intent = typeof selections.intent === "string" ? selections.intent : "Aether";
  return `${intent.charAt(0).toUpperCase()}${intent.slice(1)} User`;
}

function buildGoals(selections: Record<string, SelectionValue>) {
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
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [selections, setSelections] = useState<Record<string, SelectionValue>>({});

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
      router.push("/app");
    },
  });

  const handleSelect = (optionId: string) => {
    if (!isBoundaryStep(step) && step.multiSelect) {
      const current = Array.isArray(selections[step.id]) ? (selections[step.id] as string[]) : [];
      const updated = current.includes(optionId)
        ? current.filter((id) => id !== optionId)
        : [...current, optionId];
      setSelections({ ...selections, [step.id]: updated });
      return;
    }

    setSelections({ ...selections, [step.id]: optionId });
  };

  const canProceed = isBoundaryStep(step)
    ? true
    : !!(
        selections[step.id] &&
        (Array.isArray(selections[step.id]) ? (selections[step.id] as string[]).length > 0 : true)
      );

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
      return;
    }

    createUserMutation.mutate({
      email: buildEmailFromSelections(selections),
      display_name: buildDisplayName(selections),
      timezone: "Asia/Kolkata",
      support_style: typeof selections.style === "string" ? selections.style : "reflective",
      wellbeing_goals: buildGoals(selections),
      focus_areas: Array.isArray(selections.focus) ? selections.focus.join(",") : "",
    });
  };

  return (
    <div className="flex min-h-svh flex-col bg-background">
      <div className="h-0.5 bg-border">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4 }}
        />
      </div>

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-lg">
          <AnimatePresence mode="wait">
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.35 }}
            >
              <h1 className="mb-2 font-heading text-2xl font-bold text-foreground md:text-3xl">
                {step.title}
              </h1>

              {step.subtitle && <p className="mb-8 text-sm text-muted-foreground">{step.subtitle}</p>}

              {isBoundaryStep(step) ? (
                <div className="mb-8 space-y-5">
                  <div className="rounded-lg border border-border bg-card p-5 shadow-card">
                    <p className="mb-3 text-sm leading-relaxed text-foreground">
                      <strong>Aether is</strong> a wellbeing companion for self-reflection, coping
                      guidance, habit support, and trend awareness.
                    </p>
                    <p className="mb-3 text-sm leading-relaxed text-foreground">
                      <strong>Aether is not</strong> a therapist, a clinical diagnostic tool, or an
                      emergency response system.
                    </p>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      If you are in crisis, Aether will guide you to appropriate resources. Human
                      oversight governs safety at every layer of this system.
                    </p>
                  </div>
                </div>
              ) : (
                <div
                  className={`mb-8 grid gap-3 ${
                    step.options.length > 3 ? "grid-cols-2" : "grid-cols-1"
                  }`}
                >
                  {step.options.map((opt) => {
                    const isSelected = step.multiSelect
                      ? ((selections[step.id] as string[]) || []).includes(opt.id)
                      : selections[step.id] === opt.id;

                    return (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => handleSelect(opt.id)}
                        className={`rounded-lg border p-4 text-left transition-aether ${
                          isSelected
                            ? "border-primary bg-primary/5 shadow-card"
                            : "border-border bg-card hover:border-primary/30"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <opt.icon
                            className={`h-5 w-5 shrink-0 ${
                              isSelected ? "text-primary" : "text-muted-foreground"
                            }`}
                            strokeWidth={1.5}
                          />
                          <div>
                            <span className="text-sm font-medium text-foreground">{opt.label}</span>
                            {opt.desc && (
                              <p className="mt-0.5 text-xs text-muted-foreground">{opt.desc}</p>
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
                  : isBoundaryStep(step)
                    ? "I understand"
                    : currentStep === steps.length - 1
                      ? "Begin"
                      : "Continue"}
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}