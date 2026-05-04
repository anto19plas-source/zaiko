import re
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
]

RESTO_NAV = [
    ("dashboard",   "Dashboard"),
    ("inventaire",  "Inventaire"),
    ("historique",  "Historique inventaire"),
    ("performance", "Performance"),
    ("fiches",      "Fiches techniques"),
]

FORMATS_PREDEFINIS = [
    "bouteille",
    # Centilitres — mesures bar et petits formats
    "1cl", "2cl", "3cl", "4cl", "5cl", "6cl", "8cl",
    "10cl", "12cl", "15cl", "18cl", "20cl", "25cl",
    # Centilitres — standards boissons
    "33cl", "35cl", "37.5cl", "40cl", "44cl", "48.5cl", "50cl",
    "60cl", "66cl", "70cl", "75cl",
    # Magnums et grandes contenances
    "100cl", "150cl",
    # Litres
    "1L", "1.25L", "1.5L", "2L", "3L", "5L",
    # Fûts
    "10L", "15L", "20L", "25L", "30L", "50L",
    # Solides
    "100g", "150g", "200g", "250g", "500g", "750g",
    "1kg", "1.5kg", "2kg", "3kg", "5kg", "10kg",
    # Génériques
    "pièce", "lot", "carton", "douzaine", "barquette",
]

# ─── Logo SVG (inline, adapté au fond navy) ─────────────────────────────────

