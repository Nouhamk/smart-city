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
                  <option value="airQuality">Qualité de l'air</option>
                  <option value="temperature">Température</option>
                  <option value="humidity">Humidité</option>
                </select>
              </div>
            </div>
            <div class="col-md-4">
              <div class="mb-3">
                <label for="city" class="form-label">Ville</label>
                <select v-model="filters.city" class="form-select" id="city">
                  <option value="all">Toutes</option>
                  <option v-for="city in cities" :key="city.id" :value="city.name">{{ city.name }}</option>
                </select>
              </div>
            </div>
            <div class="col-md-4">
              <div class="mb-3">
                <label for="quality" class="form-label">Qualité</label>
                <select v-model="filters.quality" class="form-select" id="quality">
                  <option value="all">Tous</option>
                  <option value="good">Bonne</option>
                  <option value="moderate">Moyenne</option>
                  <option value="poor">Mauvaise</option>
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
                placeholder="Rechercher un lieu" 
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
              <span>Bon (0-50)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: #ffc107;"></span>
              <span>Moyen (51-75)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: #dc3545;"></span>
              <span>Mauvais (76+)</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Modal pour les détails du capteur -->
      <div class="modal fade" id="sensorDetailModal" tabindex="-1" aria-labelledby="sensorDetailModalLabel" aria-hidden="true" ref="modalRef">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="sensorDetailModalLabel">Détails du capteur</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" v-if="selectedSensor">
              <h5>{{ selectedSensor.name }}</h5>
              <p><strong>Emplacement:</strong> {{ selectedSensor.location }}</p>
              <div class="mb-3">
                <div class="sensor-value-item">
                  <span class="badge" :class="getQualityClass(selectedSensor.airQuality)">Qualité de l'air: {{ selectedSensor.airQuality }}</span>
                  <span class="sensor-description">{{ getQualityLabel(selectedSensor.airQuality) }}</span>
                </div>
                <div class="sensor-value-item">
                  <span class="badge bg-primary">Température: {{ selectedSensor.temperature }}°C</span>
                </div>
                <div class="sensor-value-item">
                  <span class="badge bg-info text-dark">Humidité: {{ selectedSensor.humidity }}%</span>
                </div>
              </div>
              <p class="text-muted">Dernière mise à jour: {{ formatDate(selectedSensor.lastUpdated) }}</p>
              
              <h6>Tendance sur 24h</h6>
              <div class="mini-chart" ref="miniChartRef"></div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
              <button type="button" class="btn btn-primary" @click="viewSensorHistory">Voir l'historique</button>
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
  import * as Chart from 'chart.js';
  import environmentalApiService from '@/services/environmentalApiService';
  
  // Corriger le problème d'icône de marqueur de Leaflet
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  });
  
  interface Sensor {
    id: number;
    name: string;
    location: string;
    latitude: number;
    longitude: number;
    airQuality: number;
    temperature: number;
    humidity: number;
    lastUpdated: string;
    historicalData?: {
      timestamps: string[];
      values: number[];
    };
  }
  
  interface Filters {
    dataType: string;
    city: string;
    quality: string;
  }
  
  // Nouvelle liste statique des villes
  interface CityData {
    id: string;
    name: string;
    latitude: number;
    longitude: number;
  }
  
  const cities = ref<CityData[]>([
    { id: '1', name: 'New York', latitude: 40.712776, longitude: -74.005974 },
    { id: '2', name: 'Los Angeles', latitude: 34.052235, longitude: -118.243683 },
    { id: '3', name: 'London', latitude: 51.507351, longitude: -0.127758 },
    { id: '4', name: 'Paris', latitude: 48.856614, longitude: 2.352222 },
    { id: '5', name: 'Sao Paolo', latitude: -23.550520, longitude: -46.633308 },
    { id: '6', name: 'Istanbul', latitude: 41.008240, longitude: 28.978359 },
    { id: '7', name: 'Beijing', latitude: 39.904202, longitude: 116.407394 },
    { id: '8', name: 'Berlin', latitude: 52.520008, longitude: 13.404954 },
    { id: '9', name: 'Tokyo', latitude: 35.689487, longitude: 139.691711 },
    { id: '10', name: 'Mosco', latitude: 55.755825, longitude: 37.617298 },
    { id: '11', name: 'Cairo', latitude: 30.044420, longitude: 31.235712 },
    { id: '12', name: 'Mumbai', latitude: 19.076090, longitude: 72.877426 },
    { id: '13', name: 'Mexico City', latitude: 19.432608, longitude: -99.133209 },
    { id: '14', name: 'Toronto', latitude: 43.653225, longitude: -79.383186 }
  ]);
  
  // Adapter les capteurs simulés pour correspondre aux nouvelles villes
  const mockSensors: Sensor[] = [
    {
      id: 1,
      name: 'Sensor New York',
      location: 'New York',
      latitude: 40.712776,
      longitude: -74.005974,
      airQuality: 42,
      temperature: 22,
      humidity: 65,
      lastUpdated: '2023-01-10T10:30:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [45, 40, 42, 38, 42]
      }
    },
    {
      id: 2,
      name: 'Sensor Los Angeles',
      location: 'Los Angeles',
      latitude: 34.052235,
      longitude: -118.243683,
      airQuality: 65,
      temperature: 24,
      humidity: 60,
      lastUpdated: '2023-01-10T10:35:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [60, 58, 65, 68, 65]
      }
    },
    {
      id: 3,
      name: 'Sensor London',
      location: 'London',
      latitude: 51.507351,
      longitude: -0.127758,
      airQuality: 85,
      temperature: 26,
      humidity: 55,
      lastUpdated: '2023-01-10T10:40:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [75, 80, 85, 90, 85]
      }
    },
    {
      id: 4,
      name: 'Sensor Paris',
      location: 'Paris',
      latitude: 48.856614,
      longitude: 2.352222,
      airQuality: 48,
      temperature: 20,
      humidity: 70,
      lastUpdated: '2023-01-10T10:45:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [50, 52, 48, 47, 48]
      }
    },
    {
      id: 5,
      name: 'Sensor Sao Paolo',
      location: 'Sao Paolo',
      latitude: -23.550520,
      longitude: -46.633308,
      airQuality: 55,
      temperature: 18,
      humidity: 75,
      lastUpdated: '2023-01-10T10:50:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [52, 54, 55, 56, 55]
      }
    },
    {
      id: 6,
      name: 'Sensor Istanbul',
      location: 'Istanbul',
      latitude: 41.008240,
      longitude: 28.978359,
      airQuality: 60,
      temperature: 23,
      humidity: 68,
      lastUpdated: '2023-01-10T10:55:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [62, 61, 60, 59, 60]
      }
    },
    {
      id: 7,
      name: 'Sensor Beijing',
      location: 'Beijing',
      latitude: 39.904202,
      longitude: 116.407394,
      airQuality: 90,
      temperature: 28,
      humidity: 50,
      lastUpdated: '2023-01-10T11:00:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [88, 89, 90, 92, 90]
      }
    },
    {
      id: 8,
      name: 'Sensor Berlin',
      location: 'Berlin',
      latitude: 52.520008,
      longitude: 13.404954,
      airQuality: 35,
      temperature: 19,
      humidity: 72,
      lastUpdated: '2023-01-10T11:05:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [36, 34, 35, 33, 35]
      }
    },
    {
      id: 9,
      name: 'Sensor Tokyo',
      location: 'Tokyo',
      latitude: 35.689487,
      longitude: 139.691711,
      airQuality: 70,
      temperature: 27,
      humidity: 60,
      lastUpdated: '2023-01-10T11:10:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [68, 69, 70, 71, 70]
      }
    },
    {
      id: 10,
      name: 'Sensor Mosco',
      location: 'Mosco',
      latitude: 55.755825,
      longitude: 37.617298,
      airQuality: 50,
      temperature: 16,
      humidity: 80,
      lastUpdated: '2023-01-10T11:15:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [52, 51, 50, 49, 50]
      }
    },
    {
      id: 11,
      name: 'Sensor Cairo',
      location: 'Cairo',
      latitude: 30.044420,
      longitude: 31.235712,
      airQuality: 77,
      temperature: 32,
      humidity: 40,
      lastUpdated: '2023-01-10T11:20:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [75, 76, 77, 78, 77]
      }
    },
    {
      id: 12,
      name: 'Sensor Mumbai',
      location: 'Mumbai',
      latitude: 19.076090,
      longitude: 72.877426,
      airQuality: 68,
      temperature: 30,
      humidity: 85,
      lastUpdated: '2023-01-10T11:25:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [66, 67, 68, 69, 68]
      }
    },
    {
      id: 13,
      name: 'Sensor Mexico City',
      location: 'Mexico City',
      latitude: 19.432608,
      longitude: -99.133209,
      airQuality: 80,
      temperature: 25,
      humidity: 60,
      lastUpdated: '2023-01-10T11:30:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [78, 79, 80, 81, 80]
      }
    },
    {
      id: 14,
      name: 'Sensor Toronto',
      location: 'Toronto',
      latitude: 43.653225,
      longitude: -79.383186,
      airQuality: 40,
      temperature: 17,
      humidity: 75,
      lastUpdated: '2023-01-10T11:35:00',
      historicalData: {
        timestamps: ['00:00', '06:00', '12:00', '18:00', '00:00'],
        values: [42, 41, 40, 39, 40]
      }
    }
  ];
  
  export default defineComponent({
    name: 'MapView',
    setup() {
      const router = useRouter();
      const mapContainer = ref<HTMLElement | null>(null);
      const miniChartRef = ref<HTMLElement | null>(null);
      const modalRef = ref<HTMLElement | null>(null);
      const map = ref<L.Map | null>(null);
      const markers = ref<L.Marker[]>([]);
      const selectedSensor = ref<Sensor | null>(null);
      const searchQuery = ref('');
      const filters = reactive<Filters>({
        dataType: 'all',
        city: 'all',
        quality: 'all'
      });
      // const cities = ref<{ id: string; name: string; latitude: number; longitude: number }[]>([]);
      // cities est déjà défini plus haut avec la nouvelle liste statique
      let miniChart: Chart.Chart | null = null;
      
      // Méthode pour obtenir la couleur en fonction de la qualité de l'air
      const getQualityColor = (value: number): string => {
        if (value <= 50) return '#28a745'; // Vert (bon)
        if (value <= 75) return '#ffc107'; // Jaune (moyen)
        return '#dc3545'; // Rouge (mauvais)
      };
      
      // Méthode pour obtenir la classe CSS en fonction de la qualité de l'air
      const getQualityClass = (value: number): string => {
        if (value <= 50) return 'bg-success';
        if (value <= 75) return 'bg-warning text-dark';
        return 'bg-danger';
      };
      
      // Méthode pour obtenir le label en fonction de la qualité de l'air
      const getQualityLabel = (value: number): string => {
        if (value <= 50) return 'Bonne qualité';
        if (value <= 75) return 'Qualité moyenne';
        return 'Mauvaise qualité';
      };
      
      // Méthode pour formater la date
      const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        return date.toLocaleString();
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
        
        // Filtrer les capteurs
        const filteredSensors = mockSensors.filter(sensor => {
          if (filters.city !== 'all' && !sensor.location.includes(filters.city)) return false;
          
          if (filters.quality !== 'all') {
            if (filters.quality === 'good' && sensor.airQuality > 50) return false;
            if (filters.quality === 'moderate' && (sensor.airQuality <= 50 || sensor.airQuality > 75)) return false;
            if (filters.quality === 'poor' && sensor.airQuality <= 75) return false;
          }
          
          return true;
        });
        
        // Ajouter les nouveaux marqueurs
        filteredSensors.forEach(sensor => {
          const markerIcon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${getQualityColor(sensor.airQuality)}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
          });
          
          const marker = L.marker([sensor.latitude, sensor.longitude], { icon: markerIcon }).addTo(map.value!);
          
          // Popup et événements
          marker.bindTooltip(`${sensor.name}: ${sensor.airQuality} (${getQualityLabel(sensor.airQuality)})`);
          marker.on('click', () => showSensorDetail(sensor));
          
          markers.value.push(marker);
        });
      };
      
      // Afficher les détails d'un capteur
      const showSensorDetail = (sensor: Sensor) => {
        selectedSensor.value = sensor;
        
        // Utiliser Bootstrap pour afficher la modal
        if (modalRef.value) {
          const modal = new (window as any).bootstrap.Modal(modalRef.value);
          modal.show();
          
          // Dessiner le mini graphique après l'affichage de la modal
          setTimeout(() => {
            drawMiniChart();
          }, 500);
        }
      };
      
      // Dessiner le mini graphique
      const drawMiniChart = () => {
        if (!miniChartRef.value || !selectedSensor.value || !selectedSensor.value.historicalData) return;
        
        // Détruire le graphique existant
        if (miniChart) {
          miniChart.destroy();
        }
        
        const ctx = miniChartRef.value.getContext('2d');
        if (!ctx) return;
        
        const data = selectedSensor.value.historicalData;
        
        miniChart = new Chart.Chart(ctx, {
          type: 'line',
          data: {
            labels: data.timestamps,
            datasets: [{
              label: 'Qualité de l\'air',
              data: data.values,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              y: {
                beginAtZero: false
              }
            }
          }
        });
      };
      
      // Méthode pour rechercher un lieu
      const searchLocation = () => {
        if (!searchQuery.value || !map.value) return;
        
        // Dans un environnement réel, vous utiliseriez un service de géocodage
        // Pour cette démonstration, nous allons simplement chercher parmi les capteurs
        const sensor = mockSensors.find(s => 
          s.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
          s.location.toLowerCase().includes(searchQuery.value.toLowerCase())
        );
        
        if (sensor) {
          map.value.setView([sensor.latitude, sensor.longitude], 12);
          showSensorDetail(sensor);
        } else {
          alert(`Aucun résultat trouvé pour "${searchQuery.value}"`);
        }
      };
      
      // Méthode pour actualiser la carte
      const refreshMap = () => {
        // Dans un environnement réel, vous rechargeriez les données depuis l'API
        addMarkers();
      };
      
      // Méthode pour voir l'historique complet d'un capteur
      const viewSensorHistory = () => {
        if (!selectedSensor.value) return;
        
        // Rediriger vers la page d'historique avec l'ID du capteur
        router.push({
          name: 'history',
          query: { sensor: selectedSensor.value.id.toString() }
        });
      };
      
      // Observer les changements dans les filtres
      watch(filters, () => {
        addMarkers();
      });
      
      // Initialiser la carte après le montage du composant
      onMounted(async () => {
        // Supprimer l'appel à l'API pour les villes
        // try {
        //   console.log('Appel /api/regions/ depuis MapView');
        //   const response = await environmentalApiService.getAvailableCities();
        //   cities.value = response.data;
        // } catch (e) {
        //   cities.value = [];
        // }
        // Charger Bootstrap pour les modals
        const bootstrapScript = document.createElement('script');
        bootstrapScript.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js';
        document.head.appendChild(bootstrapScript);
        
        // Charger les icônes Bootstrap
        const bootstrapIconsLink = document.createElement('link');
        bootstrapIconsLink.rel = 'stylesheet';
        bootstrapIconsLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css';
        document.head.appendChild(bootstrapIconsLink);
        
        // Initialiser la carte après un court délai
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
        miniChartRef,
        modalRef,
        selectedSensor,
        searchQuery,
        filters,
        cities,
        getQualityColor,
        getQualityClass,
        getQualityLabel,
        formatDate,
        searchLocation,
        refreshMap,
        viewSensorHistory
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
  
  .mini-chart {
    height: 200px;
    width: 100%;
  }
  
  /* Styles personnalisés pour les marqueurs */
  :deep(.custom-marker) {
    background: transparent;
    border: none;
  }
  </style>