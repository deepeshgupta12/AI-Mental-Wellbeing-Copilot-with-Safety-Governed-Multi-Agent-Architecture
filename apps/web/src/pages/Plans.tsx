import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, Clock, RotateCcw } from "lucide-react";

const plans = {
  now: [
    { id: "1", text: "5-minute box breathing", done: true },
    { id: "2", text: "Step outside for fresh air", done: false },
  ],
  today: [
    { id: "3", text: "15-minute walk after lunch", done: false },
    { id: "4", text: "Write one journal sentence", done: false },
    { id: "5", text: "Evening wind-down at 9:30 PM", done: false },
  ],
  week: [
    { id: "6", text: "Try the sleep reset routine twice", done: false },
    { id: "7", text: "Reach out to one supportive person", done: false },
    { id: "8", text: "Complete weekly reflection on Sunday", done: false },
  ],
};

export default function PlansPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2">Action Plans</h1>
        <p className="text-muted-foreground text-sm mb-8">Practical, flexible steps. No pressure — just direction.</p>

        {[
          { label: "Right now", icon: Clock, items: plans.now },
          { label: "Today", icon: Circle, items: plans.today },
          { label: "This week", icon: RotateCcw, items: plans.week },
        ].map((section) => (
          <div key={section.label} className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <section.icon className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
              <h2 className="font-heading font-semibold text-foreground text-sm">{section.label}</h2>
            </div>
            <div className="space-y-2">
              {section.items.map((item) => (
                <div
                  key={item.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border transition-aether ${
                    item.done
                      ? "border-safe/20 bg-safe/5"
                      : "border-border bg-card shadow-card"
                  }`}
                >
                  <button className="shrink-0">
                    {item.done ? (
                      <CheckCircle2 className="w-5 h-5 text-safe" />
                    ) : (
                      <Circle className="w-5 h-5 text-border" />
                    )}
                  </button>
                  <span
                    className={`text-sm ${
                      item.done ? "text-muted-foreground line-through" : "text-foreground"
                    }`}
                  >
                    {item.text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground mb-3">
            Plans adapt based on your check-ins and conversations. Missed something? That's okay — re-entry is always gentle.
          </p>
          <Button variant="soft" size="sm">Adjust my plan</Button>
        </div>
      </motion.div>
    </div>
  );
}
