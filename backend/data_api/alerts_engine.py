import os
import django
import redis
from django.utils import timezone
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
django.setup()

from django_api.models import Alert, AlertThreshold, Prediction

# Connexion à Redis (localhost par défaut)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Charger dynamiquement les seuils depuis la base

def get_threshold(alert_type, zone=None):
    try:
        if zone:
            return AlertThreshold.objects.get(type=alert_type, zone=zone).value
        return AlertThreshold.objects.get(type=alert_type, zone__isnull=True).value
    except AlertThreshold.DoesNotExist:
        return None

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
    # Envoi d'email (bonus)
    send_mail(
        f'Alerte {alert_type}',
        message,
        'from@example.com',
        ['admin@example.com'],
        fail_silently=True,
    )
    return alert

def analyze_and_trigger_alerts(weather_data, zone=None):
    """
    weather_data: dict, ex: { 'rain': 35, 'heatwave': 29, 'wind': 90 }
    """
    for alert_type, value in weather_data.items():
        threshold = get_threshold(alert_type, zone)
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

# Intégration IA : analyse des prédictions

def analyze_predictions():
    predictions = Prediction.objects.filter(date__gte=timezone.now())
    for pred in predictions:
        threshold = get_threshold(pred.type, pred.zone)
        if threshold is not None and pred.value > threshold:
            create_alert(pred.type, f"Prédiction : {pred.value} dépasse le seuil {threshold}", data={'prediction_id': pred.id, 'value': pred.value, 'threshold': threshold})

# Exemple d'utilisation
if __name__ == '__main__':
    # Simuler des données météo
    sample_data = {'rain': 35, 'heatwave': 27, 'wind': 90}
    analyze_and_trigger_alerts(sample_data) 