import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Types
export interface MetricData {
  city: string;
  timestamp: string;
  hour: number;
  value: number;
  displayTime: string;
}

export interface MetricConfig {
  label: string;
  unit: string;
  color: string;
}

export const useDashboardStore = defineStore('dashboard', () => {
  // État
  const selectedMetric = ref('temp');
  const selectedCity = ref('all');
  const cities = ref(['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille']);
  const metricData = ref<MetricData[]>([]);
  const currentValues = ref<Record<string, number>>({});
  const averageValues = ref<Record<string, number>>({});
  const trendValues = ref<Record<string, number>>({});
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Propriétés calculées
  const metricConfig = computed<MetricConfig>(() => {
    const configs: Record<string, MetricConfig> = {
      temp: { label: 'Température (2 m)', unit: '°C', color: '#f44336' },
      feelslike: { label: 'Température ressentie', unit: '°C', color: '#ff9800' },
      humidity: { label: 'Humidité relative (2 m)', unit: '%', color: '#2196f3' },
      dew: { label: 'Point de rosée (2 m)', unit: '°C', color: '#4caf50' },
      precipprob: { label: 'Probabilité de précipitation', unit: '%', color: '#03a9f4' },
      precip: { label: 'Précipitation (pluie + averses + neige)', unit: 'mm', color: '#3f51b5' },
      snow: { label: 'Chute de neige', unit: 'cm', color: '#9c27b0' },
      snowdepth: { label: 'Épaisseur de neige', unit: 'cm', color: '#673ab7' },
      windgust: { label: 'Rafales de vent (10 m)', unit: 'km/h', color: '#795548' },
      windspeed: { label: 'Vitesse du vent (10 m)', unit: 'km/h', color: '#8d6e63' },
      winddir: { label: 'Direction du vent (10 m)', unit: '°', color: '#607d8b' },
      pressure: { label: 'Pression au niveau de la mer', unit: 'hPa', color: '#ff5722' },
      visibility: { label: 'Visibilité', unit: 'km', color: '#009688' },
      cloudcover: { label: 'Couverture nuageuse totale', unit: '%', color: '#78909c' }
    };
    
    return configs[selectedMetric.value] || { label: selectedMetric.value, unit: '', color: '#000000' };
  });

  // Actions
  const fetchMetricData = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      // Dans une implémentation réelle, on fera un appel API ici
      // Exemple: const response = await api.getMetricData(selectedMetric.value, selectedCity.value);
      
      // Pour la démonstration, nous générons des données fictives
      const allData = generateDataForMetric(selectedMetric.value, cities.value);
      
      // Filtrer par ville si nécessaire
      const filteredData = selectedCity.value === 'all' 
        ? allData 
        : allData.filter(item => item.city === selectedCity.value);
      
      metricData.value = filteredData;
      
      // Calculer les valeurs actuelles et moyennes
      const current: Record<string, number> = {};
      const average: Record<string, number> = {};
      const trend: Record<string, number> = {};
      
      cities.value.forEach(city => {
        const cityData = allData.filter(item => item.city === city);
        // Trier les données par timestamp (plus récente d'abord)
        cityData.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        
        // Prendre la valeur la plus récente pour chaque ville
        current[city] = cityData.length > 0 ? cityData[0].value : 0;
        
        // Calculer la moyenne pour chaque ville
        average[city] = cityData.length > 0 
          ? parseFloat((cityData.reduce((sum, item) => sum + item.value, 0) / cityData.length).toFixed(1))
          : 0;

        // Calculer la tendance (différence entre la valeur actuelle et la précédente)
        trend[city] = cityData.length > 1 ? parseFloat((cityData[0].value - cityData[1].value).toFixed(1)) : 0;
      });
      
      currentValues.value = current;
      averageValues.value = average;
      trendValues.value = trend;
    } catch (err: any) {
      error.value = 'Erreur lors du chargement des données: ' + (err.message || 'Erreur inconnue');
      console.error(err);
    } finally {
      loading.value = false;
    }
  };

  // Générer des données fictives pour la démo
  const generateDataForMetric = (metric: string, cities: string[]): MetricData[] => {
    const now = new Date();
    const data: MetricData[] = [];
    
    cities.forEach(city => {
      // Générer 24 heures de données pour chaque ville
      for (let i = 0; i < 24; i++) {
        const date = new Date(now);
        date.setHours(date.getHours() - i);
        
        let value: number;
        switch(metric) {
          case 'temp':
            value = 15 + Math.random() * 10; // Entre 15°C et 25°C
            break;
          case 'feelslike':
            value = 14 + Math.random() * 10; // Légèrement plus bas que la température réelle
            break;
          case 'humidity':
            value = 50 + Math.random() * 30; // Entre 50% et 80%
            break;
          case 'dew':
            value = 5 + Math.random() * 10; // Entre 5°C et 15°C
            break;
          case 'precipprob':
            value = Math.random() * 100; // Entre 0% et 100%
            break;
          case 'precip':
            value = Math.random() * 10; // Entre 0mm et 10mm
            break;
          case 'snow':
            value = Math.random() * 5; // Entre 0cm et 5cm
            break;
          case 'snowdepth':
            value = Math.random() * 10; // Entre 0cm et 10cm
            break;
          case 'windgust':
            value = 10 + Math.random() * 20; // Entre 10km/h et 30km/h
            break;
          case 'windspeed':
            value = 5 + Math.random() * 15; // Entre 5km/h et 20km/h
            break;
          case 'winddir':
            value = Math.random() * 360; // Entre 0° et 360°
            break;
          case 'pressure':
            value = 1000 + Math.random() * 30; // Entre 1000hPa et 1030hPa
            break;
          case 'visibility':
            value = 5 + Math.random() * 15; // Entre 5km et 20km
            break;
          case 'cloudcover':
            value = Math.random() * 100; // Entre 0% et 100%
            break;
          default:
            value = Math.random() * 100;
        }
        
        data.push({
          city,
          timestamp: date.toISOString(),
          hour: date.getHours(),
          value: parseFloat(value.toFixed(1)),
          displayTime: `${date.getHours()}:00`
        });
      }
    });
    
    return data;
  };

  // Méthodes utilitaires
  const formatValue = (value: number | undefined): string => {
    return value !== undefined ? value.toFixed(1) : '0.0';
  };

  const getCurrentValue = (city?: string): string => {
    const cityToUse = city || selectedCity.value;
    
    if (cityToUse === 'all') {
      const values = Object.values(currentValues.value);
      if (values.length === 0) return '0.0';
      return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(1);
    }
    
    return formatValue(currentValues.value[cityToUse]);
  };

  const getAverageValue = (city?: string): string => {
    const cityToUse = city || selectedCity.value;
    
    if (cityToUse === 'all') {
      const values = Object.values(averageValues.value);
      if (values.length === 0) return '0.0';
      return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(1);
    }
    
    return formatValue(averageValues.value[cityToUse]);
  };

  const getMinValue = (): string => {
    const filteredData = selectedCity.value === 'all'
      ? metricData.value
      : metricData.value.filter(item => item.city === selectedCity.value);
    
    if (filteredData.length === 0) return '0.0';
    
    return Math.min(...filteredData.map(item => item.value)).toFixed(1);
  };

  const getMaxValue = (): string => {
    const filteredData = selectedCity.value === 'all'
      ? metricData.value
      : metricData.value.filter(item => item.city === selectedCity.value);
    
    if (filteredData.length === 0) return '0.0';
    
    return Math.max(...filteredData.map(item => item.value)).toFixed(1);
  };

  const getTrendValue = (city: string): number => {
    return trendValues.value[city] || 0;
  };

  // Changer la métrique sélectionnée et charger les données
  const changeMetric = (metric: string) => {
    selectedMetric.value = metric;
    fetchMetricData();
  };

  // Changer la ville sélectionnée et charger les données
  const changeCity = (city: string) => {
    selectedCity.value = city;
    fetchMetricData();
  };

  return {
    // État
    selectedMetric,
    selectedCity,
    cities,
    metricData,
    currentValues,
    averageValues,
    trendValues,
    loading,
    error,
    
    // Propriétés calculées
    metricConfig,
    
    // Actions
    fetchMetricData,
    changeMetric,
    changeCity,
    
    // Méthodes utilitaires
    formatValue,
    getCurrentValue,
    getAverageValue,
    getMinValue,
    getMaxValue,
    getTrendValue
  };
});