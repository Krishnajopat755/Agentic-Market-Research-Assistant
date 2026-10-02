# Agentic Market Research Assistant

An automated equity research assistant that generates real-time quantitative reports for Indian stocks (**NIFTY 50** & **S&P BSE SENSEX**) and global equities.

It pulls live price action and financial news, runs technical and sentiment analysis, calculates a bounded research signal (`BULLISH`, `BEARISH`, or `NEUTRAL`), and delivers a clean dashboard report with zero lookahead bias.

---

## What It Does

When you search for any stock (like `RELIANCE`, `TCS`, `HDFCBANK`, `INFY`, or indices like `NIFTY`):

1. **Fetches Live Market Data:** Retrieves real-time quotes, day high/lows, trading volume, and historical daily bars via Yahoo Finance (`yfinance`).
2. **Scrapes & Filters News:** Pulls recent news headlines and deduplicates articles so the same wire story isn't counted twice.
3. **Calculates Technical Indicators:** Computes 20/50-day Simple Moving Averages, EMA, 14-day RSI, MACD, Average True Range (ATR), and 20-day realized volatility.
4. **Scores Sentiment:** Uses a financial lexicon to grade recent headlines into positive, neutral, or negative sentiment.
5. **Combines Multi-Factor Signals:** Weights price momentum, trend, volatility, and sentiment into an overall signal score between `-1.0` and `+1.0` with a confidence percentage.
6. **Produces an Auditable Report:** Formats everything into a dark-mode dashboard with live Rupee (`₹`) pricing, dynamic summaries, and verifiable evidence claims.

---

## Quick Start (Run Locally)

### Prerequisites
- **Python 3.11+** installed on your system.
- `git` installed.

### 1. Clone the Repository
```bash
git clone https://github.com/Krishnajopat755/Agentic-Market-Research-Assistant.git
cd Agentic-Market-Research-Assistant
```

### 2. Set Up a Virtual Environment

**Using `venv` (standard):**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

**Or using `uv` (recommended for faster installs):**
```bash
uv venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
uv sync
```

### 3. Install Dependencies
```bash
pip install -e .
```

If you plan to run live market analysis, make sure `yfinance` is installed:
```bash
pip install yfinance
```

### 4. Start the Application
Run the FastAPI server with Uvicorn:
```bash
uvicorn apps.api.main:app --reload --port 8000
```

### 5. Open the Dashboard
Open your browser and navigate to:
- **Interactive Web Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check API:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Select any stock pill (`RELIANCE`, `TCS`, `INFY`, `NIFTY 50`, `SENSEX`) or type any NSE/BSE ticker into the search box and click **Analyze**.

---

## Running Tests

To verify that the indicator math, leakage checks, and Indian stock resolvers work properly:

```bash
pytest
```

To run with concise output:
```bash
pytest -q
```

All 29 tests should pass.

---

## API Usage Example

You can run research runs directly through the REST API using `curl` or Python.

### Example Request (`POST /research/run`)
```bash
curl -X POST "http://127.0.0.1:8000/research/run" \
     -H "Content-Type: application/json" \
     -d '{
       "symbols": ["RELIANCE"],
       "price_lookback_days": 120,
       "news_lookback_hours": 48,
       "signal_horizon_bars": 5,
       "mode": "live"
     }'
```

### Sample Response Excerpt
```json
{
  "run_id": "a4af3275-7ecd-486a-b9ba-89a96fb673b6",
  "status": "COMPLETED",
  "reports": {
    "RELIANCE": {
      "symbol": "RELIANCE.NS",
      "market_state": "BULLISH",
      "signal_score": 0.28,
      "confidence": 0.72,
      "headline": "Reliance Industries Demonstrates Bullish Momentum in Energy & Retail",
      "snapshot": {
        "price": 1167.70,
        "change": 16.65,
        "change_percent": 1.45
      }
    }
  }
}
```

---

## Project Structure

```text
├── apps/
│   └── api/
│       ├── main.py               # FastAPI entry point & API endpoints
│       └── dashboard.py          # Interactive HTML/JS dashboard UI
├── src/
│   ├── contracts/                # Pydantic data schemas (reports, market, signals)
│   ├── finance_core/             # Deterministic math engine
│   │   ├── indicators/           # Technical indicators (SMA, RSI, MACD, ATR)
│   │   ├── news/                 # News cleaning & deduplication
│   │   ├── sentiment/            # Financial lexicon sentiment analysis
│   │   ├── signal/               # Scorecard & ML signal classification
│   │   └── evaluation/           # Point-in-time leakage tests & backtesting
│   ├── providers/
│   │   ├── indian_stocks.py      # NIFTY 50 / SENSEX catalog & symbol normalizer
│   │   ├── live_provider.py      # Real-time Yahoo Finance & Google News RSS provider
│   │   └── fixture_provider.py   # Offline test fixture provider
│   ├── agents/                   # Report synthesis agent
│   ├── orchestrator/             # 5-stage pipeline state machine
│   └── storage/                  # In-memory and file-based report repositories
├── tests/                        # Unit, contract, and end-to-end test suite
├── pyproject.toml                # Project dependencies and configurations
└── README.md
```

---

## Configuration & Environment Variables

For offline development, no external API keys are required. If you want to use Alpha Vantage or external services, create a `.env` file:

```bash
cp .env.example .env
```

Available options:
```ini
# Application mode: "live" (default for real-time market data) or "fixture" (offline test mode)
APP_MODE=live

# Optional provider keys:
ALPHAVANTAGE_API_KEY=
POLYGON_API_KEY=
ANTHROPIC_API_KEY=
```

---

## Disclaimer

This project is built for market research, quantitative analysis, and educational purposes. It does not place live orders or provide certified financial investment advice.