LOGO_NAV_SVG = """
<svg width="34" height="37" viewBox="0 0 122 132" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
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
  <text x="146" y="92" font-family="Inter,system-ui,sans-serif" font-weight="700"
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
        padding-top:   102px !important;
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
        height: 76px;
        background: var(--zk-navy-deep);
        display: flex;
        align-items: center;
        padding: 0 36px;
        border-bottom: 1px solid rgba(201, 162, 75, 0.18);
        box-shadow: 0 1px 0 rgba(0,0,0,.25), 0 6px 24px rgba(0,0,0,.22);
    }

    .zk-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        text-decoration: none !important;
        margin-right: 36px;
        flex-shrink: 0;
        height: 76px;
        padding: 0 4px;
    }
    .zk-brand:hover { text-decoration: none !important; }
    .zk-brand-text {
        font-family: var(--zk-font-sans);
        font-size: 20px;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--zk-bone);
        line-height: 1;
    }

    .zk-sep {
        width: 1px;
        height: 22px;
        background: rgba(244, 239, 230, .10);
        flex-shrink: 0;
    }

    .zk-group {
        position: relative;
        height: 76px;
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
        top: 68px;
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
        padding: 32px 36px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        border: 1px solid var(--zk-navy-soft);
        box-shadow: 0 8px 24px -10px rgba(8, 26, 47, .35);
    }
    .zk-resto-accent-bar {
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 4px;
        z-index: 2;
    }
    .zk-resto-motif {
        position: absolute;
        top: -10px;
        right: -10px;
        width: 280px;
        height: 200px;
        z-index: 1;
        pointer-events: none;
    }
    .zk-resto-eyebrow {
        position: relative;
        z-index: 2;
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--zk-gold);
        margin-bottom: 12px;
    }
    .zk-resto-name {
        position: relative;
        z-index: 2;
        font-family: var(--zk-font-sans);
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: var(--zk-bone);
        line-height: 1.05;
        margin: 0;
    }
    .zk-resto-type {
        position: relative;
        z-index: 2;
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
    .zk-prod-price.zk-no-price {
        color: var(--zk-red);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 11px;
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

    /* ═══════════════════════════════════════
       CATALOGUE — barre catégorie + lignes interactives
    ═══════════════════════════════════════ */
    .zk-cat-bar {
        background: var(--zk-navy);
        border-radius: 10px 10px 0 0;
        padding: 14px 24px;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-top: 18px;
        border-bottom: 2px solid var(--zk-gold);
    }
    .zk-cat-bar-title {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--zk-gold);
    }
    .zk-cat-bar-count {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--zk-muted-dark);
    }
    .zk-row-name {
        font-family: var(--zk-font-sans);
        font-size: 14px;
        font-weight: 500;
        color: var(--zk-ink);
        padding: 6px 0;
        line-height: 1.4;
    }
    .zk-row-format {
        font-family: var(--zk-font-mono);
        font-size: 12px;
        color: var(--zk-muted);
        padding: 6px 0;
        line-height: 1.4;
    }
    .zk-row-price {
        font-family: var(--zk-font-mono);
        font-size: 13px;
        font-weight: 500;
        color: var(--zk-gold-deep);
        text-align: right;
        padding: 6px 0;
        font-variant-numeric: tabular-nums;
        line-height: 1.4;
    }
    .zk-row-price.zk-no-price {
        color: var(--zk-red);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 11px;
    }

    /* ═══════════════════════════════════════
       ÉVOLUTION DES PRIX — résumé par produit
    ═══════════════════════════════════════ */
    .zk-prix-head {
        display: grid;
        grid-template-columns: 2fr 1.5fr 1.5fr 0.8fr 0.6fr 0.9fr 0.8fr;
        gap: 14px;
        padding: 12px 18px;
        background: var(--zk-paper);
        border: 1px solid var(--zk-rule);
        border-radius: 10px 10px 0 0;
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-top: 12px;
        margin-bottom: 4px;
    }
    .zk-prix-name {
        font-family: var(--zk-font-sans);
        font-size: 14px;
        font-weight: 500;
        color: var(--zk-ink);
        padding: 6px 0;
        line-height: 1.4;
    }
    .zk-prix-meta {
        font-family: var(--zk-font-mono);
        font-size: 12px;
        color: var(--zk-muted);
        padding: 6px 0;
        line-height: 1.4;
    }
    .zk-prix-evol {
        font-family: var(--zk-font-mono);
        font-size: 13px;
        color: var(--zk-ink);
        font-variant-numeric: tabular-nums;
        padding: 6px 0;
        line-height: 1.4;
    }
    .zk-prix-var {
        font-family: var(--zk-font-mono);
        font-size: 13px;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
        padding: 6px 0;
        line-height: 1.4;
    }
    .zk-prix-var.up   { color: var(--zk-red); }
    .zk-prix-var.down { color: var(--zk-success); }
    .zk-prix-var.flat { color: var(--zk-muted); }

    /* ═══════════════════════════════════════
       FICHE PRIX — historique chronologique 3 colonnes
    ═══════════════════════════════════════ */
    .zk-fiche-price-block {
        background: white;
        border: 1px solid var(--zk-rule);
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 16px;
    }
    .zk-fiche-price-head {
        display: grid;
        grid-template-columns: 140px 1fr 120px;
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
    .zk-fiche-price-row {
        display: grid;
        grid-template-columns: 140px 1fr 120px;
        gap: 16px;
        align-items: center;
        padding: 14px 22px;
        border-bottom: 1px solid var(--zk-rule);
    }
    .zk-fiche-price-row:last-child { border-bottom: none; }
    .zk-fiche-price-row:hover { background: var(--zk-paper); }

    /* ═══════════════════════════════════════
       PAGE D'ACCUEIL — Hero & cards
    ═══════════════════════════════════════ */
    .zk-hero {
        background: var(--zk-navy-deep);
        border-radius: 18px;
        padding: 88px 40px 76px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 44px;
        border: 1px solid rgba(201, 162, 75, 0.14);
        box-shadow: 0 24px 48px -16px rgba(8, 26, 47, .55);
        position: relative;
        overflow: hidden;
    }
    .zk-hero-eyebrow {
        position: relative;
        z-index: 2;
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.32em;
        text-transform: uppercase;
        color: var(--zk-gold);
        margin-bottom: 28px;
    }
    .zk-hero-logo { position: relative; z-index: 2; margin-bottom: 24px; }
    .zk-hero-rule {
        position: relative;
        z-index: 2;
        width: 56px;
        height: 2px;
        background: var(--zk-gold);
        margin: 14px 0 26px 0;
        border-radius: 1px;
    }
    .zk-hero-quote {
        position: relative;
        z-index: 2;
        font-family: var(--zk-font-serif);
        font-style: italic;
        font-weight: 400;
        font-size: 30px;
        line-height: 1.3;
        letter-spacing: -0.015em;
        color: rgba(244, 239, 230, 0.78);
        max-width: 560px;
        margin: 0;
    }

    .zk-home-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 12px;
    }
    .zk-home-card {
        background: white;
        border: 1px solid var(--zk-rule);
        border-radius: 12px;
        padding: 22px 22px 22px 26px;
        text-decoration: none !important;
        display: block;
        transition: box-shadow .18s ease, transform .14s ease, border-color .18s ease;
        position: relative;
        overflow: hidden;
        min-height: 168px;
    }
    .zk-home-card:hover {
        box-shadow: 0 12px 28px -8px rgba(8, 26, 47, .18);
        transform: translateY(-3px);
        border-color: rgba(201, 162, 75, 0.35);
        text-decoration: none !important;
    }
    .zk-home-card-accent {
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 4px;
        border-radius: 12px 0 0 12px;
    }
    .zk-home-card-mini {
        position: absolute;
        top: 18px;
        right: 18px;
        opacity: 0.65;
    }
    .zk-home-card-eyebrow {
        font-family: var(--zk-font-mono);
        font-size: 9.5px;
        font-weight: 500;
        letter-spacing: 0.24em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-bottom: 12px;
    }
    .zk-home-card-name {
        font-family: var(--zk-font-sans);
        font-size: 17px;
        font-weight: 700;
        color: var(--zk-ink);
        margin-bottom: 4px;
        letter-spacing: -0.015em;
        line-height: 1.15;
    }
    .zk-home-card-type {
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-bottom: 22px;
    }
    .zk-home-card-cta {
        font-family: var(--zk-font-mono);
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--zk-navy);
    }

    .zk-home-access-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }
    .zk-home-access {
        background: var(--zk-navy);
        border: 1px solid var(--zk-navy-soft);
        border-radius: 12px;
        padding: 22px 24px;
        text-decoration: none !important;
        display: block;
        transition: background .14s, border-color .14s;
        position: relative;
    }
    .zk-home-access::after {
        content: "→";
        position: absolute;
        top: 22px;
        right: 22px;
        color: var(--zk-gold);
        font-family: var(--zk-font-sans);
        font-weight: 500;
        opacity: 0.55;
        transition: opacity .14s, transform .14s;
    }
    .zk-home-access:hover {
        background: var(--zk-navy-soft);
        border-color: rgba(201, 162, 75, 0.30);
        text-decoration: none !important;
    }
    .zk-home-access:hover::after { opacity: 1; transform: translateX(3px); }
    .zk-home-access-eyebrow {
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted-dark);
        margin-bottom: 8px;
    }
    .zk-home-access-name {
        font-family: var(--zk-font-sans);
        font-size: 16px;
        font-weight: 600;
        color: var(--zk-bone);
        letter-spacing: -0.01em;
        margin-bottom: 4px;
    }
    .zk-home-access-sub {
        font-family: var(--zk-font-sans);
        font-size: 12px;
        color: var(--zk-muted-dark);
        line-height: 1.4;
    }

    /* Footer brand minimal */
    .zk-footer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin-top: 56px;
        padding-top: 28px;
        border-top: 1px solid var(--zk-rule);
        opacity: 0.7;
    }
    .zk-footer-mark {
        font-family: var(--zk-font-sans);
        font-size: 14px;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: var(--zk-ink);
    }
    .zk-footer-bar {
        width: 24px;
        height: 1px;
        background: var(--zk-rule);
    }
    .zk-footer-tag {
        font-family: var(--zk-font-serif);
        font-style: italic;
        font-size: 13px;
        color: var(--zk-muted);
    }

    /* Avertissement non-bloquant */
    .zk-warn-line {
        background: rgba(201, 162, 75, .10);
        border: 1px solid rgba(201, 162, 75, .30);
        border-left: 3px solid var(--zk-gold);
        border-radius: 6px;
        padding: 11px 14px;
        font-family: var(--zk-font-sans);
        font-size: 13px;
        color: var(--zk-ink);
        line-height: 1.5;
        margin: 8px 0 16px 0;
    }

    /* ═══════════════════════════════════════
       CATALOGUE — séparateurs entre catégories
    ═══════════════════════════════════════ */
    .zk-cat-sep {
        height: 1px;
        background: var(--zk-rule);
        margin: 2px 0 28px 0;
        border-radius: 1px;
    }

    /* ═══════════════════════════════════════
       FICHES TECHNIQUES — en-têtes de tableau
    ═══════════════════════════════════════ */
    .zk-fiches-head {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr 0.7fr 0.7fr 0.8fr;
        gap: 14px;
        padding: 12px 18px;
        background: var(--zk-paper);
        border: 1px solid var(--zk-rule);
        border-radius: 10px 10px 0 0;
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-top: 12px;
        margin-bottom: 4px;
    }
    .zk-fiches-ing-head {
        display: grid;
        grid-template-columns: 3fr 0.8fr 0.8fr 0.9fr 0.7fr;
        gap: 14px;
        padding: 12px 18px;
        background: var(--zk-paper);
        border: 1px solid var(--zk-rule);
        border-radius: 10px 10px 0 0;
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-top: 12px;
        margin-bottom: 4px;
    }

    /* ═══════════════════════════════════════
       INVENTAIRE — saisie inline
    ═══════════════════════════════════════ */
    .zk-inv-head {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr 0.7fr 0.9fr 0.7fr;
        gap: 14px;
        padding: 10px 18px;
        background: var(--zk-paper);
        border: 1px solid var(--zk-rule);
        border-radius: 0;
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-top: 0;
        margin-bottom: 4px;
    }
    .zk-inv-snap-head {
        display: grid;
        grid-template-columns: 2fr 0.8fr 0.6fr 0.6fr 0.6fr 0.7fr 0.8fr 0.7fr;
        gap: 14px;
        padding: 10px 18px;
        background: var(--zk-paper);
        border: 1px solid var(--zk-rule);
        font-family: var(--zk-font-mono);
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--zk-muted);
        margin-top: 0;
        margin-bottom: 4px;
    }
    .zk-inv-alert-tag {
        display: inline-block;
        margin-left: 8px;
        padding: 2px 8px;
        background: rgba(178, 58, 42, .12);
        color: var(--zk-red);
        border-radius: 999px;
        font-family: var(--zk-font-mono);
        font-size: 9px;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        vertical-align: middle;
    }
    .zk-inv-alert-num {
        color: var(--zk-red) !important;
        font-weight: 600;
    }
    .zk-help-line {
        background: var(--zk-paper);
        border: 1px solid var(--zk-rule);
        border-radius: 8px;
        padding: 12px 16px;
        font-family: var(--zk-font-sans);
        font-size: 13px;
        color: var(--zk-muted);
        line-height: 1.5;
    }
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

        # short display name (avoid overflow) — troncature dynamique
        short = nom if len(nom) <= 18 else (nom[:16].rstrip() + "…")

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
        <a class="zk-brand" href="?page=accueil" target="_self">
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
#  FICHES TECHNIQUES — helpers de calcul
# ═══════════════════════════════════════════════════════════════════════════════

UNITES_RECETTE = ["cl", "L", "g", "kg", "pièce"]


def parse_unite_catalogue(unite: str) -> tuple[float, str]:
    """
    Convertit l'unité catalogue (ex: '75cl', '1.5L', '500g', '1kg', 'bouteille')
    en (quantité_normalisée, dimension) où dimension ∈ {'cl', 'g', 'piece'}.
    Pour 'bouteille', 'pièce', 'lot', 'carton', 'douzaine', 'barquette' → (1, 'piece').
    """
    if not unite:
        return (1.0, "piece")
    u = unite.strip().lower().replace(",", ".")

    if u.endswith("cl"):
        try:
            return (float(u[:-2]), "cl")
        except ValueError:
            pass
    if u.endswith("kg"):
        try:
            return (float(u[:-2]) * 1000.0, "g")
        except ValueError:
            pass
    if u.endswith("l"):
        try:
            return (float(u[:-1]) * 100.0, "cl")
        except ValueError:
            pass
    if u.endswith("g"):
        try:
            return (float(u[:-1]), "g")
        except ValueError:
            pass
    return (1.0, "piece")


def normaliser_qte_recette(qte: float, unite_recette: str) -> tuple[float, str]:
    """Ramène la quantité recette dans la dimension de base (cl, g, ou piece)."""
    u = (unite_recette or "").strip()
    if u == "cl":   return (qte, "cl")
    if u == "L":    return (qte * 100.0, "cl")
    if u == "g":    return (qte, "g")
    if u == "kg":   return (qte * 1000.0, "g")
    return (qte, "piece")


def cout_ingredient(produit: dict, qte: float, unite_recette: str) -> float | None:
    """
    Coût d'un ingrédient (€). Retourne None si la dimension recette est
    incompatible avec le format catalogue (ex: 'g' pour un produit en cl).
    """
    if not produit:
        return None
    prix = float(produit.get("prix_unitaire") or 0)
    if prix <= 0 or qte <= 0:
        return 0.0
    cat_qte, cat_dim = parse_unite_catalogue(produit.get("unite") or produit.get("produit_unite") or "")
    rec_qte, rec_dim = normaliser_qte_recette(qte, unite_recette)
    if cat_dim != rec_dim:
        return None
    if cat_qte <= 0:
        return 0.0
    return prix * rec_qte / cat_qte


def calculer_indicateurs_fiche(ingredients: list, prix_vente_ttc: float, tva: float) -> dict:
    """Renvoie coût brut, coût avec 10% perte, prix HT, ratio, coefficient."""
    cout_brut = 0.0
    for ing in ingredients:
        prod = ing.get("_produit")
        if not prod:
            continue
        c = cout_ingredient(prod, float(ing.get("quantite") or 0), ing.get("unite_recette") or "pièce")
        if c is not None:
            cout_brut += c

    cout_perte = cout_brut * 1.10
    prix_ht = (prix_vente_ttc / (1.0 + tva / 100.0)) if (prix_vente_ttc and tva is not None) else 0.0
    ratio = (cout_perte / prix_ht * 100.0) if prix_ht > 0 else 0.0
    coeff = (prix_ht / cout_perte) if cout_perte > 0 else 0.0
    return {
        "cout_brut": cout_brut,
        "cout_perte": cout_perte,
        "prix_ht": prix_ht,
        "ratio": ratio,
        "coefficient": coeff,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  ACCUEIL
# ═══════════════════════════════════════════════════════════════════════════════

def render_accueil():
    # ── Hero navy-deep avec motif barres + Display + baseline ──
    # Motif de stock en filigrane (barres horizontales empilées)
    pattern_svg = '''<svg width="100%" height="100%" viewBox="0 0 600 480" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" style="position:absolute;top:0;left:0;width:100%;height:100%;opacity:0.06;pointer-events:none;">
      <g fill="#C9A24B">
        <rect x="60"  y="40"  width="200" height="14" rx="2"></rect>
        <rect x="60"  y="68"  width="120" height="14" rx="2" opacity="0.7"></rect>
        <rect x="60"  y="96"  width="160" height="14" rx="2" opacity="0.5"></rect>
        <rect x="60"  y="124" width="200" height="14" rx="2"></rect>
        <rect x="380" y="320" width="180" height="14" rx="2"></rect>
        <rect x="380" y="348" width="100" height="14" rx="2" opacity="0.7"></rect>
        <rect x="380" y="376" width="140" height="14" rx="2" opacity="0.5"></rect>
        <rect x="380" y="404" width="180" height="14" rx="2"></rect>
      </g>
    </svg>'''

    logo_hero_svg = '''<svg width="320" height="118" viewBox="0 0 360 132" xmlns="http://www.w3.org/2000/svg" aria-label="Zaiko">
      <g>
        <rect x="10"  y="14"  width="100" height="18" rx="2" fill="#F4EFE6"></rect>
        <rect x="14"  y="14"  width="92"  height="4"        fill="#C9A24B" opacity="0.95"></rect>
        <rect x="62"  y="40"  width="34"  height="14" rx="2" fill="#F4EFE6" opacity="0.45"></rect>
        <rect x="46"  y="60"  width="34"  height="14" rx="2" fill="#F4EFE6" opacity="0.6"></rect>
        <rect x="30"  y="80"  width="34"  height="14" rx="2" fill="#B23A2A" opacity="0.95"></rect>
        <rect x="10"  y="100" width="100" height="18" rx="2" fill="#F4EFE6"></rect>
        <rect x="14"  y="114" width="92"  height="4"        fill="#C9A24B" opacity="0.95"></rect>
      </g>
      <text x="146" y="92" font-family="Inter,system-ui,sans-serif" font-weight="700"
            font-size="84" letter-spacing="-3.4" fill="#F4EFE6">Zaiko</text>
    </svg>'''

    st.markdown(f'''
    <div class="zk-hero">
        {pattern_svg}
        <div class="zk-hero-eyebrow">Groupe WAC · 4 établissements</div>
        <div class="zk-hero-logo">{logo_hero_svg}</div>
        <div class="zk-hero-rule"></div>
        <p class="zk-hero-quote">« Le stock bouge. Zaiko s'adapte. »</p>
    </div>
    ''', unsafe_allow_html=True)

    # ── Établissements ──
    section("Établissements")

    # Mini SVG décoratif (3 barres) coloré par accent du resto
    def _mini_stock(accent: str) -> str:
        return f'''<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <rect x="0"  y="2"  width="32" height="4" rx="1" fill="{accent}" opacity="0.95"></rect>
          <rect x="14" y="11" width="14" height="3" rx="1" fill="{accent}" opacity="0.65"></rect>
          <rect x="8"  y="18" width="14" height="3" rx="1" fill="{accent}" opacity="0.45"></rect>
          <rect x="0"  y="26" width="32" height="4" rx="1" fill="{accent}" opacity="0.95"></rect>
        </svg>'''

    cards_html = "".join(f'''
        <a class="zk-home-card" href="?page={r["key"]}_dashboard" target="_self">
            <div class="zk-home-card-accent" style="background:{r["accent"]}"></div>
            <div class="zk-home-card-mini">{_mini_stock(r["accent"])}</div>
            <div class="zk-home-card-eyebrow">Établissement {idx+1}</div>
            <div class="zk-home-card-name">{r["nom"]}</div>
            <div class="zk-home-card-type">{r["type"]}</div>
            <div class="zk-home-card-cta">Accéder &nbsp;→</div>
        </a>''' for idx, r in enumerate(RESTAURANTS))
    st.markdown(f'<div class="zk-home-grid">{cards_html}</div>', unsafe_allow_html=True)

    # ── Outils Groupe WAC ──
    section("Outils Groupe WAC")
    access_items = [
        ("groupe_catalogue", "Catalogue produits", "Référentiel des 729 références"),
        ("groupe_prix",      "Évolution des prix", "Suivi des variations tarifaires"),
        ("groupe_dashboard", "Vue consolidée",     "KPIs et CA des 4 enseignes"),
    ]
    access_html = "".join(f'''
        <a class="zk-home-access" href="?page={pid}" target="_self">
            <div class="zk-home-access-eyebrow">Groupe WAC</div>
            <div class="zk-home-access-name">{label}</div>
            <div class="zk-home-access-sub">{sub}</div>
        </a>''' for pid, label, sub in access_items)
    st.markdown(f'<div class="zk-home-access-grid">{access_html}</div>', unsafe_allow_html=True)

    # ── Footer brand ──
    st.markdown('''
    <div class="zk-footer">
        <span class="zk-footer-mark">Zaiko</span>
        <span class="zk-footer-bar"></span>
        <span class="zk-footer-tag">Le stock bouge. Zaiko s'adapte.</span>
    </div>
    ''', unsafe_allow_html=True)


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

def render_fiche_produit(prod, cats, cat_labels):
    if st.button("← Retour au catalogue", key="back_to_catalogue"):
        st.session_state.pop("editing_product_id", None)
        st.rerun()

    page_header(
        "Fiche produit",
        prod["nom"],
        f'{prod.get("categorie_nom") or "Sans catégorie"} · {prod["unite"]}',
    )

    section("Modifier la référence")

    with st.form("fiche_edit_form"):
        e1, e2, e3 = st.columns([2, 1, 1])
        with e1:
            nom_edit = st.text_input("Nom de la référence *", value=prod["nom"])
        with e2:
            cat_index = cat_labels.index(prod["categorie_nom"]) if prod.get("categorie_nom") in cat_labels else 0
            cat_edit = st.selectbox("Catégorie *", cat_labels, index=cat_index)
        with e3:
            fmt_index = FORMATS_PREDEFINIS.index(prod["unite"]) if prod["unite"] in FORMATS_PREDEFINIS else 0
            fmt_edit = st.selectbox("Conditionnement *", FORMATS_PREDEFINIS, index=fmt_index)

        e4, e5 = st.columns([1, 2])
        with e4:
            prix_edit = st.number_input(
                "Prix unitaire (€)",
                min_value=0.0, step=0.5, format="%.2f",
                value=float(prod["prix_unitaire"] or 0.0),
            )
        with e5:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            confirm_delete = st.checkbox("Confirmer la suppression de cette référence")

        b1, b2 = st.columns(2)
        with b1:
            save_btn = st.form_submit_button("Valider les modifications", use_container_width=True)
        with b2:
            delete_btn = st.form_submit_button("Supprimer la référence", use_container_width=True)

        if save_btn:
            if nom_edit.strip():
                cid_edit = cats[cat_labels.index(cat_edit)]["id"]
                db.update_produit(prod["id"], nom_edit.strip(), cid_edit, fmt_edit, prix_edit)
                st.session_state.pop("editing_product_id", None)
                st.success("Modifications enregistrées.")
                st.rerun()
            else:
                st.error("Le nom de la référence est requis.")
        elif delete_btn:
            if confirm_delete:
                db.archive_produit(prod["id"])
                st.session_state.pop("editing_product_id", None)
                st.success("Référence supprimée.")
                st.rerun()
            else:
                st.error("Coche « Confirmer la suppression » avant de supprimer.")

    histo = db.get_historique_prix(produit_id=prod["id"])
    histo_chrono = sorted(histo, key=lambda h: h["date_changement"])
    changes = [h for h in histo_chrono if float(h["ancien_prix"]) != float(h["nouveau_prix"])]

    if changes:
        section("Historique des prix de cette référence")

        dates = [h["date_changement"] for h in histo_chrono]
        prix = [h["nouveau_prix"] for h in histo_chrono]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=prix,
            mode="lines+markers",
            line=dict(color=NAVY, width=2.5, shape="hv"),
            marker=dict(color=GOLD, size=9, line=dict(color=NAVY, width=1.5)),
            hovertemplate="%{x}<br>%{y:.2f} €<extra></extra>",
        ))
        plotly_layout(fig, height=280)
        fig.update_yaxes(title=None, ticksuffix=" €")
        fig.update_xaxes(title=None)
        st.plotly_chart(fig, use_container_width=True)

        if st.button("Voir le détail complet de l'évolution des prix", key="goto_prix_from_fiche"):
            st.session_state.viewing_price_product_id = prod["id"]
            st.session_state.pop("editing_product_id", None)
            st.query_params.update({"page": "groupe_prix"})
            st.rerun()


def render_groupe_catalogue():
    cats = db.get_categories()
    cat_labels = [c["nom"] for c in cats]
    produits = db.get_produits()

    editing_id = st.session_state.get("editing_product_id")
    if editing_id:
        prod = next((p for p in produits if p["id"] == editing_id), None)
        if prod:
            render_fiche_produit(prod, cats, cat_labels)
            return
        st.session_state.pop("editing_product_id", None)

    page_header("Groupe WAC", "Catalogue produits",
                "Référentiel commun à tous les établissements")

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
                key="cat_search",
            )
        with f2:
            cat_filter = st.selectbox(
                "Catégorie",
                ["Toutes catégories"] + cats_dispos,
                label_visibility="collapsed",
                key="cat_filter",
            )
        with f3:
            fmt_filter = st.selectbox(
                "Conditionnement",
                ["Tous conditionnements"] + formats_dispos,
                label_visibility="collapsed",
                key="fmt_filter",
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
                count_label = f'{len(items)} référence{"s" if len(items) > 1 else ""}'

                st.markdown(f'''
                <div class="zk-cat-bar">
                    <div class="zk-cat-bar-title">{cat_nom}</div>
                    <div class="zk-cat-bar-count">{count_label}</div>
                </div>
                ''', unsafe_allow_html=True)

                for p in items:
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 0.8])
                    with c1:
                        st.markdown(f'<div class="zk-row-name">{p["nom"]}</div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f'<div class="zk-row-format">{p["unite"]}</div>', unsafe_allow_html=True)
                    with c3:
                        if not p["prix_unitaire"] or float(p["prix_unitaire"]) == 0:
                            st.markdown('<div class="zk-row-price zk-no-price">prix à définir</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="zk-row-price">{p["prix_unitaire"]:.2f} €</div>', unsafe_allow_html=True)
                    with c4:
                        if st.button("Ouvrir", key=f"open_prod_{p['id']}", use_container_width=True):
                            st.session_state.editing_product_id = p["id"]
                            st.rerun()
                st.markdown('<div class="zk-cat-sep"></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="zk-cat-empty">Aucune référence ne correspond aux filtres.</div>',
                unsafe_allow_html=True,
            )

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
    viewing_id = st.session_state.get("viewing_price_product_id")
    if viewing_id:
        _render_fiche_prix(viewing_id)
        return

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

    # Agréger par produit (sur les vrais changements uniquement)
    produits_map: dict = {}
    for h in changements:
        pid = h["produit_id"]
        if pid not in produits_map:
            produits_map[pid] = {
                "id": pid,
                "nom": h["produit_nom"],
                "categorie": h["categorie_nom"] or "Sans catégorie",
                "unite": h["unite"],
                "changements": [],
            }
        produits_map[pid]["changements"].append(h)

    for data in produits_map.values():
        chrono = sorted(data["changements"], key=lambda h: h["date_changement"])
        data["prix_initial"] = float(chrono[0]["ancien_prix"])
        data["prix_actuel"] = float(chrono[-1]["nouveau_prix"])
        data["nb_changements"] = len(chrono)
        data["derniere_date"] = chrono[-1]["date_changement"]
        if data["prix_initial"] > 0:
            data["variation_totale"] = (data["prix_actuel"] - data["prix_initial"]) / data["prix_initial"] * 100
        else:
            data["variation_totale"] = 0.0

    # Tri par défaut : dernière modification (plus récent en haut)
    produits_list = sorted(produits_map.values(), key=lambda x: x["derniere_date"], reverse=True)

    # 4 KPIs
    refs_concernees = len(produits_map)
    total_changements = len(changements)
    derniere_date = produits_list[0]["derniere_date"] if produits_list else "—"
    variations_totales = [d["variation_totale"] for d in produits_list if d["prix_initial"] > 0]
    var_moyenne = sum(variations_totales) / len(variations_totales) if variations_totales else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi("Références concernées", str(refs_concernees), "ayant changé de prix")
    with k2: kpi("Total des changements", str(total_changements), "depuis la mise en service")
    with k3: kpi("Dernière modification", derniere_date, accent="navy")
    with k4:
        signe = "+" if var_moyenne >= 0 else ""
        kpi("Variation moyenne", f"{signe}{var_moyenne:.1f} %", "sur toutes les références", accent="navy")

    # Filtres
    cats_dispos = sorted({d["categorie"] for d in produits_list})
    f1, f2 = st.columns([2, 1])
    with f1:
        recherche = st.text_input(
            "Rechercher une référence",
            placeholder="Rechercher une référence…",
            label_visibility="collapsed",
            key="prix_search",
        )
    with f2:
        cat_filter = st.selectbox(
            "Catégorie",
            ["Toutes catégories"] + cats_dispos,
            label_visibility="collapsed",
            key="prix_cat_filter",
        )

    terme = recherche.strip().lower()
    produits_filtres = [
        d for d in produits_list
        if (not terme or terme in d["nom"].lower())
        and (cat_filter == "Toutes catégories" or d["categorie"] == cat_filter)
    ]

    if not produits_filtres:
        st.markdown(
            '<div class="zk-cat-empty">Aucune référence ne correspond aux filtres.</div>',
            unsafe_allow_html=True,
        )
        return

    # En-tête du tableau
    st.markdown('''
    <div class="zk-prix-head">
        <div>Référence</div>
        <div>Catégorie · Format</div>
        <div>Évolution</div>
        <div>Variation</div>
        <div>Modifs</div>
        <div>Dernière modif</div>
        <div></div>
    </div>
    ''', unsafe_allow_html=True)

    # Lignes du tableau (mix HTML + bouton Streamlit)
    for d in produits_filtres:
        var = d["variation_totale"]
        if var > 0:
            cls, signe_var = "up", "+"
        elif var < 0:
            cls, signe_var = "down", ""
        else:
            cls, signe_var = "flat", ""

        c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1.5, 1.5, 0.8, 0.6, 0.9, 0.8])
        with c1:
            st.markdown(f'<div class="zk-prix-name">{d["nom"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="zk-prix-meta">{d["categorie"]} · {d["unite"]}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(
                f'<div class="zk-prix-evol">{d["prix_initial"]:.2f} € → {d["prix_actuel"]:.2f} €</div>',
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f'<div class="zk-prix-var {cls}">{signe_var}{var:.1f} %</div>',
                unsafe_allow_html=True,
            )
        with c5:
            st.markdown(f'<div class="zk-prix-meta">{d["nb_changements"]}</div>', unsafe_allow_html=True)
        with c6:
            st.markdown(f'<div class="zk-prix-meta">{d["derniere_date"]}</div>', unsafe_allow_html=True)
        with c7:
            if st.button("Détail", key=f"prix_detail_{d['id']}", use_container_width=True):
                st.session_state.viewing_price_product_id = d["id"]
                st.rerun()


def _render_fiche_prix(produit_id: int):
    if st.button("← Retour à l'évolution des prix", key="back_to_prix"):
        st.session_state.pop("viewing_price_product_id", None)
        st.rerun()

    historique = db.get_historique_prix(produit_id=produit_id)
    if not historique:
        st.warning("Aucune donnée pour cette référence.")
        return

    histo_chrono = sorted(historique, key=lambda h: h["date_changement"])
    prod_nom = histo_chrono[0]["produit_nom"]
    categorie = histo_chrono[0]["categorie_nom"] or "Sans catégorie"
    unite = histo_chrono[0]["unite"]

    page_header("Évolution des prix", prod_nom, f"{categorie} · {unite}")

    changements = [h for h in histo_chrono if float(h["ancien_prix"]) != float(h["nouveau_prix"])]

    prix_initial = float(histo_chrono[0]["ancien_prix"])
    prix_actuel = float(histo_chrono[-1]["nouveau_prix"])
    nb_changements = len(changements)
    if prix_initial > 0:
        variation_totale = (prix_actuel - prix_initial) / prix_initial * 100
    else:
        variation_totale = 0.0

    signe = "+" if variation_totale >= 0 else ""
    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi("Prix initial", f"{prix_initial:.2f} €", "point d'ancrage")
    with k2: kpi("Prix actuel", f"{prix_actuel:.2f} €", "tarif en vigueur")
    with k3: kpi("Variation totale", f"{signe}{variation_totale:.1f} %", "depuis le début", accent="navy")
    with k4: kpi("Changements", str(nb_changements), "enregistrés")

    # Courbe Plotly (tous les points de l'historique, y compris ancrage initial)
    dates = [h["date_changement"] for h in histo_chrono]
    prix_vals = [float(h["nouveau_prix"]) for h in histo_chrono]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=prix_vals,
        mode="lines+markers",
        line=dict(color=NAVY, width=2.5, shape="hv"),
        marker=dict(color=GOLD, size=9, line=dict(color=NAVY, width=1.5)),
        hovertemplate="%{x}<br>%{y:.2f} €<extra></extra>",
    ))
    plotly_layout(fig, height=320)
    fig.update_yaxes(title=None, ticksuffix=" €")
    fig.update_xaxes(title=None)
    st.plotly_chart(fig, use_container_width=True)

    # Détail chronologique
    section("Historique détaillé")
    lignes_html = []
    for h in histo_chrono:
        ancien = float(h["ancien_prix"])
        nouveau = float(h["nouveau_prix"])
        if ancien == 0:
            var_pct = 0.0
        else:
            var_pct = (nouveau - ancien) / ancien * 100
        if var_pct > 0:
            cls, signe_var = "up", "+"
        elif var_pct < 0:
            cls, signe_var = "down", ""
        else:
            cls, signe_var = "flat", ""
        lignes_html.append(f'''
            <div class="zk-fiche-price-row">
                <div>{h["date_changement"]}</div>
                <div class="zk-prix-evol">{ancien:.2f} € → {nouveau:.2f} €</div>
                <div class="zk-prix-var {cls}">{signe_var}{var_pct:.1f} %</div>
            </div>
        ''')

    st.markdown(f'''
    <div class="zk-fiche-price-block">
        <div class="zk-fiche-price-head">
            <div>Date</div>
            <div>Évolution</div>
            <div>Variation</div>
        </div>
        {"".join(lignes_html)}
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  GROUPE WAC — FICHES TECHNIQUES
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — HEADER BANNER
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_banner(resto: dict):
    accent = resto["accent"]
    motif = f'''<svg class="zk-resto-motif" viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <g fill="{accent}">
        <rect x="20"  y="20"  width="120" height="10" rx="2" opacity="0.18"></rect>
        <rect x="40"  y="38"  width="80"  height="8"  rx="2" opacity="0.12"></rect>
        <rect x="60"  y="54"  width="100" height="8"  rx="2" opacity="0.10"></rect>
        <rect x="20"  y="72"  width="120" height="10" rx="2" opacity="0.18"></rect>
      </g>
    </svg>'''
    st.markdown(f'''
    <div class="zk-resto-banner">
        <div class="zk-resto-accent-bar" style="background:{accent}"></div>
        {motif}
        <div class="zk-resto-eyebrow">Établissement</div>
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
                        <div class="zk-alert-meta">{a["quantite"]:.1f} {a["unite"]} · seuil {a["seuil_alerte"]:.0f}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="zk-empty-ok">Tous les stocks sont au-dessus des seuils.</div>',
                        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — INVENTAIRE (saisie inline par lieu : bar / réserve)
# ═══════════════════════════════════════════════════════════════════════════════

def _save_qte_callback(rid, pid, lieu, key):
    """Callback déclenché à chaque changement d'un number_input de qté."""
    val = st.session_state.get(key)
    if val is None:
        return
    try:
        db.set_inventaire_ligne(rid, pid, lieu, float(val))
    except Exception as e:
        try:
            st.toast(f"Erreur enregistrement : {e}", icon=None)
        except Exception:
            pass


