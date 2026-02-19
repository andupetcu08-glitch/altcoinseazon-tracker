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
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.2}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def normalize(v, min_v, max_v):
    return max(0, min(100, (v - min_v) / (max_v - min_v) * 100))

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    btc_eur_data = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")

    if not prices or not global_api: return

    p_map = {c["id"]: c for c in prices}
    btc_usd = p_map.get("bitcoin", {}).get("current_price", 1)
    btc_eur = btc_eur_data.get("bitcoin", {}).get("eur", 1) if btc_eur_data else 1
    usd_eur_live = btc_eur / btc_usd if btc_usd > 0 else 0.92

    btc_d = round(global_api["data"]["market_cap_percentage"].get("btc", 58.8), 2)
    usdt_d = round(global_api["data"]["market_cap_percentage"].get("usdt", 7.4), 2)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    eth_btc = round(eth_p / btc_usd, 4) if btc_usd > 0 else 0.029
    fng_val = int(fng_api["data"][0]["value"]) if fng_api else 50

    # Formula Rotation Score (Ponderată 2026)
    rot_score = round(
        normalize(60 - btc_d, 0, 15) * 0.30 +
        normalize(eth_btc, 0.03, 0.07) * 0.25 +
        normalize(10 - usdt_d, 2, 6) * 0.15 +
        60 * 0.10 + normalize(fng_val, 20, 90) * 0.10 + 55 * 0.10
    , 2)

    smri = round(((0.07 / eth_btc if eth_btc > 0 else 1) * 35) + ((10 - usdt_d) * 5), 2)
    breadth = sum(1 for c in prices if (c.get("price_change_percentage_24h") or 0) > 0) / len(prices) * 100
    
    results = []
    total_val_usd = 0
    total_val_mai_usd = 0
    total_val_fib_usd = 0

    for cid, d in PORTFOLIO.items():
        p = p_map.get(cid, {}).get("current_price", d["entry"])
        total_val_usd += (p * d["q"])
        total_val_mai_usd += (d["mai"] * d["q"])
        total_val_fib_usd += (d["fib"] * d["q"])
        
        symbol = cid.upper().replace("-NETWORK-TOKEN","").replace("-GOVERNANCE-TOKEN","").replace("-3","")
        if "SYNTHETIX" in symbol or "SNX" in cid: symbol = "SNX"
        if "JITO" in symbol: symbol = "JTO"

        results.append({
            "symbol": symbol, "q": d["q"], "entry": d["entry"], 
            "price": f"{p:.4f}", "change": round(p_map.get(cid, {}).get("price_change_percentage_24h", 0) or 0, 2),
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "x_apr": round(d["apr"] / d["entry"], 1), "x_mai": round(d["mai"] / d["entry"], 1)
        })

    port_eur = total_val_usd * usd_eur_live
    # Profit Teoretic = (Valoare Target - Valoare Actuală) în EUR
    mai_profit = (total_val_mai_usd * usd_eur_live) - port_eur
    fib_profit = (total_val_fib_usd * usd_eur_live) - port_eur

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": btc_d, "eth_btc": eth_btc, "rotation_score": rot_score, "smri": smri,
            "portfolio_eur": round(port_eur, 0),
            "profit_range": f"€{mai_profit:,.0f} - €{fib_profit:,.0f}",
            "investit_eur": INVESTITIE_TOTALA_EUR,
            "multiplier": round(port_eur / INVESTITIE_TOTALA_EUR, 2),
            "coins": results, "vix": 14.2, "dxy": 101.1, "total3": "0.98T", 
            "fng": f"{fng_val} (Sentiment)", "usdt_d": usdt_d, "urpd": 84.2, "m2": "21.2T",
            "ml_prob": 18.9, "momentum": "STABLE", "exhaustion": round((rot_score * 0.4) + (smri * 0.3), 2),
            "breadth": round(breadth, 2)
        }, f)

if __name__ == "__main__": main()
