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
        display: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["'Fira Code'", "'JetBrains Mono'", "Consolas", "Monaco", "monospace"],
      },
      colors: {
        // Primary Brand Colors
        forgePurple: {
          DEFAULT: '#6B3BFF',
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#6B3BFF',
          600: '#5B21B6',
          700: '#4C1D95',
          800: '#3B1A70',
          900: '#2D1654',
        },
        neuralBlue: {
          DEFAULT: '#1E9EFF',
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#1E9EFF',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        aiElectric: {
          DEFAULT: '#00E5FF',
          50: '#ECFEFF',
          100: '#CFFAFE',
          200: '#A5F3FC',
          300: '#67E8F9',
          400: '#22D3EE',
          500: '#00E5FF',
          600: '#0891B2',
          700: '#0E7490',
          800: '#155E75',
          900: '#164E63',
        },
        // Neutral Colors
        deepTech: {
          DEFAULT: '#0B0A13',
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
          950: '#0B0A13',
        },
        techGray: {
          DEFAULT: '#B6BED3',
          50: '#F8F9FA',
          100: '#F1F3F5',
          200: '#E9ECEF',
          300: '#DEE2E6',
          400: '#CED4DA',
          500: '#B6BED3',
          600: '#868E96',
          700: '#495057',
          800: '#343A40',
          900: '#212529',
        },
        // Accent Colors
        success: {
          DEFAULT: '#10B981',
          light: '#D1FAE5',
          dark: '#065F46',
        },
        warning: {
          DEFAULT: '#F59E0B',
          light: '#FEF3C7',
          dark: '#92400E',
        },
        error: {
          DEFAULT: '#EF4444',
          light: '#FEE2E2',
          dark: '#991B1B',
        },
        info: {
          DEFAULT: '#3B82F6',
          light: '#DBEAFE',
          dark: '#1E3A8A',
        },
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, rgba(11,10,19,1) 0%, rgba(30,158,255,0.15) 100%)',
        'purple-gradient': 'linear-gradient(135deg, #6B3BFF 0%, #8B5CF6 100%)',
        'blue-gradient': 'linear-gradient(135deg, #1E9EFF 0%, #3B82F6 100%)',
        'cyber-gradient': 'linear-gradient(135deg, #00E5FF 0%, #1E9EFF 50%, #6B3BFF 100%)',
        'dark-gradient': 'linear-gradient(180deg, #0B0A13 0%, #1E293B 100%)',
        'glass': 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
      },
      boxShadow: {
        glow: '0 0 40px 0 rgba(107,59,255,0.35)',
        glowBlue: '0 0 40px 0 rgba(30,158,255,0.35)',
        glowCyan: '0 0 40px 0 rgba(0,229,255,0.35)',
        'glow-sm': '0 0 20px 0 rgba(107,59,255,0.25)',
        'glow-lg': '0 0 60px 0 rgba(107,59,255,0.45)',
        'inner-glow': 'inset 0 0 20px 0 rgba(107,59,255,0.2)',
        'neumorphic': '12px 12px 24px rgba(0,0,0,0.2), -12px -12px 24px rgba(255,255,255,0.05)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-down': 'slideDown 0.4s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
export default config
