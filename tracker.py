import requests, json, time, math

PORTFOLIO = {
 "optimism":{"entry":4.6,"apr":4.8,"mai":5.2,"fib":6.0,"q":6400},
 "notcoin":{"entry":0.03,"apr":0.035,"mai":0.045,"fib":0.06,"q":1297036},
 "arbitrum":{"entry":3.3,"apr":3.8,"mai":4.4,"fib":5.2,"q":3500},
 "celestia":{"entry":15.5,"apr":12,"mai":15,"fib":20,"q":4504},
 "jito-governance-token":{"entry":7.5,"apr":8,"mai":10,"fib":13,"q":7366},
 "lido-dao":{"entry":7.8,"apr":6,"mai":8,"fib":11,"q":9296},
 "cartesi":{"entry":0.20,"apr":0.22,"mai":0.30,"fib":0.45,"q":49080},
 "immutable-x":{"entry":3.5,"apr":4,"mai":5,"fib":7,"q":2500},
 "sonic-3":{"entry":1,"apr":1.2,"mai":1.6,"fib":2.4,"q":13449},
 "synthetix-network-token":{"entry":7.8,"apr":7.5,"mai":9.5,"fib":13,"q":20073}
}

def norm(x,a,b):
    return max(0,min(1,(x-a)/(b-a)))

def exhaustion(progress,momentum):
    return min(100, progress*0.7 + max(0,momentum)*1.5)

def detect_blowoff(momentum,progress):
    return momentum>15 and progress>70

def detect_divergence(momentum,progress):
    return progress>65 and momentum<0

def fetch_prices(ids):
    url="https://api.coingecko.com/api/v3/coins/markets"
    r=requests.get(url,params={
        "vs_currency":"usd",
        "ids":",".join(ids),
        "price_change_percentage":"24h"
    },timeout=20)
    return r.json()

def main():
    ids=list(PORTFOLIO.keys())
    data=fetch_prices(ids)
    price_map={c["id"]:c for c in data}

    coins=[]
    green=0
    rotation_components=[]

    for cid,d in PORTFOLIO.items():
        c=price_map.get(cid,{})
        p=float(c.get("current_price") or 0)
        mom=float(c.get("price_change_percentage_24h") or 0)

        if d["fib"]>d["entry"]:
            progress=((p-d["entry"])/(d["fib"]-d["entry"]))*100
        else:
            progress=0

        progress=max(0,min(100,progress))

        if mom>0: green+=1

        ex=exhaustion(progress,mom)

        coins.append({
            "symbol":cid.upper().replace("-NETWORK-TOKEN","").replace("-GOVERNANCE-TOKEN","").replace("-3",""),
            "price":round(p,5),
            "change":round(mom,2),
            "trend":"up" if mom>=0 else "down",
            "entry":d["entry"],
            "apr":d["apr"],
            "mai":d["mai"],
            "fib":d["fib"],
            "progress":round(progress,1),
            "exhaustion":round(ex,1),
            "blowoff":detect_blowoff(mom,progress),
            "divergence":detect_divergence(mom,progress),
            "heat":round(norm(mom,-15,25),2)
        })

        rotation_components.append(
            norm(progress,0,100)*0.6 + norm(mom,-10,20)*0.4
        )

    rotation_score=round(sum(rotation_components)/len(rotation_components)*100,1)
    breadth=round(green/len(coins)*100,1)

    if rotation_score<50:
        regime="HOLD"
    elif rotation_score<70:
        regime="PREPARE"
    else:
        regime="SELL"

    out={
        "rotation":rotation_score,
        "breadth":breadth,
        "regime":regime,
        "coins":coins,
        "updated":time.time()
    }

    with open("data.json","w") as f:
        json.dump(out,f,indent=2)

if __name__=="__main__":
    main()
