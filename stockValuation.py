import datetime
import math
import os
import time
import pandas
import requests
import talib
import database
import utils
from company import Company
from bs4 import BeautifulSoup

BALANCE_SHEET_URL = 'https://fintables.com/sirketler/{}/finansal-tablolar/bilanco'
INCOME_STATEMENT_URL = 'https://fintables.com/sirketler/{}/finansal-tablolar/ceyreklik-gelir-tablosu'
industryInfo = 'Perakende'
PROCESS_TIME_LOG = "İşlem {} saniyede tamamlandı."


def initialize(industry):
    tickerList = database.selectFromCompanyInfoIndustry(industry)
    if len(tickerList) == 0:
        database.readExcel()
        tickerList = database.selectFromCompanyInfoIndustry(industry)
        for ticker in tickerList:
            balanceSheetValues = fetch_balance_sheet(ticker)
            database.insertCompanyValuationInfo(ticker, balanceSheetValues)
            print("{} hissesi için veri toplama işlemi tamamlandı.".format(ticker))
    return tickerList


def fetch_balance_sheet(ticker):
    netRevenueQ4 = 0
    netRevenueQ3 = 0
    netRevenueQ2 = 0
    netRevenueQ1 = 0

    initialCapital = 0
    equity = 0

    url = BALANCE_SHEET_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for trElements in soup.find_all("tr"):
        header = trElements.text
        if header.startswith('Özkaynaklar'.lower()):
            tdElements = trElements.find_all_next("td")
            equity = utils.parseInt(tdElements[1].text)
        elif header.startswith('Ödenmiş Sermaye'.lower()):
            tdElements = trElements.find_all_next("td")
            initialCapital = utils.parseInt(tdElements[1].text)

    url = INCOME_STATEMENT_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for trElements in soup.find_all("tr"):
        header = trElements.text
        if header.startswith('Ana Ortaklık Payları'.lower()) or header.startswith('Dönem Net Karı Veya Zararı'.lower()):
            tdElements = trElements.find_all_next("td")
            netRevenueQ4 = utils.parseInt(tdElements[1].text) + utils.parseInt(tdElements[2].text) + utils.parseInt(
                tdElements[3].text) + utils.parseInt(tdElements[4].text)
            netRevenueQ3 = utils.parseInt(tdElements[2].text) + utils.parseInt(tdElements[3].text) + utils.parseInt(
                tdElements[4].text) + utils.parseInt(tdElements[5].text)
            netRevenueQ2 = utils.parseInt(tdElements[3].text) + utils.parseInt(tdElements[4].text) + utils.parseInt(
                tdElements[5].text) + utils.parseInt(tdElements[6].text)
            netRevenueQ1 = utils.parseInt(tdElements[4].text) + utils.parseInt(tdElements[5].text) + utils.parseInt(
                tdElements[6].text) + utils.parseInt(tdElements[7].text)

    parameters = (equity, initialCapital, netRevenueQ4, netRevenueQ3, netRevenueQ2, netRevenueQ1)
    return parameters


def price_book_ratio(company):
    market_value = company.price * company.initialCapitalAmount
    return round(market_value / company.equityAmount, 2)


def peg_ratio(company):
    # Her bir çeyrek için hisse başı kâr bilgisi hesaplanıyor.
    EPSQ4 = company.netRevenueQ4 / company.initialCapitalAmount
    EPSQ3 = company.netRevenueQ3 / company.initialCapitalAmount
    EPSQ2 = company.netRevenueQ2 / company.initialCapitalAmount
    EPSQ1 = company.netRevenueQ1 / company.initialCapitalAmount

    # 4 çeyrek için hisse başı kar büyüme oranı % üzerinden hesaplanıyor.
    EPS_GROWTH_RATE = round(((EPSQ4 / EPSQ3 - 1 + EPSQ3 / EPSQ2 - 1 + EPSQ2 / EPSQ1 - 1) / 3) * 100, 2)

    # Fiyat / Kazanç oranı hesaplanıyor.
    PE = round(company.price / EPSQ4, 2)

    if 0 < PE < 40:
        if EPS_GROWTH_RATE > 0:
            return round(PE / EPS_GROWTH_RATE, 2)
        else:
            print("{0} için anlamsız HBK büyüme oranı: {1}".format(company.ticker, EPS_GROWTH_RATE))
            return 0
    else:
        print("{0} için anlamsız F/K oranı: {1}".format(company.ticker, PE))
        return 0


