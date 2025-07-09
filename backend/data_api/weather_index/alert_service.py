from datetime import datetime, timedelta
from typing import List, Dict, Any
from django.utils import timezone
from django.core.mail import send_mail
import os

from .weather_index_calculator import weather_index_calculator
from data_api.supabase.database import supabase


class WeatherIndexAlertService:
    """
    Service de gestion des alertes basées sur l'indice météo global
    """
    
    def __init__(self):
        self.alert_levels = {
            'low': {
                'name': 'Conditions normales',
                'color': '#28a745',
                'description': 'Conditions météorologiques normales'
            },
            'medium': {
                'name': 'Attention',
                'color': '#ffc107',
                'description': 'Conditions météorologiques nécessitant une attention particulière'
            },
            'high': {
                'name': 'Alerte',
                'color': '#fd7e14',
                'description': 'Conditions météorologiques défavorables - alerte active'
            },
            'critical': {
                'name': 'Alerte critique',
                'color': '#dc3545',
                'description': 'Conditions météorologiques critiques - alerte urgente'
            }
        }
    
    def check_and_create_alerts(self, regions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Vérifie les indices météo et crée des alertes si nécessaire
        """
        try:
            # Récupérer les indices météo actuels
            weather_indices = weather_index_calculator.get_latest_weather_index(regions)
            
            created_alerts = []
            
            for index_data in weather_indices:
                region = index_data['region']
                index_value = index_data['index']
                level = index_data['level']
                
                # Vérifier si une alerte active existe déjà pour cette région
                existing_alert = self._get_active_alert_for_region(region)
                
                if existing_alert:
                    # Mettre à jour l'alerte existante si le niveau a changé
                    if existing_alert['level'] != level:
                        self._update_alert(existing_alert['id'], level, index_value, index_data)
                        created_alerts.append({
                            'action': 'updated',
                            'region': region,
                            'level': level,
                            'index': index_value
                        })
                else:
                    # Créer une nouvelle alerte si le niveau est medium ou plus
                    if level in ['medium', 'high', 'critical']:
                        alert_id = self._create_alert(region, level, index_value, index_data)
                        if alert_id:
                            created_alerts.append({
                                'action': 'created',
                                'region': region,
                                'level': level,
                                'index': index_value,
                                'alert_id': alert_id
                            })
            
            return created_alerts
            
        except Exception as e:
            print(f"Erreur lors de la vérification des alertes: {e}")
            return []
    
    def _get_active_alert_for_region(self, region: str) -> Dict[str, Any]:
        """
        Récupère l'alerte active pour une région donnée
        """
        try:
            response = supabase.table("alert") \
                .select("*") \
                .eq("type", "weather_index") \
                .eq("data->region", region) \
                .eq("status", "active") \
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'alerte pour {region}: {e}")
            return None
    
    def _create_alert(self, region: str, level: str, index_value: float, index_data: Dict) -> str:
        """
        Crée une nouvelle alerte dans la base de données
        """
        try:
            level_info = self.alert_levels.get(level, {})
            
            alert_data = {
                'type': 'weather_index',
                'message': f"Indice météo global: {index_value:.3f} - {level_info.get('name', level)}",
                'level': level,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'data': {
                    'region': region,
                    'index_value': index_value,
                    'level': level,
                    'details': index_data.get('details', {}),
                    'prediction_time': index_data.get('prediction_time'),
                    'description': level_info.get('description', '')
                }
            }
            
            response = supabase.table("alert").insert(alert_data).execute()
            
            if response.data:
                alert_id = response.data[0]['id']
                
                # Envoyer une notification par email (optionnel)
                self._send_email_notification(region, level, index_value, level_info)
                
                return alert_id
            
            return None
            
        except Exception as e:
            print(f"Erreur lors de la création de l'alerte pour {region}: {e}")
            return None
    
    def _update_alert(self, alert_id: str, level: str, index_value: float, index_data: Dict):
        """
        Met à jour une alerte existante
        """
        try:
            level_info = self.alert_levels.get(level, {})
            
            update_data = {
                'level': level,
                'message': f"Indice météo global: {index_value:.3f} - {level_info.get('name', level)}",
                'updated_at': datetime.now().isoformat(),
                'data': {
                    'index_value': index_value,
                    'level': level,
                    'details': index_data.get('details', {}),
                    'prediction_time': index_data.get('prediction_time'),
                    'description': level_info.get('description', '')
                }
            }
            
            supabase.table("alert") \
                .update(update_data) \
                .eq("id", alert_id) \
                .execute()
                
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'alerte {alert_id}: {e}")
    
    def _send_email_notification(self, region: str, level: str, index_value: float, level_info: Dict):
        """
        Envoie une notification par email (optionnel)
        """
        try:
            # Vérifier si l'envoi d'email est configuré
            if not os.getenv('EMAIL_HOST'):
                return
            
            subject = f"Alerte météo - {region} - {level_info.get('name', level)}"
            message = f"""
            Nouvelle alerte météo détectée :
            
            Région: {region}
            Niveau: {level_info.get('name', level)}
            Indice: {index_value:.3f}
            Description: {level_info.get('description', '')}
            
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # Envoyer à l'administrateur (à configurer selon vos besoins)
            send_mail(
                subject,
                message,
                'noreply@smartcity.com',
                ['admin@smartcity.com'],
                fail_silently=True,
            )
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
    
    def resolve_alerts_for_region(self, region: str):
        """
        Résout toutes les alertes actives pour une région donnée
        """
        try:
            supabase.table("alert") \
                .update({
                    'status': 'resolved',
                    'resolved_at': datetime.now().isoformat()
                }) \
                .eq("type", "weather_index") \
                .eq("data->region", region) \
                .eq("status", "active") \
                .execute()
                
        except Exception as e:
            print(f"Erreur lors de la résolution des alertes pour {region}: {e}")
    
    def get_weather_index_alerts(self, status: str = 'active') -> List[Dict[str, Any]]:
        """
        Récupère toutes les alertes d'indice météo
        """
        try:
            response = supabase.table("alert") \
                .select("*") \
                .eq("type", "weather_index") \
                .eq("status", status) \
                .order("created_at", desc=True) \
                .execute()
            
            return response.data
            
        except Exception as e:
            print(f"Erreur lors de la récupération des alertes: {e}")
            return []

# Instance globale du service d'alerte
weather_index_alert_service = WeatherIndexAlertService() 