import flask
from talib import RSI
from flask import Flask, request
from flask_restful import Api
from datetime import datetime, timedelta
from numpy import array
from pandas import DataFrame
from yahoo_fin.stock_info import get_data

app = Flask(__name__)
api = Api(app)


@app.route('/price', methods=['POST'])
def get_current_price():
    now = datetime.now() + timedelta(days=1)
    one_year_ago = now - timedelta(days=365)
    stock_data = get_data(ticker="{}.IS".format(request.args.get('ticker')),
                          start_date=one_year_ago.strftime("%Y/%m/%d"),
                          end_date=now.strftime("%Y/%m/%d"),
                          index_as_date=True,
                          interval='1d')
    stock_data = stock_data.dropna()
    close_data = DataFrame.to_numpy(stock_data)
    price_list = array([float(x[3]) for x in close_data])

    del stock_data
    del now
    del one_year_ago
    del close_data

    rsi = RSI(price_list, 14)

    response_dict = {
        "price": round(price_list[-1], 2),
        "rsi": round(rsi[-1], 2)
    }

    del rsi
    del price_list

    response = flask.jsonify(response_dict)
    response.headers.add_header("Access-Control-Allow-Origin", "*")
    return response



if __name__ == "__main__":
    app.run(host="localhost", port=8090)
