import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "VERITAS AI — Autonomous Banking Trust Intelligence",
  description: "Real-time fraud detection, regulatory compliance, and explainable underwriting intelligence powered by local AI models.",
  keywords: ["banking", "fraud detection", "compliance", "AI", "underwriting", "VERITAS"],
  authors: [{ name: "VERITAS AI" }],
  openGraph: {
    title: "VERITAS AI",
    description: "Autonomous Banking Trust Intelligence Platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "hsl(220, 18%, 12%)",
              color: "hsl(220, 10%, 92%)",
              border: "1px solid hsl(220, 12%, 22%)",
              borderRadius: "8px",
              fontSize: "0.875rem",
            },
          }}
        />
      </body>
    </html>
  );
}
