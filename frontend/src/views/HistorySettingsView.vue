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
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Paramètres d'autorité</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveSettings">
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
                  <option v-for="city in cities" :key="city" :value="city">
                    {{ city }}
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
            <h5 class="mb-0">Historique des mesures</h5>
          </div>
          <div class="card-body">
            <!-- Filtres -->
            <div class="row mb-4">
              <div class="col-md-4">
                <label class="form-label">Type de données</label>
                <select class="form-select" v-model="historyFilter.dataType">
                  <option value="all">Toutes les mesures</option>
                  <option value="temperature">Température</option>
                  <option value="humidity">Humidité</option>
                  <option value="air_quality">Qualité de l'air</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Date début</label>
                <input type="date" class="form-control" v-model="historyFilter.startDate">
              </div>
              <div class="col-md-4">
                <label class="form-label">Date fin</label>
                <input type="date" class="form-control" v-model="historyFilter.endDate">
              </div>
            </div>

            <!-- Tableau des données -->
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Valeur</th>
                    <th>Localisation</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in historyData" :key="item.id">
                    <td>{{ formatDate(item.timestamp) }}</td>
                    <td>{{ item.type }}</td>
                    <td>{{ item.value }} {{ item.unit }}</td>
                    <td>{{ item.location }}</td>
                    <td>
                      <button class="btn btn-sm btn-info me-1" @click="viewDetails(item)">
                        <i class="bi bi-eye"></i>
                      </button>
                      <button class="btn btn-sm btn-danger" @click="deleteRecord(item.id)">
                        <i class="bi bi-trash"></i>
                      </button>
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
import { defineComponent, ref, reactive, onMounted } from 'vue';
import { useEnvironmentalStore } from '../store/environmental';
import WeatherIndexCard from '@/components/weather/WeatherIndexCard.vue';
import WeatherIndexAlerts from '@/components/weather/WeatherIndexAlerts.vue';
import type { WeatherIndex, WeatherAlert } from '@/services/weatherIndexService';

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
      // Load initial data
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
      viewDetails,
      deleteRecord,
      onIndexUpdated,
      onIndexError,
      onAlertsUpdated,
      onAlertsError
    };
  }
});
</script>

<style scoped>
.history-settings {
  padding: 20px 0;
}
</style>
