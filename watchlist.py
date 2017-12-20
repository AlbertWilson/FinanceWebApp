import quandl
import datetime
import os.path
from copy import deepcopy

def get_week_percent_change(symbol):
    quandl.ApiConfig.api_key = '3_sxFydrNzVvGNNFTQbd'

    query_list = ['WIKI' + '/' + symbol + '.' + str(4)]

    start_date = datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()

    prices = quandl.get(query_list,
            returns='numpy',
            start_date=start_date,
            end_date=end_date,
            collapse='daily',
            order='asc'
            )

    if len(prices) < 1: # determine if the symbol is not valid
        return None

    end_price = prices[len(prices)-1][1]
    start_price = prices[0][1]

    current_price = end_price

    week_percent_change = ((end_price - start_price) / start_price) * float(100)
    return (current_price, week_percent_change)

class Stock:
    def __init__(self, symbol):
        self.companySymbol = symbol
        info = get_week_percent_change(symbol)
        if info:
            self.current_price = info[0]
            self.week_percent_change = info[1]
        else:
            self.current_price = None
            self.week_percent_change = None

class User:
    def __init__(self, username):
        self.username = username
        self.watchlist = []

    def insert_stock(self, companySymbol):
        self.watchlist.append(Stock(companySymbol))

    def remove_stock(self, companySymbol):
        for stock in self.watchlist:
            if stock.companySymbol == companySymbol:
                self.watchlist.remove(stock)

    def sort_watchlist(self):
        self.watchlist.sort(key=lambda x: x.week_percent_change, reverse=True)

    def five_best_performers(self):
        return self.watchlist[0:5]

    def five_worst_performers(self):
        return self.watchlist[-5:]

