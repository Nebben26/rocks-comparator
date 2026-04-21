"""
THE ROCKS THROWN COMPARATOR · Signal 05
Backend preserved from the original. Layout rewritten to the user's scaffold:
left = politician picker; right = one verdict line + one chart.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime, timedelta
from urllib.parse import quote as urlquote


st.set_page_config(
    page_title="Signal 05 · Congressional Conflict Score",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===================================================================
# CSS
# ===================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

.stApp {
    background: #000000;
    color: #ffffff;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.main .block-container {
    max-width: 1400px;
    padding: 1rem 2rem 3rem 2rem;
}

/* Kill Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stDeployButton"] { display: none !important; }

/* Tight column gap */
[data-testid="stHorizontalBlock"] { gap: 1rem !important; }

/* Zero out Streamlit inter-element margins in columns so the panel reads as one unit */
[data-testid="element-container"] { margin-bottom: 0 !important; }
[data-testid="stVerticalBlockBorderWrapper"] { gap: 0 !important; }
div[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* Header strip */
.tool-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 1rem;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #8a8a8a;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding-bottom: 0.55rem;
}
.tool-title { color: #00ff9f; font-weight: 600; }
.tool-meta { font-size: 0.68rem; }

/* ---------- LEFT COLUMN: PICKER ---------- */
.picker-head {
    background: #0a0a0a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 4px 0 0;
    border-bottom: none;
    padding: 0.75rem 0.9rem 0.5rem;
}
.picker-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #8a8a8a;
    margin-bottom: 0.25rem;
}
.picker-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #4a4a4a;
    letter-spacing: 0.05em;
}

/* Search box — styled to sit flush with picker-head above and list below */
.stTextInput {
    background: #0a0a0a;
    border-left: 1px solid rgba(255,255,255,0.08);
    border-right: 1px solid rgba(255,255,255,0.08);
    padding: 0 0.9rem 0.55rem !important;
}
.stTextInput > div { background: transparent !important; }
.stTextInput label { display: none !important; }
.stTextInput input {
    background: #000 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    padding: 0.42rem 0.55rem !important;
    border-radius: 3px !important;
}
.stTextInput input:focus {
    border-color: rgba(0,255,159,0.4) !important;
    box-shadow: 0 0 0 1px rgba(0,255,159,0.25) !important;
}

/* Politician list */
.pol-list {
    background: #0a0a0a;
    border: 1px solid rgba(255,255,255,0.08);
    border-top: none;
    border-radius: 0 0 4px 4px;
    padding: 0.35rem 0.55rem 0.55rem;
    max-height: 560px;
    overflow-y: auto;
}
.pol-list::-webkit-scrollbar { width: 6px; }
.pol-list::-webkit-scrollbar-track { background: transparent; }
.pol-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }

.pol-item {
    display: grid;
    grid-template-columns: 1.3fr 0.6fr 0.7fr;
    column-gap: 0.4rem;
    align-items: center;
    padding: 0.45rem 0.55rem;
    margin: 0.15rem 0;
    border: 1px solid transparent;
    border-radius: 3px;
    text-decoration: none;
    color: inherit;
    transition: background 0.15s, border-color 0.15s;
}
.pol-item:hover {
    background: rgba(255,255,255,0.025);
    border-color: rgba(255,255,255,0.08);
}
.pol-item.active {
    border-color: #00ff9f;
    background: rgba(0,255,159,0.06);
}
.pol-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    color: #fff;
    line-height: 1.15;
    letter-spacing: -0.01em;
}
.pol-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #8a8a8a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 2px;
}
.pol-s-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: #6a6a6a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    line-height: 1;
    margin-bottom: 2px;
}
.pol-s-value {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    color: #fff;
    line-height: 1;
    letter-spacing: -0.02em;
}
.pol-s-value.dim { color: #4a4a4a; font-weight: 400; }

/* ---------- RIGHT COLUMN: HERO ---------- */
.hero-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    background: #0a0a0a;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 4px 0 0;
    border-bottom: none;
    padding: 0.85rem 1rem 0.6rem;
    gap: 1rem;
    flex-wrap: wrap;
}
.hero-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: #fff;
    letter-spacing: -0.015em;
}
.hero-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #8a8a8a;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 3px;
}
.hero-hold {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: nowrap;
}
.hold-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #6a6a6a;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.hold-row {
    display: flex;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 2px;
    overflow: hidden;
}
.hold-pill {
    padding: 0.3rem 0.55rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #8a8a8a;
    text-decoration: none;
    border-right: 1px solid rgba(255,255,255,0.08);
    letter-spacing: 0.05em;
    transition: all 0.15s;
}
.hold-pill:last-child { border-right: none; }
.hold-pill:hover { color: #fff; background: rgba(255,255,255,0.03); }
.hold-pill.active { background: rgba(0,255,159,0.1); color: #00ff9f; }

/* Verdict line */
.verdict-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    color: #d0d0d0;
    background: #0a0a0a;
    border-left: 1px solid rgba(255,255,255,0.08);
    border-right: 1px solid rgba(255,255,255,0.08);
    padding: 0.35rem 1rem 0.7rem;
}
.verdict-line .good { color: #00ff9f; font-weight: 600; }
.verdict-line .muted { color: #b8b8b8; font-weight: 500; }
.verdict-line .bad  { color: #ff4d4d; font-weight: 600; }
.verdict-line .gap-val { color: #ff4d4d; font-weight: 700; }
.verdict-line .gap-val.pos { color: #00ff9f; }

/* Chart wrapper — plotly container becomes the middle of the card */
[data-testid="stPlotlyChart"] {
    background: #000000 !important;
    border-left: 1px solid rgba(255,255,255,0.08) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    padding: 0.2rem 0.4rem 0.2rem !important;
}

/* Caption */
.chart-caption {
    background: #0a0a0a;
    border: 1px solid rgba(255,255,255,0.08);
    border-top: none;
    border-radius: 0 0 4px 4px;
    padding: 0.55rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #8a8a8a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ---------- LEDGER ---------- */
.ledger-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #8a8a8a;
    margin: 1.4rem 0 0.55rem;
    font-weight: 600;
}
.stDataFrame {
    background: #0a0a0a !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 4px !important;
}

/* Progress bar */
[data-testid="stProgress"] > div > div > div { background: #00ff9f !important; }

/* Alerts */
[data-testid="stAlert"] {
    background: #0a0a0a !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 3px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)


# ===================================================================
# DATA LOADING   (UNCHANGED from original)
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
    # Optional — present on some Quiver endpoints, absent on others. Purely additive.
    for k in ["party"]:
        if k in lower_cols:
            out["party"] = df[lower_cols[k]].astype(str).str.strip()
            break
    for k in ["state"]:
        if k in lower_cols:
            out["state"] = df[lower_cols[k]].astype(str).str.strip()
            break
    for k in ["chamber", "house", "body"]:
        if k in lower_cols:
            out["chamber"] = df[lower_cols[k]].astype(str).str.strip()
            break

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
# BACKTEST LOGIC   (UNCHANGED from original)
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
# UI HELPERS (pandas aggregation only, no data fetch, no backtest)
# ===================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def build_politician_summary(trades_df):
    """Per-politician aggregates from the already-loaded trades dataframe."""
    purchases = trades_df[~trades_df["type"].str.contains("sale", case=False, na=False)].copy()
    purchases["lag_days"] = (purchases["disclosure_date"] - purchases["transaction_date"]).dt.days
    agg_spec = {
        "trades": ("ticker", "count"),
        "avg_lag_days": ("lag_days", "mean"),
        "latest_trade": ("transaction_date", "max"),
    }
    for col in ["party", "state", "chamber"]:
        if col in purchases.columns:
            agg_spec[col] = (col, "first")
    g = purchases.groupby("politician").agg(**agg_spec).reset_index()
    g["avg_lag_days"] = g["avg_lag_days"].fillna(30).round(0).astype(int)
    return g


FEATURED_POLITICIANS = [
    "Nancy Pelosi",
    "Dan Crenshaw",
    "Tommy Tuberville",
    "Michael McCaul",
    "Josh Gottheimer",
    "Mark Green",
    "Kevin Hern",
    "Ro Khanna",
    "Kathy Manning",
    "Alan Lowenthal",
    "Maxine Waters",
    "Ron Wyden",
    "Richard Burr",
    "Kelly Loeffler",
    "David Perdue",
    "Marjorie Taylor Greene",
]


@st.cache_data(ttl=86400, show_spinner=False)
def pick_default_politician(trades, hold_days=90):
    """Prescan a short featured list, pick the politician with the most brutal gap.

    Rules (per user):
      - pol return meaningfully positive
      - retail return flat or negative
      - gap large enough to be visually obvious
    Sort surviving candidates by biggest positive gap; fall back to max-gap overall,
    then to most-traded politician if the prescan returns nothing usable.
    """
    cache = {}
    for name in FEATURED_POLITICIANS:
        if name not in trades["politician"].values:
            continue
        tr = trades[
            (trades["politician"] == name) &
            (~trades["type"].str.contains("sale", case=False, na=False))
        ]
        if len(tr) < 3:
            continue
        bt = backtest_with_lag_analysis(tr, hold_days=hold_days)
        if len(bt) < 3:
            continue
        s = compute_lag_stats(bt)
        cache[name] = {
            "pol_return": s["politician_return"],
            "retail_return": s["retail_return"],
            "gap": s["alpha_gap"],
        }

    if not cache:
        fallback = trades["politician"].value_counts().idxmax() if len(trades) else ""
        return fallback, {}

    # Slam-dunk filter: pol solidly positive, retail flat/neg, gap >= 2pp (more inclusive for real data)
    slam_dunks = [
        (n, d) for n, d in cache.items()
        if d["pol_return"] > 1.5 and d["retail_return"] <= 2.0 and d["gap"] >= 2.0
    ]
    if slam_dunks:
        best = max(slam_dunks, key=lambda x: x[1]["gap"])[0]
    else:
        # Fall back to biggest positive gap among prescanned
        positive = [(n, d) for n, d in cache.items() if d["gap"] > 0]
        if positive:
            best = max(positive, key=lambda x: x[1]["gap"])[0]
        else:
            best = max(cache.items(), key=lambda x: x[1]["gap"])[0]

    # Return only the gap-per-name dict for cache seeding
    return best, {n: d["gap"] for n, d in cache.items()}


def relative_date(d):
    if pd.isna(d):
        return "—"
    if hasattr(d, 'date'):
        d = d.date()
    days = (datetime.now().date() - d).days
    if days < 0: return "future"
    if days == 0: return "today"
    if days < 7: return f"{days}d ago"
    if days < 30: return f"{days // 7}w ago"
    if days < 365: return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


# ===================================================================
# LOAD DATA
# ===================================================================

with st.spinner("Loading Quiver data..."):
    trades, source_name = load_congressional_trades()

if trades is None:
    if source_name == "NO_API_KEY":
        st.error("Quiver API key not configured. Set `QUIVER_API_KEY` in App Settings → Secrets.")
    elif source_name == "INVALID_API_KEY":
        st.error("Quiver returned 401. Invalid or expired key.")
    elif source_name == "RATE_LIMITED":
        st.error("Quiver returned 429. Rate limited — wait a few minutes.")
    elif source_name.startswith("ALL_ENDPOINTS_FAILED"):
        st.error("All Quiver endpoints failed.")
        st.code(source_name, language="text")
    elif source_name.startswith("COLUMN_MAPPING"):
        st.error("Column mapping failed.")
        st.code(source_name, language="text")
    else:
        st.warning(f"Load failed: `{source_name}`.")
    uploaded = st.file_uploader("Upload CSV fallback", type=["csv"])
    if uploaded:
        trades = normalize_df(pd.read_csv(uploaded), "upload")
        source_name = "Manual Upload"
    else:
        st.stop()

summary = build_politician_summary(trades)


# ===================================================================
# QUERY PARAM STATE
# ===================================================================

qp = st.query_params
try:
    hold_days = int(qp.get("hold", "90"))
except Exception:
    hold_days = 90
if hold_days not in [30, 60, 90, 180, 365]:
    hold_days = 90

if len(summary) == 0:
    st.error("No politicians with purchase trades in the dataset.")
    st.stop()

# Hero default: prescan a featured list, pick the most brutal example.
with st.spinner("Warming up..."):
    prescan_default, prescan_gaps = pick_default_politician(trades, hold_days=hold_days)

if "gap_cache" not in st.session_state:
    st.session_state["gap_cache"] = {}
# Seed the gap cache with prescan results so featured names show real gaps immediately
for _name, _gap in prescan_gaps.items():
    st.session_state["gap_cache"].setdefault(_name, _gap)

default_pol = prescan_default if prescan_default else summary.sort_values("trades", ascending=False).iloc[0]["politician"]
selected_politician = qp.get("p", default_pol)
if selected_politician not in summary["politician"].values:
    selected_politician = default_pol


# ===================================================================
# HEADER STRIP
# ===================================================================

latest_trade_date = trades["transaction_date"].max().strftime("%b %d, %Y")
st.markdown(f"""
<div class="tool-header">
  <div class="tool-title">Signal 05 · Congressional Conflict Score</div>
  <div class="tool-meta">Data from Quiver · Updated {latest_trade_date}</div>
