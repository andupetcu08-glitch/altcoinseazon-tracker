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
    fng_data = fetch("https://api.alternative.me/fng/")

    if not prices or not global_data: return
    p_map = {c["id"]: c for c in prices}
    total_mcap = global_data["data"]["total_market_cap"]["usd"]

    # --- Calcule Macro ---
    btcd = round((p_map.get("bitcoin", {}).get("market_cap", 0) / total_mcap) * 100, 2)
    usdtd = round((p_map.get("tether", {}).get("market_cap", 0) / total_mcap) * 100, 2)
    ethbtc = round(p_map.get("ethereum", {}).get("current_price", 0) / p_map.get("bitcoin", {}).get("current_price", 1), 4)
    fng_val = int(fng_data["data"][0]["value"]) if fng_data else 10

    # --- Calcule Portofoliu & Tabel ---
    total_usd = 0
    coins_list = []
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", d["entry"])
        if cid == "synthetix-network-token" and (p > 0.8 or p == d["entry"]): p = 0.294 # SNX Fix
        
        total_usd += (p * d["q"])
        coins_list.append({
            "name": cid.split("-")[0].upper().replace("SYNTHETIX", "SNX"),
            "q": d["q"], "entry": d["entry"], "price": p,
            "change": round(c.get("price_change_percentage_24h", 0) or 0, 2),
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"]
        })

    port_eur = total_usd * 0.92
    # Scorul de rotatie urca spre 70% daca dominanta BTC scade sub 60%
    rot_score = round(max(0, min(100, (62 - btcd) * 5 + (fng_val / 3))), 0)

    output = {
        "port_eur": round(port_eur, 0),
        "invest_eur": INVEST_EUR,
        "mult": round(port_eur / INVEST_EUR, 2), # Rezolva 'undefined'
        "rotation": int(rot_score),
        "btcd": btcd, "ethbtc": ethbtc, "usdtd": usdtd,
        "fng": f"{fng_val} ({fng_data['data'][0]['value_classification'] if fng_data else 'N/A'})",
        "coins": coins_list
    }
    with open("data.json", "w") as f: json.dump(output, f)

if __name__ == "__main__": main()
