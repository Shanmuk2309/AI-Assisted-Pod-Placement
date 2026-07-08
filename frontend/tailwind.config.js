/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Space Grotesk", "system-ui", "sans-serif"],
      },
      colors: {
        surface: {
          900: "#0b0f1a",
          800: "#111827",
          700: "#1a2236",
          600: "#243049",
        },
        accent: {
          DEFAULT: "#6366f1",
          light: "#818cf8",
          glow: "#4f46e5",
        },
        success: "#10b981",
        warning: "#f59e0b",
      },
      boxShadow: {
        glow: "0 0 40px rgba(99, 102, 241, 0.15)",
        card: "0 4px 24px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [],
};
