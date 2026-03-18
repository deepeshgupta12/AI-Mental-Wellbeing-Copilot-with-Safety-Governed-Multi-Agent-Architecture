"use client";

import { motion } from "framer-motion";

export default function AnalyticsPage() {
  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="mb-6 font-heading text-2xl font-bold text-foreground">
          Analytics
        </h1>

        <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
          Admin analytics is not yet expanded beyond V1 operational views.
          Use Overview, Flagged Sessions, Session Logs, Audit Logs, and Policy & Prompts for current V1 operations.
        </div>
      </motion.div>
    </div>
  );
}