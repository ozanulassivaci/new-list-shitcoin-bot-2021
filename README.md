# New List Shitcoin Trading Bot

A Selenium-based bot that watches CoinMarketCap for newly listed coins on the
BNB Smart Chain and attempts to automatically buy them on PancakeSwap through
a MetaMask browser extension.

> This is an old educational/personal project from high school, shared for
> portfolio purposes. It is NOT financial advice, NOT USE FOR TRADE
> significant real funds, and comes with no guarantee of profitability or
> safety. Use entirely at your own risk.

This project was a simple self-study exercise I built in high school (2021)
to develop my programming skills.

## Features

- Scrapes CoinMarketCap's "new" listings page and logs coins that were
  listed within the last few hours and run on the BNB chain
- Logs unlocks MetaMask and connects the wallet to PancakeSwap through
  Selenium
- Buys newly listed tokens by contract address and records the purchase
- Sizes each buy from the available BNB balance, clamped to a
  user-configurable min/max spend per coin (a risk profile read from
  `.env`, editable while the bot is running)
- Tracks open positions in CSV form so a restart resumes monitoring
  whatever was bought but not yet sold
- Sells a position once it either fails to gain +30% within its first 24
  hours, or has clearly turned over after a bigger run-up (see
  [docs/ALGORITHM.md](docs/ALGORITHM.md#the-exit-rule) for the exact rule)
- Generates a weekly profit/loss chart from closed positions
- Keeps a running CSV log of tokens already bought, to avoid buying the
  same coin twice
- Small utility modules for reading Binance's public market data and
  converting between BNB and USD (`bot/binance_api.py`, `bot/price_utils.py`)

## Tech stack

- Python 3.8+
- Selenium + `webdriver-manager` (Chrome automation)
- MetaMask browser extension (`.crx`, not included, see Installation)
- pandas (CSV handling)
- matplotlib (weekly profit/loss chart)
- `python-dotenv` (loading wallet credentials and risk profile from `.env`)
- `requests` (Binance public REST API)

## Installation

1. Clone the repository and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Download the MetaMask extension `.crx` file yourself and place it at
   `bot/metamask_10_8_1_0.crx` (the file is not included in this repository,
   see [Limitations](#limitations)).

3. Copy `.env.example` to `.env` and fill in your own MetaMask wallet
   password and seed phrase:

   ```bash
   cp .env.example .env
   ```

   ```
   METAMASK_PASSWORD=your_metamask_password_here
   METAMASK_SEED_PHRASE=your_metamask_seed_phrase_here
   MIN_SPEND_PER_COIN_USD=5
   MAX_SPEND_PER_COIN_USD=50
   ```

   `.env` is git-ignored and only read locally, by `bot/metamask_wallet.py`
   (credentials) and `bot/risk_config.py` (risk profile). The risk profile
   is re-read every loop iteration, so it can be edited while the bot runs.

## Usage

Run the scraper to start logging newly listed BNB chain coins:

```bash
python bot/scraper.py
```

Run the trader to unlock MetaMask, connect to PancakeSwap, buy coins found
by the scraper, and monitor/sell whatever it's currently holding:

```bash
python bot/trader.py
```

Both scripts run in an infinite loop and open a visible Chrome window
driven by Selenium. `bot/trader.py` resumes any open positions from a
previous run automatically (see [docs/ALGORITHM.md](docs/ALGORITHM.md)).

## Project structure

```
bot/                  bot source code
  scraper.py           CoinMarketCap scraper (new BNB chain listings)
  metamask_wallet.py    MetaMask Selenium automation
  pancake_dex.py         PancakeSwap connection and settings
  trader.py               main buy loop, position sizing
  seller.py                monitors and sells open positions
  positions.py              open/closed position CSV ledger
  risk_config.py            reads the min/max spend risk profile from .env
  pnl_graph.py               weekly profit/loss chart
  binance_api.py             public Binance REST API helper
  price_check.py              reads a token's price off bogged.finance
  price_utils.py               BNB <-> USD conversion helper
  storage.py                    shared CSV read/write helpers
data/
  new_listings/         scraper output, one CSV per day
  bought/                 log of tokens the bot has bought, plus positions.csv
  sold/                    closed positions, sold.csv
  reports/                  weekly_pnl.png
docs/                  algorithm diagrams, case study and notes from the original design
  ALGORITHM.md           write-up of the design, see the Design section below
assets/icons/          notification icons
tests/                 ad-hoc scripts used while developing individual pieces
```

## Design

The original flowcharts and a short case study on why early detection
matters are in [docs/ALGORITHM.md](docs/ALGORITHM.md), along with a
step-by-step comparison of what was designed versus what actually got
implemented, including the exit rule the sell logic follows.

## Limitations

- The PancakeSwap steps `bot/seller.py` uses to actually execute a sell
  have never been run against the live site, unlike the rest of the
  Selenium flow, which at least worked at some point in 2022 (see the
  historical CSVs in `data/`). The exit *decision* logic (24h/30% cutoff,
  peak-and-reversal tracking) is plain Python and is covered by the
  reasoning in [docs/ALGORITHM.md](docs/ALGORITHM.md#the-exit-rule); the
  selectors that click through the actual swap are the part most likely
  to need fixing.
- The MetaMask `.crx` extension file is not included (18 MB third-party
  binary); you need to download your own copy and place it in `bot/`.
- Selenium automation is brittle: it relies on hardcoded XPath selectors
  that will break whenever CoinMarketCap, PancakeSwap, or MetaMask change
  their UI.
- No automated test suite; `tests/` holds small standalone scripts used
  while building individual features, not a CI-run suite.
- `bot/trader.py` reads a hardcoded date (`2022-02-02`) for which listings
  CSV to use, left over from the original project instead of always using
  the current day's file.
- `tests/toast_notification_test.py` imports a `wintoast` package; verify
  the exact package name (e.g. `win10toast`) before installing it.

## License

MIT, see [LICENSE](LICENSE).
