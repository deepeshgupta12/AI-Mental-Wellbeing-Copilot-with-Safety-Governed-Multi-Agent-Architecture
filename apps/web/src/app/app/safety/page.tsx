"use client";

import { motion } from "framer-motion";
import { ArrowRight, FileText, Heart, Phone, ShieldAlert, Wind } from "lucide-react";

export default function SafetyPage() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-8 md:px-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <ShieldAlert className="mb-4 h-8 w-8 text-urgent" strokeWidth={1.5} />
          <h1 className="mb-3 font-heading text-2xl font-bold text-foreground md:text-3xl">
            Immediate support options
          </h1>
          <p className="text-base leading-relaxed text-muted-foreground">
            If this feels urgent, choose the fastest human support available. You can also use
            the grounding and distress-mode steps below while you reach out.
          </p>
        </div>

        <div className="mb-6 rounded-xl border-2 border-urgent/20 bg-urgent/5 p-5">
          <div className="flex items-start gap-4">
            <Phone className="mt-1 h-6 w-6 shrink-0 text-urgent" strokeWidth={1.5} />
            <div className="min-w-0 flex-1">
              <h2 className="font-heading text-base font-semibold text-foreground">
                Talk to a human now
              </h2>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                If you may be in immediate danger or might act on these thoughts, contact local
                emergency services now or go to the nearest emergency department.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <a href="tel:988">
                  <button className="rounded-md bg-urgent px-4 py-2 text-sm font-medium text-white transition-aether hover:opacity-90">
                    Call or text 988
                  </button>
                </a>
                <a href="tel:911">
                  <button className="rounded-md border border-border bg-background px-4 py-2 text-sm font-medium text-foreground transition-aether hover:bg-muted">
                    Call emergency services
                  </button>
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-border bg-card p-5 shadow-card">
            <div className="mb-3 flex items-center gap-3">
              <Wind className="h-5 w-5 text-safe" strokeWidth={1.5} />
              <h2 className="font-heading text-base font-semibold text-foreground">
                Distress mode
              </h2>
            </div>
            <ol className="space-y-2 text-sm leading-relaxed text-muted-foreground">
              <li>1. Put both feet on the ground.</li>
              <li>2. Exhale slightly longer than you inhale.</li>
              <li>3. Name 5 things you can see.</li>
              <li>4. Contact one trusted person now.</li>
            </ol>
          </div>

          <div className="rounded-lg border border-border bg-card p-5 shadow-card">
            <div className="mb-3 flex items-center gap-3">
              <FileText className="h-5 w-5 text-primary" strokeWidth={1.5} />
              <h2 className="font-heading text-base font-semibold text-foreground">
                Guided escalation
              </h2>
            </div>
            <ol className="space-y-2 text-sm leading-relaxed text-muted-foreground">
              <li>1. Say out loud: “I need support right now.”</li>
              <li>2. Call or text a crisis line, emergency number, or trusted contact.</li>
              <li>3. Avoid being alone if you can.</li>
              <li>4. Move toward a safer, more public, or supported place.</li>
            </ol>
          </div>
        </div>

        <div className="space-y-3">
          <button className="w-full rounded-lg border border-border bg-card p-5 text-left shadow-card transition-aether hover:shadow-aether-md">
            <div className="flex items-center gap-4">
              <Wind className="h-6 w-6 shrink-0 text-safe" strokeWidth={1.5} />
              <div className="flex-1">
                <h2 className="font-heading text-base font-semibold text-foreground">
                  Grounding exercise
                </h2>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  Use a simple breathing and grounding sequence to reduce intensity moment by
                  moment.
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
                  Review the contacts, steps, and reminders you want available in difficult
                  moments.
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
                Aether is not a crisis service and is not a replacement for professional or
                emergency support. If you are in immediate danger, contact emergency services or
                go to your nearest emergency room now.
              </p>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                <strong className="text-foreground">Additional resource:</strong> Crisis Text
                Line — text HOME to 741741.
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}