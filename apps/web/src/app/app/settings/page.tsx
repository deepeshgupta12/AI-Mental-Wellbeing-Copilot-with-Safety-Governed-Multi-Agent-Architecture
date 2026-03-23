"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  Globe2,
  Languages,
  ListChecks,
  MessageCircle,
  Settings2,
  Sparkles,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { getApiErrorMessage } from "@/lib/api-client";
import {
  getLocalizationCatalog,
  getLocalizationRuntimeCopy,
  getUserLanguagePreference,
  updateUserLanguagePreference,
} from "@/lib/localization-api";
import { getCurrentUserId } from "@/lib/demo-session";
import { getUser } from "@/lib/users-api";

const toneGuides = [
  {
    id: "direct",
    title: "Direct and structured",
    description: "Clear next steps, less fluff, more movement.",
    chatHref: "/app/chat",
  },
  {
    id: "reflective",
    title: "Soft and reflective",
    description: "Gentle prompts, more room to think and feel.",
    chatHref: "/app/chat",
  },
  {
    id: "minimal",
    title: "Minimal and calm",
    description: "Short, steady guidance with less cognitive load.",
    chatHref: "/app/chat",
  },
];

export default function SettingsPage() {
  const userId = getCurrentUserId();
  const queryClient = useQueryClient();

  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [contentLanguage, setContentLanguage] = useState("en");
  const [fallbackLanguage, setFallbackLanguage] = useState("en");
  const [previewLanguage, setPreviewLanguage] = useState("en");

  const userQuery = useQuery({
    queryKey: ["user", userId],
    queryFn: () => getUser(userId!),
    enabled: !!userId,
  });

  const catalogQuery = useQuery({
    queryKey: ["localization-catalog"],
    queryFn: getLocalizationCatalog,
    enabled: !!userId,
  });

  const languageQuery = useQuery({
    queryKey: ["user-language-preference", userId],
    queryFn: () => getUserLanguagePreference(userId!),
    enabled: !!userId,
  });

  const previewQuery = useQuery({
    queryKey: ["localization-runtime-copy", previewLanguage],
    queryFn: () => getLocalizationRuntimeCopy(previewLanguage),
    enabled: !!userId,
  });

  const saveLanguageMutation = useMutation({
    mutationFn: async () =>
      updateUserLanguagePreference(userId!, {
        preferred_language: preferredLanguage,
        content_language: contentLanguage,
        fallback_language: fallbackLanguage,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["user-language-preference", userId] });
    },
  });

  useEffect(() => {
    const current = languageQuery.data;
    if (!current) return;
    setPreferredLanguage(current.preferred_language);
    setContentLanguage(current.content_language);
    setFallbackLanguage(current.fallback_language);
    setPreviewLanguage(current.content_language || current.preferred_language || "en");
  }, [languageQuery.data]);

  const currentSupportStyle = useMemo(() => {
    return userQuery.data?.profile?.support_style ?? "reflective";
  }, [userQuery.data]);

  const currentToneGuide =
    toneGuides.find((item) => item.id === currentSupportStyle) ?? toneGuides[1];

  const supportedLanguages = catalogQuery.data?.supported_languages ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 md:px-8 md:py-10">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
            <Settings2 className="h-3.5 w-3.5" />
            Personal preferences
          </div>
          <h1 className="font-heading text-3xl font-bold text-foreground">Settings</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            Choose how support should feel, what language you prefer, and how the experience
            should read when you come back.
          </p>
        </div>

        {!userId ? (
          <div className="rounded-2xl border border-border bg-card p-5 text-sm text-muted-foreground shadow-card">
            No active user session found. Please complete onboarding first.
          </div>
        ) : (
          <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <section className="space-y-6">
              <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
                <div className="mb-4">
                  <h2 className="font-heading text-xl font-semibold text-foreground">
                    Language and reading comfort
                  </h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Choose the language you want to see most often, the language for content,
                    and the backup language if something is unavailable.
                  </p>
                </div>

                {languageQuery.isLoading || catalogQuery.isLoading ? (
                  <div className="rounded-xl border border-border bg-background p-4 text-sm text-muted-foreground">
                    Loading language settings...
                  </div>
                ) : (
                  <>
                    <div className="mb-4 grid gap-3 sm:grid-cols-3">
                      <div className="rounded-xl border border-border bg-background p-4">
                        <p className="text-xs text-muted-foreground">Preferred language</p>
                        <p className="mt-1 text-sm font-medium text-foreground">
                          {languageQuery.data?.preferred_language ?? preferredLanguage}
                        </p>
                      </div>
                      <div className="rounded-xl border border-border bg-background p-4">
                        <p className="text-xs text-muted-foreground">Content language</p>
                        <p className="mt-1 text-sm font-medium text-foreground">
                          {languageQuery.data?.content_language ?? contentLanguage}
                        </p>
                      </div>
                      <div className="rounded-xl border border-border bg-background p-4">
                        <p className="text-xs text-muted-foreground">Fallback language</p>
                        <p className="mt-1 text-sm font-medium text-foreground">
                          {languageQuery.data?.fallback_language ?? fallbackLanguage}
                        </p>
                      </div>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-3">
                      <label className="space-y-2">
                        <span className="text-sm font-medium text-foreground">Preferred language</span>
                        <select
                          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                          value={preferredLanguage}
                          onChange={(e) => {
                            setPreferredLanguage(e.target.value);
                            setPreviewLanguage(e.target.value);
                          }}
                        >
                          {supportedLanguages.map((item) => (
                            <option key={item.language_code} value={item.language_code}>
                              {item.display_name}
                            </option>
                          ))}
                        </select>
                      </label>

                      <label className="space-y-2">
                        <span className="text-sm font-medium text-foreground">Content language</span>
                        <select
                          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                          value={contentLanguage}
                          onChange={(e) => {
                            setContentLanguage(e.target.value);
                            setPreviewLanguage(e.target.value);
                          }}
                        >
                          {supportedLanguages.map((item) => (
                            <option key={item.language_code} value={item.language_code}>
                              {item.display_name}
                            </option>
                          ))}
                        </select>
                      </label>

                      <label className="space-y-2">
                        <span className="text-sm font-medium text-foreground">Fallback language</span>
                        <select
                          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                          value={fallbackLanguage}
                          onChange={(e) => setFallbackLanguage(e.target.value)}
                        >
                          {supportedLanguages.map((item) => (
                            <option key={item.language_code} value={item.language_code}>
                              {item.display_name}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-3">
                      <Button
                        variant="hero"
                        onClick={() => saveLanguageMutation.mutate()}
                        disabled={saveLanguageMutation.isPending}
                      >
                        Save language preferences
                      </Button>
                      <Button
                        variant="soft"
                        onClick={() => {
                          const current = languageQuery.data;
                          setPreferredLanguage(current?.preferred_language ?? "en");
                          setContentLanguage(current?.content_language ?? "en");
                          setFallbackLanguage(current?.fallback_language ?? "en");
                          setPreviewLanguage(current?.content_language ?? "en");
                        }}
                      >
                        Reset to current
                      </Button>
                    </div>
                  </>
                )}
              </div>

              <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
                <div className="mb-4 flex items-center gap-2">
                  <Languages className="h-5 w-5 text-primary" />
                  <h2 className="font-heading text-xl font-semibold text-foreground">
                    Preview how support sounds
                  </h2>
                </div>

                <label className="mb-4 block space-y-2">
                  <span className="text-sm font-medium text-foreground">Preview language</span>
                  <select
                    value={previewLanguage}
                    onChange={(e) => setPreviewLanguage(e.target.value)}
                    className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
                  >
                    {supportedLanguages.map((item) => (
                      <option key={item.language_code} value={item.language_code}>
                        {item.display_name}
                      </option>
                    ))}
                  </select>
                </label>

                <div className="grid gap-3 md:grid-cols-2">
                  {Object.entries(previewQuery.data?.copy ?? {}).slice(0, 6).map(([key, value]) => (
                    <div key={key} className="rounded-xl border border-border bg-background p-4">
                      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        {key}
                      </p>
                      <p className="mt-2 text-sm text-foreground">{String(value)}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-4 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-muted-foreground">
                  This preview helps you check whether the language feels clear, supportive,
                  and natural before you keep using it.
                </div>
              </div>
            </section>

            <section className="space-y-6">
              <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
                <div className="mb-4 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  <h2 className="font-heading text-xl font-semibold text-foreground">
                    How support currently feels
                  </h2>
                </div>

                <div className="rounded-2xl border border-primary/20 bg-primary/5 p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-primary">
                    Current tone
                  </p>
                  <p className="mt-1 text-lg font-semibold text-foreground">
                    {currentToneGuide.title}
                  </p>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {currentToneGuide.description}
                  </p>
                </div>

                <div className="mt-4 space-y-3">
                  {toneGuides.map((item) => {
                    const isCurrent = item.id === currentSupportStyle;

                    return (
                      <div
                        key={item.id}
                        className={`rounded-xl border p-4 ${
                          isCurrent
                            ? "border-primary/30 bg-primary/5"
                            : "border-border bg-background"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-foreground">{item.title}</p>
                            <p className="mt-1 text-sm text-muted-foreground">
                              {item.description}
                            </p>
                          </div>
                          {isCurrent ? (
                            <span className="rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-medium text-primary">
                              Current
                            </span>
                          ) : null}
                        </div>

                        <div className="mt-3">
                          <Button asChild variant="soft" size="sm">
                            <Link href={item.chatHref}>
                              Use in chat
                              <ArrowRight className="h-4 w-4" />
                            </Link>
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-3xl border border-border bg-card p-5 shadow-card">
                <div className="mb-4 flex items-center gap-2">
                  <Globe2 className="h-5 w-5 text-primary" />
                  <h2 className="font-heading text-xl font-semibold text-foreground">
                    Helpful shortcuts
                  </h2>
                </div>

                <div className="space-y-3">
                  <Link
                    href="/app/plans"
                    className="flex items-center justify-between rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground transition-aether hover:bg-muted"
                  >
                    <span className="flex items-center gap-2">
                      <ListChecks className="h-4 w-4 text-muted-foreground" />
                      Open Plans
                    </span>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </Link>

                  <Link
                    href="/app/programs"
                    className="flex items-center justify-between rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground transition-aether hover:bg-muted"
                  >
                    <span className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-muted-foreground" />
                      Open Support Programs
                    </span>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </Link>

                  <Link
                    href="/app/chat"
                    className="flex items-center justify-between rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground transition-aether hover:bg-muted"
                  >
                    <span className="flex items-center gap-2">
                      <MessageCircle className="h-4 w-4 text-muted-foreground" />
                      Continue a conversation
                    </span>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </Link>
                </div>
              </div>
            </section>
          </div>
        )}

        {(saveLanguageMutation.isError ||
          languageQuery.isError ||
          catalogQuery.isError ||
          previewQuery.isError) && (
          <div className="mt-6 rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
            {getApiErrorMessage(
              saveLanguageMutation.error ||
                languageQuery.error ||
                catalogQuery.error ||
                previewQuery.error,
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}