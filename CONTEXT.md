# Zaiko — Contexte de session pour reprise

> Ce document résume l'état actuel du projet Zaiko.
> À donner à une nouvelle session Claude pour reprendre proprement.

---

## 1. Projet

**Zaiko** — Logiciel de gestion d'inventaire, ratios et stocks pour le **Groupe WAC** (4 restaurants).

**Baseline officielle :** *« Le stock bouge. Zaiko s'adapte. »*

**Stack :**
- Streamlit (Python) — front + back
- SQLite — stockage local (`zaiko.db`, recréé au démarrage si absent)
- Plotly — graphiques
- Pandas — manipulation tabulaire
- Déploiement : **Streamlit Community Cloud** depuis `anto19plas-source/zaiko` (public)

**Compte GitHub** : `anto19plas-source` · `gh` CLI authentifié.

---

## 2. Structure du projet

```
/Users/plasantonin/Desktop/CODE ZAIKO/
├── app.py                  # App Streamlit (~1300 lignes, toutes les pages)
├── database.py             # Couche SQLite + seed (~370 lignes)
├── seed_data.py            # Catalogue WAC réel : 33 catégories + 729 produits
├── base prix wac .xlsx     # Source Excel du catalogue (gitignored, local only)
├── requirements.txt        # streamlit, pandas, plotly
├── .streamlit/config.toml  # Thème Streamlit aligné brand
├── .gitignore              # ignore zaiko.db, base prix wac .xlsx, __pycache__, .env, .DS_Store
├── handoff/                # ASSETS BRAND OFFICIELS — référence absolue
│   ├── BRAND.md            # Spec brand complète (palette, typo, voix)
│   ├── tokens.css / tokens.ts
│   ├── components.tsx
│   ├── tailwind.config.js
│   ├── logo.svg / logo-dark.svg / app-icon.svg / favicon.svg / logo.tsx
└── ZAIKO/Logo ZAIKO.zip
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

**Ratio cible 60/30/8/2 :** 60% Navy/Ink · 30% Paper/Bone · 8% Gold (rare) · 2% Red (alerte uniquement).

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
ZAIKO | Groupe WAC ▾ | Chéri Chéri ▾ | Chéri Guapito ▾ | Chéri Guapo ▾ | Les Halles ▾
```

**Dropdown Groupe WAC :** Dashboard · Catalogue · **Évolution des prix** · Fiches techniques

**Dropdown chaque restaurant (×4) :** Dashboard · Inventaire · Mouvements · Ventes & Ratios

**Routing :** `st.query_params["page"]`, format `?page={key}_{section}` ou `?page=groupe_{section}`.

---

## 6. État actuel des modules

### Page Groupe WAC

#### Dashboard
KPIs · tableau résumé restos · chart CA consolidé 30j. **Stable.**

