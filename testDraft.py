from inputs import config
from inputs import parameter
from inputs import variable
from pybitget import Client
import logging
import time

#response = requests.get("https://api/spot/v1/trade/orders?symbol=BTCUSDT&price=274265&&quantity=0.001&side=buy&orderType=limit&force=normal")
#result = response.json()
#print(result)

client = Client(config.API_KEY, config.SECRET_KEY, config.API_PASSPHARSE)
#buy_order = client.spot_place_order(symbol='btcusdt_spbl', price='31426.5', quantity='0.0010000914588683622', side='buy', orderType='limit',force="normal")
sell_order = client.spot_place_order(symbol='btcusdt_spbl', price='29426.5', quantity='0.0003', side='sell', orderType='limit',force="normal")
#print(buy_order)
print(sell_order)
print(client.spot_get_account_assets())
#print(client.mix_get_accounts('UMCBL'))
#print(client.mix_get_single_symbol_ticker('BTCUSDT_UMCBL').get('data').get('bestAsk'))
#print(client.mix_get_single_symbol_ticker('BTCUSDT_UMCBL').get('data').get('bestBid'))
#print(sell_order)