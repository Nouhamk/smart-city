from flask import Flask, request, jsonify
from datetime import datetime
import re

app = Flask(__name__)

all_measures = [
    "temperature",
    "apparent_temperature",
    "humidity",
    "dewpoint",
    "precipprob",
    "precip",
    "snow",
    "snow depth",
    "wind_gust",
    "wind_speed",
    "wind_direction",
    "pressure",
    "visibility",
    "cloudcover"
]

def error(message: str):
    return jsonify({
        'error': message
    }), 400


@app.route('/data')
def data():
    required_args = ['start', 'end', 'region_name']
    if any([arg not in request.args for arg in required_args]):
        return error(
            f"arg {list(filter(lambda x: x not in request.args, required_args))[0]} missing"
        )

    # Getting parameters
    start = datetime.strptime(request.args.get('start'), "%Y-%m-%d").date()
    end = datetime.strptime(request.args.get('end'), "%Y-%m-%d").date()
    region_name = request.args.get('region_name')

    measures = (
        all_measures
        if request.args.get('mesures') is None
        else [value for value in request.args.get('mesures').split(',')]
    )

    measures = [m for m in measures if m in all_measures] or error(
        f"Unknown measure(s): {', '.join(set(measures) - set(all_measures))}")

    pattern = r"^\d{4}-\d{2}-\d{2}$"

    if not re.match(pattern, request.args.get('start')): return error("Start date format invalid")
    if not re.match(pattern, request.args.get('end')): return error("End date format invalid")
    if start > end: return error("Start date can't be superior to end date.")

    data = load_normalized_data()
