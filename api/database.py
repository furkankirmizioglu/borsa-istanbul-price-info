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
                                    EQUITY REAL,
                                    INITIAL_CAPITAL REAL,
                                    NET_PROFIT_Q4 REAL,
                                    NET_PROFIT_Q3 REAL,
                                    NET_PROFIT_Q2 REAL,
                                    NET_PROFIT_Q1 REAL
                                    ); """
SQL_SELECT_FROM_COMPANY_VALUATION_INFO = ''' SELECT * FROM COMPANY_VALUATION_INFO WHERE TICKER=? '''
SQL_INSERT_COMPANY_VALUATION_INFO = ''' INSERT INTO COMPANY_VALUATION_INFO (
GUID,
LAST_UPDATED,
TICKER,
EQUITY,
INITIAL_CAPITAL,
NET_PROFIT_Q4,
NET_PROFIT_Q3,
NET_PROFIT_Q2,
NET_PROFIT_Q1) 
VALUES(?,?,?,?,?,?,?,?,?); '''
SQL_UPDATE_COMPANY_VALUATION_INFO = ''' UPDATE COMPANY_VALUATION_INFO SET {} WHERE TICKER=?'''

UPDATE_COLUMNS: list[str] = ['LAST_UPDATED', 'EQUITY', 'INITIAL_CAPITAL', 'NET_PROFIT_Q4',
                             'NET_PROFIT_Q3', 'NET_PROFIT_Q2', 'NET_PROFIT_Q1']

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
SQL_SELECT_COMPANY_INFO_INDUSTRY = ''' SELECT TICKER FROM COMPANY_INFO WHERE INDUSTRY=? ORDER BY TICKER '''
SQL_INSERT_COMPANY_INFO = ''' INSERT INTO COMPANY_INFO (
GUID,
LAST_UPDATED,
TICKER,
COMPANY_NAME,
INDUSTRY)
VALUES(?,?,?,?,?); '''


def create_connection():
    try:
        conn = sqlite3.connect(database)
        return conn
    except Exception as ex:
        print(ex)


def create_company_info_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_COMPANY_INFO_TABLE)
        conn.close()
    except Exception as e:
        print(e)


def get_company(ticker):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_SELECT_COMPANY_INFO_TICKER, (ticker,))
        rows = cursor.fetchall()
        conn.close()
        return rows[0]
    except Exception as ex:
        print(ex)
        conn.close()


def get_industries():
    conn = create_connection()
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


def get_all_tickers():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_SELECT_COMPANY_INFO_FETCH_ALL_TICKERS)
        rows = cursor.fetchall()
        rows = [''.join(i) for i in rows]
        conn.close()
        return rows
    except Exception as ex:
        print(ex)
        conn.close()


def get_tickers_from_industry(industry):
    conn = create_connection()
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


def insert_company_info(ticker, company_name, industry):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        create_company_info_table()
        parameters = (
            random.randint(1000000000, 9999999999),
            now(),
            ticker,
            company_name,
            industry)
        cursor.execute(SQL_INSERT_COMPANY_INFO, parameters)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def create_company_valuation_info_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_CREATE_COMPANY_VALUATION_INFO_TABLE)
        conn.close()
    except Exception as e:
        print(e)


def select_valuation(ticker):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(SQL_SELECT_FROM_COMPANY_VALUATION_INFO, (ticker,))
        rows = cursor.fetchall()
        conn.close()
        if len(rows) == 0:
            return rows
        else:
            return rows[0]
    except Exception as ex:
        print(ex)
        conn.close()


def insert_valuation(ticker, bs_parameters):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        create_company_valuation_info_table()
        parameters = (
            random.randint(1000000000, 9999999999),
            now(),
            ticker,
            bs_parameters[0],
            bs_parameters[1],
            bs_parameters[2],
            bs_parameters[3],
            bs_parameters[4],
            bs_parameters[5])
        cursor.execute(SQL_INSERT_COMPANY_VALUATION_INFO, parameters)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def update_valuation(ticker, values):
    conn = create_connection()
    cursor = conn.cursor()
    values = (now(),) + values
    query = ""
    for column in UPDATE_COLUMNS:
        query = query + column + ' = ?,'
    query = query[:-1]
    try:
        values += (ticker,)
        query = SQL_UPDATE_COMPANY_VALUATION_INFO.format(query)
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)


def read_excel():
    df = pd.read_excel(excel)
    for data in df.index:
        ticker = df['Kod'][data]
        company_name = df['Hisse Adı'][data]
        industry = df['Sektör'][data]
        insert_company_info(ticker, company_name, industry)
