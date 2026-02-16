import json, urllib.request

INVEST_EUR = 101235.0 

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
    ids = ",".join(list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"])
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}")
    global_data = fetch("https://api.coingecko.com/api/v3/global")
    
    if not prices or not global_data: return
    p_map = {c["id"]: c for c in prices}
    total_mcap = global_data["data"]["total_market_cap"]["usd"]

    # --- Calcule Macro ---
    btc_mcap = p_map.get("bitcoin", {}).get("market_cap", 0)
    btcd = round((btc_mcap / total_mcap) * 100, 2) # BTC.D Live
    eth_p = p_map.get("ethereum", {}).get("current_price", 1)
    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    
    # --- Calcule Portofoliu ---
    total_usd = 0
    coins_out = []
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", d["entry"])
        if cid == "synthetix-network-token" and (p > 0.8 or p == d["entry"]): p = 0.294 # SNX Fix
        
        total_usd += (p * d["q"])
        coins_out.append({
            "symbol": cid.split("-")[0].upper().replace("SYNTHETIX", "SNX"),
            "q": d["q"], "price": p, "entry": d["entry"],
            "change": round(c.get("price_change_percentage_24h", 0) or 0, 2),
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"]
        })

    # Rotation Score spre 70% [cite: 2026-02-14]
    rot_score = round(max(0, min(100, (62 - btcd) * 5 + 20)), 0)

    with open("data.json", "w") as f:
        json.dump({
            "port_eur": round(total_usd * 0.92, 0),
            "invest_eur": INVEST_EUR,
            "mult": round((total_usd * 0.92) / INVEST_EUR, 2),
            "rotation": int(rot_score),
            "btcd": btcd,
            "ethbtc": round(eth_p / btc_p, 4),
            "coins": coins_out
        }, f)

if __name__ == "__main__": main()
