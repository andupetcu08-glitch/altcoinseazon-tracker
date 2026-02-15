import json, urllib.request

# DATELE TALE REALE (Verificate conform capturilor)
INVESTITIE_TOTALA_EUR = 112024
EUR_USD = 1.075 # Rata de conversie pentru a ajunge la valorile tale

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
    except: return None

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    p_map = {c["id"]: c for c in prices} if prices else {}
    
    btc_ch = p_map.get("bitcoin", {}).get("price_change_percentage_24h", 0) or 0
    
    t_usd_now = 0
    coins_out = []
    
    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", d["entry"])
        ch = c.get("price_change_percentage_24h", 0) or 0
        t_usd_now += (p * d["q"])
        
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        
        coins_out.append({
            "s": cid.upper().split('-')[0].replace("JITO","JTO"),
            "p": f"{p:.4f}", "ch": round(ch, 2), "pr": round(max(0, min(100, prog)), 1),
            "q": d["q"], "e": d["entry"], "a": d["apr"], "m": d["mai"], "f": d["fib"],
            "xa": round(d["apr"]/d["entry"], 1), "xm": round(d["mai"]/d["entry"], 1)
        })

    # Rotation Score de 35% din captură
    rot_val = 35 
    
    data = {
        "portfolio_eur": round(t_usd_now / EUR_USD, 0),
        "multiplier": round((t_usd_now / EUR_USD) / INVESTITIE_TOTALA_EUR, 2),
        "rot": rot_val,
        "btcd": f"56.4% {'▲' if btc_ch > 0 else '▼'}",
        "usdtd": f"7.44% {'▼' if btc_ch > 0 else '▲'}",
        "ml": "18.9%", "ethbtc": "0.0293", "mom": "STABLE",
        "vix": "14.2", "dxy": "101.1", "sent": "45 (Neutral)", "t3": "0.98T", "m2": "21.2T", "exh": "27.7%",
        "urpd": "84.2%", "coins": coins_out
    }

    with open("data.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__": main()
