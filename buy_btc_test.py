from binance.client import Client
from binance.enums import *
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

symbol = "BTCUSDC"
buy_amount_usdc = 50


def round_step_size(quantity, step_size):
    return float(Decimal(quantity).quantize(Decimal(step_size), rounding=ROUND_DOWN))

try:
    # Get current ask price
    book = client.get_order_book(symbol=symbol)
    ask = float(book['asks'][0][0])

    # Calculate quantity of BTC
    qty = buy_amount_usdc / ask
    filters = client.get_symbol_info(symbol)['filters']
    lot_size_filter = next(f for f in filters if f['filterType'] == 'LOT_SIZE')
    step = lot_size_filter['stepSize']
    qty = round_step_size(qty, step)

    # Submit market buy order
    print(f"Attempting to buy {qty:.8f} BTC at approx {ask} USDC...")
    order = client.order_market_buy(symbol=symbol, quantity=qty)
    print("✅ Order executed:")
    for fill in order["fills"]:
        print(f"- Price: {fill['price']}, Qty: {fill['qty']}")

except Exception as e:
    print("❌ Error:", e)
