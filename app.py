import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("forex-api")

app = Flask(__name__)
CORS(app)

SIGNALS_FILE = os.path.join(os.path.dirname(__file__), "signals.json")

TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN"]

def load_signals():
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, "r") as f:
            return json.load(f)
    return []

def save_signals(signals):
    with open(SIGNALS_FILE, "w") as f:
        json.dump(signals, f, indent=2)

def generate_signal(symbol, timeframe, signal_type):
    import random

    base_prices = {
        "XAUUSD": 4030.0,
        "EURUSD": 1.0850,
        "GBPUSD": 1.2680,
        "USDJPY": 149.50,
        "BTCUSD": 67500.0,
        "ETHUSD": 3450.0,
    }

    base = base_prices.get(symbol, 100.0)

    if base > 1000:
        spread = 5.0
        sl_mult = 3.0
        tp_mult = 2.0
    elif base > 100:
        spread = 0.5
        sl_mult = 3.0
        tp_mult = 2.0
    elif base > 10:
        spread = 0.05
        sl_mult = 3.0
        tp_mult = 2.0
    else:
        spread = 0.005
        sl_mult = 3.0
        tp_mult = 2.0

    entry = round(base + spread * random.uniform(-0.5, 0.5), 3)

    if signal_type == "SELL":
        tp = round(entry - spread * tp_mult * random.uniform(1.0, 2.0), 3)
        sl = round(entry + spread * sl_mult * random.uniform(1.0, 1.5), 3)
    else:
        tp = round(entry + spread * tp_mult * random.uniform(1.0, 2.0), 3)
        sl = round(entry - spread * sl_mult * random.uniform(1.0, 1.5), 3)

    sell_zone = {
        "rec1": {
            "from": round(base + spread * random.uniform(0.5, 1.5), 3),
            "to": round(base + spread * random.uniform(1.5, 2.5), 3)
        },
        "rec2": {
            "from": round(base + spread * random.uniform(2.0, 3.0), 3),
            "to": round(base + spread * random.uniform(3.0, 4.0), 3)
        },
        "rec3": {
            "from": round(base + spread * random.uniform(1.0, 2.0), 3),
            "to": round(base + spread * random.uniform(2.0, 3.0), 3)
        }
    }

    buy_zone = {
        "rec1": {
            "from": round(base - spread * random.uniform(0.5, 1.5), 3),
            "to": round(base - spread * random.uniform(0.1, 0.5), 3)
        },
        "rec2": {
            "from": round(base - spread * random.uniform(2.0, 4.0), 3),
            "to": round(base - spread * random.uniform(0.5, 2.0), 3)
        },
        "rec3": {
            "from": round(base - spread * random.uniform(1.0, 2.0), 3),
            "to": round(base - spread * random.uniform(0.5, 1.0), 3)
        }
    }

    risk_reward = round(abs(tp - entry) / abs(sl - entry), 2) if abs(sl - entry) > 0 else 1.0

    return {
        "id": int(datetime.now().timestamp() * 1000),
        "symbol": symbol,
        "timeframe": timeframe,
        "type": signal_type,
        "confirmation": signal_type if random.random() > 0.3 else "WAIT",
        "entry": entry,
        "takeProfit": tp,
        "stopLoss": sl,
        "riskReward": risk_reward,
        "sellZone": sell_zone,
        "buyZone": buy_zone,
        "active": True,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Forex Signals API",
        "version": "1.0.0",
        "timeframes": TIMEFRAMES,
        "endpoints": {
            "GET /api/signals": "Get all signals",
            "POST /api/signals": "Add new signal",
            "DELETE /api/signals/<id>": "Delete signal",
            "GET /api/health": "Health check"
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/signals', methods=['GET'])
def get_signals():
    signals = load_signals()
    return jsonify(signals)


@app.route('/api/signals', methods=['POST'])
def add_signal():
    data = request.json

    if not data or 'symbol' not in data or 'type' not in data:
        return jsonify({"error": "Missing required fields: symbol, type"}), 400

    symbol = data['symbol'].upper()
    timeframe = data.get('timeframe', 'M15').upper()
    signal_type = data['type'].upper()

    if timeframe not in TIMEFRAMES:
        return jsonify({"error": f"Invalid timeframe. Use: {', '.join(TIMEFRAMES)}"}), 400

    if signal_type not in ['BUY', 'SELL']:
        return jsonify({"error": "Type must be BUY or SELL"}), 400

    signal = generate_signal(symbol, timeframe, signal_type)

    signals = load_signals()
    signals.append(signal)
    save_signals(signals)

    logger.info(f"Signal added: {symbol} {timeframe} {signal_type}")
    return jsonify({"status": "ok", "signal": signal}), 201


@app.route('/api/signals/<int:signal_id>', methods=['DELETE'])
def delete_signal(signal_id):
    signals = load_signals()
    original_count = len(signals)
    signals = [s for s in signals if s.get('id') != signal_id]

    if len(signals) == original_count:
        return jsonify({"error": "Signal not found"}), 404

    save_signals(signals)
    logger.info(f"Signal deleted: {signal_id}")
    return jsonify({"status": "ok"})


@app.route('/api/signals', methods=['DELETE'])
def clear_signals():
    save_signals([])
    logger.info("All signals cleared")
    return jsonify({"status": "ok", "message": "All signals cleared"})


# Initialize sample signals on startup
if not load_signals():
    sample_signals = [
        generate_signal("XAUUSD", "M15", "SELL"),
        generate_signal("XAUUSD", "H1", "BUY"),
        generate_signal("EURUSD", "M5", "BUY"),
        generate_signal("EURUSD", "H4", "SELL"),
        generate_signal("GBPUSD", "M15", "SELL"),
        generate_signal("GBPUSD", "D1", "BUY"),
        generate_signal("USDJPY", "M30", "BUY"),
        generate_signal("USDJPY", "H1", "SELL"),
        generate_signal("BTCUSD", "H4", "BUY"),
        generate_signal("BTCUSD", "D1", "SELL"),
        generate_signal("ETHUSD", "M5", "BUY"),
        generate_signal("ETHUSD", "W1", "SELL"),
    ]
    save_signals(sample_signals)
    logger.info("Initialized with 12 sample signals")


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
