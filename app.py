import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import database as db

# ─── Config ──────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Zaiko",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Brand tokens (alignés sur tokens.css) ───────────────────────────────────

INK         = "#0B1220"
NAVY        = "#0F2A4A"
NAVY_DEEP   = "#081A2F"
NAVY_SOFT   = "#1B3558"
GOLD        = "#C9A24B"
GOLD_LIGHT  = "#E3C275"
GOLD_DEEP   = "#A8862F"
RED         = "#B23A2A"
RED_DEEP    = "#8C2A1E"
BONE        = "#F4EFE6"
PAPER       = "#FAF7F1"
RULE        = "#E2D9C7"
MUTED       = "#54688A"
MUTED_DARK  = "#9FB2CF"
SUCCESS     = "#2A6F4F"

RESTAURANTS = db.RESTAURANTS_CONFIG

GROUPE_NAV = [
    ("groupe_dashboard", "Dashboard"),
    ("groupe_catalogue", "Catalogue"),
    ("groupe_prix",      "Évolution des prix"),
    ("groupe_fiches",    "Fiches techniques"),
]

RESTO_NAV = [
    ("dashboard",   "Dashboard"),
    ("inventaire",  "Inventaire"),
    ("mouvements",  "Mouvements"),
    ("ventes",      "Ventes & Ratios"),
]

TYPE_MV_COLORS = {
    "entrée":    SUCCESS,
    "sortie":    NAVY,
    "perte":     RED,
    "transfert": GOLD,
}

FORMATS_PREDEFINIS = [
    "20cl", "25cl", "33cl", "37.5cl", "50cl", "70cl", "75cl",
    "1L", "1.5L", "2L", "5L",
    "100g", "250g", "500g", "750g", "1kg", "2kg", "5kg", "10kg",
    "pièce", "lot", "carton",
]

# ─── Logo SVG (inline, adapté au fond navy) ─────────────────────────────────

LOGO_NAV_SVG = """
<svg width="22" height="24" viewBox="0 0 122 132" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="10"  y="14"  width="100" height="18" rx="2" fill="#F4EFE6"></rect>
  <rect x="14"  y="14"  width="92"  height="4"        fill="#C9A24B" opacity="0.95"></rect>
  <rect x="62"  y="40"  width="34"  height="14" rx="2" fill="#F4EFE6" opacity="0.45"></rect>
  <rect x="46"  y="60"  width="34"  height="14" rx="2" fill="#F4EFE6" opacity="0.6"></rect>
  <rect x="30"  y="80"  width="34"  height="14" rx="2" fill="#B23A2A" opacity="0.95"></rect>
  <rect x="10"  y="100" width="100" height="18" rx="2" fill="#F4EFE6"></rect>
  <rect x="14"  y="114" width="92"  height="4"        fill="#C9A24B" opacity="0.95"></rect>
</svg>
"""

