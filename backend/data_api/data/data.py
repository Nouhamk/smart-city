from datetime import datetime, date
import re

from rest_framework import status
from rest_framework.response import Response
from data_api.ingestion.cities_ingestion import get_all_regions
from data_api.mapping.metrics import get_all_metrics
from data_api.supabase.database import load_normalized_data, load_predictions, get_latest_timestamp_by_cities


def get_data_common(regions=None, start=None, end=None, metrics=None):
    # Extract parameters from query params
    regions_param = regions
    start_param = start
    end_param = end

    # Set defaults
    metrics_param = metrics
    if not start_param:
        start = "2025-03-01"
    else:
        try:
            start = datetime.strptime(start_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {'error': 'Invalid start date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

    if not end_param:
        end = str(date.today())
    else:
        try:
            end = datetime.strptime(end_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {'error': 'Invalid end date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

    all_metrics = get_all_metrics()
    all_regions = get_all_regions()

    metrics = metrics_param if metrics_param else all_metrics
    regions = regions_param if regions_param else all_regions

    invalid_metrics = set(metrics) - set(all_metrics)
    if invalid_metrics:
        return Response(
            {'error': f"Unknown metric(s): {', '.join(invalid_metrics)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    invalid_regions = set(regions) - set(all_regions)
    if invalid_regions:
        return Response(
            {'error': f"Unknown region(s): {', '.join(invalid_regions)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = load_normalized_data(start, end, regions, metrics)
    return Response(
        data,
        status=status.HTTP_200_OK
    )


def get_predictions(regions=None, start=None, metrics=None):
    regions_param = regions
    start_param = start

    # Set defaults
    metrics_param = metrics
    if not start_param:
        start = next(iter(sorted(
            get_latest_timestamp_by_cities(),
            key=lambda x: x["latest_time"]
        )), None)["latest_time"]
    else:
        try:
            start = datetime.strptime(start_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {'error': 'Invalid start date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )



    all_metrics = get_all_metrics()
    all_regions = get_all_regions()

    metrics = metrics_param if metrics_param else all_metrics
    regions = regions_param if regions_param else all_regions

    invalid_metrics = set(metrics) - set(all_metrics)
    if invalid_metrics:
        return Response(
            {'error': f"Unknown metric(s): {', '.join(invalid_metrics)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    invalid_regions = set(regions) - set(all_regions)
    if invalid_regions:
        return Response(
            {'error': f"Unknown region(s): {', '.join(invalid_regions)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = load_predictions(start, regions, metrics)
    return Response(
        data,
        status=status.HTTP_200_OK
    )