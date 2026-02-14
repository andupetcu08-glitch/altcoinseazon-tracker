import time
try:
    html = f"""
    <html><body style="background: #0e1117; color: white; text-align: center; font-family: sans-serif;">
        <h1>Dashboard Activ ✅</h1>
        <p>Update: {time.strftime('%H:%M:%S')}</p>
        <p>Daca vezi asta, totul functioneaza perfect!</p>
    </body></html>
    """
    with open("index.html", "w") as f:
        f.write(html)
    print("Succes!")
except Exception as e:
    print(f"Eroare: {e}")
import json, urllib.request, time

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r: return r.read().decode()

def run_logic():
    try:
        # Luam pretul BTC ca test
        data = json.loads(fetch("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"))
        price = float(data['price'])
        
        # Generam un HTML simplu si curat
        html = f"""
        <html>
        <head><title>Crypto Tracker</title></head>
        <body style="background: #0e1117; color: white; font-family: sans-serif; text-align: center; padding: 50px;">
            <div style="padding: 20px; border: 1px solid #333; border-radius: 10px; display: inline-block;">
                <h1>BTC Price Live</h1>
                <p style="font-size: 48px; color: #00ff88;">${price:,.2f}</p>
                <p style="color: #666;">Ultima actualizare: {time.strftime('%H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Succes: index.html a fost creat!")
    except Exception as e:
        print(f"Eroare: {str(e)}")
        exit(1)

if __name__ == "__main__":
    run_logic()
