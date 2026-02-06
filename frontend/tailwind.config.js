/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["Space Mono", "Courier New", "monospace"],
      },
      colors: {
        core: {
          50: "#f8f9fa",
          100: "#e9ecef",
          200: "#dee2e6",
          300: "#adb5bd",
          400: "#6c757d",
          500: "#2d3436",
          600: "#212529",
          700: "#1a1d20",
          800: "#0f1214",
          900: "#0a0c0e",
          950: "#000000",
        },
        cyber: {
          50: "#f0fdfa",
          100: "#ccfbf1",
          200: "#99f6e4",
          300: "#5eead4",
          400: "#2dd4bf",
          500: "#14b8a6",
          600: "#0d9488",
          700: "#0f766e",
          800: "#115e59",
          900: "#134e4a",
        },
        neon: {
          pink: "#ff006e",
          purple: "#8338ec",
          blue: "#3a86ff",
          cyan: "#00f5ff",
          green: "#06ffa5",
          yellow: "#ffbe0b",
        },
        slate: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          850: "#172033",
          900: "#0f172a",
          925: "#0c1220",
          950: "#0a0a0f",
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "gradient-core": "linear-gradient(135deg, #2d3436 0%, #0a0c0e 100%)",
        "gradient-cyber":
          "linear-gradient(135deg, #334155 0%, #1e293b 50%, #0f172a 100%)",
        "gradient-neon":
          "linear-gradient(135deg, #475569 0%, #334155 50%, #1e293b 100%)",
        "gradient-mesh":
          "linear-gradient(135deg, rgba(45, 52, 54, 0.1) 0%, rgba(30, 41, 59, 0.1) 100%)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "bounce-subtle": "bounce-subtle 1s infinite",
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-in-right": "slideInRight 0.3s ease-out",
        "slide-in-left": "slideInLeft 0.3s ease-out",
        typing: "typing 1.5s infinite",
        glow: "glow 2s ease-in-out infinite",
        float: "float 3s ease-in-out infinite",
        shimmer: "shimmer 2s linear infinite",
        scan: "scan 3s linear infinite",
      },
      keyframes: {
        "bounce-subtle": {
          "0%, 100%": { transform: "translateY(-5%)" },
          "50%": { transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideInLeft: {
          "0%": { opacity: "0", transform: "translateX(-20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        typing: {
          "0%, 60%, 100%": { opacity: "0.3" },
          "30%": { opacity: "1" },
        },
        glow: {
          "0%, 100%": {
            boxShadow:
              "0 0 20px rgba(45, 52, 54, 0.3), 0 0 40px rgba(45, 52, 54, 0.1)",
          },
          "50%": {
            boxShadow:
              "0 0 30px rgba(45, 52, 54, 0.5), 0 0 60px rgba(45, 52, 54, 0.2)",
          },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-1000px 0" },
          "100%": { backgroundPosition: "1000px 0" },
        },
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
      },
      boxShadow: {
        neon: "0 0 20px rgba(45, 52, 54, 0.5)",
        "neon-lg": "0 0 30px rgba(45, 52, 54, 0.6)",
        cyber: "0 0 20px rgba(20, 184, 166, 0.5)",
        "cyber-lg": "0 0 30px rgba(20, 184, 166, 0.6)",
        glow: "0 0 15px rgba(45, 52, 54, 0.3)",
        "inner-glow": "inset 0 0 20px rgba(45, 52, 54, 0.1)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
