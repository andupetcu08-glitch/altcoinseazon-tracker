import json, urllib.request

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

def calculate_rotation_score(btc_d, eth_btc, fng, usdt_d, dxy):
    score = 10 
    if btc_d < 50: score += 20
    if eth_btc > 0.045: score += 20
    if fng > 75: score += 15
    if usdt_d < 5.8: score += 20
    if dxy < 101: score += 15
    return min(100, score)

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    btc_eur_data = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")
    
    p_map = {c["id"]: c for c in prices} if prices else {}
    btc_usd = p_map.get("bitcoin", {}).get("current_price", 1)
    usd_eur_live = (btc_eur_data.get("bitcoin", {}).get("eur", 1) / btc_usd) if btc_usd and btc_eur_data else 0.92

    btc_d = round(global_api["data"]["market_cap_percentage"]["btc"], 1) if global_api else 56.4
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    eth_btc = round(eth_p / btc_usd, 4) if btc_usd > 0 else 0.0299
    fng_val = int(fng_api["data"][0]["value"]) if fng_api else 45
    
    # Parametrii solicitați anterior
    usdt_d, vix, dxy = 7.5, 13.8, 101.2
    total3, m2, urpd = "0.98T", "21.2T", "84.2%"
    
    score = calculate_rotation_score(btc_d, eth_btc, fng_val, usdt_d, dxy)
    
    results = []
    t_usd = t_apr = t_fib = 0
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", 0)
        if p == 0 and "synthetix" in cid: p = 0.3026
        ch = c.get("price_change_percentage_24h", 0) or 0
        t_usd += (p * d["q"]); t_apr += (d["apr"] * d["q"]); t_fib += (d["fib"] * d["q"])
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        
        results.append({
            "symbol": cid.upper().split('-')[0].replace("JITO","JTO"), "q": d["q"], "entry": d["entry"], 
            "progres": round(max(0, min(100, prog)), 1), "price": f"{p:.4f}", 
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"], "change": round(ch, 2),
            "x_apr": round(d["apr"] / d["entry"], 2), "x_mai": round(d["mai"] / d["entry"], 2)
        })

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": btc_d, "eth_btc": eth_btc, "rotation_score": score, "vix": vix, "dxy": dxy,
            "portfolio_eur": round(t_usd * usd_eur_live, 0), "investit": round(INVESTITIE_TOTALA_USD * usd_eur_live, 0),
            "profit_range": f"€{((t_apr - INVESTITIE_TOTALA_USD) * usd_eur_live):,.0f} - €{((t_fib - INVESTITIE_TOTALA_USD) * usd_eur_live):,.0f}",
            "multiplier": round((t_usd * usd_eur_live) / (INVESTITIE_TOTALA_USD * usd_eur_live), 2),
            "coins": results, "total3": total3, "fng": f"{fng_val} (Neutral)", "usdt_d": usdt_d, "m2": m2, "urpd": urpd
        }, f)

if __name__ == "__main__": main()
