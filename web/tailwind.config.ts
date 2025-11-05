import type { Config } from "tailwindcss";
const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        panel: "#111827",
        border: "#223042",
        input: "#0b1220",
        text: "#e6eef6",
        brand: "#1f2a44",
        brandHover: "#24314f"
      },
      borderRadius: {
        xl2: "1rem"
      }
    },
  },
  plugins: [],
};
export default config;
