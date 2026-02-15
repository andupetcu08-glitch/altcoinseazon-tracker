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

def main():
    # Fetching live data
    prices = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,tether," + ",".join(PORTFOLIO.keys()) + "&price_change_percentage=24h")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")
    
    p_map = {c["id"]: c for c in prices} if prices else {}
    btc = p_map.get("bitcoin", {})
    btc_p = btc.get("current_price", 1)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    
    # CALCUL LIVE INDICATORS
    btc_d = round(global_api["data"]["market_cap_percentage"]["btc"], 1) if global_api else 56.5
    eth_btc = round(eth_p / btc_p, 4) if btc_p > 0 else 0.03
    fng_val = int(fng_api["data"][0]["value"]) if fng_api else 50
    
    # Simulăm VIX bazat pe volatilitatea BTC 24h (dacă scade tare, VIX crește)
    btc_change = btc.get("price_change_percentage_24h", 0) or 0
    live_vix = round(15 + abs(btc_change), 1)
    live_dxy = 101.5 # Proxy
    usdt_d = 7.2 # Proxy
    
    # LOGICA ROTATION SCORE (Reparată să nu mai stea în 10%)
    score = 10
    if btc_d < 54: score += 20
    if eth_btc > 0.035: score += 20
    if fng_val > 60: score += 20
    if usdt_d < 7.5: score += 20
    if btc_change > 0: score += 10

    # Exhaustion & ML Logic
    alts_changes = [c.get("price_change_percentage_24h", 0) or 0 for k, c in p_map.items() if k not in ["bitcoin", "ethereum", "tether"]]
    avg_momentum = sum(alts_changes) / len(alts_changes) if alts_changes else 0
    exhaustion = min(100, max(0, (avg_momentum * 3) + (fng_val / 2)))
    ml_prob = round((score * 0.4) + (exhaustion * 0.4) + (fng_val * 0.2), 1)

    results = []
    t_usd = t_apr = t_fib = 0
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", 0) or d["entry"]
        ch = c.get("price_change_percentage_24h", 0) or 0
        t_usd += (p * d["q"]); t_apr += (d["apr"] * d["q"]); t_fib += (d["fib"] * d["q"])
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        
        results.append({
            "symbol": cid.upper()[:4], "price": f"{p:.4f}", "change": round(ch, 2),
            "progres": round(max(0, min(100, prog)), 1), "q": d["q"], "entry": d["entry"],
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "x_apr": round(d["apr"]/d["entry"],1), "x_mai": round(d["mai"]/d["entry"],1)
        })

    with open("data.json", "w") as f:
        json.dump({
            "score": score, "ml_prob": ml_prob, "exhaustion": round(exhaustion, 1),
            "btc_d": btc_d, "eth_btc": eth_btc, "vix": live_vix, "dxy": live_dxy,
            "fng": fng_val, "usdt_d": usdt_d, "portfolio_eur": round(t_usd * 0.93, 0),
            "profit_range": f"€{int((t_apr-INVESTITIE_TOTALA_USD)*0.93):,} - €{int((t_fib-INVESTITIE_TOTALA_USD)*0.93):,}",
            "multiplier": round(t_usd/INVESTITIE_TOTALA_USD, 2), "coins": results
        }, f)

if __name__ == "__main__": main()
