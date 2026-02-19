import json
import requests

# --- CONFIGURARE ---
CMC_API_KEY = "46b755eda86e436d87dd4d6c6192ac03"
# -------------------

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
        # 1. Fetch Crypto Prices (CoinGecko)
        cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COINS_MAP.values())},bitcoin,ethereum,tether&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(cg_url, timeout=20).json()
        
        # 2. Fetch Fear & Greed Index (Alternative.me)
        fng_res = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        fng_val = int(fng_res['data'][0]['value'])
        fng_txt = fng_res['data'][0]['value_classification']

        # 3. Fetch Global Metrics (CoinMarketCap)
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        cmc_res = requests.get(cmc_url, headers=headers).json()
        cmc_data = cmc_res['data']
        
        btc_d = round(cmc_data['btc_dominance'], 2)
        # Calculăm USDT.D: (Cap USDT / Total Cap) * 100
        total_mc = cmc_data['quote']['USD']['total_market_cap']
        usdt_mc = requests.get(f"https://api.coingecko.com/api/v3/coins/tether").json()['market_data']['market_cap']['usd']
        usdt_d = round((usdt_mc / total_mc) * 100, 2)
        
        total3 = f"{round(cmc_data['quote']['USD']['total_market_cap_yesterday_percentage_change'], 2)}%" # Folosim o metrica dinamica aici sau Total MC
        total3_val = f"{round(total_mc / 1e12, 2)}T"

        # Logica portofoliu
        val_usd, apr_usd, fib_usd, results = 0, 0, 0, []
        investitie_eur = 101235
        
        for sym, m_id in COINS_MAP.items():
            coin_data = data.get(m_id, {})
            p = coin_data.get("usd", 0)
            if sym == "SNX" and (p == 0 or p is None): p = 0.34
            
            change_24h = coin_data.get("usd_24h_change", 0)
            info = PORTFOLIO_DATA[sym]
            val_usd += (p * info["q"])
            apr_usd += (info["apr"] * info["q"])
            fib_usd += (info["fib"] * info["q"])
            
            results.append({
                "symbol": sym, "price": p, "entry": info["entry"], "q": info["q"], 
                "change": round(change_24h, 2),
                "apr": info["apr"], "mai": info["mai"], "fib": info["fib"]
            })

        # Calcul Dinamic Rotation Score (bazat pe Altcoin Season Index logic simplificat)
        # Media 24h a portofoliului tau vs Bitcoin
        btc_change = data['bitcoin']['usd_24h_change']
        alts_avg_change = sum([c['change'] for c in results]) / len(results)
        dynamic_rotation = round(50 + (alts_avg_change - btc_change) * 2, 2)
        if dynamic_rotation > 100: dynamic_rotation = 100
        if dynamic_rotation < 0: dynamic_rotation = 0

        output = {
            "rotation_score": dynamic_rotation, 
            "btc_d": btc_d, 
            "eth_btc": round(data["ethereum"]["usd"]/data["bitcoin"]["usd"], 5),
            "usdt_d": usdt_d, 
            "smri": round(50 + (fng_val - 50), 2), # SMRI dinamic legat de sentiment
            "portfolio_eur": int(val_usd * 0.92), 
            "investitie_eur": investitie_eur,
            "p_apr": f"{int((apr_usd * 0.92) - investitie_eur):,} €",
            "p_fib": f"{int((fib_usd * 0.92) - investitie_eur):,} €",
            "coins": results, 
            "total3": total3_val, 
            "fng": f"{fng_val} ({fng_txt})", 
            "momentum": "BULLISH" if alts_avg_change > btc_change else "BEARISH",
            "vix": 14.2, "dxy": 101.1, "ml_prob": round(100 - dynamic_rotation, 1), "breadth": "54%",
            "m2": "21.2T", "exhaustion": "12.1%", "volat": "HIGH", "liq": "HIGH", "urpd": "84.2%"
        }
        
        with open("data.json", "w") as f:
            json.dump(output, f, indent=4)
        print(f"Update OK - BTC.D: {btc_d}%, F&G: {fng_val}, ROTATION: {dynamic_rotation}%")

    except Exception as e:
        print(f"Eroare: {e}")

if __name__ == "__main__":
    main()
