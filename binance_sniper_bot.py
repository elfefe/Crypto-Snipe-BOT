# binance_sniper_bot.py
# Core engine for multi-token snipe bot with auto-sell, stop-loss, and Flask dashboard

import threading
import time
import json
from binance.client import Client
from binance.enums import *
from flask import Flask, jsonify, render_template
from decimal import Decimal
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

# Load config
with open("bot_config.json") as f:
    config = json.load(f)

tracked_tokens = {}

app = Flask(__name__)

# Util

def round_step_size(quantity, step_size):
    return float(Decimal(quantity) - (Decimal(quantity) % Decimal(step_size)))

# Core trading logic

def track_token(symbol, buy_amount_usdt, stop_loss_pct, take_profit_x):
    status = {
        "symbol": symbol,
        "bought": False,
        "buy_price": None,
        "current_price": None,
        "pnl": 0,
        "status": "Waiting for market"
    }
    tracked_tokens[symbol] = status

    def run():
        while True:
            try:
                book = client.get_order_book(symbol=symbol)
                ask = float(book['asks'][0][0])
                status['current_price'] = ask

                if not status['bought']:
                    qty = float(buy_amount_usdt) / ask
                    step = client.get_symbol_info(symbol)['filters'][2]['stepSize']
                    qty = round_step_size(qty, step)
                    order = client.order_market_buy(symbol=symbol, quantity=qty)
                    buy_price = float(order['fills'][0]['price'])
                    status['buy_price'] = buy_price
                    status['bought'] = True
                    status['status'] = f"Bought at {buy_price}"
                else:
                    pnl = (ask - status['buy_price']) / status['buy_price'] * 100
                    status['pnl'] = pnl

                    if ask >= status['buy_price'] * take_profit_x:
                        client.order_market_sell(symbol=symbol, quantity=float(order['executedQty']))
                        status['status'] = f"Sold for 50x profit at {ask}"
                        break
                    elif ask <= status['buy_price'] * (1 - stop_loss_pct / 100):
                        client.order_market_sell(symbol=symbol, quantity=float(order['executedQty']))
                        status['status'] = f"Stopped out at {ask}"
                        break

                time.sleep(1)
            except Exception as e:
                status['status'] = f"Error: {e}"
                time.sleep(2)

    threading.Thread(target=run, daemon=True).start()

# Flask routes

@app.route('/')
def index():
    return render_template('dashboard.html', tokens=tracked_tokens)

@app.route('/api/status')
def api_status():
    return jsonify(tracked_tokens)

# Launch bot

for token in config["tokens"]:
    track_token(
        token["symbol"],
        token["buy_amount_usdt"],
        token["stop_loss_pct"],
        token["take_profit_x"]
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
