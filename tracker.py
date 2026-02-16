import json, urllib.request

INVEST_EUR = 101235.0 

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())
    except: return None

def get_yahoo(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        data = fetch(url)
        return data['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 1.0

def main():
    # Surse Date
    p_data = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,tether,optimism,notcoin,arbitrum,celestia,jito-governance-token,lido-dao,cartesi,immutable-x,sonic-3,synthetix-network-token")
    g_data = fetch("https://api.coingecko.com/api/v3/global")
    f_data = fetch("https://api.alternative.me/fng/")

    if not p_data or not g_data: return

    p_map = {c["id"]: c for c in p_data}
    total_mcap = g_data["data"]["total_market_cap"]["usd"]

    # --- Calcule Casete Live ---
    # BTC.D
    btcd = round((p_map.get("bitcoin", {}).get("market_cap", 0) / total_mcap) * 100, 2)
    
    # ETH/BTC
    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    ethbtc = round(eth_p / btc_p, 4)

    # USDT.D
    usdtd = round((p_map.get("tether", {}).get("market_cap", 0) / total_mcap) * 100, 2)
    
    # Fear & Greed
    fng_val = int(f_data["data"][0]["value"]) if f_data else 10
    fng_txt = f_data["data"][0]["value_classification"] if f_data else "N/A"

    # Macro Automatizat
    vix = get_yahoo("^VIX")
    dxy = get_yahoo("DX-Y.NYB")

    # Rotation Score (Target 70%)
    # Formula: daca BTCD scade spre 46%, rotatia urca spre 70%
    rot_score = round(max(0, min(100, (63 - btcd) * 5 + (fng_val / 2))), 0)

    # --- Portofoliu ---
    total_usd = 0
    # Aici procesezi portofoliul tau (Optimism, Notcoin, etc.)
    # SNX forțat la 0.294
    
    port_eur = total_usd * 0.92
    multiplier = round(port_eur / INVEST_EUR, 2)

    output = {
        "port_eur": round(port_eur, 0),
        "invest_eur": INVEST_EUR,
        "mult": multiplier, # Doar numarul
        "rotation": int(rot_score),
        "btcd": btcd,
        "ethbtc": ethbtc,
        "usdtd": usdtd,
        "fng": f"{fng_val} ({fng_txt})",
        "vix": round(vix, 2),
        "dxy": round(dxy, 2),
        "m2": "22.4T" # M2 ramane momentan estimat
    }

    with open("data.json", "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    main()
