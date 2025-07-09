import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from data_api.supabase.database import load_predictions, load_normalized_data
from data_api.mapping.metrics import get_all_metrics

class WeatherIndexCalculator:
    """
    Calculateur d'indice global météo basé sur les prédictions et données normalisées
    """
    
    def __init__(self):
        # Définition des poids pour chaque métrique (doit faire 100%)
        self.weights = {
            'temperature': 0.25,      # 25%
            'humidity': 0.20,         # 20%
            'pressure': 0.15,         # 15%
            'precipitation': 0.15,    # 15%
            'wind_speed': 0.10,       # 10%
            'visibility': 0.10,       # 10%
            'cloud_cover': 0.05       # 5%
        }
        
        # Seuils d'alerte pour l'indice global
        self.alert_thresholds = {
            'low': 0.3,      # Indice < 0.3 : conditions normales
            'medium': 0.5,   # Indice 0.3-0.5 : attention
            'high': 0.7,     # Indice 0.5-0.7 : alerte
            'critical': 0.8  # Indice > 0.8 : alerte critique
        }
        
        # Valeurs de référence pour la normalisation (basées sur des données historiques)
        self.reference_values = {
            'temperature': {'min': -10, 'max': 40, 'optimal': 20},
            'humidity': {'min': 0, 'max': 100, 'optimal': 60},
            'pressure': {'min': 950, 'max': 1050, 'optimal': 1013},
            'precipitation': {'min': 0, 'max': 50, 'optimal': 0},
            'wind_speed': {'min': 0, 'max': 100, 'optimal': 10},
            'visibility': {'min': 0, 'max': 50, 'optimal': 10},
            'cloud_cover': {'min': 0, 'max': 100, 'optimal': 30}
        }
    
    def normalize_metric(self, value: float, metric: str) -> float:
        """
        Normalise une valeur métrique entre 0 et 1
        Utilise une fonction gaussienne centrée sur la valeur optimale
        """
        if metric not in self.reference_values:
            return 0.5  # Valeur par défaut si métrique inconnue
        
        ref = self.reference_values[metric]
        min_val = ref['min']
        max_val = ref['max']
        optimal = ref['optimal']
        
        # Normalisation Min-Max de base
        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0, min(1, normalized))  # Clamp entre 0 et 1
        
        # Application d'une fonction gaussienne pour pénaliser les écarts à l'optimal
        # Plus la valeur s'éloigne de l'optimal, plus l'indice augmente (conditions défavorables)
        sigma = (max_val - min_val) / 6  # Écart-type pour la gaussienne
        deviation = abs(value - optimal)
        gaussian_factor = 1 - np.exp(-(deviation ** 2) / (2 * sigma ** 2))
        
        # Combinaison de la normalisation et de la gaussienne
        final_index = normalized * 0.3 + gaussian_factor * 0.7
        
        return min(1, max(0, final_index))
    
    def calculate_weather_index(self, data: Dict[str, float], region: str) -> Dict[str, Any]:
        """
        Calcule l'indice global météo pour une région donnée
        """
        if not data:
            return {'index': 0.5, 'level': 'unknown', 'details': {}}
        
        weighted_sum = 0
        total_weight = 0
        details = {}
        
        for metric, weight in self.weights.items():
            if metric in data and data[metric] is not None:
                normalized_value = self.normalize_metric(data[metric], metric)
                weighted_sum += normalized_value * weight
                total_weight += weight
                details[metric] = {
                    'raw_value': data[metric],
                    'normalized': normalized_value,
                    'weight': weight,
                    'contribution': normalized_value * weight
                }
        
        # Calcul de l'indice final
        if total_weight > 0:
            final_index = weighted_sum / total_weight
        else:
            final_index = 0.5
        
        # Détermination du niveau d'alerte
        level = self._get_alert_level(final_index)
        
        return {
            'index': round(final_index, 3),
            'level': level,
            'details': details,
            'region': region,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_alert_level(self, index: float) -> str:
        """
        Détermine le niveau d'alerte basé sur l'indice
        """
        if index >= self.alert_thresholds['critical']:
            return 'critical'
        elif index >= self.alert_thresholds['high']:
            return 'high'
        elif index >= self.alert_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def get_latest_weather_index(self, regions: Optional[List[str]] = None) -> List[Dict]:
        """
        Récupère et calcule l'indice météo pour les dernières prédictions
        """
        if not regions:
            # Récupérer toutes les régions disponibles
            from data_api.supabase.database import load_regions
            regions = [region['name'] for region in load_regions()]
        
        results = []
        
        for region in regions:
            try:
                # Récupérer les dernières prédictions pour cette région
                latest_predictions = load_predictions(
                    start_time=(datetime.now() - timedelta(hours=1)).isoformat(),
                    regions=[region],
                    metrics=list(self.weights.keys())
                )
                
                if latest_predictions:
                    # Prendre la prédiction la plus récente
                    latest_data = max(latest_predictions, key=lambda x: x['time'])
                    
                    # Extraire les valeurs métriques
                    weather_data = {}
                    for metric in self.weights.keys():
                        if metric in latest_data:
                            weather_data[metric] = latest_data[metric]
                    
                    # Calculer l'indice
                    index_result = self.calculate_weather_index(weather_data, region)
                    index_result['prediction_time'] = latest_data['time']
                    results.append(index_result)
                
            except Exception as e:
                print(f"Erreur lors du calcul de l'indice pour {region}: {e}")
                continue
        
        return results
    
    def get_weather_index_history(self, region: str, hours: int = 24) -> List[Dict]:
        """
        Récupère l'historique des indices météo pour une région
        """
        try:
            # Récupérer les données historiques
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            end_time = datetime.now().isoformat()
            
            historical_data = load_normalized_data(
                start_time=start_time,
                end_time=end_time,
                regions=[region],
                metrics=list(self.weights.keys())
            )
            
            results = []
            for data_point in historical_data:
                weather_data = {}
                for metric in self.weights.keys():
                    if metric in data_point:
                        weather_data[metric] = data_point[metric]
                
                index_result = self.calculate_weather_index(weather_data, region)
                index_result['timestamp'] = data_point['time']
                results.append(index_result)
            
            return sorted(results, key=lambda x: x['timestamp'])
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'historique pour {region}: {e}")
            return []

# Instance globale du calculateur
weather_index_calculator = WeatherIndexCalculator() 