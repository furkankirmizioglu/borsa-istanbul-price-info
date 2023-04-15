import math
import talib
import time
import requests
from bs4 import BeautifulSoup
import database
from company import Company
from utils import parse_int, suggestion

BALANCE_SHEET_URL = 'https://fintables.com/sirketler/{}/finansal-tablolar/bilanco'
INCOME_STATEMENT_URL = 'https://fintables.com/sirketler/{}/finansal-tablolar/ceyreklik-gelir-tablosu'
PROCESS_TIME_LOG = "İşlem {} saniyede tamamlandı."


def build_database(industry):
    tickers = database.get_tickers_from_industry(industry)
    for ticker in tickers:
        valuation = database.select_valuation(ticker)
        # Eğer valuation_info tablosunda bilanço bilgisi yoksa tablo sorgusundan boş döner.
        # Web scraping ile gerekli bilgiler alınır ve tabloya kaydedilir.
        if len(valuation) == 0:
            if industry == 'Bankacılık':
                balance_sheet_values = balance_sheet_banking(ticker)
            elif industry == 'Sigorta':
                balance_sheet_values = balance_sheet_insurance(ticker)
            else:
                balance_sheet_values = balance_sheet(ticker)
            database.insert_valuation(ticker, balance_sheet_values)
            print("{} için veri işleme tamamlandı.".format(ticker))

    return tickers


# Sigorta şirketleri için bilanço okuma fonksiyonu.
def balance_sheet_insurance(ticker):
    current_ttm_net_profit = 0
    last_ttm_net_profit = 0
    lt_liabilities = 0
    initial_capital = 0
    old_initial_capital = 0
    equity = 0
    main_equity = 0
    latest_balance_sheet_term = ""
    url = BALANCE_SHEET_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for tr_elements in soup.find_all("tr"):
        header = tr_elements.text
        if header.startswith('Kalem'):
            th_elements = tr_elements.find_all_next("th")
            latest_balance_sheet_term = th_elements[1].text
        elif header.startswith('Özkaynaklar'.lower()):
            td_elements = tr_elements.find_all_next("td")
            equity = parse_int(td_elements[1].text)
            main_equity = equity
        elif header.startswith('Ödenmiş Sermaye'.lower()):
            td_elements = tr_elements.find_all_next("td")
            initial_capital = parse_int(td_elements[1].text)
            old_initial_capital = parse_int(td_elements[4].text)
        elif header.startswith('Uzun Vadeli Yükümlülükler Toplamı'.lower()):
            td_elements = tr_elements.find_all_next("td")
            lt_liabilities = parse_int(td_elements[1].text)

    url = INCOME_STATEMENT_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for trElements in soup.find_all("tr"):
        header = trElements.text
        if header.startswith('Dönem Net Karı Veya Zararı'.lower()):
            balanceSheetCells = trElements.find_all_next("td")
            q4 = parse_int(balanceSheetCells[1].text)
            q3 = parse_int(balanceSheetCells[2].text)
            q2 = parse_int(balanceSheetCells[3].text)
            q1 = parse_int(balanceSheetCells[4].text)
            current_ttm_net_profit = q4 + q3 + q2 + q1

            q4_1 = parse_int(balanceSheetCells[5].text)
            q3_1 = parse_int(balanceSheetCells[6].text)
            q2_1 = parse_int(balanceSheetCells[7].text)
            q1_1 = parse_int(balanceSheetCells[8].text)
            last_ttm_net_profit = q4_1 + q3_1 + q2_1 + q1_1

    parameters = (latest_balance_sheet_term, equity, main_equity, initial_capital, old_initial_capital, lt_liabilities,
                  current_ttm_net_profit,
                  last_ttm_net_profit)
    return parameters


