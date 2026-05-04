import sqlite3
from datetime import date, timedelta
import random
from seed_data import CATEGORIES as SEED_CATEGORIES, PRODUITS as SEED_PRODUITS

DB_PATH = "zaiko.db"

RESTAURANTS_CONFIG = [
    {"id": 1, "nom": "Chéri Chéri",         "type": "Restaurant italien", "accent": "#D89593", "key": "cheri_cheri"},
    {"id": 2, "nom": "Chéri Guapito",        "type": "Tapas espagnol",     "accent": "#B23A2A", "key": "guapito"},
    {"id": 3, "nom": "Chéri Guapo",          "type": "Tapas espagnol",     "accent": "#7A2A22", "key": "guapo"},
    {"id": 4, "nom": "Les Halles de la Cité","type": "Corner food",        "accent": "#C9A24B", "key": "halles"},
]


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id              INTEGER PRIMARY KEY,
            nom             TEXT NOT NULL,
            type            TEXT,
            couleur_accent  TEXT,
            adresse         TEXT
        );

        CREATE TABLE IF NOT EXISTS categories (
            id    INTEGER PRIMARY KEY,
            nom   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS produits (
            id              INTEGER PRIMARY KEY,
            nom             TEXT NOT NULL,
            categorie_id    INTEGER REFERENCES categories(id),
            unite           TEXT    DEFAULT 'unité',
            prix_unitaire   REAL    DEFAULT 0,
            seuil_alerte    REAL    DEFAULT 5,
            actif           INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS inventaire (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id   INTEGER REFERENCES restaurants(id),
            produit_id      INTEGER REFERENCES produits(id),
            lieu            TEXT    DEFAULT 'reserve',
            quantite        REAL    DEFAULT 0,
            date_saisie     TEXT,
            note            TEXT,
            UNIQUE (restaurant_id, produit_id, lieu)
        );

        CREATE TABLE IF NOT EXISTS ventes (
            id                  INTEGER PRIMARY KEY,
            restaurant_id       INTEGER REFERENCES restaurants(id),
            date_vente          TEXT,
            montant_reel        REAL,
            montant_theorique   REAL,
            note                TEXT
        );

        CREATE TABLE IF NOT EXISTS historique_prix (
            id                INTEGER PRIMARY KEY,
            produit_id        INTEGER REFERENCES produits(id),
            ancien_prix       REAL,
            nouveau_prix      REAL,
            date_changement   TEXT
        );

        CREATE TABLE IF NOT EXISTS fiches_techniques (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id   INTEGER NOT NULL REFERENCES restaurants(id),
            type            TEXT NOT NULL,
            nom             TEXT NOT NULL,
            prix_vente_ttc  REAL DEFAULT 0,
            tva             REAL DEFAULT 20,
            notes           TEXT DEFAULT '',
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS fiche_ingredients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            fiche_id        INTEGER NOT NULL REFERENCES fiches_techniques(id) ON DELETE CASCADE,
            produit_id      INTEGER NOT NULL REFERENCES produits(id),
            quantite        REAL NOT NULL,
            unite_recette   TEXT NOT NULL,
            ordre           INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS inventaires_mensuels (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id   INTEGER NOT NULL REFERENCES restaurants(id),
            mois            TEXT NOT NULL,
            date_cloture    TEXT NOT NULL,
            valeur_totale   REAL DEFAULT 0,
            nb_refs         INTEGER DEFAULT 0,
            notes           TEXT DEFAULT '',
            UNIQUE (restaurant_id, mois)
        );

        CREATE TABLE IF NOT EXISTS inventaire_mensuel_lignes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            inventaire_mensuel_id INTEGER NOT NULL REFERENCES inventaires_mensuels(id) ON DELETE CASCADE,
            produit_id      INTEGER NOT NULL REFERENCES produits(id),
            lieu            TEXT NOT NULL,
            quantite        REAL NOT NULL,
            prix_snapshot   REAL NOT NULL
        );
    """)

    # Migration douce : ajouter la colonne `lieu` si elle manque (DB existante)
    cols = [r[1] for r in c.execute("PRAGMA table_info(inventaire)").fetchall()]
    if "lieu" not in cols:
        c.execute("ALTER TABLE inventaire ADD COLUMN lieu TEXT DEFAULT 'reserve'")

    if not c.execute("SELECT 1 FROM restaurants LIMIT 1").fetchone():
        _seed(c)

    if not c.execute("SELECT 1 FROM historique_prix LIMIT 1").fetchone():
        today = date.today().isoformat()
        for p in c.execute("SELECT id, prix_unitaire FROM produits WHERE actif=1").fetchall():
            c.execute(
                "INSERT INTO historique_prix (produit_id, ancien_prix, nouveau_prix, date_changement) VALUES (?,?,?,?)",
                (p["id"], p["prix_unitaire"], p["prix_unitaire"], today)
            )

    conn.commit()
    conn.close()


def _seed(c):
    c.executemany("INSERT INTO restaurants VALUES (?,?,?,?,?)", [
        (1, "Chéri Chéri",          "Restaurant italien", "#D89593", "Paris 11e"),
        (2, "Chéri Guapito",         "Tapas espagnol",     "#B23A2A", "Paris 2e"),
        (3, "Chéri Guapo",           "Tapas espagnol",     "#7A2A22", "Paris 9e"),
        (4, "Les Halles de la Cité", "Corner food",        "#C9A24B", "Paris 1er"),
    ])

    c.executemany("INSERT INTO categories (id, nom) VALUES (?,?)",
                  list(SEED_CATEGORIES))

    c.executemany(
        "INSERT INTO produits (id, nom, categorie_id, unite, prix_unitaire, seuil_alerte, actif) VALUES (?,?,?,?,?,0,1)",
        [(pid, nom, cid, fmt, prix) for pid, nom, cid, fmt, prix in SEED_PRODUITS]
    )

    random.seed(42)
    today = date.today()

    nb_produits = len(SEED_PRODUITS)
    base_ca = {1: 2200, 2: 2800, 3: 3200, 4: 1800}
    v_id = 1
    for i in range(30):
        d = (today - timedelta(days=i)).isoformat()
        for r in range(1, 5):
            reel = round(base_ca[r] * random.uniform(0.70, 1.30), 2)
            theo = round(reel * random.uniform(0.82, 1.18), 2)
            c.execute("INSERT INTO ventes VALUES (?,?,?,?,?,?)",
                      (v_id, r, d, reel, theo, None))
            v_id += 1


# ─── Read ────────────────────────────────────────────────────────────────────

def get_restaurants():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM restaurants ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY nom").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_produits(categorie_id=None):
    conn = get_connection()
    q = """
        SELECT p.*, c.nom AS categorie_nom
        FROM produits p
        LEFT JOIN categories c ON p.categorie_id = c.id
        WHERE p.actif = 1
    """
    params = []
    if categorie_id:
        q += " AND p.categorie_id = ?"
        params.append(categorie_id)
    q += " ORDER BY c.nom, p.nom"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_inventaire(restaurant_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.*, p.nom AS produit_nom, p.unite, p.seuil_alerte, p.prix_unitaire,
               c.nom AS categorie_nom
        FROM inventaire i
        JOIN produits p ON i.produit_id = p.id
        LEFT JOIN categories c ON p.categorie_id = c.id
        WHERE i.restaurant_id = ?
        ORDER BY c.nom, p.nom
    """, (restaurant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_alertes(restaurant_id):
    """Alertes par produit (somme sur tous les lieux), seuil non atteint."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            p.id              AS produit_id,
            p.nom             AS produit_nom,
            p.unite           AS unite,
            p.seuil_alerte    AS seuil_alerte,
            SUM(i.quantite)   AS quantite
        FROM inventaire i
        JOIN produits p ON i.produit_id = p.id
        WHERE i.restaurant_id = ? AND p.actif = 1
        GROUP BY p.id
        HAVING SUM(i.quantite) > 0 AND SUM(i.quantite) < p.seuil_alerte
        ORDER BY SUM(i.quantite) ASC
    """, (restaurant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ventes(restaurant_id, days=30):
    conn = get_connection()
    since = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT * FROM ventes
        WHERE restaurant_id = ? AND date_vente >= ?
        ORDER BY date_vente ASC
    """, (restaurant_id, since)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ventes_periode(restaurant_id, date_debut, date_fin):
    """Ventes d'un resto entre deux dates incluses (objets date ou ISO strings)."""
    d_iso = date_debut.isoformat() if hasattr(date_debut, "isoformat") else date_debut
    f_iso = date_fin.isoformat()   if hasattr(date_fin,   "isoformat") else date_fin
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM ventes
        WHERE restaurant_id = ?
          AND date_vente >= ?
          AND date_vente <= ?
        ORDER BY date_vente ASC
    """, (restaurant_id, d_iso, f_iso)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_kpis_groupe():
    conn = get_connection()
    nb_produits = conn.execute("SELECT COUNT(*) FROM produits WHERE actif=1").fetchone()[0]
    # Alertes agrégées par (resto, produit) — somme tous lieux confondus
    nb_alertes = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT i.restaurant_id, p.id
            FROM inventaire i
            JOIN produits p ON i.produit_id = p.id
            WHERE p.actif = 1
            GROUP BY i.restaurant_id, p.id
            HAVING SUM(i.quantite) > 0 AND SUM(i.quantite) < p.seuil_alerte
        )
    """).fetchone()[0]
    since_7j = (date.today() - timedelta(days=7)).isoformat()
    ca_semaine = conn.execute(
        "SELECT COALESCE(SUM(montant_reel),0) FROM ventes WHERE date_vente >= ?",
        (since_7j,)
    ).fetchone()[0]
    since_30j = (date.today() - timedelta(days=30)).isoformat()
    ratio_row = conn.execute(
        "SELECT AVG(CAST(montant_reel AS REAL)/montant_theorique) FROM ventes "
        "WHERE montant_theorique > 0 AND date_vente >= ?",
        (since_30j,)
    ).fetchone()[0]
    conn.close()
    return {
        "nb_produits": nb_produits,
        "nb_alertes":  nb_alertes,
        "ca_semaine":  ca_semaine or 0,
        "ratio_moyen": (ratio_row or 1) * 100,
    }


def get_kpis_resto(restaurant_id):
    conn = get_connection()
    nb_articles = conn.execute("""
        SELECT COUNT(DISTINCT i.produit_id) FROM inventaire i
        JOIN produits p ON i.produit_id = p.id
        WHERE i.restaurant_id=? AND p.actif=1 AND i.quantite > 0
    """, (restaurant_id,)).fetchone()[0]
    nb_alertes = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT p.id FROM inventaire i
            JOIN produits p ON i.produit_id = p.id
            WHERE i.restaurant_id=? AND p.actif=1
            GROUP BY p.id
            HAVING SUM(i.quantite) > 0 AND SUM(i.quantite) < p.seuil_alerte
        )
    """, (restaurant_id,)).fetchone()[0]
    since_7j = (date.today() - timedelta(days=7)).isoformat()
    ca_7j = conn.execute(
        "SELECT COALESCE(SUM(montant_reel),0) FROM ventes WHERE restaurant_id=? AND date_vente>=?",
        (restaurant_id, since_7j)
    ).fetchone()[0]
    since_30j = (date.today() - timedelta(days=30)).isoformat()
    ratio_row = conn.execute(
        "SELECT AVG(CAST(montant_reel AS REAL)/montant_theorique) FROM ventes "
        "WHERE restaurant_id=? AND montant_theorique>0 AND date_vente>=?",
        (restaurant_id, since_30j)
    ).fetchone()[0]
    conn.close()
    return {
        "nb_articles": nb_articles,
        "nb_alertes":  nb_alertes,
        "ca_7j":       ca_7j or 0,
        "ratio":       (ratio_row or 1) * 100,
    }


def get_ventes_groupe_30j():
    conn = get_connection()
    since = (date.today() - timedelta(days=29)).isoformat()
    rows = conn.execute("""
        SELECT v.date_vente, SUM(v.montant_reel) AS total_reel,
               SUM(v.montant_theorique) AS total_theo,
               r.nom AS resto_nom
        FROM ventes v
        JOIN restaurants r ON v.restaurant_id = r.id
        WHERE v.date_vente >= ?
        GROUP BY v.date_vente, v.restaurant_id
        ORDER BY v.date_vente
    """, (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Write ───────────────────────────────────────────────────────────────────

def add_vente(restaurant_id, date_vente, montant_reel, montant_theorique, note=""):
    reel = float(montant_reel or 0)
    theo = float(montant_theorique or 0)
    if reel < 0 or theo < 0:
        raise ValueError("Les montants ne peuvent pas être négatifs.")
    if reel > 1_000_000 or theo > 1_000_000:
        raise ValueError("Montant aberrant (> 1 000 000 €).")
    conn = get_connection()
    conn.execute(
        "INSERT INTO ventes (restaurant_id, date_vente, montant_reel, montant_theorique, note) VALUES (?,?,?,?,?)",
        (restaurant_id, str(date_vente), reel, theo, note or None)
    )
    conn.commit()
    conn.close()


def add_produit(nom, categorie_id, unite, prix_unitaire, seuil_alerte):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO produits (nom, categorie_id, unite, prix_unitaire, seuil_alerte) VALUES (?,?,?,?,?)",
        (nom, categorie_id, unite, prix_unitaire, seuil_alerte)
    )
    new_id = cur.lastrowid
    conn.execute(
        "INSERT INTO historique_prix (produit_id, ancien_prix, nouveau_prix, date_changement) VALUES (?,?,?,?)",
        (new_id, prix_unitaire, prix_unitaire, date.today().isoformat())
    )
    conn.commit()
    conn.close()


def get_produit(produit_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT p.*, c.nom AS categorie_nom
        FROM produits p
        LEFT JOIN categories c ON p.categorie_id = c.id
        WHERE p.id = ?
    """, (produit_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_produit(produit_id, nom, categorie_id, unite, prix_unitaire):
    conn = get_connection()
    row = conn.execute("SELECT prix_unitaire FROM produits WHERE id=?", (produit_id,)).fetchone()
    ancien_prix = row["prix_unitaire"] if row else None
    conn.execute(
        "UPDATE produits SET nom=?, categorie_id=?, unite=?, prix_unitaire=? WHERE id=?",
        (nom, categorie_id, unite, prix_unitaire, produit_id)
    )
    if ancien_prix is not None and float(ancien_prix) != float(prix_unitaire):
        conn.execute(
            "INSERT INTO historique_prix (produit_id, ancien_prix, nouveau_prix, date_changement) VALUES (?,?,?,?)",
            (produit_id, ancien_prix, prix_unitaire, date.today().isoformat())
        )
    conn.commit()
    conn.close()


def archive_produit(produit_id):
    conn = get_connection()
    conn.execute("UPDATE produits SET actif=0 WHERE id=?", (produit_id,))
    conn.commit()
    conn.close()


def get_historique_prix(produit_id=None, limit=None):
    conn = get_connection()
    q = """
        SELECT h.*, p.nom AS produit_nom, p.unite, c.nom AS categorie_nom
        FROM historique_prix h
        JOIN produits p ON h.produit_id = p.id
        LEFT JOIN categories c ON p.categorie_id = c.id
    """
    params = []
    if produit_id:
        q += " WHERE h.produit_id = ?"
        params.append(produit_id)
    q += " ORDER BY h.date_changement DESC, h.id DESC"
    if limit:
        q += f" LIMIT {int(limit)}"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Fiches techniques ───────────────────────────────────────────────────────

def get_fiches(restaurant_id, type_filter=None):
    conn = get_connection()
    q = "SELECT * FROM fiches_techniques WHERE restaurant_id = ?"
    params = [restaurant_id]
    if type_filter:
        q += " AND type = ?"
        params.append(type_filter)
    q += " ORDER BY nom"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_fiche(fiche_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM fiches_techniques WHERE id = ?",
        (fiche_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_fiche_ingredients(fiche_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT fi.*, p.nom AS produit_nom, p.unite AS produit_unite,
               p.prix_unitaire, c.nom AS categorie_nom
        FROM fiche_ingredients fi
        JOIN produits p ON fi.produit_id = p.id
        LEFT JOIN categories c ON p.categorie_id = c.id
        WHERE fi.fiche_id = ?
        ORDER BY fi.ordre, fi.id
    """, (fiche_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_fiche(restaurant_id, type_fiche, nom, prix_vente_ttc, tva, notes):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO fiches_techniques
           (restaurant_id, type, nom, prix_vente_ttc, tva, notes, created_at, updated_at)
           VALUES (?,?,?,?,?,?, datetime('now'), datetime('now'))""",
        (restaurant_id, type_fiche, nom, prix_vente_ttc, tva, notes)
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_fiche(fiche_id, nom, prix_vente_ttc, tva, notes):
    conn = get_connection()
    conn.execute(
        """UPDATE fiches_techniques
           SET nom = ?, prix_vente_ttc = ?, tva = ?, notes = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (nom, prix_vente_ttc, tva, notes, fiche_id)
    )
    conn.commit()
    conn.close()


def delete_fiche(fiche_id):
    conn = get_connection()
    conn.execute("DELETE FROM fiche_ingredients WHERE fiche_id = ?", (fiche_id,))
    conn.execute("DELETE FROM fiches_techniques WHERE id = ?", (fiche_id,))
    conn.commit()
    conn.close()


def replace_fiche_ingredients(fiche_id, ingredients):
    """ingredients: list of dicts {produit_id, quantite, unite_recette}"""
    conn = get_connection()
    conn.execute("DELETE FROM fiche_ingredients WHERE fiche_id = ?", (fiche_id,))
    for ordre, ing in enumerate(ingredients):
        if ing.get("produit_id") is None:
            continue
        conn.execute(
            """INSERT INTO fiche_ingredients
               (fiche_id, produit_id, quantite, unite_recette, ordre)
               VALUES (?,?,?,?,?)""",
            (fiche_id, ing["produit_id"], float(ing.get("quantite", 0) or 0),
             ing.get("unite_recette", "pièce"), ordre)
        )
    conn.commit()
    conn.close()


# ─── Inventaire (par lieu : bar / reserve) ───────────────────────────────────

LIEUX_INVENTAIRE = ["bar", "reserve"]


def get_inventaire_resto(restaurant_id):
    """
    Retourne pour chaque produit du catalogue actif :
    {produit_id, nom, categorie_nom, unite, prix_unitaire, seuil_alerte,
     qte_bar, qte_reserve, qte_total, valeur, derniere_saisie, note}
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            p.id              AS produit_id,
            p.nom             AS nom,
            p.unite           AS unite,
            p.prix_unitaire   AS prix_unitaire,
            p.seuil_alerte    AS seuil_alerte,
            c.nom             AS categorie_nom,
            COALESCE(SUM(CASE WHEN i.lieu = 'bar'     THEN i.quantite END), 0) AS qte_bar,
            COALESCE(SUM(CASE WHEN i.lieu = 'reserve' THEN i.quantite END), 0) AS qte_reserve,
            COALESCE(SUM(i.quantite), 0) AS qte_total,
            MAX(i.date_saisie) AS derniere_saisie
        FROM produits p
        LEFT JOIN categories c ON p.categorie_id = c.id
        LEFT JOIN inventaire i ON i.produit_id = p.id AND i.restaurant_id = ?
        WHERE p.actif = 1
        GROUP BY p.id
        ORDER BY c.nom, p.nom
    """, (restaurant_id,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        prix = float(d.get("prix_unitaire") or 0)
        d["valeur"] = prix * float(d.get("qte_total") or 0)
        out.append(d)
    return out


def get_inventaire_produit(restaurant_id, produit_id):
    """Retourne {qte_bar, qte_reserve, note_bar, note_reserve} pour un produit."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT lieu, quantite, note FROM inventaire
        WHERE restaurant_id = ? AND produit_id = ?
    """, (restaurant_id, produit_id)).fetchall()
    conn.close()
    out = {"qte_bar": 0.0, "qte_reserve": 0.0, "note_bar": "", "note_reserve": ""}
    for r in rows:
        lieu = r["lieu"] or "reserve"
        if lieu == "bar":
            out["qte_bar"] = float(r["quantite"] or 0)
            out["note_bar"] = r["note"] or ""
        elif lieu == "reserve":
            out["qte_reserve"] = float(r["quantite"] or 0)
            out["note_reserve"] = r["note"] or ""
    return out


def set_inventaire_ligne(restaurant_id, produit_id, lieu, quantite, note=None):
    """Upsert d'une ligne d'inventaire pour un (resto, produit, lieu)."""
    if lieu not in LIEUX_INVENTAIRE:
        raise ValueError(f"Lieu invalide : {lieu}")
    conn = get_connection()
    today = date.today().isoformat()
    existing = conn.execute(
        "SELECT id, note FROM inventaire WHERE restaurant_id=? AND produit_id=? AND lieu=?",
        (restaurant_id, produit_id, lieu)
    ).fetchone()
    if existing:
        if note is None:
            conn.execute(
                "UPDATE inventaire SET quantite=?, date_saisie=? WHERE id=?",
                (float(quantite or 0), today, existing["id"])
            )
        else:
            conn.execute(
                "UPDATE inventaire SET quantite=?, date_saisie=?, note=? WHERE id=?",
                (float(quantite or 0), today, note, existing["id"])
            )
    else:
        conn.execute(
            """INSERT INTO inventaire (restaurant_id, produit_id, lieu, quantite, date_saisie, note)
               VALUES (?,?,?,?,?,?)""",
            (restaurant_id, produit_id, lieu, float(quantite or 0), today, note or "")
        )
    conn.commit()
    conn.close()


def get_kpis_inventaire(restaurant_id):
    """Retourne {nb_refs_en_stock, valeur_totale, nb_alertes, derniere_saisie}."""
    conn = get_connection()
    row = conn.execute("""
        SELECT
            SUM(CASE WHEN totaux.qte_total > 0 THEN 1 ELSE 0 END) AS nb_refs,
            COALESCE(SUM(totaux.qte_total * p.prix_unitaire), 0) AS valeur_totale,
            SUM(CASE WHEN totaux.qte_total > 0 AND totaux.qte_total < p.seuil_alerte THEN 1 ELSE 0 END) AS nb_alertes,
            MAX(totaux.derniere_saisie) AS derniere_saisie
        FROM (
            SELECT produit_id,
                   SUM(quantite) AS qte_total,
                   MAX(date_saisie) AS derniere_saisie
            FROM inventaire
            WHERE restaurant_id = ?
            GROUP BY produit_id
        ) totaux
        JOIN produits p ON p.id = totaux.produit_id
        WHERE p.actif = 1
    """, (restaurant_id,)).fetchone()
    conn.close()
    return {
        "nb_refs": int(row["nb_refs"] or 0),
        "valeur_totale": float(row["valeur_totale"] or 0),
        "nb_alertes": int(row["nb_alertes"] or 0),
        "derniere_saisie": row["derniere_saisie"] or "—",
    }


# ─── Inventaires mensuels (snapshots figés) ──────────────────────────────────

def cloturer_inventaire_mois(restaurant_id, mois):
    """
    Crée (ou écrase) un snapshot mensuel pour (resto, mois). 'mois' au format 'YYYY-MM'.
    Snapshot = copie de toutes les lignes inventaire courant avec prix unitaire figé.
    Retourne l'id du snapshot. Tout se fait dans une transaction unique :
    en cas d'échec, l'ancien snapshot est préservé.
    """
    conn = get_connection()
    today = date.today().isoformat()
    try:
        conn.execute("BEGIN")

        # Supprimer un snapshot existant pour ce mois (écrasement)
        existing = conn.execute(
            "SELECT id FROM inventaires_mensuels WHERE restaurant_id=? AND mois=?",
            (restaurant_id, mois)
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM inventaire_mensuel_lignes WHERE inventaire_mensuel_id=?", (existing["id"],))
            conn.execute("DELETE FROM inventaires_mensuels WHERE id=?", (existing["id"],))

        # Snapshot des lignes courantes (uniquement celles avec quantité > 0)
        lignes = conn.execute("""
            SELECT i.produit_id, i.lieu, i.quantite, p.prix_unitaire
            FROM inventaire i
            JOIN produits p ON p.id = i.produit_id
            WHERE i.restaurant_id = ? AND p.actif = 1 AND i.quantite > 0
        """, (restaurant_id,)).fetchall()

        valeur_totale = 0.0
        refs_set = set()
        for l in lignes:
            valeur_totale += float(l["quantite"] or 0) * float(l["prix_unitaire"] or 0)
            refs_set.add(l["produit_id"])

        cur = conn.execute(
            """INSERT INTO inventaires_mensuels (restaurant_id, mois, date_cloture, valeur_totale, nb_refs, notes)
               VALUES (?,?,?,?,?,'')""",
            (restaurant_id, mois, today, valeur_totale, len(refs_set))
        )
        snapshot_id = cur.lastrowid

        for l in lignes:
            conn.execute(
                """INSERT INTO inventaire_mensuel_lignes
                   (inventaire_mensuel_id, produit_id, lieu, quantite, prix_snapshot)
                   VALUES (?,?,?,?,?)""",
                (snapshot_id, l["produit_id"], l["lieu"] or "reserve",
                 float(l["quantite"] or 0), float(l["prix_unitaire"] or 0))
            )

        conn.commit()
        return snapshot_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_inventaires_mensuels(restaurant_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM inventaires_mensuels
        WHERE restaurant_id = ?
        ORDER BY mois DESC
    """, (restaurant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_inventaire_mensuel(snapshot_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM inventaires_mensuels WHERE id = ?",
        (snapshot_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_snapshot_lignes(snapshot_id):
    """
    Retourne les lignes d'un snapshot agrégées par produit, avec qté par lieu.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            l.produit_id,
            p.nom AS produit_nom,
            p.unite AS unite,
            c.nom AS categorie_nom,
            COALESCE(SUM(CASE WHEN l.lieu='bar'     THEN l.quantite END), 0) AS qte_bar,
            COALESCE(SUM(CASE WHEN l.lieu='reserve' THEN l.quantite END), 0) AS qte_reserve,
            SUM(l.quantite) AS qte_total,
            MAX(l.prix_snapshot) AS prix_snapshot,
            SUM(l.quantite * l.prix_snapshot) AS valeur
        FROM inventaire_mensuel_lignes l
        JOIN produits p ON p.id = l.produit_id
        LEFT JOIN categories c ON p.categorie_id = c.id
        WHERE l.inventaire_mensuel_id = ?
        GROUP BY l.produit_id
        ORDER BY c.nom, p.nom
    """, (snapshot_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_snapshot_produit(snapshot_id, produit_id):
    """Détail d'un produit dans un snapshot : qté par lieu, prix figé, valeur."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT lieu, quantite, prix_snapshot
        FROM inventaire_mensuel_lignes
        WHERE inventaire_mensuel_id = ? AND produit_id = ?
    """, (snapshot_id, produit_id)).fetchall()
    conn.close()
    out = {"qte_bar": 0.0, "qte_reserve": 0.0, "prix_snapshot": 0.0, "valeur": 0.0}
    for r in rows:
        lieu = r["lieu"] or "reserve"
        q = float(r["quantite"] or 0)
        out["prix_snapshot"] = float(r["prix_snapshot"] or 0)
        if lieu == "bar":
            out["qte_bar"] = q
        elif lieu == "reserve":
            out["qte_reserve"] = q
    out["qte_total"] = out["qte_bar"] + out["qte_reserve"]
    out["valeur"] = out["qte_total"] * out["prix_snapshot"]
    return out


def get_kpis_historique_inventaire(restaurant_id):
    """KPIs pour la page historique : valeur dernier, variation vs M-1, nb refs, moyenne 3M."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT mois, valeur_totale, nb_refs
        FROM inventaires_mensuels
        WHERE restaurant_id = ?
        ORDER BY mois DESC
        LIMIT 3
    """, (restaurant_id,)).fetchall()
    conn.close()

    snaps = [dict(r) for r in rows]
    if not snaps:
        return {"valeur_dernier": 0.0, "variation": None, "nb_refs": 0, "moyenne_3m": 0.0, "dernier_mois": None}
    dernier = snaps[0]
    variation = None
    if len(snaps) >= 2 and snaps[1]["valeur_totale"]:
        variation = (dernier["valeur_totale"] - snaps[1]["valeur_totale"]) / snaps[1]["valeur_totale"] * 100
    moyenne = sum(s["valeur_totale"] for s in snaps) / len(snaps)
    return {
        "valeur_dernier": float(dernier["valeur_totale"] or 0),
        "variation": variation,
        "nb_refs": int(dernier["nb_refs"] or 0),
        "moyenne_3m": float(moyenne),
        "dernier_mois": dernier["mois"],
    }
