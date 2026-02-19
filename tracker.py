import json
import requests

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

def main():
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COINS_MAP.values())},bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url, timeout=20).json()
        val_usd, apr_usd, fib_usd, results = 0, 0, 0, []
        
        for sym, m_id in COINS_MAP.items():
            p = data.get(m_id, {}).get("usd", 0)
            if sym == "SNX" and (p == 0 or p is None): p = 0.34
            
            info = PORTFOLIO_DATA[sym]
            val_usd += (p * info["q"])
            apr_usd += (info["apr"] * info["q"])
            fib_usd += (info["fib"] * info["q"])
            
            results.append({
                "symbol": sym, "price": p, "entry": info["entry"], "q": info["q"], 
                "change": round(data.get(m_id, {}).get("usd_24h_change", 0), 2),
                "apr": info["apr"], "mai": info["mai"], "fib": info["fib"]
            })

        fng_val = 9 
        fng_txt = "Extreme Fear" if fng_val <= 25 else "Fear" if fng_val <= 45 else "Neutral" if fng_val <= 55 else "Greed" if fng_val <= 75 else "Extreme Greed"

        output = {
            "rotation_score": 30.18, "btc_d": 58.82, 
            "eth_btc": round(data["ethereum"]["usd"]/data["bitcoin"]["usd"], 5),
            "usdt_d": 7.73, "smri": 24.14, 
            "portfolio_eur": round(val_usd * 0.92, 0), "investitie_eur": 101235,
            "p_apr": f"€{round(apr_usd * 0.92, 0):,}", "p_fib": f"€{round(fib_usd * 0.92, 0):,}",
            "coins": results, "total3": "0.98T", "fng": f"{fng_val} ({fng_txt})", "momentum": "STABLE",
            "vix": 14.2, "dxy": 101.1, "ml_prob": 10.1, "breadth": "15%",
            "m2": "21.2T", "exhaustion": "12.1%", "volat": "HIGH", "liq": "HIGH", "urpd": "84.2%"
        }
        with open("data.json", "w") as f:
            json.dump(output, f, indent=4)
        print("Update OK")
    except Exception as e:
        print(f"Eroare: {e}")

if __name__ == "__main__":
    main()
