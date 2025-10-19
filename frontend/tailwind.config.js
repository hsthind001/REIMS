/** @type {import('tailwindcss').Config} */
import reimsColors from './tailwind.config.colors.js'

export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Import full REIMS color system
        ...reimsColors,
        
        // Semantic aliases for common use
        primary: reimsColors.brand.blue,
        secondary: reimsColors.neutral.slate,
        success: reimsColors.status.success,
        warning: reimsColors.status.warning,
        error: reimsColors.status.error,
        info: reimsColors.status.info,
        
        // shadcn/ui compatibility
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: reimsColors.brand.blue[500],
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        destructive: {
          DEFAULT: reimsColors.status.error[500],
          foreground: "#FFFFFF",
        },
        muted: {
          DEFAULT: reimsColors.neutral.slate[100],
          foreground: reimsColors.neutral.slate[600],
        },
        accent: {
          DEFAULT: reimsColors.accent.purple[500],
          foreground: "#FFFFFF",
        },
        popover: {
          DEFAULT: "#FFFFFF",
          foreground: reimsColors.neutral.slate[900],
        },
        card: {
          DEFAULT: "#FFFFFF",
          foreground: reimsColors.neutral.slate[900],
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}