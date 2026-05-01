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

#### Catalogue (refondu, version interactive)
- **Barre de filtres** en haut : recherche texte (nom) · catégorie · conditionnement, options dynamiques basées sur le contenu réel
- **Vue par catégorie** : pour chaque catégorie, une barre header navy/gold (titre + count) suivie des lignes produits en colonnes Streamlit
- **Chaque ligne produit** : `nom · conditionnement · prix · bouton "Ouvrir"`
- **Clic sur "Ouvrir"** → ouvre la **fiche produit** (via `st.session_state.editing_product_id`)
- **Fiche produit** (`render_fiche_produit`) : header avec page_header dédié, form édition (nom, catégorie, conditionnement, prix), boutons "Valider les modifications" / "Supprimer la référence" (avec checkbox de confirmation), aperçu courbe Plotly de l'évolution des prix de la ref + bouton vers le détail complet
- **Bouton "← Retour au catalogue"** en haut de la fiche
- **Section "Ajouter un produit"** en bas du catalogue : form simplifié, pas de seuil d'alerte
- **15 refs en "prix à définir"** affichées en rouge — à compléter manuellement par l'utilisateur via la fiche produit
- L'ancienne section "Modifier une référence" avec selectbox a été **supprimée** (remplacée par le clic depuis le catalogue)

`FORMATS_PREDEFINIS` (étendu pour boissons) :
- `bouteille` (par défaut)
- **cl** : 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 20, 25, 33, 35, 37.5, 40, 44, 48.5, 50, 60, 66, 70, 75, 100, 150
- **L** : 1, 1.25, 1.5, 2, 3, 5, 10, 15, 20, 25, 30, 50
- **g/kg** : 100g, 150g, 200g, 250g, 500g, 750g, 1kg, 1.5kg, 2kg, 3kg, 5kg, 10kg
- **génériques** : pièce, lot, carton, douzaine, barquette

#### Évolution des prix (à refondre — voir §8)
**État actuel (à remplacer) :**
- Routing : `?page=groupe_prix`
- Table SQLite `historique_prix` (produit_id, ancien_prix, nouveau_prix, date_changement)
- Log automatique à chaque changement de prix (via `db.update_produit()`)
- Au démarrage : seed un point d'ancrage par produit existant si la table est vide
- 3 KPIs : nb total de changements · dernière modification · variation moyenne (%)
- Selectbox "Toutes les références" ou une seule
- Si une réf : courbe Plotly (ligne navy + points gold) + tableau des changements
- Sinon : tableau des 30 derniers changements
- Variations en rouge (hausse) / success (baisse) / muted (flat)

**À refondre :** structure plus lisible et exploitable, vue tableau résumé par produit (avec n° de modifs, prix initial → prix actuel, variation totale), clic sur un produit → fiche prix dédiée avec courbe + détail chronologique. CSS pour cette refonte est déjà en place (`zk-prix-head`, `zk-prix-name`, `zk-fiche-price-block`, `zk-fiche-price-row`, etc.).

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

## 8. Prochaines étapes

### 8.1 — Refonte page Évolution des prix (immédiat)

**À faire dans la prochaine session.** L'utilisateur a validé l'approche, le CSS est déjà ajouté, **seule la fonction `render_groupe_prix()` reste à réécrire** dans `app.py`.

**Spec de la refonte :**

1. **Vue principale** (par défaut) : page lisible avec
   - 4 KPIs : références concernées (qui ont changé de prix) · total des changements · dernière modification · variation moyenne
   - **Tableau résumé par produit** : une ligne par référence ayant changé de prix, avec colonnes :
     - Référence (nom)
     - Catégorie · Format
     - Évolution `prix_initial € → prix_actuel €`
     - Variation totale (%) — en rouge si hausse, success si baisse
     - Nombre de changements
     - Date dernière modif
     - Bouton **"Détail"** par ligne
   - Filtres en haut : recherche texte + filtre catégorie
   - Tri par défaut : dernière modification (plus récent en haut)

2. **Clic sur "Détail"** → ouvre la **fiche prix** d'un produit (via `st.session_state.viewing_price_product_id`) :
   - Bouton "← Retour à l'évolution des prix"
   - `page_header` avec nom du produit + catégorie · format
   - 4 KPIs : prix initial · prix actuel · variation totale · nombre de changements
   - **Courbe Plotly** ligne navy + points gold (shape="hv" pour les paliers)
   - **Détail chronologique** : tableau HTML avec date · évolution `ancien → nouveau` · variation % — utiliser les classes CSS `zk-fiche-price-block`, `zk-fiche-price-head`, `zk-fiche-price-row` déjà ajoutées

3. **Cohérence avec le catalogue** : reprendre exactement le même pattern de routing par session_state que la fiche produit du catalogue, avec un bouton retour clair

**Code de référence :** voir `render_fiche_produit()` dans `app.py` (pattern session_state + bouton retour + page_header) — la fiche prix doit suivre la même structure.

### 8.2 — Refonte saisie inventaire restaurants (plus tard)

L'utilisateur a annoncé qu'il veut changer la structure de saisie d'inventaire pour chaque restaurant. **La spec exacte sera donnée plus tard**, après validation de la refonte des prix. Voir `app.py:render_resto_inventaire()` pour le code actuel (tableau filtrable + form de saisie classique).

Quand la spec arrive : **proposer l'approche AVANT de coder**, attendre validation, puis implémenter et pousser sur GitHub directement.

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
> La prochaine étape est §8.1 : refondre la page **Évolution des prix**. La spec est dans le CONTEXT, le CSS est déjà en place, il reste juste à réécrire `render_groupe_prix()` dans `app.py` selon la spec.
>
> Avant de coder, confirme-moi que tu as bien lu la spec §8.1 et le pattern `render_fiche_produit()` qui sert de référence. Pousse sur `main` directement après codage.

---

## 13. Journal de session (récap des dernières évolutions)

**Session du 30 avril 2026 (commit `73b551e`) — Refonte catalogue + fiche produit**
- `FORMATS_PREDEFINIS` étendu (toutes mesures bar 1-8cl, standards boissons 15/20/35/40/44/60/66/70cl, fûts 15/25/50L, magnums 100/150cl, formats solides complets, génériques douzaine/barquette)
- Catalogue refondu : barre catégorie navy/gold + lignes produits en colonnes Streamlit avec bouton "Ouvrir" sur chaque ligne
- Nouvelle fonction `render_fiche_produit()` : édition complète d'une référence (nom, catégorie, conditionnement, prix), suppression avec checkbox de confirmation, aperçu courbe d'évolution des prix + lien vers le détail complet
- Pattern `st.session_state.editing_product_id` pour le routing fiche/catalogue
- Suppression de l'ancienne section "Modifier une référence" avec selectbox
- CSS ajouté pour la refonte de la page prix (`.zk-prix-*`, `.zk-fiche-price-*`) — pas encore utilisé
- **Reste à faire :** réécrire `render_groupe_prix()` selon spec §8.1

---

*Document mis à jour le 1ᵉʳ mai 2026 — fin de session après refonte catalogue + fiche produit cliquable.*
