import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from rest_framework.response import Response
from rest_framework import status

# Configuration par défaut de l'indice météo
DEFAULT_CONFIG = {
    "critical_threshold": 85,
    "high_threshold": 70,
    "medium_threshold": 50,
    "weights": {
        "temperature": 0.25,
        "humidity": 0.20,
        "pressure": 0.15,
        "precipitation": 0.20,
        "wind_speed": 0.15,
        "visibility": 0.05
    }
}

class WeatherIndexCalculator:
    def __init__(self):
        self.config = self._load_config()
        self.api_base_url = "http://backend:8000"  # Utiliser le nom du service Docker
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis un fichier JSON"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}")
        return DEFAULT_CONFIG
    
    def _save_config(self, config: Dict[str, Any]):
        """Sauvegarde la configuration dans un fichier JSON"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la config: {e}")
    
    def _normalize_metric(self, value: float, metric: str) -> float:
        """Normalise une métrique entre 0 et 1"""
        if value is None:
            return 0.0
            
        # Ranges de normalisation pour chaque métrique
        ranges = {
            "temperature": (-20, 45),  # -20°C à 45°C
            "humidity": (0, 100),      # 0% à 100%
            "pressure": (900, 1100),   # 900hPa à 1100hPa
            "precipitation": (0, 50),  # 0mm à 50mm
            "wind_speed": (0, 100),    # 0km/h à 100km/h
            "visibility": (0, 50),     # 0km à 50km
            "cloud_cover": (0, 100),   # 0% à 100%
            "apparent_temperature": (-20, 45),
            "dew_point": (-20, 45),
            "precipitation_probability": (0, 100),
            "snow": (0, 50),
            "snow_depth": (0, 100),
            "wind_gust": (0, 150),
            "wind_direction": (0, 360)
        }
        
        if metric not in ranges:
            return 0.0
            
        min_val, max_val = ranges[metric]
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))  # Clamp entre 0 et 1
    
    def _get_metric_contribution(self, normalized_value: float, weight: float) -> float:
        """Calcule la contribution d'une métrique à l'indice global"""
        return normalized_value * weight
    
    def _determine_level(self, index_value: float) -> str:
        """Détermine le niveau d'alerte basé sur la valeur de l'indice"""
        if index_value >= self.config["critical_threshold"]:
            return "critical"
        elif index_value >= self.config["high_threshold"]:
            return "high"
        elif index_value >= self.config["medium_threshold"]:
            return "medium"
        else:
            return "low"
    
    def _fetch_predictions_data(self) -> List[Dict[str, Any]]:
        """Récupère les données de prédictions depuis Supabase"""
        try:
            from data_api.supabase.database import load_predictions
            from data_api.ingestion.cities_ingestion import get_all_regions
            from data_api.mapping.metrics import get_all_metrics
            
            # Récupérer toutes les régions et métriques
            regions = get_all_regions()
            metrics = get_all_metrics()
            
            # Récupérer les prédictions depuis Supabase
            predictions_data = load_predictions(
                start_time=datetime.now().date(),
                regions=regions,
                metrics=metrics
            )
            
            return predictions_data
                
        except Exception as e:
            print(f"Erreur lors de la récupération des prédictions: {e}")
            return []
    
    def calculate_index(self) -> Dict[str, Any]:
        """Calcule l'indice météo global basé sur les prédictions réelles"""
        # Récupérer les données de prédictions
        predictions_data = self._fetch_predictions_data()
        
        if not predictions_data:
            return {
                "error": "Impossible de récupérer les données de prédictions",
                "value": 0,
                "level": "unknown",
                "timestamp": datetime.now().isoformat()
            }
        
        # Prendre les données les plus récentes pour chaque région
        latest_data = {}
        for prediction in predictions_data:
            region_name = prediction.get('region', {}).get('name', 'unknown')
            if region_name not in latest_data:
                latest_data[region_name] = prediction
            else:
                # Garder la donnée la plus récente
                current_time = datetime.fromisoformat(prediction.get('time', '1970-01-01'))
                existing_time = datetime.fromisoformat(latest_data[region_name].get('time', '1970-01-01'))
                if current_time > existing_time:
                    latest_data[region_name] = prediction
        
        # Calculer l'indice global en moyennant toutes les régions
        total_index = 0
        region_count = 0
        all_contributions = {}
        all_details = {}
        
        for region_name, data in latest_data.items():
            region_index = 0
            region_contributions = {}
            region_details = {}
            
            # Calculer l'indice pour cette région
            for metric, weight in self.config["weights"].items():
                raw_value = data.get(metric)
                if raw_value is not None:
                    normalized_value = self._normalize_metric(raw_value, metric)
                    contribution = self._get_metric_contribution(normalized_value, weight)
                    
                    region_index += contribution
                    region_contributions[metric] = contribution
                    region_details[metric] = {
                        "raw_value": raw_value,
                        "normalized": normalized_value,
                        "weight": weight,
                        "contribution": contribution
                    }
            
            # Normaliser les poids pour cette région
            total_weight = sum(self.config["weights"].values())
            if total_weight > 0:
                region_index = (region_index / total_weight) * 100
            
            total_index += region_index
            region_count += 1
            
            # Accumuler les contributions globales
            for metric, contribution in region_contributions.items():
                if metric not in all_contributions:
                    all_contributions[metric] = 0
                all_contributions[metric] += contribution
            
            # Accumuler les détails
            for metric, details in region_details.items():
                if metric not in all_details:
                    all_details[metric] = {
                        "raw_value": 0,
                        "normalized": 0,
                        "weight": details["weight"],
                        "contribution": 0
                    }
                all_details[metric]["raw_value"] += details["raw_value"]
                all_details[metric]["normalized"] += details["normalized"]
                all_details[metric]["contribution"] += details["contribution"]
        
        # Calculer l'indice global moyen
        if region_count > 0:
            global_index = total_index / region_count
            
            # Normaliser les contributions globales
            for metric in all_contributions:
                all_contributions[metric] = all_contributions[metric] / region_count
            
            # Normaliser les détails globaux
            for metric in all_details:
                all_details[metric]["raw_value"] = all_details[metric]["raw_value"] / region_count
                all_details[metric]["normalized"] = all_details[metric]["normalized"] / region_count
                all_details[metric]["contribution"] = all_details[metric]["contribution"] / region_count
        else:
            global_index = 0
        
        # Déterminer le niveau d'alerte
        level = self._determine_level(global_index)
        
        return {
            "value": round(global_index, 2),
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "prediction_time": predictions_data[0].get('time') if predictions_data else None,
            "contributions": all_contributions,
            "details": all_details,
            "regions_count": region_count,
            "config": self.config
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour la configuration de l'indice météo"""
        # Valider la nouvelle configuration
        if "critical_threshold" in new_config:
            self.config["critical_threshold"] = new_config["critical_threshold"]
        if "high_threshold" in new_config:
            self.config["high_threshold"] = new_config["high_threshold"]
        if "medium_threshold" in new_config:
            self.config["medium_threshold"] = new_config["medium_threshold"]
        if "weights" in new_config:
            self.config["weights"].update(new_config["weights"])
        
        # Sauvegarder la nouvelle configuration
        self._save_config(self.config)
        
        return self.config
    
    def get_config(self) -> Dict[str, Any]:
        """Retourne la configuration actuelle"""
        return self.config

# Instance globale du calculateur
weather_index_calculator = WeatherIndexCalculator() 