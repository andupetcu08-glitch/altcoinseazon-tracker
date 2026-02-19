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
    """ Încearcă să ia prețul SNX din surse alternative dacă CoinGecko eșuează. """
    try:
        # Sursa 1: CryptoCompare
        r = requests.get("https://min-api.cryptocompare.com/data/price?fsym=SNX&tsyms=USD", timeout=5)
        price = r.json().get("USD", 0)
        if price > 0: return price
    except:
        pass
    
    try:
        # Sursa 2: Binance Public API (Ticker)
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=SNXUSDT", timeout=5)
        price = float(r.json().get("price", 0))
        if price > 0: return price
    except:
        pass
        
    return 0.34 # Ultimul resort dacă pică totul

def update_data():
    try:
        # 1. Fetch Price Data
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(COINS_MAP.values())},bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=20)
        data = response.json()
        
        # 2. Fetch Global Data (BTC.D)
        g_url = "https://api.coingecko.com/api/v3/global"
        global_data = requests.get(g_url, timeout=20).json()
        btc_d = round(global_data["data"]["market_cap_percentage"]["btc"], 2)
        usdt_d = round(global_data["data"]["market_cap_percentage"].get("usdt", 7.5), 2)
        
        val_usd, apr_usd, fib_usd, results = 0, 0, 0, []
        investitie_eur = 101235
        
        for sym, m_id in COINS_MAP.items():
            coin_info = data.get(m_id, {})
            p = coin_info.get("usd", 0)
            change_24h = coin_info.get("usd_24h_change", 0)
            
            # LOGICA SPECIALĂ SNX
            if sym == "SNX":
                if p == 0 or p is None:
                    p = get_snx_price_backup()
                    print(f"[{time.strftime('%H:%M:%S')}] SNX price fetched from Backup: ${p}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] SNX price fetched from CoinGecko: ${p}")
            
            info = PORTFOLIO_DATA[sym]
            val_usd += (p * info["q"])
            apr_usd += (info["apr"] * info["q"])
            fib_usd += (info["fib"] * info["q"])
            
            results.append({
                "symbol": sym, "price": p, "entry": info["entry"], "q": info["q"], 
                "change": round(change_24h, 2),
                "apr": info["apr"], "mai": info["mai"], "fib": info["fib"]
            })

        # 3. Calcul Dinamic Rotation Score
        eth_p = data.get("ethereum", {}).get("usd", 2500)
        btc_p = data.get("bitcoin", {}).get("usd", 60000)
        eth_btc = round(eth_p / btc_p, 5)
        
        # O formulă care urcă spre 70 dacă ETH/BTC crește și BTC.D scade
        # (Exemplu: (100 - 58) * (0.04/0.05) * factor)
        rotation_score = round(((100 - btc_d) * (eth_btc / 0.055)) * 0.8, 2)
        rotation_score = min(max(rotation_score, 15), 98)

        # 4. Fear & Greed Dinamic bazat pe schimbarea BTC
        btc_change = data.get("bitcoin", {}).get("usd_24h_change", 0)
        fng_val = int(50 + (btc_change * 2.5))
        fng_val = min(max(fng_val, 5), 95)
        
        profit_apr = int((apr_usd * 0.92) - investitie_eur)
        profit_fib = int((fib_usd * 0.92) - investitie_eur)

        output = {
            "rotation_score": rotation_score,
            "btc_d": btc_d,
            "eth_btc": eth_btc,
            "usdt_d": usdt_d,
            "smri": round(rotation_score * 0.85, 2),
            "portfolio_eur": int(val_usd * 0.92),
            "investitie_eur": investitie_eur,
            "p_apr": f"{profit_apr:,} €",
            "p_fib": f"{profit_fib:,} €",
            "coins": results,
            "total3": "0.98T", "fng": f"{fng_val}", "momentum": "DYNAMIC",
            "vix": 14.2, "dxy": 101.1, "ml_prob": 12.4, "breadth": "28%",
            "m2": "21.2T", "exhaustion": "8%", "volat": "MED", "liq": "HIGH", "urpd": "81%"
        }
        
        with open("data.json", "w") as f:
            json.dump(output, f, indent=4)
        print(f"[{time.strftime('%H:%M:%S')}] Global Update OK (BTC.D: {btc_d}%).")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Incepe monitorizarea dinamică (Platină)...")
    while True:
        update_data()
        time.sleep(300) # 5 minute
