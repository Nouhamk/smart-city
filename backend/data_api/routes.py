from datetime import datetime, date

from apscheduler.schedulers.background import BackgroundScheduler
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from data_api.data.data import get_data_common, get_predictions
from data_api.ingestion.update_ingestion import update_ingestion

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample,
    OpenApiResponse, inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

import atexit

from data_api.predictions.predictions import write_predictions



class NormalizedDataSerializer(serializers.Serializer):
    time = serializers.DateTimeField(help_text="Data timestamp")
    region_id = serializers.IntegerField(help_text="Region identifier")
    region = inline_serializer(
        name='RegionInfo',
        fields={'name': serializers.CharField(help_text="Region name")}
    )
    # Dynamic fields for metrics - these will be present based on available data
    temperature = serializers.FloatField(required=False, help_text="Temperature in Celsius")
    humidity = serializers.FloatField(required=False, help_text="Humidity percentage")
    pollution = serializers.FloatField(required=False, help_text="Pollution index")
    pressure = serializers.FloatField(required=False, help_text="Atmospheric pressure")
    wind_speed = serializers.FloatField(required=False, help_text="Wind speed")
    rainfall = serializers.FloatField(required=False, help_text="Rainfall amount")

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


@extend_schema_view(
    get=extend_schema(
        tags=['Data'],
        summary='Get normalized data',
        description='''
        Retrieve weather and environmental data filtered by regions, date range, and metrics.
        
        **Default Behavior:**
        - If no regions specified: returns data for all available regions
        - If no start date specified: defaults to 2025-03-01
        - If no end date specified: defaults to today
        - If no metrics specified: returns all available metrics
        
        **Available Metrics:** 
        The system supports various environmental metrics like temperature, humidity, pollution, 
        pressure, wind_speed, rainfall, etc. Use the metrics parameter to filter specific ones.
        
        **Date Format:** 
        Dates must be in YYYY-MM-DD format. Start date cannot be later than end date.
        ''',
        parameters=[
            OpenApiParameter(
                name='regions',
                description='List of region names to filter by (case-insensitive)',
                required=False,
                type=OpenApiTypes.STR,
                many=True,
                style='form',
                explode=True,
                examples=[
                    OpenApiExample(
                        'Single Region',
                        value=['paris']
                    ),
                    OpenApiExample(
                        'Multiple Regions',
                        value=['paris', 'lyon', 'marseille']
                    )
                ]
            ),
            OpenApiParameter(
                name='start',
                description='Start date (YYYY-MM-DD format). Defaults to 2025-03-01 if not provided.',
                required=False,
                type=OpenApiTypes.DATE,
                examples=[
                    OpenApiExample('Start Date', value='2025-03-01'),
                    OpenApiExample('Recent Start', value='2025-07-01')
                ]
            ),
            OpenApiParameter(
                name='end',
                description='End date (YYYY-MM-DD format). Defaults to today if not provided.',
                required=False,
                type=OpenApiTypes.DATE,
                examples=[
                    OpenApiExample('End Date', value='2025-07-08'),
                    OpenApiExample('Future End', value='2025-12-31')
                ]
            ),
            OpenApiParameter(
                name='metrics',
                description='List of specific metrics to include in the response',
                required=False,
                type=OpenApiTypes.STR,
                many=True,
                style='form',
                explode=True,
                examples=[
                    OpenApiExample(
                        'Weather Metrics',
                        value=['temperature', 'humidity', 'pressure']
                    ),
                    OpenApiExample(
                        'Environmental Metrics',
                        value=['pollution', 'wind_speed', 'rainfall']
                    ),
                    OpenApiExample(
                        'Single Metric',
                        value=['temperature']
                    )
                ]
            )
        ],
        responses={
            200: OpenApiResponse(
                response=NormalizedDataSerializer(many=True),
                description='Data retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Successful Response',
                        value=[
                            {
                                'time': '2025-07-08T10:00:00Z',
                                'region_id': 1,
                                'region': {'name': 'paris'},
                                'temperature': 25.5,
                                'humidity': 65.2,
                                'pollution': 42.8,
                                'pressure': 1013.25,
                                'wind_speed': 12.3,
                                'rainfall': 0.0
                            },
                            {
                                'time': '2025-07-08T11:00:00Z',
                                'region_id': 2,
                                'region': {'name': 'lyon'},
                                'temperature': 23.1,
                                'humidity': 58.7,
                                'pollution': 38.2,
                                'pressure': 1015.12,
                                'wind_speed': 8.7,
                                'rainfall': 2.1
                            }
                        ]
                    )
                ]
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Invalid parameters',
                examples=[
                    OpenApiExample(
                        'Invalid Date Format',
                        value={'error': 'Invalid start date format. Use YYYY-MM-DD'}
                    ),
                    OpenApiExample(
                        'Unknown Metric',
                        value={'error': 'Unknown metric(s): invalid_metric, another_invalid'}
                    ),
                    OpenApiExample(
                        'Unknown Region',
                        value={'error': 'Unknown region(s): invalid_region'}
                    ),
                    OpenApiExample(
                        'Invalid Date Range',
                        value={'error': "Start date can't be superior to end date."}
                    ),
                    OpenApiExample(
                        'Invalid Date Format Regex',
                        value={'error': 'Start date format invalid'}
                    )
                ]
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Server error while loading data',
                examples=[
                    OpenApiExample(
                        'Database Error',
                        value={'error': 'Failed to load data: Database connection failed'}
                    )
                ]
            )
        }
    )
)

class DataView(APIView):
    """
    API view to retrieve normalized data based on regions, date range, and metrics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return get_data_common(
            regions=request.data.get('regions'),
            start=request.data.get('start'),
            end=request.data.get('end'),
            metrics=request.data.get('metrics')
        )

class PredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return get_predictions(
            regions=request.data.get('regions'),
            start=request.data.get('start'),
            metrics=request.data.get('metrics')
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