def balance_sheet_banking(ticker):
    current_ttm_net_profit = 0
    last_ttm_net_profit = 0
    lt_liabilities = 0
    initial_capital = 0
    old_initial_capital = 0
    equity = 0
    main_equity = 0
    latest_balance_sheet_term = ""

    url = BALANCE_SHEET_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for tr_elements in soup.find_all("tr"):
        header = tr_elements.text
        if header.startswith('Kalem'):
            th_elements = tr_elements.find_all_next("th")
            latest_balance_sheet_term = th_elements[1].text
        elif header.startswith('Özkaynaklar'.lower()):
            td_elements = tr_elements.find_all_next("td")
            equity = parse_int(td_elements[1].text)
            main_equity = equity
        elif header.startswith('Ödenmiş Sermaye'.lower()):
            td_elements = tr_elements.find_all_next("td")
            initial_capital = parse_int(td_elements[1].text)
            old_initial_capital = parse_int(td_elements[4].text)
        elif header.startswith('Uzun Vadeli Yükümlülükler Toplamı'.lower()):
            td_elements = tr_elements.find_all_next("td")
            lt_liabilities = parse_int(td_elements[1].text)

    url = INCOME_STATEMENT_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for trElements in soup.find_all("tr"):
        header = trElements.text
        if header.startswith('Dönem Net Karı Veya Zararı'.lower()):
            balanceSheetCells = trElements.find_all_next("td")
            q4 = parse_int(balanceSheetCells[1].text)
            q3 = parse_int(balanceSheetCells[2].text)
            q2 = parse_int(balanceSheetCells[3].text)
            q1 = parse_int(balanceSheetCells[4].text)
            current_ttm_net_profit = q4 + q3 + q2 + q1

            q4_1 = parse_int(balanceSheetCells[5].text)
            q3_1 = parse_int(balanceSheetCells[6].text)
            q2_1 = parse_int(balanceSheetCells[7].text)
            q1_1 = parse_int(balanceSheetCells[8].text)
            last_ttm_net_profit = q4_1 + q3_1 + q2_1 + q1_1

    parameters = (latest_balance_sheet_term, equity, main_equity, initial_capital, old_initial_capital, lt_liabilities,
                  current_ttm_net_profit,
                  last_ttm_net_profit)
    return parameters


def balance_sheet(ticker):
    current_ttm_net_profit = 0
    last_ttm_net_profit = 0
    lt_liabilities = 0
    initial_capital = 0
    old_initial_capital = 0
    equity = 0
    main_equity = 0
    latest_balance_sheet_term = ""
    url = BALANCE_SHEET_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for tr_elements in soup.find_all("tr"):
        header = tr_elements.text
        if header.startswith('Kalem'):
            th_elements = tr_elements.find_all_next("th")
            latest_balance_sheet_term = th_elements[1].text
        elif header.startswith('Özkaynaklar'.lower()):
            td_elements = tr_elements.find_all_next("td")
            equity = parse_int(td_elements[1].text)
        elif header.startswith('Ana Ortaklığa Ait Özkaynaklar'.lower()):
            td_elements = tr_elements.find_all_next("td")
            main_equity = parse_int(td_elements[1].text)
        elif header.startswith('Ödenmiş Sermaye'.lower()):
            td_elements = tr_elements.find_all_next("td")
            initial_capital = parse_int(td_elements[1].text)
            old_initial_capital = parse_int(td_elements[4].text)
        elif header.startswith('Uzun Vadeli Yükümlülükler'.lower()):
            td_elements = tr_elements.find_all_next("td")
            lt_liabilities = parse_int(td_elements[1].text)

    if main_equity == 0:
        main_equity = equity

    url = INCOME_STATEMENT_URL.format(ticker)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for trElements in soup.find_all("tr"):
        header = trElements.text
        if header.startswith('Ana Ortaklık Payları'.lower()):
            balanceSheetCells = trElements.find_all_next("td")
            q4 = parse_int(balanceSheetCells[1].text)
            q3 = parse_int(balanceSheetCells[2].text)
            q2 = parse_int(balanceSheetCells[3].text)
            q1 = parse_int(balanceSheetCells[4].text)
            current_ttm_net_profit = q4 + q3 + q2 + q1

            q4_1 = parse_int(balanceSheetCells[5].text)
            q3_1 = parse_int(balanceSheetCells[6].text)
            q2_1 = parse_int(balanceSheetCells[7].text)
            q1_1 = parse_int(balanceSheetCells[8].text)
            last_ttm_net_profit = q4_1 + q3_1 + q2_1 + q1_1

    parameters = (latest_balance_sheet_term, equity, main_equity, initial_capital, old_initial_capital, lt_liabilities,
                  current_ttm_net_profit,
                  last_ttm_net_profit)
    return parameters


