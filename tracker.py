import json, urllib.request
import yfinance as yf

# CONFIGURAȚIE EXACTĂ
INVESTITIE_FIXA_EUR = 101235.0 

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.2, "fib": 5.95},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.4, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 15.0, "fib": 18.5},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.2, "fib": 9.2},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.2, "fib": 6.9},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "sonic-3": {"q": 13449.38, "entry": 0.81633, "apr": 1.05, "mai": 1.35, "fib": 1.55},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.2}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def get_live_macro():
    """Extrage VIX si DXY din Yahoo Finance"""
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        dxy = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
        return round(vix, 2), round(dxy, 3)
    except: return 14.2, 101.1

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum", "tether"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}&price_change_percentage=24h")
    btc_eur_data = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng_api = fetch("https://api.alternative.me/fng/")
    
    p_map = {c["id"]: c for c in prices} if prices else {}
    btc_usd = p_map.get("bitcoin", {}).get("current_price", 1)
    
    # Curs USD/EUR live
    btc_eur = btc_eur_data.get("bitcoin", {}).get("eur", 1)
    usd_eur_live = btc_eur / btc_usd if btc_usd > 0 else 0.92

    # Date Macro
    total_mcap = global_api["data"]["total_market_cap"]["usd"] if global_api else 1
    usdt_mcap = p_map.get("tether", {}).get("market_cap", 0)
    usdt_d = round((usdt_mcap / total_mcap) * 100, 2)
    btc_d = round(global_api["data"]["market_cap_percentage"]["btc"], 1) if global_api else 56.4
    
    vix_live, dxy_live = get_live_macro()
    fng_val = int(fng_api["data"][0]["value"]) if fng_api else 45

    results = []
    total_val_usd = 0
    total_val_apr_usd = 0
    total_val_fib_usd = 0

    for cid, d in PORTFOLIO.items():
        c = p_map.get(cid, {})
        p = c.get("current_price", 0)
        if p == 0: p = d["entry"]
        if "synthetix" in cid: p = 0.294 # SNX fixat
        
        total_val_usd += (p * d["q"])
        total_val_apr_usd += (d["apr"] * d["q"])
        total_val_fib_usd += (d["fib"] * d["q"])
        
        prog = ((p - d["entry"]) / (d["fib"] - d["entry"])) * 100 if d["fib"] > d["entry"] else 0
        symbol = cid.upper().split("-")[0].replace("SYNTHETIX", "SNX")

        results.append({
            "symbol": symbol, "q": d["q"], "entry": d["entry"], "progres": round(max(0, min(100, prog)), 1),
            "price": f"{p:.4f}", "change": round(c.get("price_change_percentage_24h", 0) or 0, 2),
            "apr": d["apr"], "mai": d["mai"], "fib": d["fib"],
            "x_apr": round(d["apr"] / d["entry"], 1), "x_mai": round(d["mai"] / d["entry"], 1)
        })

    port_eur = total_val_usd * usd_eur_live
    # Rotation Score recalculat live
    rot_score = int(max(0, min(100, (65 - btc_d) * 4 + (7.5 - usdt_d) * 10)))

    with open("data.json", "w") as f:
        json.dump({
            "btc_d": btc_d, "eth_btc": round(p_map.get("ethereum", {}).get("current_price", 0) / btc_usd, 4),
            "rotation_score": rot_score,
            "portfolio_eur": round(port_eur, 0),
            "investit_eur": INVESTITIE_FIXA_EUR,
            "multiplier": round(port_eur / INVESTITIE_FIXA_EUR, 2),
            "profit_range": f"€{((total_val_apr_usd * usd_eur_live) - INVESTITIE_FIXA_EUR):,.0f} - €{((total_val_fib_usd * usd_eur_live) - INVESTITIE_FIXA_EUR):,.0f}",
            "coins": results, "vix": vix_live, "dxy": dxy_live, "usdt_d": usdt_d, "fng": fng_val
        }, f)

if __name__ == "__main__": main()
