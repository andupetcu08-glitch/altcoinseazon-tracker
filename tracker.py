import json, urllib.request, math

INVESTITIE_TOTALA_USD = 120456.247

PORTFOLIO = {
    "optimism": {"q": 6400, "entry": 0.773, "apr": 4.8, "mai": 5.20, "fib": 5.95},
    "notcoin": {"q": 1297106.88, "entry": 0.001291, "apr": 0.028, "mai": 0.028, "fib": 0.034},
    "arbitrum": {"q": 14326.44, "entry": 1.134, "apr": 3.0, "mai": 3.40, "fib": 3.82},
    "celestia": {"q": 4504.47, "entry": 5.911, "apr": 12.0, "mai": 15.00, "fib": 18.50},
    "jito-governance-token": {"q": 7366.42, "entry": 2.711, "apr": 8.0, "mai": 8.20, "fib": 9.20},
    "lido-dao": {"q": 9296.65, "entry": 1.121, "apr": 5.6, "mai": 6.20, "fib": 6.90},
    "cartesi": {"q": 49080, "entry": 0.19076, "apr": 0.2, "mai": 0.2, "fib": 0.24},
    "immutable-x": {"q": 1551.82, "entry": 3.4205, "apr": 3.5, "mai": 4.3, "fib": 4.85},
    "sonic-3": {"q": 13449.38, "entry": 0.81633, "apr": 1.05, "mai": 1.35, "fib": 1.55},
    "synthetix-network-token": {"q": 20073.76, "entry": 0.8773, "apr": 7.8, "mai": 9.3, "fib": 10.20}
}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def rotation_score(btc_d, eth_btc, fng, usdt_d):
    score = 10
    score += 25 if btc_d < 50 else 15 if btc_d <= 55 else 5
    score += 25 if eth_btc > 0.05 else 15 if eth_btc >= 0.04 else 5
    score += 20 if fng > 70 else 10 if fng >= 40 else 5
    score += 20 if usdt_d < 5.5 else 10 if usdt_d <= 7.5 else 0
    return min(100, score)

def exhaustion(progress, momentum):
    return round(min(100, progress * 0.7 + abs(momentum) * 2),1)

def detect_blowoff(momentum, progress):
    return momentum > 25 and progress > 80

def detect_divergence(momentum, progress):
    return momentum < 0 and progress > 70

def main():
    ids = list(PORTFOLIO.keys()) + ["bitcoin","ethereum"]
    market = fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(ids)}")
    global_api = fetch("https://api.coingecko.com/api/v3/global")
    fng = fetch("https://api.alternative.me/fng/")["data"][0]["value"]

    price_map = {c["id"]:c for c in market}
    btc = price_map["bitcoin"]["current_price"]
    eth = price_map["ethereum"]["current_price"]

    btc_d = round(global_api["data"]["market_cap_percentage"]["btc"],1)
    eth_btc = round(eth/btc,4)

    usdt_d = 7.5

    rot = rotation_score(btc_d, eth_btc, int(fng), usdt_d)

    coins=[]
    total=0
    total_apr=0
    total_fib=0

    green=0
    for cid,d in PORTFOLIO.items():
        c=price_map.get(cid,{})
        p=c.get("current_price",0)
        mom=c.get("price_change_percentage_24h",0)

        total+=p*d["q"]
        total_apr+=d["apr"]*d["q"]
        total_fib+=d["fib"]*d["q"]

        prog=((p-d["entry"])/(d["fib"]-d["entry"]))*100 if d["fib"]>d["entry"] else 0
        prog=max(0,min(100,prog))

        if mom>0: green+=1

        coins.append({
            "symbol":cid.upper().replace("-NETWORK-TOKEN","").replace("-GOVERNANCE-TOKEN","").replace("-3",""),
            "price":round(p,4),
            "change":round(mom,2),
            "trend":"up" if mom>=0 else "down",
            "q":d["q"],
            "entry":d["entry"],
            "apr":d["apr"],
            "mai":d["mai"],
            "fib":d["fib"],
            "x_apr":round(d["apr"]/d["entry"],2),
            "x_mai":round(d["mai"]/d["entry"],2),
            "progres":round(prog,1),
            "exhaustion":exhaustion(prog,mom),
            "blowoff":detect_blowoff(mom,prog),
            "divergence":detect_divergence(mom,prog),
            "heat":round((mom+10)/40,2)
        })

    breadth=round(green/len(coins)*100,1)

    usd_eur=0.92

    with open("data.json","w") as f:
        json.dump({
            "btc_d":btc_d,
            "eth_btc":eth_btc,
            "rotation_score":rot,
            "breadth":breadth,
            "portfolio_eur":round(total*usd_eur,0),
            "profit_range":f"€{round((total_apr-INVESTITIE_TOTALA_USD)*usd_eur):,} - €{round((total_fib-INVESTITIE_TOTALA_USD)*usd_eur):,}",
            "investit_eur":round(INVESTITIE_TOTALA_USD*usd_eur,0),
            "multiplier":round(total/INVESTITIE_TOTALA_USD,2),
            "coins":coins,
            "vix":13.8,
            "dxy":101,
            "total3":"0.98T",
            "fng":fng,
            "usdt_d":usdt_d,
            "urpd":"84.2%",
            "m2":"21.2T"
        },f)

if __name__=="__main__":
    main()
