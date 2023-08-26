from inputs import config
from pybit.unified_trading import HTTP

session = HTTP(
    testnet=False,
    api_key=config.API_KEY,
    api_secret=config.SECRET_KEY
)
#Get the buying power in derivatives
print(session.get_wallet_balance(accountType="CONTRACT"))
print(session.get_wallet_balance(accountType="CONTRACT")['result']['list'][0]['coin'][0]['availableToWithdraw'])

#Get BTC amount currently holding
print(session.get_wallet_balance(accountType="CONTRACT",coin='BTC'))
print(session.get_coins_balance(accountType="CONTRACT",coin="BTC"))

#Get position
print(session.get_positions(
    category="linear",
    symbol="BTCUSDT",
))

# Get ticker price
bid_price = session.get_tickers(category="linear",symbol="BTCUSDT")['result']['list'][0]['bid1Price']
ask_price = session.get_tickers(category="linear",symbol="BTCUSDT")['result']['list'][0]['ask1Price']
print(bid_price)
print(ask_price)

#Place a buy order
'''
print(session.place_order(
    category="linear",
    symbol="BTCUSDT",
    side="Buy",
    orderType="Limit",
    qty="0.01",
    price=ask_price,
    takeProfit=str(ask_price),
    tpTriggerBy="MarketPrice",
    positionIdx ="1",
    timeInForce="GTC",
))
'''
#Place a sell order
'''
print(session.place_order(
    category="linear",
    symbol="BTCUSDT",
    side="Sell",
    orderType="Limit",
    qty="0.01",
    price=bid_price,
    tpTriggerBy="MarketPrice",
    positionIdx ="2",
    timeInForce="GTC",
))
'''





