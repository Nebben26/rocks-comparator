"""
THE ROCKS THROWN COMPARATOR · Signal 05
========================================
Powered by The Fifth Signal

Attacks the congressional copy-trading lie with real data.
Backend unchanged. UI rebuilt for one-screenshot comprehension.

Run locally:
    pip install -r requirements.txt
    streamlit run rocks_comparator.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime, timedelta
from urllib.parse import quote as urlquote

# ===================================================================
# PAGE CONFIG
# ===================================================================
st.set_page_config(
    page_title="Signal 05 · Rocks Thrown Comparator · The Fifth Signal",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===================================================================
# STYLING — brand tokens from thecapitoldossier.com/index.html
# ===================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

/* --- CORE --- */
.stApp {
    background-color: #000000;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
}
.main > div { max-width: 1240px; padding-top: 1rem !important; padding-bottom: 3rem !important; }
[data-testid="stHeader"] { background: #000; height: 0; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stStatusWidget"] { display: none !important; }

/* Kill sidebar entirely — all controls are inline now */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] { display: none !important; }

/* Brand atmosphere — grain + green scanline overlay */
.stApp::before {
    content: ''; position: fixed; inset: 0; pointer-events: none;
    opacity: 0.04; z-index: 9998;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
}
.stApp::after {
    content: ''; position: fixed; inset: 0; pointer-events: none;
    z-index: 9999; mix-blend-mode: overlay;
    background: linear-gradient(180deg, transparent 0%, rgba(0,255,159,0.012) 50%, transparent 100%);
    background-size: 100% 8px;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.025em; color: #ffffff;
    font-weight: 700 !important;
}

/* --- TOOL NAV (matches site nav) --- */
.tnav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 0 16px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    flex-wrap: wrap; gap: 12px;
}
.tnav-left { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.tnav-logo {
    width: 26px; height: 26px; border-radius: 50%;
    border: 1.5px solid #00ff9f; position: relative;
    box-shadow: 0 0 10px rgba(0,255,159,0.5);
    flex-shrink: 0;
}
.tnav-logo::before, .tnav-logo::after {
    content: ''; position: absolute; border-radius: 50%;
    border: 1px solid rgba(0,255,159,0.4);
}
.tnav-logo::before { inset: -5px; }
.tnav-logo::after { inset: -10px; opacity: 0.5; }
.tnav-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 17px; letter-spacing: -0.015em;
}
.tnav-name em { font-style: normal; color: #00ff9f; }
.tnav-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600;
    color: #00ff9f; letter-spacing: 0.22em; text-transform: uppercase;
    padding: 4px 9px; border: 1px solid rgba(0,255,159,0.35);
}
.tnav-cta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; font-weight: 600;
    padding: 9px 16px;
    border: 1px solid rgba(0,255,159,0.35);
    color: #00ff9f;
    letter-spacing: 0.08em; text-transform: uppercase;
    border-radius: 2px; text-decoration: none;
    transition: all 0.3s;
}
.tnav-cta:hover {
    background: #00ff9f; color: #000;
    box-shadow: 0 0 24px rgba(0,255,159,0.55);
}

/* --- KICKER (site's section-kicker pattern) --- */
.kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 600;
    color: #00ff9f;
    letter-spacing: 0.22em; text-transform: uppercase;
    display: flex; align-items: center; gap: 10px;
    margin: 32px 0 14px;
}
.kicker::before {
    content: ''; width: 7px; height: 7px; border-radius: 50%;
    background: #00ff9f; box-shadow: 0 0 8px #00ff9f;
    animation: kpulse 1.8s ease-in-out infinite;
}
@keyframes kpulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

/* --- TOOLBAR --- */
.tbar {
    display: flex; gap: 14px; flex-wrap: wrap;
    align-items: center;
    padding: 12px 0 0;
    margin-bottom: 8px;
}
.tbar-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #6a6a6a;
    letter-spacing: 0.2em; text-transform: uppercase;
}
.pill-row {
    display: flex;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 2px; overflow: hidden;
}
.pill {
    padding: 8px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 500;
    color: #8a8a8a;
    letter-spacing: 0.1em; text-transform: uppercase;
    border-right: 1px solid rgba(255,255,255,0.08);
    text-decoration: none;
    transition: all 0.2s;
    white-space: nowrap;
}
.pill:last-child { border-right: none; }
.pill:hover { color: #fff; background: rgba(255,255,255,0.03); }
.pill.active { background: rgba(0,255,159,0.08); color: #00ff9f; }

/* --- POLITICIAN LEADERBOARD GRID --- */
.pgrid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 10px;
    margin-bottom: 4px;
}
.pcard {
    background: #0a0a0a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 3px;
    padding: 16px;
    text-decoration: none; color: inherit;
    display: block; position: relative;
    transition: all 0.25s;
    overflow: hidden;
}
.pcard::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(circle at 100% 0%, rgba(0,255,159,0.10), transparent 55%);
    opacity: 0; pointer-events: none; transition: opacity 0.25s;
}
.pcard:hover {
    border-color: rgba(0,255,159,0.35);
    transform: translateY(-2px);
}
.pcard:hover::before { opacity: 1; }
.pcard.active {
    border-color: #00ff9f;
    background: #050a08;
}
.pcard.active::before { opacity: 1; }
.pcard.active::after {
    content: 'ACTIVE';
    position: absolute; top: 12px; right: 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; font-weight: 600; color: #00ff9f;
    letter-spacing: 0.22em;
    padding: 2px 6px; border: 1px solid #00ff9f;
    background: #000;
    z-index: 2;
}
.pc-head {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 14px;
    position: relative; z-index: 2;
}
.pc-avatar {
    width: 40px; height: 40px;
    background: #000;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 2px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 12px;
    color: #8a8a8a;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    letter-spacing: -0.01em;
}
.pcard.active .pc-avatar {
    color: #00ff9f;
    border-color: rgba(0,255,159,0.35);
}
.pc-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600; font-size: 14px; color: #fff;
    letter-spacing: -0.01em; line-height: 1.2;
}
.pc-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #8a8a8a;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-top: 3px;
}
.pc-stats {
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.06);
    position: relative; z-index: 2;
}
.pc-s-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: #4a4a4a;
    letter-spacing: 0.15em; text-transform: uppercase;
    margin-bottom: 3px;
}
.pc-s-val {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 15px; color: #fff;
    letter-spacing: -0.02em;
}
.pgrid-more {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #8a8a8a;
    letter-spacing: 0.15em; text-transform: uppercase;
    margin-top: 14px; padding: 12px 16px;
    background: #0a0a0a;
    border: 1px dashed rgba(255,255,255,0.08);
    border-radius: 3px; text-align: center;
}

/* --- THE SCREENSHOT BLOCK --- */
.shot {
    background: #0a0a0a;
    border: 1px solid rgba(0,255,159,0.35);
    border-radius: 4px;
    margin: 28px 0 36px;
    position: relative;
    overflow: hidden;
}
.shot::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00ff9f, transparent);
    animation: scanLine 3s linear infinite;
    z-index: 3;
}
@keyframes scanLine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
.shot-head {
    padding: 22px 28px;
    display: flex; align-items: center; gap: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    flex-wrap: wrap;
}
.shot-avatar {
    width: 52px; height: 52px;
    background: #000; border: 1px solid rgba(0,255,159,0.35);
    border-radius: 3px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 16px;
    color: #00ff9f;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    letter-spacing: -0.01em;
}
.shot-id-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 22px;
    letter-spacing: -0.02em; color: #fff;
}
.shot-id-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: #8a8a8a;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-top: 5px;
}
.shot-stamp {
    margin-left: auto; flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600;
    color: #00ff9f; letter-spacing: 0.22em;
    padding: 6px 10px; border: 1px solid rgba(0,255,159,0.35);
}
.shot-nums {
    padding: 36px 28px 20px;
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    gap: 20px; align-items: center;
}
.shot-n { text-align: center; }
.shot-n-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #8a8a8a;
    letter-spacing: 0.22em; text-transform: uppercase;
    margin-bottom: 12px;
}
.shot-n-val {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 54px;
    line-height: 0.9;
    letter-spacing: -0.035em;
    font-variant-numeric: tabular-nums;
}
.shot-n-val.good { color: #00ff9f; text-shadow: 0 0 28px rgba(0,255,159,0.55); }
.shot-n-val.bad { color: #ff4d4d; text-shadow: 0 0 18px rgba(255,77,77,0.45); }
.shot-n-val.big { color: #fff; font-size: 64px; }
.shot-n-val .u {
    font-size: 22px; color: #8a8a8a; margin-left: 2px;
    text-shadow: none; font-weight: 500;
}
.shot-sep {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px; color: #4a4a4a;
}
.shot-spark { padding: 0 28px 16px; }
.shot-spark-legend {
    display: flex; gap: 18px; justify-content: flex-end;
    padding-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #6a6a6a;
    letter-spacing: 0.1em;
}
.shot-spark-legend span { display: inline-flex; align-items: center; gap: 6px; }
.shot-spark-legend .sw { width: 12px; height: 2px; }
.shot-spark-legend .sw.g { background: #00ff9f; box-shadow: 0 0 4px #00ff9f; }
.shot-spark-legend .sw.r { background: #ff4d4d; }
.shot-verdict {
    padding: 4px 28px 24px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 500;
    font-size: 17px; line-height: 1.42;
    color: #e5e5e5;
    letter-spacing: -0.005em;
}
.shot-verdict b { color: #fff; font-weight: 700; }
.shot-foot {
    padding: 12px 28px;
    background: #000;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #6a6a6a;
    letter-spacing: 0.18em;
    text-align: center;
    display: flex; justify-content: space-between; align-items: center;
    gap: 10px; flex-wrap: wrap;
}
.shot-foot a { color: #00ff9f; text-decoration: none; }
.shot-foot-hint::before { content: '↓ '; color: #00ff9f; }

/* --- METRIC STRIP (inline below screenshot) --- */
.mstrip {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 3px;
    background: #0a0a0a;
    margin-bottom: 40px;
    overflow: hidden;
}
.ms-cell {
    padding: 16px 20px;
    border-right: 1px solid rgba(255,255,255,0.06);
}
.ms-cell:last-child { border-right: none; }
.ms-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: #6a6a6a;
    letter-spacing: 0.18em; text-transform: uppercase;
    margin-bottom: 6px;
}
.ms-val {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 20px;
    letter-spacing: -0.02em; color: #fff;
    line-height: 1;
}
.ms-val.g { color: #00ff9f; }
.ms-val.r { color: #ff4d4d; }

/* --- Data tables / dataframes --- */
.stDataFrame, [data-testid="stTable"] {
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 3px !important;
}

/* --- Methodology footer --- */
.method-card {
    background: #0a0a0a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 3px;
    padding: 22px 26px; margin: 40px 0 12px;
}
.method-body {
    font-size: 12px; line-height: 1.7;
    color: #8a8a8a; letter-spacing: 0.01em;
}
.method-body strong { color: #fff; font-weight: 600; }
.method-brand {
    margin-top: 14px; padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #4a4a4a;
    letter-spacing: 0.1em;
}
.method-brand a { color: #00ff9f; text-decoration: none; }

.disclaimer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: #3a3a3a;
    line-height: 1.7; letter-spacing: 0.02em;
    margin-top: 12px;
}

/* Progress bar & dividers */
[data-testid="stProgress"] > div > div > div { background: #00ff9f !important; }
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.08) !important;
    margin: 20px 0 !important;
}

/* Plotly chart container */
.js-plotly-plot { background: transparent !important; }

/* Streamlit captions */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #6a6a6a !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
}

/* Responsive */
@media (max-width: 900px) {
    .shot-nums { grid-template-columns: 1fr; gap: 20px; padding: 28px 20px 16px; }
    .shot-sep { display: none; }
    .shot-n-val { font-size: 44px; }
    .shot-n-val.big { font-size: 52px; }
    .mstrip { grid-template-columns: repeat(2, 1fr); }
    .ms-cell { border-bottom: 1px solid rgba(255,255,255,0.06); }
    .tbar { gap: 10px; }
    .tnav { gap: 10px; }
}
</style>
""", unsafe_allow_html=True)


