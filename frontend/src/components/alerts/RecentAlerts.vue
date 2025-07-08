<template>
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">Alertes récentes</h5>
      </div>
      <div class="card-body p-0">
        <div v-if="alerts.length === 0" class="text-center p-3">
          <p class="text-muted mb-0">Aucune alerte active</p>
        </div>
        <div v-else>
          <div v-for="(alert, index) in alerts" :key="index" 
               class="alert-item border-start border-5" 
               :class="getAlertClass(alert.level)">
            <div class="d-flex p-3">
              <div class="alert-icon me-3">
                <i class="bi" :class="getAlertIcon(alert.level)"></i>
              </div>
              <div class="alert-content flex-grow-1">
                <h6 class="mb-1 fw-bold">{{ alert.title }}</h6>
                <p class="mb-1">{{ alert.description }}</p>
                <small class="text-muted">{{ formatDate(alert.timestamp) }}</small>
              </div>
            </div>
            <div v-if="index < alerts.length - 1" class="border-bottom"></div>
          </div>
        </div>
      </div>
    </div>
</template>
  
<script lang="ts">
  import { defineComponent, ref, onMounted } from "vue";
  
  interface Alert {
    id: number;
    title: string;
    description: string;
    level: "INFO" | "WARNING" | "DANGER";
    timestamp: string;
    metricType?: string;
    value?: number;
    unit?: string;
  }
  
  export default defineComponent({
    name: "RecentAlerts",
    props: {
      limit: {
        type: Number,
        default: 4
      }
    },
    setup(props) {
      // État
      const alerts = ref<Alert[]>([]);
  
      // Simuler la récupération des données d'alertes
      const fetchAlerts = () => {
        // Données d'alerte fictives pour la démonstration, adaptées aux métriques de l"application
        const allAlerts = [
          {
            id: 1,
            title: "Température élevée",
            description: "Pic de température à 35.2°C dans le centre de Paris",
            level: "DANGER",
            timestamp: new Date().toISOString(),
            metricType: "temp",
            value: 35.2,
            unit: "°C"
          },
          {
            id: 2,
            title: "Pic de pollution atmosphérique",
            description: "Indice de qualité de l'air supérieur à 80 à Marseille",
            level: "WARNING",
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            metricType: "airquality",
            value: 82,
            unit: "AQI"
          },
          {
            id: 3,
            title: "Risque de précipitations",
            description: "Probabilité de précipitation de 75% à Lyon",
            level: "INFO",
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            metricType: "precipprob",
            value: 75,
            unit: "%"
          },
          {
            id: 4,
            title: "Humidité élevée",
            description: "Niveau d'humidité de 85% à Bordeaux",
            level: "INFO",
            timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
            metricType: "humidity",
            value: 85,
            unit: "%"
          },
          {
            id: 5,
            title: "Baisse de la pression atmosphérique",
            description: "Chute de pression à 995 hPa, risque de dégradation météo",
            level: "WARNING",
            timestamp: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
            metricType: "pressure",
            value: 995,
            unit: "hPa"
          }
        ];
        
        // Limiter le nombre d"alertes à afficher selon la propriété limit
        alerts.value = allAlerts.slice(0, props.limit);
      };
  
      // Obtenir la classe CSS pour le style d"alerte en fonction du niveau
      const getAlertClass = (level: string): string => {
        switch (level) {
          case "DANGER":
            return "border-danger bg-danger bg-opacity-10";
          case "WARNING":
            return "border-warning bg-warning bg-opacity-10";
          case "INFO":
          default:
            return "border-info bg-info bg-opacity-10";
        }
      };
  
      // Obtenir l"icône en fonction du niveau d"alerte
      const getAlertIcon = (level: string): string => {
        switch (level) {
          case "DANGER":
            return 'bi-exclamation-circle-fill text-danger';
          case "WARNING":
            return "bi-exclamation-triangle-fill text-warning";
          case "INFO":
          default:
            return "bi-info-circle-fill text-info";
        }
      };
  
      // Formater la date
      const formatDate = (dateString: string): string => {
        const date = new Date(dateString);
        const now = new Date();
        const isToday = date.getDate() === now.getDate() && 
                        date.getMonth() === now.getMonth() && 
                        date.getFullYear() === now.getFullYear();
        
        const isYesterday = date.getDate() === now.getDate() - 1 && 
                            date.getMonth() === now.getMonth() && 
                            date.getFullYear() === now.getFullYear();
        
        const timeStr = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        
        if (isToday) {
          return `Aujourd"hui, ${timeStr}`;
        } else if (isYesterday) {
          return `Hier, ${timeStr}`;
        } else {
          return date.toLocaleDateString() + `, ${timeStr}`;
        }
      };
  
      // Charger les données au montage du composant
      onMounted(() => {
        fetchAlerts();
        console.log("RecentAlerts component mounted");
      });
  
      return {
        alerts,
        getAlertClass,
        getAlertIcon,
        formatDate
      };
    }
  });
</script>
  
<style scoped>
  .alert-item {
    transition: background-color 0.2s;
  }
  
  .alert-item:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }
  
  .alert-icon {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
  }
</style>