def long_term_debt_equity_ratio(company):
    return round(company.lt_liabilities / company.equity * 100, 2)


def price_book_ratio(company):
    market_value = company.price * company.initial_capital
    return round(market_value / company.main_equity, 2)


def peg_ratio(company):
    try:
        # Her yıl için hisse başı kâr bilgisi hesaplanıyor.
        EPS_2 = round(company.current_ttm_net_profit / company.initial_capital, 2)
        EPS_1 = round(company.last_ttm_net_profit / company.old_initial_capital, 2)
        # 4 çeyrek için hisse başı kar büyüme oranı % üzerinden hesaplanıyor.
        EPS_GROWTH_RATE = (EPS_2 / EPS_1 - 1) * 100

        # Fiyat / Kazanç oranı hesaplanıyor.
        PE = round(company.price / EPS_2, 2)
        print("{0} F/K: {1} | HBK'22: {2} | HBK'21: {3} | HBK Büyümesi: {4}".format(company.ticker, PE, EPS_2, EPS_1,
                                                                                    EPS_GROWTH_RATE))
        return round(PE / EPS_GROWTH_RATE, 4)
    except Exception as ex:
        print(ex)
        return 0


def rsi_value(company):
    x = talib.RSI(company.prices_list, 14)[-1]
    if not math.isnan(x):
        return round(x, 2)
    else:
        return 0


def lt_debt_equity(company_list):
    lt_list = []
    for company in company_list:
        lt_debt_equity_int = long_term_debt_equity_ratio(company)
        if lt_debt_equity_int > 0:
            lt_list.append((company.ticker, lt_debt_equity_int))

    lt_list.sort(key=lambda x: x[1])
    for idx, lt in enumerate(lt_list):
        # Değerleme puan hesaplanıp tuple'a ekleniyor.
        lt += (len(company_list) - idx,)
        lt_list[idx] = lt
    return lt_list


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
        peg += (len(company_list) - idx,)
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
        rsi += (len(company_list) - idx,)  # Değerleme puanı hesaplanıp tuple'a ekleniyor.
        rsi_ratio_list[idx] = rsi
    return rsi_ratio_list


# LIST OF TUPLES
# TUPLE FORMAT: COMPANY_NAME | P/B | VALUATION SCORE
def pb(company_list):
    price_book_list = []

    for company in company_list:
        price_book_int = price_book_ratio(company)
        print("{0} Piyasa / Defter Değeri: {1}".format(company.ticker, price_book_int))
        if price_book_int > 0:
            price_book_list.append((company.ticker, price_book_int))

    # PD/DD bazında düşükten büyüğe doğru sıralama yapılıyor.
    price_book_list.sort(key=lambda x: x[1])

    for idx, pb in enumerate(price_book_list):
        # Değerleme puan hesaplanıp tuple'a ekleniyor.
        pb += (len(price_book_list) - idx,)
        price_book_list[idx] = pb
    return price_book_list


