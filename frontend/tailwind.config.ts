import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        cafe: {
          green: "#00704A",
          "green-dark": "#1E3932",
          "green-light": "#D4E9E2",
          cream: "#F2F0EB",
          gold: "#CBA258",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
