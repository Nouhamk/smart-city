from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from rest_framework import serializers
from typing import List, Dict, Any

from .weather_index_calculator import weather_index_calculator


class WeatherIndexSerializer(serializers.Serializer):
    """Sérialiseur pour l'indice météo"""
    index = serializers.FloatField(help_text="Indice global météo (0-1)")
    level = serializers.CharField(help_text="Niveau d'alerte (low/medium/high/critical)")
    region = serializers.CharField(help_text="Nom de la région")
    timestamp = serializers.DateTimeField(help_text="Timestamp du calcul")
    prediction_time = serializers.DateTimeField(required=False, help_text="Timestamp de la prédiction")
    details = serializers.DictField(help_text="Détails des contributions par métrique")


class WeatherIndexHistorySerializer(serializers.Serializer):
    """Sérialiseur pour l'historique de l'indice météo"""
    index = serializers.FloatField(help_text="Indice global météo (0-1)")
    level = serializers.CharField(help_text="Niveau d'alerte")
    region = serializers.CharField(help_text="Nom de la région")
    timestamp = serializers.DateTimeField(help_text="Timestamp de la donnée")


class WeatherIndexView(APIView):
    """Vue pour récupérer l'indice météo global actuel"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Récupérer l'indice météo global",
        description="Calcule et retourne l'indice météo global basé sur les dernières prédictions",
        parameters=[
            OpenApiParameter(
                name='regions',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Régions séparées par des virgules (ex: paris,lyon,marseille)",
                required=False
            )
        ],
        responses={
            200: WeatherIndexSerializer(many=True),
            400: inline_serializer(
                name='ErrorResponse',
                fields={'error': serializers.CharField()}
            )
        },
        examples=[
            OpenApiExample(
                'Exemple de réponse',
                value=[
                    {
                        "index": 0.65,
                        "level": "high",
                        "region": "Paris",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "prediction_time": "2024-01-15T10:00:00Z",
                        "details": {
                            "temperature": {
                                "raw_value": 28.5,
                                "normalized": 0.7,
                                "weight": 0.25,
                                "contribution": 0.175
                            },
                            "humidity": {
                                "raw_value": 75.0,
                                "normalized": 0.6,
                                "weight": 0.20,
                                "contribution": 0.120
                            }
                        }
                    }
                ]
            )
        ]
    )
    def get(self, request):
        """Récupère l'indice météo global pour les régions spécifiées"""
        try:
            # Récupérer les régions depuis les paramètres de requête
            regions_param = request.query_params.get('regions')
            regions = None
            if regions_param:
                regions = [region.strip() for region in regions_param.split(',')]
            
            # Calculer l'indice météo
            weather_indices = weather_index_calculator.get_latest_weather_index(regions)
            
            return Response(weather_indices, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul de l\'indice météo: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class WeatherIndexHistoryView(APIView):
    """Vue pour récupérer l'historique de l'indice météo"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Récupérer l'historique de l'indice météo",
        description="Récupère l'historique de l'indice météo pour une région donnée",
        parameters=[
            OpenApiParameter(
                name='region',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Nom de la région",
                required=True
            ),
            OpenApiParameter(
                name='hours',
                type=int,
                location=OpenApiParameter.QUERY,
                description="Nombre d'heures d'historique (défaut: 24)",
                required=False
            )
        ],
        responses={
            200: WeatherIndexHistorySerializer(many=True),
            400: inline_serializer(
                name='ErrorResponse',
                fields={'error': serializers.CharField()}
            )
        }
    )
    def get(self, request):
        """Récupère l'historique de l'indice météo"""
        try:
            region = request.query_params.get('region')
            if not region:
                return Response(
                    {'error': 'Le paramètre "region" est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            hours = request.query_params.get('hours', 24)
            try:
                hours = int(hours)
            except ValueError:
                return Response(
                    {'error': 'Le paramètre "hours" doit être un entier'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupérer l'historique
            history = weather_index_calculator.get_weather_index_history(region, hours)
            
            return Response(history, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de l\'historique: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class WeatherIndexConfigView(APIView):
    """Vue pour récupérer la configuration de l'indice météo"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Récupérer la configuration de l'indice météo",
        description="Retourne les poids, seuils et valeurs de référence utilisés pour le calcul",
        responses={
            200: inline_serializer(
                name='ConfigResponse',
                fields={
                    'weights': serializers.DictField(),
                    'alert_thresholds': serializers.DictField(),
                    'reference_values': serializers.DictField()
                }
            )
        }
    )
    def get(self, request):
        """Récupère la configuration de l'indice météo"""
        try:
            config = {
                'weights': weather_index_calculator.weights,
                'alert_thresholds': weather_index_calculator.alert_thresholds,
                'reference_values': weather_index_calculator.reference_values
            }
            
            return Response(config, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de la configuration: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            ) 