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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg: #000000;
  --panel: #070707;
  --panel-2: #0b0b0b;
  --border: rgba(255,255,255,0.09);
  --muted: #8a8f98;
  --muted-2: #5d636d;
  --text: #f4f7fa;
  --signal: #00ff9f;
  --signal-soft: rgba(0,255,159,0.10);
  --danger: #ff4d4d;
  --danger-soft: rgba(255,77,77,0.14);
}

html, body, [class*="css"]  {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.stApp {
  background:
    radial-gradient(circle at top left, rgba(0,255,159,0.055), transparent 28%),
    linear-gradient(180deg, #030303 0%, #000000 100%);
  color: var(--text);
}
.main .block-container {
  max-width: 1480px;
  padding: 1.1rem 1.6rem 3rem 1.6rem;
}

#MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stStatusWidget"], [data-testid="stDecoration"], [data-testid="stDeployButton"] { display:none !important; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display:none !important; }
[data-testid="element-container"] { margin-bottom: 0 !important; }
div[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 1.15rem !important; }
a, a:hover, a:visited { text-decoration: none !important; }

/* header */
.top-shell {
  display:flex; justify-content:space-between; align-items:flex-end; gap:1rem; flex-wrap:wrap;
  margin-bottom: 0.95rem;
  border-bottom:1px solid var(--border); padding-bottom:0.8rem;
}
.top-kicker {
  font-family:'JetBrains Mono', monospace; font-size:0.73rem; letter-spacing:0.22em; text-transform:uppercase;
  color:var(--signal); font-weight:600; display:flex; align-items:center; gap:0.55rem;
}
.top-dot { width:8px; height:8px; border-radius:50%; background:var(--signal); box-shadow:0 0 16px rgba(0,255,159,0.65); }
.top-title {
  font-family:'Space Grotesk', sans-serif; font-size:2rem; line-height:0.98; font-weight:700; letter-spacing:-0.04em;
  color:var(--text); margin-top:0.55rem;
}
.top-sub {
  margin-top:0.4rem; color:var(--muted); font-size:0.95rem; max-width:760px;
}
.top-meta {
  font-family:'JetBrains Mono', monospace; font-size:0.70rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted);
}

.dataset-bar {
  display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:0.8rem; margin:0.2rem 0 1rem;
}
.dataset-chip, .metric-card, .evidence-card {
  background:linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.01));
  border:1px solid var(--border); border-radius:14px;
}
.dataset-chip { padding:0.85rem 0.95rem; }
.dataset-label {
  font-family:'JetBrains Mono', monospace; font-size:0.62rem; letter-spacing:0.16em; text-transform:uppercase; color:var(--muted);
  margin-bottom:0.45rem;
}
.dataset-value {
  font-family:'Space Grotesk', sans-serif; font-size:1.25rem; font-weight:700; letter-spacing:-0.03em; color:var(--text);
}

/* controls */
.control-row { display:flex; justify-content:space-between; align-items:center; gap:1rem; margin:0 0 0.9rem; flex-wrap:wrap; }
.pill-row { display:flex; gap:0.45rem; flex-wrap:wrap; }
.pill, .hold-pill {
  padding:0.46rem 0.72rem; border:1px solid var(--border); border-radius:999px; background:rgba(255,255,255,0.025);
  font-family:'JetBrains Mono', monospace; font-size:0.66rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--muted);
  transition:all .15s ease;
}
.pill:hover, .hold-pill:hover { color:var(--text); border-color:rgba(255,255,255,0.18); background:rgba(255,255,255,0.045); }
.pill.active, .hold-pill.active { color:var(--signal); border-color:rgba(0,255,159,0.45); background:var(--signal-soft); box-shadow: inset 0 0 0 1px rgba(0,255,159,0.12); }

