import json, urllib.request, time

# Constantele tale
INVESTITIE_TOTALA_USD = 120456.247
USD_EUR = 0.96 

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.6},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.03},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.6},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 14.0},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.5},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.4},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3},
    "sonic-3": {"q": 13449.38, "entry": 0.61633, "apr": 1.05, "mai": 1.2},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def main():
    coin_ids = ",".join(PORTFOLIO.keys())
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_ids}")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_data = fetch("https://api.alternative.me/fng/")
    
    price_map = {c["id"]: c for c in prices} if prices else {}
    global_data = global_api["data"] if global_api else {}
    
    btc_d = global_data.get("market_cap_percentage", {}).get("btc", 56.7)
    # USDT.D estimat din API Global
    usdtd = global_data.get("market_cap_percentage", {}).get("usdt", 5.1)

    results = []
    total_val = 0
    total_exit_mai = 0
    for cid, d in PORTFOLIO.items():
        p = price_map.get(cid, {}).get("current_price", 0)
        total_val += (p * d["q"])
        total_exit_mai += (d["mai"] * d["q"])
        
        symbol = cid.upper().split('-')[0]
        if "governance" in cid: symbol = "JTO"
        if "synthetix" in cid: symbol = "SNX"
        if "sonic" in cid: symbol = "SONIC"

        results.append({
            "symbol": symbol, "q": d["q"], "entry": d["entry"],
            "price": f"{p:.7f}" if d["entry"] < 0.01 else f"{p:.4f}",
            "apr": d["apr"], "mai": d["mai"],
            "pot_apr": round(d["apr"] / d["entry"], 2),
            "pot_mai": round(d["mai"] / d["entry"], 2)
        })

    # Corectat eroarea de variabila de aici
    profit_eur = (total_exit_mai - INVESTITIE_TOTALA_USD) * USD_EUR

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": round(btc_d, 1),
            "total3": round(0.82, 2), # Exemplu static sau calculat
            "fng": fng_data["data"][0]["value"] if fng_data else "9",
            "portfolio": round(total_val, 0),
            "profit_teoretic": f"{profit_eur:,.0f}",
            "multiplier": round(total_val / INVESTITIE_TOTALA_USD, 2),
            "coins": results,
            "usdtd": round(usdtd, 1),
            "vix": 14.1, "dxy": 103.8, "urpd": 84.2, "m2": "21.2T"
        }, f)

if __name__ == "__main__": main()
