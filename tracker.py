import json, urllib.request

INVESTITIE_TOTALA_EUR = 101235

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.2, "fib": 6.86},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.4, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 15.0, "fib": 18.5},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.2, "fib": 9.2},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.2, "fib": 6.9},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "sonic-3": {"q": 13449.38, "entry": 0.81633, "apr": 1.05, "mai": 1.35, "fib": 1.55},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.32, "apr": 7.8, "mai": 9.3, "fib": 10.2}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")

    p_map = {c["id"]: c for c in prices} if prices else {}
    
    # 1. BTC.D Live Fix (TradingView are ~58.2% acum)
    btc_d = round(global_api["data"]["market_cap_percentage"].get("btc", 58.21), 2) if global_api else 58.21
    usdt_d = round(global_api["data"]["market_cap_percentage"].get("usdt", 7.62), 2) if global_api else 7.62
    
    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    eth_btc = round(eth_p / btc_p, 4) if btc_p > 0 else 0.0295
    fng_val = fng_api["data"][0]["value"] if fng_api else "12"

    results = []
    total_val_usd = 0
    for cid, d in PORTFOLIO.items():
        p = p_map.get(cid, {}).get("current_price", d["entry"])
        total_val_usd += (p * d["q"])
        sym = cid.upper().replace("-NETWORK-TOKEN","").replace("-GOVERNANCE-TOKEN","").replace("-3","")
        if "SYNTHETIX" in sym: sym = "SNX"
        results.append({
            "symbol": sym, "q": d["q"], "entry": d["entry"], "price": p,
            "change": round(p_map.get(cid, {}).get("price_change_percentage_24h", 0) or 0, 2),
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"]
        })

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": btc_d, "eth_btc": eth_btc, "rotation_score": 19.84, # Scorul tau actual
            "portfolio_eur": round(total_val_usd * 0.92, 0), "usdt_d": usdt_d,
            "fng": fng_val, "investit": INVESTITIE_TOTALA_EUR,
            "coins": results, "vix": 14.2, "dxy": 101.1, "total3": "0.98T",
            "ml_prob": 18.9, "momentum": "STABLE", "exhaustion": 36.33, "urpd": 84.2, "m2": "21.2T"
        }, f)

if __name__ == "__main__": main()
