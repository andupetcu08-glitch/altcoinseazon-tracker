import json
import urllib.request
import time

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode()

def run_logic():
    try:
        # Folosim CoinGecko in loc de Binance pentru a evita Error 451
        raw_data = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = json.loads(raw_data)
        price = float(data['bitcoin']['usd'])
        
        html_content = f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="background: #0e1117; color: white; font-family: sans-serif; text-align: center; padding: 50px 20px;">
            <div style="background: #1a1c24; padding: 30px; border-radius: 20px; border: 1px solid #333; display: inline-block;">
                <h1 style="color: #888; font-size: 18px;">Bitcoin Price (via CoinGecko)</h1>
                <div style="font-size: 48px; color: #00ff88; font-weight: bold; margin: 20px 0;">${price:,.2f}</div>
                <p style="color: #444; font-size: 12px;">Update: {time.strftime('%H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Succes: index.html creat folosind date CoinGecko.")
    except Exception as e:
        print(f"Eroare: {e}")
        raise e

if __name__ == "__main__":
    run_logic()
