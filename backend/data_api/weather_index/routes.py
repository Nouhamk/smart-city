from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from rest_framework import serializers
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta

from .weather_index_calculator import weather_index_calculator


class WeatherIndexSerializer(serializers.Serializer):
    """Sérialiseur pour l'indice météo"""
    id = serializers.IntegerField(required=False, help_text="ID de l'enregistrement")
    value = serializers.FloatField(help_text="Indice global météo (0-100)")
    level = serializers.CharField(help_text="Niveau d'alerte (low, medium, high, critical)")
    region = serializers.CharField(required=False, help_text="Région concernée")
    timestamp = serializers.DateTimeField(help_text="Horodatage du calcul")
    prediction_time = serializers.DateTimeField(required=False, help_text="Horodatage de la prédiction")
    temperature = serializers.FloatField(required=False, help_text="Température")
    humidity = serializers.FloatField(required=False, help_text="Humidité")
    pressure = serializers.FloatField(required=False, help_text="Pression")
    precipitation = serializers.FloatField(required=False, help_text="Précipitations")
    wind_speed = serializers.FloatField(required=False, help_text="Vitesse du vent")
    visibility = serializers.FloatField(required=False, help_text="Visibilité")
    cloud_cover = serializers.FloatField(required=False, help_text="Couverture nuageuse")
    contributions = serializers.DictField(required=False, help_text="Contributions des métriques")
    details = serializers.DictField(required=False, help_text="Détails du calcul")


class WeatherIndexConfigSerializer(serializers.Serializer):
    """Sérialiseur pour la configuration de l'indice météo"""
    critical_threshold = serializers.FloatField(help_text="Seuil critique")
    high_threshold = serializers.FloatField(help_text="Seuil élevé")
    medium_threshold = serializers.FloatField(help_text="Seuil moyen")
    weights = serializers.DictField(help_text="Poids des métriques")


class WeatherIndexHistorySerializer(serializers.Serializer):
    """Sérialiseur pour l'historique de l'indice météo"""
    count = serializers.IntegerField(help_text="Nombre total d'enregistrements")
    next = serializers.CharField(required=False, help_text="URL de la page suivante")
    previous = serializers.CharField(required=False, help_text="URL de la page précédente")
    results = WeatherIndexSerializer(many=True, help_text="Liste des indices météo")


