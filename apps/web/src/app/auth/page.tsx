// apps/web/src/app/auth/page.tsx
"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

function AuthPageInner() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [mode, setMode] = useState<"signin" | "signup">(
    searchParams.get("mode") === "signup" ? "signup" : "signin",
  );
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push(mode === "signup" ? "/onboarding" : "/app");
  };

  return (
    <div className="flex min-h-svh bg-background">
      <div className="hidden w-[45%] flex-col justify-between border-r border-border bg-primary/[0.03] p-10 lg:flex">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
            <span className="font-heading text-sm font-bold text-primary-foreground">A</span>
          </div>
          <span className="font-heading text-lg font-semibold text-foreground">Aether</span>
        </Link>

        <div className="max-w-sm">
          <h2 className="mb-4 font-heading text-3xl font-bold leading-tight text-foreground">
            Your wellbeing, supported with calm intelligence.
          </h2>
          <p className="text-sm leading-relaxed text-muted-foreground">
            Aether helps you reflect, cope, and build better habits — with safety and privacy at
            its core.
          </p>
        </div>

        <p className="text-xs text-muted-foreground">
          Not a replacement for therapy or emergency services.
        </p>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <Link
            href="/"
            className="mb-8 flex items-center gap-2 text-sm text-muted-foreground transition-aether hover:text-foreground lg:hidden"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Link>

          <AnimatePresence mode="wait">
            <motion.div
              key={mode}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              <h1 className="mb-2 font-heading text-2xl font-bold text-foreground">
                {mode === "signin" ? "Welcome back" : "Begin your journey"}
              </h1>

              <p className="mb-8 text-sm text-muted-foreground">
                {mode === "signin"
                  ? "Sign in to continue with Aether."
                  : "Create your account to get started."}
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium">
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-medium">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11"
                  />
                </div>

                <Button type="submit" variant="hero" className="w-full" size="lg">
                  {mode === "signin" ? "Sign in" : "Create account"}
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-muted-foreground">
                {mode === "signin" ? (
                  <>
                    New to Aether?{" "}
                    <button
                      type="button"
                      onClick={() => setMode("signup")}
                      className="font-medium text-primary hover:underline"
                    >
                      Create an account
                    </button>
                  </>
                ) : (
                  <>
                    Already have an account?{" "}
                    <button
                      type="button"
                      onClick={() => setMode("signin")}
                      className="font-medium text-primary hover:underline"
                    >
                      Sign in
                    </button>
                  </>
                )}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default function AuthPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-svh items-center justify-center bg-background text-sm text-muted-foreground">
          Loading...
        </div>
      }
    >
      <AuthPageInner />
    </Suspense>
  );
}