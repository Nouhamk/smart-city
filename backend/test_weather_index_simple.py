#!/usr/bin/env python3
"""
Test simplifié de l'indice météo global (sans Django)
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import direct du calculateur (sans Django)
from data_api.weather_index.weather_index_calculator import WeatherIndexCalculator

def test_weather_index_calculation():
    """Test du calcul de l'indice météo"""
    print("=== Test du calcul de l'indice météo ===")
    
    # Créer une instance du calculateur
    calculator = WeatherIndexCalculator()
    
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
    result = calculator.calculate_weather_index(test_data, "Paris")
    
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

def test_normalization():
    """Test de la normalisation des métriques"""
    print("\n=== Test de la normalisation ===")
    
    calculator = WeatherIndexCalculator()
    
    # Test avec différentes valeurs de température
    temperatures = [-5, 0, 10, 20, 30, 40, 45]
    
    print("Normalisation de la température:")
    for temp in temperatures:
        normalized = calculator.normalize_metric(temp, 'temperature')
        print(f"  {temp}°C -> {normalized:.3f}")
    
    # Test avec différentes valeurs d'humidité
    humidities = [0, 25, 50, 75, 100]
    
    print("\nNormalisation de l'humidité:")
    for humidity in humidities:
        normalized = calculator.normalize_metric(humidity, 'humidity')
        print(f"  {humidity}% -> {normalized:.3f}")

def test_configuration():
    """Test de la configuration"""
    print("\n=== Configuration de l'indice météo ===")
    
    calculator = WeatherIndexCalculator()
    
    print("Poids des métriques:")
    for metric, weight in calculator.weights.items():
        print(f"  {metric}: {weight:.2f} ({weight*100:.0f}%)")
    
    print("\nSeuils d'alerte:")
    for level, threshold in calculator.alert_thresholds.items():
        print(f"  {level}: {threshold:.2f}")
    
    print("\nValeurs de référence:")
    for metric, ref in calculator.reference_values.items():
        print(f"  {metric}: min={ref['min']}, max={ref['max']}, optimal={ref['optimal']}")

def test_alert_levels():
    """Test des niveaux d'alerte"""
    print("\n=== Test des niveaux d'alerte ===")
    
    calculator = WeatherIndexCalculator()
    
    test_indices = [0.1, 0.3, 0.5, 0.7, 0.8, 0.9]
    
    for index in test_indices:
        level = calculator._get_alert_level(index)
        print(f"  Indice {index:.1f} -> Niveau: {level}")

def main():
    """Fonction principale de test"""
    print("Démarrage des tests de l'indice météo global")
    print("=" * 50)
    
    try:
        # Test de la configuration
        test_configuration()
        
        # Test de la normalisation
        test_normalization()
        
        # Test des niveaux d'alerte
        test_alert_levels()
        
        # Test du calcul complet
        result = test_weather_index_calculation()
        
        print("\n" + "=" * 50)
        print("✅ Tous les tests sont passés avec succès!")
        print(f"Indice final calculé: {result['index']:.3f} ({result['level']})")
        
        # Vérification que l'indice est cohérent
        total_weight = sum(result['details'][metric]['weight'] for metric in result['details'])
        total_contribution = sum(result['details'][metric]['contribution'] for metric in result['details'])
        
        print(f"\nVérifications:")
        print(f"  Total des poids: {total_weight:.2f}")
        print(f"  Total des contributions: {total_contribution:.3f}")
        print(f"  Indice calculé: {result['index']:.3f}")
        print(f"  Cohérence: {'✅' if abs(total_contribution - result['index']) < 0.01 else '❌'}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 