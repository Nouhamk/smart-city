<template>
  <div class="dashboard">
    <!-- En-tête et filtres -->
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h1 class="mb-0">Tableau de Bord Environnemental</h1>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="metricSelect" class="form-label">Métrique</label>
            <select id="metricSelect" class="form-select" v-model="selectedMetric">
              <option value="temp">Température (2 m)</option>
              <option value="feelslike">Température ressentie</option>
              <option value="humidity">Humidité relative (2 m)</option>
              <option value="dew">Point de rosée (2 m)</option>
              <option value="precipprob">Probabilité de précipitation</option>
              <option value="precip">Précipitation (pluie + averses + neige)</option>
              <option value="snow">Chute de neige</option>
              <option value="snowdepth">Épaisseur de neige</option>
              <option value="windgust">Rafales de vent (10 m)</option>
              <option value="windspeed">Vitesse du vent (10 m)</option>
              <option value="winddir">Direction du vent (10 m)</option>
              <option value="pressure">Pression au niveau de la mer</option>
              <option value="visibility">Visibilité</option>
              <option value="cloudcover">Couverture nuageuse totale</option>
            </select>
          </div>
          <div class="col-md-6 mb-3">
            <label for="citySelect" class="form-label">Ville</label>
            <select id="citySelect" class="form-select" v-model="selectedCity">
              <option value="all">Toutes les villes</option>
              <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    

    <!-- KPI principaux -->
    <div class="row mb-4">
      <!-- Valeur actuelle -->
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Valeur actuelle</h5>
          </div>
          <div class="card-body d-flex flex-column justify-content-center">
            <div class="d-flex align-items-baseline">
              <h2 class="mb-0">{{ getCurrentValue() }}</h2>
              <span class="ms-2">{{ metricConfig.unit }}</span>
            </div>
            <div class="text-muted">{{ metricConfig.label }}</div>
          </div>
        </div>
      </div>

      <!-- Moyenne -->
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Moyenne (24h)</h5>
          </div>
          <div class="card-body d-flex flex-column justify-content-center">
            <div class="d-flex align-items-baseline">
              <h2 class="mb-0">{{ getAverageValue() }}</h2>
              <span class="ms-2">{{ metricConfig.unit }}</span>
            </div>
            <div class="text-muted">{{ metricConfig.label }}</div>
          </div>
        </div>
      </div>

      <!-- Min/Max -->
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Min / Max (24h)</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-6">
                <div class="text-muted">Min</div>
                <div class="d-flex align-items-baseline">
                  <h4 class="mb-0">{{ getMinValue() }}</h4>
                  <small class="ms-1">{{ metricConfig.unit }}</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-muted">Max</div>
                <div class="d-flex align-items-baseline">
                  <h4 class="mb-0">{{ getMaxValue() }}</h4>
                  <small class="ms-1">{{ metricConfig.unit }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Graphiques -->
    <div class="row mb-4">
      <!-- Graphique d'évolution temporelle -->
      <div class="col-lg-8 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Évolution sur 24 heures</h5>
          </div>
          <div class="card-body">
            <div class="chart-container" style="height: 300px;">
              <canvas ref="lineChartRef"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Distribution par ville -->
      <div class="col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Distribution par ville</h5>
          </div>
          <div class="card-body">
            <div class="chart-container" style="height: 300px;">
              <canvas ref="pieChartRef"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Section Alertes récentes -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Alertes récentes</h5>
          </div>
          <div class="card-body p-0">
            <div v-if="alerts.length === 0" class="text-center p-3">
              <p class="text-muted mb-0">Aucune alerte active</p>
            </div>
            <div v-else>
              <div v-for="(alert, index) in alerts" :key="index" 
                   class="alert-item border-start border-5" 
                   :class="getAlertClass(alert.level)">
                <div class="d-flex p-3">
                  <div class="alert-icon me-3">
                    <i class="bi" :class="getAlertIcon(alert.level)"></i>
                  </div>
                  <div class="alert-content flex-grow-1">
                    <h6 class="mb-1 fw-bold">{{ alert.title }}</h6>
                    <p class="mb-1">{{ alert.description }}</p>
                    <small class="text-muted">{{ formatDate(alert.timestamp) }}</small>
                  </div>
                </div>
                <div v-if="index < alerts.length - 1" class="border-bottom"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Graphique de comparaison par ville -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Comparaison par ville (moyenne)</h5>
          </div>
          <div class="card-body">
            <div class="chart-container" style="height: 300px;">
              <canvas ref="barChartRef"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tableau des valeurs actuelles -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Valeurs actuelles par ville</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Ville</th>
                    <th>Valeur actuelle</th>
                    <th>Moyenne (24h)</th>
                    <th>Tendance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="city in cities" :key="city">
                    <td>{{ city }}</td>
                    <td>{{ formatValue(currentValues[city]) }} {{ metricConfig.unit }}</td>
                    <td>{{ formatValue(averageValues[city]) }} {{ metricConfig.unit }}</td>
                    <td>
                      <div class="d-flex align-items-center">
                        <span :class="getTrendClass(getTrendValue(city))">
                          {{ getTrendValue(city) > 0 ? '↑' : getTrendValue(city) < 0 ? '↓' : '→' }}
                        </span>
                        <span class="ms-1">{{ formatValue(Math.abs(getTrendValue(city))) }} {{ metricConfig.unit }}</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, computed } from 'vue';
