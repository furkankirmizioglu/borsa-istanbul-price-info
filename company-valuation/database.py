import os
import random
import sqlite3
from utils import now
import pandas as pd

path = os.path.dirname(__file__)
database = path + "/data/CompanyValuation.db"
excel = path + "/data/şirketler.xlsx"

SQL_CREATE_COMPANY_VALUATION_INFO_TABLE = """ CREATE TABLE IF NOT EXISTS COMPANY_VALUATION_INFO (
                                    GUID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                                    LAST_UPDATED TEXT,
                                    TICKER TEXT,
                                    EQUITY_AMOUNT REAL,
                                    INITIAL_CAPITAL_AMOUNT REAL,
                                    NET_REVENUE_Q4 REAL,
                                    NET_REVENUE_Q3 REAL,
                                    NET_REVENUE_Q2 REAL,
                                    NET_REVENUE_Q1 REAL
                                    ); """
SQL_SELECT_FROM_COMPANY_VALUATION_INFO = ''' SELECT * FROM COMPANY_VALUATION_INFO WHERE TICKER=? '''
SQL_INSERT_COMPANY_VALUATION_INFO = ''' INSERT INTO COMPANY_VALUATION_INFO (
GUID,
LAST_UPDATED,
TICKER,
EQUITY_AMOUNT,
INITIAL_CAPITAL_AMOUNT,
NET_REVENUE_Q4,
NET_REVENUE_Q3,
NET_REVENUE_Q2,
NET_REVENUE_Q1) 
VALUES(?,?,?,?,?,?,?,?,?); '''
SQL_UPDATE_COMPANY_VALUATION_INFO = ''' UPDATE COMPANY_VALUATION_INFO SET {} WHERE TICKER=?'''

UPDATE_COLUMNS: list[str] = ['LAST_UPDATED', 'EQUITY_AMOUNT', 'INITIAL_CAPITAL_AMOUNT', 'NET_REVENUE_Q4',
                             'NET_REVENUE_Q3', 'NET_REVENUE_Q2', 'NET_REVENUE_Q1']

SQL_CREATE_COMPANY_INFO_TABLE = """CREATE TABLE IF NOT EXISTS COMPANY_INFO (
                                    GUID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                                    LAST_UPDATED TEXT,
                                    TICKER TEXT,
                                    COMPANY_NAME TEXT,
                                    INDUSTRY TEXT
                                    ); """

SQL_SELECT_COMPANY_INFO_FETCH_ALL_INDUSTRIES = ''' SELECT DISTINCT INDUSTRY FROM COMPANY_INFO ORDER BY INDUSTRY '''
SQL_SELECT_COMPANY_INFO_FETCH_ALL_TICKERS = ''' SELECT DISTINCT TICKER FROM COMPANY_INFO ORDER BY TICKER '''
SQL_SELECT_COMPANY_INFO_TICKER = ''' SELECT * FROM COMPANY_INFO WHERE TICKER=? '''
SQL_SELECT_COMPANY_INFO_INDUSTRY = ''' SELECT TICKER FROM COMPANY_INFO WHERE INDUSTRY=? '''
SQL_INSERT_COMPANY_INFO = ''' INSERT INTO COMPANY_INFO (
GUID,
LAST_UPDATED,
TICKER,
COMPANY_NAME,
INDUSTRY)
VALUES(?,?,?,?,?); '''


def createConnection():
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except Exception as ex:
        print(ex)
    return conn


def createCompanyInfoTable():
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_COMPANY_INFO_TABLE)
        conn.close();
    except Exception as e:
        print(e)


def selectFromCompanyInfoTicker(ticker):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_SELECT_COMPANY_INFO_TICKER, (ticker,))
        rows = cursor.fetchall()
        conn.close()
        return rows[0]
    except Exception as ex:
        print(ex)
        conn.close()


def selectFromCompanyInfoIndustriesList():
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_SELECT_COMPANY_INFO_FETCH_ALL_INDUSTRIES)
        rows = cursor.fetchall()
        rows = [''.join(i) for i in rows]
        conn.close()
        return rows
    except Exception as ex:
        print(ex)
        conn.close()


def selectFromCompanyInfoIndustry(industry):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_SELECT_COMPANY_INFO_INDUSTRY, (industry,))
        rows = cursor.fetchall()
        rows = [''.join(i) for i in rows]
        conn.close()
        return rows
    except Exception as ex:
        print(ex)
        conn.close()


def insertCompanyInfo(ticker, companyName, industry):
    conn = createConnection();
    cursor = conn.cursor();
    try:
        createCompanyInfoTable()
        parameters = (
            random.randint(1000000000, 9999999999),
            now(),
            ticker,
            companyName,
            industry)
        cursor.execute(SQL_INSERT_COMPANY_INFO, parameters)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def createCompanyValuationInfoTable():
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_COMPANY_VALUATION_INFO_TABLE)
        conn.close();
    except Exception as e:
        print(e)


def selectFromCompanyValuationInfo(ticker):
    conn = createConnection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_SELECT_FROM_COMPANY_VALUATION_INFO, (ticker,))
        rows = cursor.fetchall()
        conn.close()
        return rows[0]
    except Exception as ex:
        print(ex)
        conn.close()


def insertCompanyValuationInfo(ticker, balanceSheetParameters):
    conn = createConnection();
    cursor = conn.cursor();
    try:
        createCompanyValuationInfoTable()
        parameters = (
            random.randint(1000000000, 9999999999),
            now(),
            ticker,
            balanceSheetParameters[0],
            balanceSheetParameters[1],
            balanceSheetParameters[2],
            balanceSheetParameters[3],
            balanceSheetParameters[4],
            balanceSheetParameters[5])
        cursor.execute(SQL_INSERT_COMPANY_VALUATION_INFO, parameters)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def updateCompanyValuationInfo(ticker, balanceSheetValues):
    conn = createConnection();
    cursor = conn.cursor();
    balanceSheetValues = (now(),) + balanceSheetValues
    query = ""
    for column in UPDATE_COLUMNS:
        query = query + column + ' = ?,'
    query = query[:-1]
    try:
        balanceSheetValues += (ticker,)
        query = SQL_UPDATE_COMPANY_VALUATION_INFO.format(query)
        cursor.execute(query, balanceSheetValues)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def readExcel():
    dataFrame = pd.read_excel(excel)
    for data in dataFrame.index:
        ticker = dataFrame['Kod'][data]
        companyName = dataFrame['Hisse Adı'][data]
        industry = dataFrame['Sektör'][data]
        insertCompanyInfo(ticker, companyName, industry)
