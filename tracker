import json, urllib.request, time, csv, io, math

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r: return r.read().decode()

def j(url): return json.loads(fetch(url))
def csv_last(url): return next(csv.DictReader(io.StringIO(fetch(url))))
def norm(x, a, b): return max(0, min(1, (x - a) / (b - a)))

def run_logic():
    # Date Live de pe Binance și CoinGecko
    prices = {i["symbol"]: float(i["price"]) for i in j("https://api.binance.com/api/v3/ticker/price")}
    g = j("https://api.coingecko.com/api/v3/global")["data"]
    m = j("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250")
    
    momentum = {i["symbol"].upper(): (i["price_change_percentage_24h"] or 0) for i in m if i["symbol"]}
    btc_d = g["market_cap_percentage"]["btc"]
    total3 = (g["total_market_cap"]["usd"] * (1 - (btc_d + g["market_cap_percentage"]["eth"]) / 100)) / 1e12
    
    # Date Macro
    sp = float(csv_last("https://stooq.pl/q/l/?s=^spx&f=sd2t2ohlcv&e=csv")["Close"])

    # Engine Logica pentru probabilitatea de Exit
    prob = round(((1 - norm(btc_d, 42, 58)) * 0.6 + norm(sp, 5000, 6500) * 0.4) * 100, 1)
    regime = "🔴 SELL" if prob > 75 else "🟡 PREPARE" if prob > 55 else "🟢 HOLD"

    # Activele tale țintă
    targets = {"OPUSDT":4.8,"NOTUSDT":0.03,"ARBUSDT":3.5,"TIAUSDT":12,"JTOUSDT":8,"LDOUSDT":6,"CTSIUSDT":0.2,"IMXUSDT":4,"SONICUSDT":1,"SNXUSDT":7.8}
    rows = []
    for c, t in targets.items():
        if c in prices:
            p = prices[c]; prog = (p/t)*100; mom = momentum.get(c.replace("USDT",""), 0)
            rows.append(f"<tr><td>{c.replace('USDT','')}</td><td>{p:.4f}</td><td>{t}</td><td>{prog:.1f}%</td><td>{mom:.1f}%</td></tr>")

    # Generare site HTML
    html = f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
    body {{ font-family: sans-serif; background: #0e1117; color: white; padding: 20px; text-align: center; }}
    .card {{ background: #1a1c24; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #333; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
    th, td {{ padding: 12px; border-bottom: 1px solid #222; }}
    th {{ color: #888; font-size: 12px; }}
    .status {{ font-size: 24px; font-weight: bold; color: #00ff88; }}
    </style></head><body>
    <div class="card"><div>EXIT PROBABILITY</div><div class="status">{prob}%</div><div>MODE: {regime}</div></div>
    <table><tr><th>COIN</th><th>PRICE</th><th>TARGET</th><th>PROG%</th><th>24H</th></tr>{''.join(rows)}</table>
    <p style='color: #444; font-size: 10px;'>Updated: {time.strftime('%H:%M:%S')}</p></body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__": run_logic()
