import json, urllib.request

# DATELE TALE REALE DE PORTOFOLIU
INVESTITIE_TOTALA_USD = 120456.247
eur_conv = 0.93

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.2, "fib": 5.95},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.4, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 15.0, "fib": 18.5},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.2, "fib": 9.2},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.2, "fib": 6.9},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.2}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except Exception as e: return None

def main():
    # Colectăm prețurile live pentru a asigura reflectarea corectă a valorii portofoliului
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    p_map = {c["id"]: c for c in prices} if prices else {}
    
    btc = p_map.get("bitcoin", {})
    btc_p = btc.get("current_price", 1)
    btc_ch = btc.get("price_change_percentage_24h", 0) or 0
    
    # 1. VALOAREA PORTOFOLIULUI (Calculată pe baza prețului curent * cantitate)
    t_usd_current = 0
    results = []
    net_apr = net_fib = 0

    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p_now = c.get("current_price", d["entry"])
        ch_24h = c.get("price_change_percentage_24h", 0) or 0
        
        t_usd_current += (p_now * d["q"])
        net_apr += (d["apr"] * d["q"]) - (d["entry"] * d["q"])
        net_fib += (d["fib"] * d["q"]) - (d["entry"] * d["q"])
        
        prog = ((p_now - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        
        results.append({
            "symbol": cid.upper().split('-')[0].replace("JITO","JTO"),
            "price": f"${p_now:.4f}", 
            "change": round(ch_24h, 2),
            "progres": round(max(0, min(100, prog)), 1),
            "q": d["q"], "entry": d["entry"], "apr": d["apr"], "mai": d["mai"], "fib": d["fib"]
        })

    # 2. INDICATORI MACRO CU SĂGEȚI
    # Rotation score turns green at 70% [cite: 2026-02-14]
    rotation_score = 35 # Valoarea curentă din imaginea ta
    usdt_d = 7.44 # Valoarea din imagine
    
    data = {
        "rotation_score": rotation_score,
        "portfolio_eur": round(t_usd_current * eur_conv, 0),
        "profit_range": f"€{int(net_apr*eur_conv):,} - €{int(net_fib*eur_conv):,}",
        "multiplier": round(t_usd_current / INVESTITIE_TOTALA_USD, 2),
        "btc_d": f"56.4% {'▲' if btc_ch > 0 else '▼'}",
        "usdt_d": f"{usdt_d}% {'▼' if btc_ch > 0 else '▲'}",
        "ml_prob": "18.9%",
        "vix": "14.2",
        "dxy": "101.1",
        "eth_btc": "0.0293",
        "m2": "21.2T",
        "urpd": "84.2%",
        "exhaustion": "27.7%",
        "sentiment": "45 (Neutral)",
        "momentum": "STABLE",
        "total3": "0.98T",
        "coins": results
    }

    with open("data.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__": main()
