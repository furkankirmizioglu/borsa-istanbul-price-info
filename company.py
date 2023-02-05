import datetime
import numpy
import pandas
import database
from yahoo_fin.stock_info import get_data


class Company:
    companyName = ""
    ticker = ""
    industry = ""
    equityAmount = 0
    initialCapitalAmount = 0
    netRevenueQ4 = 0
    netRevenueQ3 = 0
    netRevenueQ2 = 0
    netRevenueQ1 = 0
    priceList = 0
    price = 0

    def __init__(self, ticker):
        self.ticker = ticker
        valuationInfo = database.selectFromCompanyValuationInfo(ticker=self.ticker)
        companyInfo = database.selectFromCompanyInfoTicker(ticker=self.ticker)
        # valuationInfo[0] = GUID
        # valuationInfo[1] = LASTUPDATED
        # valuationInfo[2] = STOCK_TICKER_SYMBOL
        # valuationInfo[3] = EQUITY_AMOUNT
        # valuationInfo[4] = INITIAL_CAPITAL_AMOUNT
        # valuationInfo[5] = NET_REVENUE_Q4
        # valuationInfo[6] = NET_REVENUE_Q3
        # valuationInfo[7] = NET_REVENUE_Q2
        # valuationInfo[8] = NET_REVENUE_Q1
        # companyInfo[0] = GUID
        # companyInfo[1] = LAST_UPDATED
        # companyInfo[2] = STOCK_TICKER_SYMBOL
        # companyInfo[3] = COMPANY_NAME
        # companyInfo[4] = INDUSTRY
        self.companyName = companyInfo[3]
        self.industry = companyInfo[4]
        self.equityAmount = valuationInfo[3]
        self.initialCapitalAmount = valuationInfo[4]
        self.netRevenueQ4 = valuationInfo[5]
        self.netRevenueQ3 = valuationInfo[6]
        self.netRevenueQ2 = valuationInfo[7]
        self.netRevenueQ1 = valuationInfo[8]
        self.priceList = self.getPriceInfo()
        self.price = round(self.priceList[-1],2)

    def getPriceInfo(self):
        yahooTicker = "{}.IS".format(self.ticker.upper())
        now = datetime.datetime.now()
        now = now + datetime.timedelta(days=1)
        oneYearAgo = now - datetime.timedelta(days=365)
        stock_data = get_data(ticker=yahooTicker,
                              start_date=oneYearAgo.strftime("%Y/%m/%d"),
                              end_date=now.strftime("%Y/%m/%d"),
                              index_as_date=True,
                              interval='1d')
        close_data = pandas.DataFrame.to_numpy(stock_data)
        return numpy.array([float(x[3]) for x in close_data])



