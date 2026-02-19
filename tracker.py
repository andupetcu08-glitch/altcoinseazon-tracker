import json
import requests
import time

COINS_MAP = {
    "OP": "optimism", "NOT": "notcoin", "ARB": "arbitrum", "TIA": "celestia",
    "JTO": "jito-governance-token", "LDO": "lido-dao", "CTSI": "cartesi",
    "IMX": "immutable-x", "SONIC": "sonic-3", "SNX": "synthetix-network-token"
}

PORTFOLIO_DATA = {
    "OP": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.2, "fib": 6.86},
    "NOT": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034},
    "ARB": {"q": 14326.44, "entry": 1.134, "apr": 3, "mai": 3.4, "fib": 3.82},
    "TIA": {"q": 4504.47, "entry": 5.911, "apr": 12, "mai": 15, "fib": 18.5},
    "JTO": {"q": 7366.42, "entry": 2.711, "apr": 8, "mai": 8.2, "fib": 9.2},
    "LDO": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.2, "fib": 6.9},
    "CTSI": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "IMX": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "SONIC": {"q": 13449.38, "entry": 0.81633, "apr": 1.05, "mai": 1.35, "fib": 1.55},
    "SNX": {"q": 20073.76, "entry": 0.722, "apr": 7.8, "mai": 9.3, "fib": 10.2}
}

def get_snx_price_backup():
    try:
        r = requests.get("https://min-api.cryptocompare.com/data/price?fsym=SNX&tsyms=USD", timeout=10)
        return r.json().get("USD", 1.85) # Valoare de backup daca pica API-ul
    except:
        return 1.85

def update_data():
    print(f"[{time.strftime('%H:%M:%S')}] Incerc actualizarea...")
    try:
        # 1. Preturi de baza
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COINS_MAP.values())},bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url, timeout=20).json()
        
        # 2. Date Globale
        g_data = requests.get("https://api.coingecko.com/api/v3/global", timeout=20).json()
        btc_d = g_data["data"]["market_cap_percentage"]["btc"]
        
        results = []
        val_usd, apr_usd, fib_usd = 0, 0, 0
        investitie_eur = 101235
        
        for sym, m_id in COINS_MAP.items():
            p = data.get(m_id, {}).get("usd", 0)
            change = data.get(m_id, {}).get("usd_24h_change", 0)
            
            if sym == "SNX" and p == 0:
                p = get_snx_price_backup()
            
            info = PORTFOLIO_DATA[sym]
            val_usd += (p * info["q"])
            apr_usd += (info["apr"] * info["q"])
            fib_usd += (info["fib"] * info["q"])
            
            results.append({
                "symbol": sym, "price": p, "entry": info["entry"], "q": info["q"], 
                "change": round(change, 2), "apr": info["apr"], "mai": info["mai"], "fib": info["fib"]
            })

        # Calcule finale
        eth_btc = data["ethereum"]["usd"] / data["bitcoin"]["usd"]
        rot_score = ((100 - btc_d) * (eth_btc / 0.055)) * 0.85
        rot_score = min(max(rot_score, 15), 95)

        output = {
            "rotation_score": round(rot_score, 2),
            "btc_d": round(btc_d, 2),
            "eth_btc": round(eth_btc, 5),
            "portfolio_eur": int(val_usd * 0.92),
            "investitie_eur": investitie_eur,
            "p_apr": f"{int((apr_usd * 0.92) - investitie_eur):,} €",
            "p_fib": f"{int((fib_usd * 0.92) - investitie_eur):,} €",
            "coins": results,
            "usdt_d": 7.5, "smri": 25, "total3": "1.0T", "fng": "20", "momentum": "STABLE",
            "vix": 14, "dxy": 101, "ml_prob": 10, "breadth": "20%", "m2": "21T", 
            "exhaustion": "10%", "volat": "LOW", "liq": "HIGH", "urpd": "80%"
        }
        
        with open("data.json", "w") as f:
            json.dump(output, f, indent=4)
        print("✅ Update reusit! Fisierul data.json a fost creat.")
        
    except Exception as e:
        print(f"❌ Eroare critica: {e}")

if __name__ == "__main__":
    while True:
        update_data()
        time.sleep(300)
