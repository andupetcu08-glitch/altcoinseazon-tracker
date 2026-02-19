import json, urllib.request, time

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
    "synthetix-network-token": {"q": 20073.76, "entry": 0.32, "apr": 7.8, "mai": 9.3, "fib": 10.2}
}

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = urllib.request.urlopen(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}").read()
    p_data = json.loads(prices)
    global_data = json.loads(urllib.request.urlopen("https://api.coingecko.com/api/v3/global").read())
    
    p_map = {c["id"]: c for c in p_data}
    btc_p = p_map["bitcoin"]["current_price"]
    eth_p = p_map["ethereum"]["current_price"]
    
    # Calcule Macro
    btc_d = round(global_data["data"]["market_cap_percentage"]["btc"], 2)
    usdt_d = round(global_data["data"]["market_cap_percentage"]["usdt"], 2)
    eth_btc = round(eth_p / btc_p, 5)
    
    # Fix Breadth (nu mai e 0%)
    up_coins = sum(1 for c in p_data if c.get("price_change_percentage_24h", 0) > 0)
    breadth_val = round((up_coins / len(p_data)) * 100, 1)

    results = []
    total_val_usd = 0
    for cid, d in PORTFOLIO.items():
        price = 0.32 if "synthetix" in cid else p_map[cid]["current_price"]
        total_val_usd += (price * d["q"])
        results.append({"symbol": cid.upper()[:4], "price": price, "entry": d["entry"], "q": d["q"], 
                        "change": p_map[cid].get("price_change_percentage_24h", 0), "apr": d["apr"], "mai": d["mai"], "fib": d["fib"]})

    output = {
        "btc_d": btc_d, "eth_btc": eth_btc, "rotation_score": round((60-btc_d)*5, 2),
        "usdt_d": usdt_d, "smri": 36.33, "fng": 25, "total3": "0.98T", "vix": 14.2, "dxy": 101.1,
        "portfolio_eur": round(total_val_usd * 0.92, 0), "investitie": 101235,
        "profit_mai": "€420,289 - €486,060", "coins": results, "ml_prob": 18.9,
        "breadth": f"{breadth_val}%", "momentum": "STABLE", "exhaustion": 12.1,
        "volat": "LOW", "liq": "HIGH", "div": "NORMAL", "m2": "21.2T", "urpd": 84.2
    }
    with open("data.json", "w") as f: json.dump(output, f)

if __name__ == "__main__": main()
