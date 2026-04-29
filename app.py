import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import database as db

# ─── Config ──────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Zaiko",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Constants ───────────────────────────────────────────────────────────────

NAVY   = "#1C2B4A"
GOLD   = "#C9A84C"
RED    = "#C0392B"
PAPER  = "#F5F0E8"
BONE   = "#E8E0D0"

RESTAURANTS = db.RESTAURANTS_CONFIG

GROUPE_NAV = [
    ("groupe_dashboard", "Dashboard"),
    ("groupe_catalogue", "Catalogue"),
    ("groupe_fiches",    "Fiches techniques"),
]

RESTO_NAV = [
    ("dashboard",   "Dashboard"),
    ("inventaire",  "Inventaire"),
    ("mouvements",  "Mouvements"),
    ("ventes",      "Ventes & Ratios"),
]

TYPE_MV_COLORS = {
    "entrée":    "#2D8A4E",
    "sortie":    "#1C2B4A",
    "perte":     "#C0392B",
    "transfert": "#C9A84C",
}


# ─── CSS ─────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;1,9..144,300&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --navy:        #1C2B4A;
        --navy-mid:    #243354;
        --navy-deep:   #162238;
        --gold:        #C9A84C;
        --gold-lt:     #E4C97A;
        --red:         #C0392B;
        --paper:       #F5F0E8;
        --bone:        #E8E0D0;
        --txt:         #1C1C1C;
        --txt-muted:   #6B6860;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; }
    html, body, .stApp { background: var(--paper) !important; font-family: 'Inter', sans-serif; color: var(--txt); }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer { display: none !important; }
    [data-testid="stSidebar"]          { display: none !important; }
    [data-testid="stToolbar"]          { display: none !important; }
    .stDeployButton                    { display: none !important; }
    [data-testid="stDecoration"]       { display: none !important; }
    [data-testid="stStatusWidget"]     { display: none !important; }
    header[data-testid="stHeader"]     { display: none !important; }

    /* ── Main padding (below fixed navbar) ── */
    .main .block-container {
        padding-top:    72px  !important;
        padding-left:   36px  !important;
        padding-right:  36px  !important;
        max-width:      1360px !important;
    }

    /* ═══════════════════════════════════════
       NAVBAR
    ═══════════════════════════════════════ */
    .z-nav {
        position:      fixed;
        top: 0; left: 0; right: 0;
        z-index:       9999;
        height:        52px;
        background:    var(--navy);
        display:       flex;
        align-items:   center;
        padding:       0 24px;
        gap:           0;
        border-bottom: 1px solid rgba(201,168,76,.12);
        box-shadow:    0 1px 0 rgba(0,0,0,.15), 0 2px 12px rgba(0,0,0,.12);
    }

    .z-wordmark {
        font-family:     'Fraunces', serif;
        font-size:       17px;
        font-weight:     700;
        letter-spacing:  3.5px;
        text-transform:  uppercase;
        color:           var(--gold);
        text-decoration: none;
        flex-shrink:     0;
        margin-right:    28px;
        line-height:     1;
    }

    .z-sep {
        width:      1px;
        height:     18px;
        background: rgba(245,240,232,.08);
        flex-shrink: 0;
    }

    /* Each nav group (trigger + dropdown) */
    .z-group {
        position:    relative;
        height:      52px;
        display:     flex;
        align-items: center;
    }

    .z-trigger {
        display:      flex;
        align-items:  center;
        gap:          6px;
        padding:      4px 10px;
        border-radius: 6px;
        color:        rgba(245,240,232,.60);
        font-size:    12.5px;
        font-weight:  500;
        font-family:  'Inter', sans-serif;
        white-space:  nowrap;
        cursor:       default;
        transition:   color .12s, background .12s;
        user-select:  none;
    }

    .z-group:hover .z-trigger {
        color:      rgba(245,240,232,.92);
        background: rgba(245,240,232,.06);
    }

    .z-trigger.z-active {
        color: var(--gold) !important;
    }

    .z-dot {
        width:         7px;
        height:        7px;
        border-radius: 50%;
        flex-shrink:   0;
        display:       inline-block;
    }

    .z-chevron {
        font-size:  9px;
        opacity:    .45;
        transition: transform .15s, opacity .15s;
        margin-left: 1px;
    }
    .z-group:hover .z-chevron {
        transform: rotate(180deg);
        opacity:   .75;
    }

    /* Dropdown panel */
    .z-dropdown {
        position:      absolute;
        top:           48px;
        left:          0;
        background:    var(--navy-deep);
        border:        1px solid rgba(201,168,76,.18);
        border-radius: 10px;
        padding:       5px;
        min-width:     188px;
        opacity:       0;
        pointer-events: none;
        transform:     translateY(-6px);
        transition:    opacity .14s ease, transform .14s ease;
        box-shadow:    0 16px 48px rgba(0,0,0,.5), 0 2px 8px rgba(0,0,0,.25);
    }
    .z-group:hover .z-dropdown {
        opacity:        1;
        pointer-events: all;
        transform:      translateY(0);
    }

    .z-dropdown a {
        display:       flex;
        align-items:   center;
        gap:           8px;
        padding:       7px 10px;
        border-radius: 6px;
        color:         rgba(245,240,232,.60);
        font-size:     12.5px;
        font-weight:   400;
        font-family:   'Inter', sans-serif;
        text-decoration: none;
        transition:    color .1s, background .1s;
    }
    .z-dropdown a:hover {
        color:      rgba(245,240,232,.92);
        background: rgba(255,255,255,.05);
    }
    .z-dropdown a.z-link-active {
        color:       var(--gold);
        background:  rgba(201,168,76,.09);
        font-weight: 500;
    }

    .z-section-label {
        color:          rgba(245,240,232,.22);
        font-size:      10px;
        font-weight:    600;
        letter-spacing: .9px;
        text-transform: uppercase;
        padding:        6px 10px 2px;
        font-family:    'Inter', sans-serif;
    }
    .z-dropdown hr {
        border:        none;
        border-top:    1px solid rgba(255,255,255,.06);
        margin:        4px 0;
    }

    /* ═══════════════════════════════════════
       PAGE HEADER
    ═══════════════════════════════════════ */
    .ph-wrap {
        padding:       20px 0 24px;
        border-bottom: 1px solid var(--bone);
        margin-bottom: 28px;
    }
    .ph-eyebrow {
        font-size:      10.5px;
        font-weight:    600;
        letter-spacing: 1.4px;
        text-transform: uppercase;
        color:          var(--gold);
        margin-bottom:  6px;
    }
    .ph-title {
        font-family: 'Fraunces', serif;
        font-size:   30px;
        font-weight: 700;
        color:       var(--navy);
        line-height: 1.1;
    }
    .ph-sub {
        font-size:   13.5px;
        color:       var(--txt-muted);
        margin-top:  4px;
    }
    .ph-quote {
        font-family: 'Fraunces', serif;
        font-style:  italic;
        font-size:   13px;
        color:       var(--txt-muted);
        margin-top:  2px;
    }

    /* ═══════════════════════════════════════
       KPI CARDS
    ═══════════════════════════════════════ */
    .kpi-card {
        background:    white;
        border:        1px solid var(--bone);
        border-radius: 12px;
        padding:       20px 22px;
        transition:    border-color .15s, box-shadow .15s;
        height:        100%;
    }
    .kpi-card:hover {
        border-color: rgba(201,168,76,.30);
        box-shadow:   0 4px 18px rgba(28,43,74,.07);
    }
    .kpi-label {
        font-size:      10.5px;
        font-weight:    600;
        letter-spacing: .7px;
        text-transform: uppercase;
        color:          var(--txt-muted);
        margin-bottom:  10px;
    }
    .kpi-value {
        font-family:  'JetBrains Mono', monospace;
        font-size:    26px;
        font-weight:  500;
        color:        var(--navy);
        line-height:  1;
    }
    .kpi-sub {
        font-size:  12px;
        color:      var(--txt-muted);
        margin-top: 7px;
    }
    .badge { border-radius: 4px; padding: 2px 7px; font-size: 11px; font-weight: 600; }
    .badge-ok   { color: #2D8A4E; background: #E7F5EE; }
    .badge-warn { color: #B5621B; background: #FEF3E8; }
    .badge-bad  { color: #C0392B; background: #FDECEB; }

    /* ═══════════════════════════════════════
       SECTION TITLE
    ═══════════════════════════════════════ */
    .section-title {
        font-size:      11px;
        font-weight:    600;
        letter-spacing: .8px;
        text-transform: uppercase;
        color:          var(--txt-muted);
        padding-bottom: 10px;
        border-bottom:  1px solid var(--bone);
        margin-bottom:  16px;
        margin-top:     32px;
    }

    /* ═══════════════════════════════════════
       ALERT ROWS
    ═══════════════════════════════════════ */
    .alert-row {
        display:       flex;
        align-items:   center;
        gap:           10px;
        background:    #FDECEB;
        border:        1px solid rgba(192,57,43,.15);
        border-radius: 8px;
        padding:       10px 14px;
        font-size:     13px;
        color:         var(--red);
        margin-bottom: 6px;
    }
    .alert-row strong { color: #962D22; }

    /* ═══════════════════════════════════════
       RESTO HEADER BANNER
    ═══════════════════════════════════════ */
    .resto-banner {
        border-radius: 14px;
        padding:       22px 28px;
        margin-bottom: 24px;
        display:       flex;
        align-items:   center;
        gap:           20px;
    }
    .resto-emoji-big {
        font-size:   40px;
        line-height: 1;
    }
    .resto-banner-name {
        font-family: 'Fraunces', serif;
        font-size:   26px;
        font-weight: 700;
        color:       white;
        line-height: 1.1;
    }
    .resto-banner-type {
        font-size:  13px;
        color:      rgba(255,255,255,.65);
        margin-top: 3px;
    }

    /* ═══════════════════════════════════════
       TABLES / DATAFRAMES
    ═══════════════════════════════════════ */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

    /* ═══════════════════════════════════════
       FORMS
    ═══════════════════════════════════════ */
    [data-testid="stForm"] {
        background:    white;
        border:        1px solid var(--bone) !important;
        border-radius: 12px !important;
        padding:       20px !important;
    }

    /* ═══════════════════════════════════════
       BUTTONS
    ═══════════════════════════════════════ */
    .stButton > button {
        background:    var(--navy) !important;
        color:         var(--paper) !important;
        border:        none !important;
        border-radius: 7px !important;
        font-family:   'Inter', sans-serif !important;
        font-size:     13px !important;
        font-weight:   500 !important;
        padding:       8px 20px !important;
        transition:    background .15s !important;
    }
    .stButton > button:hover {
        background: #243354 !important;
    }

    /* ═══════════════════════════════════════
       MISC
    ═══════════════════════════════════════ */
    ::-webkit-scrollbar              { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track        { background: transparent; }
    ::-webkit-scrollbar-thumb        { background: var(--bone); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover  { background: #ccc; }

    /* Tabs (internal) */
    [data-testid="stTabs"] [role="tablist"] {
        gap: 0;
        border-bottom: 1px solid var(--bone);
    }
    [data-testid="stTabs"] button[role="tab"] {
        font-family:   'Inter', sans-serif !important;
        font-size:     13px !important;
        font-weight:   500 !important;
        color:         var(--txt-muted) !important;
        padding:       10px 18px !important;
        border-radius: 0 !important;
        border:        none !important;
        background:    transparent !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color:         var(--navy) !important;
        border-bottom: 2px solid var(--navy) !important;
        font-weight:   600 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─── Navbar ──────────────────────────────────────────────────────────────────

def render_navbar(current_page: str):
    def _active(page_id):
        return "z-link-active" if current_page == page_id else ""

    def _trigger_active(prefix):
        return "z-active" if current_page.startswith(prefix) else ""

    # Groupe WAC links
    groupe_links = "\n".join(
        f'<a href="?page={pid}" class="{_active(pid)}"><span>◈</span>{label}</a>'
        for pid, label in GROUPE_NAV
    )

    # Per-restaurant dropdowns
    resto_blocks = ""
    for r in RESTAURANTS:
        key    = r["key"]
        accent = r["accent"]
        emoji  = r["emoji"]
        nom    = r["nom"]

        links = "\n".join(
            f'<a href="?page={key}_{sid}" class="{_active(key+"_"+sid)}">'
            f'<span style="color:{accent};font-size:8px;">●</span>{label}</a>'
            for sid, label in RESTO_NAV
        )

        is_active = _trigger_active(key + "_")
        # Short display name for nav (avoid overflow on "Les Halles de la Cité")
        short_nom = nom if len(nom) <= 14 else nom[:13] + "…"

        resto_blocks += f"""
        <div class="z-sep"></div>
        <div class="z-group">
            <div class="z-trigger {is_active}">
                <span class="z-dot" style="background:{accent}"></span>
                {emoji} {short_nom}
                <span class="z-chevron">▾</span>
            </div>
            <div class="z-dropdown">{links}</div>
        </div>"""

    st.markdown(f"""
    <nav class="z-nav">
        <a class="z-wordmark" href="?page=groupe_dashboard">ZAIKO</a>
        <div class="z-group">
            <div class="z-trigger {_trigger_active('groupe_')}">
                ◈ Groupe WAC
                <span class="z-chevron">▾</span>
            </div>
            <div class="z-dropdown">{groupe_links}</div>
        </div>
        {resto_blocks}
    </nav>
    """, unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def page_header(eyebrow: str, title: str, subtitle: str = "", quote: bool = False):
    q = '<p class="ph-quote">Le stock bouge. Zaiko s\'adapte.</p>' if quote else ""
    sub = f'<p class="ph-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="ph-wrap">
        <p class="ph-eyebrow">{eyebrow}</p>
        <h1 class="ph-title">{title}</h1>
        {sub}{q}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "", badge: str = "", badge_type: str = "ok"):
    badge_html = f'<span class="badge badge-{badge_type}">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub} {badge_html}</div>
    </div>
    """, unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def plotly_base_layout(fig, title=""):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        font_color=NAVY,
        title_text=title,
        title_font_family="Fraunces",
        title_font_size=16,
        title_font_color=NAVY,
        margin=dict(l=0, r=0, t=36 if title else 8, b=0),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font_size=12,
        ),
        xaxis=dict(showgrid=False, linecolor=BONE, tickfont_size=11),
        yaxis=dict(showgrid=True, gridcolor=BONE, linecolor="rgba(0,0,0,0)", tickfont_size=11),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render_groupe_dashboard():
    page_header("Groupe WAC", "Dashboard", "Vue consolidée des 4 établissements", quote=True)

    kpis = db.get_kpis_groupe()
    ratio = kpis["ratio_moyen"]
    ratio_badge = "ok" if ratio >= 95 else ("warn" if ratio >= 85 else "bad")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Références catalogue", str(kpis["nb_produits"]), "produits actifs")
    with c2:
        alert_n = kpis["nb_alertes"]
        kpi_card("Alertes stock", str(alert_n), "toutes enseignes",
                 badge="⚠ " + str(alert_n) if alert_n else "✓ RAS",
                 badge_type="bad" if alert_n else "ok")
    with c3:
        kpi_card("CA semaine", f"{kpis['ca_semaine']:,.0f} €", "7 derniers jours")
    with c4:
        kpi_card("Ratio moyen", f"{ratio:.1f}%", "réel / théorique",
                 badge=f"{ratio:.0f}%", badge_type=ratio_badge)

    # ── Tableau synthèse restos ──
    section_title("Résumé par établissement")

    rows = []
    for r in RESTAURANTS:
        k = db.get_kpis_resto(r["id"])
        alertes_v = db.get_alertes(r["id"])
        ratio_v = k["ratio"]
        rows.append({
            "Établissement": f"{r['emoji']} {r['nom']}",
            "Type":          r["type"],
            "Articles":      k["nb_articles"],
            "Alertes":       k["nb_alertes"],
            "CA 7j (€)":    round(k["ca_7j"], 2),
            "Ratio":         f"{ratio_v:.1f}%",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Chart CA consolidé 30j ──
    section_title("Chiffre d'affaires — 30 derniers jours")

    raw = db.get_ventes_groupe_30j()
    if raw:
        df_v = pd.DataFrame(raw)
        accent_map = {r["nom"]: r["accent"] for r in RESTAURANTS}
        fig = px.line(
            df_v, x="date_vente", y="total_reel", color="resto_nom",
            color_discrete_map=accent_map,
            labels={"date_vente": "", "total_reel": "CA réel (€)", "resto_nom": ""},
            markers=True,
        )
        fig.update_traces(line_width=2, marker_size=4)
        plotly_base_layout(fig)
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — CATALOGUE
# ═══════════════════════════════════════════════════════════════════════════════

def render_groupe_catalogue():
    page_header("Groupe WAC", "Catalogue produits", "Référentiel commun à tous les établissements")

    cats = db.get_categories()
    cat_options = {"Toutes catégories": None} | {f"{c['emoji']} {c['nom']}": c["id"] for c in cats}

    col_filter, col_add = st.columns([3, 1])
    with col_filter:
        selected_cat_label = st.selectbox("Filtrer par catégorie", list(cat_options.keys()), label_visibility="collapsed")
    selected_cat_id = cat_options[selected_cat_label]

    produits = db.get_produits(selected_cat_id)

    if produits:
        df = pd.DataFrame([{
            "Produit":    p["nom"],
            "Catégorie":  f"{p['categorie_emoji']} {p['categorie_nom']}",
            "Unité":      p["unite"],
            "Prix (€)":   p["prix_unitaire"],
            "Seuil alerte": p["seuil_alerte"],
        } for p in produits])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun produit dans cette catégorie.")

    section_title("Ajouter un produit")

    with st.form("form_add_produit", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nom du produit *")
            unite = st.text_input("Unité", value="bouteille")
        with c2:
            cat_labels = [f"{c['emoji']} {c['nom']}" for c in cats]
            cat_choice = st.selectbox("Catégorie *", cat_labels)
            prix = st.number_input("Prix unitaire (€)", min_value=0.0, step=0.5, format="%.2f")
        seuil = st.number_input("Seuil d'alerte", min_value=0.0, step=1.0, value=5.0)
        submitted = st.form_submit_button("Ajouter au catalogue")
        if submitted:
            if nom.strip():
                cat_id = cats[cat_labels.index(cat_choice)]["id"]
                db.add_produit(nom.strip(), cat_id, unite, prix, seuil)
                st.success(f"✓ {nom} ajouté au catalogue.")
                st.rerun()
            else:
                st.error("Le nom du produit est requis.")


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — FICHES TECHNIQUES
# ═══════════════════════════════════════════════════════════════════════════════

def render_groupe_fiches():
    page_header("Groupe WAC", "Fiches techniques", "Recettes, grammages et coûts théoriques")
    st.markdown("""
    <div style="background:white;border:1px solid #E8E0D0;border-radius:14px;padding:48px 40px;text-align:center;margin-top:24px;">
        <div style="font-size:36px;margin-bottom:16px;">📋</div>
        <div style="font-family:'Fraunces',serif;font-size:22px;color:#1C2B4A;margin-bottom:8px;">Module en préparation</div>
        <div style="font-size:14px;color:#6B6860;max-width:380px;margin:0 auto;">
            Les fiches techniques avec grammages, coûts matière et ratios théoriques
            seront disponibles dans la prochaine version de Zaiko.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_banner(resto: dict):
    accent = resto["accent"]
    # Compute a slightly darker shade for gradient
    st.markdown(f"""
    <div class="resto-banner" style="background:linear-gradient(135deg,{NAVY} 0%,{accent}33 100%);border:1px solid {accent}30;">
        <div class="resto-emoji-big">{resto['emoji']}</div>
        <div>
            <div class="resto-banner-name">{resto['nom']}</div>
            <div class="resto-banner-type">{resto['type']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_dashboard(resto: dict):
    rid    = resto["id"]
    accent = resto["accent"]

    page_header(
        eyebrow=f"◈ Groupe WAC — {resto['type']}",
        title=resto["nom"],
        subtitle="Vue d'ensemble de l'établissement",
    )

    render_resto_banner(resto)

    kpis = db.get_kpis_resto(rid)
    ratio = kpis["ratio"]
    ratio_badge = "ok" if ratio >= 95 else ("warn" if ratio >= 85 else "bad")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Articles en stock", str(kpis["nb_articles"]), "références inventoriées")
    with c2:
        alert_n = kpis["nb_alertes"]
        kpi_card("Alertes stock", str(alert_n), "sous le seuil d'alerte",
                 badge="⚠ " + str(alert_n) if alert_n else "✓ RAS",
                 badge_type="bad" if alert_n else "ok")
    with c3:
        kpi_card("CA 7 jours", f"{kpis['ca_7j']:,.0f} €", "chiffre d'affaires réel")
    with c4:
        kpi_card("Ratio 30j", f"{ratio:.1f}%", "réel / théorique",
                 badge=f"{ratio:.0f}%", badge_type=ratio_badge)

    col_chart, col_alerts = st.columns([2, 1])

    with col_chart:
        section_title("CA 14 derniers jours")
        ventes = db.get_ventes(rid, days=14)
        if ventes:
            df_v = pd.DataFrame(ventes)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_v["date_vente"], y=df_v["montant_theorique"],
                name="Théorique", marker_color=BONE, marker_line_width=0,
            ))
            fig.add_trace(go.Scatter(
                x=df_v["date_vente"], y=df_v["montant_reel"],
                name="Réel", line=dict(color=accent, width=2.5),
                mode="lines+markers", marker=dict(size=5, color=accent),
            ))
            plotly_base_layout(fig)
            st.plotly_chart(fig, use_container_width=True)

    with col_alerts:
        section_title("Alertes stock")
        alertes = db.get_alertes(rid)
        if alertes:
            for a in alertes[:6]:
                st.markdown(f"""
                <div class="alert-row">
                    ⚠
                    <span><strong>{a['produit_nom']}</strong><br>
                    <small>{a['quantite']} {a['unite']} · seuil {a['seuil_alerte']}</small></span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#E7F5EE;border:1px solid rgba(45,138,78,.2);border-radius:8px;
                        padding:14px 16px;font-size:13px;color:#2D8A4E;">
                ✓ Tous les stocks sont au-dessus des seuils.
            </div>
            """, unsafe_allow_html=True)

    section_title("Derniers mouvements")
    mvts = db.get_mouvements(rid, limit=5)
    if mvts:
        df_m = pd.DataFrame([{
            "Date":     m["date_mouvement"],
            "Produit":  m["produit_nom"],
            "Type":     m["type_mouvement"],
            "Qté":      f"{m['quantite']} {m['unite']}",
        } for m in mvts])
        st.dataframe(df_m, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — INVENTAIRE
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_inventaire(resto: dict):
    rid    = resto["id"]
    accent = resto["accent"]

    page_header(
        eyebrow=f"{resto['emoji']} {resto['nom']}",
        title="Inventaire",
        subtitle="Consultation et mise à jour des stocks",
    )

    inv = db.get_inventaire(rid)

    if inv:
        cats_present = sorted({i["categorie_nom"] for i in inv if i["categorie_nom"]})
        cat_filter = st.selectbox(
            "Catégorie", ["Toutes"] + cats_present,
            label_visibility="collapsed", key=f"inv_cat_{rid}"
        )
        if cat_filter != "Toutes":
            inv = [i for i in inv if i["categorie_nom"] == cat_filter]

        rows = []
        for i in inv:
            en_alerte = i["quantite"] <= i["seuil_alerte"]
            rows.append({
                "Catégorie":    f"{i['categorie_emoji']} {i['categorie_nom']}",
                "Produit":      i["produit_nom"],
                "Quantité":     i["quantite"],
                "Unité":        i["unite"],
                "Seuil alerte": i["seuil_alerte"],
                "Valeur (€)":   round(i["quantite"] * i["prix_unitaire"], 2),
                "Statut":       "⚠ Alerte" if en_alerte else "✓ OK",
                "Date saisie":  i["date_saisie"] or "—",
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        valeur_totale = sum(i["quantite"] * i["prix_unitaire"] for i in db.get_inventaire(rid))
        nb_alertes = sum(1 for i in db.get_inventaire(rid) if i["quantite"] <= i["seuil_alerte"])
        st.markdown(f"""
        <div style="display:flex;gap:16px;margin-top:12px;">
            <div style="background:white;border:1px solid {BONE};border-radius:8px;padding:12px 18px;font-size:13px;">
                Valeur totale du stock :
                <strong style="font-family:'JetBrains Mono',monospace;color:{NAVY};">
                    {valeur_totale:,.2f} €
                </strong>
            </div>
            <div style="background:{'#FDECEB' if nb_alertes else '#E7F5EE'};
                        border:1px solid {'rgba(192,57,43,.15)' if nb_alertes else 'rgba(45,138,78,.2)'};
                        border-radius:8px;padding:12px 18px;font-size:13px;
                        color:{'#C0392B' if nb_alertes else '#2D8A4E'};">
                {'⚠ ' + str(nb_alertes) + ' alerte(s)' if nb_alertes else '✓ Aucune alerte'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucun inventaire enregistré pour cet établissement.")

    section_title("Mettre à jour une quantité")

    produits = db.get_produits()
    prod_options = {f"{p['nom']} ({p['unite']})": p["id"] for p in produits}

    with st.form(f"form_inv_{rid}", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            prod_label = st.selectbox("Produit", list(prod_options.keys()))
        with c2:
            qty = st.number_input("Quantité", min_value=0.0, step=0.5, format="%.1f")
        with c3:
            note = st.text_input("Note (optionnel)")
        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            db.upsert_inventaire(rid, prod_options[prod_label], qty, note)
            st.success("✓ Stock mis à jour.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — MOUVEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_mouvements(resto: dict):
    rid    = resto["id"]
    accent = resto["accent"]

    page_header(
        eyebrow=f"{resto['emoji']} {resto['nom']}",
        title="Mouvements de stock",
        subtitle="Historique des entrées, sorties, pertes et transferts",
    )

    section_title("Saisir un mouvement")

    produits    = db.get_produits()
    prod_opts   = {f"{p['nom']} ({p['unite']})": p["id"] for p in produits}
    types_mv    = ["entrée", "sortie", "perte", "transfert"]

    with st.form(f"form_mv_{rid}", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            prod_label = st.selectbox("Produit", list(prod_opts.keys()))
        with c2:
            type_mv = st.selectbox("Type", types_mv)
        with c3:
            qty = st.number_input("Quantité", min_value=0.1, step=0.5, format="%.1f")
        note = st.text_input("Note (optionnel)")
        submitted = st.form_submit_button("Enregistrer le mouvement")
        if submitted:
            db.add_mouvement(rid, prod_opts[prod_label], type_mv, qty, note)
            st.success("✓ Mouvement enregistré.")
            st.rerun()

    section_title("50 derniers mouvements")

    mvts = db.get_mouvements(rid, limit=50)
    if mvts:
        palette = [TYPE_MV_COLORS.get(m["type_mouvement"], NAVY) for m in mvts]

        df = pd.DataFrame([{
            "Date":    m["date_mouvement"],
            "Produit": m["produit_nom"],
            "Type":    m["type_mouvement"],
            "Quantité":f"{m['quantite']} {m['unite']}",
            "Note":    m["note"] or "—",
        } for m in mvts])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Chart répartition par type
        section_title("Répartition des mouvements")
        type_counts = df["Type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Nombre"]
        color_map = {t: TYPE_MV_COLORS.get(t, NAVY) for t in type_counts["Type"]}
        fig = px.bar(
            type_counts, x="Type", y="Nombre",
            color="Type", color_discrete_map=color_map,
            labels={"Type": "", "Nombre": "Nombre de mouvements"},
        )
        fig.update_traces(marker_line_width=0)
        plotly_base_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun mouvement enregistré.")


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — VENTES & RATIOS
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_ventes(resto: dict):
    rid    = resto["id"]
    accent = resto["accent"]

    page_header(
        eyebrow=f"{resto['emoji']} {resto['nom']}",
        title="Ventes & Ratios",
        subtitle="Chiffre d'affaires réel vs théorique sur 30 jours",
    )

    ventes = db.get_ventes(rid, days=30)

    if ventes:
        df_v = pd.DataFrame(ventes)
        total_reel  = df_v["montant_reel"].sum()
        total_theo  = df_v["montant_theorique"].sum()
        ratio       = (total_reel / total_theo * 100) if total_theo else 0
        ecart       = total_reel - total_theo
        ratio_badge = "ok" if ratio >= 95 else ("warn" if ratio >= 85 else "bad")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card("CA réel 30j", f"{total_reel:,.0f} €", "total période")
        with c2:
            kpi_card("CA théorique 30j", f"{total_theo:,.0f} €", "attendu fiches")
        with c3:
            kpi_card("Ratio", f"{ratio:.1f}%", "réel / théorique",
                     badge=f"{ratio:.0f}%", badge_type=ratio_badge)
        with c4:
            sign = "+" if ecart >= 0 else ""
            kpi_card("Écart cumulé", f"{sign}{ecart:,.0f} €",
                     "positif = sur-performance",
                     badge=sign + str(round(ecart)) + " €",
                     badge_type="ok" if ecart >= 0 else "bad")

        section_title("Courbe réel vs théorique")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_v["date_vente"], y=df_v["montant_theorique"],
            name="Théorique",
            line=dict(color=BONE, width=2, dash="dash"),
            mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=df_v["date_vente"], y=df_v["montant_reel"],
            name="Réel",
            line=dict(color=accent, width=2.5),
            mode="lines+markers",
            marker=dict(size=5, color=accent),
            fill="tonexty",
            fillcolor=f"{accent}18",
        ))
        plotly_base_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

        section_title("Détail par jour")
        df_display = df_v[["date_vente","montant_reel","montant_theorique"]].copy()
        df_display["ratio"] = (df_display["montant_reel"] / df_display["montant_theorique"] * 100).round(1).astype(str) + "%"
        df_display["écart"] = (df_display["montant_reel"] - df_display["montant_theorique"]).round(2)
        df_display.columns = ["Date","CA réel (€)","CA théorique (€)","Ratio","Écart (€)"]
        df_display = df_display.sort_values("Date", ascending=False).reset_index(drop=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune vente enregistrée sur les 30 derniers jours.")

    section_title("Saisir les ventes du jour")

    with st.form(f"form_ventes_{rid}", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            date_v = st.date_input("Date", value=date.today())
        with c2:
            reel = st.number_input("CA réel (€)", min_value=0.0, step=10.0, format="%.2f")
        with c3:
            theo = st.number_input("CA théorique (€)", min_value=0.0, step=10.0, format="%.2f")
        note = st.text_input("Note (optionnel)")
        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            if reel > 0:
                db.add_vente(rid, date_v, reel, theo, note)
                st.success("✓ Ventes enregistrées.")
                st.rerun()
            else:
                st.error("Le CA réel doit être supérieur à 0.")


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

def route(page: str):
    # ── Groupe WAC ──
    if page == "groupe_dashboard":
        return render_groupe_dashboard()
    if page == "groupe_catalogue":
        return render_groupe_catalogue()
    if page == "groupe_fiches":
        return render_groupe_fiches()

    # ── Restaurants ──
    for r in RESTAURANTS:
        key = r["key"]
        if page.startswith(key + "_"):
            sub = page[len(key) + 1:]
            if sub == "dashboard":  return render_resto_dashboard(r)
            if sub == "inventaire": return render_resto_inventaire(r)
            if sub == "mouvements": return render_resto_mouvements(r)
            if sub == "ventes":     return render_resto_ventes(r)

    # ── Default ──
    render_groupe_dashboard()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    db.init_db()
    inject_css()

    current_page = st.query_params.get("page", "groupe_dashboard")
    render_navbar(current_page)
    route(current_page)


if __name__ == "__main__":
    main()
