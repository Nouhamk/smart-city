<template>
  <div class="weather-index-card">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="bi bi-cloud-sun me-2"></i>
          Indice Météo Global
        </h5>
        <div class="d-flex align-items-center">
          <span class="badge me-2" :class="getLevelBadgeClass(currentIndex?.level)">
            {{ getLevelLabel(currentIndex?.level) }}
          </span>
          <button 
            class="btn btn-sm btn-outline-secondary" 
            @click="refreshData"
            :disabled="loading"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
          </button>
        </div>
      </div>
      
      <div class="card-body">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Chargement...</span>
          </div>
        </div>
        
        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        
        <div v-else-if="currentIndex" class="weather-index-content">
          <!-- Indice principal -->
          <div class="index-display text-center mb-4">
            <div class="index-value" :class="getIndexValueClass(currentIndex.index)">
              {{ (currentIndex.index * 100).toFixed(1) }}
            </div>
            <div class="index-label">Indice Global</div>
            <div class="index-region">{{ currentIndex.region }}</div>
          </div>
          
          <!-- Barre de progression -->
          <div class="progress mb-3" style="height: 8px;">
            <div 
              class="progress-bar" 
              :class="getProgressBarClass(currentIndex.level)"
              :style="{ width: (currentIndex.index * 100) + '%' }"
              role="progressbar"
              :aria-valuenow="currentIndex.index * 100"
              aria-valuemin="0"
              aria-valuemax="100"
            ></div>
          </div>
          
          <!-- Seuils d'alerte -->
          <div class="thresholds mb-3">
            <div class="d-flex justify-content-between small text-muted">
              <span>Normal</span>
              <span>Attention</span>
              <span>Alerte</span>
              <span>Critique</span>
            </div>
            <div class="d-flex justify-content-between small">
              <span>0%</span>
              <span>30%</span>
              <span>50%</span>
              <span>70%</span>
              <span>80%</span>
            </div>
          </div>
          
          <!-- Détails des métriques -->
          <div class="metrics-details">
            <h6 class="mb-3">Contributions par métrique</h6>
            <div class="row">
              <div 
                v-for="(detail, metric) in currentIndex.details" 
                :key="metric"
                class="col-md-6 mb-2"
              >
                <div class="metric-item">
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="metric-name">{{ getMetricLabel(metric) }}</span>
                    <span class="metric-value">{{ detail.raw_value.toFixed(1) }}</span>
                  </div>
                  <div class="metric-bar">
                    <div 
                      class="metric-progress" 
                      :style="{ 
                        width: (detail.contribution / currentIndex.index * 100) + '%',
                        backgroundColor: getMetricColor(metric)
                      }"
                    ></div>
                  </div>
                  <div class="d-flex justify-content-between small text-muted">
                    <span>Poids: {{ (detail.weight * 100).toFixed(0) }}%</span>
                    <span>Contribution: {{ (detail.contribution * 100).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Timestamp -->
          <div class="text-muted small text-center mt-3">
            Dernière mise à jour: {{ formatTimestamp(currentIndex.timestamp) }}
          </div>
        </div>
        
        <div v-else class="text-center py-3 text-muted">
          Aucune donnée disponible
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { WeatherIndex } from '../../services/weatherIndexService';

export default defineComponent({
  name: 'WeatherIndexCard',
  props: {
    region: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const currentIndex = ref<WeatherIndex | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const refreshData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Simuler l'appel API pour l'instant
        // const data = await weatherIndexService.getCurrentWeatherIndex(props.region ? [props.region] : undefined);
        // currentIndex.value = data[0] || null;
        
        // Données simulées pour la démonstration
        await new Promise(resolve => setTimeout(resolve, 1000));
        currentIndex.value = {
          index: 0.65,
          level: 'high',
          region: props.region || 'Paris',
          timestamp: new Date().toISOString(),
          details: {
            temperature: {
              raw_value: 28.5,
              normalized: 0.7,
              weight: 0.25,
              contribution: 0.175
            },
            humidity: {
              raw_value: 75.0,
              normalized: 0.6,
              weight: 0.20,
              contribution: 0.120
            },
            pressure: {
              raw_value: 1010.0,
              normalized: 0.4,
              weight: 0.15,
              contribution: 0.060
            },
            precipitation: {
              raw_value: 5.0,
              normalized: 0.8,
              weight: 0.15,
              contribution: 0.120
            },
            wind_speed: {
              raw_value: 25.0,
              normalized: 0.5,
              weight: 0.10,
              contribution: 0.050
            },
            visibility: {
              raw_value: 8.0,
              normalized: 0.3,
              weight: 0.10,
              contribution: 0.030
            },
            cloud_cover: {
              raw_value: 60.0,
              normalized: 0.6,
              weight: 0.05,
              contribution: 0.030
            }
          }
        };
      } catch (err: any) {
        error.value = err.message || 'Erreur lors du chargement des données';
      } finally {
        loading.value = false;
      }
    };

    const getLevelBadgeClass = (level: string | undefined) => {
      switch (level) {
        case 'low': return 'bg-success';
        case 'medium': return 'bg-warning';
        case 'high': return 'bg-danger';
        case 'critical': return 'bg-dark';
        default: return 'bg-secondary';
      }
    };

    const getLevelLabel = (level: string | undefined) => {
      switch (level) {
        case 'low': return 'Normal';
        case 'medium': return 'Attention';
        case 'high': return 'Alerte';
        case 'critical': return 'Critique';
        default: return 'Inconnu';
      }
    };

    const getIndexValueClass = (index: number) => {
      if (index >= 0.8) return 'text-danger';
      if (index >= 0.7) return 'text-warning';
      if (index >= 0.5) return 'text-info';
      return 'text-success';
    };

    const getProgressBarClass = (level: string) => {
      switch (level) {
        case 'low': return 'bg-success';
        case 'medium': return 'bg-warning';
        case 'high': return 'bg-danger';
        case 'critical': return 'bg-dark';
        default: return 'bg-secondary';
      }
    };

    const getMetricLabel = (metric: string) => {
      const labels: { [key: string]: string } = {
        temperature: 'Température',
        humidity: 'Humidité',
        pressure: 'Pression',
        precipitation: 'Précipitations',
        wind_speed: 'Vitesse du vent',
        visibility: 'Visibilité',
        cloud_cover: 'Couverture nuageuse'
      };
      return labels[metric] || metric;
    };

    const getMetricColor = (metric: string) => {
      const colors: { [key: string]: string } = {
        temperature: '#dc3545',
        humidity: '#0d6efd',
        pressure: '#6f42c1',
        precipitation: '#198754',
        wind_speed: '#fd7e14',
        visibility: '#20c997',
        cloud_cover: '#6c757d'
      };
      return colors[metric] || '#6c757d';
    };

    const formatTimestamp = (timestamp: string) => {
      return new Date(timestamp).toLocaleString('fr-FR');
    };

    onMounted(() => {
      refreshData();
    });

    return {
      currentIndex,
      loading,
      error,
      refreshData,
      getLevelBadgeClass,
      getLevelLabel,
      getIndexValueClass,
      getProgressBarClass,
      getMetricLabel,
      getMetricColor,
      formatTimestamp
    };
  }
});
</script>

<style scoped>
.weather-index-card {
  height: 100%;
}

.index-display {
  padding: 1rem 0;
}

.index-value {
  font-size: 3rem;
  font-weight: bold;
  line-height: 1;
}

.index-label {
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 0.5rem;
}

.index-region {
  font-size: 1.1rem;
  font-weight: 500;
  margin-top: 0.25rem;
}

.thresholds {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.metric-item {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
}

.metric-name {
  font-weight: 500;
  font-size: 0.9rem;
}

.metric-value {
  font-weight: bold;
  color: #495057;
}

.metric-bar {
  height: 4px;
  background-color: #e9ecef;
  border-radius: 2px;
  margin: 0.5rem 0;
  overflow: hidden;
}

.metric-progress {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 