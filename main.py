from inputs import config
from inputs import parameter
from inputs import variable
from analysis import normal_distribution
import bybit
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
    client = bybit.bybit(test=False, api_key=config.API_KEY, api_secret=config.SECRET_KEY)
    btc_usd_index = 51
    last_trade_price = variable.last_trade_price
    holding_amount = 0
    buying_power = 0
    seconds = variable.seconds
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
    def grid_trading(self, ticker, high, low, percentage, buying_power_percentage, period, threshold):
        # Get the buying power from account
        self.refresh_holding_amount('BTC')
        self.refresh_buying_power()

        self.logger.info('buying power is: ' + str(self.buying_power))
        self.logger.info('last trade price is: ' + str(self.last_trade_price))
        self.logger.info('holding amount is: ' + str(self.holding_amount))

        if self.last_trade_price is not None:
            while self.seconds < period:
                # Get the current price of ticker in Binance in every 1 sec
                bid_price = float(self.get_price('BTCUSDT_UMCBL')[0])
                ask_price = float(self.get_price('BTCUSDT_UMCBL')[1])

                # If the price is in range low to high, if the price drop 'percentage' then buy, else if price reach 'percentage' then sell
                # Buy or Sell amount will be buy_power_percentage of buying power divided by current price of ticker.
                if bid_price is not None and ask_price is not None and ask_price <= high and bid_price >= low:
                    if ask_price <= self.last_trade_price * (1 - percentage):
                        self.buy_and_update_info(ticker, buying_power_percentage * self.buy_balance, ask_price, threshold)

                    elif bid_price >= self.last_trade_price * (1 + percentage):
                        self.sell_and_update_info(ticker, buying_power_percentage * self.sell_balance, bid_price, threshold)
                #wait for 1 sec for the price update
                time.sleep(1)
                self.seconds += 1
                self.write_variable('./inputs/variable.py', self.last_trade_price)

    '''
       Get the bid and ask price of crypto
    '''
    def get_price(self, ticker):
        # Get the current price of ticker
        bid_price = None
        ask_price = None
        try:
            bid_price = self.info[0]['result'][self.btc_usd_index]['bid_price']
            ask_price = self.info[0]['result'][self.btc_usd_index]['ask_price']
            self.logger2.info('ask_price:' + str(ask_price))
            self.logger2.info('bid_price:' + str(bid_price))
        except Exception as e:
            print('last trade price is: ' + str(self.last_trade_price))
            logging.exception("No such ticker or fail to get price: " + str(e))
        return bid_price, ask_price

    '''
        refresh the holding amount of crypto
    '''
    def refresh_holding_amount(self, ticker):
        try:
            self.holding_amount = float(self.client.spot_get_account_assets(ticker).get('data')[0].get('available'))
        except Exception as e:
            logging.exception(e)

    '''
        refresh the buying power
    '''
    def refresh_buying_power(self):
        try:
            self.buying_power = float(self.client.spot_get_account_assets()['data'][2]['available'])
        except Exception as e:
            logging.exception(e)

    '''
        place a limit buying order when ask price touch the trading line, after trading completed, update the buying_power,holding_amount, buy and sell balance 
        and last_trade_price in variable.py as well.
    '''
    def buy_and_update_info(self, ticker, buying_power_percentage, ask_price, threshold):
        try:
            buying_amount = self.buying_power * buying_power_percentage / ask_price
            self.logger.info("ask_price: " + str(ask_price))
            self.logger.info("buying_amount: "+str(buying_amount))
            self.client.spot_place_order(symbol=ticker, price=ask_price, quantity=round(buying_amount,4), side='buy',
                                         orderType='limit', force="normal")
            self.logger.info("Bought " + str(round(buying_amount,4)) + " of " + str(ticker) + " at price: " + str(ask_price))

            # Update the last_trade_price and holding_amount
            self.last_trade_price = ask_price
            self.logger.info('last trade price is: ' + str(self.last_trade_price))
            self.refresh_holding_amount('BTC')
            self.write_variable('./inputs/variable.py', self.last_trade_price,'last_trade_price')
            if self.reach_threshold(threshold):
                self.buy_balance += 1
                self.write_variable('./inputs/variable.py', self.last_trade_price)
            else:
                self.buy_balance = 1
                os.system('say "Buying order reached threshold"')
            if self.reach_threshold(threshold):
                self.sell_balance -= 1
                self.write_variable('./inputs/variable.py', self.last_trade_price)
            else:
                self.sell_balance = 1

            self.refresh_buying_power()

        except Exception as e:
            self.logger.exception("Buy Order submission failed: "+str(e))

    '''
        place a limit selling order when bid price touch the trading line, after trading completed, update the buying_power, holding_amount, buy and sell balance
        and last_trade_price in variable.py as well.
    '''
    def sell_and_update_info(self, ticker, buying_power_percentage, bid_price, threshold):
        try:
            selling_amount = self.buying_power * buying_power_percentage / bid_price
            self.logger.info("bid_price: " + str(bid_price))
            self.logger.info("selling_amount: " + str(selling_amount))

            if self.selling_amount_enough_to_sell(str(selling_amount)) is False:
                selling_amount = 0
            if self.not_hold_enough_amount(selling_amount):
                selling_amount = self.holding_amount

            if selling_amount > 0.000000002:
                self.client.spot_place_order(symbol=ticker, price=bid_price, quantity=round(selling_amount,4), side='sell',
                                             orderType='limit', force="normal")
                self.logger.info("Sold " + str(round(selling_amount,4)) + " of " + str(ticker) + " at price: " + str(bid_price))
                self.last_trade_price = bid_price
                self.logger.info('last trade price is: ' + str(self.last_trade_price))
                self.refresh_holding_amount('BTC')

            self.write_variable('./inputs/variable.py', self.last_trade_price,'last_trade_price')

            if self.reach_threshold(threshold):
                self.sell_balance = self.sell_balance + 1
                self.write_variable('./inputs/variable.py', self.last_trade_price)
            else:
                self.sell_balance = 1
                os.system('say "Selling order reached threshold"')
            if self.reach_threshold(threshold):
                self.buy_balance -= 1
                self.write_variable('./inputs/variable.py', self.last_trade_price)
            else:
                self.buy_balance = 1

            self.refresh_buying_power()

        except Exception as e:
            self.logger.exception("Sell Order submission failed: "+str(e))

    '''
        edge case when selling_amount is too low to sell
    '''
    def selling_amount_enough_to_sell(self, selling_amount):
        # if selling_amount less than 2e-9
        if selling_amount.__contains__('e') and float(selling_amount[len(selling_amount) - 1]) >= 8:
            if self.holding_amount > 0.000000002:
                return True
            else:
                self.logger.info("Selling amount is too low to sell")
                return False

        return True

    '''
        edge case when selling_amount is higher than holding amount
    '''
    def not_holding_enough_amount(self, selling_amount):
        # if selling amount is out of the qty we hold
        if self.holding_amount < selling_amount:
            self.logger.info("Not enough amount to sell")
            return True

        return False

    '''
       write the last_trade_price into variable.py
    '''
    def write_variable(self, doc, last_trade_price):
        with open(doc, 'w') as f:
            f.write(f'last_trade_price={last_trade_price}\n')
            f.write(f'seconds={self.seconds}\n')
            f.write(f'buy_balance={self.buy_balance}\n')
            f.write(f'sell_balance={self.sell_balance}\n')

    def reach_threshold(self,threshold):
        return float(self.buy_balance) <= threshold or float(self.buy_balance) > 0 \
            or float(self.sell_balance) <=threshold or float(self.sell_balance) > 0

    def normal_distribution_calculate(self,ticker,percentage,buying_power_percentage,period,threshold):
        while True:
            self.logger2.info(datetime.datetime.now())
            distribution = normal_distribution.Distribution()
            result = distribution.distribution_cal('./analysis/price_data.txt')
            self.grid_trading(ticker, result[0], result[1], percentage, buying_power_percentage, period, threshold)
            self.seconds = 0
            self.write_variable('./inputs/variable.py', self.last_trade_price, 'last_trade_price')
            self.write_variable('./inputs/variable.py', self.seconds, 'seconds')

    def run_trade(self,ticker,percentage,buying_power_percentage,period,threshold):
        self.normal_distribution_calculate(ticker, percentage, buying_power_percentage, period, threshold)


if __name__ == '__main__':
    crypt_trade = CryptoTrade()
    print("grid trading start")
    crypt_trade.run_trade(parameter.ticker,parameter.percentage,
                             parameter.buying_power_percentage,parameter.period,parameter.threshold)
