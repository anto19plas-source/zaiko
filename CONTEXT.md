# Zaiko — Contexte de session pour reprise

> Ce document résume l'état actuel du projet Zaiko.
> À donner à une nouvelle session Claude pour reprendre proprement.

*Dernière mise à jour : 4 mai 2026 — session « audit + cleanup mort code + bugs/sécurité + UX + décisions auth/caisse ».*

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
| 1 | Chéri Chéri | Restaurant italien | `#D89593` (rose pêche) | `cheri_cheri` |
| 2 | Chéri Guapito | Tapas espagnol | `#B23A2A` (rouge) | `guapito` |
| 3 | Chéri Guapo | Tapas espagnol | `#7A2A22` (bordeaux) | `guapo` |
| 4 | Les Halles de la Cité | Corner food | `#C9A24B` (gold) | `halles` |

> Sur Streamlit Cloud, la table `restaurants` n'est seedée qu'à la création de la DB. Après tout changement de types/noms : **Reboot app** depuis Manage app pour repartir d'une DB neuve.

---

## 5. Architecture de navigation (à jour)

**Navbar fixe** (76px de haut, brand → accueil) avec dropdowns :
```
ZAIKO | Groupe WAC ▾ | Chéri Chéri ▾ | Chéri Guapito ▾ | Chéri Guapo ▾ | Les Halles ▾
```

**Dropdown Groupe WAC :** Dashboard · Catalogue · Évolution des prix
*(Fiches techniques supprimé — fonction `render_groupe_fiches` et route `?page=groupe_fiches` retirées du code.)*

**Dropdown chaque restaurant (×4) :** Dashboard · Inventaire · Historique inventaire · Performance · Fiches techniques
*(Mouvements supprimé — fonction `render_resto_mouvements`, route `_mouvements`, table `mouvements`, helpers `add_mouvement` / `get_mouvements` retirés du code.)*
*(Ancienne route `?page={key}_ventes` conservée en alias vers Performance, pour compat bookmarks.)*

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
| Inventaire | Saisie inline par lieu (bar/réserve) — clôture via selectbox 12 derniers mois |
| Historique inventaire | Snapshots mensuels figés + export CSV |
| Performance | Sélecteur période (semaine/mois/trim/an) + blocs CA & Ratios + export CSV |
| Fiches techniques | Cocktails / plats avec calcul ratio/coefficient |
| ~~Mouvements~~ | **supprimé du code** (mort code retiré) |
| ~~Ventes & Ratios~~ | renommé `Performance`, route `_ventes` reste en alias |

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

**Bouton "Clôturer le mois"** en bas → crée un snapshot figé. Le mois se choisit via un **selectbox des 12 derniers mois** avec libellés français (« Mai 2026 »…) — plus de saisie texte regex. La clôture est **transactionnelle** (BEGIN/COMMIT/rollback) : un crash en cours d'écriture ne perd plus l'ancien snapshot.

### 8.3 Performance restaurant (ex « Ventes & Ratios »)

**Renommée** `Performance` dans la nav, code dans `render_resto_performance` (app.py). Route `?page={key}_performance`. Ancienne route `?page={key}_ventes` conservée en alias silencieux.

**Sélecteur de période unique** en haut de page (selectbox) — partagé pour CA + Ratios :
- `Semaine en cours` (lun → dim)
- `Mois en cours` (défaut, 1er → fin du mois)
- `Trimestre en cours` (Q1/Q2/Q3/Q4 calendaire)
- `Année en cours` (1er janvier → 31 décembre)

Helper central : `_periode_dates(label, today)` → `(debut, fin, debut_prev, fin_prev)` en bornes incluses, gère bascules d'année (janvier → déc préc., Q1 → Q4 préc., etc.).

**Récupération données** : `db.get_ventes_periode(rid, debut, fin)` (nouvelle fonction) — bornes incluses début et fin.

