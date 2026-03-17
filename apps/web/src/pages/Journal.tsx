import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Calendar } from "lucide-react";
import { createJournalEntry, listJournalEntries } from "@/lib/journal-api";
import { getCurrentUserId } from "@/lib/demo-session";
import { getApiErrorMessage } from "@/lib/api-client";

const guidedPrompts = [
  "What is one thing that felt heavy today?",
  "Describe a moment of calm from your week.",
  "What boundary do you wish you had set this week?",
  "What helped you cope today, even a little?",
];

export default function JournalPage() {
  const userId = getCurrentUserId();
  const queryClient = useQueryClient();

  const [view, setView] = useState<"list" | "write">("list");
  const [journalText, setJournalText] = useState("");
  const [selectedPrompt, setSelectedPrompt] = useState<string | null>(null);

  const journalQuery = useQuery({
    queryKey: ["journal-entries", userId],
    queryFn: () => listJournalEntries(userId!),
    enabled: !!userId,
  });

  const createJournalMutation = useMutation({
    mutationFn: createJournalEntry,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["journal-entries", userId] });
      setJournalText("");
      setSelectedPrompt(null);
      setView("list");
    },
  });

  const detectedThemes = useMemo(() => {
    const text = journalText.toLowerCase();
    const themes: string[] = [];
    if (text.includes("work")) themes.push("Work");
    if (text.includes("stress")) themes.push("Stress");
    if (text.includes("sleep")) themes.push("Sleep");
    if (text.includes("boundary")) themes.push("Boundaries");
    if (text.includes("calm")) themes.push("Calm");
    return themes.slice(0, 3);
  }, [journalText]);

  const handleSave = () => {
    if (!userId || !journalText.trim()) return;

    createJournalMutation.mutate({
      user_id: userId,
      title: selectedPrompt ? "Guided reflection" : "Journal entry",
      content: journalText.trim(),
      entry_type: selectedPrompt ? "guided" : "freeform",
    });
  };

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
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">
                Guided prompt
              </span>
              <p className="text-sm text-foreground mt-1 font-medium">{selectedPrompt}</p>
            </div>
          )}

          {!userId && (
            <div className="mb-6 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
              No active user session found. Please complete onboarding first.
            </div>
          )}

          <Textarea
            value={journalText}
            onChange={(e) => setJournalText(e.target.value)}
            placeholder="Write freely. This is your private space."
            className="min-h-[300px] resize-none text-base leading-relaxed border-none shadow-none focus-visible:ring-0 p-0 placeholder:text-muted-foreground/50"
            autoFocus
          />

          {journalText.length > 50 && detectedThemes.length > 0 && (
            <div className="mt-6 p-4 rounded-lg border border-border bg-card shadow-card">
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">
                Detected themes
              </span>
              <div className="flex gap-2 mt-2">
                {detectedThemes.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 rounded-full bg-muted text-[11px] text-muted-foreground font-medium"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {createJournalMutation.isError && (
            <div className="mt-4 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
              {getApiErrorMessage(createJournalMutation.error)}
            </div>
          )}

          <div className="flex gap-3 mt-6">
            <Button
              variant="hero"
              size="lg"
              onClick={handleSave}
              disabled={!userId || !journalText.trim() || createJournalMutation.isPending}
            >
              {createJournalMutation.isPending ? "Saving..." : "Save entry"}
            </Button>
            <Button variant="outline" size="lg" onClick={() => setView("list")}>
              Discard
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  const entries = journalQuery.data ?? [];

  return (
    <div className="max-w-2xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground">Journal</h1>
            <p className="text-muted-foreground text-sm mt-1">Your private reflective space.</p>
          </div>
          <Button
            variant="hero"
            size="sm"
            onClick={() => {
              setSelectedPrompt(null);
              setJournalText("");
              setView("write");
            }}
          >
            <Plus className="w-4 h-4 mr-1" /> New entry
          </Button>
        </div>

        <div className="mb-8">
          <h2 className="font-heading font-semibold text-foreground text-sm mb-3">Guided prompts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {guidedPrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => {
                  setSelectedPrompt(prompt);
                  setJournalText("");
                  setView("write");
                }}
                className="text-left p-3 rounded-lg border border-border bg-card hover:shadow-card transition-aether"
              >
                <p className="text-sm text-foreground leading-relaxed">{prompt}</p>
              </button>
            ))}
          </div>
        </div>

        <div>
          <h2 className="font-heading font-semibold text-foreground text-sm mb-3">Recent entries</h2>

          {!userId ? (
            <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
              No active user session found. Please complete onboarding first.
            </div>
          ) : journalQuery.isLoading ? (
            <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
              Loading journal entries...
            </div>
          ) : entries.length === 0 ? (
            <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
              No journal entries yet. Create your first one above.
            </div>
          ) : (
            <div className="space-y-3">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className="p-4 rounded-lg border border-border bg-card shadow-card hover:shadow-aether-md transition-aether"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                      <Calendar className="w-3 h-3" />
                      {new Date(entry.created_at).toLocaleString()}
                    </div>
                    <span className="text-[11px] text-muted-foreground">·</span>
                    <span className="text-[11px] text-muted-foreground">
                      {entry.entry_type || "freeform"}
                    </span>
                  </div>
                  <p className="text-sm text-foreground leading-relaxed line-clamp-3">
                    {entry.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}