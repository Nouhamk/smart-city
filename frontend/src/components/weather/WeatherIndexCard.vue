<template>
  <div class="weather-index-card">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="fas fa-cloud-sun me-2"></i>
          Indice Global Météo
        </h5>
        <div class="refresh-btn" @click="refreshIndex" :class="{ 'spinning': loading }">
          <i class="fas fa-sync-alt"></i>
        </div>
      </div>
      
      <div class="card-body">
        <!-- Indice principal -->
        <div class="index-display" v-if="!loading && weatherIndex">
          <div class="index-value" :class="getLevelClass(weatherIndex.level)">
            {{ weatherIndex.value.toFixed(1) }}
          </div>
          <div class="index-level" :class="getLevelClass(weatherIndex.level)">
            {{ getLevelText(weatherIndex.level) }}
          </div>
          <div class="index-timestamp">
            Mis à jour: {{ formatTimestamp(weatherIndex.timestamp) }}
          </div>
        </div>

        <!-- Loading state -->
        <div class="loading-state" v-if="loading">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Chargement...</span>
          </div>
          <p class="mt-2">Calcul de l'indice météo...</p>
        </div>

        <!-- Error state -->
        <div class="error-state" v-if="error">
          <i class="fas fa-exclamation-triangle text-warning"></i>
          <p class="mt-2">{{ error }}</p>
          <button class="btn btn-sm btn-outline-primary" @click="refreshIndex">
            Réessayer
          </button>
        </div>

        <!-- Détails des contributions -->
        <div class="contributions" v-if="weatherIndex && weatherIndex.contributions">
          <h6 class="mt-3 mb-2">Contributions par métrique:</h6>
          <div class="contribution-bars">
            <div 
              v-for="(contribution, metric) in weatherIndex.contributions" 
              :key="metric"
              class="contribution-item"
            >
              <div class="metric-name">{{ getMetricName(metric) }}</div>
              <div class="progress">
                <div 
                  class="progress-bar" 
                  :style="{ width: Math.abs(contribution * 100) + '%' }"
                  :class="contribution > 0 ? 'bg-success' : 'bg-danger'"
                ></div>
              </div>
              <div class="contribution-value" :class="contribution > 0 ? 'text-success' : 'text-danger'">
                {{ (contribution * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>

        <!-- Valeurs brutes -->
        <div class="raw-values" v-if="weatherIndex && hasRawValues(weatherIndex)">
          <h6 class="mt-3 mb-2">Valeurs actuelles:</h6>
          <div class="row">
            <div class="col-6" v-if="weatherIndex.temperature !== undefined">
              <div class="metric-item">
                <i class="fas fa-thermometer-half"></i>
                <span>{{ weatherIndex.temperature.toFixed(1) }}°C</span>
              </div>
            </div>
            <div class="col-6" v-if="weatherIndex.humidity !== undefined">
              <div class="metric-item">
                <i class="fas fa-tint"></i>
                <span>{{ weatherIndex.humidity.toFixed(1) }}%</span>
              </div>
            </div>
            <div class="col-6" v-if="weatherIndex.pressure !== undefined">
              <div class="metric-item">
                <i class="fas fa-compress-alt"></i>
                <span>{{ weatherIndex.pressure.toFixed(0) }} hPa</span>
              </div>
            </div>
            <div class="col-6" v-if="weatherIndex.precipitation !== undefined">
              <div class="metric-item">
                <i class="fas fa-cloud-rain"></i>
                <span>{{ weatherIndex.precipitation.toFixed(1) }} mm</span>
              </div>
            </div>
            <div class="col-6" v-if="weatherIndex.wind_speed !== undefined">
              <div class="metric-item">
                <i class="fas fa-wind"></i>
                <span>{{ weatherIndex.wind_speed.toFixed(1) }} km/h</span>
              </div>
            </div>
            <div class="col-6" v-if="weatherIndex.visibility !== undefined">
              <div class="metric-item">
                <i class="fas fa-eye"></i>
                <span>{{ weatherIndex.visibility.toFixed(0) }} km</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { weatherIndexService, type WeatherIndex } from '@/services/weatherIndexService';

// Props et emits
const props = defineProps<{
  autoRefresh?: boolean;
  refreshInterval?: number;
}>();

const emit = defineEmits<{
  indexUpdated: [index: WeatherIndex];
  error: [error: string];
}>();

// Reactive data
const weatherIndex = ref<WeatherIndex | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
let refreshTimer: number | null = null;

// Methods
const refreshIndex = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const index = await weatherIndexService.getCurrentIndex();
    weatherIndex.value = index;
    emit('indexUpdated', index);
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Erreur lors du chargement de l\'indice météo';
    emit('error', error.value);
  } finally {
    loading.value = false;
  }
};

const getLevelClass = (level: string) => {
  switch (level) {
    case 'low': return 'level-low';
    case 'medium': return 'level-medium';
    case 'high': return 'level-high';
    case 'critical': return 'level-critical';
    default: return 'level-low';
  }
};

const getLevelText = (level: string) => {
  switch (level) {
    case 'low': return 'Faible';
    case 'medium': return 'Modéré';
    case 'high': return 'Élevé';
    case 'critical': return 'Critique';
    default: return 'Inconnu';
  }
};

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getMetricName = (metric: string) => {
  const names: { [key: string]: string } = {
    temperature: 'Température',
    humidity: 'Humidité',
    pressure: 'Pression',
    precipitation: 'Précipitations',
    wind_speed: 'Vitesse du vent',
    visibility: 'Visibilité',
    cloud_cover: 'Couverture nuageuse'
  };
  return names[metric] || metric;
};

const hasRawValues = (index: WeatherIndex) => {
  return index.temperature !== undefined || 
         index.humidity !== undefined || 
         index.pressure !== undefined || 
         index.precipitation !== undefined || 
         index.wind_speed !== undefined || 
         index.visibility !== undefined;
};

// Lifecycle
onMounted(() => {
  refreshIndex();
  
  if (props.autoRefresh && props.refreshInterval) {
    refreshTimer = window.setInterval(refreshIndex, props.refreshInterval);
  }
});

// Cleanup
import { onUnmounted } from 'vue';
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});
</script>

<style scoped>
.weather-index-card {
  margin-bottom: 1rem;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: none;
}

.refresh-btn {
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.refresh-btn.spinning i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.index-display {
  text-align: center;
  padding: 1rem 0;
}

.index-value {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.index-level {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.index-timestamp {
  font-size: 0.9rem;
  color: #6c757d;
}

.level-low {
  color: #28a745;
}

.level-medium {
  color: #ffc107;
}

.level-high {
  color: #fd7e14;
}

.level-critical {
  color: #dc3545;
}

.loading-state, .error-state {
  text-align: center;
  padding: 2rem 0;
}

.contributions {
  margin-top: 1rem;
}

.contribution-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

.metric-name {
  min-width: 100px;
  font-size: 0.9rem;
}

.progress {
  flex: 1;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.contribution-value {
  min-width: 60px;
  text-align: right;
  font-size: 0.8rem;
  font-weight: 600;
}

.raw-values {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.metric-item i {
  width: 16px;
  color: #6c757d;
}
</style> 