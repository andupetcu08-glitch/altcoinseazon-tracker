import json
import urllib.request
import time

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode()

def run_logic():
    try:
        # Preluare preț
        raw_data = fetch("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        data = json.loads(raw_data)
        price = float(data['price'])
        
        # Generare HTML
        html_content = f"""
        <html>
        <body style="background: #0e1117; color: white; font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #888;">Bitcoin Price Live</h1>
            <div style="font-size: 48px; color: #00ff88; font-weight: bold;">${price:,.2f}</div>
            <p style="color: #444;">Ultima actualizare: {time.strftime('%H:%M:%S')}</p>
        </body>
        </html>
        """
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Succes: index.html creat.")
    except Exception as e:
        print(f"Eroare: {e}")
        raise e

if __name__ == "__main__":
    run_logic()
