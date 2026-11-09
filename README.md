# Altcoin Anomaly Radar — Lite

A free, dependency-free Python scanner for **Bitget USDT perpetual futures**.
It reads every contract in one pass and prints only the coins that are *actually doing something*,
with a one-line explanation of why they showed up.

```bash
python radar_lite.py
```

No API key. No account. No pip install. Read-only public market data.

## What it flags

| Signal | What it means |
|---|---|
| Funding rate extreme (≥0.05%/interval) | One side is crowded and paying the other. Stalling prices tend to get sold. |
| 24h move ≥15% | Momentum event. The scanner does not tell you to chase it. |
| Volume floor (≥$3M) | Keeps illiquid noise out of the list |

## Sample output

```
6 anomalies found (volume >= $3M, move >= 15%, majors excluded)

 1. UAI        0.04439      24h  -40.5%  vol $   18M
    - 24h move -40.5%
 2. RSR        0.001708     24h   +1.2%  vol $    4M
    - funding -0.217%/8h — shorts crowded, paying longs (-238% annualised)
```

## Options

```
--top N        how many rows to print (default 10)
--move PCT    24h move threshold (default 15)
--volume USD   minimum 24h volume (default 3,000,000)
--all          include majors (BTC, ETH, ...)
--proxy URL    HTTP proxy, if your network needs one
```

## Lite vs Full

This repo is the free core: funding extremes + 24h moves, majors excluded by name.

The paid version adds the parts that need more work:

- **Open interest deltas** — is a move backed by new money, or just position closing?
- **5-minute spikes** — price and OI changing together in a short window
- **Coin vs market** — is it falling *with* ETH (beta) or on its own (coin-specific news)?
- **Live market-cap filter** — excludes the top 100 by market cap automatically instead of a hardcoded list
- **Auto-rescan every 5 minutes + saved reports**

Full version: **https://172.245.28.157:8443/** (BNB Chain / Solana, files delivered on-chain confirmation)

## Requirements

Python 3.8+. Nothing else.

The tool calls `https://api.bitget.com`. If your network cannot reach it, pass `--proxy`.

## Disclaimer

This tool organises public market data. It is **not** investment advice and gives no
buy/sell signals. Trading derivatives can lose you your entire capital.


## Further reading

A short write-up of the ideas this scanner is built on — funding rates, the price/OI matrix, and
market beta vs coin-specific weakness:

**https://172.245.28.157:8443/blog/funding-rates.html**

The same page is also linked from the free Telegram bot [@feiyu_radar_bot](https://t.me/feiyu_radar_bot),
which posts three of these anomalies every day for free.

## License

MIT — see [LICENSE](LICENSE).
