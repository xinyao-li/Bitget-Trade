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
buy_order = client.spot_place_order(symbol='btcusdt_spbl', price='27426.5', quantity='0.001', side='buy', orderType='limit',force="normal")
#sell_order = client.spot_place_order(symbol='BTCUSDT', price='26426.5', quantity='0.001', side='sell', orderType='limit',force="normal")
print(buy_order)
#print(sell_order)