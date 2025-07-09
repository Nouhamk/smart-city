<template>
    <div class="map-view">
      <h1 class="mb-4">Carte interactive</h1>
      
      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">
            <i class="bi bi-geo-alt me-2"></i>
            Filtres
          </div>
          <button class="btn btn-sm btn-outline-secondary" @click="refreshMap">
            <i class="bi bi-arrow-clockwise me-1"></i> Actualiser
          </button>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-4">
              <div class="mb-3">
                <label for="dataType" class="form-label">Type de données</label>
                <select v-model="filters.dataType" class="form-select" id="dataType">
                  <option value="all">Tous</option>
                  <option value="temperature">Température</option>
                  <option value="humidity">Humidité</option>
                  <option value="pressure">Pression</option>
                </select>
              </div>
            </div>
            <div class="col-md-4">
              <div class="mb-3">
                <label for="region" class="form-label">Région</label>
                <select v-model="filters.region" class="form-select" id="region">
                  <option value="all">Toutes</option>
                  <option v-for="prediction in predictions" :key="prediction.region.id" :value="prediction.region.name">{{ prediction.region.name }}</option>
                </select>
              </div>
            </div>
            <div class="col-md-4">
              <div class="mb-3">
                <label for="quality" class="form-label">Niveau</label>
                <select v-model="filters.quality" class="form-select" id="quality">
                  <option value="all">Tous</option>
                  <option value="low">Faible</option>
                  <option value="moderate">Modéré</option>
                  <option value="high">Élevé</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-body">
          <div class="search-container mb-3">
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Rechercher une région" 
                v-model="searchQuery"
                @keyup.enter="searchLocation"
              >
              <button class="btn btn-primary" type="button" @click="searchLocation">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <!-- Loading state -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="mt-2">Chargement des données météo...</p>
          </div>
          
          <div id="map" class="map-container" ref="mapContainer" v-show="!loading"></div>
          
          <div class="map-legend" v-show="!loading">
            <h6>Légende</h6>
            <div class="legend-item">
              <span class="legend-color" style="background-color: #28a745;"></span>
              <span>Faible (0-30)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: #ffc107;"></span>
              <span>Modéré (31-60)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: #dc3545;"></span>
              <span>Élevé (61-100)</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Modal pour les détails de la région -->
      <div class="modal fade" id="regionDetailModal" tabindex="-1" aria-labelledby="regionDetailModalLabel" aria-hidden="true" ref="modalRef">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="regionDetailModalLabel">Détails de la région</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" v-if="selectedRegion">
              <h5>{{ selectedRegion.region.name }}</h5>
              <p><strong>Date:</strong> {{ formatPredictionDate(selectedRegion.time) }}</p>
              <div class="mb-3">
                <div class="sensor-value-item">
                  <span class="badge" :class="getTemperatureBadgeClass(selectedRegion.temperature)">Température: {{ selectedRegion.temperature.toFixed(1) }}°C</span>
                  <span class="sensor-description">{{ getTemperatureStatus(selectedRegion.temperature) }}</span>
                </div>
                <div class="sensor-value-item">
                  <span class="badge bg-primary">Humidité: {{ selectedRegion.humidity.toFixed(1) }}%</span>
                </div>
                <div class="sensor-value-item">
                  <span class="badge bg-info text-dark">Pression: {{ selectedRegion.pressure.toFixed(1) }} hPa</span>
                </div>
              </div>
              <p class="text-muted">Dernière mise à jour: {{ formatPredictionDate(selectedRegion.time) }}</p>
              
              <h6>Indice météorologique</h6>
              <div class="weather-index-display">
                <div class="index-value" :class="getIndexClass(selectedRegion.weatherIndex)">
                  {{ selectedRegion.weatherIndex }}
                </div>
                <div class="index-label">{{ getIndexLabel(selectedRegion.weatherIndex) }}</div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
              <button type="button" class="btn btn-primary" @click="viewRegionHistory">Voir l'historique</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted, onUnmounted, reactive, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import 'leaflet/dist/leaflet.css';
  import * as L from 'leaflet';
  import { predictionService } from '@/services/api.service';
  
  // Corriger le problème d'icône de marqueur de Leaflet
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  });
  
  interface Filters {
    dataType: string;
    region: string;
    quality: string;
  }
  
  export default defineComponent({
    name: 'MapView',
    setup() {
      const router = useRouter();
      const mapContainer = ref<HTMLElement | null>(null);
      const modalRef = ref<HTMLElement | null>(null);
      const map = ref<L.Map | null>(null);
      const markers = ref<L.Marker[]>([]);
      const selectedRegion = ref<any>(null);
      const searchQuery = ref('');
      const filters = reactive<Filters>({
        dataType: 'all',
        region: 'all',
        quality: 'all'
      });
      const predictions = ref<any[]>([]);
      const loading = ref(false);
      
      // Méthode pour obtenir la couleur en fonction de la valeur
      const getQualityColor = (value: number): string => {
        if (value <= 30) return '#28a745'; // Vert (faible)
        if (value <= 60) return '#ffc107'; // Jaune (modéré)
        return '#dc3545'; // Rouge (élevé)
      };
      
      // Méthode pour obtenir la classe CSS en fonction de la valeur
      const getQualityClass = (value: number): string => {
        if (value <= 30) return 'bg-success';
        if (value <= 60) return 'bg-warning text-dark';
        return 'bg-danger';
      };
      
      // Méthode pour obtenir le label en fonction de la valeur
      const getQualityLabel = (value: number): string => {
        if (value <= 30) return 'Faible';
        if (value <= 60) return 'Modéré';
        return 'Élevé';
      };
      
      // Méthode pour obtenir la classe de l'indice météorologique
      const getIndexClass = (index: number): string => {
        if (index <= 30) return 'index-low';
        if (index <= 60) return 'index-moderate';
        return 'index-high';
      };
      
      // Méthode pour obtenir le label de l'indice météorologique
      const getIndexLabel = (index: number): string => {
        if (index <= 30) return 'Conditions normales';
        if (index <= 60) return 'Conditions modérées';
        return 'Conditions critiques';
      };
      
      // Méthode pour formater la date
      const formatPredictionDate = (dateString: string): string => {
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
      
      // Obtenir les coordonnées d'une région
      const getRegionCoordinates = (regionName: string): { lat: number; lng: number } => {
        const coordinates: { [key: string]: { lat: number; lng: number } } = {
          'Paris': { lat: 48.856614, lng: 2.352222 },
          'Lyon': { lat: 45.764043, lng: 4.835659 },
          'Marseille': { lat: 43.296482, lng: 5.369780 },
          'Bordeaux': { lat: 44.837789, lng: -0.579180 },
          'Lille': { lat: 50.629250, lng: 3.057256 },
          'Toulouse': { lat: 43.604652, lng: 1.444209 },
          'Nantes': { lat: 47.218371, lng: -1.553621 },
          'Strasbourg': { lat: 48.573405, lng: 7.752111 },
          'Montpellier': { lat: 43.610769, lng: 3.876716 },
          'Nice': { lat: 43.710173, lng: 7.261953 }
        };
        
        return coordinates[regionName] || { lat: 46.603354, lng: 1.888334 }; // Centre de la France par défaut
      };
      
      // Charger les données des prédictions
      const loadPredictionsData = async () => {
        loading.value = true;
        try {
          const response = await predictionService.getPredictions();
          predictions.value = response.data.map((prediction: any) => {
            // Calculer un indice basé sur les métriques (même logique que dans HistorySettingsView)
            const tempScore = Math.min(100, Math.max(0, (prediction.temperature - 10) * 5));
            const humidityScore = Math.min(100, Math.max(0, Math.abs(prediction.humidity - 50) * 2));
            const pressureScore = Math.min(100, Math.max(0, Math.abs(prediction.pressure - 1013) * 0.5));
            
            const calculatedIndex = Math.round((tempScore * 0.4 + humidityScore * 0.35 + pressureScore * 0.25));
            
            return {
              ...prediction,
              weatherIndex: calculatedIndex,
              coordinates: getRegionCoordinates(prediction.region.name)
            };
          });
        } catch (error) {
          console.error('Erreur lors du chargement des données:', error);
        } finally {
          loading.value = false;
        }
      };
      
      // Initialiser la carte
      const initMap = () => {
        if (!mapContainer.value) return;
        
        // Créer la carte
        map.value = L.map(mapContainer.value).setView([46.603354, 1.888334], 6); // Centre sur la France
        
        // Ajouter le fond de carte
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map.value);
        
        // Ajouter les marqueurs
        addMarkers();
      };
      
      // Ajouter les marqueurs sur la carte
      const addMarkers = () => {
        if (!map.value) return;
        
        // Supprimer les marqueurs existants
        markers.value.forEach(marker => marker.remove());
        markers.value = [];
        
        // Filtrer les prédictions
        const filteredPredictions = predictions.value.filter(prediction => {
          if (filters.region !== 'all' && prediction.region.name !== filters.region) return false;
          
          if (filters.quality !== 'all') {
            if (filters.quality === 'low' && prediction.weatherIndex > 30) return false;
            if (filters.quality === 'moderate' && (prediction.weatherIndex <= 30 || prediction.weatherIndex > 60)) return false;
            if (filters.quality === 'high' && prediction.weatherIndex <= 60) return false;
          }
          
          return true;
        });
        
        // Ajouter les nouveaux marqueurs
        filteredPredictions.forEach(prediction => {
          const markerIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${getQualityColor(prediction.weatherIndex)}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: bold;">${Math.round(prediction.weatherIndex)}</div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
          });
          
          const marker = L.marker([prediction.coordinates.lat, prediction.coordinates.lng], { icon: markerIcon }).addTo(map.value!);
          
          // Popup et événements
          marker.bindTooltip(`${prediction.region.name}: ${prediction.weatherIndex} (${getIndexLabel(prediction.weatherIndex)})`);
          marker.on('click', () => showRegionDetail(prediction));
          
          markers.value.push(marker);
        });
      };
      
      // Afficher les détails d'une région
      const showRegionDetail = (prediction: any) => {
        selectedRegion.value = prediction;
        
        // Utiliser Bootstrap pour afficher la modal
        if (modalRef.value) {
          const modal = new (window as any).bootstrap.Modal(modalRef.value);
          modal.show();
        }
      };
      
      // Méthode pour rechercher un lieu
      const searchLocation = () => {
        if (!searchQuery.value || !map.value) return;
        
        const prediction = predictions.value.find(p => 
          p.region.name.toLowerCase().includes(searchQuery.value.toLowerCase())
        );
        
        if (prediction) {
          map.value.setView([prediction.coordinates.lat, prediction.coordinates.lng], 12);
          showRegionDetail(prediction);
        } else {
          alert(`Aucun résultat trouvé pour "${searchQuery.value}"`);
        }
      };
      
      // Méthode pour actualiser la carte
      const refreshMap = async () => {
        await loadPredictionsData();
        addMarkers();
      };
      
      // Méthode pour voir l'historique complet d'une région
      const viewRegionHistory = () => {
        if (!selectedRegion.value) return;
        
        // Rediriger vers la page d'historique avec la région
        router.push({
          name: 'history',
          query: { region: selectedRegion.value.region.name }
        });
      };
      
      // Observer les changements dans les filtres
      watch(filters, () => {
        addMarkers();
      });
      
      // Initialiser la carte après le montage du composant
      onMounted(async () => {
        // Charger Bootstrap pour les modals
        const bootstrapScript = document.createElement('script');
        bootstrapScript.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js';
        document.head.appendChild(bootstrapScript);
        
        // Charger les icônes Bootstrap
        const bootstrapIconsLink = document.createElement('link');
        bootstrapIconsLink.rel = 'stylesheet';
        bootstrapIconsLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css';
        document.head.appendChild(bootstrapIconsLink);
        
        // Charger les données et initialiser la carte
        await loadPredictionsData();
        setTimeout(() => {
          initMap();
        }, 100);
      });
      
      // Nettoyer les ressources lors du démontage du composant
      onUnmounted(() => {
        if (map.value) {
          map.value.remove();
        }
      });
      
      return {
        mapContainer,
        modalRef,
        selectedRegion,
        searchQuery,
        filters,
        predictions,
        loading,
        getQualityColor,
        getQualityClass,
        getQualityLabel,
        getIndexClass,
        getIndexLabel,
        formatPredictionDate,
        getTemperatureBadgeClass,
        getTemperatureStatus,
        searchLocation,
        refreshMap,
        viewRegionHistory
      };
    }
  });
  </script>
  
  <style scoped>
  .map-container {
    height: 500px;
    width: 100%;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
  
  .map-legend {
    background: white;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.2);
    position: absolute;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
  }
  
  .legend-color {
    display: inline-block;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    margin-right: 8px;
  }
  
  .search-container {
    z-index: 1000;
    width: 100%;
  }
  
  .sensor-value-item {
    margin-bottom: 8px;
  }
  
  .sensor-description {
    margin-left: 8px;
  }
  
  .weather-index-display {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    background: #f8f9fa;
  }
  
  .index-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 10px;
  }
  
  .index-low {
    color: #28a745;
  }
  
  .index-moderate {
    color: #ffc107;
  }
  
  .index-high {
    color: #dc3545;
  }
  
  .index-label {
    font-size: 1.1rem;
    color: #6c757d;
  }
  
  /* Styles personnalisés pour les marqueurs */
  :deep(.custom-marker) {
    background: transparent;
    border: none;
  }
  </style>