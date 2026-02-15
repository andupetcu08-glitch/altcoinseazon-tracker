import json, urllib.request, math, time

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
    except Exception as e: return None

def get_ml_sell_probability(score, exhaustion, fng):
    # Model probabilistic: evaluează riscul de inversare a trendului
    prob = (score * 0.4) + (exhaustion * 0.4) + (fng * 0.2)
    return round(min(100, prob), 1)

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    data = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    global_m = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")

    if not data: return
    p_map = {c["id"]: c for c in data}
    btc = p_map.get("bitcoin", {})
    eth = p_map.get("ethereum", {})
    usdt = p_map.get("tether", {})
    
    # 1. Real Breadth (Câte monede din portofoliu sunt pe verde?)
    alts_up = sum(1 for cid in PORTFOLIO if p_map.get(cid, {}).get("price_change_percentage_24h", 0) > 0)
    breadth = (alts_up / len(PORTFOLIO)) * 100

    # 2. Rotation Score Logic
    btc_d = global_m["data"]["market_cap_percentage"]["btc"] if global_m else 56.4
    eth_btc = eth.get("current_price", 0) / btc.get("current_price", 1)
    fng_val = int(fng_api["data"][0]["value"]) if fng_api else 10
    usdt_d = 7.5 # Valoare simulată (necesită API macro pt real-time)

    # 3. Exhaustion & Blow-off Detection
    # Calculat ca deviație față de media de profit a portofoliului
    avg_change = sum(c.get("price_change_percentage_24h", 0) for c in p_map.values()) / len(p_map)
    exhaustion = min(100, max(0, avg_change * 5)) # Dacă piața crește cu 20% într-o zi, exhaustion e 100
    
    score = 10
    if btc_d < 50: score += 25
    if eth_btc > 0.04: score += 25
    if fng_val > 70: score += 20
    if usdt_d < 6: score += 20
    
    ml_prob = get_ml_sell_probability(score, exhaustion, fng_val)

    results = []
    t_usd, t_apr, t_fib = 0, 0, 0
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", 0)
        ch = c.get("price_change_percentage_24h", 0)
        t_usd += (p * d["q"]); t_apr += (d["apr"] * d["q"]); t_fib += (d["fib"] * d["q"])
        
        # Progres Real APR -> FIB
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        
        results.append({
            "symbol": c.get("symbol", cid).upper(),
            "price": p, "change": round(ch or 0, 2),
            "prog": round(max(0, min(100, prog)), 1),
            "entry": d["entry"], "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "heatmap": "up" if ch > 2 else "down" if ch < -2 else "neutral"
        })

    with open("data.json", "w") as f:
        json.dump({
            "score": score, "ml_prob": ml_prob, "exhaustion": exhaustion,
            "btc_d": round(btc_d, 1), "eth_btc": round(eth_btc, 4), "fng": fng_val,
            "breadth": round(breadth, 1), "usdt_d": usdt_d,
            "portfolio_eur": round(t_usd * 0.92, 0),
            "multiplier": round((t_usd*0.92)/(INVESTITIE_TOTALA_USD*0.92), 2),
            "coins": results, "divergence": "BULLISH" if eth_btc > 0.035 and btc_d < 55 else "NONE"
        }, f)

if __name__ == "__main__": main()
