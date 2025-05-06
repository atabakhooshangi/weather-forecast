<template>
  <div class="station-list">
    <div v-if="isLoading" class="loading-spinner">
      Loading stations...
    </div>
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-else>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search stations..."
        class="search-input"
      />
      <div class="stations">
        <div
          v-for="station in filteredStations"
          :key="station.id"
          :class="['station-item', { selected: station.id === selectedStation }]"
          @click="$emit('select', station.id)"
        >
          <h3>{{ station.name }}</h3>
          <p>{{ station.location }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  stations: {
    type: Array,
    required: true
  },
  selectedStation: {
    type: String,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

defineEmits(['select'])

const searchQuery = ref('')

const filteredStations = computed(() => {
  if (!searchQuery.value) return props.stations
  const query = searchQuery.value.toLowerCase()
  return props.stations.filter(station => 
    station.name.toLowerCase().includes(query) ||
    station.location.toLowerCase().includes(query)
  )
})
</script>

<style scoped>
.station-list {
  padding: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.stations {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.station-item {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.station-item:hover {
  background-color: #f5f5f5;
}

.station-item.selected {
  background-color: #e3f2fd;
  border-color: #2196f3;
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