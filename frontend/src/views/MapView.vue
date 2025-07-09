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
                <label for="city" class="form-label">Région</label>
                <select v-model="filters.city" class="form-select" id="city">
                  <option value="all">Toutes</option>
                  <option v-for="city in cities" :key="city.id" :value="city.name">{{ city.name }}</option>
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
          
          <div id="map" class="map-container" ref="mapContainer"></div>
          
          <div class="map-legend">
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
              <h5>{{ selectedRegion.region }}</h5>
              <p><strong>Date:</strong> {{ formatDate(selectedRegion.date) }}</p>
              <div class="mb-3">
                <div class="sensor-value-item">
                  <span class="badge" :class="getQualityClass(selectedRegion.temperature)">Température: {{ selectedRegion.temperature }}°C</span>
                  <span class="sensor-description">{{ getQualityLabel(selectedRegion.temperature) }}</span>
                </div>
                <div class="sensor-value-item">
                  <span class="badge bg-primary">Humidité: {{ selectedRegion.humidity }}%</span>
                </div>
                <div class="sensor-value-item">
                  <span class="badge bg-info text-dark">Pression: {{ selectedRegion.pressure }} hPa</span>
                </div>
              </div>
              <p class="text-muted">Dernière mise à jour: {{ formatDate(selectedRegion.date) }}</p>
              
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
  import environmentalApiService from '@/services/environmentalApiService';
  import predictionService from '@/services/predictionService';
  import weatherIndexService from '@/services/weatherIndexService';
  
  // Corriger le problème d'icône de marqueur de Leaflet
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  });
  
  interface RegionData {
    region: string;
    date: string;
    temperature: number;
    humidity: number;
    pressure: number;
    weatherIndex: number;
    latitude: number;
    longitude: number;
  }
  
  interface Filters {
    dataType: string;
    city: string;
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
      const selectedRegion = ref<RegionData | null>(null);
      const searchQuery = ref('');
      const filters = reactive<Filters>({
        dataType: 'all',
        city: 'all',
        quality: 'all'
      });
      const cities = ref<{ id: string; name: string; latitude: number; longitude: number }[]>([]);
      const regionsData = ref<RegionData[]>([]);
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
      const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        return date.toLocaleString();
      };
      
      // Charger les données des régions
      const loadRegionsData = async () => {
        loading.value = true;
        try {
          // Charger les prédictions
          const predictionsResponse = await predictionService.getPredictions();
          const predictions = predictionsResponse.data;
          
          // Charger l'indice météorologique actuel
          const weatherIndexResponse = await weatherIndexService.getCurrentIndex();
          const weatherIndex = weatherIndexResponse.data;
          
          // Transformer les données
          regionsData.value = predictions.map((prediction: any) => {
            // Calculer un indice basé sur les métriques
            const tempScore = Math.min(100, Math.max(0, (prediction.temperature - 10) * 5));
            const humidityScore = Math.min(100, Math.max(0, Math.abs(prediction.humidity - 50) * 2));
            const pressureScore = Math.min(100, Math.max(0, Math.abs(prediction.pressure - 1013) * 0.5));
            
            const calculatedIndex = Math.round((tempScore * 0.4 + humidityScore * 0.35 + pressureScore * 0.25));
            
            return {
              region: prediction.region,
              date: prediction.date,
              temperature: prediction.temperature,
              humidity: prediction.humidity,
              pressure: prediction.pressure,
              weatherIndex: calculatedIndex,
              latitude: getRegionCoordinates(prediction.region).lat,
              longitude: getRegionCoordinates(prediction.region).lng
            };
          });
        } catch (error) {
          console.error('Erreur lors du chargement des données:', error);
        } finally {
          loading.value = false;
        }
      };
      
      // Obtenir les coordonnées d'une région
      const getRegionCoordinates = (region: string): { lat: number; lng: number } => {
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
        
        return coordinates[region] || { lat: 46.603354, lng: 1.888334 }; // Centre de la France par défaut
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
        
        // Filtrer les régions
        const filteredRegions = regionsData.value.filter(region => {
          if (filters.city !== 'all' && region.region !== filters.city) return false;
          
          if (filters.quality !== 'all') {
            if (filters.quality === 'low' && region.weatherIndex > 30) return false;
            if (filters.quality === 'moderate' && (region.weatherIndex <= 30 || region.weatherIndex > 60)) return false;
            if (filters.quality === 'high' && region.weatherIndex <= 60) return false;
          }
          
          return true;
        });
        
        // Ajouter les nouveaux marqueurs
        filteredRegions.forEach(region => {
          const markerIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${getQualityColor(region.weatherIndex)}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: bold;">${Math.round(region.weatherIndex)}</div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
          });
          
          const marker = L.marker([region.latitude, region.longitude], { icon: markerIcon }).addTo(map.value!);
          
          // Popup et événements
          marker.bindTooltip(`${region.region}: ${region.weatherIndex} (${getIndexLabel(region.weatherIndex)})`);
          marker.on('click', () => showRegionDetail(region));
          
          markers.value.push(marker);
        });
      };
      
      // Afficher les détails d'une région
      const showRegionDetail = (region: RegionData) => {
        selectedRegion.value = region;
        
        // Utiliser Bootstrap pour afficher la modal
        if (modalRef.value) {
          const modal = new (window as any).bootstrap.Modal(modalRef.value);
          modal.show();
        }
      };
      
      // Méthode pour rechercher un lieu
      const searchLocation = () => {
        if (!searchQuery.value || !map.value) return;
        
        const region = regionsData.value.find(r => 
          r.region.toLowerCase().includes(searchQuery.value.toLowerCase())
        );
        
        if (region) {
          map.value.setView([region.latitude, region.longitude], 12);
          showRegionDetail(region);
        } else {
          alert(`Aucun résultat trouvé pour "${searchQuery.value}"`);
        }
      };
      
      // Méthode pour actualiser la carte
      const refreshMap = async () => {
        await loadRegionsData();
        addMarkers();
      };
      
      // Méthode pour voir l'historique complet d'une région
      const viewRegionHistory = () => {
        if (!selectedRegion.value) return;
        
        // Rediriger vers la page d'historique avec la région
        router.push({
          name: 'history',
          query: { region: selectedRegion.value.region }
        });
      };
      
      // Observer les changements dans les filtres
      watch(filters, () => {
        addMarkers();
      });
      
      // Initialiser la carte après le montage du composant
      onMounted(async () => {
        try {
          console.log('Appel /api/regions/ depuis MapView');
          const response = await environmentalApiService.getAvailableCities();
          cities.value = response.data;
        } catch (e) {
          cities.value = [];
        }
        
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
        await loadRegionsData();
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
        cities,
        loading,
        getQualityColor,
        getQualityClass,
        getQualityLabel,
        getIndexClass,
        getIndexLabel,
        formatDate,
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