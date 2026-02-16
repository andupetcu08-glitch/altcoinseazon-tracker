import json, urllib.request

# Investitia initiala conform datelor tale
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
    p_api = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=" + ",".join(list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"])
    prices = fetch_data(p_api) or []
    global_data = fetch_data("https://api.coingecko.com/api/v3/global")
    fng_data = fetch_data("https://api.alternative.me/fng/")
    
    p_map = {c["id"]: c for c in prices}
    vix = get_yahoo("^VIX") or 14.2
    dxy = get_yahoo("DX-Y.NYB") or 101.1
    m2_val = "21.5T" 

    btcd = round(global_data["data"]["market_cap_percentage"]["btc"], 2) if global_data else 56.37
    total_cap = global_data["data"]["total_market_cap"]["usd"] if global_data else 1
    usdt_cap = p_map.get("tether", {}).get("market_cap", 0)
    usdtd = round((usdt_cap / total_cap) * 100, 2) if usdt_cap > 0 else 7.63
    
    fng_val = fng_data["data"][0]["value"] if fng_data else "12"
    fng_txt = fng_data["data"][0]["value_classification"] if fng_data else "Extreme Fear"

    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)

    total_usd, pot_min_usd, pot_max_usd = 0, 0, 0
    coins_out = []
    
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", d["entry"])
        if cid == "synthetix-network-token": p = 0.294 # Fix manual SNX

        ch = c.get("price_change_percentage_24h", 0) or 0
        total_usd += (p * d["q"])
        pot_min_usd += (d["q"] * d["apr"])
        pot_max_usd += (d["q"] * d["fib"])
        
        prog = min(100, max(0, ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100))
        name = "SNX" if "synthetix" in cid else cid.replace("-governance-token","").replace("-network-token","").split("-")[0].upper()

        coins_out.append({
            "symbol": name, "q": d["q"], "price": p, "entry": d["entry"],
            "change": round(ch, 2), "apr": d["apr"], "mai": d["mai"], "fib": d["fib"], "prog": round(prog, 1)
        })

    # Calcul Rotation Score
    rot_score = round(max(0, min(100, (65 - btcd) * 6 + (int(fng_val) / 3))), 0)

    with open("data.json", "w") as f:
        json.dump({
            "port_eur": round(total_usd * 0.92, 0),
            "invest_eur": INVEST_EUR,
            "mult": round((total_usd * 0.92) / INVEST_EUR, 2),
            "pot_min_eur": round(pot_min_usd * 0.92, 0),
            "pot_max_eur": round(pot_max_usd * 0.92, 0),
            "rotation": rot_score, 
            "btcd": btcd, 
            "ethbtc": round(eth_p / btc_p, 4) if btc_p > 0 else 0,
            "usdtd": f"{usdtd}%", 
            "fng": f"{fng_val} ({fng_txt})",
            "vix": round(vix, 2), 
            "dxy": round(dxy, 2), 
            "m2": m2_val, 
            "urpd": "84.2%",
            "coins": coins_out
        }, f)

if __name__ == "__main__":
    main()