</div>
""", unsafe_allow_html=True)


# ===================================================================
# TWO-COLUMN LAYOUT
# ===================================================================

col_left, col_right = st.columns([0.38, 0.62], gap="small")


# ---------------- LEFT: PICKER ----------------

with col_left:
    st.markdown("""
    <div class="picker-head">
      <div class="picker-title">Politician Backtest</div>
      <div class="picker-sub">Search. Click one. Right side shows you vs them.</div>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input(
        "Search",
        key="pol_search",
        label_visibility="collapsed",
        placeholder="Search name...",
    )

    q = (search or "").strip().lower()
    filtered_sum = summary.copy()
    if q:
        filtered_sum = filtered_sum[filtered_sum["politician"].str.lower().str.contains(q, na=False)]
    filtered_sum = filtered_sum.sort_values("trades", ascending=False).head(60)

    gap_cache = st.session_state["gap_cache"]

    rows = []
    for _, r in filtered_sum.iterrows():
        name = r["politician"]
        is_active = (name == selected_politician)
        trades_count = int(r["trades"])
        avg_lag = int(r["avg_lag_days"])

        # Meta line: prefer party · state · chamber; fall back to latest-activity
        meta_bits = []
        party_val = r.get("party") if "party" in r.index else None
        state_val = r.get("state") if "state" in r.index else None
        chamber_val = r.get("chamber") if "chamber" in r.index else None
        if pd.notna(party_val) and str(party_val).strip() and str(party_val).lower() != "nan":
            meta_bits.append(str(party_val)[:1].upper())
        if pd.notna(state_val) and str(state_val).strip() and str(state_val).lower() != "nan":
            meta_bits.append(str(state_val).upper()[:2])
        if pd.notna(chamber_val) and str(chamber_val).strip() and str(chamber_val).lower() != "nan":
            ch = str(chamber_val).strip()
            meta_bits.append("House" if "house" in ch.lower() or ch.lower() == "h" else ("Senate" if "senate" in ch.lower() or ch.lower() == "s" else ch))
        if meta_bits:
            meta_line = " · ".join(meta_bits) + f" · {avg_lag}d lag"
        else:
            meta_line = f"{relative_date(r['latest_trade'])} · {avg_lag}d avg lag"

        gap_val = gap_cache.get(name)
        if gap_val is not None:
            gap_display = f"{gap_val:+.1f}pp"
            gap_class = ""
        else:
            gap_display = "—"
            gap_class = " dim"

        href = f"?p={urlquote(name)}&hold={hold_days}"
        active_cls = " active" if is_active else ""

        rows.append(
            f'<a href="{href}" class="pol-item{active_cls}" target="_self">'
            f'<div><div class="pol-name">{name}</div><div class="pol-meta">{meta_line}</div></div>'
            f'<div><div class="pol-s-label">Trades</div><div class="pol-s-value">{trades_count}</div></div>'
            f'<div><div class="pol-s-label">Avg. Gap</div><div class="pol-s-value{gap_class}">{gap_display}</div></div>'
            f'</a>'
        )

    st.markdown(f'<div class="pol-list">{"".join(rows)}</div>', unsafe_allow_html=True)


