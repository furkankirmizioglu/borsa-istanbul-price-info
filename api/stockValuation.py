import math
import talib
import time
import requests
from bs4 import BeautifulSoup
import database
from company import Company
from utils import parse_int

BALANCE_SHEET_URL = 'https://fintables.com/sirketler/{}/finansal-tablolar/bilanco'
INCOME_STATEMENT_URL = 'https://fintables.com/sirketler/{}/finansal-tablolar/ceyreklik-gelir-tablosu'
industryInfo = 'Meşrubat / İçecek'
PROCESS_TIME_LOG = "İşlem {} saniyede tamamlandı."


def build_database(industry):
    tickers = database.get_tickers_from_industry(industry)
    for ticker in tickers:
        valuation = database.select_valuation(ticker)
        if valuation is None or len(valuation) == 0:
            balance_sheet_values = fetch_balance_sheet(ticker)
            database.insert_valuation(ticker, balance_sheet_values)
            print("{} için veri işleme tamamlandı.".format(ticker))

    return tickers


def fetch_balance_sheet(ticker):
    net_profit_q4 = 0
    net_profit_q3 = 0
    net_profit_q2 = 0
    net_profit_q1 = 0

    initial_capital = 0
    equity = 0

    try:
        url = BALANCE_SHEET_URL.format(ticker)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        for tr_elements in soup.find_all("tr"):
            header = tr_elements.text
            if header.startswith('Özkaynaklar'.lower()):
                td_elements = tr_elements.find_all_next("td")
                equity = parse_int(td_elements[1].text)
            elif header.startswith('Ödenmiş Sermaye'.lower()):
                td_elements = tr_elements.find_all_next("td")
                initial_capital = parse_int(td_elements[1].text)

        url = INCOME_STATEMENT_URL.format(ticker)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        for tr_elements in soup.find_all("tr"):
            header = tr_elements.text
            if header.startswith('Ana Ortaklık Payları'.lower()) or header.startswith(
                    'Dönem Net Karı Veya Zararı'.lower()):
                td_elements = tr_elements.find_all_next("td")
                net_profit_q4 = parse_int(td_elements[1].text) + parse_int(td_elements[2].text) + parse_int(
                    td_elements[3].text) + parse_int(td_elements[4].text)
                net_profit_q3 = parse_int(td_elements[2].text) + parse_int(td_elements[3].text) + parse_int(
                    td_elements[4].text) + parse_int(td_elements[5].text)
                net_profit_q2 = parse_int(td_elements[3].text) + parse_int(td_elements[4].text) + parse_int(
                    td_elements[5].text) + parse_int(td_elements[6].text)
                net_profit_q1 = parse_int(td_elements[4].text) + parse_int(td_elements[5].text) + parse_int(
                    td_elements[6].text) + parse_int(td_elements[7].text)

        parameters = (equity, initial_capital, net_profit_q4, net_profit_q3, net_profit_q2, net_profit_q1)
        return parameters
    except Exception as ex:
        print(ex)


def price_book_ratio(company):
    market_value = company.price * company.initial_capital
    return round(market_value / company.equity, 2)


def peg_ratio(company):
    try:
        # Her bir çeyrek için hisse başı kâr bilgisi hesaplanıyor.
        EPSQ4 = company.net_profit_q4 / company.initial_capital
        EPSQ3 = company.net_profit_q3 / company.initial_capital
        EPSQ2 = company.net_profit_q2 / company.initial_capital
        EPSQ1 = company.net_profit_q1 / company.initial_capital

        DELTA_3 = (EPSQ4 - EPSQ3) / abs(EPSQ3)
        DELTA_2 = (EPSQ3 - EPSQ2) / abs(EPSQ2)
        DELTA_1 = (EPSQ2 - EPSQ1) / abs(EPSQ1)

        # 4 çeyrek için hisse başı kar büyüme oranı % üzerinden hesaplanıyor.
        EPS_GROWTH_RATE = ((DELTA_3 + DELTA_2 + DELTA_1) / 3) * 100

        # Fiyat / Kazanç oranı hesaplanıyor.
        PE = company.price / EPSQ4
        return round(PE / EPS_GROWTH_RATE, 2)
    except Exception as ex:
        print(ex)
        return 0


def rsi_value(company):
    x = talib.RSI(company.prices_list, 14)[-1]
    if not math.isnan(x):
        return round(x, 2)
    else:
        return 0


