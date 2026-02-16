import json, urllib.request

INVEST_EUR = 101235.0 

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"Eroare API la {url}: {e}")
        return None

def main():
    # Preluăm datele esențiale
    p_data = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,tether,optimism,notcoin,arbitrum,celestia,jito-governance-token,lido-dao,cartesi,immutable-x,sonic-3,synthetix-network-token")
    g_data = fetch("https://api.coingecko.com/api/v3/global")
    f_data = fetch("https://api.alternative.me/fng/")

    if not p_data or not g_data:
        print("Eroare critică: Nu s-au putut prelua datele de piață.")
        return

    p_map = {c["id"]: c for c in p_data}
    total_mcap = g_data["data"]["total_market_cap"]["usd"]

    # 1. BTC.D Live (Calculat manual pentru precizie)
    btc_mcap = p_map.get("bitcoin", {}).get("market_cap", 0)
    btcd = round((btc_mcap / total_mcap) * 100, 2)

    # 2. ETH/BTC
    btc_p = p_map.get("bitcoin", {}).get("current_price", 1)
    eth_p = p_map.get("ethereum", {}).get("current_price", 0)
    ethbtc = round(eth_p / btc_p, 4)

    # 3. USDT.D Live
    usdt_mcap = p_map.get("tether", {}).get("market_cap", 0)
    usdtd = round((usdt_mcap / total_mcap) * 100, 2)

    # 4. Rotation Score (Legat de target-ul de 70%)
    # Daca BTCD scade spre 46%, scorul trebuie sa urce spre 70-100%
    fng_val = int(f_data["data"][0]["value"]) if f_data else 20
    rot_score = round(max(0, min(100, (60 - btcd) * 4 + (fng_val / 2))), 0)

    # 5. Portofoliu & SNX Fix
    total_usd = 0
    coins_out = []
    # (Lista ta de monede ramane neschimbata aici, folosind entry-urile tale)
    # ... logică calcul monede ...
    # SNX fix: 0.294 daca API-ul livreaza gresit

    port_eur = total_usd * 0.92 # Conversie USD -> EUR
    multiplier = round(port_eur / INVEST_EUR, 2)

    # Creăm structura JSON curată pentru a evita "undefined"
    output = {
        "port_eur": round(port_eur, 0),
        "invest_eur": INVEST_EUR,
        "mult": f"{multiplier}x", # String cu "x" inclus pentru afisaj
        "rotation": int(rot_score),
        "btcd": f"{btcd}%",
        "ethbtc": ethbtc,
        "usdtd": f"{usdtd}%",
        "fng": f"{fng_val} ({f_data['data'][0]['value_classification'] if f_data else 'N/A'})",
        "vix": 20.54, # De automatizat prin Yahoo in pasul urmator daca e stabil
        "dxy": 96.99,
        "m2": "22.4T",
        "coins": coins_out # Lista cu datele monedelor
    }

    with open("data.json", "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    main()
