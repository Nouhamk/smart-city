import axios, { AxiosResponse, AxiosRequestConfig } from 'axios';

// Types pour l'indice météo
export interface WeatherIndex {
  id?: number;
  value: number;
  level: 'low' | 'medium' | 'high' | 'critical';
  region?: string;
  timestamp: string;
  prediction_time?: string;
  temperature?: number;
  humidity?: number;
  pressure?: number;
  precipitation?: number;
  wind_speed?: number;
  visibility?: number;
  cloud_cover?: number;
  contributions?: {
    [metric: string]: number;
  };
  details?: {
    [metric: string]: {
      raw_value: number;
      normalized: number;
      weight: number;
      contribution: number;
    };
  };
}

export interface WeatherIndexConfig {
  critical_threshold: number;
  high_threshold: number;
  medium_threshold: number;
  weights: {
    [metric: string]: number;
  };
}

export interface WeatherIndexHistory {
  count: number;
  next?: string;
  previous?: string;
  results: WeatherIndex[];
}

export interface WeatherAlert {
  id: number;
  type: string;
  message: string;
  level: string;
  status: string;
  created_at: string;
  weather_index_value?: number;
  weather_index_level?: string;
}

// Configuration de l'API
const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

// Client axios configuré
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Service pour l'indice météo
export const weatherIndexService = {
  // Obtenir l'indice météo actuel
  async getCurrentIndex(): Promise<WeatherIndex> {
    try {
      const response: AxiosResponse<WeatherIndex> = await apiClient.get('/api/weather-index/');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'indice météo actuel:', error);
      throw error;
    }
  },

  // Obtenir l'historique de l'indice météo
  async getHistory(page: number = 1, pageSize: number = 10): Promise<WeatherIndexHistory> {
    try {
      // Pour l'instant, retourner un historique vide car l'endpoint n'est pas encore implémenté
      return {
        count: 0,
        results: []
      };
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
      throw error;
    }
  },

  // Obtenir la configuration de l'indice météo
  async getConfig(): Promise<WeatherIndexConfig> {
    try {
      const response: AxiosResponse<WeatherIndexConfig> = await apiClient.get('/api/weather-index/config/');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de la configuration:', error);
      throw error;
    }
  },

  // Mettre à jour la configuration de l'indice météo
  async updateConfig(config: Partial<WeatherIndexConfig>): Promise<WeatherIndexConfig> {
    try {
      const response: AxiosResponse<WeatherIndexConfig> = await apiClient.put('/api/weather-index/config/', config);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la mise à jour de la configuration:', error);
      throw error;
    }
  },

  // Obtenir les alertes météo actives
  async getAlerts(status: string = 'active'): Promise<{ alerts: WeatherAlert[] }> {
    try {
      // Pour l'instant, retourner des alertes vides car l'endpoint n'existe pas encore
      return { alerts: [] };
    } catch (error) {
      console.error('Erreur lors de la récupération des alertes:', error);
      throw error;
    }
  },

  // Calculer l'indice météo (pour forcer un recalcul)
  async calculateIndex(): Promise<WeatherIndex> {
    try {
      const response: AxiosResponse<WeatherIndex> = await apiClient.get('/api/weather-index/');
      return response.data;
    } catch (error) {
      console.error('Erreur lors du calcul de l\'indice météo:', error);
      throw error;
    }
  },
};

export default weatherIndexService; 