# ===================================================================
# DATA LOADING  (unchanged)
# ===================================================================

def get_quiver_api_key():
    try:
        return st.secrets.get("QUIVER_API_KEY", None)
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def load_congressional_trades():
    api_key = get_quiver_api_key()
    if not api_key:
        return None, "NO_API_KEY"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    endpoints = [
        ("https://api.quiverquant.com/beta/live/congresstrading", 60, "Quiver Live"),
        ("https://api.quiverquant.com/beta/bulk/congresstrading", 300, "Quiver Bulk"),
        ("https://api.quiverquant.com/beta/historical/congresstrading", 300, "Quiver Historical"),
    ]
    last_error = None
    for url, timeout, label in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200:
                try:
                    data = r.json()
                except Exception as je:
                    last_error = f"JSON_PARSE: {je}"
                    continue
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    try:
                        normalized = normalize_df(df, "quiver_api")
                        return normalized, f"Quiver Quantitative API ({label})"
                    except ValueError as ve:
                        return None, f"COLUMN_MAPPING: {ve}"
                else:
                    last_error = f"{label}: empty response"
                    continue
            elif r.status_code == 401:
                return None, "INVALID_API_KEY"
            elif r.status_code == 403:
                last_error = f"{label}: forbidden (tier restriction)"
                continue
            elif r.status_code == 429:
                return None, "RATE_LIMITED"
            else:
                last_error = f"{label}: HTTP {r.status_code}"
                continue
        except requests.exceptions.Timeout:
            last_error = f"{label}: timeout after {timeout}s"
            continue
        except Exception as e:
            last_error = f"{label}: {str(e)[:150]}"
            continue
    return None, f"ALL_ENDPOINTS_FAILED: {last_error}"


