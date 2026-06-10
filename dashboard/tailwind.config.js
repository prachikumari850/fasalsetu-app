/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand — matches Flutter AppColors
        primary: {
          50:  '#f0fdf0',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#60AD5E',
          700: '#2E7D32',
          800: '#166534',
          900: '#005005',
          DEFAULT: '#2E7D32',
        },
        secondary: {
          DEFAULT: '#F9A825',
          light:   '#FFD95A',
          dark:    '#C17900',
        },
        // Semantic
        success: '#388E3C',
        warning: '#F57C00',
        danger:  '#C62828',
        info:    '#1565C0',
        // Neutrals
        surface:  '#FFFFFF',
        muted:    '#F5F5F0',
        border:   '#E0E4E0',
        // Text
        ink: {
          DEFAULT: '#1A1C1A',
          secondary: '#4A4D4A',
          hint:    '#9E9E9E',
        },
        // Claim status
        status: {
          draft:       '#9E9E9E',
          submitted:   '#1565C0',
          review:      '#F57C00',
          approved:    '#388E3C',
          rejected:    '#C62828',
          inspection:  '#6A1B9A',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        devanagari: ['"Noto Sans Devanagari"', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        card: '1rem',
        xl: '1.25rem',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(0 0 0 / 0.05), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
        dropdown: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        modal: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
      },
      screens: {
        xs: '475px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}