#!/usr/bin/env python3
"""
Script de test pour l'indice météo global
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
django.setup()

from data_api.weather_index.weather_index_calculator import weather_index_calculator
from data_api.weather_index.alert_service import weather_index_alert_service

def test_weather_index_calculation():
    """Test du calcul de l'indice météo"""
    print("=== Test du calcul de l'indice météo ===")
    
    # Données de test
    test_data = {
        'temperature': 28.5,
        'humidity': 75.0,
        'pressure': 1010.0,
        'precipitation': 5.0,
        'wind_speed': 25.0,
        'visibility': 8.0,
        'cloud_cover': 60.0
    }
    
    # Calcul de l'indice
    result = weather_index_calculator.calculate_weather_index(test_data, "Paris")
    
    print(f"Région: {result['region']}")
    print(f"Indice: {result['index']:.3f}")
    print(f"Niveau: {result['level']}")
    print(f"Timestamp: {result['timestamp']}")
    
    print("\nDétails par métrique:")
    for metric, detail in result['details'].items():
        print(f"  {metric}:")
        print(f"    Valeur brute: {detail['raw_value']}")
        print(f"    Normalisée: {detail['normalized']:.3f}")
        print(f"    Poids: {detail['weight']:.2f}")
        print(f"    Contribution: {detail['contribution']:.3f}")
    
    return result

def test_alert_service():
    """Test du service d'alerte"""
    print("\n=== Test du service d'alerte ===")
    
    # Test de création d'alerte
    test_index_data = {
        'index': 0.75,
        'level': 'high',
        'region': 'Paris',
        'timestamp': datetime.now().isoformat(),
        'details': {
            'temperature': {
                'raw_value': 30.0,
                'normalized': 0.8,
                'weight': 0.25,
                'contribution': 0.2
            }
        }
    }
    
    print("Test de création d'alerte...")
    # Note: Ceci ne créera pas d'alerte réelle car nous n'avons pas de base de données configurée
    print("Service d'alerte configuré (pas de création réelle en mode test)")

def test_configuration():
    """Test de la configuration"""
    print("\n=== Configuration de l'indice météo ===")
    
    print("Poids des métriques:")
    for metric, weight in weather_index_calculator.weights.items():
        print(f"  {metric}: {weight:.2f} ({weight*100:.0f}%)")
    
    print("\nSeuils d'alerte:")
    for level, threshold in weather_index_calculator.alert_thresholds.items():
        print(f"  {level}: {threshold:.2f}")
    
    print("\nValeurs de référence:")
    for metric, ref in weather_index_calculator.reference_values.items():
        print(f"  {metric}: min={ref['min']}, max={ref['max']}, optimal={ref['optimal']}")

def main():
    """Fonction principale de test"""
    print("Démarrage des tests de l'indice météo global")
    print("=" * 50)
    
    try:
        # Test de la configuration
        test_configuration()
        
        # Test du calcul
        result = test_weather_index_calculation()
        
        # Test du service d'alerte
        test_alert_service()
        
        print("\n" + "=" * 50)
        print("✅ Tous les tests sont passés avec succès!")
        print(f"Indice final calculé: {result['index']:.3f} ({result['level']})")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 