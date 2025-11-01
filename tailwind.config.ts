import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./src/pages/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/app/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "Noto Sans", "sans-serif"],
      },
      colors: {
        forgePurple: '#6B3BFF',
        neuralBlue: '#1E9EFF',
        aiElectric: '#00E5FF',
        deepTech: '#0B0A13',
        techGray: '#B6BED3'
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, rgba(11,10,19,1) 0%, rgba(30,158,255,0.15) 100%)',
      },
      boxShadow: {
        glow: '0 0 40px 0 rgba(107,59,255,0.35)',
        glowBlue: '0 0 40px 0 rgba(30,158,255,0.35)',
      },
    },
  },
  plugins: [],
}
export default config
