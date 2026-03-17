import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Phone, Wind, FileText, ShieldAlert, Heart, ArrowRight } from "lucide-react";

export default function SafetyPage() {
  return (
    <div className="max-w-lg mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <ShieldAlert className="w-8 h-8 text-urgent mb-4" strokeWidth={1.5} />
          <h1
            className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-3"
            style={{ textWrap: "balance" } as React.CSSProperties}
          >
            You're not alone.
          </h1>
          <p className="text-muted-foreground text-base leading-relaxed">
            Let's take a moment to breathe. Choose the support you need right now.
          </p>
        </div>

        <div className="space-y-3">
          <a
            href="tel:988"
            className="flex items-center gap-4 p-5 rounded-lg border-2 border-urgent/20 bg-urgent/5 hover:bg-urgent/10 transition-aether"
          >
            <Phone className="w-6 h-6 text-urgent shrink-0" strokeWidth={1.5} />
            <div className="flex-1">
              <h2 className="font-heading font-semibold text-foreground text-base">Talk to a human</h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                988 Suicide & Crisis Lifeline — call or text 988
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-urgent shrink-0" />
          </a>

          <button className="w-full flex items-center gap-4 p-5 rounded-lg border border-border bg-card shadow-card hover:shadow-aether-md transition-aether text-left">
            <Wind className="w-6 h-6 text-safe shrink-0" strokeWidth={1.5} />
            <div className="flex-1">
              <h2 className="font-heading font-semibold text-foreground text-base">Grounding exercise</h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                A simple guided breathing and grounding technique.
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-muted-foreground shrink-0" />
          </button>

          <button className="w-full flex items-center gap-4 p-5 rounded-lg border border-border bg-card shadow-card hover:shadow-aether-md transition-aether text-left">
            <FileText className="w-6 h-6 text-primary shrink-0" strokeWidth={1.5} />
            <div className="flex-1">
              <h2 className="font-heading font-semibold text-foreground text-base">View my safety plan</h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Personal steps and contacts you've set up for moments like this.
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-muted-foreground shrink-0" />
          </button>
        </div>

        <div className="mt-10 pt-6 border-t border-border">
          <div className="flex items-start gap-3">
            <Heart className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" strokeWidth={1.5} />
            <div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Aether is not a crisis service or a replacement for professional help. If you are in immediate danger, please contact emergency services (911) or go to your nearest emergency room.
              </p>
              <p className="text-sm text-muted-foreground leading-relaxed mt-2">
                <strong className="text-foreground">Additional resources:</strong> Crisis Text Line — text HOME to 741741
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
