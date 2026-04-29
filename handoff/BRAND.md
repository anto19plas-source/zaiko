# Zaiko — Brand Specification

## 1. Identité

**Nom** : Zaiko
**Produit** : Logiciel de gestion d'inventaire, de ratios et de stocks pour groupes de bars & restaurants.
**Baseline** : *« Le stock bouge. Zaiko s'adapte. »*

## 2. Logo

Le logo officiel combine un **symbole de niveaux de stock** (deux barres pleines encadrant trois barres décroissantes) + le **wordmark « Zaiko »** en Inter 600.

- **Espace de protection** : marge minimale égale à la hauteur du « k » du wordmark.
- **Tailles minimales** :
  - Wordmark + symbole : 32 px de haut
  - Symbole seul : 24 px
  - Favicon : 16 px (utiliser `favicon.svg`)
- **Le wordmark est toujours « Zaiko » seul**, sans tagline accolée.
- **Versions disponibles** :
  - `logo.svg` — fond clair (wordmark ink)
  - `logo-dark.svg` — fond sombre (wordmark bone)
  - `app-icon.svg` — icône d'application 1024×1024 (fond navy gradient)
  - `favicon.svg` — favicon 64×64

## 3. Palette

| Token | Hex | Rôle |
|---|---|---|
| Ink | `#0B1220` | Texte principal |
| Navy | `#0F2A4A` | Surface primaire |
| Navy deep | `#081A2F` | Profondeur, dark mode |
| Navy soft | `#1B3558` | Tracks, surfaces 2nd |
| Gold | `#C9A24B` | Accent principal |
| Gold light | `#E3C275` | Hover, highlights |
| Gold deep | `#A8862F` | Pressed |
| Red | `#B23A2A` | Alerte, stock bas |
| Red deep | `#8C2A1E` | Pressed danger |
| Bone | `#F4EFE6` | Texte sur sombre |
| Paper | `#FAF7F1` | Fond clair |
| Rule | `#E2D9C7` | Filets, borders |
| Muted | `#54688A` | Texte secondaire (light) |
| Muted dark | `#9FB2CF` | Texte secondaire (dark) |

### Ratio cible 60 / 30 / 8 / 2

- **60%** Navy / Ink
- **30%** Paper / Bone
- **8%** Gold (accent rare)
- **2%** Red (uniquement alerte)

### Règles strictes

- Le doré **n'est jamais en aplat dominant**.
- Le rouge **ne touche jamais le doré** (séparer par navy ou paper).
- Pas de gradients flashy. Le seul gradient autorisé est le radial subtil de l'app icon.

## 4. Typographie

| Famille | Usage | Graisses |
|---|---|---|
| **Inter** | UI, wordmark, labels, boutons | 300, 400, 500, 600, 700, 800 |
| **Fraunces** | Display, accents éditoriaux, citations | 400, 500, 600, 700 (italique inclus) |
| **JetBrains Mono** | Données, tags, codes, métriques, eyebrows | 400, 500, 600 |

### Échelle

| Token | Taille | Weight | Tracking |
|---|---|---|---|
| Display | 72 px | 700 | -0.04em |
| H1 | 56 px | 700 | -0.035em |
| H2 | 40 px | 700 | -0.02em |
| H3 | 32 px | 600 | -0.02em |
| Body | 16 px | 400 | normal |
| Small | 13 px | 400 | normal |
| Eyebrow (mono) | 11 px | 500 | 0.28em uppercase |

## 5. Iconographie

Le langage visuel se construit à partir de **barres horizontales empilées** qui évoquent des niveaux de stock.

- Coins arrondis : `rx 2-3` sur barres, `rx 23%` sur app icon
- Hauteur de barre : 12–14 unités sur grille 100
- Espacement entre barres ≥ hauteur de barre
- Gold = état OK / valeur · Red = alerte · Navy = neutre

## 6. Voix & ton

### On dit
- ✓ Précis, factuel, chiffré
- ✓ Direct — pas de jargon SaaS
- ✓ Métier d'abord (bar, cuisine, cave)
- ✓ Calme, posé — outil de pro

### On évite
- ✗ Emoji, exclamations
- ✗ « révolutionnaire », « game-changer »
- ✗ Références asiatiques visuelles (le nom suffit)
- ✗ Néons, gradients flashy

## 7. Composants clés

- **Buttons** : 5 variantes (primary navy, gold, ghost, ink, danger)
- **Badges** : 6 statuts (en stock, inventorié, seuil bas, rupture, brouillon, premium)
- **KPI cards** : valeur + label mono + trend coloré + barre d'accent gauche
- **Eyebrows** : labels JetBrains Mono uppercase tracking 0.28em
- **Quotes** : Fraunces italique sur fond ink

Voir `components.tsx` pour les implémentations React de référence.
