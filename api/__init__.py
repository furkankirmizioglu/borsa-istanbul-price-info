import flask
import talib
from flask import Flask, request
from flask_restful import Api
from datetime import datetime, timedelta
from matplotlib.dates import date2num
from numpy import array
from pandas import DataFrame
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
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
    close_data = DataFrame.to_numpy(stock_data)
    price_list = array([float(x[3]) for x in close_data])
    date_list = stock_data.index.to_list()

    forecast_value = forecast(date_list, price_list)

    print("{} forecast value: {}".format(request.args.get('ticker'), forecast_value))

    del stock_data
    del date_list
    del now
    del one_year_ago
    del close_data

    rsi = talib.RSI(price_list, 14)

    response_dict = {
        "price": round(price_list[-1], 2),
        "rsi": round(rsi[-1], 2),
        "forecast": forecast_value
    }

    del rsi
    del forecast_value
    del price_list

    response = flask.jsonify(response_dict)
    response.headers.add_header("Access-Control-Allow-Origin", "*")
    return response


def forecast(date_list, price_list):
    date_float_list = date2num(date_list)
    poly = PolynomialFeatures(degree=2, include_bias=False)
    poly_features = poly.fit_transform(date_float_list.reshape(-1, 1))
    poly_reg_model = LinearRegression()
    poly_reg_model.fit(poly_features, price_list)
    base_trend = poly_reg_model.predict(poly_features)
    return round((base_trend[-1] / price_list[-1] - 1) * 100, 2)


if __name__ == "__main__":
    app.run(host="localhost", port=8090)
