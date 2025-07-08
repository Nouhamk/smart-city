import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { Measurement, Prediction, Alert, HistoryFilter } from '../types/models'
import { alertService, dataService } from '../services/api.service'

export const useEnvironmentalStore = defineStore('environmental', () => {
  // State
  const currentMeasurements = ref<Measurement[]>([])
  const predictions = ref<Prediction[]>([])
  const alerts = ref<Alert[]>([])
  const historyData = ref<Measurement[]>([])
  const historyFilter = ref<HistoryFilter>({
    dataType: 'airQuality',
    startDate: '',
    endDate: ''
  })
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const latestAirQuality = computed(() => {
    return currentMeasurements.value
      .filter(m => m.measurementType.name.toLowerCase().includes('air') || 
                   m.measurementType.name.toLowerCase().includes('pm'))
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0]
  })
  
  const latestTemperature = computed(() => {
    return currentMeasurements.value
      .filter(m => m.measurementType.name.toLowerCase().includes('temp'))
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0]
  })
  
  const activeAlerts = computed(() => {
    return alerts.value.filter(a => a.isActive)
  })
  
  // Actions
  const fetchCurrentMeasurements = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await environmentalService.getCurrentMeasurements()
      currentMeasurements.value = response.data.results
    } catch (err: any) {
      error.value = 'Erreur lors du chargement des mesures actuelles'
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  const fetchPredictions = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await environmentalService.getPredictions()
      predictions.value = response.data.results
    } catch (err: any) {
      error.value = 'Erreur lors du chargement des prédictions'
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  const fetchAlerts = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await environmentalService.getAlerts()
      alerts.value = response.data.results
    } catch (err: any) {
      error.value = 'Erreur lors du chargement des alertes'
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  const fetchHistoryData = async (filter: HistoryFilter = historyFilter.value) => {
    loading.value = true
    error.value = null
    historyFilter.value = filter
    
    try {
      const params: any = {}
      
      if (filter.dataType) {
        params.measurementType = filter.dataType
      }
      
      if (filter.startDate) {
        params.startDate = filter.startDate
      }
      
      if (filter.endDate) {
        params.endDate = filter.endDate
      }
      
      const response = await environmentalService.getMeasurementHistory(params)
      historyData.value = response.data.results
    } catch (err: any) {
      error.value = 'Erreur lors du chargement des données historiques'
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  const refreshAllData = async () => {
    await Promise.all([
      fetchCurrentMeasurements(),
      fetchPredictions(),
      fetchAlerts()
    ])
  }
  
  return {
    // State
    currentMeasurements,
    predictions,
    alerts,
    historyData,
    historyFilter,
    loading,
    error,
    
    // Getters
    latestAirQuality,
    latestTemperature,
    activeAlerts,
    
    // Actions
    fetchCurrentMeasurements,
    fetchPredictions,
    fetchAlerts,
    fetchHistoryData,
    refreshAllData
  }
})
