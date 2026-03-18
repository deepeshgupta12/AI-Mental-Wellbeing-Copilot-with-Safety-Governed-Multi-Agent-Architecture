"use client";

import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Calendar, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { getApiErrorMessage } from "@/lib/api-client";
import { getCurrentUserId } from "@/lib/demo-session";
import { createJournalEntry, listJournalEntries } from "@/lib/journal-api";

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
      <div className="mx-auto max-w-2xl px-4 py-8 md:px-8 md:py-12">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <button
            onClick={() => setView("list")}
            className="mb-6 text-sm text-muted-foreground transition-aether hover:text-foreground"
          >
            ← Back to journal
          </button>

          {selectedPrompt && (
            <div className="mb-6 rounded-lg border border-primary/10 bg-primary/5 p-4">
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Guided prompt
              </span>
              <p className="mt-1 text-sm font-medium text-foreground">{selectedPrompt}</p>
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
            className="min-h-[300px] resize-none border-none p-0 text-base leading-relaxed shadow-none placeholder:text-muted-foreground/50 focus-visible:ring-0"
            autoFocus
          />

          {journalText.length > 50 && detectedThemes.length > 0 && (
            <div className="mt-6 rounded-lg border border-border bg-card p-4 shadow-card">
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Detected themes
              </span>
              <div className="mt-2 flex gap-2">
                {detectedThemes.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground"
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

          <div className="mt-6 flex gap-3">
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
    <div className="mx-auto max-w-2xl px-4 py-8 md:px-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="font-heading text-2xl font-bold text-foreground md:text-3xl">
              Journal
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Your private reflective space.
            </p>
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
            <Plus className="mr-1 h-4 w-4" /> New entry
          </Button>
        </div>

        <div className="mb-8">
          <h2 className="mb-3 font-heading text-sm font-semibold text-foreground">
            Guided prompts
          </h2>
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
            {guidedPrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => {
                  setSelectedPrompt(prompt);
                  setJournalText("");
                  setView("write");
                }}
                className="rounded-lg border border-border bg-card p-3 text-left transition-aether hover:shadow-card"
              >
                <p className="text-sm leading-relaxed text-foreground">{prompt}</p>
              </button>
            ))}
          </div>
        </div>

        <div>
          <h2 className="mb-3 font-heading text-sm font-semibold text-foreground">
            Recent entries
          </h2>

          {!userId ? (
            <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
              No active user session found. Please complete onboarding first.
            </div>
          ) : journalQuery.isLoading ? (
            <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
              Loading journal entries...
            </div>
          ) : entries.length === 0 ? (
            <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
              No journal entries yet. Create your first one above.
            </div>
          ) : (
            <div className="space-y-3">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className="rounded-lg border border-border bg-card p-4 shadow-card transition-aether hover:shadow-aether-md"
                >
                  <div className="mb-2 flex items-center gap-3">
                    <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                      <Calendar className="h-3 w-3" />
                      {new Date(entry.created_at).toLocaleString()}
                    </div>
                    <span className="text-[11px] text-muted-foreground">·</span>
                    <span className="text-[11px] text-muted-foreground">
                      {entry.entry_type || "freeform"}
                    </span>
                  </div>
                  <p className="line-clamp-3 text-sm leading-relaxed text-foreground">
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