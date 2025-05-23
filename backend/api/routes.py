from flask import Flask, request, jsonify
from datetime import datetime
import re

from backend.mapping.metrics import get_all_metrics
from backend.supabase.database import load_normalized_data

app = Flask(__name__)

def error(message: str):
    return jsonify({
        'error': message
    }), 400


@app.route('/data')
def get_data():
    required_args = ['start', 'end', 'region_name']
    if any([arg not in request.args for arg in required_args]):
        return error(
            f"arg {list(filter(lambda x: x not in request.args, required_args))[0]} missing"
        )

    # Getting parameters
    start = datetime.strptime(request.args.get('start'), "%Y-%m-%d").date()
    end = datetime.strptime(request.args.get('end'), "%Y-%m-%d").date()
    region_name = request.args.get('region_name')

    all_metrics = get_all_metrics()

    metrics = (
        all_metrics
        if request.args.get('mesures') is None
        else [value for value in request.args.get('mesures').split(',')]
    )

    metrics = [m for m in metrics if m in all_metrics] or error(
        f"Unknown metric(s): {', '.join(set(metrics) - set(all_metrics))}")

    pattern = r"^\d{4}-\d{2}-\d{2}$"

    if not re.match(pattern, request.args.get('start')): return error("Start date format invalid")
    if not re.match(pattern, request.args.get('end')): return error("End date format invalid")
    if start > end: return error("Start date can't be superior to end date.")

    data = load_normalized_data(start, end, region_name, metrics)
    print(data)
    return data
