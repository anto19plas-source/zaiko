// Zaiko — Design tokens (TypeScript)
// Source unique de vérité. Garde aligné avec tokens.css.

export const colors = {
  ink: '#0B1220',
  navy: '#0F2A4A',
  navyDeep: '#081A2F',
  navySoft: '#1B3558',

  gold: '#C9A24B',
  goldLight: '#E3C275',
  goldDeep: '#A8862F',

  red: '#B23A2A',
  redDeep: '#8C2A1E',

  bone: '#F4EFE6',
  paper: '#FAF7F1',
  rule: '#E2D9C7',

  muted: '#54688A',
  mutedDark: '#9FB2CF',

  success: '#2A6F4F',
  warning: '#C9A24B',
  danger: '#B23A2A',
} as const;

export const fonts = {
  sans:  "'Inter', system-ui, -apple-system, sans-serif",
  serif: "'Fraunces', Georgia, serif",
  mono:  "'JetBrains Mono', ui-monospace, monospace",
} as const;

export const fontSize = {
  xs: '11px', sm: '13px', base: '16px', lg: '18px',
  xl: '24px', '2xl': '32px', '3xl': '40px', '4xl': '56px', '5xl': '72px',
} as const;

export const radius = {
  sm: '4px', md: '6px', lg: '10px', xl: '16px', app: '23%',
} as const;

export const space = {
  1: '4px', 2: '8px', 3: '12px', 4: '16px',
  5: '24px', 6: '32px', 7: '44px', 8: '64px',
} as const;

export const shadow = {
  sm: '0 2px 6px -2px rgba(8, 26, 47, 0.08)',
  md: '0 8px 24px -8px rgba(8, 26, 47, 0.18)',
  lg: '0 24px 48px -16px rgba(8, 26, 47, 0.45)',
} as const;

// Ratio cible d'utilisation des couleurs sur une page
export const colorRatio = {
  navy: 60,   // %
  paper: 30,
  gold: 8,
  red: 2,
} as const;

export const tokens = { colors, fonts, fontSize, radius, space, shadow, colorRatio };
export default tokens;
