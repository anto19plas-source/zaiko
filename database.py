import sqlite3
from datetime import date, timedelta
import random

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
    """)

    if not c.execute("SELECT 1 FROM restaurants LIMIT 1").fetchone():
        _seed(c)

    conn.commit()
    conn.close()


def _seed(c):
    c.executemany("INSERT INTO restaurants VALUES (?,?,?,?,?)", [
        (1, "Chéri Chéri",          "Bar à cocktails",     "#D89593", "Paris 11e"),
        (2, "Chéri Guapito",         "Restaurant mexicain", "#B23A2A", "Paris 2e"),
        (3, "Chéri Guapo",           "Restaurant argentin", "#7A2A22", "Paris 9e"),
        (4, "Les Halles de la Cité", "Brasserie",           "#C9A24B", "Paris 1er"),
    ])

    c.executemany("INSERT INTO categories VALUES (?,?,?)", [
        (1, "Alcools",          ""),
        (2, "Soft & Jus",       ""),
        (3, "Viandes",          ""),
        (4, "Légumes",          ""),
        (5, "Produits laitiers",""),
        (6, "Épicerie",         ""),
    ])

    c.executemany("INSERT INTO produits VALUES (?,?,?,?,?,?,1)", [
        (1,  "Gin Hendricks",          1, "bouteille", 28.50,  3),
        (2,  "Vodka Grey Goose",       1, "bouteille", 32.00,  3),
        (3,  "Rum Bacardi",            1, "bouteille", 18.50,  5),
        (4,  "Whisky Monkey Shoulder", 1, "bouteille", 24.00,  3),
        (5,  "Champagne Billecart",    1, "bouteille", 45.00,  6),
        (6,  "Jus d'orange frais",     2, "litre",      4.50, 10),
        (7,  "Sirop de sucre",         2, "litre",      3.00,  5),
        (8,  "Coca-Cola 33cl",         2, "bouteille",  1.50, 24),
        (9,  "Bœuf haché",             3, "kg",        12.00,  5),
        (10, "Poulet fermier",         3, "kg",         8.50,  8),
        (11, "Tomates cerises",        4, "kg",         4.00,  5),
        (12, "Avocat",                 4, "pièce",      1.20, 20),
        (13, "Comté 18 mois",          5, "kg",        22.00,  2),
        (14, "Crème fraîche",          5, "litre",      3.50,  5),
        (15, "Sel de mer",             6, "kg",         2.00,  2),
    ])

    random.seed(42)
    today = date.today()

    inv_id = 1
    for r in range(1, 5):
        for p in range(1, 16):
            qty = round(random.uniform(1, 40), 1)
            c.execute("INSERT INTO inventaire VALUES (?,?,?,?,?,?)",
                      (inv_id, r, p, qty, today.isoformat(), None))
            inv_id += 1

    types_mv = ["entrée", "sortie", "perte", "transfert"]
    for mv_id in range(1, 101):
        d = (today - timedelta(days=random.randint(0, 30))).isoformat()
        c.execute("INSERT INTO mouvements VALUES (?,?,?,?,?,?,?)", (
            mv_id, random.randint(1, 4), random.randint(1, 15),
            random.choice(types_mv), round(random.uniform(1, 12), 1), d, None,
        ))

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
    conn.execute(
        "INSERT INTO produits (nom, categorie_id, unite, prix_unitaire, seuil_alerte) VALUES (?,?,?,?,?)",
        (nom, categorie_id, unite, prix_unitaire, seuil_alerte)
    )
    conn.commit()
    conn.close()
