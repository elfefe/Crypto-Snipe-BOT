from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

symbol = "BTCUSDC"

try:
    # Get balance
    balances = client.get_asset_balance(asset="BTC")
    qty = float(balances["free"])

    if qty == 0:
        raise Exception("No BTC available to sell.")

    # Get LOT_SIZE filter for rounding
    filters = client.get_symbol_info(symbol)['filters']
    lot_size_filter = next(f for f in filters if f['filterType'] == 'LOT_SIZE')
    step = lot_size_filter['stepSize']
    from decimal import Decimal, ROUND_DOWN
    def round_step_size(quantity, step_size):
        return float(Decimal(quantity).quantize(Decimal(step_size), rounding=ROUND_DOWN))

    qty = round_step_size(qty, step_size=step)

    print(f"Selling {qty} BTC at market...")
    order = client.order_market_sell(symbol=symbol, quantity=qty)

    print("✅ Sell order executed:")
    for fill in order["fills"]:
        print(f"- Price: {fill['price']}, Qty: {fill['qty']}")

except Exception as e:
    print("❌ Error:", e)
