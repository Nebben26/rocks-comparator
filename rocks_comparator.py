"""
THE ROCKS THROWN COMPARATOR
============================
Powered by The Fifth Signal

Attacks the congressional copy-trading lie with real data.
Pulls actual disclosed trades from public Congress disclosures,
backtests what would happen if a retail buyer copied them at
disclosure date (the only date retail can actually act on),
and compares to the S&P 500.

Why this proves the thesis:
- The STOCK Act mandates disclosure within 45 days
- Retail cannot act on the trade date (they don't know about it)
- Retail can only act on the disclosure date (45 days later)
- By then, the move is usually over

Run locally:
    pip install -r requirements.txt
    streamlit run rocks_comparator.py

Deploy free:
    1. Push this folder to GitHub
    2. Go to share.streamlit.io
    3. Connect the repo, select rocks_comparator.py as entry point
    4. Live URL in ~2 minutes
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime, timedelta
from io import StringIO
import time

# ===================================================================
# PAGE CONFIG
# ===================================================================
st.set_page_config(
    page_title="The Rocks Thrown Comparator · The Fifth Signal",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===================================================================
# STYLING — matches thefifthsignal.com landing page
# ===================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    /* =============================================
       THE ROCKS THROWN COMPARATOR · STYLE
       Journalistic, data-focused, quiet.
       ============================================= */

    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    /* Core */
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .main > div { max-width: 1100px; padding-top: 2rem !important; }
    [data-testid="stHeader"] { background: #000; }
    [data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * { color: #ffffff; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stDateInput label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #8a8a8a !important;
        margin-bottom: 6px;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.025em;
        color: #ffffff;
        font-weight: 700 !important;
    }
    h2 { font-size: 36px !important; margin-top: 32px !important; margin-bottom: 4px !important; }
    h3 { font-size: 22px !important; margin-top: 36px !important; margin-bottom: 12px !important; }

    /* Main header */
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 46px;
        line-height: 1.05;
        letter-spacing: -0.035em;
        margin-bottom: 12px;
    }
    .main-title .accent {
        color: #00ff9f;
        text-shadow: 0 0 32px rgba(0,255,159,0.55);
    }
    .main-sub {
        color: #00ff9f;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 32px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .main-sub::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #00ff9f;
        border-radius: 50%;
        box-shadow: 0 0 12px #00ff9f;
    }
    .main-lede {
        color: #a8a8a8;
        font-size: 15px;
        line-height: 1.6;
        max-width: 680px;
        margin-bottom: 20px;
    }

    /* Caption under headers */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #6a6a6a !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.08em;
    }

    /* Buttons */
    .stButton > button {
        background-color: #00ff9f;
        color: #000;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border: none;
        border-radius: 2px;
        padding: 12px 24px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 32px rgba(0,255,159,0.45);
        transform: translateY(-1px);
    }

    /* Form inputs */
    .stSelectbox [data-baseweb="select"] > div,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: #0a0a0a !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #fff !important;
        border-radius: 2px;
        font-family: 'Inter', sans-serif;
    }
    .stSelectbox [data-baseweb="select"] > div:hover {
        border-color: rgba(0,255,159,0.4) !important;
    }

    /* Metric cards — tighter and cleaner */
    [data-testid="stMetric"] {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 3px;
        padding: 20px;
        transition: border-color 0.2s;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(0,255,159,0.25);
    }
    [data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #6a6a6a !important;
        margin-bottom: 4px;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 32px !important;
        letter-spacing: -0.02em;
        color: #ffffff !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.05em;
    }

    /* DataFrames — sleeker */
    .stDataFrame {
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 3px !important;
    }
    [data-testid="stTable"] {
        background: #0a0a0a !important;
    }

    /* Verdict boxes — toned down */
    .verdict-lie {
        background: linear-gradient(135deg, rgba(255,77,77,0.06), rgba(255,77,77,0.01));
        border-left: 3px solid #ff4d4d;
        border-top: 1px solid rgba(255,77,77,0.15);
        border-right: 1px solid rgba(255,77,77,0.15);
        border-bottom: 1px solid rgba(255,77,77,0.15);
        border-radius: 3px;
        padding: 24px 28px;
        margin: 16px 0 32px 0;
    }
    .verdict-lie-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #ff4d4d;
        margin-bottom: 10px;
    }
    .verdict-lie-headline {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 28px;
        line-height: 1.25;
        letter-spacing: -0.02em;
        color: #ffffff;
    }

    .verdict-truth {
        background: linear-gradient(135deg, rgba(0,255,159,0.06), rgba(0,255,159,0.01));
        border-left: 3px solid #00ff9f;
        border-top: 1px solid rgba(0,255,159,0.2);
        border-right: 1px solid rgba(0,255,159,0.2);
        border-bottom: 1px solid rgba(0,255,159,0.2);
        border-radius: 3px;
        padding: 24px 28px;
        margin: 16px 0 32px 0;
    }
    .verdict-truth-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #00ff9f;
        margin-bottom: 10px;
    }
    .verdict-truth-headline {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 28px;
        line-height: 1.25;
        letter-spacing: -0.02em;
        color: #ffffff;
    }

    /* Footer — quiet and journalistic */
    .footer-card {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 3px;
        padding: 28px;
        margin-top: 56px;
    }
    .footer-method {
        font-size: 13px;
        line-height: 1.65;
        color: #a8a8a8;
        margin-bottom: 16px;
    }
    .footer-method strong {
        color: #ffffff;
        font-weight: 600;
    }
    .footer-brand {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.05em;
        color: #6a6a6a;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.06);
    }
    .footer-brand a {
        color: #00ff9f;
        text-decoration: none;
    }
    .footer-brand a:hover {
        text-decoration: underline;
    }

    /* Disclaimer */
    .disclaimer {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: #4a4a4a;
        line-height: 1.8;
        margin-top: 24px;
        padding: 0 4px;
        letter-spacing: 0.02em;
    }

    /* Info/warning boxes */
    [data-testid="stAlert"] {
        background: #0a0a0a;
        border: 1px solid rgba(0,255,159,0.2);
        border-radius: 3px;
    }
    [data-testid="stExpander"] {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 3px;
    }
    [data-testid="stExpander"] summary {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.05em;
        color: #ffffff !important;
    }

    /* Progress bar */
    [data-testid="stProgress"] > div > div > div {
        background: #00ff9f !important;
    }

    /* Dividers */
    hr {
        border: none !important;
        border-top: 1px solid rgba(255,255,255,0.08) !important;
        margin: 24px 0 !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stStatusWidget"] { display: none !important; }

    /* Sidebar section labels */
    .sb-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #00ff9f;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .sb-label:first-of-type { margin-top: 0; }

    /* Section headings inside main content */
    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #00ff9f;
        margin-top: 48px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ===================================================================
# DATA LOADING
# ===================================================================

# ===================================================================
# DATA SOURCES — authenticated Quiver Quantitative API (primary)
# ===================================================================

# The Quiver API key is loaded from Streamlit Secrets, never hardcoded.
# In local dev: create a file at .streamlit/secrets.toml with:
#     QUIVER_API_KEY = "your_key_here"
# On Streamlit Cloud: go to App Settings → Secrets and add the same line.

def get_quiver_api_key():
    """Fetch the Quiver API key from Streamlit secrets. Returns None if not set."""
    try:
        return st.secrets.get("QUIVER_API_KEY", None)
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)  # cache for 24 hours
def load_congressional_trades():
    """
    Pull congressional trade disclosures from the authenticated Quiver API.

    Quiver has multiple endpoints with different scope and speed:
    - /beta/live/congresstrading — recent trades only, fast, available on all tiers
    - /beta/bulk/congresstrading — full history, slow, may timeout on Hobbyist tier

    We try live first (it's fast and always works), then bulk as a fallback.
    """
    api_key = get_quiver_api_key()

    if not api_key:
        return None, "NO_API_KEY"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # Endpoints to try, in order. We use a longer timeout for bulk because it
    # can return tens of thousands of records. Cache means this only runs once
    # per day per Streamlit instance.
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
                        # Column mapping failed — surface the actual columns
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
    """
    Different sources use different column names.
    This normalizes everything to: politician, ticker, type, transaction_date, disclosure_date, amount

    If a critical column can't be found, raises ValueError with the actual columns
    so we know what the source provided.
    """
    # Lowercase all cols for matching
    df.columns = [str(c).strip() for c in df.columns]
    lower_cols = {c.lower(): c for c in df.columns}

    out = pd.DataFrame()

    # Politician — Quiver uses "Representative" (House) or "Senator" (Senate)
    for k in ["representative", "senator", "politician", "name", "member", "reporter", "trader"]:
        if k in lower_cols:
            out["politician"] = df[lower_cols[k]]
            break

    # Ticker — Quiver uses "Ticker"
    for k in ["ticker", "symbol", "stock_ticker", "stockticker"]:
        if k in lower_cols:
            out["ticker"] = df[lower_cols[k]].astype(str).str.upper().str.strip()
            break

    # Type — Quiver uses "Transaction" with values like "Purchase", "Sale (Full)", "Sale (Partial)"
    for k in ["transaction", "type", "transaction_type", "txn_type", "tradetype", "trade_type"]:
        if k in lower_cols:
            out["type"] = df[lower_cols[k]].astype(str).str.lower()
            break

    # Transaction date — Quiver uses "TransactionDate" or sometimes just "Traded"
    for k in ["transactiondate", "transaction_date", "trade_date", "tradedate", "date", "traded", "traded_on"]:
        if k in lower_cols:
            out["transaction_date"] = pd.to_datetime(df[lower_cols[k]], errors="coerce")
            break

    # Disclosure date / report date — Quiver uses "ReportDate" or "Disclosed"
    for k in ["reportdate", "report_date", "disclosure_date", "disclosuredate", "filing_date", "filed", "disclosed"]:
        if k in lower_cols:
            out["disclosure_date"] = pd.to_datetime(df[lower_cols[k]], errors="coerce")
            break

    # Amount / range — Quiver uses "Range" or "Amount"
    for k in ["range", "amount", "value", "size", "trade_size", "transactionsize"]:
        if k in lower_cols:
            out["amount"] = df[lower_cols[k]].astype(str)
            break

    # CRITICAL VALIDATION — if any required column is missing, surface the problem clearly
    required = ["politician", "ticker", "transaction_date"]
    missing = [r for r in required if r not in out.columns]
    if missing:
        raise ValueError(
            f"Could not map these required columns: {missing}. "
            f"Actual columns from source: {list(df.columns)}. "
            f"Sample row: {df.iloc[0].to_dict() if len(df) > 0 else 'empty'}"
        )

    # Clean
    out = out.dropna(subset=["politician", "ticker", "transaction_date"])
    out["ticker"] = out["ticker"].str.replace(r"[^A-Z]", "", regex=True)
    out = out[out["ticker"].str.len().between(1, 5)]
    out = out[out["transaction_date"] >= "2020-01-01"]

    # If disclosure_date missing, assume 30-day lag (conservative; law allows 45)
    if "disclosure_date" not in out.columns or out["disclosure_date"].isna().all():
        out["disclosure_date"] = out["transaction_date"] + pd.Timedelta(days=30)
    else:
        out["disclosure_date"] = out["disclosure_date"].fillna(
            out["transaction_date"] + pd.Timedelta(days=30)
        )

    # Default type if missing
    if "type" not in out.columns:
        out["type"] = "purchase"
    out["type"] = out["type"].fillna("purchase").str.lower()

    return out.reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def get_price_history(ticker, start, end):
    """Pull daily adjusted close prices from yfinance."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(start=start, end=end, auto_adjust=True)
        if len(hist) == 0:
            return None
        return hist["Close"]
    except Exception:
        return None


# ===================================================================
# BACKTEST LOGIC
# ===================================================================

def get_spy_benchmark(start, end):
    """Returns SPY total return between two dates."""
    prices = get_price_history("SPY", start, end + timedelta(days=5))
    if prices is None or len(prices) < 2:
        return None
    return float((prices.iloc[-1] / prices.iloc[0] - 1) * 100)


def backtest_with_lag_analysis(trades_df, hold_days=90):
    """
    For every disclosed purchase, compute three returns:

    1. POLITICIAN'S return: bought at transaction_date, held hold_days.
       (What they plausibly captured if they held for this period.)
    2. RETAIL copy return: bought at disclosure_date, held hold_days.
       (What YOU actually get by copying them.)
    3. LAG ALPHA: price change from transaction_date to disclosure_date.
       (Pure alpha stolen by the disclosure blackout — inaccessible to retail.)

    The gap between #1 and #2 is the structural advantage of trading
    information that is embargoed by law for 45 days.

    Returns DataFrame with per-trade results.
    """
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

        # Skip sales — retail rarely shorts
        if "sale" in str(row.get("type", "")).lower():
            continue

        # Exit dates: both parties hold hold_days from their respective entries
        pol_exit = trade_date + timedelta(days=hold_days)
        retail_exit = disc_date + timedelta(days=hold_days)
        if pol_exit > today:
            pol_exit = today
        if retail_exit > today:
            retail_exit = today

        # Pull prices covering the full range
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
        lag_alpha = (disc_price / pol_entry - 1) * 100  # price move during the blackout
        alpha_gap = pol_return - retail_return

        results.append({
            "politician": row["politician"],
            "ticker": ticker,
            "trade_date": trade_date,
            "disclosure_date": disc_date,
            "lag_days": (disc_date - trade_date).days,
            "pol_entry": round(pol_entry, 2),
            "disc_price": round(disc_price, 2),
            "retail_exit_price": round(retail_exit_price, 2),
            "pol_return": round(pol_return, 2),
            "retail_return": round(retail_return, 2),
            "lag_alpha": round(lag_alpha, 2),
            "alpha_gap": round(alpha_gap, 2),
        })

    return pd.DataFrame(results)


def compute_lag_stats(bt_results):
    """Aggregate the per-trade results into portfolio-level stats."""
    if len(bt_results) == 0:
        return None

    bt_sorted = bt_results.sort_values("trade_date").reset_index(drop=True)
    n = len(bt_sorted)

    # Equal-weighted compounded portfolio returns for both strategies
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

    # How many trades had the price already move up before retail could act?
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


# Keep the old backtest function for backward compatibility but route to new one
def backtest_copy_politician(trades_df, hold_days=90):
    return backtest_with_lag_analysis(trades_df, hold_days=hold_days)


def compute_portfolio_stats(bt_results):
    """Legacy stats for compatibility. Prefer compute_lag_stats for new UI."""
    if len(bt_results) == 0:
        return None
    returns = bt_results["retail_return"] if "retail_return" in bt_results.columns else bt_results.get("return_pct", pd.Series([]))
    if len(returns) == 0:
        return None
    wins = int((returns > 0).sum())
    losses = int((returns <= 0).sum())
    total_trades = len(returns)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_return = float(returns.mean())
    median_return = float(returns.median())

    bt_sorted = bt_results.sort_values("disclosure_date" if "disclosure_date" in bt_results.columns else "trade_date").reset_index(drop=True)
    cumulative = 100.0
    equity = []
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
        "trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 1),
        "avg_return": round(avg_return, 2),
        "median_return": round(median_return, 2),
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_dd, 2),
        "equity_curve": equity_df,
    }


