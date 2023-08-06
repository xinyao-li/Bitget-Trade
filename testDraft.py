from inputs import config
from inputs import parameter
from inputs import variable
import bybit
import logging
import time


client = bybit.bybit(test=False,api_key=config.API_KEY,api_secret=config.SECRET_KEY)
info = client.Market.Market_symbolInfo().result()
keys = info[0]['result']
balance = client.Wallet.Wallet_getBalance(coin='BTC').result()
btc_usd_index = 51
btc = keys[btc_usd_index]['last_price']
pos = client.Positions.Positions_myPosition(symbol="BTCUSD").result()
print(pos)
print(balance)
print(keys[btc_usd_index])
print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Limit",qty=0.0001,price=btc,time_in_force="GoodTillCancel").result())