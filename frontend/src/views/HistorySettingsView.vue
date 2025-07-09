<template>
  <div class="history-settings">
    <h1 class="mb-4">Paramètres et Historique</h1>

    <!-- Section Indice Météo Actuel -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Indice Météo Global</h5>
            <span class="badge" :class="getIndexBadgeClass(currentIndex?.level)">
              {{ currentIndex?.level || 'Chargement...' }}
            </span>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="d-flex align-items-center mb-3">
                  <div class="weather-index-display me-3">
                    <div class="index-value">{{ currentIndex?.value || '--' }}</div>
                    <div class="index-label">Indice Global</div>
                  </div>
                  <div class="index-details">
                    <div class="text-muted">Dernière mise à jour</div>
                    <div>{{ formatDate(currentIndex?.timestamp) || '--' }}</div>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="metric-contributions">
                  <h6>Contributions des métriques :</h6>
                  <div v-if="currentIndex?.contributions" class="row">
                    <div v-for="(contribution, metric) in currentIndex.contributions" :key="metric" class="col-6 mb-2">
                      <div class="d-flex justify-content-between">
                        <span class="text-capitalize">{{ getMetricLabel(metric) }}</span>
                        <span class="fw-bold">{{ contribution.toFixed(1) }}%</span>
                      </div>
                      <div class="progress" style="height: 4px;">
                        <div class="progress-bar" :style="{ width: contribution + '%' }"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Section Paramètres -->
      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Paramètres d'autorité</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveSettings">
              <!-- Seuil d'alerte existant -->
              <div class="mb-3">
                <label class="form-label">Seuil d'alerte</label>
                <div class="input-group">
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="settings.alertThreshold"
                    min="0"
                    max="100"
                  >
                  <span class="input-group-text">%</span>
                </div>
                <small class="form-text text-muted">Seuil pour déclencher les alertes météo</small>
              </div>

              <!-- Nouveaux paramètres pour l'indice météo -->
              <div class="mb-3">
                <label class="form-label">Seuils de l'indice météo</label>
                <div class="row">
                  <div class="col-6">
                    <label class="form-label small">Seuil Critique</label>
                    <input 
                      type="number" 
                      class="form-control" 
                      v-model="settings.criticalThreshold"
                      min="0"
                      max="100"
                    >
                  </div>
                  <div class="col-6">
                    <label class="form-label small">Seuil Élevé</label>
                    <input 
                      type="number" 
                      class="form-control" 
                      v-model="settings.highThreshold"
                      min="0"
                      max="100"
                    >
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Poids des métriques</label>
                <div v-for="metric in weatherMetrics" :key="metric.key" class="mb-2">
                  <div class="d-flex justify-content-between align-items-center">
                    <label class="form-label small mb-0">{{ metric.label }}</label>
                    <span class="text-muted small">{{ settings.metricWeights[metric.key] }}%</span>
                  </div>
                  <input 
                    type="range" 
                    class="form-range" 
                    v-model="settings.metricWeights[metric.key]"
                    min="0"
                    max="100"
                    @input="normalizeWeights"
                  >
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Fréquence de notification</label>
                <select class="form-select" v-model="settings.notificationFrequency">
                  <option value="realtime">Temps réel</option>
                  <option value="hourly">Toutes les heures</option>
                  <option value="daily">Quotidien</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Zone de surveillance</label>
                <select class="form-select" v-model="settings.monitoringZone" multiple>
                  <option v-for="city in cities" :key="city.id" :value="city.name">
                    {{ city.name }}
                  </option>
                </select>
              </div>

              <div class="form-check mb-3">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="autoAlert"
                  v-model="settings.autoAlert"
                >
                <label class="form-check-label" for="autoAlert">
                  Alertes automatiques
                </label>
              </div>

              <button type="submit" class="btn btn-primary" :disabled="isSaving">
                <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
                Enregistrer
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- Section Historique -->
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Historique de l'indice météo</h5>
          </div>
          <div class="card-body">
            <!-- Filtres -->
            <div class="row mb-4">
              <div class="col-md-3">
                <label class="form-label">Niveau d'alerte</label>
                <select class="form-select" v-model="historyFilter.level">
                  <option value="all">Tous les niveaux</option>
                  <option value="low">Faible</option>
                  <option value="medium">Moyen</option>
                  <option value="high">Élevé</option>
                  <option value="critical">Critique</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Date début</label>
                <input type="date" class="form-control" v-model="historyFilter.startDate">
              </div>
              <div class="col-md-3">
                <label class="form-label">Date fin</label>
                <input type="date" class="form-control" v-model="historyFilter.endDate">
              </div>
              <div class="col-md-3">
                <label class="form-label">&nbsp;</label>
                <button class="btn btn-outline-primary d-block w-100" @click="loadHistory">
                  <i class="bi bi-search"></i> Rechercher
                </button>
              </div>
            </div>

            <!-- Tableau des données -->
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Indice</th>
                    <th>Niveau</th>
                    <th>Température</th>
                    <th>Humidité</th>
                    <th>Pression</th>
                    <th>Précipitations</th>
                    <th>Vent</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyData" :key="item.id">
                    <td>{{ formatDate(item.timestamp) }}</td>
                    <td>
                      <span class="fw-bold">{{ item.value.toFixed(1) }}</span>
                    </td>
                    <td>
                      <span class="badge" :class="getIndexBadgeClass(item.level)">
                        {{ item.level }}
                      </span>
                    </td>
                    <td>{{ item.temperature?.toFixed(1) || '--' }}°C</td>
                    <td>{{ item.humidity?.toFixed(1) || '--' }}%</td>
                    <td>{{ item.pressure?.toFixed(0) || '--' }} hPa</td>
                    <td>{{ item.precipitation?.toFixed(1) || '--' }} mm</td>
                    <td>{{ item.wind_speed?.toFixed(1) || '--' }} km/h</td>
                    <td>
                      <button class="btn btn-sm btn-info me-1" @click="viewDetails(item)">
                        <i class="bi bi-eye"></i>
                      </button>
                      <button class="btn btn-sm btn-warning" @click="viewAlerts(item)">
                        <i class="bi bi-exclamation-triangle"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div class="d-flex justify-content-between align-items-center mt-3">
              <div class="text-muted">
                {{ historyData.length }} enregistrements trouvés
              </div>
              <nav v-if="totalPages > 1">
                <ul class="pagination pagination-sm mb-0">
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Précédent</a>
                  </li>
                  <li v-for="page in visiblePages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                    <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Suivant</a>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Section Alertes Actives -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Alertes Actives</h5>
          </div>
          <div class="card-body">
            <div v-if="activeAlerts.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-check-circle fs-1"></i>
              <p class="mt-2">Aucune alerte active</p>
            </div>
            <div v-else class="row">
              <div v-for="alert in activeAlerts" :key="alert.id" class="col-md-6 mb-3">
                <div class="alert" :class="getAlertClass(alert.severity)">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="alert-heading">{{ alert.title }}</h6>
                      <p class="mb-1">{{ alert.description }}</p>
                      <small class="text-muted">
                        Créée le {{ formatDate(alert.created_at) }}
                      </small>
                    </div>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-secondary" @click="acknowledgeAlert(alert.id)">
                        <i class="bi bi-check"></i>
                      </button>
                      <button class="btn btn-outline-success" @click="resolveAlert(alert.id)">
                        <i class="bi bi-check-circle"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
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
import environmentalApiService from '../services/environmentalApiService';
import weatherIndexService from '../services/weatherIndexService';

