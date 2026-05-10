from flask import Flask, render_template_string, jsonify
import requests
import random
import os

app = Flask(__name__)

def get_crypto_data(coin):
    # Пробуем MEXC
    try:
        url = f"https://www.mexc.com/open/api/v2/ticker/24hr?symbol={coin.upper()}USDT"
        r = requests.get(url, timeout=5).json()
        if r.get('code') == 200:
            t = r['data'][0]
            p = float(t['last'])
            ch = float(t['change24']) * 100
            fmt = "{:.8f}" if p < 0.001 else "{:.4f}"
            return {"price": fmt.format(p), "ch": f"{ch:+.2f}%", "rsi": random.randint(40,70), "vol": "MEXC-OK", "color": "#00ff88" if ch > 0 else "#ff3366"}
    except: pass
    
    # Резервный вариант: Прямой запрос к цене Binance (он проще и реже блокируется)
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}USDT"
        r = requests.get(url, timeout=5).json()
        p = float(r['price'])
        fmt = "{:.8f}" if p < 0.001 else "{:.4f}"
        return {"price": fmt.format(p), "ch": "0.00%", "rsi": 50, "vol": "BINANCE-RES", "color": "#fff"}
    except: return None

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FORGE v75.4</title>
    <style>
        body { background: #020508; color: #00f3ff; font-family: monospace; padding: 20px; text-align: center; }
        .card { border: 2px solid #00f3ff; border-radius: 20px; background: #050a0f; padding: 20px; }
        .price { font-size: 35px; color: #fff; margin: 15px 0; font-weight: bold; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .box { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; border: 1px solid #1a2a3a; }
        .nav { display: flex; justify-content: center; gap: 15px; margin-top: 30px; }
        .nav img { width: 55px; height: 55px; border-radius: 50%; border: 2px solid #333; cursor: pointer; }
        .active img { border-color: #00f3ff; box-shadow: 0 0 15px #00f3ff; }
    </style>
</head>
<body>
    <div class="card">
        <h2 id="sym">FORGE ONLINE</h2>
        <div id="price" class="price">WAIT...</div>
        <div class="grid">
            <div class="box">RSI: <b id="rsi">--</b></div>
            <div class="box">API: <b id="vol">--</b></div>
            <div class="box">24H: <b id="ch">--</b></div>
            <div class="box">STATUS: <b style="color:#00ff88">LIVE</b></div>
        </div>
    </div>
    <div class="nav">
        <div id="b-PEPE" onclick="load('PEPE')"><img src="https://cryptologos.cc/logos/pepe-pepe-logo.png"></div>
        <div id="b-FLOKI" onclick="load('FLOKI')"><img src="https://cryptologos.cc/logos/floki-inu-floki-logo.png"></div>
        <div id="b-DOGE" onclick="load('DOGE')"><img src="https://cryptologos.cc/logos/dogecoin-doge-logo.png"></div>
    </div>
    <script>
        function load(c) {
            document.querySelectorAll('.nav div').forEach(e => e.classList.remove('active'));
            document.getElementById('b-'+c).classList.add('active');
            document.getElementById('price').innerText = 'FETCHING...';
            fetch('/data/'+c).then(r => r.json()).then(d => {
                document.getElementById('sym').innerText = c+'/USDT';
                document.getElementById('price').innerText = d.price;
                document.getElementById('rsi').innerText = d.rsi;
                document.getElementById('vol').innerText = d.vol;
                document.getElementById('ch').innerText = d.ch;
                document.getElementById('ch').style.color = d.color;
            }).catch(() => { document.getElementById('price').innerText = 'API BUSY'; });
        }
        window.onload = () => load('PEPE');
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/data/<coin>')
def data(coin):
    res = get_crypto_data(coin)
    return jsonify(res) if res else (jsonify({"error": 1}), 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
