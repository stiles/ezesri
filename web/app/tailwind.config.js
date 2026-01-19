/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Deep navy/charcoal base
        'ink': {
          50: '#f6f7f9',
          100: '#eceef2',
          200: '#d5dae2',
          300: '#b0b9c9',
          400: '#8594ab',
          500: '#667790',
          600: '#516077',
          700: '#434e61',
          800: '#3a4352',
          900: '#333a46',
          950: '#1e2329',
        },
        // Warm accent
        'ember': {
          50: '#fef6ee',
          100: '#fcebd7',
          200: '#f8d3ae',
          300: '#f3b47b',
          400: '#ed8c46',
          500: '#e96f23',
          600: '#da5519',
          700: '#b54017',
          800: '#90341a',
          900: '#742d18',
          950: '#3e140a',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