#### Catalogue (refondu et complet)
- Vue par **blocs catégorie** (HTML custom navy/gold) — pas de tableau plat
- Chaque ligne : `nom · conditionnement · prix` en grille 3 colonnes
- **Barre de filtres** (recherche texte sur le nom · catégorie · conditionnement) avec options dynamiques basées sur le contenu réel
- **Section "Modifier une référence"** : selectbox de la ref + form pré-rempli + boutons Enregistrer / Supprimer (avec checkbox de confirmation)
- **Section "Ajouter un produit"** : form simplifié, pas de seuil d'alerte
- **15 refs en "prix à définir"** affichées en rouge (5 avec note d'alerte du fichier source + 10 sans prix renseigné) — l'utilisateur les complétera manuellement
- `FORMATS_PREDEFINIS` : `bouteille` (par défaut) · 10cl · 20cl · 25cl · 33cl · 37.5cl · 48.5cl · 50cl · 70cl · 75cl · 1L · 1.5L · 2L · 3L · 5L · 10L · 20L · 30L · 100g · 150g · 250g · 500g · 750g · 1kg · 2kg · 5kg · 10kg · pièce · lot · carton

#### Évolution des prix (nouvelle page)
- Routing : `?page=groupe_prix`
- Table SQLite `historique_prix` (produit_id, ancien_prix, nouveau_prix, date_changement)
- Log automatique à chaque changement de prix (via `db.update_produit()`)
- Au démarrage : seed un point d'ancrage par produit existant si la table est vide
- 3 KPIs : nb total de changements · dernière modification · variation moyenne (%)
- Selectbox "Toutes les références" ou une seule
- Si une réf : courbe Plotly (ligne navy + points gold) + tableau des changements de cette réf
- Sinon : tableau des 30 derniers changements (date, ref, ancien → nouveau, variation %)
- Variations en rouge (hausse) / success (baisse) / muted (flat)

#### Fiches techniques
Placeholder "Module en préparation".

### Pages Restaurant (×4)

| Page | État |
|---|---|
| Dashboard | Stable — banner navy + KPIs + chart 14j + alertes + derniers mouvements |
| Inventaire | **À refondre — voir §8** (structure de saisie à changer) |
| Mouvements | Stable — historique + form saisie + chart répartition |
| Ventes & Ratios | Stable — KPIs + courbe réel/théorique + form saisie |

---

## 7. Catalogue produits — données réelles importées

Le seed dummy (15 produits) a été remplacé par le **catalogue WAC réel** issu de `base prix wac .xlsx` :

- **729 références**, **33 catégories** dans `seed_data.py`
- Catégories conservées telles quelles depuis le fichier source (CUBIS, RHUMS, WHISKYS, GINS, VODKA, TEQUILAS, APERITIF/LIQUEUR/BITTER, DIGESTIFS, EAUX LITRE, SCHWEPPES TONIC, SODAS/SOFT, PAGO, JUS LITRE, SODA LITRE, BIERE, BIERE FUT, SIROP, PUREE, COMPLEMENT BAR, EPICE/FRUIT, CAFE, VIN ROSE, VIN ROSE (MAGNUM), VIN BLANC, VIN ROUGE, VIN ROUGE (MAGNUM), etc.)
- Magnums **conservés en catégories séparées** comme demandé
- Format `bouteille` par défaut quand non précisé dans la source
- L'inventaire et les mouvements ont été retirés du seed → la DB démarre **propre** côté restaurants (les vrais relevés seront saisis via les pages restaurants)

**Pour ré-importer / modifier le catalogue source :**
1. Mettre à jour `base prix wac .xlsx` (local, non commit)
2. Re-exécuter le script de parsing (à recréer si besoin — voir l'historique git du commit `777df90`)
3. Le script génère un nouveau `seed_data.py`
4. **Attention :** le seed ne se déclenche QUE si la table `restaurants` est vide. Pour forcer un re-seed sur Streamlit Cloud, il faut **Reboot l'app** depuis Manage app.

---

## 8. Prochaine étape — Refonte saisie inventaire restaurants

**À faire dès que l'utilisateur communique la nouvelle structure :**

L'utilisateur a annoncé qu'il veut changer la structure de saisie d'inventaire pour chaque restaurant. La spec exacte sera donnée en prochain message. Voir `app.py:render_resto_inventaire()` pour le code actuel (tableau filtrable + form de saisie classique).

Quand la spec arrive : **proposer l'approche AVANT de coder**, attendre validation, puis implémenter et pousser sur GitHub directement (l'utilisateur préfère valider via Streamlit Cloud plutôt qu'en local).

---

## 9. Décisions UX/design clés prises

- **Tabs internes vs scroll** : navbar top avec dropdowns CSS (Linear/Vercel pattern)
- **Chaque restaurant a son propre dropdown** (pas un mega-menu "Restaurants")
- **Sidebar Streamlit cachée** complètement
- **KPI cards** avec barre d'accent gauche 3px (pas de border uniforme)
- **Badges en pill** avec dot et mono uppercase
- **Banner restaurant** : navy strict + barre d'accent latérale (pas de gradient)
- **Routing par query params** `?page=xxx` (compatible Streamlit Cloud)
- **Logo SVG inline** dans navbar (pas de fichier externe pour fiabilité)
- **Catalogue : vue par blocs**, pas de DataFrame Streamlit
- **Édition de référence** : form séparé sous la vue lecture (pas d'édition inline car incompatible avec rendu HTML custom)

---

## 10. Déploiement

**Repo GitHub :** https://github.com/anto19plas-source/zaiko (public)
**Streamlit Cloud :** URL configurée par l'utilisateur sur share.streamlit.io
**App pointe sur :** `app.py`, branche `main`

**Workflow :**
1. Modifier le code localement
2. `git add -A && git commit -m "..." && git push`
3. Streamlit Cloud redéploie automatiquement (~2 min)

**Note sur le re-seed :** la DB SQLite est éphémère sur Streamlit Cloud (le conteneur recrée `zaiko.db` à chaque redémarrage). Le seed ne se redéclenche QUE si la table `restaurants` est vide. Si après un push une mise à jour du catalogue ne s'affiche pas, faire **Reboot app** depuis Manage app sur Streamlit Cloud pour forcer un nouveau démarrage propre.

**Lancement local :**
```bash
cd "Desktop/CODE ZAIKO"
streamlit run app.py
# → http://localhost:8501
```

---

## 11. Préférences utilisateur (importantes)

- **Communication en français**
- **Toujours proposer une approche AVANT de coder**, attendre validation
- **Après validation et fin du codage : push direct sur `origin/main` sans test local** (l'utilisateur valide via Streamlit Cloud, pas en local) — voir mémoire `feedback_zaiko_workflow.md`
- **Vérifier qu'il n'y a pas d'erreurs après modification** (`python3 -m py_compile`)
- **Pas d'emojis dans l'app finale** (charte stricte)
- **Style "professionnel, métier d'abord, calme, posé"** (cf BRAND.md §6)
- **Ne PAS utiliser** : "révolutionnaire", "game-changer", références asiatiques visuelles, néons, gradients flashy

---

## 12. Pour reprendre la session

**Premier message à donner à la nouvelle session Claude :**

> Salut, je reprends Zaiko. Lis `/Users/plasantonin/Desktop/CODE ZAIKO/CONTEXT.md` pour avoir l'état actuel.
>
> La prochaine étape est dans le §8 : refondre la saisie d'inventaire pour les restaurants. Voici la nouvelle structure que je veux : [SPEC À COMPLÉTER PAR L'UTILISATEUR].
>
> Avant de coder, propose-moi ton approche en respectant strictement la charte (§3) et tout ce qui a déjà été fait.

---

*Document mis à jour le 30 avril 2026 — fin de session après import du catalogue réel WAC + page Évolution des prix.*
