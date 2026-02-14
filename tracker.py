import json, urllib.request, time

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r: return r.read().decode()

def run_logic():
    try:
        # Luam pretul BTC de pe Binance
        data = json.loads(fetch("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"))
        price = float(data['price'])
        
        # Generam pagina web
        html = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Crypto Tracker Live</title>
            <style>
                body {{ background: #0e1117; color: white; font-family: sans-serif; text-align: center; padding: 50px 20px; }}
                .card {{ background: #1a1c24; padding: 30px; border-radius: 20px; border: 1px solid #333; display: inline-block; min-width: 300px; }}
                .price {{ font-size: 48px; color: #00ff88; font-weight: bold; margin: 20px 0; }}
                .label {{ color: #888; text-transform: uppercase; letter-spacing: 2px; }}
                .footer {{ margin-top: 30px; color: #444; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="label">Bitcoin Price</div>
                <div class="price">${price:,.2f}</div>
                <div style="color: #00ff88;">● Live Dashboard</div>
            </div>
            <div class="footer">Ultima actualizare: {time.strftime('%H:%M:%S')}</div>
        </body>
        </html>
        """
        
        # Salvam fisierul
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Succes: index.html a fost generat!")
        
    except Exception as e:
        print(f"Eroare: {str(e)}")
        exit(1)

if __name__ == "__main__":
    run_logic()
