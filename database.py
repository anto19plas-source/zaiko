import sqlite3
from datetime import date, timedelta
import random
from seed_data import CATEGORIES as SEED_CATEGORIES, PRODUITS as SEED_PRODUITS

DB_PATH = "zaiko.db"

RESTAURANTS_CONFIG = [
    {"id": 1, "nom": "Chéri Chéri",         "type": "Bar à cocktails",     "accent": "#D89593", "key": "cheri_cheri"},
    {"id": 2, "nom": "Chéri Guapito",        "type": "Restaurant mexicain", "accent": "#B23A2A", "key": "guapito"},
    {"id": 3, "nom": "Chéri Guapo",          "type": "Restaurant argentin", "accent": "#7A2A22", "key": "guapo"},
    {"id": 4, "nom": "Les Halles de la Cité","type": "Brasserie",           "accent": "#C9A24B", "key": "halles"},
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
            nom   TEXT NOT NULL,
            emoji TEXT
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
            id              INTEGER PRIMARY KEY,
            restaurant_id   INTEGER REFERENCES restaurants(id),
            produit_id      INTEGER REFERENCES produits(id),
            quantite        REAL    DEFAULT 0,
            date_saisie     TEXT,
            note            TEXT
        );

        CREATE TABLE IF NOT EXISTS mouvements (
            id              INTEGER PRIMARY KEY,
            restaurant_id   INTEGER REFERENCES restaurants(id),
            produit_id      INTEGER REFERENCES produits(id),
            type_mouvement  TEXT,
            quantite        REAL,
            date_mouvement  TEXT,
            note            TEXT
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
    """)

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
        (1, "Chéri Chéri",          "Bar à cocktails",     "#D89593", "Paris 11e"),
        (2, "Chéri Guapito",         "Restaurant mexicain", "#B23A2A", "Paris 2e"),
        (3, "Chéri Guapo",           "Restaurant argentin", "#7A2A22", "Paris 9e"),
        (4, "Les Halles de la Cité", "Brasserie",           "#C9A24B", "Paris 1er"),
    ])

    c.executemany("INSERT INTO categories (id, nom, emoji) VALUES (?,?,?)",
                  [(cid, nom, "") for cid, nom in SEED_CATEGORIES])

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
        SELECT p.*, c.nom AS categorie_nom, c.emoji AS categorie_emoji
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
               c.nom AS categorie_nom, c.emoji AS categorie_emoji
        FROM inventaire i
        JOIN produits p ON i.produit_id = p.id
        LEFT JOIN categories c ON p.categorie_id = c.id
        WHERE i.restaurant_id = ?
        ORDER BY c.nom, p.nom
    """, (restaurant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_alertes(restaurant_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.*, p.nom AS produit_nom, p.unite, p.seuil_alerte
        FROM inventaire i
        JOIN produits p ON i.produit_id = p.id
        WHERE i.restaurant_id = ? AND i.quantite <= p.seuil_alerte
        ORDER BY i.quantite ASC
    """, (restaurant_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_mouvements(restaurant_id, limit=50):
    conn = get_connection()
    rows = conn.execute("""
        SELECT m.*, p.nom AS produit_nom, p.unite
        FROM mouvements m
        JOIN produits p ON m.produit_id = p.id
        WHERE m.restaurant_id = ?
        ORDER BY m.date_mouvement DESC, m.id DESC
        LIMIT ?
    """, (restaurant_id, limit)).fetchall()
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


def get_kpis_groupe():
    conn = get_connection()
    nb_produits = conn.execute("SELECT COUNT(*) FROM produits WHERE actif=1").fetchone()[0]
    nb_alertes = conn.execute("""
        SELECT COUNT(*) FROM inventaire i
        JOIN produits p ON i.produit_id = p.id
        WHERE i.quantite <= p.seuil_alerte
    """).fetchone()[0]
    since_7j = (date.today() - timedelta(days=7)).isoformat()
    ca_semaine = conn.execute(
        "SELECT COALESCE(SUM(montant_reel),0) FROM ventes WHERE date_vente >= ?",
        (since_7j,)
    ).fetchone()[0]
    ratio_row = conn.execute(
        "SELECT AVG(CAST(montant_reel AS REAL)/montant_theorique) FROM ventes WHERE montant_theorique > 0"
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
    nb_articles = conn.execute(
        "SELECT COUNT(*) FROM inventaire WHERE restaurant_id=?", (restaurant_id,)
    ).fetchone()[0]
    nb_alertes = conn.execute("""
        SELECT COUNT(*) FROM inventaire i
        JOIN produits p ON i.produit_id = p.id
        WHERE i.restaurant_id=? AND i.quantite <= p.seuil_alerte
    """, (restaurant_id,)).fetchone()[0]
    since_7j = (date.today() - timedelta(days=7)).isoformat()
    ca_7j = conn.execute(
        "SELECT COALESCE(SUM(montant_reel),0) FROM ventes WHERE restaurant_id=? AND date_vente>=?",
        (restaurant_id, since_7j)
    ).fetchone()[0]
    ratio_row = conn.execute(
        "SELECT AVG(CAST(montant_reel AS REAL)/montant_theorique) FROM ventes WHERE restaurant_id=? AND montant_theorique>0",
        (restaurant_id,)
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

def upsert_inventaire(restaurant_id, produit_id, quantite, note=""):
    conn = get_connection()
    exists = conn.execute(
        "SELECT id FROM inventaire WHERE restaurant_id=? AND produit_id=?",
        (restaurant_id, produit_id)
    ).fetchone()
    if exists:
        conn.execute(
            "UPDATE inventaire SET quantite=?, date_saisie=?, note=? WHERE restaurant_id=? AND produit_id=?",
            (quantite, date.today().isoformat(), note or None, restaurant_id, produit_id)
        )
    else:
        conn.execute(
            "INSERT INTO inventaire (restaurant_id, produit_id, quantite, date_saisie, note) VALUES (?,?,?,?,?)",
            (restaurant_id, produit_id, quantite, date.today().isoformat(), note or None)
        )
    conn.commit()
    conn.close()


def add_mouvement(restaurant_id, produit_id, type_mouvement, quantite, note=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO mouvements (restaurant_id, produit_id, type_mouvement, quantite, date_mouvement, note) VALUES (?,?,?,?,?,?)",
        (restaurant_id, produit_id, type_mouvement, quantite, date.today().isoformat(), note or None)
    )
    conn.commit()
    conn.close()


def add_vente(restaurant_id, date_vente, montant_reel, montant_theorique, note=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO ventes (restaurant_id, date_vente, montant_reel, montant_theorique, note) VALUES (?,?,?,?,?)",
        (restaurant_id, str(date_vente), montant_reel, montant_theorique, note or None)
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
