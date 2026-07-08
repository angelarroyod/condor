import type { Config } from "tailwindcss";

// "Luxe" theme — warm near-black, champagne accent, jade/wine market colors.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        lx: {
          bg: "#0C0B09",
          surface: "#14120F",
          surface2: "#1A1814",
          panel: "#11100D",
          input: "#0F0E0B",
          text: "#EAE4D6",
          text2: "#A79F8E",
          text3: "#6E6759",
          bright: "#F2EDE1",
          hair: "rgba(214,200,176,0.1)",
          faint: "rgba(214,200,176,0.06)",
          accent: "#C9A66B",
          "accent-bright": "#E4C98F",
          "accent-dim": "rgba(201,166,107,0.14)",
          "accent-border": "rgba(201,166,107,0.35)",
          up: "#3E8E72",
          "up-text": "#74C4A4",
          "up-dim": "rgba(79,163,131,0.15)",
          down: "#B05244",
          "down-text": "#DD8875",
          "down-dim": "rgba(192,95,81,0.15)",
        },
      },
      fontFamily: {
        sans: ["'Hanken Grotesk'", "sans-serif"],
        serif: ["'Instrument Serif'", "serif"],
        mono: ["'Spline Sans Mono'", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
