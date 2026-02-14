import json, urllib.request

# DATE EXACTE DIN EXCEL
INVESTITIE_TOTALA = 120456.247
PORTFOLIO = {
    "optimism": {"q": 6400, "apr": 4.8, "mai": 5.7},
    "notcoin": {"q": 1297106.88, "apr": 0.028, "mai": 0.03},
    "arbitrum": {"q": 14326.44, "apr": 3.0, "mai": 3.6},
    "celestia": {"q": 4504.47, "apr": 12.0, "mai": 16.0},
    "jito-governance-token": {"q": 7366.42, "apr": 8.0, "mai": 8.0},
    "lido-dao": {"q": 9296.65, "apr": 5.6, "mai": 6.8},
    "cartesi": {"q": 49080, "apr": 0.2, "mai": 0.2},
    "immutable-x": {"q": 1551.82, "apr": 3.5, "mai": 4.5},
    "sonic-coin": {"q": 13449.38, "apr": 1.05, "mai": 1.0},
    "synthetix-network-token": {"q": 20073.76, "apr": 7.8, "mai": 9.5}
}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())

def main():
    prices = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=optimism,notcoin,arbitrum,celestia,jito-governance-token,lido-dao,cartesi,immutable-x,sonic-coin,synthetix-network-token")
    global_data = fetch("https://api.coingecko.com/api/v3/global")["data"]
    price_map = {c["id"]: c for c in prices}

    btc_d = global_data["market_cap_percentage"]["btc"]
    total3 = (global_data["total_market_cap"]["usd"] * (1 - (btc_d + global_data["market_cap_percentage"]["eth"]) / 100)) / 1e12

    results = []
    total_val = 0
    total_exit_apr = 542137.78 # Valoare fixă din Excel
    total_exit_mai = 823117.11 # Valoare fixă din Excel

    for cid, d in PORTFOLIO.items():
        if cid in price_map:
            p = price_map[cid]["current_price"]
            v = p * d["q"]
            total_val += v
            results.append({
                "symbol": price_map[cid]["symbol"].upper(),
                "price": p, "value": round(v, 0), "apr": d["apr"], "mai": d["mai"],
                "pot": round(d["mai"] / p, 1)
            })

    # Rotation Score bazat pe BTC.D Target
    score = round(max(0, min(100, (56.7 - btc_d) * 10 + 15)), 1)

    with open("data.json", "w") as f:
        json.dump({
            "exit_score": score, "btc_d": round(btc_d, 1), "t3": round(total3, 2),
            "portfolio": round(total_val, 0), "multiplier": round(total_val / INVESTITIE_TOTALA, 2),
            "exit_apr": total_exit_apr, "exit_mai": total_exit_mai, "coins": results
        }, f)

if __name__ == "__main__": main()