@extend_schema(
    tags=['Weather Index'],
    summary='Calculer l\'indice météo global',
    description='Calcule l\'indice météo global basé sur les prédictions réelles de toutes les régions',
    responses={
        200: WeatherIndexSerializer,
        500: inline_serializer(
            name='ErrorResponse',
            fields={'error': serializers.CharField()}
        )
    }
)
class WeatherIndexView(APIView):
    """Vue pour calculer l'indice météo global"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Calcule et retourne l'indice météo global actuel"""
        try:
            result = weather_index_calculator.calculate_index()
            
            if "error" in result:
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Erreur lors du calcul de l'indice: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Weather Index'],
    summary='Obtenir l\'indice météo actuel',
    description='Retourne l\'indice météo global actuel avec les détails',
    responses={
        200: WeatherIndexSerializer,
        500: inline_serializer(
            name='ErrorResponse',
            fields={'error': serializers.CharField()}
        )
    }
)
class WeatherIndexCurrentView(APIView):
    """Vue pour obtenir l'indice météo actuel"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourne l'indice météo global actuel"""
        try:
            result = weather_index_calculator.calculate_index()
            
            if "error" in result:
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la récupération de l'indice: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Weather Index'],
    summary='Obtenir l\'historique de l\'indice météo',
    description='Retourne l\'historique des indices météo avec pagination',
    parameters=[
        OpenApiParameter(
            name='page',
            description='Numéro de page',
            required=False,
            type=int,
            default=1
        ),
        OpenApiParameter(
            name='page_size',
            description='Taille de page',
            required=False,
            type=int,
            default=10
        ),
        OpenApiParameter(
            name='start_date',
            description='Date de début (YYYY-MM-DD)',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='end_date',
            description='Date de fin (YYYY-MM-DD)',
            required=False,
            type=str
        )
    ],
    responses={
        200: WeatherIndexHistorySerializer,
        400: inline_serializer(
            name='ErrorResponse',
            fields={'error': serializers.CharField()}
        )
    }
)
class WeatherIndexHistoryView(APIView):
    """Vue pour l'historique de l'indice météo"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourne l'historique de l'indice météo"""
        try:
            # Pour l'instant, on retourne l'indice actuel car l'historique n'est pas encore implémenté
            # TODO: Implémenter la sauvegarde et récupération de l'historique
            current_index = weather_index_calculator.calculate_index()
            
            if "error" in current_index:
                return Response(
                    {"error": current_index["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Simuler un historique avec l'indice actuel
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Pour l'instant, on retourne juste l'indice actuel
            # TODO: Récupérer l'historique depuis la base de données
            history_data = {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [current_index]
            }
            
            return Response(history_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la récupération de l'historique: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    tags=['Weather Index'],
    summary='Obtenir la configuration de l\'indice météo',
    description='Retourne la configuration actuelle des seuils et poids',
    responses={
        200: WeatherIndexConfigSerializer
    }
)
class WeatherIndexConfigView(APIView):
    """Vue pour la configuration de l'indice météo"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourne la configuration actuelle"""
        try:
            config = weather_index_calculator.get_config()
            return Response(config, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la récupération de la configuration: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """Met à jour la configuration"""
        try:
            new_config = request.data
            updated_config = weather_index_calculator.update_config(new_config)
            return Response(updated_config, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la mise à jour de la configuration: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Weather Index'],
    summary='Obtenir les alertes météo actives',
    description='Retourne les alertes météo actives basées sur l\'indice global',
    parameters=[
        OpenApiParameter(
            name='status',
            description='Statut des alertes à filtrer',
            required=False,
            type=str,
            default='active'
        )
    ],
    responses={
        200: inline_serializer(
            name='AlertsResponse',
            fields={
                'alerts': serializers.ListField(
                    child=inline_serializer(
                        name='Alert',
                        fields={
                            'id': serializers.IntegerField(),
                            'type': serializers.CharField(),
                            'message': serializers.CharField(),
                            'level': serializers.CharField(),
                            'status': serializers.CharField(),
                            'created_at': serializers.DateTimeField(),
                            'weather_index_value': serializers.FloatField(),
                            'weather_index_level': serializers.CharField()
                        }
                    )
                )
            }
        )
    }
)
class WeatherIndexAlertsView(APIView):
    """Vue pour les alertes météo basées sur l'indice global"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourne les alertes météo actives"""
        try:
            # Calculer l'indice actuel
            current_index = weather_index_calculator.calculate_index()
            
            if "error" in current_index:
                return Response(
                    {"error": current_index["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Créer des alertes basées sur l'indice
            alerts = []
            index_value = current_index.get("value", 0)
            index_level = current_index.get("level", "low")
            
            # Générer des alertes selon le niveau
            if index_level == "critical":
                alerts.append({
                    "id": 1,
                    "type": "weather_index",
                    "message": f"Indice météo critique: {index_value} (seuil: {weather_index_calculator.config['critical_threshold']})",
                    "level": "critical",
                    "status": "active",
                    "created_at": current_index.get("timestamp"),
                    "weather_index_value": index_value,
                    "weather_index_level": index_level
                })
            elif index_level == "high":
                alerts.append({
                    "id": 2,
                    "type": "weather_index",
                    "message": f"Indice météo élevé: {index_value} (seuil: {weather_index_calculator.config['high_threshold']})",
                    "level": "warning",
                    "status": "active",
                    "created_at": current_index.get("timestamp"),
                    "weather_index_value": index_value,
                    "weather_index_level": index_level
                })
            
            return Response({"alerts": alerts}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la récupération des alertes: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 