# The Rocks Thrown Comparator

Powered by **The Fifth Signal**. Attacks the congressional copy-trading lie with real data.

## What it does

- Pulls real disclosed trades from public Congress filings (updated daily)
- Backtests what would have happened if a retail buyer bought at the **disclosure date** (the earliest a non-member could legally have acted) and held for a user-selected period
- Compares to the S&P 500 over the same window
- Shows trade-by-trade breakdown, biggest winners, biggest losers, equity curve
- Drives traffic back to thefifthsignal.com / thecapitoldossier.com

## Files in this folder

- `rocks_comparator.py` — the full Streamlit app
- `requirements.txt` — Python dependencies
- `README.md` — this file

## Deploy to Streamlit Cloud (free, ~3 minutes)

### Step 1 — Push these files to GitHub

Create a new public GitHub repo (call it anything — e.g. `rocks-comparator`). Upload all three files to the root of the repo.

You can do this through the GitHub web UI: click "Add file → Upload files" and drag all three in.

### Step 2 — Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "Sign in with GitHub" and authorize
3. Click "New app"
4. Select your `rocks-comparator` repo
5. Main file path: `rocks_comparator.py`
6. Click "Deploy"

You'll get a public URL like `rocks-comparator-yourname.streamlit.app` in about 2 minutes. The app will install dependencies from `requirements.txt` automatically.

### Step 3 — Custom domain (optional)

You can point a subdomain at the Streamlit app. In Streamlit Cloud settings → "Custom subdomain" lets you change `rocks-comparator-yourname.streamlit.app` to a cleaner URL.

For a true custom domain like `rocks.thefifthsignal.com`, you'd need to set up a reverse proxy (Cloudflare Workers works for this, free).

## Cost

- **Streamlit Cloud hosting: $0/month forever** (free tier, community apps)
- **yfinance (stock prices): $0**
- **Congressional trade data: $0** (public STOCK Act disclosures)

Total ongoing cost: **$0/month**.

## How to use it for marketing

1. **Embed screenshots in your landing page** — take a screenshot of Pelosi's result, drop it on thefifthsignal.com with a "Run the numbers yourself" link
2. **Post on Reddit** — r/options, r/wallstreetbets, r/stocks. "I built a tool that backtests every politician's trades. Results are bad."
3. **Newsletter swap pitches** — "Here's a tool that exposes the copy-trading lie. Link to your readers, 40% recurring on conversions."
4. **Affiliate asset** — give affiliates a direct link to the comparator with a UTM tag. They send traffic to the tool, the tool funnels to your trial page.

## Notes on data sources

The app tries multiple sources in order:
1. Quiver Quantitative public CSV (primary)
2. Community GitHub mirrors (fallback)
3. Manual CSV upload (if all live sources fail)

If your deployed app ever shows "All sources failed," download a fresh CSV from https://www.quiverquant.com/congresstrading/ and upload it via the file uploader. The app will handle it.

## Customizing

**Change the CTA link:** Edit the line near the bottom that says `href="https://thecapitoldossier.com"` — change to your Fifth Signal domain when ready.

**Change accent color:** The neon green `#00ff9f` appears ~6 times in the CSS block. Find/replace to change throughout.

**Add more politicians to the priority list:** Edit the `priority = [...]` list in the sidebar section. These appear at the top of the dropdown.

## What this tool does NOT do yet

- Does not include the Fifth Signal convergence benchmark (requires 5 signal pipelines — separate 2-3 week project)
- Does not handle short sales (sales disclosed by politicians are skipped — retail rarely shorts)
- Uses 30-day disclosure lag when the actual disclosure date is missing (the STOCK Act allows up to 45; 30 is conservative)

These are deliberate v1 scoping decisions. The attack thesis (politicians don't beat the market after disclosure lag) is fully proven with what's here.
