<template>
  <div class="weather-alerts">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="fas fa-exclamation-triangle me-2"></i>
          Alertes Météo
        </h5>
        <div class="refresh-btn" @click="refreshAlerts" :class="{ 'spinning': loading }">
          <i class="fas fa-sync-alt"></i>
        </div>
      </div>
      
      <div class="card-body">
        <!-- Loading state -->
        <div class="loading-state" v-if="loading">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Chargement...</span>
          </div>
          <p class="mt-2">Chargement des alertes...</p>
        </div>

        <!-- Error state -->
        <div class="error-state" v-if="error">
          <i class="fas fa-exclamation-triangle text-warning"></i>
          <p class="mt-2">{{ error }}</p>
          <button class="btn btn-sm btn-outline-primary" @click="refreshAlerts">
            Réessayer
          </button>
        </div>

        <!-- No alerts state -->
        <div class="no-alerts" v-if="!loading && !error && (!alerts || alerts.length === 0)">
          <i class="fas fa-check-circle text-success"></i>
          <p class="mt-2">Aucune alerte météo active</p>
          <small class="text-muted">La situation météorologique est normale</small>
        </div>

        <!-- Alerts list -->
        <div class="alerts-list" v-if="!loading && !error && alerts && alerts.length > 0">
          <div 
            v-for="alert in alerts" 
            :key="alert.id"
            class="alert-item"
            :class="getAlertClass(alert.level)"
          >
            <div class="alert-header">
              <div class="alert-icon">
                <i :class="getAlertIcon(alert.type)"></i>
              </div>
              <div class="alert-info">
                <div class="alert-title">{{ alert.type }}</div>
                <div class="alert-level">{{ getLevelText(alert.level) }}</div>
              </div>
              <div class="alert-time">
                {{ formatTimestamp(alert.created_at) }}
              </div>
            </div>
            
            <div class="alert-message">
              {{ alert.message }}
            </div>
            
            <div class="alert-details" v-if="alert.weather_index_value !== undefined">
              <div class="index-info">
                <span class="label">Indice météo:</span>
                <span class="value" :class="getLevelClass(alert.weather_index_level)">
                  {{ alert.weather_index_value.toFixed(1) }}
                </span>
                <span class="level" :class="getLevelClass(alert.weather_index_level)">
                  ({{ getLevelText(alert.weather_index_level) }})
                </span>
              </div>
            </div>
            
            <div class="alert-status">
              <span class="badge" :class="getStatusClass(alert.status)">
                {{ getStatusText(alert.status) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { weatherIndexService, type WeatherAlert } from '@/services/weatherIndexService';

// Props et emits
const props = defineProps<{
  autoRefresh?: boolean;
  refreshInterval?: number;
  status?: string;
}>();

const emit = defineEmits<{
  alertsUpdated: [alerts: WeatherAlert[]];
  error: [error: string];
}>();

// Reactive data
const alerts = ref<WeatherAlert[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
let refreshTimer: number | null = null;

// Methods
const refreshAlerts = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await weatherIndexService.getAlerts(props.status || 'active');
    alerts.value = response.alerts;
    emit('alertsUpdated', response.alerts);
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Erreur lors du chargement des alertes';
    emit('error', error.value);
  } finally {
    loading.value = false;
  }
};

const getAlertClass = (level: string) => {
  switch (level) {
    case 'low': return 'alert-low';
    case 'medium': return 'alert-medium';
    case 'high': return 'alert-high';
    case 'critical': return 'alert-critical';
    default: return 'alert-low';
  }
};

const getAlertIcon = (type: string) => {
  const icons: { [key: string]: string } = {
    'temperature': 'fas fa-thermometer-half',
    'humidity': 'fas fa-tint',
    'pressure': 'fas fa-compress-alt',
    'precipitation': 'fas fa-cloud-rain',
    'wind': 'fas fa-wind',
    'visibility': 'fas fa-eye',
    'storm': 'fas fa-bolt',
    'flood': 'fas fa-water',
    'heat': 'fas fa-fire',
    'cold': 'fas fa-snowflake',
    'default': 'fas fa-exclamation-triangle'
  };
  return icons[type.toLowerCase()] || icons.default;
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

const getLevelClass = (level: string) => {
  switch (level) {
    case 'low': return 'text-success';
    case 'medium': return 'text-warning';
    case 'high': return 'text-danger';
    case 'critical': return 'text-danger fw-bold';
    default: return 'text-muted';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return 'Active';
    case 'resolved': return 'Résolue';
    case 'acknowledged': return 'Reconnue';
    default: return status;
  }
};

const getStatusClass = (status: string) => {
  switch (status) {
    case 'active': return 'bg-danger';
    case 'resolved': return 'bg-success';
    case 'acknowledged': return 'bg-warning';
    default: return 'bg-secondary';
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

// Lifecycle
onMounted(() => {
  refreshAlerts();
  
  if (props.autoRefresh && props.refreshInterval) {
    refreshTimer = window.setInterval(refreshAlerts, props.refreshInterval);
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
.weather-alerts {
  margin-bottom: 1rem;
}

.card-header {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
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

.loading-state, .error-state, .no-alerts {
  text-align: center;
  padding: 2rem 0;
}

.no-alerts i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.alerts-list {
  max-height: 400px;
  overflow-y: auto;
}

.alert-item {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
}

.alert-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.alert-low {
  border-left: 4px solid #28a745;
}

.alert-medium {
  border-left: 4px solid #ffc107;
}

.alert-high {
  border-left: 4px solid #fd7e14;
}

.alert-critical {
  border-left: 4px solid #dc3545;
  background-color: #fff5f5;
}

.alert-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.75rem;
}

.alert-icon {
  font-size: 1.5rem;
  width: 40px;
  text-align: center;
}

.alert-info {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.alert-level {
  font-size: 0.9rem;
  color: #6c757d;
}

.alert-time {
  font-size: 0.8rem;
  color: #6c757d;
  text-align: right;
}

.alert-message {
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.alert-details {
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.index-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.index-info .label {
  font-weight: 600;
}

.index-info .value {
  font-weight: bold;
}

.alert-status {
  text-align: right;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
</style> 