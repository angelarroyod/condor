import type { Config } from "tailwindcss";

// Dark trading-terminal palette. Extended per-feature in later phases.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#0a0e14",
          panel: "#121821",
          border: "#1f2733",
          up: "#26a69a",
          down: "#ef5350",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
