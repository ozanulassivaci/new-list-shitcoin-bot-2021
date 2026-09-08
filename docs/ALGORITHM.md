# Algorithm design

This document walks through the bot's original design, based on the
flowcharts and research notes from the project's planning phase, and maps
each step to what actually ended up in the code.

Two design passes exist:

- **v0** (August 2021) — the first pass at the flow, in English.
  ![early design flowchart](algorithm-diagram.png)
  Source: [algorithm-diagram.drawio](algorithm-diagram.drawio)

- **v1.0a** (December 2021) — a more detailed revision, including
  risk-based position sizing and a save/resume step.
  ![v1.0a design flowchart](design-v1.0a.png)
  Source: [design-v1.0a.drawio](design-v1.0a.drawio), with an earlier
  working copy at [design-v1.0a-draft.drawio](design-v1.0a-draft.drawio).

## Designed flow (v1.0a)

1. **Startup** — the user enters their MetaMask credentials and sets a
   risk profile (target PNL / ROE, min/max amount to spend per coin).
2. **Resume check** — if data from a previous run exists, load it and keep
   monitoring any coins that were bought but not yet sold, plotting a
   weekly earnings graph. Otherwise, log into MetaMask and connect it to
   PancakeSwap.
3. **Find new listings** — go to CoinMarketCap and find the newest coin
   listed on the BNB (Binance Smart Chain) network.
4. **Size the position** — based on the user's risk profile and remaining
   balance, calculate how much to spend on this coin.
5. **Buy** — buy the coin through PancakeSwap.
6. **Record** — save the purchase (token, chain, address, amount) so it
   survives a restart.
7. **Monitor and sell** — keep watching the coin's price on CoinMarketCap;
   sell once it hits the configured profit or loss target, or if the
   remaining balance runs low. Log the result to a profit/loss graph.
8. Loop back to step 3 for the next newly listed coin.

## Why speed matters: the DOGEDI case study

![DOGEDI case study](case-study-dogedi.png)

While designing the bot, I tracked one coin (DOGEDI) across the sites
that pick it up over time: a raw BSC contract explorer first, then
CoinGecko, then CoinMarketCap roughly an hour later. The price at each
stage was already noticeably higher than at first detection — the whole
premise of the bot is that watching the earliest possible source (rather
than CoinMarketCap, which lists things later) is where the edge is. This
is also why `bot/scraper.py` polls CoinMarketCap's own "new" page directly
instead of waiting for a coin to reach a slower-moving listings site.

## Filtering to the BNB chain

![CoinMarketCap new-listings table, BNB chain rows highlighted](coinmarketcap-bnb-filter-example.png)

CoinMarketCap's "new" page lists coins across every chain. The screenshot
above is an early manual pass at the filter `bot/scraper.py` automates:
only rows on the BNB / Binance Coin network (highlighted) are kept, and
only if they were listed within the last few hours — see the `"hours" in
word and "BNB" in word` check in `GetCapNewListedToday.go2Cap`.

## What actually got implemented

The buy-side pipeline matches the design closely; the position-sizing,
sell, and resume logic were designed but never built:

| Design step | Status | Where |
| --- | --- | --- |
| Log into MetaMask, connect to PancakeSwap | Implemented | `bot/metamask_wallet.py`, `bot/pancake_dex.py` |
| Scrape CoinMarketCap for new BNB chain listings | Implemented | `bot/scraper.py` |
| Buy the coin via PancakeSwap | Implemented | `bot/trader.py` (`Swap.pancake_ex`) |
| Record the purchase | Implemented | `data/bought/`, `bot/storage.py` |
| Split remaining BNB evenly across queued coins | Implemented (simplified) | `bot/trader.py` (`bnb_to_usd_calculator`) — this is the one part of position sizing that made it in, but it is an even split, not the risk-profile-based sizing from the design |
| User-set risk profile (PNL / ROE / min-max per coin) | Not implemented | no equivalent in code |
| Resume monitoring of previously bought, unsold coins on startup | Not implemented | no equivalent in code |
| Auto-sell on profit/loss target | Not implemented | no equivalent in code |
| Profit/loss and weekly earnings graphs | Not implemented | no equivalent in code |

In short: the bot buys, but it never sells anything on its own — selling
was always meant to happen, but that part of the design was never coded.
