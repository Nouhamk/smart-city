from datetime import datetime, date
import re

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.data_api.ingestion.cities_ingestion import get_all_regions
from backend.data_api.mapping.metrics import get_all_metrics
from backend.supabase.database import load_normalized_data
from apscheduler.schedulers.blocking import BlockingScheduler
from backend.data_api.ingestion.update_ingestion import update_ingestion


class DataView(APIView):
    """
    API view to retrieve normalized data based on regions, date range, and metrics.
    """
    permission_classes = [IsAuthenticated]  # Add appropriate permissions

    def get_data_common(self, regions=None, start=None, end=None, metrics=None):
        """Helper method to process common data retrieval logic"""
        # Default start date
        start = (
            "2025-03-01"
            if start is None
            else start
        )

        # Default end date
        end = (
            str(date.today())
            if end is None
            else end
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

        # Validate metrics
        invalid_metrics = set(metrics) - set(all_metrics)
        if invalid_metrics:
            return None, f"Unknown metric(s): {', '.join(invalid_metrics)}"

        # Validate date format
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern, str(start)):
            return None, "Start date format invalid"
        if not re.match(pattern, str(end)):
            return None, "End date format invalid"
        if start > end:
            return None, "Start date can't be superior to end date."

        data = load_normalized_data(start, end, regions, metrics)
        return data, None

    def post(self, request):
        """Handle POST requests for data retrieval"""
        data = request.data

        # Extract parameters from request data
        regions = data.get('regions')
        start = data.get('start')
        end = data.get('end')
        metrics = data.get('metrics')

        # Parse dates if provided
        if start:
            try:
                start = datetime.strptime(start, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {'error': 'Invalid start date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if end:
            try:
                end = datetime.strptime(end, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {'error': 'Invalid end date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Get data using common method
        result, error_msg = self.get_data_common(
            regions=regions,
            start=start,
            end=end,
            metrics=metrics
        )

        if error_msg:
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(result, status=status.HTTP_200_OK)

#job to update ingestion every hour
scheduler = BlockingScheduler()
scheduler.add_job(update_ingestion, 'interval', hours=1)
scheduler.start()