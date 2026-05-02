# Zaiko — Contexte de session pour reprise

> Ce document résume l'état actuel du projet Zaiko.
> À donner à une nouvelle session Claude pour reprendre proprement.

*Dernière mise à jour : 2 mai 2026 — fin de session « refonte inventaires + DA renforcée + audit bugs ».*

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
**Repo** : https://github.com/anto19plas-source/zaiko

---

## 2. Structure du projet

```
/Users/plasantonin/Desktop/CODE ZAIKO/
├── app.py                  # App Streamlit (~3000 lignes, toutes les pages)
├── database.py             # Couche SQLite + seed (~870 lignes)
├── seed_data.py            # Catalogue WAC réel : 33 catégories + 729 produits
├── base prix wac .xlsx     # Source Excel du catalogue (gitignored, local only)
├── requirements.txt        # streamlit, pandas, plotly
├── .streamlit/config.toml  # Thème Streamlit aligné brand
├── .gitignore
├── handoff/                # ASSETS BRAND OFFICIELS — référence absolue
│   ├── BRAND.md            # Spec brand complète (palette, typo, voix)
│   ├── tokens.css / tokens.ts
│   ├── components.tsx
│   ├── tailwind.config.js
│   ├── logo.svg / logo-dark.svg / app-icon.svg / favicon.svg / logo.tsx
└── ZAIKO/Logo ZAIKO.zip
```

---

## 3. Charte graphique — règles strictes (rappel)

**Palette officielle :** Ink `#0B1220` · Navy `#0F2A4A` · Navy deep `#081A2F` · Navy soft `#1B3558` · Gold `#C9A24B` · Gold light `#E3C275` · Gold deep `#A8862F` · Red `#B23A2A` · Bone `#F4EFE6` · Paper `#FAF7F1` · Rule `#E2D9C7` · Muted `#54688A` · Success `#2A6F4F`.

**Ratio cible 60/30/8/2** : 60% Navy/Ink · 30% Paper/Bone · 8% Gold (rare) · 2% Red (alerte uniquement).

