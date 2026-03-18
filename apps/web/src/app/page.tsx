"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center px-6 text-center">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-primary-foreground font-heading font-bold">
            A
          </div>
          <span className="font-heading text-2xl font-semibold">Aether</span>
        </div>

        <h1 className="font-heading text-4xl font-bold tracking-tight md:text-5xl">
          Next.js migration in progress
        </h1>

        <p className="mt-4 max-w-2xl text-muted-foreground">
          V1.12 is now running on a Next.js scaffold. In the next step, we will
          move the existing V1 user and admin routes into the App Router without
          changing product behavior.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link href="/onboarding">
            <Button variant="hero" size="lg">
              Go to onboarding
            </Button>
          </Link>
          <Link href="/admin">
            <Button variant="outline" size="lg">
              Open admin
            </Button>
          </Link>
        </div>
      </div>
    </main>
  );
}