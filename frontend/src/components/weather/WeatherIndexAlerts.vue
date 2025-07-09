<template>
  <div class="weather-index-alerts">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="bi bi-exclamation-triangle me-2"></i>
          Alertes Indice Météo
        </h5>
        <div class="d-flex align-items-center">
          <span class="badge bg-primary me-2">{{ alerts.length }}</span>
          <button 
            class="btn btn-sm btn-outline-secondary" 
            @click="refreshAlerts"
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
        
        <div v-else-if="alerts.length === 0" class="text-center py-3 text-muted">
          <i class="bi bi-check-circle fs-1 text-success"></i>
          <p class="mt-2">Aucune alerte active</p>
        </div>
        
        <div v-else class="alerts-list">
          <div 
            v-for="alert in alerts" 
            :key="alert.id"
            class="alert-item"
            :class="getAlertClass(alert.level)"
          >
            <div class="alert-header d-flex justify-content-between align-items-start">
              <div class="alert-info">
                <div class="alert-title d-flex align-items-center">
                  <span class="badge me-2" :class="getLevelBadgeClass(alert.level)">
                    {{ getLevelLabel(alert.level) }}
                  </span>
                  <strong>{{ alert.data.region }}</strong>
                </div>
                <div class="alert-message mt-1">{{ alert.message }}</div>
                <div class="alert-details mt-2">
                  <small class="text-muted">
                    Indice: {{ alert.data.index_value.toFixed(3) }} | 
                    Créé: {{ formatTimestamp(alert.created_at) }}
                  </small>
                </div>
              </div>
              
              <div class="alert-actions">
                <div class="btn-group btn-group-sm">
                  <button 
                    v-if="alert.status === 'active'"
                    class="btn btn-outline-primary"
                    @click="acknowledgeAlert(alert.id)"
                    :disabled="processingAlert === alert.id"
                  >
                    <i class="bi bi-check"></i>
                  </button>
                  <button 
                    class="btn btn-outline-success"
                    @click="resolveAlert(alert.id)"
                    :disabled="processingAlert === alert.id"
                  >
                    <i class="bi bi-check-circle"></i>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Détails des métriques -->
            <div v-if="alert.data.details" class="alert-metrics mt-3">
              <h6 class="mb-2">Contributions par métrique :</h6>
              <div class="row">
                <div 
                  v-for="(detail, metric) in alert.data.details" 
                  :key="metric"
                  class="col-md-6 mb-2"
                >
                  <div class="metric-summary">
                    <div class="d-flex justify-content-between align-items-center">
                      <span class="metric-name">{{ getMetricLabel(metric) }}</span>
                      <span class="metric-value">{{ detail.raw_value.toFixed(1) }}</span>
                    </div>
                    <div class="metric-bar">
                      <div 
                        class="metric-progress" 
                        :style="{ 
                          width: (detail.contribution / alert.data.index_value * 100) + '%',
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { WeatherIndexAlert } from '../../services/weatherIndexService';

