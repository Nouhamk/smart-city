import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { User, UserPreference, Measurement, Prediction, Alert, PaginatedResponse, ApiResponse } from '../types/models';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Création d'une instance axios avec configuration de base
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification aux requêtes
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig): AxiosRequestConfig => {
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

// Interface pour les credentials d'authentification
interface LoginCredentials {
  username: string;
  password: string;
}

// Interface pour l'enregistrement d'un utilisateur
interface RegisterData {
  username: string;
  email: string;
  password: string;
}

// Interface pour la réponse d'authentification
interface AuthResponse {
  refresh: string;
  access: string;
  user?: User;
}

// Interface pour le changement de mot de passe
interface PasswordChangeData {
  currentPassword: string;
  newPassword: string;
}

// Service d'authentification
export const authService = {
  login(credentials: LoginCredentials): Promise<AxiosResponse<AuthResponse>> {
    return apiClient.post<AuthResponse>('auth/login/', credentials);
  },
  register(user: RegisterData): Promise<AxiosResponse<AuthResponse>> {
    return apiClient.post<AuthResponse>('auth/register/', user);
  },
  getProfile(): Promise<AxiosResponse<User>> {
    return apiClient.get<User>('auth/profile/');
  },
  updateProfile(profile: Partial<User>): Promise<AxiosResponse<User>> {
    return apiClient.put<User>('auth/profile/', profile);
  },
  changePassword(passwordData: PasswordChangeData): Promise<AxiosResponse<ApiResponse<null>>> {
    return apiClient.post<ApiResponse<null>>('auth/change-password/', passwordData);
  },
};

// Interface pour les paramètres de filtrage des mesures
interface MeasurementParams {
  sensor?: number;
  measurementType?: number;
  startDate?: string;
  endDate?: string;
  source?: string;
  page?: number;
  pageSize?: number;
}

// Service pour les données environnementales
export const environmentalService = {
  getCurrentMeasurements(): Promise<AxiosResponse<PaginatedResponse<Measurement>>> {
    return apiClient.get<PaginatedResponse<Measurement>>('environmental-data/measurements/');
  },
  getMeasurementHistory(params: MeasurementParams): Promise<AxiosResponse<PaginatedResponse<Measurement>>> {
    return apiClient.get<PaginatedResponse<Measurement>>('environmental-data/measurements/', { params });
  },
  getPredictions(): Promise<AxiosResponse<PaginatedResponse<Prediction>>> {
    return apiClient.get<PaginatedResponse<Prediction>>('environmental-data/predictions/');
  },
  getAlerts(): Promise<AxiosResponse<PaginatedResponse<Alert>>> {
    return apiClient.get<PaginatedResponse<Alert>>('environmental-data/alerts/');
  },
};

// Service pour les préférences utilisateur
export const userPreferenceService = {
  getSettings(): Promise<AxiosResponse<UserPreference>> {
    return apiClient.get<UserPreference>('user-preferences/');
  },
  updateSettings(settings: Partial<UserPreference>): Promise<AxiosResponse<UserPreference>> {
    return apiClient.put<UserPreference>('user-preferences/', settings);
  },
};

export default {
  auth: authService,
  environmental: environmentalService,
  preferences: userPreferenceService,
};
