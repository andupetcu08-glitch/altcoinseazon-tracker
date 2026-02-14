import requests, json, time, os

COINS = {
 "optimism":4.8,
 "notcoin":0.03,
 "arbitrum":3.5,
 "celestia":12,
 "jito-governance-token":8,
 "lido-dao":6,
 "cartesi":0.2,
 "immutable-x":4,
 "sonic-coin":1,
 "synthetix-network-token":7.8
}

HISTORY_FILE="history.json"

def clamp(x): return max(0,min(1,x))
def norm(x,a,b): return clamp((x-a)/(b-a))

def fetch(url):
    return requests.get(url,timeout=15).json()

def load_history():
    if os.path.exists(HISTORY_FILE):
        return json.load(open(HISTORY_FILE))
    return []

def save_history(h):
    json.dump(h[-300:],open(HISTORY_FILE,"w"),indent=2)

def main():
    prices=fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250")
    global_data=fetch("https://api.coingecko.com/api/v3/global")["data"]

    price_map={c["id"]:c for c in prices}

    btc_d=global_data["market_cap_percentage"]["btc"]
    eth_d=global_data["market_cap_percentage"]["eth"]
    total3=(global_data["total_market_cap"]["usd"]*(1-(btc_d+eth_d)/100))/1e12

    history=load_history()
    history.append({
        "time":time.time(),
        "btc_d":btc_d,
        "total3":total3
    })
    save_history(history)

    if len(history)>5:
        rot=(history[-1]["total3"]-history[-5]["total3"])/history[-5]["total3"]*100
        btc_trend=history[-5]["btc_d"]-btc_d
    else:
        rot=0
        btc_trend=0

    crypto_score=(1-norm(btc_d,42,58))*0.45 + norm(total3,0.4,2)*0.35 + norm(rot,0,20)*0.2
    exit_prob=round(crypto_score*100,1)

    regime="SELL" if exit_prob>75 else "PREPARE" if exit_prob>50 else "HOLD"

    results=[]
    for coin,target in COINS.items():
        if coin in price_map:
            p=price_map[coin]["current_price"]
            mom=price_map[coin]["price_change_percentage_24h"] or 0
            progress=round(p/target*100,1)
            upside=round((target/p-1)*100,1)
            alpha=round(mom*0.6+(100-progress)*0.4,1)

            results.append({
                "coin":coin.upper(),
                "price":p,
                "target":target,
                "progress":progress,
                "upside":upside,
                "momentum":mom,
                "alpha":alpha
            })

    results=sorted(results,key=lambda x:x["alpha"],reverse=True)

    out={
        "timestamp":time.strftime("%Y-%m-%d %H:%M"),
        "btc_d":round(btc_d,2),
        "btc_trend":round(btc_trend,3),
        "total3":round(total3,3),
        "rotation_change":round(rot,2),
        "exit_probability":exit_prob,
        "regime":regime,
        "coins":results
    }

    json.dump(out,open("data.json","w"),indent=2)

if _name=="main_":
    main()
