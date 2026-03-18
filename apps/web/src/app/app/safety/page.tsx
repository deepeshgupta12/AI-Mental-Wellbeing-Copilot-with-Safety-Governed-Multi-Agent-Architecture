"use client";

import { motion } from "framer-motion";
import { ArrowRight, FileText, Heart, Phone, ShieldAlert, Wind } from "lucide-react";

export default function SafetyPage() {
  return (
    <div className="mx-auto max-w-lg px-4 py-8 md:px-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <ShieldAlert className="mb-4 h-8 w-8 text-urgent" strokeWidth={1.5} />
          <h1 className="mb-3 font-heading text-2xl font-bold text-foreground md:text-3xl">
            You're not alone.
          </h1>
          <p className="text-base leading-relaxed text-muted-foreground">
            Let's take a moment to breathe. Choose the support you need right now.
          </p>
        </div>

        <div className="space-y-3">
          <a
            href="tel:988"
            className="flex items-center gap-4 rounded-lg border-2 border-urgent/20 bg-urgent/5 p-5 transition-aether hover:bg-urgent/10"
          >
            <Phone className="h-6 w-6 shrink-0 text-urgent" strokeWidth={1.5} />
            <div className="flex-1">
              <h2 className="font-heading text-base font-semibold text-foreground">
                Talk to a human
              </h2>
              <p className="mt-0.5 text-sm text-muted-foreground">
                988 Suicide & Crisis Lifeline — call or text 988
              </p>
            </div>
            <ArrowRight className="h-5 w-5 shrink-0 text-urgent" />
          </a>

          <button className="w-full rounded-lg border border-border bg-card p-5 text-left shadow-card transition-aether hover:shadow-aether-md">
            <div className="flex items-center gap-4">
              <Wind className="h-6 w-6 shrink-0 text-safe" strokeWidth={1.5} />
              <div className="flex-1">
                <h2 className="font-heading text-base font-semibold text-foreground">
                  Grounding exercise
                </h2>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  A simple guided breathing and grounding technique.
                </p>
              </div>
              <ArrowRight className="h-5 w-5 shrink-0 text-muted-foreground" />
            </div>
          </button>

          <button className="w-full rounded-lg border border-border bg-card p-5 text-left shadow-card transition-aether hover:shadow-aether-md">
            <div className="flex items-center gap-4">
              <FileText className="h-6 w-6 shrink-0 text-primary" strokeWidth={1.5} />
              <div className="flex-1">
                <h2 className="font-heading text-base font-semibold text-foreground">
                  View my safety plan
                </h2>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  Personal steps and contacts you've set up for moments like this.
                </p>
              </div>
              <ArrowRight className="h-5 w-5 shrink-0 text-muted-foreground" />
            </div>
          </button>
        </div>

        <div className="mt-10 border-t border-border pt-6">
          <div className="flex items-start gap-3">
            <Heart className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" strokeWidth={1.5} />
            <div>
              <p className="text-sm leading-relaxed text-muted-foreground">
                Aether is not a crisis service or a replacement for professional help. If you are in immediate danger, please contact emergency services (911) or go to your nearest emergency room.
              </p>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                <strong className="text-foreground">Additional resources:</strong> Crisis Text Line — text HOME to 741741
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}