#!/usr/bin/env python3
"""
Test de récupération des vraies prédictions depuis Supabase
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_real_predictions():
    """Test de récupération des vraies prédictions"""
    print("=== Test de récupération des vraies prédictions ===")
    
    try:
        # Import de la fonction de récupération
        from data_api.supabase.database import load_predictions, load_regions
        
        # Récupérer toutes les régions
        regions = load_regions()
        print(f"Régions disponibles: {[r['name'] for r in regions]}")
        
        # Récupérer les prédictions de la dernière heure
        start_time = (datetime.now() - timedelta(hours=1)).isoformat()
        metrics = ['temperature', 'humidity', 'pressure', 'precipitation', 'wind_speed', 'visibility', 'cloud_cover']
        
        print(f"\nRécupération des prédictions depuis {start_time}")
        print(f"Métriques recherchées: {metrics}")
        
        # Récupérer les prédictions pour toutes les régions
        predictions = load_predictions(
            start_time=start_time,
            regions=[r['name'] for r in regions],
            metrics=metrics
        )
        
        if predictions:
            print(f"\n✅ {len(predictions)} prédictions trouvées:")
            
            for pred in predictions:
                print(f"\n--- Prédiction pour {pred.get('region', {}).get('name', 'Inconnu')} ---")
                print(f"Timestamp: {pred.get('time')}")
                
                for metric in metrics:
                    if metric in pred:
                        print(f"  {metric}: {pred[metric]}")
                    else:
                        print(f"  {metric}: Non disponible")
        else:
            print("\n❌ Aucune prédiction trouvée dans la dernière heure")
            print("Cela peut signifier:")
            print("1. Les modèles LSTM n'ont pas encore généré de prédictions")
            print("2. La table 'predictions' est vide")
            print("3. Problème de connexion à Supabase")
            
            # Essayer de récupérer toutes les prédictions disponibles
            print("\n--- Tentative de récupération de toutes les prédictions ---")
            all_predictions = load_predictions(
                start_time="2020-01-01T00:00:00",  # Date très ancienne
                regions=[r['name'] for r in regions],
                metrics=metrics
            )
            
            if all_predictions:
                print(f"✅ {len(all_predictions)} prédictions trouvées au total")
                print("Dernières prédictions:")
                for pred in all_predictions[-3:]:  # Afficher les 3 dernières
                    print(f"  {pred.get('region', {}).get('name')} - {pred.get('time')}")
            else:
                print("❌ Aucune prédiction dans la base de données")
                
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {e}")
        import traceback
        traceback.print_exc()

def test_weather_index_with_real_data():
    """Test de l'indice météo avec de vraies données"""
    print("\n=== Test de l'indice météo avec de vraies données ===")
    
    try:
        from data_api.weather_index.weather_index_calculator import weather_index_calculator
        from data_api.supabase.database import load_predictions, load_regions
        
        # Récupérer les régions
        regions = load_regions()
        
        # Calculer l'indice pour chaque région
        for region in regions[:3]:  # Limiter aux 3 premières régions
            region_name = region['name']
            print(f"\n--- Calcul de l'indice pour {region_name} ---")
            
            # Récupérer les prédictions
            predictions = load_predictions(
                start_time=(datetime.now() - timedelta(hours=1)).isoformat(),
                regions=[region_name],
                metrics=list(weather_index_calculator.weights.keys())
            )
            
            if predictions:
                # Prendre la plus récente
                latest_pred = max(predictions, key=lambda x: x['time'])
                
                # Extraire les données météo
                weather_data = {}
                for metric in weather_index_calculator.weights.keys():
                    if metric in latest_pred:
                        weather_data[metric] = latest_pred[metric]
                
                # Calculer l'indice
                result = weather_index_calculator.calculate_weather_index(weather_data, region_name)
                
                print(f"✅ Indice calculé: {result['index']:.3f} ({result['level']})")
                print(f"Timestamp prédiction: {latest_pred['time']}")
                
                for metric, detail in result['details'].items():
                    print(f"  {metric}: {detail['raw_value']} → Contribution: {detail['contribution']:.3f}")
            else:
                print(f"❌ Aucune prédiction trouvée pour {region_name}")
                
    except Exception as e:
        print(f"❌ Erreur lors du calcul de l'indice: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Fonction principale"""
    print("Test de récupération des vraies prédictions depuis Supabase")
    print("=" * 60)
    
    # Test 1: Récupération des prédictions
    test_real_predictions()
    
    # Test 2: Calcul de l'indice avec vraies données
    test_weather_index_with_real_data()
    
    print("\n" + "=" * 60)
    print("Test terminé")

if __name__ == "__main__":
    main() 