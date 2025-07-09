<template>
  <div class="history-settings">
    <h1 class="mb-4">Paramètres et Historique</h1>

    <!-- Section Indice Météo Global -->
    <div class="row mb-4">
      <div class="col-md-6">
        <WeatherIndexCard 
          :auto-refresh="true" 
          :refresh-interval="300000"
          @index-updated="onIndexUpdated"
          @error="onIndexError"
        />
      </div>
      <div class="col-md-6">
        <WeatherIndexAlerts 
          :auto-refresh="true" 
          :refresh-interval="60000"
          status="active"
          @alerts-updated="onAlertsUpdated"
          @error="onAlertsError"
        />
      </div>
    </div>

    <div class="row">
      <!-- Section Paramètres -->
      <div class="col-md-4 mb-4">
        <div class="card mb-4">
          <div class="card-body">
            <h5 class="card-title">Paramètres d'autorité</h5>
            <div class="table-responsive-authority">
              <table class="table table-sm table-bordered mb-0">
                <thead>
                  <tr>
                    <th>Région</th>
                    <th>Date</th>
                    <th>Température</th>
                    <th>Humidité</th>
                    <th>Pression</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in realMetrics" :key="row.region + row.date">
                    <td>{{ row.region }}</td>
                    <td>{{ row.date }}</td>
                    <td>{{ row.temperature !== undefined ? row.temperature + ' °C' : 'Non disponible' }}</td>
                    <td>{{ row.humidity !== undefined ? row.humidity + ' %' : 'Non disponible' }}</td>
                    <td>{{ row.pressure !== undefined ? row.pressure + ' hPa' : 'Non disponible' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

            <!-- Formulaire de config des seuils/poids -->
            <form @submit.prevent="saveConfig" v-if="weatherConfig">
              <div class="mb-3">
                <label class="form-label">Seuil critique</label>
                <input type="number" class="form-control" v-model.number="weatherConfig.critical_threshold">
              </div>
              <div class="mb-3">
                <label class="form-label">Seuil élevé</label>
                <input type="number" class="form-control" v-model.number="weatherConfig.high_threshold">
              </div>
              <div class="mb-3">
                <label class="form-label">Seuil moyen</label>
                <input type="number" class="form-control" v-model.number="weatherConfig.medium_threshold">
              </div>
              <div class="mb-3">
                <label class="form-label">Poids par métrique</label>
                <div v-for="(weight, metric) in weatherConfig.weights" :key="metric" class="input-group mb-1">
                  <span class="input-group-text">{{ metric }}</span>
                  <input type="number" step="0.01" class="form-control" v-model.number="weatherConfig.weights[metric]">
                </div>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="isSaving">
                <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
                Enregistrer la configuration
              </button>
            </form>
          </div>

      <!-- Section Historique -->
      <div class="col-md-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="fas fa-chart-line me-2"></i>
              Analyse des tendances météo
            </h5>
            <div class="refresh-btn" @click="loadPredictions" :class="{ 'spinning': loadingPredictions }">
              <i class="fas fa-sync-alt"></i>
            </div>
          </div>
          <div class="card-body">
            <!-- Loading state -->
            <div v-if="loadingPredictions" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Chargement...</span>
              </div>
              <p class="mt-2">Analyse des données météo...</p>
            </div>

            <!-- Error state -->
            <div v-if="errorPredictions" class="alert alert-danger">
              {{ errorPredictions }}
            </div>

            <!-- Data analysis -->
            <div v-if="!loadingPredictions && predictions.length > 0">
              <!-- Statistiques globales -->
              <div class="row mb-4">
                <div class="col-md-3">
                  <div class="stat-card bg-primary text-white p-3 rounded">
                    <h6 class="mb-1">Régions analysées</h6>
                    <h3 class="mb-0">{{ predictions.length }}</h3>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card bg-success text-white p-3 rounded">
                    <h6 class="mb-1">Temp. moyenne</h6>
                    <h3 class="mb-0">{{ averageTemperature.toFixed(1) }}°C</h3>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card bg-info text-white p-3 rounded">
                    <h6 class="mb-1">Temp. max</h6>
                    <h3 class="mb-0">{{ maxTemperature.toFixed(1) }}°C</h3>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card bg-warning text-white p-3 rounded">
                    <h6 class="mb-1">Temp. min</h6>
                    <h3 class="mb-0">{{ minTemperature.toFixed(1) }}°C</h3>
                  </div>
                </div>
              </div>

              <!-- Répartition par région -->
              <div class="row mb-4">
                <div class="col-md-6">
                  <h6 class="mb-3">
                    <i class="fas fa-map-marker-alt me-2"></i>
                    Répartition par région
                  </h6>
                  <div class="region-stats">
                    <div v-for="region in regionStats" :key="region.name" class="region-item d-flex justify-content-between align-items-center p-2 border-bottom">
                      <div>
                        <strong>{{ region.name }}</strong>
                        <br>
                        <small class="text-muted">{{ region.count }} prédiction(s)</small>
                      </div>
                      <div class="text-end">
                        <div class="fw-bold">{{ region.avgTemp.toFixed(1) }}°C</div>
                        <small class="text-muted">{{ region.minTemp.toFixed(1) }}°C - {{ region.maxTemp.toFixed(1) }}°C</small>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <h6 class="mb-3">
                    <i class="fas fa-thermometer-half me-2"></i>
                    Analyse des températures
                  </h6>
                  <div class="temperature-analysis">
                    <div class="temp-range mb-2">
                      <div class="d-flex justify-content-between">
                        <span>Froid</span>
                        <span>Chaud</span>
                      </div>
                      <div class="progress" style="height: 8px;">
                        <div class="progress-bar bg-info" :style="{ width: coldPercentage + '%' }"></div>
                        <div class="progress-bar bg-warning" :style="{ width: moderatePercentage + '%' }"></div>
                        <div class="progress-bar bg-danger" :style="{ width: hotPercentage + '%' }"></div>
                      </div>
                      <div class="d-flex justify-content-between mt-1">
                        <small class="text-muted">&lt; 15°C ({{ coldCount }})</small>
                        <small class="text-muted">15-25°C ({{ moderateCount }})</small>
                        <small class="text-muted">&gt; 25°C ({{ hotCount }})</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Détails des prédictions -->
              <div class="row">
                <div class="col-12">
                  <h6 class="mb-3">
                    <i class="fas fa-list me-2"></i>
                    Détails des prédictions
                  </h6>
                  <div class="table-responsive">
                    <table class="table table-sm table-hover">
                      <thead class="table-light">
                        <tr>
                          <th>Région</th>
                          <th>Date de prédiction</th>
                          <th>Température</th>
                          <th>Statut</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="pred in predictions" :key="pred.region_id">
                          <td>
                            <strong>{{ pred.region.name }}</strong>
                          </td>
                          <td>{{ formatPredictionDate(pred.time) }}</td>
                          <td>
                            <span class="badge" :class="getTemperatureBadgeClass(pred.temperature)">
                              {{ pred.temperature.toFixed(1) }}°C
                            </span>
                          </td>
                          <td>
                            <span class="badge bg-secondary">{{ getTemperatureStatus(pred.temperature) }}</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            <!-- No data state -->
            <div v-if="!loadingPredictions && predictions.length === 0" class="text-center py-4">
              <i class="fas fa-cloud-slash fa-3x text-muted mb-3"></i>
              <p class="text-muted">Aucune donnée de prédiction disponible</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted, computed } from 'vue';
import { useEnvironmentalStore } from '../store/environmental';
import WeatherIndexCard from '@/components/weather/WeatherIndexCard.vue';
import WeatherIndexAlerts from '@/components/weather/WeatherIndexAlerts.vue';
import type { WeatherIndex, WeatherAlert } from '@/services/weatherIndexService';
import { predictionService } from '@/services/api.service';
import weatherIndexService from '@/services/weatherIndexService';

export default defineComponent({
  name: 'HistorySettingsView',
  components: {
    WeatherIndexCard,
    WeatherIndexAlerts
  },
  setup() {
    const environmentalStore = useEnvironmentalStore();
    const cities = ref(['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille']);
    const isSaving = ref(false);

    // Weather index state
    const currentWeatherIndex = ref<WeatherIndex | null>(null);
    const currentAlerts = ref<WeatherAlert[]>([]);

    // Settings state
    const settings = reactive({
      alertThreshold: 75,
      notificationFrequency: 'hourly',
      monitoringZone: ['Paris'],
      autoAlert: true
    });

    // History state
    const historyFilter = reactive({
      dataType: 'all',
      startDate: '',
      endDate: ''
    });

    // Mock history data
    const historyData = ref([
      {
        id: 1,
        timestamp: '2024-03-10T10:00:00',
        type: 'temperature',
        value: 22.5,
        unit: '°C',
        location: 'Paris'
      },
      // ... more data
    ]);

    // Météo réelle
    const predictions = ref<any[]>([]);
    const weatherConfig = ref<any>(null);
    const loadingPredictions = ref(false);
    const loadingConfig = ref(false);
    const errorPredictions = ref('');
    const errorConfig = ref('');

    // Charger les prédictions météo réelles
    const loadPredictions = async () => {
      loadingPredictions.value = true;
      errorPredictions.value = '';
      try {
        const res = await predictionService.getPredictions();
        predictions.value = res.data;
      } catch (e: any) {
        errorPredictions.value = e?.message || 'Erreur lors du chargement des prédictions';
      } finally {
        loadingPredictions.value = false;
      }
    };

    // Charger la config de l'indice météo
    const loadConfig = async () => {
      loadingConfig.value = true;
      errorConfig.value = '';
      try {
        weatherConfig.value = await weatherIndexService.getConfig();
      } catch (e: any) {
        errorConfig.value = e?.message || 'Erreur lors du chargement de la config';
      } finally {
        loadingConfig.value = false;
      }
    };

    // Sauvegarder la config
    const saveConfig = async () => {
      isSaving.value = true;
      try {
        await weatherIndexService.updateConfig(weatherConfig.value);
        await loadConfig();
      } catch (e: any) {
        alert('Erreur lors de la sauvegarde de la config : ' + (e?.message || '')); 
      } finally {
        isSaving.value = false;
      }
    };

    // Computed properties pour les statistiques
    const averageTemperature = computed(() => {
      if (predictions.value.length === 0) return 0;
      const sum = predictions.value.reduce((acc, pred) => acc + pred.temperature, 0);
      return sum / predictions.value.length;
    });

    const maxTemperature = computed(() => {
      if (predictions.value.length === 0) return 0;
      return Math.max(...predictions.value.map(pred => pred.temperature));
    });

    const minTemperature = computed(() => {
      if (predictions.value.length === 0) return 0;
      return Math.min(...predictions.value.map(pred => pred.temperature));
    });

    const regionStats = computed(() => {
      const stats: { [key: string]: { name: string; count: number; temps: number[] } } = {};
      
      predictions.value.forEach(pred => {
        const regionName = pred.region.name;
        if (!stats[regionName]) {
          stats[regionName] = { name: regionName, count: 0, temps: [] };
        }
        stats[regionName].count++;
        stats[regionName].temps.push(pred.temperature);
      });

      return Object.values(stats).map(region => ({
        name: region.name,
        count: region.count,
        avgTemp: region.temps.reduce((a, b) => a + b, 0) / region.temps.length,
        minTemp: Math.min(...region.temps),
        maxTemp: Math.max(...region.temps)
      }));
    });

    const coldCount = computed(() => {
      return predictions.value.filter(pred => pred.temperature < 15).length;
    });

    const moderateCount = computed(() => {
      return predictions.value.filter(pred => pred.temperature >= 15 && pred.temperature <= 25).length;
    });

    const hotCount = computed(() => {
      return predictions.value.filter(pred => pred.temperature > 25).length;
    });

    const coldPercentage = computed(() => {
      if (predictions.value.length === 0) return 0;
      return (coldCount.value / predictions.value.length) * 100;
    });

    const moderatePercentage = computed(() => {
      if (predictions.value.length === 0) return 0;
      return (moderateCount.value / predictions.value.length) * 100;
    });

    const hotPercentage = computed(() => {
      if (predictions.value.length === 0) return 0;
      return (hotCount.value / predictions.value.length) * 100;
    });

    // Methods
    const saveSettings = async () => {
      isSaving.value = true;
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('Settings saved:', settings);
      } finally {
        isSaving.value = false;
      }
    };

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };

    const formatPredictionDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const getTemperatureBadgeClass = (temp: number) => {
      if (temp < 15) return 'bg-info';
      if (temp <= 25) return 'bg-warning';
      return 'bg-danger';
    };

    const getTemperatureStatus = (temp: number) => {
      if (temp < 15) return 'Froid';
      if (temp <= 25) return 'Modéré';
      return 'Chaud';
    };

    const viewDetails = (item: any) => {
      console.log('View details:', item);
    };

    const deleteRecord = async (id: number) => {
      if (confirm('Êtes-vous sûr de vouloir supprimer cet enregistrement ?')) {
        console.log('Delete record:', id);
      }
    };

    // Weather index event handlers
    const onIndexUpdated = (index: WeatherIndex) => {
      currentWeatherIndex.value = index;
      console.log('Weather index updated:', index);
    };

    const onIndexError = (error: string) => {
      console.error('Weather index error:', error);
    };

    const onAlertsUpdated = (alerts: WeatherAlert[]) => {
      currentAlerts.value = alerts;
      console.log('Weather alerts updated:', alerts);
    };

    const onAlertsError = (error: string) => {
      console.error('Weather alerts error:', error);
    };

    onMounted(() => {
      loadPredictions();
      loadConfig();
    });

    return {
      cities,
      settings,
      isSaving,
      historyFilter,
      historyData,
      currentWeatherIndex,
      currentAlerts,
      saveSettings,
      formatDate,
      formatPredictionDate,
      getTemperatureBadgeClass,
      getTemperatureStatus,
      viewDetails,
      deleteRecord,
      onIndexUpdated,
      onIndexError,
      onAlertsUpdated,
      onAlertsError,
      predictions,
      weatherConfig,
      loadingPredictions,
      loadingConfig,
      errorPredictions,
      errorConfig,
      loadPredictions,
      loadConfig,
      saveConfig,
      // Computed properties
      averageTemperature,
      maxTemperature,
      minTemperature,
      regionStats,
      coldCount,
      moderateCount,
      hotCount,
      coldPercentage,
      moderatePercentage,
      hotPercentage,
      realMetrics: computed(() => {
        const metrics: { region: string; date: string; temperature: number | undefined; humidity: number | undefined; pressure: number | undefined }[] = [];
        predictions.value.forEach(pred => {
          metrics.push({
            region: pred.region.name,
            date: formatPredictionDate(pred.time),
            temperature: pred.temperature,
            humidity: pred.humidity,
            pressure: pred.pressure
          });
        });
        return metrics;
      })
    };
  }
});
</script>

<style scoped>
.history-settings {
  padding: 20px 0;
}

.refresh-btn {
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.refresh-btn.spinning i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.stat-card {
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.region-item {
  transition: background-color 0.2s ease;
}

.region-item:hover {
  background-color: #f8f9fa;
}

.temperature-analysis .progress {
  border-radius: 10px;
}

.temperature-analysis .progress-bar {
  transition: width 0.3s ease;
}

.badge {
  font-size: 0.8em;
  padding: 0.4em 0.6em;
}

.table-responsive-authority {
  width: 100%;
  overflow-x: auto;
}
.table-responsive-authority table {
  min-width: 600px;
}
@media (max-width: 600px) {
  .table-responsive-authority table {
    min-width: 400px;
    font-size: 13px;
  }
}
</style>
