from pybitget import Client
from inputs import config
class Distribution:
    # Instantiate REST API Connection
    client = Client(config.API_KEY, config.SECRET_KEY, config.API_PASSPHARSE)

    def shapeData(self,file):
        bid_price_list = []
        ask_price_list = []
        with open(file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            info = str(line)
            array = info.split(':')
            if array[0] == 'bid_price':
                bid_price_list.append(float(array[1]))
            elif array[0] == 'ask_price':
                ask_price_list.append(float(array[1]))

        return bid_price_list,ask_price_list

    def distribution_cal(self,file):
        bid_price_list = self.shapeData(file)[0]
        ask_price_list = self.shapeData(file)[1]

        bid_price_mean = 0.0
        ask_price_mean = 0.0
        for price in bid_price_list:
            bid_price_mean += float(price)

        for price in ask_price_list:
            ask_price_mean += float(price)

        bid_price_mean /= len(bid_price_list)
        ask_price_mean /= len(ask_price_list)

        bid_standard = 0.0
        ask_standard = 0.0

        for price in bid_price_list:
            bid_standard += (price - bid_price_mean) ** 2
        for price in ask_price_list:
            ask_standard += (price - ask_price_mean) ** 2

        bid_standard = (bid_standard/len(bid_price_list)) ** (1/2)
        ask_standard = (ask_standard/len(ask_price_list)) ** (1/2)

        map_bid = {}
        map_ask = {}
        map_bid['mean'] = 0
        map_ask['mean'] = 0
        map_bid['1s'] = 0
        map_ask['1s'] = 0
        map_bid['2s'] = 0
        map_ask['2s'] = 0
        map_bid['3s'] = 0
        map_ask['3s'] = 0
        map_bid['-1s'] = 0
        map_ask['-1s'] = 0
        map_bid['-2s'] = 0
        map_ask['-2s'] = 0
        map_bid['-3s'] = 0
        map_ask['-3s'] = 0

        for price in bid_price_list:
            if price == bid_price_mean:
                map_bid['mean']+=1
            if price > bid_price_mean and price <= bid_price_mean + bid_standard:
                map_bid['1s']+=1
            if price > bid_price_mean + bid_standard and price <= bid_price_mean + 2 * bid_standard:
                map_bid['2s']+=1
            if price > bid_price_mean + 2 * bid_standard and price <= bid_price_mean + 3 * bid_standard:
                map_bid['3s']+=1
            if price < bid_price_mean and price >= bid_price_mean - bid_standard:
                map_bid['-1s']+=1
            if price < bid_price_mean - bid_standard and price >= bid_price_mean - 2 * bid_standard:
                map_bid['-2s']+=1
            if price < bid_price_mean - 2 * bid_standard and price >=bid_price_mean - 3 * bid_standard:
                map_bid['-3s']+=1

        for price in ask_price_list:
            if price == ask_price_mean:
                map_ask['mean']+=1
            if price > ask_price_mean and price <= ask_price_mean + ask_standard:
                map_ask['1s']+=1
            if price > ask_price_mean + ask_standard and price <= ask_price_mean + 2 * ask_standard:
                map_ask['2s']+=1
            if price > ask_price_mean + 2 * ask_standard and price <= ask_price_mean + 3 * ask_standard:
                map_ask['3s']+=1
            if price < ask_price_mean and price >= ask_price_mean - ask_standard:
                map_ask['-1s']+=1
            if price < ask_price_mean - ask_standard and price >= ask_price_mean - 2 * ask_standard:
                map_ask['-2s']+=1
            if price < ask_price_mean - 2 * ask_standard and price >=ask_price_mean - 3 * ask_standard:
                map_ask['-3s']+=1

        map_bid['mean'] = map_bid['mean']/len(bid_price_list) * 100
        map_bid['1s'] = map_bid['1s']/len(bid_price_list) * 100
        map_bid['2s'] = map_bid['2s'] / len(bid_price_list) * 100
        map_bid['3s'] = map_bid['3s'] / len(bid_price_list) * 100
        map_bid['-1s'] = map_bid['-1s'] / len(bid_price_list) * 100
        map_bid['-2s'] = map_bid['-2s'] / len(bid_price_list) * 100
        map_bid['-3s'] = map_bid['-3s'] / len(bid_price_list) * 100
        map_ask['mean'] = map_ask['mean'] / len(ask_price_list) * 100
        map_ask['1s'] = map_ask['1s'] / len(ask_price_list) * 100
        map_ask['2s'] = map_ask['2s'] / len(ask_price_list) * 100
        map_ask['3s'] = map_ask['3s'] / len(ask_price_list) * 100
        map_ask['-1s'] = map_ask['-1s'] / len(ask_price_list) * 100
        map_ask['-2s'] = map_ask['-2s'] / len(ask_price_list) * 100
        map_ask['-3s'] = map_ask['-3s'] / len(ask_price_list) * 100

        print('bid price distribution: '+ str(map_bid))
        print('ask price distribution: ' + str(map_ask))
        print('bid mean: '+str(bid_price_mean))
        print('ask mean: ' + str(ask_price_mean))
        print('bid standard: '+str(bid_standard))
        print('ask standard: ' + str(ask_standard))
        print('bid - 2s: ' + str(bid_price_mean - 2 * bid_standard))
        print('ask - 2s: ' + str(ask_price_mean - 2 * ask_standard))
        print('bid + 2s: ' + str(bid_price_mean + 2 * bid_standard))
        print('ask + 2s: ' + str(ask_price_mean + 2 * ask_standard))

        high_price = ask_price_mean + 2 * ask_standard
        low_price = bid_price_mean - 2 * bid_standard
        return high_price, low_price

if __name__ == '__main__':
    distribution = Distribution()
    distribution.distribution_cal('price_data.txt')