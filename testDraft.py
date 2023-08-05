from inputs import config
from inputs import parameter
from inputs import variable
import bybit
import logging
import time


client =bybit.bybit(test=False,api_key=config.API_KEY,api_secret=config.SECRET_KEY)
info = client.Market.Market_symbolInfo().result()
keys = info[0]['result']
balance = client.Wallet.Wallet_getBalance(coin='BTC').result()
btc = keys[0]['last_price']
print(balance)
print(keys[0])
