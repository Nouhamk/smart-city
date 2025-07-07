from datetime import datetime, date
import re

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from data_api.ingestion.cities_ingestion import get_all_regions
from data_api.mapping.metrics import get_all_metrics

from data_api.database import load_normalized_data


class DataView(APIView):
    """
    API view to retrieve normalized data based on regions, date range, and metrics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extract parameters from query params
        regions_param = request.query_params.getlist('regions')
        start_param = request.query_params.get('start')
        end_param = request.query_params.get('end')
        metrics_param = request.query_params.getlist('metrics')

        # Set defaults
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

        # Get all available options
        all_metrics = get_all_metrics()
        all_regions = get_all_regions()

        # Set defaults if not provided
        metrics = metrics_param if metrics_param else all_metrics
        regions = regions_param if regions_param else all_regions

        # Validate metrics
        invalid_metrics = set(metrics) - set(all_metrics)
        if invalid_metrics:
            return Response(
                {'error': f"Unknown metric(s): {', '.join(invalid_metrics)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate regions
        invalid_regions = set(regions) - set(all_regions)
        if invalid_regions:
            return Response(
                {'error': f"Unknown region(s): {', '.join(invalid_regions)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate date format and logic
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern, str(start)):
            return Response(
                {'error': 'Start date format invalid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not re.match(pattern, str(end)):
            return Response(
                {'error': 'End date format invalid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if start > end:
            return Response(
                {'error': "Start date can't be superior to end date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = load_normalized_data(start, end, regions, metrics)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to load data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )