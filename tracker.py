import json, urllib.request

INVESTITIE_TOTALA_USD = 120456.247
USD_EUR = 0.96 

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.6, "fib": 5.95},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.03, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.6, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 14.0, "fib": 17.50},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.5, "fib": 9.20},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.4, "fib": 6.90},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "sonic-3": {"q": 13449.38, "entry": 0.61633, "apr": 1.05, "mai": 1.2, "fib": 1.45},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.20}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    
    price_map = {c["id"]: c for c in prices} if prices else {}
    global_data = global_api["data"] if global_api else {}
    
    # Date Macro
    btc_p = price_map.get("bitcoin", {}).get("current_price", 1)
    eth_p = price_map.get("ethereum", {}).get("current_price", 0)
    eth_btc = eth_p / btc_p if eth_p > 0 else 0
    btc_d = global_data.get("market_cap_percentage", {}).get("btc", 56.5)
    vix = 13.8 # Parametru macro

    # --- LOGICA SCOR DINAMIC (MULTI-FACTOR) ---
    score = 50 
    if btc_d > 55: score -= 15
    if eth_btc > 0.04: score += 15
    if vix > 20: score -= 20
    score = max(0, min(100, score))

    results = []
    total_val_usd = 0
    total_val_mai_usd = 0

    for cid, d in PORTFOLIO.items():
        if cid in ["bitcoin", "ethereum"]: continue
        p = price_map.get(cid, {}).get("current_price", 0)
        if p == 0 and "synthetix" in cid: p = 0.3026 
        
        total_val_usd += (p * d["q"])
        total_val_mai_usd += (d["mai"] * d["q"])
        
        # Calcul Progres catre Target Final (Fibonacci)
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        prog = max(0, min(100, prog))

        symbol = cid.upper().split('-')[0]
        if "governance" in cid: symbol = "JTO"
        if "network" in cid: symbol = "SNX"
        if "sonic" in cid: symbol = "SONIC"

        results.append({
            "symbol": symbol, "q": d["q"], "entry": d["entry"], "progres": round(prog, 1),
            "price": f"{p:.7f}" if d["entry"] < 0.01 else f"{p:.4f}", 
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "x_apr": round(d["apr"] / d["entry"], 2), "x_mai": round(d["mai"] / d["entry"], 2)
        })

    portfolio_eur = total_val_usd * USD_EUR
    profit_mai_eur = (total_val_mai_usd - INVESTITIE_TOTALA_USD) * USD_EUR

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": round(btc_d, 1), "eth_btc": round(eth_btc, 4), "eth_btc_trend": "up" if eth_btc > 0.029 else "down",
            "rotation_score": score, "portfolio_eur": round(portfolio_eur, 0),
            "profit_mai_eur": f"{profit_mai_eur:,.0f}", "investit_eur": round(INVESTITIE_TOTALA_USD * USD_EUR, 0), 
            "multiplier": round(portfolio_eur / (INVESTITIE_TOTALA_USD * USD_EUR), 2),
            "coins": results, "usdtd": round(global_data.get("market_cap_percentage", {}).get("usdt", 7.5), 1),
            "vix": vix, "dxy": 101, "urpd": 84.2, "total3": "0.98T", "m2": "21.2T", "fng": "9 (Extreme Fear)"
        }, f)

if __name__ == "__main__": main()