/* left rail */
.directory-panel {
  background:linear-gradient(180deg, rgba(255,255,255,0.022), rgba(255,255,255,0.012));
  border:1px solid var(--border); border-radius:18px; overflow:hidden;
}
.directory-head {
  padding:1rem 1rem 0.8rem; border-bottom:1px solid rgba(255,255,255,0.06);
}
.directory-title {
  font-family:'JetBrains Mono', monospace; font-size:0.68rem; letter-spacing:0.2em; text-transform:uppercase; color:var(--muted);
}
.directory-sub {
  margin-top:0.45rem; color:#b7bec8; font-size:0.92rem; line-height:1.35;
}
.stTextInput { padding:0.85rem 1rem 0.75rem !important; background:transparent !important; }
.stTextInput label { display:none !important; }
.stTextInput input {
  border-radius:12px !important; border:1px solid rgba(255,255,255,0.11) !important; background:#050505 !important;
  color:var(--text) !important; font-size:0.93rem !important; padding:0.7rem 0.8rem !important;
}
.stTextInput input:focus {
  border-color:rgba(0,255,159,0.45) !important; box-shadow:0 0 0 1px rgba(0,255,159,0.22) !important;
}
.directory-list { padding:0 0.75rem 0.75rem; max-height:760px; overflow-y:auto; }
.directory-list::-webkit-scrollbar { width:8px; }
.directory-list::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.08); border-radius:999px; }
.dir-card {
  display:block; padding:0.9rem 0.95rem; margin:0 0 0.65rem; border-radius:14px; border:1px solid rgba(255,255,255,0.07);
  background:linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.01));
  transition:transform .14s ease, border-color .14s ease, background .14s ease, box-shadow .14s ease;
}
.dir-card:hover { transform:translateY(-1px); border-color:rgba(255,255,255,0.14); background:rgba(255,255,255,0.03); }
.dir-card.active {
  border-color:rgba(0,255,159,0.45); background:linear-gradient(180deg, rgba(0,255,159,0.08), rgba(0,255,159,0.03));
  box-shadow:0 0 0 1px rgba(0,255,159,0.10), 0 18px 34px rgba(0,255,159,0.06);
}
.dir-top { display:flex; align-items:flex-start; justify-content:space-between; gap:0.85rem; }
.dir-name { font-family:'Space Grotesk', sans-serif; font-size:1.02rem; font-weight:700; letter-spacing:-0.03em; color:var(--text); }
.dir-meta { margin-top:0.22rem; font-family:'JetBrains Mono', monospace; font-size:0.61rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); }
.dir-badge {
  padding:0.2rem 0.46rem; border-radius:999px; border:1px solid rgba(255,255,255,0.09); background:rgba(255,255,255,0.035);
  font-family:'JetBrains Mono', monospace; font-size:0.58rem; letter-spacing:0.11em; text-transform:uppercase; color:var(--muted);
  white-space:nowrap;
}
.dir-stats { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:0.7rem; margin-top:0.9rem; }
.dir-stat-label { font-family:'JetBrains Mono', monospace; font-size:0.56rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--muted-2); margin-bottom:0.22rem; }
.dir-stat-value { font-family:'Space Grotesk', sans-serif; font-size:1.02rem; font-weight:700; letter-spacing:-0.03em; color:var(--text); }
.dir-stat-value.pos { color:#ff7373; }
.dir-stat-value.neg { color:var(--signal); }
.empty-note { padding:1rem; color:var(--muted); font-size:0.9rem; }

/* right hero */
.hero-panel {
  background:linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.012));
  border:1px solid var(--border); border-radius:18px; overflow:hidden; margin-bottom:1rem;
}
.hero-head { padding:1.05rem 1.1rem 0.8rem; border-bottom:1px solid rgba(255,255,255,0.06); display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.hero-name { font-family:'Space Grotesk', sans-serif; font-size:1.7rem; line-height:0.98; font-weight:700; letter-spacing:-0.05em; color:var(--text); }
.hero-meta { margin-top:0.42rem; font-family:'JetBrains Mono', monospace; font-size:0.64rem; letter-spacing:0.15em; text-transform:uppercase; color:var(--muted); }
.hero-note { margin-top:0.6rem; color:#c8d0da; font-size:0.98rem; line-height:1.35; max-width:740px; }
.metric-strip { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:0.8rem; padding:1rem 1.1rem 0.2rem; }
.metric-card { padding:0.95rem 1rem; }
.metric-label { font-family:'JetBrains Mono', monospace; font-size:0.60rem; letter-spacing:0.16em; text-transform:uppercase; color:var(--muted); margin-bottom:0.4rem; }
.metric-value { font-family:'Space Grotesk', sans-serif; font-size:2.15rem; line-height:0.92; font-weight:700; letter-spacing:-0.06em; color:var(--text); }
.metric-value.signal { color:var(--signal); text-shadow:0 0 26px rgba(0,255,159,0.16); }
.metric-value.danger { color:var(--danger); text-shadow:0 0 24px rgba(255,77,77,0.12); }
.metric-sub { margin-top:0.42rem; font-size:0.90rem; color:#bcc4cf; }
.verdict-band {
  margin:1rem 1.1rem 0; padding:0.95rem 1rem; border-radius:14px; border:1px solid rgba(255,77,77,0.20);
  background:linear-gradient(180deg, rgba(255,77,77,0.09), rgba(255,77,77,0.035));
  font-family:'Space Grotesk', sans-serif; font-size:1.18rem; font-weight:700; letter-spacing:-0.03em; color:var(--text);
}
.verdict-band .danger { color:var(--danger); }
.verdict-band .signal { color:var(--signal); }
.evidence-row { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:0.8rem; padding:1rem 1.1rem 0.35rem; }
.evidence-card { padding:0.85rem 0.9rem; }
.evidence-ticker { font-family:'Space Grotesk', sans-serif; font-size:1.02rem; font-weight:700; letter-spacing:-0.03em; color:var(--text); }
.evidence-line { margin-top:0.28rem; font-family:'JetBrains Mono', monospace; font-size:0.60rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--muted); }
.evidence-gap { margin-top:0.55rem; font-family:'Space Grotesk', sans-serif; font-size:1.15rem; font-weight:700; color:var(--danger); }
.chart-wrap-open { padding:0.6rem 1.1rem 0.15rem; }
.chart-title { font-family:'JetBrains Mono', monospace; font-size:0.60rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); margin-bottom:0.5rem; }
[data-testid="stPlotlyChart"] {
  background:transparent !important; border:none !important; padding:0 !important; margin-top:0 !important;
}
.chart-caption { padding:0.3rem 1.1rem 1rem; font-family:'JetBrains Mono', monospace; font-size:0.64rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); }

