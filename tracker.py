import json, urllib.request

INVEST_USD = 120456.247

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
        with urllib.request.urlopen(req, timeout=10) as r: return json.loads(r.read().decode())
    except: return None

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin", "ethereum"]
    prices = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    p_map = {c["id"]: c for c in prices} if prices else {}
    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    
    total_usd = 0
    total_usd_prev = 0
    coins_out = []
    
    for cid, d
