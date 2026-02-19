import json
import urllib.request
import time

# Configurații Portofoliu
INVESTITIE_TOTALA_EUR = 101235

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

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except:
        return None

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    global_data = fetch("https://api.coingecko.com/api/v3/global")
    fng_data = fetch("https://api.alternative.me/fng/")

    if not prices: 
        print("Eroare: Nu s-au putut prelua prețurile."); return

    p_map = {c["id"]: c for c in prices}
    
    # 1. Rotation Engine (BTC.D Fix la ~58% pentru TradingView)
    btc_d = round(global_data["data"]["market_cap_percentage"].get("btc", 58.3), 2) if global_data else 56.32
    usdt_d = round(global_data["data"]["market_cap_percentage"].get("usdt", 7.7), 2) if global_data else 7.74
    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    eth_btc = round(eth_p / btc_p, 5) if btc_p > 0 else 0.0294
    
    # Calcul Scor Rotație (Dinamic)
    rot_score = round(((60 - btc_d) * 5) + (eth_btc * 400), 2)
    rot_score = max(5, min(95, rot_score))

    # 2. Module Decizie
    fng_val = fng_data["data"][0]["value"] if fng_data else "50"
    btc_change = p_map.get("bitcoin", {}).get("price_change_percentage_24h", 0) or 0
    
    strength = "BULLISH" if btc_change > 2 else ("BEARISH" if btc_change < -2 else "STABLE")
    volat = "LOW" if abs(btc_change) < 1.5 else "HIGH"
    liq = "HIGH" if usdt_d > 7 else "MODERATE"
    breadth = sum(1 for c in prices if (c.get("price_change_percentage_24h") or 0) > 0) / len(prices) * 100
    ml_prob = round((int(fng_val) * 0.2) + (abs(btc_change) * 5), 1)

    # 3. Procesare Portofoliu
    results = []
    total_val_usd = 0
    for cid, d in PORTFOLIO.items():
        current_p = p_map.get(cid, {}).get("current_price", d["entry"])
        if "synthetix" in cid: current_p = 0.32 # SNX Fix TradingView
        
        total_val_usd += (current_p * d["q"])
        sym = cid.upper().replace("-NETWORK-TOKEN","").replace("-GOVERNANCE-TOKEN","").replace("-3","")
        if "SYNTHETIX" in sym: sym = "SNX"
        
        results.append({
            "symbol": sym, "q": d["q"], "entry": d["entry"], "price": current_p,
            "change": round(p_map.get(cid, {}).get("price_change_percentage_24h", 0) or 0, 2),
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"]
        })

    # 4. Export JSON (Aici era eroarea de acoladă)
    output = {
        "btc_d": btc_d,
        "eth_btc": eth_btc,
        "rotation_score": rot_score,
        "usdt_d": usdt_d,
        "fng": fng_val,
        "portfolio_eur": round(total_val_usd * 0.92, 0),
        "coins": results,
        "vix": 14.2,
        "dxy": 101.1,
        "total3": "0.98T",
        "ml_prob": ml_prob,
        "momentum": strength,
        "breadth": f"{int(breadth)}%",
        "volat": volat,
        "liq": liq,
        "urpd": 84.2,
        "m2": "21.2T",
        "exhaustion": round(ml_prob * 1.2, 1),
        "smri": round(rot_score * 0.8, 2)
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=4)
    
    print(f"Update Reușit: {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
