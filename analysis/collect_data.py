import logging
from pybitget import Client
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

    client = Client(config.API_KEY, config.SECRET_KEY, config.API_PASSPHARSE)

    def data_retrieve(self,ticker):
        while True:
            try:
                bid_price = self.client.mix_get_single_symbol_ticker(ticker).get('data').get('bestBid')
                ask_price = self.client.mix_get_single_symbol_ticker(ticker).get('data').get('bestAsk')
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