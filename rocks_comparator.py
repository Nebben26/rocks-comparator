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

    /* Core */
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stHeader"] { background: #000; }
    [data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * { color: #ffffff; }

    /* Headings — Space Grotesk */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.02em;
        color: #ffffff;
    }

    /* Main title */
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 48px;
        line-height: 1;
        letter-spacing: -0.03em;
        margin-bottom: 8px;
    }
    .main-title .accent {
        color: #00ff9f;
        text-shadow: 0 0 32px rgba(0,255,159,0.55);
    }
    .main-sub {
        color: #8a8a8a;
        font-size: 16px;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 40px;
    }
    .main-sub::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #00ff9f;
        border-radius: 50%;
        box-shadow: 0 0 12px #00ff9f;
        margin-right: 12px;
        vertical-align: middle;
    }

    /* Buttons */
    .stButton>button {
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
    .stButton>button:hover {
        box-shadow: 0 0 40px rgba(0,255,159,0.55);
        transform: translateY(-1px);
    }

    /* Selectbox + slider */
    .stSelectbox [data-baseweb="select"] > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.08);
        color: #fff;
        border-radius: 2px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 4px;
        padding: 24px;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #8a8a8a !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 36px !important;
        letter-spacing: -0.02em;
    }

    /* Dataframes */
    .stDataFrame { border: 1px solid rgba(255,255,255,0.08); }

    /* Verdict box — LIE */
    .verdict-lie {
        background: linear-gradient(135deg, rgba(255,77,77,0.08), rgba(255,77,77,0.02));
        border: 1px solid rgba(255,77,77,0.35);
        border-radius: 4px;
        padding: 24px 28px;
        margin: 12px 0;
    }
    .verdict-lie-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #ff4d4d;
        margin-bottom: 12px;
    }
    .verdict-lie-headline {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 24px;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    /* Verdict box — TRUTH */
    .verdict-truth {
        background: linear-gradient(135deg, rgba(0,255,159,0.08), rgba(0,255,159,0.02));
        border: 1px solid rgba(0,255,159,0.35);
        border-radius: 4px;
        padding: 24px 28px;
        margin: 12px 0;
    }
    .verdict-truth-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #00ff9f;
        margin-bottom: 12px;
    }
    .verdict-truth-headline {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 24px;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    /* Footer CTA */
    .cta-card {
        background: #0a0a0a;
        border: 1px solid rgba(0,255,159,0.35);
        border-radius: 4px;
        padding: 40px;
        text-align: center;
        margin-top: 60px;
    }
    .cta-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 32px;
        line-height: 1.1;
        letter-spacing: -0.02em;
        margin-bottom: 12px;
    }
    .cta-title .accent { color: #00ff9f; text-shadow: 0 0 24px rgba(0,255,159,0.55); }
    .cta-sub {
        color: #8a8a8a;
        font-size: 15px;
        margin-bottom: 24px;
    }
    .cta-button {
        display: inline-block;
        background: #00ff9f;
        color: #000 !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 16px 32px;
        border-radius: 2px;
        text-decoration: none;
        transition: all 0.3s;
    }
    .cta-button:hover {
        box-shadow: 0 0 40px rgba(0,255,159,0.55);
        transform: translateY(-2px);
    }

    /* Disclaimer */
    .disclaimer {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: #4a4a4a;
        line-height: 1.7;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.08);
        letter-spacing: 0.02em;
    }

    /* Info/warning boxes */
    [data-testid="stAlert"] {
        background: #0a0a0a;
        border: 1px solid rgba(0,255,159,0.25);
        border-radius: 4px;
    }
    [data-testid="stExpander"] {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 4px;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* Sidebar section labels */
    .sb-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #00ff9f;
        margin-top: 20px;
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

def backtest_copy_politician(trades_df, hold_days=90):
    """
    For each disclosed trade, simulate what a retail buyer would have
    experienced if they bought at the disclosure date (the only date
    they could realistically have acted) and held for hold_days.

    Returns: list of dicts with per-trade results.
    """
    results = []
    today = datetime.now().date()

    for _, row in trades_df.iterrows():
        ticker = row["ticker"]
        disc_date = row["disclosure_date"].date() if pd.notna(row["disclosure_date"]) else None
        if disc_date is None:
            continue
        if disc_date > today:
            continue

        exit_date = disc_date + timedelta(days=hold_days)
        if exit_date > today:
            exit_date = today

        # Only model purchases. Sales would require shorting which retail rarely does.
        if "sale" in str(row.get("type", "")).lower():
            continue

        prices = get_price_history(
            ticker,
            disc_date - timedelta(days=5),
            exit_date + timedelta(days=5),
        )
        if prices is None or len(prices) < 2:
            continue

        # Find closest entry / exit trading days
        entry_price = prices[prices.index.date >= disc_date].iloc[0] if any(prices.index.date >= disc_date) else None
        exit_prices = prices[prices.index.date <= exit_date]
        exit_price = exit_prices.iloc[-1] if len(exit_prices) > 0 else None

        if entry_price is None or exit_price is None or entry_price == 0:
            continue

        ret = (exit_price / entry_price - 1) * 100

        results.append({
            "politician": row["politician"],
            "ticker": ticker,
            "transaction_date": row["transaction_date"].date(),
            "disclosure_date": disc_date,
            "exit_date": exit_date,
            "entry_price": round(float(entry_price), 2),
            "exit_price": round(float(exit_price), 2),
            "return_pct": round(float(ret), 2),
        })

    return pd.DataFrame(results)


def get_spy_benchmark(start, end):
    """Returns SPY total return between two dates."""
    prices = get_price_history("SPY", start, end + timedelta(days=5))
    if prices is None or len(prices) < 2:
        return None
    return (prices.iloc[-1] / prices.iloc[0] - 1) * 100


def compute_portfolio_stats(bt_results):
    """Summary stats from per-trade results."""
    if len(bt_results) == 0:
        return None

    returns = bt_results["return_pct"]
    wins = (returns > 0).sum()
    losses = (returns <= 0).sum()
    total_trades = len(returns)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_return = returns.mean()
    median_return = returns.median()

    # Equal-weighted portfolio equity curve
    bt_sorted = bt_results.sort_values("disclosure_date").reset_index(drop=True)
    cumulative = 100.0
    equity = []
    # Simplified: each trade represents a 1/N allocation sequentially — compound
    for _, t in bt_sorted.iterrows():
        cumulative *= (1 + t["return_pct"] / 100) ** (1 / total_trades)
        equity.append({"date": t["exit_date"], "equity": cumulative})
    equity_df = pd.DataFrame(equity)

    total_return = cumulative - 100

    # Max drawdown from equity curve
    if len(equity_df) > 0:
        peak = equity_df["equity"].cummax()
        dd = (equity_df["equity"] / peak - 1) * 100
        max_dd = dd.min()
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
<div class="main-sub">The Rocks Thrown Comparator · Powered by The Fifth Signal</div>
<div class="main-title">They watch politicians.<br><span class="accent">We watch what politicians watch.</span></div>
""", unsafe_allow_html=True)

st.markdown(
    "Run the numbers yourself. Pick any politician, pick any hold period, "
    "and see what copying their trades would have actually returned — using their "
    "real disclosed trades and the real date a retail buyer could have acted on them.",
)

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

st.caption(f"Data source: **{source_name}** · {len(trades):,} trades loaded · Updated daily")

# ===================================================================
# SIDEBAR CONTROLS
# ===================================================================
st.sidebar.markdown('<div class="sb-label">// Target</div>', unsafe_allow_html=True)

politicians = sorted(trades["politician"].dropna().unique().tolist())
# Put well-known names at top
priority = ["Nancy Pelosi", "Paul Pelosi", "Dan Crenshaw", "Marjorie Taylor Greene",
            "Josh Gottheimer", "Ro Khanna", "Mark Green", "Tommy Tuberville",
            "Shelley Moore Capito", "Ron Wyden"]
priority_present = [p for p in priority if p in politicians]
others = [p for p in politicians if p not in priority_present]
ordered = priority_present + others

selected_politician = st.sidebar.selectbox(
    "Politician",
    ordered,
    index=0 if ordered else None,
)

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
    r = backtest_copy_politician(chunk, hold_days=hold_days)
    bt_chunks.append(r)
    progress.progress(min(1.0, (i + chunk_size) / len(filtered)),
                      text=f"Running backtest... ({min(i+chunk_size, len(filtered))}/{len(filtered)} trades)")
progress.empty()

bt = pd.concat(bt_chunks, ignore_index=True) if bt_chunks else pd.DataFrame()

if len(bt) == 0:
    st.warning("No trades could be priced (tickers may be delisted or outside yfinance coverage).")
    st.stop()

stats = compute_portfolio_stats(bt)

# SPY benchmark over the same period
bt_start = bt["disclosure_date"].min()
bt_end = bt["exit_date"].max()
spy_return = get_spy_benchmark(bt_start, bt_end)

# ===================================================================
# VERDICT HEADLINE
# ===================================================================
st.markdown("---")
st.markdown(f"### Results · Copying {selected_politician}")

col_a, col_b = st.columns(2)
with col_a:
    if stats["total_return"] < 0 or (spy_return and stats["total_return"] < spy_return):
        st.markdown(f"""
        <div class="verdict-lie">
            <div class="verdict-lie-label">// The Lie Exposed</div>
            <div class="verdict-lie-headline">
                Copying {selected_politician} returned {stats['total_return']:+.1f}%<br>
                {"· Lost money" if stats['total_return'] < 0 else f"· Underperformed S&P by {spy_return - stats['total_return']:.1f}pp" if spy_return else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-truth">
            <div class="verdict-truth-label">// Mixed Signal</div>
            <div class="verdict-truth-headline">
                Copying {selected_politician} returned {stats['total_return']:+.1f}%<br>
                · {"Beat" if spy_return and stats['total_return'] > spy_return else "Matched"} S&P — but disclosure lag kills scalability
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div class="verdict-truth">
        <div class="verdict-truth-label">// The Fifth Signal Thesis</div>
        <div class="verdict-truth-headline">
            Track the data politicians react to — not their 45-day-old filings.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===================================================================
# METRICS
# ===================================================================
st.markdown("### Performance Metrics")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Return", f"{stats['total_return']:+.1f}%",
              delta=f"{stats['total_return'] - spy_return:+.1f}pp vs S&P" if spy_return else None)
with m2:
    st.metric("Win Rate", f"{stats['win_rate']}%",
              help=f"{stats['wins']} winners / {stats['losses']} losers")
with m3:
    st.metric("Avg Trade", f"{stats['avg_return']:+.2f}%")
with m4:
    st.metric("Max Drawdown", f"{stats['max_drawdown']:.1f}%")

m5, m6, m7, m8 = st.columns(4)
with m5:
    st.metric("Trades Backtested", f"{stats['trades']}")
with m6:
    st.metric("S&P 500 Benchmark", f"{spy_return:+.1f}%" if spy_return else "N/A",
              help="Total return on SPY over the same date range")
with m7:
    exit_liq_score = max(0, min(100, int(50 + (spy_return - stats['total_return']) if spy_return else 50)))
    st.metric("Exit Liquidity Score", f"{exit_liq_score}/100",
              help="Higher = more likely retail was exit liquidity. Based on underperformance vs S&P.")
with m8:
    st.metric("Median Trade", f"{stats['median_return']:+.2f}%")

# ===================================================================
# EQUITY CURVE
# ===================================================================
st.markdown("### Equity Curve")

equity_df = stats["equity_curve"]

# Build SPY curve starting at same base
if spy_return is not None:
    spy_prices = get_price_history("SPY", bt_start, bt_end + timedelta(days=5))
    if spy_prices is not None:
        spy_df = pd.DataFrame({
            "date": spy_prices.index.date,
            "equity": (spy_prices.values / spy_prices.iloc[0]) * 100
        })
    else:
        spy_df = None
else:
    spy_df = None

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=equity_df["date"], y=equity_df["equity"],
    mode="lines", name=f"Copy {selected_politician}",
    line=dict(color="#ff4d4d", width=3),
    fill="tozeroy", fillcolor="rgba(255,77,77,0.05)",
))
if spy_df is not None:
    fig.add_trace(go.Scatter(
        x=spy_df["date"], y=spy_df["equity"],
        mode="lines", name="S&P 500 (Buy & Hold)",
        line=dict(color="#8a8a8a", width=2, dash="dot"),
    ))

