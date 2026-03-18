import type { Metadata } from "next";
import "./globals.css";

import { AppProviders } from "@/components/providers/AppProviders";

export const metadata: Metadata = {
  title: "Aether — AI Mental Wellbeing Copilot",
  description:
    "A trusted AI mental wellbeing copilot for stress, burnout, overwhelm, reflection, habits, and safe support.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}