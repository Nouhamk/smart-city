import axios from 'axios';

import { MetricData } from '../store/dashboard'; 
import { apiClient } from './api.service';

const API_URL_RAW = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const API_URL = API_URL_RAW.endsWith('/api') ? API_URL_RAW : API_URL_RAW.replace(/\/?$/, '/api');

// Service pour les données environnementales
const environmentalApiService = {
  /**
   * Récupérer les données pour une métrique spécifique
   * @param metric La métrique à récupérer
   * @param city La ville (optionnel)
   * @param startDate Date de début (optionnel)
   * @param endDate Date de fin (optionnel)
   */
  getMetricData(metric: string, city?: string, startDate?: string, endDate?: string) {
    const params: Record<string, string> = { metric };
    
    if (city && city !== 'all') {
      params.city = city;
    }
    
    if (startDate) {
      params.startDate = startDate;
    }
    
    if (endDate) {
      params.endDate = endDate;
    }
    
    return apiClient.get<{ results: MetricData[] }>(`${API_URL}/environmental-data/metrics/`, { params });
  },
  
  /**
   * Récupérer les données météorologiques actuelles
   * @param city La ville (optionnel)
   */
  getCurrentWeather(city?: string) {
    const params: Record<string, string> = {};
    
    if (city && city !== 'all') {
      params.city = city;
    }
    
    return apiClient.get(`${API_URL}/environmental-data/current-weather/`, { params });
  },
  
  /**
   * Récupérer les prévisions météorologiques
   * @param city La ville (optionnel)
   * @param days Nombre de jours (optionnel, par défaut 5)
   */
  getWeatherForecast(city?: string, days: number = 5) {
    const params: Record<string, string | number> = { days };
    
    if (city && city !== 'all') {
      params.city = city;
    }
    
    return apiClient.get(`${API_URL}/environmental-data/forecast/`, { params });
  },
  
  /**
   * Récupérer les alertes environnementales
   * @param city La ville (optionnel)
   * @param type Type d'alerte (optionnel)
   */
  getAlerts(city?: string, type?: string) {
    const params: Record<string, string> = {};
    
    if (city && city !== 'all') {
      params.city = city;
    }
    
    if (type) {
      params.type = type;
    }
    
    return apiClient.get(`${API_URL}/environmental-data/alerts/`, { params });
  },
  
  /**
   * Récupérer la liste des villes/régions disponibles
   */
  getAvailableCities() {
    console.log('API_URL utilisé pour getAvailableCities:', API_URL);
    return apiClient.get<{ id: string; name: string; latitude: number; longitude: number }[]>(`${API_URL}/regions/`);
  },
  
  /**
   * Récupérer la liste des métriques disponibles
   */
  getAvailableMetrics() {
    return apiClient.get<{ id: string; label: string; unit: string }[]>(`${API_URL}/environmental-data/metrics/available/`);
  }
};

export default environmentalApiService;