def normalize_df(df, source_type):
    df.columns = [str(c).strip() for c in df.columns]
    lower_cols = {c.lower(): c for c in df.columns}
    out = pd.DataFrame()

    for k in ["representative", "senator", "politician", "name", "member", "reporter", "trader"]:
        if k in lower_cols:
            out["politician"] = df[lower_cols[k]]
            break
    for k in ["ticker", "symbol", "stock_ticker", "stockticker"]:
        if k in lower_cols:
            out["ticker"] = df[lower_cols[k]].astype(str).str.upper().str.strip()
            break
    for k in ["transaction", "type", "transaction_type", "txn_type", "tradetype", "trade_type"]:
        if k in lower_cols:
            out["type"] = df[lower_cols[k]].astype(str).str.lower()
            break
    for k in ["transactiondate", "transaction_date", "trade_date", "tradedate", "date", "traded", "traded_on"]:
        if k in lower_cols:
            out["transaction_date"] = pd.to_datetime(df[lower_cols[k]], errors="coerce")
            break
    for k in ["reportdate", "report_date", "disclosure_date", "disclosuredate", "filing_date", "filed", "disclosed"]:
        if k in lower_cols:
            out["disclosure_date"] = pd.to_datetime(df[lower_cols[k]], errors="coerce")
            break
    for k in ["range", "amount", "value", "size", "trade_size", "transactionsize"]:
        if k in lower_cols:
            out["amount"] = df[lower_cols[k]].astype(str)
            break
    # Optional: party, state, chamber — preserved when source provides them
    for k in ["party"]:
        if k in lower_cols:
            out["party"] = df[lower_cols[k]].astype(str).str.strip()
            break
    for k in ["state"]:
        if k in lower_cols:
            out["state"] = df[lower_cols[k]].astype(str).str.upper().str.strip()
            break
    for k in ["house", "chamber", "office"]:
        if k in lower_cols:
            out["chamber"] = df[lower_cols[k]].astype(str).str.strip()
            break
    # Infer chamber from column name if missing (Quiver splits endpoints)
    if "chamber" not in out.columns:
        if "senator" in lower_cols:
            out["chamber"] = "Senate"
        elif "representative" in lower_cols:
            out["chamber"] = "House"

    required = ["politician", "ticker", "transaction_date"]
    missing = [r for r in required if r not in out.columns]
    if missing:
        raise ValueError(
            f"Could not map these required columns: {missing}. "
            f"Actual columns from source: {list(df.columns)}. "
            f"Sample row: {df.iloc[0].to_dict() if len(df) > 0 else 'empty'}"
        )

    out = out.dropna(subset=["politician", "ticker", "transaction_date"])
    out["ticker"] = out["ticker"].str.replace(r"[^A-Z]", "", regex=True)
    out = out[out["ticker"].str.len().between(1, 5)]
    out = out[out["transaction_date"] >= "2020-01-01"]

    if "disclosure_date" not in out.columns or out["disclosure_date"].isna().all():
        out["disclosure_date"] = out["transaction_date"] + pd.Timedelta(days=30)
    else:
        out["disclosure_date"] = out["disclosure_date"].fillna(
            out["transaction_date"] + pd.Timedelta(days=30)
        )

    if "type" not in out.columns:
        out["type"] = "purchase"
    out["type"] = out["type"].fillna("purchase").str.lower()

    return out.reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def get_price_history(ticker, start, end):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(start=start, end=end, auto_adjust=True)
        if len(hist) == 0:
            return None
        return hist["Close"]
    except Exception:
        return None


