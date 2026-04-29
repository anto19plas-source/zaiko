// Zaiko — Composant Logo officiel
// Utilisation : <ZaikoLogo /> ou <ZaikoLogo variant="dark" />
// Le wordmark s'adapte automatiquement au variant.

import React from 'react';

type Variant = 'light' | 'dark';

interface ZaikoLogoProps {
  variant?: Variant;
  /** Hauteur en px. Le ratio est conservé (≈ 2.7:1). */
  height?: number;
  /** Si true, n'affiche que le symbole sans le wordmark. */
  symbolOnly?: boolean;
  className?: string;
}

export function ZaikoLogo({
  variant = 'light',
  height = 44,
  symbolOnly = false,
  className,
}: ZaikoLogoProps) {
  const wordColor = variant === 'dark' ? '#F4EFE6' : '#0B1220';
  const width = symbolOnly ? height * (120 / 132) : height * (360 / 132);
  const viewBox = symbolOnly ? '0 0 120 132' : '0 0 360 132';

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={viewBox}
      width={width}
      height={height}
      role="img"
      aria-label="Zaiko"
      className={className}
    >
      {/* Symbol — 4 niveaux de stock */}
      <g>
        <rect x="10"  y="14"  width="100" height="18" rx="2" fill="#0F2A4A" />
        <rect x="14"  y="14"  width="92"  height="4"  fill="#C9A24B" opacity="0.9" />
        <rect x="62"  y="40"  width="34"  height="14" rx="2" fill="#0F2A4A" opacity="0.75" />
        <rect x="46"  y="60"  width="34"  height="14" rx="2" fill="#0F2A4A" opacity="0.6" />
        <rect x="30"  y="80"  width="34"  height="14" rx="2" fill="#B23A2A" opacity="0.9" />
        <rect x="10"  y="100" width="100" height="18" rx="2" fill="#0F2A4A" />
        <rect x="14"  y="114" width="92"  height="4"  fill="#C9A24B" opacity="0.9" />
      </g>
      {!symbolOnly && (
        <text
          x="146" y="92"
          fontFamily="Inter, system-ui, sans-serif"
          fontWeight={600}
          fontSize={84}
          letterSpacing={-3.4}
          fill={wordColor}
        >
          Zaiko
        </text>
      )}
    </svg>
  );
}

export default ZaikoLogo;