# LIST OF TUPLES
# TUPLE FORMAT: COMPANY NAME | PEG RATIO | VALUATION SCORE
def peg(tickerList):
    pegRatioList = []
    peg_sum = 0
    for ticker in tickerList:
        company = Company(ticker)
        PEG = peg_ratio(company)
        if PEG > 0:
            pegRatioList.append((company.ticker, PEG))
            peg_sum += PEG
        else:
            print("{0} için anlamsız PEG oranı: {1}".format(company.ticker, PEG))

    avg = peg_sum / len(pegRatioList)  # Sektörün ortalama PEG oranı hesaplanıyor.
    print("{} Sektörü Ortalama PEG Oranı: {}".format(industryInfo, round(avg, 2)))

    # Sektörel PEG Çarpanı bazında sıralama yapılıyor.
    # Bu sıraya göre yüksekten düşüğe doğru puanlama yapılacak.
    pegRatioList.sort(key=lambda x: x[1])

    for idx, peg in enumerate(pegRatioList):
        peg += (abs(pegRatioList.index(peg) - len(pegRatioList)),)  # Değerleme puanı hesaplanıp tuple'a ekleniyor.
        pegRatioList[idx] = peg
    return pegRatioList


# LIST OF TUPLES
# TUPLE FORMAT: COMPANY_NAME | RSI | VALUATION SCORE
def rsi(tickerList):
    rsiRatioList = []
    for ticker in tickerList:
        objCompany = Company(ticker)
        RSI = talib.RSI(objCompany.priceList, 14)[-1]
        if not math.isnan(RSI):
            RSI = round(RSI, 2)
            rsiRatioList.append((objCompany.ticker, RSI))
    rsiRatioList.sort(key=lambda x: x[1])

    for idx, rsi in enumerate(rsiRatioList):
        rsi += (abs(rsiRatioList.index(rsi) - len(rsiRatioList)),)  # Değerleme puanı hesaplanıp tuple'a ekleniyor.
        rsiRatioList[idx] = rsi
    return rsiRatioList


# LIST OF TUPLES
# TUPLE FORMAT: COMPANY_NAME | P/B | VALUATION SCORE
def priceBook(tickerList):
    priceBookList = []
    priceBookSum = 0

    for ticker in tickerList:
        company = Company(ticker)
        priceBookInt = price_book_ratio(company)
        priceBookList.append((company.ticker, priceBookInt))
        priceBookSum += priceBookInt

    avg = priceBookSum / len(priceBookList)
    print("{} Sektörü Ortalama PD/DD Oranı: {}".format(industryInfo, round(avg, 2)))

    # PD/DD bazında sıralama yapılıyor.
    # Bu sıraya göre yüksekten düşüğe doğru puanlama yapılacak.
    priceBookList.sort(key=lambda x: x[1])

    for idx, pddd in enumerate(priceBookList):
        pddd += (abs(priceBookList.index(pddd) - len(priceBookList)),)  # Değerleme puanı hesaplanıp tuple'a ekleniyor.
        priceBookList[idx] = pddd
    return priceBookList


