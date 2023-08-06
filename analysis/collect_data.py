import logging
import bybit
from inputs import config
import time
import datetime
class CryptoData:
    logger = logging.getLogger('my_logger')
    # set the logging level to INFO
    logger.setLevel(logging.INFO)
    # create a file handler that writes logs to a file named logs.txt
    handler = logging.FileHandler('./price_data.txt')
    logger.addHandler(handler)

    client = bybit.bybit(test=False, api_key=config.API_KEY, api_secret=config.SECRET_KEY)
    info = client.Market.Market_symbolInfo().result()
    btc_usd_index = 51

    def data_retrieve(self,ticker):
        while True:
            try:
                bid_price = self.info[0]['result'][self.btc_usd_index]['bid_price']
                ask_price = self.info[0]['result'][self.btc_usd_index]['ask_price']
                self.logger.info('ask_price:' + str(ask_price))
                self.logger.info('bid_price:' + str(bid_price))
                time.sleep(1)
            except Exception as e:
                logging.exception("No such ticker or fail to get price: " + str(e))

if __name__ == '__main__':
    current_time = datetime.datetime.now()
    crypt_data = CryptoData()
    print('data collection start:')
    crypt_data.logger.info(current_time)
    crypt_data.data_retrieve('BTCUSDT_UMCBL')