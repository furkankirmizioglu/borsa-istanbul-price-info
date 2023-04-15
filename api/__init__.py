import valuation
import flask
from flask import Flask, request
from flask_restful import Api
import database

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

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
