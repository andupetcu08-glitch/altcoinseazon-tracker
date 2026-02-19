import json
import urllib.request
import statistics
import math
from datetime import datetime

# Configurații fixe
INVESTITIE_TOTALA_USD = 120456.247
PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.20, "fib": 5.95},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.40, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 15.00, "fib": 18.50},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.20, "fib": 9.20},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.20, "fib": 6.90},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "sonic-3": {"q": 13449.38, "entry": 0.81633, "apr": 1.05, "mai": 1.35, "fib": 1.55},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.20}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except: return None

def normalize(val, minv, maxv):
    return max(0, min(100, round((val - minv) / (maxv - minv) * 100, 2))) if maxv > minv else 0

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    global_data = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")
    
    pm = {c["id"]: c for c in prices} if prices else {}
    
    # Date Macro
    btc_d = global_data["data"]["market_cap_percentage"]["btc"] if global_data else 52
    eth_p, btc_p = pm.get("ethereum", {}).get("current_price", 1), pm.get("bitcoin", {}).get("current_price", 1)
    ethbtc = round(eth_p / btc_p, 5)
    fng = int(fng_api["data"][0]["value"]) if fng_api else 50
    
    # Placeholder date externe (DXY, VIX, M2 pot fi luate prin API-uri dedicate sau manual)
    usdt_d = 5.8; vix = 16.5; dxy = 102.4; m2 = 4.8; total3 = 1.15 # In Trilioane

    # Calcul Monede & Exhaustion
    coins, prog_list = [], []
    port_val = 0
    for cid, d in PORTFOLIO.items():
        p = pm.get(cid, {}).get("current_price", d["entry"])
        ch = pm.get(cid, {}).get("price_change_percentage_24h", 0)
        prog = max(0, min(100, ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100))
        prog_list.append(prog)
        port_val += p * d["q"]
        
        coins.append({
            "symbol": cid.upper().replace("-NETWORK-TOKEN","").split("-")[0],
            "price": round(p, 4), "change": round(ch, 2), "progress": round(prog, 2),
            "exhaustion": round(prog * 0.85 + (ch if ch > 0 else 0), 2)
        })

    # MODULE SCORING
    liq = (normalize(m2, -2, 8) * 0.5 + normalize(110-dxy, 0, 15) * 0.5)
    lev = (normalize(80-vix, 40, 68) * 0.4 + normalize(fng, 20, 90) * 0.6)
    rot = (normalize(60-btc_d, 0, 15) * 0.4 + normalize(ethbtc, 0.04, 0.08) * 0.6)
    exh = statistics.mean(prog_list)
    
    # SMART MONEY ROTATION INDEX (SMRI)
    # Corelează scăderea USDT.D cu creșterea ETHBTC
    smri = (normalize(10-usdt_d, 0, 6) * 0.5 + normalize(ethbtc, 0.035, 0.075) * 0.5)

    # FINAL PROBABILISTIC SCORE
    # Ponderare: 30% Rotation, 30% Smart Money, 20% Exhaustion, 20% Liquidity
    final_score = round((rot * 0.3 + smri * 0.3 + exh * 0.2 + liq * 0.2), 2)
    
    # REGIME LOGIC
    regime = "SELL" if final_score >= 70 else ("PREPARE" if final_score >= 50 else "HOLD")
    prob_top = round(1 / (1 + math.exp(-(final_score/100 - 0.55) * 10)) * 100, 2)

    out = {
        "btc_d": round(btc_d, 2), "ethbtc": ethbtc, "usdt_d": usdt_d, "dxy": dxy, "vix": vix,
        "liquidity_score": round(liq, 1), "leverage_score": round(lev, 1),
        "rotation_score": final_score, "smri": round(smri, 1),
        "exhaustion_score": round(exh, 1), "probability_top": prob_top,
        "regime": regime, "portfolio_value": round(port_val, 2),
        "coins": coins, "updated": datetime.utcnow().strftime("%H:%M:%S")
    }

    with open("data.json", "w") as f: json.dump(out, f, indent=2)

if __name__ == "__main__": main()
