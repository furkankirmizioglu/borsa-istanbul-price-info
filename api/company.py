import datetime
from numpy import array, logical_not, isnan
import pandas
import database
from yahoo_fin.stock_info import get_data


class Company:
    name = ""
    ticker = ""
    industry = ""
    latest_balance_sheet_term = ""
    equity = 0
    main_equity = 0
    initial_capital = 0
    old_initial_capital = 0
    lt_liabilities = 0
    current_ttm_net_profit = 0
    last_ttm_net_profit = 0
    prices_list = 0
    price = 0

    def __init__(self, ticker):
        self.ticker = ticker
        valuation = database.select_valuation(ticker=self.ticker)
        company = database.get_company(ticker=self.ticker)
        self.name = company[3]
        self.industry = company[4]
        self.latest_balance_sheet_term = valuation[3]
        self.equity = valuation[4]
        self.main_equity = valuation[5]
        self.initial_capital = valuation[6]
        self.old_initial_capital = valuation[7]
        self.lt_liabilities = valuation[8]
        self.current_ttm_net_profit = valuation[9]
        self.last_ttm_net_profit = valuation[10]
        self.prices_list = self.get_price()
        self.price = round(self.prices_list[-1], 2)

    def get_price(self):
        yahoo_ticker = "{}.IS".format(self.ticker.upper())
        now = datetime.datetime.now() + datetime.timedelta(days=1)
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