# Bankacılık harici bütük sektörlerin raporlamasının yapılacağı fonksiyon.
def report(tickers):
    # Her bir metrik için ayrı tuple objeleri oluşturuyorum.
    # Bu bilgileri daha sonra bir dataframe'de birleştiriyorum.

    company_list = []
    for ticker in tickers:
        company = Company(ticker=ticker)
        company_list.append(company)

    peg_list = peg(company_list)
    # rsi_list = rsi(company_list)
    pb_list = pb(company_list)
    lt_debt_list = lt_debt_equity(company_list)

    response_data = []

    # Her bir hisse için metrik tuple'larında gezerek o değerleri alıyorum.
    for company in company_list:
        peg_filter = [item for item in peg_list if item[0] == company.ticker]
        if len(peg_filter) == 0:
            peg_filter = [(company.ticker, 0, 0)]

        # rsi_filter = [item for item in rsi_list if item[0] == company.ticker]
        # if len(rsi_filter) == 0:
        # rsi_filter = [(company.ticker, 'N/A', 0)]

        pb_filter = [item for item in pb_list if item[0] == company.ticker]
        if len(pb_filter) == 0:
            pb_filter = [(company.ticker, 'N/A', 0)]

        ltde_filter = [item for item in lt_debt_list if item[0] == company.ticker]
        if len(ltde_filter) == 0:
            ltde_filter = [(company.ticker, 'N/A', 0)]

        # Her bir metrik için değerleme puanları toplanır, hisse sayısı * metrik sayısına bölünür ve 100'e endekslenir.
        score = round((peg_filter[0][2] + pb_filter[0][2] + ltde_filter[0][2]) / (len(tickers) * 3) * 100, 2)

        element = (
            company.ticker,
            company.name,
            company.latest_balance_sheet_term,
            company.price,
            pb_filter[0][1],
            peg_filter[0][1],
            ltde_filter[0][1],
            score,
            suggestion(score))

        # DataFrame'in veri kaynağı olan listeye eklenir.
        response_data.append(element)

    # Veri kaynağının değerleme puanı bazında büyükten küçüğe doğru sıralanır.
    response_data.sort(key=lambda x: (-x[7], x[5]))
    return response_data


# Uzun Vadeli Borç / Özkaynak Oranı henüz hesaplanamadığından
# bu metriğin N/A olarak gösterilmesi ve hesaba katılmaması için
# ayrı raporlama fonksiyonu yazdım.
def banking_report(tickers):
    # Her bir metrik için ayrı tuple objeleri oluşturuyorum.
    # Bu bilgileri daha sonra bir dataframe'de birleştiriyorum.

    company_list = []
    for ticker in tickers:
        company = Company(ticker=ticker)
        company_list.append(company)

    peg_list = peg(company_list)
    # rsi_list = rsi(company_list)
    pb_list = pb(company_list)
    lt_debt_list = lt_debt_equity(company_list)

    response_data = []

    # Her bir hisse için metrik tuple'larında gezerek o değerleri alıyorum.
    for company in company_list:
        peg_filter = [item for item in peg_list if item[0] == company.ticker]
        if len(peg_filter) == 0:
            peg_filter = [(company.ticker, 0, 0)]

        # rsi_filter = [item for item in rsi_list if item[0] == company.ticker]
        # if len(rsi_filter) == 0:
        # rsi_filter = [(company.ticker, 'N/A', 0)]

        pb_filter = [item for item in pb_list if item[0] == company.ticker]
        if len(pb_filter) == 0:
            pb_filter = [(company.ticker, 'N/A', 0)]

        ltde_filter = [item for item in lt_debt_list if item[0] == company.ticker]
        if len(ltde_filter) == 0:
            ltde_filter = [(company.ticker, 'N/A', 0)]

        # Her bir metrik için değerleme puanları toplanır, hisse sayısı * metrik sayısına bölünür ve 100'e endekslenir.
        score = round((peg_filter[0][2] + pb_filter[0][2] + ltde_filter[0][2]) / (len(tickers) * 2) * 100, 2)

        element = (
            company.ticker, company.name, company.latest_balance_sheet_term, company.price, pb_filter[0][1],
            peg_filter[0][1], ltde_filter[0][1], score,
            suggestion(score))

        # DataFrame'in veri kaynağı olan listeye eklenir.
        response_data.append(element)

    # Veri kaynağının değerleme puanı bazında büyükten küçüğe doğru sıralanır.
    response_data.sort(key=lambda x: (-x[7], x[5]))
    return response_data


def main_report(industry, tickers):
    if industry == 'Bankacılık':
        return banking_report(tickers=tickers)
    else:
        return report(tickers)


def process(industry):
    start = time.perf_counter()
    ticker_list = build_database(industry)
    response = main_report(industry, ticker_list)
    finish = time.perf_counter()
    print(PROCESS_TIME_LOG.format(round(finish - start, 2)))
    return response