import Chart from 'chart.js/auto';

// Types
interface MetricData {
  city: string;
  timestamp: string;
  hour: number;
  value: number;
  displayTime: string;
}

interface MetricConfig {
  label: string;
  unit: string;
  color: string;
}

interface Alert {
  id: number;
  title: string;
  description: string;
  level: 'INFO' | 'WARNING' | 'DANGER';
  timestamp: string;
}

export default defineComponent({
  name: 'EnvironmentalDashboard',
  setup() {
    // Références pour les graphiques
    const lineChartRef = ref<HTMLCanvasElement | null>(null);
    const barChartRef = ref<HTMLCanvasElement | null>(null);
    const pieChartRef = ref<HTMLCanvasElement | null>(null);
    
    // Charts instances
    let lineChart: Chart | null = null;
    let barChart: Chart | null = null;
    let pieChart: Chart | null = null;

    // État
    const selectedMetric = ref('temp');
    const selectedCity = ref('all');
    const cities = ref(['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille']);
    const metricData = ref<MetricData[]>([]);
    const currentValues = ref<Record<string, number>>({});
    const averageValues = ref<Record<string, number>>({});
    const trendValues = ref<Record<string, number>>({});

    // Données d'alertes
    const alerts = ref<Alert[]>([
      {
            id: 1,
            title: "Température élevée",
            description: "Pic de température à 35.2°C dans le centre de Paris",
            level: "DANGER",
            timestamp: new Date().toISOString(),
            metricType: "temp",
            value: 35.2,
            unit: "°C"
          },
          {
            id: 2,
            title: "Pic de pollution atmosphérique",
            description: "Indice de qualité de l'air supérieur à 80 à Marseille",
            level: "WARNING",
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            metricType: "airquality",
            value: 82,
            unit: "AQI"
          },
          {
            id: 3,
            title: "Risque de précipitations",
            description: "Probabilité de précipitation de 75% à Lyon",
            level: "INFO",
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            metricType: "precipprob",
            value: 75,
            unit: "%"
          },
          {
            id: 4,
            title: "Humidité élevée",
            description: "Niveau d'humidité de 85% à Bordeaux",
            level: "INFO",
            timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
            metricType: "humidity",
            value: 85,
            unit: "%"
          },
          {
            id: 5,
            title: "Baisse de la pression atmosphérique",
            description: "Chute de pression à 995 hPa, risque de dégradation météo",
            level: "WARNING",
            timestamp: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
            metricType: "pressure",
            value: 995,
            unit: "hPa"
          }
    ]);

    // Fonctions pour les alertes
    const getAlertClass = (level: string): string => {
      switch (level) {
        case 'DANGER':
          return 'border-danger bg-danger bg-opacity-10';
        case 'WARNING':
          return 'border-warning bg-warning bg-opacity-10';
        case 'INFO':
        default:
          return 'border-info bg-info bg-opacity-10';
      }
    };

    const getAlertIcon = (level: string): string => {
      switch (level) {
        case 'DANGER':
          return 'bi-exclamation-circle-fill text-danger';
        case 'WARNING':
          return 'bi-exclamation-triangle-fill text-warning';
        case 'INFO':
        default:
          return 'bi-info-circle-fill text-info';
      }
    };

    const formatDate = (dateString: string): string => {
      const date = new Date(dateString);
      const now = new Date();
      const isToday = date.getDate() === now.getDate() && 
                     date.getMonth() === now.getMonth() && 
                     date.getFullYear() === now.getFullYear();
      
      const isYesterday = date.getDate() === now.getDate() - 1 && 
                         date.getMonth() === now.getMonth() && 
                         date.getFullYear() === now.getFullYear();
      
      const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      if (isToday) {
        return `Aujourd'hui, ${timeStr}`;
      } else if (isYesterday) {
        return `Hier, ${timeStr}`;
      } else {
        return date.toLocaleDateString() + `, ${timeStr}`;
      }
    };

    // Couleurs pour les graphiques
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

    // Configuration de la métrique
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

    // Génération de données fictives
    const generateDataForMetric = (metric: string, cities: string[]) => {
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

    // Charger les données
    const loadData = () => {
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
      
      // Mettre à jour les graphiques
      updateCharts();
    };

    // Préparer les données pour le graphique en ligne
    const prepareLineChartData = () => {
      if (metricData.value.length === 0) return { labels: [], datasets: [] };
      
      // Grouper par heure et ville
      const groupedData: Record<string, Record<string, any>> = {};
      
      metricData.value.forEach(item => {
        if (!groupedData[item.displayTime]) {
          groupedData[item.displayTime] = { displayTime: item.displayTime };
        }
        groupedData[item.displayTime][item.city] = item.value;
      });
      
      const sortedData = Object.values(groupedData).sort((a, b) => {
        const hourA = parseInt(a.displayTime.split(':')[0]);
        const hourB = parseInt(b.displayTime.split(':')[0]);
        return hourB - hourA; // Tri par ordre croissant des heures
      });
      
      const labels = sortedData.map(item => item.displayTime);
      
      const datasets = selectedCity.value === 'all'
        ? cities.value.map((city, index) => ({
            label: city,
            data: sortedData.map(item => item[city] || null),
            backgroundColor: COLORS[index % COLORS.length] + '20',
            borderColor: COLORS[index % COLORS.length],
            tension: 0.4
          }))
        : [{
            label: selectedCity.value,
            data: sortedData.map(item => item[selectedCity.value] || null),
            backgroundColor: metricConfig.value.color + '20',
            borderColor: metricConfig.value.color,
            tension: 0.4
          }];
      
      return { labels, datasets };
    };

    // Préparer les données pour le graphique à barres
    const prepareBarChartData = () => {
      if (Object.keys(averageValues.value).length === 0) return { labels: [], datasets: [] };
      
      const labels = cities.value;
      const data = cities.value.map(city => averageValues.value[city] || 0);
      
      return {
        labels,
        datasets: [{
          label: metricConfig.value.label,
          data,
          backgroundColor: metricConfig.value.color + '80',
          borderColor: metricConfig.value.color,
          borderWidth: 1
        }]
      };
    };

    // Préparer les données pour le graphique circulaire
    const preparePieChartData = () => {
      if (Object.keys(currentValues.value).length === 0) return { labels: [], datasets: [] };
      
      const labels = cities.value;
      const data = cities.value.map(city => currentValues.value[city] || 0);
      
      return {
        labels,
        datasets: [{
          label: metricConfig.value.label,
          data,
          backgroundColor: cities.value.map((_, index) => COLORS[index % COLORS.length]),
          borderWidth: 1
        }]
      };
    };

    // Créer ou mettre à jour les graphiques
    const updateCharts = () => {
      // Graphique en ligne
      if (lineChartRef.value) {
        if (lineChart) {
          lineChart.destroy();
        }
        
        const lineChartData = prepareLineChartData();
        const ctx = lineChartRef.value.getContext('2d');
        
        if (ctx) {
          lineChart = new Chart(ctx, {
            type: 'line',
            data: lineChartData,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return `${context.dataset.label}: ${context.raw} ${metricConfig.value.unit}`;
                    }
                  }
                }
              },
              scales: {
                y: {
                  beginAtZero: false,
                  title: {
                    display: true,
                    text: metricConfig.value.unit
                  }
                }
              }
            }
          });
        }
      }

      // Graphique à barres
      if (barChartRef.value) {
        if (barChart) {
          barChart.destroy();
        }
        
        const barChartData = prepareBarChartData();
        const ctx = barChartRef.value.getContext('2d');
        
        if (ctx) {
          barChart = new Chart(ctx, {
            type: 'bar',
            data: barChartData,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return `${context.dataset.label}: ${context.raw} ${metricConfig.value.unit}`;
                    }
                  }
                }
              },
              scales: {
                y: {
                  beginAtZero: false,
                  title: {
                    display: true,
                    text: metricConfig.value.unit
                  }
                }
              }
            }
          });
        }
      }

      // Graphique circulaire
      if (pieChartRef.value) {
        if (pieChart) {
          pieChart.destroy();
        }
        
        const pieChartData = preparePieChartData();
        const ctx = pieChartRef.value.getContext('2d');
        
        if (ctx) {
          pieChart = new Chart(ctx, {
            type: 'pie',
            data: pieChartData,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return `${context.label}: ${context.raw} ${metricConfig.value.unit}`;
                    }
                  }
                }
              }
            }
          });
        }
      }
    };

    // Formater les valeurs
    const formatValue = (value: number | undefined): string => {
      return value !== undefined ? value.toFixed(1) : '0.0';
    };

    // Obtenir la valeur actuelle
    const getCurrentValue = () => {
      if (selectedCity.value === 'all') {
        const values = Object.values(currentValues.value);
        if (values.length === 0) return '0.0';
        return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(1);
      }
      
      return formatValue(currentValues.value[selectedCity.value]);
    };

    // Obtenir la valeur moyenne
    const getAverageValue = () => {
      if (selectedCity.value === 'all') {
        const values = Object.values(averageValues.value);
        if (values.length === 0) return '0.0';
        return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(1);
      }
      
      return formatValue(averageValues.value[selectedCity.value]);
    };

    // Obtenir la valeur minimale
    const getMinValue = () => {
      const filteredData = selectedCity.value === 'all'
        ? metricData.value
        : metricData.value.filter(item => item.city === selectedCity.value);
      
      if (filteredData.length === 0) return '0.0';
      
      return Math.min(...filteredData.map(item => item.value)).toFixed(1);
    };

    // Obtenir la valeur maximale
    const getMaxValue = () => {
      const filteredData = selectedCity.value === 'all'
        ? metricData.value
        : metricData.value.filter(item => item.city === selectedCity.value);
      
      if (filteredData.length === 0) return '0.0';
      
      return Math.max(...filteredData.map(item => item.value)).toFixed(1);
    };

    // Obtenir la valeur de tendance
    const getTrendValue = (city: string): number => {
      return trendValues.value[city] || 0;
    };

    // Obtenir la classe CSS pour la tendance
    const getTrendClass = (value: number): string => {
      if (value > 0) return 'text-success';
      if (value < 0) return 'text-danger';
      return 'text-secondary';
    };

    // Surveiller les changements de métrique et de ville
    watch([selectedMetric, selectedCity], () => {
      loadData();
    });

    // Initialiser les données au montage du composant
    onMounted(() => {
      loadData();
      console.log("Dashboard component mounted");
      console.log("Alerts:", alerts.value);
    });

    return {
      // Références
      lineChartRef,
      barChartRef,
      pieChartRef,
      
      // État
      selectedMetric,
      selectedCity,
      cities,
      metricData,
      currentValues,
      averageValues,
      
      // Propriétés calculées
      metricConfig,
      
      // Méthodes
      formatValue,
      getCurrentValue,
      getAverageValue,
      getMinValue,
      getMaxValue,
      getTrendValue,
      getTrendClass,
      
      // Pour les alertes
      alerts,
      getAlertClass,
      getAlertIcon,
      formatDate
    };
  }
});
</script>

<style scoped>
.dashboard {
  padding: 20px 0;
}

.chart-container {
  position: relative;
  margin: auto;
}

.alert-item {
  transition: background-color 0.2s;
}

.alert-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.alert-icon {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
}
</style>