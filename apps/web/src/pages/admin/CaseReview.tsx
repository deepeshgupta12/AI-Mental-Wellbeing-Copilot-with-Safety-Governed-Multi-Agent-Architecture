import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowLeft, AlertTriangle, Clock, User, MessageCircle, Shield, CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";

const transcript = [
  { role: "user", text: "I don't know how much longer I can keep doing this.", flagged: false },
  { role: "assistant", text: "I hear you. That sounds like a heavy weight to carry. Can you tell me more about what 'this' feels like right now?", flagged: false },
  { role: "user", text: "Everything. Work, home, I just feel like I'm drowning. Sometimes I wonder what the point is.", flagged: true },
  { role: "assistant", text: "[Safety Protocol Activated] I want to make sure I understand what you're saying. When you say 'what the point is,' are you having thoughts of harming yourself?", flagged: false },
  { role: "user", text: "No, not like that. I just feel empty and exhausted.", flagged: false },
  { role: "assistant", text: "Thank you for being honest with me. Feeling empty and exhausted is really difficult. Let's talk about what might help you feel a little more grounded right now.", flagged: false },
];

const timeline = [
  { time: "14:23", event: "Session started", type: "info" },
  { time: "14:31", event: "Distress keyword detected", type: "flag" },
  { time: "14:31", event: "Safety protocol activated by AI", type: "action" },
  { time: "14:32", event: "User clarified — no self-harm intent", type: "info" },
  { time: "14:35", event: "Session flagged for review", type: "flag" },
  { time: "14:48", event: "Reviewer assigned: Dr. Chen", type: "action" },
];

export default function CaseReviewPage() {
  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <Link to="/admin" className="text-sm text-muted-foreground hover:text-foreground transition-aether mb-4 inline-flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to overview
        </Link>

        <div className="flex items-center gap-3 mb-6 mt-2">
          <h1 className="font-heading text-xl font-bold text-foreground">Case Review — USR-4821</h1>
          <span className="px-2 py-0.5 rounded-full bg-urgent/10 text-urgent text-[10px] font-medium">High Risk</span>
          <span className="px-2 py-0.5 rounded-full bg-muted text-muted-foreground text-[10px] font-medium">Pending Review</span>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Transcript */}
          <div className="md:col-span-2 rounded-lg border border-border bg-card shadow-card overflow-hidden">
            <div className="p-4 border-b border-border">
              <h2 className="font-heading font-semibold text-foreground text-sm flex items-center gap-2">
                <MessageCircle className="w-4 h-4" /> Conversation Transcript
              </h2>
            </div>
            <div className="p-4 space-y-3 max-h-[500px] overflow-y-auto">
              {transcript.map((msg, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg text-sm leading-relaxed ${
                    msg.flagged
                      ? "border-2 border-urgent/30 bg-urgent/5"
                      : msg.role === "assistant"
                      ? "bg-muted/50"
                      : "bg-background"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-medium text-muted-foreground uppercase">
                      {msg.role === "assistant" ? "AI Agent" : "User"}
                    </span>
                    {msg.flagged && (
                      <span className="flex items-center gap-1 text-[10px] text-urgent font-medium">
                        <AlertTriangle className="w-3 h-3" /> Risk Point
                      </span>
                    )}
                  </div>
                  <p className="text-foreground">{msg.text}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar: timeline + user info */}
          <div className="space-y-4">
            <div className="rounded-lg border border-border bg-card shadow-card p-4">
              <h3 className="font-heading font-semibold text-foreground text-sm flex items-center gap-2 mb-3">
                <User className="w-4 h-4" /> User Profile
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-muted-foreground">ID</span><span className="text-foreground font-mono text-xs">USR-4821</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Risk History</span><span className="text-foreground">2 prior flags</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Avg Mood (7d)</span><span className="text-foreground">3.2 / 10</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Sessions (30d)</span><span className="text-foreground">18</span></div>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card shadow-card p-4">
              <h3 className="font-heading font-semibold text-foreground text-sm flex items-center gap-2 mb-3">
                <Clock className="w-4 h-4" /> Audit Trail
              </h3>
              <div className="space-y-2">
                {timeline.map((t, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="text-[10px] text-muted-foreground font-mono w-10 shrink-0 mt-0.5">{t.time}</span>
                    <div className={`w-1.5 h-1.5 rounded-full shrink-0 mt-1.5 ${
                      t.type === "flag" ? "bg-urgent" : t.type === "action" ? "bg-primary" : "bg-border"
                    }`} />
                    <span className="text-xs text-foreground">{t.event}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="rounded-lg border border-border bg-card shadow-card p-4">
              <h3 className="font-heading font-semibold text-foreground text-sm mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4" /> Actions
              </h3>
              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <CheckCircle2 className="w-4 h-4 mr-2" /> Dismiss Flag
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <MessageCircle className="w-4 h-4 mr-2" /> Send System Message
                </Button>
                <Button variant="urgent" size="sm" className="w-full justify-start">
                  <AlertTriangle className="w-4 h-4 mr-2" /> Manual Escalation
                </Button>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
