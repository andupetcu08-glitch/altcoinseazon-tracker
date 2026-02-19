import json
import requests
import pandas as pd # Optional, pentru prelucrare date daca e cazul

# --- CONFIGURARE ---
CMC_API_KEY = "46b755eda86e436d87dd4d6c6192ac03"

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

def get_macro_data():
    """Trage VIX si DXY din surse publice (Stooq)"""
    try:
        # VIX
        vix_res = requests.get("https://stooq.com/q/l/?s=^vix&f=sd2t2ohlc&h&e=csv")
        vix = float(vix_res.text.splitlines()[1].split(',')[6])
        # DXY
        dxy_res = requests.get("https://stooq.com/q/l/?s=dx.f&f=sd2t2ohlc&h&e=csv")
        dxy = float(dxy_res.text.splitlines()[1].split(',')[6])
        return vix, dxy
    except:
        return 14.2, 101.1 # Fallback daca serverele macro sunt ocupate

def main():
    try:
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        
        # 1. Fetch SNX si USDT via CMC (SNX ID: 2502, USDT ID: 825)
        # Am pus ID-urile in loc de simboluri pentru a evita ambiguitatea
        cmc_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id=1,1027,2502,825&convert=USD"
        cmc_res = requests.get(cmc_url, headers=headers).json()
        
        snx_p = cmc_res['data']['2502']['quote']['USD']['price']
        usdt_mc = cmc_res['data']['825']['quote']['USD']['market_cap']
        
        # 2. Global Metrics (CMC)
        global_res = requests.get("https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest", headers=headers).json()
        total_mc = global_res['data']['quote']['USD']['total_market_cap']
        btc_d = round(global_res['data']['btc_dominance'], 2)
        usdt_d = round((usdt_mc / total_mc) * 100, 2)

        # 3. Restul monedelor (CoinGecko) + Fear & Greed
        cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COINS_MAP.values())},bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        cg_data = requests.get(cg_url).json()
        
        fng_res = requests.get("https://api.alternative.me/fng/").json()
        fng_val = int(fng_res['data'][0]['value'])

        # 4. Macro Data Dinamic
        vix, dxy = get_macro_data()

        # Calcule Portofoliu
        val_usd, apr_usd, fib_usd, results = 0, 0, 0, []
        investitie_eur = 101235
        
        for sym, m_id in COINS_MAP.items():
            coin_data = cg_data.get(m_id, {})
            p = snx_p if sym == "SNX" else coin_data.get("usd", 0)
            change = coin_data.get("usd_24h_change", 0)
            
            info = PORTFOLIO_DATA[sym]
            val_usd += (p * info["q"])
            apr_usd += (info["apr"] * info["q"])
            fib_usd += (info["fib"] * info["q"])
            
            results.append({
                "symbol": sym, "price": p, "entry": info["entry"], "q": info["q"], 
                "change": round(change, 2), "apr": info["apr"], "mai": info["mai"], "fib": info["fib"]
            })

        # Logică Dinamică Scorul de Rotație & ML Prob
        # Corelație: Rotația crește dacă Dominanța BTC scade și F&G crește
        rot_score = round(((65 - btc_d) * 1.5) + (fng_val * 0.4), 2)
        ml_prob = round((rot_score / 70) * 45, 1)

        output = {
            "rotation_score": rot_score, 
            "btc_d": btc_d, 
            "usdt_d": usdt_d,
            "eth_btc": round(cg_data["ethereum"]["usd"]/cg_data["bitcoin"]["usd"], 5),
            "portfolio_eur": int(val_usd * 0.92), 
            "investitie_eur": investitie_eur,
            "p_apr": f"{int((apr_usd * 0.92) - investitie_eur):,} €",
            "p_fib": f"{int((fib_usd * 0.92) - investitie_eur):,} €",
            "coins": results, 
            "total3": f"{round(total_mc/1e12, 2)}T", 
            "fng": f"{fng_val} ({fng_res['data'][0]['value_classification']})",
            "ml_prob": ml_prob, 
            "vix": vix, 
            "dxy": dxy, 
            "smri": round(fng_val * 0.8, 2), # SMRI dinamic legat de sentiment
            "momentum": "BULLISH" if fng_val > 50 else "BEARISH",
            "breadth": f"{round(100 - btc_d, 1)}%", # Alts breadth aprox.
            "m2": "21.4T", # M2 e raportat lunar, ramane cvasistatic
            "exhaustion": f"{round(ml_prob * 0.5, 1)}%", 
            "volat": "HIGH" if vix > 18 else "LOW",
            "liq": "HIGH" if dxy < 102 else "LOW",
            "urpd": "84.2%" 
        }
        
        with open("data.json", "w") as f:
            json.dump(output, f, indent=4)
        print(f"Update OK - SNX: {snx_p:.4f} - VIX: {vix} - DXY: {dxy}")

    except Exception as e:
        print(f"Eroare: {e}")

if __name__ == "__main__":
    main()