def render_resto_inventaire(resto: dict):
    rid = resto["id"]

    # Si fiche stock ouverte
    viewing_pid = st.session_state.get("viewing_stock_pid")
    viewing_resto = st.session_state.get("viewing_stock_resto")
    if viewing_pid and viewing_resto == rid:
        render_fiche_stock(resto, viewing_pid)
        return

    page_header(resto["type"], "Inventaire",
                "Saisie directe par lieu : bar et réserve")
    render_resto_banner(resto)

    inv = db.get_inventaire_resto(rid)
    kpis = db.get_kpis_inventaire(rid)

    # ── 4 KPIs ──
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Références en stock", str(kpis["nb_refs"]), "qté > 0")
    with c2: kpi("Valeur totale stock", f"{kpis['valeur_totale']:,.2f} €", "tous lieux confondus", accent="navy")
    with c3:
        kpi("Alertes", str(kpis["nb_alertes"]), "sous seuil",
            accent="red" if kpis["nb_alertes"] else "success")
    with c4: kpi("Dernière saisie", kpis["derniere_saisie"], accent="navy")

    # ── Filtres ──
    cats_dispos = sorted({i["categorie_nom"] for i in inv if i["categorie_nom"]})
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        recherche = st.text_input(
            "Rechercher", placeholder="Rechercher une référence…",
            label_visibility="collapsed", key=f"inv_search_{rid}",
        )
    with f2:
        cat_filter = st.selectbox(
            "Catégorie", ["Toutes catégories"] + cats_dispos,
            label_visibility="collapsed", key=f"inv_cat_{rid}",
        )
    with f3:
        lieu_filter = st.selectbox(
            "Lieu", ["Tous lieux", "Bar uniquement", "Réserve uniquement"],
            label_visibility="collapsed", key=f"inv_lieu_{rid}",
        )

    # ── Application filtres ──
    terme = recherche.strip().lower()
    inv_filtres = [
        i for i in inv
        if (not terme or terme in i["nom"].lower())
        and (cat_filter == "Toutes catégories" or i["categorie_nom"] == cat_filter)
    ]

    show_bar = lieu_filter in ("Tous lieux", "Bar uniquement")
    show_res = lieu_filter in ("Tous lieux", "Réserve uniquement")

    # ── Groupement par catégorie ──
    inv_par_cat = {}
    for i in inv_filtres:
        key = i["categorie_nom"] or "Sans catégorie"
        inv_par_cat.setdefault(key, []).append(i)

    if not inv_par_cat:
        st.markdown(
            '<div class="zk-cat-empty">Aucune référence ne correspond aux filtres.</div>',
            unsafe_allow_html=True,
        )
    else:
        for cat_nom in sorted(inv_par_cat.keys()):
            items = inv_par_cat[cat_nom]
            count_label = f'{len(items)} référence{"s" if len(items) > 1 else ""}'

            st.markdown(f'''
            <div class="zk-cat-bar">
                <div class="zk-cat-bar-title">{cat_nom}</div>
                <div class="zk-cat-bar-count">{count_label}</div>
            </div>
            ''', unsafe_allow_html=True)

            # En-tête colonnes
            st.markdown(f'''
            <div class="zk-inv-head">
                <div>Référence</div>
                <div>Format</div>
                <div>{"Bar" if show_bar else ""}</div>
                <div>{"Réserve" if show_res else ""}</div>
                <div>Total</div>
                <div>Valeur</div>
                <div></div>
            </div>
            ''', unsafe_allow_html=True)

            for p in items:
                pid = p["produit_id"]
                qte_total = float(p["qte_total"] or 0)
                valeur = float(p["valeur"] or 0)
                seuil = float(p["seuil_alerte"] or 0)
                en_alerte = qte_total > 0 and qte_total < seuil

                c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1, 1, 1, 0.7, 0.9, 0.7])
                with c1:
                    name_class = "zk-row-name"
                    label = p["nom"]
                    if en_alerte:
                        label = f'{label} <span class="zk-inv-alert-tag">alerte</span>'
                    st.markdown(f'<div class="{name_class}">{label}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="zk-row-format">{p["unite"]}</div>', unsafe_allow_html=True)
                # Suffixe basé sur le filtre lieu pour éviter les collisions de keys
                # quand on bascule entre Tous / Bar / Réserve
                lieu_tag = lieu_filter.split()[0].lower() if lieu_filter != "Tous lieux" else "all"
                with c3:
                    if show_bar:
                        key_bar = f"inv_qte_bar_{lieu_tag}_{rid}_{pid}"
                        st.number_input(
                            "bar", min_value=0.0, step=0.5, format="%.1f",
                            value=float(p["qte_bar"] or 0),
                            key=key_bar, label_visibility="collapsed",
                            on_change=_save_qte_callback,
                            args=(rid, pid, "bar", key_bar),
                        )
                    else:
                        st.markdown(f'<div class="zk-row-format">{p["qte_bar"]:.1f}</div>', unsafe_allow_html=True)
                with c4:
                    if show_res:
                        key_res = f"inv_qte_res_{lieu_tag}_{rid}_{pid}"
                        st.number_input(
                            "res", min_value=0.0, step=0.5, format="%.1f",
                            value=float(p["qte_reserve"] or 0),
                            key=key_res, label_visibility="collapsed",
                            on_change=_save_qte_callback,
                            args=(rid, pid, "reserve", key_res),
                        )
                    else:
                        st.markdown(f'<div class="zk-row-format">{p["qte_reserve"]:.1f}</div>', unsafe_allow_html=True)
                with c5:
                    cls = "zk-row-format" + (" zk-inv-alert-num" if en_alerte else "")
                    st.markdown(f'<div class="{cls}">{qte_total:.1f}</div>', unsafe_allow_html=True)
                with c6:
                    val_text = f"{valeur:.2f} €" if valeur > 0 else "—"
                    st.markdown(f'<div class="zk-row-price">{val_text}</div>', unsafe_allow_html=True)
                with c7:
                    if st.button("Fiche", key=f"open_stock_{rid}_{pid}", use_container_width=True):
                        st.session_state.viewing_stock_pid = pid
                        st.session_state.viewing_stock_resto = rid
                        st.rerun()

            st.markdown('<div class="zk-cat-sep"></div>', unsafe_allow_html=True)

    # ── Clôture mensuelle ──
    section("Clôture mensuelle")
    today = date.today()
    mois_default = today.strftime("%Y-%m")

    cc1, cc2, cc3 = st.columns([1, 2, 1])
    with cc1:
        mois_input = st.text_input(
            "Mois à clôturer (YYYY-MM)", value=mois_default,
            key=f"cloture_mois_{rid}",
        )
    with cc2:
        st.markdown(f'<div class="zk-help-line">Crée un snapshot figé du stock à ce jour pour le mois <b>{mois_input}</b>. Si un snapshot existe déjà pour ce mois, il sera <b>écrasé</b>.</div>', unsafe_allow_html=True)
    with cc3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Clôturer le mois", key=f"btn_cloture_{rid}", use_container_width=True):
            if re.match(r"^\d{4}-(0[1-9]|1[0-2])$", mois_input or ""):
                db.cloturer_inventaire_mois(rid, mois_input)
                st.success(f"Inventaire {mois_input} clôturé. Visible dans l'historique.")
                st.rerun()
            else:
                st.error("Format attendu : YYYY-MM (exemple : 2026-05).")