# LIST OF TUPLES
# TUPLE FORMAT: COMPANY NAME | PEG RATIO | VALUATION SCORE
def peg(company_list):
    peg_ratio_list = []
    for company in company_list:
        PEG = peg_ratio(company)
        if PEG > 0:
            peg_ratio_list.append((company.ticker, PEG))
        else:
            print("{0} için anlamsız PEG oranı: {1}".format(company.ticker, PEG))

    # PEG bazında düşükten yükseğe doğru sıralama yapılıyor. Bu sıraya göre puanlama yapılacak.
    peg_ratio_list.sort(key=lambda x: x[1])

    for idx, peg in enumerate(peg_ratio_list):
        # Değerleme puanı hesaplanıp tuple'a ekleniyor.
        peg += (len(peg_ratio_list) - peg_ratio_list.index(peg),)
        peg_ratio_list[idx] = peg
    return peg_ratio_list


# LIST OF TUPLES
# TUPLE FORMAT: COMPANY_NAME | RSI | VALUATION SCORE
def rsi(company_list):
    rsi_ratio_list = []
    for company in company_list:
        rsi_ratio_list.append((company.ticker, rsi_value(company)))
    rsi_ratio_list.sort(key=lambda x: x[1])
    for idx, rsi in enumerate(rsi_ratio_list):
        rsi += (len(rsi_ratio_list) - rsi_ratio_list.index(rsi),)  # Değerleme puanı hesaplanıp tuple'a ekleniyor.
        rsi_ratio_list[idx] = rsi
    return rsi_ratio_list


# LIST OF TUPLES
# TUPLE FORMAT: COMPANY_NAME | P/B | VALUATION SCORE
def pb(company_list):
    price_book_list = []

    for company in company_list:
        price_book_int = price_book_ratio(company)
        if price_book_int > 0:
            price_book_list.append((company.ticker, price_book_int))

    # PD/DD bazında düşükten büyüğe doğru sıralama yapılıyor.
    price_book_list.sort(key=lambda x: x[1])

    for idx, pb in enumerate(price_book_list):
        # Değerleme puan hesaplanıp tuple'a ekleniyor.
        pb += (len(price_book_list) - price_book_list.index(pb),)
        price_book_list[idx] = pb
    return price_book_list


def report(tickers):
    # Her bir metrik için ayrı tuple objeleri oluşturuyorum.
    # Bu bilgileri daha sonra bir dataframe'de birleştiriyorum.

    company_list = []
    for ticker in tickers:
        company = Company(ticker=ticker)
        company_list.append(company)

    peg_list = peg(company_list)
    rsi_list = rsi(company_list)
    pb_list = pb(company_list)

    response_data = []

    # Her bir hisse için metrik tuple'larında gezerek o değerleri alıyorum.
    for company in company_list:
        peg_filter = [item for item in peg_list if item[0] == company.ticker]
        if len(peg_filter) == 0:
            peg_filter = [(company.ticker, 0, 0, 0)]

        rsi_filter = [item for item in rsi_list if item[0] == company.ticker]
        if len(rsi_filter) == 0:
            rsi_filter = [(company.ticker, 0, 0)]

        pb_filter = [item for item in pb_list if item[0] == company.ticker]
        if len(pb_filter) == 0:
            pb_filter = [(company.ticker, 0, 0)]

        # Her bir metrik için değerleme puanları toplanır, hisse sayısı * metrik sayısına bölünür ve 100'e endekslenir.
        score = round((peg_filter[0][2] + rsi_filter[0][2] + pb_filter[0][2]) / (len(tickers) * 3) * 100, 2)

        if score > 80:
            suggestion = "Güçlü Al"
        elif 70 < score < 80:
            suggestion = "Al"
        elif 50 < score < 70:
            suggestion = "Nötr"
        else:
            suggestion = "Sat"

        element = (company.ticker, company.name, pb_filter[0][1], peg_filter[0][1], rsi_filter[0][1], score, suggestion)

        # DataFrame'in veri kaynağı olan listeye eklenir.
        response_data.append(element)

    # Veri kaynağının değerleme puanı bazında büyükten küçüğe doğru sıralanır.
    response_data.sort(key=lambda x: (-x[5], x[3]))

    return response_data


def process(industry):
    start = time.perf_counter()
    ticker_list = build_database(industry)
    response = report(ticker_list)
    finish = time.perf_counter()
    print(PROCESS_TIME_LOG.format(round(finish - start, 2)))
    return response