# ---------------- RIGHT: HERO (verdict + one chart) ----------------

filtered_trades = trades[
    (trades["politician"] == selected_politician) &
    (~trades["type"].str.contains("sale", case=False, na=False))
].copy()

with col_right:
    if len(filtered_trades) == 0:
        st.warning(f"No purchase trades found for {selected_politician}.")
        st.stop()

    progress = st.progress(0, text=f"Running backtest on {len(filtered_trades)} trades...")
    bt_chunks = []
    chunk_size = max(1, len(filtered_trades) // 20)
    for i in range(0, len(filtered_trades), chunk_size):
        chunk = filtered_trades.iloc[i:i+chunk_size]
        r = backtest_with_lag_analysis(chunk, hold_days=hold_days)
        bt_chunks.append(r)
        progress.progress(
            min(1.0, (i + chunk_size) / len(filtered_trades)),
            text=f"Running backtest... ({min(i+chunk_size, len(filtered_trades))}/{len(filtered_trades)})",
        )
    progress.empty()

    bt = pd.concat(bt_chunks, ignore_index=True) if bt_chunks else pd.DataFrame()
    if len(bt) == 0:
        st.warning("No priceable trades (tickers may be delisted or outside yfinance coverage).")
        st.stop()

    stats = compute_lag_stats(bt)
    pol_r = stats["politician_return"]
    ret_r = stats["retail_return"]
    gap = stats["alpha_gap"]
    avg_lag = int(round(stats["avg_lag_days"]))

    # Conditional verdict text and annotation based on who actually won (for honest communication)
    if gap >= 0:
        gap_text = f"{gap:.1f}pp stolen by the lag"
        gap_class = "gap-val"
        annotation_text = f"<b>{gap:.1f}pp</b> stolen"
        annotation_color = "#ff4d4d"
    else:
        gap_text = f"{abs(gap):.1f}pp retail outperformed"
        gap_class = "gap-val pos"
        annotation_text = f"<b>{abs(gap):.1f}pp</b> retail beat"
        annotation_color = "#00ff9f"

    # Cache the computed gap so the left-list "Avg. Gap" column fills in over time
    st.session_state["gap_cache"][selected_politician] = gap

    # --- Hero top row: name + meta + hold pills ---
    active_row = summary[summary["politician"] == selected_politician].iloc[0]
    active_latest = relative_date(active_row["latest_trade"])

    hero_meta_bits = []
    for col, fmt in [("party", lambda v: str(v)[:1].upper()),
                     ("state", lambda v: str(v).upper()[:2]),
                     ("chamber", lambda v: "House" if "house" in str(v).lower() or str(v).lower() == "h" else ("Senate" if "senate" in str(v).lower() or str(v).lower() == "s" else str(v)))]:
        if col in active_row.index:
            val = active_row[col]
            if pd.notna(val) and str(val).strip() and str(val).lower() != "nan":
                hero_meta_bits.append(fmt(val))
    hero_meta_bits.append(f"{int(active_row['trades'])} trades")
    hero_meta_bits.append(f"latest {active_latest}")
    hero_meta = " · ".join(hero_meta_bits)

    hold_options = [30, 60, 90, 180, 365]
    hold_pills = "".join(
        f'<a href="?p={urlquote(selected_politician)}&hold={h}" '
        f'class="hold-pill{" active" if h == hold_days else ""}" target="_self">{h}d</a>'
        for h in hold_options
    )

    st.markdown(f"""
    <div class="hero-top">
      <div>
        <div class="hero-name">{selected_politician}</div>
        <div class="hero-meta">{hero_meta}</div>
      </div>
      <div class="hero-hold">
        <span class="hold-lbl">Hold</span>
        <div class="hold-row">{hold_pills}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Verdict line: one sentence, always the same shape ---
    st.markdown(f"""
    <div class="verdict-line">
      They captured <span class="good">{pol_r:+.1f}%</span>
      · You get <span class="muted">{ret_r:+.1f}%</span>
      · <span class="{gap_class}">{gap_text}</span>
    </div>
    """, unsafe_allow_html=True)

    # --- One chart: two lines, shaded gap, midpoint label ---
    pol_eq = stats["pol_equity_curve"]
    retail_eq = stats["retail_equity_curve"]

    fig = go.Figure()

    # Retail (red) first so the politician line's fill="tonexty" shades between them
    fig.add_trace(go.Scatter(
        x=retail_eq["date"],
        y=retail_eq["equity"],
        mode="lines",
        name="You",
        line=dict(color="#ff4d4d", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=pol_eq["date"],
        y=pol_eq["equity"],
        mode="lines",
        name="Them",
        line=dict(color="#00ff9f", width=3),
        fill="tonexty",
        fillcolor="rgba(255,77,77,0.10)",
    ))

    # End-point value callouts for instant comprehension
    if len(pol_eq) > 0:
        fig.add_annotation(
            x=pol_eq["date"].iloc[-1],
            y=pol_eq["equity"].iloc[-1],
            text=f"Them {pol_r:+.1f}%",
            showarrow=False,
            font=dict(family="JetBrains Mono", size=9, color="#00ff9f"),
            xanchor="left",
            yanchor="middle",
            bgcolor="rgba(0,0,0,0.6)",
            borderpad=3,
        )
    if len(retail_eq) > 0:
        fig.add_annotation(
            x=retail_eq["date"].iloc[-1],
            y=retail_eq["equity"].iloc[-1],
            text=f"You {ret_r:+.1f}%",
            showarrow=False,
            font=dict(family="JetBrains Mono", size=9, color="#ff4d4d"),
            xanchor="left",
            yanchor="middle",
            bgcolor="rgba(0,0,0,0.6)",
            borderpad=3,
        )

    # One inline label over the gap
    if len(pol_eq) > 0 and len(retail_eq) > 0:
        mid_p = len(pol_eq) // 2
        mid_r = min(mid_p, len(retail_eq) - 1)
        mid_x = pol_eq["date"].iloc[mid_p]
        mid_y = (pol_eq["equity"].iloc[mid_p] + retail_eq["equity"].iloc[mid_r]) / 2
        fig.add_annotation(
            x=mid_x, y=mid_y,
            text=annotation_text,
            showarrow=False,
            font=dict(family="JetBrains Mono", size=12, color=annotation_color),
            bgcolor="rgba(0,0,0,0.78)",
            bordercolor="rgba(255,77,77,0.5)" if gap >= 0 else "rgba(0,255,159,0.5)",
            borderwidth=1,
            borderpad=5,
        )

    fig.update_layout(
        height=400,
        margin=dict(l=50, r=20, t=26, b=36),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(family="JetBrains Mono", size=10, color="#8a8a8a"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.08)",
            title="",
            showspikes=False,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.08)",
            title="",
            showticklabels=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1.0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#b0b0b0"),
        ),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # --- Caption ---
    st.markdown(f"""
    <div class="chart-caption">
      {stats['trades']} trades · {hold_days}-day hold · avg. disclosure lag {avg_lag} days
    </div>
    """, unsafe_allow_html=True)


# ===================================================================
# BELOW FOLD: PER-TRADE TABLE
# ===================================================================

st.markdown('<div class="ledger-title">Per-trade breakdown</div>', unsafe_allow_html=True)

display_bt = bt[["ticker", "trade_date", "disclosure_date", "lag_days",
                 "pol_return", "retail_return", "alpha_gap"]].copy()
display_bt = display_bt.sort_values("alpha_gap", ascending=False)
display_bt.columns = ["Ticker", "Trade Date", "Disclosed", "Lag (days)",
                      "Their %", "Your %", "Gap (pp)"]


def _style_gap(v):
    try:
        x = float(v)
    except Exception:
        return ""
    if x > 1.0:
        return "color: #ff4d4d; font-weight: 600"
    if x < -1.0:
        return "color: #00ff9f; font-weight: 600"
    return "color: #8a8a8a"


styled_bt = display_bt.style.map(_style_gap, subset=["Gap (pp)"])

st.dataframe(
    styled_bt,
    use_container_width=True,
    hide_index=True,
    height=min(460, 38 * (len(display_bt) + 1) + 3),
    column_config={
        "Their %": st.column_config.NumberColumn(format="%+.2f%%"),
        "Your %": st.column_config.NumberColumn(format="%+.2f%%"),
        "Gap (pp)": st.column_config.NumberColumn(format="%+.2f"),
    },
)
