from inputs import config
from inputs import parameter
from inputs import variable
from analysis import normal_distribution
from pybit.unified_trading import HTTP
import logging
import time
import os
import datetime


class CryptoTrade:
    # create a logger for record trading history
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('logs.txt')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create a logger for collect the price data
    logger2 = logging.getLogger('my_logger2')
    logger2.setLevel(logging.INFO)
    handler2 = logging.FileHandler('./analysis/price_data.txt')
    handler2.setLevel(logging.INFO)
    logger2.addHandler(handler2)

    # Instantiate REST API Connection
    session = HTTP(
        testnet=False,
        api_key=config.API_KEY,
        api_secret=config.SECRET_KEY
    )
    last_trade_price = variable.last_trade_price
    equity = 0
    last_trade_price = variable.last_trade_price
    buy_balance = variable.buy_balance
    sell_balance = variable.sell_balance

    '''
        The method use for executing grid trading in range of low to high, it will check the bid_price and ask_price every second, buy or sell
        the amount of "buying power * buying_power_percentage / current price" when increase or decrease the certain percentage from last trading price
        :param ticker: the crypto type
        :param high: the highest price in trading range
        :param low: the lowest price in trading range
        :param percentage: the vibration percentage for triggering the trading api
        :param buying_power_percentage: the percentage of buying power we're going to use in this trade
    '''
    def grid_trading(self, ticker, high, low, percentage, trading_amount, period, threshold):
        # Get the buying power from account
        self.refresh_equity()

        self.logger.info('equity is: ' + str(self.equity))
        self.logger.info('last trade price is: ' + str(self.last_trade_price))

        if self.last_trade_price is not None:
            for price in range(int(low),int(high)):
                if price < self.last_trade_price:
                    self.place_buying_order(ticker,trading_amount,price,percentage)
                    self.buy_balance,self.sell_balance = self.update_balance(self.buy_balance,self.sell_balance,threshold)
                elif price > self.last_trade_price:
                    self.place_selling_order(ticker,trading_amount,price,percentage)
                    self.sell_balance,self.buy_balance = self.update_balance(self.sell_balance, self.buy_balance,threshold)

                self.write_variable('./inputs/variable.py', self.last_trade_price)

        time.sleep(period)

    def update_balance(self,increase_balance,decrease_balance,threshold):
        increase_balance += 1
        decrease_balance -= 1
        if increase_balance > threshold:
            increase_balance = 1
        if decrease_balance < 1:
            decrease_balance = 1
        return increase_balance, decrease_balance


    def refresh_equity(self):
        try:
            self.equity = float(self.session.get_wallet_balance(accountType="CONTRACT")['result']['list'][0]['coin'][0]['equity'])
        except Exception as e:
            logging.exception(e)

    def place_buying_order(self, ticker, trading_amount, price, percentage):
        try:
            self.session.place_order(
                category="linear",
                symbol=ticker,
                side="Buy",
                orderType="Limit",
                qty=str(trading_amount* self.buy_balance),
                price=price,
                takeProfit=str(price * (1 + percentage)),
                tpTriggerBy="MarketPrice",
                positionIdx="1",
                timeInForce="GTC",
            )
            self.logger.info("Bought " + trading_amount + " of " + str(ticker) + " at price: " + str(price))
            self.last_trade_price = price

        except Exception as e:
            self.logger.exception("Buy Order submission failed: " + str(e))

    def place_selling_order(self, ticker, trading_amount, price, percentage):
        try:
            self.session.place_order(
                category="linear",
                symbol=ticker,
                side="Sell",
                orderType="Limit",
                qty=str(trading_amount * self.sell_balance),
                price=price,
                takeProfit=str(price * (1 - percentage)),
                tpTriggerBy="MarketPrice",
                positionIdx="2",
                timeInForce="GTC",
            )
            self.logger.info("Sold " + str(trading_amount) + " of " + str(ticker) + " at price: " + str(price))
        except Exception as e:
            self.logger.exception("Sell Order submission failed: " + str(e))
    '''
       Get the bid and ask price of crypto
    '''
    def get_price(self, ticker):
        # Get the current price of ticker
        bid_price = None
        ask_price = None
        try:
            bid_price = self.session.get_tickers(category="linear",symbol="BTCUSDT")['result']['list'][0]['bid1Price']
            ask_price = self.session.get_tickers(category="linear",symbol="BTCUSDT")['result']['list'][0]['ask1Price']
            self.logger2.info('ask_price:' + str(ask_price))
            self.logger2.info('bid_price:' + str(bid_price))
        except Exception as e:
            print('last trade price is: ' + str(self.last_trade_price))
            logging.exception("No such ticker or fail to get price: " + str(e))
        return bid_price, ask_price

    def write_variable(self, doc, last_trade_price):
        with open(doc, 'w') as f:
            f.write(f'last_trade_price={last_trade_price}\n')
            f.write(f'buy_balance={self.buy_balance}\n')
            f.write(f'sell_balance={self.sell_balance}\n')

    def normal_distribution_calculate(self,ticker,percentage,trading_amount,period,threshold):
        while True:
            self.logger2.info(datetime.datetime.now())
            distribution = normal_distribution.Distribution()
            result = distribution.distribution_cal('./analysis/price_data.txt')
            self.grid_trading(ticker, result[0], result[1], percentage, trading_amount, period, threshold)
            self.write_variable('./inputs/variable.py', self.last_trade_price)

    def run_trade(self,ticker,percentage,trading_amount,period,threshold):
        self.normal_distribution_calculate(ticker, percentage, trading_amount, period, threshold)


if __name__ == '__main__':
    crypt_trade = CryptoTrade()
    print("grid trading start")
    crypt_trade.run_trade(parameter.ticker,parameter.percentage,
                             parameter.trading_amount,parameter.period,parameter.threshold)