**Bloc Chiffre d'affaires** : 3 KPIs
- CA période + libellé `dd/mm/yyyy → dd/mm/yyyy`
- Δ vs période précédente (%) — coloré success/red
- CA cumulé année (YTD)
- Chart Plotly aire en couleur d'accent du resto

**Bloc Ratios** : 3 KPIs + chart + tableau
- Ratio matière (= CA réel / CA théorique × 100), seuils success ≥95% / gold ≥85% / red sinon
- Δ vs période précédente (en points)
- Écart cumulé en €
- Chart théorique (pointillés rule) vs réel (couleur d'accent)
- Tableau détail par jour (date, CA réel, CA théorique, ratio, écart)

**Saisie CA quotidienne** conservée en bas (form date + CA réel + CA théorique manuel + note), fonction `db.add_vente` inchangée.

> Note : le CA théorique reste **saisi à la main**. Décision produit du 4 mai 2026 : la caisse utilisée par WAC est **Cashpad**, mais le propriétaire **ne souhaite pas brancher l'API Cashpad** — il préfère saisir lui-même les quelques données nécessaires. Le lien automatique `fiches_techniques × ventes` (chantier 3 de l'audit) est donc reporté/abandonné dans sa forme « import caisse » ; granularité de saisie à préciser quand on y reviendra.

> **Export CSV** disponible sur le tableau Date / CA réel / CA théo / Ratio / Écart, fichier nommé `performance_{resto}_{debut}_{fin}.csv`.

### 8.4 Historique inventaire (snapshots mensuels)

**Tables** : `inventaires_mensuels` (id, restaurant_id, mois `YYYY-MM`, date_cloture, valeur_totale, nb_refs, notes) + `inventaire_mensuel_lignes` (id, inventaire_mensuel_id, produit_id, lieu, quantite, **prix_snapshot**).

**Prix figé** au moment de la clôture pour que la valorisation historique reste juste même si les prix bougent ensuite.

**Clôture** (`db.cloturer_inventaire_mois`) : copie toutes les lignes inventaire courant avec quantité > 0 du resto. Si snapshot du même mois existe déjà → **écrasement** (suppression puis re-création).

**Vue principale** : 4 KPIs valorisation (valeur dernier inventaire · variation vs M-1 · nb refs · moyenne 3 mois) + liste des snapshots.

**Détail d'un mois** : KPIs + tableau complet par catégorie avec qté bar/réserve, prix figé, valeur. **Chaque produit est cliquable** vers son détail snapshotté. **Export CSV** disponible (séparateur `;`, BOM UTF-8 → ouvre direct dans Excel français).

**Détail produit dans snapshot** : 4 KPIs (qté bar, qté réserve, total, valeur figée) + note rappelant que les prix sont figés au jour de clôture.

---

## 9. Bugs corrigés

**Audit interne du 2 mai 2026 :**
- **DB** : suppression de `upsert_inventaire` (mort code, cassait `UNIQUE` sur lieu).
- **DB** : `get_kpis_groupe` agrège correctement les alertes par (resto, produit) avec `HAVING SUM(qte) > 0` (plus de doublons).
- `_save_qte_callback` notifie via `st.toast` au lieu d'avaler les exceptions.
- Keys de saisie inline préfixées par le filtre lieu (évite collision Tous/Bar/Réserve).
- `query_params.update()` (compat Streamlit récent).
- Validation mois clôture par regex stricte `^\d{4}-(0[1-9]|1[0-2])$` *(remplacée par selectbox le 4 mai)*.
- Garde `if not f` dans `render_fiche_editor` si fiche supprimée concurremment.
- `_cleanup_state_on_nav()` central : purge des états `viewing_*` / `editing_*` au changement de page.
- Warning visuel si une fiche technique contient des ingrédients à prix=0.
- Short name resto : troncature dynamique (`nom[:16] + "…"`) au lieu du hardcode "Les Halles".

