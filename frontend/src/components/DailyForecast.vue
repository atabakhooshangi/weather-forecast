<template>
  <div class="mt-8">
    <h3 class="text-xl font-bold mb-4">Daily Forecast</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div v-for="day in dailyForecasts" :key="day.date" 
        class="bg-gradient-to-br from-white to-indigo-50 p-5 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 border border-indigo-100">
        <div class="text-lg font-bold mb-3 text-indigo-700">{{ formatDate(day.date) }}</div>
        <div class="flex justify-between items-center mb-4 bg-white/50 p-3 rounded-lg">
          <div class="text-center">
            <div class="text-xs text-gray-500 uppercase mb-1">Max</div>
            <span class="text-2xl font-bold text-red-500">{{ day.maxTemp }}°</span>
          </div>
          <div class="h-8 w-px bg-gray-200"></div>
          <div class="text-center">
            <div class="text-xs text-gray-500 uppercase mb-1">Min</div>
            <span class="text-2xl font-bold text-blue-500">{{ day.minTemp }}°</span>
          </div>
        </div>
        <div class="space-y-2">
          <div class="text-sm font-medium text-gray-600 mb-2">Conditions:</div>
          <div class="space-y-2">
            <div v-for="(condition, index) in day.commonConditions" :key="index"
              class="flex items-center bg-white/70 px-3 py-2 rounded-lg shadow-sm">
              <img :src="getWeatherIcon(condition)" :alt="condition" class="w-5 h-5 mr-2">
              <span class="text-sm font-medium text-gray-700">{{ condition }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { format } from 'date-fns'

const props = defineProps({
  forecasts: {
    type: Array,
    required: true
  }
})

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

const formatDate = (date) => {
  return format(new Date(date), 'EEE, MMM d')
}

const dailyForecasts = computed(() => {
  const days = {}
  
  props.forecasts.forEach(forecast => {
    const date = new Date(forecast.timestamp).toDateString()
    if (!days[date]) {
      days[date] = {
        date,
        temperatures: [],
        conditions: {},
        maxTemp: -Infinity,
        minTemp: Infinity,
        commonConditions: []
      }
    }
    
    const temp = parseFloat(forecast.temperature)
    days[date].temperatures.push(temp)
    days[date].maxTemp = Math.max(days[date].maxTemp, temp)
    days[date].minTemp = Math.min(days[date].minTemp, temp)
    
    days[date].conditions[forecast.condition] = (days[date].conditions[forecast.condition] || 0) + 1
  })
  
  return Object.values(days).map(day => {
    // Round temperatures
    day.maxTemp = Math.round(day.maxTemp)
    day.minTemp = Math.round(day.minTemp)
    
    // Get top 2 most common conditions
    day.commonConditions = Object.entries(day.conditions)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 2)
      .map(([condition]) => condition)
    
    return day
  })
})
</script> 