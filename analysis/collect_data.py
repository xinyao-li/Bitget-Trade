import logging
from pybit.unified_trading import HTTP
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

    session = HTTP(
        testnet=False,
        api_key=config.API_KEY,
        api_secret=config.SECRET_KEY
    )

    def data_retrieve(self,ticker):
        while True:
            try:
                bid_price = self.session.get_tickers(category="linear",symbol="BTCUSDT")['result']['list'][0]['bid1Price']
                ask_price = self.session.get_tickers(category="linear",symbol="BTCUSDT")['result']['list'][0]['ask1Price']
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