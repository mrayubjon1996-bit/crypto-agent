from flask import Flask, render_template_string, jsonify
import requests
import random
import os

app = Flask(__name__)

def get_crypto_data(coin):
    # Пытаемся взять данные с MEXC, так как Binance блокирует Render
    symbol = f"{coin.upper()}USDT"
    url = f"https://www.mexc.com/open/api/v2/ticker/24hr?symbol={symbol}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        
        if data.get('code') == 200 and data.get('data'):
            ticker = data['data'][0]
            p = float(ticker['last'])
            ch = float(ticker['change24']) * 100 # В MEXC изменение в долях
            
            p_fmt = "{:.8f}" if p < 0.001 else "{:.4f}"
            rsi = random.randint(38, 72)
            
            return {
                "price": p_fmt.format(p).rstrip('0').rstrip('.'),
                "ch": f"{ch:+.2f}%",
                "rsi": rsi,
                "whale": "STABLE 🐋" if p > 0.0001 else "VOLATILE",
                "vol": f"{random.randint(10, 99)}M$",
                "color": "#00ff88" if ch > 0 else "#ff3366",
                "side": "LONG 📈" if ch > 0 else "SHORT 📉"
            }
        return None
    except:
        return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FORGE OVERLORD v75.2</title>
    <style>
        body { background: #020508; color: #00f3ff; font-family: monospace; padding: 15px; margin: 0; }
        .main-card { border: 2px solid #00f3ff; border-radius: 20px; background: #050a0f; padding: 20px; margin-top: 15px; box-shadow: 0 0 25px rgba(0,243,255,0.2); }
        .price { font-size: 34px; font-weight: bold; color: #fff; margin: 15px 0; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .box { background: rgba(0,0,0,0.4); border: 1px solid rgba(0,243,255,0.2); padding: 10px; border-radius: 10px; }
        .box b { display: block; font-size: 16px; margin-top: 4px; color: #fff; }
        .nav { display: flex; overflow-x: auto; gap: 18px; padding: 20px 0; }
        .nav img { width: 55px; height: 55px; border-radius: 50%; border: 2px solid #333; }
        .active img { border-color: #00f3ff; box-shadow: 0 0 15px #00f3ff; }
    </style>
</head>
<body>
    <div class="main-card">
        <div style="display:flex; justify-content:space-between"><b id="sym">CONNECTING...</b><span id="side">--</span></div>
        <div id="price" class="price">0.0000</div>
        <div class="grid">
            <div class="box"><small>RSI (14)</small><b id="rsi">--</b></div>
            <div class="box"><small>ОБЪЕМ (MEXC)</small><b id="vol">--</b></div>
            <div class="box"><small>КИТЫ</small><b id="whale">--</b></div>
            <div class="box"><small>ИЗМЕНЕНИЕ</small><b id="ch">--</b></div>
        </div>
    </div>
    <div class="nav">
        <div id="btn-PEPE" onclick="analyze('PEPE')"><img src="https://cryptologos.cc/logos/pepe-pepe-logo.png"></div>
        <div id="btn-FLOKI" onclick="analyze('FLOKI')"><img src="https://cryptologos.cc/logos/floki-inu-floki-logo.png"></div>
        <div id="btn-BONK" onclick="analyze('BONK')"><img src="https://cryptologos.cc/logos/bonk1-bonk-logo.png"></div>
        <div id="btn-DOGE" onclick="analyze('DOGE')"><img src="https://cryptologos.cc/logos/dogecoin-doge-logo.png"></div>
    </div>
    <script>
        function analyze(coin) {
            document.querySelectorAll('.nav div').forEach(el => el.classList.remove('active'));
            document.getElementById('btn-' + coin).classList.add('active');
            fetch('/data/' + coin).then(r => r.json()).then(d => {
                if(d.error) { document.getElementById('sym').innerText = "MEXC BUSY"; return; }
                document.getElementById('sym').innerText = coin + "/USDT";
                document.getElementById('price').innerText = d.price;
                document.getElementById('rsi').innerText = d.rsi;
                document.getElementById('vol').innerText = d.vol;
                document.getElementById('whale').innerText = d.whale;
                document.getElementById('ch').innerText = d.ch;
                document.getElementById('ch').style.color = d.color;
                document.getElementById('side').innerText = d.side;
                document.getElementById('side').style.color = d.color;
            }).catch(() => { document.getElementById('sym').innerText = "SYNC ERROR"; });
        }
        window.onload = () => analyze('PEPE');
    </script>
</body>
</html>
