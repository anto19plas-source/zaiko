# Zaiko — Contexte de session pour reprise

> Ce document résume l'intégralité du travail effectué sur le projet Zaiko.
> À donner à une nouvelle session Claude pour reprendre là où on s'est arrêtés.

---

## 1. Projet

**Zaiko** — Logiciel de gestion d'inventaire, ratios et stocks pour le **Groupe WAC** (4 restaurants).

**Baseline officielle :** *« Le stock bouge. Zaiko s'adapte. »*

**Stack :**
- Streamlit (Python) — front + back
- SQLite — stockage local (fichier `zaiko.db`)
- Plotly — graphiques
- Pandas — manipulation tabulaire
- Déploiement : **Streamlit Community Cloud** depuis le repo GitHub `anto19plas-source/zaiko` (public)

**Compte GitHub** : `anto19plas-source` · `gh` CLI authentifié sur la machine.

---

## 2. Structure du projet

```
/Users/plasantonin/Desktop/CODE ZAIKO/
├── app.py                  # App Streamlit complète (~1000 lignes)
├── database.py             # Couche SQLite + seed (~280 lignes)
├── requirements.txt        # streamlit, pandas, plotly
├── .streamlit/
│   └── config.toml         # Thème Streamlit aligné brand
├── .gitignore              # ignore zaiko.db, __pycache__, .env, .DS_Store
├── handoff/                # ASSETS BRAND OFFICIELS — référence absolue
│   ├── BRAND.md            # Spec brand complète (palette, typo, voix)
│   ├── tokens.css          # CSS tokens officiels
│   ├── tokens.ts           # TS tokens
│   ├── components.tsx      # Composants React de référence
│   ├── tailwind.config.js
│   ├── logo.svg            # Logo + wordmark fond clair
│   ├── logo-dark.svg       # Logo + wordmark fond sombre
│   ├── app-icon.svg        # Icône d'app 1024×1024
│   ├── favicon.svg
│   └── logo.tsx            # Logo en composant React
└── ZAIKO/
    └── Logo ZAIKO.zip      # Archive logo (référence)
```

---

## 3. Charte graphique — règles strictes

**Palette officielle (à utiliser EXACTEMENT) :**

| Token | Hex | Rôle |
|---|---|---|
| Ink | `#0B1220` | Texte principal |
| Navy | `#0F2A4A` | Surface primaire |
| Navy deep | `#081A2F` | Profondeur, dark mode |
| Navy soft | `#1B3558` | Tracks, surfaces 2nd |
| Gold | `#C9A24B` | Accent principal |
| Gold light | `#E3C275` | Hover |
| Gold deep | `#A8862F` | Pressed |
| Red | `#B23A2A` | Alerte |
| Red deep | `#8C2A1E` | Pressed danger |
| Bone | `#F4EFE6` | Texte sur sombre |
| Paper | `#FAF7F1` | Fond clair |
| Rule | `#E2D9C7` | Filets, borders |
| Muted | `#54688A` | Texte secondaire light |
| Muted dark | `#9FB2CF` | Texte secondaire dark |
| Success | `#2A6F4F` | États positifs |

**Ratio cible 60/30/8/2 :**
- 60% Navy/Ink
- 30% Paper/Bone
- 8% Gold (accent rare)
- 2% Red (uniquement alerte)

**Règles strictes :**
- Le doré n'est JAMAIS en aplat dominant
- Le rouge ne touche JAMAIS le doré (séparer par navy ou paper)
- Pas de gradients flashy
- **Aucun emoji** — couleurs d'accent uniquement

**Typographie :**

| Famille | Usage |
|---|---|
| **Inter** | UI, wordmark "Zaiko", labels, boutons |
| **Fraunces** | Display, citations italiques uniquement |
| **JetBrains Mono** | Données, eyebrows, métriques, codes |

- Wordmark **"Zaiko" en Inter 600** (PAS Fraunces)
- Eyebrows en JetBrains Mono **uppercase tracking 0.28em**
- Citations en Fraunces italique

---

## 4. Restaurants du Groupe WAC

| ID | Nom | Type | Couleur d'accent | Clé URL |
|---|---|---|---|---|
| 1 | Chéri Chéri | Bar à cocktails | `#D89593` (rose pêche) | `cheri_cheri` |
| 2 | Chéri Guapito | Restaurant mexicain | `#B23A2A` (rouge) | `guapito` |
| 3 | Chéri Guapo | Restaurant argentin | `#7A2A22` (bordeaux) | `guapo` |
| 4 | Les Halles de la Cité | Brasserie | `#C9A24B` (gold) | `halles` |

---

## 5. Architecture de navigation

**Top navbar fixe** (pas de sidebar) avec dropdowns CSS au survol :

```
ZAIKO (logo+wordmark) | Groupe WAC ▾ | Chéri Chéri ▾ | Chéri Guapito ▾ | Chéri Guapo ▾ | Les Halles ▾
```

**Dropdown Groupe WAC :**
- Dashboard
- Catalogue
- Fiches techniques

**Dropdown chaque restaurant (×4) :**
- Dashboard
- Inventaire
- Mouvements
- Ventes & Ratios

**Routing :** via `st.query_params["page"]`, format `?page={key}_{section}` ou `?page=groupe_{section}`.

---

## 6. État actuel des modules

### ✅ Terminé