# ===================================================================
# HEADER
# ===================================================================
st.markdown("""
<div class="main-sub">The Rocks Thrown Comparator</div>
<div class="main-title">They watch politicians.<br><span class="accent">We watch what politicians watch.</span></div>
<p class="main-lede">
Pick any politician. Pick any hold period. See what you would have actually returned by copying their disclosed trades on the earliest date you could have legally acted on them &mdash; then compare to the S&amp;P 500 over the same window.
</p>
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

        1. In your deployed Streamlit app, click the **`⋮`** menu in the top-right → **Settings** → **Secrets**
        2. Paste this line (replace with your actual key):
           ```
           QUIVER_API_KEY = "your_quiver_api_key_here"
           ```
        3. Click **Save**. The app will reboot automatically.

        **Or upload a CSV manually for a one-time run:**
        """)
    elif source_name == "INVALID_API_KEY":
        st.error("Quiver API returned 401 Unauthorized. The API key in your secrets is invalid or expired.")
        st.info("Double-check the key at api.quiverquant.com → your account. Then update it in App Settings → Secrets.")
    elif source_name == "FORBIDDEN":
        st.error("Quiver API returned 403 Forbidden. Your subscription tier may not include the congressional trading endpoint.")
        st.info("Check your Quiver plan at api.quiverquant.com/pricing/")
    elif source_name == "RATE_LIMITED":
        st.error("Quiver API returned 429 Too Many Requests. You've hit the rate limit for your plan.")
        st.info("Wait a few minutes and refresh. Or upload a CSV manually below to proceed.")
    elif source_name.startswith("ALL_ENDPOINTS_FAILED"):
        st.error("All Quiver endpoints failed.")
        st.code(source_name, language="text")
        st.info("This usually means a temporary network issue or that your tier doesn't include these endpoints. Try refreshing, or upload a CSV manually below.")
    elif source_name.startswith("COLUMN_MAPPING"):
        st.error("API worked but column names don't match what was expected.")
        st.code(source_name, language="text")
        st.info("Copy the text above (especially the 'Actual columns' and 'Sample row' parts) and send it to the developer to fix the column mapping.")
    else:
        st.warning(f"Could not load live data. Reason: `{source_name}`. Upload a CSV manually below.")

    st.markdown("**Manual CSV upload (fallback):**")
    uploaded = st.file_uploader("Upload congressional trades CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        trades = normalize_df(df, "upload")
        source_name = "Manual Upload"
    else:
        st.stop()

date_min_str = trades["transaction_date"].min().strftime("%b %d, %Y")
date_max_str = trades["transaction_date"].max().strftime("%b %d, %Y")
st.caption(
    f"Data source: **{source_name}** · {len(trades):,} trades "
    f"(from {date_min_str} to {date_max_str}) · Updated daily · "
    f"Full history available on higher Quiver tiers"
)

# ===================================================================
# SIDEBAR CONTROLS
# ===================================================================
st.sidebar.markdown('<div class="sb-label">// Target</div>', unsafe_allow_html=True)

# Count trades per politician to determine the best default
trade_counts = trades.groupby("politician").size().sort_values(ascending=False)
politicians = trade_counts.index.tolist()

# Priority order: put well-known names at top of dropdown IF they have enough trades
priority = ["Nancy Pelosi", "Paul Pelosi", "Dan Crenshaw", "Marjorie Taylor Greene",
            "Josh Gottheimer", "Ro Khanna", "Mark Green", "Tommy Tuberville",
            "Shelley Moore Capito", "Ron Wyden"]
priority_present = [p for p in priority if p in politicians and trade_counts[p] >= 5]
others = [p for p in politicians if p not in priority_present]
ordered = priority_present + others

# Smart default: the politician with the most trades (makes the demo compelling)
# Unless a priority name has at least 5 trades, in which case use them
if priority_present:
    default_idx = ordered.index(priority_present[0])
else:
    default_idx = 0  # top trader overall

selected_politician = st.sidebar.selectbox(
    "Politician",
    ordered,
    index=default_idx,
)
st.sidebar.caption(f"{trade_counts[selected_politician]} trades in dataset")

# Show data coverage info
date_min = trades["transaction_date"].min().date()
date_max = trades["transaction_date"].max().date()
st.sidebar.caption(f"Dataset: {len(trades):,} trades · {date_min} to {date_max}")

st.sidebar.markdown('<div class="sb-label">// Hold Period</div>', unsafe_allow_html=True)
hold_days = st.sidebar.selectbox(
    "Days held after disclosure",
    [30, 60, 90, 180, 365],
    index=2,
    help="How long you would hold each position after buying on the disclosure date.",
)

st.sidebar.markdown('<div class="sb-label">// Date Range</div>', unsafe_allow_html=True)
min_date = trades["transaction_date"].min().date()
max_date = trades["transaction_date"].max().date()
date_range = st.sidebar.date_input(
    "Trades disclosed between",
    value=(max(min_date, datetime(2022, 1, 1).date()), max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt, end_dt = date_range
else:
    start_dt, end_dt = min_date, max_date

st.sidebar.markdown('<div class="sb-label">// Trade Types</div>', unsafe_allow_html=True)
st.sidebar.caption("Only purchases are modeled. Sales require shorting, which retail rarely executes.")

# ===================================================================
# FILTER + BACKTEST
# ===================================================================
filtered = trades[
    (trades["politician"] == selected_politician) &
    (trades["transaction_date"].dt.date >= start_dt) &
    (trades["transaction_date"].dt.date <= end_dt) &
    (~trades["type"].str.contains("sale", case=False, na=False))
].copy()

if len(filtered) == 0:
    st.warning(f"No purchase trades found for {selected_politician} in this date range.")
    st.stop()

progress = st.progress(0, text=f"Running backtest on {len(filtered)} trades...")

# Backtest with progress updates — cache makes reruns instant
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

# SPY benchmark over the same period
bt_start = bt["trade_date"].min()
bt_end_pol = bt["trade_date"].max() + timedelta(days=hold_days)
bt_end_retail = bt["disclosure_date"].max() + timedelta(days=hold_days)
spy_return = get_spy_benchmark(bt_start, bt_end_retail)

# ===================================================================
# VERDICT HEADLINE — THE LAG NARRATIVE
# ===================================================================
st.markdown("---")
st.markdown(f"## Copying {selected_politician}")
st.caption(
    f"{stats['trades']} disclosed purchases · {hold_days}-day hold period · "
    f"Avg disclosure lag: {stats['avg_lag_days']:.0f} days · "
    f"{stats['lag_blackout_rate']:.0f}% of stocks moved up before you could act"
)

# Build the verdict narrative from the lag data
pol_r = stats["politician_return"]
ret_r = stats["retail_return"]
gap = stats["alpha_gap"]
avg_lag = stats["avg_lag_days"]
spy_r = spy_return if spy_return is not None else 0

# Four possible narrative cases:
# 1. Politician crushed it, retail got scraps (the classic "lag exposed")
# 2. Politician lost, retail also lost (strategy failed either way)
# 3. Politician lost, retail actually did better (bad timing protected retail)
# 4. Both made money, but the gap or SPY context reveals something
if gap > 1.0:
    # Politician captured meaningfully more — the lag did its work
    verdict_class = "verdict-lie"
    label = "// The Lag Exposed"
    headline = f"{selected_politician} captured {pol_r:+.1f}%. You got {ret_r:+.1f}%."
    subline1 = (
        f"By the time you could legally act — {avg_lag:.0f} days after their trade — "
        f"the stocks had already moved {stats['avg_lag_alpha']:+.1f}% on average."
    )
    subline2 = (
        f"The disclosure lag stole {gap:.1f} percentage points of alpha you could never touch. "
        f"Meanwhile the S&P 500 returned {spy_r:+.1f}% to anyone who just held the index."
    )
elif pol_r < 0 and ret_r < 0:
    # Both lost money
    verdict_class = "verdict-lie"
    label = "// The Strategy Failed"
    headline = f"Both sides lost money on {selected_politician}'s trades."
    subline1 = f"{selected_politician} would have returned {pol_r:+.1f}% on these picks. You, copying them, got {ret_r:+.1f}%."
    subline2 = (
        f"The S&P 500 returned {spy_r:+.1f}% over the same window. "
        f"Buying the index beat copying the senator on both entry dates."
    )
elif ret_r > pol_r:
    # Rare case: retail outperformed because the politician's timing was bad
    verdict_class = "verdict-lie"
    label = "// Bad Timing, Mixed Signal"
    headline = f"You got {ret_r:+.1f}%. {selected_politician} would have gotten {pol_r:+.1f}%."
    subline1 = (
        f"In this sample, the politician's entry date was actually worse than the disclosure date — "
        f"stocks sometimes dropped during the {avg_lag:.0f}-day blackout. You benefited from their bad timing."
    )
    subline2 = (
        f"Neither outperformed the S&P 500, which returned {spy_r:+.1f}%. "
        f"Either strategy is still worse than the index. This is why the whole premise of copying is unreliable."
    )
elif spy_r > max(pol_r, ret_r):
    # Both made money but the S&P beat both
    verdict_class = "verdict-lie"
    label = "// The Index Still Wins"
    headline = f"Both strategies made money. The S&P 500 made more."
    subline1 = (
        f"{selected_politician}'s entry: {pol_r:+.1f}%. Retail copy: {ret_r:+.1f}%. "
        f"S&P 500 buy-and-hold: {spy_r:+.1f}%."
    )
    subline2 = (
        f"You could have skipped the analysis, bought an index fund, and outperformed the trade-copy strategy "
        f"by {spy_r - ret_r:.1f} percentage points."
    )
else:
    # Politician and retail both beat the S&P (rare)
    verdict_class = "verdict-truth"
    label = "// Signal Present"
    headline = f"{selected_politician}'s trades beat the market."
    subline1 = (
        f"{selected_politician} entry: {pol_r:+.1f}%. Retail copy: {ret_r:+.1f}%. "
        f"S&P 500: {spy_r:+.1f}%. Both entries outperformed the index."
    )
    subline2 = (
        f"Even so, the disclosure lag cost retail {gap:.1f} percentage points. "
        f"There is signal here — but by the time you can legally trade it, most of the alpha is gone."
    )

st.markdown(f"""
<div class="{verdict_class}">
    <div class="verdict-lie-label">{label}</div>
    <div class="verdict-lie-headline">{headline}</div>
    <div style="margin-top: 16px; font-size: 15px; line-height: 1.55; color: #a8a8a8;">{subline1}</div>
    <div style="margin-top: 10px; font-size: 15px; line-height: 1.55; color: #e5e5e5;">{subline2}</div>
</div>
""", unsafe_allow_html=True)

# ===================================================================
# HERO METRICS — the three-way comparison
# ===================================================================
st.markdown('<div class="section-label">// The Gap</div>', unsafe_allow_html=True)

h1, h2, h3 = st.columns(3)
with h1:
    st.metric(
        "Their Return",
        f"{pol_r:+.1f}%",
        help=f"What {selected_politician} hypothetically captured: bought on their trade date and held for {hold_days} days."
    )
with h2:
    st.metric(
        "Your Return",
        f"{ret_r:+.1f}%",
        help=f"What a retail buyer copying them actually gets: bought on the disclosure date ({avg_lag:.0f} days later on average) and held for {hold_days} days."
    )
with h3:
    st.metric(
        "The Gap",
        f"{gap:+.1f}pp",
        help="Percentage points of return the disclosure lag stole from retail. Positive means the politician captured alpha retail never could."
    )

# ===================================================================
# SECONDARY METRICS — 3 columns to avoid label truncation
# ===================================================================
st.markdown('<div class="section-label">// Detail</div>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.metric(
        "Their Win Rate",
        f"{stats['pol_win_rate']:.0f}%",
        help=f"Percentage of {selected_politician}'s {stats['trades']} trades that closed profitably when entered on their trade date."
    )
with m2:
    st.metric(
        "Your Win Rate",
        f"{stats['retail_win_rate']:.0f}%",
        help=f"Percentage of those same trades that closed profitably when entered on the disclosure date."
    )
with m3:
    st.metric(
        "S&P 500",
        f"{spy_r:+.1f}%" if spy_return is not None else "N/A",
        help="Simple buy-and-hold on SPY over the same window. The benchmark retail could always have chosen instead."
    )

m4, m5, m6 = st.columns(3)
with m4:
    st.metric(
        "Disclosure Lag",
        f"{avg_lag:.0f} days",
        help="Average days between a trade and its required disclosure under the STOCK Act. Law allows up to 45."
    )
with m5:
    st.metric(
        "Blackout Move",
        f"{stats['avg_lag_alpha']:+.1f}%",
        help="Average price change during the disclosure blackout — time retail had zero legal access to the information."
    )
with m6:
    st.metric(
        "Pre-Disclosure Runs",
        f"{stats['lag_blackout_rate']:.0f}%",
        help="Percentage of trades where the stock had already moved up before retail could legally act. The best entries were gone."
    )

# ===================================================================
# EQUITY CURVE — three lines
# ===================================================================
st.markdown('<div class="section-label">// Equity Curve</div>', unsafe_allow_html=True)
st.caption("$100 invested. Green: if you could have traded on the politician's schedule. Red: what you actually got. Dotted gray: just holding the S&P 500.")

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
    mode="lines", name=f"{selected_politician} (trade date entry)",
    line=dict(color="#00ff9f", width=3),
))
fig.add_trace(go.Scatter(
    x=retail_eq["date"], y=retail_eq["equity"],
    mode="lines", name="Retail copy (disclosure date entry)",
    line=dict(color="#ff4d4d", width=3),
))
if spy_df is not None:
    fig.add_trace(go.Scatter(
        x=spy_df["date"], y=spy_df["equity"],
        mode="lines", name="S&P 500 (buy & hold)",
        line=dict(color="#b0b0b0", width=2, dash="dot"),
    ))

fig.update_layout(
    plot_bgcolor="#0a0a0a",
    paper_bgcolor="#000000",
    font=dict(family="JetBrains Mono, monospace", color="#ffffff", size=12),
    hovermode="x unified",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="", showspikes=True),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Portfolio Value (Starting $100)"),
    height=500,
    margin=dict(l=50, r=60, t=20, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
)
fig.add_hline(
    y=100,
    line_dash="dash",
    line_color="rgba(255,255,255,0.15)",
    annotation_text="$100 start",
    annotation_position="top left",
)

st.plotly_chart(fig, use_container_width=True)

# ===================================================================
# TRADE-BY-TRADE BREAKDOWN
# ===================================================================
with st.expander(f"Trade-by-trade breakdown ({len(bt)} trades) — see exactly where the lag ate your alpha"):
    display_bt = bt[["ticker", "trade_date", "disclosure_date", "lag_days",
                     "pol_entry", "disc_price", "retail_exit_price",
                     "pol_return", "retail_return", "lag_alpha", "alpha_gap"]].copy()
    display_bt = display_bt.sort_values("trade_date", ascending=False)
    display_bt.columns = ["Ticker", "Trade Date", "Disclosed", "Lag (days)",
                          "Entry $", "Disclosure $", "Exit $",
                          "Their %", "Your %", "Lag Alpha %", "Gap (pp)"]
    st.dataframe(
        display_bt,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Their %": st.column_config.NumberColumn(format="%+.2f%%"),
            "Your %": st.column_config.NumberColumn(format="%+.2f%%"),
            "Lag Alpha %": st.column_config.NumberColumn(format="%+.2f%%",
                help="How much the stock moved during the blackout period"),
            "Gap (pp)": st.column_config.NumberColumn(format="%+.2f",
                help="Percentage points of return the politician captured over retail"),
        }
    )

