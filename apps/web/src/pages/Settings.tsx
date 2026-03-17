import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { User, Bell, Lock, MessageCircle, Brain, Eye, Shield, Trash2 } from "lucide-react";

const sections = [
  {
    title: "Communication",
    icon: MessageCircle,
    items: [
      { label: "Communication style", value: "Direct & Structured", editable: true },
      { label: "Check-in frequency", value: "Daily", editable: true },
      { label: "Notification preferences", value: "Gentle reminders only", editable: true },
    ],
  },
  {
    title: "Privacy & Data",
    icon: Lock,
    items: [
      { label: "Journal visibility", value: "Private — only you can see", editable: false },
      { label: "Data storage", value: "Encrypted, stored securely", editable: false },
      { label: "Conversation history", value: "Retained for continuity", editable: true },
    ],
  },
  {
    title: "Wellbeing Boundaries",
    icon: Shield,
    items: [
      { label: "AI capabilities", value: "Not therapy, not diagnosis", editable: false },
      { label: "Memory & context", value: "AI remembers across sessions", editable: true },
      { label: "Safety escalation", value: "Enabled — keyword detection active", editable: false },
    ],
  },
];

export default function SettingsPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 md:px-8 py-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground mb-2">Settings</h1>
        <p className="text-muted-foreground text-sm mb-8">Preferences, privacy, and boundaries.</p>

        {/* Profile */}
        <div className="p-5 rounded-lg border border-border bg-card shadow-card mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="font-medium text-foreground text-sm">Alex</p>
              <p className="text-xs text-muted-foreground">alex@example.com</p>
            </div>
            <Button variant="outline" size="sm" className="ml-auto">Edit profile</Button>
          </div>
        </div>

        {/* Sections */}
        {sections.map((section) => (
          <div key={section.title} className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <section.icon className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
              <h2 className="font-heading font-semibold text-foreground text-sm">{section.title}</h2>
            </div>
            <div className="rounded-lg border border-border bg-card shadow-card divide-y divide-border">
              {section.items.map((item) => (
                <div key={item.label} className="flex items-center justify-between p-4">
                  <div>
                    <p className="text-sm text-foreground">{item.label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{item.value}</p>
                  </div>
                  {item.editable && (
                    <Button variant="ghost" size="sm" className="text-xs">Change</Button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Danger zone */}
        <div className="pt-6 border-t border-border">
          <div className="flex items-center gap-2 mb-3">
            <Trash2 className="w-4 h-4 text-destructive" strokeWidth={1.5} />
            <h2 className="font-heading font-semibold text-destructive text-sm">Danger Zone</h2>
          </div>
          <p className="text-sm text-muted-foreground mb-3">
            Delete all your data, conversations, and account. This action cannot be undone.
          </p>
          <Button variant="destructive" size="sm">Delete my account</Button>
        </div>
      </motion.div>
    </div>
  );
}