LOGO_LIGHT_SVG = """
<svg width="120" height="44" viewBox="0 0 360 132" xmlns="http://www.w3.org/2000/svg" aria-label="Zaiko">
  <rect x="10"  y="14"  width="100" height="18" rx="2" fill="#0F2A4A"></rect>
  <rect x="14"  y="14"  width="92"  height="4"        fill="#C9A24B" opacity="0.9"></rect>
  <rect x="62"  y="40"  width="34"  height="14" rx="2" fill="#0F2A4A" opacity="0.75"></rect>
  <rect x="46"  y="60"  width="34"  height="14" rx="2" fill="#0F2A4A" opacity="0.6"></rect>
  <rect x="30"  y="80"  width="34"  height="14" rx="2" fill="#B23A2A" opacity="0.9"></rect>
  <rect x="10"  y="100" width="100" height="18" rx="2" fill="#0F2A4A"></rect>
  <rect x="14"  y="114" width="92"  height="4"        fill="#C9A24B" opacity="0.9"></rect>
  <text x="146" y="92" font-family="Inter,system-ui,sans-serif" font-weight="600"
        font-size="84" letter-spacing="-3.4" fill="#0B1220">Zaiko</text>
</svg>
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════════════════

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --zk-ink:        #0B1220;
        --zk-navy:       #0F2A4A;
        --zk-navy-deep:  #081A2F;
        --zk-navy-soft:  #1B3558;
        --zk-gold:       #C9A24B;
        --zk-gold-light: #E3C275;
        --zk-gold-deep:  #A8862F;
        --zk-red:        #B23A2A;
        --zk-red-deep:   #8C2A1E;
        --zk-bone:       #F4EFE6;
        --zk-paper:      #FAF7F1;
        --zk-rule:       #E2D9C7;
        --zk-muted:      #54688A;
        --zk-muted-dark: #9FB2CF;
        --zk-success:    #2A6F4F;
        --zk-font-sans:  'Inter', system-ui, -apple-system, sans-serif;
        --zk-font-serif: 'Fraunces', Georgia, serif;
        --zk-font-mono:  'JetBrains Mono', ui-monospace, monospace;
    }

    *, *::before, *::after { box-sizing: border-box; }
    html, body, .stApp {
        background: var(--zk-paper) !important;
        font-family: var(--zk-font-sans);
        color: var(--zk-ink);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* ── Hide all Streamlit chrome ── */
    #MainMenu, footer { display: none !important; }
    [data-testid="stSidebar"]      { display: none !important; }
    [data-testid="stToolbar"]      { display: none !important; }
    [data-testid="stDecoration"]   { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    [data-testid="stHeader"]       { display: none !important; }
    .stDeployButton                { display: none !important; }
    div[data-testid="stAppViewContainer"] > section > div:first-child { padding-top: 0 !important; }

    /* ── Main container padding (compense la navbar fixe) ── */
    .main .block-container {
        padding-top:   84px !important;
        padding-left:  40px !important;
        padding-right: 40px !important;
        padding-bottom: 64px !important;
        max-width:     1380px !important;
    }

    /* ═══════════════════════════════════════
       NAVBAR
    ═══════════════════════════════════════ */
    .zk-nav {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 99999;
        height: 60px;
        background: var(--zk-navy-deep);
        display: flex;
        align-items: center;
        padding: 0 28px;
        border-bottom: 1px solid rgba(201, 162, 75, 0.10);
        box-shadow: 0 1px 0 rgba(0,0,0,.2), 0 4px 16px rgba(0,0,0,.18);
    }

    .zk-brand {
        display: flex;
        align-items: center;
        gap: 9px;
        text-decoration: none !important;
        margin-right: 28px;
        flex-shrink: 0;
        height: 60px;
        padding: 0 4px;
    }
    .zk-brand:hover { text-decoration: none !important; }
    .zk-brand-text {
        font-family: var(--zk-font-sans);
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--zk-bone);
        line-height: 1;
    }

    .zk-sep {
        width: 1px;
        height: 18px;
        background: rgba(244, 239, 230, .08);
        flex-shrink: 0;
    }

    .zk-group {
        position: relative;
        height: 60px;
        display: flex;
        align-items: center;
    }

    .zk-trigger {
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 5px 11px;
        border-radius: 6px;
        color: rgba(244, 239, 230, .58);
        font-family: var(--zk-font-sans);
        font-size: 13px;
        font-weight: 500;
        white-space: nowrap;
        cursor: default;
        transition: color .14s, background .14s;
        user-select: none;
        height: 32px;
    }
    .zk-group:hover .zk-trigger {
        color: var(--zk-bone);
        background: rgba(244, 239, 230, .06);
    }
    .zk-trigger.zk-active { color: var(--zk-gold) !important; }

    .zk-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        flex-shrink: 0;
        display: inline-block;
    }
    .zk-chev {
        font-size: 8px;
        opacity: .42;
        transition: transform .15s, opacity .15s;
        margin-left: 1px;
        line-height: 1;
    }
    .zk-group:hover .zk-chev {
        transform: rotate(180deg);
        opacity: .7;
    }

    .zk-dropdown {
        position: absolute;
        top: 54px;
        left: 0;
        background: var(--zk-navy-deep);
        border: 1px solid rgba(201, 162, 75, .18);
        border-radius: 10px;
        padding: 6px;
        min-width: 200px;
        opacity: 0;
        pointer-events: none;
        transform: translateY(-6px);
        transition: opacity .14s ease, transform .14s ease;
        box-shadow: 0 24px 48px -16px rgba(8, 26, 47, .55), 0 4px 12px rgba(0,0,0,.25);
    }
    .zk-group:hover .zk-dropdown {
        opacity: 1;
        pointer-events: auto;
        transform: translateY(0);
    }

    .zk-dropdown a, .zk-dropdown a:link, .zk-dropdown a:visited {
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 8px 12px;
        border-radius: 6px;
        color: rgba(244, 239, 230, .60) !important;
        font-family: var(--zk-font-sans);
        font-size: 13px;
        font-weight: 400;
        text-decoration: none !important;
        transition: color .12s, background .12s;
    }
    .zk-dropdown a:hover {
        color: var(--zk-bone) !important;
        background: rgba(255,255,255,.05);
        text-decoration: none !important;
    }
    .zk-dropdown a.zk-link-active {
        color: var(--zk-gold) !important;
        background: rgba(201, 162, 75, .09);
        font-weight: 500;
    }

    /* ═══════════════════════════════════════
       PAGE HEADER
    ═══════════════════════════════════════ */
    .zk-page-head {
        padding: 16px 0 28px;
        margin-bottom: 32px;
        border-bottom: 1px solid var(--zk-rule);
    }
    .zk-eyebrow {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-bottom: 12px;
    }
    .zk-h1 {
        font-family: var(--zk-font-sans);
        font-size: 40px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--zk-ink);
        line-height: 1.05;
        margin: 0;
    }
    .zk-sub {
        font-size: 14px;
        color: var(--zk-muted);
        margin-top: 6px;
        font-weight: 400;
    }
    .zk-quote {
        font-family: var(--zk-font-serif);
        font-style: italic;
        font-weight: 400;
        font-size: 16px;
        color: var(--zk-muted);
        margin-top: 12px;
        letter-spacing: -0.01em;
    }

    /* ═══════════════════════════════════════
       SECTION TITLE
    ═══════════════════════════════════════ */
    .zk-section {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
        padding-bottom: 10px;
        border-bottom: 1px solid var(--zk-rule);
        margin: 36px 0 18px;
    }

    /* ═══════════════════════════════════════
       KPI CARDS — bord gauche d'accent 3px
    ═══════════════════════════════════════ */
    .zk-kpi {
        background: white;
        border: 1px solid var(--zk-rule);
        border-left: 3px solid var(--zk-gold);
        border-radius: 8px;
        padding: 18px 20px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        height: 100%;
        transition: box-shadow .15s;
    }
    .zk-kpi:hover { box-shadow: 0 2px 6px -2px rgba(8, 26, 47, .08); }
    .zk-kpi-label {
        font-family: var(--zk-font-mono);
        font-size: 9.5px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
    }
    .zk-kpi-value {
        font-family: var(--zk-font-sans);
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--zk-ink);
        line-height: 1;
    }
    .zk-kpi-sub {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        color: var(--zk-muted);
        margin-top: 2px;
    }
    .zk-kpi-sub.zk-pos { color: var(--zk-success); }
    .zk-kpi-sub.zk-neg { color: var(--zk-red); }

    .zk-kpi.zk-acc-navy { border-left-color: var(--zk-navy); }
    .zk-kpi.zk-acc-red  { border-left-color: var(--zk-red); }
    .zk-kpi.zk-acc-success { border-left-color: var(--zk-success); }

    /* ═══════════════════════════════════════
       BADGES (pill)
    ═══════════════════════════════════════ */
    .zk-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 10px;
        border-radius: 999px;
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }
    .zk-badge-dot { width: 6px; height: 6px; border-radius: 50%; }
    .zk-badge-stock { background: var(--zk-navy); color: var(--zk-bone); }
    .zk-badge-stock .zk-badge-dot { background: var(--zk-gold); }
    .zk-badge-low   { background: var(--zk-gold); color: var(--zk-ink); }
    .zk-badge-out   { background: var(--zk-red); color: var(--zk-bone); }
    .zk-badge-out   .zk-badge-dot { background: var(--zk-bone); }
    .zk-badge-ok    { background: transparent; color: var(--zk-success); border: 1px solid var(--zk-success); }
    .zk-badge-ok    .zk-badge-dot { background: var(--zk-success); }

    /* ═══════════════════════════════════════
       RESTO BANNER (header de page resto)
    ═══════════════════════════════════════ */
    .zk-resto-banner {
        background: var(--zk-navy);
        border-radius: 14px;
        padding: 28px 32px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        border: 1px solid var(--zk-navy-soft);
    }
    .zk-resto-accent-bar {
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 4px;
    }
    .zk-resto-name {
        font-family: var(--zk-font-sans);
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--zk-bone);
        line-height: 1.05;
        margin: 0;
    }
    .zk-resto-type {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted-dark);
        margin-top: 8px;
    }

    /* ═══════════════════════════════════════
       ALERT ROW
    ═══════════════════════════════════════ */
    .zk-alert {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(178, 58, 42, .06);
        border: 1px solid rgba(178, 58, 42, .15);
        border-left: 3px solid var(--zk-red);
        border-radius: 6px;
        padding: 11px 14px;
        font-size: 13px;
        color: var(--zk-ink);
        margin-bottom: 8px;
    }
    .zk-alert-name { font-weight: 600; color: var(--zk-ink); }
    .zk-alert-meta {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        color: var(--zk-muted);
        margin-top: 2px;
    }

    .zk-empty-ok {
        background: rgba(42, 111, 79, .06);
        border: 1px solid rgba(42, 111, 79, .18);
        border-left: 3px solid var(--zk-success);
        border-radius: 6px;
        padding: 14px 16px;
        font-size: 13px;
        color: var(--zk-success);
        font-weight: 500;
    }

    /* ═══════════════════════════════════════
       TABLES / DATAFRAMES
    ═══════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--zk-rule) !important;
        border-radius: 8px !important;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] [data-testid="stTable"] { background: white; }

    /* ═══════════════════════════════════════
       FORMS
    ═══════════════════════════════════════ */
    [data-testid="stForm"] {
        background: white !important;
        border: 1px solid var(--zk-rule) !important;
        border-radius: 10px !important;
        padding: 22px !important;
    }
    [data-testid="stForm"] label {
        font-family: var(--zk-font-mono) !important;
        font-size: 10.5px !important;
        font-weight: 500 !important;
        letter-spacing: 0.18em !important;
        text-transform: uppercase !important;
        color: var(--zk-muted) !important;
    }

    /* ═══════════════════════════════════════
       BUTTONS
    ═══════════════════════════════════════ */
    .stButton > button, .stForm button[type="submit"] {
        background: var(--zk-navy) !important;
        color: var(--zk-bone) !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: var(--zk-font-sans) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 11px 22px !important;
        letter-spacing: -0.005em !important;
        transition: background .15s !important;
    }
    .stButton > button:hover, .stForm button[type="submit"]:hover {
        background: var(--zk-navy-soft) !important;
    }

    /* ═══════════════════════════════════════
       INPUTS
    ═══════════════════════════════════════ */
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div, .stDateInput input {
        font-family: var(--zk-font-sans) !important;
        border-radius: 6px !important;
        border-color: var(--zk-rule) !important;
    }

    /* ═══════════════════════════════════════
       SCROLLBAR + DIVERS
    ═══════════════════════════════════════ */
    ::-webkit-scrollbar              { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track        { background: transparent; }
    ::-webkit-scrollbar-thumb        { background: var(--zk-rule); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover  { background: #c8bfac; }

    /* Plotly */
    .js-plotly-plot { font-family: var(--zk-font-sans) !important; }

    /* ═══════════════════════════════════════
       CATALOGUE — blocs par catégorie
    ═══════════════════════════════════════ */
    .zk-cat-block {
        background: var(--zk-navy);
        border: 1px solid var(--zk-navy-soft);
        border-radius: 12px;
        padding: 22px 28px 14px 28px;
        margin-bottom: 16px;
    }
    .zk-cat-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        padding-bottom: 12px;
        margin-bottom: 6px;
        border-bottom: 1px solid var(--zk-navy-soft);
    }
    .zk-cat-title {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--zk-gold);
    }
    .zk-cat-count {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--zk-muted-dark);
    }
    .zk-prod-line {
        display: grid;
        grid-template-columns: 1fr 110px 110px;
        align-items: center;
        gap: 16px;
        padding: 12px 4px;
        border-bottom: 1px solid rgba(226,217,199,0.08);
        transition: background 0.15s ease;
    }
    .zk-prod-line:last-child { border-bottom: none; }
    .zk-prod-line:hover { background: var(--zk-navy-soft); }
    .zk-prod-name {
        font-family: var(--zk-font-sans);
        font-size: 14px;
        font-weight: 500;
        color: var(--zk-bone);
    }
    .zk-prod-format {
        font-family: var(--zk-font-mono);
        font-size: 12px;
        color: var(--zk-muted-dark);
        text-align: left;
    }
    .zk-prod-price {
        font-family: var(--zk-font-mono);
        font-size: 13px;
        font-weight: 500;
        color: var(--zk-gold);
        text-align: right;
        font-variant-numeric: tabular-nums;
    }
    .zk-cat-empty {
        background: white;
        border: 1px solid var(--zk-rule);
        border-radius: 12px;
        padding: 40px 24px;
        text-align: center;
        font-family: var(--zk-font-sans);
        font-size: 13px;
        color: var(--zk-muted);
    }

    /* ═══════════════════════════════════════
       ÉVOLUTION DES PRIX — historique
    ═══════════════════════════════════════ */
    .zk-price-block {
        background: white;
        border: 1px solid var(--zk-rule);
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 16px;
    }
    .zk-price-head {
        display: grid;
        grid-template-columns: 110px 1fr 180px 110px;
        gap: 16px;
        padding: 14px 22px;
        background: var(--zk-paper);
        border-bottom: 1px solid var(--zk-rule);
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
    }
    .zk-price-row {
        display: grid;
        grid-template-columns: 110px 1fr 180px 110px;
        gap: 16px;
        align-items: center;
        padding: 14px 22px;
        border-bottom: 1px solid var(--zk-rule);
    }
    .zk-price-row:last-child { border-bottom: none; }
    .zk-price-row:hover { background: var(--zk-paper); }
    .zk-price-date {
        font-family: var(--zk-font-mono);
        font-size: 12px;
        color: var(--zk-muted);
    }
    .zk-price-prod {
        font-family: var(--zk-font-sans);
        font-size: 14px;
        color: var(--zk-ink);
    }
    .zk-price-prod-meta {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        color: var(--zk-muted);
        margin-top: 2px;
    }
    .zk-price-evol {
        font-family: var(--zk-font-mono);
        font-size: 13px;
        color: var(--zk-ink);
        font-variant-numeric: tabular-nums;
    }
    .zk-price-evol-arrow {
        color: var(--zk-muted);
        margin: 0 8px;
    }
    .zk-price-var {
        font-family: var(--zk-font-mono);
        font-size: 13px;
        font-weight: 500;
        text-align: right;
        font-variant-numeric: tabular-nums;
    }
    .zk-price-var.up   { color: var(--zk-red); }
    .zk-price-var.down { color: var(--zk-success); }
    .zk-price-var.flat { color: var(--zk-muted); }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  NAVBAR
# ═══════════════════════════════════════════════════════════════════════════════

def render_navbar(current_page: str):
    def _link_active(page_id):
        return "zk-link-active" if current_page == page_id else ""

    def _trigger_active(prefix):
        return "zk-active" if current_page.startswith(prefix) else ""

    # Groupe WAC dropdown items
    groupe_links = "".join(
        f'<a href="?page={pid}" class="{_link_active(pid)}" target="_self">{label}</a>'
        for pid, label in GROUPE_NAV
    )

    # Per-restaurant dropdowns
    resto_blocks = []
    for r in RESTAURANTS:
        key    = r["key"]
        accent = r["accent"]
        nom    = r["nom"]

        # short display name (avoid overflow)
        short = nom if len(nom) <= 18 else "Les Halles"

        links = "".join(
            f'<a href="?page={key}_{sid}" class="{_link_active(key + "_" + sid)}" target="_self">'
            f'<span class="zk-dot" style="background:{accent}"></span>{label}</a>'
            for sid, label in RESTO_NAV
        )

        is_active = _trigger_active(key + "_")
        resto_blocks.append(f'''<div class="zk-sep"></div>
        <div class="zk-group">
            <div class="zk-trigger {is_active}">
                <span class="zk-dot" style="background:{accent}"></span>{short}<span class="zk-chev">▾</span>
            </div>
            <div class="zk-dropdown">{links}</div>
        </div>''')

    resto_html = "".join(resto_blocks)

    nav_html = f'''<div class="zk-nav">
        <a class="zk-brand" href="?page=groupe_dashboard" target="_self">
            {LOGO_NAV_SVG.strip()}
            <span class="zk-brand-text">Zaiko</span>
        </a>
        <div class="zk-group">
            <div class="zk-trigger {_trigger_active("groupe_")}">Groupe WAC<span class="zk-chev">▾</span></div>
            <div class="zk-dropdown">{groupe_links}</div>
        </div>
        {resto_html}
    </div>'''

    st.markdown(nav_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE HEADER + HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def page_header(eyebrow: str, title: str, subtitle: str = "", quote: bool = False):
    sub = f'<div class="zk-sub">{subtitle}</div>' if subtitle else ""
    q = '<div class="zk-quote">« Le stock bouge. Zaiko s\'adapte. »</div>' if quote else ""
    st.markdown(f'''<div class="zk-page-head">
        <div class="zk-eyebrow">{eyebrow}</div>
        <h1 class="zk-h1">{title}</h1>
        {sub}{q}
    </div>''', unsafe_allow_html=True)


def section(text: str):
    st.markdown(f'<div class="zk-section">{text}</div>', unsafe_allow_html=True)


def kpi(label: str, value: str, sub: str = "", accent: str = "gold", trend: str = ""):
    """ accent ∈ gold | navy | red | success """
    cls = f"zk-kpi zk-acc-{accent}" if accent != "gold" else "zk-kpi"
    trend_cls = ""
    if trend:
        trend_cls = "zk-pos" if trend.startswith("+") else "zk-neg"
    sub_html = ""
    if sub or trend:
        sub_html = f'<div class="zk-kpi-sub {trend_cls}">{trend} {sub}</div>'.strip()
    st.markdown(f'''<div class="{cls}">
        <div class="zk-kpi-label">{label}</div>
        <div class="zk-kpi-value">{value}</div>
        {sub_html}
    </div>''', unsafe_allow_html=True)


def badge(status: str, text: str) -> str:
    """ status ∈ stock | low | out | ok """
    return f'<span class="zk-badge zk-badge-{status}"><span class="zk-badge-dot"></span>{text}</span>'


def plotly_layout(fig, height=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        font_color=INK,
        font_size=12,
        margin=dict(l=0, r=0, t=8, b=0),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font_size=11,
            orientation="h",
            yanchor="bottom", y=1.02, xanchor="left", x=0,
        ),
        xaxis=dict(showgrid=False, linecolor=RULE, tickfont_size=11, tickfont_color=MUTED),
        yaxis=dict(showgrid=True, gridcolor=RULE, linecolor="rgba(0,0,0,0)",
                   tickfont_size=11, tickfont_color=MUTED, zerolinecolor=RULE),
    )
    if height:
        fig.update_layout(height=height)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render_groupe_dashboard():
    page_header("Groupe WAC", "Vue consolidée", "Pilotage des 4 établissements", quote=True)

    k = db.get_kpis_groupe()
    ratio = k["ratio_moyen"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Références", str(k["nb_produits"]), "produits actifs")
    with c2: kpi("Alertes stock", str(k["nb_alertes"]),
                 "toutes enseignes", accent="red" if k["nb_alertes"] else "success")
    with c3: kpi("CA semaine", f"{k['ca_semaine']:,.0f} €", "7 derniers jours")
    with c4:
        trend = f"{ratio - 100:+.1f}%" if ratio != 100 else ""
        kpi("Ratio moyen", f"{ratio:.1f}%", "réel / théorique",
            accent="success" if ratio >= 95 else ("gold" if ratio >= 85 else "red"),
            trend=trend)

    # ── Tableau synthèse ──
    section("Résumé par établissement")

    rows = []
    for r in RESTAURANTS:
        rk = db.get_kpis_resto(r["id"])
        rows.append({
            "Établissement": r["nom"],
            "Type":          r["type"],
            "Articles":      rk["nb_articles"],
            "Alertes":       rk["nb_alertes"],
            "CA 7j (€)":     round(rk["ca_7j"], 2),
            "Ratio":         f"{rk['ratio']:.1f}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Chart CA consolidé 30j ──
    section("Chiffre d'affaires — 30 derniers jours")

    raw = db.get_ventes_groupe_30j()
    if raw:
        df = pd.DataFrame(raw)
        accent_map = {r["nom"]: r["accent"] for r in RESTAURANTS}
        fig = px.line(
            df, x="date_vente", y="total_reel", color="resto_nom",
            color_discrete_map=accent_map,
            labels={"date_vente": "", "total_reel": "CA réel (€)", "resto_nom": ""},
        )
        fig.update_traces(line_width=2.2, mode="lines")
        plotly_layout(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — CATALOGUE
# ═══════════════════════════════════════════════════════════════════════════════

def render_groupe_catalogue():
    page_header("Groupe WAC", "Catalogue produits",
                "Référentiel commun à tous les établissements")

    cats = db.get_categories()
    produits = db.get_produits()

    if not produits:
        st.markdown(
            '<div class="zk-cat-empty">Aucun produit au catalogue pour le moment.</div>',
            unsafe_allow_html=True,
        )
    else:
        formats_dispos = sorted({p["unite"] for p in produits if p["unite"]})
        cats_dispos = sorted({p["categorie_nom"] for p in produits if p["categorie_nom"]})

        f1, f2, f3 = st.columns([2, 1, 1])
        with f1:
            recherche = st.text_input(
                "Rechercher une référence",
                placeholder="Rechercher une référence…",
                label_visibility="collapsed",
            )
        with f2:
            cat_filter = st.selectbox(
                "Catégorie",
                ["Toutes catégories"] + cats_dispos,
                label_visibility="collapsed",
            )
        with f3:
            fmt_filter = st.selectbox(
                "Conditionnement",
                ["Tous conditionnements"] + formats_dispos,
                label_visibility="collapsed",
            )

        terme = recherche.strip().lower()
        produits_filtres = [
            p for p in produits
            if (not terme or terme in p["nom"].lower())
            and (cat_filter == "Toutes catégories" or p["categorie_nom"] == cat_filter)
            and (fmt_filter == "Tous conditionnements" or p["unite"] == fmt_filter)
        ]

        produits_par_cat = {}
        for p in produits_filtres:
            key = p["categorie_nom"] or "Sans catégorie"
            produits_par_cat.setdefault(key, []).append(p)

        if produits_par_cat:
            for cat_nom in sorted(produits_par_cat.keys()):
                items = produits_par_cat[cat_nom]
                lignes_html = "".join(
                    f'''<div class="zk-prod-line">
                        <div class="zk-prod-name">{p["nom"]}</div>
                        <div class="zk-prod-format">{p["unite"]}</div>
                        <div class="zk-prod-price">{p["prix_unitaire"]:.2f} €</div>
                    </div>'''
                    for p in items
                )
                count_label = f'{len(items)} référence{"s" if len(items) > 1 else ""}'
                st.markdown(f'''
                <div class="zk-cat-block">
                    <div class="zk-cat-header">
                        <div class="zk-cat-title">{cat_nom}</div>
                        <div class="zk-cat-count">{count_label}</div>
                    </div>
                    {lignes_html}
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="zk-cat-empty">Aucune référence ne correspond aux filtres.</div>',
                unsafe_allow_html=True,
            )

    cat_labels = [c["nom"] for c in cats]

    if produits:
        section("Modifier une référence")
        prod_options = {
            f'{p["nom"]} — {p["categorie_nom"] or "Sans catégorie"} — {p["unite"]}': p["id"]
            for p in sorted(produits, key=lambda x: (x["categorie_nom"] or "", x["nom"]))
        }
        prod_label = st.selectbox(
            "Référence à modifier",
            list(prod_options.keys()),
            key="edit_prod_select",
        )
        prod_id = prod_options[prod_label]
        prod_actuel = next(p for p in produits if p["id"] == prod_id)

        with st.form("form_edit_prod"):
            e1, e2, e3 = st.columns([2, 1, 1])
            with e1:
                nom_edit = st.text_input("Nom de la référence *", value=prod_actuel["nom"])
            with e2:
                cat_index = cat_labels.index(prod_actuel["categorie_nom"]) if prod_actuel["categorie_nom"] in cat_labels else 0
                cat_edit = st.selectbox("Catégorie *", cat_labels, index=cat_index)
            with e3:
                fmt_index = FORMATS_PREDEFINIS.index(prod_actuel["unite"]) if prod_actuel["unite"] in FORMATS_PREDEFINIS else 0
                fmt_edit = st.selectbox("Conditionnement *", FORMATS_PREDEFINIS, index=fmt_index)

            e4, e5, e6 = st.columns([2, 1, 1])
            with e4:
                prix_edit = st.number_input(
                    "Prix unitaire (€)",
                    min_value=0.0, step=0.5, format="%.2f",
                    value=float(prod_actuel["prix_unitaire"] or 0.0),
                )
            with e5:
                confirm_delete = st.checkbox("Confirmer la suppression")
            with e6:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

            b1, b2 = st.columns(2)
            with b1:
                save_btn = st.form_submit_button("Enregistrer les modifications", use_container_width=True)
            with b2:
                delete_btn = st.form_submit_button("Supprimer la référence", use_container_width=True)

            if save_btn:
                if nom_edit.strip():
                    cid_edit = cats[cat_labels.index(cat_edit)]["id"]
                    db.update_produit(prod_id, nom_edit.strip(), cid_edit, fmt_edit, prix_edit)
                    st.success("Modifications enregistrées.")
                    st.rerun()
                else:
                    st.error("Le nom de la référence est requis.")
            elif delete_btn:
                if confirm_delete:
                    db.archive_produit(prod_id)
                    st.success("Référence supprimée.")
                    st.rerun()
                else:
                    st.error("Coche « Confirmer la suppression » avant de supprimer.")

    section("Ajouter un produit")
    with st.form("form_add_prod", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            nom = st.text_input("Nom du produit *")
        with c2:
            cat_choice = st.selectbox("Catégorie *", cat_labels)
        with c3:
            format_choice = st.selectbox("Conditionnement *", FORMATS_PREDEFINIS)

        c4, _, c6 = st.columns([2, 1, 1])
        with c4:
            prix = st.number_input("Prix unitaire (€)", min_value=0.0, step=0.5, format="%.2f")
        with c6:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Ajouter au catalogue", use_container_width=True)

        if submitted:
            if nom.strip():
                cid = cats[cat_labels.index(cat_choice)]["id"]
                db.add_produit(nom.strip(), cid, format_choice, prix, 0)
                st.success("Produit ajouté.")
                st.rerun()
            else:
                st.error("Le nom du produit est requis.")


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — ÉVOLUTION DES PRIX
# ═══════════════════════════════════════════════════════════════════════════════

def render_groupe_prix():
    page_header("Groupe WAC", "Évolution des prix",
                "Suivi des variations tarifaires par référence")

    historique = db.get_historique_prix()
    changements = [h for h in historique if float(h["ancien_prix"]) != float(h["nouveau_prix"])]

    if not changements:
        st.markdown(
            '<div class="zk-cat-empty">Aucun changement de prix enregistré pour le moment. '
            'Les variations apparaîtront ici dès que tu modifieras un prix dans le catalogue.</div>',
            unsafe_allow_html=True,
        )
        return

    nb_changements = len(changements)
    derniere_date = max(h["date_changement"] for h in changements)
    variations = [
        ((h["nouveau_prix"] - h["ancien_prix"]) / h["ancien_prix"] * 100)
        for h in changements if h["ancien_prix"]
    ]
    var_moyenne = sum(variations) / len(variations) if variations else 0

    k1, k2, k3 = st.columns(3)
    with k1: kpi("Changements de prix", str(nb_changements), "depuis la mise en service")
    with k2: kpi("Dernière modification", derniere_date, accent="navy")
    with k3:
        signe = "+" if var_moyenne >= 0 else ""
        kpi("Variation moyenne", f"{signe}{var_moyenne:.1f} %",
            "moyenne pondérée sur l'ensemble", accent="navy")

    section("Filtrer par référence")
    produits_avec_histo = sorted(
        {(h["produit_id"], h["produit_nom"], h["unite"], h["categorie_nom"] or "Sans catégorie")
         for h in historique},
        key=lambda x: (x[3], x[1])
    )
    options = {"Toutes les références": None}
    for pid, pnom, punite, pcat in produits_avec_histo:
        options[f"{pnom} — {pcat} — {punite}"] = pid

    choix = st.selectbox(
        "Référence",
        list(options.keys()),
        label_visibility="collapsed",
    )
    produit_id = options[choix]

    if produit_id:
        histo_prod = db.get_historique_prix(produit_id=produit_id)
        histo_prod_chrono = sorted(histo_prod, key=lambda h: h["date_changement"])

        if len(histo_prod_chrono) >= 1:
            section(f"Courbe d'évolution — {choix}")
            dates = [h["date_changement"] for h in histo_prod_chrono]
            prix = [h["nouveau_prix"] for h in histo_prod_chrono]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=prix,
                mode="lines+markers",
                line=dict(color=NAVY, width=2.5, shape="hv"),
                marker=dict(color=GOLD, size=9, line=dict(color=NAVY, width=1.5)),
                hovertemplate="%{x}<br>%{y:.2f} €<extra></extra>",
            ))
            plotly_layout(fig, height=320)
            fig.update_yaxes(title=None, tickprefix="", ticksuffix=" €")
            fig.update_xaxes(title=None)
            st.plotly_chart(fig, use_container_width=True)

        section("Historique des changements")
        rows = [h for h in histo_prod if float(h["ancien_prix"]) != float(h["nouveau_prix"])]
    else:
        section("Derniers changements")
        rows = changements[:30]

    if not rows:
        st.markdown(
            '<div class="zk-cat-empty">Aucun changement de prix pour cette référence.</div>',
            unsafe_allow_html=True,
        )
        return

    lignes_html = []
    for h in rows:
        ancien = float(h["ancien_prix"])
        nouveau = float(h["nouveau_prix"])
        if ancien == 0:
            var_pct = 0.0
        else:
            var_pct = (nouveau - ancien) / ancien * 100
        if var_pct > 0:
            cls = "up"
            signe = "+"
        elif var_pct < 0:
            cls = "down"
            signe = ""
        else:
            cls = "flat"
            signe = ""
        lignes_html.append(f'''
            <div class="zk-price-row">
                <div class="zk-price-date">{h["date_changement"]}</div>
                <div>
                    <div class="zk-price-prod">{h["produit_nom"]}</div>
                    <div class="zk-price-prod-meta">{(h["categorie_nom"] or "Sans catégorie")} · {h["unite"]}</div>
                </div>
                <div class="zk-price-evol">
                    {ancien:.2f} €<span class="zk-price-evol-arrow">→</span>{nouveau:.2f} €
                </div>
                <div class="zk-price-var {cls}">{signe}{var_pct:.1f} %</div>
            </div>
        ''')

    st.markdown(f'''
    <div class="zk-price-block">
        <div class="zk-price-head">
            <div>Date</div>
            <div>Référence</div>
            <div>Évolution</div>
            <div style="text-align:right;">Variation</div>
        </div>
        {"".join(lignes_html)}
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — FICHES TECHNIQUES
# ═══════════════════════════════════════════════════════════════════════════════

def render_groupe_fiches():
    page_header("Groupe WAC", "Fiches techniques",
                "Recettes, grammages et coûts théoriques")
    st.markdown(f'''
    <div style="background:white;border:1px solid {RULE};border-radius:12px;
                padding:64px 40px;text-align:center;margin-top:8px;">
        <div style="font-family:var(--zk-font-mono);font-size:11px;font-weight:500;
                    letter-spacing:0.28em;text-transform:uppercase;color:{MUTED};
                    margin-bottom:16px;">Module en préparation</div>
        <div style="font-family:var(--zk-font-sans);font-size:24px;font-weight:700;
                    letter-spacing:-0.02em;color:{INK};margin-bottom:12px;">
            Disponible prochainement
        </div>
        <div style="font-size:14px;color:{MUTED};max-width:440px;margin:0 auto;
                    line-height:1.55;">
            Fiches techniques avec grammages, coûts matière et ratios théoriques —
            intégration dans la prochaine version.
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — HEADER BANNER
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_banner(resto: dict):
    st.markdown(f'''
    <div class="zk-resto-banner">
        <div class="zk-resto-accent-bar" style="background:{resto["accent"]}"></div>
        <div class="zk-resto-name">{resto["nom"]}</div>
        <div class="zk-resto-type">{resto["type"]}</div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_dashboard(resto: dict):
    rid    = resto["id"]
    accent = resto["accent"]

    page_header(resto["type"], resto["nom"], "Vue d'ensemble de l'établissement")
    render_resto_banner(resto)

    k = db.get_kpis_resto(rid)
    ratio = k["ratio"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Articles en stock", str(k["nb_articles"]), "références")
    with c2: kpi("Alertes", str(k["nb_alertes"]), "sous le seuil",
                 accent="red" if k["nb_alertes"] else "success")
    with c3: kpi("CA 7 jours", f"{k['ca_7j']:,.0f} €", "réel")
    with c4:
        trend = f"{ratio - 100:+.1f}%" if ratio != 100 else ""
        kpi("Ratio 30j", f"{ratio:.1f}%", "réel / théorique",
            accent="success" if ratio >= 95 else ("gold" if ratio >= 85 else "red"),
            trend=trend)

    col_chart, col_alerts = st.columns([2, 1])

    with col_chart:
        section("CA 14 derniers jours")
        ventes = db.get_ventes(rid, days=14)
        if ventes:
            df = pd.DataFrame(ventes)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["date_vente"], y=df["montant_theorique"],
                name="Théorique", marker_color=RULE, marker_line_width=0,
            ))
            fig.add_trace(go.Scatter(
                x=df["date_vente"], y=df["montant_reel"],
                name="Réel", line=dict(color=accent, width=2.5),
                mode="lines+markers", marker=dict(size=5, color=accent),
            ))
            plotly_layout(fig, height=320)
            st.plotly_chart(fig, use_container_width=True)

    with col_alerts:
        section("Alertes stock")
        alertes = db.get_alertes(rid)
        if alertes:
            for a in alertes[:6]:
                st.markdown(f'''
                <div class="zk-alert">
                    <div style="flex:1;">
                        <div class="zk-alert-name">{a["produit_nom"]}</div>
                        <div class="zk-alert-meta">{a["quantite"]} {a["unite"]} · seuil {a["seuil_alerte"]}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="zk-empty-ok">Tous les stocks sont au-dessus des seuils.</div>',
                        unsafe_allow_html=True)

    section("Derniers mouvements")
    mvts = db.get_mouvements(rid, limit=5)
    if mvts:
        df = pd.DataFrame([{
            "Date":     m["date_mouvement"],
            "Produit":  m["produit_nom"],
            "Type":     m["type_mouvement"],
            "Quantité": f"{m['quantite']} {m['unite']}",
        } for m in mvts])
        st.dataframe(df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — INVENTAIRE
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_inventaire(resto: dict):
    rid = resto["id"]

    page_header(resto["nom"], "Inventaire", "Consultation et mise à jour des stocks")

    inv = db.get_inventaire(rid)

    if inv:
        cats_present = sorted({i["categorie_nom"] for i in inv if i["categorie_nom"]})
        cat_filter = st.selectbox(
            "Catégorie", ["Toutes catégories"] + cats_present,
            label_visibility="collapsed", key=f"inv_cat_{rid}"
        )
        inv_view = inv if cat_filter == "Toutes catégories" else [i for i in inv if i["categorie_nom"] == cat_filter]

        rows = []
        for i in inv_view:
            en_alerte = i["quantite"] <= i["seuil_alerte"]
            rows.append({
                "Catégorie":    i["categorie_nom"] or "—",
                "Produit":      i["produit_nom"],
                "Quantité":     i["quantite"],
                "Unité":        i["unite"],
                "Seuil":        i["seuil_alerte"],
                "Valeur (€)":   round(i["quantite"] * i["prix_unitaire"], 2),
                "Statut":       "Alerte" if en_alerte else "OK",
                "Date saisie":  i["date_saisie"] or "—",
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        valeur = sum(i["quantite"] * i["prix_unitaire"] for i in inv)
        nb_a   = sum(1 for i in inv if i["quantite"] <= i["seuil_alerte"])

        c1, c2 = st.columns(2)
        with c1:
            kpi("Valeur du stock", f"{valeur:,.2f} €", "total inventaire")
        with c2:
            kpi("Alertes actives", str(nb_a),
                "produits sous seuil",
                accent="red" if nb_a else "success")
    else:
        st.info("Aucun inventaire enregistré pour cet établissement.")

    section("Mettre à jour une quantité")

    produits = db.get_produits()
    prod_options = {f"{p['nom']} ({p['unite']})": p["id"] for p in produits}

    with st.form(f"form_inv_{rid}", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: prod_label = st.selectbox("Produit", list(prod_options.keys()))
        with c2: qty = st.number_input("Quantité", min_value=0.0, step=0.5, format="%.1f")
        with c3: note = st.text_input("Note (optionnel)")
        if st.form_submit_button("Enregistrer"):
            db.upsert_inventaire(rid, prod_options[prod_label], qty, note)
            st.success("Stock mis à jour.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — MOUVEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_mouvements(resto: dict):
    rid = resto["id"]

    page_header(resto["nom"], "Mouvements de stock",
                "Historique des entrées, sorties, pertes et transferts")

    section("Saisir un mouvement")

    produits  = db.get_produits()
    prod_opts = {f"{p['nom']} ({p['unite']})": p["id"] for p in produits}
    types_mv  = ["entrée", "sortie", "perte", "transfert"]

    with st.form(f"form_mv_{rid}", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: prod_label = st.selectbox("Produit", list(prod_opts.keys()))
        with c2: type_mv = st.selectbox("Type", types_mv)
        with c3: qty = st.number_input("Quantité", min_value=0.1, step=0.5, format="%.1f")
        note = st.text_input("Note (optionnel)")
        if st.form_submit_button("Enregistrer le mouvement"):
            db.add_mouvement(rid, prod_opts[prod_label], type_mv, qty, note)
            st.success("Mouvement enregistré.")
            st.rerun()

    section("50 derniers mouvements")

    mvts = db.get_mouvements(rid, limit=50)
    if mvts:
        df = pd.DataFrame([{
            "Date":     m["date_mouvement"],
            "Produit":  m["produit_nom"],
            "Type":     m["type_mouvement"],
            "Quantité": f"{m['quantite']} {m['unite']}",
            "Note":     m["note"] or "—",
        } for m in mvts])
        st.dataframe(df, use_container_width=True, hide_index=True)

        section("Répartition par type")
        type_counts = df["Type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Nombre"]
        color_map = {t: TYPE_MV_COLORS.get(t, NAVY) for t in type_counts["Type"]}
        fig = px.bar(
            type_counts, x="Type", y="Nombre",
            color="Type", color_discrete_map=color_map,
            labels={"Type": "", "Nombre": ""},
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        plotly_layout(fig, height=260)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun mouvement enregistré.")


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — VENTES & RATIOS
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_ventes(resto: dict):
    rid    = resto["id"]
    accent = resto["accent"]

    page_header(resto["nom"], "Ventes & Ratios",
                "Chiffre d'affaires réel vs théorique sur 30 jours")

    ventes = db.get_ventes(rid, days=30)

    if ventes:
        df = pd.DataFrame(ventes)
        total_reel = df["montant_reel"].sum()
        total_theo = df["montant_theorique"].sum()
        ratio      = (total_reel / total_theo * 100) if total_theo else 0
        ecart      = total_reel - total_theo

        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("CA réel 30j", f"{total_reel:,.0f} €", "période complète")
        with c2: kpi("CA théorique 30j", f"{total_theo:,.0f} €", "attendu fiches")
        with c3:
            trend = f"{ratio - 100:+.1f}%"
            kpi("Ratio", f"{ratio:.1f}%", "réel / théorique",
                accent="success" if ratio >= 95 else ("gold" if ratio >= 85 else "red"),
                trend=trend)
        with c4:
            sign = "+" if ecart >= 0 else ""
            kpi("Écart cumulé", f"{sign}{ecart:,.0f} €",
                "positif = sur-performance",
                accent="success" if ecart >= 0 else "red")

        section("Courbe réel vs théorique")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date_vente"], y=df["montant_theorique"],
            name="Théorique",
            line=dict(color=RULE, width=2, dash="dash"),
            mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=df["date_vente"], y=df["montant_reel"],
            name="Réel",
            line=dict(color=accent, width=2.5),
            mode="lines+markers",
            marker=dict(size=5, color=accent),
            fill="tonexty", fillcolor=f"{accent}1A",
        ))
        plotly_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

        section("Détail par jour")
        df_d = df[["date_vente", "montant_reel", "montant_theorique"]].copy()
        df_d["Ratio"] = (df_d["montant_reel"] / df_d["montant_theorique"] * 100).round(1).astype(str) + "%"
        df_d["Écart (€)"] = (df_d["montant_reel"] - df_d["montant_theorique"]).round(2)
        df_d.columns = ["Date", "CA réel (€)", "CA théorique (€)", "Ratio", "Écart (€)"]
        df_d = df_d.sort_values("Date", ascending=False).reset_index(drop=True)
        st.dataframe(df_d, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune vente enregistrée sur les 30 derniers jours.")

    section("Saisir les ventes du jour")

    with st.form(f"form_ventes_{rid}", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: date_v = st.date_input("Date", value=date.today())
        with c2: reel = st.number_input("CA réel (€)", min_value=0.0, step=10.0, format="%.2f")
        with c3: theo = st.number_input("CA théorique (€)", min_value=0.0, step=10.0, format="%.2f")
        note = st.text_input("Note (optionnel)")
        if st.form_submit_button("Enregistrer"):
            if reel > 0:
                db.add_vente(rid, date_v, reel, theo, note)
                st.success("Ventes enregistrées.")
                st.rerun()
            else:
                st.error("Le CA réel doit être supérieur à 0.")


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

def route(page: str):
    if page == "groupe_dashboard": return render_groupe_dashboard()
    if page == "groupe_catalogue": return render_groupe_catalogue()
    if page == "groupe_prix":      return render_groupe_prix()
    if page == "groupe_fiches":    return render_groupe_fiches()

    for r in RESTAURANTS:
        key = r["key"]
        if page.startswith(key + "_"):
            sub = page[len(key) + 1:]
            if sub == "dashboard":  return render_resto_dashboard(r)
            if sub == "inventaire": return render_resto_inventaire(r)
            if sub == "mouvements": return render_resto_mouvements(r)
            if sub == "ventes":     return render_resto_ventes(r)

    render_groupe_dashboard()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    db.init_db()
    inject_css()
    current = st.query_params.get("page", "groupe_dashboard")
    render_navbar(current)
    route(current)


if __name__ == "__main__":
    main()
