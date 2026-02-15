import json, urllib.request

INVESTITIE_TOTALA_USD = 120456.247
eur_conv = 0.93

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.2, "fib": 5.95},
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

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    p_map = {c["id"]: c for c in prices} if prices else {}
    
    btc = p_map.get("bitcoin", {})
    btc_p = btc.get("current_price", 1)
    btc_ch = btc.get("price_change_percentage_24h", 0) or 0
    
    # Macro Indicators
    btc_d = 56.4 # Exemplu live
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    eth_btc = round(eth_p / btc_p, 4) if btc_p > 0 else 0.03
    usdt_d = round(7.5 - (btc_ch * 0.12), 2)
    fng_val = 45 # Neutral
    
    # Calcul Rotation Score
    score = 10
    if btc_d < 50: score += 20
    if eth_btc > 0.035: score += 15
    if usdt_d < 5.8: score += 20
    if btc_ch > 1.5: score += 15
    rotation_score = min(100, score)

    # ML & Exhaustion
    alts_changes = [c.get("price_change_percentage_24h", 0) or 0 for k, c in p_map.items() if k not in ["bitcoin", "ethereum", "tether"]]
    avg_momentum = sum(alts_changes)/len(alts_changes) if alts_changes else 0
    exhaustion = min(100, max(0, (avg_momentum * 3) + (fng_val / 2)))
    ml_prob = round((rotation_score * 0.3) + (exhaustion * 0.5) + (abs(btc_ch) * 2), 1)

    # Timeframe Estimate (Logic for the new box)
    days_to_target = "FAST" if avg_momentum > 5 else "STABLE" if avg_momentum > 0 else "SLOW"

    results = []
    t_usd = net_apr = net_fib = 0
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", 0) or d["entry"]
        ch = c.get("price_change_percentage_24h", 0) or 0
        t_usd += (p * d["q"])
        net_apr += (d["apr"] * d["q"]) - (d["entry"] * d["q"])
        net_fib += (d["fib"] * d["q"]) - (d["entry"] * d["q"])
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        
        results.append({
            "symbol": cid.upper().split('-')[0].replace("JITO","JTO"),
            "price": f"{p:.4f}", "change": round(ch, 2), "progres": round(max(0, min(100, prog)), 1),
            "q": d["q"], "entry": d["entry"], "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "x_apr": round(d["apr"]/d["entry"], 1), "x_mai": round(d["mai"]/d["entry"], 1)
        })

    with open("data.json", "w") as f:
        json.dump({
            "rotation_score": rotation_score, "ml_prob": ml_prob, "exhaustion": f"{round(exhaustion,1)}%",
            "btc_d": btc_d, "usdt_d": usdt_d, "eth_btc": eth_btc, "vix": 14.2, "dxy": 101.1,
            "fng": f"{fng_val} (Neutral)", "total3": "0.98T", "m2": "21.2T", "urpd": 84.2,
            "momentum": days_to_target, "portfolio_eur": round(t_usd * eur_conv, 0),
            "investit": round(INVESTITIE_TOTALA_USD * eur_conv, 0), "multiplier": round(t_usd / INVESTITIE_TOTALA_USD, 2),
            "profit_range": f"€{int(net_apr*eur_conv):,} - €{int(net_fib*eur_conv):,}",
            "coins": results
        }, f)

if __name__ == "__main__": main()
