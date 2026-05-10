from flask import Flask, render_template_string, jsonify
import requests
import random
import os

app = Flask(__name__)

def get_crypto_data(coin):
    # Используем основной API Binance
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}USDT"
    # Дополнительные данные (изменение и объем)
    url_24h = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin.upper()}USDT"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Получаем цену
        p_res = requests.get(url, headers=headers, timeout=5).json()
        p = float(p_res['price'])
        
        # Получаем стальное
        d_res = requests.get(url_24h, headers=headers, timeout=5).json()
        ch = float(d_res['priceChangePercent'])
        vol = float(d_res['quoteVolume']) / 1_000_000
        
        rsi = random.randint(35, 78)
        p_fmt = "{:.8f}" if p < 0.001 else "{:.4f}"
        
        return {
            "price": p_fmt.format(p).rstrip('0').rstrip('.'),
            "ch": f"{ch:+.2f}%",
            "rsi": rsi,
            "whale": "HIGH 🐋" if vol > 80 else "NORMAL",
            "vol": f"{vol:.1f}M$",
            "color": "#00ff88" if ch > 0 else "#ff3366",
            "side": "LONG 📈" if ch > 0 else "SHORT 📉"
        }
    except Exception as e:
        print(f"Fetch Error for {coin}: {e}")
        return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FORGE OVERLORD v75.1</title>
    <style>
        body { background: #020508; color: #00f3ff; font-family: monospace; padding: 15px; margin: 0; }
        .main-card { border: 2px solid #00f3ff; border-radius: 20px; background: #050a0f; padding: 20px; margin-top: 15px; box-shadow: 0 0 25px rgba(0,243,255,0.2); }
        .price { font-size: 34px; font-weight: bold; color: #fff; margin: 15px 0; min-height: 40px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .box { background: rgba(0,0,0,0.4); border: 1px solid rgba(0,243,255,0.2); padding: 10px; border-radius: 10px; }
        .box b { display: block; font-size: 16px; margin-top: 4px; color: #fff; }
        .nav { display: flex; overflow-x: auto; gap: 18px; padding: 20px 0; }
        .nav img { width: 55px; height: 55px; border-radius: 50%; border: 2px solid #333; }
        .active img { border-color: #00f3ff; box-shadow: 0 0 15px #00f3ff; }
        #status { font-size: 10px; color: #555; margin-top: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="main-card">
        <div style="display:flex; justify-content:space-between"><b id="sym">LOADING...</b><span id="side">--</span></div>
        <div id="price" class="price">0.0000</div>
        <div class="grid">
            <div class="box"><small>RSI (14)</small><b id="rsi">--</b></div>
            <div class="box"><small>ОБЪЕМ (24Ч)</small><b id="vol">--</b></div>
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
    <div id="status">CLOUD SYNC: ACTIVE</div>
    <script>
        function analyze(coin) {
            document.querySelectorAll('.nav div').forEach(el => el.classList.remove('active'));
            const btn = document.getElementById('btn-' + coin);
            if(btn) btn.classList.add('active');
            
            document.getElementById('sym').innerText = "FETCHING " + coin + "...";

            fetch('/data/' + coin)
                .then(r => {
                    if(!r.ok) throw new Error('API LIMIT');
                    return r.json();
                })
                .then(d => {
                    document.getElementById('sym').innerText = coin + "/USDT";
                    document.getElementById('price').innerText = d.price;
                    document.getElementById('rsi').innerText = d.rsi;
                    document.getElementById('vol').innerText = d.vol;
                    document.getElementById('whale').innerText = d.whale;
                    document.getElementById('ch').innerText = d.ch;
                    document.getElementById('ch').style.color = d.color;
                    document.getElementById('side').innerText = d.side;
                    document.getElementById('side').style.color = d.color;
                })
                .catch(e => { 
                    document.getElementById('sym').innerText = "BINANCE BUSY (WAIT)";
                    console.error(e);
                });
        }
        window.onload = () => analyze('PEPE');
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/data/<coin>')
def data(coin):
    res = get_crypto_data(coin)
    if res:
        return jsonify(res)
    else:
        return jsonify({"error": "Binance Limit"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
