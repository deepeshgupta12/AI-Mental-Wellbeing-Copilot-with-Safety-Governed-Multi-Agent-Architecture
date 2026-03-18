"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, CheckCircle2, Shield } from "lucide-react";

import { Button } from "@/components/ui/button";
import { getApiErrorMessage } from "@/lib/api-client";
import { getSafetyQueue, updateSafetyFlag } from "@/lib/safety-api";

export default function CaseReviewPage() {
  const queryClient = useQueryClient();

  const queueQuery = useQuery({
    queryKey: ["safety-queue"],
    queryFn: getSafetyQueue,
  });

  const targetFlag =
    queueQuery.data?.find((item) => !item.is_resolved) ?? queueQuery.data?.[0];

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
          href="/admin"
          className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground transition-aether hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to overview
        </Link>

        {queueQuery.isLoading ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            Loading case review data...
          </div>
        ) : !targetFlag ? (
          <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground shadow-card">
            No safety flags available for review.
          </div>
        ) : (
          <>
            <div className="mt-2 mb-6 flex items-center gap-3">
              <h1 className="font-heading text-xl font-bold text-foreground">
                Case Review — {targetFlag.id.slice(0, 8)}
              </h1>
              <span className="rounded-full bg-urgent/10 px-2 py-0.5 text-[10px] font-medium text-urgent">
                {targetFlag.severity}
              </span>
              <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                {targetFlag.is_resolved
                  ? "Resolved"
                  : targetFlag.needs_review
                    ? "Pending Review"
                    : "Reviewed"}
              </span>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              <div className="overflow-hidden rounded-lg border border-border bg-card shadow-card md:col-span-2">
                <div className="border-b border-border p-4">
                  <h2 className="flex items-center gap-2 font-heading text-sm font-semibold text-foreground">
                    <AlertTriangle className="h-4 w-4" /> Safety Event Detail
                  </h2>
                </div>
                <div className="space-y-4 p-4">
                  <div className="rounded-lg border border-border bg-background p-3">
                    <p className="mb-1 text-[10px] font-medium uppercase text-muted-foreground">
                      User ID
                    </p>
                    <p className="font-mono text-sm text-foreground">{targetFlag.user_id}</p>
                  </div>
                  <div className="rounded-lg border border-border bg-background p-3">
                    <p className="mb-1 text-[10px] font-medium uppercase text-muted-foreground">
                      Trigger
                    </p>
                    <p className="text-sm text-foreground">{targetFlag.flag_type}</p>
                  </div>
                  <div className="rounded-lg border border-border bg-background p-3">
                    <p className="mb-1 text-[10px] font-medium uppercase text-muted-foreground">
                      Summary
                    </p>
                    <p className="text-sm text-foreground">
                      {targetFlag.summary || "No summary provided."}
                    </p>
                  </div>
                  <div className="rounded-lg border border-border bg-background p-3">
                    <p className="mb-1 text-[10px] font-medium uppercase text-muted-foreground">
                      Created At
                    </p>
                    <p className="text-sm text-foreground">
                      {new Date(targetFlag.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-lg border border-border bg-card p-4 shadow-card">
                  <h3 className="mb-3 flex items-center gap-2 font-heading text-sm font-semibold text-foreground">
                    <Shield className="h-4 w-4" /> Actions
                  </h3>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => resolveMutation.mutate()}
                      disabled={resolveMutation.isPending || targetFlag.is_resolved}
                    >
                      <CheckCircle2 className="mr-2 h-4 w-4" />
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