import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Send, Sparkles, Wind, Lightbulb, ListChecks } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  cards?: { type: string; title: string; content: string }[];
}

const initialMessages: Message[] = [
  {
    id: "1",
    role: "assistant",
    content:
      "Welcome back, Alex. Your recent check-ins suggest stress has been elevated, especially around work boundaries. Would you like to explore that, or is there something else on your mind today?",
  },
];

const modeLabels = [
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
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [currentMode, setCurrentMode] = useState("reflective");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    // Simulated assistant response
    setTimeout(() => {
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "That's a really important observation. Work boundaries often connect to deeper patterns around how we manage expectations — both from others and from ourselves. Let me offer you a structured way to think about this.",
        cards: [
          {
            type: "exercise",
            title: "Boundary Reflection",
            content:
              "Think of one moment this week where you said 'yes' when you wanted to say 'no.' What was the cost of that yes?",
          },
        ],
      };
      setMessages((prev) => [...prev, assistantMsg]);
    }, 1200);
  };

  const activeMode = modeLabels.find((m) => m.id === currentMode);

  return (
    <div className="flex flex-col h-[calc(100svh-3.5rem)] md:h-svh">
      {/* Header */}
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

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto px-4 md:px-6 py-6 space-y-1">
          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`py-4 px-4 rounded-lg ${
                  msg.role === "assistant" ? "bg-muted/50" : ""
                }`}
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
                    {msg.cards?.map((card, i) => (
                      <div
                        key={i}
                        className="mt-4 p-4 rounded-md border border-border bg-card shadow-card"
                      >
                        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                          {card.type}
                        </span>
                        <h3 className="font-heading font-semibold text-foreground text-sm mt-1 mb-2">
                          {card.title}
                        </h3>
                        <p className="text-sm text-muted-foreground leading-relaxed">{card.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Suggested prompts */}
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

      {/* Input */}
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
            disabled={!input.trim()}
            className="shrink-0 h-[42px] w-[42px]"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
