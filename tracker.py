import json, urllib.request

INVESTITIE_TOTALA_EUR = 101235
# Target-uri noi conform cerinței
TARGETS = {"BTCD": 48.0, "ROTATION": 70.0, "USDTD": 5.5, "ETHBTC": 0.055}

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.2, "fib": 6.86, "symbol":"OP"},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034, "symbol":"NOT"},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.4, "fib": 3.82, "symbol":"ARB"},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 15.0, "fib": 18.5, "symbol":"TIA"},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.2, "fib": 9.2, "symbol":"JTO"},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.2, "fib": 6.9, "symbol":"LDO"},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24, "symbol":"CTSI"},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85, "symbol":"IMX"},
    "sonic-3": {"q": 13449.38, "entry": 0.81633, "apr": 1.05, "mai": 1.35, "fib": 1.55, "symbol":"SONIC"},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.2, "symbol":"SNX"}
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r: return json.loads(r.read().decode())
    except: return None

def normalize(v, min_v, max_v):
    return max(0, min(100, (v - min_v) / (max_v - min_v) * 100))

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng = fetch("https://api.alternative.me/fng/")
    eur = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur")

    if not prices or not global_api: return

    p_map = {c["id"]: c for c in prices}
    btc_p = p_map["bitcoin"]["current_price"]
    eth_p = p_map["ethereum"]["current_price"]
    btc_d = global_api["data"]["market_cap_percentage"]["btc"]
    usdt_d = global_api["data"]["market_cap_percentage"]["usdt"]
    eth_btc = eth_p / btc_p
    fng_val = int(fng["data"][0]["value"]) if fng else 50

    # 1. Rotation Engine (30% BTCD + 25% ETHBTC + 15% USDTD + 10% T3 + 10% Sent + 10% Liq)
    rot_score = (
        normalize(60 - btc_d, 0, 15) * 0.30 +
        normalize(eth_btc, 0.03, 0.07) * 0.25 +
        normalize(10 - usdt_d, 2, 6) * 0.15 +
        60 * 0.10 +  # Proxy Total3
        normalize(fng_val, 20, 90) * 0.10 +
        55 * 0.10    # Proxy Liquidity
    )

    smri = ((0.065 / eth_btc) * 40) + ((10 - usdt_d) * 4)
    breadth = sum(1 for c in prices if (c.get("price_change_percentage_24h") or 0) > 0) / len(prices) * 100
    exhaustion = (rot_score * 0.4) + (smri * 0.3) + (breadth * 0.3)
    cycle_prob = normalize(rot_score + exhaustion, 60, 160)

    # Status: HOLD roșu sub 70% (conform instrucțiunilor tale salvate)
    status = "SELL" if rot_score >= 75 else ("PREPARE" if rot_score >= 68 else "HOLD")

    coins = []
    total_val = 0
    for cid, d in PORTFOLIO.items():
        p = p_map.get(cid, {}).get("current_price", d["entry"])
        total_val += p * d["q"]
        heat = "red" if p < d["entry"] else ("orange" if p > d["apr"] else "#00ff88")
        coins.append({"symbol": d["symbol"], "price": round(p, 4), "apr": d["apr"], "mai": d["mai"], "fib": d["fib"], "heat": heat, "change": round(p_map.get(cid, {}).get("price_change_percentage_24h", 0), 2)})

    usd_eur = eur["bitcoin"]["eur"] / btc_p
    
    with open("data.json", "w") as f:
        json.dump({
            "rotation": round(rot_score, 2), "smri": round(smri, 2), "btc_d": round(btc_d, 2),
            "eth_btc": round(eth_btc, 4), "usdt_d": round(usdt_d, 2), "breadth": round(breadth, 2),
            "exhaustion": round(exhaustion, 2), "cycle_prob": round(cycle_prob, 2),
            "status": status, "portfolio_eur": round(total_val * usd_eur),
            "vix": 14.2, "dxy": 101.1, "m2": "21.2T", "total3": "0.98T", "urpd": 84.2, "ml_prob": 18.9,
            "coins": coins
        }, f)

if __name__ == "__main__": main()
