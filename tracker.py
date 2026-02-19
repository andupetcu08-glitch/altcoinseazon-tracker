import json
import requests
import sys

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

def main():
    try:
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        # Fetch CMC (BTC, ETH, SNX id:64, USDT)
        cmc_res = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id=1,1027,64,825&convert=USD", headers=headers).json()
        
        snx_p = cmc_res['data']['64']['quote']['USD']['price']
        usdt_mc = cmc_res['data']['825']['quote']['USD']['market_cap']
        
        global_res = requests.get("https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest", headers=headers).json()
        total_mc = global_res['data']['quote']['USD']['total_market_cap']
        btc_d = round(global_res['data']['btc_dominance'], 2)
        usdt_d = round((usdt_mc / total_mc) * 100, 2)

        cg_data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COINS_MAP.values())},bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true").json()
        fng_val = int(requests.get("https://api.alternative.me/fng/").json()['data'][0]['value'])

        val_usd, apr_usd, fib_usd, results = 0, 0, 0, []
        investitie_eur = 101235
        
        for sym, m_id in COINS_MAP.items():
            coin_info = cg_data.get(m_id, {})
            p = snx_p if sym == "SNX" else coin_info.get("usd", 0)
            if p is None: p = 0 # Protectie anti NoneType
            
            change = coin_info.get("usd_24h_change", 0) or 0
            info = PORTFOLIO_DATA[sym]
            val_usd += (p * info["q"])
            apr_usd += (info["apr"] * info["q"])
            fib_usd += (info["fib"] * info["q"])
            
            results.append({
                "symbol": sym, "price": p, "entry": info["entry"], "q": info["q"], 
                "change": round(change, 2), "apr": info["apr"], "mai": info["mai"], "fib": info["fib"]
            })

        rot_score = round(((60 - btc_d) * 2) + (fng_val * 0.5), 2)
        ml_prob = round((rot_score / 70) * 45, 1)

        output = {
            "rotation_score": rot_score, "btc_d": btc_d, "usdt_d": usdt_d,
            "eth_btc": round(cg_data["ethereum"]["usd"]/cg_data["bitcoin"]["usd"], 5),
            "portfolio_eur": int(val_usd * 0.92), "investitie_eur": investitie_eur,
            "p_apr": f"{int((apr_usd * 0.92) - investitie_eur):,} €",
            "p_fib": f"{int((fib_usd * 0.92) - investitie_eur):,} €",
            "coins": results, "total3": f"{round(total_mc/1e12, 2)}T", 
            "fng": f"{fng_val}", "ml_prob": ml_prob, 
            "vix": 14.8, "dxy": 101.4, "smri": round(fng_val * 0.82, 2),
            "momentum": "PREPARE" if rot_score > 50 else "HOLD",
            "breadth": f"{int(100 - btc_d)}%", "m2": "21.4T", "exhaustion": "LOW", "volat": "LOW", "liq": "HIGH", "urpd": "84.2%"
        }
        
        with open("data.json", "w") as f:
            json.dump(output, f, indent=4)
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
