import flask
from flask import Flask, request
from flask_restful import Api
import datetime
from numpy import array
import pandas
from yahoo_fin.stock_info import get_data

app = Flask(__name__)
api = Api(app)


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
    response_dict = {
        "price": round(price_list[-1], 2)
    }
    response = flask.jsonify(response_dict)
    response.headers.add_header("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(host="localhost", port=8090)
