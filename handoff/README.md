# Zaiko — Design System Handoff

Ce dossier contient la charte graphique de **Zaiko** (logiciel de gestion d'inventaire et de ratios pour groupes de bars & restaurants) prête à être implémentée dans un site / une app.

## Comment l'utiliser avec Claude Code

Glisse ce dossier dans ta conversation Claude Code et dis-lui :

> Voici le design system de Zaiko. Implémente l'interface en respectant strictement les tokens définis dans `tokens.css` (ou `tokens.ts` selon le stack), la typographie, et les composants donnés en exemple. Le logo officiel est dans `logo.tsx` (composant React) et `logo.svg` (asset statique). La baseline de marque est : « Le stock bouge. Zaiko s'adapte. »

## Fichiers

| Fichier | Usage |
|---|---|
| `tokens.css` | Variables CSS — à importer dans le `:root` global |
| `tokens.ts` | Mêmes tokens en TypeScript (objet exporté) |
| `tailwind.config.js` | Configuration Tailwind si tu pars sur Tailwind |
| `logo.svg` | Logo principal — fond clair, asset SVG inline |
| `logo-dark.svg` | Logo principal — fond sombre |
| `logo.tsx` | Composant React `<ZaikoLogo />` (variant light/dark) |
| `app-icon.svg` | App icon 1024x1024 |
| `favicon.svg` | Favicon optimisé |
| `BRAND.md` | Spécification complète de la marque |
| `components.tsx` | Composants React de référence (Button, Badge, KpiCard, etc.) |

## Règles d'or

1. **Palette** : 60% navy / 30% paper / 8% gold / 2% red — **respecter ce ratio**
2. **Le doré est un accent**, jamais un aplat dominant
3. **Rouge et doré ne se touchent jamais** (toujours séparés par navy ou paper)
4. **Wordmark** : « Zaiko » seul, sans tagline accolée, Inter 700 letter-spacing -0.04em
5. **Typographies** : Inter (UI), Fraunces (éditorial), JetBrains Mono (data)
6. **Métaphore visuelle** : barres horizontales empilées = niveaux de stock
7. **Pas de gradients flashy, pas d'emoji, pas de référents asiatiques**

## Stack recommandé

- React + Vite + TypeScript
- Tailwind CSS (config fournie) **ou** CSS modules avec `tokens.css`
- Polices via Google Fonts (Inter, Fraunces, JetBrains Mono)

## Polices à charger

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fraunces:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```
