/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0a0f1c', // Deep dark blue background
        surface: '#131b2f', // Slightly lighter for cards
        border: '#1f2940',
        primary: {
          DEFAULT: '#10b981', // Emerald green
          hover: '#059669',
        },
        accent: {
          DEFAULT: '#3b82f6', // Electric blue
          hover: '#2563eb',
        },
        text: {
          main: '#f8fafc',
          muted: '#94a3b8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      }
    },
  },
  plugins: [],
}