def render_fiche_stock(resto: dict, produit_id: int):
    rid = resto["id"]
    prod = db.get_produit(produit_id)
    if not prod:
        st.session_state.pop("viewing_stock_pid", None)
        st.session_state.pop("viewing_stock_resto", None)
        st.rerun()
        return

    if st.button("← Retour à l'inventaire", key="back_inv"):
        st.session_state.pop("viewing_stock_pid", None)
        st.session_state.pop("viewing_stock_resto", None)
        st.rerun()

    page_header(
        resto["nom"], prod["nom"],
        f'{prod.get("categorie_nom") or "Sans catégorie"} · {prod["unite"]}',
    )

    stock = db.get_inventaire_produit(rid, produit_id)
    qte_total = stock["qte_bar"] + stock["qte_reserve"]
    prix = float(prod.get("prix_unitaire") or 0)
    valeur = qte_total * prix
    seuil = float(prod.get("seuil_alerte") or 0)
    en_alerte = qte_total > 0 and qte_total < seuil

    # KPIs
    k1, k2, k3 = st.columns(3)
    with k1: kpi("Stock total", f"{qte_total:.1f}", f"unité : {prod['unite']}")
    with k2: kpi("Valeur stock", f"{valeur:.2f} €", f"prix unitaire : {prix:.2f} €", accent="navy")
    with k3:
        kpi("État", "Alerte" if en_alerte else "OK",
            f"seuil : {seuil:.0f}",
            accent="red" if en_alerte else "success")

    # Saisie par lieu
    section("Quantité par lieu")
    with st.form(f"fiche_stock_form_{produit_id}"):
        c1, c2 = st.columns(2)
        with c1:
            qte_bar_new = st.number_input(
                "Bar", min_value=0.0, step=0.5, format="%.2f",
                value=float(stock["qte_bar"]),
            )
            note_bar = st.text_input("Note bar (optionnel)", value=stock.get("note_bar", ""))
        with c2:
            qte_res_new = st.number_input(
                "Réserve", min_value=0.0, step=0.5, format="%.2f",
                value=float(stock["qte_reserve"]),
            )
            note_res = st.text_input("Note réserve (optionnel)", value=stock.get("note_reserve", ""))

        if st.form_submit_button("Enregistrer", use_container_width=True):
            db.set_inventaire_ligne(rid, produit_id, "bar", qte_bar_new, note_bar)
            db.set_inventaire_ligne(rid, produit_id, "reserve", qte_res_new, note_res)
            st.success("Stock mis à jour.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — HISTORIQUE INVENTAIRE
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_historique(resto: dict):
    rid = resto["id"]

    # Si on visualise le détail d'un mois
    viewing_snap = st.session_state.get("viewing_snap_id")
    viewing_resto = st.session_state.get("viewing_snap_resto")
    if viewing_snap and viewing_resto == rid:
        render_snapshot_detail(resto, viewing_snap)
        return

    page_header(resto["type"], "Historique inventaire",
                "Valorisation et snapshots mensuels figés")
    render_resto_banner(resto)

    kpis = db.get_kpis_historique_inventaire(rid)
    var = kpis["variation"]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        sub = f'mois {kpis["dernier_mois"]}' if kpis["dernier_mois"] else "aucun snapshot"
        kpi("Valeur dernier inventaire", f'{kpis["valeur_dernier"]:,.2f} €', sub)
    with k2:
        if var is None:
            kpi("Variation vs M-1", "—", "données insuffisantes", accent="navy")
        else:
            signe = "+" if var >= 0 else ""
            kpi("Variation vs M-1", f"{signe}{var:.1f} %", "valorisation", accent="navy")
    with k3: kpi("Références inventoriées", str(kpis["nb_refs"]), "dans le dernier")
    with k4: kpi("Moyenne 3 derniers mois", f'{kpis["moyenne_3m"]:,.2f} €', "valorisation", accent="navy")

    # Liste des snapshots
    section("Inventaires mensuels")
    snaps = db.get_inventaires_mensuels(rid)

    if not snaps:
        st.markdown(
            '<div class="zk-cat-empty">Aucun inventaire mensuel clôturé pour le moment. Va dans la page Inventaire pour clôturer le mois en cours.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('''
    <div class="zk-fiches-head">
        <div>Mois</div>
        <div>Date clôture</div>
        <div>Valeur totale</div>
        <div>Références</div>
        <div>Variation</div>
        <div></div>
        <div></div>
    </div>
    ''', unsafe_allow_html=True)

    for idx, s in enumerate(snaps):
        valeur = float(s["valeur_totale"] or 0)
        # Variation vs snapshot suivant (M-1)
        var_pct = None
        if idx + 1 < len(snaps):
            prev = float(snaps[idx + 1]["valeur_totale"] or 0)
            if prev > 0:
                var_pct = (valeur - prev) / prev * 100

        if var_pct is None:
            var_text, var_cls = "—", "flat"
        elif var_pct > 0:
            var_text, var_cls = f"+{var_pct:.1f} %", "up"
        elif var_pct < 0:
            var_text, var_cls = f"{var_pct:.1f} %", "down"
        else:
            var_text, var_cls = "0.0 %", "flat"

        c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1, 1, 1, 0.7, 0.7, 0.8])
        with c1:
            st.markdown(f'<div class="zk-prix-name">{s["mois"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="zk-prix-meta">{s["date_cloture"]}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="zk-prix-evol">{valeur:,.2f} €</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="zk-prix-meta">{s["nb_refs"]}</div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="zk-prix-var {var_cls}">{var_text}</div>', unsafe_allow_html=True)
        with c6:
            st.markdown('<div></div>', unsafe_allow_html=True)
        with c7:
            if st.button("Détail", key=f"open_snap_{s['id']}", use_container_width=True):
                st.session_state.viewing_snap_id = s["id"]
                st.session_state.viewing_snap_resto = rid
                st.rerun()


def render_snapshot_detail(resto: dict, snapshot_id: int):
    rid = resto["id"]

    # Si on visualise un produit dans le snapshot
    viewing_snap_pid = st.session_state.get("viewing_snap_pid")
    if viewing_snap_pid:
        render_snapshot_produit_detail(resto, snapshot_id, viewing_snap_pid)
        return

    snap = db.get_inventaire_mensuel(snapshot_id)
    if not snap:
        st.session_state.pop("viewing_snap_id", None)
        st.session_state.pop("viewing_snap_resto", None)
        st.rerun()
        return

    if st.button("← Retour à l'historique", key="back_hist"):
        st.session_state.pop("viewing_snap_id", None)
        st.session_state.pop("viewing_snap_resto", None)
        st.session_state.pop("viewing_snap_pid", None)
        st.rerun()

    page_header(
        f"Inventaire {snap['mois']}",
        f"Snapshot du {snap['date_cloture']}",
        f'{resto["nom"]} · {resto["type"]}',
    )

    valeur = float(snap["valeur_totale"] or 0)
    nb_refs = int(snap["nb_refs"] or 0)

    k1, k2, k3 = st.columns(3)
    with k1: kpi("Valeur totale", f"{valeur:,.2f} €", "prix figés au jour de clôture")
    with k2: kpi("Références", str(nb_refs), "produits inventoriés", accent="navy")
    with k3: kpi("Date de clôture", snap["date_cloture"], accent="navy")

    section("Détail par référence")
    lignes = db.get_snapshot_lignes(snapshot_id)

    if not lignes:
        st.markdown(
            '<div class="zk-cat-empty">Aucune ligne dans ce snapshot.</div>',
            unsafe_allow_html=True,
        )
        return

    # Groupement par catégorie
    par_cat = {}
    for l in lignes:
        par_cat.setdefault(l["categorie_nom"] or "Sans catégorie", []).append(l)

    for cat_nom in sorted(par_cat.keys()):
        items = par_cat[cat_nom]
        count_label = f'{len(items)} référence{"s" if len(items) > 1 else ""}'
        st.markdown(f'''
        <div class="zk-cat-bar">
            <div class="zk-cat-bar-title">{cat_nom}</div>
            <div class="zk-cat-bar-count">{count_label}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="zk-inv-snap-head">
            <div>Référence</div>
            <div>Format</div>
            <div>Bar</div>
            <div>Réserve</div>
            <div>Total</div>
            <div>Prix figé</div>
            <div>Valeur</div>
            <div></div>
        </div>
        ''', unsafe_allow_html=True)

        for l in items:
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([2, 0.8, 0.6, 0.6, 0.6, 0.7, 0.8, 0.7])
            with c1:
                st.markdown(f'<div class="zk-row-name">{l["produit_nom"]}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="zk-row-format">{l["unite"]}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="zk-row-format">{l["qte_bar"]:.1f}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="zk-row-format">{l["qte_reserve"]:.1f}</div>', unsafe_allow_html=True)
            with c5:
                st.markdown(f'<div class="zk-prix-evol">{l["qte_total"]:.1f}</div>', unsafe_allow_html=True)
            with c6:
                st.markdown(f'<div class="zk-row-format">{l["prix_snapshot"]:.2f} €</div>', unsafe_allow_html=True)
            with c7:
                st.markdown(f'<div class="zk-row-price">{l["valeur"]:.2f} €</div>', unsafe_allow_html=True)
            with c8:
                if st.button("Détail", key=f"open_snap_p_{snapshot_id}_{l['produit_id']}", use_container_width=True):
                    st.session_state.viewing_snap_pid = l["produit_id"]
                    st.rerun()
        st.markdown('<div class="zk-cat-sep"></div>', unsafe_allow_html=True)


def render_snapshot_produit_detail(resto: dict, snapshot_id: int, produit_id: int):
    snap = db.get_inventaire_mensuel(snapshot_id)
    prod = db.get_produit(produit_id)
    if not snap or not prod:
        st.session_state.pop("viewing_snap_pid", None)
        st.rerun()
        return

    if st.button("← Retour au détail du mois", key="back_snap_detail"):
        st.session_state.pop("viewing_snap_pid", None)
        st.rerun()

    page_header(
        f"Inventaire {snap['mois']}",
        prod["nom"],
        f'{prod.get("categorie_nom") or "Sans catégorie"} · {prod["unite"]} · {resto["nom"]}',
    )

    detail = db.get_snapshot_produit(snapshot_id, produit_id)

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi("Quantité bar", f'{detail["qte_bar"]:.1f}', f"unité : {prod['unite']}")
    with k2: kpi("Quantité réserve", f'{detail["qte_reserve"]:.1f}', f"unité : {prod['unite']}", accent="navy")
    with k3: kpi("Total", f'{detail["qte_total"]:.1f}', "tous lieux", accent="navy")
    with k4: kpi("Valeur figée", f'{detail["valeur"]:.2f} €', f'prix : {detail["prix_snapshot"]:.2f} €', accent="navy")

    section("Contexte")
    st.markdown(
        f'<div class="zk-help-line">Ce détail est <b>figé</b> à la date de clôture du {snap["date_cloture"]}. '
        f'Le prix unitaire courant peut être différent (modifications postérieures dans le catalogue).</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANT — PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

PERIODES_PERF = ["Semaine en cours", "Mois en cours", "Trimestre en cours", "Année en cours"]


def _periode_dates(label: str, today: date | None = None):
    """(debut, fin, debut_prev, fin_prev) en bornes incluses pour la période demandée."""
    today = today or date.today()
    if label == "Semaine en cours":
        debut = today - timedelta(days=today.weekday())
        fin = debut + timedelta(days=6)
        debut_prev = debut - timedelta(days=7)
        fin_prev = fin - timedelta(days=7)
    elif label == "Trimestre en cours":
        q = (today.month - 1) // 3
        debut = date(today.year, q * 3 + 1, 1)
        fin = (date(today.year, 12, 31) if q == 3
               else date(today.year, (q + 1) * 3 + 1, 1) - timedelta(days=1))
        if q == 0:
            debut_prev = date(today.year - 1, 10, 1)
            fin_prev = date(today.year - 1, 12, 31)
        else:
            debut_prev = date(today.year, (q - 1) * 3 + 1, 1)
            fin_prev = debut - timedelta(days=1)
    elif label == "Année en cours":
        debut = date(today.year, 1, 1)
        fin = date(today.year, 12, 31)
        debut_prev = date(today.year - 1, 1, 1)
        fin_prev = date(today.year - 1, 12, 31)
    else:  # "Mois en cours" (défaut)
        debut = today.replace(day=1)
        fin = (date(debut.year, 12, 31) if debut.month == 12
               else date(debut.year, debut.month + 1, 1) - timedelta(days=1))
        if debut.month == 1:
            debut_prev = date(debut.year - 1, 12, 1)
            fin_prev = date(debut.year - 1, 12, 31)
        else:
            debut_prev = date(debut.year, debut.month - 1, 1)
            fin_prev = debut - timedelta(days=1)
    return debut, fin, debut_prev, fin_prev


def render_resto_performance(resto: dict):
    rid    = resto["id"]
    accent = resto["accent"]

    page_header(resto["nom"], "Performance",
                "Chiffre d'affaires et ratio matière par période")

    # ─── Sélecteur de période (partagé CA + Ratios) ───────────────────────────
    periode = st.selectbox(
        "Période",
        PERIODES_PERF,
        index=1,  # Mois en cours par défaut
        key=f"perf_periode_{rid}",
    )
    debut, fin, debut_prev, fin_prev = _periode_dates(periode)

    ventes_p  = db.get_ventes_periode(rid, debut, fin)
    ventes_pp = db.get_ventes_periode(rid, debut_prev, fin_prev)

    debut_ytd  = date(date.today().year, 1, 1)
    ventes_ytd = db.get_ventes_periode(rid, debut_ytd, date.today())

    libelle_periode = f"{debut.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}"

    # ─── Chiffre d'affaires ───────────────────────────────────────────────────
    section("Chiffre d'affaires")

    ca_p   = sum(v["montant_reel"] for v in ventes_p)
    ca_pp  = sum(v["montant_reel"] for v in ventes_pp)
    ca_ytd = sum(v["montant_reel"] for v in ventes_ytd)
    delta_ca = ((ca_p - ca_pp) / ca_pp * 100) if ca_pp else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi(f"CA — {periode.lower()}", f"{ca_p:,.0f} €", libelle_periode)
    with c2:
        if ca_pp:
            sign = "+" if delta_ca >= 0 else ""
            kpi("Δ vs période précédente", f"{sign}{delta_ca:.1f}%",
                f"vs {ca_pp:,.0f} €",
                accent="success" if delta_ca >= 0 else "red")
        else:
            kpi("Δ vs période précédente", "—", "pas de données antérieures")
    with c3:
        kpi("CA cumulé année", f"{ca_ytd:,.0f} €",
            f"depuis le 01/01/{debut_ytd.year}")

    if ventes_p:
        df = pd.DataFrame(ventes_p)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date_vente"], y=df["montant_reel"],
            name="CA réel",
            line=dict(color=accent, width=2.5),
            mode="lines+markers",
            marker=dict(size=5, color=accent),
            fill="tozeroy", fillcolor=f"{accent}1A",
        ))
        plotly_layout(fig, height=320)
        st.plotly_chart(fig, use_container_width=True, key=f"chart_ca_{rid}")
    else:
        st.info("Aucune vente enregistrée sur cette période.")

    # ─── Ratios ───────────────────────────────────────────────────────────────
    section("Ratios")

    if ventes_p:
        df = pd.DataFrame(ventes_p)
        total_reel = df["montant_reel"].sum()
        total_theo = df["montant_theorique"].sum()
        ratio = (total_reel / total_theo * 100) if total_theo else 0
        ecart = total_reel - total_theo

        if ventes_pp:
            df_pp   = pd.DataFrame(ventes_pp)
            tr_pp   = df_pp["montant_reel"].sum()
            tt_pp   = df_pp["montant_theorique"].sum()
            ratio_pp = (tr_pp / tt_pp * 100) if tt_pp else 0
            delta_ratio = ratio - ratio_pp
        else:
            ratio_pp = None
            delta_ratio = None

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi("Ratio matière", f"{ratio:.1f}%", "réel / théorique",
                accent="success" if ratio >= 95 else ("gold" if ratio >= 85 else "red"))
        with c2:
            if delta_ratio is not None:
                sign = "+" if delta_ratio >= 0 else ""
                kpi("Δ vs période précédente", f"{sign}{delta_ratio:.1f} pts",
                    f"vs {ratio_pp:.1f}%",
                    accent="success" if delta_ratio >= 0 else "red")
            else:
                kpi("Δ vs période précédente", "—", "pas de données antérieures")
        with c3:
            sign = "+" if ecart >= 0 else ""
            kpi("Écart cumulé", f"{sign}{ecart:,.0f} €",
                "réel − théorique",
                accent="success" if ecart >= 0 else "red")

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
        ))
        plotly_layout(fig, height=320)
        st.plotly_chart(fig, use_container_width=True, key=f"chart_ratio_{rid}")

        df_d = df[["date_vente", "montant_reel", "montant_theorique"]].copy()
        df_d["Ratio"] = (df_d["montant_reel"] / df_d["montant_theorique"] * 100).round(1).astype(str) + "%"
        df_d["Écart (€)"] = (df_d["montant_reel"] - df_d["montant_theorique"]).round(2)
        df_d.columns = ["Date", "CA réel (€)", "CA théorique (€)", "Ratio", "Écart (€)"]
        df_d = df_d.sort_values("Date", ascending=False).reset_index(drop=True)
        st.dataframe(df_d, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée de ratio sur cette période.")

    # ─── Saisie ───────────────────────────────────────────────────────────────
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
#  RESTAURANT — FICHES TECHNIQUES
# ═══════════════════════════════════════════════════════════════════════════════

def render_resto_fiches(resto: dict):
    if st.session_state.get("editing_fiche_resto") == resto["id"]:
        render_fiche_editor(resto)
        return

    page_header(resto["type"], "Fiches techniques",
                "Recettes, coût matière, ratio et coefficient")
    render_resto_banner(resto)

    produits_all = db.get_produits()
    produits_map = {p["id"]: p for p in produits_all}

    for type_fiche, label_titre, label_btn in [
        ("cocktail", "Cocktails", "Nouvelle fiche cocktail"),
        ("plat",     "Plats",     "Nouvelle fiche plat"),
    ]:
        section(label_titre)
        fiches = db.get_fiches(resto["id"], type_filter=type_fiche)

        if fiches:
            st.markdown('''
            <div class="zk-fiches-head">
                <div>Fiche</div>
                <div>Coût matière</div>
                <div>Coût + 10% perte</div>
                <div>Prix vente TTC</div>
                <div>Ratio</div>
                <div>Coefficient</div>
                <div></div>
            </div>
            ''', unsafe_allow_html=True)

            for f in fiches:
                ings_db = db.get_fiche_ingredients(f["id"])
                ingredients = [
                    {**i, "_produit": produits_map.get(i["produit_id"])}
                    for i in ings_db
                ]
                ind = calculer_indicateurs_fiche(
                    ingredients, float(f["prix_vente_ttc"] or 0), float(f["tva"] or 0)
                )

                c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1, 1, 1, 0.7, 0.7, 0.8])
                with c1:
                    st.markdown(f'<div class="zk-prix-name">{f["nom"]}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="zk-prix-evol">{ind["cout_brut"]:.2f} €</div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="zk-prix-evol">{ind["cout_perte"]:.2f} €</div>', unsafe_allow_html=True)
                with c4:
                    pv = float(f["prix_vente_ttc"] or 0)
                    pv_text = f"{pv:.2f} €" if pv > 0 else "—"
                    st.markdown(f'<div class="zk-prix-evol">{pv_text}</div>', unsafe_allow_html=True)
                with c5:
                    ratio_text = f'{ind["ratio"]:.1f} %' if ind["ratio"] > 0 else "—"
                    st.markdown(f'<div class="zk-prix-evol">{ratio_text}</div>', unsafe_allow_html=True)
                with c6:
                    coeff_text = f'×{ind["coefficient"]:.2f}' if ind["coefficient"] > 0 else "—"
                    st.markdown(f'<div class="zk-prix-evol">{coeff_text}</div>', unsafe_allow_html=True)
                with c7:
                    if st.button("Ouvrir", key=f"open_fiche_{f['id']}", use_container_width=True):
                        st.session_state.editing_fiche_id = f["id"]
                        st.session_state.editing_fiche_resto = resto["id"]
                        st.rerun()
            st.markdown('<div class="zk-cat-sep"></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="zk-cat-empty">Aucune fiche {label_titre.lower()} pour le moment.</div>',
                unsafe_allow_html=True,
            )

        if st.button(label_btn, key=f"new_fiche_{type_fiche}_{resto['id']}"):
            st.session_state.editing_fiche_id = "new"
            st.session_state.editing_fiche_type = type_fiche
            st.session_state.editing_fiche_resto = resto["id"]
            st.rerun()


def render_fiche_editor(resto: dict):
    fiche_id = st.session_state.editing_fiche_id
    is_new = (fiche_id == "new")

    draft_key = f"fiche_draft_{fiche_id}_{resto['id']}"
    if draft_key not in st.session_state:
        if is_new:
            type_fiche = st.session_state.get("editing_fiche_type", "cocktail")
            tva_default = 20.0 if type_fiche == "cocktail" else 10.0
            st.session_state[draft_key] = {
                "id": None, "type": type_fiche, "nom": "",
                "prix_vente_ttc": 0.0, "tva": tva_default, "notes": "",
                "ingredients": [], "_next_uid": 1,
            }
        else:
            f = db.get_fiche(fiche_id)
            if not f:
                st.session_state.pop("editing_fiche_id", None)
                st.session_state.pop("editing_fiche_type", None)
                st.session_state.pop("editing_fiche_resto", None)
                st.warning("Cette fiche n'existe plus.")
                st.rerun()
                return
            ings = db.get_fiche_ingredients(fiche_id)
            st.session_state[draft_key] = {
                "id": f["id"], "type": f["type"], "nom": f["nom"],
                "prix_vente_ttc": float(f["prix_vente_ttc"] or 0),
                "tva": float(f["tva"] or 20),
                "notes": f["notes"] or "",
                "ingredients": [
                    {"_uid": k+1, "produit_id": i["produit_id"],
                     "quantite": float(i["quantite"]),
                     "unite_recette": i["unite_recette"]}
                    for k, i in enumerate(ings)
                ],
                "_next_uid": len(ings) + 1,
            }

    draft = st.session_state[draft_key]

    if st.button("← Retour aux fiches techniques", key="back_fiches"):
        st.session_state.pop("editing_fiche_id", None)
        st.session_state.pop("editing_fiche_type", None)
        st.session_state.pop("editing_fiche_resto", None)
        st.session_state.pop(draft_key, None)
        st.rerun()

    type_label = "Fiche cocktail" if draft["type"] == "cocktail" else "Fiche plat"
    title = draft["nom"] if draft["nom"] else f"Nouvelle {type_label.lower()}"
    page_header(type_label, title, f'{resto["nom"]} · {resto["type"]}')

    # ── Informations générales ──
    section("Informations générales")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        nom = st.text_input("Nom de la fiche *", value=draft["nom"], key=f"nom_{draft_key}")
    with c2:
        prix_v = st.number_input("Prix de vente TTC (€)", min_value=0.0, step=0.5,
                                 value=float(draft["prix_vente_ttc"]), format="%.2f",
                                 key=f"pv_{draft_key}")
    with c3:
        tva = st.number_input("TVA (%)", min_value=0.0, step=1.0,
                              value=float(draft["tva"]), format="%.1f",
                              key=f"tva_{draft_key}")
    notes = st.text_area("Notes", value=draft["notes"], height=70, key=f"notes_{draft_key}")
    draft["nom"] = nom.strip()
    draft["prix_vente_ttc"] = float(prix_v)
    draft["tva"] = float(tva)
    draft["notes"] = notes.strip()

    # ── Ingrédients ──
    section("Ingrédients")

    produits = db.get_produits()
    produits_map = {p["id"]: p for p in produits}
    placeholder = "— Choisir une référence —"
    options = [placeholder] + [
        f'{p["nom"]} ({p["categorie_nom"] or "Sans catégorie"} · {p["unite"]})'
        for p in produits
    ]
    pid_by_label = {options[k+1]: produits[k]["id"] for k in range(len(produits))}
    label_by_pid = {produits[k]["id"]: options[k+1] for k in range(len(produits))}

    if draft["ingredients"]:
        st.markdown('''
        <div class="zk-fiches-ing-head">
            <div>Référence</div>
            <div>Quantité</div>
            <div>Unité</div>
            <div>Coût</div>
            <div></div>
        </div>
        ''', unsafe_allow_html=True)

        to_remove = None
        for ing in draft["ingredients"]:
            uid = ing["_uid"]
            c1, c2, c3, c4, c5 = st.columns([3, 0.8, 0.8, 0.9, 0.7])

            current_label = label_by_pid.get(ing["produit_id"], placeholder) if ing["produit_id"] else placeholder
            idx = options.index(current_label) if current_label in options else 0

            with c1:
                new_label = st.selectbox(
                    "ref", options, index=idx,
                    key=f"ing_prod_{draft_key}_{uid}",
                    label_visibility="collapsed",
                )
                ing["produit_id"] = pid_by_label.get(new_label) if new_label != placeholder else None

            with c2:
                ing["quantite"] = float(st.number_input(
                    "qte", min_value=0.0, step=0.5,
                    value=float(ing["quantite"] or 0), format="%.2f",
                    key=f"ing_qte_{draft_key}_{uid}",
                    label_visibility="collapsed",
                ))

            with c3:
                u_idx = UNITES_RECETTE.index(ing["unite_recette"]) if ing["unite_recette"] in UNITES_RECETTE else 0
                ing["unite_recette"] = st.selectbox(
                    "u", UNITES_RECETTE, index=u_idx,
                    key=f"ing_unite_{draft_key}_{uid}",
                    label_visibility="collapsed",
                )

            with c4:
                prod = produits_map.get(ing["produit_id"])
                cout = cout_ingredient(prod, ing["quantite"], ing["unite_recette"]) if prod else None
                if cout is None:
                    st.markdown('<div class="zk-prix-meta">unité incompatible</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="zk-prix-evol">{cout:.2f} €</div>', unsafe_allow_html=True)

            with c5:
                if st.button("Retirer", key=f"ing_rm_{draft_key}_{uid}", use_container_width=True):
                    to_remove = uid

        if to_remove is not None:
            draft["ingredients"] = [i for i in draft["ingredients"] if i["_uid"] != to_remove]
            st.rerun()
    else:
        st.markdown(
            '<div class="zk-cat-empty">Aucun ingrédient. Clique sur « Ajouter un ingrédient ».</div>',
            unsafe_allow_html=True,
        )

    if st.button("Ajouter un ingrédient", key=f"ing_add_{draft_key}"):
        default_unite = "cl" if draft["type"] == "cocktail" else "g"
        draft["ingredients"].append({
            "_uid": draft["_next_uid"],
            "produit_id": None,
            "quantite": 0.0,
            "unite_recette": default_unite,
        })
        draft["_next_uid"] += 1
        st.rerun()

    # ── Indicateurs ──
    section("Indicateurs")
    ingredients_enriched = [
        {**ing, "_produit": produits_map.get(ing["produit_id"])}
        for ing in draft["ingredients"]
    ]
    # Avertir si certains ingrédients ont un prix catalogue à 0 (fausse le coût)
    refs_sans_prix = [
        ing["_produit"]["nom"] for ing in ingredients_enriched
        if ing.get("_produit") and not (ing["_produit"].get("prix_unitaire") or 0)
    ]
    if refs_sans_prix:
        st.markdown(
            f'<div class="zk-warn-line">Attention : {len(refs_sans_prix)} référence(s) avec prix à définir dans le catalogue — '
            f'le coût matière en sera faussé. Réfs concernées : <b>{", ".join(refs_sans_prix[:5])}'
            f'{"…" if len(refs_sans_prix) > 5 else ""}</b></div>',
            unsafe_allow_html=True,
        )
    ind = calculer_indicateurs_fiche(ingredients_enriched, draft["prix_vente_ttc"], draft["tva"])

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        kpi("Coût matière", f'{ind["cout_brut"]:.2f} €', "brut, sans perte")
    with k2:
        kpi("Coût + 10% perte", f'{ind["cout_perte"]:.2f} €', "réaliste", accent="navy")
    with k3:
        kpi("Prix HT", f'{ind["prix_ht"]:.2f} €', f'TVA {draft["tva"]:.0f}%', accent="navy")
    with k4:
        ratio_text = f'{ind["ratio"]:.1f} %' if ind["ratio"] > 0 else "—"
        kpi("Ratio matière", ratio_text, "sur coût + 10% perte")
    with k5:
        coeff_text = f'×{ind["coefficient"]:.2f}' if ind["coefficient"] > 0 else "—"
        kpi("Coefficient", coeff_text, "Prix HT / coût")

    # ── Enregistrement ──
    section("Enregistrement")
    s1, s2 = st.columns(2)
    with s1:
        if st.button("Enregistrer la fiche", use_container_width=True, key=f"save_{draft_key}"):
            if not draft["nom"]:
                st.error("Le nom de la fiche est requis.")
            else:
                payload = [
                    {"produit_id": i["produit_id"],
                     "quantite": i["quantite"],
                     "unite_recette": i["unite_recette"]}
                    for i in draft["ingredients"]
                    if i.get("produit_id")
                ]
                if is_new:
                    new_id = db.create_fiche(
                        resto["id"], draft["type"], draft["nom"],
                        draft["prix_vente_ttc"], draft["tva"], draft["notes"],
                    )
                    db.replace_fiche_ingredients(new_id, payload)
                    new_draft_key = f"fiche_draft_{new_id}_{resto['id']}"
                    st.session_state[new_draft_key] = {**draft, "id": new_id}
                    st.session_state.pop(draft_key, None)
                    st.session_state.editing_fiche_id = new_id
                    st.success("Fiche créée.")
                    st.rerun()
                else:
                    db.update_fiche(
                        draft["id"], draft["nom"],
                        draft["prix_vente_ttc"], draft["tva"], draft["notes"],
                    )
                    db.replace_fiche_ingredients(draft["id"], payload)
                    st.success("Fiche enregistrée.")
                    st.rerun()
    with s2:
        if not is_new:
            confirm = st.checkbox("Confirmer la suppression", key=f"confirm_del_{draft_key}")
            if st.button("Supprimer la fiche", use_container_width=True, key=f"del_{draft_key}"):
                if confirm:
                    db.delete_fiche(draft["id"])
                    st.session_state.pop("editing_fiche_id", None)
                    st.session_state.pop("editing_fiche_resto", None)
                    st.session_state.pop(draft_key, None)
                    st.success("Fiche supprimée.")
                    st.rerun()
                else:
                    st.error("Coche « Confirmer la suppression » avant de supprimer.")


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

_PAGE_STATE_KEYS = {
    "groupe_catalogue": ("editing_product_id",),
    "groupe_prix":      ("viewing_price_product_id",),
}


def _cleanup_state_on_nav(current: str):
    """Nettoie les states 'viewing/editing' quand on change de page."""
    last = st.session_state.get("_last_page")
    if last == current:
        return
    # On quitte une page qui avait des states résidentiels → on les vide
    for page, keys in _PAGE_STATE_KEYS.items():
        if last == page and current != page:
            for k in keys:
                st.session_state.pop(k, None)
    # Pour les sous-pages restos, on nettoie au changement de sous-page
    if last and current and last != current:
        # Si on quitte une page d'inventaire / historique d'un resto donné
        if not current.endswith("_inventaire"):
            st.session_state.pop("viewing_stock_pid", None)
            st.session_state.pop("viewing_stock_resto", None)
        if not current.endswith("_historique"):
            st.session_state.pop("viewing_snap_id", None)
            st.session_state.pop("viewing_snap_resto", None)
            st.session_state.pop("viewing_snap_pid", None)
        if not current.endswith("_fiches"):
            st.session_state.pop("editing_fiche_id", None)
            st.session_state.pop("editing_fiche_type", None)
            st.session_state.pop("editing_fiche_resto", None)
    st.session_state["_last_page"] = current


def route(page: str):
    _cleanup_state_on_nav(page)

    if page == "accueil":          return render_accueil()
    if page == "groupe_dashboard": return render_groupe_dashboard()
    if page == "groupe_catalogue": return render_groupe_catalogue()
    if page == "groupe_prix":      return render_groupe_prix()

    for r in RESTAURANTS:
        key = r["key"]
        if page.startswith(key + "_"):
            sub = page[len(key) + 1:]
            if sub == "dashboard":  return render_resto_dashboard(r)
            if sub == "inventaire": return render_resto_inventaire(r)
            if sub == "historique": return render_resto_historique(r)
            if sub == "performance": return render_resto_performance(r)
            if sub == "ventes":     return render_resto_performance(r)  # alias compat
            if sub == "fiches":     return render_resto_fiches(r)

    render_accueil()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    db.init_db()
    inject_css()
    current = st.query_params.get("page", "accueil")
    render_navbar(current)
    route(current)


if __name__ == "__main__":
    main()
