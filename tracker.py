import json, urllib.request, time, os

COINS = {
    "optimism":4.8, "notcoin":0.03, "arbitrum":3.5, "celestia":12,
    "jito-governance-token":8, "lido-dao":6, "cartesi":0.2,
    "immutable-x":4, "sonic-coin":1, "synthetix-network-token":7.8
}

HISTORY_FILE = "history.json"

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_history(h):
    with open(HISTORY_FILE, "w") as f: json.dump(h[-300:], f, indent=2)

def norm(x, a, b): return max(0, min(1, (x - a) / (b - b))) if a == b else max(0, min(1, (x - a) / (b - a)))

def main():
    prices = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250")
    global_data = fetch("https://api.coingecko.com/api/v3/global")["data"]
    price_map = {c["id"]: c for c in prices}

    btc_d = global_data["market_cap_percentage"]["btc"]
    eth_d = global_data["market_cap_percentage"]["eth"]
    total3 = (global_data["total_market_cap"]["usd"] * (1 - (btc_d + eth_d) / 100)) / 1e12

    history = load_history()
    history.append({"time": time.time(), "btc_d": btc_d, "total3": total3})
    save_history(history)

    rot = (history[-1]["total3"] - history[-5]["total3"]) / history[-5]["total3"] * 100 if len(history) > 5 else 0
    btc_trend = history[-5]["btc_d"] - btc_d if len(history) > 5 else 0

    crypto_score = (1 - norm(btc_d, 42, 58)) * 0.45 + norm(total3, 0.4, 2) * 0.35 + norm(rot, 0, 20) * 0.2
    exit_prob = round(crypto_score * 100, 1)
    regime = "🔴 SELL" if exit_prob > 75 else "🟡 PREPARE" if exit_prob > 50 else "🟢 HOLD"

    rows = ""
    for coin_id, target in COINS.items():
        if coin_id in price_map:
            c = price_map[coin_id]
            p = c["current_price"]
            mom = c["price_change_percentage_24h"] or 0
            prog = round(p / target * 100, 1)
            rows += f"<tr><td>{c['symbol'].upper()}</td><td>${p}</td><td>{prog}%</td><td>{mom:.1f}%</td></tr>"

    html = f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ background: #0e1117; color: white; font-family: sans-serif; text-align: center; }}
        .stat {{ display: inline-block; margin: 10px; padding: 15px; background: #1a1c24; border-radius: 10px; border: 1px solid #333; }}
        table {{ width: 100%; margin-top: 20px; border-collapse: collapse; }}
        td, th {{ padding: 10px; border-bottom: 1px solid #222; }}
    </style></head><body>
        <h2>Altcoin Engine v2</h2>
        <div class="stat"><div>EXIT PROB</div><div style="font-size:30px; color:#00ff88;">{exit_prob}%</div></div>
        <div class="stat"><div>REGIME</div><div style="font-size:20px;">{regime}</div></div>
        <br>
        <div class="stat">BTC Dom: {btc_d:.1f}%</div>
        <div class="stat">TOTAL3: ${total3:.2f}T</div>
        <table>
            <tr><th>COIN</th><th>PRICE</th><th>GOAL</th><th>24H</th></tr>
            {rows}
        </table>
    </body></html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    main()
