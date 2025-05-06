<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold mb-4">Weather Forecast</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2">
            <div class="mb-6">
              <label for="station" class="block text-sm font-medium text-gray-700 mb-2">Select Station</label>
              <select
                id="station"
                v-model="selectedStation"
                @change="getWeather"
                class="w-full p-2 border rounded-lg bg-white"
                :disabled="isLoading"
              >
                <option value="">Select a station</option>
                <option v-for="station in stations" :key="station.id" :value="station.id">
                  {{ station.name }} ({{ station.id }})
                </option>
              </select>
              <div v-if="isLoading" class="mt-2 flex items-center text-blue-600">
                <div class="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent mr-2"></div>
                <span class="text-sm">Loading weather data...</span>
              </div>
            </div>

            <div v-if="weatherData && weatherData.length > 0" class="space-y-6">
              <div>
                <h3 class="text-xl font-bold mb-4">Next 12 Hours</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="(forecast, index) in first12Hours" :key="index" 
                    class="bg-gradient-to-br from-white to-blue-50 p-4 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 border border-blue-100">
                    <div class="text-sm text-gray-600 font-medium">
                      {{ formatTime(forecast.timestamp) }}
                    </div>
                    <div class="flex items-center justify-between mt-2">
                      <div class="text-3xl font-bold text-blue-600">
                        {{ Math.round(parseFloat(forecast.temperature)) }}°C
                      </div>
                      <img :src="getWeatherIcon(forecast.condition)" :alt="forecast.condition" 
                        class="w-12 h-12 text-blue-500">
                    </div>
                    <div class="mt-2 flex flex-wrap gap-2">
                      <div class="px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium inline-block">
                        {{ forecast.condition }}
                      </div>
                      <div class="px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium inline-block">
                        RH: {{ forecast.humidity }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <DailyForecast :forecasts="weatherData" />
            </div>

            <div v-if="error" class="mt-4 text-red-500">
              {{ error }}
            </div>

            <div v-if="isLoading" class="mt-4 text-center">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            </div>
          </div>

          <div class="lg:col-span-1">
            <WeatherGraphs v-if="weatherData && weatherData.length > 0" :forecasts="first12Hours" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getWeatherForecast } from '../services/weatherService'
import { getStations } from '../services/stationsService'
import { format } from 'date-fns'
import DailyForecast from '../components/DailyForecast.vue'
import WeatherGraphs from '../components/TemperatureGraph.vue'

const stations = ref(getStations())
const selectedStation = ref('')
const weatherData = ref(null)
const isLoading = ref(false)
const error = ref(null)

const first12Hours = computed(() => {
  if (!weatherData.value) return []
  return weatherData.value.slice(0, 12)
})

const formatTime = (timestamp) => {
  return format(new Date(timestamp), 'HH:mm')
}

const getWeatherIcon = (condition) => {
  const icons = {
    'Clear': '/icons/clear.svg',
    'Cloudy': '/icons/cloudy.svg',
    'Fog': '/icons/fog.svg',
    'Rainy': '/icons/rain.svg',
    'Snowy': '/icons/snow.svg',
    'Storm': '/icons/storm.svg',
    'Thunderstorm': '/icons/thunderstorm.svg'
  }
  return icons[condition] || icons['Clear']
}

const getWeather = async () => {
  if (!selectedStation.value) {
    error.value = 'Please select a station'
    return
  }

  isLoading.value = true
  error.value = null

  try {
    const data = await getWeatherForecast(selectedStation.value)
    weatherData.value = data
  } catch (err) {
    error.value = 'Failed to fetch weather data. Please try again.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}
</script> 