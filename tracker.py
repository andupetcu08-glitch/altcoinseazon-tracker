import json, urllib.request

INVESTITIE_TOTALA = 120456.247
# Datele exacte din tabelul tău
PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.7},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.03},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.6},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 16.0},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.0},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.8},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.5},
    "sonic-coin": {"q": 13449.38, "entry": 0.61633, "apr": 1.05, "mai": 1.0},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.5}
}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())

def main():
    coin_ids = ",".join(PORTFOLIO.keys())
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_ids}")
    global_data = fetch("https://api.coingecko.com/api/v3/global")["data"]
    
    # Sentiment (Fear & Greed Index)
    fng = fetch("https://api.alternative.me/fng/")["data"][0]["value"]
    
    price_map = {c["id"]: c for c in prices}
    btc_d = global_data["market_cap_percentage"]["btc"]
    total3 = (global_data["total_market_cap"]["usd"] * (1 - (btc_d + global_data["market_cap_percentage"]["eth"]) / 100)) / 1e12

    results = []
    total_val = 0
    for cid, d in PORTFOLIO.items():
        if cid in price_map:
            p = price_map[cid]["current_price"]
            v = p * d["q"]
            total_val += v
            results.append({
                "symbol": "S" if cid == "sonic-coin" else price_map[cid]["symbol"].upper(),
                "q": d["q"],
                "entry": d["entry"],
                "price": f"{p:.7f}" if d["entry"] < 0.01 else f"{p:.3f}",
                "apr": d["apr"],
                "mai": d["mai"],
                "pot_apr": round(d["apr"] / d["entry"], 2), # Calcul corect Potential vs Entry
                "pot_mai": round(d["mai"] / d["entry"], 2)
            })

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": round(btc_d, 1), 
            "total3": round(total3, 2),
            "fng": fng,
            "portfolio": round(total_val, 0), 
            "multiplier": round(total_val / INVESTITIE_TOTALA, 2),
            "coins": results
        }, f)

if __name__ == "__main__": main()
