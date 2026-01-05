/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a365d',
          light: '#2c5282',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          DEFAULT: '#2563eb',
        },
        success: {
          DEFAULT: '#059669',
          light: '#d1fae5',
          dark: '#065f46',
        },
        warning: {
          DEFAULT: '#d97706',
          light: '#fef3c7',
          dark: '#92400e',
        },
        danger: {
          DEFAULT: '#dc2626',
          light: '#fee2e2',
          dark: '#991b1b',
        },
        info: {
          DEFAULT: '#0284c7',
          light: '#e0f2fe',
          dark: '#075985',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
}
