from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

symbol = "XRPUSDC"
buy_amount_usdc = 50

from decimal import Decimal, ROUND_DOWN
def round_step_size(quantity, step_size):
    return float(Decimal(str(quantity)).quantize(Decimal(str(step_size)), rounding=ROUND_DOWN))

try:
    # Get current ask price
    book = client.get_order_book(symbol=symbol)
    ask = float(book['asks'][0][0])

    # Calculate quantity of XRP
    qty = buy_amount_usdc / ask
    filters = client.get_symbol_info(symbol)['filters']
    lot_size_filter = next(f for f in filters if f['filterType'] == 'LOT_SIZE')
    step = lot_size_filter['stepSize']
    min_qty = float(lot_size_filter['minQty'])
    qty = round_step_size(qty, step)

    if qty < min_qty:
        raise ValueError(f"La quantité calculée ({qty}) est inférieure au minimum autorisé ({min_qty}).")

    print(f"Buying {qty:.8f} {symbol} at approx {ask} USDC...\n{lot_size_filter}")
    order = client.order_market_buy(symbol=symbol, quantity=qty)

    print("\u2705 Buy order executed:")
    for fill in order["fills"]:
        print(f"- Price: {fill['price']}, Qty: {fill['qty']}")

except Exception as e:
    print("\u274c Error:", e)