- **Navbar** avec dropdowns CSS, logo SVG officiel inline, wordmark Inter 600
- **CSS complet** aligné sur tokens officiels (`#0F2A4A` navy, `#C9A24B` gold, etc.)
- **Page Groupe WAC > Dashboard** — KPIs, tableau résumé restos, chart CA consolidé 30j
- **Page Groupe WAC > Catalogue** — vue tableau (à refondre, voir §7)
- **Page Groupe WAC > Fiches techniques** — placeholder "Module en préparation"
- **Page Restaurant > Dashboard** — banner navy + KPIs + chart 14j + alertes + derniers mouvements
- **Page Restaurant > Inventaire** — tableau filtrable + form de saisie
- **Page Restaurant > Mouvements** — historique + form saisie + chart répartition
- **Page Restaurant > Ventes & Ratios** — KPIs + courbe réel/théorique + form saisie

### 🚧 En cours — REFONTE CATALOGUE (interrompue)

L'utilisateur a demandé de refondre la page Catalogue. La nouvelle spec :

**Vue lecture :**
- Sections visuelles distinctes par catégorie (pas un tableau plat)
- Hiérarchie : catégorie en partie principale → références dessous
- Pour chaque référence sur la même ligne : `nom · conditionnement · prix`
- **PAS d'alertes** dans la vue
- Plus visuel, plus intuitif, moins brouillon

**Formulaire d'ajout (refonte) :**
- **Saisie manuelle libre** : nom + prix
- **Menus déroulants prédéfinis** pour : catégorie + conditionnement
- **Conditionnements à intégrer** : 20cl, 25cl, 33cl, 37.5cl, 50cl, 70cl, 75cl, 1L, 1.5L, 2L, 5L, 100g, 250g, 500g, 750g, 1kg, 2kg, 5kg, 10kg, pièce, lot, carton
- **Retirer le champ "seuil d'alerte"**

**Ce qui a été fait avant interruption :**
- ✅ `database.py` : seed des 15 produits mis à jour avec formats propres (70cl, 75cl, 1L, 33cl, 1kg, 500g, pièce)
- ❌ `app.py` : la fonction `render_groupe_catalogue()` n'a PAS été refondue — elle utilise encore le tableau Streamlit avec form ancien

**Note utilisateur importante :** *« une fois que la structure me conviendra on pourra importer toutes les données »* — l'utilisateur a ses vraies données réelles à importer après validation de la structure.

### 📋 Ce qu'il reste à faire

1. Refondre `render_groupe_catalogue()` dans `app.py` :
   - Vue par catégorie en blocs (HTML personnalisé, pas de DataFrame)
   - Lignes produits en grid 3 colonnes : nom | format | prix
   - Form simplifié sans seuil d'alerte
2. Ajouter le CSS pour `.zk-cat-block`, `.zk-cat-header`, `.zk-prod-line`
3. Ajouter une constante `FORMATS_PREDEFINIS` dans app.py
4. Ajuster `db.add_produit()` pour rendre `seuil_alerte` optionnel (default=0)
5. Une fois validé par l'utilisateur → préparer un script d'import des vraies données

---

## 7. Décisions UX/design clés prises

- **Tabs internes vs scroll** : option **navbar top avec dropdowns** retenue (Linear/Vercel pattern)
- **Chaque restaurant a son propre dropdown** (pas un mega-menu "Restaurants")
- **Sidebar Streamlit cachée** complètement
- **KPI cards** avec barre d'accent gauche 3px (pas de border uniforme)
- **Badges en pill** avec dot et mono uppercase
- **Banner restaurant** : navy strict + barre d'accent latérale (pas de gradient)
- **Routing par query params** `?page=xxx` (compatible Streamlit Cloud)
- **Logo SVG inline** dans navbar (pas de fichier externe pour fiabilité)

---

## 8. Déploiement

**Repo GitHub** : https://github.com/anto19plas-source/zaiko (public)
**Streamlit Cloud** : URL configurée par l'utilisateur sur share.streamlit.io
**App pointe sur** : `app.py`, branche `main`

**Workflow de déploiement :**
1. Modifier le code localement
2. `git add -A && git commit -m "..." && git push`
3. Streamlit Cloud redéploie automatiquement (~2 min)

**Lancement local :**
```bash
cd "Desktop/CODE ZAIKO"
streamlit run app.py
# → http://localhost:8501
```

---

## 9. Préférences de l'utilisateur (importantes)

- **Communication en français**
- **Toujours proposer une approche AVANT de coder**, attendre validation
- **Vérifier qu'il n'y a pas d'erreurs après modification**
- **Garder `database.py` intact** sauf si vraiment nécessaire (l'utilisateur l'a explicitement demandé au départ)
- **Pas d'emojis dans l'app finale** (charte stricte)
- **Style "professionnel, métier d'abord, calme, posé"** (cf BRAND.md §6 voix & ton)
- **Ne PAS utiliser** : "révolutionnaire", "game-changer", références asiatiques visuelles, néons, gradients flashy

---

## 10. Pour reprendre la session

**Premier message à donner à la nouvelle session Claude :**

> Salut, je reprends le projet Zaiko. Lis le fichier `/Users/plasantonin/Desktop/CODE ZAIKO/CONTEXT.md` pour avoir tout le contexte.
>
> Là où on s'est arrêté : on doit refondre la page Catalogue. La spec exacte est dans le §6 du CONTEXT.md.
>
> Avant de coder, propose-moi ton approche pour la nouvelle vue Catalogue + le formulaire d'ajout, en respectant strictement la charte (cf §3) et tout ce qui a déjà été fait.

---

*Document généré le 30 avril 2026 — fin de session avant refonte du Catalogue.*
