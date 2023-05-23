import valuation
import flask
from flask import Flask, request
from flask_restful import Api
import datetime
from numpy import array, logical_not, isnan
import pandas
import database
from yahoo_fin.stock_info import get_data

app = Flask(__name__)
api = Api(app)


@app.route('/getIndustries', methods=['GET'])
def get_industries():
    database.check_table_existence()
    industry_info = database.get_industries()
    if len(industry_info) == 0:
        database.read_excel()
        industry_info = database.get_industries()

    json = []
    for x in industry_info:
        json.append({"industry": x})

    response = flask.jsonify(json)
    response.headers.add_header("Access-Control-Allow-Origin", "*")
    return response


@app.route('/valuation', methods=['POST'])
def get_valuation():
    industry = request.args.get('industry')
    report = valuation.process(industry)
    response = flask.jsonify(report)
    response.headers.add_header("Access-Control-Allow-Origin", "*")
    return response


@app.route('/price', methods=['POST'])
def get_current_price():
    yahoo_ticker = "{}.IS".format(request.args.get('ticker'))
    now = datetime.datetime.now() + datetime.timedelta(days=1)
    one_year_ago = now - datetime.timedelta(days=365)
    stock_data = get_data(ticker=yahoo_ticker,
                          start_date=one_year_ago.strftime("%Y/%m/%d"),
                          end_date=now.strftime("%Y/%m/%d"),
                          index_as_date=True,
                          interval='1d')
    close_data = pandas.DataFrame.to_numpy(stock_data)
    price_list = array([float(x[3]) for x in close_data])
    responseDict = {
        "price": round(price_list[-1], 2)
    }

    response = flask.jsonify(responseDict)
    response.headers.add_header("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(host="localhost", port=8090)
