import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { BookOpen, Plus, Calendar, Tag, ArrowRight } from "lucide-react";

const pastEntries = [
  {
    id: "1",
    date: "Mar 15, 2026",
    preview: "I noticed I get tense every Sunday evening thinking about the week ahead...",
    tags: ["Work", "Anxiety"],
    mood: "Reflective",
  },
  {
    id: "2",
    date: "Mar 14, 2026",
    preview: "Good day today. Walked in the park and actually felt present for the first time in a while...",
    tags: ["Nature", "Presence"],
    mood: "Calm",
  },
  {
    id: "3",
    date: "Mar 12, 2026",
    preview: "Couldn't sleep again. Mind racing about the project deadline...",
    tags: ["Sleep", "Work"],
    mood: "Restless",
  },
];

const guidedPrompts = [
  "What is one thing that felt heavy today?",
  "Describe a moment of calm from your week.",
  "What boundary do you wish you had set this week?",
  "What helped you cope today, even a little?",
];

export default function JournalPage() {
  const [view, setView] = useState<"list" | "write">("list");
  const [journalText, setJournalText] = useState("");
  const [selectedPrompt, setSelectedPrompt] = useState<string | null>(null);

  if (view === "write") {
    return (
      <div className="max-w-2xl mx-auto px-4 md:px-8 py-8 md:py-12">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <button
            onClick={() => setView("list")}
            className="text-sm text-muted-foreground hover:text-foreground mb-6 transition-aether"
          >
            ← Back to journal
          </button>

          {selectedPrompt && (
            <div className="p-4 rounded-lg bg-primary/5 border border-primary/10 mb-6">
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Guided prompt</span>
              <p className="text-sm text-foreground mt-1 font-medium">{selectedPrompt}</p>
            </div>
          )}

          <Textarea
            value={journalText}
            onChange={(e) => setJournalText(e.target.value)}
            placeholder="Write freely. This is your private space."
            className="min-h-[300px] resize-none text-base leading-relaxed border-none shadow-none focus-visible:ring-0 p-0 placeholder:text-muted-foreground/50"
            autoFocus
          />

          {/* Insight sidebar preview */}
          {journalText.length > 50 && (
            <div className="mt-6 p-4 rounded-lg border border-border bg-card shadow-card">
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Detected themes</span>
              <div className="flex gap-2 mt-2">
                {["Work", "Stress", "Boundaries"].map((tag) => (
                  <span key={tag} className="px-2 py-0.5 rounded-full bg-muted text-[11px] text-muted-foreground font-medium">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3 mt-6">
            <Button variant="hero" size="lg" onClick={() => setView("list")}>
              Save entry
            </Button>
            <Button variant="outline" size="lg" onClick={() => setView("list")}>
              Discard
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground">Journal</h1>
            <p className="text-muted-foreground text-sm mt-1">Your private reflective space.</p>
          </div>
          <Button variant="hero" size="sm" onClick={() => { setSelectedPrompt(null); setJournalText(""); setView("write"); }}>
            <Plus className="w-4 h-4 mr-1" /> New entry
          </Button>
        </div>

        {/* Guided prompts */}
        <div className="mb-8">
          <h2 className="font-heading font-semibold text-foreground text-sm mb-3">Guided prompts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {guidedPrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => { setSelectedPrompt(prompt); setJournalText(""); setView("write"); }}
                className="text-left p-3 rounded-lg border border-border bg-card hover:shadow-card transition-aether"
              >
                <p className="text-sm text-foreground leading-relaxed">{prompt}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Past entries */}
        <div>
          <h2 className="font-heading font-semibold text-foreground text-sm mb-3">Recent entries</h2>
          <div className="space-y-3">
            {pastEntries.map((entry) => (
              <div
                key={entry.id}
                className="p-4 rounded-lg border border-border bg-card shadow-card hover:shadow-aether-md transition-aether cursor-pointer"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    {entry.date}
                  </div>
                  <span className="text-[11px] text-muted-foreground">·</span>
                  <span className="text-[11px] text-muted-foreground">{entry.mood}</span>
                </div>
                <p className="text-sm text-foreground leading-relaxed line-clamp-2">{entry.preview}</p>
                <div className="flex gap-1.5 mt-2">
                  {entry.tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 rounded-full bg-muted text-[10px] text-muted-foreground font-medium">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
