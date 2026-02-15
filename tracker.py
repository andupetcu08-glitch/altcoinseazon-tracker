import json, urllib.request

# DATE PORTOFOLIU (Verifică să fie corecte cu input-ul tău)
INVESTITIE_TOTALA_USD = 120456.247

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

def get_sentiment_label(val):
    if val <= 25: return "Extreme Fear"
    if val <= 45: return "Fear"
    if val <= 55: return "Neutral"
    if val <= 75: return "Greed"
    return "Extreme Greed"

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    btc_eur_data = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")
    
    p_map = {c["id"]: c for c in prices} if prices else {}
    btc_usd = p_map.get("bitcoin", {}).get("current_price", 1)
    
    # Rata de schimb Live USD/EUR bazată pe prețul BTC în ambele monede
    btc_eur = btc_eur_data.get("bitcoin", {}).get("eur", 1)
    usd_eur_live = btc_eur / btc_usd if btc_usd > 0 else 0.92

    fng_val = int(fng_api["data"][0]["value"]) if fng_api else 8 # Fallback la 8 pentru test
    sentiment_txt = f"{fng_val} ({get_sentiment_label(fng_val)})"

    total_val_usd = 0
    results = []

    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", 0)
        if p == 0: p = d["entry"] # Fallback dacă API-ul nu returnează prețul
        
        # SINCRONIZARE PORTOFOLIU: Preț * Cantitate
        current_value_usd = p * d["q"]
        total_val_usd += current_value_usd
        
        results.append({
            "symbol": cid.upper().replace("-NETWORK-TOKEN","").replace("-GOVERNANCE-TOKEN","").split("-")[0],
            "price": p, "change": c.get("price_change_percentage_24h", 0) or 0,
            "q": d["q"], "entry": d["entry"], "apr": d["apr"], "mai": d["mai"], "fib": d["fib"]
        })

    with open("data.json", "w") as f:
        json.dump({
            "portfolio_eur": round(total_val_usd * usd_eur_live, 0),
            "fng": sentiment_txt,
            "btc_d": round(global_api["data"]["market_cap_percentage"]["btc"], 1) if global_api else 56.4,
            "eth_btc": round(p_map.get("ethereum", {}).get("current_price", 0) / btc_usd, 4) if btc_usd > 0 else 0.029,
            "coins": results,
            # Restul valorilor macro rămân conform datelor tale preferate
            "rotation_score": 35, "usdt_d": 7.44, "ml_prob": 18.9, "momentum": "STABLE", 
            "vix": 14.2, "dxy": 101.1, "total3": "0.98T", "urpd": "84.2%", "m2": "21.2T",
            "exhaustion": "27.7%", "multiplier": round((total_val_usd / INVESTITIE_TOTALA_USD), 2)
        }, f)

if __name__ == "__main__": main()
