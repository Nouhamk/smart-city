import os
import django
import redis
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
django.setup()

from django_api.models import Alert

# Connexion à Redis (localhost par défaut)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Exemple de seuils (à stocker dans Redis ou en base)
ALERT_THRESHOLDS = {
    'rain': 30,        # mm
    'heatwave': 28,   # °C
    'wind': 80,       # km/h
}

def create_alert(alert_type, message, level='warning', data=None):
    alert = Alert.objects.create(
        type=alert_type,
        message=message,
        level=level,
        status='active',
        data=data or {}
    )
    # Stocker l'alerte active dans Redis (clé simple)
    redis_client.set(f'alert:{alert.id}', alert.status)
    return alert

def analyze_and_trigger_alerts(weather_data):
    """
    weather_data: dict, ex: { 'rain': 35, 'heatwave': 29, 'wind': 90 }
    """
    for alert_type, value in weather_data.items():
        threshold = ALERT_THRESHOLDS.get(alert_type)
        if threshold is not None and value > threshold:
            # Vérifier si une alerte active existe déjà pour ce type
            existing = Alert.objects.filter(type=alert_type, status='active').first()
            if not existing:
                message = f"{alert_type.capitalize()} détecté : {value} (seuil : {threshold})"
                create_alert(alert_type, message, data={'value': value, 'threshold': threshold})
                print(f'Alerte {alert_type} déclenchée !')
            else:
                print(f'Alerte {alert_type} déjà active.')
        else:
            print(f'Pas d\'alerte pour {alert_type} (valeur : {value}, seuil : {threshold})')

# Exemple d'utilisation
if __name__ == '__main__':
    # Simuler des données météo
    sample_data = {'rain': 35, 'heatwave': 27, 'wind': 90}
    analyze_and_trigger_alerts(sample_data) 