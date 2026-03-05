/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      keyframes: {
        slideIn: {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        progress: {
          "0%": { width: "0%", marginLeft: "0%" },
          "50%": { width: "60%", marginLeft: "20%" },
          "100%": { width: "0%", marginLeft: "100%" },
        },
      },
      animation: {
        slideIn: "slideIn 0.3s ease-out",
        progress: "progress 2s ease-in-out infinite",
      },
      colors: {
        navy: {
          50: "#f0f3f9",
          100: "#d9e0f0",
          200: "#b3c1e1",
          300: "#8da2d2",
          400: "#6783c3",
          500: "#4164b4",
          600: "#345090",
          700: "#273c6c",
          800: "#1a2848",
          900: "#0d1424",
        },
      },
    },
  },
  plugins: [],
};