# ===================================================================
# WORST LAG DAMAGE — single merged table
# ===================================================================
st.markdown('<div class="section-label" style="margin-top: 32px;">// Where The Lag Hurt Most</div>', unsafe_allow_html=True)
st.caption("The trades where the disclosure blackout created the biggest gap between what they captured and what retail got")

top_damage = bt.nlargest(8, "alpha_gap")[[
    "ticker", "trade_date", "disclosure_date", "lag_days",
    "pol_return", "retail_return", "alpha_gap", "lag_alpha"
]].copy()
top_damage.columns = [
    "Ticker", "Trade Date", "Disclosed", "Lag (days)",
    "Their %", "Your %", "Gap (pp)", "Blackout %"
]
st.dataframe(
    top_damage,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Their %": st.column_config.NumberColumn(format="%+.2f%%",
            help="What the politician's entry would have captured"),
        "Your %": st.column_config.NumberColumn(format="%+.2f%%",
            help="What you got copying on the disclosure date"),
        "Gap (pp)": st.column_config.NumberColumn(format="%+.2f",
            help="Percentage points the lag stole from you"),
        "Blackout %": st.column_config.NumberColumn(format="%+.2f%%",
            help="Pure price move during the blackout window"),
    }
)

# ===================================================================
# FOOTER
# ===================================================================
st.markdown(f"""
<div class="footer-card">
    <div class="footer-method">
        <strong>Methodology.</strong> For every purchase disclosed by the selected politician in the dataset, this tool simulates two entries: one on the politician's actual trade date (what they captured), and one on the disclosure date — the earliest a non-member could legally have known about the trade (what retail actually gets). Both hold for the same period. Sales are excluded because retail rarely shorts. The S&amp;P 500 benchmark is a simple buy-and-hold over the same window. Dataset currently covers {trades["transaction_date"].min().strftime("%b %Y")} to {trades["transaction_date"].max().strftime("%b %Y")} via the Quiver Quantitative live endpoint — older historical trades require a paid data tier.
    </div>
    <div class="footer-brand">
        Built by <a href="https://thefifthsignal.com" target="_blank">The Fifth Signal</a> &nbsp;·&nbsp; Data from public STOCK Act disclosures via Quiver Quantitative
    </div>
</div>

<div class="disclaimer">
    For informational and educational purposes only. Not investment advice. All performance data is hypothetical and derived from publicly disclosed congressional transactions. Past performance does not guarantee future results. Options trading involves substantial risk. The Fifth Signal is an educational publication and is not a registered investment advisor.
</div>
""", unsafe_allow_html=True)
