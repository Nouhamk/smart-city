from flask import Flask, request, jsonify
from datetime import datetime, date
import re

from backend.ingestion.cities_ingestion import get_all_regions
from backend.mapping.metrics import get_all_metrics
from backend.supabase.database import load_normalized_data

app = Flask(__name__)

def error(message: str):
    return jsonify({
        'error': message
    }), 400


def get_data_common(regions=None, start=None, end=None, metrics=None):
    # Getting parameters
    start = (
        "2025-03-01"
        if start is None
        else datetime.strptime(request.get_json().get('start'), "%Y-%m-%d").date()
    )

    end = (
        str(date.today())
        if end is None
        else datetime.strptime(request.get_json().get('end'), "%Y-%m-%d").date()
    )

    all_metrics = get_all_metrics()
    all_regions = get_all_regions()

    metrics = (
        all_metrics
        if metrics is None
        else metrics
    )

    regions = (
        all_regions
        if regions is None
        else regions
    )


    metrics = [m for m in metrics if m in all_metrics] or error(
        f"Unknown metric(s): {', '.join(set(metrics) - set(all_metrics))}")

    pattern = r"^\d{4}-\d{2}-\d{2}$"

    if not re.match(pattern, start): return error("Start date format invalid")
    if not re.match(pattern, end): return error("End date format invalid")
    if start > end: return error("Start date can't be superior to end date.")

    data = load_normalized_data(start, end, regions, metrics)
    return data


@app.route('/data')
def get_data():
    required_args = []
    if any([arg not in request.get_json() for arg in required_args]):
        return error(
            f"arg {list(filter(lambda x: x not in request.get_json(), required_args))[0]} missing"
        )

    return get_data_common(
        regions=request.get_json().get('regions'),
        start=request.get_json().get('start'),
        end=request.get_json().get('end'),
        metrics=request.get_json().get('metrics')
    )
