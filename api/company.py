import datetime
from numpy import array, logical_not, isnan
import pandas
import database
from yahoo_fin.stock_info import get_data


class Company:
    name = ""
    ticker = ""
    industry = ""
    equity = 0
    initial_capital = 0
    net_profit_q4 = 0
    net_profit_q3 = 0
    net_profit_q2 = 0
    net_profit_q1 = 0
    prices_list = 0
    price = 0

    def __init__(self, ticker):
        self.ticker = ticker
        valuation = database.select_valuation(ticker=self.ticker)
        company = database.get_company(ticker=self.ticker)
        self.name = company[3]
        self.industry = company[4]
        self.equity = valuation[3]
        self.initial_capital = valuation[4]
        self.net_profit_q4 = valuation[5]
        self.net_profit_q3 = valuation[6]
        self.net_profit_q2 = valuation[7]
        self.net_profit_q1 = valuation[8]
        self.prices_list = self.get_price()
        self.price = round(self.prices_list[-1], 2)

    def get_price(self):
        yahoo_ticker = "{}.IS".format(self.ticker.upper())
        now = datetime.datetime.now()
        now = now + datetime.timedelta(days=1)
        one_year_ago = now - datetime.timedelta(days=365)
        stock_data = get_data(ticker=yahoo_ticker,
                              start_date=one_year_ago.strftime("%Y/%m/%d"),
                              end_date=now.strftime("%Y/%m/%d"),
                              index_as_date=True,
                              interval='1d')
        close_data = pandas.DataFrame.to_numpy(stock_data)
        price_list = array([float(x[3]) for x in close_data])
        price_list = price_list[logical_not(isnan(price_list))]
        return price_list



