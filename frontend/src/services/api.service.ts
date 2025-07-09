import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Interface pour les credentials d'authentification 
interface LoginCredentials {
  username: string;
  password: string;
}

// Interface pour l'enregistrement
interface RegisterData {
  username: string;
  email: string;
  password: string;
  role?: string; // 'user' | 'admin' | 'public'
}

// Interface pour la réponse d'authentification
interface AuthResponse {
  user: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
  access: string;
  refresh: string;
  message: string;
}

// Interface pour les alertes
interface Alert {
  id: number;
  type: string;
  message: string;
  level: string;
  status: string;
  created_at: string;
  updated_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  data: any;
}

// Interface pour les seuils d'alerte (admin seulement)
interface AlertThreshold {
  id: number;
  type: string;
  value: number;
  zone: string | null;
}

// Interface pour les prédictions (admin seulement)
interface Prediction {
  id: number;
  type: string;
  value: number;
  date: string;
  zone: string | null;
  created_at: string;
}

// Création d'une instance axios avec configuration de base
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 secondes
});

// Intercepteur pour ajouter le token d'authentification aux requêtes
apiClient.interceptors.request.use(
  (config: any) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs de réponse
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('roles');
      localStorage.removeItem('isAdmin');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Service d'authentification
export const authService = {
  // POST /api/auth/login/
  login(credentials: LoginCredentials): Promise<AxiosResponse<AuthResponse>> {
    return apiClient.post<AuthResponse>('/api/auth/login/', credentials);
  },

  // POST /api/auth/register/
  register(userData: RegisterData): Promise<AxiosResponse<AuthResponse>> {
    return apiClient.post<AuthResponse>('/api/auth/register/', userData);
  },

  // POST /api/auth/refresh/
  refreshToken(refreshToken: string): Promise<AxiosResponse<{ access: string }>> {
    return apiClient.post<{ access: string }>('/api/auth/refresh/', {
      refresh: refreshToken
    });
  },

  // POST /api/auth/logout/
  logout(refreshToken: string): Promise<AxiosResponse<void>> {
    return apiClient.post<void>('/api/auth/logout/', {
      refresh: refreshToken
    });
  }
};

// Service pour les alertes (correspond aux endpoints Django)
export const alertService = {
  // GET /api/alerts/
  getActiveAlerts(): Promise<AxiosResponse<Alert[]>> {
    return apiClient.get<Alert[]>('/api/alerts/');
  },

  // GET /api/alerts/history/
  getAlertsHistory(): Promise<AxiosResponse<Alert[]>> {
    return apiClient.get<Alert[]>('/api/alerts/history/');
  },

  // PUT /api/alerts/<id>/acknowledge/
  acknowledgeAlert(alertId: number): Promise<AxiosResponse<Alert>> {
    return apiClient.put<Alert>(`/api/alerts/${alertId}/acknowledge/`);
  },

  // PUT /api/alerts/<id>/resolve/
  resolveAlert(alertId: number): Promise<AxiosResponse<Alert>> {
    return apiClient.put<Alert>(`/api/alerts/${alertId}/resolve/`);
  }
};

// Service pour les seuils d'alerte (admin seulement)
export const thresholdService = {
  // GET /api/alert-thresholds/
  getThresholds(): Promise<AxiosResponse<AlertThreshold[]>> {
    return apiClient.get<AlertThreshold[]>('/api/alert-thresholds/');
  },

  // POST /api/alert-thresholds/
  createThreshold(threshold: Omit<AlertThreshold, 'id'>): Promise<AxiosResponse<AlertThreshold>> {
    return apiClient.post<AlertThreshold>('/api/alert-thresholds/', threshold);
  },

  // PUT /api/alert-thresholds/<id>/
  updateThreshold(id: number, threshold: Partial<AlertThreshold>): Promise<AxiosResponse<AlertThreshold>> {
    return apiClient.put<AlertThreshold>(`/api/alert-thresholds/${id}/`, threshold);
  },

  // DELETE /api/alert-thresholds/<id>/
  deleteThreshold(id: number): Promise<AxiosResponse<void>> {
    return apiClient.delete<void>(`/api/alert-thresholds/${id}/`);
  }
};

// Service pour les prédictions (admin seulement)
export const predictionService = {
  // GET /api/predictions/
  getPredictions(): Promise<AxiosResponse<Prediction[]>> {
    return apiClient.get<Prediction[]>('/api/predictions/');
  },

  // POST /api/predictions/
  createPrediction(prediction: Omit<Prediction, 'id' | 'created_at'>): Promise<AxiosResponse<Prediction>> {
    return apiClient.post<Prediction>('/api/predictions/', prediction);
  },

  // PUT /api/predictions/<id>/
  updatePrediction(id: number, prediction: Partial<Prediction>): Promise<AxiosResponse<Prediction>> {
    return apiClient.put<Prediction>(`/api/predictions/${id}/`, prediction);
  },

  // DELETE /api/predictions/<id>/
  deletePrediction(id: number): Promise<AxiosResponse<void>> {
    return apiClient.delete<void>(`/api/predictions/${id}/`);
  },

  // POST /api/predictions/analyze/
  analyzePredictions(): Promise<AxiosResponse<{ status: string }>> {
    return apiClient.post<{ status: string }>('/api/predictions/analyze/');
  }
};

// Service pour les données environnementales
export const dataService = {
  // GET /api/data
  getData(params: {
    regions?: string[];
    start?: string;
    end?: string;
    metrics?: string[];
  }): Promise<AxiosResponse<any[]>> {
    return apiClient.get('/api/data', { params });
  }
};

export { apiClient };

export default {
  auth: authService,
  alert: alertService,
  threshold: thresholdService,
  prediction: predictionService,
  data: dataService
};