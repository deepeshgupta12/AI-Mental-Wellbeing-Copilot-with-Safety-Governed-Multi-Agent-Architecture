import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ArrowLeft, AlertTriangle, Shield, CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";
import { getSafetyQueue, updateSafetyFlag } from "@/lib/safety-api";
import { getApiErrorMessage } from "@/lib/api-client";

export default function CaseReviewPage() {
  const queryClient = useQueryClient();

  const queueQuery = useQuery({
    queryKey: ["safety-queue"],
    queryFn: getSafetyQueue,
  });

  const targetFlag = queueQuery.data?.find((item) => !item.is_resolved) ?? queueQuery.data?.[0];

  const resolveMutation = useMutation({
    mutationFn: async () => {
      if (!targetFlag) throw new Error("No safety flag available to review.");
      return updateSafetyFlag(targetFlag.id, {
        needs_review: false,
        is_resolved: true,
        reviewer_note: "Reviewed from admin case review console.",
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["safety-queue"] });
      await queryClient.invalidateQueries({ queryKey: ["safety-dashboard-counts"] });
    },
  });

  return (
    <div className="p-6 md:p-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <Link
          to="/admin"
          className="text-sm text-muted-foreground hover:text-foreground transition-aether mb-4 inline-flex items-center gap-1"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to overview
        </Link>

        {queueQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            Loading case review data...
          </div>
        ) : !targetFlag ? (
          <div className="rounded-lg border border-border bg-card shadow-card p-4 text-sm text-muted-foreground">
            No safety flags available for review.
          </div>
        ) : (
          <>
            <div className="flex items-center gap-3 mb-6 mt-2">
              <h1 className="font-heading text-xl font-bold text-foreground">
                Case Review — {targetFlag.id.slice(0, 8)}
              </h1>
              <span className="px-2 py-0.5 rounded-full bg-urgent/10 text-urgent text-[10px] font-medium">
                {targetFlag.severity}
              </span>
              <span className="px-2 py-0.5 rounded-full bg-muted text-muted-foreground text-[10px] font-medium">
                {targetFlag.is_resolved
                  ? "Resolved"
                  : targetFlag.needs_review
                    ? "Pending Review"
                    : "Reviewed"}
              </span>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-2 rounded-lg border border-border bg-card shadow-card overflow-hidden">
                <div className="p-4 border-b border-border">
                  <h2 className="font-heading font-semibold text-foreground text-sm flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Safety Event Detail
                  </h2>
                </div>
                <div className="p-4 space-y-4">
                  <div className="p-3 rounded-lg border border-border bg-background">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase mb-1">User ID</p>
                    <p className="text-sm text-foreground font-mono">{targetFlag.user_id}</p>
                  </div>
                  <div className="p-3 rounded-lg border border-border bg-background">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase mb-1">Trigger</p>
                    <p className="text-sm text-foreground">{targetFlag.flag_type}</p>
                  </div>
                  <div className="p-3 rounded-lg border border-border bg-background">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase mb-1">Summary</p>
                    <p className="text-sm text-foreground">
                      {targetFlag.summary || "No summary provided."}
                    </p>
                  </div>
                  <div className="p-3 rounded-lg border border-border bg-background">
                    <p className="text-[10px] font-medium text-muted-foreground uppercase mb-1">Created At</p>
                    <p className="text-sm text-foreground">
                      {new Date(targetFlag.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-lg border border-border bg-card shadow-card p-4">
                  <h3 className="font-heading font-semibold text-foreground text-sm mb-3 flex items-center gap-2">
                    <Shield className="w-4 h-4" /> Actions
                  </h3>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => resolveMutation.mutate()}
                      disabled={resolveMutation.isPending || targetFlag.is_resolved}
                    >
                      <CheckCircle2 className="w-4 h-4 mr-2" />
                      {resolveMutation.isPending ? "Resolving..." : "Resolve flag"}
                    </Button>
                  </div>

                  {resolveMutation.isError && (
                    <div className="mt-3 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-xs text-destructive">
                      {getApiErrorMessage(resolveMutation.error)}
                    </div>
                  )}

                  {resolveMutation.isSuccess && (
                    <div className="mt-3 rounded-md border border-green-200 bg-green-50 p-3 text-xs text-green-700">
                      Safety flag resolved successfully.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
}