/* tables */
.section-title { font-family:'JetBrains Mono', monospace; font-size:0.68rem; letter-spacing:0.2em; text-transform:uppercase; color:var(--muted); margin:1rem 0 0.7rem; }
.tape-table {
  width:100%; border-collapse:separate; border-spacing:0; overflow:hidden; border-radius:16px;
  border:1px solid var(--border); background:linear-gradient(180deg, rgba(255,255,255,0.022), rgba(255,255,255,0.01));
}
.tape-table th {
  text-align:left; padding:0.92rem 0.85rem; border-bottom:1px solid rgba(255,255,255,0.06); background:rgba(255,255,255,0.03);
  font-family:'JetBrains Mono', monospace; font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); white-space:nowrap;
}
.tape-table td {
  padding:0.95rem 0.85rem; border-bottom:1px solid rgba(255,255,255,0.05); color:var(--text); font-size:0.92rem; white-space:nowrap;
}
.tape-table tr:last-child td { border-bottom:none; }
.tape-ticker { font-family:'Space Grotesk', sans-serif; font-size:1rem; font-weight:700; letter-spacing:-0.03em; }
.tape-mono { font-family:'JetBrains Mono', monospace; font-size:0.74rem; color:#d7dee8; }
.tape-pos { color:var(--signal); font-weight:700; }
.tape-neg { color:var(--danger); font-weight:700; }
.tape-wrap { overflow-x:auto; }
.table-note { margin-top:0.55rem; color:var(--muted); font-size:0.86rem; }

[data-testid="stAlert"] {
  background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.015)) !important;
  border:1px solid var(--border) !important; border-radius:14px !important;
}

