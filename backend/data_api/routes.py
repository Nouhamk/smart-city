from datetime import datetime, date

from apscheduler.schedulers.background import BackgroundScheduler
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from data_api.data.data import get_data_common
from data_api.ingestion import update_ingestion

import atexit

from data_api.predictions.predictions import write_predictions


class DataView(APIView):
    """
    API view to retrieve normalized data based on regions, date range, and metrics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return get_data_common(
            regions=request.get_json().get('regions'),
            start=request.get_json().get('start'),
            end=request.get_json().get('end'),
            metrics=request.get_json().get('metrics')
        )

    def get_predictions(self, request):
        return get_data_common(
            regions=request.get_json().get('regions'),
            start=date.now(),
            metrics=request.get_json().get('metrics')
        )


def ingestion_job():
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"🔄 Ingestion job running at: {current_time}")
    update_ingestion()
    write_predictions()

scheduler = BackgroundScheduler()
print("Background scheduler started")

# Ingestion job every hour
scheduler.add_job(ingestion_job, 'interval', hours=1, id='ingestion_job')

scheduler.start()
atexit.register(lambda: scheduler.shutdown())