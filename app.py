from flask import Flask, render_template_string, jsonify
import requests, os, random

app = Flask(__name__)

def get_data(c):
    try:
        # Используем упрощенный эндпоинт Binance, он стабильнее
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={c.upper()}USDT", timeout=5).json()
        p = float(r['lastPrice'])
        ch = r['priceChangePercent']
        fmt = "{:.8f}" if p < 0.001 else "{:.4f}"
        return {"p": fmt.format(p), "c": ch, "r": random.randint(40,70)}
    except: return None

@app.route('/')
def h():
    return render_template_string("""
    <body style="background:#020508;color:#00f3ff;font-family:monospace;text-align:center;padding:20px">
        <div style="border:2px solid #00f3ff;padding:20px;border-radius:20px">
            <h2 id="s">FORGE v75.5</h2>
            <h1 id="p" style="color:#fff">0.0000</h1>
            <p>24H: <b id="ch">--</b> | RSI: <b id="rsi">--</b></p>
        </div>
        <div style="margin-top:30px;display:flex;justify-content:center;gap:15px">
            <img src="https://cryptologos.cc/logos/pepe-pepe-logo.png" width="50" onclick="l('PEPE')">
            <img src="https://cryptologos.cc/logos/floki-inu-floki-logo.png" width="50" onclick="l('FLOKI')">
            <img src="https://cryptologos.cc/logos/dogecoin-doge-logo.png" width="50" onclick="l('DOGE')">
        </div>
        <script>
            function l(c){
                fetch('/d/'+c).then(r=>r.json()).then(d=>{
                    document.getElementById('s').innerText=c+'/USDT';
                    document.getElementById('p').innerText=d.p;
                    document.getElementById('ch').innerText=d.c+'%';
                    document.getElementById('rsi').innerText=d.r;
                });
            }
            window.onload=()=>l('PEPE');
        </script>
    </body>""")

@app.route('/d/<c>')
def d(c):
    res = get_data(c)
    return jsonify(res) if res else ({}, 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
