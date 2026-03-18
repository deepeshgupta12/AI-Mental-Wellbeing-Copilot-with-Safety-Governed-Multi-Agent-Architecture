"use client";

import { motion } from "framer-motion";
import { Lock, MessageCircle, Shield, Trash2, User } from "lucide-react";

import { Button } from "@/components/ui/button";

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
    <div className="mx-auto max-w-2xl px-4 py-8 md:px-8 md:py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-2 font-heading text-2xl font-bold text-foreground md:text-3xl">
          Settings
        </h1>
        <p className="mb-8 text-sm text-muted-foreground">
          Preferences, privacy, and boundaries.
        </p>

        <div className="mb-6 rounded-lg border border-border bg-card p-5 shadow-card">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Alex</p>
              <p className="text-xs text-muted-foreground">alex@example.com</p>
            </div>
            <Button variant="outline" size="sm" className="ml-auto">
              Edit profile
            </Button>
          </div>
        </div>

        {sections.map((section) => (
          <div key={section.title} className="mb-6">
            <div className="mb-3 flex items-center gap-2">
              <section.icon className="h-4 w-4 text-muted-foreground" strokeWidth={1.5} />
              <h2 className="font-heading text-sm font-semibold text-foreground">
                {section.title}
              </h2>
            </div>
            <div className="divide-y divide-border rounded-lg border border-border bg-card shadow-card">
              {section.items.map((item) => (
                <div key={item.label} className="flex items-center justify-between p-4">
                  <div>
                    <p className="text-sm text-foreground">{item.label}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{item.value}</p>
                  </div>
                  {item.editable && (
                    <Button variant="ghost" size="sm" className="text-xs">
                      Change
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="border-t border-border pt-6">
          <div className="mb-3 flex items-center gap-2">
            <Trash2 className="h-4 w-4 text-destructive" strokeWidth={1.5} />
            <h2 className="font-heading text-sm font-semibold text-destructive">
              Danger Zone
            </h2>
          </div>
          <p className="mb-3 text-sm text-muted-foreground">
            Delete all your data, conversations, and account. This action cannot be undone.
          </p>
          <Button variant="destructive" size="sm">
            Delete my account
          </Button>
        </div>
      </motion.div>
    </div>
  );
}