def onlyPegReport(tickerList):
    data = []
    pegList = peg(tickerList)

    for ticker in tickerList:
        pegfilter = [item for item in pegList if item[0] == ticker]
        if len(pegfilter) == 0:
            pegfilter = [(ticker, 0, 0, 0)]
        pegRatio = pegfilter[0][1]
        industrialMultiplier = pegfilter[0][2]
        totalScore = pegfilter[0][3]
        element = (ticker, pegRatio, industrialMultiplier, totalScore)
        data.append(element)

    data.sort(key=lambda x: x[3], reverse=True)
    reportColumns = ['Şirket', 'PEG Oranı', 'Sektörel PEG Çarpanı', 'Değerleme Puanı']
    df = pandas.DataFrame(data=data, columns=reportColumns)
    df.set_index('Şirket', inplace=True)
    fileHeader = industryInfo
    if fileHeader.__contains__('/'):
        fileHeader = industryInfo.replace('/', '-')
    fileName = "{0} Sektörü Değerleme Raporu_{1}.xlsx".format(fileHeader, datetime.datetime.now().strftime('%Y%m%d'))
    df.to_excel(fileName)
    os.startfile(fileName)


def multiReport(tickerList):
    # Her bir metrik için ayrı tuple objeleri oluşturuyorum.
    # Bu bilgileri daha sonra bir dataframe'de birleştiriyorum.

    pegList = peg(tickerList)
    rsiList = rsi(tickerList)
    priceBookList = priceBook(tickerList)

    excelData = []  # Excel dosyasının veri kaynağı bu array olacak.

    # Her bir hisse için metrik tuple'larında gezerek o değerleri alıyorum.
    for ticker in tickerList:
        pegfilter = [item for item in pegList if item[0] == ticker]
        if len(pegfilter) == 0:
            pegfilter = [(ticker, 0, 0, 0)]

        rsifilter = [item for item in rsiList if item[0] == ticker]
        if len(rsifilter) == 0:
            rsifilter = [(ticker, 0, 0)]

        pBfilter = [item for item in priceBookList if item[0] == ticker]
        if len(pBfilter) == 0:
            pBfilter = [(ticker, 0, 0)]

        # Şirket adı bilgisini almak için COMPANY_INFO tablosuna gidilir.
        companyName = database.selectFromCompanyInfoTicker(ticker)[3]

        # Filtrelenmiş satırlardan değerler alınır.
        pbValue = pBfilter[0][1]
        pegRatio = pegfilter[0][1]
        rsiValue = rsifilter[0][1]

        # Her bir metrik için değerleme puanları toplanır, hisse sayısı * metrik sayısına bölünür ve 100'e endekslenir.
        totalScore = round((pegfilter[0][2] + rsifilter[0][2] + pBfilter[0][2]) / (len(tickerList) * 3) * 100, 0)
        element = (ticker, companyName, pbValue, pegRatio, rsiValue, totalScore)

        # DataFrame'in veri kaynağı olan listeye eklenir.
        excelData.append(element)

    # Veri kaynağının değerleme puanı bazında büyükten küçüğe doğru sıralanır.
    excelData.sort(key=lambda x: x[5], reverse=True)

    # Excel'deki başlık bilgileri set edilir.
    reportColumns = ['Hisse Senedi Kodu', 'Şirket Unvanı', 'Piyasa / Defter Değeri', 'PEG Oranı', 'Son RSI Değeri',
                     'Değerleme Puanı (%)']
    df = pandas.DataFrame(data=excelData, columns=reportColumns)
    df.set_index('Hisse Senedi Kodu', inplace=True)
    print(df)

    # Dosya adı Windows standartlarına göre düzenlenir ve excel çıktısı üretilir. Oluşan çıktı otomatik açılır.

    fileHeader = industryInfo
    if fileHeader.__contains__('/'):
        fileHeader = industryInfo.replace('/', '-')
    fileName = "{0} Sektörü Değerleme Raporu_{1}.xlsx".format(fileHeader, datetime.datetime.now().strftime('%Y%m%d'))
    df.to_excel(fileName)
    os.startfile(fileName)


def main():
    startTime = time.perf_counter()
    tickerList = initialize(industryInfo)
    multiReport(tickerList)
    finishTime = time.perf_counter()
    print(PROCESS_TIME_LOG.format(round(finishTime - startTime, 2)))


main()
