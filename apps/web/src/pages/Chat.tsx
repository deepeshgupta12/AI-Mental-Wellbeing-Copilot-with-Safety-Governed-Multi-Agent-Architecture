import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Send, Sparkles, Wind, Lightbulb, ListChecks } from "lucide-react";
import {
  createConversationMessage,
  createConversationSession,
  listConversationMessages,
} from "@/lib/conversations-api";
import { runAgentRuntimeSmoke } from "@/lib/agent-runtime-api";
import {
  getCurrentConversationSessionId,
  getCurrentUserId,
  setCurrentConversationSessionId,
} from "@/lib/demo-session";
import { getApiErrorMessage } from "@/lib/api-client";

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

export default function ChatPage() {
  const userId = getCurrentUserId();
  const [input, setInput] = useState("");
  const [currentMode, setCurrentMode] = useState<LocalMode>("reflective");
  const [sessionId, setSessionId] = useState<string | null>(getCurrentConversationSessionId());
  const bottomRef = useRef<HTMLDivElement>(null);

  const messagesQuery = useQuery({
    queryKey: ["conversation-messages", sessionId],
    queryFn: () => listConversationMessages(sessionId!),
    enabled: !!sessionId,
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
    if (userId && !sessionId && !createSessionMutation.isPending) {
      createSessionMutation.mutate();
    }
  }, [userId, sessionId, createSessionMutation]);

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
    <div className="flex flex-col h-[calc(100svh-3.5rem)] md:h-svh">
      <div className="border-b border-border px-4 md:px-6 py-3 flex items-center justify-between bg-background shrink-0">
        <div>
          <h1 className="font-heading font-semibold text-foreground text-base">Conversation</h1>
          <div className="flex items-center gap-1.5 mt-0.5">
            {activeMode && <activeMode.icon className="w-3 h-3 text-muted-foreground" />}
            <span className="text-[11px] text-muted-foreground">{activeMode?.label} Mode</span>
          </div>
        </div>
        <div className="flex gap-1">
          {modeLabels.map((mode) => (
            <button
              key={mode.id}
              onClick={() => setCurrentMode(mode.id)}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-aether ${
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

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto px-4 md:px-6 py-6 space-y-1">
          {!userId ? (
            <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
              No active user session found. Please complete onboarding first.
            </div>
          ) : messagesQuery.isLoading || createSessionMutation.isPending ? (
            <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
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
                  className={`py-4 px-4 rounded-lg ${msg.role === "assistant" ? "bg-muted/50" : ""}`}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold mt-0.5 ${
                        msg.role === "assistant"
                          ? "bg-primary text-primary-foreground"
                          : "bg-secondary text-secondary-foreground"
                      }`}
                    >
                      {msg.role === "assistant" ? "A" : "Y"}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-foreground leading-relaxed">{msg.content}</p>
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
        <div className="px-4 md:px-6 pb-2 flex gap-2 overflow-x-auto max-w-2xl mx-auto w-full">
          {suggestedPrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => setInput(prompt)}
              className="whitespace-nowrap px-3 py-1.5 rounded-full border border-border text-xs text-muted-foreground hover:bg-muted transition-aether shrink-0"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      <div className="border-t border-border px-4 md:px-6 py-3 bg-background shrink-0">
        <div className="max-w-2xl mx-auto flex items-end gap-2">
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
            className="flex-1 resize-none border border-input rounded-md px-3 py-2.5 text-sm bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring min-h-[42px] max-h-[160px]"
            style={{ fieldSizing: "content" } as React.CSSProperties}
          />
          <Button
            onClick={handleSend}
            variant="hero"
            size="icon"
            disabled={!input.trim() || !sessionId || !userId || sendFlowMutation.isPending}
            className="shrink-0 h-[42px] w-[42px]"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}