export default defineComponent({
  name: 'HistorySettingsView',
  setup() {
    const environmentalStore = useEnvironmentalStore();
    const cities = ref<{ id: string; name: string; latitude: number; longitude: number }[]>([]);
    const isSaving = ref(false);
    const isLoading = ref(false);

    // Current weather index
    const currentIndex = ref<any>(null);
    const activeAlerts = ref<any[]>([]);

    // Settings state
    const settings = reactive({
      alertThreshold: 75,
      criticalThreshold: 85,
      highThreshold: 70,
      notificationFrequency: 'hourly',
      monitoringZone: ['Paris'],
      autoAlert: true,
      metricWeights: {
        temperature: 25,
        humidity: 20,
        pressure: 15,
        precipitation: 20,
        wind_speed: 15,
        visibility: 5
      }
    });

    // History state
    const historyFilter = reactive({
      level: 'all',
      startDate: '',
      endDate: ''
    });

    const historyData = ref<any[]>([]);
    const currentPage = ref(1);
    const totalPages = ref(1);
    const itemsPerPage = 10;

    // Weather metrics configuration
    const weatherMetrics = [
      { key: 'temperature', label: 'Température' },
      { key: 'humidity', label: 'Humidité' },
      { key: 'pressure', label: 'Pression' },
      { key: 'precipitation', label: 'Précipitations' },
      { key: 'wind_speed', label: 'Vitesse du vent' },
      { key: 'visibility', label: 'Visibilité' }
    ];

    // Computed
    const visiblePages = computed(() => {
      const pages = [];
      const start = Math.max(1, currentPage.value - 2);
      const end = Math.min(totalPages.value, currentPage.value + 2);
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    });

    // Methods
    const normalizeWeights = () => {
      const total = Object.values(settings.metricWeights).reduce((sum, weight) => sum + weight, 0);
      if (total !== 100) {
        const factor = 100 / total;
        Object.keys(settings.metricWeights).forEach(key => {
          settings.metricWeights[key] = Math.round(settings.metricWeights[key] * factor);
        });
      }
    };

    const getIndexBadgeClass = (level: string) => {
      const classes = {
        low: 'bg-success',
        medium: 'bg-warning',
        high: 'bg-orange',
        critical: 'bg-danger'
      };
      return classes[level] || 'bg-secondary';
    };

    const getAlertClass = (severity: string) => {
      const classes = {
        low: 'alert-info',
        medium: 'alert-warning',
        high: 'alert-orange',
        critical: 'alert-danger'
      };
      return classes[severity] || 'alert-secondary';
    };

    const getMetricLabel = (metric: string) => {
      const metricMap: { [key: string]: string } = {
        temperature: 'Température',
        humidity: 'Humidité',
        pressure: 'Pression',
        precipitation: 'Précipitations',
        wind_speed: 'Vent',
        visibility: 'Visibilité'
      };
      return metricMap[metric] || metric;
    };

    const saveSettings = async () => {
      isSaving.value = true;
      try {
        // Sauvegarder les paramètres de l'indice météo
        await weatherIndexService.updateConfiguration({
          critical_threshold: settings.criticalThreshold,
          high_threshold: settings.highThreshold,
          metric_weights: settings.metricWeights
        });
        
        // Simuler la sauvegarde des autres paramètres
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('Settings saved:', settings);
      } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
      } finally {
        isSaving.value = false;
      }
    };

    const loadCurrentIndex = async () => {
      try {
        const response = await weatherIndexService.getCurrentIndex();
        currentIndex.value = response.data;
      } catch (error) {
        console.error('Erreur lors du chargement de l\'indice actuel:', error);
      }
    };

    const loadActiveAlerts = async () => {
      try {
        const response = await weatherIndexService.getActiveAlerts();
        activeAlerts.value = response.data;
      } catch (error) {
        console.error('Erreur lors du chargement des alertes:', error);
      }
    };

    const loadHistory = async () => {
      isLoading.value = true;
      try {
        const params = {
          page: currentPage.value,
          page_size: itemsPerPage,
          level: historyFilter.level !== 'all' ? historyFilter.level : undefined,
          start_date: historyFilter.startDate || undefined,
          end_date: historyFilter.endDate || undefined
        };
        
        const response = await weatherIndexService.getIndexHistory(params);
        historyData.value = response.data.results;
        totalPages.value = Math.ceil(response.data.count / itemsPerPage);
      } catch (error) {
        console.error('Erreur lors du chargement de l\'historique:', error);
        historyData.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    const changePage = (page: number) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
        loadHistory();
      }
    };

    const acknowledgeAlert = async (alertId: number) => {
      try {
        await weatherIndexService.acknowledgeAlert(alertId);
        await loadActiveAlerts();
      } catch (error) {
        console.error('Erreur lors de l\'acquittement de l\'alerte:', error);
      }
    };

    const resolveAlert = async (alertId: number) => {
      try {
        await weatherIndexService.resolveAlert(alertId);
        await loadActiveAlerts();
      } catch (error) {
        console.error('Erreur lors de la résolution de l\'alerte:', error);
      }
    };

    const formatDate = (dateString: string) => {
      if (!dateString) return '--';
      return new Date(dateString).toLocaleString('fr-FR');
    };

    const viewDetails = (item: any) => {
      console.log('View details:', item);
    };

    const viewAlerts = (item: any) => {
      console.log('View alerts for:', item);
    };

    onMounted(async () => {
      try {
        // Charger les villes
        console.log('Appel /api/regions/ depuis HistorySettingsView');
        const response = await environmentalApiService.getAvailableCities();
        cities.value = response.data;

        // Charger l'indice actuel et les alertes
        await Promise.all([
          loadCurrentIndex(),
          loadActiveAlerts(),
          loadHistory()
        ]);

        // Charger la configuration actuelle
        try {
          const configResponse = await weatherIndexService.getConfiguration();
          const config = configResponse.data;
          settings.criticalThreshold = config.critical_threshold;
          settings.highThreshold = config.high_threshold;
          if (config.metric_weights) {
            Object.assign(settings.metricWeights, config.metric_weights);
          }
        } catch (error) {
          console.error('Erreur lors du chargement de la configuration:', error);
        }
      } catch (e) {
        console.error('Erreur lors de l\'initialisation:', e);
        cities.value = [];
      }
    });

    return {
      cities,
      settings,
      isSaving,
      isLoading,
      historyFilter,
      historyData,
      currentIndex,
      activeAlerts,
      currentPage,
      totalPages,
      weatherMetrics,
      visiblePages,
      saveSettings,
      loadHistory,
      changePage,
      acknowledgeAlert,
      resolveAlert,
      formatDate,
      viewDetails,
      viewAlerts,
      getIndexBadgeClass,
      getAlertClass,
      getMetricLabel,
      normalizeWeights
    };
  }
});
</script>

<style scoped>
.history-settings {
  padding: 20px 0;
}

.weather-index-display {
  text-align: center;
  min-width: 80px;
}

.index-value {
  font-size: 2rem;
  font-weight: bold;
  line-height: 1;
}

.index-label {
  font-size: 0.8rem;
  color: #6c757d;
  text-transform: uppercase;
}

.metric-contributions {
  font-size: 0.9rem;
}

.progress {
  background-color: #e9ecef;
}

.progress-bar {
  background-color: #007bff;
}

.bg-orange {
  background-color: #fd7e14 !important;
}

.alert-orange {
  background-color: #fff3cd;
  border-color: #fd7e14;
  color: #856404;
}

.form-range {
  height: 6px;
}

.form-range::-webkit-slider-thumb {
  height: 16px;
  width: 16px;
}

.form-range::-moz-range-thumb {
  height: 16px;
  width: 16px;
}
</style>