@media (max-width: 980px) {
  .dataset-bar, .metric-strip, .evidence-row, .dir-stats { grid-template-columns:1fr; }
  .top-title { font-size:1.6rem; }
  .metric-value { font-size:1.75rem; }
}
</style>
""", unsafe_allow_html=True)


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
    """Pick the clearest cold-load example for a normal person.

    Priority:
      1) politician return clearly positive
      2) retail return flat or negative
      3) biggest positive gap
    Also seeds a small gap cache for prominent names so the picker doesn't look empty.
    """
    summary = build_politician_summary(trades)
    top_traders = summary.sort_values("trades", ascending=False)["politician"].head(18).tolist()
    candidate_names = []
    for name in FEATURED_POLITICIANS + top_traders:
        if name in trades["politician"].values and name not in candidate_names:
            candidate_names.append(name)

    cache = {}
    for name in candidate_names:
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
            "trades": len(bt),
        }

    if not cache:
        fallback = summary.sort_values("trades", ascending=False).iloc[0]["politician"] if len(summary) else ""
        return fallback, {}

    slam_dunks = {
        n: d for n, d in cache.items()
        if d["pol_return"] > 1.5 and d["retail_return"] <= 0.5 and d["gap"] >= 3.0
    }
    pool = slam_dunks if slam_dunks else {n: d for n, d in cache.items() if d["gap"] > 0}
    if not pool:
        pool = cache

    best = max(
        pool.items(),
        key=lambda item: (
            item[1]["gap"],
            item[1]["pol_return"],
            -max(item[1]["retail_return"], 0),
            item[1]["trades"],
        ),
    )[0]

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


def dedupe_trades(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    dedupe_cols = [c for c in ["politician", "ticker", "type", "transaction_date", "disclosure_date", "amount"] if c in out.columns]
    if dedupe_cols:
        out = out.drop_duplicates(subset=dedupe_cols, keep="first")
    out = out.sort_values([c for c in ["politician", "transaction_date", "disclosure_date", "ticker"] if c in out.columns]).reset_index(drop=True)
    return out


trades = dedupe_trades(trades)
summary = build_politician_summary(trades)

if len(summary) == 0:
    st.error("No politicians with purchase trades in the dataset.")
    st.stop()


@st.cache_data(ttl=1800, show_spinner=False)
def get_backtest_for_member(trades_df: pd.DataFrame, politician: str, hold_days: int):
    filtered = trades_df[
        (trades_df["politician"] == politician)
        & (~trades_df["type"].str.contains("sale", case=False, na=False))
    ].copy()
    bt = backtest_with_lag_analysis(filtered, hold_days=hold_days)
    if len(bt) == 0:
        return pd.DataFrame(), None
    bt = bt.drop_duplicates(subset=["ticker", "trade_date", "disclosure_date", "lag_days", "pol_return", "retail_return", "alpha_gap"]).copy()
    bt = bt.sort_values(["alpha_gap", "trade_date", "ticker"], ascending=[False, False, True]).reset_index(drop=True)
    stats = compute_lag_stats(bt)
    return bt, stats


@st.cache_data(ttl=1800, show_spinner=False)
def get_preview_gap_map(trades_df: pd.DataFrame, names: tuple, hold_days: int):
    out = {}
    for name in names:
        bt, stats = get_backtest_for_member(trades_df, name, hold_days)
        if stats:
            out[name] = {
                "gap": float(stats["alpha_gap"]),
                "pol_return": float(stats["politician_return"]),
                "retail_return": float(stats["retail_return"]),
                "trades": int(stats["trades"]),
            }
    return out


def format_party_state_chamber(row) -> str:
    bits = []
    if "party" in row.index and pd.notna(row.get("party")) and str(row.get("party")).strip() and str(row.get("party")).lower() != "nan":
        bits.append(str(row.get("party"))[:1].upper())
    if "state" in row.index and pd.notna(row.get("state")) and str(row.get("state")).strip() and str(row.get("state")).lower() != "nan":
        bits.append(str(row.get("state")).upper()[:2])
    if "chamber" in row.index and pd.notna(row.get("chamber")) and str(row.get("chamber")).strip() and str(row.get("chamber")).lower() != "nan":
        chamber = str(row.get("chamber")).strip()
        if chamber.lower() in {"h", "house"} or "house" in chamber.lower():
            bits.append("House")
        elif chamber.lower() in {"s", "senate"} or "senate" in chamber.lower():
            bits.append("Senate")
        else:
            bits.append(chamber)
    return " · ".join(bits)


def build_merged_curve(stats: dict) -> pd.DataFrame:
    pol = stats["pol_equity_curve"].copy()
    retail = stats["retail_equity_curve"].copy()
    if len(pol) == 0 or len(retail) == 0:
        return pd.DataFrame(columns=["date", "pol_perf", "retail_perf"])
    pol["pol_perf"] = pol["equity"] - 100
    retail["retail_perf"] = retail["equity"] - 100
    merged = pd.merge(
        pol[["date", "pol_perf"]],
        retail[["date", "retail_perf"]],
        on="date",
        how="outer",
    ).sort_values("date")
    merged["pol_perf"] = merged["pol_perf"].ffill().fillna(0)
    merged["retail_perf"] = merged["retail_perf"].ffill().fillna(0)
    return merged.reset_index(drop=True)


def fmt_pct(x: float) -> str:
    return f"{x:+.1f}%"


def fmt_gap(x: float) -> str:
    return f"{x:+.1f}pp"


def render_table_html(df: pd.DataFrame) -> str:
    cols = ["Ticker", "Trade Date", "Disclosed", "Lag (days)", "Their %", "Your %", "Gap (pp)"]
    rows = []
    for _, r in df.iterrows():
        gap = float(r["Gap (pp)"])
        their = float(r["Their %"])
        yours = float(r["Your %"])
        gap_cls = "tape-neg" if gap > 0 else ("tape-pos" if gap < 0 else "")
        their_cls = "tape-pos" if their > 0 else ("tape-neg" if their < 0 else "")
        your_cls = "tape-pos" if yours > 0 else ("tape-neg" if yours < 0 else "")
        rows.append(
            "<tr>"
            f"<td class='tape-ticker'>{r['Ticker']}</td>"
            f"<td class='tape-mono'>{pd.to_datetime(r['Trade Date']).strftime('%Y-%m-%d')}</td>"
            f"<td class='tape-mono'>{pd.to_datetime(r['Disclosed']).strftime('%Y-%m-%d')}</td>"
            f"<td class='tape-mono'>{int(r['Lag (days)'])}</td>"
            f"<td class='tape-mono {their_cls}'>{their:+.2f}%</td>"
            f"<td class='tape-mono {your_cls}'>{yours:+.2f}%</td>"
            f"<td class='tape-mono {gap_cls}'>{gap:+.2f}</td>"
            "</tr>"
        )
    head = "".join(f"<th>{c}</th>" for c in cols)
    return f"<div class='tape-wrap'><table class='tape-table'><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"


# ===================================================================
# QUERY PARAM STATE
# ===================================================================

qp = st.query_params
try:
    hold_days = int(qp.get("hold", "180"))
except Exception:
    hold_days = 180
if hold_days not in [30, 60, 90, 180, 365]:
    hold_days = 180

sort_key = qp.get("sort", "trades")
if sort_key not in ["trades", "recent", "lag", "gap"]:
    sort_key = "trades"

selected_politician = qp.get("p", "")
if selected_politician not in summary["politician"].values:
    with st.spinner("Warming up..."):
        selected_politician, _ = pick_default_politician(trades, hold_days=hold_days)
    if not selected_politician:
        selected_politician = summary.sort_values(["trades", "latest_trade"], ascending=[False, False]).iloc[0]["politician"]

# ===================================================================
# HEADER
# ===================================================================

latest_trade_date = trades["transaction_date"].max().strftime("%b %d, %Y")
latest_file_date = trades["disclosure_date"].max().strftime("%b %d, %Y") if "disclosure_date" in trades.columns else latest_trade_date
purchase_trades = trades[~trades["type"].str.contains("sale", case=False, na=False)].copy()
avg_lag_dataset = int(round((purchase_trades["disclosure_date"] - purchase_trades["transaction_date"]).dt.days.mean())) if len(purchase_trades) else 0

st.markdown(f"""
<div class="top-shell">
  <div>
    <div class="top-kicker"><span class="top-dot"></span> Signal 05 · Congressional Conflict Score</div>
    <div class="top-title">Copy-trading Congress looks obvious. The lag kills it.</div>
    <div class="top-sub">This tool is supposed to prove one thing fast: by the time a normal person can legally see the filing, the edge is often already gone.</div>
  </div>
  <div class="top-meta">Quiver source · trade data through {latest_trade_date} · disclosures through {latest_file_date}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="dataset-bar">
  <div class="dataset-chip"><div class="dataset-label">Politicians</div><div class="dataset-value">{int(summary['politician'].nunique())}</div></div>
  <div class="dataset-chip"><div class="dataset-label">Purchase trades</div><div class="dataset-value">{len(purchase_trades):,}</div></div>
  <div class="dataset-chip"><div class="dataset-label">Avg. disclosure lag</div><div class="dataset-value">{avg_lag_dataset} days</div></div>
  <div class="dataset-chip"><div class="dataset-label">Updated</div><div class="dataset-value">{latest_trade_date}</div></div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([0.37, 0.63], gap="small")

