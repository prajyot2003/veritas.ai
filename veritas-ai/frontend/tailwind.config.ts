import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Veritas brand palette
        background: "hsl(220, 20%, 6%)",
        surface: "hsl(220, 18%, 10%)",
        "surface-2": "hsl(220, 16%, 14%)",
        "surface-3": "hsl(220, 14%, 18%)",
        border: "hsl(220, 12%, 22%)",
        "border-light": "hsl(220, 12%, 28%)",
        muted: "hsl(220, 10%, 50%)",
        foreground: "hsl(220, 10%, 92%)",
        primary: {
          DEFAULT: "hsl(213, 94%, 55%)",
          dark: "hsl(213, 94%, 42%)",
          light: "hsl(213, 94%, 70%)",
        },
        accent: {
          cyan: "hsl(188, 94%, 50%)",
          violet: "hsl(265, 80%, 60%)",
          emerald: "hsl(160, 84%, 45%)",
          amber: "hsl(38, 92%, 55%)",
          rose: "hsl(350, 89%, 60%)",
        },
        risk: {
          low: "hsl(160, 84%, 45%)",
          medium: "hsl(38, 92%, 55%)",
          high: "hsl(25, 95%, 55%)",
          critical: "hsl(350, 89%, 60%)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "hero-gradient": "linear-gradient(135deg, hsl(220,20%,6%) 0%, hsl(230,40%,10%) 50%, hsl(220,20%,6%) 100%)",
        "card-gradient": "linear-gradient(135deg, hsl(220,18%,11%) 0%, hsl(220,16%,14%) 100%)",
        "glow-primary": "radial-gradient(ellipse at center, hsl(213,94%,55%,0.15) 0%, transparent 70%)",
        "glow-danger": "radial-gradient(ellipse at center, hsl(350,89%,60%,0.15) 0%, transparent 70%)",
      },
      boxShadow: {
        "glow-primary": "0 0 20px hsl(213,94%,55%,0.3), 0 0 60px hsl(213,94%,55%,0.1)",
        "glow-danger": "0 0 20px hsl(350,89%,60%,0.3)",
        "glow-success": "0 0 20px hsl(160,84%,45%,0.3)",
        glass: "0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.08)",
        card: "0 4px 24px rgba(0,0,0,0.4)",
      },
      animation: {
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "scan-line": "scan-line 3s linear infinite",
        "float": "float 3s ease-in-out infinite",
        "slide-up": "slide-up 0.4s ease-out",
        "fade-in": "fade-in 0.3s ease-out",
        "counter": "counter 1s ease-out",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: "1", boxShadow: "0 0 20px hsl(213,94%,55%,0.4)" },
          "50%": { opacity: "0.8", boxShadow: "0 0 40px hsl(213,94%,55%,0.6)" },
        },
        "scan-line": {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-6px)" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

export default config;
