// Zaiko — Composants de référence
// Tokens lus depuis ./tokens (TS) — adapte les imports à ton arbo.

import React from 'react';
import { colors, fonts } from './tokens';

// === Button ============================================================
type ButtonVariant = 'primary' | 'gold' | 'ghost' | 'ink' | 'danger';
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: 'sm' | 'md' | 'lg';
}

const buttonStyles: Record<ButtonVariant, React.CSSProperties> = {
  primary: { background: colors.navy,   color: colors.bone, border: 'none' },
  gold:    { background: colors.gold,   color: colors.ink,  border: 'none', boxShadow: `inset 0 -2px 0 ${colors.goldDeep}` },
  ghost:   { background: 'transparent', color: colors.navy, border: `1px solid ${colors.navy}` },
  ink:     { background: colors.ink,    color: colors.bone, border: 'none' },
  danger:  { background: colors.red,    color: colors.bone, border: 'none' },
};

const sizePadding = { sm: '6px 10px', md: '11px 18px', lg: '14px 22px' };
const sizeFont    = { sm: 11, md: 14, lg: 16 };
const sizeRadius  = { sm: 4, md: 6, lg: 8 };

export function Button({ variant = 'primary', size = 'md', style, ...rest }: ButtonProps) {
  return (
    <button
      {...rest}
      style={{
        ...buttonStyles[variant],
        padding: sizePadding[size],
        fontFamily: fonts.sans,
        fontSize: sizeFont[size],
        fontWeight: 600,
        borderRadius: sizeRadius[size],
        cursor: 'pointer',
        letterSpacing: '-0.005em',
        ...style,
      }}
    />
  );
}

// === Badge =============================================================
type BadgeStatus = 'in-stock' | 'inventoried' | 'low' | 'out' | 'draft' | 'premium';
interface BadgeProps { status: BadgeStatus; children: React.ReactNode; }

const badgeMap: Record<BadgeStatus, { bg: string; fg: string; border?: string; dot?: string }> = {
  'in-stock':    { bg: colors.navy, fg: colors.bone, dot: colors.gold },
  'inventoried': { bg: 'transparent', fg: colors.navy, border: colors.navy, dot: colors.navy },
  'low':         { bg: colors.gold, fg: colors.ink },
  'out':         { bg: colors.red,  fg: colors.bone, dot: colors.bone },
  'draft':       { bg: colors.bone, fg: colors.ink, border: colors.rule },
  'premium':     { bg: colors.ink,  fg: colors.gold },
};

export function Badge({ status, children }: BadgeProps) {
  const s = badgeMap[status];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '5px 10px', borderRadius: 999,
      background: s.bg, color: s.fg,
      border: s.border ? `1px solid ${s.border}` : 'none',
      fontFamily: fonts.mono, fontSize: 10, letterSpacing: '0.18em',
      textTransform: 'uppercase', fontWeight: 600,
    }}>
      {s.dot && <span style={{ width: 6, height: 6, borderRadius: '50%', background: s.dot }} />}
      {children}
    </span>
  );
}

// === KpiCard ===========================================================
interface KpiCardProps {
  label: string;
  value: string;
  trend?: string;
  /** Couleur de la barre d'accent gauche */
  accent?: keyof typeof colors;
}

export function KpiCard({ label, value, trend, accent = 'gold' }: KpiCardProps) {
  const isPositive = trend?.startsWith('+');
  return (
    <div style={{
      flex: 1, background: colors.paper,
      border: `1px solid ${colors.rule}`,
      borderLeft: `3px solid ${colors[accent]}`,
      borderRadius: 8, padding: '18px 20px',
      display: 'flex', flexDirection: 'column', gap: 6,
    }}>
      <div style={{
        fontFamily: fonts.mono, fontSize: 9,
        letterSpacing: '0.22em', textTransform: 'uppercase',
        color: colors.muted,
      }}>{label}</div>
      <div style={{
        fontFamily: fonts.sans, fontSize: 30, fontWeight: 700,
        letterSpacing: '-0.02em', color: colors.ink, lineHeight: 1,
      }}>{value}</div>
      {trend && (
        <div style={{
          fontFamily: fonts.mono, fontSize: 11,
          color: isPositive ? colors.success : colors.danger,
        }}>{trend}</div>
      )}
    </div>
  );
}

// === Eyebrow / Label ===================================================
export function Eyebrow({ children, dark }: { children: React.ReactNode; dark?: boolean }) {
  return (
    <div style={{
      fontFamily: fonts.mono, fontSize: 11,
      letterSpacing: '0.28em', textTransform: 'uppercase',
      color: dark ? colors.mutedDark : colors.muted,
      fontWeight: 500,
    }}>{children}</div>
  );
}

// === Headline / Display ================================================
export function Headline({ children }: { children: React.ReactNode }) {
  return (
    <h1 style={{
      fontFamily: fonts.sans, fontWeight: 700, fontSize: 56,
      letterSpacing: '-0.035em', lineHeight: 1, color: colors.ink, margin: 0,
    }}>{children}</h1>
  );
}

export function Quote({ children }: { children: React.ReactNode }) {
  return (
    <p style={{
      fontFamily: fonts.serif, fontStyle: 'italic', fontWeight: 400,
      fontSize: 36, lineHeight: 1.25, letterSpacing: '-0.015em',
      color: colors.bone, maxWidth: 540, margin: 0,
    }}>{children}</p>
  );
}