with col_left:
    st.markdown("""
    <div class="directory-panel">
      <div class="directory-head">
        <div class="directory-title">Politician directory</div>
        <div class="directory-sub">Pick a real name, not a toy example. The right side should make the lag obvious in one glance.</div>
      </div>
    """, unsafe_allow_html=True)

    search = st.text_input("Search", placeholder="Search politician name...", label_visibility="collapsed")
    q = (search or "").strip().lower()

    st.markdown(
        "<div class='control-row'><div class='pill-row'>"
        + "".join(
            f"<a href='?p={urlquote(selected_politician)}&hold={hold_days}&sort={key}' class='pill{' active' if key == sort_key else ''}' target='_self'>{label}</a>"
            for key, label in [("trades", "Most trades"), ("recent", "Most recent"), ("lag", "Longest lag"), ("gap", "Biggest gap")]
        )
        + "</div></div>",
        unsafe_allow_html=True,
    )

    base = summary.copy()
    if q:
        base = base[base["politician"].str.lower().str.contains(q, na=False)]
    else:
        base = base[base["trades"] >= 5]

    if sort_key == "recent":
        base = base.sort_values(["latest_trade", "trades"], ascending=[False, False])
    elif sort_key == "lag":
        base = base.sort_values(["avg_lag_days", "trades"], ascending=[False, False])
    else:
        base = base.sort_values(["trades", "latest_trade"], ascending=[False, False])

    candidate_df = base.head(24).copy()
    if selected_politician not in candidate_df["politician"].values:
        selected_row = summary[summary["politician"] == selected_politician]
        if len(selected_row):
            candidate_df = pd.concat([selected_row, candidate_df], ignore_index=True).drop_duplicates(subset=["politician"]).head(24)

    preview_map = get_preview_gap_map(trades, tuple(candidate_df["politician"].tolist()), hold_days)
    candidate_df["preview_gap"] = candidate_df["politician"].map(lambda n: preview_map.get(n, {}).get("gap"))

    if sort_key == "gap":
        candidate_df["preview_gap_sort"] = candidate_df["preview_gap"].fillna(-9999)
        candidate_df = candidate_df.sort_values(["preview_gap_sort", "trades"], ascending=[False, False]).drop(columns=["preview_gap_sort"])

    cards = []
    for _, row in candidate_df.iterrows():
        name = row["politician"]
        gap = row["preview_gap"]
        gap_text = "—"
        gap_cls = ""
        if pd.notna(gap):
            gap_text = fmt_gap(float(gap))
            gap_cls = " pos" if gap > 0 else (" neg" if gap < 0 else "")
        meta_primary = format_party_state_chamber(row)
        meta_bits = [b for b in [meta_primary, f"latest {relative_date(row['latest_trade'])}"] if b]
        meta_line = " · ".join(meta_bits)
        badge = "Selected" if name == selected_politician else f"{int(row['trades'])} trades"
        href = f"?p={urlquote(name)}&hold={hold_days}&sort={sort_key}"
        cards.append(
            f"<a href='{href}' class='dir-card{' active' if name == selected_politician else ''}' target='_self'>"
            f"<div class='dir-top'><div><div class='dir-name'>{name}</div><div class='dir-meta'>{meta_line}</div></div><div class='dir-badge'>{badge}</div></div>"
            f"<div class='dir-stats'>"
            f"<div><div class='dir-stat-label'>Trades</div><div class='dir-stat-value'>{int(row['trades'])}</div></div>"
            f"<div><div class='dir-stat-label'>Avg. Lag</div><div class='dir-stat-value'>{int(row['avg_lag_days'])}d</div></div>"
            f"<div><div class='dir-stat-label'>Gap</div><div class='dir-stat-value{gap_cls}'>{gap_text}</div></div>"
            f"</div></a>"
        )

    if cards:
        st.markdown(f"<div class='directory-list'>{''.join(cards)}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='empty-note'>No politicians matched that search.</div></div>", unsafe_allow_html=True)

