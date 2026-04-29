/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,html}'],
  theme: {
    extend: {
      colors: {
        ink:       '#0B1220',
        navy: {
          DEFAULT: '#0F2A4A',
          deep:    '#081A2F',
          soft:    '#1B3558',
        },
        gold: {
          DEFAULT: '#C9A24B',
          light:   '#E3C275',
          deep:    '#A8862F',
        },
        red: {
          DEFAULT: '#B23A2A',
          deep:    '#8C2A1E',
        },
        bone:  '#F4EFE6',
        paper: '#FAF7F1',
        rule:  '#E2D9C7',
        muted: {
          DEFAULT: '#54688A',
          dark:    '#9FB2CF',
        },
      },
      fontFamily: {
        sans:  ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Fraunces', 'Georgia', 'serif'],
        mono:  ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        wordmark: '-0.04em',
        eyebrow:  '0.28em',
      },
      borderRadius: {
        app: '23%',
      },
      boxShadow: {
        zk: '0 24px 48px -16px rgba(8, 26, 47, 0.45)',
      },
    },
  },
  plugins: [],
};