**Règles strictes :**
- Doré jamais en aplat dominant
- Rouge ne touche jamais le doré
- Pas de gradients flashy (sauf le radial subtil de l'app icon)
- **Aucun emoji** — couleurs et formes uniquement
- **Wordmark Inter 700** (et non 600), letter-spacing -0.04em
- Métaphore visuelle : barres horizontales empilées = niveaux de stock

**Typographie :**
- **Inter** — UI, wordmark, labels, boutons
- **Fraunces** — display, citations italiques uniquement
- **JetBrains Mono** — données, eyebrows uppercase tracking 0.28em, métriques

---

## 4. Restaurants du Groupe WAC

| ID | Nom | Type | Couleur d'accent | Clé URL |
|---|---|---|---|---|
| 1 | Chéri Chéri | Bar à cocktails | `#D89593` (rose pêche) | `cheri_cheri` |
| 2 | Chéri Guapito | Restaurant mexicain | `#B23A2A` (rouge) | `guapito` |
| 3 | Chéri Guapo | Restaurant argentin | `#7A2A22` (bordeaux) | `guapo` |
| 4 | Les Halles de la Cité | Brasserie | `#C9A24B` (gold) | `halles` |

---

## 5. Architecture de navigation (à jour)

**Navbar fixe** (76px de haut, brand → accueil) avec dropdowns :
```
ZAIKO | Groupe WAC ▾ | Chéri Chéri ▾ | Chéri Guapito ▾ | Chéri Guapo ▾ | Les Halles ▾
```

**Dropdown Groupe WAC :** Dashboard · Catalogue · Évolution des prix
*(Fiches techniques retiré — code conservé, route `?page=groupe_fiches` accessible mais cachée)*

**Dropdown chaque restaurant (×4) :** Dashboard · Inventaire · Historique inventaire · Ventes & Ratios · Fiches techniques
*(Mouvements retiré — code conservé, route `?page={key}_mouvements` accessible mais cachée)*

**Routing :** `st.query_params["page"]`. Page par défaut = `accueil`. Format `?page={key}_{section}` ou `?page=groupe_{section}`.

Au changement de page, `_cleanup_state_on_nav()` purge automatiquement les états résidentiels (`viewing_*`, `editing_*`).

---

## 6. État actuel des modules

### Page d'accueil (`?page=accueil`, défaut)
- **Hero block navy-deep** avec motif barres en filigrane gold (métaphore niveaux de stock), eyebrow `Groupe WAC · 4 établissements`, logo Zaiko grand format (Inter 700), filet gold, baseline `« Le stock bouge. Zaiko s'adapte. »` en Fraunces italic 30px.
- **4 cartes restaurants** : eyebrow `Établissement N`, mini-pictogramme barres en couleur d'accent, nom Inter 700 17px, type en mono, CTA `Accéder →`.
- **3 accès rapides Groupe WAC** : Catalogue · Prix · Vue consolidée — fond navy, flèche gold animée au hover.
- **Footer brand** minimal : wordmark + filet + baseline italic.

### Groupe WAC

#### Dashboard
KPIs · tableau résumé restos · chart CA consolidé 30j. **Stable.**

#### Catalogue (refondu, version interactive)
- Barre de filtres : recherche · catégorie · conditionnement
- Vue par catégorie : barre header navy/gold + lignes produits en colonnes Streamlit + **`zk-cat-sep` après chaque groupe** (séparation visuelle).
- Clic sur "Ouvrir" → fiche produit (`render_fiche_produit`) avec édition complète, suppression confirmée, courbe d'évolution + lien vers détail prix.
- Section "Ajouter un produit" en bas. Pas de seuil d'alerte à la création.

#### Évolution des prix (refondue)
- Vue principale : 4 KPIs (refs concernées · total changements · dernière modif · variation moyenne) + filtres texte/catégorie + tableau résumé par produit (prix initial → actuel, variation %, nb modifs, date, bouton Détail).
- Fiche prix : retour, page header, 4 KPIs (prix initial, actuel, variation totale, nb changements), courbe Plotly navy/gold shape=hv, historique chronologique HTML.

#### Fiches techniques (Groupe — caché, code conservé)
Placeholder. Le module a été déplacé par restaurant.

### Pages restaurant (×4)

| Page | État |
|---|---|
| Dashboard | KPIs + chart 14j + alertes (agrégées par produit) |
| Inventaire | **Refondu — saisie inline par lieu (bar/réserve)** |
| Historique inventaire | **NOUVEAU — snapshots mensuels figés** |
| Ventes & Ratios | KPIs + courbe réel/théorique + form saisie |
| Fiches techniques | **NOUVEAU — cocktails / plats avec calcul ratio/coefficient** |
| ~~Mouvements~~ | retiré de la nav, route encore disponible par URL |

---

## 7. Catalogue produits — données réelles

- **729 références**, **33 catégories** dans `seed_data.py`, issues de `base prix wac .xlsx`.
- Magnums conservés en catégories séparées.
- Format `bouteille` par défaut quand non précisé.
- 15 refs en `prix à définir` (affichées en rouge dans le catalogue) — à compléter via la fiche produit.

`FORMATS_PREDEFINIS` (étendu pour boissons) :
- `bouteille` (par défaut)
- **cl** : 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 20, 25, 33, 35, 37.5, 40, 44, 48.5, 50, 60, 66, 70, 75, 100, 150
- **L** : 1, 1.25, 1.5, 2, 3, 5, 10, 15, 20, 25, 30, 50
- **g/kg** : 100g, 150g, 200g, 250g, 500g, 750g, 1kg, 1.5kg, 2kg, 3kg, 5kg, 10kg
- **génériques** : pièce, lot, carton, douzaine, barquette

---

## 8. Modules détaillés (nouveautés)

### 8.1 Fiches techniques par restaurant

**Tables** : `fiches_techniques` (id, restaurant_id, type ['cocktail'|'plat'], nom, prix_vente_ttc, tva, notes, dates) + `fiche_ingredients` (id, fiche_id, produit_id, quantite, unite_recette, ordre).

**Logique de conversion** (`parse_unite_catalogue` dans app.py) :
- `"75cl"` → 75 cl · `"1L"` → 100 cl · `"1.5kg"` → 1500 g · `"500g"` → 500 g
- `bouteille`, `pièce`, `lot`, `carton`, `douzaine`, `barquette` → 1 pièce

**Coût ingrédient** (`cout_ingredient`) : `prix × qté_recette / qté_format` dans la même dimension. Renvoie `None` si dimensions incompatibles (ex: g pour produit en cl) → affichage `"unité incompatible"`.

**Indicateurs** (5 KPIs affichés) :
- Coût matière brut
- Coût + 10% perte (réaliste)
- Prix HT = `TTC / (1 + TVA/100)`
- **Ratio matière** = `coût+perte / prix_HT × 100` (en %, brut, sans seuil/couleur)
- **Coefficient** = `prix_HT / coût+perte` (multiplicateur ×N.NN)

**TVA par défaut** : 20% cocktail, 10% plat (modifiable par fiche).

**Liaison catalogue** : on stocke uniquement `produit_id`, donc tout changement de prix dans le catalogue est répercuté **automatiquement** dans toutes les fiches qui utilisent cette référence.

**Warning visuel** si une fiche contient des ingrédients à `prix_unitaire = 0`.

### 8.2 Inventaire par lieu (saisie inline)

**Lieux fixes : `bar` et `reserve`** (2 colonnes éditables par produit).

**Table `inventaire`** modifiée : ajout de la colonne `lieu` + contrainte `UNIQUE (restaurant_id, produit_id, lieu)`. Migration douce via `ALTER TABLE` pour les DB existantes.

**Saisie pratique (Option B retenue)** : 2 number_inputs visibles dans chaque ligne de la liste (Bar / Réserve), sauvegarde automatique on_change vers la DB (callback `_save_qte_callback`). Toast affiché en cas d'erreur DB.

**4 KPIs en haut de page** : nb références en stock · valeur totale · alertes (sous seuil) · dernière saisie.

**Filtres** : recherche + catégorie + lieu (Tous / Bar uniquement / Réserve uniquement). Quand on filtre sur un seul lieu, l'autre est affiché en lecture seule.

**Fiche stock dédiée** (clic sur "Fiche") : 3 KPIs (stock total, valeur, état OK/Alerte), form Bar/Réserve avec notes par lieu.

**Bouton "Clôturer le mois"** en bas → crée un snapshot figé.

### 8.3 Historique inventaire (snapshots mensuels)

**Tables** : `inventaires_mensuels` (id, restaurant_id, mois `YYYY-MM`, date_cloture, valeur_totale, nb_refs, notes) + `inventaire_mensuel_lignes` (id, inventaire_mensuel_id, produit_id, lieu, quantite, **prix_snapshot**).

**Prix figé** au moment de la clôture pour que la valorisation historique reste juste même si les prix bougent ensuite.

**Clôture** (`db.cloturer_inventaire_mois`) : copie toutes les lignes inventaire courant avec quantité > 0 du resto. Si snapshot du même mois existe déjà → **écrasement** (suppression puis re-création).

**Vue principale** : 4 KPIs valorisation (valeur dernier inventaire · variation vs M-1 · nb refs · moyenne 3 mois) + liste des snapshots.

**Détail d'un mois** : KPIs + tableau complet par catégorie avec qté bar/réserve, prix figé, valeur. **Chaque produit est cliquable** vers son détail snapshotté.

**Détail produit dans snapshot** : 4 KPIs (qté bar, qté réserve, total, valeur figée) + note rappelant que les prix sont figés au jour de clôture.

---

## 9. Bugs corrigés (audit interne du 2 mai 2026)

- **DB** : suppression de `upsert_inventaire` (mort code, cassait `UNIQUE` sur lieu).
- **DB** : `get_kpis_groupe` agrège correctement les alertes par (resto, produit) avec `HAVING SUM(qte) > 0` (plus de doublons).
- `_save_qte_callback` notifie via `st.toast` au lieu d'avaler les exceptions.
- Keys de saisie inline préfixées par le filtre lieu (évite collision Tous/Bar/Réserve).
- `query_params.update()` (compat Streamlit récent).
- Validation mois clôture par regex stricte `^\d{4}-(0[1-9]|1[0-2])$`.
- Garde `if not f` dans `render_fiche_editor` si fiche supprimée concurremment.
- `_cleanup_state_on_nav()` central : purge des états `viewing_*` / `editing_*` au changement de page.
- Warning visuel si une fiche technique contient des ingrédients à prix=0.
- Short name resto : troncature dynamique (`nom[:16] + "…"`) au lieu du hardcode "Les Halles".

---

## 10. Renforts identité visuelle (DA)

Charte handoff/ appliquée plus strictement :
- **Wordmark Inter 700** (et non 600) dans tous les SVG, conformément à BRAND.md.
- **Hero accueil** : motif barres décoratif en filigrane gold (métaphore niveaux de stock), eyebrow gold uppercase tracking 0.32em, filet gold sous le logo, baseline en Fraunces italic 30px.
- **Cards restaurants** : eyebrow `Établissement N`, mini-pictogramme barres en couleur d'accent, hover plus marqué (translate Y -3px, border gold subtle).
- **Cards Outils Groupe** : flèche gold animée au hover, sub-text descriptif sous chaque CTA.
- **Banner restaurants** : motif barres en filigrane en couleur d'accent du resto, eyebrow `Établissement`, titre 30px tracking -0.025em, ombre douce.
- **Footer brand minimal** sur l'accueil : wordmark + filet + baseline italic.

CSS classes principales ajoutées : `.zk-hero-eyebrow`, `.zk-hero-rule`, `.zk-home-card-mini`, `.zk-home-card-eyebrow`, `.zk-home-access::after`, `.zk-resto-motif`, `.zk-resto-eyebrow`, `.zk-footer*`, `.zk-warn-line`, `.zk-cat-sep`, `.zk-fiches-head`, `.zk-fiches-ing-head`, `.zk-inv-head`, `.zk-inv-snap-head`.

---

## 11. Décisions UX/design clés prises

- Tabs internes vs scroll : navbar top avec dropdowns CSS (Linear/Vercel pattern)
- Chaque restaurant a son propre dropdown
- Sidebar Streamlit cachée
- KPI cards avec barre d'accent gauche 3px
- Banner restaurant : navy + barre d'accent latérale (pas de gradient) + motif barres en filigrane
- Routing par query params `?page=xxx`
- Logo SVG inline (Inter 700, métaphore barres de stock)
- Catalogue : vue par blocs avec séparateurs, pas de DataFrame
- Fiches techniques : 1 fichier par fiche, ingrédients en liste éditable
- Inventaire : saisie inline (Option B) directement dans la liste
- Historique : snapshot avec prix figé pour valorisation juste

---

## 12. Déploiement

**Repo GitHub :** https://github.com/anto19plas-source/zaiko (public)
**Streamlit Cloud :** URL configurée par l'utilisateur sur share.streamlit.io
**App pointe sur :** `app.py`, branche `main`

**Workflow :**
1. Modifier le code localement
2. `git add -A && git commit -m "..." && git push`
3. Streamlit Cloud redéploie automatiquement (~2 min)

**Reboot nécessaire** sur Streamlit Cloud après tout changement de schéma DB (Manage app → Reboot app), car la DB est éphémère mais peut conserver l'ancienne structure tant que le conteneur tourne.

**Lancement local :**
```bash
cd "Desktop/CODE ZAIKO"
streamlit run app.py
# → http://localhost:8501
```

---

## 13. Préférences utilisateur (importantes)

- **Communication en français**
- **Toujours proposer une approche AVANT de coder**, attendre validation
- **Après validation et fin du codage : push direct sur `origin/main` sans test local** (l'utilisateur valide via Streamlit Cloud, pas en local)
- **Vérifier qu'il n'y a pas d'erreurs après modification** (`python3 -m py_compile`)
- **Pas d'emojis dans l'app finale** (charte stricte)
- **Style "professionnel, métier d'abord, calme, posé"**
- **Ne PAS utiliser** : "révolutionnaire", "game-changer", références asiatiques visuelles, néons, gradients flashy

---

## 14. Pour reprendre la session

**Premier message à donner à la nouvelle session Claude :**

> Salut, je reprends Zaiko. Lis `/Users/plasantonin/Desktop/CODE ZAIKO/CONTEXT.md` pour avoir l'état actuel.
>
> Le projet est dans un état stable et commercialisable : page d'accueil avec hero brand fort, catalogue groupe, évolution des prix, et par restaurant : dashboard / inventaire (saisie inline par lieu bar+réserve) / historique inventaire (snapshots mensuels figés) / ventes & ratios / fiches techniques (cocktails+plats avec ratio et coefficient).
>
> Confirme-moi que tu as bien lu le CONTEXT, puis dis-moi sur quoi tu peux m'aider ensuite.

---

## 15. Journal de session (récap des dernières évolutions)

**Session du 2 mai 2026 (commits récents `137f3fb` → `c9de1ad`)**

- **`684d77e` — Évolution des prix** : refonte complète de `render_groupe_prix()`. Vue principale (4 KPIs + tableau résumé par produit + filtres) et fiche prix dédiée (KPIs, courbe, historique chronologique). Pattern session_state `viewing_price_product_id`.

- **`a2ed4d8` — Refonte visuelle navbar + accueil + catalogue** : navbar 60→76px, logo agrandi, page d'accueil avec hero navy-deep + slogan Fraunces, séparateurs `zk-cat-sep` dans le catalogue.

- **`137f3fb` — Fiches techniques par restaurant** : 2 nouvelles tables, parsing unités, calcul ratio/coefficient, TVA 20% cocktail / 10% plat, UI éditeur avec ingrédients en liste éditable + 5 KPIs (coût brut, coût+perte, prix HT, ratio, coefficient).

- **`ebeb077` — Refonte inventaires + historique** : ajout colonne `lieu` à inventaire (bar/réserve), saisie inline (Option B), `set_inventaire_ligne` avec callback on_change, page Historique inventaire avec 4 KPIs valorisation, snapshots mensuels figés (`inventaires_mensuels` + `inventaire_mensuel_lignes`), détail mois → détail produit cliquable. "Mouvements" retiré de la nav.

- **`c9de1ad` — Bugfixes audit + DA renforcée** : 10 bugs corrigés (mort code, agrégation alertes, callback silent, keys collision, regex mois, garde fiche supprimée, cleanup states, warning prix=0, etc.) + identité visuelle renforcée (wordmark Inter 700, hero avec motif barres, cards restos avec mini-pictogrammes, banner avec motif d'accent, footer brand).

---

*Document mis à jour le 2 mai 2026 — projet Zaiko commercialisable, charte appliquée strictement, modules complets.*