**Audit + cleanup du 4 mai 2026 :**
- **Mort code retiré** : `render_resto_mouvements`, `render_groupe_fiches`, `add_mouvement`, `get_mouvements`, table `mouvements`, `TYPE_MV_COLORS`, colonne `emoji` (table `categories`), import `re` devenu inutile.
- **`cloturer_inventaire_mois` atomique** : tout dans `BEGIN/COMMIT` avec `rollback` en cas d'exception. Avant, un crash entre DELETE et INSERT perdait l'ancien snapshot sans en écrire de nouveau.
- **`add_vente` validé en API** : refuse les montants négatifs et > 1 000 000 € (avant, `min_value=0` côté UI pouvait être contourné en appel direct). `ValueError` attrapée et affichée proprement dans le formulaire Performance.
- **Ratio matière borné sur 30 jours** dans `get_kpis_groupe` et `get_kpis_resto`. Avant, `AVG` sur toutes les ventes depuis la création → KPI gelé après quelques mois.

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

## 12 bis. Décisions produit en attente d'implémentation (4 mai 2026)

Suite à l'audit priorisé du 4 mai, 3 chantiers structurants ont été identifiés. Les décisions produit ont été prises mais l'implémentation est différée :

### Chantier 1 — Persistance DB
**Statut : non décidé.** La DB SQLite est éphémère sur Streamlit Cloud (purgée à chaque reboot). À migrer vers **Supabase / Turso / Neon** (Postgres free tier). Décision en attente.

