// Interfaces pour les modèles de données

// Interface utilisateur
export interface User {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  isStaff: boolean;
}

// Interface des préférences utilisateur
export interface UserPreference {
  user: number;
  receiveAlerts: boolean;
  alertThreshold: number;
  defaultLocation: string;
  displayUnit: 'celsius' | 'fahrenheit';
}

// Interface capteur
export interface Sensor {
  id: number;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
  description?: string;
}

// Interface type de mesure
export interface MeasurementType {
  id: number;
  name: string;
  unit: string;
  description?: string;
}

// Interface mesure
export interface Measurement {
  id: number;
  sensor: Sensor;
  measurementType: MeasurementType;
  value: number;
  timestamp: string;
  source: string;
}

// Interface prédiction
export interface Prediction {
  id: number;
  measurementType: MeasurementType;
  sensor: Sensor;
  predictedValue: number;
  predictionTimestamp: string;
  targetTimestamp: string;
  confidence?: number;
}

// Interface alerte
export interface Alert {
  id: number;
  title: string;
  description: string;
  level: 'INFO' | 'WARNING' | 'DANGER';
  measurementType?: MeasurementType;
  sensor?: Sensor;
  timestamp: string;
  isActive: boolean;
}

// Interface pour les données du tableau de bord
export interface DashboardData {
  airQualityIndex: string;
  airQualityLabel: string;
  temperature: string;
  weatherDescription: string;
  trafficLevel: string;
  trafficDescription: string;
  predictions: {
    airQuality: string;
    temperature: string;
    humidity: string;
  };
  alerts: Array<{
    message: string;
    level?: string;
  }>;
}

// Interface pour le filtrage des données historiques
export interface HistoryFilter {
  dataType: string;
  startDate: string;
  endDate: string;
}

// Interface réponse API
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

// Interface pagination
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