fig.update_layout(
    plot_bgcolor="#0a0a0a",
    paper_bgcolor="#000000",
    font=dict(family="JetBrains Mono, monospace", color="#ffffff", size=12),
    hovermode="x unified",
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="", showspikes=True),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Portfolio Value (Starting $100)"),
    height=500,
    margin=dict(l=40, r=20, t=20, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
    ),
)
# Add $100 baseline
fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.15)",
              annotation_text="Starting Capital", annotation_position="right")

st.plotly_chart(fig, use_container_width=True)

# ===================================================================
# TRADE-BY-TRADE BREAKDOWN
# ===================================================================
with st.expander(f"Trade-by-trade breakdown ({len(bt)} trades)"):
    display_bt = bt.copy()
    display_bt = display_bt.sort_values("disclosure_date", ascending=False)
    display_bt.columns = ["Politician", "Ticker", "Trade Date", "Disclosure Date",
                          "Exit Date", "Entry $", "Exit $", "Return %"]
    st.dataframe(
        display_bt,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Return %": st.column_config.NumberColumn(
                format="%+.2f%%",
            ),
        }
    )

# ===================================================================
# BIGGEST WINNERS + LOSERS
# ===================================================================
w_col, l_col = st.columns(2)
with w_col:
    st.markdown("#### Biggest Winners")
    winners = bt.nlargest(5, "return_pct")[["ticker", "disclosure_date", "return_pct"]]
    winners.columns = ["Ticker", "Disclosed", "Return %"]
    st.dataframe(winners, use_container_width=True, hide_index=True,
                 column_config={"Return %": st.column_config.NumberColumn(format="%+.2f%%")})

