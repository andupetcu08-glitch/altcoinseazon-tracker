import json
import urllib.request
import statistics
import math
from datetime import datetime

# Configurații Portofoliu
PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "fib": 5.95},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "fib": 18.50},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "fib": 9.20},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "fib": 6.90},
    "cartesi": {"q": 49080, "entry": 0.19076, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "fib": 4.85},
    "sonic-3": {"q": 13449.38, "entry": 0.81633, "fib": 1.55},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "fib": 10.20}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except: return None

def normalize(val, minv, maxv):
    return max(0, min(100, round((val - minv) / (maxv - minv) * 100, 2)))

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    global_data = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")
    
    pm = {c["id"]: c for c in prices} if prices else {}
    
    # Date Macro (Unele simulate/statice pentru stabilitate dacă API lipsește)
    btc_d = global_data["data"]["market_cap_percentage"]["btc"] if global_data else 56.28
    eth_p = pm.get("ethereum", {}).get("current_price", 1)
    btc_p = pm.get("bitcoin", {}).get("current_price", 1)
    ethbtc = round(eth_p / btc_p, 5)
    fng = int(fng_api["data"][0]["value"]) if fng_api else 35
    
    usdt_d = 7.61; vix = 14.2; dxy = 101.1; m2 = 21.2; total3 = 0.98 

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
            "exhaustion": round(prog * 0.85, 2)
        })

    # Calcule Scoruri
    liq_score = normalize(m2, 18, 25)
    lev_score = normalize(fng, 20, 80)
    rot_score_val = round((normalize(60-btc_d, 0, 15) * 0.4 + normalize(ethbtc, 0.03, 0.07) * 0.6), 2)
    smri = round((normalize(10-usdt_d, 2, 8) * 0.5 + normalize(ethbtc, 0.03, 0.07) * 0.5), 2)
    exh_avg = statistics.mean(prog_list)
    
    # Final Score & Regime
    final_score = round((rot_score_val * 0.4 + smri * 0.3 + exh_avg * 0.3), 2)
    regime = "SELL" if final_score >= 70 else ("PREPARE" if final_score >= 50 else "HOLD")
    prob_top = round(normalize(final_score, 20, 90), 1)

    out = {
        "btc_d": btc_d, "ethbtc": ethbtc, "usdt_d": usdt_d, "dxy": dxy, "vix": vix, "m2": m2, "total3": total3,
        "liquidity_score": liq_score, "leverage_score": lev_score,
        "rotation_score": final_score, "smri": smri,
        "exhaustion_score": round(exh_avg, 1), "probability_top": prob_top,
        "regime": regime, "portfolio_value": round(port_val, 2),
        "coins": coins, "updated": datetime.utcnow().strftime("%H:%M:%S")
    }

    with open("data.json", "w") as f: json.dump(out, f, indent=2)

if __name__ == "__main__": main()