# ===================================================================
# BACKTEST LOGIC  (unchanged)
# ===================================================================

def get_spy_benchmark(start, end):
    prices = get_price_history("SPY", start, end + timedelta(days=5))
    if prices is None or len(prices) < 2:
        return None
    return float((prices.iloc[-1] / prices.iloc[0] - 1) * 100)


def backtest_with_lag_analysis(trades_df, hold_days=90):
    results = []
    today = datetime.now().date()
    for _, row in trades_df.iterrows():
        ticker = row["ticker"]
        trade_date = row["transaction_date"].date() if pd.notna(row["transaction_date"]) else None
        disc_date = row["disclosure_date"].date() if pd.notna(row["disclosure_date"]) else None
        if not trade_date or not disc_date:
            continue
        if disc_date > today:
            continue
        if "sale" in str(row.get("type", "")).lower():
            continue
        pol_exit = trade_date + timedelta(days=hold_days)
        retail_exit = disc_date + timedelta(days=hold_days)
        if pol_exit > today: pol_exit = today
        if retail_exit > today: retail_exit = today
        price_start = min(trade_date, disc_date) - timedelta(days=5)
        price_end = max(pol_exit, retail_exit) + timedelta(days=5)
        prices = get_price_history(ticker, price_start, price_end)
        if prices is None or len(prices) < 2:
            continue

        def price_at_or_after(d):
            m = prices[prices.index.date >= d]
            return float(m.iloc[0]) if len(m) > 0 else None
        def price_at_or_before(d):
            m = prices[prices.index.date <= d]
            return float(m.iloc[-1]) if len(m) > 0 else None

        pol_entry = price_at_or_after(trade_date)
        disc_price = price_at_or_after(disc_date)
        pol_exit_price = price_at_or_before(pol_exit)
        retail_exit_price = price_at_or_before(retail_exit)
        if any(p is None or p == 0 for p in [pol_entry, disc_price, pol_exit_price, retail_exit_price]):
            continue

        pol_return = (pol_exit_price / pol_entry - 1) * 100
        retail_return = (retail_exit_price / disc_price - 1) * 100
        lag_alpha = (disc_price / pol_entry - 1) * 100
        alpha_gap = pol_return - retail_return

        results.append({
            "politician": row["politician"], "ticker": ticker,
            "trade_date": trade_date, "disclosure_date": disc_date,
            "lag_days": (disc_date - trade_date).days,
            "pol_entry": round(pol_entry, 2), "disc_price": round(disc_price, 2),
            "retail_exit_price": round(retail_exit_price, 2),
            "pol_return": round(pol_return, 2), "retail_return": round(retail_return, 2),
            "lag_alpha": round(lag_alpha, 2), "alpha_gap": round(alpha_gap, 2),
        })
    return pd.DataFrame(results)


def compute_lag_stats(bt_results):
    if len(bt_results) == 0:
        return None
    bt_sorted = bt_results.sort_values("trade_date").reset_index(drop=True)
    n = len(bt_sorted)
    pol_total = 100.0
    retail_total = 100.0
    pol_equity = []
    retail_equity = []
    for _, t in bt_sorted.iterrows():
        pol_total *= (1 + t["pol_return"] / 100) ** (1 / n)
        retail_total *= (1 + t["retail_return"] / 100) ** (1 / n)
        pol_equity.append({"date": t["trade_date"], "equity": pol_total})
        retail_equity.append({"date": t["disclosure_date"], "equity": retail_total})
    pol_return_pct = pol_total - 100
    retail_return_pct = retail_total - 100
    alpha_gap_pct = pol_return_pct - retail_return_pct
    lag_blackout_hits = int((bt_sorted["lag_alpha"] > 0).sum())
    lag_blackout_rate = (lag_blackout_hits / n) * 100
    return {
        "trades": n,
        "politician_return": round(pol_return_pct, 2),
        "retail_return": round(retail_return_pct, 2),
        "alpha_gap": round(alpha_gap_pct, 2),
        "avg_lag_days": round(float(bt_sorted["lag_days"].mean()), 1),
        "avg_lag_alpha": round(float(bt_sorted["lag_alpha"].mean()), 2),
        "median_lag_alpha": round(float(bt_sorted["lag_alpha"].median()), 2),
        "lag_blackout_rate": round(lag_blackout_rate, 1),
        "pol_win_rate": round((bt_sorted["pol_return"] > 0).mean() * 100, 1),
        "retail_win_rate": round((bt_sorted["retail_return"] > 0).mean() * 100, 1),
        "pol_equity_curve": pd.DataFrame(pol_equity),
        "retail_equity_curve": pd.DataFrame(retail_equity),
    }


def backtest_copy_politician(trades_df, hold_days=90):
    return backtest_with_lag_analysis(trades_df, hold_days=hold_days)


def compute_portfolio_stats(bt_results):
    if len(bt_results) == 0:
        return None
    returns = bt_results["retail_return"] if "retail_return" in bt_results.columns else bt_results.get("return_pct", pd.Series([]))
    if len(returns) == 0:
        return None
    wins = int((returns > 0).sum()); losses = int((returns <= 0).sum())
    total_trades = len(returns)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_return = float(returns.mean()); median_return = float(returns.median())
    bt_sorted = bt_results.sort_values("disclosure_date" if "disclosure_date" in bt_results.columns else "trade_date").reset_index(drop=True)
    cumulative = 100.0; equity = []
    for _, t in bt_sorted.iterrows():
        r = t.get("retail_return", t.get("return_pct", 0))
        cumulative *= (1 + r / 100) ** (1 / total_trades)
        exit_col = "disclosure_date" if "disclosure_date" in bt_results.columns else "trade_date"
        equity.append({"date": t[exit_col], "equity": cumulative})
    equity_df = pd.DataFrame(equity)
    total_return = cumulative - 100
    if len(equity_df) > 0:
        peak = equity_df["equity"].cummax()
        dd = (equity_df["equity"] / peak - 1) * 100
        max_dd = float(dd.min())
    else:
        max_dd = 0
    return {
        "trades": total_trades, "wins": wins, "losses": losses,
        "win_rate": round(win_rate, 1), "avg_return": round(avg_return, 2),
        "median_return": round(median_return, 2), "total_return": round(total_return, 2),
        "max_drawdown": round(max_dd, 2), "equity_curve": equity_df,
    }