with l_col:
    st.markdown("#### Biggest Losers")
    losers = bt.nsmallest(5, "return_pct")[["ticker", "disclosure_date", "return_pct"]]
    losers.columns = ["Ticker", "Disclosed", "Return %"]
    st.dataframe(losers, use_container_width=True, hide_index=True,
                 column_config={"Return %": st.column_config.NumberColumn(format="%+.2f%%")})

# ===================================================================
# FOOTER CTA
# ===================================================================
st.markdown(f"""
<div class="cta-card">
    <div class="cta-title">Stop trading <span class="accent">yesterday's news.</span></div>
    <div class="cta-sub">
        The politicians aren't the signal. The data they're reacting to is.<br>
        Two weeks. One dollar. Every alert. Every loser published.
    </div>
    <a href="https://thecapitoldossier.com" class="cta-button" target="_blank">
        Start 14-Day Trial · $1 →
    </a>
</div>

<div class="disclaimer">
    This tool is provided for informational and educational purposes only. It is not investment advice.
    All performance data is hypothetical and based on publicly disclosed congressional transactions.
    The "copy politician" strategy modeled here assumes a retail buyer purchases each disclosed trade
    at the disclosure date (the earliest a non-member could realistically act) and holds for the
    selected period. Past performance does not guarantee future results. Options trading involves
    substantial risk. The Fifth Signal is an educational options alerts publication and is not a
    registered investment advisor. Data sourced from public STOCK Act disclosures.
</div>
""", unsafe_allow_html=True)
