import json, urllib.request

# CONFIGURARE INVESTIȚIE [cite: 2026-02-14]
INVESTITIE_TOTALA_USD = 120456.247

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.20, "fib": 5.95},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.40, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 15.00, "fib": 18.50},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.20, "fib": 9.20},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.20, "fib": 6.90},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "sonic-3": {"q": 13449.38, "entry": 0.81633, "apr": 1.05, "mai": 1.35, "fib": 1.55},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.20}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def calculate_rotation_score(btc_d, eth_btc, fng, usdt_d):
    score = 10 
    if btc_d < 50: score += 25
    elif btc_d <= 55: score += 15
    else: score += 5
    if eth_btc > 0.05: score += 25
    elif eth_btc >= 0.04: score += 15
    else: score += 5
    if fng > 70: score += 20
    elif fng >= 40: score += 10
    else: score += 5
    if usdt_d < 5.5: score += 20
    elif usdt_d <= 7.5: score += 10
    else: score += 0
    return min(100, score)

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    btc_eur_data = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")
    
    price_map = {c["id"]: c for c in prices} if prices else {}
    btc_data = price_map.get("bitcoin", {})
    btc_usd = btc_data.get("current_price", 1)
    btc_ch = btc_data.get("price_change_percentage_24h", 0) or 0
    
    btc_eur = btc_eur_data.get("bitcoin", {}).get("eur", 1)
    usd_eur_live = btc_eur / btc_usd if btc_usd > 0 else 0.92

    btc_d = round(global_api["data"]["market_cap_percentage"]["btc"], 1) if global_api else 56.4
    eth_p = price_map.get("ethereum", {}).get("current_price", 0)
    eth_btc = round(eth_p / btc_usd, 4) if btc_usd > 0 else 0.0299
    fng_val = int(fng_api["data"][0]["value"]) if fng_api else 45
    
    # Parametrii Macro
    usdt_d = 7.44
    ml_sell_prob = 18.9
    rotation_score = calculate_rotation_score(btc_d, eth_btc, fng_val, usdt_d)

    results = []
    total_val_usd = 0
    total_val_apr_usd = 0
    total_val_fib_usd = 0

    for cid, d in PORTFOLIO.items():
        c_data = price_map.get(cid, {})
        p = c_data.get("current_price", 0)
        ch_24h = c_data.get("price_change_percentage_24h", 0) or 0
        if p == 0: p = d["entry"] # Fallback

        # CALCUL LIVE: Preț * Cantitate
        total_val_usd += (p * d["q"])
        total_val_apr_usd += (d["apr"] * d["q"])
        total_val_fib_usd += (d["fib"] * d["q"])
        
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        symbol = cid.upper().replace("-NETWORK-TOKEN","").replace("-GOVERNANCE-TOKEN","").replace("-3","")
        if "JITO" in symbol: symbol = "JTO"

        results.append({
            "symbol": symbol, "q": d["q"], "entry": d["entry"], "progres": round(max(0, min(100, prog)), 1),
            "price": f"{p:.4f}", "change": round(ch_24h, 2), "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "x_apr": round(d["apr"] / d["entry"], 1), "x_mai": round(d["mai"] / d["entry"], 1)
        })

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": btc_d, "btc_ch": btc_ch, "eth_btc": eth_btc, "rotation_score": rotation_score,
            "portfolio_eur": round(total_val_usd * usd_eur_live, 0),
            "profit_range": f"€{((total_val_apr_usd - INVESTITIE_TOTALA_USD) * usd_eur_live):,.0f} - €{((total_val_fib_usd - INVESTITIE_TOTALA_USD) * usd_eur_live):,.0f}",
            "investit_eur": round(INVESTITIE_TOTALA_USD * usd_eur_live, 0),
            "multiplier": round((total_val_usd * usd_eur_live) / (INVESTITIE_TOTALA_USD * usd_eur_live), 2),
            "coins": results, "vix": 14.2, "dxy": 101.1, "total3": "0.98T", 
            "fng": f"{fng_val} (Neutral)", "usdt_d": usdt_d, "urpd": "84.2%", "m2": "21.2T",
            "ml_prob": ml_sell_prob, "momentum": "STABLE", "exhaustion": "27.7%"
        }, f)

if __name__ == "__main__": main()
