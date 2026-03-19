"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Suspense, useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Lightbulb, ListChecks, Send, Sparkles, Wind } from "lucide-react";
import { useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { getApiErrorMessage } from "@/lib/api-client";
import { runAgentRuntimeSmoke } from "@/lib/agent-runtime-api";
import {
  createConversationMessage,
  createConversationSession,
  listConversationMessages,
} from "@/lib/conversations-api";
import {
  getCurrentConversationSessionId,
  getCurrentUserId,
  setCurrentConversationSessionId,
} from "@/lib/demo-session";
import { listSupportTracks } from "@/lib/support-tracks-api";

type LocalMode = "reflective" | "calming" | "problem-solving" | "planning";

const modeLabels: { id: LocalMode; label: string; icon: React.ElementType }[] = [
  { id: "reflective", label: "Reflective", icon: Sparkles },
  { id: "calming", label: "Calming", icon: Wind },
  { id: "problem-solving", label: "Problem-solving", icon: Lightbulb },
  { id: "planning", label: "Action Planning", icon: ListChecks },
];

const suggestedPrompts = [
  "I want to unpack why I feel overwhelmed at work.",
  "Help me think about my sleep routine.",
  "I'm feeling low today — what can I try?",
];

function ChatPageContent() {
  const searchParams = useSearchParams();

  const [isHydrated, setIsHydrated] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [currentMode, setCurrentMode] = useState<LocalMode>("reflective");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [supportTrack, setSupportTrack] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const supportTracksQuery = useQuery({
    queryKey: ["support-tracks"],
    queryFn: listSupportTracks,
    enabled: isHydrated,
  });

  const messagesQuery = useQuery({
    queryKey: ["conversation-messages", sessionId],
    queryFn: () => listConversationMessages(sessionId!),
    enabled: isHydrated && !!sessionId,
  });

  const createSessionMutation = useMutation({
    mutationFn: () =>
      createConversationSession({
        user_id: userId!,
        title: "Live support conversation",
        status: "active",
      }),
    onSuccess: (session) => {
      setSessionId(session.id);
      setCurrentConversationSessionId(session.id);
    },
  });

  useEffect(() => {
    setIsHydrated(true);
    setUserId(getCurrentUserId());
    setSessionId(getCurrentConversationSessionId());
    setSupportTrack(searchParams.get("track"));
  }, [searchParams]);

  useEffect(() => {
    if (!isHydrated) return;
    const nextTrack = searchParams.get("track");
    if (nextTrack) {
      setSupportTrack(nextTrack);
    }
  }, [isHydrated, searchParams]);

  useEffect(() => {
    if (!isHydrated) return;
    if (userId && !sessionId && !createSessionMutation.isPending) {
      createSessionMutation.mutate();
    }
  }, [isHydrated, userId, sessionId, createSessionMutation]);

  const sendFlowMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!sessionId || !userId) {
        throw new Error("Conversation session is not ready yet.");
      }

      await createConversationMessage({
        session_id: sessionId,
        role: "user",
        content,
        message_type: "text",
      });

      const runtimeResponse = await runAgentRuntimeSmoke({
        user_input: content,
        provider: "mock",
        user_id: userId,
        support_track: supportTrack,
      });

      await createConversationMessage({
        session_id: sessionId,
        role: "assistant",
        content: runtimeResponse.final_response,
        message_type: "text",
      });

      return runtimeResponse;
    },
    onSuccess: async () => {
      setInput("");
      await messagesQuery.refetch();
    },
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messagesQuery.data, sendFlowMutation.isPending]);

  const handleSend = () => {
    if (!input.trim() || !sessionId || !userId) return;
    sendFlowMutation.mutate(input.trim());
  };

  const activeMode = modeLabels.find((m) => m.id === currentMode);
  const messages = messagesQuery.data ?? [];

  return (
    <>
      <div className="shrink-0 border-b border-border bg-background px-4 py-2 md:px-6">
        <div className="mx-auto flex max-w-2xl gap-2 overflow-x-auto">
          {(supportTracksQuery.data ?? []).map((track) => (
            <button
              key={track.id}
              onClick={() => setSupportTrack(track.id)}
              className={`shrink-0 rounded-full border px-3 py-1.5 text-xs transition-aether ${
                supportTrack === track.id
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:bg-muted"
              }`}
            >
              {track.title}
            </button>
          ))}
        </div>
      </div>

      <div className="flex h-[calc(100svh-3.5rem)] flex-col md:h-svh">
        <div className="shrink-0 border-b border-border bg-background px-4 py-3 md:px-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-heading text-base font-semibold text-foreground">
                Conversation
              </h1>
              <div className="mt-0.5 flex items-center gap-1.5">
                {activeMode && <activeMode.icon className="h-3 w-3 text-muted-foreground" />}
                <span className="text-[11px] text-muted-foreground">
                  {activeMode?.label} Mode
                </span>
              </div>
            </div>

            <div className="flex gap-1">
              {modeLabels.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setCurrentMode(mode.id)}
                  className={`rounded px-2.5 py-1 text-[11px] font-medium transition-aether ${
                    currentMode === mode.id
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted"
                  }`}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-2xl space-y-1 px-4 py-6 md:px-6">
            {!isHydrated ? (
              <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
                Loading conversation...
              </div>
            ) : !userId ? (
              <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
                No active user session found. Please complete onboarding first.
              </div>
            ) : messagesQuery.isLoading || createSessionMutation.isPending ? (
              <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
                Starting your conversation...
              </div>
            ) : (
              <AnimatePresence>
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`rounded-lg px-4 py-4 ${msg.role === "assistant" ? "bg-muted/50" : ""}`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${
                          msg.role === "assistant"
                            ? "bg-primary text-primary-foreground"
                            : "bg-secondary text-secondary-foreground"
                        }`}
                      >
                        {msg.role === "assistant" ? "A" : "Y"}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm leading-relaxed text-foreground">{msg.content}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            )}

            {sendFlowMutation.isError && (
              <div className="rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
                {getApiErrorMessage(sendFlowMutation.error)}
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        {messages.length <= 2 && (
          <div className="mx-auto flex w-full max-w-2xl gap-2 overflow-x-auto px-4 pb-2 md:px-6">
            {suggestedPrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => setInput(prompt)}
                className="shrink-0 whitespace-nowrap rounded-full border border-border px-3 py-1.5 text-xs text-muted-foreground transition-aether hover:bg-muted"
              >
                {prompt}
              </button>
            ))}
          </div>
        )}

        <div className="shrink-0 border-t border-border bg-background px-4 py-3 md:px-6">
          <div className="mx-auto flex max-w-2xl items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="What's on your mind?"
              rows={1}
              className="min-h-[42px] max-h-[160px] flex-1 resize-none rounded-md border border-input bg-background px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              style={{ fieldSizing: "content" } as React.CSSProperties}
            />
            <Button
              onClick={handleSend}
              variant="hero"
              size="icon"
              disabled={!input.trim() || !sessionId || !userId || sendFlowMutation.isPending}
              className="h-[42px] w-[42px] shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-2xl px-4 py-8 md:px-6">
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading conversation...
          </div>
        </div>
      }
    >
      <ChatPageContent />
    </Suspense>
  );
}