import json, urllib.request, time, os

# Datele extrase exact din tabelul tău Excel
PORTFOLIO_DATA = {
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

HISTORY_FILE = "history.json"

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())

def main():
    # 1. Date de piață
    prices = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250")
    global_data = fetch("https://api.coingecko.com/api/v3/global")["data"]
    price_map = {c["id"]: c for c in prices}

    # 2. Indicatori Macro
    btc_d = global_data["market_cap_percentage"]["btc"]
    eth_d = global_data["market_cap_percentage"]["eth"]
    total3 = (global_data["total_market_cap"]["usd"] * (1 - (btc_d + eth_d) / 100)) / 1e12

    # 3. Calcul Scenariu Exit
    # Probabilitatea crește dacă BTC.D scade sub 47% (conform tabelului tău) și TOTAL3 crește
    exit_score = (max(0, 58 - btc_d) / 16) * 50 + (min(total3, 2.5) / 2.5) * 50
    exit_prob = round(max(0, min(100, exit_score)), 1)

    # 4. Calcul Portofoliu
    total_value = 0
    total_invested = 0
    coin_results = []

    for cid, data in PORTFOLIO_DATA.items():
        if cid in price_map:
            p = price_map[cid]["current_price"]
            val = p * data["q"]
            total_value += val
            total_invested += data["entry"] * data["q"]
            
            coin_results.append({
                "symbol": price_map[cid]["symbol"].upper(),
                "price": p,
                "val": round(val, 0),
                "target_apr": data["apr"],
                "target_mai": data["mai"],
                "progress": round((p / data["apr"]) * 100, 1),
                "potential": round(data["mai"] / p, 1) if p > 0 else 0
            })

    # 5. Salvare JSON
    output = {
        "exit_probability": exit_prob,
        "btc_d": round(btc_d, 1),
        "total3": round(total3, 2),
        "total_value": round(total_value, 0),
        "profit_mult": round(total_value / total_invested, 2) if total_invested > 0 else 0,
        "coins": coin_results,
        "time": time.strftime("%H:%M")
    }
    
    with open("data.json", "w") as f: json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
