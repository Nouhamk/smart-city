<template>
  <div class="air-quality-chart">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, PropType } from 'vue'
import { Chart, ChartConfiguration, ChartData, LineController, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Measurement } from '../../types/models'

// Enregistrer les composants Chart.js nécessaires
Chart.register(LineController, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default defineComponent({
  name: 'AirQualityChart',
  props: {
    data: {
      type: Array as PropType<Measurement[]>,
      required: true
    },
    title: {
      type: String,
      default: 'Qualité de l\'air'
    }
  },
  setup(props) {
    const chartRef = ref<HTMLCanvasElement | null>(null)
    let chart: Chart | null = null
    
    const createChart = () => {
      if (!chartRef.value) return
      
      // Préparer les données pour le graphique
      const labels = props.data.map(item => {
        const date = new Date(item.timestamp)
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
      })
      
      const values = props.data.map(item => item.value)
      
      const chartData: ChartData = {
        labels,
        datasets: [
          {
            label: 'Indice de qualité',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            data: values,
            tension: 0.4
          }
        ]
      }
      
      const config: ChartConfiguration = {
        type: 'line',
        data: chartData,
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: props.title
            },
            tooltip: {
              mode: 'index',
              intersect: false
            },
            legend: {
              position: 'top'
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      }
      
      // Créer le graphique
      chart = new Chart(chartRef.value, config)
    }
    
    const updateChart = () => {
      if (!chart) return
      
      // Mettre à jour les données du graphique
      const labels = props.data.map(item => {
        const date = new Date(item.timestamp)
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
      })
      
      const values = props.data.map(item => item.value)
      
      chart.data.labels = labels
      chart.data.datasets[0].data = values
      chart.update()
    }
    
    onMounted(() => {
      createChart()
    })
    
    // Observer les changements dans les données pour mettre à jour le graphique
    watch(() => props.data, () => {
      if (chart) {
        updateChart()
      } else {
        createChart()
      }
    }, { deep: true })
    
    return {
      chartRef
    }
  }
})
</script>
