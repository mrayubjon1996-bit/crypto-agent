from flask import Flask, render_template_string, jsonify
import requests
import os

app = Flask(__name__)

def get_crypto_data(coin):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin.upper()}USDT"
    try:
        data = requests.get(url, timeout=5).json()
        p = float(data['lastPrice'])
        return {
            "price": "{:.8f}".format(p).rstrip('0').rstrip('.'),
            "symbol": coin.upper()
        }
    except: return None

@app.route('/')
def index():
    return "<h1>FORGE AGENT LIVE</h1>"

@app.route('/data/<coin>')
def data(coin):
    res = get_crypto_data(coin)
    return jsonify(res) if res else (jsonify({"error": "not found"}), 404)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