# ===================================================================
# NEW: PRECOMPUTED POLITICIAN SUMMARY (cheap, no pricing)
# ===================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def build_politician_summary(trades_df):
    """Per-politician metadata — count, avg lag, recency. No pricing."""
    purchases = trades_df[~trades_df["type"].str.contains("sale", case=False, na=False)].copy()
    purchases["lag_days"] = (purchases["disclosure_date"] - purchases["transaction_date"]).dt.days
    agg = {
        "trades": ("ticker", "count"),
        "avg_lag_days": ("lag_days", "mean"),
        "latest_trade": ("transaction_date", "max"),
        "unique_tickers": ("ticker", "nunique"),
    }
    g = purchases.groupby("politician").agg(**agg).reset_index()
    # Carry optional fields if present
    for optional in ["party", "state", "chamber"]:
        if optional in purchases.columns:
            first = purchases.groupby("politician")[optional].first().reset_index()
            g = g.merge(first, on="politician", how="left")
    g["avg_lag_days"] = g["avg_lag_days"].fillna(30).round(0).astype(int)
    return g


# ===================================================================
# NEW: UI HELPERS
# ===================================================================

def initials(name):
    parts = [p for p in str(name).replace("Dr.", "").replace("Sen.", "").replace("Rep.", "").split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "??"


def relative_date(d):
    if pd.isna(d):
        return "—"
    if hasattr(d, 'date'):
        d = d.date()
    days = (datetime.now().date() - d).days
    if days < 0: return "future"
    if days == 0: return "today"
    if days < 7: return f"{days}d"
    if days < 30: return f"{days // 7}w"
    if days < 365: return f"{days // 30}mo"
    return f"{days // 365}y"


def build_link(selected_politician, sort_by, hold_days):
    """Stateful URL — clicking any control preserves the others."""
    return f"?p={urlquote(str(selected_politician))}&sort={sort_by}&hold={hold_days}"


def sparkline_svg(pol_eq, retail_eq, width=800, height=90):
    """Inline SVG: pol_eq (signal green) vs retail_eq (danger red). Zero-line dashed."""
    if pol_eq is None or len(pol_eq) == 0 or retail_eq is None or len(retail_eq) == 0:
        return ""
    all_y = list(pol_eq["equity"]) + list(retail_eq["equity"])
    ymin, ymax = min(all_y), max(all_y)
    span = max(ymax - ymin, 0.5)
    pad = span * 0.15
    ymin -= pad; ymax += pad
    span = ymax - ymin

    def path(df):
        n = len(df)
        if n == 0: return ""
        if n == 1:
            y = height - 4 - ((df["equity"].iloc[0] - ymin) / span) * (height - 8)
            return f"{4:.1f},{y:.1f} {(width-4):.1f},{y:.1f}"
        pts = []
        for i, v in enumerate(df["equity"]):
            x = (i / (n - 1)) * (width - 8) + 4
            y = height - 4 - ((v - ymin) / span) * (height - 8)
            pts.append(f"{x:.1f},{y:.1f}")
        return " ".join(pts)

    pol_pts = path(pol_eq)
    ret_pts = path(retail_eq)
    zero_y = height - 4 - ((100 - ymin) / span) * (height - 8)
    zero_y = max(4, min(height - 4, zero_y))

    return f'''<svg viewBox="0 0 {width} {height}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:{height}px; display:block;">
  <line x1="0" y1="{zero_y:.1f}" x2="{width}" y2="{zero_y:.1f}" stroke="rgba(255,255,255,0.12)" stroke-width="1" stroke-dasharray="3 3"/>
  <polyline fill="none" stroke="#ff4d4d" stroke-width="2" points="{ret_pts}"/>
  <polyline fill="none" stroke="#00ff9f" stroke-width="2.2" points="{pol_pts}" style="filter: drop-shadow(0 0 3px rgba(0,255,159,0.6));"/>
</svg>'''


# ===================================================================
# NAV BAR
# ===================================================================

st.markdown("""
<div class="tnav">
  <div class="tnav-left">
    <div class="tnav-logo"></div>
    <div class="tnav-name">The Fifth<em>Signal</em></div>
    <div class="tnav-badge">Signal 05 · Conflict Score</div>
  </div>
  <a href="https://thecapitoldossier.com/#pricing" target="_blank" class="tnav-cta">Start 7-Day Trial →</a>
</div>
""", unsafe_allow_html=True)


# ===================================================================
# DATA LOAD
# ===================================================================

with st.spinner("Loading congressional trade data from Quiver (first load may take up to 5 minutes; cached for 24 hours after)..."):
    trades, source_name = load_congressional_trades()

if trades is None:
    if source_name == "NO_API_KEY":
        st.error("Quiver API key not configured.")
        st.markdown("""
        **To connect your Quiver API key:**
        1. In your deployed Streamlit app, click the `⋮` menu → **Settings** → **Secrets**
        2. Paste: `QUIVER_API_KEY = "your_key_here"`
        3. Save. The app reboots automatically.

        Or upload a CSV manually below for a one-time run.
        """)
    elif source_name == "INVALID_API_KEY":
        st.error("Quiver returned 401 Unauthorized. Key is invalid or expired.")
    elif source_name == "RATE_LIMITED":
        st.error("Quiver returned 429 Too Many Requests. Wait a few minutes.")
    elif source_name.startswith("ALL_ENDPOINTS_FAILED"):
        st.error("All Quiver endpoints failed.")
        st.code(source_name, language="text")
    elif source_name.startswith("COLUMN_MAPPING"):
        st.error("API worked but columns don't match.")
        st.code(source_name, language="text")
    else:
        st.warning(f"Could not load live data: `{source_name}`. Upload a CSV below.")

    uploaded = st.file_uploader("Upload congressional trades CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        trades = normalize_df(df, "upload")
        source_name = "Manual Upload"
    else:
        st.stop()


# ===================================================================
# PRECOMPUTE SUMMARY
# ===================================================================

summary = build_politician_summary(trades)
total_pols = len(summary)
total_trades = int(summary["trades"].sum())
avg_lag_all = int(summary["avg_lag_days"].median()) if len(summary) else 30


# ===================================================================
# QUERY PARAM STATE
# ===================================================================

qp = st.query_params
priority_names = ["Nancy Pelosi", "Paul Pelosi", "Dan Crenshaw", "Marjorie Taylor Greene",
                  "Josh Gottheimer", "Ro Khanna", "Mark Green", "Tommy Tuberville",
                  "Shelley Moore Capito", "Ron Wyden"]
priority_in_data = [p for p in priority_names if p in summary["politician"].values]
default_pol = priority_in_data[0] if priority_in_data else summary.iloc[0]["politician"]

selected_politician = qp.get("p", default_pol)
if selected_politician not in summary["politician"].values:
    selected_politician = default_pol

sort_by = qp.get("sort", "trades")
if sort_by not in ["trades", "lag", "recent", "alpha"]:
    sort_by = "trades"

try:
    hold_days = int(qp.get("hold", "90"))
except Exception:
    hold_days = 90
if hold_days not in [30, 60, 90, 180, 365]:
    hold_days = 90


# ===================================================================
# TOOLBAR — sort pills + hold pills (both inline)
# ===================================================================

sort_options = [
    ("trades", "Most Trades"),
    ("lag", "Longest Lag"),
    ("recent", "Recent Activity"),
    ("alpha", "A – Z"),
]
hold_options = [30, 60, 90, 180, 365]

sort_html = "".join(
    f'<a href="?p={urlquote(selected_politician)}&sort={s}&hold={hold_days}" '
    f'class="pill {"active" if s == sort_by else ""}">{label}</a>'
    for s, label in sort_options
)
hold_html = "".join(
    f'<a href="?p={urlquote(selected_politician)}&sort={sort_by}&hold={h}" '
    f'class="pill {"active" if h == hold_days else ""}">{h}d</a>'
    for h in hold_options
)

st.markdown(f"""
<div class="tbar">
  <div class="tbar-lbl">Sort</div>
  <div class="pill-row">{sort_html}</div>
  <div class="tbar-lbl" style="margin-left:12px;">Hold</div>
  <div class="pill-row">{hold_html}</div>
</div>
""", unsafe_allow_html=True)


# ===================================================================
# POLITICIAN LEADERBOARD GRID
# ===================================================================

if sort_by == "trades":
    ranked = summary.sort_values("trades", ascending=False)
elif sort_by == "lag":
    ranked = summary.sort_values(["avg_lag_days", "trades"], ascending=[False, False])
elif sort_by == "recent":
    ranked = summary.sort_values("latest_trade", ascending=False)
else:  # alpha
    ranked = summary.sort_values("politician", ascending=True)

# Limit to top 12 for the grid; user can switch sort to find others
visible = ranked.head(12).copy()

cards_html = []
for _, r in visible.iterrows():
    name = r["politician"]
    is_active = name == selected_politician
    meta_parts = []
    if "party" in r and pd.notna(r.get("party")) and str(r.get("party")).strip():
        meta_parts.append(str(r["party"])[:1])
    if "state" in r and pd.notna(r.get("state")) and str(r.get("state")).strip():
        meta_parts.append(str(r["state"]))
    if "chamber" in r and pd.notna(r.get("chamber")) and str(r.get("chamber")).strip():
        meta_parts.append(str(r["chamber"]))
    meta_line = " · ".join(meta_parts) if meta_parts else "Congressional"

    link = build_link(name, sort_by, hold_days)
    cards_html.append(f'''
    <a href="{link}" class="pcard {'active' if is_active else ''}">
      <div class="pc-head">
        <div class="pc-avatar">{initials(name)}</div>
        <div>
          <div class="pc-name">{name}</div>
          <div class="pc-meta">{meta_line}</div>
        </div>
      </div>
      <div class="pc-stats">
        <div><div class="pc-s-lbl">Trades</div><div class="pc-s-val">{int(r["trades"])}</div></div>
        <div><div class="pc-s-lbl">Avg Lag</div><div class="pc-s-val">{int(r["avg_lag_days"])}d</div></div>
        <div><div class="pc-s-lbl">Latest</div><div class="pc-s-val">{relative_date(r["latest_trade"])}</div></div>
      </div>
    </a>
    ''')

st.markdown(
    f'<div class="kicker">Defendants · {total_pols} members · showing top 12 by {sort_by}</div>',
    unsafe_allow_html=True
)
st.markdown(f'<div class="pgrid">{"".join(cards_html)}</div>', unsafe_allow_html=True)

if total_pols > 12:
    st.markdown(
        f'<div class="pgrid-more">Sort pills above cycle through all {total_pols} members · '
        f'selected defendant below backtests in real time</div>',
        unsafe_allow_html=True
    )


# ===================================================================
# FILTER + BACKTEST the selected politician
# ===================================================================

filtered = trades[
    (trades["politician"] == selected_politician) &
    (~trades["type"].str.contains("sale", case=False, na=False))
].copy()

if len(filtered) == 0:
    st.warning(f"No purchase trades found for {selected_politician}.")
    st.stop()

progress = st.progress(0, text=f"Running backtest on {len(filtered)} trades...")
bt_chunks = []
chunk_size = max(1, len(filtered) // 20)
for i in range(0, len(filtered), chunk_size):
    chunk = filtered.iloc[i:i+chunk_size]
    r = backtest_with_lag_analysis(chunk, hold_days=hold_days)
    bt_chunks.append(r)
    progress.progress(min(1.0, (i + chunk_size) / len(filtered)),
                      text=f"Running backtest... ({min(i+chunk_size, len(filtered))}/{len(filtered)} trades)")
progress.empty()
bt = pd.concat(bt_chunks, ignore_index=True) if bt_chunks else pd.DataFrame()

if len(bt) == 0:
    st.warning("No trades could be priced (tickers may be delisted or outside yfinance coverage).")
    st.stop()

stats = compute_lag_stats(bt)
bt_start = bt["trade_date"].min()
bt_end_retail = bt["disclosure_date"].max() + timedelta(days=hold_days)
spy_return = get_spy_benchmark(bt_start, bt_end_retail)

pol_r = stats["politician_return"]
ret_r = stats["retail_return"]
gap = stats["alpha_gap"]
avg_lag = stats["avg_lag_days"]
spy_r = spy_return if spy_return is not None else 0


# ===================================================================
# THE SCREENSHOT BLOCK — one card, two-second comprehension
# ===================================================================

# Build meta line for the active politician from summary
active_row = summary[summary["politician"] == selected_politician].iloc[0]
meta_bits = [f"{int(active_row['trades'])} trades"]
if "party" in active_row and pd.notna(active_row.get("party")) and str(active_row.get("party")).strip():
    meta_bits.insert(0, str(active_row["party"])[:1])
if "state" in active_row and pd.notna(active_row.get("state")) and str(active_row.get("state")).strip():
    meta_bits.insert(-1, str(active_row["state"]))
if "chamber" in active_row and pd.notna(active_row.get("chamber")) and str(active_row.get("chamber")).strip():
    meta_bits.insert(-1, str(active_row["chamber"]))
meta_bits.append(f"{int(avg_lag)}d avg lag")
meta_bits.append(f"{hold_days}d hold")
shot_meta = " · ".join(meta_bits)

# Single-line verdict — match the four narrative cases, one sentence each
if gap > 1.0:
    verdict = (
        f"The <b>{int(avg_lag)}-day disclosure lag</b> stole <b>{gap:.1f} percentage points</b> of alpha — "
        f"the stocks had already run <b>{stats['avg_lag_alpha']:+.1f}%</b> before retail could legally act. "
        f"S&amp;P returned <b>{spy_r:+.1f}%</b> over the same window."
    )
elif pol_r < 0 and ret_r < 0:
    verdict = (
        f"<b>Both entries lost money.</b> The strategy fails regardless of timing. "
        f"S&amp;P returned <b>{spy_r:+.1f}%</b> — buying the index beat copying the member on either entry date."
    )
elif ret_r > pol_r:
    verdict = (
        f"<b>The member's timing was actually worse</b> — stocks dropped during the blackout. "
        f"Neither entry beat the S&amp;P's <b>{spy_r:+.1f}%</b>. The copy-trading premise is unreliable either way."
    )
elif spy_r > max(pol_r, ret_r):
    verdict = (
        f"Both strategies made money. <b>The S&amp;P made more ({spy_r:+.1f}%)</b>. "
        f"You could have skipped the analysis, bought an index fund, and outperformed by <b>{spy_r - ret_r:.1f}pp</b>."
    )
else:
    verdict = (
        f"Both entries beat the S&amp;P. The lag still cost retail <b>{gap:.1f}pp</b> of the member's captured alpha."
    )

spark = sparkline_svg(stats["pol_equity_curve"], stats["retail_equity_curve"])

# Big-number class for the gap depends on sign
gap_class = "big"
gap_prefix = ""
gap_display = f"{abs(gap):.1f}"

shot_html = f"""
<div class="shot">
  <div class="shot-head">
    <div class="shot-avatar">{initials(selected_politician)}</div>
    <div>
      <div class="shot-id-name">{selected_politician}</div>
      <div class="shot-id-meta">{shot_meta}</div>
    </div>
    <div class="shot-stamp">Signal 05</div>
  </div>
  <div class="shot-nums">
    <div class="shot-n">
      <div class="shot-n-lbl">They Captured</div>
      <div class="shot-n-val {'good' if pol_r >= 0 else 'bad'}">{pol_r:+.1f}<span class="u">%</span></div>
    </div>
    <div class="shot-sep">→</div>
    <div class="shot-n">
      <div class="shot-n-lbl">You Got</div>
      <div class="shot-n-val {'good' if ret_r >= 0 else 'bad'}">{ret_r:+.1f}<span class="u">%</span></div>
    </div>
    <div class="shot-sep">=</div>
    <div class="shot-n">
      <div class="shot-n-lbl">Stolen by Lag</div>
      <div class="shot-n-val {gap_class}">{gap:+.1f}<span class="u">pp</span></div>
    </div>
  </div>
  <div class="shot-spark">
    <div class="shot-spark-legend">
      <span><span class="sw g"></span>Member (trade-date entry)</span>
      <span><span class="sw r"></span>Retail copy (disclosure entry)</span>
    </div>
    {spark}
  </div>
  <div class="shot-verdict">{verdict}</div>
  <div class="shot-foot">
    <span class="shot-foot-hint">SCREENSHOT THIS CARD · POST IT</span>
    <a href="https://thecapitoldossier.com/" target="_blank">thecapitoldossier.com</a>
  </div>
</div>
"""
st.markdown(shot_html, unsafe_allow_html=True)


# ===================================================================
# METRIC STRIP — supporting numbers in one inline row
# ===================================================================

st.markdown(f"""
<div class="mstrip">
  <div class="ms-cell">
    <div class="ms-lbl">Trades Analyzed</div>
    <div class="ms-val">{stats['trades']}</div>
  </div>
  <div class="ms-cell">
    <div class="ms-lbl">S&amp;P 500</div>
    <div class="ms-val">{spy_r:+.1f}%</div>
  </div>
  <div class="ms-cell">
    <div class="ms-lbl">Their Win Rate</div>
    <div class="ms-val g">{stats['pol_win_rate']:.0f}%</div>
  </div>
  <div class="ms-cell">
    <div class="ms-lbl">Your Win Rate</div>
    <div class="ms-val r">{stats['retail_win_rate']:.0f}%</div>
  </div>
  <div class="ms-cell">
    <div class="ms-lbl">Pre-Disclosure Runs</div>
    <div class="ms-val">{stats['lag_blackout_rate']:.0f}%</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ===================================================================
# FULL EQUITY CURVE
# ===================================================================

st.markdown('<div class="kicker">The full curve</div>', unsafe_allow_html=True)
st.caption(f"$100 invested · green: member's trade-date entry · red: retail's disclosure-date entry · dotted gray: S&P buy-and-hold · {hold_days}-day hold")

pol_eq = stats["pol_equity_curve"]
retail_eq = stats["retail_equity_curve"]
spy_df = None
if spy_return is not None:
    spy_prices = get_price_history("SPY", bt_start, bt_end_retail + timedelta(days=5))
    if spy_prices is not None:
        spy_df = pd.DataFrame({
            "date": spy_prices.index.date,
            "equity": (spy_prices.values / spy_prices.iloc[0]) * 100
        })

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=pol_eq["date"], y=pol_eq["equity"],
    mode="lines", name=f"{selected_politician} (trade-date entry)",
    line=dict(color="#00ff9f", width=3),
))
fig.add_trace(go.Scatter(
    x=retail_eq["date"], y=retail_eq["equity"],
    mode="lines", name="Retail copy (disclosure-date entry)",
    line=dict(color="#ff4d4d", width=3),
))
if spy_df is not None:
    fig.add_trace(go.Scatter(
        x=spy_df["date"], y=spy_df["equity"],
        mode="lines", name="S&P 500",
        line=dict(color="#6a6a6a", width=2, dash="dot"),
    ))

fig.update_layout(
    plot_bgcolor="#0a0a0a",
    paper_bgcolor="#000000",
    font=dict(family="JetBrains Mono, monospace", color="#ffffff", size=12),
    hovermode="x unified",
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", title=""),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="$100 start → value"),
    height=420,
    margin=dict(l=50, r=30, t=20, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="left", x=0,
    ),
)
fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.12)")
st.plotly_chart(fig, use_container_width=True)


# ===================================================================
# EVERY TRADE — all receipts, visible by default (no expander)
# ===================================================================

st.markdown('<div class="kicker">Every trade · the receipts</div>', unsafe_allow_html=True)
st.caption(f"{len(bt)} purchases · click column headers to sort · widest-gap trades are where the blackout hurt most")

display_bt = bt[["ticker", "trade_date", "disclosure_date", "lag_days",
                 "pol_return", "retail_return", "alpha_gap", "lag_alpha"]].copy()
display_bt = display_bt.sort_values("alpha_gap", ascending=False)
display_bt.columns = ["Ticker", "Trade Date", "Disclosed", "Lag (days)",
                      "Their %", "Your %", "Gap (pp)", "Blackout %"]
st.dataframe(
    display_bt,
    use_container_width=True,
    hide_index=True,
    height=min(480, 42 * (len(display_bt) + 1) + 3),
    column_config={
        "Their %": st.column_config.NumberColumn(format="%+.2f%%",
            help="What the member captured from trade date entry"),
        "Your %": st.column_config.NumberColumn(format="%+.2f%%",
            help="What retail got copying on the disclosure date"),
        "Gap (pp)": st.column_config.NumberColumn(format="%+.2f",
            help="Percentage points the lag stole from retail on this trade"),
        "Blackout %": st.column_config.NumberColumn(format="%+.2f%%",
            help="Pure price move during the disclosure blackout window"),
    }
)


# ===================================================================
# METHODOLOGY FOOTER
# ===================================================================

date_min_str = trades["transaction_date"].min().strftime("%b %Y")
date_max_str = trades["transaction_date"].max().strftime("%b %Y")

st.markdown(f"""
<div class="method-card">
  <div class="method-body">
    <strong>Methodology.</strong> For every disclosed purchase in the selected window, two entries are simulated: one on the member's actual trade date (what they captured), one on the disclosure date — the earliest a non-member could legally have known (what retail gets). Both hold {hold_days} days. Sales are excluded (retail rarely shorts). S&amp;P benchmark is buy-and-hold SPY over the same window. Dataset currently covers <strong>{date_min_str} – {date_max_str}</strong> · <strong>{total_trades:,} trades</strong> across <strong>{total_pols} members</strong> via the Quiver Quantitative live endpoint. Older history requires a paid Quiver tier.
  </div>
  <div class="method-brand">
    DATA · QUIVER QUANTITATIVE · STOCK ACT PTRs &nbsp;·&nbsp;
    SIGNAL 05 · THE FIFTH SIGNAL · <a href="https://thecapitoldossier.com/" target="_blank">thecapitoldossier.com</a>
  </div>
</div>

<div class="disclaimer">
For informational and educational purposes only. Not investment advice. All performance data is hypothetical and derived from publicly disclosed congressional transactions. Past performance does not guarantee future results. Options trading involves substantial risk. The Fifth Signal is an educational publication, not a registered investment advisor.
</div>
""", unsafe_allow_html=True)
