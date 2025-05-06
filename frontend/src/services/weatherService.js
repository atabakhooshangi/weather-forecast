import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const getWeatherForecast = async (stationId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/forecast/?station_id=${stationId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching weather forecast:', error)
    throw error
  }
}

export const getStations = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/stations`)
    return response.data
  } catch (error) {
    console.error('Error fetching stations:', error)
    throw error
  }
} 