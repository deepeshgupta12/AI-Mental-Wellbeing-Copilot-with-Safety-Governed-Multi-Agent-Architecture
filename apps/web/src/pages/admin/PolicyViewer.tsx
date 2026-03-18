import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { getAdminPolicyConfig } from "@/lib/admin-api";

export default function PolicyViewerPage() {
  const policyQuery = useQuery({
    queryKey: ["admin-policy-config"],
    queryFn: getAdminPolicyConfig,
  });

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold text-foreground mb-6">
          Policy & Prompts
        </h1>

        {policyQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            Loading policy configuration...
          </div>
        ) : !policyQuery.data ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            Policy configuration is not available.
          </div>
        ) : (
          <div className="grid gap-6">
            <div className="rounded-lg border border-border bg-card shadow-card p-4">
              <h2 className="font-heading font-semibold text-foreground text-sm mb-3">
                Runtime Policy
              </h2>
              <pre className="text-xs text-muted-foreground overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(policyQuery.data.runtime_policy, null, 2)}
              </pre>
            </div>

            <div className="rounded-lg border border-border bg-card shadow-card p-4">
              <h2 className="font-heading font-semibold text-foreground text-sm mb-3">
                Prompt Registry
              </h2>
              <pre className="text-xs text-muted-foreground overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(policyQuery.data.prompt_registry, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}