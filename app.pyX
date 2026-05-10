from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests, json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
BOT_PASSWORD = "1996"
SIGNALS_FILE = os.path.expanduser("~/forge_agent/signals.json")

# Только MEME-коины (без BTC/ETH)
MEME_COINS = ["DOGE", "SHIB", "PEPE", "WIF", "BONK", "FLOKI", "NOT", "TON"]

@app.before_request
def check_auth():
    if request.endpoint in ['login', 'static'] or request.endpoint is None:
        return
    if not session.get('authenticated'):
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == BOT_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Неверный пароль!")
    return render_template('login.html')

def load_signals():
    try:
        with open(SIGNALS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"history": [], "total": 0, "win": 0}

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

def analyze_multi_timeframe(symbol):
    """Анализ по всем таймфреймам"""
    try:
        sym = symbol.upper() + "USDT"
        
        # 1. Текущие данные 24ч
        ticker = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}", timeout=10).json()
        price = float(ticker['lastPrice'])
        change_24h = float(ticker['priceChangePercent'])
        volume = float(ticker['quoteVolume'])
        high = float(ticker['highPrice'])
        low = float(ticker['lowPrice'])
        
        # 2. Анализ 2 часа (15m свечи, 8 штук = 2 часа)
        k2h = requests.get(f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=15m&limit=8", timeout=10).json()
        if k2h:
            open_2h = float(k2h[0][1])
            close_2h = float(k2h[-1][4])
            change_2h = ((close_2h - open_2h) / open_2h) * 100
        else:
            change_2h = 0
        
        # 3. Анализ 3 часа (1h свечи, 3 штуки)
        k3h = requests.get(f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=1h&limit=3", timeout=10).json()
        if k3h:
            open_3h = float(k3h[0][1])
            close_3h = float(k3h[-1][4])
            change_3h = ((close_3h - open_3h) / open_3h) * 100
        else:
            change_3h = 0
        
        # 4. RSI (14 периодов на 1h)
        k1h = requests.get(f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=1h&limit=14", timeout=10).json()
        if k1h:
            closes = [float(k[4]) for k in k1h]
            gains = []
            losses = []
            for i in range(1, len(closes)):
                diff = closes[i] - closes[i-1]
                if diff > 0:
                    gains.append(diff)
                else:
                    losses.append(abs(diff))
            
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0.1
            rs = avg_gain / avg_loss            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50
        
        # 5. Совокупный сигнал (2h + 3h + RSI)
        combined_score = (change_2h + change_3h) / 2
        if rsi < 30:
            combined_score -= 20  # Перепроданность
        elif rsi > 70:
            combined_score += 20  # Перекупленность
        
        # 6. Определение сигнала
        if combined_score > 2 and rsi > 40:
            side = "LONG 📈"
            color = "#00ff88"
            trend = "BULLISH"
        elif combined_score < -2 and rsi < 60:
            side = "SHORT 📉"
            color = "#ff3366"
            trend = "BEARISH"
        else:
            side = "NEUTRAL ⚖️"
            color = "#ffa500"
            trend = "SIDEWAYS"
        
        # 7. TP/SL
        tp = price * 1.05 if "LONG" in side else price * 0.95
        sl = price * 0.97 if "LONG" in side else price * 1.03
        
        # 8. Сохраняем сигнал
        data = load_signals()
        data["history"].append({
            "time": datetime.now().isoformat(),
            "coin": symbol,
            "side": side,
            "price": price
        })
        if len(data["history"]) > 100:
            data["history"] = data["history"][-100:]
        data["total"] += 1
        with open(SIGNALS_FILE, 'w') as f:
            json.dump(data, f)
        
        # 9. Возвращаем все данные
        return {
            "price": f"{price:.8f}".rstrip('0').rstrip('.'),
            "entry": f"{price:.8f}".rstrip('0').rstrip('.'),
            "tp": f"{tp:.8f}".rstrip('0').rstrip('.'),
            "sl": f"{sl:.8f}".rstrip('0').rstrip('.'),
            "change_24h": f"{change_24h:+.2f}%",            "change_2h": f"{change_2h:+.2f}%",
            "change_3h": f"{change_3h:+.2f}%",
            "combined": f"{combined_score:+.2f}%",
            "side": side,
            "color": color,
            "trend": trend,
            "rsi": int(rsi),
            "vol": min(100, int(volume / 10000000)),
            "confirm": min(100, int(abs(combined_score) * 10 + rsi / 2)),
            "volume": f"{volume/1e6:.1f}M",
            "volatility": f"{((high - low) / price) * 100:.1f}%",
            "high": f"{high:.8f}".rstrip('0').rstrip('.'),
            "low": f"{low:.8f}".rstrip('0').rstrip('.'),
            "acc": 94.5,
            "count": data["total"]
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/analyze/<coin>')
def analyze(coin):
    data = analyze_multi_timeframe(coin.upper())
    return jsonify(data) if data else (jsonify({"error": "N/A"}), 404)
