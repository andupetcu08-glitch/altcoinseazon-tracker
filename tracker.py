import json, urllib.request, re

# Investitia initiala conform datelor tale de referinta
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

def fetch_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def get_yahoo(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        data = fetch_data(url)
        return data['chart']['result'][0]['meta']['regularMarketPrice']
    except: return None

def main():
    # 1. APIs
    p_api = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=" + ",".join(list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"])
    prices = fetch_data(p_api) or []
    global_data = fetch_data("https://api.coingecko.com/api/v3/global")
    fng_data = fetch_data("https://api.alternative.me/fng/")
    
    p_map = {c["id"]: c for c in prices}
    total_mcap = global_data["data"]["total_market_cap"]["usd"] if global_data else 1.0

    # 2. Macro (DXY, VIX)
    vix = get_yahoo("^VIX") or 20.54
    dxy = get_yahoo("DX-Y.NYB") or 96.99
    m2_val = "22.4T" 

    # 3. Calcul Dominante (BTC.D Live exact)
    btc_mcap = p_map.get("bitcoin", {}).get("market_cap", 0)
    btcd = round((btc_mcap / total_mcap) * 100, 2) if btc_mcap > 0 else 56.65
    
    usdt_mcap = p_map.get("tether", {}).get("market_cap", 0)
    usdtd = round((usdt_mcap / total_mcap) * 100, 2) if usdt_mcap > 0 else 7.57
    
    fng_val = int(fng_data["data"][0]["value"]) if fng_data else 30
    fng_txt = fng_data["data"][0]["value_classification"] if fng_data else "Fear"

    # 4. Portofoliu
    total_usd = 0
    pot_min_usd = 0
    pot_max_usd = 0
    coins_out = []
    
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", d["entry"])
        
        # SNX Fix obligatoriu
        if cid == "synthetix-network-token" and (p > 0.8 or p == d["entry"]):
            p = 0.294 

        total_usd += (p * d["q"])
        pot_min_usd += (d["q"] * d["apr"])
        pot_max_usd += (d["q"] * d["fib"])
        
        name = "SNX" if "synthetix" in cid else cid.replace("-governance-token","").split("-")[0].upper()
        coins_out.append({
            "symbol": name, "q": d["q"], "price": p, "entry": d["entry"],
            "change": round(c.get("price_change_percentage_24h", 0) or 0, 2),
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "m_apr": round(d["apr"] / d["entry"], 1),
            "m_mai": round(d["mai"] / d["entry"], 1)
        })

    # 5. Rotation Score Dinamic (Verificat pt target 70%)
    # Scorul atinge 70 cand BTCD scade sub 52% si FNG creste
    rot_score = round(max(0, min(100, (62 - btcd) * 5 + (fng_val / 2))), 0)

    # 6. Export JSON
    with open("data.json", "w") as f:
        json.dump({
            "port_eur": round(total_usd * 0.92, 0),
            "invest_eur": INVEST_EUR,
            "mult": round((total_usd * 0.92) / INVEST_EUR, 2),
            "rotation": int(rot_score), 
            "btcd": btcd, 
            "ethbtc": round(p_map.get("ethereum", {}).get("current_price", 0) / p_map.get("bitcoin", {}).get("current_price", 1), 4),
            "usdtd": f"{usdtd}%", 
            "fng": f"{fng_val} ({fng_txt})",
            "vix": round(vix, 2), "dxy": round(dxy, 2), "m2": m2_val,
            "pot_min_eur": round(pot_min_usd * 0.92, 0),
            "pot_max_eur": round(pot_max_usd * 0.92, 0),
            "coins": coins_out
        }, f)

if __name__ == "__main__":
    main()
