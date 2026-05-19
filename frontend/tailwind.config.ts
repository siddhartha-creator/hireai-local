import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        mist: "#eef3f8",
        signal: "#0f766e",
        ember: "#b45309",
      },
    },
  },
  plugins: [],
};

export default config;
