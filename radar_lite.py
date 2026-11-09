#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Altcoin Anomaly Radar — Lite
============================
Free, open-source scanner for Bitget USDT perpetuals.

It flags three things and nothing else:
  1. Funding rate extremes (which side is crowded and paying)
  2. 24-hour moves above a threshold
  3. Coins meeting either, with enough volume to matter

No API key. No account. Read-only public data.

Usage:
    python radar_lite.py
    python radar_lite.py --top 15 --move 10
    python radar_lite.py --proxy http://127.0.0.1:7890

MIT License. Contributions welcome.
"""

import argparse
import json
import os
import sys
import urllib.request

API = "https://api.bitget.com/api/v2/mix/market"

# Majors are excluded by default; the full version filters by live market cap instead.
MAJORS = {
    "BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "TRX", "AVAX", "LINK",
    "DOT", "MATIC", "TON", "SHIB", "LTC", "BCH", "UNI", "XLM", "ETC", "APT",
    "FIL", "ATOM", "ARB", "OP", "NEAR", "INJ", "SUI", "SEI", "PEPE", "WIF",
}
MIN_VOLUME = 3_000_000     # USD
FUNDING_EXTREME = 0.0005   # 0.05% per funding interval
MOVE_24H = 15.0            # percent


def fetch(url, proxy=None):
    req = urllib.request.Request(url, headers={"User-Agent": "radar-lite/1.0"})
    if proxy:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
        with opener.open(req, timeout=20) as r:
            return json.loads(r.read().decode())
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def num(row, key, default=0.0):
    try:
        return float(row.get(key) or default)
    except (TypeError, ValueError):
        return default


def funding_read(rate, interval):
    annual = rate * (24 / interval) * 365 * 100
    if rate > 0:
        return f"longs crowded, paying shorts ({annual:.0f}% annualised)"
    return f"shorts crowded, paying longs ({annual:.0f}% annualised)"


def main():
    ap = argparse.ArgumentParser(description="Scan Bitget USDT perpetuals for anomalies.")
    ap.add_argument("--top", type=int, default=10, help="max rows to print (default 10)")
    ap.add_argument("--move", type=float, default=MOVE_24H, help="24h move threshold in %% (default 15)")
    ap.add_argument("--volume", type=float, default=MIN_VOLUME, help="min 24h USD volume (default 3M)")
    ap.add_argument("--all", action="store_true", help="include majors")
    ap.add_argument("--proxy", default=os.environ.get("HTTPS_PROXY", ""), help="HTTP proxy URL")
    args = ap.parse_args()

    try:
        contracts = fetch(f"{API}/contracts?productType=USDT-FUTURES", args.proxy).get("data") or []
    except Exception as e:
        print(f"Cannot reach the exchange API: {e}")
        print("If your network blocks it, pass --proxy.")
        sys.exit(1)

    meta = {}
    for row in contracts:
        meta[row["symbol"]] = {
            "rwa": str(row.get("isRwa", "")).upper() == "YES",
            "interval": int(row.get("fundInterval") or 8),
        }

    rows = fetch(f"{API}/tickers?productType=USDT-FUTURES", args.proxy).get("data") or []
    found = []
    for row in rows:
        symbol = row.get("symbol", "")
        if not symbol.endswith("USDT"):
            continue
        m = meta.get(symbol, {})
        if m.get("rwa"):
            continue                      # tokenised stocks, not altcoins
        base = symbol[:-4]
        if not args.all and base in MAJORS:
            continue
        price = num(row, "lastPr")
        volume = num(row, "usdtVolume")
        if price <= 0 or volume < args.volume:
            continue

        chg = num(row, "change24h") * 100
        rate = num(row, "fundingRate")
        interval = m.get("interval", 8)

        reasons = []
        if abs(rate) >= FUNDING_EXTREME:
            reasons.append(f"funding {rate*100:+.3f}%/{interval}h — " + funding_read(rate, interval))
        if abs(chg) >= args.move:
            reasons.append(f"24h move {chg:+.1f}%")
        if not reasons:
            continue

        found.append({
            "symbol": base, "price": price, "chg": chg, "rate": rate,
            "interval": interval, "volume": volume,
            "score": abs(rate) * 10000 + abs(chg),
            "reasons": reasons,
        })

    found.sort(key=lambda x: -x["score"])
    print(f"{len(found)} anomalies found (volume >= ${args.volume/1e6:g}M, move >= {args.move:g}%)"
          f"{'' if args.all else ', majors excluded'}\n")
    for i, x in enumerate(found[:args.top], 1):
        print(f"{i:2d}. {x['symbol']:<10} {x['price']:<12g} 24h {x['chg']:+6.1f}%  "
              f"vol ${x['volume']/1e6:5.0f}M")
        for r in x["reasons"]:
            print(f"    - {r}")
    print("\nData observations only, not trading advice.")


if __name__ == "__main__":
    main()
