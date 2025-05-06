<template>
  <div class="weather-display">
    <div v-if="isLoading" class="loading-spinner">
      Loading weather data...
    </div>
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-else-if="weatherData" class="weather-data">
      <div class="temperature">
        {{ weatherData.temperature }}°C
      </div>
      <div class="humidity">
        Humidity: {{ weatherData.humidity }}%
      </div>
      <div class="condition">
        {{ weatherData.condition }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getWeatherForecast } from '../services/weatherService'

const props = defineProps({
  stationId: {
    type: String,
    required: true
  }
})

const weatherData = ref(null)
const isLoading = ref(true)
const error = ref('')

const fetchWeatherData = async () => {
  try {
    isLoading.value = true
    error.value = ''
    weatherData.value = await getWeatherForecast(props.stationId)
  } catch (err) {
    error.value = err.message || 'Failed to fetch weather data'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchWeatherData)
</script>

<style scoped>
.weather-display {
  padding: 1rem;
  text-align: center;
}

.temperature {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.humidity {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.condition {
  font-size: 1.5rem;
  color: #333;
}

.loading-spinner {
  text-align: center;
  padding: 1rem;
}

.error-message {
  color: #f44336;
  padding: 1rem;
  text-align: center;
}
</style> 