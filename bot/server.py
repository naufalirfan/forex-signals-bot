import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='webapp')
CORS(app)

SIGNALS_FILE = 'signals.json'

def load_signals():
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, 'r') as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    return send_from_directory('webapp', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('webapp', path)

@app.route('/api/signals', methods=['GET'])
def get_signals():
    signals = load_signals()
    return jsonify(signals)

@app.route('/api/signals', methods=['POST'])
def add_signal():
    data = request.json
    signals = load_signals()
    signals.append(data)

    with open(SIGNALS_FILE, 'w') as f:
        json.dump(signals, f, indent=2)

    return jsonify({"status": "ok", "signal": data})

@app.route('/api/signals/<int:signal_id>', methods=['DELETE'])
def delete_signal(signal_id):
    signals = load_signals()
    signals = [s for s in signals if s.get('id') != signal_id]

    with open(SIGNALS_FILE, 'w') as f:
        json.dump(signals, f, indent=2)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
