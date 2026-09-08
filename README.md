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
- Splits the available BNB balance across the coins queued for that run
- Keeps a running CSV log of tokens already bought, to avoid buying the
  same coin twice
- Small utility modules for reading Binance's public market data and
  converting between BNB and USD (`bot/binance_api.py`, `bot/price_utils.py`)

## Tech stack

- Python 3.8+
- Selenium + `webdriver-manager` (Chrome automation)
- MetaMask browser extension (`.crx`, not included, see Installation)
- pandas (CSV handling)
- `python-dotenv` (loading wallet credentials from `.env`)
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
   ```

   `.env` is git-ignored and is only read locally by `bot/metamask_wallet.py`.

## Usage

Run the scraper to start logging newly listed BNB chain coins:

```bash
python bot/scraper.py
```

Run the trader to unlock MetaMask, connect to PancakeSwap, and buy coins
found by the scraper:

```bash
python bot/trader.py
```

Both scripts run in an infinite loop and open a visible Chrome window
driven by Selenium.

## Project structure

```
bot/                  bot source code
  scraper.py           CoinMarketCap scraper (new BNB chain listings)
  metamask_wallet.py    MetaMask Selenium automation
  pancake_dex.py         PancakeSwap connection and settings
  trader.py               main buy loop
  binance_api.py           public Binance REST API helper
  price_utils.py            BNB <-> USD conversion helper
  storage.py                 shared CSV read/write helpers
data/
  new_listings/         scraper output, one CSV per day
  bought/                 log of tokens the bot has bought
docs/                  algorithm diagrams, case study and notes from the original design
  ALGORITHM.md           write-up of the design, see the Design section below
assets/icons/          notification icons
tests/                 ad-hoc scripts used while developing individual pieces
```

## Design

The original flowcharts and a short case study on why early detection
matters are in [docs/ALGORITHM.md](docs/ALGORITHM.md), along with a
step-by-step comparison of what was designed versus what actually got
implemented (short version: the bot buys, but the sell side of the
design was never built).

## Limitations

- Only the buy side of the original design was implemented: there is no
  risk-based position sizing, no automatic selling on a profit/loss
  target, and no resuming of previously bought coins on restart. See
  [docs/ALGORITHM.md](docs/ALGORITHM.md) for the full comparison.
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
