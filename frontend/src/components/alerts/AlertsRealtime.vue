<template>
  <div class="alerts-realtime">
    <h3>Alertes en temps réel</h3>
    <div v-if="alerts.length === 0" class="no-alerts">
      Aucune alerte active
    </div>
    <div v-else class="alerts-container">
      <div v-for="(alert, index) in alerts" :key="index" 
           class="alert" :class="'alert-' + alert.level.toLowerCase()">
        <h4>{{ alert.title }}</h4>
        <p>{{ alert.description }}</p>
        <small>{{ formatDate(alert.timestamp) }}</small>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue'

interface AlertData {
  title: string;
  description: string;
  level: 'INFO' | 'WARNING' | 'DANGER';
  timestamp: string;
}

export default defineComponent({
  name: 'AlertsRealtime',
  setup() {
    const alerts = ref<AlertData[]>([])
    const socket = ref<WebSocket | null>(null)
    
    const formatDate = (dateString: string): string => {
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    const setupWebSocket = () => {
      // Créer une connexion WebSocket
      socket.value = new WebSocket('ws://localhost:8000/ws/alerts/')
      
      if (socket.value) {
        // Événement de réception d'un message
        socket.value.onmessage = (event) => {
          const data = JSON.parse(event.data) as AlertData
          alerts.value.unshift(data)
          
          // Limiter à 10 alertes affichées
          if (alerts.value.length > 10) {
            alerts.value.pop()
          }
        }
        
        // Gestion des erreurs et déconnexions
        socket.value.onerror = (error) => {
          console.error('Erreur WebSocket:', error)
        }
        
        socket.value.onclose = () => {
          console.log('WebSocket déconnecté')
          // Tenter de se reconnecter après 5 secondes
          setTimeout(setupWebSocket, 5000)
        }
      }
    }
    
    onMounted(() => {
      setupWebSocket()
    })
    
    onBeforeUnmount(() => {
      // Fermer proprement la connexion WebSocket
      if (socket.value) {
        socket.value.close()
      }
    })
    
    return {
      alerts,
      formatDate
    }
  }
})
</script>

<style scoped>
.alerts-container {
  max-height: 400px;
  overflow-y: auto;
}

.alert {
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;
}

.alert-info {
  background-color: #cfe8ff;
  border-left: 4px solid #0d6efd;
}

.alert-warning {
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
}

.alert-danger {
  background-color: #f8d7da;
  border-left: 4px solid #dc3545;
}
</style>
