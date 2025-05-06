<template>
  <div class="temperature-graph">
    <div v-if="!forecasts || forecasts.length === 0" class="no-data-message">
      No temperature data available
    </div>
    <div v-else class="chart-container">
      <Line
        v-if="!isTest"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="test-chart">
        Temperature Chart ({{ forecasts.length }} data points)
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js'
import 'chartjs-adapter-date-fns'

// Check if we're in a test environment
const isTest = process.env.NODE_ENV === 'test'

if (!isTest) {
  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
  )
}

const props = defineProps({
  forecasts: {
    type: Array,
    required: true
  },
  timeRange: {
    type: String,
    default: '24h'
  }
})

const chartData = computed(() => {
  const temperatures = props.forecasts.map(forecast => parseFloat(forecast.temperature))
  const labels = props.forecasts.map(forecast => new Date(forecast.timestamp))

  return {
    labels,
    datasets: [
      {
        label: 'Temperature (°C)',
        data: temperatures,
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'time',
      time: {
        unit: props.timeRange === '7d' ? 'day' : 'hour',
        displayFormats: {
          hour: 'HH:mm',
          day: 'MMM dd'
        }
      },
      title: {
        display: true,
        text: 'Time'
      }
    },
    y: {
      title: {
        display: true,
        text: 'Temperature (°C)'
      }
    }
  },
  plugins: {
    legend: {
      display: true
    },
    tooltip: {
      callbacks: {
        label: (context) => `${context.parsed.y}°C`
      }
    }
  }
}))
</script>

<style scoped>
.temperature-graph {
  width: 100%;
  height: 300px;
  padding: 1rem;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.no-data-message {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.test-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
  color: #666;
}
</style> 