with col_right:
    bt, stats = get_backtest_for_member(trades, selected_politician, hold_days)
    if not stats or len(bt) == 0:
        st.warning("No priceable trades were found for this politician in the current dataset.")
        st.stop()

    active_row = summary[summary["politician"] == selected_politician].iloc[0]
    meta_left = format_party_state_chamber(active_row)
    meta_bits = [b for b in [meta_left, f"{int(active_row['trades'])} trades", f"avg lag {int(round(stats['avg_lag_days']))}d", f"latest {relative_date(active_row['latest_trade'])}"] if b]
    hero_meta = " · ".join(meta_bits)

    hold_pills = "".join(
        f"<a href='?p={urlquote(selected_politician)}&hold={h}&sort={sort_key}' class='hold-pill{' active' if h == hold_days else ''}' target='_self'>{h}d</a>"
        for h in [30, 60, 90, 180, 365]
    )

    pol_r = float(stats["politician_return"])
    ret_r = float(stats["retail_return"])
    gap = float(stats["alpha_gap"])

    narrative = (
        f"On this composite backtest, the politician side finished {fmt_pct(pol_r)} while a retail follower starting at disclosure finished {fmt_pct(ret_r)}."
    )

    st.markdown(f"""
    <div class="hero-panel">
      <div class="hero-head">
        <div>
          <div class="hero-name">{selected_politician}</div>
          <div class="hero-meta">{hero_meta}</div>
          <div class="hero-note">{narrative}</div>
        </div>
        <div class="pill-row">{hold_pills}</div>
      </div>
      <div class="metric-strip">
        <div class="metric-card">
          <div class="metric-label">They captured</div>
          <div class="metric-value signal">{fmt_pct(pol_r)}</div>
          <div class="metric-sub">Composite return from trade date</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">You get</div>
          <div class="metric-value">{fmt_pct(ret_r)}</div>
          <div class="metric-sub">Composite return from disclosure date</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Stolen by lag</div>
          <div class="metric-value danger">{fmt_gap(gap)}</div>
          <div class="metric-sub">The performance gap between those two paths</div>
        </div>
      </div>
      <div class="verdict-band">Retail is <span class="danger">late to the move</span>. On this sample, the lag cost <span class="danger">{fmt_gap(gap)}</span> versus the original entry.</div>
    """, unsafe_allow_html=True)

    top_missed = bt.sort_values(["alpha_gap", "lag_days"], ascending=[False, False]).head(3).copy()
    cards = []
    for _, row in top_missed.iterrows():
        cards.append(
            f"<div class='evidence-card'>"
            f"<div class='evidence-ticker'>{row['ticker']}</div>"
            f"<div class='evidence-line'>{pd.to_datetime(row['trade_date']).strftime('%b %d, %Y')} trade · {int(row['lag_days'])}d lag</div>"
            f"<div class='evidence-gap'>{row['alpha_gap']:+.2f}pp gap</div>"
            f"<div class='evidence-line'>They {row['pol_return']:+.2f}% · You {row['retail_return']:+.2f}%</div>"
            f"</div>"
        )
    st.markdown(f"<div class='evidence-row'>{''.join(cards)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-wrap-open'><div class='chart-title'>Composite path across analyzed trades</div></div>", unsafe_allow_html=True)

    curve = build_merged_curve(stats)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=curve["date"], y=curve["retail_perf"], mode="lines", name="Retail at disclosure",
        line=dict(color="#ff4d4d", width=4),
    ))
    fig.add_trace(go.Scatter(
        x=curve["date"], y=curve["pol_perf"], mode="lines", name="Original entry",
        line=dict(color="#00ff9f", width=4),
        fill="tonexty", fillcolor="rgba(255,77,77,0.14)",
    ))

    if len(curve):
        y_values = list(curve["pol_perf"]) + list(curve["retail_perf"])
        ymin, ymax = min(y_values), max(y_values)
        pad = max(1.25, (ymax - ymin) * 0.20)

        fig.add_hline(y=0, line_width=1, line_color="rgba(255,255,255,0.12)")
        fig.add_annotation(
            x=curve["date"].iloc[-1], y=curve["pol_perf"].iloc[-1], text=f"<b>Original {fmt_pct(pol_r)}</b>",
            showarrow=False, xanchor="left", yanchor="bottom", xshift=8, yshift=8,
            font=dict(family="JetBrains Mono", size=12, color="#00ff9f"),
            bgcolor="rgba(0,0,0,0.88)", bordercolor="rgba(0,255,159,0.38)", borderwidth=1, borderpad=5,
        )
        fig.add_annotation(
            x=curve["date"].iloc[-1], y=curve["retail_perf"].iloc[-1], text=f"<b>Retail {fmt_pct(ret_r)}</b>",
            showarrow=False, xanchor="left", yanchor="top", xshift=8, yshift=-8,
            font=dict(family="JetBrains Mono", size=12, color="#ff4d4d"),
            bgcolor="rgba(0,0,0,0.88)", bordercolor="rgba(255,77,77,0.38)", borderwidth=1, borderpad=5,
        )
        mid_idx = len(curve) // 2
        fig.add_annotation(
            x=curve["date"].iloc[mid_idx],
            y=(curve["pol_perf"].iloc[mid_idx] + curve["retail_perf"].iloc[mid_idx]) / 2,
            text=f"<b>{fmt_gap(gap)}</b> lost to delay",
            showarrow=False,
            font=dict(family="JetBrains Mono", size=13, color="#ff4d4d"),
            bgcolor="rgba(0,0,0,0.88)", bordercolor="rgba(255,77,77,0.45)", borderwidth=1, borderpad=6,
        )

        fig.update_layout(
            height=520,
            margin=dict(l=30, r=120, t=10, b=50),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#040404",
            font=dict(family="JetBrains Mono", size=11, color="#8a8f98"),
            xaxis=dict(
                showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False, title="",
                tickfont=dict(size=10, color="#8a8f98"),
            ),
            yaxis=dict(
                showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, title="Return",
                title_font=dict(size=11, color="#8a8f98"), tickfont=dict(size=10, color="#8a8f98"),
                ticksuffix="%", range=[ymin - pad, ymax + pad],
            ),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#a6adb7")
            ),
            hovermode="x unified",
        )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(f"<div class='chart-caption'>{int(stats['trades'])} analyzed trades · {hold_days}-day hold · average disclosure lag {int(round(stats['avg_lag_days']))} days</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>All analyzed trades</div>", unsafe_allow_html=True)
    display_bt = bt[["ticker", "trade_date", "disclosure_date", "lag_days", "pol_return", "retail_return", "alpha_gap"]].copy()
    display_bt = display_bt.drop_duplicates(subset=["ticker", "trade_date", "disclosure_date", "lag_days", "pol_return", "retail_return", "alpha_gap"])
    display_bt = display_bt.sort_values(["alpha_gap", "trade_date"], ascending=[False, False])
    display_bt.columns = ["Ticker", "Trade Date", "Disclosed", "Lag (days)", "Their %", "Your %", "Gap (pp)"]
    st.markdown(render_table_html(display_bt), unsafe_allow_html=True)
    st.markdown("<div class='table-note'>This table is deduplicated before render. If the same trade ever appears twice on screen again, the bug is upstream in the raw source or mapping step.</div>", unsafe_allow_html=True)
