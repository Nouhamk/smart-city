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
  metric_weights: {
    [metric: string]: number;
  };
  reference_values?: {
    [metric: string]: {
      min: number;
      max: number;
      optimal: number;
    };
  };
}

export interface WeatherIndexAlert {
  id: number;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'acknowledged' | 'resolved';
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  data?: {
    region: string;
    index_value: number;
    level: string;
    details: any;
  };
}

export interface WeatherIndexHistoryResponse {
  count: number;
  next?: string;
  previous?: string;
  results: WeatherIndex[];
}

const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

// Instance axios avec configuration
const apiClient = axios.create({
  baseURL: API_URL,
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

export const weatherIndexService = {
  /**
   * Récupère l'indice météo global actuel
   */
  async getCurrentIndex(): Promise<AxiosResponse<WeatherIndex>> {
    try {
      const response: AxiosResponse<WeatherIndex> = await apiClient.get('/api/weather-index/current/');
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'indice météo actuel:', error);
      throw error;
    }
  },

  /**
   * Récupère l'historique de l'indice météo avec pagination
   */
  async getIndexHistory(params: {
    page?: number;
    page_size?: number;
    level?: string;
    start_date?: string;
    end_date?: string;
  } = {}): Promise<AxiosResponse<WeatherIndexHistoryResponse>> {
    try {
      const response: AxiosResponse<WeatherIndexHistoryResponse> = await apiClient.get('/api/weather-index/history/', {
        params
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
      throw error;
    }
  },

  /**
   * Récupère la configuration de l'indice météo
   */
  async getConfiguration(): Promise<AxiosResponse<WeatherIndexConfig>> {
    try {
      const response: AxiosResponse<WeatherIndexConfig> = await apiClient.get('/api/weather-index/config/');
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération de la configuration:', error);
      throw error;
    }
  },

  /**
   * Met à jour la configuration de l'indice météo
   */
  async updateConfiguration(config: Partial<WeatherIndexConfig>): Promise<AxiosResponse<WeatherIndexConfig>> {
    try {
      const response: AxiosResponse<WeatherIndexConfig> = await apiClient.put('/api/weather-index/config/', config);
      return response;
    } catch (error) {
      console.error('Erreur lors de la mise à jour de la configuration:', error);
      throw error;
    }
  },

  /**
   * Récupère les alertes actives
   */
  async getActiveAlerts(): Promise<AxiosResponse<WeatherIndexAlert[]>> {
    try {
      const response: AxiosResponse<WeatherIndexAlert[]> = await apiClient.get('/api/weather-index/alerts/', {
        params: { status: 'active' }
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des alertes actives:', error);
      throw error;
    }
  },

  /**
   * Accuse réception d'une alerte
   */
  async acknowledgeAlert(alertId: number): Promise<AxiosResponse<void>> {
    try {
      const response: AxiosResponse<void> = await apiClient.put(`/api/weather-index/alerts/${alertId}/acknowledge/`);
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'accusé de réception:', error);
      throw error;
    }
  },

  /**
   * Résout une alerte
   */
  async resolveAlert(alertId: number): Promise<AxiosResponse<void>> {
    try {
      const response: AxiosResponse<void> = await apiClient.put(`/api/weather-index/alerts/${alertId}/resolve/`);
      return response;
    } catch (error) {
      console.error('Erreur lors de la résolution de l\'alerte:', error);
      throw error;
    }
  },

  // Méthodes legacy pour compatibilité
  async getCurrentWeatherIndex(regions?: string[]): Promise<WeatherIndex[]> {
    try {
      const params: any = {};
      if (regions && regions.length > 0) {
        params.regions = regions.join(',');
      }
      
      const response: AxiosResponse<WeatherIndex[]> = await apiClient.get('/api/weather-index/', { params });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'indice météo:', error);
      throw error;
    }
  },

  async getWeatherIndexHistory(region: string, hours: number = 24): Promise<WeatherIndex[]> {
    try {
      const response: AxiosResponse<WeatherIndex[]> = await apiClient.get('/api/weather-index/history/', {
        params: { region, hours }
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
      throw error;
    }
  },

  async getWeatherIndexConfig(): Promise<WeatherIndexConfig> {
    try {
      const response: AxiosResponse<WeatherIndexConfig> = await apiClient.get('/api/weather-index/config/');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de la configuration:', error);
      throw error;
    }
  },

  async getWeatherIndexAlerts(status: string = 'active'): Promise<WeatherIndexAlert[]> {
    try {
      const response: AxiosResponse<WeatherIndexAlert[]> = await apiClient.get('/api/alerts/', {
        params: { type: 'weather_index', status }
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des alertes:', error);
      throw error;
    }
  }
};

export default weatherIndexService; 