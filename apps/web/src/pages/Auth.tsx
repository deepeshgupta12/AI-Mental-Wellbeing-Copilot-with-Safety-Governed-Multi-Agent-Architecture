import { useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Mail } from "lucide-react";

export default function AuthPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"signin" | "signup">(
    searchParams.get("mode") === "signup" ? "signup" : "signin"
  );
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(mode === "signup" ? "/onboarding" : "/app");
  };

  return (
    <div className="min-h-svh bg-background flex">
      {/* Left panel - branding */}
      <div className="hidden lg:flex flex-col justify-between w-[45%] bg-primary/[0.03] border-r border-border p-10">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-md bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-heading font-bold text-sm">A</span>
          </div>
          <span className="font-heading font-semibold text-foreground text-lg">Aether</span>
        </Link>
        <div className="max-w-sm">
          <h2 className="font-heading text-3xl font-bold text-foreground leading-tight mb-4">
            Your wellbeing, supported with calm intelligence.
          </h2>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Aether helps you reflect, cope, and build better habits — with safety and privacy at its core.
          </p>
        </div>
        <p className="text-xs text-muted-foreground">
          Not a replacement for therapy or emergency services.
        </p>
      </div>

      {/* Right panel - form */}
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <Link to="/" className="lg:hidden flex items-center gap-2 text-sm text-muted-foreground mb-8 hover:text-foreground transition-aether">
            <ArrowLeft className="w-4 h-4" />
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
              <h1 className="font-heading text-2xl font-bold text-foreground mb-2">
                {mode === "signin" ? "Welcome back" : "Begin your journey"}
              </h1>
              <p className="text-muted-foreground text-sm mb-8">
                {mode === "signin"
                  ? "Sign in to continue with Aether."
                  : "Create your account to get started."}
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium">Email</Label>
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
                  <Label htmlFor="password" className="text-sm font-medium">Password</Label>
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

              <p className="text-center text-sm text-muted-foreground mt-6">
                {mode === "signin" ? (
                  <>
                    New to Aether?{" "}
                    <button
                      onClick={() => setMode("signup")}
                      className="text-primary font-medium hover:underline"
                    >
                      Create an account
                    </button>
                  </>
                ) : (
                  <>
                    Already have an account?{" "}
                    <button
                      onClick={() => setMode("signin")}
                      className="text-primary font-medium hover:underline"
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
