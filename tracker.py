import json, urllib.request, time

INVESTITIE_TOTALA_USD = 120456.247
# Curs fix pentru conversia in EUR (poti sa il faci si pe acesta dinamic ulterior)
USD_EUR = 0.94 

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
    
    results = []
    total_val_usd = 0
    total_exit_mai_usd = 0

    for cid, d in PORTFOLIO.items():
        # Daca API-ul nu returneaza pretul, punem 0.0001 ca sa nu crape calculele, dar sa vedem ca e eroare
        p = price_map.get(cid, {}).get("current_price", 0)
        total_val_usd += (p * d["q"])
        total_exit_mai_usd += (d["mai"] * d["q"]) # Suma estimata in Mai
        
        symbol = cid.split('-')[0].upper()
        if cid == "sonic-3": symbol = "SONIC"
        if "synthetix" in cid: symbol = "SNX"

        results.append({
            "symbol": symbol, "q": d["q"], "entry": d["entry"],
            "price": f"{p:.7f}" if d["entry"] < 0.01 else f"{p:.4f}",
            "apr": d["apr"], "mai": d["mai"],
            "pot_apr": round(d["apr"] / d["entry"], 2),
            "pot_mai": round(d["mai"] / d["entry"], 2)
        })

    # Calcul Profit Teoretic in EUR (Suma Exit Mai - Investitie Initiala)
    profit_teoretic_eur = (total_exit_mai_usd - INVESTITIE_TOTAL_USD) * USD_EUR

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": round(global_api["data"]["market_cap_percentage"]["btc"], 1) if global_api else 0,
            "total3": round(global_api["data"]["total_market_cap"]["usd"] / 1e12, 2) if global_api else 0,
            "fng": fng_data["data"][0]["value"] if fng_data else "50",
            "portfolio": round(total_val_usd, 0),
            "multiplier": round(total_val_usd / INVESTITIE_TOTAL_USD, 2),
            "profit_teoretic": f"{profit_teoretic_eur:,.0f}",
            "coins": results,
            "vix": 14.1, "urpd": 84.2, "dxy": 103.8, "m2": "21.2T"
        }, f)

if __name__ == "__main__": main()
