import json, urllib.request, time, os

# Datele tale din Excel
COINS = {
    "optimism": [4.8, 5.7], "notcoin": [0.028, 0.03], "arbitrum": [3.0, 3.6],
    "celestia": [12.0, 16.0], "jito-governance-token": [8.0, 8.0],
    "lido-dao": [5.6, 6.8], "cartesi": [0.2, 0.2], "immutable-x": [3.5, 4.5],
    "sonic-coin": [1.05, 1.0], "synthetix-network-token": [7.8, 9.5]
}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())

def main():
    # 1. Preluare date Crypto
    prices = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250")
    global_data = fetch("https://api.coingecko.com/api/v3/global")["data"]
    price_map = {c["id"]: c for c in prices}

    # 2. Indicatori Macro
    btc_d = global_data["market_cap_percentage"]["btc"]
    eth_d = global_data["market_cap_percentage"]["eth"]
    total3 = (global_data["total_market_cap"]["usd"] * (1 - (btc_d + eth_d) / 100)) / 1e12
    
    # M2 Supply (Simulat/Proxy - in mod real necesita API platit, folosim o valoare de referinta pt calculul de scor)
    m2_index = 1.05 # Trend pozitiv al lichiditatii

    # 3. Calcul Scor Exit (0-100)
    # Ponderea: 45% BTC Dom, 35% Total3, 20% Macro/M2
    norm_btc = max(0, min(1, (btc_d - 42) / (58 - 42)))
    exit_prob = round(((1 - norm_btc) * 0.45 + (total3 / 2.5) * 0.35 + (m2_index - 1) * 2 * 0.20) * 100, 1)
    
    regime = "🔴 SELL" if exit_prob > 75 else "🟡 PREPARE" if exit_prob > 50 else "🟢 HOLD"

    # 4. Procesare Monede
    results = []
    for cid, targets in COINS.items():
        if cid in price_map:
            p = price_map[cid]["current_price"]
            results.append({
                "coin": price_map[cid]["symbol"].upper(),
                "price": p,
                "target_apr": targets[0],
                "target_mai": targets[1],
                "progress": round((p / targets[0]) * 100, 1),
                "potential": round(targets[1] / p, 1) if p > 0 else 0
            })

    # 5. Salvare date
    output = {
        "timestamp": time.strftime("%H:%M"),
        "btc_d": round(btc_d, 1),
        "total3": round(total3, 2),
        "exit_probability": exit_prob,
        "regime": regime,
        "coins": results
    }
    
    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