export default defineComponent({
  name: 'WeatherIndexAlerts',
  setup() {
    const alerts = ref<WeatherIndexAlert[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const processingAlert = ref<string | null>(null);

    const refreshAlerts = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Simuler l'appel API pour l'instant
        // const data = await weatherIndexService.getWeatherIndexAlerts('active');
        // alerts.value = data;
        
        // Données simulées pour la démonstration
        await new Promise(resolve => setTimeout(resolve, 1000));
        alerts.value = [
          {
            id: '1',
            type: 'weather_index',
            message: 'Indice météo global: 0.750 - Alerte',
            level: 'high',
            status: 'active',
            created_at: new Date().toISOString(),
            data: {
              region: 'Paris',
              index_value: 0.750,
              level: 'high',
              details: {
                temperature: {
                  raw_value: 32.0,
                  normalized: 0.8,
                  weight: 0.25,
                  contribution: 0.2
                },
                humidity: {
                  raw_value: 85.0,
                  normalized: 0.7,
                  weight: 0.20,
                  contribution: 0.14
                },
                precipitation: {
                  raw_value: 15.0,
                  normalized: 0.9,
                  weight: 0.15,
                  contribution: 0.135
                }
              },
              description: 'Conditions météorologiques défavorables - alerte active'
            }
          },
          {
            id: '2',
            type: 'weather_index',
            message: 'Indice météo global: 0.650 - Attention',
            level: 'medium',
            status: 'active',
            created_at: new Date(Date.now() - 3600000).toISOString(),
            data: {
              region: 'Lyon',
              index_value: 0.650,
              level: 'medium',
              details: {
                temperature: {
                  raw_value: 28.0,
                  normalized: 0.6,
                  weight: 0.25,
                  contribution: 0.15
                },
                wind_speed: {
                  raw_value: 35.0,
                  normalized: 0.7,
                  weight: 0.10,
                  contribution: 0.07
                }
              },
              description: 'Conditions météorologiques nécessitant une attention particulière'
            }
          }
        ];
      } catch (err: any) {
        error.value = err.message || 'Erreur lors du chargement des alertes';
      } finally {
        loading.value = false;
      }
    };

    const acknowledgeAlert = async (alertId: string) => {
      processingAlert.value = alertId;
      try {
        // await weatherIndexService.acknowledgeAlert(alertId);
        await new Promise(resolve => setTimeout(resolve, 500));
        // Mettre à jour le statut localement
        const alert = alerts.value.find(a => a.id === alertId);
        if (alert) {
          alert.status = 'acknowledged';
        }
      } catch (err: any) {
        console.error('Erreur lors de l\'accusé de réception:', err);
      } finally {
        processingAlert.value = null;
      }
    };

    const resolveAlert = async (alertId: string) => {
      processingAlert.value = alertId;
      try {
        // await weatherIndexService.resolveAlert(alertId);
        await new Promise(resolve => setTimeout(resolve, 500));
        // Supprimer l'alerte de la liste
        alerts.value = alerts.value.filter(a => a.id !== alertId);
      } catch (err: any) {
        console.error('Erreur lors de la résolution:', err);
      } finally {
        processingAlert.value = null;
      }
    };

    const getAlertClass = (level: string) => {
      switch (level) {
        case 'low': return 'alert-success';
        case 'medium': return 'alert-warning';
        case 'high': return 'alert-danger';
        case 'critical': return 'alert-dark';
        default: return 'alert-secondary';
      }
    };

    const getLevelBadgeClass = (level: string) => {
      switch (level) {
        case 'low': return 'bg-success';
        case 'medium': return 'bg-warning';
        case 'high': return 'bg-danger';
        case 'critical': return 'bg-dark';
        default: return 'bg-secondary';
      }
    };

    const getLevelLabel = (level: string) => {
      switch (level) {
        case 'low': return 'Normal';
        case 'medium': return 'Attention';
        case 'high': return 'Alerte';
        case 'critical': return 'Critique';
        default: return 'Inconnu';
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
      refreshAlerts();
    });

    return {
      alerts,
      loading,
      error,
      processingAlert,
      refreshAlerts,
      acknowledgeAlert,
      resolveAlert,
      getAlertClass,
      getLevelBadgeClass,
      getLevelLabel,
      getMetricLabel,
      getMetricColor,
      formatTimestamp
    };
  }
});
</script>

<style scoped>
.weather-index-alerts {
  height: 100%;
}

.alerts-list {
  max-height: 600px;
  overflow-y: auto;
}

.alert-item {
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f8f9fa;
}

.alert-item.alert-success {
  border-color: #198754;
  background-color: #d1e7dd;
}

.alert-item.alert-warning {
  border-color: #ffc107;
  background-color: #fff3cd;
}

.alert-item.alert-danger {
  border-color: #dc3545;
  background-color: #f8d7da;
}

.alert-item.alert-dark {
  border-color: #212529;
  background-color: #d3d3d4;
}

.alert-title {
  font-size: 1.1rem;
}

.alert-message {
  color: #495057;
}

.metric-summary {
  background-color: rgba(255, 255, 255, 0.7);
  padding: 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
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
  background-color: rgba(0, 0, 0, 0.1);
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