### Chantier 2 — Authentification (décidé)
**Modèle retenu :** 5 comptes au total
- **1 compte propriétaire/créateur** (Antonin) — accès complet : Groupe WAC + les 4 restos
- **4 comptes directeur** (un par resto) — accès uniquement à leur établissement (et probablement Groupe WAC en lecture seule, à préciser au moment de l'implémentation)

Implémentation à faire avec `streamlit-authenticator` (config YAML hashée bcrypt) + table `users` (id, email, role, restaurants_autorisés). Filtrage du routing dans `route()` selon le rôle. À implémenter après / en même temps que le chantier 1 (la persistance DB est un prérequis pour stocker les comptes).

### Chantier 3 — Source des ventes (décidé)
**Caisse utilisée :** Cashpad.
**Décision propriétaire :** **pas d'intégration API Cashpad**. Le propriétaire saisit lui-même les données nécessaires. Le CA théorique reste donc en saisie manuelle (formulaire Performance).

Granularité de saisie à préciser le moment venu :
- **Option A (actuelle)** : saisie quotidienne d'un CA réel + CA théorique chiffré.
- **Option B** : saisie quotidienne des **quantités vendues par fiche technique** → calcul auto du CA théorique à partir des fiches existantes. Plus précis et plus utile métier, mais plus de saisie quotidienne.

À débattre quand on relance ce chantier.

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

**Session du 4 mai 2026 — soir (commits `cd12b65` → `7e53d75`)**

Audit priorisé du projet via agent `general-purpose`, puis 3 commits autonomes :

- **`cd12b65` — Nettoyage mort code** : suppression de la page Mouvements (déjà retirée de la nav) — `render_resto_mouvements`, route `_mouvements`, `db.add_mouvement`, `db.get_mouvements`, table `mouvements`, `TYPE_MV_COLORS`. Suppression du placeholder `render_groupe_fiches` + route `groupe_fiches`. Suppression de la colonne `emoji` de `categories` (toujours seedée à `""`, charte interdit).

- **`d09f970` — Bugs et sécurité** : `cloturer_inventaire_mois` atomique (BEGIN/COMMIT + rollback). `add_vente` valide les montants côté DB (refuse négatifs, refuse > 1 000 000 €), `ValueError` affichée dans le formulaire. `get_kpis_groupe` et `get_kpis_resto` bornent le ratio matière sur 30 jours glissants (au lieu de toutes les ventes depuis la création).

- **`7e53d75` — Quality of life inventaire et performance** : clôture mensuelle via `selectbox` des 12 derniers mois avec libellés français (« Mai 2026 »…) à la place du `text_input` + regex. Erreur de clôture désormais affichée à l'utilisateur. Export CSV (séparateur `;`, BOM UTF-8) sur la page Performance et sur le détail snapshot. Suppression de l'import `re` inutilisé.

**Décisions produit prises pendant cette session** (cf §12 bis) :
- **Auth** : modèle 1 propriétaire + 4 directeurs (un par resto), à implémenter après la migration DB.
- **Caisse** : Cashpad, mais pas d'intégration API — saisie manuelle conservée.
- **Persistance DB** : non décidée (Supabase / Turso / Neon à choisir).

> Reboot Streamlit Cloud nécessaire après ce push pour seed la nouvelle structure DB (sans colonne `emoji` ni table `mouvements`).

---

**Session du 4 mai 2026 — matin (commit `90a9273`)**

- **`90a9273` — Refonte page Performance + maj types restos** :
  - **Types restos mis à jour** dans `RESTAURANTS_CONFIG` (`database.py:8-13`) et seed (`database.py:151-156`) : Chéri Chéri = `Restaurant italien`, Chéri Guapito = `Tapas espagnol`, Chéri Guapo = `Tapas espagnol`, Les Halles = `Corner food`.
  - **Onglet `Ventes & Ratios` renommé `Performance`** (`RESTO_NAV` dans `app.py`). Route `_performance`, ancienne route `_ventes` conservée en alias.
  - **Nouvelle fonction DB** `get_ventes_periode(rid, debut, fin)` (`database.py`).
  - **Helper période** `_periode_dates(label, today)` couvrant les 4 périodes calendaires + leur précédente, avec gestion bascules d'année.
  - **`render_resto_performance(resto)`** : sélecteur unique en haut, bloc CA (3 KPIs + chart aire), bloc Ratios (3 KPIs + chart théo/réel + tableau), saisie quotidienne conservée.
  - Reboot Streamlit Cloud nécessaire pour seed les nouveaux types dans `restaurants`.

---

**Session du 2 mai 2026 (commits `137f3fb` → `c9de1ad`)**

- **`684d77e` — Évolution des prix** : refonte complète de `render_groupe_prix()`. Vue principale (4 KPIs + tableau résumé par produit + filtres) et fiche prix dédiée (KPIs, courbe, historique chronologique). Pattern session_state `viewing_price_product_id`.

- **`a2ed4d8` — Refonte visuelle navbar + accueil + catalogue** : navbar 60→76px, logo agrandi, page d'accueil avec hero navy-deep + slogan Fraunces, séparateurs `zk-cat-sep` dans le catalogue.

- **`137f3fb` — Fiches techniques par restaurant** : 2 nouvelles tables, parsing unités, calcul ratio/coefficient, TVA 20% cocktail / 10% plat, UI éditeur avec ingrédients en liste éditable + 5 KPIs (coût brut, coût+perte, prix HT, ratio, coefficient).

- **`ebeb077` — Refonte inventaires + historique** : ajout colonne `lieu` à inventaire (bar/réserve), saisie inline (Option B), `set_inventaire_ligne` avec callback on_change, page Historique inventaire avec 4 KPIs valorisation, snapshots mensuels figés (`inventaires_mensuels` + `inventaire_mensuel_lignes`), détail mois → détail produit cliquable. "Mouvements" retiré de la nav.

- **`c9de1ad` — Bugfixes audit + DA renforcée** : 10 bugs corrigés (mort code, agrégation alertes, callback silent, keys collision, regex mois, garde fiche supprimée, cleanup states, warning prix=0, etc.) + identité visuelle renforcée (wordmark Inter 700, hero avec motif barres, cards restos avec mini-pictogrammes, banner avec motif d'accent, footer brand).

---

*Document mis à jour le 4 mai 2026 (soir) — projet Zaiko commercialisable, charte appliquée strictement, modules complets, audit du 4 mai exécuté (cleanup mort code + bugs/sécurité + UX) et décisions produit prises pour les chantiers persistance / auth / caisse.*
